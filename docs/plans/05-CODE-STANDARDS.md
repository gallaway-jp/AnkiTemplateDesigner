# 05 - Code Standards & Quality Guidelines

> **Purpose**: Define code review standards and quality requirements for the Anki Template Designer addon.
> **Target Agent**: Claude Haiku 4.5 chat agent in VS Code
> **Date**: January 11, 2026

---

## Overview

All code contributions must pass review against these 13 standards before merging. Each standard has specific rules and automated checks where applicable.

---

## 1. Security (OWASP Compliance)

### Requirements

- **XSS Prevention**: All user input must be sanitized before rendering
- **Input Validation**: Validate all inputs on both Python and JavaScript sides
- **Path Traversal**: Use `utils/security.py` for all file path operations
- **Content Security Policy**: Enforce CSP in QWebEngineView
- **No eval()**: Never use `eval()`, `exec()`, or `Function()` constructor

### Implementation Patterns

```python
# utils/security.py - KEEP AND USE THIS FILE

from utils.security import (
    sanitize_html,
    sanitize_css,
    validate_file_path,
    is_safe_url
)

# Always sanitize before rendering
safe_html = sanitize_html(user_input)

# Validate file paths
if not validate_file_path(path, allowed_dirs):
    raise SecurityError("Invalid path")
```

```javascript
// JavaScript - Sanitization
function sanitizeForHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Never do this:
// element.innerHTML = userInput;  // DANGEROUS
// eval(userCode);                 // DANGEROUS
```

### Checklist

- [ ] All user inputs sanitized
- [ ] File paths validated against allowed directories
- [ ] No dangerous function usage (eval, exec, Function)
- [ ] CSP headers configured
- [ ] Third-party scripts integrity-checked

---

## 2. Performance

### Requirements

- **Startup Time**: Addon initialization < 500ms
- **UI Response**: All UI actions respond < 100ms
- **Memory**: Peak memory usage < 100MB
- **Asset Loading**: Lazy load non-critical assets

### Implementation Patterns

```python
# Lazy loading pattern
class DesignerDialog:
    _editor = None
    
    @property
    def editor(self):
        if self._editor is None:
            self._editor = self._create_editor()
        return self._editor

# Async operations for heavy tasks
from aqt.qt import QThread, pyqtSignal

class AssetDownloader(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool)
    
    def run(self):
        # Download in background
        pass
```

```javascript
// Debounce expensive operations
function debounce(fn, delay) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

// Use for editor changes
editor.on('update', debounce(saveToStorage, 500));
```

### Checklist

- [ ] Startup time measured and < 500ms
- [ ] No blocking operations on main thread
- [ ] Large assets loaded asynchronously
- [ ] Event handlers debounced where appropriate
- [ ] Memory profiled under typical usage

---

## 3. Best Practices

### Python Best Practices

```python
# Type hints required
def convert_to_html(data: dict) -> str:
    """Convert GrapeJS data to HTML.
    
    Args:
        data: GrapeJS project JSON data
        
    Returns:
        Generated HTML string
        
    Raises:
        ConversionError: If data format is invalid
    """
    pass

# Context managers for resources
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Dataclasses for data structures
from dataclasses import dataclass

@dataclass
class Component:
    id: str
    type: str
    content: str
    styles: dict
```

### JavaScript Best Practices

```javascript
// Use const/let, never var
const CONSTANTS = Object.freeze({ ... });
let mutableValue = 0;

// Async/await over callbacks
async function loadTemplate(id) {
    try {
        const data = await bridge.loadTemplate(id);
        return data;
    } catch (error) {
        console.error('Failed to load template:', error);
        throw error;
    }
}

// Destructuring
const { components, styles, assets } = projectData;
```

### Checklist

- [ ] Type hints on all function signatures
- [ ] Docstrings on all public functions/classes
- [ ] No bare except clauses
- [ ] Resources properly closed/released
- [ ] Modern JavaScript features used appropriately

---

## 4. Maintainability

### Requirements

- **Single Responsibility**: Each module/class has one purpose
- **DRY**: No duplicated code blocks > 5 lines
- **Naming**: Descriptive names, consistent conventions
- **File Size**: No file exceeds 500 lines

