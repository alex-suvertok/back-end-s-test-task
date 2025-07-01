from django.contrib import admin
from django.utils.html import format_html

from main.models import FeedParsingReport, ProductAttribute, ProductImage
from main.models.store.feed import FeedParsingReportItem


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1
    raw_id_fields = ("attribute", "value")
    fields = ("attribute", "value", "raw_value")


class FeedParsingReportInline(admin.TabularInline):
    model = FeedParsingReport
    extra = 0
    readonly_fields = (
        "status",
        "started_at",
        "finished_at",
        "total_products",
        "products_added",
        "products_updated",
        "products_failed",
        "products_unpublished",
        "download_error",
        "parsing_error",
    )
    fields = (
        "status",
        "started_at",
        "finished_at",
        ("total_products", "products_added", "products_updated"),
        ("products_failed", "products_unpublished"),
        "download_error",
        "parsing_error",
    )
    ordering = ("-started_at",)
    max_num = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "position", "preview")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px;" />', obj.image.url
            )
        return "-"

    preview.short_description = "Preview"


class FeedParsingReportItemInline(admin.TabularInline):
    model = FeedParsingReportItem
    extra = 0
    readonly_fields = ["product_external_id", "success", "error_message"]
    fields = ["product_external_id", "success", "error_message"]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False
