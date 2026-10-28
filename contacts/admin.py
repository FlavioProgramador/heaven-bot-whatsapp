from django.contrib import admin

from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("display_contact", "conversation_state", "human_handoff_active", "first_contact_at", "last_contact_at")
    list_filter = ("conversation_state", "human_handoff_active")
    search_fields = ("name", "phone_number")
    readonly_fields = ("first_contact_at", "last_contact_at")
    actions = ("resume_automatic_service", "pause_automatic_service")

    @admin.display(description="Contato")
    def display_contact(self, obj):
        return obj.name or f"…{obj.phone_number[-4:]}"

    @admin.action(description="Retomar atendimento automático")
    def resume_automatic_service(self, request, queryset):
        queryset.update(human_handoff_active=False, conversation_state=Contact.ConversationState.MAIN_MENU)
        self.message_user(request, "Atendimento automático retomado para os contatos selecionados.")

    @admin.action(description="Pausar atendimento automático (atendimento humano)")
    def pause_automatic_service(self, request, queryset):
        queryset.update(human_handoff_active=True, conversation_state=Contact.ConversationState.HUMAN)
        self.message_user(request, "Atendimento automático pausado para os contatos selecionados.")
