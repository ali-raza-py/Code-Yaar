"""Authentication API views.

Contract:
- Access tokens are returned in JSON (short-lived, held in memory by the SPA).
- Refresh tokens are HttpOnly cookies and never appear in a response body.
- Cookie-authenticated endpoints (`token/refresh/`, `logout/`) additionally
  require a double-submit CSRF header.
- Unknown accounts always get the same generic response as known ones.
"""

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.middleware.csrf import get_token
from django.utils import timezone
from django.utils.crypto import constant_time_compare
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .auth_serializers import (
    AuthUserSerializer,
    ChangePasswordSerializer,
    EmailVerifySerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    ResendVerificationSerializer,
    me_payload,
)
from .models import AuthenticationAuditLog
from .services.auth import (
    audit,
    clear_refresh_cookie,
    find_user_by_identifier,
    get_profile,
    issue_email_verification,
    issue_password_reset,
    refresh_token_from_request,
    reset_password,
    revoke_refresh_tokens,
    set_refresh_cookie,
    verify_email,
)

User = get_user_model()

GENERIC_LOGIN_ERROR = 'Invalid credentials.'


# ─── Helpers ────────────────────────────────────────────────────────────────


def _access_lifetime_seconds():
    return int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())


def _start_session(user):
    """Create a refresh token + access token pair for a user."""
    refresh = RefreshToken.for_user(user)
    return str(refresh), str(refresh.access_token)


def _session_payload(user, access_token):
    return {
        'access': access_token,
        'token_type': 'Bearer',
        'expires_in': _access_lifetime_seconds(),
        'user': AuthUserSerializer(user).data,
    }


def _csrf_failure():
    return Response(
        {'detail': 'CSRF verification failed. Reload the page and try again.'},
        status=status.HTTP_403_FORBIDDEN,
    )


def require_double_submit_csrf(request):
    """Validate the CSRF cookie against its header twin.

    Django's own middleware is bypassed for DRF API views, so cookie-backed
    endpoints perform the same double-submit comparison explicitly.
    """
    cookie = request.COOKIES.get(settings.CSRF_COOKIE_NAME)
    header = request.META.get('HTTP_X_CSRFTOKEN')
    if not cookie or not header:
        return False
    return constant_time_compare(cookie, header)


def _user_from_refresh_cookie(raw_token):
    if not raw_token:
        return None
    try:
        token = RefreshToken(raw_token)
    except TokenError:
        return None
    return User.objects.filter(pk=token.get('user_id')).first()


# ─── Registration / login / logout ──────────────────────────────────────────


