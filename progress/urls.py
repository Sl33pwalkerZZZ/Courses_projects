from django.urls import path

from .views import CompleteLessonView, MyActivityView, MyEnrollmentRequestsView, MyEnrollmentsView

urlpatterns = [
    path("my/activity/", MyActivityView.as_view(), name="my-activity"),
    path("my/enrollments/", MyEnrollmentsView.as_view(), name="my-enrollments"),
    path("my/enrollment-requests/", MyEnrollmentRequestsView.as_view(), name="my-enrollment-requests"),
    path("lessons/<int:lesson_id>/complete/", CompleteLessonView.as_view(), name="lesson-complete"),
]
