import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from concurrent.futures import ThreadPoolExecutor

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from .security import security_settings


class SigningConfigurationTests(SimpleTestCase):
    def test_local_key_private_stable_and_not_public_default(self):
        with TemporaryDirectory() as directory:
            first, debug = security_settings(directory, {})
            second, _ = security_settings(directory, {})
            self.assertEqual(first, second)
            self.assertGreaterEqual(len(first), 50)
            self.assertFalse(first.startswith('django-insecure-'))
            self.assertTrue(debug)
            self.assertEqual((Path(directory) / '.local-django-secret').stat().st_mode & 0o777, 0o600)

    def test_concurrent_local_startup_shares_one_complete_key(self):
        with TemporaryDirectory() as directory, ThreadPoolExecutor(max_workers=6) as pool:
            keys = list(pool.map(lambda _: security_settings(directory, {})[0], range(12)))
            self.assertEqual(len(set(keys)), 1)
            self.assertEqual(len(list(Path(directory).iterdir())), 1)

    def test_production_has_no_local_or_public_fallback(self):
        with TemporaryDirectory() as directory:
            for env in [
                {'DJANGO_ENV': 'production'},
                {'DJANGO_ENV': 'production', 'DJANGO_SECRET_KEY': 'django-insecure-' + 'x' * 60},
                {'DJANGO_ENV': 'production', 'DJANGO_SECRET_KEY': 'a' * 60},
                {'DJANGO_ENV': 'production', 'DJANGO_SECRET_KEY': 'too-short'},
                {'DJANGO_ENV': 'production', 'DJANGO_SECRET_KEY': 'Private-test-only-1234567890' * 3, 'DJANGO_DEBUG': 'true'},
            ]:
                with self.subTest(env_names=list(env)), self.assertRaises(ImproperlyConfigured):
                    security_settings(directory, env)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_private_environment_key_and_debug_false(self):
        with TemporaryDirectory() as directory:
            key = 'Private-test-only-1234567890' * 3
            actual, debug = security_settings(directory, {'DJANGO_ENV': 'production', 'DJANGO_SECRET_KEY': key})
            self.assertEqual(actual, key)
            self.assertFalse(debug)
            self.assertFalse(list(Path(directory).iterdir()))

    def test_invalid_modes_and_unsafe_local_files_fail_closed(self):
        with TemporaryDirectory() as directory:
            for env in [{'DJANGO_ENV': 'prodution'}, {'DJANGO_DEBUG': 'maybe'}]:
                with self.assertRaises(ImproperlyConfigured):
                    security_settings(directory, env)
            key = Path(directory) / '.local-django-secret'
            key.write_text('Private-test-only-1234567890' * 3)
            key.chmod(0o644)
            with self.assertRaises(ImproperlyConfigured):
                security_settings(directory, {})

    def test_production_settings_and_deploy_checks_use_only_isolated_database(self):
        with TemporaryDirectory() as directory:
            env = {**os.environ, 'DJANGO_SETTINGS_MODULE': 'config.production', 'DJANGO_ENV': 'production',
                'DJANGO_DEBUG': 'false', 'DJANGO_SECRET_KEY': 'Private-test-only-1234567890' * 3,
                'DJANGO_ALLOWED_HOSTS': 'courses.example.test',
                'DJANGO_CSRF_TRUSTED_ORIGINS': 'https://courses.example.test',
                'DJANGO_CORS_ALLOWED_ORIGINS': 'https://courses.example.test',
                'SQLITE_PATH': directory + '/database.sqlite3', 'DJANGO_MEDIA_ROOT': directory + '/private',
                'DJANGO_PUBLIC_MEDIA_ROOT': directory + '/public', 'DJANGO_STATIC_ROOT': directory + '/static'}
            code = """import django; django.setup()
from django.conf import settings
assert settings.DEBUG is False
assert settings.SECRET_KEY_FALLBACKS == []
assert settings.CERTIFICATES_ENABLED is False
assert settings.SECURE_SSL_REDIRECT and settings.SESSION_COOKIE_SECURE and settings.CSRF_COOKIE_SECURE
from django.core.management import call_command
call_command('check', deploy=True, fail_level='ERROR')
"""
            result = subprocess.run([sys.executable, '-B', '-c', code], env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, 'Production check failed; inspect sanitized settings checks.')
            # Existing application checks may open SQLite; they must not create records.
            import sqlite3
            with sqlite3.connect(Path(directory) / 'database.sqlite3') as database:
                self.assertEqual(database.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall(), [])
