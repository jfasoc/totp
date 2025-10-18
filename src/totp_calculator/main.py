"""Provides a command-line tool to calculate TOTP codes from URLs."""

import argparse
import re
import sys

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


def generate_totp(totp: pyotp.TOTP) -> str:
    """Generate a Time-Based One-Time Password (TOTP).

    Args:
        totp: The TOTP object.

    Returns:
        The current TOTP code as a string.
    """
    return totp.now()


def find_totp_url(text: str) -> str:
    """Find a TOTP URL in the given text.

    Args:
        text: The text to search for a TOTP URL.

    Returns:
        The TOTP URL if found.

    Raises:
        ValueError: If no TOTP URL is found or multiple URLs are found.
    """
    urls: list[str] = re.findall(r"otpauth://[^\s]+", text)
    if len(urls) == 0:
        raise ValueError("No TOTP URL found in the input.")
    if len(urls) > 1:
        raise ValueError("Multiple TOTP URLs found in the input.")
    return urls[0]


def get_totp_from_url(url: str) -> pyotp.TOTP:
    """Parse a TOTP URL and return a TOTP object.

    Args:
        url: The TOTP URL.

    Returns:
        A TOTP object.

    Raises:
        ValueError: If the URL is malformed.
    """
    try:
        # We need to cast the result of parse_uri to TOTP, because it's defined as
        # -> Union[TOTP, HOTP] and this application only supports TOTP.
        totp = pyotp.parse_uri(url)
        if not isinstance(totp, pyotp.TOTP):
            raise TypeError("Only TOTP is supported.")
        return totp
    except Exception as e:
        raise ValueError(f"Failed to parse TOTP URL: {e}") from e


def read_stdin() -> str:
    """Read the entire content from stdin."""
    return sys.stdin.read()


def main() -> None:
    """Run the main entry point of the application."""
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
        totp_obj = get_totp_from_url(totp_url)
        totp_code = generate_totp(totp_obj)

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
