"""
Seed command for Real World Projects — idempotent upsert.

Usage:
    python manage.py seed_projects

Creates or updates three portfolio-grade projects that a learner can actually
build end to end. Every milestone states a concrete deliverable and how to
prove it is finished ("Done when ..."), so the checklist is verifiable instead
of aspirational. Nothing is fabricated: each project maps to a real career
track, uses mainstream tooling, and produces an artifact the learner can show.

Re-running the command updates titles, descriptions, and milestones in place;
milestones beyond the current spec are removed (they carry no learner data).
"""

from django.core.management.base import BaseCommand

from learning.models import CareerTrack, Project, ProjectMilestone

PROJECT_FIELDS = (
    'title', 'description', 'difficulty', 'technologies',
    'estimated_hours', 'thumbnail',
)

# Used only when the track does not exist yet, so this command can run on a
# fresh database without depending on the course seeders.
TRACK_FALLBACKS = {
    'python': {
        'title': 'Python',
        'description': 'Master Python from fundamentals to advanced concepts.',
        'difficulty': 'beginner', 'estimated_hours': 40, 'order': 1,
    },
    'web': {
        'title': 'Web Development',
        'description': 'Build accessible interfaces and full-stack web applications.',
        'difficulty': 'beginner', 'estimated_hours': 40, 'order': 3,
    },
    'developer-tools': {
        'title': 'Developer Tools',
        'description': 'The everyday tools of real software work: version control and collaboration.',
        'difficulty': 'beginner', 'estimated_hours': 6, 'order': 2,
    },
}

