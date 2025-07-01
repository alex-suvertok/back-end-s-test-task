from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from ..base import BaseModel


class FeedSource(BaseModel):
    name = models.CharField(_("Name"), max_length=255)
    company = models.CharField(_("Company"), max_length=255, blank=True, null=True)
    xml_url = models.URLField(_("XML URL"))
    frequency = models.IntegerField(
        _("Update Frequency (hours)"),
        default=3,
        help_text=_("Feed update frequency in hours"),
    )
    last_update = models.DateTimeField(_("Last Update"), null=True, blank=True)
    next_update = models.DateTimeField(_("Next Update"), null=True, blank=True)

    class Meta:
        db_table = "store_feedsource"
        verbose_name = _("Feed Source")
        verbose_name_plural = _("Feed Sources")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.next_update:
            self.next_update = timezone.now()
        super().save(*args, **kwargs)


class FeedParsingReport(BaseModel):
    class Status(models.IntegerChoices):
        STARTED = 1, _("Started")
        SUCCESS = 2, _("Success")
        ERROR = 3, _("Error")

    feed = models.ForeignKey(
        "FeedSource",
        on_delete=models.CASCADE,
        related_name="parsing_reports",
        verbose_name=_("Feed"),
    )
    status = models.PositiveSmallIntegerField(
        _("Status"), choices=Status.choices, default=Status.SUCCESS
    )
    started_at = models.DateTimeField(_("Started At"), auto_now_add=True)
    finished_at = models.DateTimeField(_("Finished At"), null=True, blank=True)

    total_products = models.IntegerField(_("Total Products"), default=0)
    products_added = models.IntegerField(_("Products Added"), default=0)
    products_updated = models.IntegerField(_("Products Updated"), default=0)
    products_failed = models.IntegerField(_("Products Failed"), default=0)
    products_unpublished = models.IntegerField(_("Products Unpublished"), default=0)

    download_error = models.TextField(_("Download Error"), blank=True, null=True)
    parsing_error = models.TextField(_("Parsing Error"), blank=True, null=True)

    class Meta:
        db_table = "store_feedparsingreport"
        verbose_name = _("Feed Parsing Report")
        verbose_name_plural = _("Feed Parsing Reports")
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["feed_id", "created"], name="fpr_feed_created_idx"),
            models.Index(fields=["started_at"], name="fpr_started_idx"),
        ]

    def __str__(self):
        return f"{self.feed.name} - {self.started_at}"


class FeedParsingReportItem(models.Model):
    report = models.ForeignKey(
        FeedParsingReport, related_name="items", on_delete=models.CASCADE
    )
    product_external_id = models.CharField(max_length=255)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "store_feedparsingreportitem"
        verbose_name = _("Feed Parsing Report Item")
        verbose_name_plural = _("Feed Parsing Report Items")
