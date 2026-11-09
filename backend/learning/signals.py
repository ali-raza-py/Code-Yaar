"""Organizer-side competition events, wired as model signals.

Competition administration lives in the Django admin (registration approvals,
submission reviews, result publication, manual team invitations), so the
notifications are attached to the state transitions themselves: whichever
surface makes the change, the participant hears about it through the same
single notification path.

Every handler:
- fires only on a genuine transition (old status != new status, captured from
  the database in ``pre_save``), so re-saving an unchanged row is silent;
- is idempotent (event-derived ``dedupe_key``), so replays cannot re-notify;
- is best-effort — a notification failure never blocks the organizer's save.
"""

import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import (
    CompetitionRegistration,
    CompetitionResult,
    CompetitionSubmission,
    CompetitionTeamMember,
)
from .services.notifications import format_event_dt, notify

logger = logging.getLogger(__name__)

REVIEW_STATUS_META = {
    ('accepted', 'Submission accepted',
     'Your submission was accepted by the organizers. Nicely done — results '
     'follow as announced.'),
    ('needs_revision', 'Revision requested',
     'The organizers reviewed your submission and asked for changes. Update '
     'and resend before the deadline.'),
    ('rejected', 'Submission not accepted',
     'Your submission was not accepted this time. Feedback can come with '
     'the review; your other work is unaffected.'),
}


def _competition_of(obj):
    """Resolve the competition row either directly or through a related chain."""
    if hasattr(obj, 'competition') and getattr(obj, 'competition_id', None):
        return obj.competition
    registration = getattr(obj, 'registration', None)
    if registration is not None:
        return registration.competition
    team = getattr(obj, 'team', None)
    if team is not None:
        return team.competition
    return None


@receiver(pre_save, sender=CompetitionRegistration,
          dispatch_uid='learning.notifs.reg_pre')
def _remember_registration_status(instance, **_kwargs):
    instance._previous_status = None
    if instance.pk:
        prev = CompetitionRegistration.objects.filter(pk=instance.pk).only(
            'registration_status'
        ).first()
        if prev is not None:
            instance._previous_status = prev.registration_status


@receiver(post_save, sender=CompetitionRegistration,
          dispatch_uid='learning.notifs.reg_post')
def _registration_status_changed(instance, created, **_kwargs):
    previous = getattr(instance, '_previous_status', None)
    new = instance.registration_status
    if created or previous is None or previous == new:
        return
    if previous == 'approved' and new == 'approved':
        return
    if getattr(instance, '_notification_handled', False):
        # The admin review endpoint owns this decision: it sends a richer
        # notification (reference number, chosen status) right after saving,
        # so reacting here too would mail the applicant twice for one verdict.
        return

    competition = instance.competition
    user = instance.user
    if user is None or competition is None:
        return
    if new == 'approved':
        notify(
            user,
            type='competition_approved',
            title=f'Registration approved: {competition.title}',
            body=(
                'The organizers approved your registration. Check the '
                'problem statement and dates so you are ready when it starts.'
            ),
            link=f'/competitions/{competition.slug}',
            related_object_type='competition',
            related_object_id=competition.slug,
            dedupe_key=f'comp-approved:{instance.pk}',
            email_subject=f'Registration approved — {competition.title}',
            email_context={
                'preheader': f'Your {competition.title} registration was approved.',
                'heading': 'Registration approved',
                'competition_title': competition.title,
                'message': (
                    'The organizers approved your registration for '
                    f'{competition.title}. You are in.'
                ),
                'cta_url': f"{_frontend()}/competitions/{competition.slug}",
                'cta_label': 'View competition',
                'info_rows': [
                    ['Competition', competition.title],
                    ['Starts', format_event_dt(competition.competition_start)],
                ],
            },
            email_key=f'comp-approved:{instance.pk}',
        )
    elif new == 'rejected':
        notify(
            user,
            type='competition_rejected',
            title=f'Registration not approved: {competition.title}',
            body=(
                'Your registration was not approved by the organizers. Your '
                'other competitions and progress are unaffected.'
            ),
            link='/competitions',
            related_object_type='competition',
            related_object_id=competition.slug,
            dedupe_key=f'comp-rejected:{instance.pk}',
            email_subject=f'Registration not approved — {competition.title}',
            email_context={
                'preheader': f'Update on your {competition.title} registration.',
                'heading': 'Registration not approved',
                'competition_title': competition.title,
                'message': (
                    f'Your registration for {competition.title} was not '
                    'approved by the organizers.'
                ),
                'cta_url': f"{_frontend()}/competitions",
                'cta_label': 'Browse competitions',
                'info_rows': [['Competition', competition.title]],
            },
            email_key=f'comp-rejected:{instance.pk}',
        )


@receiver(pre_save, sender=CompetitionSubmission,
          dispatch_uid='learning.notifs.sub_pre')
def _remember_submission_status(instance, **_kwargs):
    instance._previous_status = None
    if instance.pk:
        prev = CompetitionSubmission.objects.filter(pk=instance.pk).only(
            'status', 'organizer_feedback'
        ).first()
        if prev is not None:
            instance._previous_status = prev.status
            instance._previous_feedback = prev.organizer_feedback


