# Plan 03: Dialog System Setup

## Objective
Implement the full dialog system with WebView and proper sizing/positioning, based on `test_addon_minimal` pattern.

---

## Prerequisites
- [ ] Plan 01 completed and tested
- [ ] Plan 02 completed and tested
- [ ] Basic dialog opens from Tools menu

---

## Step 3.1: Implement QWebEngineView Integration

### Task
Replace the placeholder label with a QWebEngineView that can load HTML content.

### Implementation

**anki_template_designer/gui/designer_dialog.py**
```python
"""Main designer dialog with WebView for GrapeJS editor."""

import os
from typing import Optional, Any
import logging

try:
    from aqt.qt import (
        QDialog, QVBoxLayout, QWebEngineView, QUrl, 
        QSize, Qt, QScreen
    )
    from aqt import mw
    HAS_ANKI = True
except ImportError:
    from PyQt6.QtWidgets import QDialog, QVBoxLayout
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtCore import QUrl, QSize, Qt
    from PyQt6.QtGui import QScreen
    mw = None
    HAS_ANKI = False

logger = logging.getLogger("anki_template_designer.gui.designer_dialog")


class DesignerDialog(QDialog):
    """Main template designer dialog with embedded WebView editor.
    
    Hosts a QWebEngineView that loads the GrapeJS-based template editor.
    Supports responsive sizing based on screen dimensions.
    
    Attributes:
        MIN_WIDTH: Minimum dialog width in pixels.
        MIN_HEIGHT: Minimum dialog height in pixels.
        DEFAULT_WIDTH_RATIO: Default width as ratio of screen width.
        DEFAULT_HEIGHT_RATIO: Default height as ratio of screen height.
    """
    
    MIN_WIDTH = 1200
    MIN_HEIGHT = 800
    DEFAULT_WIDTH_RATIO = 0.85
    DEFAULT_HEIGHT_RATIO = 0.85
    MAX_WIDTH = 1920
    MAX_HEIGHT = 1080
    
    def __init__(self, parent: Optional[QDialog] = None) -> None:
        """Initialize the designer dialog.
        
        Args:
            parent: Parent widget, defaults to Anki main window.
        """
        super().__init__(parent or mw)
        
        self._webview: Optional[QWebEngineView] = None
        
        self._setup_window()
        self._setup_ui()
        self._load_editor()
        
        logger.info("DesignerDialog initialized")
    
    def _setup_window(self) -> None:
        """Configure window properties and sizing."""
        self.setWindowTitle("Anki Template Designer")
        
        # Window flags for standard dialog behavior
        flags = Qt.WindowType.Window
        flags |= Qt.WindowType.WindowCloseButtonHint
        flags |= Qt.WindowType.WindowMinimizeButtonHint
        flags |= Qt.WindowType.WindowMaximizeButtonHint
        self.setWindowFlags(flags)
        
        # Non-modal allows Anki interaction
        self.setModal(False)
        
        # Set size constraints
        self.setMinimumSize(QSize(self.MIN_WIDTH, self.MIN_HEIGHT))
        
        # Calculate optimal size
        self._set_optimal_size()
    
    def _get_screen(self) -> Optional[QScreen]:
        """Get the screen for size calculations.
        
        Returns:
            QScreen object or None if unavailable.
        """
        if mw is not None:
            return mw.screen()
        return None
    
    def _set_optimal_size(self) -> None:
        """Set optimal window size based on screen dimensions."""
        screen = self._get_screen()
        
        if screen is None:
            # Fallback to minimum size
            self.resize(self.MIN_WIDTH, self.MIN_HEIGHT)
            return
        
        geometry = screen.geometry()
        screen_width = geometry.width()
        screen_height = geometry.height()
        
        # Calculate size as percentage of screen
        width = int(screen_width * self.DEFAULT_WIDTH_RATIO)
        height = int(screen_height * self.DEFAULT_HEIGHT_RATIO)
        
        # Apply constraints
        width = max(self.MIN_WIDTH, min(width, self.MAX_WIDTH))
        height = max(self.MIN_HEIGHT, min(height, self.MAX_HEIGHT))
        
        # Center on screen
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.setGeometry(x, y, width, height)
        logger.debug(f"Dialog size set to {width}x{height} at ({x}, {y})")
    
    def _setup_ui(self) -> None:
        """Set up the user interface with WebView."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # No margins for full WebView
        
        # Create WebEngine view
        self._webview = QWebEngineView(self)
        layout.addWidget(self._webview)
        
        self.setLayout(layout)
    
    def _get_web_path(self) -> str:
        """Get the path to the web content.
        
        Returns:
            Absolute path to the index.html file.
        """
        addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(addon_dir, "web", "index.html")
    
    def _load_editor(self) -> None:
        """Load the editor HTML into the WebView."""
        if self._webview is None:
            logger.error("WebView not initialized")
            return
        
        html_path = self._get_web_path()
        
        if not os.path.exists(html_path):
            logger.error(f"Editor HTML not found: {html_path}")
            self._show_error("Editor files not found. Please reinstall the addon.")
            return
        
        file_url = QUrl.fromLocalFile(html_path)
        self._webview.load(file_url)
        logger.info(f"Loading editor from: {html_path}")
    
    def _show_error(self, message: str) -> None:
        """Display an error message in the WebView.
        
        Args:
            message: Error message to display.
        """
        if self._webview is None:
            return
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: #f5f5f5;
                }}
                .error {{
                    background: white;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                    max-width: 500px;
                }}
                .error h2 {{
                    color: #d32f2f;
                    margin-top: 0;
                }}
                .error p {{
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="error">
                <h2>Error</h2>
                <p>{message}</p>
            </div>
        </body>
        </html>
        """
        self._webview.setHtml(error_html)
    
    def closeEvent(self, event: Any) -> None:
        """Handle dialog close event.
        
        Args:
            event: Close event object.
        """
        logger.info("DesignerDialog closing")
        # Clean up WebView
        if self._webview is not None:
            self._webview.setUrl(QUrl("about:blank"))
        
        super().closeEvent(event)
    
    @property
    def webview(self) -> Optional[QWebEngineView]:
        """Get the WebView widget.
        
        Returns:
            The QWebEngineView instance.
        """
        return self._webview
```

