# 06 - Implementation Phases

> **Purpose**: Define iterative implementation phases with milestones and deliverables.
> **Target Agent**: Claude Haiku 4.5 chat agent in VS Code
> **Date**: January 11, 2026

---

## Overview

The implementation is divided into 6 phases, each building on the previous. Each phase has:
- Clear deliverables
- Acceptance criteria
- Estimated duration
- Dependencies

**Total Estimated Duration**: 8-10 weeks

---

## Phase 1: Cleanup & Foundation

**Duration**: 1 week  
**Dependencies**: None

### Objectives

1. Remove deprecated files
2. Set up new folder structure
3. Configure development environment
4. Establish testing infrastructure

### Tasks

#### 1.1 File Cleanup

```powershell
# Execute in project root
# Remove deprecated UI files
Remove-Item -Recurse -Force ui/
Remove-Item -Recurse -Force renderers/

# Remove deprecated service
Remove-Item services/container.py

# Keep these files:
# - utils/security.py
# - utils/template_utils.py
# - utils/css_utils.py
# - config/constants.py
# - __init__.py
# - manifest.json
```

#### 1.2 Create New Structure

```powershell
# Create new directories
New-Item -ItemType Directory -Force -Path core
New-Item -ItemType Directory -Force -Path gui
New-Item -ItemType Directory -Force -Path hooks
New-Item -ItemType Directory -Force -Path web
New-Item -ItemType Directory -Force -Path web/blocks
New-Item -ItemType Directory -Force -Path web/assets
New-Item -ItemType Directory -Force -Path tests/unit
New-Item -ItemType Directory -Force -Path tests/integration
```

#### 1.3 Create Placeholder Files

```python
# core/__init__.py
"""Core business logic for template conversion."""

# gui/__init__.py
"""GUI components for the designer."""

# hooks/__init__.py
"""Anki hooks for menu and webview integration."""

# web/__init__.py - NOT NEEDED (static files)
```

#### 1.4 Update Configuration

```python
# config/constants.py - Update with new constants
ADDON_NAME = "Anki Template Designer"
ADDON_VERSION = "2.0.0"

GRAPEJS_VERSION = "0.21.10"
GRAPEJS_JS_URL = f"https://unpkg.com/grapesjs@{GRAPEJS_VERSION}/dist/grapes.min.js"
GRAPEJS_CSS_URL = f"https://unpkg.com/grapesjs@{GRAPEJS_VERSION}/dist/css/grapes.min.css"

ASSETS_DIR = "web/assets"
BLOCKS_DIR = "web/blocks"
```

### Deliverables

- [ ] Old files removed (30 files)
- [ ] New folder structure created
- [ ] Placeholder files with docstrings
- [ ] Updated constants.py
- [ ] Git commit with cleanup

### Acceptance Criteria

- Project runs without import errors
- All tests pass (existing utils tests)
- Folder structure matches 02-ARCHITECTURE.md

---

## Phase 2: Asset Management

**Duration**: 1 week  
**Dependencies**: Phase 1

### Objectives

1. Implement GrapeJS auto-downloader
2. Create asset verification system
3. Set up .gitignore for downloaded assets

### Tasks

#### 2.1 Implement Downloader

```python
# core/asset_manager.py
from dataclasses import dataclass
from pathlib import Path
import hashlib
import urllib.request
from typing import Optional, Callable
from config.constants import GRAPEJS_VERSION, GRAPEJS_JS_URL, GRAPEJS_CSS_URL

@dataclass
class Asset:
    name: str
    url: str
    filename: str
    expected_hash: Optional[str] = None

class AssetManager:
    ASSETS = [
        Asset("GrapeJS JavaScript", GRAPEJS_JS_URL, "grapes.min.js"),
        Asset("GrapeJS CSS", GRAPEJS_CSS_URL, "grapes.min.css"),
    ]
    
    def __init__(self, assets_dir: Path):
        self.assets_dir = assets_dir
        self.assets_dir.mkdir(parents=True, exist_ok=True)
    
    def ensure_assets(self, progress_callback: Optional[Callable] = None) -> bool:
        """Ensure all required assets are downloaded."""
        for i, asset in enumerate(self.ASSETS):
            if progress_callback:
                progress_callback(i, len(self.ASSETS), asset.name)
            
            asset_path = self.assets_dir / asset.filename
            if not asset_path.exists():
                if not self._download(asset):
                    return False
        return True
    
    def _download(self, asset: Asset) -> bool:
        """Download a single asset with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                path = self.assets_dir / asset.filename
                urllib.request.urlretrieve(asset.url, path)
                return True
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
        return False
```

#### 2.2 Create Progress Dialog

