"""Certificate API views.

Access model:
- Eligibility & issuance require an authenticated owner; grading is re-checked
  server-side, so a learner can never self-issue by editing a request.
- Download is restricted to the certificate owner (or staff).
- Public verification returns only minimal, privacy-safe fields.
"""

from django.http import FileResponse
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from learning.models import Course

from . import services
from .models import Certificate
from .serializers import (
    CertificateSummarySerializer, EligibilitySerializer,
    PublicVerificationSerializer,
)


class _IsOwnerOrStaff(permissions.BasePermission):
    """Object-level guard so only the learner (or staff) touches a certificate."""

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return obj.user == request.user


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_certificates(request):
    """List the current user's issued certificates."""
    certs = (
        Certificate.objects.filter(user=request.user)
        .select_related('course')
        .order_by('-issued_at')
    )
    return Response(CertificateSummarySerializer(certs, many=True, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def course_eligibility(request, slug):
    """Show the learner their real certification progress for a course."""
    course = Course.objects.filter(slug=slug, is_active=True).first()
    if not course:
        return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
    result = services.check_eligibility(request.user, course)
    return Response(EligibilitySerializer(result.to_dict()).data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def issue_certificate(request, slug):
    """Issue a certificate after the server re-verifies completion.

    Idempotent: a second call for an eligible learner returns the existing
    certificate rather than a duplicate.
    """
    course = Course.objects.filter(
        slug=slug, is_active=True, is_published=True
    ).first()
    if not course:
        return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        certificate = services.issue_certificate(request.user, course)
    except services.CertificateNotEligible as exc:
        return Response(
            {
                'detail': 'Certificate requirements are not yet met.',
                'eligibility': exc.result.to_dict(),
            },
            status=status.HTTP_412_PRECONDITION_FAILED,
        )

    return Response(
        CertificateSummarySerializer(certificate, context={'request': request}).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, _IsOwnerOrStaff])
def download_certificate(request, public_id):
    """Serve the certificate PDF to its owner (or staff)."""
    certificate = Certificate.objects.filter(public_id=public_id).first()
    if not certificate:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    # Function-based views do not run object permissions automatically, so the
    # owner/staff check is applied explicitly here.
    if not (request.user == certificate.user or request.user.is_staff):
        return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)

    from .models import CertificateEvent
    CertificateEvent.objects.create(
        certificate=certificate,
        action=CertificateEvent.Action.DOWNLOADED,
        performed_by=request.user if request.user.is_authenticated else None,
        reason='',
        snapshot=services._snapshot(certificate),
    )

    if certificate.pdf_file:
        return FileResponse(
            certificate.pdf_file.open('rb'),
            as_attachment=True,
            filename=f'code-yaar-{certificate.credential_id}.pdf',
            content_type='application/pdf',
        )

    # PDF missing (e.g. generation failed at issuance) — render on demand.
    from .pdf import render_certificate_pdf
    buf = render_certificate_pdf(certificate)
    return FileResponse(
        buf, as_attachment=True,
        filename=f'code-yaar-{certificate.credential_id}.pdf',
        content_type='application/pdf',
    )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def verify_certificate(request, public_id):
    """Public verification. Query Django and reflect the real record only."""
    certificate = Certificate.objects.filter(public_id=public_id).first()
    if not certificate:
        return Response(
            {'valid': False, 'found': False,
             'detail': 'No certificate matches this identifier.'},
            status=status.HTTP_404_NOT_FOUND,
        )
    data = PublicVerificationSerializer(certificate).data
    data['found'] = True
    data['public_id'] = certificate.public_id
    return Response(data)
