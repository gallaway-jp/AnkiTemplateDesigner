# Quick Start: Testing

## Installation

```bash
# Install test dependencies
pip install -r requirements-test.txt
```

## Running Tests

### All Tests
```bash
python run_tests.py
```

### With Coverage Report
```bash
python run_tests.py --coverage
```

### HTML Coverage Report (opens in browser)
```bash
python run_tests.py --html-cov
```

### Unit Tests Only
```bash
python run_tests.py --unit
```

### Integration Tests Only
```bash
python run_tests.py --integration
```

### Quick Mode (skip slow tests)
```bash
python run_tests.py --quick
```

### Parallel Execution (faster)
```bash
python run_tests.py --parallel 4
```

### Re-run Failed Tests
```bash
python run_tests.py --failed
```

## Direct pytest Commands

### All Tests
```bash
$env:QT_QPA_PLATFORM="offscreen"  # Windows PowerShell
pytest tests/ -v
```

### Specific Test File
```bash
pytest tests/unit/test_constraints.py -v
```

### Specific Test Class
```bash
pytest tests/unit/test_constraints.py::TestConstraintResolver -v
```

### Specific Test Method
```bash
pytest tests/unit/test_constraints.py::TestConstraintResolver::test_center_horizontal -v
```

### With Coverage
```bash
pytest tests/ --cov=ui --cov=utils --cov-report=term-missing
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Show Print Statements
```bash
pytest tests/ -s
```

## Current Test Results

- **Total Tests**: 99
- **Passing**: 16 tests (infrastructure working)
- **Need Fixing**: 83 tests (API alignment needed)

See [TEST_RESULTS.md](TEST_RESULTS.md) for details.

## Documentation

- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Comprehensive testing guide
- [TESTING_SUMMARY.md](TESTING_SUMMARY.md) - Implementation summary
- [TEST_RESULTS.md](TEST_RESULTS.md) - Current test status

## Example Test Session

```bash
# 1. Install dependencies
pip install -r requirements-test.txt

# 2. Run unit tests
python run_tests.py --unit

# 3. Run with coverage
python run_tests.py --coverage

# 4. View HTML coverage report
python run_tests.py --html-cov

# 5. Fix failing tests and re-run
python run_tests.py --failed
```

## Troubleshooting

### Qt Platform Plugin Error
```bash
# Set environment variable
$env:QT_QPA_PLATFORM="offscreen"  # PowerShell
```

### Import Errors
Run from project root:
```bash
cd D:\Development\Python\AnkiTemplateDesigner
python run_tests.py
```

## Next Steps

1. Review [TEST_RESULTS.md](TEST_RESULTS.md) for known issues
2. Align test API expectations with actual implementation
3. Run tests iteratively to fix issues
4. Achieve 80%+ code coverage

---

For more details, see [TESTING_GUIDE.md](TESTING_GUIDE.md)
