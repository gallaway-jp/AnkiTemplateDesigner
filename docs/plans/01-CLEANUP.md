# 01 - Cleanup Plan: Files to Remove and Migration Path

> **Purpose**: Document all current files that will be removed or replaced in the GrapeJS-based rewrite.
> **Target Agent**: Claude Haiku 4.5 chat agent in VS Code
> **Date**: January 11, 2026

---

## Overview

The current AnkiTemplateDesigner project contains 50+ files implementing a custom Qt-based visual designer. This will be replaced with a GrapeJS-powered web-based designer running inside QWebEngineView. Most existing UI files will be removed, while core utilities and security logic will be preserved.

---

## Files to DELETE (Complete Removal)

### UI Components (`ui/` folder) - DELETE ALL
These implement the old Qt-based visual designer that will be replaced by GrapeJS:

| File | Lines | Reason for Removal |
|------|-------|-------------------|
| `ui/android_studio_dialog.py` | 534 | Replaced by GrapeJS designer dialog |
| `ui/base_dialog.py` | ~200 | No longer needed with single dialog |
| `ui/commands.py` | 330 | GrapeJS has built-in undo/redo |
| `ui/component_search.py` | 380 | GrapeJS has built-in block search |
| `ui/component_tree.py` | ~250 | GrapeJS has built-in layer manager |
| `ui/components.py` | 355 | Replaced by GrapeJS block definitions |
| `ui/constraints.py` | ~200 | Not needed - using CSS grid/flexbox |
| `ui/design_surface.py` | ~300 | Replaced by GrapeJS canvas |
| `ui/designer_dialog.py` | ~400 | Replaced by new GrapeJS dialog |
| `ui/editor_widget.py` | ~250 | GrapeJS has built-in code editor |
| `ui/grid.py` | 360 | GrapeJS handles grid snapping |
| `ui/layout_strategies.py` | ~200 | CSS handles layouts |
| `ui/multi_selection.py` | 380 | GrapeJS has multi-select built-in |
| `ui/preview_widget.py` | ~300 | Will be reimplemented with AnkiWebView |
| `ui/progress_indicators.py` | 350 | Overly complex, simplify |
| `ui/properties_panel.py` | ~300 | GrapeJS has built-in trait manager |
| `ui/recent_templates.py` | 310 | Keep concept, reimplement simply |
| `ui/shortcuts.py` | 380 | GrapeJS has keymaps plugin |
| `ui/syntax_highlighter.py` | 370 | GrapeJS code editor handles this |
| `ui/template_converter.py` | ~200 | Will be completely rewritten |
| `ui/template_io.py` | 420 | Rewrite for new format |
| `ui/template_library.py` | 480 | BROKEN - reimplement |
| `ui/visual_builder.py` | ~300 | Replaced by GrapeJS |
| `ui/zoom_and_preview.py` | 380 | GrapeJS handles zoom |
| `ui/__init__.py` | ~20 | Recreate with new exports |

**Total UI files to delete**: 25 files (~7,500+ lines)

### Renderers (`renderers/` folder) - DELETE ALL
Will be replaced by new converter system:

| File | Reason |
|------|--------|
| `renderers/__init__.py` | Recreate |
| `renderers/base_renderer.py` | Replace with converter |
| `renderers/desktop_renderer.py` | Merge into single converter |
| `renderers/mobile_renderer.py` | Merge into single converter |

### Services (`services/` folder) - REFACTOR
| File | Action |
|------|--------|
| `services/__init__.py` | Keep, update exports |
| `services/container.py` | DELETE - over-engineered |
| `services/template_service.py` | REWRITE - simplify |

### Root Test Files - MOVE TO `tests/`
| File | Action |
|------|--------|
| `test_addon_init.py` | Move to `tests/` |
| `test_imports.py` | Move to `tests/` |
| `test_metaclass.py` | Move to `tests/` |
| `test_output.txt` | DELETE |
| `debug_init.py` | DELETE after migration |
| `final_verification.py` | DELETE after migration |
| `verify_syntax.py` | DELETE after migration |

