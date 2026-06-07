from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.views.decorators.http import require_GET


@require_GET
def spa_index(request):
    """Serve the built SPA's index.html

    react-router takes over client-side routing for child routes
    """
    index_file = settings.SPA_DIR / "index.html"
    if index_file.exists():
        return FileResponse(open(index_file, "rb"))
    return HttpResponse(
        "SPA build not found. Run `npm run build` in frontend/ "
        "(or use the Vite dev server during development).",
        status=501,
        content_type="text/plain",
    )
