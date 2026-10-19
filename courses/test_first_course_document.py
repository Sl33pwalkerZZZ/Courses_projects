import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase

from courses.management.first_course_document import plain_text, read_document
from courses.models import Course, CourseImport, Direction, Lesson, Module
from quizzes.models import Quiz, QuizChoice, QuizQuestion


class DocumentMappingTests(SimpleTestCase):
    def test_checked_in_manifest_contains_complete_source_and_four_tables(self):
        manifest = json.loads((Path(settings.BASE_DIR) / "courses/management/first_course_content.json").read_text())
        self.assertEqual(len(manifest["lessons"]), 6)
        self.assertEqual(manifest["provenance"]["table_count"], 4)
        self.assertEqual(len(manifest["quiz"]["questions"]), 15)
        self.assertEqual(sum(len(q["choices"]) for q in manifest["quiz"]["questions"]), 60)
        source = Path(settings.BASE_DIR) / "course_sources" / manifest["provenance"]["source_name"]
        if not source.exists():
            self.skipTest("Private source is intentionally not checked into Git.")
        parsed = read_document(source)
        self.assertEqual(parsed["source_sha256"], manifest["provenance"]["source_sha256"])
        bodies = "\n\n".join(lesson["text_content"] for lesson in manifest["lessons"])
        for block in parsed["blocks"]:
            self.assertIn(plain_text([block]), bodies)
        tables = [interaction for lesson in manifest["lessons"] for interaction in lesson["interactions"] if "rows" in interaction]
        self.assertEqual(len(tables), 4)
        for table in parsed["tables"]:
            self.assertTrue(any(t["headers"] == table["headers"] and t["rows"] == table["rows"] for t in tables))

    def test_reader_rejects_incomplete_chapter_without_extracting_archive(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "incomplete.docx"
            with ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Only a title</w:t></w:r></w:p></w:body></w:document>')
            with self.assertRaises(ValueError):
                read_document(path)


class ImportedQuizReviewTests(TestCase):
    def setUp(self):
        author = get_user_model().objects.create_user(username="editorial-fixture")
        direction = Direction.objects.create(name="Editorial fixture", slug="editorial-fixture")
        self.course = Course.objects.create(title="Draft", slug="editorial-fixture", description="Draft source", author=author, direction=direction)
        module = Module.objects.create(course=self.course, title="Chapter", order=1)
        lesson = Lesson.objects.create(module=module, title="Final", text_content="Source", order=1)
        self.quiz = Quiz.objects.create(lesson=lesson, title="Draft assessment")
        question = QuizQuestion.objects.create(quiz=self.quiz, text="Question", type="single")
        QuizChoice.objects.create(question=question, text="Choice one", is_correct=True)
        QuizChoice.objects.create(question=question, text="Choice two", is_correct=False)

    def test_new_import_requires_editorial_approval_before_quiz_publication(self):
        imported = CourseImport.objects.create(
            course=self.course, source_name="source.docx", source_sha256="a" * 64,
            manifest_sha256="b" * 64, content_sha256="c" * 64, version="1",
        )
        self.quiz.is_published = True
        with self.assertRaises(ValidationError):
            self.quiz.clean()
        imported.review_approved = True
        imported.save(update_fields=["review_approved"])
        self.quiz.clean()