@receiver(post_save, sender=CompetitionSubmission,
          dispatch_uid='learning.notifs.sub_post')
def _submission_reviewed(instance, created, **_kwargs):
    previous = getattr(instance, '_previous_status', None)
    new = instance.status
    if created or previous == new or new not in ('accepted', 'needs_revision', 'rejected'):
        return

    meta = REVIEW_STATUS_META[new]
    competition = _competition_of(instance)
    if competition is None:
        return
    feedback = (instance.organizer_feedback or '').strip()
    message = meta[2]
    if feedback:
        message = f'{message} Organizer feedback: {feedback}'

    notify(
        instance.registration.user,
        type='submission_reviewed',
        title=f'{meta[1]}: {competition.title}',
        body=message[:1200],
        link=f'/competitions/{competition.slug}',
        related_object_type='competition',
        related_object_id=str(instance.pk),
        dedupe_key=f'comp-review:{instance.pk}:{new}',
        email_subject=f'{meta[1]} — {competition.title}',
        email_context={
            'preheader': f'{meta[1]} for {competition.title}.',
            'heading': meta[1],
            'competition_title': competition.title,
            'message': message,
            'cta_url': f"{_frontend()}/competitions/{competition.slug}",
            'cta_label': 'View competition',
            'info_rows': [
                ['Competition', competition.title],
                ['Status', instance.get_status_display()],
            ],
        },
        email_key=f'comp-review:{instance.pk}:{new}',
    )


@receiver(post_save, sender=CompetitionTeamMember,
          dispatch_uid='learning.notifs.member_post')
def _team_invitation_sent(instance, created, **_kwargs):
    if not created or instance.invitation_status != 'pending':
        return
    team = instance.team
    user = instance.user
    if team is None or user is None or user.pk == team.leader.pk:
        return  # the leader's own auto-join is not an invitation
    competition = team.competition
    leader = team.leader
    invitee_name = (leader.get_full_name() or '').strip() or leader.username
    notify(
        user,
        type='team_invitation',
        title=f'Team invitation: {team.name}',
        body=(
            f'{invitee_name} invited you to join {team.name} for '
            f'{competition.title}. Coordinate with them before registering.'
        ),
        link=f'/competitions/{competition.slug}',
        related_object_type='competition',
        related_object_id=str(team.pk),
        dedupe_key=f'team-invite:{instance.pk}',
        email_subject=f'Team invitation: {team.name} — {competition.title}',
        email_context={
            'preheader': f'{invitee_name} invited you to {team.name}.',
            'heading': 'You are invited to join a team',
            'competition_title': competition.title,
            'invited_by_name': invitee_name,
            'team_name': team.name,
            'message': (
                f'{invitee_name} invited you to join {team.name} for '
                f'{competition.title}.'
            ),
            'cta_url': f"{_frontend()}/competitions/{competition.slug}",
            'cta_label': 'View competition',
            'info_rows': [
                ['Competition', competition.title],
                ['Team', team.name],
            ],
        },
        email_key=f'team-invite:{instance.pk}',
    )


@receiver(pre_save, sender=CompetitionResult,
          dispatch_uid='learning.notifs.result_pre')
def _remember_result_publication(instance, **_kwargs):
    instance._previous_published = None
    if instance.pk:
        prev = CompetitionResult.objects.filter(pk=instance.pk).only(
            'is_published'
        ).first()
        if prev is not None:
            instance._previous_published = prev.is_published


@receiver(post_save, sender=CompetitionResult,
          dispatch_uid='learning.notifs.result_post')
def _result_published(instance, created, **_kwargs):
    previous = getattr(instance, '_previous_published', None)
    # Fire only for a genuinely new publication: a fresh published row, or a
    # row flipping from unpublished to published. The dedupe key below keeps
    # even an accidental duplicate silent.
    if instance.is_published is not True or previous is True:
        return

    competition = instance.registration.competition
    user = instance.registration.user
    award = instance.award.strip()
    placement = f'rank {instance.rank}' + (f' — {award}' if award else '')
    notify(
        user,
        type='results_published',
        title=f'Results published: {competition.title}',
        body=(
            f'You finished {placement}. See the full leaderboard on the '
            'competition page.'
        ),
        link=f'/competitions/{competition.slug}',
        related_object_type='competition',
        related_object_id=competition.slug,
        dedupe_key=f'comp-result:{instance.pk}',
        email_subject=f'Results published — {competition.title}',
        email_context={
            'preheader': f'{competition.title} results are out — you placed {instance.rank}.',
            'heading': 'Results published',
            'competition_title': competition.title,
            'rank': instance.rank,
            'award': award,
            'message': (
                f'The results for {competition.title} have been published. '
                f'You finished rank {instance.rank}'
                + (f' and received: {award}.' if award else '.')
            ),
            'cta_url': f"{_frontend()}/competitions/{competition.slug}",
            'cta_label': 'See full results',
            'info_rows': [
                ['Competition', competition.title],
                ['Your rank', str(instance.rank)],
                ['Score', str(instance.final_score)],
                *( [['Award', award]] if award else [] ),
            ],
        },
        email_key=f'comp-result:{instance.pk}',
    )


def _frontend() -> str:
    from django.conf import settings
    return settings.FRONTEND_URL
