"""Loopback HTTP service that runs learner programs in disposable Docker containers."""

import hmac
import json
import logging
import math
import os
import subprocess
import tempfile
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


logger = logging.getLogger('sandbox_runner')

MAX_CODE_BYTES = 64 * 1024
MAX_STDIN_BYTES = 16 * 1024
MAX_REQUEST_BYTES = (MAX_CODE_BYTES + MAX_STDIN_BYTES) * 12 + 4096
MAX_OUTPUT_BYTES = 100_000
MAX_TIMEOUT_SECONDS = 10.0
MEMORY_LIMIT = '256m'
CPU_LIMIT = '0.5'
PIDS_LIMIT = '64'
IMAGE_NAME = 'codeyaar-sandbox:latest'


class RunnerRequestError(ValueError):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


def validate_payload(payload: Any) -> dict:
    if not isinstance(payload, dict):
        raise RunnerRequestError('Request body must be a JSON object.')

    code = payload.get('code')
    language = payload.get('language')
    stdin = payload.get('stdin', '')
    if not isinstance(code, str) or not code.strip():
        raise RunnerRequestError('Code must be a non-empty string.')
    try:
        code_size = len(code.encode('utf-8'))
        stdin_size = len(stdin.encode('utf-8')) if isinstance(stdin, str) else 0
    except UnicodeEncodeError:
        raise RunnerRequestError('Code and standard input must be valid UTF-8 text.') from None
    if code_size > MAX_CODE_BYTES:
        raise RunnerRequestError('Code exceeds the runner size limit.', 413)
    if not isinstance(language, str) or language not in {'python', 'cpp'}:
        raise RunnerRequestError('Only Python and C++ are supported.')
    if not isinstance(stdin, str):
        raise RunnerRequestError('Standard input must be a string.')
    if stdin_size > MAX_STDIN_BYTES:
        raise RunnerRequestError('Standard input exceeds the runner size limit.', 413)

    requested_timeout = payload.get('timeout_seconds', MAX_TIMEOUT_SECONDS)
    if isinstance(requested_timeout, bool) or not isinstance(requested_timeout, (int, float)):
        raise RunnerRequestError('Execution timeout must be a number.')
    try:
        timeout_seconds = float(requested_timeout)
    except OverflowError:
        raise RunnerRequestError('Execution timeout must be finite.') from None
    if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise RunnerRequestError('Execution timeout must be positive.')

    requested_output = payload.get('max_output_bytes', MAX_OUTPUT_BYTES)
    if isinstance(requested_output, bool) or not isinstance(requested_output, int):
        raise RunnerRequestError('Output limit must be an integer.')
    if requested_output <= 0:
        raise RunnerRequestError('Output limit must be positive.')

    return {
        'code': code,
        'language': language,
        'stdin': stdin,
        'timeout_seconds': min(timeout_seconds, MAX_TIMEOUT_SECONDS),
        'max_output_bytes': min(requested_output, MAX_OUTPUT_BYTES),
    }


def build_docker_command(
    image: str,
    container_name: str,
    source_dir: str,
    language: str,
) -> list[str]:
    command = [
        'docker', 'run', '--rm', '--interactive',
        '--name', container_name,
        '--label', 'com.codeyaar.sandbox-runner=true',
        '--network', 'none',
        '--read-only',
        '--tmpfs', '/tmp:rw,nosuid,nodev,size=32m'
        if language == 'cpp'
        else '/tmp:rw,noexec,nosuid,nodev,size=32m',
        '--memory', MEMORY_LIMIT,
        '--memory-swap', MEMORY_LIMIT,
        '--cpus', CPU_LIMIT,
        '--pids-limit', PIDS_LIMIT,
        '--ulimit', 'cpu=10:10',
        '--ulimit', 'nofile=64:64',
        '--ulimit', 'fsize=1048576:1048576',
        '--cap-drop', 'ALL',
        '--security-opt', 'no-new-privileges:true',
        '--user', '65534:65534',
        '--mount', f'type=bind,src={source_dir},dst=/workspace,readonly',
        '--workdir', '/tmp',
        image,
    ]
    if language == 'python':
        command.extend(['python3', '-I', '/workspace/main.py'])
    else:
        command.extend([
            'sh', '-c',
            'g++ -std=c++17 -O1 -pipe /workspace/main.cpp -o /tmp/main '
            '>/dev/null 2>/tmp/build.err; build_status=$?; '
            'if [ "$build_status" -ne 0 ]; then cat /tmp/build.err >&2; '
            'exit "$build_status"; fi; exec /tmp/main',
        ])
    return command


def _read_limited_output(stream, output: bytearray, limit: int, exceeded: threading.Event) -> None:
    total = 0
    while True:
        try:
            chunk = stream.read(4096)
        except OSError:
            break
        if not chunk:
            break
        total += len(chunk)
        if len(output) < limit:
            output.extend(chunk[:limit - len(output)])
        if total > limit:
            exceeded.set()


