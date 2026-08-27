from django.core.management.base import BaseCommand

from courses.models import Assignment, Course, Direction, Lesson, Module
from users.models import User


DEMO_COURSES = [
    {
        "direction": "Видео и монтаж",
        "title": "AI в видеомонтаже",
        "slug": "ai-video-editing",
        "description": "Как использовать нейросети для апскейла, шумоподавления и цветокоррекции видео.",
        "level": Course.Level.BEGINNER,
        "modules": [
            {
                "title": "Модуль 1. Основы",
                "lessons": [
                    {
                        "title": "Урок 1. Зачем монтажёру AI",
                        "text_content": "Плейсхолдер-контент. Здесь будет текст урока с иллюстрациями.",
                        "assignment": "Опишите, какие задачи в своём монтаже вы хотели бы автоматизировать.",
                    },
                ],
            },
        ],
    },
    {
        "direction": "Разработка",
        "title": "AI для разработчиков",
        "slug": "ai-for-developers",
        "description": "Использование AI-ассистентов в написании и тестировании кода.",
        "level": Course.Level.BEGINNER,
        "modules": [
            {
                "title": "Модуль 1. Основы",
                "lessons": [
                    {
                        "title": "Урок 1. AI-ассистенты в разработке",
                        "text_content": "Плейсхолдер-контент. Здесь будет текст урока с иллюстрациями.",
                        "assignment": "Опишите свой текущий воркфлоу разработки без AI.",
                    },
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Создаёт 2 демо-курса-заглушки для пилота"

    def handle(self, *args, **options):
        author, _ = User.objects.get_or_create(
            username="demo_author",
            defaults={"email": "author@example.com", "role": User.Role.AUTHOR, "is_staff": True},
        )
        if not author.has_usable_password():
            author.set_password("author12345")
            author.save()

        for course_data in DEMO_COURSES:
            direction, _ = Direction.objects.get_or_create(
                name=course_data["direction"],
                defaults={"slug": course_data["direction"].lower().replace(" ", "-")},
            )
            course, created = Course.objects.update_or_create(
                slug=course_data["slug"],
                defaults={
                    "title": course_data["title"],
                    "description": course_data["description"],
                    "direction": direction,
                    "level": course_data["level"],
                    "author": author,
                    "is_published": True,
                },
            )
            for module_order, module_data in enumerate(course_data["modules"], start=1):
                module, _ = Module.objects.update_or_create(
                    course=course,
                    order=module_order,
                    defaults={"title": module_data["title"]},
                )
                for lesson_order, lesson_data in enumerate(module_data["lessons"], start=1):
                    lesson, _ = Lesson.objects.update_or_create(
                        module=module,
                        order=lesson_order,
                        defaults={
                            "title": lesson_data["title"],
                            "text_content": lesson_data["text_content"],
                        },
                    )
                    Assignment.objects.update_or_create(
                        lesson=lesson,
                        type=Assignment.Type.TEXT_ANSWER,
                        defaults={"description": lesson_data["assignment"]},
                    )
            self.stdout.write(self.style.SUCCESS(f"{'Создан' if created else 'Обновлён'} курс: {course.title}"))
