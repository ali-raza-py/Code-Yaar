"""Seed the badge registry into the database idempotently.

Definitions come from ``learning.badge_registry`` — the single source of
truth. Re-running creates zero duplicates and never touches a learner's
already-earned ``UserAchievement`` rows or their credential IDs.
"""

from django.core.management.base import BaseCommand

from learning.badge_registry import BADGES
from learning.models import Achievement


class Command(BaseCommand):
    help = 'Create or update Achievement rows from the centralized badge registry'

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for badge in BADGES:
            slug = badge['slug']
            defaults = {k: v for k, v in badge.items() if k != 'slug'}
            _obj, was_created = Achievement.objects.update_or_create(
                slug=slug, defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(
            f'Badges seeded: {created} created, {updated} updated, '
            f'{len(BADGES)} in registry.'
        ))
