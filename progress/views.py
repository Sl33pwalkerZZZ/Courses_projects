from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, Lesson, Module

from .models import Enrollment, EnrollmentRequest, LessonProgress
from .activity import student_activity
from .serializers import (
    EnrollmentProgressSerializer, EnrollmentRequestCreateSerializer,
    EnrollmentRequestSerializer, EnrollmentSerializer,
)
from .services import submit_enrollment_request


class MyEnrollmentRequestsView(generics.ListAPIView):
    serializer_class = EnrollmentRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EnrollmentRequest.objects.filter(student=self.request.user).select_related(
            "course", "course__direction", "course__author",
        )


class MyActivityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(student_activity(request.user))


class CourseEnrollmentRequestsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug, is_published=True)
        serializer = EnrollmentRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            application = submit_enrollment_request(
                student=request.user, course=course, message=serializer.validated_data["message"],
            )
        except ValidationError as error:
            return Response(
                {"code": getattr(error, "code", "invalid_request"), "detail": " ".join(error.messages)},
                status=status.HTTP_409_CONFLICT,
            )
        except IntegrityError:
            # The partial unique constraint also handles concurrent submissions.
            if EnrollmentRequest.objects.filter(student=request.user, course=course, status="pending").exists():
                return Response(
                    {"code": "duplicate_pending", "detail": "You already have a pending application."},
                    status=status.HTTP_409_CONFLICT,
                )
            raise
        return Response(EnrollmentRequestSerializer(application).data, status=status.HTTP_201_CREATED)


class MyEnrollmentsView(generics.ListAPIView):
    serializer_class = EnrollmentProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        modules = Module.objects.order_by("order", "pk").prefetch_related(
            Prefetch("lessons", queryset=Lesson.objects.order_by("order", "pk"))
        )
        return (
            Enrollment.objects.filter(student=self.request.user)
            .select_related("course", "course__direction", "course__author")
            .prefetch_related(
                Prefetch("course__modules", queryset=modules),
                Prefetch(
                    "lesson_progress",
                    queryset=LessonProgress.objects.filter(completed_at__isnull=False).only(
                        "enrollment_id", "lesson_id", "completed_at"
                    ),
                ),
            )
        )


class EnrollView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        with transaction.atomic():
            course = get_object_or_404(Course.objects.select_for_update(), slug=slug, is_published=True)
            enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
            if enrollment is None and course.enrollment_mode == Course.EnrollmentMode.APPROVAL:
                return Response(
                    {"code": "approval_required", "detail": "Request enrollment and wait for approval."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            created = enrollment is None
            if created:
                enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class CompleteLessonView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        try:
            enrollment = Enrollment.objects.get(student=request.user, course=lesson.module.course)
        except Enrollment.DoesNotExist:
            raise PermissionDenied("Нет доступа к этому курсу — сначала запишитесь на курс.")

        progress, _ = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
        if progress.completed_at is None:
            # Preserve the first completion time, including concurrent retries.
            LessonProgress.objects.filter(pk=progress.pk, completed_at__isnull=True).update(
                completed_at=timezone.now(),
            )
            progress.refresh_from_db(fields=["completed_at"])
        return Response({"lesson_id": lesson.id, "completed_at": progress.completed_at})
