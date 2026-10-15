import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from progress.models import Enrollment

from .image_descriptions import image_alt_text, load_image_descriptions
from .models import Course, Direction, Lesson, LessonImage, Module
from .serializers import LessonImageSerializer


class ImageDescriptionTests(SimpleTestCase):
    def test_only_authored_supported_language_strings_are_returned(self):
        entries = {"7": {"en": " A diagram ", "ru": "Описание", "kk": "Сипаттама", "fr": "ignored", "other": 42}}
        self.assertEqual(image_alt_text(entries, 7), {"en": "A diagram", "ru": "Описание", "kk": "Сипаттама"})
        self.assertEqual(image_alt_text(entries, 99), {})
        for invalid in (None, [], "filename.png", {"en": 42}, {"en": "   "}):
            self.assertEqual(image_alt_text({"7": invalid}, 7), {})

    def test_optional_file_can_be_missing_and_valid_utf8_is_preserved(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "descriptions.json"
            with override_settings(LESSON_IMAGE_DESCRIPTIONS_FILE=path):
                self.assertEqual(load_image_descriptions(), {})
                entries = {"7": {"kk": "Сызбаның сипаттамасы"}}
                path.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")
                self.assertEqual(load_image_descriptions(), entries)

    def test_bad_optional_metadata_does_not_break_lesson_serialization(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "descriptions.json"
            for content in ("{invalid", "[]", '"invalid"'):
                path.write_text(content, encoding="utf-8")
                with override_settings(LESSON_IMAGE_DESCRIPTIONS_FILE=path), self.assertLogs("courses.image_descriptions", level="WARNING") as logs:
                    self.assertEqual(load_image_descriptions(), {})
                self.assertNotIn(content, " ".join(logs.output))

    def test_images_share_one_metadata_read_and_keep_protected_id_urls(self):
        images = [LessonImage(id=7, image="lessons/private.png"), LessonImage(id=8, image="lessons/decorative.png")]
        with patch("courses.serializers.load_image_descriptions", return_value={"7": {"en": "An informative diagram"}, "8": {}}) as load:
            data = LessonImageSerializer(images, many=True).data
        self.assertEqual(load.call_count, 1)
        self.assertEqual(data[0]["alt_text"], {"en": "An informative diagram"})
        self.assertEqual(data[1]["alt_text"], {})
        self.assertEqual(data[0]["image"], reverse("lesson-image", args=[7]))
        self.assertNotIn("private.png", str(data))


class LessonDescriptionAccessTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.student = User.objects.create_user(username="description-student")
        cls.other = User.objects.create_user(username="description-outsider")
        direction = Direction.objects.create(name="Description fixture", slug="description-fixture")
        course = Course.objects.create(title="Fixture course", slug="description-course", description="", direction=direction, author=cls.other, is_published=True)
        module = Module.objects.create(course=course, title="Fixture module", order=1)
        cls.lesson = Lesson.objects.create(module=module, title="Fixture lesson", text_content="Fixture material", order=1)
        cls.image = LessonImage.objects.create(lesson=cls.lesson, image="lessons/fixture.png")
        Enrollment.objects.create(student=cls.student, course=course)

    def test_only_authorized_lesson_responses_expose_authored_descriptions(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "descriptions.json"
            descriptions = {"en": "Fixture informative description", "ru": "Описание", "kk": "Сипаттама"}
            path.write_text(json.dumps({str(self.image.pk): descriptions}), encoding="utf-8")
            with override_settings(LESSON_IMAGE_DESCRIPTIONS_FILE=path):
                lesson_url = reverse("lesson-detail", args=[self.lesson.pk])
                self.assertEqual(self.client.get(lesson_url).status_code, 401)
                self.client.force_authenticate(self.other)
                self.assertEqual(self.client.get(lesson_url).status_code, 403)
                self.client.force_authenticate(self.student)
                data = self.client.get(lesson_url).data
                self.assertEqual(data["images"][0]["alt_text"], descriptions)
                self.assertEqual(self.client.get("/api/private-media/lesson-image-descriptions.json").status_code, 404)
                self.assertEqual(self.client.get("/media/lesson-image-descriptions.json").status_code, 404)
                # Public syllabus previews do not include lesson bodies or descriptions.
                public = self.client.get(reverse("course-detail", args=["description-course"]))
                self.assertEqual(public.status_code, 200)
                self.assertNotIn("Fixture informative description", str(public.data))
