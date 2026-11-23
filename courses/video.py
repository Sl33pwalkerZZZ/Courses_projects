"""Private native playback: short-lived cookie grants and bounded range streaming."""
import time
import asyncio
import stat
from django.core.handlers.asgi import ASGIRequest
import hashlib
import secrets
from datetime import datetime, timezone as datetime_timezone
from django.utils import timezone
import re
from pathlib import Path
from django.conf import settings
from django.core import signing
from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.crypto import constant_time_compare
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied, APIException
from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import LessonAttachment, LessonPlaybackGrant
from .permissions import can_access_lesson
from .media import private_lesson_file

SALT = 'courses.video-playback.v1'

def cookie_name(pk, grant_pk=None):
    # Distinct names also prevent a legacy parent-path cookie shadowing a new one.
    return f'lesson_playback_{pk}' if grant_pk is None else f'lesson_playback_{pk}_{grant_pk}'

def ttl():
    return min(900, max(30, int(getattr(settings, 'LESSON_VIDEO_GRANT_SECONDS', 300))))

def grants_ready():
    if LessonPlaybackGrant._meta.db_table not in connection.introspection.table_names():
        error = APIException('Video playback requires the pending courses migration.')
        error.status_code = 503
        raise error


def attachment(pk):
    return get_object_or_404(LessonAttachment.objects.select_related('lesson__module__course'), pk=pk, kind__in=['video', 'vtt'])

def file_chunks(stream, start, length):
    """Bounded WSGI iterator; closing it releases the open descriptor."""
    try:
        stream.seek(start)
        remaining = length
        while remaining:
            block = stream.read(min(64 * 1024, remaining))
            if not block:
                break
            remaining -= len(block)
            yield block
    finally:
        stream.close()


async def async_file_chunks(stream, start, length):
    """ASGI must receive an async iterator, avoiding Django's buffering fallback."""
    try:
        await asyncio.to_thread(stream.seek, start)
        remaining = length
        while remaining:
            block = await asyncio.to_thread(stream.read, min(64 * 1024, remaining))
            if not block:
                break
            remaining -= len(block)
            yield block
    finally:
        await asyncio.to_thread(stream.close)


class PlaybackGrantView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'private, no-store'
        response['Referrer-Policy'] = 'no-referrer'
        return response

    def get_authenticators(self):
        return [] if self.request.method == 'DELETE' else super().get_authenticators()

    def get_permissions(self):
        return [permissions.AllowAny()] if self.request.method == 'DELETE' else super().get_permissions()

    def delete(self, request, pk):
        grants_ready()
        try:
            nonce = signing.loads(request.data.get('revoke_token', ''), salt=SALT+'.revoke', max_age=ttl())
            digest = hashlib.sha256(nonce.encode()).hexdigest()
        except (signing.BadSignature, TypeError, AttributeError):
            raise PermissionDenied('Invalid revocation proof.')
        grant = LessonPlaybackGrant.objects.filter(token_hash=digest, attachment_id=pk).first()
        if grant:
            LessonPlaybackGrant.objects.filter(pk=grant.pk, revoked_at=None).update(revoked_at=timezone.now())
        response = Response(status=204)
        # Only this grant's slot is cleared, even for an already-revoked nonce.
        # Never clear the legacy shared cookie: another old player may own it.
        if grant:
            response.delete_cookie(cookie_name(pk, grant.pk),
                                   path=reverse('lesson-playback-scoped', args=[pk, grant.pk]), samesite='Strict')
        response['Cache-Control'] = 'private, no-store'
        return response

    def post(self, request, pk):
        grants_ready()
        row = attachment(pk)
        if not can_access_lesson(request.user, row.lesson):
            raise PermissionDenied('No access to this lesson.')
        lifetime = ttl()
        if request.auth is not None and hasattr(request.auth, 'get'):
            lifetime = min(lifetime, max(0, int(request.auth.get('exp', 0))-int(time.time())))
        if lifetime <= 0:
            raise PermissionDenied('Session expired.')
        expires = int(time.time()) + lifetime
        nonce = secrets.token_urlsafe(32)
        grant = LessonPlaybackGrant.objects.create(token_hash=hashlib.sha256(nonce.encode()).hexdigest(), user=request.user, attachment=row, expires_at=datetime.fromtimestamp(expires, datetime_timezone.utc))
        path = reverse('lesson-playback-scoped', args=[pk, grant.pk])
        value = signing.dumps({'gid': grant.pk, 'nonce': nonce, 'uid': request.user.pk, 'pk': pk, 'sha': row.sha256,
                               'exp': expires, 'auth': request.user.get_session_auth_hash()}, salt=SALT)
        response = Response({'url': path, 'expires_in': lifetime, 'expires_at': expires, 'revoke_token': signing.dumps(nonce, salt=SALT+'.revoke')})
        response.set_cookie(cookie_name(pk, grant.pk), value, max_age=lifetime, httponly=True,
                            secure=request.is_secure(), samesite='Strict', path=path)
        response['Cache-Control'] = 'private, no-store'
        return response

