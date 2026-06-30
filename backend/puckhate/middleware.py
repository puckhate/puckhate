from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.urls import Resolver404, resolve


class SPAFallbackMiddleware:
    """Serve the built SPA's index.html for any GET/HEAD path no backend route
    claims, so react-router can take over client-side routing.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            response.status_code == 404
            and request.method in ("GET", "HEAD")
            # Keep the API namespace returning real 404s
            # rather than the SPA shell.
            and not request.path_info.startswith("/api/")
        ):
            try:
                resolve(request.path_info)
            except Resolver404:
                return self._spa_index()
        return response

    @staticmethod
    def _spa_index():
        index_file = settings.SPA_DIR / "index.html"
        if index_file.exists():
            response = FileResponse(open(index_file, "rb"))
            # The SPA shell references the latest content-hashed assets, so it
            # must never be served stale
            response["Cache-Control"] = "no-cache"
            return response
        return HttpResponse(
            "SPA build not found. Run `npm run build` in frontend/ "
            "(or use the Vite dev server during development).",
            status=501,
            content_type="text/plain",
        )
