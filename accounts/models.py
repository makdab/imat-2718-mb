from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Site user.

    Extends Django's built-in user so we keep secure password hashing,
    sessions and permissions for free. ``is_teacher`` flags staff members;
    a user who is not a teacher is treated as a student.
    """

    is_teacher = models.BooleanField(
        default=False,
        help_text="Designates whether this user is a member of teaching staff.",
    )

    def __str__(self):
        full_name = self.get_full_name()
        return full_name or self.username
