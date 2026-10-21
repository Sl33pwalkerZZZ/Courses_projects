from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.MeView.as_view()), path('meta/', views.MetaView.as_view()), path('dashboard/', views.DashboardView.as_view()),
    path('courses/', views.CourseListView.as_view()), path('courses/<int:pk>/', views.CourseDetailView.as_view()),
    path('courses/<int:pk>/modules/', views.CourseModulesView.as_view()), path('courses/<int:pk>/reorder/', views.ReorderView.as_view()),
    path('modules/<int:pk>/', views.ModuleDetailView.as_view()), path('modules/<int:pk>/lessons/', views.ModuleLessonsView.as_view()), path('modules/<int:pk>/reorder/', views.LessonReorderView.as_view()),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view()), path('lessons/<int:pk>/quiz/', views.LessonQuizView.as_view()),
    path('lessons/<int:pk>/assignments/', views.LessonAssignmentsView.as_view()), path('assignments/<int:pk>/', views.AssignmentDetailView.as_view()), path('lessons/<int:pk>/images/', views.LessonImagesView.as_view()),
    path('courses/<int:pk>/submissions/', views.CourseSubmissionsView.as_view()), path('submissions/<int:pk>/review/', views.SubmissionReviewView.as_view()), path('submissions/<int:pk>/file/', views.SubmissionFileView.as_view()),
    path('courses/<int:pk>/publication/', views.PublicationView.as_view()), path('reviews/', views.ReviewsView.as_view()), path('reviews/<int:pk>/decision/', views.ReviewDecisionView.as_view()),
    path('instructors/', views.InstructorsView.as_view()), path('instructors/<int:pk>/', views.InstructorRoleView.as_view()),
    path('enrollment-requests/', views.EnrollmentRequestsView.as_view()),
    path('enrollment-requests/<int:pk>/decision/', views.EnrollmentRequestDecisionView.as_view()),
    path('imports/preview/', views.ImportPreviewView.as_view()), path('imports/<uuid:pk>/confirm/', views.ImportConfirmView.as_view()),
]
