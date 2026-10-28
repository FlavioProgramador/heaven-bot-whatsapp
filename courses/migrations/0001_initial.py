# Generated for the Heaven Bot initial course catalog.
from decimal import Decimal

from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True, verbose_name="nome")),
                ("description", models.TextField(blank=True, verbose_name="descrição")),
                ("is_active", models.BooleanField(default=True, verbose_name="ativa")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="criada em")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="atualizada em")),
            ],
            options={"verbose_name": "categoria", "verbose_name_plural": "categorias", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Course",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160, verbose_name="nome")),
                ("description", models.TextField(blank=True, verbose_name="descrição")),
                ("price", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name="preço")),
                ("billing_unit", models.CharField(choices=[("monthly", "Mensalidade"), ("per_class", "Aula avulsa"), ("package", "Pacote"), ("other", "A confirmar")], default="other", max_length=20, verbose_name="unidade de cobrança")),
                ("viva_price", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name="mensalidade para alunos da escola Viva")),
                ("lessons_per_week", models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name="aulas por semana (padrão provisório)")),
                ("lesson_duration_minutes", models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="duração da aula (minutos)")),
                ("additional_information", models.TextField(blank=True, verbose_name="informações adicionais")),
                ("is_active", models.BooleanField(default=True, verbose_name="ativo")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="criado em")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="atualizado em")),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="courses", to="courses.category", verbose_name="categoria")),
            ],
            options={"verbose_name": "curso", "verbose_name_plural": "cursos", "ordering": ["category__name", "name"], "constraints": [models.UniqueConstraint(fields=("category", "name"), name="unique_course_name_per_category")]},
        ),
        migrations.CreateModel(
            name="Schedule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("weekday", models.PositiveSmallIntegerField(choices=[(0, "Segunda-feira"), (1, "Terça-feira"), (2, "Quarta-feira"), (3, "Quinta-feira"), (4, "Sexta-feira"), (5, "Sábado"), (6, "Domingo")], verbose_name="dia da semana")),
                ("starts_at", models.TimeField(verbose_name="início")),
                ("ends_at", models.TimeField(verbose_name="término")),
                ("notes", models.CharField(blank=True, max_length=240, verbose_name="observações")),
                ("is_active", models.BooleanField(default=True, verbose_name="ativo")),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="schedules", to="courses.course", verbose_name="curso")),
            ],
            options={"verbose_name": "horário", "verbose_name_plural": "horários", "ordering": ["weekday", "starts_at"], "constraints": [models.CheckConstraint(condition=models.Q(("ends_at__gt", models.F("starts_at"))), name="schedule_end_after_start")]},
        ),
    ]
