from django_filters import rest_framework as filters
from main.models import Product


class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")
    attributes = filters.CharFilter(method="filter_by_attributes")

    class Meta:
        model = Product
        fields = ["min_price", "max_price", "attributes"]

    def filter_by_attributes(self, queryset, name, value):
        if not value:
            return queryset

        try:
            attr_pairs = [pair.split(":", 1) for pair in value.split(",")]
        except ValueError:
            return queryset.none()

        for attr_key, attr_value in attr_pairs:
            queryset = queryset.filter(
                product_attributes__attribute__title=attr_key,
                product_attributes__raw_value=attr_value,
            )
        return queryset
