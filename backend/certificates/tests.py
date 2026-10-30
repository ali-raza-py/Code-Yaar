"""Tests for certificate eligibility, issuance, security, and verification."""

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from learning.models import (
    CareerTrack, Course, Chapter, Lesson, Exercise,
    Enrollment, LessonProgress, ExerciseAttempt,
    Certification as LearningCertification, UserCertification,
)
from . import services
from .models import Certificate, CertificateEvent


class CertificateFactoryMixin:
    def make_course(self, slug='py', *, passing=70, require_all=True, require_assess=True):
        track, _ = CareerTrack.objects.get_or_create(
            slug=f't-{slug}', defaults={'title': 'T', 'description': 'T'})
        course = Course.objects.create(
            slug=slug, title=f'Course {slug}', description='d', track=track,
            is_published=True, is_active=True,
            certification_passing_score=passing,
            require_all_lessons=require_all,
            require_final_assessment=require_assess,
        )
        chapter = Chapter.objects.create(course=course, title='Ch', slug=f'{slug}-ch', order=1)
        l1 = Lesson.objects.create(chapter=chapter, title='L1', slug=f'{slug}-l1', order=1)
        l2 = Lesson.objects.create(chapter=chapter, title='L2', slug=f'{slug}-l2', order=2)
        return course, [l1, l2]

    def make_assessment(self, course, lessons, count=4):
        """Create final-assessment MCQ exercises under the first lesson."""
        exercises = []
        for i in range(count):
            exercises.append(Exercise.objects.create(
                lesson=lessons[0], title=f'A{i}', slug=f'{course.slug}-a{i}',
                exercise_type='multiple_choice', instructions='q',
                choices=[{'id': 'a', 'text': 'x', 'is_correct': True}],
                is_final_assessment=True, is_active=True,
            ))
        return exercises

    def complete_lessons(self, user, lessons):
        for lesson in lessons:
            LessonProgress.objects.create(user=user, lesson=lesson, status='completed')

    def pass_assessment(self, user, exercises, n):
        for ex in exercises[:n]:
            ExerciseAttempt.objects.create(
                user=user, exercise=ex, status='correct', attempt_number=1)


class EligibilityTests(CertificateFactoryMixin, TestCase):
    def setUp(self):
        self.user = User.objects.create_user('learn', password='p')
        self.course, self.lessons = self.make_course()
        self.assessments = self.make_assessment(self.course, self.lessons)
        Enrollment.objects.create(user=self.user, course=self.course)

    def test_no_progress_not_eligible(self):
        result = services.check_eligibility(self.user, self.course)
        self.assertFalse(result.eligible)

    def test_missing_assessment_score_not_eligible(self):
        self.complete_lessons(self.user, self.lessons)
        result = services.check_eligibility(self.user, self.course)
        self.assertFalse(result.eligible)

    def test_full_completion_and_pass_is_eligible(self):
        self.complete_lessons(self.user, self.lessons)
        self.pass_assessment(self.user, self.assessments, 4)  # 100%
        result = services.check_eligibility(self.user, self.course)
        self.assertTrue(result.eligible)
        self.assertEqual(result.final_score, 100.0)

    def test_below_threshold_not_eligible(self):
        self.complete_lessons(self.user, self.lessons)
        self.pass_assessment(self.user, self.assessments, 2)  # 50% < 70%
        result = services.check_eligibility(self.user, self.course)
        self.assertFalse(result.eligible)
        self.assertEqual(result.final_score, 50.0)

    def test_unenrolled_not_eligible(self):
        other = User.objects.create_user('other', password='p')
        self.complete_lessons(other, self.lessons)
        self.pass_assessment(other, self.assessments, 4)
        result = services.check_eligibility(other, self.course)
        self.assertFalse(result.eligible)


