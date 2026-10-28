from django.core.exceptions import ValidationError
from django.db import models


class InstitutionSettings(models.Model):
    name = models.CharField("nome do estabelecimento", max_length=160, default="Heaven")
    address = models.TextField("endereço", blank=True)
    google_maps_url = models.URLField("link do Google Maps", blank=True)
    human_support_phone = models.CharField("telefone de atendimento humano", max_length=20, blank=True)
    opening_hours = models.TextField("horário de funcionamento", blank=True)
    welcome_message = models.TextField(
        "mensagem de boas-vindas",
        default="Olá! Seja bem-vindo ao Heaven!\n\nComo podemos ajudar?"
    )
    closing_message = models.TextField("mensagem de encerramento", blank=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "configuração institucional"
        verbose_name_plural = "configurações institucionais"

    def clean(self):
        if not self.pk and InstitutionSettings.objects.exists():
            raise ValidationError("Mantenha apenas um registro de configuração institucional.")

    def save(self, *args, **kwargs):
        if not self.pk and InstitutionSettings.objects.exists():
            self.pk = InstitutionSettings.objects.order_by("pk").values_list("pk", flat=True).first()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
