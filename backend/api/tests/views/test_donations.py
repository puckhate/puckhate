from datetime import timedelta
from decimal import Decimal
from unittest import mock

from django.urls import reverse
from django.utils import timezone

from api import banned_words as bw
from api.models import Ban, Charity, Donation, SiteStats
from api.tests.base import ApiTestCase
from api.tests.factories import make_charity, make_donation, make_receipt
from api.throttling import DonationReportThrottle


class DonationListTests(ApiTestCase):
    """GET /api/donations/"""

    url = reverse("donations")

    def test_lists_only_verified_donations(self):
        verified = make_donation(verified=True)
        make_donation(verified=False)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual([d["id"] for d in response.data["results"]], [verified.pk])  # ty: ignore[unresolved-attribute]

    def test_paginates_with_limit_and_offset(self):
        make_donation(_count=3)
        response = self.client.get(self.url, {"limit": 2})
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

    def test_default_order_is_most_recently_verified_first(self):
        older = make_donation(amount=Decimal("10.00"))
        newer = make_donation(amount=Decimal("20.00"))
        Donation.objects.filter(pk=older.pk).update(  # ty: ignore[unresolved-attribute]
            verified=timezone.now() - timedelta(days=1)
        )
        response = self.client.get(self.url)
        self.assertEqual(
            [d["id"] for d in response.data["results"]],
            [newer.pk, older.pk],  # ty: ignore[unresolved-attribute]
        )

    def test_top_orders_by_amount_descending(self):
        small = make_donation(amount=Decimal("5.00"))
        large = make_donation(amount=Decimal("500.00"))
        medium = make_donation(amount=Decimal("50.00"))
        response = self.client.get(self.url, {"top": ""})
        self.assertEqual(
            [d["id"] for d in response.data["results"]],
            [large.pk, medium.pk, small.pk],  # ty: ignore[unresolved-attribute]
        )

    def test_serializes_expected_fields(self):
        make_donation(
            amount=Decimal("25.00"),
            name="Jane",
            charity=make_charity(name="Great Cause"),
        )
        response = self.client.get(self.url)
        result = response.data["results"][0]
        self.assertEqual(
            set(result.keys()), {"id", "created", "amount", "name", "charity"}
        )
        self.assertEqual(result["amount"], "25.00")
        self.assertEqual(result["name"], "Jane")
        self.assertEqual(result["charity"], "Great Cause")

    def test_blank_name_displays_as_anonymous(self):
        make_donation(name="")
        response = self.client.get(self.url)
        self.assertEqual(response.data["results"][0]["name"], "Anonymous")

    def test_empty_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])


