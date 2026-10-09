from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Lesson
from progress.models import Enrollment

from .models import Quiz, QuizAttempt
from .serializers import AttemptDetailSerializer, AttemptSummarySerializer, QuizSerializer, SubmissionSerializer
from .services import submit_attempt, usable_questions


def accessible_lesson(user, lesson_id):
    lesson = get_object_or_404(Lesson.objects.select_related("module"), pk=lesson_id)
    if not Enrollment.objects.filter(student=user, course_id=lesson.module.course_id).exists():
        raise PermissionDenied("Enrollment is required to access this quiz.")
    return lesson


class LessonQuizView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, lesson_id):
        lesson = accessible_lesson(request.user, lesson_id)
        quiz = Quiz.objects.filter(lesson=lesson, is_published=True).prefetch_related("questions__choices").first()
        if quiz is None:
            return Response({"quiz": None})
        usable_questions(quiz)
        return Response({"quiz": QuizSerializer(quiz).data})


class AttemptPagination(PageNumberPagination):
    page_size = 10


class LessonQuizAttemptsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, lesson_id):
        lesson = accessible_lesson(request.user, lesson_id)
        quiz = get_object_or_404(Quiz, lesson=lesson)
        attempts = QuizAttempt.objects.filter(quiz=quiz, student=request.user)
        pagination = AttemptPagination()
        page = pagination.paginate_queryset(attempts, request)
        response = pagination.get_paginated_response(AttemptSummarySerializer(page, many=True).data)
        latest = attempts.first()
        best = attempts.order_by("-score", "-submitted_at", "-pk").first()
        response.data.update({
            "latest": AttemptSummarySerializer(latest).data if latest else None,
            "best": AttemptSummarySerializer(best).data if best else None,
        })
        return response

    def post(self, request, lesson_id):
        lesson = accessible_lesson(request.user, lesson_id)
        quiz = get_object_or_404(Quiz, lesson=lesson)
        serializer = SubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attempt, created = submit_attempt(quiz_id=quiz.pk, student=request.user, **serializer.validated_data)
        return Response(
            AttemptDetailSerializer(attempt).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class OwnQuizAttemptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        attempt = get_object_or_404(
            QuizAttempt.objects.filter(student=request.user).select_related("quiz").prefetch_related("answers"), pk=pk,
        )
        accessible_lesson(request.user, attempt.quiz.lesson_id)
        return Response(AttemptDetailSerializer(attempt).data)
