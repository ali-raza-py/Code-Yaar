"""Send daily or weekly notification digests selected by learners."""

from datetime import timedelta, timezone as datetime_timezone

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Subquery
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from learning.models import NotificationEmailLog, UserNotification, UserProfile
from learning.services.email_service import send_notification_email


class Command(BaseCommand):
    help = 'Send notification digests to users who selected daily or weekly delivery.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--frequency',
            choices=('daily', 'weekly'),
            default='daily',
            help='Digest cadence to process (default: daily).',
        )
        parser.add_argument(
            '--now',
            help='Use this ISO-8601 timestamp as the end of the digest period.',
        )

    def handle(self, *args, **options):
        frequency = options['frequency']
        now = self._resolve_now(options.get('now'))
        start = now - timedelta(days=1 if frequency == 'daily' else 7)
        sent = 0

        profiles = UserProfile.objects.filter(
            user__is_active=True,
            notification_preferences__email_digest=frequency,
        ).select_related('user').order_by('pk')

        for profile in profiles.iterator():
            user = profile.user
            if not user.email:
                continue
            notifications = self._notifications_for(user, start, now)
            if not notifications:
                continue

            notifications_url = f'{settings.FRONTEND_URL}/notifications'
            items = [
                {
                    'title': notification.title,
                    'body': notification.body,
                    'url': self._notification_url(notification, notifications_url),
                }
                for notification in notifications
            ]
            label = 'Daily digest' if frequency == 'daily' else 'Weekly digest'
            log = send_notification_email(
                user,
                template='digest',
                subject=f'Your Code Yaar {frequency} digest',
                context={
                    'heading': label,
                    'period_label': label,
                    'items': items,
                    'notifications_url': notifications_url,
                },
                email_key=(
                    f'digest:{frequency}:{user.pk}:'
                    f'{now.astimezone(datetime_timezone.utc).date().isoformat()}'
                ),
                kind='digest',
            )
            if log is not None:
                sent += 1

        self.stdout.write(
            self.style.SUCCESS(f'Queued or sent {sent} {frequency} digest(s).')
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
    def _notifications_for(user, start, end):
        # A queued individual email is excluded too: its on-commit callback may
        # still be pending, and including it would race two emails for one event.
        individually_emailed = NotificationEmailLog.objects.filter(
            user=user,
            notification_id__isnull=False,
            status__in=(
                NotificationEmailLog.Status.QUEUED,
                NotificationEmailLog.Status.SENT,
                NotificationEmailLog.Status.RENDER_ONLY,
            ),
        ).values('notification_id')
        return list(
            UserNotification.objects.filter(
                user=user,
                created_at__gte=start,
                created_at__lte=end,
            ).exclude(pk__in=Subquery(individually_emailed)).order_by('created_at', 'pk')
        )

    @staticmethod
    def _notification_url(notification, fallback):
        link = (notification.link or '').strip()
        if not link:
            return fallback
        if link.startswith(('https://', 'http://')):
            return link
        return f"{settings.FRONTEND_URL.rstrip('/')}/{link.lstrip('/')}"
