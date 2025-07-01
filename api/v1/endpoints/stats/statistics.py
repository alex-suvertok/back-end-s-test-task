import logging
from datetime import timedelta

from django.db.models import Case, Count, IntegerField, Max, Q, When
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.serializers.feed import FeedSummarySerializer
from api.v1.serializers.product import ProductShortSerializer
from main.models import Category, FeedParsingReport, FeedSource, Product

logger = logging.getLogger(__name__)


class TopViewedProductsView(APIView):
    @extend_schema(
        summary="Top viewed products",
        description="Returns top N most viewed products. Optional filters: category_id, days.",
        parameters=[
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                required=False,
                description="Max products to return",
            ),
            OpenApiParameter(name="category_id", type=OpenApiTypes.INT, required=False),
            OpenApiParameter(
                name="days",
                type=OpenApiTypes.INT,
                required=False,
                description="Filter by publish date (days ago)",
            ),
        ],
        responses={200: ProductShortSerializer(many=True)},
    )
    def get(self, request):
        try:
            limit = max(1, int(request.query_params.get("limit", 10)))
        except ValueError:
            logger.warning(
                f"Invalid 'limit' parameter: '{request.query_params.get('limit')}' — expected integer."
            )
            limit = 10

        category_id = request.query_params.get("category_id")
        days = request.query_params.get("days")

        products = Product.objects.filter(is_active=True)

        if category_id:
            products = products.filter(category_id=category_id)

        if days:
            try:
                days_int = int(days)
                date_threshold = timezone.now() - timedelta(days=days_int)
                products = products.filter(published_at__gte=date_threshold)
            except ValueError:
                logger.warning(
                    f"Invalid 'days' parameter: '{days}' — expected integer."
                )

        top_products = products.order_by("-views_count")[:limit]
        serializer = ProductShortSerializer(
            top_products, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class FeedParsingSummaryView(APIView):
    @extend_schema(
        summary="Feed parsing summary",
        description="Returns summary of feed parsing results per feed: total runs, success/error counts, and timestamps.",
        responses={200: FeedSummarySerializer(many=True)},
    )
    def get(self, request):
        feeds = FeedSource.objects.all()
        reports = FeedParsingReport.objects.values("feed_id").annotate(
            total=Count("id"),
            success=Count("id", filter=Q(status=FeedParsingReport.Status.SUCCESS)),
            error=Count("id", filter=Q(status=FeedParsingReport.Status.ERROR)),
            last_success_at=Max(
                "finished_at", filter=Q(status=FeedParsingReport.Status.SUCCESS)
            ),
            last_error_at=Max(
                "finished_at", filter=Q(status=FeedParsingReport.Status.ERROR)
            ),
        )

        report_map = {item["feed_id"]: item for item in reports}

        summary = []
        for feed in feeds:
            data = report_map.get(feed.id, {})
            summary.append(
                {
                    "feed_id": feed.id,
                    "feed_name": feed.name,
                    "total": data.get("total", 0),
                    "success": data.get("success", 0),
                    "error": data.get("error", 0),
                    "last_success_at": data.get("last_success_at"),
                    "last_error_at": data.get("last_error_at"),
                }
            )

        serializer = FeedSummarySerializer(summary, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductStatusStatsView(APIView):
    @extend_schema(
        summary="Product status statistics",
        description="Returns number of products in each status: active, draft, archived.",
        responses={200: dict},
    )
    def get(self, request):
        stats = Product.objects.aggregate(
            total=Count("id"),
            active=Count(
                Case(
                    When(status=Product.Status.ACTIVE, then=1),
                    output_field=IntegerField(),
                )
            ),
            draft=Count(
                Case(
                    When(status=Product.Status.DRAFT, then=1),
                    output_field=IntegerField(),
                )
            ),
            archived=Count(
                Case(
                    When(status=Product.Status.ARCHIVED, then=1),
                    output_field=IntegerField(),
                )
            ),
        )
        return Response(stats, status=status.HTTP_200_OK)


class PopularCategoriesView(APIView):
    def get(self, request):
        qs = Category.objects.annotate(product_count=Count("products")).order_by(
            "-product_count"
        )[:10]
        return Response(
            [
                {"id": c.id, "title": c.title, "product_count": c.product_count}
                for c in qs
            ]
        )
