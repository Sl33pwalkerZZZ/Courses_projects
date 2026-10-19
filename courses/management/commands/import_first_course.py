"""Transactional, opt-in import of the reviewed Chapter 1 manifest.

Dry-run is the default. Existing records are never updated. An owned import is
only a no-op when both its manifest and its actual curriculum remain unchanged.
"""
import hashlib
import json
import sqlite3
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from courses.models import Assignment, Course, CourseImport, Direction, Lesson, LessonLearningContent, Module
from quizzes.models import Quiz, QuizChoice, QuizQuestion
from quizzes.validation import validate_choices, validate_quiz

SLUG = "kak-vybrat-neyroset-pod-svoyu-zadachu"
SOURCE_NAME = "Глава_1_Выбор_ИИ_модели_и_сервиса.docx"
DIRECTION_SLUG = "ai-foundations"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def curriculum_snapshot(course):
    """Only educational rows; never query enrollments, submissions or attempts."""
    snapshot = {key: getattr(course, key) for key in (
        "id", "title", "slug", "description", "direction_id", "level", "author_id", "is_published", "enrollment_mode",
    )}
    snapshot["modules"] = []
    for module in course.modules.order_by("order", "pk"):
        item = {"id": module.pk, "title": module.title, "order": module.order, "lessons": []}
        for lesson in module.lessons.order_by("order", "pk"):
            content = getattr(lesson, "learning_content", None)
            row = {"id": lesson.pk, "title": lesson.title, "text_content": lesson.text_content, "order": lesson.order}
            row["learning_content"] = {key: getattr(content, key) for key in (
                "id", "content_language", "source_sections", "objectives", "interactions",
            )} if content else None
            row["images"] = list(lesson.images.order_by("order", "pk").values("id", "image", "order"))
            row["assignments"] = list(lesson.assignments.order_by("pk").values("id", "type", "description", "learning_activity"))
            quiz = getattr(lesson, "quiz", None)
            row["quiz"] = None
            if quiz:
                row["quiz"] = {key: getattr(quiz, key) for key in ("id", "title", "instructions", "passing_percentage", "is_published")}
                row["quiz"]["questions"] = []
                for question in quiz.questions.order_by("order", "pk"):
                    question_data = {key: getattr(question, key) for key in ("id", "text", "type", "order", "explanation")}
                    question_data["choices"] = list(question.choices.order_by("order", "pk").values("id", "text", "order", "is_correct"))
                    row["quiz"]["questions"].append(question_data)
            item["lessons"].append(row)
        snapshot["modules"].append(item)
    return snapshot


def required_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise CommandError(f"{label} must be nonempty text.")
    return value


