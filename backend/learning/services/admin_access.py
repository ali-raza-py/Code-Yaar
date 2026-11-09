"""Administrative capability resolution for the Code Yaar admin platform.

``learning.services.auth.user_role()`` collapses every privileged account into one
of three strings (``administrator`` / ``instructor`` / ``student``). That is exactly
right for the learner-facing API, and it must not change: 76 auth tests and the
whole sign-in path depend on it. It is too coarse for the admin platform, where the
specification calls for nine distinct roles.

Rather than widening ``user_role()``, this module layers *capabilities* on top of it.
A capability is a narrow verb the API can check ("may publish a course", "may review
applications"), and a role is simply a bundle of capabilities resolved from Django
groups. Frontend navigation filtering is a UX affordance; every check here runs
server-side.

Two invariants worth stating because they are load-bearing:

* A legacy administrator who belongs to none of the specialised groups keeps broad
  access. Introducing roles must never silently downgrade somebody who can already
  run the platform.
* A leadership title (Hackathon Lead, Campus Ambassador, ...) is not a group in this
  matrix and grants nothing here. Student leadership is a public honour, not a
  technical privilege.
"""

from .auth import user_role

# ─── Capability names ──────────────────────────────────────────────────────────

ALL = '*'

COURSE_STUDIO_VIEW = 'course.studio.view'
COURSE_STUDIO_EDIT = 'course.studio.edit'
COURSE_PUBLISH = 'course.publish'
COURSE_ARCHIVE = 'course.archive'
CONTENT_EDIT = 'content.edit'
STUDENT_READ = 'student.read'
STUDENT_WRITE = 'student.write'
ENROLLMENT_READ = 'enrollment.read'
INSTRUCTOR_READ = 'instructor.read'
SUBMISSION_REVIEW = 'submission.review'
COMPETITION_MANAGE = 'competition.manage'
APPLICATION_REVIEW = 'application.review'
CAMPAIGN_MANAGE = 'campaign.manage'
ANNOUNCEMENT_MANAGE = 'announcement.manage'
PLATFORM_UPDATE_MANAGE = 'platform_update.manage'
CERTIFICATE_MANAGE = 'certificate.manage'
ACHIEVEMENT_MANAGE = 'achievement.manage'
LEADERSHIP_MANAGE = 'leadership.manage'
ANALYTICS_VIEW = 'analytics.view'
ANALYTICS_EXPORT = 'analytics.export'
AUDIT_VIEW = 'audit.view'
PLATFORM_CONFIG = 'platform.config'
ROLES_MANAGE = 'roles.manage'

CONTENT_CAPABILITIES = frozenset({
    COURSE_STUDIO_VIEW, COURSE_STUDIO_EDIT, COURSE_PUBLISH, COURSE_ARCHIVE,
    CONTENT_EDIT, ANALYTICS_VIEW, ANALYTICS_EXPORT,
})

# Django group names. Created by migration ``0031_admin_platform_groups`` so the
# mapping below has something real to resolve against in every environment.
GROUP_ACADEMIC_MANAGER = 'Academic Manager'
GROUP_COURSE_EDITOR = 'Course Editor'
GROUP_COMPETITION_MANAGER = 'Competition Manager'
GROUP_LEADERSHIP_MANAGER = 'Leadership Manager'
GROUP_COMMUNICATION_MANAGER = 'Communication Manager'
GROUP_STUDENT_SUPPORT = 'Student Support'

#: Spec role -> Django group -> capabilities. ``super_admin`` and
#: ``platform_administrator`` are resolved from flags rather than a group, and the
#: instructor row is reached through ``user_role()``.
ROLE_GROUPS = {
    'academic_manager': GROUP_ACADEMIC_MANAGER,
    'course_editor': GROUP_COURSE_EDITOR,
    'competition_manager': GROUP_COMPETITION_MANAGER,
    'leadership_manager': GROUP_LEADERSHIP_MANAGER,
    'communication_manager': GROUP_COMMUNICATION_MANAGER,
    'student_support': GROUP_STUDENT_SUPPORT,
}