class DonationReportTests(ApiTestCase):
    """POST /api/donations/"""

    url = reverse("donations")

    def test_creates_a_draft_donation(self):
        response = self.client.post(
            self.url, {"amount": "25.00", "charity": "Feel Good, Inc."}
        )
        self.assertEqual(response.status_code, 201)
        donation = Donation.objects.get()  # ty: ignore[unresolved-attribute]
        self.assertFalse(donation.is_verified)
        self.assertEqual(donation.amount, Decimal("25.00"))
        self.assertEqual(donation.charity.name, "Feel Good, Inc.")
        self.assertEqual(response.data["charity"], "Feel Good, Inc.")

    def test_usd_amount_is_stored_verbatim(self):
        self.client.post(
            self.url,
            {"amount": "30.00", "charity": "Helping Hamburgers", "currency": "USD"},
        )
        donation = Donation.objects.get()  # ty: ignore[unresolved-attribute]
        self.assertEqual(donation.amount, Decimal("30.00"))
        self.assertEqual(donation.effective_exchange_rate, Decimal("1.0000"))

    def test_cad_amount_is_converted_to_usd(self):
        stats = SiteStats.load()
        stats.ca_exchange_rate = Decimal("1.2500")
        stats.save()
        self.client.post(
            self.url,
            {"amount": "25.00", "charity": "Helping Hamburgers", "currency": "CAD"},
        )
        donation = Donation.objects.get()  # ty: ignore[unresolved-attribute]
        self.assertEqual(donation.amount, Decimal("20.00"))
        self.assertEqual(donation.effective_exchange_rate, Decimal("1.2500"))

    def test_reuses_existing_charity_case_insensitively(self):
        make_charity(name="Blue and Pink Cross")
        self.client.post(
            self.url, {"amount": "25.00", "charity": "blue and pink cross"}
        )
        self.assertEqual(Charity.objects.count(), 1)  # ty: ignore[unresolved-attribute]
        self.assertEqual(Donation.objects.get().charity.name, "Blue and Pink Cross")  # ty: ignore[unresolved-attribute]
        self.assertTrue(Donation.objects.get().charity.approved)  # ty: ignore[unresolved-attribute]

    def test_proposed_charity_is_created_unapproved(self):
        self.client.post(self.url, {"amount": "25.00", "charity": "Brand New Cause"})
        charity = Charity.objects.get(name="Brand New Cause")  # ty: ignore[unresolved-attribute]
        self.assertFalse(charity.approved)

    def test_claims_a_receipt_by_token(self):
        receipt = make_receipt()
        response = self.client.post(
            self.url,
            {
                "amount": "25.00",
                "charity": "Saving Lives",
                "receipt": str(receipt.token),  # ty: ignore[unresolved-attribute]
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Donation.objects.get().receipt_id, receipt.pk)  # ty: ignore[unresolved-attribute]

    def test_rejects_a_receipt_already_claimed(self):
        receipt = make_receipt()
        make_donation(receipt=receipt)
        response = self.client.post(
            self.url,
            {
                "amount": "25.00",
                "charity": "Solving Problems",
                "receipt": str(receipt.token),  # ty: ignore[unresolved-attribute]
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("receipt", response.data)

    def test_rejects_non_positive_amount(self):
        response = self.client.post(self.url, {"amount": "0", "charity": "Making Hope"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("amount", response.data)
        self.assertEqual(Donation.objects.count(), 0)  # ty: ignore[unresolved-attribute]

    def test_requires_a_charity(self):
        response = self.client.post(self.url, {"amount": "25.00"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("charity", response.data)

    @mock.patch.object(bw, "BANNED_WORDS", frozenset({"badword"}))
    def test_banned_word_is_silently_dropped(self):
        with self.assertLogs("api.serializers", level="INFO"):
            response = self.client.post(
                self.url, {"amount": "25.00", "charity": "badword fund"}
            )
        self.assertEqual(response.status_code, 201)  # feigned success with a 201
        self.assertFalse(response.data)
        self.assertEqual(Donation.objects.count(), 0)  # ty: ignore[unresolved-attribute]

    @mock.patch.object(bw, "BANNED_WORDS", frozenset({"badword"}))
    def test_banned_word_auto_bans_the_ip(self):
        with self.assertLogs("api.serializers", level="INFO"):
            self.client.post(
                self.url,
                {"amount": "25.00", "charity": "Happy Days Fund", "name": "badword"},
            )
        ban = Ban.objects.get(ip="127.0.0.1")  # ty: ignore[unresolved-attribute]
        self.assertEqual(ban.type, Ban.Type.AUTO)

    def test_banned_ip_is_silently_dropped(self):
        Ban.objects.create(ip="127.0.0.1", type=Ban.Type.ADMIN, reason="spam")  # ty: ignore[unresolved-attribute]
        response = self.client.post(
            self.url, {"amount": "25.00", "charity": "Big Foundation"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.data)
        self.assertEqual(Donation.objects.count(), 0)  # ty: ignore[unresolved-attribute]


class DonationThrottleTests(ApiTestCase):
    """api.throttling.DonationReportThrottle"""

    url = reverse("donations")

    def setUp(self):
        super().setUp()
        # Patch the rate on the throttle class to a low value
        patcher = mock.patch.dict(
            DonationReportThrottle.THROTTLE_RATES, {"donations": "1/min"}
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_second_write_is_throttled(self):
        payload = {"amount": "25.00", "charity": "Helpers"}
        first = self.client.post(self.url, payload)
        second = self.client.post(self.url, payload)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 429)

    def test_reads_are_not_throttled(self):
        make_donation(_count=2)
        self.client.post(self.url, {"amount": "25.00", "charity": "Helpers"})
        for _ in range(3):
            self.assertEqual(self.client.get(self.url).status_code, 200)
