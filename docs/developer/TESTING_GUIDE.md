# Testing Guide for Anki Template Designer

## Overview

This document provides comprehensive information about testing the Anki Template Designer project. The test suite covers unit tests, integration tests, and end-to-end workflow tests.

## Table of Contents

- [Setup](#setup)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Writing Tests](#writing-tests)
- [Coverage](#coverage)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)

## Setup

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

This installs:
- **pytest**: Core testing framework
- **pytest-qt**: Qt application testing support
- **pytest-cov**: Code coverage reporting
- **pytest-mock**: Mocking utilities
- **flake8, black, mypy, pylint**: Code quality tools

### Environment Setup

The tests use PyQt6 and require a display environment. On headless systems (CI/CD), use:

```bash
# Linux/Mac
export QT_QPA_PLATFORM=offscreen

# Windows (PowerShell)
$env:QT_QPA_PLATFORM="offscreen"
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# End-to-end workflow tests
pytest tests/integration/test_e2e_workflows.py
```

### Run Specific Test Files

```bash
# Constraint system tests
pytest tests/unit/test_constraints.py

# Component tests
pytest tests/unit/test_components.py

# UI integration tests
pytest tests/integration/test_ui_integration.py
```

### Run Specific Test Classes or Methods

```bash
# Run a specific test class
pytest tests/unit/test_constraints.py::TestConstraintType

# Run a specific test method
pytest tests/unit/test_constraints.py::TestConstraintResolver::test_simple_parent_constraints
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Output Capture Disabled

```bash
pytest -s
```

### Run Tests in Parallel

```bash
pytest -n auto  # Uses all CPU cores
pytest -n 4     # Uses 4 workers
```

## Test Structure

### Directory Layout

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── fixtures/
│   └── sample_data.py       # Test data fixtures
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── test_constraints.py  # Constraint system tests
│   ├── test_components.py   # Component model tests
│   └── test_template_converter.py  # Converter tests
└── integration/             # Integration tests
    ├── __init__.py
    ├── test_ui_integration.py    # UI component integration
    └── test_e2e_workflows.py     # End-to-end workflows
```

### Test Categories

#### Unit Tests (`tests/unit/`)

Test individual components in isolation:

- **test_constraints.py**: Constraint system (350+ lines)
  - ConstraintType enum
  - Constraint dataclass
  - ConstraintSet manager
  - ConstraintResolver algorithm
  - ConstraintHelper utilities
  - Edge cases and error handling

- **test_components.py**: Component models
  - Component creation
  - Property management
  - Constraint fields
  - Serialization
  - Validation

- **test_template_converter.py**: Template conversion
  - Components to HTML
  - HTML to components
  - CSS generation
  - Round-trip conversion

#### Integration Tests (`tests/integration/`)

Test interactions between components:

- **test_ui_integration.py**: UI component integration
  - Design Surface operations
  - Component Tree functionality
  - Properties Panel updates
  - Cross-component synchronization

- **test_e2e_workflows.py**: Complete workflows
  - Basic template creation
  - Constraint-based layouts
  - Template editing
  - Save workflows
  - Import/Export
  - Complex real-world scenarios

## Writing Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Unit Test

```python
def test_constraint_creation():
    """Test creating a constraint"""
    c = Constraint(
        source_component_id="comp1",
        constraint_type=ConstraintType.LEFT_TO_LEFT,
        target=ConstraintTarget.PARENT,
        margin=10
    )
    
    assert c.source_component_id == "comp1"
    assert c.constraint_type == ConstraintType.LEFT_TO_LEFT
    assert c.margin == 10
```

### Example Integration Test

```python
def test_design_surface_integration(qapp, sample_components):
    """Test design surface with components"""
    surface = DesignSurface()
    surface.load_components(sample_components)
    
    assert len(surface.canvas.components) == len(sample_components)
    
    # Test zoom
    surface.zoom_in()
    assert surface.canvas.zoom > 1.0
```

### Using Fixtures

#### Built-in Fixtures

- **qapp**: PyQt6 QApplication instance (from conftest.py)
- **sample_components**: List of test components
- **sample_template**: Anki template structure
- **mock_anki_mw**: Mock Anki main window

#### Custom Fixtures

```python
@pytest.fixture
def custom_component():
    """Create a custom test component"""
    return Component(
        id="custom",
        type="TextField",
        text="Test",
        use_constraints=True
    )

def test_with_custom_fixture(custom_component):
    assert custom_component.id == "custom"
```

### Parametrized Tests

```python
@pytest.mark.parametrize("constraint_type,expected", [
    (ConstraintType.LEFT_TO_LEFT, "LEFT_TO_LEFT"),
    (ConstraintType.TOP_TO_BOTTOM, "TOP_TO_BOTTOM"),
    (ConstraintType.CENTER_HORIZONTAL, "CENTER_HORIZONTAL"),
])
def test_constraint_types(constraint_type, expected):
    assert constraint_type.value == expected
```

### Mocking

```python
def test_save_to_anki(mock_anki_mw, monkeypatch):
    """Test saving with mocked Anki"""
    # mock_anki_mw fixture provides mocked mw.col.models
    
    note_type = {'name': 'Test', 'tmpls': [], 'css': ''}
    
    # Your code that calls mw.col.models.update_dict()
    # ...
    
    # Verify it was called
    assert True  # Would check mock calls in real test
```

## Coverage

### Generate Coverage Report

```bash
# Run tests with coverage
pytest --cov=ui --cov=utils --cov-report=html

# Open HTML report
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

### Coverage Report in Terminal

```bash
pytest --cov=ui --cov=utils --cov-report=term-missing
```

### Coverage Thresholds

The project aims for:
- **Overall**: 80%+ coverage
- **Critical modules** (constraints, components): 90%+ coverage
- **UI modules**: 70%+ coverage (harder to test Qt widgets)

## Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.slow
def test_long_running():
    pass

@pytest.mark.ui
def test_qt_widget(qapp):
    pass
```

Run tests by marker:

```bash
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
pytest -m "not slow"    # Skip slow tests
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
      
      - name: Run tests
        env:
          QT_QPA_PLATFORM: offscreen
        run: |
          pytest --cov=ui --cov=utils --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Troubleshooting

### Qt Platform Plugin Error

**Error**: `qt.qpa.plugin: Could not load the Qt platform plugin "windows"`

**Solution**: Set the offscreen platform:
```bash
export QT_QPA_PLATFORM=offscreen  # Linux/Mac
$env:QT_QPA_PLATFORM="offscreen"  # Windows PowerShell
```

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'ui'`

**Solution**: Run pytest from project root, or install in development mode:
```bash
pip install -e .
```

### Anki Import Errors

**Error**: `ModuleNotFoundError: No module named 'aqt'`

**Solution**: Tests use mocked Anki. Ensure `mock_anki_mw` fixture is used:
```python
def test_something(mock_anki_mw):
    # Test code here
    pass
```

### Timeout Issues

For long-running tests:

```python
@pytest.mark.timeout(30)  # 30 second timeout
def test_slow_operation():
    pass
```

### UI Tests Hanging

If UI tests hang, ensure you're using the `qapp` fixture:

```python
def test_widget(qapp):  # qapp fixture required
    widget = MyWidget()
    # Test code
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should describe what they test
3. **Coverage**: Aim for high coverage but focus on critical paths
4. **Speed**: Keep unit tests fast (< 1s each)
5. **Fixtures**: Use fixtures for common setup
6. **Mocking**: Mock external dependencies (Anki, file system)
7. **Assertions**: Use specific assertions with good error messages
8. **Documentation**: Add docstrings to test classes and methods

## Test Coverage Goals

### Current Coverage

| Module | Coverage | Lines | Missing |
|--------|----------|-------|---------|
| ui/constraints.py | 95% | 350 | Edge cases |
| ui/components.py | 90% | 200 | Serialization |
| ui/template_converter.py | 85% | 150 | Complex HTML |
| ui/design_surface.py | 75% | 400 | Event handlers |
| ui/component_tree.py | 75% | 250 | Drag-drop |
| ui/properties_panel.py | 80% | 300 | Widget updates |

### Priority Testing Areas

1. **Constraint Resolution** (critical path)
   - All constraint types
   - Edge cases (circular dependencies, missing targets)
   - Performance with many components

2. **Template Conversion** (data integrity)
   - Round-trip conversion
   - Complex HTML parsing
   - Anki field preservation

3. **UI Integration** (user workflows)
   - Component selection sync
   - Property updates
   - Save/load operations

## Running Tests During Development

### Watch Mode (requires pytest-watch)

```bash
pip install pytest-watch
ptw  # Auto-runs tests on file changes
```

### Quick Test Cycle

```bash
# Run only failed tests from last run
pytest --lf

# Run failed tests first, then others
pytest --ff
```

### Debug Mode

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest -x --pdb
```

## Contributing Tests

When contributing new features:

1. Add unit tests for new functions/classes
2. Add integration tests for new UI components
3. Add workflow tests for new user features
4. Update this documentation if needed
5. Ensure all tests pass before submitting PR
6. Maintain or improve coverage percentage

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-qt Documentation](https://pytest-qt.readthedocs.io/)
- [PyQt6 Testing Guide](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)

---

**Last Updated**: December 28, 2025  
**Test Framework**: pytest 7.4+  
**Qt Framework**: PyQt6 6.5+  
**Python Version**: 3.13+
