"""URL map for the authentication API (mounted under ``/api/auth/``)."""

from django.urls import path

from . import auth_views

urlpatterns = [
    path('csrf/', auth_views.CsrfTokenView.as_view(), name='auth-csrf'),
    path('register/', auth_views.RegisterView.as_view(), name='auth-register'),
    path('login/', auth_views.LoginView.as_view(), name='auth-login'),
    path('logout/', auth_views.LogoutView.as_view(), name='auth-logout'),
    path(
        'token/refresh/',
        auth_views.TokenRefreshView.as_view(),
        name='auth-token-refresh',
    ),
    path('me/', auth_views.MeView.as_view(), name='auth-me'),
    path(
        'verify-email/',
        auth_views.VerifyEmailView.as_view(),
        name='auth-verify-email',
    ),
    path(
        'resend-verification/',
        auth_views.ResendVerificationView.as_view(),
        name='auth-resend-verification',
    ),
    path(
        'password-reset/',
        auth_views.PasswordResetRequestView.as_view(),
        name='auth-password-reset',
    ),
    path(
        'password-reset/confirm/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='auth-password-reset-confirm',
    ),
    path(
        'change-password/',
        auth_views.ChangePasswordView.as_view(),
        name='auth-change-password',
    ),
]
