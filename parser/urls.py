from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static

static_urls = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
media_urls = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += (
    i18n_patterns(
        path("admin/", admin.site.urls),
        path("", RedirectView.as_view(url="admin/")),
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/docs/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path("api/", include("api.urls")),
        prefix_default_language=True,
    )
    + static_urls
    + media_urls
)