```python
# gui/download_dialog.py
from aqt.qt import QDialog, QVBoxLayout, QLabel, QProgressBar

class DownloadProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloading Assets")
        self.setFixedWidth(300)
        
        layout = QVBoxLayout(self)
        self.label = QLabel("Preparing...")
        self.progress = QProgressBar()
        
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
    
    def update_progress(self, current: int, total: int, name: str):
        self.label.setText(f"Downloading: {name}")
        self.progress.setMaximum(total)
        self.progress.setValue(current + 1)
```

#### 2.3 Update .gitignore

```gitignore
# Add to .gitignore
web/assets/grapes.min.js
web/assets/grapes.min.css
web/assets/*.min.js
web/assets/*.min.css
```

### Deliverables

- [ ] `core/asset_manager.py` - Download logic
- [ ] `gui/download_dialog.py` - Progress UI
- [ ] Updated `.gitignore`
- [ ] Unit tests for AssetManager

### Acceptance Criteria

- Assets download successfully on first run
- Progress dialog shows during download
- Assets not tracked in git
- Retry logic works on network failure

---

## Phase 3: GrapeJS Integration

**Duration**: 2 weeks  
**Dependencies**: Phase 2

### Objectives

1. Create web interface files (HTML, CSS, JS)
2. Implement QWebEngineView container
3. Set up Python-JavaScript bridge

### Tasks

#### 3.1 Week 1: Web Interface

Create files as specified in 03b-GRAPEJS-EDITOR.md:
- `web/index.html` - Main editor HTML
- `web/designer.js` - GrapeJS initialization
- `web/designer.css` - Editor styling
- `web/bridge.js` - QWebChannel integration

#### 3.2 Week 2: Python Integration

```python
# gui/designer_dialog.py
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QWebEngineView, QWebChannel
)
from pathlib import Path

class DesignerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Anki Template Designer")
        self.resize(1200, 800)
        
        self._setup_ui()
        self._setup_bridge()
        self._load_editor()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.preview_btn = QPushButton("Preview")
        self.export_btn = QPushButton("Export")
        toolbar.addWidget(self.save_btn)
        toolbar.addWidget(self.preview_btn)
        toolbar.addWidget(self.export_btn)
        toolbar.addStretch()
        
        # WebView
        self.webview = QWebEngineView()
        
        layout.addLayout(toolbar)
        layout.addWidget(self.webview)
    
    def _setup_bridge(self):
        self.channel = QWebChannel()
        self.bridge = WebViewBridge(self)
        self.channel.registerObject("bridge", self.bridge)
        self.webview.page().setWebChannel(self.channel)
    
    def _load_editor(self):
        html_path = Path(__file__).parent.parent / "web" / "index.html"
        self.webview.setUrl(QUrl.fromLocalFile(str(html_path)))
```

```python
# gui/webview_bridge.py
from aqt.qt import QObject, pyqtSlot, pyqtSignal
import json

class WebViewBridge(QObject):
    templateLoaded = pyqtSignal(str)
    
    def __init__(self, dialog):
        super().__init__()
        self.dialog = dialog
    
    @pyqtSlot(str, result=str)
    def saveTemplate(self, data: str) -> str:
        """Save template data from JavaScript."""
        try:
            template_data = json.loads(data)
            # Process and save
            return json.dumps({"success": True})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def loadTemplate(self, template_id: str) -> str:
        """Load template data for JavaScript."""
        # Load from Anki
        return json.dumps({"id": template_id, "data": {}})
```

### Deliverables

- [ ] `web/index.html` - Complete
- [ ] `web/designer.js` - GrapeJS initialized
- [ ] `web/designer.css` - Styled
- [ ] `web/bridge.js` - Communication working
- [ ] `gui/designer_dialog.py` - WebView container
- [ ] `gui/webview_bridge.py` - Python bridge

### Acceptance Criteria

- GrapeJS editor loads in dialog
- Can add blocks to canvas
- Python can send/receive data from JS
- No console errors

---

## Phase 4: Component Library

**Duration**: 2 weeks  
**Dependencies**: Phase 3

### Objectives

1. Implement all 200+ component blocks
2. Organize blocks by category
3. Add Anki-specific field placeholders

### Tasks

#### 4.1 Week 1: Core Components

Create block files as specified in 04a through 04f:
- `web/blocks/layout.js` - 22 components
- `web/blocks/navigation.js` - 15 components
- `web/blocks/inputs.js` - 29 components
- `web/blocks/buttons.js` - 13 components

#### 4.2 Week 2: Extended Components

