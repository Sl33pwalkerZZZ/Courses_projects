from progress.models import Enrollment


def can_preview_lessons(user):
    """Use Django permissions for administrator previews, never the display role."""
    return user.is_active and (
        user.is_superuser or (user.is_staff and user.has_perm("courses.view_lesson"))
    )


def can_access_lesson(user, lesson):
    """One access rule for lesson content and its private images."""
    return user.is_authenticated and user.is_active and (
        can_preview_lessons(user)
        or (user.role == 'author' and lesson.module.course.author_id == user.pk)
        or Enrollment.objects.filter(student=user, course_id=lesson.module.course_id).exists()
    )


def can_preview_course(user, course):
    """Admin preview requires real Django permissions; display roles grant nothing."""
    return user.is_authenticated and user.is_active and (
        (user.role == 'author' and course.author_id == user.pk)
        or user.is_superuser or (
            user.is_staff and user.has_perm("courses.view_course")
            and user.has_perm("courses.view_lesson")
        )
    )
