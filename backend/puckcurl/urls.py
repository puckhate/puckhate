from django.contrib import admin
from django.urls import include, path, re_path

from puckcurl.views import protected_media

admin.site.site_header = "PUCKCURL!"
admin.site.site_title = "PUCKCURL! Admin"
admin.site.index_title = "PUCKCURL! Admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    # Staff-only private media (receipts).
    re_path(r"^private-media/(?P<path>.+)$", protected_media, name="protected-media"),
    # Anything not matched above is served the SPA by SPAFallbackMiddleware
]
