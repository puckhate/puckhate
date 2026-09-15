from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponsePermanentRedirect
from django.urls import Resolver404, resolve


class SPAFallbackMiddleware:
    """Serve the SPA for any GET/HEAD path no backend route claims.

    The build prerenders one index.html per route, so a known route is served
    its own HTML with a 200.
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
                return self._spa_response(request)
        return response

    @staticmethod
    def _prerendered_index_html(path_info):
        """Return the prerendered index.html for a request path if it exists, or None."""
        spa_root = settings.SPA_DIR.resolve()
        relative = path_info.strip("/") or "."
        try:
            candidate = (spa_root / relative / "index.html").resolve()
        except OSError, ValueError:
            return None
        # A path like /../../etc resolves outside the build output
        if spa_root not in candidate.parents:
            return None
        return candidate if candidate.is_file() else None

    @staticmethod
    def _canonical_path(path_info):
        """Collapse a request path to a slash-free form."""
        return "/" + path_info.strip("/")

    @classmethod
    def _spa_response(cls, request):
        """Serve the SPA as an HTTPResponse"""
        path_info = request.path_info

        # /about/ and /about answer with the same document.
        # redirect to the cannonical version with a trailing slash.
        canonical = cls._canonical_path(path_info)
        if canonical != path_info and cls._prerendered_index_html(canonical):
            query = request.META.get("QUERY_STRING")
            return HttpResponsePermanentRedirect(
                f"{canonical}?{query}" if query else canonical
            )

        prerendered = cls._prerendered_index_html(path_info)
        if prerendered is not None:
            return cls._html(prerendered, 200)

        # __spa-fallback.html is emitted by the react-router build
        # for paths that were not prerendered
        fallback = settings.SPA_DIR / "__spa-fallback.html"
        if fallback.is_file():
            return cls._html(fallback, 404)

        return HttpResponse(
            "SPA build not found. Run project with `make dev`",
            status=501,
            content_type="text/plain",
        )

    @staticmethod
    def _html(path, status):
        """Return the contents of an HTML file as a response"""
        response = FileResponse(path.open("rb"), status=status)
        # These documents reference the latest content-hashed assets, so they
        # must never be served stale
        response["Cache-Control"] = "no-cache"
        return response
