from django.db import models
from ..base import BaseModel
from django.utils.translation import gettext_lazy as _


class CategoryAttributeConfig(BaseModel):
    sort_order = models.IntegerField(verbose_name=_("Sort Order"))
    is_grouping = models.BooleanField(default=False, verbose_name=_("Is Grouping"))
    is_blocking = models.BooleanField(default=False, verbose_name=_("Is Blocking"))
    is_comparison = models.BooleanField(default=False, verbose_name=_("Is Comparison"))
    is_required = models.BooleanField(default=False, verbose_name=_("Is Required"))
    attribute = models.ForeignKey(
        "main.Attribute",
        on_delete=models.CASCADE,
        related_name="category_attribute_configs",
        db_column="attribute_id",
        verbose_name=_("Attribute"),
    )
    category = models.ForeignKey(
        "main.Category",
        on_delete=models.CASCADE,
        related_name="category_attribute_configs",
        db_column="category_id",
        verbose_name=_("Category"),
        blank=True,
        null=True,
    )
    metadata = models.JSONField(verbose_name=_("Metadata"), blank=True, null=True)
    private_metadata = models.JSONField(
        verbose_name=_("Private Metadata"), blank=True, null=True
    )
    create_widget_type = models.CharField(
        max_length=15, verbose_name=_("Create Widget Type"), blank=True, null=True
    )
    filter_widget_type = models.CharField(
        max_length=15, verbose_name=_("Filter Widget Type"), blank=True, null=True
    )
    create_widget_attributes = models.JSONField(
        verbose_name=_("Create Widget Attributes"), blank=True, null=True
    )
    is_filterable = models.BooleanField(default=False, verbose_name=_("Is Filterable"))
    is_show_variant_preview = models.BooleanField(
        default=False, verbose_name=_("Is Show Variant Preview")
    )
    display_for_category_descendants = models.BooleanField(
        default=False, verbose_name=_("Display For Category Descendants")
    )

    class Meta:
        db_table = "store_categoryattributeconfig"
        verbose_name = _("Category Attribute Config")
        verbose_name_plural = _("Category Attribute Configs")
        ordering = ["sort_order"]
        indexes = [
            models.Index(
                fields=["attribute", "category"], name="category_attribute_idx"
            )
        ]
