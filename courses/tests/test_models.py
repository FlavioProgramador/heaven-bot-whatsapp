from decimal import Decimal

from django.test import TestCase

from courses.models import Category, Course


class CourseModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Música")

    def test_course_price_is_formatted_with_billing_unit(self):
        course = Course.objects.create(
            name="Violão",
            category=self.category,
            price=Decimal("125.50"),
            billing_unit=Course.BillingUnit.MONTHLY,
        )
        self.assertEqual(course.formatted_price(), "R$ 125,50 — mensalidade.")

    def test_missing_price_is_not_invented(self):
        course = Course.objects.create(name="Piano", category=self.category)
        self.assertEqual(course.formatted_price(), "Preço a confirmar com a equipe.")

    def test_inactive_courses_are_excluded_from_active_catalog(self):
        from courses.services import active_courses

        Course.objects.create(name="Ativo", category=self.category, is_active=True)
        Course.objects.create(name="Inativo", category=self.category, is_active=False)
        self.assertEqual(list(active_courses().values_list("name", flat=True)), ["Ativo"])
