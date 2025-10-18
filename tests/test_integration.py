"""
Integration tests for the TOTP calculator.
"""

import io
import runpy
import sys
import unittest
from datetime import datetime, timezone

import pytest
from unittest.mock import MagicMock, patch

import pyperclip
from freezegun import freeze_time

from totp_calculator.main import main


class TestTotpCalculatorIntegration(unittest.TestCase):
    """Test suite for the TOTP calculator."""

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
            with pytest.warns(
                RuntimeWarning,
                match=r"'totp_calculator\.main' found in sys\.modules",
            ):
                runpy.run_module("totp_calculator.main", run_name="__main__")
        self.assertEqual(mock_stdout.getvalue().strip(), "987654")

    @freeze_time(datetime(2023, 1, 1, 1, 1, 1, tzinfo=timezone.utc))
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_with_all_non_default_params(self, mock_stdout: io.StringIO) -> None:
        """
        Test the main function with a TOTP URL that has all non-default parameters.
        """
        url = (
            "otpauth://totp/Test:user@example.com?secret=JBSWY3DPEHPK3PXP"
            "&issuer=Test&algorithm=SHA512&digits=7&period=45"
        )
        # This is the expected TOTP code for the given time and parameters.
        # It was generated using the following command:
        # oathtool --totp=SHA512 --base32 --digits=7 --time-step-size=45s \
        # "JBSWY3DPEHPK3PXP" --now "2023-01-01 01:01:01 UTC"
        expected_totp = "1989734"
        stdin_content = f"Some text before the URL\n{url}\nSome text after the URL"

        with patch("sys.stdin", io.StringIO(stdin_content)):
            with patch.object(sys, "argv", ["main.py"]):
                main()
                self.assertEqual(mock_stdout.getvalue().strip(), expected_totp)


if __name__ == "__main__":
    unittest.main()
