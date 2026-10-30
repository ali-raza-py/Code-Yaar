"""Server-side certificate eligibility checks and issuance.

All completion/grading logic lives here so the frontend can never self-issue a
certificate by editing a request. Issuance is transactional and duplicate-safe.
"""

from dataclasses import dataclass, field

from django.db import transaction
from django.utils import timezone

from learning.models import Course, Enrollment, Exercise, Lesson, LessonProgress

from .models import Certificate, CertificateEvent


@dataclass
class EligibilityResult:
    eligible: bool
    final_score: float | None
    requirements: list = field(default_factory=list)
    # Convenience flags surfaced to the client for progress display.
    lessons_required: bool = True
    lessons_completed: int = 0
    lessons_total: int = 0
    assessment_required: bool = True
    assessment_items: int = 0
    assessment_passed: int = 0

    def to_dict(self) -> dict:
        return {
            'eligible': self.eligible,
            'final_score': self.final_score,
            'requirements': self.requirements,
            'lessons_required': self.lessons_required,
            'lessons_completed': self.lessons_completed,
            'lessons_total': self.lessons_total,
            'assessment_required': self.assessment_required,
            'assessment_items': self.assessment_items,
            'assessment_passed': self.assessment_passed,
        }


def _lesson_completion(user, course):
    total = Lesson.objects.filter(
        chapter__course=course, chapter__is_active=True, is_active=True
    ).count()
    completed = LessonProgress.objects.filter(
        user=user,
        lesson__chapter__course=course,
        lesson__is_active=True,
        status__in=['completed', 'mastered'],
    ).count()
    return completed, total


def _final_assessment(user, course):
    """Best-effort grade over the course's final-assessment exercises.

    Each assessment exercise contributes equally; a learner passes an item
    once any attempt is recorded as correct by the server-side grader.
    """
    items = Exercise.objects.filter(
        lesson__chapter__course=course,
        lesson__chapter__is_active=True,
        lesson__is_active=True,
        is_final_assessment=True,
        is_active=True,
    )
    total = items.count()
    if total == 0:
        return None, 0, 0
    passed = items.filter(
        attempts__user=user, attempts__status='correct'
    ).distinct().count()
    score = round((passed / total) * 100, 1)
    return score, passed, total


def check_eligibility(user, course: Course) -> EligibilityResult:
    """Evaluate the course's configured certification rules against real data."""
    result = EligibilityResult(eligible=False, final_score=None)

    if not course.certification_enabled:
        result.requirements.append({
            'key': 'certification', 'label': 'Certification',
            'met': False, 'detail': 'This course does not offer a certificate.',
        })
        return result

    if not user.is_authenticated:
        result.requirements.append({
            'key': 'auth', 'label': 'Signed in',
            'met': False, 'detail': 'Sign in to earn a certificate.',
        })
        return result

    enrollment = Enrollment.objects.filter(user=user, course=course).first()
    result.requirements.append({
        'key': 'enrolled', 'label': 'Enrolled in course',
        'met': enrollment is not None,
        'detail': 'You are enrolled.' if enrollment else 'Enroll before you can be certified.',
    })

    # Lessons
    completed, total = _lesson_completion(user, course)
    result.lessons_completed = completed
    result.lessons_total = total
    result.lessons_required = course.require_all_lessons
    lessons_met = (not course.require_all_lessons) or (total > 0 and completed >= total)
    result.requirements.append({
        'key': 'lessons', 'label': 'Complete all lessons',
        'met': lessons_met,
        'detail': f'{completed} of {total} lessons completed.',
    })

    # Final assessment
    score, passed, items = _final_assessment(user, course)
    result.final_score = score
    result.assessment_required = course.require_final_assessment
    result.assessment_items = items
    result.assessment_passed = passed
    if course.require_final_assessment:
        threshold = course.certification_passing_score
        if items == 0:
            assessment_met = False
            detail = 'This course has no final assessment configured yet.'
        else:
            assessment_met = (score or 0) >= threshold
            detail = f'Final assessment {score or 0}% (need {threshold}%).'
        result.requirements.append({
            'key': 'assessment', 'label': f'Pass final assessment ({threshold}%)',
            'met': assessment_met, 'detail': detail,
        })

    result.eligible = all(r['met'] for r in result.requirements) and enrollment is not None
    return result


class CertificateNotEligible(Exception):
    """Raised when issuance is attempted before eligibility is satisfied."""

    def __init__(self, result: EligibilityResult):
        self.result = result
        super().__init__('Certificate requirements not met.')


