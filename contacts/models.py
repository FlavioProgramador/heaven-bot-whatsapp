from django.db import models


class Contact(models.Model):
    class ConversationState(models.TextChoices):
        MAIN_MENU = "MENU_PRINCIPAL", "Menu principal"
        LISTING_CATEGORIES = "LISTANDO_CATEGORIAS", "Listando categorias"
        LISTING_COURSES = "LISTANDO_CURSOS", "Listando cursos"
        COURSE_DETAILS = "CONSULTANDO_CURSO", "Consultando curso"
        SCHEDULES = "CONSULTANDO_HORARIOS", "Consultando horários"
        HUMAN = "ATENDIMENTO_HUMANO", "Atendimento humano"

    phone_number = models.CharField("telefone normalizado", max_length=20, unique=True, db_index=True)
    name = models.CharField("nome", max_length=160, blank=True)
    conversation_state = models.CharField(
        "estado da conversa", max_length=32,
        choices=ConversationState.choices, default=ConversationState.MAIN_MENU
    )
    human_handoff_active = models.BooleanField("atendimento humano ativo", default=False, db_index=True)
    first_contact_at = models.DateTimeField("primeiro contato", auto_now_add=True)
    last_contact_at = models.DateTimeField("último contato", auto_now=True)

    class Meta:
        ordering = ["-last_contact_at"]
        verbose_name = "contato"
        verbose_name_plural = "contatos"

    def __str__(self):
        return self.name or f"Contato {self.phone_number[-4:]}"
