from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from api.models import SiteStats
from api.tests.base import ApiTestCase, ExchangeRateAPIMixin
from libraries.currencylayer.exceptions import CurrencyLayerAPIException


@override_settings(CURRENCYLAYER_API_KEY="test-key")
class UpdateExchangeRateCommandTests(ExchangeRateAPIMixin, ApiTestCase):
    """manage.py update_exchange_rate"""

    def run_command(self, *args):
        call_command("update_exchange_rate", *args, stdout=StringIO())

    def current_rate(self) -> Decimal:
        return SiteStats.load().ca_exchange_rate

    def set_rate(self, value: Decimal):
        stats = SiteStats.load()
        stats.ca_exchange_rate = value
        stats.save(update_fields=["ca_exchange_rate"])

    def test_updates_rate_on_success(self):
        self.mock_get_rate.return_value = {"CAD": 1.36}
        self.run_command()
        self.assertEqual(self.current_rate(), Decimal("1.3600"))

    def test_quantizes_rate_to_four_places(self):
        """A longer decimal is rounded to four places before storage."""
        self.mock_get_rate.return_value = {"CAD": 1.365551}
        self.run_command()
        self.assertEqual(self.current_rate(), Decimal("1.3656"))

    def test_dry_run_does_not_save(self):
        self.set_rate(Decimal("1.5000"))
        self.mock_get_rate.return_value = {"CAD": 1.36}
        self.run_command("--dry-run")
        self.assertEqual(self.current_rate(), Decimal("1.5000"))

    def test_api_exception_leaves_rate_unchanged(self):
        """A transport / non-2xx error surfaces as CommandError, rate intact."""
        self.set_rate(Decimal("1.5000"))
        self.mock_get_rate.side_effect = CurrencyLayerAPIException("boom")
        with self.assertRaises(CommandError):
            self.run_command()
        self.assertEqual(self.current_rate(), Decimal("1.5000"))

    def test_missing_target_currency_raises(self):
        """A response with no CAD rate is rejected."""
        self.set_rate(Decimal("1.5000"))
        self.mock_get_rate.return_value = {"USD": 1.0}
        with self.assertRaises(CommandError):
            self.run_command()
        self.assertEqual(self.current_rate(), Decimal("1.5000"))

    def test_unparseable_rate_raises(self):
        """A non-numeric CAD value is rejected."""
        self.set_rate(Decimal("1.5000"))
        self.mock_get_rate.return_value = {"CAD": "not-a-number"}
        with self.assertRaises(CommandError):
            self.run_command()
        self.assertEqual(self.current_rate(), Decimal("1.5000"))

    def test_non_positive_rate_raises(self):
        """A zero or negative rate is rejected."""
        self.set_rate(Decimal("1.5000"))
        self.mock_get_rate.return_value = {"CAD": 0}
        with self.assertRaises(CommandError):
            self.run_command()
        self.assertEqual(self.current_rate(), Decimal("1.5000"))

    @override_settings(CURRENCYLAYER_API_KEY="")
    def test_missing_api_key_raises(self):
        """With no API key the command fails before touching the client."""
        with self.assertRaises(CommandError):
            self.run_command()
        self.mock_currencylayer.assert_not_called()