def _write_stdin(stream, data: bytes) -> None:
    try:
        stream.write(data)
        stream.flush()
    except (BrokenPipeError, OSError, ValueError):
        pass
    finally:
        try:
            stream.close()
        except OSError:
            pass


class DockerExecutor:
    def __init__(
        self,
        work_root: str,
        image: str = IMAGE_NAME,
        timeout_seconds: float = MAX_TIMEOUT_SECONDS,
        max_output_bytes: int = MAX_OUTPUT_BYTES,
    ):
        self.work_root = Path(work_root)
        self.image = image
        self.timeout_seconds = min(timeout_seconds, MAX_TIMEOUT_SECONDS)
        self.max_output_bytes = min(max_output_bytes, MAX_OUTPUT_BYTES)

    def image_available(self) -> bool:
        try:
            result = subprocess.run(
                ['docker', 'image', 'inspect', self.image],
                capture_output=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return False
        return result.returncode == 0

    def execute(self, payload: dict) -> dict:
        code = payload['code']
        language = payload['language']
        stdin = payload['stdin']
        timeout_seconds = min(payload['timeout_seconds'], self.timeout_seconds)
        output_limit = min(payload['max_output_bytes'], self.max_output_bytes)
        container_name = f'cy-run-{uuid.uuid4().hex}'
        source_name = 'main.py' if language == 'python' else 'main.cpp'
        started = time.monotonic()
        try:
            self.work_root.mkdir(mode=0o700, parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(
                prefix='run-', dir=self.work_root,
            ) as source_dir:
                source_path = Path(source_dir) / source_name
                source_path.write_text(code, encoding='utf-8')
                os.chmod(source_dir, 0o755)
                source_path.chmod(0o644)
                process = subprocess.Popen(
                    build_docker_command(
                        self.image, container_name, source_dir, language,
                    ),
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    close_fds=True,
                )
                output = bytearray()
                error = bytearray()
                exceeded = threading.Event()
                output_reader = threading.Thread(
                    target=_read_limited_output,
                    args=(process.stdout, output, output_limit, exceeded),
                    daemon=True,
                )
                error_reader = threading.Thread(
                    target=_read_limited_output,
                    args=(process.stderr, error, output_limit, exceeded),
                    daemon=True,
                )
                output_reader.start()
                error_reader.start()
                input_writer = threading.Thread(
                    target=_write_stdin,
                    args=(process.stdin, stdin.encode('utf-8')),
                    daemon=True,
                )
                input_writer.start()

                deadline = started + timeout_seconds
                timed_out = False
                while process.poll() is None:
                    if exceeded.wait(0.05):
                        self._remove_container(container_name)
                        process.terminate()
                        break
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        timed_out = True
                        self._remove_container(container_name)
                        process.terminate()
                        break
                    try:
                        process.wait(timeout=min(0.05, remaining))
                    except subprocess.TimeoutExpired:
                        continue

                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=2)
                output_reader.join(timeout=2)
                error_reader.join(timeout=2)
                input_writer.join(timeout=1)

                elapsed = int((time.monotonic() - started) * 1000)
                output_text = bytes(output).decode('utf-8', errors='replace')
                error_text = bytes(error).decode('utf-8', errors='replace')
                output_text = output_text.replace('/workspace/', '')
                error_text = error_text.replace('/workspace/', '')
                if timed_out:
                    return {
                        'status': 'timeout',
                        'output': output_text,
                        'error': (
                            f'Execution timed out after {timeout_seconds:g} seconds. '
                            'Check for an infinite loop or a range that is too large.'
                        ),
                        'return_code': -1,
                        'execution_time_ms': elapsed,
                    }
                if exceeded.is_set():
                    return {
                        'status': 'error',
                        'output': output_text,
                        'error': 'Output limit exceeded.',
                        'return_code': process.returncode or -1,
                        'execution_time_ms': elapsed,
                    }
                if output_reader.is_alive() or error_reader.is_alive():
                    return self._infrastructure_error(elapsed)
                if process.returncode is None or process.returncode in {125, 126, 127}:
                    return self._infrastructure_error(elapsed)
                if process.returncode:
                    return {
                        'status': 'error',
                        'output': output_text,
                        'error': error_text.strip() or 'Program exited with an error.',
                        'return_code': process.returncode,
                        'execution_time_ms': elapsed,
                    }
                return {
                    'status': 'success',
                    'output': output_text,
                    'error': error_text,
                    'return_code': 0,
                    'execution_time_ms': elapsed,
                }
        except (OSError, subprocess.SubprocessError) as exc:
            logger.warning('Sandbox execution failed: %s', type(exc).__name__)
            return self._infrastructure_error(int((time.monotonic() - started) * 1000))
        finally:
            self._remove_container(container_name)

    @staticmethod
    def _infrastructure_error(elapsed: int) -> dict:
        return {
            'status': 'error',
            'output': '',
            'error': 'Execution service is unavailable.',
            'return_code': -1,
            'execution_time_ms': elapsed,
        }

    @staticmethod
    def _remove_container(container_name: str) -> None:
        try:
            subprocess.run(
                ['docker', 'rm', '--force', container_name],
                capture_output=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            logger.warning('Could not remove a sandbox container.')


class BoundedThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 16

    def __init__(self, server_address, request_handler, max_concurrency: int):
        self._slots = threading.BoundedSemaphore(max_concurrency)
        super().__init__(server_address, request_handler)

    def process_request(self, request, client_address):
        if not self._slots.acquire(blocking=False):
            try:
                request.sendall(
                    b'HTTP/1.1 503 Service Unavailable\r\n'
                    b'Content-Length: 0\r\nConnection: close\r\n\r\n'
                )
            finally:
                self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self._slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._slots.release()


class RunnerHandler(BaseHTTPRequestHandler):
    server_version = 'CodeYaarRunner'
    sys_version = ''

    @property
    def executor(self) -> DockerExecutor:
        return self.server.executor

    @property
    def token(self) -> str:
        return self.server.token

    def _send_json(self, status_code: int, payload: dict) -> None:
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self) -> bool:
        provided = self.headers.get('Authorization', '')
        scheme, _, supplied = provided.partition(' ')
        if scheme.lower() != 'bearer':
            return False
        try:
            return hmac.compare_digest(supplied.encode('ascii'), self.token.encode('ascii'))
        except UnicodeEncodeError:
            return False

    def do_GET(self) -> None:
        if self.path != '/health':
            self._send_json(404, {'error': 'Not found.'})
            return
        if not self._authorized():
            self._send_json(401, {'error': 'Unauthorized.'})
            return
        if not self.executor.image_available():
            self._send_json(503, {'status': 'unavailable'})
            return
        self._send_json(200, {'status': 'ok'})

    def do_POST(self) -> None:
        if self.path != '/v1/execute':
            self._send_json(404, {'error': 'Not found.'})
            return
        if not self._authorized():
            self._send_json(401, {'error': 'Unauthorized.'})
            return
        content_length = self.headers.get('Content-Length')
        try:
            body_length = int(content_length or '')
        except ValueError:
            self._send_json(411, {'error': 'Content-Length is required.'})
            return
        if body_length < 0 or body_length > MAX_REQUEST_BYTES:
            self._send_json(413, {'error': 'Request body exceeds the runner size limit.'})
            return
        try:
            payload = json.loads(self.rfile.read(body_length).decode('utf-8'))
            validated = validate_payload(payload)
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {'error': 'Request body must be valid JSON.'})
            return
        except RunnerRequestError as exc:
            self._send_json(exc.status_code, {'error': str(exc)})
            return

        result = self.executor.execute(validated)
        self._send_json(200, result)

    def log_message(self, format_string: str, *args) -> None:
        logger.info('%s - %s', self.address_string(), format_string % args)


