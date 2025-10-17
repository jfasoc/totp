"""Tests for the app module."""

from app import hello_world


def test_hello_world() -> None:
    """Tests the hello_world function.

    This test verifies that the hello_world function returns the expected
    greeting. It is used to ensure that the testing pipeline is working
    correctly.
    """
    assert hello_world() == "Hello, world!"
