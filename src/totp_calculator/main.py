"""
This module provides a command-line tool to calculate TOTP codes from URLs.
"""

import argparse
import re
import sys
from urllib.parse import parse_qs, urlparse

import pyotp
import pyperclip


LICENSE_NOTICE = """
MIT License

Copyright (c) 2025 jfasoc <7720125+jfasoc@users.noreply.github.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def generate_totp(secret: str) -> str:
    """
    Generates a Time-Based One-Time Password (TOTP) from a given secret.

    Args:
        secret: The base32 encoded secret key.

    Returns:
        The current TOTP code as a string.
    """
    totp = pyotp.TOTP(secret)
    return totp.now()


def find_totp_url(text: str) -> str:
    """
    Finds a TOTP URL in the given text.

    Args:
        text: The text to search for a TOTP URL.

    Returns:
        The TOTP URL if found.

    Raises:
        ValueError: If no TOTP URL is found or multiple URLs are found.
    """
    urls = re.findall(r"otpauth://[^\s]+", text)
    if len(urls) == 0:
        raise ValueError("No TOTP URL found in the input.")
    if len(urls) > 1:
        raise ValueError("Multiple TOTP URLs found in the input.")
    return urls[0]


def get_secret_from_url(url: str) -> str:
    """
    Extracts the secret from a TOTP URL.

    Args:
        url: The TOTP URL.

    Returns:
        The secret key.

    Raises:
        ValueError: If the URL is malformed or the secret is missing.
    """
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if "secret" not in query_params:
            raise ValueError("The TOTP URL is missing the 'secret' parameter.")
        return query_params["secret"][0]
    except Exception as e:
        raise ValueError(f"Failed to parse TOTP URL: {e}")


def read_stdin() -> str:
    """Reads the entire content from stdin."""
    return sys.stdin.read()


def main() -> None:
    """The main entry point of the application."""
    parser = argparse.ArgumentParser(
        description=(
            "Scans for a TOTP URL from stdin, "
            "computes the current TOTP code, and prints it."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=f"License Information:\n{LICENSE_NOTICE}",
    )
    parser.add_argument(
        "-c", "--copy", action="store_true", help="Copy the TOTP code to the clipboard."
    )
    args = parser.parse_args()

    try:
        stdin_content = read_stdin()
        totp_url = find_totp_url(stdin_content)
        secret = get_secret_from_url(totp_url)
        totp_code = generate_totp(secret)

        print(totp_code)

        if args.copy:
            try:
                pyperclip.copy(totp_code)
                print("Copied to clipboard.", file=sys.stderr)
            except pyperclip.PyperclipException as e:
                print(f"Warning: Could not copy to clipboard. {e}", file=sys.stderr)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
