from django.urls import path

from .views import LessonQuizAttemptsView, LessonQuizView, OwnQuizAttemptView

urlpatterns = [
    path("lessons/<int:lesson_id>/quiz/", LessonQuizView.as_view(), name="lesson-quiz"),
    path("lessons/<int:lesson_id>/quiz/attempts/", LessonQuizAttemptsView.as_view(), name="lesson-quiz-attempts"),
    path("quiz-attempts/<int:pk>/", OwnQuizAttemptView.as_view(), name="quiz-attempt-detail"),
]
