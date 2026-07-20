from io import StringIO

from django.core.management import call_command
from django.test import override_settings

from api.models import Charity, Donation
from api.tests.base import ApiTestCase


@override_settings(SITE_URL="http://localhost")
class SeedTestDataCommandTests(ApiTestCase):
    """manage.py seed_test_data"""

    def run_command(self, **kwargs):
        call_command("seed_test_data", stdout=StringIO(), **kwargs)

    def test_seeds_requested_counts(self):
        """Smoke test: the seeder creates the requested rows without erroring.

        Guards against model drift silently breaking the dev seeder.
        """
        charities_before = Charity.objects.count()  # ty: ignore[unresolved-attribute]
        self.run_command(charities=3, donations=5)
        self.assertEqual(Charity.objects.count(), charities_before + 3)  # ty: ignore[unresolved-attribute]
        self.assertEqual(Donation.objects.count(), 5)  # ty: ignore[unresolved-attribute]
        # Seeded donations are verified.
        self.assertEqual(Donation.objects.filter(verified__isnull=False).count(), 5)  # ty: ignore[unresolved-attribute]

    @override_settings(SITE_URL="https://puckhate.com")
    def test_does_nothing_in_production(self):
        """The production guard prevents seeding fake data on the live site."""
        charities_before = Charity.objects.count()  # ty: ignore[unresolved-attribute]
        self.run_command(charities=3, donations=5)
        self.assertEqual(Charity.objects.count(), charities_before)  # ty: ignore[unresolved-attribute]
        self.assertEqual(Donation.objects.count(), 0)  # ty: ignore[unresolved-attribute]
