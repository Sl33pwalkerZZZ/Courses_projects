from progress.models import Enrollment
from studio.permissions import moderator


def can_preview_lessons(user):
    """Use Studio authority for previews; staff/student flags grant no override."""
    return moderator(user)


def can_access_lesson(user, lesson):
    """One access rule for lesson content and its private images."""
    return user.is_authenticated and user.is_active and (
        can_preview_lessons(user)
        or (user.role == 'author' and lesson.module.course.author_id == user.pk)
        or Enrollment.objects.filter(student=user, course_id=lesson.module.course_id).exists()
    )


def can_preview_course(user, course):
    """Only owning authors and administrators with actual permissions may preview."""
    return user.is_authenticated and user.is_active and (
        (user.role == 'author' and course.author_id == user.pk)
        or moderator(user)
    )