ROLE_CAPABILITIES = {
    # Owns the whole academic surface: curriculum, people, analytics, audit.
    'academic_manager': CONTENT_CAPABILITIES | frozenset({
        STUDENT_READ, ENROLLMENT_READ, INSTRUCTOR_READ, SUBMISSION_REVIEW,
        ACHIEVEMENT_MANAGE, CERTIFICATE_MANAGE, AUDIT_VIEW,
    }),
    # Editorial hands only: builds courses and lessons, publishes nothing on its own
    # authority beyond the courses it is given, and sees no learner records.
    'course_editor': frozenset({
        COURSE_STUDIO_VIEW, COURSE_STUDIO_EDIT, CONTENT_EDIT, ANALYTICS_VIEW,
    }),
    'competition_manager': frozenset({
        COMPETITION_MANAGE, APPLICATION_REVIEW, STUDENT_READ,
        ANALYTICS_VIEW, ANALYTICS_EXPORT,
    }),
    # Phase 3 will add the leadership models; the capability exists now so the role
    # is provisionable without a second migration later.
    'leadership_manager': frozenset({
        LEADERSHIP_MANAGE, STUDENT_READ, COMPETITION_MANAGE, ANALYTICS_VIEW,
    }),
    'communication_manager': frozenset({
        CAMPAIGN_MANAGE, ANNOUNCEMENT_MANAGE, PLATFORM_UPDATE_MANAGE,
        STUDENT_READ, ANALYTICS_VIEW,
    }),
    # Reads enough to answer a support ticket and nothing more.
    'student_support': frozenset({
        STUDENT_READ, ENROLLMENT_READ, COURSE_STUDIO_VIEW, ANALYTICS_VIEW,
    }),
    # Scoped by object permissions (see ``ScopedCourseAccess``): an instructor only
    # reaches courses where ``Course.instructor_user`` is their own account.
    'instructor': frozenset({
        COURSE_STUDIO_VIEW, COURSE_STUDIO_EDIT, SUBMISSION_REVIEW, ANALYTICS_VIEW,
    }),
}

PLATFORM_ADMINISTRATOR_CAPABILITIES = frozenset({ALL})

SUPER_ADMIN_CAPABILITIES = frozenset({ALL})


def _group_names(user):
    if getattr(user, 'pk', None) is None:
        return set()
    return set(user.groups.values_list('name', flat=True))


def admin_roles(user):
    """Every spec role that applies to this account, most privileged first.

    Returning a list rather than a single string matters: a Course Editor who is
    also moved into Communication Manager should gain campaigns without losing the
    studio, and the roles page needs to show both.
    """
    if not getattr(user, 'is_authenticated', False):
        return []
    roles = []
    if user.is_superuser:
        roles.append('super_admin')
    role = user_role(user)
    if role == 'administrator' and not user.is_superuser:
        roles.append('platform_administrator')
    if role == 'instructor':
        roles.append('instructor')
    names = _group_names(user)
    for spec_role, group_name in ROLE_GROUPS.items():
        if group_name in names:
            roles.append(spec_role)
    return roles


def capabilities(user):
    """Resolve the capability set for a user, memoised per request-user object.

    Resolution order, most privileged first: super user, then the legacy
    administrator-with-no-group case, then group-scoped administrators, then
    instructors, then anybody else holding a specialised group.
    """
    if not getattr(user, 'is_authenticated', False):
        return frozenset()
    cached = getattr(user, '_admin_capabilities', None)
    if cached is not None:
        return cached

    # Answered before the group lookup: super users are the common admin-panel
    # account, and the m2M join costs a full network round trip on the
    # hosted database (~150 ms) that their capability set never consults.
    if user.is_superuser:
        user._admin_capabilities = SUPER_ADMIN_CAPABILITIES
        return SUPER_ADMIN_CAPABILITIES

    names = _group_names(user)
    grouped = frozenset().union(*(ROLE_CAPABILITIES[spec_role]
                                 for spec_role, group_name in ROLE_GROUPS.items()
                                 if group_name in names)) if names else frozenset()

    role = user_role(user)
    if role == 'administrator':
        # A legacy administrator with no specialised group keeps everything, so
        # rolling out roles never silently downgrades someone who can already run
        # the platform. Assigning any group scopes that account to that group.
        caps = grouped or PLATFORM_ADMINISTRATOR_CAPABILITIES
    elif role == 'instructor':
        caps = ROLE_CAPABILITIES['instructor'] | grouped
    else:
        # Students, including student leaders: a leadership title is not a group
        # in this matrix and therefore grants nothing.
        caps = grouped

    try:
        user._admin_capabilities = caps
    except (AttributeError, TypeError):
        pass
    return caps


def has_capability(user, capability):
    caps = capabilities(user)
    return ALL in caps or capability in caps


def can_manage_roles(user):
    """Only ever true for a super user.

    An administrator holding ``roles.manage`` still cannot hand themselves a
    capability they do not already have - see the self-escalation guard in
    ``admin_views.admin_roles``.
    """
    return bool(getattr(user, 'is_superuser', False))
