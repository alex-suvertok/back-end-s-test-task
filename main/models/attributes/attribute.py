from django.db import models
from ..base import BaseModel
from django.utils.translation import gettext_lazy as _


class Attribute(BaseModel):
    """Model for attributes."""

    sort_order = models.PositiveSmallIntegerField(
        verbose_name=_("Sort Order"), default=0
    )
    label = models.CharField(verbose_name=_("Label"), max_length=255)
    title = models.CharField(verbose_name=_("Title"), max_length=255)
    help_text = models.TextField(verbose_name=_("Help Text"), blank=True, null=True)
    value_type = models.CharField(verbose_name=_("Value Type"), max_length=255)
    unit_max = models.FloatField(verbose_name=_("Unit Max"), blank=True, null=True)
    unit_min = models.FloatField(verbose_name=_("Unit Min"), blank=True, null=True)
    unit = models.ForeignKey(
        "main.Unit",
        on_delete=models.CASCADE,
        db_column="unit_id",
        verbose_name="Unit",
        blank=True,
        null=True,
    )
    is_capitalized = models.BooleanField(
        verbose_name=_("Is Capitalized"), default=False
    )

    class Meta:
        db_table = "attributes_attribute"
        verbose_name = _("Attribute")
        verbose_name_plural = _("Attributes")
        ordering = ["sort_order"]
        indexes = [
            models.Index(fields=["title"], name="attribute_title_idx"),
            models.Index(fields=["sort_order"], name="attribute_sort_order_idx"),
        ]

    def __str__(self):
        return self.title
