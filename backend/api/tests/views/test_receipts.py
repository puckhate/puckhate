from unittest import mock

from django.urls import reverse

from api.models import Ban, DonationReceipt
from api.tests.base import ApiTestCase, make_receipt_upload
from api.throttling import ReceiptUploadThrottle
from api.validators import (
    ERROR_FILE_TOO_LARGE,
    ERROR_FILE_TYPE_INVALID,
    MAX_RECEIPT_REQUEST_SIZE,
)


class ReceiptUploadTests(ApiTestCase):
    """POST /api/receipts/"""

    url = reverse("receipts")

    def test_accepts_a_valid_upload(self):
        response = self.client.post(
            self.url, {"file": make_receipt_upload()}, format="multipart"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(DonationReceipt.objects.count(), 1)  # ty: ignore[unresolved-attribute]
        receipt = DonationReceipt.objects.get()  # ty: ignore[unresolved-attribute]
        self.assertEqual(response.data["token"], str(receipt.token))

    def test_records_the_uploader_ip(self):
        self.client.post(self.url, {"file": make_receipt_upload()}, format="multipart")
        self.assertEqual(DonationReceipt.objects.get().ip, "127.0.0.1")  # ty: ignore[unresolved-attribute]

    def test_banned_ip_is_silently_dropped(self):
        Ban.objects.create(ip="127.0.0.1", type=Ban.Type.ADMIN, reason="spam")  # ty: ignore[unresolved-attribute]
        response = self.client.post(
            self.url, {"file": make_receipt_upload()}, format="multipart"
        )
        self.assertEqual(response.status_code, 201)  # feigned success with a 201
        self.assertIn("token", response.data)
        self.assertEqual(DonationReceipt.objects.count(), 0)  # ty: ignore[unresolved-attribute]

    def test_rejects_get(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)


class ReceiptValidationTests(ApiTestCase):
    """api.validators.*"""

    url = reverse("receipts")

    def test_oversized_request_is_rejected_early(self):
        response = self.client.post(
            self.url,
            {"file": make_receipt_upload()},
            format="multipart",
            CONTENT_LENGTH=str(MAX_RECEIPT_REQUEST_SIZE + 1),
        )
        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.data, {"file": [ERROR_FILE_TOO_LARGE]})
        self.assertEqual(DonationReceipt.objects.count(), 0)  # ty: ignore[unresolved-attribute]

    def test_non_numeric_content_length_is_not_treated_as_too_large(self):
        response = self.client.post(
            self.url,
            {"file": make_receipt_upload()},
            format="multipart",
            CONTENT_LENGTH="not-a-number",
        )
        self.assertNotEqual(response.status_code, 413)

    def test_rejects_disallowed_extension(self):
        upload = make_receipt_upload(filename="receipt.txt")
        response = self.client.post(self.url, {"file": upload}, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertIn(ERROR_FILE_TYPE_INVALID, response.data["file"])
        self.assertEqual(DonationReceipt.objects.count(), 0)  # ty: ignore[unresolved-attribute]

    def test_rejects_spoofed_header(self):
        upload = make_receipt_upload(
            filename="receipt.png", content=b"<html>not an image</html>"
        )
        response = self.client.post(self.url, {"file": upload}, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertIn(ERROR_FILE_TYPE_INVALID, response.data["file"])
        self.assertEqual(DonationReceipt.objects.count(), 0)  # ty: ignore[unresolved-attribute]


class ReceiptThrottleTests(ApiTestCase):
    """api.throttling.ReceiptUploadThrottle"""

    url = reverse("receipts")

    def setUp(self):
        super().setUp()
        # Patch the rate on the throttle class to a low value
        patcher = mock.patch.dict(
            ReceiptUploadThrottle.THROTTLE_RATES, {"receipts": "1/min"}
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_second_upload_is_throttled(self):
        first = self.client.post(
            self.url, {"file": make_receipt_upload()}, format="multipart"
        )
        second = self.client.post(
            self.url, {"file": make_receipt_upload()}, format="multipart"
        )
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 429)
