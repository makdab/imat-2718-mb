"""Populate the database with demo courses, modules and staff.

Run with:  python manage.py seed_demo
Idempotent: safe to run repeatedly (uses get_or_create / update_or_create).
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Course, Module

User = get_user_model()

STAFF = [
    ("a.shargabi", "Amal", "Al-Shargabi"),
    ("j.smith", "John", "Smith"),
    ("p.patel", "Priya", "Patel"),
    ("l.chen", "Li", "Chen"),
]

# course code -> (name, description, [modules])
# each module: (code, title, description, contents, [staff usernames])
COURSES = {
    "BSC-CS": (
        "BSc Computer Science",
        "A broad foundation in software development, systems and theory.",
        [
            ("IMAT2718", "Integrated Project", "Build a full system using agile methods.",
             "Requirements\nAgile / Scrum\nDatabases\nWeb prototyping\nTesting", ["a.shargabi", "j.smith"]),
            ("IMAT1000", "Programming Fundamentals", "Core programming concepts and problem solving.",
             "Variables & types\nControl flow\nFunctions\nData structures", ["j.smith"]),
            ("IMAT2005", "Databases", "Relational modelling and SQL.",
             "ER modelling\nNormalisation\nSQL\nTransactions", ["p.patel"]),
        ],
    ),
    "BSC-SE": (
        "BSc Software Engineering",
        "Engineering large, reliable software systems in teams.",
        [
            ("IMAT3020", "Software Architecture", "Designing maintainable, scalable systems.",
             "Layered design\nComponents\nDesign patterns\nScalability", ["l.chen"]),
            ("IMAT3110", "Secure Systems", "Security and privacy by design.",
             "Authentication\nAuthorization\nData protection\nThreat modelling", ["p.patel", "l.chen"]),
        ],
    ),
    "BSC-DS": (
        "BSc Data Science",
        "Turning data into insight with statistics and machine learning.",
        [
            ("IMAT2450", "Data Analysis", "Exploring and visualising data.",
             "Cleaning\nStatistics\nVisualisation\nReporting", ["p.patel"]),
            ("IMAT3450", "Machine Learning", "Foundations of predictive modelling.",
             "Regression\nClassification\nEvaluation\nEthics", ["l.chen"]),
        ],
    ),
}


class Command(BaseCommand):
    help = "Seed the database with demo courses, modules and teaching staff."

    @transaction.atomic
    def handle(self, *args, **options):
        staff_by_username = {}
        for username, first, last in STAFF:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "email": f"{username}@example.ac.uk",
                    "is_teacher": True,
                },
            )
            if created:
                user.set_password("demopass123")
                user.is_teacher = True
                user.save()
            staff_by_username[username] = user

        for course_code, (name, description, modules) in COURSES.items():
            course, _ = Course.objects.update_or_create(
                code=course_code,
                defaults={"name": name, "description": description},
            )
            for m_code, title, m_desc, contents, staff_usernames in modules:
                module, _ = Module.objects.update_or_create(
                    code=m_code,
                    defaults={
                        "title": title,
                        "description": m_desc,
                        "contents": contents,
                        "course": course,
                    },
                )
                module.staff.set(staff_by_username[u] for u in staff_usernames)

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(COURSES)} courses, "
            f"{Module.objects.count()} modules and {len(STAFF)} staff."
        ))