class PlaybackView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    def finalize_response(self, request, response, *args, **kwargs):
        return self.media_headers(super().finalize_response(request, response, *args, **kwargs))

    def head(self, request, pk, grant_pk=None):
        return self.get(request, pk, grant_pk)
    def get(self, request, pk, grant_pk=None):
        grants_ready()
        row = attachment(pk)
        try:
            data = signing.loads(request.COOKIES.get(cookie_name(pk, grant_pk), ''), salt=SALT, max_age=ttl())
            user = get_user_model().objects.get(pk=data['uid'], is_active=True)
            grants = LessonPlaybackGrant.objects.all()
            if grant_pk is not None:
                grants = grants.filter(pk=grant_pk)
            slot_matches = data.get('gid') == grant_pk
            valid = (slot_matches and grants.filter(token_hash=hashlib.sha256(data['nonce'].encode()).hexdigest(), user=user, attachment=row, revoked_at=None, expires_at__gt=timezone.now()).exists() and data['exp'] > time.time() and data['pk'] == pk and data['sha'] == row.sha256 and
                     constant_time_compare(data['auth'], user.get_session_auth_hash()))
        except (signing.BadSignature, KeyError, ValueError, TypeError, get_user_model().DoesNotExist):
            valid = False
        if not valid or not can_access_lesson(user, row.lesson):
            raise PermissionDenied('Playback authorization expired or access denied.')
        if not row.file.name.startswith('lessons/attachments/'):
            raise Http404
        path = private_lesson_file(settings.MEDIA_ROOT, row.file.name)
        if not path.is_relative_to((Path(settings.MEDIA_ROOT) / 'lessons/attachments').resolve()):
            raise Http404
        try:
            file_stat = path.stat()
            if not stat.S_ISREG(file_stat.st_mode):
                raise Http404
            size = file_stat.st_size
        except OSError:
            raise Http404
        start, end, status = 0, size - 1, 200
        header = request.headers.get('Range') if request.method == 'GET' else None
        if header:
            match = re.fullmatch(r'bytes=(\d*)-(\d*)', header)
            try:
                if not match or not any(match.groups()):
                    raise ValueError
                first, last = match.groups()
                if first:
                    start = int(first)
                    end = min(int(last), size-1) if last else size-1
                else:
                    suffix = int(last)
                    if suffix <= 0:
                        raise ValueError
                    start = max(0, size-suffix)
                if start >= size or end < start:
                    raise ValueError
                status = 206
            except ValueError:
                response = HttpResponse(status=416)
                response['Content-Range'] = f'bytes */{size}'
                return self.media_headers(response)
        length = end-start+1
        try:
            stream = path.open('rb')
        except OSError:
            raise Http404
        if request.method == 'HEAD':
            stream.close()
            response = HttpResponse(status=status, content_type=row.mime_type)
        else:
            iterator = (async_file_chunks(stream, start, length)
                        if isinstance(request._request, ASGIRequest)
                        else file_chunks(stream, start, length))
            response = StreamingHttpResponse(iterator, status=status, content_type=row.mime_type)
            # Also close descriptors when a response is abandoned before iteration.
            response._resource_closers.append(stream.close)
        response['Content-Length'] = str(length)
        if status == 206:
            response['Content-Range'] = f'bytes {start}-{end}/{size}'
        return self.media_headers(response)
    @staticmethod
    def media_headers(response):
        response['Accept-Ranges'] = 'bytes'
        response['Cache-Control'] = 'private, no-store'
        response['X-Content-Type-Options'] = 'nosniff'
        response['Referrer-Policy'] = 'no-referrer'
        response['Vary'] = 'Cookie'
        return response
