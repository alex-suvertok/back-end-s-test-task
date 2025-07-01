import logging

from django.db.models import F
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.serializers.product import ProductDetailSerializer
from main.models import Product

logger = logging.getLogger(__name__)


class ProductDetailView(APIView):
    @extend_schema(
        summary="Get product details by ID",
        description="Retrieve detailed information about a specific product and increment its views count.",
        parameters=[
            OpenApiParameter(
                name="product_id",
                type=int,
                location=OpenApiParameter.PATH,
                description="ID of the product",
            )
        ],
        responses={
            200: ProductDetailSerializer,
            404: OpenApiResponse(
                description="Product not found",
                examples={"application/json": {"error": "Product not found"}},
            ),
            400: OpenApiResponse(
                description="Bad request",
                examples={"application/json": {"error": "Something went wrong"}},
            ),
        },
    )
    def get(self, request, product_id):
        try:
            product = get_object_or_404(
                Product.objects.filter(is_active=True), id=product_id
            )

            product.views_count = F("views_count") + 1
            product.save(update_fields=["views_count"])
            product.refresh_from_db()

            serializer = ProductDetailSerializer(product, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(f"Error fetching product {product_id}: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