### Naming Conventions

```python
# Python
class TemplateConverter:  # PascalCase for classes
    def convert_to_html(self):  # snake_case for methods
        MAX_DEPTH = 10  # UPPER_CASE for constants
        template_data = {}  # snake_case for variables

# Files: snake_case.py
```

```javascript
// JavaScript
class DesignerBridge {}  // PascalCase for classes
function registerBlocks() {}  // camelCase for functions
const MAX_UNDO_STEPS = 50;  // UPPER_CASE for constants
let currentEditor = null;  // camelCase for variables

// Files: camelCase.js
```

### Checklist

- [ ] Each file has a single, clear purpose
- [ ] No code duplication (extract to shared utilities)
- [ ] Names are self-documenting
- [ ] Files under 500 lines (split if larger)
- [ ] Logical folder structure maintained

---

## 5. Documentation

### Required Documentation

```python
"""
Module: core/converter.py
Purpose: Bidirectional conversion between GrapeJS JSON and Anki templates

Classes:
    - TemplateConverter: Main converter class
    - ConversionError: Exception for conversion failures
"""

class TemplateConverter:
    """Converts between GrapeJS JSON and Anki HTML/CSS/JS.
    
    The converter maintains a mapping of GrapeJS components to their
    Anki template equivalents, handling:
    - Component structure to HTML
    - Inline styles to CSS
    - Behavior bindings to JavaScript
    
    Example:
        converter = TemplateConverter()
        html, css, js = converter.to_anki(grapejs_data)
    """
```

### Inline Comments

```python
# Good: Explains WHY
# Skip empty components to avoid generating invalid HTML
if not component.content:
    continue

# Bad: Explains WHAT (obvious from code)
# Increment counter by 1
counter += 1
```

### Checklist

- [ ] Module-level docstring in every file
- [ ] Class docstrings with purpose and usage
- [ ] Function docstrings with args/returns/raises
- [ ] Complex logic has explanatory comments
- [ ] README updated for new features

---

## 6. Testing

### Test Requirements

- **Coverage**: Minimum 80% code coverage
- **Unit Tests**: All public functions tested
- **Integration Tests**: Python-JS bridge tested
- **Edge Cases**: Null, empty, malformed inputs tested

### Test Patterns

```python
# tests/test_converter.py
import pytest
from core.converter import TemplateConverter, ConversionError

class TestTemplateConverter:
    @pytest.fixture
    def converter(self):
        return TemplateConverter()
    
    def test_empty_project_returns_empty_html(self, converter):
        result = converter.to_html({})
        assert result == ""
    
    def test_invalid_data_raises_error(self, converter):
        with pytest.raises(ConversionError):
            converter.to_html({"invalid": "structure"})
    
    @pytest.mark.parametrize("input,expected", [
        ({"type": "text", "content": "Hello"}, "<p>Hello</p>"),
        ({"type": "heading", "content": "Title"}, "<h1>Title</h1>"),
    ])
    def test_component_conversion(self, converter, input, expected):
        assert converter.component_to_html(input) == expected
```

### Checklist

- [ ] All new code has corresponding tests
- [ ] Tests follow Arrange-Act-Assert pattern
- [ ] Edge cases and error paths tested
- [ ] Mocks used for external dependencies
- [ ] Tests run in CI pipeline

---

## 7. Accessibility

### Requirements

- **Keyboard Navigation**: All features accessible via keyboard
- **Screen Readers**: ARIA labels on interactive elements
- **Color Contrast**: WCAG AA minimum (4.5:1 for text)
- **Focus Indicators**: Visible focus states

### Implementation

```python
# PyQt dialogs
class DesignerDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Anki Template Designer")
        
        # Set accessible names
        self.save_btn.setAccessibleName("Save Template")
        self.preview_btn.setAccessibleName("Preview Template")
        
        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+S"), self, self.save)
```

```javascript
// GrapeJS components should include ARIA
bm.add('button', {
    content: {
        tagName: 'button',
        attributes: {
            'role': 'button',
            'aria-label': 'Action button'
        }
    }
});
```

### Checklist

- [ ] All interactive elements focusable
- [ ] Keyboard shortcuts documented
- [ ] ARIA labels on custom controls
- [ ] No color-only information
- [ ] Focus order is logical

