from django.contrib import admin

from .models import Category, Course


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "billing_unit", "is_active", "updated_at")
    list_filter = ("is_active", "category", "billing_unit")
    search_fields = ("name", "description", "category__name")
    autocomplete_fields = ("category",)
    list_select_related = ("category",)
