# UI Testing Guide

## Overview

This directory contains UI tests that interact with a **real Anki installation**, not mocked. These tests verify that the Template Designer addon works correctly in the actual Anki environment.

## Prerequisites

1. **Anki Installation**: Anki must be installed at:
   ```
   C:\Users\Colin\AppData\Local\Programs\Anki
   ```

2. **Python Environment**: Install test dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```

3. **Close Anki**: Make sure Anki is closed before running tests that start Anki process.

## Running Tests

### Quick Start

Run all UI tests:
```bash
python run_ui_tests.py
```

### Common Test Scenarios

**Fast tests only** (skip slow tests):
```bash
python run_ui_tests.py --fast
```

**Verbose output**:
```bash
python run_ui_tests.py --verbose
```

**Skip tests requiring Anki process**:
```bash
python run_ui_tests.py --no-anki
```

**Run specific test**:
```bash
python run_ui_tests.py -k test_dialog_creation
```

**With coverage report**:
```bash
python run_ui_tests.py --coverage --html-report
```

### Using pytest directly

```bash
# Run all UI tests
pytest tests/ui -v

# Run specific test file
pytest tests/ui/test_designer_dialog_ui.py -v

# Run specific test class
pytest tests/ui/test_designer_dialog_ui.py::TestDesignerDialogUI -v

# Run specific test method
pytest tests/ui/test_designer_dialog_ui.py::TestDesignerDialogUI::test_dialog_creation -v
```

## Test Structure

### Test Files

- **test_designer_dialog_ui.py**: Tests for the main designer dialog
  - Dialog creation and display
  - WebView integration
  - JavaScript bridge
  - GrapeJS editor loading
  - User interactions
  - Performance tests

- **test_component_blocks_ui.py**: Tests for component blocks
  - Block availability
  - Block registration
  - Component types
  - Block content and configuration
  - Editor configuration

### Test Categories

#### 1. Dialog Tests (`TestDesignerDialogUI`)
- `test_dialog_creation` - Verify dialog can be created
- `test_dialog_shows` - Verify dialog displays correctly
- `test_dialog_has_webview` - Check WebView component exists
- `test_dialog_loads_html` - Verify HTML content loads
- `test_dialog_has_minimum_size` - Check minimum size constraints
- `test_dialog_title` - Verify window title
- `test_dialog_close` - Test dialog cleanup

#### 2. WebView Bridge Tests (`TestWebViewBridge`)
- `test_bridge_exists` - Verify bridge is available
- `test_bridge_methods` - Check bridge has required methods

#### 3. GrapeJS Editor Tests (`TestGrapeJSEditor`)
- `test_grapejs_files_exist` - Verify all GrapeJS files present
- `test_component_blocks_exist` - Check component block files
- `test_editor_initialization` - Verify editor initializes

#### 4. Component Library Tests (`TestComponentLibrary`)
- `test_components_directory_structure` - Check directory structure
- `test_block_categories_count` - Verify block category count
- `test_web_assets_complete` - Check all assets present

#### 5. Interaction Tests (`TestDialogInteraction`)
- `test_dialog_can_be_resized` - Test resize functionality
- `test_dialog_escape_key` - Test keyboard shortcuts
- `test_dialog_focus` - Test focus management

#### 6. Content Tests (`TestEditorContent`)
- `test_html_template_valid` - Validate HTML structure
- `test_javascript_files_valid` - Check JS syntax
- `test_css_files_valid` - Validate CSS files

#### 7. Anki Integration Tests (`TestAnkiIntegration`)
- `test_anki_traits_file_exists` - Check Anki traits
- `test_anki_plugin_exists` - Verify Anki plugin
- `test_anki_special_blocks_defined` - Check special blocks

#### 8. Performance Tests (`TestPerformance`)
- `test_dialog_opens_quickly` - Measure startup time
- `test_multiple_open_close_cycles` - Test for memory leaks

#### 9. Block Tests (`TestComponentBlocks`)
- Test availability of all block categories:
  - Layout blocks
  - Study action bar
  - Input blocks
  - Button blocks
  - Data blocks
  - Feedback blocks
  - Overlay blocks
  - Animation blocks
  - Accessibility blocks

#### 10. Block Registration Tests (`TestBlockRegistration`)
- `test_blocks_index_imports_all_categories` - Verify imports
- `test_blocks_index_exports_registration_functions` - Check exports
- `test_blocks_use_es6_modules` - Validate ES6 syntax

#### 11. Component Type Tests (`TestComponentTypes`)
- `test_component_types_index_exists` - Check registration
- `test_input_component_types_defined` - Verify input types
- `test_component_types_have_traits` - Check trait definitions

#### 12. Block Content Tests (`TestBlockContent`)
- `test_blocks_have_labels` - Verify labels
- `test_blocks_have_categories` - Check categories
- `test_blocks_have_content` - Validate default content

#### 13. Editor Configuration Tests (`TestEditorConfiguration`)
- `test_designer_js_initializes_editor` - Check GrapeJS init
- `test_designer_js_registers_components` - Verify registration
- `test_designer_js_configures_panels` - Check panel config
- `test_designer_css_has_styles` - Validate CSS

#### 14. Bridge Tests (`TestJavaScriptBridge`)
- `test_bridge_file_exists` - Check bridge.js
- `test_bridge_defines_communication` - Verify communication
- `test_webview_bridge_py_exists` - Check Python bridge

## Fixtures

### conftest.py Fixtures

- **anki_installation**: Verifies Anki installation exists
- **qapp**: Provides QApplication instance
- **anki_process**: Starts Anki process for a test
- **addon_loaded**: Ensures addon is loaded in Anki
- **designer_dialog**: Creates DesignerDialog instance
- **wait_for_load**: Helper for waiting on async operations

## Markers

Tests can be marked with pytest markers:

- `@pytest.mark.slow` - Tests that take >1 second
- Skip with: `python run_ui_tests.py --fast`

## Troubleshooting

### Anki Not Found
```
Error: Anki not found at C:\Users\Colin\AppData\Local\Programs\Anki
```
**Solution**: Update `ANKI_DIR` in `tests/ui/conftest.py` to your Anki installation path.

### Tests Timeout
```
Error: Test timed out
```
**Solution**: 
- Close other Anki instances
- Increase wait times in tests
- Run with `--fast` to skip slow tests

### WebView Not Loading
```
Error: WebView not found
```
**Solution**:
- Ensure PyQt6 WebEngine is installed
- Check that web assets exist in `web/` directory
- Verify `index.html` is valid

### Import Errors
```
Error: Cannot import DesignerDialog
```
**Solution**:
- Run tests from project root
- Ensure addon is in Python path
- Check that all dependencies are installed

## Writing New UI Tests

### Basic Test Template

```python
def test_my_feature(designer_dialog, wait_for_load):
    """Test description"""
    designer_dialog.show()
    wait_for_load(500)
    
    # Your test code here
    assert something
    
    designer_dialog.close()
