# Project Standards

This document outlines the standards and requirements for contributing to this project. All contributions must adhere to these guidelines.

## Python

- The project uses Python >= 3.10.
- Dependencies are managed with PDM.

## Testing and Quality

- **No Warnings**: Warnings in tests and checks are not allowed and will be treated as errors.
- **100% Test Coverage**: All code must be covered by tests. It is not allowed to exclude any code from test coverage. Use `pdm run pytest` to run the tests and check coverage.
- **Code Formatting**: Code is formatted with `black`. Run `pdm run black .` to format the code.
- **Style Checking**: Code style is checked with `flake8`. Run `pdm run flake8 .` to check the style.
- **Type Checking**: Code is type-checked with `mypy`. Run `pdm run mypy .` to check the types.
- **UTF-8 Source Encoding**: All source files must be UTF-8 encoded.
- **End-of-File Newline**: All files must end with a newline.
- **88-Character Line Limit**: The maximum line length is 88 characters.
- **Docstrings**: All modules, classes, and functions must have docstrings.
- **Comments**: Comments should explain *why* decisions were made, not *what* the code does.

## Commits

Before committing any changes, you must ensure that all tests pass and that the code adheres to the formatting and style guidelines. You can run all checks with the following commands:

```bash
pdm run pytest
pdm run black --check .
pdm run flake8 .
pdm run mypy .
```

If any of these checks fail, the commit will be rejected by the CI/CD pipeline.
