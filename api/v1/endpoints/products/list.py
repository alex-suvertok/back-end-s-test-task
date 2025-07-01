from django.db.models import QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from api.v1.serializers.product import ProductShortSerializer
from main.models import Attribute, AttributeValue, Product, ProductAttribute


@method_decorator(name="get", decorator=cache_page(60 * 5, key_prefix="product_list"))
class ProductListView(ListAPIView):
    serializer_class = ProductShortSerializer
    queryset = Product.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["category"]
    ordering_fields = ["price", "views_count", "is_new"]
    ordering = ["-views_count"]

    @extend_schema(
        summary="Get list of products",
        parameters=[
            OpenApiParameter(name="search", type=OpenApiTypes.STR),
            OpenApiParameter(name="price_min", type=OpenApiTypes.FLOAT),
            OpenApiParameter(name="price_max", type=OpenApiTypes.FLOAT),
            OpenApiParameter(
                name="attrs",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Attribute filters. Format: attrs=color:Red,Blue&attrs=size:M",
                many=True,
            ),
        ],
    )
    def get_queryset(self):
        qs = super().get_queryset()

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search)

        price_min = self.request.query_params.get("price_min")
        if price_min:
            qs = qs.filter(price__gte=price_min)

        price_max = self.request.query_params.get("price_max")
        if price_max:
            qs = qs.filter(price__lte=price_max)

        order_param = self.request.query_params.get("ordering")
        if order_param == "new":
            qs = qs.order_by("-is_new", "-created")

        qs = self.filter_by_attributes(qs)

        return qs

    def filter_by_attributes(self, qs) -> QuerySet:
        raw_attrs = self.request.query_params.getlist("attrs")
        if not raw_attrs:
            return qs

        parsed_filters = []
        for pair in raw_attrs:
            try:
                label, values_str = pair.split(":")
                values = [v.strip() for v in values_str.split(",") if v.strip()]
                if values:
                    parsed_filters.append((label.lower(), values))
            except ValueError:
                continue

        if not parsed_filters:
            return qs

        labels = [label for label, _ in parsed_filters]
        attributes = Attribute.objects.filter(label__in=labels)
        attribute_map = {attr.label.lower(): attr for attr in attributes}

        product_ids = None
        for label, values in parsed_filters:
            attribute = attribute_map.get(label)
            if not attribute:
                continue

            value_ids = AttributeValue.objects.filter(
                attribute=attribute, title__in=values
            ).values_list("id", flat=True)

            matched_ids = ProductAttribute.objects.filter(
                attribute=attribute, value_id__in=value_ids
            ).values_list("product_id", flat=True)

            matched_set = set(matched_ids)
            product_ids = (
                matched_set if product_ids is None else product_ids & matched_set
            )

        return qs.filter(id__in=product_ids) if product_ids is not None else qs
