from django.contrib import admin
from django.db.models import OuterRef, Subquery
from django.utils.html import format_html

from main.models import FeedParsingReport, FeedSource
from .inlines import FeedParsingReportInline, FeedParsingReportItemInline


@admin.register(FeedSource)
class FeedSourceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company",
        "feed_status",
        "last_update",
        "next_update",
        "is_active",
    )
    list_filter = ["is_active"]
    search_fields = ["name", "company", "xml_url"]
    readonly_fields = ["last_update", "next_update"]
    inlines = [FeedParsingReportInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        latest_report_qs = FeedParsingReport.objects.filter(
            feed=OuterRef("pk")
        ).order_by("-started_at")

        return qs.annotate(
            latest_status=Subquery(latest_report_qs.values("status")[:1])
        )

    def feed_status(self, obj):
        if obj.latest_status is None:
            return format_html('<span style="color: gray;">No reports</span>')

        status_display = dict(FeedParsingReport.Status.choices).get(
            obj.latest_status, "Unknown"
        )
        return format_html("<span>{}</span>", status_display)

    feed_status.short_description = "Status"


@admin.register(FeedParsingReport)
class FeedParsingReportAdmin(admin.ModelAdmin):
    inlines = [FeedParsingReportItemInline]
    list_display = ("feed", "status", "started_at", "finished_at", "stats_summary")
    list_filter = ["status", "started_at", "feed"]
    readonly_fields = [
        "feed",
        "status",
        "started_at",
        "finished_at",
        "total_products",
        "products_added",
        "products_updated",
        "products_failed",
        "products_unpublished",
        "download_error",
        "parsing_error",
    ]

    def stats_summary(self, obj):
        return format_html(
            """
            <div style="white-space: nowrap;">
                Total: {}<br>
                <span style="color: green;">+{}</span>,
                <span style="color: blue;">~{}</span>,
                <span style="color: red;">×{}</span>,
                <span style="color: orange;">↓{}</span>
            </div>
            """,
            obj.total_products,
            obj.products_added,
            obj.products_updated,
            obj.products_failed,
            obj.products_unpublished,
        )

    stats_summary.short_description = "Statistics"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
