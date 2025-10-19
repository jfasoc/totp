# TOTP Calculator

A command-line tool to calculate TOTP codes from URLs.

## Installation

You can install the tool using `pip`:

```bash
pip install totp-calculator
```

## Usage

Pipe a TOTP URL to the `totp-calculator` command:

```bash
echo "otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&issuer=Example" | totp-calculator
```

### Copy to Clipboard

To copy the TOTP code to the clipboard, use the `--copy` or `-c` flag:

```bash
echo "otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&issuer=Example" | totp-calculator --copy
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
