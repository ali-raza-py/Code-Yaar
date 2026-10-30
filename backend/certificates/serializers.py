from rest_framework import serializers

from .models import Certificate
from .qrutil import qr_data_url


class CertificateSummarySerializer(serializers.ModelSerializer):
    """The learner's own view of an issued certificate."""
    course_slug = serializers.CharField(source='course.slug', read_only=True)
    verification_url = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()
    png_url = serializers.SerializerMethodField()
    qr_data_url = serializers.SerializerMethodField()
    is_valid = serializers.BooleanField(read_only=True)
    issuer = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = [
            'id', 'public_id', 'credential_id', 'student_name', 'course_title',
            'course', 'course_slug', 'issued_at', 'completion_verified_at',
            'final_score', 'status', 'is_valid', 'verification_url', 'pdf_url',
            'png_url', 'qr_data_url', 'issuer',
        ]

    def get_issuer(self, obj):
        return 'Code Yaar Academy'

    def get_verification_url(self, obj):
        return obj.verification_url()

    def get_pdf_url(self, obj):
        request = self.context.get('request')
        path = f'/api/certificates/{obj.public_id}/download/?format=pdf'
        return request.build_absolute_uri(path) if request else path

    def get_png_url(self, obj):
        request = self.context.get('request')
        path = f'/api/certificates/{obj.public_id}/download/?format=png'
        return request.build_absolute_uri(path) if request else path

    def get_qr_data_url(self, obj):
        return qr_data_url(obj.verification_url())


class PublicVerificationSerializer(serializers.ModelSerializer):
    """Minimal, privacy-safe payload for public verification.

    Never exposes email, account id, assessment answers, or admin notes.
    """
    valid = serializers.BooleanField(source='is_valid', read_only=True)
    revoked = serializers.SerializerMethodField()
    superseded = serializers.SerializerMethodField()

    issuer = serializers.SerializerMethodField()
    verification_url = serializers.SerializerMethodField()
    qr_data_url = serializers.SerializerMethodField()
    final_score = serializers.FloatField(read_only=True)

    class Meta:
        model = Certificate
        fields = [
            'valid', 'credential_id', 'student_name', 'course_title',
            'issued_at', 'completion_verified_at', 'status',
            'revoked', 'superseded', 'issuer', 'verification_url',
            'qr_data_url', 'final_score',
        ]

    def get_issuer(self, obj):
        return 'Code Yaar Academy'

    def get_verification_url(self, obj):
        return obj.verification_url()

    def get_qr_data_url(self, obj):
        if not obj.is_valid:
            return ''
        return qr_data_url(obj.verification_url())

    def get_revoked(self, obj):
        return obj.status == Certificate.Status.REVOKED

    def get_superseded(self, obj):
        return obj.status == Certificate.Status.SUPERSEDED


class EligibilitySerializer(serializers.Serializer):
    """Read-only eligibility snapshot for a course, shown before starting."""
    eligible = serializers.BooleanField()
    final_score = serializers.FloatField(allow_null=True)
    requirements = serializers.ListField(child=serializers.DictField())
    lessons_required = serializers.BooleanField()
    lessons_completed = serializers.IntegerField()
    lessons_total = serializers.IntegerField()
    assessment_required = serializers.BooleanField()
    assessment_items = serializers.IntegerField()
    assessment_passed = serializers.IntegerField()
