"""Isolated replacement fixtures: no real SQLite or protected media changes."""
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import tempfile
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import TransactionTestCase, override_settings

from courses.models import Course, Direction, Lesson, LessonAttachment, LessonImage, LessonLearningContent, Module
from courses.management.commands.import_media_module_4 import load_content
from courses.management.commands.import_media_module import create_backup
from courses.management.commands.finalize_module4_media import snapshot


class FinalizeMediaTests(TransactionTestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.private=self.root/'private'
        self.override=override_settings(MEDIA_ROOT=self.private)
        self.override.enable();self.addCleanup(self.override.disable)
        author=get_user_model().objects.create_user(username='fixture-author',role='author')
        direction=Direction.objects.create(name='Fixture',slug='fixture')
        self.course=Course.objects.create(title='Fixture only',slug='ai-media-content',author=author,direction=direction)
        data=json.loads((Path(settings.BASE_DIR)/'docs/courses/media-module-4-assets.json').read_text())
        module=Module.objects.create(course=self.course,title=data['module_title'],order=4)
        for order,entry in enumerate(load_content()['lessons'],1):
            lesson=Lesson.objects.create(module=module,title=entry['title'],text_content=entry['text_content'],order=order)
            LessonLearningContent.objects.create(lesson=lesson,objectives=entry['objectives'],source_sections=entry['source_sections'])
        self.module=module
        # Seed isolated fixtures only from committed final assets, then emulate prior metadata.
        seed=json.loads(json.dumps(data));seed.pop('replacement_required',None)
        seed_path=self.root/'seed.json';seed_path.write_text(json.dumps(seed))
        with patch('courses.management.commands.import_lesson_media.create_backup',return_value=self.root/'seed-backup'):
            call_command('import_lesson_media','--manifest',str(seed_path),'--apply',stdout=io.StringIO())
        for entry in data['assets']:
            if entry['kind']!='image':
                row=LessonAttachment.objects.get(lesson__module=module,filename=entry['filename'])
                if entry['key']!='srt-example':
                    row.filename='fixture-previous-'+entry['filename']
                    row.caption='Prior fixture metadata'
                    row.save(update_fields=['filename','caption'])
                entry['replacement_expected']=snapshot(row)
        self.manifest=self.root/'final.json';self.manifest.write_text(json.dumps(data))
        self.before={row.pk:snapshot(row) for row in LessonAttachment.objects.all()}
        self.old_files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.private.rglob('*') if p.is_file()}
        self.lesson_texts=list(module.lessons.values_list('pk','text_content'))
        # A tiny independent file-backed SQLite fixture exercises the real backup helper.
        self.backup_source=self.root/'fixture-source.sqlite3'
        with sqlite3.connect(self.backup_source) as db:
            db.execute('CREATE TABLE courses_course (id INTEGER PRIMARY KEY)')
            db.execute('INSERT INTO courses_course VALUES (1)')
        self.backup_patch=patch('courses.management.commands.finalize_module4_media.create_backup',
            side_effect=lambda _,directory:create_backup(self.backup_source,directory))
        self.backup=self.backup_patch.start();self.addCleanup(self.backup_patch.stop)

    def run_command(self,*args):
        output=io.StringIO()
        call_command('finalize_module4_media','--manifest',str(self.manifest),'--backup-dir',str(self.root/'backups'),*args,stdout=output)
        return output.getvalue()

    def assert_original_files(self):
        for name,digest in self.old_files.items():self.assertEqual(hashlib.sha256(Path(name).read_bytes()).hexdigest(),digest)

    def test_dry_run_then_apply_retains_ids_order_and_protected_access(self):
        preview=self.run_command('--dry-run')
        self.assertIn('"REPLACE": 5',preview);self.assertIn('"KEEP": 2',preview)
        self.backup.assert_not_called();self.assertFalse((self.root/'backups').exists())
        self.run_command('--apply')
        self.assertEqual(set(LessonAttachment.objects.values_list('pk',flat=True)),set(self.before))
        self.assertEqual(LessonAttachment.objects.count(),6);self.assertEqual(LessonImage.objects.count(),1)
        for row in LessonAttachment.objects.all():
            self.assertEqual(row.order,self.before[row.pk]['order'])
        self.assert_original_files()
        self.assertEqual(list(self.module.lessons.values_list('pk','text_content')),self.lesson_texts)
        self.course.refresh_from_db();self.assertFalse(self.course.is_published)
        from rest_framework.test import APIClient
        client=APIClient();row=LessonAttachment.objects.get(filename='m4-l10-silero-ru-roman-approved.wav')
        self.assertEqual(client.get(f'/api/lesson-attachments/{row.pk}/').status_code,401)
        student=get_user_model().objects.create_user(username='fixture-student')
        client.force_authenticate(student);self.assertEqual(client.get(f'/api/lesson-attachments/{row.pk}/').status_code,403)
        client.force_authenticate(self.course.author);response=client.get(f'/api/lesson-attachments/{row.pk}/')
        self.assertEqual(response.status_code,200)
        raw=b''.join(response.streaming_content);response.close()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),row.sha256)
        self.assertEqual(response['Cache-Control'],'private, no-store')

    def test_repeat_is_keep_without_new_backup(self):
        self.run_command('--apply');self.assertEqual(self.backup.call_count,1)
        output=self.run_command('--apply')
        self.assertIn('"KEEP": 7',output);self.assertEqual(self.backup.call_count,1)
        self.assertEqual(LessonAttachment.objects.count(),6)

    def test_bundle_contains_verified_sqlite_media_and_previous_records(self):
        self.run_command('--apply')
        bundle=next((self.root/'backups').iterdir())
        journal=json.loads((bundle/'journal.json').read_text())
        self.assertEqual(len(journal['records']),6);self.assertEqual(len(journal['media']),7)
        self.assertEqual({r['id'] for r in journal['records']},set(self.before))
        database=bundle/journal['database']
        self.assertEqual(hashlib.sha256(database.read_bytes()).hexdigest(),journal['database_sha256'])
        with sqlite3.connect(f'file:{database}?mode=ro',uri=True) as db:
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchall(),[('ok',)])
        for item in journal['media']:
            self.assertEqual(hashlib.sha256((bundle/'media'/item['storage_name']).read_bytes()).hexdigest(),item['sha256'])
        self.assertEqual(bundle.stat().st_mode & 0o777,0o700)
        self.assertEqual((bundle/'journal.json').stat().st_mode & 0o777,0o600)

    def test_midway_failure_rolls_back_rows_and_only_deletes_new_paths(self):
        from courses.management.commands.finalize_module4_media import apply_replacement
        calls=0
        def fail_second(item,created):
            nonlocal calls
            calls+=1
            apply_replacement(item,created)
            if calls==2:raise RuntimeError('fixture failure')
        with patch('courses.management.commands.finalize_module4_media.apply_replacement',side_effect=fail_second):
            with self.assertRaisesMessage(RuntimeError,'fixture failure'):self.run_command('--apply')
        self.assertEqual({row.pk:snapshot(row) for row in LessonAttachment.objects.all()},self.before)
        self.assertEqual({str(p) for p in self.private.rglob('*') if p.is_file()},set(self.old_files))
        self.assert_original_files()

    def test_changed_metadata_and_wrong_expected_id_fail_closed(self):
        row=LessonAttachment.objects.first();row.caption='Teacher edit';row.save(update_fields=['caption'])
        with self.assertRaises(CommandError):self.run_command('--apply')
        self.backup.assert_not_called()

    def test_missing_or_tampered_private_file_fails_before_backup(self):
        row=LessonAttachment.objects.first();Path(row.file.path).write_bytes(b'fixture tamper')
        with self.assertRaises(CommandError):self.run_command('--dry-run')
        self.backup.assert_not_called()

    def test_extra_duplicate_or_cross_course_target_rejected(self):
        row=LessonAttachment.objects.first();row.pk=None;row.sha256='0'*64;row.filename='unexpected.wav';row.save()
        with self.assertRaises(CommandError):self.run_command('--dry-run')
        self.backup.assert_not_called()

    def test_backup_failure_before_any_mutation(self):
        self.backup.side_effect=CommandError('fixture backup failure')
        with self.assertRaisesMessage(CommandError,'fixture backup failure'):self.run_command('--apply')
        self.assertEqual({row.pk:snapshot(row) for row in LessonAttachment.objects.all()},self.before)
        self.assert_original_files()

    def test_explicit_block_and_published_course_fail_closed(self):
        data=json.loads(self.manifest.read_text());data['apply_blocked_reason']='Teacher hold'
        self.manifest.write_text(json.dumps(data))
        with self.assertRaisesMessage(CommandError,'Teacher hold'):self.run_command('--apply')
        self.backup.assert_not_called()
        data.pop('apply_blocked_reason');self.manifest.write_text(json.dumps(data))
        self.course.is_published=True;self.course.save(update_fields=['is_published'])
        with self.assertRaises(CommandError):self.run_command('--dry-run')

    def test_explicit_empty_target_create_path_and_idempotency(self):
        LessonAttachment.objects.all().delete()  # Isolated fixture database only.
        data=json.loads(self.manifest.read_text())
        for entry in data['assets']:entry.pop('replacement_expected',None)
        self.manifest.write_text(json.dumps(data))
        self.assertIn('"CREATE": 6',self.run_command('--dry-run'))
        self.run_command('--apply')
        self.assertEqual(LessonAttachment.objects.count(),6)
        self.assertIn('"KEEP": 7',self.run_command('--apply'))

    def test_changed_expected_id_and_missing_asset_key_rejected(self):
        data=json.loads(self.manifest.read_text())
        data['assets'][0]['replacement_expected']['id']+=9999
        self.manifest.write_text(json.dumps(data))
        with self.assertRaises(CommandError):self.run_command('--dry-run')
        data['assets'].pop()
        self.manifest.write_text(json.dumps(data))
        with self.assertRaisesMessage(CommandError,'exactly the seven'):
            self.run_command('--dry-run')
        self.backup.assert_not_called()
