from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from progress.models import Enrollment
from reviews.summaries import with_review_summary

from .models import Course, Lesson
from .serializers import CourseDetailSerializer, RatedCourseListSerializer, LessonDetailSerializer


class CourseListView(generics.ListAPIView):
    queryset = with_review_summary(Course.objects.filter(is_published=True).select_related("direction", "author"))
    serializer_class = RatedCourseListSerializer
    permission_classes = [permissions.AllowAny]


class CourseDetailView(generics.RetrieveAPIView):
    queryset = with_review_summary(
        Course.objects.filter(is_published=True).select_related("direction", "author").prefetch_related("modules__lessons")
    )
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


class LessonDetailView(generics.RetrieveAPIView):
    queryset = Lesson.objects.select_related("module__course").prefetch_related("images", "assignments")
    serializer_class = LessonDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        lesson = super().get_object()
        is_enrolled = Enrollment.objects.filter(
            student=self.request.user, course=lesson.module.course
        ).exists()
        if not is_enrolled:
            raise PermissionDenied("Нет доступа к этому курсу — сначала запишитесь на курс.")
        return lesson
