from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class RegistrationTests(TestCase):
    def test_signup_creates_user_with_hashed_password(self):
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
        self.assertRedirects(response, reverse("course_list"))
        user = User.objects.get(username="alice")
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
