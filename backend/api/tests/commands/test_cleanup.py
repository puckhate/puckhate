from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.utils import timezone

from api.models import Charity, DonationReceipt
from api.tests.base import ApiTestCase
from api.tests.factories import make_charity, make_donation, make_receipt


class CleanupOrphanCharitiesTests(ApiTestCase):
    """manage.py cleanup_orphan_charities"""

    def run_command(self, *args):
        call_command("cleanup_orphan_charities", *args, stdout=StringIO())

    def test_deletes_orphaned_charity(self):
        """Unapproved, no donations, older than 30 minutes should be deleted."""
        charity = make_charity(
            approved=False, created=timezone.now() - timedelta(minutes=31)
        )
        self.run_command()
        self.assertFalse(Charity.objects.filter(pk=charity.pk).exists())  # ty: ignore[unresolved-attribute]

    def test_dry_run_deletes_nothing(self):
        """--dry-run reports orphans but leaves them in place."""
        charity = make_charity(
            approved=False, created=timezone.now() - timedelta(minutes=31)
        )
        self.run_command("--dry-run")
        self.assertTrue(Charity.objects.filter(pk=charity.pk).exists())  # ty: ignore[unresolved-attribute]

    def test_keeps_approved_orphan_charity(self):
        """An approved charity is never reaped, even with no donations."""
        charity = make_charity(
            approved=True, created=timezone.now() - timedelta(minutes=31)
        )
        self.run_command()
        self.assertTrue(Charity.objects.filter(pk=charity.pk).exists())  # ty: ignore[unresolved-attribute]

    def test_keeps_charity_with_donations(self):
        """A charity that has a donation attributed to it is not an orphan."""
        charity = make_charity(
            approved=False, created=timezone.now() - timedelta(minutes=31)
        )
        make_donation(charity=charity)
        self.run_command()
        self.assertTrue(Charity.objects.filter(pk=charity.pk).exists())  # ty: ignore[unresolved-attribute]


class CleanupOrphanReceiptsTests(ApiTestCase):
    """manage.py cleanup_orphan_receipts"""

    def run_command(self, *args):
        call_command("cleanup_orphan_receipts", *args, stdout=StringIO())

    def test_deletes_old_orphan_receipt(self):
        """Unclaimed and older than 30 minutes -> reaped."""
        receipt = make_receipt(created=timezone.now() - timedelta(minutes=31))
        self.run_command()
        self.assertFalse(DonationReceipt.objects.filter(pk=receipt.pk).exists())  # ty: ignore[unresolved-attribute]

    def test_dry_run_deletes_nothing(self):
        """--dry-run reports what it would reap but deletes nothing."""
        receipt = make_receipt(created=timezone.now() - timedelta(minutes=31))
        self.run_command("--dry-run")
        self.assertTrue(DonationReceipt.objects.filter(pk=receipt.pk).exists())  # ty: ignore[unresolved-attribute]

    def test_keeps_young_receipt(self):
        """A freshly uploaded, still-unclaimed receipt is left alone."""
        receipt = make_receipt()
        self.run_command()
        self.assertTrue(DonationReceipt.objects.filter(pk=receipt.pk).exists())  # ty: ignore[unresolved-attribute]
