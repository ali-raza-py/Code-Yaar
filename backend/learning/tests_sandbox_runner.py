import io
import json
import subprocess
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from unittest.mock import Mock, patch

from learning.services.sandbox import (
    DockerSandbox,
    SubprocessSandbox,
    _NoRedirectHandler,
)
from learning.services.sandbox_runner import (
    BoundedThreadingHTTPServer,
    RunnerHandler,
    RunnerRequestError,
    build_docker_command,
    validate_payload,
)


class RunnerPayloadTests(unittest.TestCase):
    def test_limits_requested_values_to_server_caps(self):
        payload = validate_payload({
            'code': 'print(42)',
            'language': 'python',
            'stdin': '',
            'timeout_seconds': 100,
            'max_output_bytes': 1_000_000,
        })
        self.assertEqual(payload['timeout_seconds'], 10.0)
        self.assertEqual(payload['max_output_bytes'], 100_000)

    def test_rejects_unsupported_or_malformed_input(self):
        with self.assertRaises(RunnerRequestError):
            validate_payload({'code': 'x', 'language': []})
        with self.assertRaises(RunnerRequestError):
            validate_payload({'code': 'x', 'language': 'javascript'})
        with self.assertRaises(RunnerRequestError):
            validate_payload({'code': 'x' * 65_537, 'language': 'python'})
        with self.assertRaises(RunnerRequestError):
            validate_payload({
                'code': 'x',
                'language': 'python',
                'timeout_seconds': float('nan'),
            })

    def test_container_command_has_an_isolated_read_only_boundary(self):
        python_command = build_docker_command(
            'codeyaar-sandbox:latest', 'cy-run-test', '/srv/sandbox/run-1', 'python',
        )
        cpp_command = build_docker_command(
            'codeyaar-sandbox:latest', 'cy-run-test', '/srv/sandbox/run-1', 'cpp',
        )
        self.assertIn('--network', python_command)
        self.assertIn('none', python_command)
        self.assertIn('--read-only', python_command)
        self.assertIn('--cap-drop', python_command)
        self.assertIn('--security-opt', python_command)
        self.assertIn('type=bind,src=/srv/sandbox/run-1,dst=/workspace,readonly', python_command)
        self.assertNotIn('--env', python_command)
        self.assertIn('/tmp:rw,noexec,nosuid,nodev,size=32m', python_command)
        self.assertIn('/tmp:rw,nosuid,nodev,size=32m', cpp_command)
        self.assertNotIn('noexec', cpp_command)


class FakeRunnerExecutor:
    def image_available(self):
        return True

    def execute(self, payload):
        return {
            'status': 'success',
            'output': payload['code'],
            'error': '',
            'return_code': 0,
            'execution_time_ms': 1,
        }


class RunnerHttpTests(unittest.TestCase):
    def setUp(self):
        self.token = 't' * 32
        self.server = BoundedThreadingHTTPServer(
            ('127.0.0.1', 0), RunnerHandler, max_concurrency=2,
        )
        self.server.executor = FakeRunnerExecutor()
        self.server.token = self.token
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f'http://127.0.0.1:{self.server.server_port}'

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_health_requires_runner_token(self):
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(f'{self.base_url}/health')
        self.assertEqual(error.exception.code, 401)
        error.exception.close()

        invalid_request = urllib.request.Request(
            f'{self.base_url}/health',
            headers={'Authorization': 'Bearer \u00e9'},
        )
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(invalid_request)
        self.assertEqual(error.exception.code, 401)
        error.exception.close()

        request = urllib.request.Request(
            f'{self.base_url}/health',
            headers={'Authorization': f'Bearer {self.token}'},
        )
        with urllib.request.urlopen(request) as response:
            self.assertEqual(json.loads(response.read()), {'status': 'ok'})

    def test_execution_requires_token_and_validates_body(self):
        body = json.dumps({
            'code': 'print(42)',
            'language': 'python',
        }).encode()
        request = urllib.request.Request(
            f'{self.base_url}/v1/execute',
            data=body,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request)
        self.assertEqual(error.exception.code, 401)
        error.exception.close()

        request.add_header('Authorization', f'Bearer {self.token}')
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read())
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['output'], 'print(42)')


