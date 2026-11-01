"""
Seed command for the Practice challenges — idempotent upsert.

Usage:
    python manage.py seed_challenges

Populates (or refreshes) the six standalone coding challenges from the
canonical catalog in ``learning.challenge_catalog``. Content is the single
source of truth; running this command again updates every field in place, so
editors can iterate on statements, starter code and test cases without
touching the database by hand.

Every reference solution shipped in the catalog is executed against both the
sample and hidden tests here, in the same sandbox the API uses, so the command
fails loudly if a challenge can no longer be genuinely solved and graded. This
keeps the promise that a "passed" submission is a result the server actually
computed — never a fabricated one.
"""

from django.core.management.base import BaseCommand

from learning.challenge_catalog import CHALLENGES
from learning.models import Challenge
from learning.services.sandbox import DevelopmentSandbox, get_sandbox

CHALLENGE_FIELDS = (
    'title', 'description', 'difficulty', 'topic', 'estimated_minutes',
    'languages',
    'starter_code', 'starter_code_cpp', 'solution_code', 'solution_code_cpp',
    'problem_statement', 'requirements', 'input_description',
    'output_description', 'constraints', 'examples', 'hints',
    'solution_explanation', 'time_complexity', 'space_complexity',
    'sample_tests', 'hidden_tests',
    'xp_reward', 'is_active',
)


class Command(BaseCommand):
    help = 'Create or update the six Practice coding challenges.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-solution-check',
            action='store_true',
            help='Do not execute reference solutions against the tests '
                 '(useful on a host with no code evaluator connected).',
        )

    def handle(self, *args, **options):
        for spec in CHALLENGES:
            fields = {name: spec[name] for name in CHALLENGE_FIELDS if name in spec}
            fields.setdefault('starter_code_cpp', '')
            fields.setdefault('solution_code_cpp', '')
            fields.setdefault('is_active', True)
            challenge, created = Challenge.objects.update_or_create(
                slug=spec['slug'], defaults=fields,
            )
            verb = 'Created' if created else 'Updated'
            self.stdout.write(f'{verb} challenge: {challenge.title} ({challenge.slug})')

        if options['skip_solution_check']:
            self.stdout.write(self.style.WARNING(
                'Skipped reference-solution verification.'
            ))
            return

        self._verify_solutions()

    def _verify_solutions(self):
        """Run every reference solution through the real sandbox."""
        sandbox = get_sandbox()
        if isinstance(sandbox, DevelopmentSandbox):
            self.stdout.write(self.style.WARNING(
                'No real evaluator connected (DevelopmentSandbox); skipping '
                'solution verification. Submissions will be graded once a '
                'sandbox is configured.'
            ))
            return

        failures = []
        for challenge in Challenge.objects.filter(
            slug__in=[c['slug'] for c in CHALLENGES]
        ):
            for label, tests in (('sample', challenge.sample_tests),
                                 ('hidden', challenge.hidden_tests)):
                if not tests:
                    continue
                results = sandbox.run_tests(
                    code=challenge.solution_for('python'),
                    language='python',
                    test_cases=tests,
                )
                bad = [r for r in results if r.status != 'passed']
                for r in bad:
                    failures.append(
                        f'{challenge.slug} [{label} test {r.test_number}]: '
                        f'expected {r.expected!r}, got {r.actual!r}'
                    )

        if failures:
            msg = 'Reference solution(s) do NOT pass their own tests:\n  - ' \
                  + '\n  - '.join(failures)
            raise SystemExit(self.style.ERROR(msg))

        self.stdout.write(self.style.SUCCESS(
            'All six reference solutions pass their sample and hidden tests.'
        ))