class IssuanceTests(CertificateFactoryMixin, TestCase):
    def setUp(self):
        self.user = User.objects.create_user('learner', password='p')
        self.course, self.lessons = self.make_course()
        self.assessments = self.make_assessment(self.course, self.lessons)
        Enrollment.objects.create(user=self.user, course=self.course)
        self.complete_lessons(self.user, self.lessons)
        self.pass_assessment(self.user, self.assessments, 4)

    def test_issue_creates_certificate_and_event_and_pdf(self):
        cert = services.issue_certificate(self.user, self.course)
        self.assertEqual(cert.status, Certificate.Status.ACTIVE)
        self.assertTrue(cert.is_valid)
        self.assertTrue(CertificateEvent.objects.filter(certificate=cert, action='issued').exists())
        self.assertTrue(cert.pdf_file.name)  # PDF generated and stored

    def test_issue_is_idempotent(self):
        first = services.issue_certificate(self.user, self.course)
        second = services.issue_certificate(self.user, self.course)
        self.assertEqual(first.id, second.id)
        self.assertEqual(
            Certificate.objects.filter(user=self.user, course=self.course).count(), 1)

    def test_issue_syncs_profile_certification_record(self):
        cert = services.issue_certificate(self.user, self.course)

        learning_cert = LearningCertification.objects.get(
            track=self.course.track,
            title=f'{self.course.title} Certificate',
        )
        self.assertTrue(UserCertification.objects.filter(
            user=self.user,
            certification=learning_cert,
            credential_id=cert.credential_id,
        ).exists())

    def test_issue_blocks_when_ineligible(self):
        user2 = User.objects.create_user('partial', password='p')
        Enrollment.objects.create(user=user2, course=self.course)
        with self.assertRaises(services.CertificateNotEligible):
            services.issue_certificate(user2, self.course)
        self.assertFalse(Certificate.objects.filter(user=user2).exists())

    def test_verification_url_contains_credential_id(self):
        cert = services.issue_certificate(self.user, self.course)
        self.assertIn(cert.credential_id, cert.verification_url())
        self.assertIn('/verify/certificate/', cert.verification_url())


class RevocationReissueTests(CertificateFactoryMixin, TestCase):
    def setUp(self):
        self.user = User.objects.create_user('r', password='p')
        self.staff = User.objects.create_user('s', password='p', is_staff=True)
        self.course, self.lessons = self.make_course()
        self.assessments = self.make_assessment(self.course, self.lessons)
        Enrollment.objects.create(user=self.user, course=self.course)
        self.complete_lessons(self.user, self.lessons)
        self.pass_assessment(self.user, self.assessments, 4)

    def test_revoke_marks_status_and_logs(self):
        cert = services.issue_certificate(self.user, self.course)
        services.revoke_certificate(cert, performed_by=self.staff, reason='fraud')
        cert.refresh_from_db()
        self.assertEqual(cert.status, Certificate.Status.REVOKED)
        self.assertFalse(cert.is_valid)
        self.assertTrue(CertificateEvent.objects.filter(certificate=cert, action='revoked').exists())

    def test_reissue_supersedes_original(self):
        cert = services.issue_certificate(self.user, self.course)
        corrected = services.reissue_corrected_certificate(
            cert, performed_by=self.staff, reason='name typo')
        cert.refresh_from_db()
        self.assertEqual(cert.status, Certificate.Status.SUPERSEDED)
        self.assertEqual(corrected.status, Certificate.Status.ACTIVE)
        self.assertEqual(corrected.supersedes_id, cert.id)
        self.assertEqual(corrected.policy_version, cert.policy_version + 1)


