"""
Sandbox Execution Service (spec §15)

CRITICAL SECURITY REQUIREMENT:
Never execute arbitrary learner code inside the Django application process.

Architecture:
    Django API → Execution Service → Sandbox → Result

The sandbox provides:
- CPU time limits
- Memory limits
- Execution timeout
- Isolated filesystem
- Restricted network access
- Process isolation
- Automatic cleanup

This module defines the interface and provides a development adapter
that simulates execution. In production, replace with actual sandbox
(Docker containers, AWS Lambda, or similar).
"""

import os
import subprocess
import sys
import tempfile
import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from .language_adapter import (
    ExecutionResult,
    TestResult,
    ValidationResult,
    get_adapter,
)

logger = logging.getLogger(__name__)


@dataclass
class SandboxConfig:
    """Configuration for sandbox execution limits."""
    timeout_seconds: float = 10.0
    max_memory_mb: int = 256
    max_output_bytes: int = 1_048_576  # 1MB
    max_cpu_time_seconds: float = 5.0
    allow_network: bool = False
    allowed_imports: Optional[list[str]] = None  # None = all safe imports


class SandboxService(ABC):
    """
    Abstract sandbox service interface.

    In production, implement this with:
    - Docker containers (recommended)
    - AWS Lambda / Google Cloud Functions
    - Firecracker microVMs
    - nsjail / bubblewrap on Linux
    """

    @abstractmethod
    def execute(
        self,
        code: str,
        language: str,
        config: Optional[SandboxConfig] = None,
        stdin: str = '',
    ) -> ExecutionResult:
        """
        Execute code in an isolated sandbox.

        Args:
            code: Source code to execute
            language: Language code (e.g., 'python', 'javascript')
            config: Sandbox configuration limits
            stdin: Optional standard input

        Returns:
            ExecutionResult with output, errors, and timing
        """
        pass

    @abstractmethod
    def run_tests(
        self,
        code: str,
        language: str,
        test_cases: list[dict],
        config: Optional[SandboxConfig] = None,
    ) -> list[TestResult]:
        """
        Run test cases against learner code.

        Args:
            code: Learner's source code
            language: Language code
            test_cases: List of test case dicts with 'input' and 'expected_output'
            config: Sandbox configuration limits

        Returns:
            List of TestResult for each test case
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the sandbox service is available."""
        pass


class DevelopmentSandbox(SandboxService):
    """
    Development sandbox that simulates execution without actually running code.

    WARNING: This is NOT safe for production use.
    It exists only for development and testing the interface.
    Replace with a real sandbox before deploying.
    """

    def execute(
        self,
        code: str,
        language: str,
        config: Optional[SandboxConfig] = None,
        stdin: str = '',
    ) -> ExecutionResult:
        """Simulate code execution for development."""
        config = config or SandboxConfig()

        if not code.strip():
            return ExecutionResult(
                status='error',
                error='No code provided.',
            )

        try:
            adapter = get_adapter(language)
        except ValueError as e:
            return ExecutionResult(
                status='error',
                error=str(e),
            )

        # Simulate execution delay
        time.sleep(0.1)

        # For development, return a simulated result
        wrapped = adapter.wrap_for_execution(code)
        line_count = len(wrapped.strip().split('\n'))

        return ExecutionResult(
            status='success',
            output=f'# [Development Sandbox Simulation]\n# Executed {line_count} lines of {adapter.language_name} code.\n# Connect a real sandbox for actual execution.',
            return_code=0,
            execution_time_ms=100,
        )

    def run_tests(
        self,
        code: str,
        language: str,
        test_cases: list[dict],
        config: Optional[SandboxConfig] = None,
    ) -> list[TestResult]:
        """Simulate test execution for development."""
        if not code.strip():
            return [
                TestResult(
                    test_number=1,
                    status='error',
                    message='No code provided.',
                )
            ]

        results = []
        for i, test in enumerate(test_cases):
            results.append(
                TestResult(
                    test_number=i + 1,
                    status='pending',
                    expected=test.get('expected_output', ''),
                    message='Sandbox execution required for validation.',
                )
            )
        return results

    def health_check(self) -> bool:
        return True


