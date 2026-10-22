from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course
from studio.permissions import moderator
from .models import Certificate
from .services import eligibility, issue_certificate, revoke_certificate


def certificate_data(certificate):
    return {'verification_code': certificate.verification_code, 'course_id': certificate.course_id,
            'course_title': certificate.course_title, 'learner_name': certificate.learner_name,
            'issuer_name': certificate.issuer_name, 'issued_at': certificate.issued_at,
            'revoked': bool(certificate.revoked_at), 'download_url': f'/api/certificates/{certificate.verification_code}/download/',
            'verification_url': f'/certificates/verify/{certificate.verification_code}'}


class CertificateView(APIView):
    permission_classes = [IsAuthenticated]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'private, no-store'
        return response

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if not getattr(settings, 'CERTIFICATES_ENABLED', False):
            raise NotFound('Certificates are not enabled.')


class CourseCertificateStatus(CertificateView):
    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk, is_published=True)
        result = eligibility(request.user, course)
        certificate = Certificate.objects.filter(student=request.user, course=course).first()
        return Response({'enabled': True, 'eligible': result['eligible'], 'requirements': result['requirements'], 'issuance': 'administrator', 'certificate': certificate_data(certificate) if certificate else None})


class MyCertificates(CertificateView):
    def get(self, request):
        return Response([certificate_data(item) for item in Certificate.objects.filter(student=request.user).order_by('-issued_at')])


class VerifyCertificate(CertificateView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, code):
        certificate = get_object_or_404(Certificate, verification_code=code)
        # Do not certify legacy rows with no captured eligibility evidence.
        if not certificate.evidence or not certificate.learner_name:
            raise NotFound('Certificate verification is unavailable.')
        return Response({'verification_code': certificate.verification_code,
                         'status': 'revoked' if certificate.revoked_at else 'valid',
                         'learner_initials': ' '.join(word[0] + '.' for word in certificate.learner_name.split()),
                         'course_title': certificate.course_title, 'issuer_name': certificate.issuer_name,
                         'issued_at': certificate.issued_at, 'revoked_at': certificate.revoked_at})


class DownloadCertificate(CertificateView):
    def get(self, request, code):
        certificate = get_object_or_404(Certificate, verification_code=code)
        if certificate.student_id != request.user.pk and not moderator(request.user):
            raise NotFound()
        if certificate.revoked_at or not certificate.evidence:
            raise PermissionDenied('A revoked or unverified certificate cannot be downloaded.')
        from .pdf import CertificatePDFUnavailable, render_certificate
        base = getattr(settings, 'CERTIFICATE_PUBLIC_ORIGIN', '').rstrip('/')
        if not base:
            raise PermissionDenied('A trusted public verification origin must be configured before downloading.')
        url = base + '/certificates/verify/' + certificate.verification_code
        try:
            pdf = render_certificate(certificate, url)
        except (CertificatePDFUnavailable, ValueError):
            return Response({'code': 'certificate_pdf_unavailable', 'detail': 'Certificate PDF deployment configuration is incomplete.'}, status=503)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="certificate-{certificate.verification_code}.pdf"'
        response['Cache-Control'] = 'private, no-store'
        return response


class IssueCertificate(CertificateView):
    def post(self, request):
        if not moderator(request.user):
            raise PermissionDenied('Administrator access required.')
        for key in ('student_id', 'course_id'):
            value = request.data.get(key)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValidationError({key: 'Provide a positive integer ID.'})
        student = get_object_or_404(get_user_model(), pk=request.data.get('student_id'), is_active=True)
        course = get_object_or_404(Course, pk=request.data.get('course_id'))
        certificate, created = issue_certificate(administrator=request.user, student=student, course_id=course.pk, learner_name=request.data.get('learner_name'))
        return Response(certificate_data(certificate), status=201 if created else 200)


class RevokeCertificate(CertificateView):
    def post(self, request, code):
        if not moderator(request.user):
            raise PermissionDenied('Administrator access required.')
        certificate = get_object_or_404(Certificate, verification_code=code)
        certificate = revoke_certificate(administrator=request.user, certificate=certificate, reason=request.data.get('reason'))
        return Response(certificate_data(certificate))
