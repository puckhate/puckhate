from decimal import Decimal

from model_bakery import baker

from api.models import Ban, Donation, DonationReceipt, SiteStats, make_receipt_path
from api.tests.base import ApiTestCase
from api.tests.factories import make_donation, make_receipt


class DonationModelTests(ApiTestCase):
    """Donation model (non-API cases)."""

    def test_verified_total_is_zero_without_verified_donations(self):
        """The aggregate falls back to Decimal("0"), never None."""
        make_donation(verified=False)  # a draft must not count
        self.assertEqual(Donation.verified_total(), Decimal("0"))


class SiteStatsModelTests(ApiTestCase):
    """SiteStats model"""

    def test_load_creates_row_at_pk_1(self):
        stats = SiteStats.load()
        self.assertEqual(stats.pk, 1)

    def test_load_returns_the_same_row(self):
        first = SiteStats.load()
        first.goals_scored = 7
        first.save()
        second = SiteStats.load()
        self.assertEqual(second.pk, 1)
        self.assertEqual(second.goals_scored, 7)
        self.assertEqual(SiteStats.objects.count(), 1)  # ty: ignore[unresolved-attribute]

    def test_save_always_pins_pk_1(self):
        SiteStats.load()  # ensure the singleton row exists
        extra = SiteStats(pk=99, goals_scored=3)
        extra.save()
        self.assertEqual(extra.pk, 1)
        self.assertEqual(SiteStats.objects.count(), 1)  # ty: ignore[unresolved-attribute]

    def test_delete_is_a_noop(self):
        stats = SiteStats.load()
        stats.delete()
        self.assertTrue(SiteStats.objects.filter(pk=1).exists())  # ty: ignore[unresolved-attribute]


class BanModelTests(ApiTestCase):
    """Ban model (non-API cases)."""

    def test_true_for_a_banned_ip(self):
        baker.make(Ban, ip="10.0.0.1")
        self.assertTrue(Ban.is_banned("10.0.0.1"))

    def test_false_for_an_unbanned_ip(self):
        self.assertFalse(Ban.is_banned("10.0.0.99"))

    def test_false_for_none(self):
        self.assertFalse(Ban.is_banned(None))

    def test_false_for_empty_string(self):
        self.assertFalse(Ban.is_banned(""))


class ReceiptModelTests(ApiTestCase):
    """Receipt model (non-API cases)."""

    def test_stored_under_receipts_with_lowercased_extension(self):
        path = make_receipt_path(None, "MyReceipt.PNG")
        self.assertTrue(path.startswith("receipts/"))
        self.assertTrue(path.endswith(".png"))

    def test_original_filename_is_not_reused(self):
        path = make_receipt_path(None, "secret-name.pdf")
        self.assertNotIn("secret-name", path)

    def test_each_call_is_unique(self):
        first = make_receipt_path(None, "a.png")
        second = make_receipt_path(None, "a.png")
        self.assertNotEqual(first, second)

    def test_deleting_donation_deletes_its_receipt(self):
        receipt = make_receipt()
        donation = make_donation(receipt=receipt)
        donation.delete()  # ty: ignore[unresolved-attribute]
        self.assertFalse(DonationReceipt.objects.filter(pk=receipt.pk).exists())  # ty: ignore[unresolved-attribute]

    def test_deleting_donation_without_a_receipt_does_not_error(self):
        donation = make_donation(receipt=None)
        donation.delete()  # ty: ignore[unresolved-attribute]
        self.assertFalse(Donation.objects.filter(pk=donation.pk).exists())  # ty: ignore[unresolved-attribute]

    def test_deleting_donation_with_missing_receipt_does_not_error(self):
        """The ObjectDoesNotExist guard tolerates an already-gone receipt."""
        receipt = make_receipt()
        donation = make_donation(receipt=receipt)
        # Remove the receipt row out from under our stale in-memory donation.
        DonationReceipt.objects.filter(pk=receipt.pk).delete()  # ty: ignore[unresolved-attribute]
        donation.delete()  # ty: ignore[unresolved-attribute]
        self.assertFalse(Donation.objects.filter(pk=donation.pk).exists())  # ty: ignore[unresolved-attribute]

    def test_deleting_receipt_removes_the_file_from_storage(self):
        receipt = make_receipt()
        storage = receipt.file.storage  # ty: ignore[unresolved-attribute]
        name = receipt.file.name  # ty: ignore[unresolved-attribute]
        self.assertTrue(storage.exists(name))  # ty: ignore[unresolved-attribute]
        receipt.delete()  # ty: ignore[unresolved-attribute]
        self.assertFalse(storage.exists(name))  # ty: ignore[unresolved-attribute]
