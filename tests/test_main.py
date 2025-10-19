"""Unit tests for the TOTP calculator."""

from unittest.mock import patch

import pyotp
import pytest

from totp_calculator.main import find_totp_url, generate_totp, get_totp_from_url


@pytest.fixture
def secret() -> str:
    """Fixture to generate a random secret for testing."""
    return pyotp.random_base32()


def test_generate_totp(secret: str) -> None:
    """Test that TOTP codes are generated correctly."""
    totp = pyotp.TOTP(secret)
    with patch.object(totp, "now") as mock_now:
        mock_now.return_value = "123456"
        assert generate_totp(totp) == "123456"


def test_find_totp_url_single(secret: str) -> None:
    """Test that a single TOTP URL is found correctly."""
    text = f"Here is a TOTP URL: otpauth://totp/test?secret={secret}"
    assert find_totp_url(text) == f"otpauth://totp/test?secret={secret}"


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


def test_get_totp_from_url_valid(secret: str) -> None:
    """Test that a valid URL is parsed correctly."""
    url = f"otpauth://totp/test?secret={secret}"
    totp = get_totp_from_url(url)
    assert isinstance(totp, pyotp.TOTP)
    assert totp.secret == secret


def test_get_totp_from_url_all_params(secret: str) -> None:
    """Test that a URL with all parameters is parsed correctly."""
    url = (
        f"otpauth://totp/Test:user@example.com?secret={secret}"
        "&issuer=Test&algorithm=SHA256&digits=8&period=60"
    )
    totp = get_totp_from_url(url)
    assert isinstance(totp, pyotp.TOTP)
    assert (
        totp.name,
        totp.issuer,
        totp.secret,
        totp.digits,
        totp.interval,
        totp.digest().name,
    ) == ("user@example.com", "Test", secret, 8, 60, "sha256")


def test_get_totp_from_url_hotp(secret: str) -> None:
    """Test that an error is raised for HOTP URLs."""
    url = f"otpauth://hotp/test?secret={secret}"
    with pytest.raises(ValueError, match="Only TOTP is supported"):
        get_totp_from_url(url)


def test_get_totp_from_url_malformed() -> None:
    """Test that an error is raised for a malformed URL."""
    url = "http://example.com"
    with pytest.raises(ValueError, match="Failed to parse TOTP URL"):
        get_totp_from_url(url)
