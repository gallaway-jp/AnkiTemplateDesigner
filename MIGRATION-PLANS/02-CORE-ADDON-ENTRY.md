# Plan 02: Core Addon Entry Point

## Objective
Implement the main addon entry point that integrates with Anki, based on the `test_addon_minimal` pattern.

---

## Prerequisites
- [ ] Plan 01 completed and tested
- [ ] New `anki_template_designer/` directory structure exists

---

## Step 2.1: Implement Main Entry Point

### Task
Create the main `__init__.py` that handles Anki integration and addon initialization.

### Implementation

**anki_template_designer/__init__.py**
```python
"""
Anki Template Designer Add-on

A visual template designer for creating Anki flashcard templates.
Uses GrapeJS for drag-and-drop template building.

Author: [Your Name]
License: MIT
Version: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "[Your Name]"

import os
import sys
from typing import Optional

# Module-level variables for lazy initialization
_initialized: bool = False
_designer_dialog: Optional["DesignerDialog"] = None


def _get_addon_dir() -> str:
    """Get the addon directory path.
    
    Returns:
        Absolute path to the addon directory.
    """
    return os.path.dirname(os.path.abspath(__file__))


def _setup_logging() -> None:
    """Initialize logging for the addon.
    
    Sets up file and console logging based on configuration.
    Should be called early in addon initialization.
    """
    # Minimal initial logging - will be enhanced in Plan 09
    import logging
    
    logger = logging.getLogger("anki_template_designer")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)


def _load_config() -> dict:
    """Load addon configuration.
    
    Returns:
        Configuration dictionary with defaults merged with user settings.
    """
    import json
    
    config_path = os.path.join(_get_addon_dir(), "config.json")
    defaults = {
        "debugLogging": False,
        "logLevel": "INFO",
        "autoSave": True,
        "autoSaveIntervalSeconds": 30,
        "theme": "system",
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                defaults.update(user_config)
    except (json.JSONDecodeError, IOError) as e:
        # Log error but continue with defaults
        import logging
        logging.getLogger("anki_template_designer").warning(
            f"Failed to load config: {e}"
        )
    
    return defaults


def open_designer() -> None:
    """Open the template designer dialog.
    
    Creates a new dialog instance or shows existing one.
    This is the main entry point for users.
    """
    global _designer_dialog
    
    # Import here to avoid circular imports and for lazy loading
    from .gui.designer_dialog import DesignerDialog
    from aqt import mw
    
    if _designer_dialog is None or not _designer_dialog.isVisible():
        _designer_dialog = DesignerDialog(mw)
    
    _designer_dialog.show()
    _designer_dialog.raise_()
    _designer_dialog.activateWindow()


def _setup_menu() -> None:
    """Add addon menu item to Anki's Tools menu.
    
    Creates a menu action that opens the template designer.
    """
    from aqt import mw
    from aqt.qt import QAction
    
    action = QAction("Template Designer", mw)
    action.setShortcut("Ctrl+Shift+T")
    action.triggered.connect(open_designer)
    
    # Add to Tools menu
    mw.form.menuTools.addAction(action)


def _on_profile_loaded() -> None:
    """Callback when Anki profile is loaded.
    
    Performs initialization that requires a loaded profile.
    """
    global _initialized
    
    if _initialized:
        return
    
    import logging
    logger = logging.getLogger("anki_template_designer")
    logger.info("Anki Template Designer initializing...")
    
    _setup_menu()
    _initialized = True
    
    logger.info("Anki Template Designer initialized successfully")


# Only run initialization when in Anki environment
try:
    from aqt import gui_hooks
    
    # Set up logging immediately
    _setup_logging()
    
    # Register hook for profile load
    gui_hooks.profile_did_open.append(_on_profile_loaded)
    
except ImportError:
    # Not running in Anki - allow for testing
    pass
```

### Quality Checks

#### Security
- [ ] No hardcoded paths or credentials
- [ ] Config file read safely with exception handling
- [ ] No eval() or exec() usage
- [ ] Input validation for config values

#### Performance
- [ ] Lazy loading of heavy modules (gui, services)
- [ ] Single initialization check
- [ ] Minimal imports at module level

#### Best Practices
- [ ] Type hints used throughout
- [ ] Docstrings on all public functions
- [ ] Private functions prefixed with underscore
- [ ] Global state minimized

#### Maintainability
- [ ] Clear function responsibilities
- [ ] Easy to understand flow
- [ ] Configuration separated from logic

#### Documentation
- [ ] Module docstring with author/version
- [ ] All functions documented
- [ ] Clear inline comments where needed

#### Testing
- [ ] Can be imported outside Anki (ImportError handled)
- [ ] Functions are testable in isolation
- [ ] No side effects on import

#### Accessibility
- [ ] Keyboard shortcut provided (Ctrl+Shift+T)

#### Scalability
- [ ] Easy to add more initialization hooks
- [ ] Configuration expandable

#### Compatibility
- [ ] Works with Anki 2.1.50+
- [ ] Python 3.9+ compatible
- [ ] Cross-platform paths