- `web/blocks/data.js` - 20 components
- `web/blocks/feedback.js` - 16 components
- `web/blocks/overlays.js` - 11 components
- `web/blocks/search.js` - 9 components
- `web/blocks/commerce.js` - 11 components
- `web/blocks/social.js` - 11 components
- `web/blocks/charts.js` - 13 components
- `web/blocks/accessibility.js` - 10 components
- `web/blocks/system.js` - 8 components
- `web/blocks/motion.js` - 10 components
- `web/blocks/advanced.js` - 3 components

#### 4.3 Master Registration

```javascript
// web/blocks/index.js
import { registerLayoutBlocks } from './layout.js';
import { registerNavigationBlocks } from './navigation.js';
// ... all imports

export function registerAllBlocks(editor) {
    registerLayoutBlocks(editor);
    registerNavigationBlocks(editor);
    // ... all registrations
    console.log('[ATD] All blocks registered');
}
```

### Deliverables

- [ ] All 15 block category files
- [ ] `web/blocks/index.js` master file
- [ ] 209 total components registered
- [ ] Anki field placeholder block

### Acceptance Criteria

- All blocks appear in sidebar
- Blocks organized by category
- Each block renders correctly on canvas
- Anki field placeholders work

---

## Phase 5: Bidirectional Converter

**Duration**: 2 weeks  
**Dependencies**: Phase 4

### Objectives

1. Convert GrapeJS JSON to Anki HTML/CSS/JS
2. Convert existing Anki templates to GrapeJS format
3. Handle AnkiJSApi behavior bindings

### Tasks

#### 5.1 Week 1: GrapeJS → Anki

```python
# core/converter.py
from dataclasses import dataclass
from typing import Tuple, List, Dict
from utils.security import sanitize_html, sanitize_css

@dataclass
class ConversionResult:
    html: str
    css: str
    js: str
    errors: List[str]

class TemplateConverter:
    def to_anki(self, grapejs_data: dict) -> ConversionResult:
        """Convert GrapeJS project to Anki template."""
        errors = []
        
        html = self._convert_components(grapejs_data.get('components', []))
        css = self._convert_styles(grapejs_data.get('styles', []))
        js = self._convert_behaviors(grapejs_data.get('behaviors', []))
        
        return ConversionResult(
            html=sanitize_html(html),
            css=sanitize_css(css),
            js=js,
            errors=errors
        )
    
    def _convert_components(self, components: List[dict]) -> str:
        html_parts = []
        for comp in components:
            html_parts.append(self._component_to_html(comp))
        return '\n'.join(html_parts)
    
    def _component_to_html(self, comp: dict) -> str:
        tag = comp.get('tagName', 'div')
        classes = ' '.join(comp.get('classes', []))
        attrs = self._build_attrs(comp.get('attributes', {}))
        content = comp.get('content', '')
        
        # Handle nested components
        if 'components' in comp:
            content = self._convert_components(comp['components'])
        
        return f'<{tag} class="{classes}" {attrs}>{content}</{tag}>'
```

#### 5.2 Week 2: Anki → GrapeJS

```python
# core/parser.py
from html.parser import HTMLParser
from typing import List, Dict

class AnkiTemplateParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.components = []
        self.stack = []
    
    def handle_starttag(self, tag, attrs):
        component = {
            'tagName': tag,
            'attributes': dict(attrs),
            'classes': [],
            'components': []
        }
        
        # Extract classes
        if 'class' in component['attributes']:
            component['classes'] = component['attributes']['class'].split()
            del component['attributes']['class']
        
        if self.stack:
            self.stack[-1]['components'].append(component)
        else:
            self.components.append(component)
        
        self.stack.append(component)
    
    def handle_endtag(self, tag):
        if self.stack:
            self.stack.pop()
    
    def handle_data(self, data):
        if data.strip() and self.stack:
            self.stack[-1]['content'] = data.strip()

def parse_anki_template(html: str, css: str, js: str) -> dict:
    """Parse Anki template into GrapeJS format."""
    parser = AnkiTemplateParser()
    parser.feed(html)
    
    return {
        'components': parser.components,
        'styles': _parse_css(css),
        'behaviors': _parse_behaviors(js)
    }
```

### Deliverables

- [ ] `core/converter.py` - GrapeJS → Anki
- [ ] `core/parser.py` - Anki → GrapeJS
- [ ] `core/validator.py` - Validation
- [ ] Unit tests with 80%+ coverage

### Acceptance Criteria

- Round-trip conversion preserves structure
- Anki field syntax (`{{Field}}`) preserved
- Behaviors mapped to AnkiJSApi calls
- Invalid templates produce helpful errors

---

## Phase 6: Polish & Integration

