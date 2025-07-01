from django.contrib import admin
from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin
from mptt.admin import DraggableMPTTAdmin

from main.models import Category


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin, TranslationAdmin):
    list_display = (
        "tree_actions",
        "indented_title",
        "active_products_count",
        "is_active",
        "created",
    )
    list_filter = ["is_active", "is_featured", "created"]
    search_fields = ["title", "description"]
    mptt_level_indent = 20

    fieldsets = (
        ("General", {"fields": ("parent", "title", "description", "is_active")}),
        (
            "SEO",
            {
                "fields": ("h1_title", "keywords", "google_product_category"),
                "classes": ("collapse",),
            },
        ),
        (
            "Visual",
            {
                "fields": (
                    "img",
                    "image_alt",
                    "banner",
                    "banner_alt",
                    "icon",
                    "icon_alt",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Settings",
            {
                "fields": (
                    "is_featured",
                    "commission",
                    "can_add_products",
                    "is_for_adult",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            active_products_count=Count("products", filter=Q(products__is_active=True))
        )

    def active_products_count(self, obj):
        return obj.active_products_count

    active_products_count.short_description = _("Active Products Count")
