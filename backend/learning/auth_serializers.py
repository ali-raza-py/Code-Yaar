"""Serializers for the authentication API.

Validation lives here so every endpoint gets identical rules and field-level
error shapes. Nothing in this module can grant staff, role, or permission
fields — those are read-only projections of the database.
"""

from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import Group
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from .models import UserProfile
from .services.auth import STUDENT_GROUP, get_profile, user_role

User = get_user_model()


# ─── Read projections ───────────────────────────────────────────────────────


class AuthUserSerializer(serializers.ModelSerializer):
    """Public identity of the signed-in user (never includes permissions)."""

    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    email_verified = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'date_joined', 'role', 'email_verified',
        ]
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.get_full_name().strip() or obj.username

    def get_role(self, obj):
        return user_role(obj)

    def get_email_verified(self, obj):
        return bool(get_profile(obj).email_verified)


class UserProfileSerializer(serializers.ModelSerializer):
    """Student profile. `role` is read-only: it is never user-editable."""

    user = AuthUserSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user', 'full_name', 'avatar', 'bio', 'role', 'institution',
            'education_level', 'github_url', 'linkedin_url',
            'email_verified', 'email_verified_at',
            'xp_points', 'streak_days', 'level', 'last_active_at',
            'created_at',
        ]
        read_only_fields = fields


def me_payload(user):
    """Flat + nested payload consumed by the existing frontend pages.

    The flat keys (``xp_points``, ``avatar``, …) keep the pre-existing
    ``auth.getProfile()`` consumers working without a second request.
    """
    profile = get_profile(user)
    return {
        'user': AuthUserSerializer(user).data,
        'profile': UserProfileSerializer(profile).data,
        'avatar': profile.avatar,
        'bio': profile.bio,
        'role': user_role(user),
        'email_verified': profile.email_verified,
        'institution': profile.institution,
        'education_level': profile.education_level,
        'github_url': profile.github_url,
        'linkedin_url': profile.linkedin_url,
        'xp_points': profile.xp_points,
        'streak_days': profile.streak_days,
        'level': profile.level,
        'last_active_at': (
            profile.last_active_at.isoformat() if profile.last_active_at else None
        ),
    }


# ─── Registration ───────────────────────────────────────────────────────────


def _split_full_name(full_name):
    parts = (full_name or '').strip().split()
    if not parts:
        return '', ''
    if len(parts) == 1:
        return parts[0][:150], ''
    return parts[0][:150], ' '.join(parts[1:])[:150]


class RegisterSerializer(serializers.Serializer):
    """Student registration: full name, username, email, password."""

    full_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True
    )
    first_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True
    )
    last_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True
    )
    username = serializers.CharField(
        max_length=150, validators=[UnicodeUsernameValidator()]
    )
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(
        write_only=True, trim_whitespace=False, style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True, trim_whitespace=False, style={'input_type': 'password'}
    )

    def validate_username(self, value):
        username = value.strip()
        if not username:
            raise serializers.ValidationError('Enter a username.')
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError('This username is already taken.')
        return username

    def validate_email(self, value):
        email = (value or '').strip().lower()
        if not email:
            raise serializers.ValidationError('Enter an email address.')
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                'An account with this email address already exists.'
            )
        return email

    def validate(self, attrs):
        password = attrs.get('password') or ''
        confirm = attrs.get('confirm_password') or ''
        if password != confirm:
            raise serializers.ValidationError(
                {'confirm_password': ['Passwords do not match.']}
            )

        candidate = User(
            username=attrs.get('username', ''),
            email=attrs.get('email', ''),
            first_name=attrs.get('first_name', ''),
            last_name=attrs.get('last_name', ''),
        )
        try:
            password_validation.validate_password(password, user=candidate)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': list(exc.messages)})

        if not (attrs.get('first_name') or attrs.get('last_name') or attrs.get('full_name')):
            raise serializers.ValidationError(
                {'full_name': ['Enter your full name.']}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        full_name = validated_data.pop('full_name', '')
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        if not (first_name or last_name):
            first_name, last_name = _split_full_name(full_name)

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=first_name[:150],
            last_name=last_name[:150],
        )
        # Explicitly pin non-privileged flags: registration can never grant
        # staff or superuser status.
        user.is_staff = False
        user.is_superuser = False
        user.is_active = True
        user.save(update_fields=['is_staff', 'is_superuser', 'is_active'])

        profile = get_profile(user)
        profile.role = 'student'
        profile.save(update_fields=['role'])

        group = Group.objects.filter(name=STUDENT_GROUP).first()
        if group is not None:
            user.groups.add(group)
        return user


