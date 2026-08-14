import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


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


class EmailVerification(models.Model):
    """A one-time code emailed to a user to confirm they own their address.

    A user signs up as inactive; they must enter the code we email them before
    the account is activated. This proves the address is real and belongs to
    them, which stops throwaway/duplicate signups on the same inbox.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="email_verification"
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"Email verification for {self.user}"

    @staticmethod
    def _new_code():
        # Cryptographically secure, always six digits (leading zeros kept).
        return f"{secrets.randbelow(1_000_000):06d}"

    @classmethod
    def issue(cls, user):
        """Create or replace the code for ``user`` and return the instance."""
        obj, _ = cls.objects.update_or_create(
            user=user,
            defaults={"code": cls._new_code(), "created_at": timezone.now(), "attempts": 0},
        )
        return obj

    @property
    def is_expired(self):
        ttl = timedelta(minutes=settings.EMAIL_OTP_TTL_MINUTES)
        return timezone.now() - self.created_at > ttl

    @property
    def attempts_exhausted(self):
        return self.attempts >= settings.EMAIL_OTP_MAX_ATTEMPTS

    def check_code(self, submitted):
        """Return True if ``submitted`` matches and the code is still usable.

        Every call counts as an attempt; once the limit is reached the code is
        dead and the user must request a new one.
        """
        if self.is_expired or self.attempts_exhausted:
            return False
        self.attempts += 1
        self.save(update_fields=["attempts"])
        # Constant-time comparison avoids leaking the code via timing.
        return secrets.compare_digest(str(self.code), str(submitted).strip())
