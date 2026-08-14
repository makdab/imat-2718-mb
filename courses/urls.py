from django.urls import path

from . import views

urlpatterns = [
    path("", views.course_list, name="course_list"),
    path("my-courses/", views.my_courses, name="my_courses"),
    path("course/<int:pk>/", views.course_detail, name="course_detail"),
    path("course/<int:pk>/enroll/", views.enroll, name="enroll"),
    path("course/<int:pk>/unenroll/", views.unenroll, name="unenroll"),
    path("module/<int:pk>/", views.module_detail, name="module_detail"),
]
