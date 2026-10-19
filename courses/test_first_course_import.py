"""Importer and authorized preview regression tests; isolated test DB/files only."""
import copy
import hashlib
import json
import sqlite3
import tempfile
import zipfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from progress.models import Enrollment, LessonProgress
from quizzes.models import Quiz, QuizChoice
from courses.management.commands.import_first_course import SLUG, SOURCE_NAME, curriculum_snapshot, digest
from courses.models import Assignment, Course, CourseImport, Direction, Lesson, LessonLearningContent, Module


def test_manifest(source):
    return {
        "course": {"title": "Как выбрать нейросеть под свою задачу", "slug": SLUG, "description": "Russian source-derived course",
                   "level": "beginner", "enrollment_mode": "approval", "is_published": False, "content_language": "ru"},
        "module": {"title": "Модуль 1"},
        "lessons": [{"title": f"Урок {n}", "order": n, "text_content": f"Объяснение {n}", "source_sections": [f"1.{n}"] + (["1.7", "1.8"] if n == 6 else []),
                     "objectives": ["Понять материал"], "interactions": []} for n in range(1, 7)],
        "assignment": {"lesson_order": 6, "type": "text", "learning_activity": "ai_selection_map", "description": "Карта выбора ИИ"},
        "quiz": {"lesson_order": 6, "title": "Итоговый тест", "instructions": "Выберите ответы", "passing_percentage": 70,
                 "is_published": False, "questions": [
                     {"text": f"Вопрос {n}", "type": "single" if n % 2 else "multiple", "order": n, "explanation": "Объяснение ответа",
                      "choices": [{"text": f"Вариант {i}", "order": i, "is_correct": i == 1 or (n % 2 == 0 and i == 2)} for i in range(1, 5)]}
                     for n in range(1, 16)]},
        "provenance": {"source_name": SOURCE_NAME, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "version": "1", "table_count": 4},
    }


class FirstCourseImportTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / SOURCE_NAME
        with zipfile.ZipFile(self.source, "w") as archive:
            archive.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>' + '<w:tbl/>' * 4 + '</w:body></w:document>')
        self.manifest = test_manifest(self.source)
        self.path = Path(self.temp.name) / "manifest.json"
        self.backup = Path(self.temp.name) / "backup.sqlite3"
        with sqlite3.connect(self.backup) as connection:
            connection.execute("CREATE TABLE courses_course (id INTEGER)")
        self.author = get_user_model().objects.create_user(username="author")
        self.direction = Direction.objects.create(name="Existing direction", slug="existing")
        self.old = Course.objects.create(title="Existing", slug="existing", description="Keep", direction=self.direction, author=self.author, is_published=True)
        module = Module.objects.create(course=self.old, title="Existing module", order=1)
        self.old_lesson = Lesson.objects.create(module=module, title="Existing lesson", text_content="Preserve exactly", order=1)
        self.enrollment = Enrollment.objects.create(student=self.author, course=self.old)
        self.progress = LessonProgress.objects.create(enrollment=self.enrollment, lesson=self.old_lesson)
        self.before = copy.deepcopy(curriculum_snapshot(self.old))

    def run_import(self, apply=False, **kwargs):
        self.path.write_text(json.dumps(self.manifest, ensure_ascii=False), encoding="utf-8")
        output = StringIO()
        options = {"manifest": self.path, "source": self.source, "author_id": self.author.pk, "stdout": output}
        if apply:
            options.update(apply=True, backup_file=self.backup)
        options.update(kwargs)
        call_command("import_first_course", **options)
        return output.getvalue()

    def test_default_dry_run_never_writes(self):
        self.assertIn('"lessons": 6', self.run_import())
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(CourseImport.objects.count(), 0)
        self.assertEqual(Direction.objects.count(), 1)

    def test_import_is_draft_ordered_valid_and_preserves_existing(self):
        output = self.run_import(apply=True)
        course = Course.objects.get(slug=SLUG)
        self.assertIn("Created draft course", output)
        self.assertFalse(course.is_published)
        self.assertFalse(course.content_import.review_approved)
        self.assertEqual(course.enrollment_mode, "approval")
        self.assertEqual(course.modules.count(), 1)
        lessons = list(course.modules.get().lessons.all())
        self.assertEqual([lesson.order for lesson in lessons], list(range(1, 7)))
        self.assertEqual(LessonLearningContent.objects.filter(lesson__module__course=course).count(), 6)
        self.assertEqual(lessons[-1].assignments.get().learning_activity, "ai_selection_map")
        self.assertFalse(lessons[-1].quiz.is_published)
        self.assertEqual(lessons[-1].quiz.questions.count(), 15)
        self.assertEqual(QuizChoice.objects.filter(question__quiz=lessons[-1].quiz).count(), 60)
        self.old.refresh_from_db()
        self.assertEqual(curriculum_snapshot(self.old), self.before)
        self.progress.refresh_from_db()
        self.assertIsNone(self.progress.completed_at)
        self.assertEqual(Enrollment.objects.count(), 1)

    def test_owned_rerun_is_noop(self):
        self.run_import(apply=True)
        counts = (Course.objects.count(), Lesson.objects.count(), QuizChoice.objects.count())
        self.assertIn("no-op", self.run_import(apply=True))
        self.assertEqual((Course.objects.count(), Lesson.objects.count(), QuizChoice.objects.count()), counts)

    def test_direction_reused_without_modifying_it(self):
        direction = Direction.objects.create(name="Maintainer name", slug="ai-foundations")
        self.run_import(apply=True)
        direction.refresh_from_db()
        self.assertEqual(Course.objects.get(slug=SLUG).direction_id, direction.pk)
        self.assertEqual(direction.name, "Maintainer name")

    def test_slug_conflict_without_ownership_is_never_overwritten(self):
        self.old.slug = SLUG
        self.old.save(update_fields=["slug"])
        with self.assertRaisesMessage(CommandError, "no import ownership"):
            self.run_import(apply=True)
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_edited_owned_course_is_never_overwritten(self):
        self.run_import(apply=True)
        lesson = Lesson.objects.get(module__course__slug=SLUG, order=1)
        lesson.text_content = "Maintainer edit"
        lesson.save(update_fields=["text_content"])
        with self.assertRaisesMessage(CommandError, "has been edited"):
            self.run_import(apply=True)
        lesson.refresh_from_db()
        self.assertEqual(lesson.text_content, "Maintainer edit")

    def test_changed_manifest_is_conflict(self):
        self.run_import(apply=True)
        self.manifest["lessons"][0]["text_content"] = "Different source mapping"
        with self.assertRaisesMessage(CommandError, "conflicts with"):
            self.run_import()

    def test_source_hash_mismatch_or_missing_source_blocks_import(self):
        self.manifest["provenance"]["source_sha256"] = "0" * 64
        with self.assertRaisesMessage(CommandError, "does not match"):
            self.run_import(apply=True)
        self.source.unlink()
        with self.assertRaisesMessage(CommandError, "source is missing"):
            self.run_import()
        self.assertEqual(Course.objects.count(), 1)

    def test_invalid_choices_are_rejected_before_writes(self):
        self.manifest["quiz"]["questions"][0]["choices"][0]["is_correct"] = False
        with self.assertRaises(CommandError):
            self.run_import(apply=True)
        self.assertEqual(Course.objects.count(), 1)

    def test_failure_after_creating_questions_rolls_back_every_new_row(self):
        with patch("courses.management.commands.import_first_course.validate_quiz", side_effect=ValidationError("Rejected")):
            with self.assertRaisesMessage(CommandError, "rolled back"):
                self.run_import(apply=True)
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(Lesson.objects.count(), 1)
        self.assertEqual(Assignment.objects.count(), 0)
        self.assertEqual(Quiz.objects.count(), 0)
        self.assertEqual(CourseImport.objects.count(), 0)
        self.assertEqual(Direction.objects.count(), 1)

    def test_apply_requires_verified_separate_backup(self):
        with self.assertRaisesMessage(CommandError, "backup-file"):
            self.run_import(apply=True, backup_file=None)
        self.assertEqual(Course.objects.count(), 1)

    def test_review_gate_affects_only_imported_course(self):
        self.run_import(apply=True)
        course = Course.objects.get(slug=SLUG)
        course.is_published = True
        with self.assertRaises(ValidationError):
            course.full_clean()
        course.content_import.review_approved = True
        course.content_import.save(update_fields=["review_approved"])
        course.full_clean()
        self.old.full_clean()


class FirstCoursePreviewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.student = User.objects.create_user(username="student")
        cls.author = User.objects.create_user(username="author", role="author")
        cls.staff = User.objects.create_user(username="staff", is_staff=True)
        cls.staff.user_permissions.add(*Permission.objects.filter(codename__in=["view_course", "view_lesson"], content_type__app_label="courses"))
        cls.limited = User.objects.create_user(username="limited", is_staff=True)
        cls.limited.user_permissions.add(Permission.objects.get(codename="view_lesson", content_type__app_label="courses"))
        direction = Direction.objects.create(name="AI", slug="ai")
        cls.course = Course.objects.create(title="Draft", slug=SLUG, description="Source", author=cls.author, direction=direction)
        module = Module.objects.create(course=cls.course, title="Module", order=1)
        cls.lesson = Lesson.objects.create(module=module, title="Lesson", text_content="Source", order=1)
        LessonLearningContent.objects.create(lesson=cls.lesson, objectives=["Learn"], source_sections=["1.1"], interactions=[{"type": "hierarchy", "items": []}])
        CourseImport.objects.create(course=cls.course, source_name=SOURCE_NAME, source_sha256="a"*64, manifest_sha256="b"*64, content_sha256="c"*64, version="1")
        quiz = Quiz.objects.create(lesson=cls.lesson, title="Draft assessment")
        cls.preview = reverse("instructor-course-preview", args=[SLUG])

    def test_draft_not_visible_in_public_course_endpoints(self):
        self.assertEqual(self.client.get(reverse("course-detail", args=[SLUG])).status_code, 404)
        self.assertEqual(self.client.get(reverse("course-list")).data, [])

    def test_preview_rejects_anonymous_student_display_author_and_limited_staff(self):
        self.assertEqual(self.client.get(self.preview).status_code, 401)
        for user in [self.student, self.author, self.limited]:
            self.client.force_authenticate(user)
            self.assertEqual(self.client.get(self.preview).status_code, 403)

    def test_authorized_staff_preview_without_enrollment_or_quiz_keys(self):
        self.client.force_authenticate(self.staff)
        response = self.client.get(self.preview)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["content_language"], "ru")
        self.assertEqual(response["Cache-Control"], "private, no-store")
        self.assertNotIn("quiz", response.data)
        lesson = self.client.get(reverse("lesson-detail", args=[self.lesson.pk]))
        self.assertEqual(lesson.status_code, 200)
        self.assertEqual(lesson.data["learning_content"]["source_sections"], ["1.1"])
        self.assertNotIn("is_correct", json.dumps(lesson.data))
        self.assertEqual(Enrollment.objects.count(), 0)

    def test_non_enrolled_student_cannot_read_draft_lesson(self):
        self.client.force_authenticate(self.student)
        self.assertEqual(self.client.get(reverse("lesson-detail", args=[self.lesson.pk])).status_code, 403)
