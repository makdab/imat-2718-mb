from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from .models import Course, Enrollment, Module

User = get_user_model()


class ModelTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(code="BSC-CS", name="BSc Computer Science")
        self.teacher = User.objects.create_user(
            username="teach", password="x", is_teacher=True
        )
        self.module = Module.objects.create(
            code="IMAT2718", title="Integrated Project", course=self.course
        )
        self.module.staff.add(self.teacher)

    def test_module_belongs_to_course(self):
        self.assertEqual(self.module.course, self.course)
        self.assertIn(self.module, self.course.modules.all())

    def test_module_staff_relationship(self):
        self.assertIn(self.teacher, self.module.staff.all())
        self.assertIn(self.module, self.teacher.modules_taught.all())

    def test_duplicate_enrollment_blocked(self):
        student = User.objects.create_user(username="stu", password="x")
        Enrollment.objects.create(user=student, course=self.course)
        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(user=student, course=self.course)


class EnrollmentFlowTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(code="BSC-CS", name="BSc Computer Science")
        self.student = User.objects.create_user(username="stu", password="Sup3rSecret!23")

    def test_enroll_requires_login(self):
        response = self.client.post(reverse("enroll", args=[self.course.pk]))
        login_url = reverse("login")
        self.assertEqual(response.status_code, 302)
        self.assertIn(login_url, response.url)
        self.assertEqual(Enrollment.objects.count(), 0)

    def test_enroll_and_no_duplicate(self):
        self.client.force_login(self.student)
        self.client.post(reverse("enroll", args=[self.course.pk]))
        self.client.post(reverse("enroll", args=[self.course.pk]))
        # Second enroll must not create a second row.
        self.assertEqual(
            Enrollment.objects.filter(user=self.student, course=self.course).count(), 1
        )

    def test_unenroll_withdraws(self):
        self.client.force_login(self.student)
        self.client.post(reverse("enroll", args=[self.course.pk]))
        self.client.post(reverse("unenroll", args=[self.course.pk]))
        enrollment = Enrollment.objects.get(user=self.student, course=self.course)
        self.assertEqual(enrollment.status, Enrollment.STATUS_WITHDRAWN)

    def test_enroll_rejects_get(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("enroll", args=[self.course.pk]))
        self.assertEqual(response.status_code, 405)


class BrowseTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(code="BSC-CS", name="BSc Computer Science")
        self.teacher = User.objects.create_user(
            username="teach", password="x", first_name="Amal", last_name="A", is_teacher=True
        )
        self.module = Module.objects.create(
            code="IMAT2718", title="Integrated Project", course=self.course
        )
        self.module.staff.add(self.teacher)

    def test_course_list_shows_course(self):
        response = self.client.get(reverse("course_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BSc Computer Science")

    def test_module_detail_shows_staff(self):
        response = self.client.get(reverse("module_detail", args=[self.module.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Integrated Project")
        self.assertContains(response, "Amal")