### Documentation - ARCHIVE
| File | Action |
|------|--------|
| `FEATURE_STATUS.md` | Archive to `docs/archive/` |
| `INTEGRATION_GUIDE.md` | Archive, create new |
| `INTEGRATION_SUMMARY.md` | Archive |
| `docs/REORGANIZATION_COMPLETE.md` | Archive |

---

## Files to KEEP (With Modifications)

### Core Entry Points - KEEP & MODIFY
| File | Modifications Needed |
|------|---------------------|
| `__init__.py` | Update imports for new structure |
| `manifest.json` | Update version, description |
| `config.json` | Add GrapeJS settings |

### Utilities (`utils/` folder) - KEEP MOST
| File | Action | Reason |
|------|--------|--------|
| `utils/__init__.py` | Update exports | |
| `utils/security.py` | KEEP AS-IS | Excellent security validation |
| `utils/template_utils.py` | KEEP & EXTEND | Add GrapeJS JSON support |
| `utils/css_utils.py` | KEEP AS-IS | CSS utilities still needed |
| `utils/note_utils.py` | KEEP AS-IS | Anki note integration |
| `utils/logging_utils.py` | KEEP AS-IS | Logging still needed |
| `utils/exceptions.py` | KEEP & EXTEND | Add new exception types |
| `utils/performance.py` | KEEP AS-IS | Caching utilities |

### Configuration (`config/` folder) - KEEP & MODIFY
| File | Action |
|------|--------|
| `config/__init__.py` | Update exports |
| `config/constants.py` | Add GrapeJS constants |

### Examples - KEEP & UPDATE
| File | Action |
|------|--------|
| `examples/examples.py` | Update for new format |
| `examples/README.md` | Rewrite |

---

## New Files to CREATE

### Core Module (`core/`)
```
core/
├── __init__.py
├── template.py          # Template data model
├── component.py         # Component definitions
├── converter.py         # GrapeJS JSON <-> Anki HTML converter
└── validator.py         # Template validation
```

### GUI Module (`gui/`)
```
gui/
├── __init__.py
├── designer_dialog.py   # Main GrapeJS dialog
├── preview_panel.py     # Anki card preview
├── webview_bridge.py    # Python-JS communication
└── downloader.py        # GrapeJS asset downloader
```

### Web Assets (`web/`) - GITIGNORED DOWNLOADS
```
web/
├── .gitignore           # Ignore downloaded files
├── grapesjs/
│   ├── grapes.min.js    # Downloaded from unpkg
│   └── grapes.min.css   # Downloaded from unpkg
├── designer.html        # Main designer HTML
├── designer.js          # Custom GrapeJS config
├── designer.css         # Custom styling
├── blocks/              # Component block definitions
│   ├── layout.js
│   ├── navigation.js
│   ├── inputs.js
│   ├── buttons.js
│   ├── data.js
│   ├── feedback.js
│   ├── overlays.js
│   ├── search.js
│   ├── commerce.js
│   ├── social.js
│   ├── charts.js
│   ├── accessibility.js
│   ├── system.js
│   ├── motion.js
│   └── advanced.js
└── anki-api/            # AnkiJSApi integration
    └── behaviors.js
```

### Hooks Module (`hooks/`)
```
hooks/
├── __init__.py
├── menu.py              # Menu setup
└── webview.py           # Webview injection
```

---

## Migration Steps

### Phase 1: Backup and Archive
```bash
# Create archive branch
git checkout -b archive/pre-grapejs-rewrite
git push origin archive/pre-grapejs-rewrite

# Back to main
git checkout main
```

### Phase 2: Delete UI Files
```python
# Files to delete (run from project root)
import shutil
import os

files_to_delete = [
    "ui/android_studio_dialog.py",
    "ui/base_dialog.py",
    "ui/commands.py",
    "ui/component_search.py",
    "ui/component_tree.py",
    "ui/components.py",
    "ui/constraints.py",
    "ui/design_surface.py",
    "ui/designer_dialog.py",
    "ui/editor_widget.py",
    "ui/grid.py",
    "ui/layout_strategies.py",
    "ui/multi_selection.py",
    "ui/preview_widget.py",
    "ui/progress_indicators.py",
    "ui/properties_panel.py",
    "ui/recent_templates.py",
    "ui/shortcuts.py",
    "ui/syntax_highlighter.py",
    "ui/template_converter.py",
    "ui/template_io.py",
    "ui/template_library.py",
    "ui/visual_builder.py",
    "ui/zoom_and_preview.py",
]

for f in files_to_delete:
    if os.path.exists(f):
        os.remove(f)
        print(f"Deleted: {f}")
```

