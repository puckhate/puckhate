from django.contrib import admin
from django.urls import include, path, re_path

from puckcurl.views import protected_media

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    # Staff-only private media (receipts).
    re_path(r"^private-media/(?P<path>.+)$", protected_media, name="protected-media"),
    # Anything not matched above is served the SPA by SPAFallbackMiddleware
]
