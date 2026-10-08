from django.urls import path

from progress.views import CourseEnrollmentRequestsView, EnrollView
from reviews.views import CourseReviewsView, OwnReviewDetailView
from .views import CourseDetailView, CourseListView, LessonDetailView

urlpatterns = [
    path("courses/", CourseListView.as_view(), name="course-list"),
    path("courses/<slug:slug>/", CourseDetailView.as_view(), name="course-detail"),
    path("courses/<slug:slug>/enroll/", EnrollView.as_view(), name="course-enroll"),
    path("courses/<slug:slug>/enrollment-requests/", CourseEnrollmentRequestsView.as_view(), name="course-enrollment-requests"),
    path("courses/<slug:slug>/reviews/", CourseReviewsView.as_view(), name="course-reviews"),
    path("reviews/<int:pk>/", OwnReviewDetailView.as_view(), name="review-detail"),
    path("lessons/<int:pk>/", LessonDetailView.as_view(), name="lesson-detail"),
]
