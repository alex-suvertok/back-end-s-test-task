import logging

from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.exceptions import CategoryNotFound
from api.v1.serializers.category import CategoryDetailSerializer
from main.models import Category, Product

logger = logging.getLogger(__name__)


@method_decorator(name="get", decorator=cache_page(60, key_prefix="category_detail"))
class CategoryDetailView(APIView):
    @extend_schema(
        summary="Get category details",
        description="Returns category details with its children and active products.",
        responses={
            200: CategoryDetailSerializer,
            404: OpenApiResponse(
                description="Category not found",
                examples={"application/json": {"detail": "Category not found"}},
            ),
            500: OpenApiResponse(
                description="Unexpected server error",
                examples={"application/json": {"error": "Something went wrong"}},
            ),
        },
    )
    def get(self, request, category_id):
        try:
            category = Category.objects.prefetch_related(
                Prefetch(
                    "products",
                    queryset=Product.objects.filter(is_active=True),
                    to_attr="active_products",
                ),
                "children",
            ).get(id=category_id, is_active=True)

            serializer = CategoryDetailSerializer(
                category, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Category.DoesNotExist:
            raise CategoryNotFound()
        except Exception as e:
            logger.exception(f"Unexpected error in CategoryDetailView: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