# ─── Login ──────────────────────────────────────────────────────────────────


class LoginSerializer(serializers.Serializer):
    """Accepts `identifier`, or legacy `username` / `email` keys."""

    identifier = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(
        write_only=True, trim_whitespace=False, style={'input_type': 'password'}
    )

    def validate(self, attrs):
        identifier = (
            attrs.get('identifier') or attrs.get('username') or attrs.get('email') or ''
        ).strip()
        if not identifier or not attrs.get('password'):
            raise serializers.ValidationError(
                {'detail': 'Enter your email or username and password.'}
            )
        attrs['identifier'] = identifier
        return attrs


# ─── Profile updates ────────────────────────────────────────────────────────


class ProfileUpdateSerializer(serializers.Serializer):
    """Fields a user may change about themselves — and nothing else."""

    username = serializers.CharField(
        max_length=150, required=False, validators=[UnicodeUsernameValidator()]
    )
    email = serializers.EmailField(max_length=254, required=False)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    full_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    bio = serializers.CharField(max_length=2000, required=False, allow_blank=True)
    avatar = serializers.URLField(max_length=500, required=False, allow_blank=True)
    institution = serializers.CharField(max_length=200, required=False, allow_blank=True)
    education_level = serializers.ChoiceField(
        choices=UserProfile.EDUCATION_LEVEL_CHOICES, required=False, allow_blank=True
    )
    github_url = serializers.URLField(max_length=500, required=False, allow_blank=True)
    linkedin_url = serializers.URLField(max_length=500, required=False, allow_blank=True)

    PROFILE_FIELDS = (
        'bio', 'avatar', 'institution', 'education_level', 'github_url',
        'linkedin_url',
    )

    def validate_username(self, value):
        username = value.strip()
        if not username:
            raise serializers.ValidationError('Enter a username.')
        if User.objects.filter(username__iexact=username).exclude(
            pk=self.instance.pk
        ).exists():
            raise serializers.ValidationError('This username is already taken.')
        return username

    def validate_email(self, value):
        email = (value or '').strip().lower()
        if not email:
            raise serializers.ValidationError('Enter an email address.')
        if User.objects.filter(email__iexact=email).exclude(
            pk=self.instance.pk
        ).exists():
            raise serializers.ValidationError(
                'An account with this email address already exists.'
            )
        return email

    @transaction.atomic
    def update(self, instance, validated_data):
        full_name = validated_data.pop('full_name', None)
        if full_name is not None and not (
            'first_name' in validated_data or 'last_name' in validated_data
        ):
            validated_data['first_name'], validated_data['last_name'] = (
                _split_full_name(full_name)
            )

        user_fields = ('username', 'email', 'first_name', 'last_name')
        changed = []
        for field in user_fields:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
                changed.append(field)
        if changed:
            instance.save(update_fields=changed)

        profile = get_profile(instance)
        profile_changed = []
        for field in self.PROFILE_FIELDS:
            if field in validated_data:
                setattr(profile, field, validated_data[field])
                profile_changed.append(field)
        if profile_changed:
            profile.save(update_fields=profile_changed)
        return instance


# ─── Password flows ─────────────────────────────────────────────────────────


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True, trim_whitespace=False, style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True, trim_whitespace=False, style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True, trim_whitespace=False, style={'input_type': 'password'}
    )

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs.get('current_password') or ''):
            raise serializers.ValidationError(
                {'current_password': ['Current password is incorrect.']}
            )
        if attrs.get('new_password') != attrs.get('confirm_password'):
            raise serializers.ValidationError(
                {'confirm_password': ['Passwords do not match.']}
            )
        try:
            password_validation.validate_password(attrs['new_password'], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'new_password': list(exc.messages)})
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(
        write_only=True, trim_whitespace=False, style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True, trim_whitespace=False, style={'input_type': 'password'}
    )

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError(
                {'confirm_password': ['Passwords do not match.']}
            )
        try:
            password_validation.validate_password(attrs['password'])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': list(exc.messages)})
        return attrs


class EmailVerifySerializer(serializers.Serializer):
    token = serializers.CharField()


class ResendVerificationSerializer(serializers.Serializer):
    """Email is optional for signed-in users (their own address is used)."""

    email = serializers.EmailField(max_length=254, required=False, allow_blank=True)