class CertificateAPITests(CertificateFactoryMixin, TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('api', password='p')
        self.course, self.lessons = self.make_course()
        self.assessments = self.make_assessment(self.course, self.lessons)
        Enrollment.objects.create(user=self.user, course=self.course)

    def _authenticate(self):
        self.client.force_authenticate(user=self.user)

    def test_public_verify_unknown_returns_404(self):
        resp = self.client.get('/api/certificates/verify/doesnotexist/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(resp.data['found'])

    def test_issue_requires_auth(self):
        resp = self.client.post(f'/api/courses/{self.course.slug}/certificate/issue/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_issue_requires_eligibility(self):
        self._authenticate()
        resp = self.client.post(f'/api/courses/{self.course.slug}/certificate/issue/')
        self.assertEqual(resp.status_code, status.HTTP_412_PRECONDITION_FAILED)

    def test_issue_and_verify_flow(self):
        self._authenticate()
        self.complete_lessons(self.user, self.lessons)
        self.pass_assessment(self.user, self.assessments, 4)
        resp = self.client.post(f'/api/courses/{self.course.slug}/certificate/issue/')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        public_id = resp.data['public_id']

        # Public verification works without auth and hides private fields.
        self.client.force_authenticate(user=None)
        vresp = self.client.get(f'/api/certificates/verify/{public_id}/')
        self.assertEqual(vresp.status_code, status.HTTP_200_OK)
        self.assertTrue(vresp.data['valid'])
        self.assertNotIn('email', vresp.data)
        self.assertNotIn('user', vresp.data)

    def test_download_is_owner_restricted(self):
        self.complete_lessons(self.user, self.lessons)
        self.pass_assessment(self.user, self.assessments, 4)
        cert = services.issue_certificate(self.user, self.course)
        intruder = User.objects.create_user('intruder', password='p')
        self.client.force_authenticate(user=intruder)
        resp = self.client.get(f'/api/certificates/{cert.public_id}/download/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.user)
        ok = self.client.get(f'/api/certificates/{cert.public_id}/download/')
        self.assertEqual(ok.status_code, status.HTTP_200_OK)
        self.assertEqual(ok.get('Content-Type'), 'application/pdf')

    def test_my_certificates_lists_only_mine(self):
        self.complete_lessons(self.user, self.lessons)
        self.pass_assessment(self.user, self.assessments, 4)
        services.issue_certificate(self.user, self.course)
        other = User.objects.create_user('other2', password='p')
        self.client.force_authenticate(user=other)
        resp = self.client.get('/api/me/certificates/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 0)

    def test_revoked_certificate_fails_public_verification(self):
        self.complete_lessons(self.user, self.lessons)
        self.pass_assessment(self.user, self.assessments, 4)
        cert = services.issue_certificate(self.user, self.course)
        staff = User.objects.create_user('staff2', password='p', is_staff=True)
        services.revoke_certificate(cert, performed_by=staff, reason='integrity')
        resp = self.client.get(f'/api/certificates/verify/{cert.public_id}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(resp.data['valid'])
        self.assertTrue(resp.data['revoked'])

    def test_public_verify_exposes_only_safe_fields(self):
        self.complete_lessons(self.user, self.lessons)
        self.pass_assessment(self.user, self.assessments, 4)
        cert = services.issue_certificate(self.user, self.course)
        resp = self.client.get(f'/api/certificates/verify/{cert.public_id}/')
        allowed = {
            'valid', 'found', 'public_id', 'credential_id', 'student_name',
            'course_title', 'issued_at', 'completion_verified_at', 'status',
            'revoked', 'superseded', 'issuer', 'verification_url',
            'qr_data_url', 'final_score', 'kind',
        }
        self.assertTrue(set(resp.data.keys()) <= allowed, set(resp.data.keys()) - allowed)
        self.assertNotIn('email', resp.data)
        self.assertNotIn('user', resp.data)

    def test_verify_accepts_credential_id(self):
        self.complete_lessons(self.user, self.lessons)
        self.pass_assessment(self.user, self.assessments, 4)
        cert = services.issue_certificate(self.user, self.course)
        resp = self.client.get(f'/api/certificates/verify/{cert.credential_id}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['valid'])

    def test_png_download_is_owner_restricted(self):
        self.complete_lessons(self.user, self.lessons)
        self.pass_assessment(self.user, self.assessments, 4)
        cert = services.issue_certificate(self.user, self.course)
        self.client.force_authenticate(user=self.user)
        ok = self.client.get(f'/api/certificates/{cert.public_id}/download/?format=png')
        self.assertEqual(ok.status_code, status.HTTP_200_OK)
        self.assertEqual(ok.get('Content-Type'), 'image/png')
        # FileResponse streams its body; join it before asserting the magic bytes.
        self.assertTrue(b''.join(ok.streaming_content).startswith(b'\x89PNG'))
