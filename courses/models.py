from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField("nome", max_length=120, unique=True)
    description = models.TextField("descrição", blank=True)
    is_active = models.BooleanField("ativa", default=True)
    created_at = models.DateTimeField("criada em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizada em", auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "categoria"
        verbose_name_plural = "categorias"

    def __str__(self):
        return self.name


class Course(models.Model):
    class BillingUnit(models.TextChoices):
        MONTHLY = "monthly", "Mensalidade"
        PER_CLASS = "per_class", "Aula avulsa"
        PACKAGE = "package", "Pacote"
        OTHER = "other", "A confirmar"

    name = models.CharField("nome", max_length=160)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="courses", verbose_name="categoria")
    description = models.TextField("descrição", blank=True)
    price = models.DecimalField("preço", max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    billing_unit = models.CharField("unidade de cobrança", max_length=20, choices=BillingUnit.choices, default=BillingUnit.OTHER)
    lesson_duration_minutes = models.PositiveSmallIntegerField("duração da aula (minutos)", null=True, blank=True)
    additional_information = models.TextField("informações adicionais", blank=True)
    is_active = models.BooleanField("ativo", default=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ["category__name", "name"]
        verbose_name = "curso"
        verbose_name_plural = "cursos"
        constraints = [models.UniqueConstraint(fields=["category", "name"], name="unique_course_name_per_category")]

    def __str__(self):
        return self.name

    def formatted_price(self):
        if self.price is None:
            return "Preço a confirmar com a equipe."
        whole, decimal = f"{self.price:.2f}".split(".")
        whole = f"{int(whole):,}".replace(",", ".")
        unit = dict(self.BillingUnit.choices).get(self.billing_unit, "A confirmar")
        if self.billing_unit == self.BillingUnit.OTHER:
            return f"R$ {whole},{decimal} ({unit.lower()})."
        return f"R$ {whole},{decimal} — {unit.lower()}."


class Schedule(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Segunda-feira"
        TUESDAY = 1, "Terça-feira"
        WEDNESDAY = 2, "Quarta-feira"
        THURSDAY = 3, "Quinta-feira"
        FRIDAY = 4, "Sexta-feira"
        SATURDAY = 5, "Sábado"
        SUNDAY = 6, "Domingo"

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="schedules", verbose_name="curso")
    weekday = models.PositiveSmallIntegerField("dia da semana", choices=Weekday.choices)
    starts_at = models.TimeField("início")
    ends_at = models.TimeField("término")
    notes = models.CharField("observações", max_length=240, blank=True)
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        ordering = ["weekday", "starts_at"]
        verbose_name = "horário"
        verbose_name_plural = "horários"
        constraints = [models.CheckConstraint(condition=models.Q(ends_at__gt=models.F("starts_at")), name="schedule_end_after_start")]

    def __str__(self):
        return f"{self.course.name} — {self.get_weekday_display()} {self.starts_at:%H:%M}-{self.ends_at:%H:%M}"
