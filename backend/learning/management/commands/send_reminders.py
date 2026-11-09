"""Send idempotent competition deadline reminders.

Run this command periodically (hourly is recommended). The time windows are
deliberately wider than the schedule interval, while event-derived dedupe keys
ensure that each learner receives each reminder only once.
"""

from datetime import timedelta, timezone as datetime_timezone

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from learning.models import Competition, CompetitionRegistration, UserNotification
from learning.services.notifications import format_event_dt, notify


class Command(BaseCommand):
    help = (
        'Send competition reminders for registration closing (48h), the '
        'competition starting (24h), and submission deadlines (24h).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--now',
            help=(
                'Evaluate deadlines from this ISO-8601 timestamp instead of '
                'the current time (useful for deterministic operations/tests).'
            ),
        )

    def handle(self, *args, **options):
        now = self._resolve_now(options.get('now'))
        processed = 0
        processed += self._registration_closing(now)
        processed += self._starting_soon(now)
        processed += self._submission_closing(now)
        self.stdout.write(
            self.style.SUCCESS(f'Processed {processed} competition reminder recipient(s).')
        )

    @staticmethod
    def _resolve_now(value):
        if not value:
            return timezone.now()
        parsed = parse_datetime(value)
        if parsed is None:
            raise CommandError('--now must be a valid ISO-8601 date and time.')
        if timezone.is_naive(parsed):
            parsed = timezone.make_aware(parsed, datetime_timezone.utc)
        return parsed

    @staticmethod
    def _competitions(**filters):
        # ``is_archived`` is this model's cancelled/retired state. Draft,
        # archived and already-expired competitions never produce reminders.
        return Competition.objects.filter(
            is_published=True,
            is_archived=False,
            **filters,
        ).order_by('pk')

    def _registration_closing(self, now):
        competitions = self._competitions(
            registration_start__lte=now,
            registration_deadline__gt=now,
            registration_deadline__lte=now + timedelta(hours=48),
        )
        User = get_user_model()
        count = 0
        for competition in competitions.iterator():
            registered_ids = competition.registrations.values_list('user_id', flat=True)
            recipients = User.objects.filter(
                is_active=True,
                profile__email_verified=True,
            ).exclude(pk__in=registered_ids).exclude(pk=competition.organizer_id)
            deadline = format_event_dt(competition.registration_deadline)
            for user in recipients.iterator():
                self._notify(
                    user,
                    competition,
                    kind='registration-close',
                    title=f'Registration closes soon: {competition.title}',
                    body=f'Registration closes on {deadline}. Apply before the deadline.',
                    subject=f'Registration closes soon — {competition.title}',
                    preheader=f'Registration for {competition.title} closes within 48 hours.',
                    info_rows=[
                        ('Competition', competition.title),
                        ('Registration closes', deadline),
                    ],
                )
                count += 1
        return count

    def _starting_soon(self, now):
        competitions = self._competitions(
            competition_start__gt=now,
            competition_start__lte=now + timedelta(hours=24),
            submission_deadline__gt=now,
        )
        count = 0
        for competition in competitions.iterator():
            starts = format_event_dt(competition.competition_start)
            for registration in self._active_registrations(competition):
                self._notify(
                    registration.user,
                    competition,
                    kind='start-soon',
                    title=f'{competition.title} starts soon',
                    body=f'The competition starts on {starts}. Get ready to build.',
                    subject=f'Starts soon — {competition.title}',
                    preheader=f'{competition.title} starts within 24 hours.',
                    info_rows=[
                        ('Competition', competition.title),
                        ('Starts', starts),
                    ],
                )
                count += 1
        return count

    def _submission_closing(self, now):
        competitions = self._competitions(
            competition_start__lte=now,
            submission_deadline__gt=now,
            submission_deadline__lte=now + timedelta(hours=24),
        )
        count = 0
        for competition in competitions.iterator():
            deadline = format_event_dt(competition.submission_deadline)
            for registration in self._active_registrations(competition):
                self._notify(
                    registration.user,
                    competition,
                    kind='submission-deadline',
                    title=f'Submission deadline: {competition.title}',
                    body=f'Your submission is due by {deadline}. Submit before time runs out.',
                    subject=f'Submission deadline approaching — {competition.title}',
                    preheader=f'Submissions for {competition.title} close within 24 hours.',
                    info_rows=[
                        ('Competition', competition.title),
                        ('Submission deadline', deadline),
                    ],
                )
                count += 1
        return count

    @staticmethod
    def _active_registrations(competition):
        return CompetitionRegistration.objects.filter(
            competition=competition,
            registration_status__in=('registered', 'approved'),
            user__is_active=True,
        ).select_related('user').order_by('pk').iterator()

    @staticmethod
    def _notify(user, competition, *, kind, title, body, subject, preheader, info_rows):
        key = f'reminder:{kind}:{competition.pk}:{user.pk}'
        link = f'/competitions/{competition.slug}'
        notify(
            user,
            type=UserNotification.Type.COMPETITION_REMINDER,
            title=title,
            body=body,
            link=link,
            dedupe_key=key,
            related_object_type='competition',
            related_object_id=str(competition.pk),
            email_subject=subject,
            email_context={
                'heading': title,
                'message': body,
                'preheader': preheader,
                'cta_url': f'{settings.FRONTEND_URL}{link}',
                'cta_label': 'View competition',
                'info_rows': info_rows,
            },
            email_key=key,
        )