class SubprocessPythonSandbox(SandboxService):
    """
    Real Python execution for local development and self-hosted deployments.

    Runs each program in a separate `python -I` process with:
    - a wall-clock timeout (killed and reported as timeout)
    - captured output with a hard byte cap
    - isolated mode (-I: ignores site-packages user dirs and env vars)
    - a temporary working directory that is deleted after the run
    - stdin supplied from test-case input

    This is process isolation with resource limits, NOT a hardened security
    boundary. For multi-tenant production deployments, replace with
    DockerSandbox / a hosted execution service. Restricted to Python.
    """

    def __init__(
        self,
        python_exe: Optional[str] = None,
        config: Optional[SandboxConfig] = None,
    ):
        self.python_exe = python_exe or sys.executable
        self.config = config or SandboxConfig()

    def _run_one(self, code: str, stdin: str) -> ExecutionResult:
        start = time.monotonic()
        tmp_dir = tempfile.mkdtemp(prefix='cy-sandbox-')
        script_path = os.path.join(tmp_dir, 'main.py')
        try:
            with open(script_path, 'w', encoding='utf-8') as fh:
                fh.write(code)
            env = dict(os.environ)
            # Strip our own environment so learner code cannot read secrets.
            for key in list(env):
                if key.startswith(('DJANGO_', 'AWS_', 'DATABASE', 'SECRET', 'GIT', 'HOME')) and key != 'HOME':
                    env.pop(key, None)
            env['PYTHONIOENCODING'] = 'utf-8'
            try:
                proc = subprocess.run(
                    [self.python_exe, '-I', script_path],
                    input=stdin,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=self.config.timeout_seconds,
                    cwd=tmp_dir,
                    env=env,
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    status='timeout',
                    error=(
                        f'Execution timed out after '
                        f'{self.config.timeout_seconds:g} seconds. '
                        'Check for an infinite loop or a range that is too large.'
                    ),
                    execution_time_ms=int((time.monotonic() - start) * 1000),
                )
            elapsed = int((time.monotonic() - start) * 1000)
            out = (proc.stdout or '')[:self.config.max_output_bytes]
            err = (proc.stderr or '')[:self.config.max_output_bytes]
            if proc.returncode:
                return ExecutionResult(
                    status='error',
                    output=out,
                    error=err.strip(),
                    return_code=proc.returncode,
                    execution_time_ms=elapsed,
                )
            return ExecutionResult(
                status='success', output=out, error=err.strip(),
                return_code=0, execution_time_ms=elapsed,
            )
        except Exception as exc:  # noqa: BLE001 — never let the runner crash the API
            return ExecutionResult(status='error', error=f'Sandbox failure: {exc}')
        finally:
            try:
                os.remove(script_path)
                os.rmdir(tmp_dir)
            except OSError:
                pass

    def execute(
        self,
        code: str,
        language: str,
        config: Optional[SandboxConfig] = None,
        stdin: str = '',
    ) -> ExecutionResult:
        if language != 'python':
            return ExecutionResult(
                status='error',
                error=f'Server-side execution currently supports Python only (got {language!r}).',
            )
        if not code.strip():
            return ExecutionResult(status='error', error='No code provided.')
        return self._run_one(code, stdin)

    def run_tests(
        self,
        code: str,
        language: str,
        test_cases: list[dict],
        config: Optional[SandboxConfig] = None,
    ) -> list[TestResult]:
        results: list[TestResult] = []
        for i, test in enumerate(test_cases):
            expected = str(test.get('expected_output', '')).strip()
            stdin = test.get('input', '') if isinstance(test.get('input'), str) else ''
            run = self._run_one(code, stdin)
            if run.status in ('error', 'timeout'):
                results.append(TestResult(
                    test_number=i + 1,
                    status='error',
                    expected=expected,
                    actual=(run.error or run.output).strip(),
                    message=run.error or 'Runtime error.',
                ))
            elif run.output.strip() == expected:
                results.append(TestResult(
                    test_number=i + 1, status='passed',
                    expected=expected, actual=run.output.strip(),
                    message='Output matches the expected result.',
                ))
            else:
                results.append(TestResult(
                    test_number=i + 1, status='failed',
                    expected=expected, actual=run.output.strip(),
                    message=f'Expected {expected!r}, got {run.output.strip()!r}.',
                ))
        return results

    def health_check(self) -> bool:
        result = self._run_one('print(6 * 7)', '')
        return result.status == 'success' and result.output.strip() == '42'


class DockerSandbox(SandboxService):
    """
    Production Docker-based sandbox (stub).

    Implementation requires:
    1. Docker daemon running
    2. Pre-built language images (python:3.11-slim, node:18-slim, etc.)
    3. Resource limits via Docker API
    4. Network isolation
    5. Temporary filesystem mounts
    6. Automatic container cleanup

    TODO: Implement when deploying to production.
    """

    def __init__(self, docker_host: str = 'unix:///var/run/docker.sock'):
        self.docker_host = docker_host

    def execute(
        self,
        code: str,
        language: str,
        config: Optional[SandboxConfig] = None,
        stdin: str = '',
    ) -> ExecutionResult:
        raise NotImplementedError(
            'DockerSandbox is not yet implemented. '
            'Use DevelopmentSandbox for local development.'
        )

    def run_tests(
        self,
        code: str,
        language: str,
        test_cases: list[dict],
        config: Optional[SandboxConfig] = None,
    ) -> list[TestResult]:
        raise NotImplementedError(
            'DockerSandbox is not yet implemented. '
            'Use DevelopmentSandbox for local development.'
        )

    def health_check(self) -> bool:
        # TODO: Check Docker daemon availability
        return False


