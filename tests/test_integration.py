"""Integration tests for the TOTP calculator."""

import io
import runpy
import sys
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pyperclip
import pytest
from freezegun import freeze_time

from totp_calculator.main import main

STDIN_PATH = "sys.stdin"
STDOUT_PATH = "sys.stdout"
STDERR_PATH = "sys.stderr"
PYOTP_NOW_PATH = "pyotp.TOTP.now"
PYPERCLIP_COPY_PATH = "pyperclip.copy"
SYS_ARGV_PATH = "argv"
MAIN_PY_PATH = "main.py"
VALID_TOTP_URL = "otpauth://totp/test?secret=JBSWY3DPEHPK3PXP"
MOCK_TOTP_CODE = "987654"


@patch(STDIN_PATH, io.StringIO(VALID_TOTP_URL))
@patch(STDOUT_PATH, new_callable=io.StringIO)
@patch(PYOTP_NOW_PATH)
def test_main_success(mock_now: MagicMock, mock_stdout: io.StringIO) -> None:
    """Test the main function with a valid URL."""
    mock_now.return_value = MOCK_TOTP_CODE
    with patch.object(sys, SYS_ARGV_PATH, [MAIN_PY_PATH]):
        main()
        assert mock_stdout.getvalue().strip() == MOCK_TOTP_CODE


@patch(STDIN_PATH, io.StringIO("no url here"))
@patch(STDERR_PATH, new_callable=io.StringIO)
def test_main_no_url_error(mock_stderr: io.StringIO) -> None:
    """Test the main function when no URL is provided."""
    with patch.object(sys, SYS_ARGV_PATH, [MAIN_PY_PATH]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1
        assert "No TOTP URL found" in mock_stderr.getvalue()


@patch(STDIN_PATH, io.StringIO("otpauth://totp/a?secret=1 otpauth://totp/b?secret=2"))
@patch(STDERR_PATH, new_callable=io.StringIO)
def test_main_multiple_urls_error(mock_stderr: io.StringIO) -> None:
    """Test the main function when multiple URLs are provided."""
    with patch.object(sys, SYS_ARGV_PATH, [MAIN_PY_PATH]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1
        assert "Multiple TOTP URLs found" in mock_stderr.getvalue()


@patch(STDIN_PATH, io.StringIO(VALID_TOTP_URL))
@patch(PYOTP_NOW_PATH)
@patch(PYPERCLIP_COPY_PATH)
@patch(STDERR_PATH, new_callable=io.StringIO)
def test_main_copy_success(
    mock_stderr: io.StringIO, mock_copy: MagicMock, mock_now: MagicMock
) -> None:
    """Test that the copy to clipboard feature works correctly."""
    mock_now.return_value = "112233"
    with patch.object(sys, SYS_ARGV_PATH, [MAIN_PY_PATH, "--copy"]):
        main()
        mock_copy.assert_called_once_with("112233")
        assert "Copied to clipboard" in mock_stderr.getvalue()


@patch(STDIN_PATH, io.StringIO(VALID_TOTP_URL))
@patch(PYOTP_NOW_PATH)
@patch(
    PYPERCLIP_COPY_PATH,
    side_effect=pyperclip.PyperclipException("Clipboard not available"),
)
@patch(STDERR_PATH, new_callable=io.StringIO)
def test_main_copy_fail(
    mock_stderr: io.StringIO, mock_copy: MagicMock, mock_now: MagicMock
) -> None:
    """Test the graceful failure of the copy to clipboard feature."""
    mock_now.return_value = "445566"
    with patch.object(sys, SYS_ARGV_PATH, [MAIN_PY_PATH, "--copy"]):
        main()
        assert "Warning: Could not copy to clipboard" in mock_stderr.getvalue()


@patch(STDIN_PATH, io.StringIO(VALID_TOTP_URL))
@patch(STDOUT_PATH, new_callable=io.StringIO)
@patch(PYOTP_NOW_PATH)
def test_main_entry_point(mock_now: MagicMock, mock_stdout: io.StringIO) -> None:
    """Test the script's main entry point."""
    mock_now.return_value = MOCK_TOTP_CODE
    with patch.object(sys, SYS_ARGV_PATH, [MAIN_PY_PATH]):
        with pytest.warns(
            RuntimeWarning,
            match=r"'totp_calculator\.main' found in sys\.modules",
        ):
            runpy.run_module("totp_calculator.main", run_name="__main__")
    assert mock_stdout.getvalue().strip() == MOCK_TOTP_CODE


TEST_YEAR = 2023
TEST_MONTH = 1
TEST_DAY = 1
TEST_HOUR = 1
TEST_MINUTE = 1
TEST_SECOND = 1
TEST_DATETIME = datetime(
    TEST_YEAR,
    TEST_MONTH,
    TEST_DAY,
    TEST_HOUR,
    TEST_MINUTE,
    TEST_SECOND,
    tzinfo=timezone.utc,
)


@freeze_time(TEST_DATETIME)
@patch("sys.stdout", new_callable=io.StringIO)
def test_main_with_all_non_default_params(mock_stdout: io.StringIO) -> None:
    """Test main with a TOTP URL that has all non-default parameters."""
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
            assert mock_stdout.getvalue().strip() == expected_totp