PROJECT_SPECS = [
    {
        'slug': 'expense-tracker-api',
        'track_slug': 'python',
        'title': 'Expense Tracker API',
        'description': (
            'Build a production-shaped REST API for personal expenses with Django REST '
            'Framework: typed models, owner-scoped endpoints, real validation, an automated '
            'test suite, and a container image that runs the same way on every machine. '
            'This is the backend most portfolio dashboards are missing.'
        ),
        'difficulty': 'intermediate',
        'technologies': [
            'Python', 'Django', 'Django REST Framework', 'PostgreSQL',
            'pytest', 'Docker',
        ],
        'estimated_hours': 12,
        'thumbnail': '',
        'milestones': [
            (
                'Model the domain',
                'Create Expense and Category models with a Decimal amount, ISO currency code, '
                'spent_on date, and a category owned by a user. Add database constraints so '
                'amount must be positive and category names are unique per user. '
                'Done when migrations apply cleanly and both models are usable in Django admin.',
            ),
            (
                'Expose CRUD endpoints',
                'Implement a DRF ViewSet for expenses with pagination (20 per page) and filters '
                'for category and an inclusive date range. Return field-level 400 errors for bad '
                'input instead of 500s. Done when GET, POST, PATCH, and DELETE all round-trip '
                'through the browsable API and invalid payloads are rejected with field errors.',
            ),
            (
                'Scope everything to the owner',
                'Add token authentication and filter every queryset by request.user. Writes must '
                'ignore any client-supplied owner field. Done when a test signs in as a second user '
                'and gets 404 for another user\'s expense, and POST cannot reassign ownership.',
            ),
            (
                'Validate money correctly',
                'Validate amounts to two decimal places, reject zero/negative values and future '
                'spend dates, and normalise currency to uppercase ISO codes. Done when tests cover '
                'each rule and the serializer never silently rounds a value.',
            ),
            (
                'Write the automated test suite',
                'Use pytest-django to cover the happy path, authentication isolation, filtering, '
                'and validation edge cases. Run it with one command. Done when CI locally reports '
                'all tests green and the view/serializer modules are covered by real assertions.',
            ),
            (
                'Ship it like a service',
                'Add a multi-stage Dockerfile, a .env.example, and CI that runs migrations plus the '
                'test suite. Document the API with copy-paste curl examples in the README. '
                'Done when a fresh clone runs tests in CI and the container starts with `docker run`.',
            ),
        ],
    },
    {
        'slug': 'budget-dashboard',
        'track_slug': 'web',
        'title': 'Budget Dashboard',
        'description': (
            'Turn the Expense Tracker API into a typed, accessible dashboard in Next.js and '
            'TypeScript. You will handle loading and error states honestly, keep filters in the '
            'URL so views are shareable, and render charts that people can actually read — '
            'including screen-reader users.'
        ),
        'difficulty': 'intermediate',
        'technologies': [
            'TypeScript', 'Next.js', 'React', 'Tailwind CSS', 'REST APIs',
        ],
        'estimated_hours': 16,
        'thumbnail': '',
        'milestones': [
            (
                'Type the data contract',
                'Write a small API client with TypeScript types for every response and map HTTP '
                'failures to typed errors. Show a skeleton while loading and a retry action when '
                'the request fails. Done when no screen ever flashes fake numbers or an empty '
                'chart while data is still loading.',
            ),
            (
                'Build the monthly summary',
                'Render the current month total and a per-category breakdown. Format every amount '
                'with Intl.NumberFormat using the expense currency, never a hardcoded symbol. '
                'Done when totals match the API exactly and the empty month shows a clear message.',
            ),
            (
                'Add shareable filters',
                'Store the date range and category in the URL query string so a copied link opens '
                'the same view. Keep the filter controls keyboard accessible with visible focus. '
                'Done when reloading or pasting the URL reproduces the filtered result.',
            ),
            (
                'Make the charts honest',
                'One chart answers one question (spend over time) with labelled axes and an aria '
                'summary, plus a plain table fallback. No decorative data points and no animation '
                'that hides values. Done when the chart and the table always show identical numbers.',
            ),
            (
                'Harden the client',
                'Handle 401 by prompting sign-in, render a not-found state for unknown routes, '
                'and fix every console warning. Done when the browser console is clean on the '
                'summary, filter, and error paths.',
            ),
            (
                'Publish a deployable build',
                'Configure the API base URL through an environment variable, run the production '
                'build locally, and document screenshots plus setup steps in the README. '
                'Done when `npm run build` succeeds and a deployed preview talks to the live API.',
            ),
        ],
    },
    {
        'slug': 'ci-release-pipeline',
        'track_slug': 'developer-tools',
        'title': 'CI Pipeline & Release Automation',
        'description': (
            'The project that proves you can be trusted with a shared repository: a GitHub '
            'Actions pipeline that lints, tests, builds a container, and publishes versioned '
            'releases from tags — with least-privilege tokens and a runbook for when it breaks.'
        ),
        'difficulty': 'advanced',
        'technologies': [
            'Git', 'GitHub Actions', 'Docker', 'Bash', 'Python',
        ],
        'estimated_hours': 10,
        'thumbnail': '',
        'milestones': [
            (
                'Set repo hygiene rules',
                'Add .gitignore, .editorconfig, and a protected main branch. Adopt conventional '
                'commit messages so the history can be turned into release notes. Done when a '
                'direct push to main is blocked and commits follow the convention.',
            ),
            (
                'Automate the checks',
                'Create a workflow that runs formatting, linting, and the test suite on every push '
                'and pull request with dependency caching. Cancel superseded runs per branch. '
                'Done when a deliberately broken commit fails CI with a readable error.',
            ),
            (
                'Build a production container',
                'Write a multi-stage Dockerfile that runs as a non-root user, excludes dev '
                'dependencies, and publishes the image to the registry on version tags. '
                'Done when the tag build produces a runnable image with a small, audited layer set.',
            ),
            (
                'Automate releases',
                'On a v* tag, generate a changelog from commits and create a GitHub release that '
                'links the published image. Done when pushing a tag creates the release without '
                'any manual step.',
            ),
            (
                'Lock down secrets and permissions',
                'Grant workflows only the token scopes they need, use repository secrets or OIDC '
                'instead of long-lived keys, and ensure no secret can be printed in logs. '
                'Done when a permissions review of every workflow file finds nothing broader than required.',
            ),
            (
                'Write the runbook',
                'Document triage for a red pipeline, how to re-run a job safely, and rollback steps '
                'for a bad image. Include the exact commands. Done when a teammate who has never '
                'seen the repo can follow the runbook to recover a failed release.',
            ),
        ],
    },
]


class Command(BaseCommand):
    help = 'Create or update the Real World Projects library (idempotent).'

    def handle(self, *args, **options):
        for spec in PROJECT_SPECS:
            track = CareerTrack.objects.filter(slug=spec['track_slug']).first()
            if track is None:
                track, _ = CareerTrack.objects.get_or_create(
                    slug=spec['track_slug'],
                    defaults=TRACK_FALLBACKS[spec['track_slug']],
                )

            project, created = Project.objects.update_or_create(
                slug=spec['slug'],
                defaults={
                    **{f: spec[f] for f in PROJECT_FIELDS},
                    'track': track,
                    'is_active': True,
                },
            )

            self._sync_milestones(project, spec['milestones'])

            action = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(
                f"  {action} {project.title}: {project.milestones.count()} milestones "
                f"({project.difficulty}, ~{project.estimated_hours}h)"
            ))

        self.stdout.write(self.style.SUCCESS(
            f'Done. {Project.objects.filter(is_active=True).count()} active projects.'
        ))

    def _sync_milestones(self, project, milestones):
        """Upsert milestones by order and drop the surplus from earlier specs."""
        for order, (title, description) in enumerate(milestones, start=1):
            ProjectMilestone.objects.update_or_create(
                project=project,
                order=order,
                defaults={'title': title, 'description': description},
            )
        project.milestones.filter(order__gt=len(milestones)).delete()
