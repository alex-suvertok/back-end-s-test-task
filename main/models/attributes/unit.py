from django.db import models
from ..base import BaseModel
from django.utils.translation import gettext_lazy as _


class Unit(BaseModel):
    """Model for units of attributes."""

    sort_order = models.IntegerField(verbose_name=_("Sort Order"), default=0)
    title = models.CharField(verbose_name=_("Title"), max_length=255)
    label = models.CharField(verbose_name=_("Label"), max_length=255)

    class Meta:
        db_table = "attributes_unit"
        verbose_name = _("Unit")
        verbose_name_plural = _("Units")
        ordering = ["sort_order"]

    def __str__(self):
        return self.title
