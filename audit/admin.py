from django.contrib import admin

from .models import AuditEntry


@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ["created_at", "action", "target_type", "target_id", "actor"]
    list_filter = ["action", "target_type"]
    search_fields = ["reason"]
    readonly_fields = ["actor", "action", "target_type", "target_id", "reason", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
