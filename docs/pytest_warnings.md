# Pytest Warning Configuration

This document explains the rationale behind the specific warning configurations in the `pyproject.toml` file.

## Handled `RuntimeWarning`

In our `pytest` configuration, we have a general policy to treat all warnings as errors (`filterwarnings = "error"`). However, we have a specific case where a `RuntimeWarning` is expected and handled.

```
RuntimeWarning: 'totp_calculator.main' found in sys.modules after import of package 'totp_calculator', but prior to execution of 'totp_calculator.main'; this may result in unpredictable behaviour
```

### Context

This warning occurs during the execution of the `test_main_entry_point` integration test. The purpose of this test is to verify the behavior of the script when it is run as the main program, which involves testing the `if __name__ == "__main__"` block in `src/totp_calculator/main.py`.

To achieve this, the test uses the `runpy.run_module` function. This function executes the specified module in a way that mimics a direct command-line invocation.

### Why the Warning Occurs

The `pytest` test runner discovers and imports all test files and the modules they depend on at startup. Therefore, by the time `test_main_entry_point` is executed, the `totp_calculator.main` module has already been imported.

When `runpy.run_module` is called, it also loads the module, leading to a situation where the module is present in `sys.modules` before `runpy` executes it. This is what triggers the `RuntimeWarning`.

### How the Warning Is Handled

In the context of this specific test, this double-loading behavior is expected and does not cause any unpredictable behavior. The test is designed to work correctly under these conditions.

Instead of globally ignoring the warning, we use the `pytest.warns` context manager directly in the `test_main_entry_point` function. To make this even more robust, we use the `match` parameter to ensure we are catching the exact warning message we expect. This asserts that the `RuntimeWarning` is raised, effectively acknowledging and "catching" it in the one specific place where it is expected.

This approach allows us to maintain our strict "no warnings as errors" policy across the entire project while still being able to test the main entry point of our application, thus ensuring 100% test coverage.