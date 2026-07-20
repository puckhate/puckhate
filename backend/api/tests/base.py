import logging
import shutil
import tempfile
import warnings
from copy import deepcopy
from unittest import mock

from rest_framework.test import APITestCase

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from api.models import Charity, DonationReceipt

# WhiteNoise warns once per run that STATIC_ROOT is missing
# It's irrelevant to the API and clutters output.
warnings.filterwarnings("ignore", message="No directory at", category=UserWarning)

# An 8-byte PNG signature that will satisfy the magic-byte check
# in api.validators.has_allowed_file_header without needing a real image.
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
VALID_PNG_BYTES = PNG_SIGNATURE + b"\x00" * 24


def make_receipt_upload(
    filename: str = "receipt.png",
    content: bytes | None = None,
    content_type: str = "image/png",
) -> SimpleUploadedFile:
    """Build a fake, in-memory receipt upload"""
    return SimpleUploadedFile(
        filename,
        VALID_PNG_BYTES if content is None else content,
        content_type=content_type,
    )


class ApiTestCase(APITestCase):
    """Shared test harness for api tests.

    Neutralizes four pieces of runtime infrastructure:

      * throttling  – the DRF write throttles are disabled
      * caching     – cache_page and throttle run against a per-test
                      locmem cache that is cleared before and after every test
      * email       – routed to the locmem backend so mail.outbox is assertable
      * storage     – MEDIA_ROOT and PRIVATE_MEDIA_ROOT all point at throwaway temp dirs
    """

    def setUp(self):
        super().setUp()

        # Throwaway media roots
        self._media_root = tempfile.mkdtemp(prefix="puckhate-media-")
        self._private_root = tempfile.mkdtemp(prefix="puckhate-private-")
        self.addCleanup(shutil.rmtree, self._media_root, ignore_errors=True)
        self.addCleanup(shutil.rmtree, self._private_root, ignore_errors=True)

        # Disable the write throttles while preserving the rest of the DRF config
        rest_framework = deepcopy(settings.REST_FRAMEWORK)
        rest_framework["DEFAULT_THROTTLE_RATES"] = {
            scope: None for scope in rest_framework.get("DEFAULT_THROTTLE_RATES", {})
        }

        # Redirect the private receipt storage to throwaway media storage
        storages = deepcopy(settings.STORAGES)
        storages["private"]["OPTIONS"]["location"] = self._private_root

        overrides = override_settings(
            CACHES={
                "default": {
                    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                }
            },
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
            PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
            MEDIA_ROOT=self._media_root,
            PRIVATE_MEDIA_ROOT=self._private_root,
            STORAGES=storages,
            REST_FRAMEWORK=rest_framework,
        )
        overrides.enable()
        self.addCleanup(overrides.disable)

        # Point DonationReceipt's file field's storage at the temp dir
        receipt_storage = FileSystemStorage(
            location=self._private_root,
            base_url=settings.PRIVATE_MEDIA_URL,
        )
        field_patcher = mock.patch.object(
            DonationReceipt._meta.get_field("file"),  # ty: ignore[unresolved-attribute]
            "storage",
            receipt_storage,
        )
        field_patcher.start()
        self.addCleanup(field_patcher.stop)

        # Django logs a WARNING for every 4xx response. Mute these expected warnings.
        request_logger = logging.getLogger("django.request")
        previous_level = request_logger.level
        request_logger.setLevel(logging.ERROR)
        self.addCleanup(request_logger.setLevel, previous_level)

        # Approved charities are seeed by migration. Empty the table to avoid polluting tests.
        Charity.objects.all().delete()  # ty: ignore[unresolved-attribute]

        cache.clear()
        self.addCleanup(cache.clear)

    def as_staff(self, *, superuser: bool = True, **kwargs):
        """Create a staff user, log them in via the session, and return them."""
        User = get_user_model()
        defaults = {
            "username": "staff",
            "email": "staff@example.com",
            "is_staff": True,
            "is_superuser": superuser,
        }
        defaults.update(kwargs)
        user = User.objects.create_user(password="pw", **defaults)
        self.client.force_login(user)
        return user


class ExchangeRateAPIMixin:
    """Patch the CurrencyLayer client used by `update_exchange_rate`.

    Exposes `self.mock_get_rate`. By default it returns a valid CAD rate.
    Override `self.mock_get_rate.return_value` / `.side_effect` per test.
    """

    default_rate = {"CAD": 1.3600}

    def setUp(self):
        super().setUp()  # ty: ignore[unresolved-attribute]
        patcher = mock.patch(
            "api.management.commands.update_exchange_rate.CurrencyLayerAPIClient"
        )
        self.mock_currencylayer = patcher.start()
        self.addCleanup(patcher.stop)  # ty: ignore[unresolved-attribute]
        self.mock_get_rate = self.mock_currencylayer.return_value.get_rate
        self.mock_get_rate.return_value = dict(self.default_rate)


class HockeyTechAPIMixin:
    """Patch the HockeyTech client used by `update_goals_scored`.

    Exposes `self.mock_get_player_stats`. Override its return value per test.
    """

    def setUp(self):
        super().setUp()  # ty: ignore[unresolved-attribute]
        patcher = mock.patch(
            "api.management.commands.update_goals_scored.HockeyTechAPIClient"
        )
        self.mock_hockeytech = patcher.start()
        self.addCleanup(patcher.stop)  # ty: ignore[unresolved-attribute]
        self.mock_get_player_stats = self.mock_hockeytech.return_value.get_player_stats
        self.mock_get_player_stats.return_value = {}
