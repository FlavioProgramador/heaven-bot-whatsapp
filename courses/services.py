from .models import Category, Course


def active_categories():
    return Category.objects.filter(is_active=True).prefetch_related(
        "courses"
    ).order_by("name")


def active_courses(category=None):
    queryset = Course.objects.filter(is_active=True, category__is_active=True).select_related(
        "category"
    )
    if category is not None:
        queryset = queryset.filter(category=category)
    return queryset.order_by("category__name", "name")
