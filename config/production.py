"""Explicit production overrides; no changes to local database or course records."""
import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

if os.environ.setdefault('DJANGO_ENV', 'production') != 'production':
    raise ImproperlyConfigured('config.production requires DJANGO_ENV=production.')

from .settings import *  # noqa: F403,E402


def csv(name):
    return [value.strip() for value in os.environ.get(name, '').split(',') if value.strip()]


def absolute_path(name):
    value = os.environ.get(name, '')
    if not value or not Path(value).is_absolute():
        raise ImproperlyConfigured(f'{name} must be an absolute persistent filesystem path.')
    return Path(value)


DEBUG = False
SECRET_KEY_FALLBACKS = []
ALLOWED_HOSTS = csv('DJANGO_ALLOWED_HOSTS')
if not ALLOWED_HOSTS or any('*' in host or '/' in host for host in ALLOWED_HOSTS):
    raise ImproperlyConfigured('DJANGO_ALLOWED_HOSTS requires exact hostnames, not URLs or wildcards.')
CORS_ALLOWED_ORIGINS = csv('DJANGO_CORS_ALLOWED_ORIGINS')
CSRF_TRUSTED_ORIGINS = csv('DJANGO_CSRF_TRUSTED_ORIGINS')
if any(not origin.startswith('https://') or '*' in origin for origin in CORS_ALLOWED_ORIGINS + CSRF_TRUSTED_ORIGINS):
    raise ImproperlyConfigured('Production CORS/CSRF origins must be exact HTTPS origins.')
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': absolute_path('SQLITE_PATH')}}
MEDIA_ROOT = absolute_path('DJANGO_MEDIA_ROOT')
PUBLIC_MEDIA_ROOT = absolute_path('DJANGO_PUBLIC_MEDIA_ROOT')
if MEDIA_ROOT.resolve().is_relative_to(PUBLIC_MEDIA_ROOT.resolve()) or PUBLIC_MEDIA_ROOT.resolve().is_relative_to(MEDIA_ROOT.resolve()):
    raise ImproperlyConfigured('Public and private media roots must not overlap.')
LESSON_IMAGE_DESCRIPTIONS_FILE = MEDIA_ROOT / 'lesson-image-descriptions.json'
STATIC_ROOT = absolute_path('DJANGO_STATIC_ROOT')
STATIC_URL = '/static/'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
if os.environ.get('DJANGO_TRUST_PROXY_HTTPS') == 'true':
    # Enable only behind a trusted ingress that strips client-supplied headers.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CERTIFICATES_ENABLED = False
CERTIFICATE_PUBLIC_ORIGIN = ''

# Production must not silently log password-reset mail to a console.
MAILERS = {'default': {'BACKEND': 'django.core.mail.backends.smtp.EmailBackend', 'OPTIONS': {
    'host': os.environ.get('DJANGO_EMAIL_HOST', 'localhost'),
    'port': int(os.environ.get('DJANGO_EMAIL_PORT', '587')),
    'username': os.environ.get('DJANGO_EMAIL_HOST_USER', ''),
    'password': os.environ.get('DJANGO_EMAIL_HOST_PASSWORD', ''),
    'use_tls': True,
    'timeout': 15,
}}}
DEFAULT_FROM_EMAIL = os.environ.get('DJANGO_DEFAULT_FROM_EMAIL', 'webmaster@localhost')
