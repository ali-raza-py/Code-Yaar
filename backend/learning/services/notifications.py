"""In-app notification writes, gated by the learner's saved preferences.

Notifications are only ever created here, in response to a server-verified
event, so no code path can announce something that did not really happen.
Each notification type maps to one of the account-level preference keys on
``UserProfile.notification_preferences``; when that preference is off the
notification is suppressed at the source rather than hidden in the client.
"""

from ..models import UserProfile, UserNotification

# Notification type -> the profile preference key that governs it.
_PREFERENCE_BY_TYPE = {
    UserNotification.Type.BADGE_UNLOCK: 'achievements',
    UserNotification.Type.STREAK_RECORD: 'streak_reminders',
    UserNotification.Type.TRACK_COMPLETE: 'learning_reminders',
    UserNotification.Type.XP_MILESTONE: 'achievements',
}


def create_notification(user, *, type, title, body='', link=''):
    """Create one notification unless the learner muted its category.

    Returns the ``UserNotification`` or ``None`` when muted. Never raises:
    a notification is a courtesy, not part of the award's integrity, so a
    failure here must not roll back the underlying achievement transaction.
    """
    pref_key = _PREFERENCE_BY_TYPE.get(type)
    profile = UserProfile.objects.filter(user=user).first()
    if pref_key and profile is not None and not profile.get_notification_preference(pref_key):
        return None
    return UserNotification.objects.create(
        user=user, type=type, title=title, body=body, link=link,
    )
