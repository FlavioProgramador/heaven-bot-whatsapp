from django.db import models

from contacts.models import Contact


class MessageLog(models.Model):
    class Direction(models.TextChoices):
        INBOUND = "inbound", "Recebida"
        OUTBOUND = "outbound", "Enviada"

    class ProcessingStatus(models.TextChoices):
        RECEIVED = "received", "Recebida"
        PROCESSED = "processed", "Processada"
        SENT = "sent", "Enviada"
        FAILED = "failed", "Falhou"
        IGNORED = "ignored", "Ignorada"

    external_message_id = models.CharField("ID externo da mensagem", max_length=180, unique=True, null=True, blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name="messages")
    direction = models.CharField("direção", max_length=10, choices=Direction.choices)
    message_type = models.CharField("tipo", max_length=40, default="text")
    processing_status = models.CharField("status técnico", max_length=16, choices=ProcessingStatus.choices, default=ProcessingStatus.RECEIVED)
    error_code = models.CharField("código de erro", max_length=80, blank=True)
    created_at = models.DateTimeField("data e hora", auto_now_add=True)
    processed_at = models.DateTimeField("processada em", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "registro de mensagem"
        verbose_name_plural = "registros de mensagens"

    def __str__(self):
        return f"{self.direction}: {self.external_message_id or self.pk}"
