import os

from django.conf import settings
from django.test import override_settings
from django.urls import reverse

from api.tests.base import VALID_PNG_BYTES, ApiTestCase
from api.tests.factories import make_user


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


class SitemapXmlTests(ApiTestCase):
    """GET /sitemap.xml"""

    url = reverse("sitemap-xml")

    @override_settings(SITE_URL="https://example.test")
    def test_lists_public_paths(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("application/xml"))
        body = response.content.decode()
        self.assertIn("<loc>https://example.test/</loc>", body)
        self.assertIn("<loc>https://example.test/charities</loc>", body)
        self.assertIn("<loc>https://example.test/donations</loc>", body)

    def test_rejects_post(self):
        self.assertEqual(self.client.post(self.url).status_code, 405)


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
