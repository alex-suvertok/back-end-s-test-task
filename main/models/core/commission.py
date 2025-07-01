from django.db import models
from ..base import BaseModel
from django.utils.translation import gettext_lazy as _


class Commission(BaseModel):
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Amount")
    )

    class Meta:
        db_table = "core_commision"
        verbose_name = _("Commission")
        verbose_name_plural = _("Commissions")

    def __str__(self):
        return f"{self.amount}"
