from django.db import models
from ..base import BaseModel
from django.utils.translation import gettext_lazy as _


class AttributeValue(BaseModel):
    """Model for attribute values."""

    sort_order = models.PositiveSmallIntegerField(
        default=0, verbose_name=_("Sort Order")
    )
    label = models.CharField(max_length=256, verbose_name=_("Label"))
    title = models.CharField(max_length=500, verbose_name=_("Title"))
    attribute = models.ForeignKey(
        "Attribute",
        on_delete=models.CASCADE,
        related_name="values",
        db_column="attribute_id",
        verbose_name=_("Attribute"),
    )
    value_boolean = models.BooleanField(null=True, verbose_name=_("Boolean Value"))
    value_float = models.FloatField(null=True, verbose_name=_("Float Value"))
    value_integer = models.IntegerField(null=True, verbose_name=_("Integer Value"))
    value_text = models.TextField(null=True, verbose_name=_("Text Value"))
    is_for_filtering = models.BooleanField(
        default=False, verbose_name=_("Is For Filtering")
    )

    class Meta:
        db_table = "attributes_attributevalue"
        verbose_name = _("Attribute Value")
        verbose_name_plural = _("Attribute Values")
        ordering = ["sort_order"]
        indexes = [
            models.Index(
                fields=["attribute_id", "is_for_filtering"],
                name="attr_value_filter_idx",
            ),
            models.Index(fields=["sort_order"], name="attribute_value_sort_order_idx"),
            models.Index(
                fields=["label"],
                name="attributevalue_label_idx",
                opclasses=["varchar_pattern_ops"],
            ),
            models.Index(fields=["title"], name="attributevalue_title_idx"),
        ]

    def __str__(self):
        return self.title
