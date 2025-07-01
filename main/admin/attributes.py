from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from main.models import Attribute, AttributeValue, Unit
from django.utils.translation import gettext_lazy as _


@admin.register(Attribute)
class AttributeAdmin(TranslationAdmin):
    list_display = ("title", "value_type", "unit", "sort_order", "is_active")
    list_filter = ["value_type", "is_active", "is_capitalized"]
    search_fields = ["title", "help_text"]
    ordering = ["sort_order", "title"]


@admin.register(AttributeValue)
class AttributeValueAdmin(TranslationAdmin):
    list_display = (
        "title",
        "attribute",
        "value_display",
        "sort_order",
        "is_for_filtering",
    )
    list_filter = ["is_for_filtering", "is_active"]
    search_fields = ["title", "label"]
    ordering = ["attribute", "sort_order", "title"]

    def value_display(self, obj):
        for field in ("value_boolean", "value_float", "value_integer", "value_text"):
            value = getattr(obj, field)
            if value is not None:
                return str(value)
        return "-"

    value_display.short_description = _("Value")


@admin.register(Unit)
class UnitAdmin(TranslationAdmin):
    list_display = ("title", "label", "sort_order")
    search_fields = ["title", "label"]
    ordering = ["sort_order", "title"]
