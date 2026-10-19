from rest_framework.permissions import BasePermission


def moderator(user):
    # The role is set only by trusted administrators, never registration/profile writes.
    return bool(user.is_authenticated and user.is_active and (user.is_superuser or (user.is_staff and user.role == 'admin' and user.has_perm('courses.change_course'))))


class InstructorPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and user.is_active and (moderator(user) or user.role == 'author'))
