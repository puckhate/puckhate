from django.contrib import admin
from django.urls import include, path, re_path

from puckcurl.views import spa_index

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    re_path(r"^.*$", spa_index, name="spa"),
]
