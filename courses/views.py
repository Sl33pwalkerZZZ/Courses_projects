from pathlib import Path
from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.utils.cache import patch_vary_headers
from rest_framework import generics, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from reviews.summaries import with_review_summary

from .media import private_lesson_file
from .models import Course, Lesson, LessonImage
from .permissions import can_access_lesson, can_preview_course
from .serializers import CourseDetailSerializer, RatedCourseListSerializer, LessonDetailSerializer


class CourseListView(generics.ListAPIView):
    queryset = with_review_summary(Course.objects.filter(is_published=True).select_related("direction", "author", "content_import", "studio_settings"))
    serializer_class = RatedCourseListSerializer
    permission_classes = [permissions.AllowAny]


class CourseDetailView(generics.RetrieveAPIView):
    queryset = with_review_summary(
        Course.objects.filter(is_published=True).select_related("direction", "author", "content_import", "studio_settings").prefetch_related("modules__lessons")
    )
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


class LessonDetailView(generics.RetrieveAPIView):
    queryset = Lesson.objects.select_related("module__course").prefetch_related(
        Prefetch("images", queryset=LessonImage.objects.select_related("studio_description")), "assignments",
    )
    serializer_class = LessonDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'private, no-store'
        patch_vary_headers(response, ['Authorization', 'Cookie'])
        return response

    def get_object(self):
        lesson = super().get_object()
        if not can_access_lesson(self.request.user, lesson):
            raise PermissionDenied("Нет доступа к этому курсу — сначала запишитесь на курс.")
        return lesson


class LessonImageView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    # JWT for React, and the existing Django session for authorized Admin previews.
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Cache-Control"] = "private, no-store"
        response["X-Content-Type-Options"] = "nosniff"
        patch_vary_headers(response, ["Authorization", "Cookie"])
        return response

    def get(self, request, pk=None, filename=None):
        images = LessonImage.objects.select_related("lesson__module__course")
        if filename is not None:
            # Only registered lesson images are served; submissions/unknown files stay private.
            private_lesson_file(settings.MEDIA_ROOT, filename)
            matches = list(images.filter(image=filename))
            if not matches:
                raise Http404("Image not found.")
            # Stored filenames are not unique: a shared file is accessible only
            # if at least one of its registered lessons is accessible to this user.
            image = matches[0]
            for candidate in matches:
                if can_access_lesson(request.user, candidate.lesson):
                    image = candidate
                    break
        else:
            image = get_object_or_404(images, pk=pk)
        if not can_access_lesson(request.user, image.lesson):
            raise PermissionDenied("Нет доступа к этому курсу — сначала запишитесь на курс.")
        file_path = private_lesson_file(settings.MEDIA_ROOT, image.image.name)
        try:
            response = FileResponse(file_path.open("rb"))
        except (FileNotFoundError, IsADirectoryError, PermissionError):
            raise Http404("Image not found.")
        return response


class InstructorCoursePreviewView(generics.RetrieveAPIView):
    """Read-only staff preview; never adds enrollment or discloses draft quiz keys."""
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CourseDetailSerializer
    lookup_field = "slug"
    queryset = with_review_summary(
        Course.objects.select_related("direction", "author", "content_import", "studio_settings")
        .prefetch_related("modules__lessons")
    )

    def get_object(self):
        course = super().get_object()
        if not can_preview_course(self.request.user, course):
            raise PermissionDenied("You do not have permission to preview this course.")
        return course

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Cache-Control"] = "private, no-store"
        patch_vary_headers(response, ["Authorization", "Cookie"])
        return response


class LessonAttachmentView(LessonImageView):
    """Same JWT/session permission boundary as images; no storage URL exposed."""
    def get(self, request, pk):
        from .attachments import attachments_ready
        from .models import LessonAttachment
        from rest_framework.exceptions import APIException
        if not attachments_ready():
            error = APIException('Lesson attachments require the pending courses migration.')
            error.status_code = 503
            raise error
        attachment = get_object_or_404(LessonAttachment.objects.select_related('lesson__module__course'), pk=pk)
        if not can_access_lesson(request.user, attachment.lesson):
            raise PermissionDenied('No access to this lesson attachment.')
        if not attachment.file.name.startswith('lessons/attachments/'):
            raise Http404('Attachment not found.')
        path = private_lesson_file(settings.MEDIA_ROOT, attachment.file.name)
        if not path.is_relative_to((Path(settings.MEDIA_ROOT) / 'lessons/attachments').resolve()):
            raise Http404('Attachment not found.')
        try:
            return FileResponse(path.open('rb'), as_attachment=attachment.kind == 'srt',
                filename=attachment.filename, content_type=attachment.mime_type)
        except (OSError, ValueError):
            raise Http404('Attachment not found.')
