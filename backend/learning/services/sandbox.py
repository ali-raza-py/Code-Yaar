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
    Defaults to DevelopmentSandbox if not configured.
    """
    global _sandbox
    if _sandbox is None:
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
    High-level validation function called by the API.
    Routes to the appropriate validation strategy based on exercise type.
    """
    exercise_type = exercise.exercise_type
    language = exercise.language

    if exercise_type in ('multiple_choice', 'multiple_select'):
        return _validate_choice(exercise, selected_answer)
    elif exercise_type == 'output_prediction':
        return _validate_output_prediction(exercise, selected_answer)
    elif exercise_type in ('code', 'debugging', 'fill_blank'):
        return _validate_code_exercise(exercise, code)

    return ValidationResult(
        all_passed=False,
        feedback='Unknown exercise type.',
    )


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
            feedback='Correct! Well done.',
            xp_earned=exercise.xp_reward,
        )
    else:
        return ValidationResult(
            all_passed=False,
            feedback='Not quite. Review the concept and try again.',
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
            feedback='Correct! You predicted the output accurately.',
            xp_earned=exercise.xp_reward,
        )
    else:
        return ValidationResult(
            all_passed=False,
            feedback='Not quite. Trace through the code step by step.',
        )


def _validate_code_exercise(exercise, code) -> ValidationResult:
    """
    Validate code exercises using the sandbox service.
    """
    if not code or code.strip() == exercise.starter_code.strip():
        return ValidationResult(
            all_passed=False,
            feedback='It looks like you haven\'t made any changes yet. Try writing your solution.',
        )

    sandbox = get_sandbox()
    test_cases = exercise.test_cases or []

    if not test_cases:
        # No test cases defined — just check that code is non-trivial
        return ValidationResult(
            all_passed=True,
            test_results=[TestResult(test_number=1, status='passed', message='Code submitted.')],
            feedback='Code submitted successfully.',
            xp_earned=exercise.xp_reward,
        )

    # Run tests through sandbox
    test_results = sandbox.run_tests(
        code=code,
        language=exercise.language,
        test_cases=test_cases,
    )

    all_passed = all(tr.status == 'passed' for tr in test_results)
    passed_count = sum(1 for tr in test_results if tr.status == 'passed')

    feedback = ''
    if all_passed:
        feedback = f'Your solution passed all {len(test_results)} checks.'
    else:
        # Find the first failing test for specific feedback
        for tr in test_results:
            if tr.status != 'passed':
                feedback = f'Test {tr.test_number} failed. {tr.message}'
                break

    return ValidationResult(
        all_passed=all_passed,
        test_results=[
            {'test': tr.test_number, 'status': tr.status, 'message': tr.message}
            for tr in test_results
        ],
        feedback=feedback,
        xp_earned=exercise.xp_reward if all_passed else 0,
    )
