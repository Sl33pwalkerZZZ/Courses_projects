from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, Lesson, Module

from .models import Enrollment, LessonProgress
from .serializers import EnrollmentProgressSerializer, EnrollmentSerializer


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
        course = get_object_or_404(Course, slug=slug, is_published=True)
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
        progress.completed_at = timezone.now()
        progress.save(update_fields=["completed_at"])
        return Response({"lesson_id": lesson.id, "completed_at": progress.completed_at})
