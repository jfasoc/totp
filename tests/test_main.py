"""
Unit tests for the TOTP calculator.
"""

import io
import runpy
import sys
import unittest
from unittest.mock import MagicMock, patch

import pyotp
import pyperclip

from totp_calculator.main import (
    find_totp_url,
    generate_totp,
    get_totp_from_url,
    main,
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

    @patch("sys.stdin", io.StringIO("otpauth://totp/test?secret=JBSWY3DPEHPK3PXP"))
    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("pyotp.TOTP.now")
    def test_main_success(self, mock_now: MagicMock, mock_stdout: io.StringIO) -> None:
        """Test the main function with a valid URL."""
        mock_now.return_value = "987654"
        with patch.object(sys, "argv", ["main.py"]):
            main()
            self.assertEqual(mock_stdout.getvalue().strip(), "987654")

    @patch("sys.stdin", io.StringIO("no url here"))
    @patch("sys.stderr", new_callable=io.StringIO)
    def test_main_no_url_error(self, mock_stderr: io.StringIO) -> None:
        """Test the main function when no URL is provided."""
        with patch.object(sys, "argv", ["main.py"]):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 1)
            self.assertIn("No TOTP URL found", mock_stderr.getvalue())

    @patch(
        "sys.stdin", io.StringIO("otpauth://totp/a?secret=1 otpauth://totp/b?secret=2")
    )
    @patch("sys.stderr", new_callable=io.StringIO)
    def test_main_multiple_urls_error(self, mock_stderr: io.StringIO) -> None:
        """Test the main function when multiple URLs are provided."""
        with patch.object(sys, "argv", ["main.py"]):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 1)
            self.assertIn("Multiple TOTP URLs found", mock_stderr.getvalue())

    @patch("sys.stdin", io.StringIO("otpauth://totp/test?secret=JBSWY3DPEHPK3PXP"))
    @patch("pyotp.TOTP.now")
    @patch("pyperclip.copy")
    @patch("sys.stderr", new_callable=io.StringIO)
    def test_main_copy_success(
        self, mock_stderr: io.StringIO, mock_copy: MagicMock, mock_now: MagicMock
    ) -> None:
        """Test that the copy to clipboard feature works correctly."""
        mock_now.return_value = "112233"
        with patch.object(sys, "argv", ["main.py", "--copy"]):
            main()
            mock_copy.assert_called_once_with("112233")
            self.assertIn("Copied to clipboard", mock_stderr.getvalue())

    @patch("sys.stdin", io.StringIO("otpauth://totp/test?secret=JBSWY3DPEHPK3PXP"))
    @patch("pyotp.TOTP.now")
    @patch(
        "pyperclip.copy",
        side_effect=pyperclip.PyperclipException("Clipboard not available"),
    )
    @patch("sys.stderr", new_callable=io.StringIO)
    def test_main_copy_fail(
        self, mock_stderr: io.StringIO, mock_copy: MagicMock, mock_now: MagicMock
    ) -> None:
        """Test the graceful failure of the copy to clipboard feature."""
        mock_now.return_value = "445566"
        with patch.object(sys, "argv", ["main.py", "--copy"]):
            main()
            self.assertIn(
                "Warning: Could not copy to clipboard", mock_stderr.getvalue()
            )

    @patch("sys.stdin", io.StringIO("otpauth://totp/test?secret=JBSWY3DPEHPK3PXP"))
    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("pyotp.TOTP.now")
    def test_main_entry_point(
        self, mock_now: MagicMock, mock_stdout: io.StringIO
    ) -> None:
        """Test the script's main entry point."""
        mock_now.return_value = "987654"
        with patch.object(sys, "argv", ["main.py"]):
            runpy.run_module("totp_calculator.main", run_name="__main__")
        self.assertEqual(mock_stdout.getvalue().strip(), "987654")


if __name__ == "__main__":
    unittest.main()
