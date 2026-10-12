from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from progress.models import Enrollment, LessonProgress
from reviews.models import Review

from .management.demo_course_data import DEMO_COURSES
from .models import Assignment, Course, Direction, Lesson, LessonImage, Module


class SeedDemoCoursesTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(username="almas")

    def seed(self, author="almas"):
        output = StringIO()
        call_command("seed_demo_courses", author=author, stdout=output)
        return output.getvalue()

    def curriculum_ids(self):
        return {
            model.__name__: list(model.objects.order_by("pk").values_list("pk", flat=True))
            for model in (Direction, Course, Module, Lesson)
        }

    def test_seeds_published_ordered_curriculum_for_existing_apis(self):
        output = self.seed()
        self.assertIn("Courses: 6\nModules: 30\nLessons: 90", output)
        self.assertIn("Created objects: 131", output)
        self.assertEqual(Direction.objects.count(), 5)
        self.assertEqual(Course.objects.count(), 6)
        self.assertEqual(Module.objects.count(), 30)
        self.assertEqual(Lesson.objects.count(), 90)

        catalog = self.client.get(reverse("course-list"))
        self.assertEqual(catalog.status_code, 200)
        self.assertEqual({item["slug"] for item in catalog.data}, {c["slug"] for c in DEMO_COURSES})
        for course_data in DEMO_COURSES:
            course = Course.objects.get(slug=course_data["slug"])
            self.assertTrue(course.is_published)
            self.assertEqual(course.author, self.author)
            self.assertEqual(course.level, course_data["level"])
            self.assertEqual(course.direction.name, course_data["direction"])
            self.assertTrue(course.description)

            detail = self.client.get(reverse("course-detail", args=[course.slug]))
            self.assertEqual(detail.status_code, 200)
            self.assertEqual([m["order"] for m in detail.data["modules"]], [1, 2, 3, 4, 5])
            self.assertEqual(
                [m["title"] for m in detail.data["modules"]],
                [m["title"] for m in course_data["modules"]],
            )
            for module_data in detail.data["modules"]:
                self.assertEqual([l["order"] for l in module_data["lessons"]], [1, 2, 3])
            for lesson in Lesson.objects.filter(module__course=course):
                self.assertIn("Example\n", lesson.text_content)
                self.assertIn("Practical task\n", lesson.text_content)
                self.assertIn("Takeaway\n", lesson.text_content)
                self.assertGreater(len(lesson.text_content.split()), 50)

        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertFalse(Enrollment.objects.exists())
        self.assertFalse(LessonProgress.objects.exists())
        self.assertFalse(Review.objects.exists())
        self.assertFalse(Assignment.objects.exists())
        self.assertFalse(LessonImage.objects.exists())

    def test_repeat_run_updates_content_without_replacing_records(self):
        self.seed()
        original_ids = self.curriculum_ids()
        course = Course.objects.get(slug="ai-fundamentals-work-study")
        course.is_published = False
        course.save(update_fields=["is_published"])
        lesson = Lesson.objects.get(module__course=course, module__order=1, order=1)
        lesson.title = "Old demonstration title"
        lesson.text_content = "Old demonstration text"
        lesson.save(update_fields=["title", "text_content"])

        output = self.seed()

        self.assertEqual(self.curriculum_ids(), original_ids)
        self.assertIn("Created objects: 0", output)
        self.assertIn("Updated existing objects: 126", output)
        course.refresh_from_db()
        lesson.refresh_from_db()
        self.assertTrue(course.is_published)
        self.assertEqual(lesson.title, DEMO_COURSES[0]["modules"][0]["lessons"][0]["title"])
        self.assertEqual(lesson.text_content, DEMO_COURSES[0]["modules"][0]["lessons"][0]["text_content"])

    def test_preserves_unrelated_courses_accounts_and_learning_records(self):
        direction = Direction.objects.create(name="TestCourse", slug="testcourse")
        course = Course.objects.create(
            title="Test_Course", slug="test_course", description="Keep this content.",
            direction=direction, author=self.author, is_published=True,
        )
        module = Module.objects.create(course=course, title="User module", order=1)
        lesson = Lesson.objects.create(module=module, title="User lesson", text_content="Keep me.", order=1)
        enrollment = Enrollment.objects.create(student=self.author, course=course)
        progress = LessonProgress.objects.create(
            enrollment=enrollment, lesson=lesson, completed_at=timezone.now(),
        )
        review = Review.objects.create(student=self.author, course=course, rating=4, text="Existing review")
        preserved_models = (get_user_model(), Enrollment, LessonProgress, Review)
        preserved = {model: list(model.objects.order_by("pk").values()) for model in preserved_models}
        course_before = Course.objects.get(pk=course.pk).__dict__.copy()

        self.seed()
        demo_course = Course.objects.get(slug="ai-fundamentals-work-study")
        demo_module = demo_course.modules.get(order=1)
        demo_lesson = demo_module.lessons.get(order=1)
        # These fixtures exist only in the temporary test database.
        demo_enrollment = Enrollment.objects.create(student=self.author, course=demo_course)
        demo_progress = LessonProgress.objects.create(
            enrollment=demo_enrollment, lesson=demo_lesson, completed_at=timezone.now(),
        )
        extra_module = Module.objects.create(course=demo_course, title="Custom extra", order=99)
        extra_lesson = Lesson.objects.create(
            module=demo_module, title="Custom extra", text_content="Keep this too.", order=99,
        )
        self.seed()

        course.refresh_from_db()
        for field in ("title", "slug", "description", "direction_id", "author_id", "is_published", "created_at"):
            self.assertEqual(getattr(course, field), course_before[field])
        self.assertEqual(Module.objects.get(pk=module.pk).title, "User module")
        self.assertEqual(Lesson.objects.get(pk=lesson.pk).text_content, "Keep me.")
        self.assertEqual(list(get_user_model().objects.order_by("pk").values()), preserved[get_user_model()])
        self.assertEqual(list(Enrollment.objects.filter(pk=enrollment.pk).values()), preserved[Enrollment])
        self.assertEqual(list(LessonProgress.objects.filter(pk=progress.pk).values()), preserved[LessonProgress])
        self.assertEqual(list(Review.objects.filter(pk=review.pk).values()), preserved[Review])
        self.assertEqual(LessonProgress.objects.get(pk=demo_progress.pk).lesson_id, demo_lesson.pk)
        self.assertEqual(Module.objects.get(pk=extra_module.pk).title, "Custom extra")
        self.assertEqual(Lesson.objects.get(pk=extra_lesson.pk).text_content, "Keep this too.")

    def test_missing_author_fails_without_creating_users_or_curriculum(self):
        with self.assertRaisesMessage(CommandError, "Author 'missing' does not exist"):
            self.seed(author="missing")
        self.assertEqual(get_user_model().objects.count(), 1)
        for model in (Direction, Course, Module, Lesson):
            self.assertFalse(model.objects.exists())

    def test_reuses_existing_direction_name_without_changing_its_slug(self):
        direction = Direction.objects.create(name="AI Foundations", slug="existing-foundations")

        self.seed()
        self.seed()

        direction.refresh_from_db()
        self.assertEqual(direction.slug, "existing-foundations")
        self.assertEqual(Direction.objects.filter(name="AI Foundations").count(), 1)
        self.assertEqual(Course.objects.filter(direction=direction).count(), 2)

    def test_conflicting_direction_slug_rolls_back_entire_seed(self):
        Direction.objects.create(name="Unrelated direction", slug="knowledge-systems")
        with self.assertRaisesMessage(CommandError, "No changes were saved"):
            self.seed()
        self.assertEqual(Direction.objects.count(), 1)
        self.assertFalse(Direction.objects.filter(name="AI Foundations").exists())
        self.assertFalse(Course.objects.exists())
        self.assertFalse(Module.objects.exists())
        self.assertFalse(Lesson.objects.exists())

    def test_duplicate_module_order_fails_without_overwriting_existing_content(self):
        self.seed()
        course = Course.objects.get(slug="ai-fundamentals-work-study")
        course.title = "Existing edited title"
        course.save(update_fields=["title"])
        Module.objects.create(course=course, title="Conflicting module", order=1)
        original_ids = self.curriculum_ids()

        with self.assertRaisesMessage(CommandError, "duplicate curriculum order"):
            self.seed()

        course.refresh_from_db()
        self.assertEqual(course.title, "Existing edited title")
        self.assertEqual(self.curriculum_ids(), original_ids)

    def test_duplicate_lesson_order_rolls_back_course_and_module_updates(self):
        self.seed()
        course = Course.objects.get(slug="ai-fundamentals-work-study")
        course.description = "Existing edited description"
        course.save(update_fields=["description"])
        module = course.modules.get(order=1)
        module.title = "Existing edited module"
        module.save(update_fields=["title"])
        Lesson.objects.create(module=module, title="Conflicting lesson", text_content="Keep me.", order=1)
        original_ids = self.curriculum_ids()

        with self.assertRaisesMessage(CommandError, "duplicate curriculum order"):
            self.seed()

        course.refresh_from_db()
        module.refresh_from_db()
        self.assertEqual(course.description, "Existing edited description")
        self.assertEqual(module.title, "Existing edited module")
        self.assertEqual(self.curriculum_ids(), original_ids)
