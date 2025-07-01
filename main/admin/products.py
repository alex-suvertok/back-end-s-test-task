from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin

from main.models import Product
from .inlines import ProductAttributeInline, ProductImageInline


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = (
        "name",
        "vendor",
        "price",
        "status",
        "available",
        "category_link",
        "views_count",
        "is_active",
    )
    list_filter = ["status", "is_active", "is_new", "available", "category"]
    list_editable = [
        "status",
        "available",
    ]
    search_fields = ["name", "description", "vendor", "article"]
    readonly_fields = ["views_count", "created", "modified", "external_id"]
    inlines = [ProductAttributeInline, ProductImageInline]

    fieldsets = (
        (
            "General",
            {
                "fields": (
                    "name",
                    "description",
                    "category",
                    "status",
                    "is_active",
                    "is_new",
                )
            },
        ),
        ("Pricing", {"fields": ("price", "old_price", "promo_price", "currency")}),
        (
            "Vendor Info",
            {"fields": ("vendor", "article", "external_id", "feed_source", "url")},
        ),
        ("Stock", {"fields": ("stock_quantity", "available")}),
        (
            "Statistics",
            {
                "fields": ("views_count", "created", "modified"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("category")

    def category_link(self, obj):
        if obj.category:
            url = f"/admin/main/category/{obj.category.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.category.title)
        return "-"

    category_link.short_description = _("Category")
