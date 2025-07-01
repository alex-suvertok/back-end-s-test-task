from rest_framework import serializers

from main.models import Product


class ProductShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "article",
            "name",
            "price",
            "old_price",
            "stock_quantity",
            "url",
            "views_count",
        )


class ProductListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="api:v1:product-detail",
        lookup_field="id",
        lookup_url_kwarg="product_id",
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "old_price",
            "promo_price",
            "stock_quantity",
            "available",
            "is_new",
            "url",
            "views_count",
        )


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