def main() -> None:
    token = os.environ.get('SANDBOX_RUNNER_TOKEN', '')
    if len(token) < 32:
        raise RuntimeError('SANDBOX_RUNNER_TOKEN must contain at least 32 characters.')
    host = os.environ.get('SANDBOX_RUNNER_HOST', '127.0.0.1')
    if host != '127.0.0.1':
        raise RuntimeError('Sandbox runner must listen on 127.0.0.1.')
    try:
        port = int(os.environ.get('SANDBOX_RUNNER_PORT', '8765'))
        concurrency = int(os.environ.get('SANDBOX_MAX_CONCURRENCY', '2'))
    except ValueError:
        raise RuntimeError('Sandbox runner port and concurrency must be integers.') from None
    if not 1 <= port <= 65535 or not 1 <= concurrency <= 4:
        raise RuntimeError('Sandbox runner port or concurrency is outside the allowed range.')

    work_root = os.environ.get('SANDBOX_WORK_ROOT', '/srv/codeyaar/sandbox')
    image = os.environ.get('SANDBOX_DOCKER_IMAGE', IMAGE_NAME)
    executor = DockerExecutor(work_root=work_root, image=image)
    if not executor.image_available():
        raise RuntimeError(f'Required Docker image is unavailable: {image}')

    class ConfiguredRunnerHandler(RunnerHandler):
        pass

    server = BoundedThreadingHTTPServer((host, port), ConfiguredRunnerHandler, concurrency)
    server.executor = executor
    server.token = token
    logger.info('Sandbox runner listening on %s:%s', host, port)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
