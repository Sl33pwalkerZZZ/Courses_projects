from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from courses.management.demo_course_data import DEMO_COURSES, DIRECTIONS
from courses.models import Course, Direction, Lesson, Module


class Command(BaseCommand):
    help = "Create or update six demo courses using an existing author's username."

    def add_arguments(self, parser):
        parser.add_argument("--author", required=True, help="Username of the existing course author.")

    def handle(self, *args, **options):
        User = get_user_model()
        try:
            author = User.objects.get(**{User.USERNAME_FIELD: options["author"]})
        except User.DoesNotExist as error:
            raise CommandError(f"Author '{options['author']}' does not exist. No data was seeded.") from error

        created_objects = 0
        updated_objects = 0
        module_count = 0
        lesson_count = 0

        # A failed lookup or write rolls back the whole seed, without deleting anything.
        try:
            with transaction.atomic():
                directions = {}
                for name, slug in DIRECTIONS.items():
                    direction, created = Direction.objects.get_or_create(name=name, defaults={"slug": slug})
                    directions[name] = direction
                    created_objects += int(created)

                for course_data in DEMO_COURSES:
                    course, created = Course.objects.update_or_create(
                        slug=course_data["slug"],
                        defaults={
                            "title": course_data["title"],
                            "description": course_data["description"],
                            "direction": directions[course_data["direction"]],
                            "level": course_data["level"],
                            "author": author,
                            "is_published": True,
                        },
                    )
                    created_objects += int(created)
                    updated_objects += int(not created)

                    for module_order, module_data in enumerate(course_data["modules"], start=1):
                        module, created = Module.objects.update_or_create(
                            course=course,
                            order=module_order,
                            defaults={"title": module_data["title"]},
                        )
                        module_count += 1
                        created_objects += int(created)
                        updated_objects += int(not created)

                        for lesson_order, lesson_data in enumerate(module_data["lessons"], start=1):
                            _, created = Lesson.objects.update_or_create(
                                module=module,
                                order=lesson_order,
                                defaults=lesson_data,
                            )
                            lesson_count += 1
                            created_objects += int(created)
                            updated_objects += int(not created)
        except (IntegrityError, Module.MultipleObjectsReturned, Lesson.MultipleObjectsReturned) as error:
            raise CommandError(
                "Demo data conflicts with an existing direction slug or duplicate curriculum order. "
                "No changes were saved; resolve the conflicting records and try again."
            ) from error

        self.stdout.write(self.style.SUCCESS("Demo curriculum seeded."))
        self.stdout.write(f"Directions: {len(directions)}")
        self.stdout.write(f"Courses: {len(DEMO_COURSES)}")
        self.stdout.write(f"Modules: {module_count}")
        self.stdout.write(f"Lessons: {lesson_count}")
        self.stdout.write(f"Updated existing objects: {updated_objects}")
        self.stdout.write(f"Created objects: {created_objects}")