```

### Testing with Anki Process

```python
def test_with_anki(anki_process, addon_loaded):
    """Test that requires Anki running"""
    # Anki is now running with addon loaded
    # Your test code here
```

### Async Operations

```python
def test_async_operation(designer_dialog, wait_for_load):
    """Test async operation"""
    designer_dialog.show()
    
    # Trigger async operation
    designer_dialog.some_async_method()
    
    # Wait for completion
    wait_for_load(1000)
    
    # Verify result
    assert designer_dialog.result is not None
```

## Best Practices

1. **Always use fixtures** for dialog creation and cleanup
2. **Wait for operations** using `wait_for_load()` fixture
3. **Clean up resources** - dialogs should be closed and deleted
4. **Mark slow tests** with `@pytest.mark.slow`
5. **Test isolation** - each test should be independent
6. **Descriptive names** - test names should describe what they test
7. **Clear assertions** - use descriptive assertion messages

## CI/CD Integration

To run UI tests in CI/CD:

```yaml
- name: Run UI Tests
  run: |
    python run_ui_tests.py --fast --no-anki --coverage
```

Note: Tests requiring Anki process (`anki_process` fixture) should be skipped in CI with `--no-anki`.

## Coverage

Generate coverage report:
```bash
python run_ui_tests.py --coverage --html-report
```

View HTML report:
```bash
# Open htmlcov/index.html in browser
start htmlcov/index.html
```

## Next Steps

After UI tests pass:
1. Test in actual Anki environment (manual testing)
2. Create integration tests for workflows
3. Add performance benchmarks
4. Document user-facing features
