from .list import ProductListView
from .detail import ProductDetailView
from api.v1.endpoints.stats.statistics import TopViewedProductsView

__all__ = [
    "ProductListView",
    "ProductDetailView",
    "TopViewedProductsView",
]
