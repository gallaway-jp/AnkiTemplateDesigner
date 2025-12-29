# Build and Development Scripts

This directory contains build scripts and development tools.

## Available Scripts

### build.py

Builds the Anki add-on package for distribution.

**Usage:**
```bash
python scripts/build.py
```

**Description:** Creates a packaged `.ankiaddon` file for distribution in Anki.

### run_tests.py

Runs the project test suite.

**Usage:**
```bash
python scripts/run_tests.py
```

**Description:** Executes all tests using pytest with coverage reporting.

**Options:**
- Run with coverage: `python scripts/run_tests.py --cov`
- Run specific test file: `python scripts/run_tests.py tests/unit/test_specific.py`
- Run with verbose output: `python scripts/run_tests.py -v`

## Requirements

Make sure all development dependencies are installed:

```bash
pip install -r requirements.txt
```

## See Also

- [Development Guide](../docs/developer/DEVELOPMENT.md) - Complete development setup
- [Testing Guide](../docs/developer/TESTING_GUIDE.md) - Testing guidelines
