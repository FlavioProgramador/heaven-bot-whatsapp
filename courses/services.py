from .models import Category, Course, Schedule


def active_categories():
    return Category.objects.filter(is_active=True).prefetch_related(
        "courses__schedules"
    ).order_by("name")


def active_courses(category=None):
    queryset = Course.objects.filter(is_active=True, category__is_active=True).select_related(
        "category"
    ).prefetch_related("schedules")
    if category is not None:
        queryset = queryset.filter(category=category)
    return queryset.order_by("category__name", "name")


def active_schedules(course):
    return Schedule.objects.filter(course=course, is_active=True).order_by("weekday", "starts_at")
