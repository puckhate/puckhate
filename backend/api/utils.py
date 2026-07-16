import ipaddress


def get_client_ip(request) -> str | None:
    """Best-effort real client IP for an incoming request.

    Resolution order:

    1. CF-Connecting-IP: set (and overwritten) by Cloudflare, so a client
       behind Cloudflare cannot spoof it. Preferred because the app sits behind
       Cloudflare in production.
    2. The left-most X-Forwarded-For: the original client when the
       app is deployed behind a plain reverse proxy.
    3. REMOTE_ADDR: the direct peer (local development / no proxy)

    Returns None  when the request is missing or no source yields a valid address.
    """
    if request is None:
        return None
    meta = getattr(request, "META", {}) or {}
    candidates = [
        meta.get("HTTP_CF_CONNECTING_IP"),
        (meta.get("HTTP_X_FORWARDED_FOR") or "").split(",")[0],
        meta.get("REMOTE_ADDR"),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        try:
            return str(ipaddress.ip_address(candidate.strip()))
        except ValueError:
            continue
    return None
