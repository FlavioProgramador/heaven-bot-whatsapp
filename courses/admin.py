from django.contrib import admin

from .models import Category, Course, Schedule


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    ordering = ("name",)


class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "viva_price", "lessons_per_week", "frequency_confirmed", "billing_unit", "is_active", "updated_at")
    list_filter = ("is_active", "category", "billing_unit", "frequency_confirmed")
    search_fields = ("name", "description", "category__name")
    autocomplete_fields = ("category",)
    list_select_related = ("category",)
    inlines = (ScheduleInline,)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("course", "weekday", "starts_at", "ends_at", "is_active")
    list_filter = ("weekday", "is_active", "course__category")
    search_fields = ("course__name", "notes")
    autocomplete_fields = ("course",)
    list_select_related = ("course", "course__category")
