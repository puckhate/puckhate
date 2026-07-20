from decimal import Decimal

from django.urls import reverse

from api.models import SiteStats
from api.tests.base import ApiTestCase
from api.tests.factories import make_charity, make_donation


class SiteStatsEndpointTests(ApiTestCase):
    """GET /api/stats/"""

    url = reverse("site-stats")

    def test_totals_verified_donations(self):
        charity = make_charity(name="Helpers")
        make_donation(amount=Decimal("10.00"), charity=charity)
        make_donation(amount=Decimal("40.00"), charity=charity)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["verified_total"], "50.00")
        self.assertEqual(response.data["verified_count"], 2)
        self.assertEqual(response.data["largest_donation"], "40.00")
        self.assertEqual(response.data["charities_donated_to"], 1)

    def test_total_ignores_unverified_donations(self):
        make_donation(amount=Decimal("10.00"), verified=True)
        make_donation(amount=Decimal("99.00"), verified=False)
        response = self.client.get(self.url)
        self.assertEqual(response.data["verified_total"], "10.00")
        self.assertEqual(response.data["verified_count"], 1)
        self.assertEqual(response.data["largest_donation"], "10.00")

    def test_counts_distinct_charities(self):
        one = make_charity(name="One")
        two = make_charity(name="Two")
        three = make_charity(name="Three")
        make_donation(charity=one, verified=True)
        make_donation(charity=one, verified=True)  # duplicate charity: ignored
        make_donation(charity=two, verified=False)  # unverified: ignored
        make_donation(charity=three, verified=True)
        response = self.client.get(self.url)
        self.assertEqual(response.data["charities_donated_to"], 2)

    def test_empty_campaign_reports_zeroes(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["verified_total"], "0.00")
        self.assertEqual(response.data["verified_count"], 0)
        self.assertIsNone(response.data["largest_donation"])
        self.assertEqual(response.data["charities_donated_to"], 0)

    def test_exposes_goals_and_exchange_rate(self):
        stats = SiteStats.load()
        stats.goals_scored = 7
        stats.ca_exchange_rate = Decimal("1.3600")
        stats.save()
        response = self.client.get(self.url)
        self.assertEqual(response.data["goals_scored"], 7)
        self.assertEqual(response.data["ca_exchange_rate"], "1.3600")

    def test_response_is_cached(self):
        make_donation(amount=Decimal("10.00"))
        first = self.client.get(self.url).data["verified_total"]
        make_donation(amount=Decimal("40.00"))
        second = self.client.get(self.url).data["verified_total"]
        self.assertEqual(first, "10.00")
        self.assertEqual(second, "10.00")

    def test_rejects_post(self):
        self.assertEqual(self.client.post(self.url).status_code, 405)


class ExchangeRateEndpointTests(ApiTestCase):
    """GET /api/exchange-rate/"""

    url = reverse("exchange-rate")

    def test_returns_current_rate(self):
        stats = SiteStats.load()
        stats.ca_exchange_rate = Decimal("1.2500")
        stats.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"ca_exchange_rate": "1.2500"})

    def test_defaults_when_no_stats_saved(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["ca_exchange_rate"], "1.0000")

    def test_rejects_post(self):
        self.assertEqual(self.client.post(self.url).status_code, 405)
