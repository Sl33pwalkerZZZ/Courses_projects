from django.urls import path
from . import views

urlpatterns = [
    path('courses/<int:pk>/certificate-status/', views.CourseCertificateStatus.as_view()),
    path('my/certificates/', views.MyCertificates.as_view()),
    path('certificates/verify/<str:code>/', views.VerifyCertificate.as_view()),
    path('certificates/admin/issue/', views.IssueCertificate.as_view()),
    path('certificates/admin/<str:code>/revoke/', views.RevokeCertificate.as_view()),
    path('certificates/<str:code>/download/', views.DownloadCertificate.as_view()),
]
