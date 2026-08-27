from django.urls import path

from .views import CompleteLessonView, MyEnrollmentsView

urlpatterns = [
    path("my/enrollments/", MyEnrollmentsView.as_view(), name="my-enrollments"),
    path("lessons/<int:lesson_id>/complete/", CompleteLessonView.as_view(), name="lesson-complete"),
]
