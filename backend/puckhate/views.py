from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, Http404
from django.views.decorators.http import require_GET


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
