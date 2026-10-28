from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Category, Course


# Official Heaven monthly prices supplied by the establishment.
# Viva prices apply only to students of Escola Viva; no discount is assumed
# for Ginástica Rítmica because none was provided.
CATALOG = [
    {"category": "Música", "name": "Música", "price": "110.00", "viva_price": "100.00"},
    {"category": "Futsal", "name": "Futsal", "price": "85.00", "viva_price": "80.00"},
    {"category": "Ballet", "name": "Ballet", "price": "110.00", "viva_price": "100.00"},
    {"category": "Ginástica Rítmica", "name": "Escolinha", "price": "100.00", "viva_price": None},
    {"category": "Ginástica Rítmica", "name": "Equipe", "price": "120.00", "viva_price": None},
    {"category": "Natação", "name": "Natação", "price": "120.00", "viva_price": "110.00"},
    {"category": "Jiu-jitsu", "name": "Jiu-jitsu", "price": "85.00", "viva_price": "80.00"},
    {"category": "Karatê", "name": "Karatê", "price": "80.00", "viva_price": "70.00"},
]


class Command(BaseCommand):
    help = "Cria ou atualiza o catálogo inicial de modalidades e mensalidades oficiais do Heaven."

    @transaction.atomic
    def handle(self, *args, **options):
        for item in CATALOG:
            category, _ = Category.objects.update_or_create(
                name=item["category"],
                defaults={"is_active": True},
            )
            defaults = {
                "price": Decimal(item["price"]),
                "viva_price": Decimal(item["viva_price"]) if item["viva_price"] else None,
                "billing_unit": Course.BillingUnit.MONTHLY,
                "is_active": True,
                "additional_information": (
                    "Frequência provisória: 1 aula por semana; confirmar com a equipe."
                ),
            }
            Course.objects.update_or_create(
                category=category,
                name=item["name"],
                defaults=defaults,
            )
        self.stdout.write(self.style.SUCCESS(
            f"Catálogo Heaven carregado: {len(CATALOG)} cursos/modalidades. "
            "A frequência de 1 aula por semana é provisória."
        ))
