from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, Http404, HttpResponse
from django.views.decorators.http import require_GET

# Public routes worth advertising to crawlers
# Must be manually maintained, see frontend/src/constants.ts#ROUTES
SITEMAP_PATHS = ("/", "/about", "/charities", "/donations", "/privacy", "/disclaimer")


@require_GET
def robots_txt(request):
    """Serve robots.txt, gated on the ROBOTS_ALLOW setting"""
    if settings.ROBOTS_ALLOW:
        lines = [
            "User-agent: *",
            "Allow: /",
            f"Sitemap: {settings.SITE_URL}/sitemap.xml",
            "Content-Signal: ai-train=no, search=yes, ai-input=yes",
        ]
    else:
        lines = [
            "User-agent: *",
            "Disallow: /",
            "Content-Signal: ai-train=no, search=no, ai-input=no",
        ]
    body = "\n".join(lines) + "\n"
    return HttpResponse(body, content_type="text/plain")


@require_GET
def sitemap_xml(request):
    """Serve a basic sitemap of the public SPA routes"""
    urls = "".join(
        f"<url><loc>{settings.SITE_URL}{path}</loc></url>" for path in SITEMAP_PATHS
    )
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{urls}</urlset>"
    )
    return HttpResponse(body, content_type="application/xml")


@staff_member_required
@require_GET
def protected_media(request, path):
    """Serve a file from PRIVATE_MEDIA_ROOT to staff only.

    Private uploads (donation receipts) are considered sensitive and are never public.
    They live under their own root, separate from the public MEDIA_ROOT, and are only
    reachable through this view.
    """
    private_root = Path(settings.PRIVATE_MEDIA_ROOT).resolve()
    full_path = (private_root / path).resolve()
    if private_root not in full_path.parents or not full_path.is_file():
        raise Http404
    response = FileResponse(open(full_path, "rb"))
    # These files are sensitive. Instruct caches / proxies never to store
    # them so a private file can't leak from a cache.
    response["Cache-Control"] = "no-store, private"
    return response