# ─── Service Registry ────────────────────────────────────────────────────────

_sandbox: Optional[SandboxService] = None


def get_sandbox() -> SandboxService:
    """
    Get the configured sandbox service.

    Resolution order:
    - SANDBOX_SERVICE setting ('django.conf.settings.DEV_SANDBOX_ENABLED=False
      forces the simulated DevelopmentSandbox).
    - By default a real SubprocessPythonSandbox (isolated process, timeout,
      output caps) so that Run/Submit genuinely execute and grade code.
    """
    global _sandbox
    if _sandbox is None:
        from django.conf import settings
        if getattr(settings, 'DEV_SANDBOX_ENABLED', True):
            _sandbox = SubprocessPythonSandbox(
                python_exe=getattr(settings, 'SANDBOX_PYTHON_EXE', None) or sys.executable,
                config=SandboxConfig(
                    timeout_seconds=getattr(settings, 'SANDBOX_TIMEOUT_SECONDS', 10.0),
                    max_output_bytes=getattr(settings, 'SANDBOX_MAX_OUTPUT_BYTES', 100_000),
                ),
            )
        else:
            _sandbox = DevelopmentSandbox()
    return _sandbox


def configure_sandbox(sandbox: SandboxService) -> None:
    """Configure the sandbox service to use."""
    global _sandbox
    _sandbox = sandbox


def validate_submission(
    exercise,
    code: str,
    selected_answer=None,
) -> ValidationResult:
    """
    High-level validation function called by the API. Single source of truth.
    Routes to the appropriate validation strategy based on exercise type.

    Server-side gradeable types (no evaluator needed):
        multiple_choice, multiple_select, output_prediction,
        fill_blank (compared against solution_code)

    Code/debugging exercises are executed and graded against test cases in
    the configured sandbox. When no real evaluator is connected, submissions
    are recorded with an honest pending result — never a fake pass.
    """
    exercise_type = exercise.exercise_type

    if exercise_type in ('multiple_choice', 'multiple_select'):
        result = _validate_choice(exercise, selected_answer)
    elif exercise_type == 'output_prediction':
        # The client may send the predicted text either as selected_answer
        # or as the submitted code string — accept both.
        answer = selected_answer if selected_answer not in (None, '') else code
        result = _validate_output_prediction(exercise, answer)
    elif exercise_type == 'fill_blank':
        result = _validate_against_solution(exercise, code)
    elif exercise_type in ('code', 'debugging'):
        result = _validate_code_exercise(exercise, code)
    else:
        return ValidationResult(
            all_passed=False,
            status='error',
            feedback='Unknown exercise type.',
        )

    # Explanations are only revealed once the learner has submitted an attempt.
    if exercise.explain:
        result.explain = exercise.explain
    return result


def _validate_choice(exercise, selected_answer) -> ValidationResult:
    """Validate MCQ/MSQ exercises."""
    if not selected_answer:
        return ValidationResult(
            all_passed=False,
            feedback='Please select an answer.',
        )

    correct_ids = [c['id'] for c in exercise.choices if c.get('is_correct')]

    if exercise.exercise_type == 'multiple_choice':
        passed = selected_answer in correct_ids
    else:
        if isinstance(selected_answer, list):
            passed = set(selected_answer) == set(correct_ids)
        else:
            passed = selected_answer in correct_ids

    if passed:
        return ValidationResult(
            all_passed=True,
            status='correct',
            feedback='Correct! Well done.',
            xp_earned=exercise.xp_reward,
        )
    else:
        return ValidationResult(
            all_passed=False,
            status='incorrect',
            feedback='Not quite. Review the concept and try again.',
            correct_answer=correct_ids,
        )


def _validate_output_prediction(exercise, selected_answer) -> ValidationResult:
    """Validate output prediction exercises."""
    if not selected_answer:
        return ValidationResult(
            all_passed=False,
            feedback='Please predict the output.',
        )

    passed = str(selected_answer).strip() == exercise.expected_output.strip()
    if passed:
        return ValidationResult(
            all_passed=True,
            status='correct',
            feedback='Correct! You predicted the output accurately.',
            xp_earned=exercise.xp_reward,
        )
    else:
        return ValidationResult(
            all_passed=False,
            status='incorrect',
            feedback='Not quite. Trace through the code step by step.',
            correct_answer=exercise.expected_output,
        )


