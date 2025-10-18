"""
Unit tests for the TOTP calculator.
"""

import io
import sys
import unittest
from unittest.mock import MagicMock, patch

import pyperclip

from totp_calculator.main import (
    find_totp_url,
    generate_totp,
    get_secret_from_url,
    main,
)


class TestTotpCalculator(unittest.TestCase):
    """Test suite for the TOTP calculator."""

    def test_generate_totp(self) -> None:
        """Test that TOTP codes are generated correctly."""
        secret = "JBSWY3DPEHPK3PXP"
        with patch("pyotp.TOTP.now") as mock_now:
            mock_now.return_value = "123456"
            self.assertEqual(generate_totp(secret), "123456")

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

    def test_get_secret_from_url_valid(self) -> None:
        """Test that the secret is extracted correctly from a valid URL."""
        url = "otpauth://totp/test?secret=JBSWY3DPEHPK3PXP"
        self.assertEqual(get_secret_from_url(url), "JBSWY3DPEHPK3PXP")

    def test_get_secret_from_url_no_secret(self) -> None:
        """Test that an error is raised when the secret is missing."""
        url = "otpauth://totp/test?issuer=Google"
        with self.assertRaisesRegex(ValueError, "missing the 'secret' parameter"):
            get_secret_from_url(url)

    def test_get_secret_from_url_malformed(self) -> None:
        """Test that an error is raised for a malformed URL."""
        url = "http://example.com"
        with self.assertRaisesRegex(ValueError, "Failed to parse TOTP URL"):
            get_secret_from_url(url)

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


if __name__ == "__main__":
    unittest.main()
