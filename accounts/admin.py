from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin for the custom user, exposing the is_teacher role flag."""

    list_display = ("username", "email", "first_name", "last_name", "is_teacher", "is_staff")
    list_filter = UserAdmin.list_filter + ("is_teacher",)
    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("is_teacher",)}),)
