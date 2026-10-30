"""Role-based permission classes for the Code Yaar API.

Frontend route guards are a UX affordance only; these classes are the
authorisation boundary. Roles are resolved from staff flags, Django groups,
and the profile row by :func:`learning.services.auth.user_role`.
"""

from django.conf import settings
from rest_framework.permissions import BasePermission

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
