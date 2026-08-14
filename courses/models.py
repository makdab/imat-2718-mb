from django.conf import settings
from django.db import models
from django.urls import reverse


class Course(models.Model):
    """A programme of study made up of several modules."""

    code = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Enrollment",
        related_name="courses",
        blank=True,
    )

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.name}"

    def get_absolute_url(self):
        return reverse("course_detail", args=[self.pk])


class Module(models.Model):
    """A unit of teaching that belongs to one course and is taught by staff."""

    code = models.CharField(max_length=12, unique=True)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    contents = models.TextField(
        blank=True,
        help_text="Syllabus / topics covered by the module.",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules",
    )
    staff = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="modules_taught",
        limit_choices_to={"is_teacher": True},
        blank=True,
    )

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.title}"

    def get_absolute_url(self):
        return reverse("module_detail", args=[self.pk])


class Enrollment(models.Model):
    """Junction table recording a student's registration on a course."""

    STATUS_ACTIVE = "active"
    STATUS_WITHDRAWN = "withdrawn"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_WITHDRAWN, "Withdrawn"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )

    class Meta:
        # A student can only be enrolled on a given course once.
        unique_together = ["user", "course"]
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.user} → {self.course.code} ({self.status})"
