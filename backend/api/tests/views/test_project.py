import json
import os
import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.test import override_settings
from django.urls import reverse

from api.tests.base import VALID_PNG_BYTES, ApiTestCase
from api.tests.factories import make_user
from puckhate.middleware import SPAFallbackMiddleware


class SPABuildMixin:
    """Stand up a fake prerendered SPA"""

    routes = ("/", "/about", "/stats")

    def setUp(self):
        super().setUp()  # ty: ignore[unresolved-attribute]
        spa_dir = Path(tempfile.mkdtemp(prefix="puckhate-spa-"))
        self.addCleanup(shutil.rmtree, spa_dir, ignore_errors=True)  # ty: ignore[unresolved-attribute]

        for route in self.routes:
            target = spa_dir / route.strip("/") / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"<html><body>route:{route}</body></html>")
        (spa_dir / "__spa-fallback.html").write_text(
            "<html><body>spa-fallback</body></html>"
        )
        (spa_dir / "routes.json").write_text(json.dumps(list(self.routes)))

        self.spa_dir = spa_dir
        overrides = override_settings(SPA_DIR=spa_dir)
        overrides.enable()
        self.addCleanup(overrides.disable)  # ty: ignore[unresolved-attribute]


class RobotsTxtTests(ApiTestCase):
    """GET /robots.txt"""

    url = reverse("robots-txt")

    @override_settings(ROBOTS_ALLOW=True, SITE_URL="https://example.test")
    def test_allows_crawlers_when_enabled(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/plain"))
        body = response.content.decode()
        self.assertIn("Allow: /", body)
        self.assertIn("Sitemap: https://example.test/sitemap.xml", body)
        self.assertIn("ai-train=no", body)
        self.assertNotIn("Disallow: /", body)

    @override_settings(ROBOTS_ALLOW=False)
    def test_disallows_crawlers_when_disabled(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("Disallow: /", body)
        self.assertIn("search=no", body)
        self.assertNotIn("Allow: /", body)

    def test_rejects_post(self):
        self.assertEqual(self.client.post(self.url).status_code, 405)


class SitemapXmlTests(SPABuildMixin, ApiTestCase):
    """GET /sitemap.xml"""

    url = reverse("sitemap-xml")

    @override_settings(SITE_URL="https://example.test")
    def test_lists_paths_from_the_build_manifest(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("application/xml"))
        body = response.content.decode()
        self.assertIn("<loc>https://example.test/</loc>", body)
        self.assertIn("<loc>https://example.test/about</loc>", body)
        self.assertIn("<loc>https://example.test/stats</loc>", body)
        # Only routes the build actually prerendered
        self.assertNotIn("<loc>https://example.test/privacy</loc>", body)

    @override_settings(
        SITE_URL="https://example.test", SPA_DIR=Path("/nonexistent/spa/client")
    )
    def test_falls_back_to_the_home_page_without_a_build(self):
        """A backend running without a SPA build still serves valid XML."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("<loc>https://example.test/</loc>", body)
        self.assertNotIn("/about", body)

    def test_rejects_post(self):
        self.assertEqual(self.client.post(self.url).status_code, 405)


class SPAFallbackTests(SPABuildMixin, ApiTestCase):
    """Serving the prerendered SPA for paths no backend route claims"""

    def body(self, response) -> str:
        return b"".join(response.streaming_content).decode()

    def test_prerendered_route_is_served_with_200(self):
        response = self.client.get("/about")
        self.assertEqual(response.status_code, 200)
        self.assertIn("route:/about", self.body(response))
        self.assertEqual(response["Cache-Control"], "no-cache")

    def test_root_is_served_with_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("route:/", self.body(response))

    def test_trailing_slash_resolves_to_the_same_route(self):
        response = self.client.get("/about/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("route:/about", self.body(response))

    def test_unknown_path_returns_404_with_the_spa_shell(self):
        """Users still get the styled NotFoundView; crawlers get a real 404."""
        response = self.client.get("/wp-admin")
        self.assertEqual(response.status_code, 404)
        self.assertIn("spa-fallback", self.body(response))

    def test_deep_unknown_path_returns_404(self):
        response = self.client.get("/about/x/y/z")
        self.assertEqual(response.status_code, 404)

    def test_api_namespace_is_left_alone(self):
        """API 404s stay real 404s rather than becoming the SPA shell."""
        response = self.client.get("/api/does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertNotIn("spa-fallback", response.content.decode())

    def test_path_traversal_is_refused(self):
        """A path escaping SPA_DIR never resolves to a file on disk."""
        outside = self.spa_dir.parent / "puckhate-outside"
        outside.mkdir(exist_ok=True)
        (outside / "index.html").write_text("<html>secret</html>")
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)

        self.assertIsNone(
            SPAFallbackMiddleware._prerendered_index_html("/../puckhate-outside"),
        )
        self.assertIsNone(
            SPAFallbackMiddleware._prerendered_index_html("/about/../../etc")
        )
        # A legitimate route still resolves
        self.assertIsNotNone(SPAFallbackMiddleware._prerendered_index_html("/about"))

    def test_post_is_not_given_the_spa(self):
        self.assertEqual(self.client.post("/about").status_code, 404)

    @override_settings(SPA_DIR=Path("/nonexistent/spa/client"))
    def test_missing_build_reports_501(self):
        response = self.client.get("/about")
        self.assertEqual(response.status_code, 501)


class ProtectedMediaTests(ApiTestCase):
    """GET /private-media/<path>"""

    def url_for(self, path: str) -> str:
        return reverse("protected-media", kwargs={"path": path})

    def create_private_file(
        self, relpath: str = "receipts/receipt.png", content: bytes = VALID_PNG_BYTES
    ) -> str:
        full_path = os.path.join(settings.PRIVATE_MEDIA_ROOT, relpath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as fh:
            fh.write(content)
        return relpath

    def test_anonymous_is_redirected_to_login(self):
        path = self.create_private_file()
        response = self.client.get(self.url_for(path))
        self.assertEqual(response.status_code, 302)

    def test_non_staff_user_is_redirected_to_login(self):
        self.client.force_login(make_user(is_staff=False))
        path = self.create_private_file()
        response = self.client.get(self.url_for(path))
        self.assertEqual(response.status_code, 302)

    def test_staff_can_download_the_file(self):
        self.as_staff()
        path = self.create_private_file(content=VALID_PNG_BYTES)
        response = self.client.get(self.url_for(path))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), VALID_PNG_BYTES)
        self.assertEqual(response["Cache-Control"], "no-store, private")

    def test_missing_file_returns_404(self):
        self.as_staff()
        response = self.client.get(self.url_for("receipts/does-not-exist.png"))
        self.assertEqual(response.status_code, 404)

    def test_path_traversal_is_blocked(self):
        """A path escaping PRIVATE_MEDIA_ROOT is refused even for staff."""
        self.as_staff()
        # A file outside the private root must not be reachable.
        outside = os.path.join(settings.PRIVATE_MEDIA_ROOT, "..", "outside.txt")
        with open(outside, "wb") as fh:
            fh.write(b"secret")
        response = self.client.get(self.url_for("../outside.txt"))
        self.assertEqual(response.status_code, 404)

    def test_staff_post_is_rejected(self):
        self.as_staff()
        path = self.create_private_file()
        self.assertEqual(self.client.post(self.url_for(path)).status_code, 405)
