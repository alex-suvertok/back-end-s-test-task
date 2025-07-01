import logging

from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.exceptions import InvalidCategoryData
from api.v1.serializers.category import CategoryListSerializer
from main.models import Category

logger = logging.getLogger(__name__)


@method_decorator(name="get", decorator=cache_page(60 * 3, key_prefix="category_list"))
class CategoryListView(APIView):
    @extend_schema(
        summary="Get list of root categories",
        description="Retrieve a list of all active root categories (categories without a parent) ordered by title.",
        responses={
            200: CategoryListSerializer(many=True),
            400: OpenApiResponse(
                description="Invalid category data",
                examples={"application/json": {"detail": "Invalid category data"}},
            ),
        },
    )
    def get(self, request):
        try:
            categories = (
                Category.objects.filter(parent__isnull=True, is_active=True)
                .annotate(child_categories_count=Count("children"))
                .order_by("title")
            )

            serializer = CategoryListSerializer(
                categories, many=True, context={"request": request}
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Unexpected error in CategoryListView: {e}")
            raise InvalidCategoryData(detail=str(e))