class CsrfTokenView(APIView):
    """Bootstraps the CSRF cookie for cookie-authenticated endpoints.

    Returns the cookie's own value (not Django's masked variant) so the
    double-submit comparison can be a literal constant-time match. The CSRF
    cookie is intentionally readable by the same-site SPA; it is not a
    credential on its own.
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        get_token(request)
        return Response({'csrfToken': request.META.get('CSRF_COOKIE', '')})


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'auth_register'

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        audit(
            AuthenticationAuditLog.Event.REGISTER,
            request=request,
            user=user,
            identifier=user.email,
        )
        verification_sent = issue_email_verification(user, request=request)
        payload = {
            'user': AuthUserSerializer(user).data,
            'verification_email_sent': verification_sent,
        }

        if settings.AUTH_REQUIRE_EMAIL_VERIFICATION:
            # The account is unusable until the link is clicked, so no session is
            # issued: the client shows the "check your email" screen and the user
            # signs in afterwards. Issuing tokens here would hand an unverified
            # account exactly the access the gate is meant to withhold.
            return Response(payload, status=status.HTTP_201_CREATED)

        raw_refresh, access = _start_session(user)
        payload = _session_payload(user, access)
        payload['verification_email_sent'] = verification_sent
        response = Response(payload, status=status.HTTP_201_CREATED)
        set_refresh_cookie(response, raw_refresh)
        return response


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'auth_login'

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data['identifier']
        password = serializer.validated_data['password']

        user = authenticate(request=request, username=identifier, password=password)
        if user is None or not user.is_active:
            audit(
                AuthenticationAuditLog.Event.LOGIN_FAILED,
                request=request,
                identifier=identifier,
            )
            return Response(
                {'detail': GENERIC_LOGIN_ERROR},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Credentials were correct, so this is not a enumeration risk: the reply
        # names the actual barrier and echoes the address so the client can offer
        # a resend without asking for it again. Staff are exempt because Django's
        # admin already admits them through a session login.
        if (
            settings.AUTH_REQUIRE_EMAIL_VERIFICATION
            and not user.is_staff
            and not get_profile(user).email_verified
        ):
            audit(
                AuthenticationAuditLog.Event.LOGIN_FAILED,
                request=request,
                user=user,
                identifier=identifier,
                metadata={'reason': 'email_not_verified'},
            )
            return Response(
                {
                    'detail': (
                        'Confirm your email address before signing in. We can '
                        'send you a new verification link.'
                    ),
                    'code': 'email_not_verified',
                    'email': user.email,
                    'can_resend': bool(user.email),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        audit(
            AuthenticationAuditLog.Event.LOGIN_SUCCESS,
            request=request,
            user=user,
            identifier=identifier,
        )

        raw_refresh, access = _start_session(user)
        response = Response(_session_payload(user, access))
        set_refresh_cookie(response, raw_refresh)
        return response


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'auth_refresh'

    def post(self, request):
        if not require_double_submit_csrf(request):
            return _csrf_failure()

        raw_refresh = refresh_token_from_request(request)
        user = _user_from_refresh_cookie(raw_refresh)
        if raw_refresh:
            try:
                RefreshToken(raw_refresh).blacklist()
            except TokenError:
                pass

        audit(
            AuthenticationAuditLog.Event.LOGOUT,
            request=request,
            user=user,
        )
        response = Response({'detail': 'Signed out.'})
        clear_refresh_cookie(response)
        return response


class TokenRefreshView(APIView):
    """Rotates the refresh cookie and returns a fresh access token."""

    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'auth_refresh'

    def post(self, request):
        if not require_double_submit_csrf(request):
            return _csrf_failure()

        raw_refresh = refresh_token_from_request(request)
        if not raw_refresh:
            return Response(
                {'detail': 'No refresh token.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = TokenRefreshSerializer(data={'refresh': raw_refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            audit(
                AuthenticationAuditLog.Event.TOKEN_REFRESH_FAILED,
                request=request,
                user=_user_from_refresh_cookie(raw_refresh),
            )
            response = Response(
                {'detail': 'Session expired. Sign in again.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            clear_refresh_cookie(response)
            return response

        data = serializer.validated_data
        audit(
            AuthenticationAuditLog.Event.TOKEN_REFRESH,
            request=request,
            user=_user_from_refresh_cookie(raw_refresh),
        )

        response = Response(
            {
                'access': data['access'],
                'token_type': 'Bearer',
                'expires_in': _access_lifetime_seconds(),
            }
        )
        # Rotation is on: persist the replacement cookie, never leak it in JSON.
        if data.get('refresh'):
            set_refresh_cookie(response, data['refresh'])
        return response


# ─── Current user / profile ─────────────────────────────────────────────────


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    FORBIDDEN_FIELDS = {
        'role', 'is_staff', 'is_superuser', 'is_active', 'permissions',
        'groups', 'user_permissions', 'password',
    }

    def get(self, request):
        return Response(me_payload(request.user))

    def patch(self, request):
        data = request.data if isinstance(request.data, dict) else {}
        attempted = self.FORBIDDEN_FIELDS.intersection(data.keys())
        if attempted:
            audit(
                AuthenticationAuditLog.Event.PRIVILEGE_ESCALATION_BLOCKED,
                request=request,
                user=request.user,
                metadata={'fields': sorted(attempted)},
            )
            return Response(
                {
                    'detail': 'You cannot change account privileges through the '
                              'profile API.',
                    'fields': sorted(attempted),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        previous_email = request.user.email
        serializer = ProfileUpdateSerializer(
            instance=request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        email_changed = user.email != previous_email
        verification_sent = False
        if email_changed:
            profile = get_profile(user)
            profile.email_verified = False
            profile.email_verified_at = None
            profile.save(update_fields=['email_verified', 'email_verified_at'])
            verification_sent = issue_email_verification(user, request=request)

        audit(
            AuthenticationAuditLog.Event.PROFILE_UPDATED,
            request=request,
            user=user,
            metadata={'email_changed': email_changed},
        )

        payload = me_payload(user)
        payload['email_changed'] = email_changed
        payload['verification_email_sent'] = verification_sent
        return Response(payload)


# ─── Email verification ─────────────────────────────────────────────────────


class VerifyEmailView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'auth_verify_email'

    MESSAGES = {
        'expired': 'This verification link has expired. Request a new one.',
        'used': 'This verification link has already been used.',
        'invalid': 'This verification link is invalid.',
    }

    def post(self, request):
        serializer = EmailVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result, user = verify_email(serializer.validated_data['token'], request=request)
        if result == 'used' and user is not None and get_profile(user).email_verified:
            # A double submit (second tab, refreshed page, mail scanner) should
            # land on the success screen instead of "link already used".
            return Response(
                {
                    'detail': 'Email already verified.',
                    'code': 'already_verified',
                    'user': AuthUserSerializer(user).data,
                }
            )
        if result != 'ok':
            return Response(
                {'detail': self.MESSAGES.get(result, 'Verification failed.'), 'code': f'token_{result}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                'detail': 'Email verified.',
                'user': AuthUserSerializer(user).data,
            }
        )


class ResendVerificationView(APIView):
    # Keeps default authentication so a signed-in user can resend for their
    # own address without typing it again; unauthenticated callers pass email.
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'auth_resend_verification'

    GENERIC = (
        'If that account exists and still needs verification, a new link is '
        'on its way.'
    )

    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = None
        if request.user.is_authenticated and not serializer.validated_data.get('email'):
            user = request.user
        else:
            user = find_user_by_identifier(serializer.validated_data.get('email') or '')

        if user is not None and user.is_active and not get_profile(user).email_verified:
            sent = issue_email_verification(user, request=request)
        else:
            sent = None

        payload = {'detail': self.GENERIC}
        # A signed-in caller asking about their own address learns nothing about
        # anybody else, so their delivery outcome is reported honestly instead of
        # being hidden behind the generic message. Anonymous callers never get the
        # flag, which keeps the endpoint useless for address enumeration.
        if sent is not None and request.user.is_authenticated and user == request.user:
            payload['verification_email_sent'] = sent
        return Response(payload)


# ─── Password reset / change ────────────────────────────────────────────────


class PasswordResetRequestView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'auth_password_reset'

    GENERIC = (
        'If an account exists for that email address, a password reset link '
        'is on its way.'
    )

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = find_user_by_identifier(serializer.validated_data['email'])
        if user is not None and user.is_active and user.email:
            issue_password_reset(user, request=request)
        return Response({'detail': self.GENERIC})


class PasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'auth_password_reset_confirm'

    MESSAGES = {
        'expired': 'This password reset link has expired. Request a new one.',
        'used': 'This password reset link has already been used.',
        'invalid': 'This password reset link is invalid.',
    }

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result, user = reset_password(
            serializer.validated_data['token'],
            serializer.validated_data['password'],
            request=request,
        )
        if result != 'ok':
            return Response(
                {'detail': self.MESSAGES.get(result, 'Password reset failed.'), 'code': f'token_{result}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {'detail': 'Password updated. Sign in with your new password.'}
        )


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = 'auth_change_password'

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=['password'])
        # Every other device is signed out; this client gets a fresh session.
        revoke_refresh_tokens(user)

        raw_refresh, access = _start_session(user)
        audit(
            AuthenticationAuditLog.Event.PASSWORD_CHANGED,
            request=request,
            user=user,
        )

        response = Response(
            {
                'detail': 'Password changed.',
                'access': access,
                'expires_in': _access_lifetime_seconds(),
            }
        )
        set_refresh_cookie(response, raw_refresh)
        return response
