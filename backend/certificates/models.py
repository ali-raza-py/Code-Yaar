"""Verifiable Code Yaar certificates of completion.

Certificates are issued records of *server-verified* course completion —
never decorative images. A certificate can only exist once the eligibility
service confirms the learner met the course's configured requirements, and
every state change is captured as an append-only audit event.
"""

import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone


def _generate_public_id() -> str:
    """Unpredictable, URL-safe public verification identifier.

    Uses 160 bits of entropy so identifiers are neither guessable nor
    enumeratable, and never expose emails, account ids, or scores.
    """
    return secrets.token_urlsafe(20)


class CertificateQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=Certificate.Status.ACTIVE)


class Certificate(models.Model):
    """A single issued certificate tied to a verified course completion."""

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        REVOKED = 'revoked', 'Revoked'
        SUPERSEDED = 'superseded', 'Superseded'

    # Business identifier used in public verification URLs.
    public_id = models.CharField(
        max_length=40, unique=True, editable=False, default=_generate_public_id
    )
    # Human-readable credential reference printed on the certificate.
    credential_id = models.CharField(max_length=32, unique=True, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates',
    )
    course = models.ForeignKey(
        'learning.Course',
        on_delete=models.CASCADE,
        related_name='certificates',
    )
    enrollment = models.ForeignKey(
        'learning.Enrollment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='certificates',
        help_text='The completion record this certificate was verified against',
    )

    # ── Immutable snapshots taken at issuance time ──
    student_name = models.CharField(
        max_length=250,
        help_text='Learner display name exactly as printed on the certificate',
    )
    course_title = models.CharField(
        max_length=200,
        help_text='Course title as printed at issuance (survives later renames)',
    )

    issued_at = models.DateTimeField(default=timezone.now, editable=False)
    completion_verified_at = models.DateTimeField(default=timezone.now)
    final_score = models.FloatField(
        null=True,
        blank=True,
        help_text='Final assessment percentage at issuance, if the policy grades one',
    )

    # Version of the certification rules used, for auditability.
    policy_version = models.PositiveIntegerField(
        default=1,
        help_text='Incremented whenever the course certification policy changes',
    )

    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.ACTIVE
    )
    # Link a corrected reissue back to the record it replaced.
    supersedes = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='superseded_by',
    )

    # Who/what authorized issuance.
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='certificates_issued',
        help_text='Staff member who issued this certificate (null = automated)',
    )
    issued_automatically = models.BooleanField(
        default=True, help_text='True when issuance was triggered by the learner/system'
    )

    pdf_file = models.FileField(
        upload_to='certificates/%Y/', null=True, blank=True,
        help_text='Generated PDF rendering of the certificate',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CertificateQuerySet.as_manager()

    class Meta:
        ordering = ['-issued_at']
        verbose_name = 'certificate'
        verbose_name_plural = 'certificates'
        # Prevent duplicate live certificates for the same learner + course.
        # Superseded and revoked records may accumulate for the audit trail.
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'course'],
                condition=models.Q(status='active'),
                name='unique_active_certificate_per_learner_course',
            ),
        ]

    def __str__(self):
        return f'{self.credential_id} — {self.student_name} — {self.course_title}'

    @property
    def is_valid(self) -> bool:
        return self.status == self.Status.ACTIVE

    def verification_url(self) -> str:
        """Public page keyed by the human-readable credential id.

        Older links that used `public_id` still resolve through the same
        verification endpoint and a frontend redirect.
        """
        return f"{settings.SITE_URL}/verify/certificate/{self.credential_id}"

    def save(self, *args, **kwargs):
        if not self.credential_id:
            self.credential_id = self._mint_credential_id()
        super().save(*args, **kwargs)

    def _mint_credential_id(self) -> str:
        """Short, human-friendly, collision-checked credential code."""
        year = timezone.localdate().year
        while True:
            token = secrets.token_hex(3).upper()  # 6 hex chars
            candidate = f'CY-{year}-{token}'
            if not Certificate.objects.filter(credential_id=candidate).exists():
                return candidate


class CertificateEvent(models.Model):
    """Append-only audit trail of every certificate lifecycle action.

    Historical certificate data is never silently altered; corrections add a
    new event and (for a reissue) a new Certificate linked via `supersedes`.
    """

    class Action(models.TextChoices):
        ISSUED = 'issued', 'Issued'
        DOWNLOADED = 'downloaded', 'Downloaded'
        REVOKED = 'revoked', 'Revoked'
        CORRECTED = 'corrected', 'Corrected'
        REISSUED = 'reissued', 'Reissued'

    certificate = models.ForeignKey(
        Certificate,
        on_delete=models.CASCADE,
        related_name='events',
    )
    action = models.CharField(max_length=12, choices=Action.choices)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='certificate_events',
        help_text='Staff member responsible (null = automated/system)',
    )
    reason = models.TextField(
        blank=True,
        default='',
        help_text='Documented reason required for revocation/correction/reissue',
    )
    snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text='Certificate field values at the time of this event',
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['created_at', 'id']

    def __str__(self):
        return f'{self.get_action_display()} — {self.certificate_id} @ {self.created_at:%Y-%m-%d %H:%M}'
