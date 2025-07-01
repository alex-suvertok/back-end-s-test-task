from django.urls import path

from .endpoints.categories import CategoryDetailView, CategoryListView
from .endpoints.products import (
    ProductDetailView,
    ProductListView,
    TopViewedProductsView,
)
from .endpoints.stats.statistics import (
    FeedParsingSummaryView,
    PopularCategoriesView,
    ProductStatusStatsView,
)

app_name = "v1"

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path(
        "categories/<int:category_id>/",
        CategoryDetailView.as_view(),
        name="category-detail",
    ),
    path("products/", ProductListView.as_view(), name="product-list"),
    path(
        "products/<int:product_id>/", ProductDetailView.as_view(), name="product-detail"
    ),
    path(
        "stats/top-viewed-products/",
        TopViewedProductsView.as_view(),
        name="top-viewed-products",
    ),
    path("stats/feeds/summary/", FeedParsingSummaryView.as_view(), name="feed-summary"),
    path(
        "stats/products/counts/",
        ProductStatusStatsView.as_view(),
        name="product-status-stats",
    ),
    path(
        "stats/categories/popular/",
        PopularCategoriesView.as_view(),
        name="popular-categories",
    ),
]