### Quality Checks

#### Security
- [ ] No external URLs loaded
- [ ] Local file URLs only
- [ ] HTML escape in error messages (prevent XSS)
- [ ] No eval in JavaScript

#### Performance
- [ ] WebView created once
- [ ] Resources cleaned on close
- [ ] Optimal sizing calculated once

#### Best Practices
- [ ] Type hints throughout
- [ ] Property for webview access
- [ ] Private methods prefixed with underscore

#### Maintainability
- [ ] Clear method separation
- [ ] Logging at key points
- [ ] Constants for magic numbers

#### Documentation
- [ ] All methods documented
- [ ] Attributes documented in class docstring

#### Testing
- [ ] Works with PyQt6 fallback
- [ ] Handles missing HTML gracefully

#### Accessibility
- [ ] Window fully resizable
- [ ] Maximize button available
- [ ] Non-modal for Anki access

#### Scalability
- [ ] Easy to add toolbar/panels later

#### Compatibility
- [ ] Anki 2.1.50+ compatible
- [ ] Cross-platform paths

#### Error Handling
- [ ] Missing HTML handled gracefully
- [ ] Error display in WebView
- [ ] Logging on errors

#### Complexity
- [ ] Linear flow
- [ ] Single responsibility methods

#### Architecture
- [ ] Clean separation between window and content

#### License
- [ ] N/A

#### Specification
- [ ] Matches test_addon_minimal pattern

---

## Step 3.2: Create Basic HTML Shell

### Task
Create a minimal index.html for the WebView.

### Implementation

**anki_template_designer/web/index.html**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';">
    <title>Anki Template Designer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html, body {
            width: 100%;
            height: 100%;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: #f5f5f5;
            color: #333;
        }

        #app {
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
        }

        .header {
            background: #2c3e50;
            color: white;
            padding: 16px 24px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header h1 {
            font-size: 20px;
            font-weight: 600;
        }

        .header-status {
            font-size: 12px;
            opacity: 0.8;
        }

        .main-content {
            display: flex;
            flex: 1;
            overflow: hidden;
        }

        .loading {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            height: 100%;
            background: white;
        }

        .loading-spinner {
            text-align: center;
        }

        .loading-spinner::before {
            content: '';
            display: block;
            width: 40px;
            height: 40px;
            margin: 0 auto 16px;
            border: 3px solid #eee;
            border-top-color: #2c3e50;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .loading-text {
            font-size: 14px;
            color: #666;
        }
    </style>
</head>
<body>
    <div id="app">
        <header class="header">
            <h1>Anki Template Designer</h1>
            <span class="header-status" id="status">Initializing...</span>
        </header>
        
        <main class="main-content">
            <div class="loading" id="loading">
                <div class="loading-spinner">
                    <span class="loading-text">Loading editor...</span>
                </div>
            </div>
        </main>
    </div>

    <script>
        // Initialize when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            const status = document.getElementById('status');
            const loading = document.getElementById('loading');
            
            // Update status
            if (status) {
                status.textContent = 'Ready';
            }
            
            // Simulate loading complete
            setTimeout(function() {
                if (loading) {
                    loading.innerHTML = '<p style="text-align: center; padding: 40px; color: #666;">Editor shell loaded. Full editor will be integrated in later steps.</p>';
                }
            }, 500);
        });
        
        // Expose ready signal for bridge
        window.editorReady = function() {
            return true;
        };
    </script>
