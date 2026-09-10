from django.contrib import admin

from .models import CustodyTransfer, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Shown here, revoked elsewhere.

    The status and the revocation reason are read-only for the same reason the
    passport code is: this site edits fields directly, so a revocation made
    here would carry no check that a reason was given and leave nothing in the
    audit trail, and the reason for a revocation already made could be
    rewritten afterwards.

    `Product.revoke` is the way in, and until Sprint 4 it is the only one:
    FR41 and FR42 are what give revocation a page, for the company and for the
    administrator. Revoking is therefore something only code does today.
    """

    list_display = ["name", "passport_code", "company", "product_type", "status"]
    list_filter = ["status", "product_type", "category"]
    search_fields = ["name", "passport_code", "company__legal_name"]
    readonly_fields = [
        "passport_code",
        "status",
        "revocation_reason",
        "integrity_hash",
        "registered_at",
        "updated_at",
    ]


@admin.register(CustodyTransfer)
class CustodyTransferAdmin(admin.ModelAdmin):
    list_display = ["product", "from_holder", "to_holder", "state", "created_at"]
    list_filter = ["state"]
    readonly_fields = ["created_at", "resolved_at"]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
