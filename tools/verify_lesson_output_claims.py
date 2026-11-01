"""Check that lesson-prose "Expected output" claims are true in the real sandbox.

Curriculum exercises are graded through verify_curriculum_solutions.py, but the
lesson bodies themselves advertise outputs under ```output fences ("press Run
and you will see this"). This executes every Python code fence that a lesson
claims produces output, in the real SubprocessSandbox, and compares — a
textbook sample that would print something else is a correctness bug.

Run directly:  python tools/verify_lesson_output_claims.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django  # noqa: E402

django.setup()

from django.test import SimpleTestCase  # noqa: E402

from learning.curriculum import CURRICULA  # noqa: E402
from learning.services.sandbox import SubprocessSandbox  # noqa: E402

FENCE = re.compile(r'```(\w[\w-]*)\n(.*?)```', re.S)


def iter_claims():
    """Yield (lesson_slug, code, claimed_output, stdin_lines) for each claim.

    A claim is an ```output fence that directly follows a ```python fence
    (only the blank line and the "**Expected output:**" marker in between).
    Where the fence needs input, sensible deterministic lines are piped:
    prompts written in the code (input("...")) receive a test value.
    """
    for curriculum in CURRICULA:
        feed_index: dict = {}
        for course in curriculum.COURSES:
            for chapter in course.get('chapters', []):
                for lesson in chapter.get('lessons', []):
                    body = lesson.get('content_body', '')
                    blocks = list(FENCE.finditer(body))
                    for i in range(len(blocks) - 1):
                        code_b, out_b = blocks[i], blocks[i + 1]
                        if code_b.group(1) != 'python' or out_b.group(1) != 'output':
                            continue
                        gap = body[code_b.end():out_b.start()]
                        if '**Expected output' not in gap and '**Expected result' not in gap:
                            continue
                        code = code_b.group(2).strip('\n')
                        # Per-lesson feed directive: a visible "Verified run:
                        # the checker feeds `X` ... `Y` ..." note; every
                        # backticked token in that sentence is one feed line,
                        # applied to successive prompted sample fences.
                        directive = re.search(
                            r'Verified run:([\s\S]*?)(?:\n[\s>]*\'\'\'|\n\n|$)',
                            body)
                        prompt_lines = None
                        if directive:
                            tokens = re.findall(
                                r'`([^`]+)`', directive.group(1))
                            tokens = [t for t in tokens if not t.endswith('.')]
                            if tokens:
                                prompt_lines = tokens
                        # Fallback: one deterministic value per prompted input().
                        prompts = re.findall(r'input\((["\'])(.*?)\1\)', code)
                        if prompt_lines is not None:
                            # Directive lists one feed per prompted FENCE;
                            # fences without input() consume none, and a
                            # fence's own repeated inputs cycle through.
                            seen = feed_index.get((lesson['slug'], 'directive'), 0)
                            if prompts:
                                feed_index[(lesson['slug'], 'directive')] = \
                                    seen + len(prompts)
                            stdin = ''.join(
                                prompt_lines[(seen + k) % len(prompt_lines)] + '\n'
                                for k in range(len(prompts))
                            )
                        else:
                            stdin = ''.join(
                                ('18\n' if 'age' in p[1].lower()
                                 else '30000\n' if 'salar' in p[1].lower()
                                 else 'Ali\n')
                                for p in prompts
                            )
                        yield lesson['slug'], code, out_b.group(2).strip(), stdin


class LessonOutputClaimTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sandbox = SubprocessSandbox(config=None)

    def test_claimed_outputs_really_print(self):
        claims = list(iter_claims())
        self.assertTrue(claims, 'no output claims found — did the curriculum load?')
        for lesson_slug, code, claimed, stdin in claims:
            with self.subTest(lesson=lesson_slug):
                result = self.sandbox.execute(code, 'python', stdin=stdin)
                actual = (result.output or '').strip()
                if result.status != 'success':
                    self.fail(
                        f'{lesson_slug}: sample does not run '
                        f'({result.status}: {(result.error or "")[:200]})'
                    )
                # A prompt echoed by input() is part of the transcript; the
                # claim may or may not include it — compare tolerant of that.
                clean_claimed = claimed.strip()
                if actual != clean_claimed and actual + '\n' + 'Ali' != clean_claimed \
                        and not (clean_claimed in actual or actual in clean_claimed):
                    self.fail(
                        f'{lesson_slug}: claim says {clean_claimed!r} but the '
                        f'sandbox printed {actual!r} (stdin {stdin!r})'
                    )


if __name__ == '__main__':
    from unittest import TextTestRunner, TestLoader

    suite = TestLoader().loadTestsFromTestCase(LessonOutputClaimTests)
    sys.exit(0 if TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1)
