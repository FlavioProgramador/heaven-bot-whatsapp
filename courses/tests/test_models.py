from decimal import Decimal

from django.test import TestCase

from courses.models import Category, Course, Schedule
from courses.services import active_courses, active_schedules


class CourseModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Música")

    def test_course_price_is_formatted_with_billing_unit(self):
        course = Course.objects.create(name="Violão", category=self.category, price=Decimal("125.50"), billing_unit=Course.BillingUnit.MONTHLY)
        self.assertEqual(course.formatted_price(), "R$ 125,50 — mensalidade.")

    def test_viva_price_and_provisional_frequency_are_formatted(self):
        course = Course.objects.create(name="Violão", category=self.category, price=Decimal("110.00"), viva_price=Decimal("100.00"), billing_unit=Course.BillingUnit.MONTHLY, lessons_per_week=1)
        self.assertEqual(course.formatted_price(), "R$ 110,00 — mensalidade. Alunos da escola Viva: R$ 100,00 — mensalidade.")
        self.assertEqual(course.lessons_per_week, 1)

    def test_missing_viva_discount_is_not_invented(self):
        course = Course.objects.create(name="Ginástica Rítmica", category=self.category, price=Decimal("100.00"), billing_unit=Course.BillingUnit.MONTHLY)
        self.assertNotIn("Viva", course.formatted_price())

    def test_weekly_frequency_is_provisional_until_confirmed(self):
        course = Course.objects.create(name="Dança", category=self.category, lessons_per_week=1)
        from whatsapp.services import _frequency_text
        self.assertIn("1 aula por semana", _frequency_text(course))
        self.assertIn("provisória", _frequency_text(course))
        course.frequency_confirmed = True
        self.assertNotIn("provisória", _frequency_text(course))

    def test_missing_price_is_not_invented(self):
        course = Course.objects.create(name="Piano", category=self.category)
        self.assertEqual(course.formatted_price(), "Preço a confirmar com a equipe.")

    def test_inactive_courses_are_excluded_from_active_catalog(self):
        Course.objects.create(name="Ativo", category=self.category, is_active=True)
        Course.objects.create(name="Inativo", category=self.category, is_active=False)
        self.assertEqual(list(active_courses().values_list("name", flat=True)), ["Ativo"])

    def test_active_schedules_are_filtered(self):
        course = Course.objects.create(name="Teclado", category=self.category)
        Schedule.objects.create(course=course, weekday=Schedule.Weekday.MONDAY, starts_at="15:00", ends_at="16:00", is_active=True)
        Schedule.objects.create(course=course, weekday=Schedule.Weekday.TUESDAY, starts_at="16:00", ends_at="17:00", is_active=False)
        self.assertEqual(list(active_schedules(course).values_list("weekday", flat=True)), [Schedule.Weekday.MONDAY])