---

## 8. Scalability

### Requirements

- **Component Count**: Handle 200+ block types efficiently
- **Template Size**: Support templates up to 1MB
- **Undo History**: Maintain 50+ undo steps without lag

### Patterns

```javascript
// Virtual rendering for large lists
class BlockPanel {
    constructor() {
        this.visibleRange = { start: 0, end: 20 };
    }
    
    renderVisibleBlocks() {
        const blocks = this.allBlocks.slice(
            this.visibleRange.start,
            this.visibleRange.end
        );
        // Only render visible blocks
    }
}

// Chunked processing for large data
async function processLargeTemplate(data) {
    const chunks = splitIntoChunks(data, 100);
    for (const chunk of chunks) {
        await processChunk(chunk);
        await yieldToUI(); // Prevent blocking
    }
}
```

### Checklist

- [ ] Large datasets handled with pagination/virtualization
- [ ] Heavy operations chunked or async
- [ ] No O(n²) algorithms on user data
- [ ] Memory released when not needed

---

## 9. Compatibility

### Requirements

- **Anki Versions**: 2.1.54+ (Qt5 and Qt6)
- **Python**: 3.9+
- **Platforms**: Windows, macOS, Linux

### Implementation

```python
# Qt compatibility
try:
    from PyQt6.QtWidgets import QDialog
    from PyQt6.QtCore import Qt
    QT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import QDialog
    from PyQt5.QtCore import Qt
    QT_VERSION = 5

# Platform detection
import sys
IS_WINDOWS = sys.platform.startswith('win')
IS_MAC = sys.platform == 'darwin'
IS_LINUX = sys.platform.startswith('linux')

# Feature detection over version checking
def supports_webengine():
    try:
        from aqt.qt import QWebEngineView
        return True
    except ImportError:
        return False
```

### Checklist

- [ ] Tested on Anki 2.1.54, 2.1.65, 24.x
- [ ] Works with both Qt5 and Qt6
- [ ] No platform-specific code without fallbacks
- [ ] Dependencies version-pinned

---

## 10. Error Handling

### Requirements

- **User-Friendly**: Technical errors translated to user messages
- **Logging**: All errors logged with context
- **Recovery**: Graceful degradation where possible
- **No Silent Failures**: All errors surfaced appropriately

### Implementation

```python
import logging
from aqt.utils import showWarning, showInfo

logger = logging.getLogger(__name__)

class ConversionError(Exception):
    """Raised when template conversion fails."""
    pass

def convert_template(data: dict) -> str:
    try:
        return _do_conversion(data)
    except KeyError as e:
        logger.error(f"Missing key in template data: {e}", exc_info=True)
        raise ConversionError(f"Template is missing required field: {e}")
    except Exception as e:
        logger.exception("Unexpected conversion error")
        raise ConversionError("An unexpected error occurred during conversion")

# In UI code
try:
    result = convert_template(data)
except ConversionError as e:
    showWarning(str(e))
```

```javascript
// JavaScript error handling
window.onerror = function(msg, url, line, col, error) {
    console.error('Global error:', { msg, url, line, col, error });
    bridge.reportError({ message: msg, stack: error?.stack });
    return false;
};

// Async error handling
async function saveTemplate() {
    try {
        await bridge.save(editor.getProjectData());
        showNotification('Template saved!', 'success');
    } catch (error) {
        showNotification('Failed to save template', 'error');
        console.error('Save failed:', error);
    }
}
```

### Checklist

- [ ] All exceptions caught at appropriate level
- [ ] User sees friendly error messages
- [ ] Errors logged with stack traces
- [ ] Critical errors prevent data loss
- [ ] Recovery attempted before failing

---

## 11. Complexity

### Requirements

- **Cyclomatic Complexity**: Max 10 per function
- **Function Length**: Max 50 lines
- **Nesting Depth**: Max 4 levels
- **Parameters**: Max 5 per function

### Refactoring Patterns

