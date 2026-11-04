"""Source-only Module 5 authoring works without local audio or a TTS install."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from django.conf import settings
from django.test import SimpleTestCase


PACKAGE = Path('course_assets/module_5/m5-l13-v1-production')
HELPER = Path('course_assets/module_4/voice_candidates')


class MediaModule5PackageTests(SimpleTestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        source = Path(settings.BASE_DIR)
        shutil.copytree(source / PACKAGE, self.root / PACKAGE,
                        ignore=shutil.ignore_patterns('*.wav', '__pycache__', 'output'))
        (self.root / HELPER).mkdir(parents=True)
        for name in ['prepare_roman_module4.py', 'LICENSE_CIS']:
            shutil.copyfile(source / HELPER / name, self.root / HELPER / name)
        (self.root / 'docs/courses').mkdir(parents=True)
        shutil.copyfile(source / 'docs/courses/media-module-5-storyboards.json',
                        self.root / 'docs/courses/media-module-5-storyboards.json')

    def run_script(self, name, *args):
        return subprocess.run([sys.executable, '-B', str(self.root / PACKAGE / name), *args],
                              capture_output=True, text=True, timeout=10)

    def test_source_package_validates_without_generated_audio(self):
        result = self.run_script('validate_package.py')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('helper hash', result.stdout)
        self.assertIn('SKIP: local preview WAV', result.stdout)
        self.assertFalse(list(self.root.rglob('*.wav')))

    def test_explicit_audio_validation_fails_if_preview_missing(self):
        result = self.run_script('validate_package.py', '--require-preview')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Local preview WAV is missing', result.stderr)

    def test_generator_help_needs_no_model_or_generated_outputs(self):
        result = self.run_script('generate_preview.py', '--help')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--output-dir', result.stdout)
        self.assertFalse(list(self.root.rglob('*.wav')))
