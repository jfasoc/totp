"""Unit tests for the TOTP calculator."""

from unittest.mock import patch

import pyotp
import pytest

import io
import pyperclip
from totp_calculator.main import (_print_stderr, _print_stdout, find_totp_url,
                                  generate_totp, get_totp_from_url, main)


def test_generate_totp() -> None:
    """Test that TOTP codes are generated correctly."""
    secret = "JBSWY3DPEHPK3PXP"
    totp = pyotp.TOTP(secret)
    with patch.object(totp, "now") as mock_now:
        mock_now.return_value = "123456"
        assert generate_totp(totp) == "123456"


def test_find_totp_url_single() -> None:
    """Test that a single TOTP URL is found correctly."""
    text = "Here is a TOTP URL: otpauth://totp/test?secret=JBSWY3DPEHPK3PXP"
    assert find_totp_url(text) == "otpauth://totp/test?secret=JBSWY3DPEHPK3PXP"


def test_find_totp_url_multiple() -> None:
    """Test that an error is raised when multiple URLs are found."""
    text = "URL 1: otpauth://totp/a?secret=1\nURL 2: otpauth://totp/b?secret=2"
    with pytest.raises(ValueError, match="Multiple TOTP URLs found"):
        find_totp_url(text)


def test_find_totp_url_none() -> None:
    """Test that an error is raised when no URL is found."""
    text = "There is no URL here."
    with pytest.raises(ValueError, match="No TOTP URL found"):
        find_totp_url(text)


def test_get_totp_from_url_valid() -> None:
    """Test that a valid URL is parsed correctly."""
    url = "otpauth://totp/test?secret=JBSWY3DPEHPK3PXP"
    totp = get_totp_from_url(url)
    assert isinstance(totp, pyotp.TOTP)
    assert totp.secret == "JBSWY3DPEHPK3PXP"


def test_get_totp_from_url_all_params() -> None:
    """Test that a URL with all parameters is parsed correctly."""
    url = (
        "otpauth://totp/Test:user@example.com?secret=JBSWY3DPEHPK3PXP"
        "&issuer=Test&algorithm=SHA256&digits=8&period=60"
    )
    totp = get_totp_from_url(url)
    assert isinstance(totp, pyotp.TOTP)
    assert totp.name == "user@example.com"
    assert totp.issuer == "Test"
    assert totp.secret == "JBSWY3DPEHPK3PXP"
    assert totp.digits == 8
    assert totp.interval == 60
    assert totp.digest().name == "sha256"


def test_get_totp_from_url_hotp() -> None:
    """Test that an error is raised for HOTP URLs."""
    url = "otpauth://hotp/test?secret=JBSWY3DPEHPK3PXP"
    with pytest.raises(ValueError, match="Only TOTP is supported"):
        get_totp_from_url(url)


def test_get_totp_from_url_malformed() -> None:
    """Test that an error is raised for a malformed URL."""
    url = "http://example.com"
    with pytest.raises(ValueError, match="Failed to parse TOTP URL"):
        get_totp_from_url(url)


def test_print_stdout(capsys):
    """Test that _print_stdout prints to stdout."""
    _print_stdout("test message")
    captured = capsys.readouterr()
    assert captured.out == "test message\n"


def test_print_stderr(capsys):
    """Test that _print_stderr prints to stderr."""
    _print_stderr("test message")
    captured = capsys.readouterr()
    assert captured.err == "test message\n"


def test_main_find_url_fail(capsys):
    """Test that main handles find_totp_url exceptions."""
    with patch("sys.stdin", io.StringIO("no url here")):
        with pytest.raises(SystemExit) as cm:
            main()
        assert cm.value.code == 1
    captured = capsys.readouterr()
    assert "Error: No TOTP URL found in the input." in captured.err


def test_main_get_totp_from_url_fail(capsys):
    """Test that main handles get_totp_from_url exceptions."""
    with patch("sys.stdin", io.StringIO("otpauth://hotp/test?secret=JBSWY3DPEHPK3PXP")):
        with pytest.raises(SystemExit) as cm:
            main()
        assert cm.value.code == 1
    captured = capsys.readouterr()
    assert "Error: Only TOTP is supported." in captured.err


def test_main_no_copy(capsys):
    """Test that the copy to clipboard feature is not triggered without the --copy flag."""
    with patch("sys.stdin", io.StringIO("otpauth://totp/test?secret=JBSWY3DPEHPK3PXP")):
        with patch("pyperclip.copy") as mock_copy:
            main()
            mock_copy.assert_not_called()
