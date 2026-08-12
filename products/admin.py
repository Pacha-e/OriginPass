from django.contrib import admin

from .models import CustodyTransfer, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "passport_code", "company", "product_type", "status"]
    list_filter = ["status", "product_type", "category"]
    search_fields = ["name", "passport_code", "company__legal_name"]
    readonly_fields = ["passport_code", "integrity_hash", "registered_at", "updated_at"]


@admin.register(CustodyTransfer)
class CustodyTransferAdmin(admin.ModelAdmin):
    list_display = ["product", "from_holder", "to_holder", "state", "created_at"]
    list_filter = ["state"]
    readonly_fields = ["created_at", "resolved_at"]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
