from rest_framework import serializers

from main.models import Category
from .product import ProductShortSerializer


class CategoryListSerializer(serializers.HyperlinkedModelSerializer):
    child_categories_count = serializers.IntegerField(read_only=True)

    url = serializers.HyperlinkedIdentityField(
        view_name="api:v1:category-detail",
        lookup_field="id",
        lookup_url_kwarg="category_id",
    )

    class Meta:
        model = Category
        fields = (
            "id",
            "label",
            "icon",
            "icon_alt",
            "title",
            "keywords",
            "active_product_count",
            "child_categories_count",
            "url",
        )


class CategoryDetailSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    categories = CategoryListSerializer(
        many=True,
        source="get_children",
        context={"request": None},  # буде перезаписано в __init__
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "request" in self.context:
            self.fields["categories"].context["request"] = self.context["request"]
            self.fields["products"].context["request"] = self.context["request"]

    def get_products(self, obj):
        products = getattr(obj, "active_products", [])
        return ProductShortSerializer(products, many=True, context=self.context).data

    class Meta:
        model = Category
        fields = [field.name for field in model._meta.fields] + [
            "products",
            "categories",
        ]
