"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from courses.media import public_media
from courses.views import LessonImageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/', include('courses.urls')),
    path('api/', include('progress.urls')),
    path('api/', include('quizzes.urls')),
    # FileField/Admin links also pass through authentication and lesson access.
    path('api/private-media/<path:filename>', LessonImageView.as_view(), name='private-media'),
]

if settings.DEBUG:
    urlpatterns += [path('media/<path:filename>', public_media, name='public-media')]
