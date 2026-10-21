import hashlib
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import SimpleTestCase

from scripts import lesson91_title_page_cleanup as cleanup


class Lesson91CleanupTests(SimpleTestCase):
    def setUp(self):
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.database = Path(self.folder.name) / 'fixture.sqlite3'
        self.backup = Path(self.folder.name) / 'backup.sqlite3'
        self.proposal = cleanup.load_proposal()
        with sqlite3.connect(self.database) as connection:
            connection.executescript('CREATE TABLE courses_course (id INTEGER PRIMARY KEY,is_published INTEGER);'
                'CREATE TABLE courses_module (id INTEGER PRIMARY KEY,course_id INTEGER);'
                'CREATE TABLE courses_lesson (id INTEGER PRIMARY KEY,module_id INTEGER,text_content TEXT);'
                'CREATE TABLE fixture_progress (id INTEGER PRIMARY KEY,completed INTEGER);'
                'INSERT INTO courses_course VALUES (8,1); INSERT INTO courses_module VALUES (31,8);'
                'INSERT INTO fixture_progress VALUES (1,2);')
            connection.execute('INSERT INTO courses_lesson VALUES (91,31,?)', (self.proposal['before'],))
        with sqlite3.connect(self.database) as source, sqlite3.connect(self.backup) as destination:
            source.backup(destination)
        self.backup_hash = hashlib.sha256(self.backup.read_bytes()).hexdigest()

    def apply(self, **overrides):
        args = dict(database=self.database, backup=self.backup, backup_sha256=self.backup_hash,
            approval_sha256=self.proposal['after_sha256'], proposal=self.proposal)
        return cleanup.apply_approved(**{**args, **overrides})

    def test_exact_diff_preserves_all_section_11_and_dry_run_is_read_only(self):
        original = self.database.read_bytes()
        with cleanup.read_only(self.database) as connection:
            self.assertEqual(cleanup.classify(cleanup.current_body(connection), self.proposal), 'ready')
        self.assertEqual(self.database.read_bytes(), original)
        self.assertTrue(self.proposal['before'].endswith(self.proposal['after']))
        self.assertEqual(len(self.proposal['removed_title_page_and_course_introduction']), 7)

    def test_approved_fixture_update_is_idempotent_and_preserves_progress(self):
        self.assertEqual(self.apply(), 'applied')
        after = self.database.read_bytes()
        self.assertEqual(self.apply(), 'already_applied')
        self.assertEqual(self.database.read_bytes(), after)
        with cleanup.read_only(self.database) as connection:
            self.assertEqual(cleanup.current_body(connection), self.proposal['after'])
            self.assertEqual(connection.execute('SELECT completed FROM fixture_progress').fetchone()[0], 2)

    def test_missing_approval_or_invalid_backup_refuses_writes(self):
        for override in [{'approval_sha256': None}, {'backup_sha256': 'invalid'}]:
            with self.assertRaises(ValueError):
                self.apply(**override)
        with cleanup.read_only(self.database) as connection:
            self.assertEqual(cleanup.current_body(connection), self.proposal['before'])

    def test_teacher_edit_or_other_writer_after_backup_is_refused(self):
        with self.assertRaises(ValueError):
            cleanup.classify('An intervening teacher edit', self.proposal)
        with sqlite3.connect(self.database) as connection:
            connection.execute('UPDATE fixture_progress SET completed=3')
        with self.assertRaises(ValueError):
            self.apply()
        with cleanup.read_only(self.database) as connection:
            self.assertEqual(cleanup.current_body(connection), self.proposal['before'])
            self.assertEqual(connection.execute('SELECT completed FROM fixture_progress').fetchone()[0], 3)

    def test_failure_after_update_rolls_back(self):
        with patch.object(cleanup, 'integrity', side_effect=[None, RuntimeError('Fixture failure')]):
            with self.assertRaises(RuntimeError):
                self.apply()
        with cleanup.read_only(self.database) as connection:
            self.assertEqual(cleanup.current_body(connection), self.proposal['before'])
