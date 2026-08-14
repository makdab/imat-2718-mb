from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import EmailVerification

User = get_user_model()


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class RegistrationTests(TestCase):
    def test_signup_creates_inactive_user_with_hashed_password(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "alice",
                "first_name": "Alice",
                "last_name": "Jones",
                "email": "alice@example.com",
                "password1": "Sup3rSecret!23",
                "password2": "Sup3rSecret!23",
            },
        )
        # Sign-up now sends the user to the email-verification step.
        self.assertRedirects(response, reverse("verify_email"))
        user = User.objects.get(username="alice")
        # Account is held inactive until the email is verified.
        self.assertFalse(user.is_active)
        # Password must be stored hashed, never in plain text.
        self.assertNotEqual(user.password, "Sup3rSecret!23")
        self.assertTrue(user.check_password("Sup3rSecret!23"))
        # New users default to student (not teaching staff).
        self.assertFalse(user.is_teacher)

    def test_signup_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "bob",
                "email": "bob@example.com",
                "password1": "Sup3rSecret!23",
                "password2": "different",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="bob").exists())

    def test_signup_rejects_duplicate_email(self):
        User.objects.create_user(username="carol", email="dup@example.com", password="x")
        response = self.client.post(
            reverse("register"),
            {
                "username": "carol2",
                "email": "dup@example.com",
                "password1": "Sup3rSecret!23",
                "password2": "Sup3rSecret!23",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="carol2").exists())


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="dave", password="Sup3rSecret!23")

    def test_valid_login(self):
        response = self.client.post(
            reverse("login"),
            {"username": "dave", "password": "Sup3rSecret!23"},
        )
        self.assertRedirects(response, reverse("course_list"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_login_rejected(self):
        response = self.client.post(
            reverse("login"),
            {"username": "dave", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("course_list"))


SIGNUP_DATA = {
    "username": "student1",
    "first_name": "Sam",
    "last_name": "Student",
    "email": "student1@example.com",
    "password1": "s3cure-Pass!2718",
    "password2": "s3cure-Pass!2718",
}


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class EmailVerificationTests(TestCase):
    def test_register_emails_a_code(self):
        self.client.post(reverse("register"), SIGNUP_DATA)
        user = User.objects.get(username="student1")
        self.assertTrue(hasattr(user, "email_verification"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(user.email_verification.code, mail.outbox[0].body)

    def test_correct_code_activates_and_logs_in(self):
        self.client.post(reverse("register"), SIGNUP_DATA)
        user = User.objects.get(username="student1")
        code = user.email_verification.code

        resp = self.client.post(reverse("verify_email"), {"code": code})
        self.assertRedirects(resp, reverse("course_list"))

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertFalse(EmailVerification.objects.filter(user=user).exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_wrong_code_keeps_account_inactive_and_counts_attempts(self):
        self.client.post(reverse("register"), SIGNUP_DATA)
        user = User.objects.get(username="student1")

        self.client.post(reverse("verify_email"), {"code": "000000"})
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        self.assertEqual(user.email_verification.attempts, 1)

    def test_code_is_locked_after_max_attempts(self):
        self.client.post(reverse("register"), SIGNUP_DATA)
        user = User.objects.get(username="student1")
        real_code = user.email_verification.code

        for _ in range(5):
            self.client.post(reverse("verify_email"), {"code": "000000"})

        # Even the real code no longer works once attempts are exhausted.
        self.client.post(reverse("verify_email"), {"code": real_code})
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_resend_issues_a_new_code(self):
        self.client.post(reverse("register"), SIGNUP_DATA)
        user = User.objects.get(username="student1")

        self.client.post(reverse("resend_code"))
        user.email_verification.refresh_from_db()
        self.assertEqual(len(mail.outbox), 2)
        # A fresh code was issued and attempts were reset.
        self.assertEqual(user.email_verification.attempts, 0)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="carol", email="carol@example.com", password="OldPass!2718"
        )

    def test_reset_email_is_sent(self):
        resp = self.client.post(
            reverse("password_reset"), {"email": "carol@example.com"}
        )
        self.assertRedirects(resp, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/reset/", mail.outbox[0].body)

    def test_full_reset_flow_sets_new_password(self):
        self.client.post(reverse("password_reset"), {"email": "carol@example.com"})

        # Extract the reset link from the emailed body and follow it.
        body = mail.outbox[0].body
        path = [ln for ln in body.splitlines() if "/reset/" in ln][0].strip()
        resp = self.client.get(path, follow=True)
        set_password_url = resp.redirect_chain[-1][0]
        resp = self.client.post(
            set_password_url,
            {"new_password1": "BrandNew!2718", "new_password2": "BrandNew!2718"},
        )
        self.assertRedirects(resp, reverse("password_reset_complete"))

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("BrandNew!2718"))
