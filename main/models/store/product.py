from django.db import models
from django.utils.translation import gettext_lazy as _

from ..base import BaseModel


class Product(BaseModel):
    class Status(models.IntegerChoices):
        DRAFT = 1, _("Draft")
        ACTIVE = 2, _("Active")
        ARCHIVED = 3, _("Archived")

    feed_source = models.ForeignKey(
        "FeedSource",
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("Feed Source"),
    )
    external_id = models.CharField(_("External ID"), max_length=255)
    vendor = models.CharField(_("Vendor"), max_length=255)
    article = models.CharField(_("Article"), max_length=255, blank=True, null=True)

    name = models.CharField(_("Name"), max_length=500)

    description = models.TextField(_("Description"), blank=True, null=True)

    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    old_price = models.DecimalField(
        _("Old Price"), max_digits=10, decimal_places=2, blank=True, null=True
    )
    promo_price = models.DecimalField(
        _("Promo Price"), max_digits=10, decimal_places=2, blank=True, null=True
    )
    currency = models.CharField(_("Currency"), max_length=3, default="UAH")

    stock_quantity = models.IntegerField(_("Stock Quantity"), default=0)
    available = models.BooleanField(_("Available"), default=True)

    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        related_name="products",
        null=True,
        blank=True,
        verbose_name=_("Category"),
    )

    url = models.URLField(_("URL"), max_length=500, blank=True, null=True)
    views_count = models.IntegerField(_("Views Count"), default=0)

    status = models.PositiveSmallIntegerField(
        _("Status"), choices=Status.choices, default=Status.DRAFT
    )
    published_at = models.DateTimeField(_("Published At"), null=True, blank=True)
    is_new = models.BooleanField(_("Is New"), default=False)

    class Meta:
        db_table = "store_product"
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        unique_together = ("feed_source", "external_id")
        indexes = [
            models.Index(
                fields=["status", "is_active"], name="product_status_active_idx"
            ),
            models.Index(fields=["price"], name="product_price_idx"),
            models.Index(fields=["created"], name="product_created_idx"),
            models.Index(
                fields=["name"],
                name="product_name_idx",
            ),
            models.Index(
                fields=["description"],
                name="product_description_idx",
            ),
        ]

    def __str__(self):
        return self.name


class ProductAttribute(BaseModel):
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="product_attributes",
        verbose_name=_("Product"),
    )
    attribute = models.ForeignKey(
        "Attribute",
        on_delete=models.CASCADE,
        related_name="product_attributes",
        verbose_name=_("Attribute"),
    )
    value = models.ForeignKey(
        "AttributeValue",
        on_delete=models.CASCADE,
        related_name="product_attributes",
        verbose_name=_("Value"),
    )
    raw_value = models.CharField(_("Raw Value"), max_length=500, blank=True, null=True)

    class Meta:
        db_table = "store_productattribute"
        verbose_name = _("Product Attribute")
        verbose_name_plural = _("Product Attributes")
        unique_together = ("product", "attribute", "value")
        indexes = [
            models.Index(fields=["product_id"], name="prod_attr_product_idx"),
            models.Index(fields=["attribute_id"], name="prod_attr_attribute_idx"),
            models.Index(fields=["raw_value"], name="prod_attr_raw_value_idx"),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.attribute.title}"


class ProductImage(BaseModel):
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Product"),
    )
    image = models.ImageField(_("Image"), upload_to="products/")
    position = models.PositiveIntegerField(_("Position"), default=0)

    class Meta:
        ordering = ["position"]
        db_table = "store_productimage"
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")

    def __str__(self):
        return f"Image for {self.product.name} (#{self.position})"