#### Error Handling
- [ ] Config load errors handled gracefully
- [ ] Import errors handled for non-Anki environments
- [ ] Logging captures failures

#### Complexity
- [ ] Simple, linear initialization flow
- [ ] No deep nesting

#### Architecture
- [ ] Single responsibility principle
- [ ] Clear separation between Anki integration and core logic

#### License
- [ ] License mentioned in module docstring

#### Specification
- [ ] Menu item matches expected "Template Designer"
- [ ] Shortcut matches common convention

---

## Step 2.2: Create Stub Designer Dialog

### Task
Create a minimal stub dialog that will be expanded in Plan 03.

### Implementation

**anki_template_designer/gui/designer_dialog.py**
```python
"""Main designer dialog for the template designer."""

from typing import Optional

try:
    from aqt.qt import QDialog, QVBoxLayout, QLabel, Qt
    from aqt import mw
    HAS_ANKI = True
except ImportError:
    # Fallback for testing
    from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
    from PyQt6.QtCore import Qt
    mw = None
    HAS_ANKI = False


class DesignerDialog(QDialog):
    """Main template designer dialog.
    
    This is a stub implementation that will be expanded
    to include the full WebView-based editor.
    
    Attributes:
        MIN_WIDTH: Minimum dialog width in pixels.
        MIN_HEIGHT: Minimum dialog height in pixels.
    """
    
    MIN_WIDTH = 1200
    MIN_HEIGHT = 800
    
    def __init__(self, parent: Optional[QDialog] = None) -> None:
        """Initialize the designer dialog.
        
        Args:
            parent: Parent widget, defaults to Anki main window.
        """
        super().__init__(parent or mw)
        self._setup_window()
        self._setup_ui()
    
    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setWindowTitle("Anki Template Designer")
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        
        # Window flags for standard dialog behavior
        flags = Qt.WindowType.Window
        flags |= Qt.WindowType.WindowCloseButtonHint
        flags |= Qt.WindowType.WindowMinimizeButtonHint
        flags |= Qt.WindowType.WindowMaximizeButtonHint
        self.setWindowFlags(flags)
        
        # Set non-modal so user can interact with Anki
        self.setModal(False)
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Placeholder label - will be replaced with WebView
        label = QLabel("Template Designer Loading...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        self.setLayout(layout)
```

### Quality Checks

#### Security
- [ ] No unsafe Qt flags
- [ ] Modal set to False (safe default)

#### Performance
- [ ] Lightweight stub
- [ ] No heavy initialization

#### Best Practices
- [ ] Type hints
- [ ] Docstrings
- [ ] Constants for magic numbers

#### Maintainability
- [ ] Clear method names
- [ ] Separation of window and UI setup

#### Documentation
- [ ] Class and method docstrings
- [ ] Attributes documented

#### Testing
- [ ] Works with PyQt6 fallback
- [ ] Can be instantiated without Anki

#### Accessibility
- [ ] Window can be minimized/maximized
- [ ] Non-modal allows Anki interaction

#### Scalability
- [ ] Easy to add more UI elements

#### Compatibility
- [ ] Anki and PyQt6 fallback
- [ ] Python 3.9+ syntax

#### Error Handling
- [ ] Safe parent fallback

#### Complexity
- [ ] Simple, clear structure

#### Architecture
- [ ] Follows Qt dialog patterns

#### License
- [ ] N/A for this step

#### Specification
- [ ] Window size matches requirements

---

## User Testing Checklist

### Automated Tests

```python
# anki_template_designer/tests/test_init.py
"""Tests for addon initialization."""

import pytest
import sys
import os

# Add addon to path for testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_version_defined():
    """Test that version is defined."""
    from anki_template_designer import __version__
    assert __version__ == "2.0.0"


def test_config_loading():
    """Test configuration loading with defaults."""
    from anki_template_designer import _load_config
    config = _load_config()
    assert "debugLogging" in config
    assert "logLevel" in config


def test_addon_dir():
    """Test addon directory detection."""
    from anki_template_designer import _get_addon_dir
    addon_dir = _get_addon_dir()
    assert os.path.isdir(addon_dir)
```

Run tests:
```bash
python -m pytest anki_template_designer/tests/test_init.py -v
```

### Manual Verification in Anki

1. [ ] Copy `anki_template_designer/` to Anki addons folder
2. [ ] Restart Anki
3. [ ] Verify "Template Designer" appears in Tools menu
4. [ ] Click menu item - dialog should open
5. [ ] Verify dialog shows "Loading..." placeholder
6. [ ] Verify dialog is resizable
7. [ ] Verify dialog has minimize/maximize buttons
8. [ ] Verify can interact with Anki while dialog open
9. [ ] Check Anki console for errors

---

## Success Criteria

- [ ] All quality checks pass
- [ ] Automated tests pass
- [ ] Manual Anki tests pass
- [ ] No errors in Anki console
- [ ] Menu item works correctly

---

## Next Step

After successful completion, proceed to [03-DIALOG-SYSTEM.md](03-DIALOG-SYSTEM.md).

---

## Notes/Issues

| Issue | Resolution | Date |
|-------|------------|------|
| | | |