```python
# Before: High complexity
def process_component(component, parent, depth, options, context):
    if component.type == 'text':
        if options.get('bold'):
            if parent.type == 'heading':
                # ... deeply nested logic
                pass

# After: Reduced complexity
def process_component(component: Component, context: ProcessContext) -> str:
    handler = self._get_handler(component.type)
    return handler.process(component, context)

class TextHandler:
    def process(self, component: Component, context: ProcessContext) -> str:
        styles = self._compute_styles(component, context)
        return self._render(component.content, styles)
```

### Checklist

- [ ] Functions do one thing
- [ ] Early returns reduce nesting
- [ ] Complex conditions extracted to named functions
- [ ] Large functions split into smaller ones

---

## 12. Architecture

### Requirements

- **Separation of Concerns**: UI, logic, and data layers separated
- **Dependency Direction**: High-level modules don't depend on low-level
- **Interfaces**: Components communicate via defined interfaces
- **Testability**: All components testable in isolation

### Layer Structure

```
┌─────────────────────────────────────┐
│           UI Layer (gui/)           │
│  DesignerDialog, PreviewDialog      │
├─────────────────────────────────────┤
│         Bridge Layer (hooks/)       │
│  WebViewBridge, menu hooks          │
├─────────────────────────────────────┤
│         Core Layer (core/)          │
│  Converter, Parser, Validator       │
├─────────────────────────────────────┤
│         Utils Layer (utils/)        │
│  Security, CSS, Template utilities  │
└─────────────────────────────────────┘
```

### Dependency Rules

```python
# Good: Core depends on nothing
# core/converter.py
class TemplateConverter:
    def convert(self, data: dict) -> tuple:
        pass  # Pure logic, no UI imports

# Good: GUI depends on Core
# gui/designer_dialog.py
from core.converter import TemplateConverter

class DesignerDialog:
    def __init__(self):
        self.converter = TemplateConverter()

# Bad: Core importing from GUI
# core/converter.py
from gui.designer_dialog import show_progress  # WRONG!
```

### Checklist

- [ ] No circular imports
- [ ] Core logic has no UI dependencies
- [ ] Clear module boundaries
- [ ] Interfaces defined for cross-layer communication

---

## 13. License Compliance

### Requirements

- **GPL v3**: Addon is GPL v3 compatible
- **Dependencies**: All dependencies license-compatible
- **Attribution**: Third-party code properly attributed
- **No Proprietary**: No proprietary dependencies

### Allowed Licenses

| License | Allowed | Notes |
|---------|---------|-------|
| MIT | ✅ | Attribution required |
| Apache 2.0 | ✅ | Attribution required |
| BSD | ✅ | Attribution required |
| GPL v3 | ✅ | Compatible |
| LGPL | ✅ | Compatible |
| Proprietary | ❌ | Not allowed |
| CC-NC | ❌ | Non-commercial restriction |

### GrapeJS License

GrapeJS uses BSD 3-Clause license - **compatible with GPL v3**.

```
// web/index.html - Include attribution
<!--
  GrapeJS - BSD 3-Clause License
  Copyright (c) GrapeJS contributors
  https://github.com/GrapesJS/grapesjs
-->
```

### Checklist

- [ ] All dependencies listed in requirements.txt
- [ ] License check performed on new dependencies
- [ ] Attribution comments in source files
- [ ] LICENSE file includes all third-party notices

---

## Code Review Process

### Before Submitting

1. Run all tests: `pytest tests/`
2. Check coverage: `pytest --cov=. --cov-report=html`
3. Lint Python: `flake8 --max-line-length=100`
4. Lint JavaScript: `eslint web/`
5. Type check: `mypy .`

### Review Checklist

```markdown
## Code Review Checklist

### Security
- [ ] No XSS vulnerabilities
- [ ] Input validation present
- [ ] No dangerous functions

### Quality
- [ ] Tests included
- [ ] Documentation updated
- [ ] No code duplication
- [ ] Follows naming conventions

### Performance
- [ ] No blocking operations
- [ ] Large data handled efficiently
- [ ] Resources released properly

### Compatibility
- [ ] Works on all platforms
- [ ] Qt5/Qt6 compatible
- [ ] Anki version requirements met
```

---

## Next Document

See [06-IMPLEMENTATION-PHASES.md](06-IMPLEMENTATION-PHASES.md) for the phased implementation plan.
