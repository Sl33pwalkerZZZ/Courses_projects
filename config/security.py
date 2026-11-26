"""Fail closed in production; keep a private, stable signing key for local work."""
import os
from pathlib import Path
import stat
import tempfile

from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key


def security_settings(base_dir, environ=None):
    env = os.environ if environ is None else environ
    mode = env.get('DJANGO_ENV', 'development').strip().lower()
    if mode not in {'development', 'production'}:
        raise ImproperlyConfigured('DJANGO_ENV must be development or production.')
    production = mode == 'production'
    debug_value = env.get('DJANGO_DEBUG', 'false' if production else 'true').lower().strip()
    if debug_value not in {'true', 'false', '1', '0'}:
        raise ImproperlyConfigured('DJANGO_DEBUG must be true or false.')
    debug = debug_value in {'true', '1'}
    if production and debug:
        raise ImproperlyConfigured('Production requires DJANGO_DEBUG=false.')
    secret = env.get('DJANGO_SECRET_KEY', '').strip()
    if secret and (len(secret) < 50 or len(set(secret)) < 5 or secret.startswith('django-insecure-')):
        raise ImproperlyConfigured('DJANGO_SECRET_KEY must be a new private random key of at least 50 characters.')
    if not secret:
        if production:
            raise ImproperlyConfigured('Production requires DJANGO_SECRET_KEY in the process environment.')
        secret = development_secret(Path(base_dir) / '.local-django-secret')
    return secret, debug


def development_secret(path):
    """Never use the public historic key, and never write a key to Git or logs."""
    nofollow = getattr(os, 'O_NOFOLLOW', 0)
    try:
        if not path.exists():
            descriptor, temporary = tempfile.mkstemp(prefix='.local-django-secret.', dir=path.parent)
            try:
                with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
                    stream.write(get_random_secret_key())
                    stream.flush()
                    os.fsync(stream.fileno())
                try:
                    # Publish only complete bytes; concurrent startups keep the winner.
                    os.link(temporary, path)
                except FileExistsError:
                    pass
            finally:
                os.unlink(temporary)  # Only our own temporary file, never an existing key.
        with os.fdopen(os.open(path, os.O_RDONLY | nofollow), 'r', encoding='utf-8') as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077:
                raise ImproperlyConfigured('Local signing-key file must be a private regular file (mode600).')
            secret = stream.read(257).strip()
        if len(secret) < 50 or len(secret) > 256 or len(set(secret)) < 5 or secret.startswith('django-insecure-'):
            raise ImproperlyConfigured('Invalid local signing key; configure DJANGO_SECRET_KEY privately.')
        return secret
    except (OSError, UnicodeError):
        raise ImproperlyConfigured('Cannot access private local signing key; configure DJANGO_SECRET_KEY.') from None