class RemoteSandboxClientTests(unittest.TestCase):
    def test_refuses_non_loopback_runner_urls(self):
        with self.assertRaises(ValueError):
            DockerSandbox('http://runner.internal:8765', 't' * 32)
        with self.assertRaises(ValueError):
            DockerSandbox('http://localhost:8765', 't' * 32)
        with self.assertRaises(ValueError):
            DockerSandbox('http://127.0.0.1:8765', 'short')

    def test_allows_https_runner_on_remote_host(self):
        sandbox = DockerSandbox('https://runner.example.test', 't' * 32)

        self.assertEqual(sandbox.runner_url, 'https://runner.example.test')

    def test_rejects_remote_runner_urls_with_path_or_credentials(self):
        for url in (
            'https://runner.example.test/api',
            'https://user:password@runner.example.test',
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                DockerSandbox(url, 't' * 32)

    def test_execute_sends_auth_and_converts_runner_result(self):
        result_body = json.dumps({
            'status': 'success',
            'output': '42\n',
            'error': '',
            'return_code': 0,
            'execution_time_ms': 12,
        }).encode()

        class FakeResponse:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self, size=-1):
                return result_body

        opener = Mock()
        opener.open.return_value = FakeResponse()
        with patch(
            'learning.services.sandbox.urllib.request.build_opener',
            return_value=opener,
        ) as build_opener:
            sandbox = DockerSandbox('http://127.0.0.1:8765', 't' * 32)
            result = sandbox.execute('print(42)', 'python')

        self.assertEqual(result.status, 'success')
        self.assertEqual(result.output, '42\n')
        request = opener.open.call_args.args[0]
        self.assertEqual(request.get_header('Authorization'), f'Bearer {"t" * 32}')
        handlers = build_opener.call_args.args
        self.assertTrue(any(
            isinstance(handler, urllib.request.ProxyHandler) and not handler.proxies
            for handler in handlers
        ))
        self.assertTrue(any(isinstance(handler, _NoRedirectHandler) for handler in handlers))


class LocalSandboxEnvironmentTests(unittest.TestCase):
    def test_strips_database_and_email_secrets_from_child_environment(self):
        with patch.dict(
            'os.environ',
            {
                'DB_PASSWORD': 'not-a-real-secret',
                'EMAIL_HOST_PASSWORD': 'not-a-real-secret',
                'THIRD_PARTY_API_KEY': 'not-a-real-secret',
            },
            clear=False,
        ):
            child_env = SubprocessSandbox()._clean_env()

        self.assertNotIn('DB_PASSWORD', child_env)
        self.assertNotIn('EMAIL_HOST_PASSWORD', child_env)
        self.assertNotIn('THIRD_PARTY_API_KEY', child_env)


class DockerExecutorTests(unittest.TestCase):
    class FakeProcess:
        def __init__(self, stdout=b'42\n', stderr=b'', return_code=0):
            self.stdin = io.BytesIO()
            self.stdout = io.BytesIO(stdout)
            self.stderr = io.BytesIO(stderr)
            self.returncode = return_code

        def poll(self):
            return self.returncode

        def wait(self, timeout=None):
            return self.returncode

        def terminate(self):
            self.returncode = -15

        def kill(self):
            self.returncode = -9

    def test_runs_only_docker_cli_and_returns_separate_program_streams(self):
        from learning.services.sandbox_runner import DockerExecutor

        payload = {
            'code': 'print(42)',
            'language': 'python',
            'stdin': '',
            'timeout_seconds': 1.0,
            'max_output_bytes': 100,
        }
        with tempfile.TemporaryDirectory() as work_root:
            with patch(
                'learning.services.sandbox_runner.subprocess.Popen',
                return_value=self.FakeProcess(stdout=b'42\n', stderr=b'diagnostic'),
            ) as popen, patch(
                'learning.services.sandbox_runner.subprocess.run',
            ):
                result = DockerExecutor(work_root).execute(payload)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['output'], '42\n')
        self.assertEqual(result['error'], 'diagnostic')
        self.assertEqual(popen.call_args.args[0][0:2], ['docker', 'run'])

    def test_caps_output(self):
        from learning.services.sandbox_runner import DockerExecutor

        payload = {
            'code': 'print("too much")',
            'language': 'python',
            'stdin': '',
            'timeout_seconds': 1.0,
            'max_output_bytes': 4,
        }
        with tempfile.TemporaryDirectory() as work_root:
            with patch(
                'learning.services.sandbox_runner.subprocess.Popen',
                return_value=self.FakeProcess(stdout=b'overflow'),
            ), patch('learning.services.sandbox_runner.subprocess.run'):
                result = DockerExecutor(work_root).execute(payload)

        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['output'], 'over')
        self.assertEqual(result['error'], 'Output limit exceeded.')

    def test_enforces_wall_clock_timeout(self):
        from learning.services.sandbox_runner import DockerExecutor

        class HangingProcess(self.FakeProcess):
            def __init__(self):
                super().__init__(stdout=b'')
                self.returncode = None

            def wait(self, timeout=None):
                if self.returncode is not None:
                    return self.returncode
                raise subprocess.TimeoutExpired('docker', timeout)

        payload = {
            'code': 'while True: pass',
            'language': 'python',
            'stdin': '',
            'timeout_seconds': 0.01,
            'max_output_bytes': 100,
        }
        with tempfile.TemporaryDirectory() as work_root:
            with patch(
                'learning.services.sandbox_runner.subprocess.Popen',
                return_value=HangingProcess(),
            ), patch('learning.services.sandbox_runner.subprocess.run'):
                result = DockerExecutor(work_root).execute(payload)

        self.assertEqual(result['status'], 'timeout')


if __name__ == '__main__':
    unittest.main()
