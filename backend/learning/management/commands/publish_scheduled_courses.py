"""Apply scheduled course publications that are due.

Run from cron / a scheduled task, e.g. every 10 minutes:

    python manage.py publish_scheduled_courses

The studio lets an administrator name a future publication time, and the promise is
only kept if something actually flips the switch. Publication here goes through the
same ``publishing.run_publish_check`` the manual Publish button uses, so a course that
was valid at scheduling time but has since been emptied of lessons stays in draft
instead of publishing itself unattended at 02:00.

The command is idempotent: it only selects rows that are due, unpublished and not
archived, so re-running it changes nothing.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from learning.models import Course, record_admin_action
from learning.services import publishing


class Command(BaseCommand):
    help = 'Publish courses whose scheduled publish_at time has arrived.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Report which courses are due without publishing any of them.',
        )

    def handle(self, *args, **options):
        now = timezone.now()
        due = Course.objects.filter(
            publish_at__isnull=False, publish_at__lte=now, is_published=False,
            archived_at__isnull=True,
        ).select_related('track')

        if not due.exists():
            self.stdout.write('No courses are due for scheduled publication.')
            return

        published, blocked = 0, 0
        for course in due:
            report = publishing.run_publish_check(course)
            if options['dry_run']:
                self.stdout.write(f'[dry-run] would publish "{course.title}"')
                continue
            if not report['ok']:
                # Leaving publish_at in place keeps the course visible in the studio's
                # scheduled list, so the administrator sees it is stuck and why.
                blocked += 1
                self.stderr.write(
                    f'Skipped "{course.title}": {len(report["blocking"])} blocking '
                    f'issue(s): {", ".join(i["code"] for i in report["blocking"])}'
                )
                continue
            course.is_published = True
            course.is_active = True
            course.published_at = now
            course.publish_at = None
            course.save(update_fields=[
                'is_published', 'is_active', 'published_at', 'publish_at', 'updated_at',
            ])
            record_admin_action(
                None, 'course.scheduled_publish', obj=course, label=course.title,
                detail={'scheduled_for': now.isoformat(), 'warning_codes': [
                    i['code'] for i in report['warnings']
                ]},
            )
            published += 1
            self.stdout.write(f'Published "{course.title}".')

        if not options['dry_run']:
            self.stdout.write(f'{published} published, {blocked} blocked by validation.')
