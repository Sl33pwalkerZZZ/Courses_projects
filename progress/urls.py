from django.urls import path

from .views import (
    CompleteLessonView, MyActivityView, MyEnrollmentRequestsView, MyEnrollmentsView,
    SelectionMapView, SelectionMapSubmitView,
)
from .assignment_views import AssignmentLegacySubmissionFileView, AssignmentSubmissionsView, AssignmentSubmissionFileView

urlpatterns = [
    path("assignments/<int:assignment_id>/submissions/", AssignmentSubmissionsView.as_view(), name="assignment-submissions"),
    path("assignments/<int:assignment_id>/submissions/<int:submission_id>/files/<int:attachment_id>/", AssignmentSubmissionFileView.as_view(), name="assignment-submission-file"),
    path("assignments/<int:assignment_id>/submissions/<int:submission_id>/legacy-file/", AssignmentLegacySubmissionFileView.as_view(), name="assignment-submission-legacy-file"),
    path("assignments/<int:assignment_id>/selection-map/", SelectionMapView.as_view(), name="selection-map"),
    path("assignments/<int:assignment_id>/selection-map/submit/", SelectionMapSubmitView.as_view(), name="selection-map-submit"),
    path("my/activity/", MyActivityView.as_view(), name="my-activity"),
    path("my/enrollments/", MyEnrollmentsView.as_view(), name="my-enrollments"),
    path("my/enrollment-requests/", MyEnrollmentRequestsView.as_view(), name="my-enrollment-requests"),
    path("lessons/<int:lesson_id>/complete/", CompleteLessonView.as_view(), name="lesson-complete"),
]
