"""
Language Adapter Architecture (spec §14)

Provides a pluggable interface for supporting multiple programming languages
in the exercise engine. Each language adapter handles:
- Code validation
- Output comparison
- Syntax checking
- Language-specific test execution

Usage:
    adapter = get_adapter('python')
    result = adapter.execute(code, test_cases)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExecutionResult:
    """Result of executing code in a sandbox."""
    status: str  # 'success', 'error', 'timeout'
    output: str = ''
    error: str = ''
    return_code: int = 0
    execution_time_ms: int = 0


@dataclass
class TestResult:
    """Result of a single test case."""
    test_number: int
    status: str  # 'passed', 'failed', 'error'
    expected: str = ''
    actual: str = ''
    message: str = ''


@dataclass
class ValidationResult:
    """Result of validating a submission against test cases."""
    all_passed: bool
    test_results: list = field(default_factory=list)
    feedback: str = ''
    xp_earned: int = 0


class LanguageAdapter(ABC):
    """Base class for language-specific adapters."""

    @property
    @abstractmethod
    def language_name(self) -> str:
        """Human-readable language name."""
        pass

    @property
    @abstractmethod
    def language_code(self) -> str:
        """Short code used in the database (e.g., 'python', 'javascript')."""
        pass

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Default file extension (e.g., '.py', '.js')."""
        pass

    @abstractmethod
    def get_default_starter_code(self) -> str:
        """Return default starter code template for this language."""
        pass

    @abstractmethod
    def wrap_for_execution(self, code: str) -> str:
        """
        Wrap user code for execution in the sandbox.
        May add imports, setup, or teardown as needed.
        """
        pass

    def format_error(self, raw_error: str) -> str:
        """
        Format a raw error message into a learner-friendly message.
        Override for language-specific error translation.
        """
        return raw_error


class PythonAdapter(LanguageAdapter):
    """Adapter for Python exercises."""

    @property
    def language_name(self) -> str:
        return 'Python'

    @property
    def language_code(self) -> str:
        return 'python'

    @property
    def file_extension(self) -> str:
        return '.py'

    def get_default_starter_code(self) -> str:
        return '# Write your code here\n'

    def wrap_for_execution(self, code: str) -> str:
        """
        Wrap Python code for safe execution.
        In production, the sandbox handles isolation.
        """
        return code

    def format_error(self, raw_error: str) -> str:
        """Translate common Python errors into learner-friendly messages."""
        error_map = {
            'IndentationError': 'Check your indentation. Python uses consistent spacing.',
            'SyntaxError': 'There\'s a syntax error in your code. Check for missing colons, parentheses, or quotes.',
            'NameError': 'You\'re using a variable that hasn\'t been defined yet.',
            'TypeError': 'You\'re trying to combine incompatible types. Check your variable types.',
            'IndexError': 'You\'re trying to access an index that doesn\'t exist. Check your list bounds.',
            'KeyError': 'The key you\'re looking for doesn\'t exist in the dictionary.',
            'ValueError': 'The value you provided is not valid for this operation.',
            'ZeroDivisionError': 'You\'re trying to divide by zero, which is not allowed.',
            'AttributeError': 'The object doesn\'t have the attribute or method you\'re trying to use.',
        }
        for error_type, friendly_msg in error_map.items():
            if error_type in raw_error:
                # Extract the specific line info
                lines = raw_error.strip().split('\n')
                detail = lines[-1] if lines else raw_error
                return f'{friendly_msg}\n\nDetails: {detail}'
        return raw_error


class JavaScriptAdapter(LanguageAdapter):
    """Adapter for JavaScript exercises."""

    @property
    def language_name(self) -> str:
        return 'JavaScript'

    @property
    def language_code(self) -> str:
        return 'javascript'

    @property
    def file_extension(self) -> str:
        return '.js'

    def get_default_starter_code(self) -> str:
        return '// Write your code here\n'

    def wrap_for_execution(self, code: str) -> str:
        return code

    def format_error(self, raw_error: str) -> str:
        error_map = {
            'SyntaxError': 'There\'s a syntax error. Check for missing semicolons, brackets, or parentheses.',
            'ReferenceError': 'You\'re using a variable that hasn\'t been declared.',
            'TypeError': 'You\'re trying to use a value in a way that doesn\'t match its type.',
        }
        for error_type, friendly_msg in error_map.items():
            if error_type in raw_error:
                return f'{friendly_msg}\n\nDetails: {raw_error}'
        return raw_error


class CppAdapter(LanguageAdapter):
    """Adapter for C++ exercises."""

    @property
    def language_name(self) -> str:
        return 'C++'

    @property
    def language_code(self) -> str:
        return 'cpp'

    @property
    def file_extension(self) -> str:
        return '.cpp'

    def get_default_starter_code(self) -> str:
        return '#include <iostream>\nusing namespace std;\n\nint main() {\n    // Write your code here\n    return 0;\n}\n'

    def wrap_for_execution(self, code: str) -> str:
        return code


# ─── Registry ────────────────────────────────────────────────────────────────

_ADAPTERS: dict[str, LanguageAdapter] = {}


def register_adapter(adapter: LanguageAdapter) -> None:
    """Register a language adapter."""
    _ADAPTERS[adapter.language_code] = adapter


def get_adapter(language_code: str) -> LanguageAdapter:
    """
    Get the language adapter for a given language code.
    Raises ValueError if the language is not supported.
    """
    if language_code not in _ADAPTERS:
        raise ValueError(
            f'Unsupported language: {language_code}. '
            f'Available: {", ".join(_ADAPTERS.keys())}'
        )
    return _ADAPTERS[language_code]


def get_supported_languages() -> list[str]:
    """Return list of supported language codes."""
    return list(_ADAPTERS.keys())


# Register built-in adapters
register_adapter(PythonAdapter())
register_adapter(JavaScriptAdapter())
register_adapter(CppAdapter())
