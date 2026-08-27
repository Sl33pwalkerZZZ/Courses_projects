from django.urls import path

from progress.views import EnrollView
from .views import CourseDetailView, CourseListView, LessonDetailView

urlpatterns = [
    path("courses/", CourseListView.as_view(), name="course-list"),
    path("courses/<slug:slug>/", CourseDetailView.as_view(), name="course-detail"),
    path("courses/<slug:slug>/enroll/", EnrollView.as_view(), name="course-enroll"),
    path("lessons/<int:pk>/", LessonDetailView.as_view(), name="lesson-detail"),
]
