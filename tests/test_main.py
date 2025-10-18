"""Unit tests for the TOTP calculator."""

import unittest
from unittest.mock import patch

import pyotp

from totp_calculator.main import (
    find_totp_url,
    generate_totp,
    get_totp_from_url,
)


class TestTotpCalculator(unittest.TestCase):
    """Test suite for the TOTP calculator."""

    def test_generate_totp(self) -> None:
        """Test that TOTP codes are generated correctly."""
        secret = "JBSWY3DPEHPK3PXP"
        totp = pyotp.TOTP(secret)
        with patch.object(totp, "now") as mock_now:
            mock_now.return_value = "123456"
            self.assertEqual(generate_totp(totp), "123456")

    def test_find_totp_url_single(self) -> None:
        """Test that a single TOTP URL is found correctly."""
        text = "Here is a TOTP URL: otpauth://totp/test?secret=JBSWY3DPEHPK3PXP"
        self.assertEqual(
            find_totp_url(text), "otpauth://totp/test?secret=JBSWY3DPEHPK3PXP"
        )

    def test_find_totp_url_multiple(self) -> None:
        """Test that an error is raised when multiple URLs are found."""
        text = "URL 1: otpauth://totp/a?secret=1\nURL 2: otpauth://totp/b?secret=2"
        with self.assertRaisesRegex(ValueError, "Multiple TOTP URLs found"):
            find_totp_url(text)

    def test_find_totp_url_none(self) -> None:
        """Test that an error is raised when no URL is found."""
        text = "There is no URL here."
        with self.assertRaisesRegex(ValueError, "No TOTP URL found"):
            find_totp_url(text)

    def test_get_totp_from_url_valid(self) -> None:
        """Test that a valid URL is parsed correctly."""
        url = "otpauth://totp/test?secret=JBSWY3DPEHPK3PXP"
        totp = get_totp_from_url(url)
        self.assertIsInstance(totp, pyotp.TOTP)
        self.assertEqual(totp.secret, "JBSWY3DPEHPK3PXP")

    def test_get_totp_from_url_all_params(self) -> None:
        """Test that a URL with all parameters is parsed correctly."""
        url = (
            "otpauth://totp/Test:user@example.com?secret=JBSWY3DPEHPK3PXP"
            "&issuer=Test&algorithm=SHA256&digits=8&period=60"
        )
        totp = get_totp_from_url(url)
        self.assertIsInstance(totp, pyotp.TOTP)
        self.assertEqual(totp.name, "user@example.com")
        self.assertEqual(totp.issuer, "Test")
        self.assertEqual(totp.secret, "JBSWY3DPEHPK3PXP")
        self.assertEqual(totp.digits, 8)
        self.assertEqual(totp.interval, 60)
        self.assertEqual(totp.digest().name, "sha256")

    def test_get_totp_from_url_hotp(self) -> None:
        """Test that an error is raised for HOTP URLs."""
        url = "otpauth://hotp/test?secret=JBSWY3DPEHPK3PXP"
        with self.assertRaisesRegex(ValueError, "Only TOTP is supported"):
            get_totp_from_url(url)

    def test_get_totp_from_url_malformed(self) -> None:
        """Test that an error is raised for a malformed URL."""
        url = "http://example.com"
        with self.assertRaisesRegex(ValueError, "Failed to parse TOTP URL"):
            get_totp_from_url(url)


if __name__ == "__main__":
    unittest.main()