</body>
</html>
```

### Quality Checks

#### Security
- [ ] Content-Security-Policy header set
- [ ] No external resource loading
- [ ] No inline event handlers (use addEventListener)

#### Performance
- [ ] Minimal CSS
- [ ] CSS animation efficient (transform, not position)
- [ ] No jQuery or heavy libraries

#### Best Practices
- [ ] Semantic HTML
- [ ] CSS reset included
- [ ] Responsive viewport meta

#### Maintainability
- [ ] CSS organized by component
- [ ] JavaScript at bottom of body
- [ ] Comments for non-obvious code

#### Documentation
- [ ] Comments in JavaScript

#### Testing
- [ ] Loads without errors
- [ ] Shows loading state

#### Accessibility
- [ ] Proper heading hierarchy
- [ ] Readable font sizes
- [ ] Sufficient contrast ratios

#### Scalability
- [ ] Easy to add more sections
- [ ] Modular structure

#### Compatibility
- [ ] Works in Qt WebEngine
- [ ] No browser-specific APIs

#### Error Handling
- [ ] Null checks before DOM manipulation

#### Complexity
- [ ] Simple, clean structure

#### Architecture
- [ ] Clear separation of content/style/script

#### License
- [ ] N/A

#### Specification
- [ ] Matches test_addon_minimal styling

---

## Step 3.3: Update GUI __init__.py

### Task
Update the GUI module's `__init__.py` to export the dialog.

### Implementation

**anki_template_designer/gui/__init__.py**
```python
"""
GUI module for Qt-based user interface components.

Contains:
- DesignerDialog: Main template designer window
- WebView integration for GrapeJS editor
"""

from .designer_dialog import DesignerDialog

__all__ = ["DesignerDialog"]
```

### Quality Checks

All standard checks apply - this is a simple export file.

---

## User Testing Checklist

### Automated Tests

```python
# anki_template_designer/tests/test_dialog.py
"""Tests for designer dialog."""

import pytest
import os


def test_web_path_exists():
    """Test that index.html exists."""
    from anki_template_designer.gui.designer_dialog import DesignerDialog
    
    # Create instance to get path
    dialog = DesignerDialog.__new__(DesignerDialog)
    dialog._webview = None
    
    # Manually set up path
    addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_path = os.path.join(addon_dir, "web", "index.html")
    
    assert os.path.exists(html_path), f"index.html not found at {html_path}"


def test_constants_valid():
    """Test that size constants are valid."""
    from anki_template_designer.gui.designer_dialog import DesignerDialog
    
    assert DesignerDialog.MIN_WIDTH > 0
    assert DesignerDialog.MIN_HEIGHT > 0
    assert DesignerDialog.MIN_WIDTH <= DesignerDialog.MAX_WIDTH
    assert DesignerDialog.MIN_HEIGHT <= DesignerDialog.MAX_HEIGHT


def test_html_valid():
    """Test that index.html is valid HTML."""
    addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_path = os.path.join(addon_dir, "web", "index.html")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert '<!DOCTYPE html>' in content
    assert '<html' in content
    assert '</html>' in content
    assert 'Content-Security-Policy' in content
```

Run tests:
```bash
python -m pytest anki_template_designer/tests/test_dialog.py -v
```

### Manual Verification in Anki

1. [ ] Restart Anki with updated addon
2. [ ] Open Template Designer from Tools menu
3. [ ] Verify dialog opens at appropriate size
4. [ ] Verify dialog is centered on screen
5. [ ] Verify header shows "Anki Template Designer"
6. [ ] Verify loading spinner appears briefly
7. [ ] Verify "Ready" status appears in header
8. [ ] Verify dialog is resizable
9. [ ] Verify dialog can be minimized/maximized
10. [ ] Verify can interact with Anki while dialog open
11. [ ] Close dialog and verify no errors
12. [ ] Reopen dialog to verify cleanup worked

---

## Success Criteria

- [ ] All quality checks pass
- [ ] Automated tests pass
- [ ] Manual Anki tests pass
- [ ] Dialog displays HTML content
- [ ] No errors or warnings in console

---

## Next Step

After successful completion, proceed to [04-WEBVIEW-BRIDGE.md](04-WEBVIEW-BRIDGE.md).

---

## Notes/Issues

| Issue | Resolution | Date |
|-------|------------|------|
| | | |
