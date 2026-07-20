from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase

from api import banned_words as bw
from api.utils import get_client_ip
from api.validators import (
    ALLOWED_RECEIPT_EXTENSIONS,
    MAX_RECEIPT_SIZE,
    has_allowed_file_extension,
    has_allowed_file_header,
    has_allowed_file_size,
)


def request_with(**meta):
    """A stand-in request exposing only the .META dict that get_client_ip reads."""
    return SimpleNamespace(META=meta)


class GetClientIpTests(SimpleTestCase):
    """api.utils.get_client_ip"""

    def test_prefers_cf_connecting_ip(self):
        request = request_with(
            HTTP_CF_CONNECTING_IP="1.1.1.1",
            HTTP_X_FORWARDED_FOR="2.2.2.2",
            REMOTE_ADDR="3.3.3.3",
        )
        self.assertEqual(get_client_ip(request), "1.1.1.1")

    def test_uses_leftmost_forwarded_for_when_no_cf(self):
        request = request_with(
            HTTP_X_FORWARDED_FOR="2.2.2.2, 5.5.5.5",
            REMOTE_ADDR="3.3.3.3",
        )
        self.assertEqual(get_client_ip(request), "2.2.2.2")

    def test_falls_back_to_remote_addr(self):
        self.assertEqual(get_client_ip(request_with(REMOTE_ADDR="3.3.3.3")), "3.3.3.3")

    def test_skips_invalid_candidate_for_next_valid(self):
        request = request_with(
            HTTP_CF_CONNECTING_IP="not-an-ip",
            REMOTE_ADDR="9.9.9.9",
        )
        self.assertEqual(get_client_ip(request), "9.9.9.9")

    def test_strips_whitespace(self):
        request = request_with(HTTP_X_FORWARDED_FOR="  4.4.4.4 , 5.5.5.5")
        self.assertEqual(get_client_ip(request), "4.4.4.4")

    def test_normalizes_ipv6(self):
        self.assertEqual(
            get_client_ip(request_with(REMOTE_ADDR="2001:DB8::1")), "2001:db8::1"
        )

    def test_returns_none_for_missing_request(self):
        self.assertIsNone(get_client_ip(None))

    def test_returns_none_when_no_valid_source(self):
        self.assertIsNone(get_client_ip(request_with(REMOTE_ADDR="still-not-an-ip")))
        self.assertIsNone(get_client_ip(request_with()))


class FileValidatorTests(SimpleTestCase):
    """api.validators.has_allowed_file_size / _extension / _header"""

    def test_size_at_limit_is_allowed(self):
        self.assertTrue(has_allowed_file_size(MAX_RECEIPT_SIZE))

    def test_size_over_limit_is_rejected(self):
        self.assertFalse(has_allowed_file_size(MAX_RECEIPT_SIZE + 1))

    def test_allowed_extensions(self):
        for ext in ALLOWED_RECEIPT_EXTENSIONS:
            with self.subTest(ext=ext):
                self.assertTrue(has_allowed_file_extension(f"receipt{ext}"))
                # Extension matching is case-insensitive.
                self.assertTrue(has_allowed_file_extension(f"receipt{ext.upper()}"))

    def test_rejected_extensions(self):
        for filename in ("malware.exe", "notes.txt", "archive.zip", "noextension"):
            with self.subTest(filename=filename):
                self.assertFalse(has_allowed_file_extension(filename))

    def test_accepted_file_headers(self):
        accepted = {
            "png": b"\x89PNG\r\n\x1a\n" + b"\x00" * 8,
            "jpeg": b"\xff\xd8\xff\xe0" + b"\x00" * 8,
            "gif87": b"GIF87a" + b"\x00" * 8,
            "gif89": b"GIF89a" + b"\x00" * 8,
            "webp": b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 4,
            "pdf": b"%PDF-1.7" + b"\x00" * 4,
            "heic": b"\x00\x00\x00\x18ftypheic" + b"\x00" * 4,
        }
        for name, head in accepted.items():
            with self.subTest(format=name):
                self.assertTrue(has_allowed_file_header(head))

    def test_rejected_file_headers(self):
        rejected = {
            "html": b"<!DOCTYPE html>",
            "empty": b"",
            "exe": b"MZ\x90\x00",
            "junk": bytes(range(16)),
        }
        for name, head in rejected.items():
            with self.subTest(kind=name):
                self.assertFalse(has_allowed_file_header(head))


@mock.patch.object(bw, "BANNED_WORDS", frozenset({"badword", "evil"}))
class BannedWordTests(SimpleTestCase):
    """api.banned_words.contains_banned_word"""

    def test_detects_a_banned_word(self):
        self.assertEqual(bw.contains_banned_word("this is a badword here"), "badword")

    def test_is_case_insensitive(self):
        self.assertEqual(bw.contains_banned_word("A BADWORD shouts"), "badword")

    def test_matches_whole_words_only(self):
        """A banned word embedded in a larger token is not a match."""
        self.assertIsNone(bw.contains_banned_word("abadworda is fine"))

    def test_ignores_invisible_characters(self):
        """Zero-width characters can't be used to slip a word past screening."""
        zwsp = chr(0x200B)  # zero-width space
        self.assertEqual(bw.contains_banned_word(f"bad{zwsp}word"), "badword")

    def test_clean_text_returns_none(self):
        self.assertIsNone(bw.contains_banned_word("a perfectly nice sentence"))

    def test_empty_text_returns_none(self):
        self.assertIsNone(bw.contains_banned_word(""))

    def test_folds_lookalike_forms(self):
        """Full-width look-alikes normalize to ASCII before matching."""
        with mock.patch.object(bw, "BANNED_WORDS", frozenset({"bad"})):
            self.assertEqual(bw.contains_banned_word("ｂａｄ"), "bad")

    def test_returns_none_when_list_is_empty(self):
        with mock.patch.object(bw, "BANNED_WORDS", frozenset()):
            self.assertIsNone(bw.contains_banned_word("badword"))
