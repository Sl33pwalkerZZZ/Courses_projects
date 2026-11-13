from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Студент"
        AUTHOR = "author", "Автор курса"
        ADMIN = "admin", "Администратор"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    certificate_name = models.CharField(max_length=200, blank=True)
    certificate_name_confirmed_at = models.DateTimeField(null=True, blank=True)
