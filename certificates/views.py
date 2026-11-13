from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course
from studio.permissions import moderator
from .models import Certificate
from .services import confirmed_certificate_name, eligibility, issue_certificate, revoke_certificate, valid_name


def certificate_data(certificate):
    return {'verification_code': certificate.verification_code, 'course_id': certificate.course_id,
            'course_title': certificate.course_title, 'learner_name': certificate.learner_name,
            'issuer_name': certificate.issuer_name, 'issued_at': certificate.issued_at,
            'revoked': bool(certificate.revoked_at), 'download_url': f'/api/certificates/{certificate.verification_code}/download/',
            'verification_url': f'/certificates/verify/{certificate.verification_code}',
            'verification_available': bool(getattr(settings, 'CERTIFICATES_ENABLED', False) and certificate.evidence and certificate.learner_name)}


class PrivateCertificateReadView(APIView):
    """Read issued snapshots without enabling issuance or public verification."""
    permission_classes = [IsAuthenticated]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'private, no-store'
        return response


class CertificateView(PrivateCertificateReadView):
    """Feature-gated eligibility, public verification and mutation endpoints."""
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if not getattr(settings, 'CERTIFICATES_ENABLED', False):
            raise NotFound('Certificates are not enabled.')


class MyCertificateName(APIView):
    """Student-owned name draft and explicit certificate-name confirmation."""
    permission_classes = [IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if request.user.role != 'student':
            raise PermissionDenied('Only a student can manage their certificate name.')

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'private, no-store'
        return response

    @staticmethod
    def state(user):
        stored_name = user.certificate_name
        try:
            display_name = valid_name(stored_name) if stored_name else ''
        except ValidationError:
            display_name = ''
        confirmed = confirmed_certificate_name(user) is not None
        return {
            'learner_name': display_name,
            'confirmed': confirmed,
            'confirmed_at': user.certificate_name_confirmed_at if confirmed else None,
        }

    def get(self, request):
        return Response(self.state(request.user))

    @transaction.atomic
    def put(self, request):
        name = valid_name(request.data.get('learner_name'))
        user = get_object_or_404(get_user_model().objects.select_for_update(), pk=request.user.pk, is_active=True)
        if user.role != 'student':
            raise PermissionDenied('Only a student can manage their certificate name.')
        if name != user.certificate_name:
            user.certificate_name = name
            user.certificate_name_confirmed_at = None
            user.save(update_fields=['certificate_name', 'certificate_name_confirmed_at'])
        return Response(self.state(user))

    @transaction.atomic
    def post(self, request):
        name = valid_name(request.data.get('learner_name'))
        if request.data.get('confirmation') is not True:
            raise ValidationError({'confirmation': 'Explicitly confirm the displayed certificate name.'})
        user = get_object_or_404(get_user_model().objects.select_for_update(), pk=request.user.pk, is_active=True)
        if user.role != 'student':
            raise PermissionDenied('Only a student can manage their certificate name.')
        if not user.certificate_name or name != user.certificate_name:
            raise ValidationError({'learner_name': 'Save and review this exact name before confirming it.'})
        user.certificate_name_confirmed_at = timezone.now()
        user.save(update_fields=['certificate_name_confirmed_at'])
        return Response(self.state(user))


class CourseCertificateStatus(CertificateView):
    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk, is_published=True)
        result = eligibility(request.user, course)
        certificate = Certificate.objects.filter(student=request.user, course=course).first()
        return Response({'enabled': True, 'eligible': result['eligible'], 'requirements': result['requirements'], 'issuance': 'administrator', 'certificate': certificate_data(certificate) if certificate else None})


class MyCertificates(PrivateCertificateReadView):
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


class DownloadCertificate(PrivateCertificateReadView):
    def get(self, request, code):
        certificate = get_object_or_404(Certificate, verification_code=code)
        if certificate.student_id != request.user.pk and not moderator(request.user):
            raise NotFound()
        if certificate.revoked_at or not certificate.evidence:
            raise PermissionDenied('A revoked or unverified certificate cannot be downloaded.')
        from .pdf import CertificatePDFUnavailable, render_certificate
        # Verification is optional, never derived from an untrusted request Host.
        from urllib.parse import urlsplit
        url = None
        base = getattr(settings, 'CERTIFICATE_PUBLIC_ORIGIN', '').rstrip('/')
        if getattr(settings, 'CERTIFICATES_ENABLED', False) and base:
            try:
                parsed = urlsplit(base)
                valid = (parsed.scheme in ('http', 'https') and parsed.hostname
                         and not parsed.username and not parsed.password
                         and not parsed.path and not parsed.query and not parsed.fragment
                         and '\\' not in base and not any(char.isspace() for char in base))
                parsed.port  # Invalid ports are not valid trusted origins.
                if valid:
                    url = base + '/certificates/verify/' + certificate.verification_code
            except ValueError:
                pass  # Omit optional verification instead of inventing an origin.
        try:
            pdf = render_certificate(certificate, url)
        except (CertificatePDFUnavailable, ValueError):
            return Response({'code': 'certificate_pdf_unavailable', 'detail': 'Certificate PDF deployment configuration is incomplete.'}, status=503)
        response = HttpResponse(pdf, content_type='application/pdf')
        disposition = 'inline' if request.query_params.get('preview') == '1' else 'attachment'
        response['Content-Disposition'] = f'{disposition}; filename="certificate-{certificate.verification_code}.pdf"'
        response['X-Content-Type-Options'] = 'nosniff'
        response['Cache-Control'] = 'private, no-store'
        return response


class IssueCertificate(CertificateView):
    def post(self, request):
        if not moderator(request.user):
            raise PermissionDenied('Administrator access required.')
        if 'learner_name' in request.data:
            raise ValidationError({'learner_name': 'The certificate name must be confirmed by the learner and cannot be overridden here.'})
        if request.data.get('confirmation') is not True:
            raise ValidationError({'confirmation': 'Confirm review of the learner-confirmed name and issuer identity.'})
        for key in ('student_id', 'course_id'):
            value = request.data.get(key)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValidationError({key: 'Provide a positive integer ID.'})
        student = get_object_or_404(get_user_model(), pk=request.data.get('student_id'), is_active=True)
        course = get_object_or_404(Course, pk=request.data.get('course_id'))
        certificate, created = issue_certificate(administrator=request.user, student=student, course_id=course.pk)
        return Response(certificate_data(certificate), status=201 if created else 200)


class RevokeCertificate(CertificateView):
    def post(self, request, code):
        if not moderator(request.user):
            raise PermissionDenied('Administrator access required.')
        certificate = get_object_or_404(Certificate, verification_code=code)
        certificate = revoke_certificate(administrator=request.user, certificate=certificate, reason=request.data.get('reason'))
        return Response(certificate_data(certificate))
