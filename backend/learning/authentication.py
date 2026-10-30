"""Authentication helpers for the learning API."""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameModelBackend(ModelBackend):
    """Allow signing in with either the username or the email address."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username and "@" in username:
            user = get_user_model().objects.filter(email__iexact=username).first()
            if user is not None and user.check_password(password):
                return user
        return super().authenticate(
            request, username=username, password=password, **kwargs
        )