def validate_manifest(data, source):
    if not isinstance(data, dict):
        raise CommandError("The manifest must be a JSON object.")
    try:
        course, module, lessons = data["course"], data["module"], data["lessons"]
        provenance, assignment, quiz = data["provenance"], data["assignment"], data["quiz"]
        if course["slug"] != SLUG or course["is_published"] is not False:
            raise CommandError("Only the expected new draft course may be imported.")
        if course["level"] != "beginner" or course["enrollment_mode"] != "approval" or course["content_language"] != "ru":
            raise CommandError("Expected a Russian beginner course with approval enrollment.")
        for field in ("title", "description"):
            required_text(course[field], f"Course {field}")
        required_text(module["title"], "Module title")
        if len(lessons) != 6 or [lesson["order"] for lesson in lessons] != list(range(1, 7)):
            raise CommandError("The manifest must contain six ordered lessons (1–6).")
        for lesson in lessons:
            for field in ("title", "text_content"):
                required_text(lesson[field], f"Lesson {field}")
            for field in ("source_sections", "objectives", "interactions"):
                if not isinstance(lesson[field], list):
                    raise CommandError(f"Lesson {field} must be a list.")
            if not lesson["source_sections"]:
                raise CommandError("Each lesson must identify its source sections.")
        covered_sections = {section for lesson in lessons for section in lesson["source_sections"]}
        if not {f"1.{n}" for n in range(1, 9)}.issubset(covered_sections):
            raise CommandError("The six lessons must preserve source sections 1.1–1.8.")
        if assignment["lesson_order"] != 6 or assignment["type"] != "text" or assignment["learning_activity"] != "ai_selection_map":
            raise CommandError("The selection-map assignment must belong to lesson six.")
        required_text(assignment["description"], "Assignment description")
        if quiz["lesson_order"] != 6 or quiz["is_published"] is not False or quiz["passing_percentage"] != 70:
            raise CommandError("The final quiz must be a draft on lesson six with a 70% threshold.")
        required_text(quiz["title"], "Quiz title")
        required_text(quiz["instructions"], "Quiz instructions")
        questions = quiz["questions"]
        if len(questions) != 15 or [q["order"] for q in questions] != list(range(1, 16)):
            raise CommandError("Exactly 15 ordered assessment questions are required.")
        for question in questions:
            required_text(question["text"], "Question text")
            required_text(question["explanation"], "Question explanation")
            choices = question["choices"]
            if [choice["order"] for choice in choices] != list(range(1, len(choices) + 1)):
                raise CommandError("Choice ordering must be explicit and contiguous.")
            if any(type(choice["is_correct"]) is not bool for choice in choices):
                raise CommandError("Choice correct-answer flags must be booleans.")
            validate_choices(question["type"], choices)
        if not source.is_file():
            raise CommandError("The original DOCX source is missing; nothing will be imported.")
        actual_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        if provenance["source_name"] != SOURCE_NAME or actual_hash != provenance["source_sha256"]:
            raise CommandError("The DOCX source does not match the manifest provenance.")
        required_text(provenance["version"], "Import version")
        with zipfile.ZipFile(source) as archive:
            document = ElementTree.fromstring(archive.read("word/document.xml"))
        tables = len(document.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl"))
        if tables != 4 or provenance["table_count"] != tables:
            raise CommandError("Expected all four source tables to be accounted for.")
    except (KeyError, TypeError, ValueError, ValidationError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        raise CommandError(f"Invalid course manifest/source: {exc}") from exc
    return data


def ensure_backup(path):
    if not path:
        raise CommandError("An existing SQLite --backup-file is required before --apply.")
    backup = Path(path).expanduser().resolve()
    database = Path(settings.DATABASES["default"]["NAME"]).resolve()
    if backup == database or not backup.is_file():
        raise CommandError("The backup must be a separate existing SQLite file.")
    try:
        with sqlite3.connect(f"file:{backup.as_posix()}?mode=ro&immutable=1", uri=True) as connection:
            if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise CommandError("SQLite backup integrity validation failed.")
            tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "courses_course" not in tables:
                raise CommandError("The backup is not an AI Courses database.")
    except sqlite3.DatabaseError as exc:
        raise CommandError("Unable to validate the SQLite backup.") from exc


class Command(BaseCommand):
    help = "Preview or explicitly import the isolated, source-derived first Russian course (draft only)."

    def add_arguments(self, parser):
        parser.add_argument("--manifest", type=Path, default=Path(__file__).resolve().parents[1] / "first_course_content.json")
        parser.add_argument("--source", type=Path, default=Path(settings.BASE_DIR) / "course_sources" / SOURCE_NAME)
        modes = parser.add_mutually_exclusive_group()
        modes.add_argument("--apply", action="store_true")
        modes.add_argument("--dry-run", action="store_true")
        authors = parser.add_mutually_exclusive_group(required=True)
        authors.add_argument("--author-id", type=int)
        authors.add_argument("--author-username")
        parser.add_argument("--backup-file", type=Path)

    def handle(self, *args, **options):
        try:
            data = validate_manifest(json.loads(options["manifest"].read_text(encoding="utf-8")), options["source"])
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError("Unable to read the course manifest.") from exc
        User = get_user_model()
        lookup = {"pk": options["author_id"]} if options["author_id"] is not None else {User.USERNAME_FIELD: options["author_username"]}
        author = User.objects.filter(**lookup, is_active=True).first()
        if author is None:
            raise CommandError("Select an existing active course author; this command never creates users.")
        manifest_hash = digest(data)
        provenance = data["provenance"]
        # Check conflict in preview and again under the write transaction.
        if self.check_existing(data, manifest_hash, author):
            return
        counts = {"courses": 1, "modules": 1, "lessons": 6, "lesson_learning_contents": 6,
                  "assignments": 1, "quizzes": 1, "questions": 15,
                  "choices": sum(len(question["choices"]) for question in data["quiz"]["questions"]),
                  "course_imports": 1, "directions": int(not Direction.objects.filter(slug=DIRECTION_SLUG).exists())}
        self.stdout.write(json.dumps({"mode": "apply" if options["apply"] else "dry-run", "create": counts, "slug": SLUG, "published": False}, ensure_ascii=False))
        if not options["apply"]:
            self.stdout.write("Dry-run: no records were written.")
            return
        ensure_backup(options["backup_file"])
        try:
            with transaction.atomic():
                if self.check_existing(data, manifest_hash, author):
                    return
                direction, _ = Direction.objects.get_or_create(slug=DIRECTION_SLUG, defaults={"name": "AI Foundations"})
                course_data = {key: data["course"][key] for key in ("title", "slug", "description", "level", "enrollment_mode", "is_published")}
                course = Course(direction=direction, author=author, **course_data)
                course.full_clean()
                course.save()
                module = Module(course=course, title=data["module"]["title"], order=1)
                module.full_clean()
                module.save()
                lessons = {}
                for item in data["lessons"]:
                    lesson = Lesson(module=module, **{key: item[key] for key in ("title", "order", "text_content")})
                    lesson.full_clean()
                    lesson.save()
                    lessons[item["order"]] = lesson
                    content = LessonLearningContent(lesson=lesson, content_language="ru", **{key: item[key] for key in ("source_sections", "objectives", "interactions")})
                    content.full_clean()
                    content.save()
                assignment = Assignment(lesson=lessons[6], **{key: data["assignment"][key] for key in ("type", "description", "learning_activity")})
                assignment.full_clean()
                assignment.save()
                quiz = Quiz(lesson=lessons[6], **{key: data["quiz"][key] for key in ( "title", "instructions", "passing_percentage", "is_published")})
                quiz.full_clean()
                quiz.save()
                for item in data["quiz"]["questions"]:
                    question = QuizQuestion(quiz=quiz, **{key: item[key] for key in ( "text", "type", "order", "explanation")})
                    question.full_clean()
                    question.save()
                    for choice_data in item["choices"]:
                        choice = QuizChoice(question=question, **choice_data)
                        choice.full_clean()
                        choice.save()
                validate_quiz(quiz)
                imported = CourseImport(course=course, source_name=provenance["source_name"], source_sha256=provenance["source_sha256"],
                                        version=provenance["version"], manifest_sha256=manifest_hash,
                                        content_sha256=digest(curriculum_snapshot(course)), content_language="ru")
                imported.full_clean()
                imported.save()
        except (ValidationError, IntegrityError) as exc:
            raise CommandError(f"Import validation/conflict failed; transaction rolled back: {exc}") from exc
        self.stdout.write(self.style.SUCCESS(f"Created draft course {course.pk}; lesson IDs {list(lessons[key].pk for key in sorted(lessons))}; quiz {quiz.pk}. No existing records updated."))

    def check_existing(self, data, manifest_hash, author):
        existing = Course.objects.filter(slug=SLUG).first()
        if existing is None:
            return False
        owned = getattr(existing, "content_import", None)
        if owned is None:
            raise CommandError("Slug conflict: existing course has no import ownership. Nothing was overwritten.")
        if owned.manifest_sha256 != manifest_hash or owned.source_sha256 != data["provenance"]["source_sha256"] or existing.author_id != author.pk:
            raise CommandError("Owned course conflicts with the source, manifest, or selected author. No updates permitted.")
        if digest(curriculum_snapshot(existing)) != owned.content_sha256:
            raise CommandError("The imported curriculum has been edited. Review manually; no records were overwritten.")
        self.stdout.write("Already imported and unchanged: no-op; no records were written.")
        return True
