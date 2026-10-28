from django.contrib import admin

from .models import InstitutionSettings


@admin.register(InstitutionSettings)
class InstitutionSettingsAdmin(admin.ModelAdmin):
    list_display = ("name", "human_support_phone", "updated_at")
    fieldsets = (
        ("Identificação", {"fields": ("name", "address", "google_maps_url")}),
        ("Atendimento", {"fields": ("human_support_phone", "opening_hours")}),
        ("Mensagens", {"fields": ("welcome_message", "closing_message")}),
    )

    def has_add_permission(self, request):
        return not InstitutionSettings.objects.exists()
