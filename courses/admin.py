from django.contrib import admin

from .models import Course, Enrollment, Module


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")
    inlines = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "course")
    list_filter = ("course",)
    search_fields = ("code", "title")
    filter_horizontal = ("staff",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "status", "enrolled_at")
    list_filter = ("status", "course")
    autocomplete_fields = ("course",)
