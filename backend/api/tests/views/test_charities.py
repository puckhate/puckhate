from django.urls import reverse

from api.tests.base import ApiTestCase
from api.tests.factories import make_charity


class CharitiesEndpointTests(ApiTestCase):
    """GET /api/charities/"""

    url = reverse("charities")

    def test_lists_only_approved_charities(self):
        make_charity(name="Approved Cause", approved=True)
        make_charity(name="Pending Cause", approved=False)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual([c["name"] for c in response.data], ["Approved Cause"])

    def test_orders_by_name(self):
        make_charity(name="Zulu Fund")
        make_charity(name="Alpha Fund")
        make_charity(name="Charlie Fund")
        response = self.client.get(self.url)
        names = [c["name"] for c in response.data]
        self.assertEqual(names, ["Alpha Fund", "Charlie Fund", "Zulu Fund"])

    def test_serializes_expected_fields(self):
        charity = make_charity(name="Doin' Good", url="https://dogood.test/give")
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(set(response.data[0].keys()), {"id", "name", "url"})
        self.assertEqual(response.data[0]["id"], charity.pk)  # ty: ignore[unresolved-attribute]
        self.assertEqual(response.data[0]["name"], "Doin' Good")
        self.assertEqual(response.data[0]["url"], "https://dogood.test/give")

    def test_returns_empty_list_when_none_approved(self):
        make_charity(approved=False)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_rejects_post(self):
        self.assertEqual(self.client.post(self.url).status_code, 405)
