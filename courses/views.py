from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Course, Enrollment, Module


def course_list(request):
    """Landing page: every available course."""
    courses = Course.objects.prefetch_related("modules")
    return render(request, "courses/course_list.html", {"courses": courses})


def course_detail(request, pk):
    """One course and the modules that make it up."""
    course = get_object_or_404(
        Course.objects.prefetch_related("modules"),
        pk=pk,
    )
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            user=request.user,
            course=course,
            status=Enrollment.STATUS_ACTIVE,
        ).exists()
    return render(
        request,
        "courses/course_detail.html",
        {"course": course, "is_enrolled": is_enrolled},
    )


def module_detail(request, pk):
    """A single module with its details and teaching staff."""
    module = get_object_or_404(
        Module.objects.select_related("course").prefetch_related("staff"),
        pk=pk,
    )
    return render(request, "courses/module_detail.html", {"module": module})


@login_required
def my_courses(request):
    """Courses the signed-in user is actively enrolled on."""
    enrollments = (
        Enrollment.objects.filter(
            user=request.user,
            status=Enrollment.STATUS_ACTIVE,
        )
        .select_related("course")
        .prefetch_related("course__modules")
    )
    return render(request, "courses/my_courses.html", {"enrollments": enrollments})


@login_required
@require_POST
def enroll(request, pk):
    """Register the current user on a course (idempotent, no duplicates)."""
    course = get_object_or_404(Course, pk=pk)
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
    )
    if not created and enrollment.status == Enrollment.STATUS_ACTIVE:
        messages.info(request, f"You are already registered on {course.name}.")
    else:
        enrollment.status = Enrollment.STATUS_ACTIVE
        enrollment.save()
        messages.success(request, f"You are now registered on {course.name}.")
    return redirect(course)


@login_required
@require_POST
def unenroll(request, pk):
    """Withdraw the current user from a course."""
    course = get_object_or_404(Course, pk=pk)
    Enrollment.objects.filter(user=request.user, course=course).update(
        status=Enrollment.STATUS_WITHDRAWN,
    )
    messages.info(request, f"You have withdrawn from {course.name}.")
    return redirect("my_courses")