### Phase 3: Delete Renderers
```python
folders_to_delete = ["renderers"]
for folder in folders_to_delete:
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f"Deleted folder: {folder}")
```

### Phase 4: Move Test Files
```python
import os
import shutil

os.makedirs("tests/unit", exist_ok=True)

test_files = [
    ("test_addon_init.py", "tests/unit/test_addon_init.py"),
    ("test_imports.py", "tests/unit/test_imports.py"),
    ("test_metaclass.py", "tests/unit/test_metaclass.py"),
]

for src, dst in test_files:
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Moved: {src} -> {dst}")

# Delete temporary files
temp_files = ["test_output.txt", "debug_init.py", "final_verification.py", "verify_syntax.py"]
for f in temp_files:
    if os.path.exists(f):
        os.remove(f)
```

### Phase 5: Archive Old Docs
```python
import shutil
import os

os.makedirs("docs/archive/v0.1", exist_ok=True)

docs_to_archive = [
    "FEATURE_STATUS.md",
    "INTEGRATION_GUIDE.md", 
    "INTEGRATION_SUMMARY.md",
    "docs/REORGANIZATION_COMPLETE.md",
]

for doc in docs_to_archive:
    if os.path.exists(doc):
        filename = os.path.basename(doc)
        shutil.move(doc, f"docs/archive/v0.1/{filename}")
        print(f"Archived: {doc}")
```

### Phase 6: Create New Structure
```python
new_folders = [
    "core",
    "gui", 
    "hooks",
    "web",
    "web/grapesjs",
    "web/blocks",
    "web/anki-api",
]

for folder in new_folders:
    os.makedirs(folder, exist_ok=True)
    init_file = os.path.join(folder, "__init__.py")
    if folder.startswith("web"):
        continue  # No __init__.py for web folders
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write(f'"""{folder.replace("/", ".")} module"""\n')
```

---

## Validation Checklist

After cleanup, verify:

- [ ] `utils/security.py` exists and unchanged
- [ ] `utils/template_utils.py` exists
- [ ] `config/constants.py` exists
- [ ] `__init__.py` exists (entry point)
- [ ] `manifest.json` exists
- [ ] `ui/` folder is empty or contains only `__init__.py`
- [ ] `renderers/` folder is deleted
- [ ] Test files moved to `tests/unit/`
- [ ] New folders created: `core/`, `gui/`, `hooks/`, `web/`
- [ ] Git archive branch exists with old code

---

## Dependency Changes

### Remove from `requirements.txt`
None - all current dependencies still needed

### Add to `requirements.txt`
```
# Already have PyQt6/aqt - no new dependencies needed
# GrapeJS is downloaded at runtime, not a Python package
```

### Update `.gitignore`
```gitignore
# GrapeJS downloaded assets
web/grapesjs/grapes.min.js
web/grapesjs/grapes.min.css
web/grapesjs/*.js
web/grapesjs/*.css

# Keep the folder structure
!web/grapesjs/.gitkeep
```

---

## Summary

| Category | Files to Delete | Files to Keep | New Files |
|----------|----------------|---------------|-----------|
| UI | 25 | 0 | 4 |
| Renderers | 4 | 0 | 0 |
| Services | 1 | 2 | 0 |
| Utils | 0 | 8 | 0 |
| Core | 0 | 0 | 5 |
| Hooks | 0 | 0 | 3 |
| Web | 0 | 0 | 20+ |
| **Total** | **30** | **10** | **32+** |

**Net result**: Cleaner, more focused codebase using GrapeJS for the heavy lifting.

---

## Next Plan

See [02-ARCHITECTURE.md](02-ARCHITECTURE.md) for the new addon architecture with GrapeJS integration.
