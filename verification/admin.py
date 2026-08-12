from django.contrib import admin

from .models import ScanEvent


@admin.register(ScanEvent)
class ScanEventAdmin(admin.ModelAdmin):
    list_display = ["scanned_at", "product", "verdict", "region", "device_category"]
    list_filter = ["verdict", "device_category"]
    readonly_fields = ["product", "scanned_at", "region", "device_category", "verdict"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