def _normalize_code(code: str) -> str:
    """Normalize source for solution comparison: drop comments/blank lines/whitespace."""
    lines = []
    for line in code.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if '#' in stripped:  # drop trailing inline comment
            stripped = stripped.split('#', 1)[0].rstrip()
        lines.append(''.join(stripped.split()))
    return '\n'.join(lines)


def _pending_evaluation(exercise, code) -> ValidationResult:
    """
    Honest result when no automated evaluator (sandbox) is available.
    The submission is recorded, but never reported as passed.
    """
    return ValidationResult(
        all_passed=False,
        status='pending',
        test_results=[
            {'test': 1, 'status': 'pending', 'message': 'Automated evaluation not yet available.'}
        ],
        feedback=(
            'Your submission has been saved. Automated evaluation of runnable '
            'code is not available yet, so we cannot confirm correctness.'
        ),
        xp_earned=0,
    )


def _validate_against_solution(exercise, code) -> ValidationResult:
    """
    Validate debugging/fill-blank exercises without an evaluator by comparing
    the submitted source against the authored solution (whitespace-, comment-
    and blank-line-insensitive). If no solution exists, return an honest
    pending result instead of a fake pass.
    """
    if not code or not code.strip():
        return ValidationResult(
            all_passed=False,
            status='incorrect',
            feedback='Please submit your answer first.',
        )

    if not exercise.solution_code.strip():
        return _pending_evaluation(exercise, code)

    if _normalize_code(code) == _normalize_code(exercise.solution_code):
        return ValidationResult(
            all_passed=True,
            status='correct',
            feedback='Correct! Your fix matches the expected solution.',
            xp_earned=exercise.xp_reward,
        )

    return ValidationResult(
        all_passed=False,
        status='incorrect',
        feedback='Not quite. Re-read the error and check the line you fixed.',
    )


def _validate_code_exercise(exercise, code) -> ValidationResult:
    """
    Validate code exercises using the sandbox service.
    A submission is only reported as passed when the sandbox confirms it.
    """
    if not code or code.strip() == exercise.starter_code.strip():
        return ValidationResult(
            all_passed=False,
            status='incorrect',
            feedback='It looks like you haven\'t made any changes yet. Try writing your solution.',
        )

    sandbox = get_sandbox()
    test_cases = list(exercise.test_cases or [])
    if not test_cases and exercise.expected_output:
        test_cases = [{'input': '', 'expected_output': exercise.expected_output}]

    # Without anything to grade against, we cannot confirm correctness.
    # If an authored solution exists, fall back to honest solution
    # comparison (this is how debugging/fill-blank style exercises are
    # graded when no runnable tests are defined). Otherwise record the
    # submission as an honest pending result — never a fake pass.
    if not test_cases:
        if exercise.solution_code.strip():
            return _validate_against_solution(exercise, code)
        return _pending_evaluation(exercise, code)

    # A real evaluator is required to execute runnable tests.
    if isinstance(sandbox, DevelopmentSandbox):
        return _pending_evaluation(exercise, code)

    # Non-Python exercises cannot be executed by the current sandbox; fall
    # back to solution comparison when an authored solution exists.
    if exercise.language != 'python':
        if exercise.solution_code.strip() and _normalize_code(code) == _normalize_code(exercise.solution_code):
            return ValidationResult(
                all_passed=True,
                status='correct',
                feedback='Correct! Your answer matches the expected solution.',
                xp_earned=exercise.xp_reward,
            )
        return _pending_evaluation(exercise, code)

    # Run tests through the real sandbox
    test_results = sandbox.run_tests(
        code=code,
        language=exercise.language,
        test_cases=test_cases,
    )

    all_passed = bool(test_results) and all(tr.status == 'passed' for tr in test_results)

    if all_passed:
        n = len(test_results)
        feedback = f'All {n} test{"es" if n != 1 else ""} passed. Great work.'
    else:
        # First failing test gives specific, honest feedback
        failure = next((tr for tr in test_results if tr.status != 'passed'), None)
        if failure is not None:
            if failure.status == 'error':
                feedback = f'Your program raised an error on test {failure.test_number}: {failure.message}'
            else:
                feedback = (
                    f'Test {failure.test_number} of {len(test_results)} failed. '
                    f'Expected output: {failure.expected!r} — your output: {failure.actual!r}'
                )
        else:
            feedback = 'No runnable test cases are defined for this exercise yet.'

    return ValidationResult(
        all_passed=all_passed,
        status='correct' if all_passed else 'incorrect',
        test_results=[
            {'test': tr.test_number, 'status': tr.status, 'message': tr.message}
            for tr in test_results
        ],
        feedback=feedback,
        xp_earned=exercise.xp_reward if all_passed else 0,
    )
