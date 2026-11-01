"""Check that every auto-graded curriculum exercise really grades correctly.

For each code/debugging exercise the authored `solution_code` must produce the
declared expected output in the real sandbox, and each multiple-choice item
must have exactly one correct option. If a solution does not pass its own test,
the exercise is broken and learners would be marked wrong for a right answer —
so this runs as part of the test suite, not just as a script.

Run directly:  python tools/verify_curriculum_solutions.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django  # noqa: E402

django.setup()

from django.test import SimpleTestCase  # noqa: E402

from learning.curriculum import CURRICULA  # noqa: E402
from learning.services.sandbox import SubprocessSandbox  # noqa: E402


def iter_exercises():
    """Walk the curriculum data straight from the source modules, no DB needed."""
    for curriculum in CURRICULA:
        for course in curriculum.COURSES:
            for chapter in course.get('chapters', []):
                for lesson in chapter.get('lessons', []):
                    for exercise in lesson.get('exercises', []):
                        yield course['slug'], lesson['slug'], exercise


class CurriculumSolutionTests(SimpleTestCase):
    """Every authored solution must pass its own tests in the real sandbox."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sandbox = SubprocessSandbox(config=None)

    def test_choice_exercises_have_exactly_the_right_answers(self):
        for course_slug, lesson_slug, ex in iter_exercises():
            kind = ex['exercise_type']
            if kind not in ('multiple_choice', 'multiple_select'):
                continue
            choices = ex.get('choices') or []
            correct = [c for c in choices if c.get('is_correct')]
            with self.subTest(exercise=ex['slug']):
                self.assertGreaterEqual(len(choices), 2, 'needs at least two options')
                if kind == 'multiple_choice':
                    self.assertEqual(len(correct), 1, 'exactly one correct option')
                else:
                    self.assertGreaterEqual(len(correct), 1, 'MSQ needs a correct option')
                    self.assertLess(len(correct), len(choices), 'MSQ needs a wrong option')
            _ = (course_slug, lesson_slug)

    def test_code_solutions_produce_the_declared_output(self):
        runnable = [
            ex for _, _, ex in iter_exercises()
            if ex['exercise_type'] in ('code', 'debugging')
            and ex.get('test_cases')
        ]
        self.assertTrue(runnable, 'no runnable code exercises found — did the curriculum load?')

        for ex in runnable:
            language = ex['language']
            if language == 'cpp' and not self.sandbox.cpp_available:
                continue
            solution = ex.get('solution_code')
            with self.subTest(exercise=ex['slug'], language=language):
                self.assertTrue(solution, f'{ex["slug"]} has test cases but no solution_code')
                results = self.sandbox.run_tests(solution, language, ex['test_cases'])
                failed = [r for r in results if r.status != 'passed']
                if failed:
                    detail = '; '.join(
                        f'test {r.test_number}: expected {r.expected!r} got {r.actual!r}'
                        for r in failed
                    )
                    self.fail(f'{ex["slug"]} solution does not pass its own tests -> {detail}')

    def test_starter_code_is_not_already_the_answer(self):
        for _, _, ex in iter_exercises():
            if ex['exercise_type'] not in ('code', 'debugging'):
                continue
            starter, solution = ex.get('starter_code', ''), ex.get('solution_code', '')
            with self.subTest(exercise=ex['slug']):
                self.assertNotEqual(
                    starter.strip(), solution.strip(),
                    'starter code must differ from the solution',
                )

    def test_every_item_cites_its_textbook_pages(self):
        for _, _, ex in iter_exercises():
            reference = ex.get('reference') or {}
            with self.subTest(exercise=ex['slug']):
                self.assertTrue(reference, 'exercise has no textbook reference')
                self.assertTrue(reference.get('textbook_pages'), 'reference needs page numbers')
                if reference.get('source_type') == 'official':
                    self.assertEqual(reference.get('verification_status'), 'verified')


if __name__ == '__main__':
    from unittest import TextTestRunner, TestLoader

    suite = TestLoader().loadTestsFromTestCase(CurriculumSolutionTests)
    sys.exit(0 if TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1)
