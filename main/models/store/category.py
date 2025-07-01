from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from ..base import BaseModel


class Category(MPTTModel, BaseModel):
    label = models.CharField(
        max_length=256, verbose_name=_("Label"), blank=True, null=True
    )
    image_alt = models.CharField(
        max_length=255, verbose_name=_("Image Alt"), blank=True, null=True
    )
    title = models.CharField(
        max_length=255, verbose_name=_("Title"), blank=True, null=True
    )
    h1_title = models.CharField(
        max_length=255, verbose_name=_("H1 Title"), blank=True, null=True
    )
    description = models.TextField(verbose_name=_("Description"), blank=True, null=True)
    google_product_category = models.TextField(
        verbose_name=_("Google Product Category"), blank=True, null=True
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        db_column="parent_id",
        verbose_name=_("Parent"),
    )
    is_featured = models.BooleanField(default=False, verbose_name=_("Is Featured"))
    banner = models.ImageField(
        upload_to="categories/banners/", verbose_name=_("Banner"), blank=True, null=True
    )
    banner_alt = models.CharField(
        max_length=255, verbose_name=_("Banner Alt"), blank=True, null=True
    )
    icon_alt = models.CharField(
        max_length=255, verbose_name=_("Icon Alt"), blank=True, null=True
    )
    commission = models.ForeignKey(
        "main.Commission",
        on_delete=models.CASCADE,
        related_name="categories",
        db_column="commission_id",
        verbose_name=_("Commission"),
        blank=True,
        null=True,
    )
    can_add_products = models.BooleanField(
        default=True, verbose_name=_("Can Add Products")
    )
    has_active_products = models.BooleanField(
        default=False, verbose_name=_("Has Active Products")
    )
    is_for_adult = models.BooleanField(default=False, verbose_name=_("Is For Adult"))
    keywords = ArrayField(
        models.CharField(max_length=255),
        verbose_name=_("Keywords"),
        blank=True,
        null=True,
    )
    icon = models.ImageField(
        upload_to="categories/icons/", verbose_name=_("Icon"), blank=True, null=True
    )
    img = models.ImageField(
        upload_to="categories/", verbose_name=_("Image"), blank=True, null=True
    )
    keywords_lowercased = ArrayField(
        models.CharField(max_length=255),
        verbose_name=_("Keywords Lowercased"),
        blank=True,
        null=True,
    )
    active_product_count = models.IntegerField(
        verbose_name=_("Active Product Count"), default=0
    )

    class Meta:
        db_table = "store_category"
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["title"]
        indexes = [
            models.Index(
                fields=["parent_id", "is_active"], name="category_parent_active_idx"
            ),
            models.Index(fields=["title"], name="category_title_idx"),
        ]

    def __str__(self):
        return self.title or f"Category #{self.pk}"
