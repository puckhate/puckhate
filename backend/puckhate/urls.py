from django.contrib import admin
from django.urls import include, path, re_path

from puckhate.views import protected_media

admin.site.site_header = "PUCKHATE!"
admin.site.site_title = "PUCKHATE! Admin"
admin.site.index_title = "PUCKHATE! Admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    # Staff-only private media (receipts).
    re_path(r"^private-media/(?P<path>.+)$", protected_media, name="protected-media"),
    # Anything not matched above is served the SPA by SPAFallbackMiddleware
]
