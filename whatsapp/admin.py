from django.contrib import admin

from .models import MessageLog


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ("external_message_id", "contact", "direction", "message_type", "processing_status", "created_at")
    list_filter = ("direction", "message_type", "processing_status", "created_at")
    search_fields = ("external_message_id", "contact__name", "error_code")
    readonly_fields = ("external_message_id", "contact", "direction", "message_type", "processing_status", "error_code", "created_at", "processed_at")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