@transaction.atomic
def issue_certificate(user, course: Course, *, issued_by=None,
                      automatically: bool = True) -> Certificate:
    """Issue a certificate after re-verifying eligibility on the server.

    Locks the learner+course rows to make issuance duplicate-safe even under
    concurrent requests.
    """
    enrollment = (
        Enrollment.objects.select_for_update()
        .filter(user=user, course=course)
        .first()
    )
    # Re-check eligibility inside the transaction against fresh data.
    result = check_eligibility(user, course)
    if not result.eligible:
        raise CertificateNotEligible(result)

    # Idempotent: return the existing live certificate if already issued.
    existing = Certificate.objects.filter(
        user=user, course=course,
        status__in=[Certificate.Status.ACTIVE, Certificate.Status.SUPERSEDED],
    ).first()
    if existing:
        return existing

    student_name = (
        user.get_full_name().strip()
        or user.username
    )

    certificate = Certificate.objects.create(
        user=user,
        course=course,
        enrollment=enrollment,
        student_name=student_name,
        course_title=course.title,
        completion_verified_at=timezone.now(),
        final_score=result.final_score,
        policy_version=course.policy_version if hasattr(course, 'policy_version') else 1,
        issued_by=issued_by,
        issued_automatically=automatically,
    )

    CertificateEvent.objects.create(
        certificate=certificate,
        action=CertificateEvent.Action.ISSUED,
        performed_by=issued_by,
        reason='Course completion requirements verified.',
        snapshot=_snapshot(certificate),
    )

    # Generate the PDF (best effort — a rendering failure must not un-issue
    # the record, which remains verifiable from the database regardless).
    from .pdf import render_certificate_pdf
    try:
        certificate.pdf_file.save(
            f'{certificate.public_id}.pdf',
            render_certificate_pdf(certificate),
            save=False,
        )
        certificate.save(update_fields=['pdf_file'])
    except Exception:  # noqa: BLE001
        pass

    return certificate


def _snapshot(certificate: Certificate) -> dict:
    return {
        'public_id': certificate.public_id,
        'credential_id': certificate.credential_id,
        'student_name': certificate.student_name,
        'course_title': certificate.course_title,
        'final_score': certificate.final_score,
        'status': certificate.status,
        'policy_version': certificate.policy_version,
    }


@transaction.atomic
def revoke_certificate(certificate: Certificate, *, performed_by, reason: str) -> Certificate:
    """Revoke a certificate with a documented reason (audit retained)."""
    if certificate.status != Certificate.Status.ACTIVE:
        raise ValueError('Only active certificates can be revoked.')
    certificate.status = Certificate.Status.REVOKED
    certificate.save(update_fields=['status', 'updated_at'])
    CertificateEvent.objects.create(
        certificate=certificate,
        action=CertificateEvent.Action.REVOKED,
        performed_by=performed_by,
        reason=reason,
        snapshot=_snapshot(certificate),
    )
    return certificate


@transaction.atomic
def reissue_corrected_certificate(certificate: Certificate, *, performed_by,
                                  reason: str) -> Certificate:
    """Reissue a corrected certificate, superseding the original.

    The original is retained (marked superseded) so history is never destroyed.
    """
    if certificate.status == Certificate.Status.SUPERSEDED:
        raise ValueError('This certificate has already been superseded.')
    result = check_eligibility(certificate.user, certificate.course)
    if not result.eligible:
        raise CertificateNotEligible(result)

    # Retire the original *first* so the learner never has two active rows
    # for the same course, preserving the one-active-certificate constraint.
    certificate.status = Certificate.Status.SUPERSEDED
    certificate.save(update_fields=['status', 'updated_at'])

    corrected = Certificate.objects.create(
        user=certificate.user,
        course=certificate.course,
        enrollment=certificate.enrollment,
        student_name=certificate.user.get_full_name().strip() or certificate.user.username,
        course_title=certificate.course.title,
        final_score=result.final_score,
        policy_version=certificate.policy_version + 1,
        issued_by=performed_by,
        issued_automatically=False,
        supersedes=certificate,
    )

    CertificateEvent.objects.create(
        certificate=certificate,
        action=CertificateEvent.Action.CORRECTED,
        performed_by=performed_by,
        reason=reason,
        snapshot=_snapshot(certificate),
    )
    CertificateEvent.objects.create(
        certificate=corrected,
        action=CertificateEvent.Action.REISSUED,
        performed_by=performed_by,
        reason=reason,
        snapshot=_snapshot(corrected),
    )

    from .pdf import render_certificate_pdf
    try:
        corrected.pdf_file.save(
            f'{corrected.public_id}.pdf',
            render_certificate_pdf(corrected),
            save=False,
        )
        corrected.save(update_fields=['pdf_file'])
    except Exception:  # noqa: BLE001
        pass

    return corrected