**Duration**: 1-2 weeks  
**Dependencies**: Phase 5

### Objectives

1. Integrate with Anki menu system
2. Add template preview
3. Implement undo/redo persistence
4. Final testing and documentation

### Tasks

#### 6.1 Menu Integration

```python
# hooks/menu.py
from aqt import mw
from aqt.qt import QAction, QMenu

def setup_menu():
    """Add Template Designer to Anki Tools menu."""
    menu = mw.form.menuTools
    
    action = QAction("Template Designer", mw)
    action.triggered.connect(open_designer)
    menu.addAction(action)

def open_designer():
    from gui.designer_dialog import DesignerDialog
    dialog = DesignerDialog(mw)
    dialog.exec()
```

#### 6.2 Addon Entry Point

```python
# __init__.py
from aqt import gui_hooks
from .core.asset_manager import AssetManager
from .hooks.menu import setup_menu
from pathlib import Path

def on_profile_loaded():
    """Initialize addon after profile loads."""
    # Ensure assets
    assets_dir = Path(__file__).parent / "web" / "assets"
    manager = AssetManager(assets_dir)
    
    if not manager.check_assets():
        from .gui.download_dialog import DownloadProgressDialog
        dialog = DownloadProgressDialog()
        dialog.show()
        manager.ensure_assets(dialog.update_progress)
        dialog.close()
    
    # Setup menu
    setup_menu()

gui_hooks.profile_did_open.append(on_profile_loaded)
```

#### 6.3 Preview Dialog

```python
# gui/preview_dialog.py
from aqt.qt import QDialog, QVBoxLayout, QWebEngineView

class PreviewDialog(QDialog):
    def __init__(self, html: str, css: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Template Preview")
        self.resize(600, 800)
        
        layout = QVBoxLayout(self)
        self.webview = QWebEngineView()
        layout.addWidget(self.webview)
        
        self._render(html, css)
    
    def _render(self, html: str, css: str):
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head><style>{css}</style></head>
        <body>{html}</body>
        </html>
        """
        self.webview.setHtml(full_html)
```

### Deliverables

- [ ] `hooks/menu.py` - Menu integration
- [ ] Updated `__init__.py` - Entry point
- [ ] `gui/preview_dialog.py` - Preview
- [ ] User documentation
- [ ] Integration tests

### Acceptance Criteria

- Addon appears in Tools menu
- Opens without errors
- Can create, save, and preview templates
- Existing templates can be imported
- No regressions from original functionality

---

## Milestone Summary

| Phase | Duration | Key Deliverable |
|-------|----------|-----------------|
| 1. Cleanup | 1 week | Clean folder structure |
| 2. Assets | 1 week | GrapeJS auto-downloader |
| 3. GrapeJS | 2 weeks | Working editor in dialog |
| 4. Components | 2 weeks | 209 blocks available |
| 5. Converter | 2 weeks | Bidirectional conversion |
| 6. Polish | 1-2 weeks | Integrated Anki addon |

**Total**: 8-10 weeks

---

## Testing Strategy

### Unit Tests (Every Phase)

```python
# tests/unit/test_converter.py
# tests/unit/test_parser.py
# tests/unit/test_asset_manager.py
```

### Integration Tests (Phase 3+)

```python
# tests/integration/test_bridge.py
# tests/integration/test_round_trip.py
```

### Manual Testing Checklist

- [ ] Fresh install works
- [ ] Upgrade from previous version works
- [ ] All 209 blocks render
- [ ] Save/load templates
- [ ] Import existing Anki templates
- [ ] Export to Anki format
- [ ] Preview matches export
- [ ] Works on Windows/macOS/Linux
- [ ] Works on Anki 2.1.54+ (Qt5 and Qt6)

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| GrapeJS CDN unavailable | High | Local fallback, version pinning |
| Qt5/Qt6 incompatibility | Medium | Compatibility layer, testing |
| Large template performance | Medium | Lazy loading, virtualization |
| Complex CSS conversion | Low | Subset support, graceful degradation |

---

## Post-Launch

### Version 2.1 Features (Future)

- Template marketplace
- Cloud sync
- Collaborative editing
- Custom component creation

### Maintenance

- Monitor GrapeJS releases
- Update for new Anki versions
- Address user-reported issues
- Performance optimization

---

## Conclusion

This plan provides a structured approach to rebuilding the Anki Template Designer with GrapeJS. Each phase builds incrementally, allowing for testing and validation before proceeding.

**Key Success Factors**:
1. Maintain the 13 code standards throughout
2. Test early and often
3. Keep the converter bidirectional and reliable
4. Prioritize user experience

**Ready to Begin**: Start with Phase 1 cleanup tasks.
