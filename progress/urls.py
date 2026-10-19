from django.urls import path

from .views import (
    CompleteLessonView, MyActivityView, MyEnrollmentRequestsView, MyEnrollmentsView,
    SelectionMapView, SelectionMapSubmitView,
)

urlpatterns = [
    path("assignments/<int:assignment_id>/selection-map/", SelectionMapView.as_view(), name="selection-map"),
    path("assignments/<int:assignment_id>/selection-map/submit/", SelectionMapSubmitView.as_view(), name="selection-map-submit"),
    path("my/activity/", MyActivityView.as_view(), name="my-activity"),
    path("my/enrollments/", MyEnrollmentsView.as_view(), name="my-enrollments"),
    path("my/enrollment-requests/", MyEnrollmentRequestsView.as_view(), name="my-enrollment-requests"),
    path("lessons/<int:lesson_id>/complete/", CompleteLessonView.as_view(), name="lesson-complete"),
]
