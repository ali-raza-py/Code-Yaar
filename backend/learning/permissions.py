"""Role-based permission classes for the Code Yaar API.

Frontend route guards are a UX affordance only; these classes are the
authorisation boundary. Roles are resolved from staff flags, Django groups,
and the profile row by :func:`learning.services.auth.user_role`.
"""

from django.conf import settings
from rest_framework.permissions import BasePermission

from .services.admin_access import ALL as ALL_CAPABILITIES, has_capability
from .services.auth import get_profile, user_role


class IsStudent(BasePermission):
    message = 'Student access required.'

    def has_permission(self, request, view):
        return user_role(request.user) in ('student', 'instructor', 'administrator')


class IsInstructor(BasePermission):
    message = 'Instructor access required.'

    def has_permission(self, request, view):
        return user_role(request.user) in ('instructor', 'administrator')


class IsAdministrator(BasePermission):
    message = 'Administrator access required.'

    def has_permission(self, request, view):
        return user_role(request.user) == 'administrator'


class IsSuperAdmin(BasePermission):
    message = 'Super Admin access required.'

    def has_permission(self, request, view):
        return bool(
            getattr(request.user, 'is_authenticated', False)
            and request.user.is_superuser
        )


class IsEmailVerified(BasePermission):
    """Gate for features that require a verified email address.

    Disabled while ``AUTH_REQUIRE_EMAIL_VERIFICATION`` is False so existing
    accounts and local development keep working.
    """

    message = 'Verify your email address to use this feature.'

    def has_permission(self, request, view):
        if not settings.AUTH_REQUIRE_EMAIL_VERIFICATION:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return bool(get_profile(request.user).email_verified)


class IsOwnerOrAdministrator(BasePermission):
    """Object-level guard against insecure direct object references."""

    message = 'You do not have access to this object.'

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, 'user', None)
        if owner == request.user:
            return True
        return user_role(request.user) == 'administrator'


class HasAdminCapability(BasePermission):
    """Gate an administrative endpoint on a resolved capability.

    Views declare ``required_admin_capability`` as a capability name (or an
    iterable of alternatives). A view that declares nothing falls back to the
    historical whole-panel administrator check, so adding this class to an
    existing viewset cannot accidentally open it up.
    """

    message = 'You do not have permission to perform this administrative action.'

    def has_permission(self, request, view):
        user = request.user
        if not getattr(user, 'is_authenticated', False):
            return False
        required = getattr(view, 'required_admin_capability', None)
        if not required:
            return user_role(user) == 'administrator'
        codes = required if isinstance(required, (list, tuple, set, frozenset)) else (required,)
        return any(has_capability(user, code) for code in codes)


class ScopedCourseAccess(BasePermission):
    """Object-level course scoping for the Course Creation Studio.

    The specification requires that an instructor can manage assigned courses and
    nothing else. That is only enforceable per object, because the same endpoint
    legitimately serves a platform administrator the whole catalogue. Combined with
    :class:`HasAdminCapability` (which decides *whether* the caller may use the
    studio at all), this decides *which* course they may touch: a super user or
    administrator reaches any course, an instructor only one whose
    ``instructor_user`` is their own account, and an unassigned course is reachable
    by nobody but an administrator.
    """

    message = 'This course is not assigned to you.'

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not getattr(user, 'is_authenticated', False):
            return False
        if has_capability(user, ALL_CAPABILITIES):
            return True
        # Studio endpoints hand out a Course; nested chapter/lesson routes hand out
        # a row that points at one. Either way the owning course is what matters.
        role = user_role(user)
        if role == 'administrator':
            # A group-scoped administrator (Academic Manager, Course Editor, ...) is
            # limited by *capabilities*, not by course ownership - scoping to assigned
            # courses is the instructor rule and must not swallow them.
            return True
        course = getattr(obj, 'course', None) or obj
        if role != 'instructor':
            return False
        instructor_id = getattr(course, 'instructor_user_id', None)
        return instructor_id is not None and instructor_id == user.pk
