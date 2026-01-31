# Broken Imports - Detailed Line-by-Line Reference

## Files Importing from Missing `ui/` Module

### tests/unit/ Directory

#### test_layout_strategies.py
```python
Line 8:   from ui.layout_strategies import (
Line 13:  from ui.components import Component, ComponentType
```

#### test_multi_selection.py
```python
Line 6:   from ui.multi_selection import SelectionManager, SelectionMode, BulkOperations
Line 7:   from ui.components import TextFieldComponent, ImageFieldComponent
```

#### test_template_library.py
```python
Line 6:   from ui.template_library import TemplateLibrary
Line 7:   from ui.components import ComponentType
```

#### test_grid.py
```python
Line 8:   from ui.grid import Grid, GridSettings, SnapHelper
```

#### test_constraints.py
```python
Line 12:  from ui.constraints import (
Line 16:  from ui.components import Component
```

#### test_components.py
```python
Line 10:  from ui.components import (
```

#### test_commands.py
```python
Line 6:   from ui.commands import (
Line 11:  from ui.components import Component, TextFieldComponent, ComponentType
```

#### test_renderers.py
```python
Line 7:   from renderers.base_renderer import BaseRenderer
Line 8:   from renderers.desktop_renderer import DesktopRenderer
Line 9:   from renderers.ankidroid_renderer import AnkiDroidRenderer
```

---

### testsuite/unit/ Directory

#### test_template_io.py
```python
Line 9:   from ui.template_io import TemplateExporter, TemplateImporter, TemplateSharing
Line 10:  from ui.components import TextFieldComponent, ImageFieldComponent
```

#### test_template_converter.py
```python
Line 11:  from ui.template_converter import TemplateConverter
Line 17:  from ui.components import TextFieldComponent, ImageFieldComponent, HeadingComponent, ContainerComponent
```

#### test_security.py
```python
Line 7:   from ui.template_converter import TemplateConverter, sanitize_html, sanitize_css, validate_field_name
Line 8:   from ui.components import TextFieldComponent, ImageFieldComponent, HeadingComponent
```

#### test_performance.py
```python
Line 13:  from ui.template_converter import TemplateConverter, sanitize_html, sanitize_css
Line 14:  from ui.components import TextFieldComponent, ImageFieldComponent, HeadingComponent, DividerComponent
```

---

### testsuite/ Base Directory

#### test_utils.py
```python
Line 5:   from ui.components import Component
Line 6:   from ui.constraints import Constraint, ConstraintType, ConstraintTarget
```

#### test_android_studio_dialog.py
```python
Line 8:   from ui.android_studio_dialog import AndroidStudioDesignerDialog
```

#### test_android_studio_dialog_expanded.py
```python
Line 7:   from ui.android_studio_dialog import AndroidStudioDesignerDialog
```

---

### testsuite/integration/ Directory

#### test_ui_integration.py
```python
Line 13:  from ui.components import (
          TextFieldComponent, ImageFieldComponent, HeadingComponent, 
          ContainerComponent, DividerComponent
          )
Line 17:  from ui.design_surface import DesignSurface
Line 18:  from ui.component_tree import ComponentTree
Line 19:  from ui.properties_panel import PropertiesPanel
```

#### test_e2e_workflows.py
```python
Line 11:  from ui.components import (
          TextFieldComponent, ImageFieldComponent, HeadingComponent, 
          ContainerComponent
          )
Line 15:  from ui.template_converter import TemplateConverter
Line 20:  from ui.constraints import ConstraintHelper, ConstraintSet, Constraint, ConstraintTarget, ConstraintType
```

---

### services/ Directory (Non-test, Still Broken)

#### template_service.py
```python
Line 13:  from ui.template_converter import TemplateConverter
Line 14:  from ui.components import Component
```

---

## Missing Submodules by Frequency

### By Import Count
```
ui.components           - 8 files (primary bottleneck)
ui.template_converter   - 5 files
ui.constraints          - 3 files
ui.android_studio_dialog - 2 files
ui.layout_strategies    - 1 file
ui.multi_selection      - 1 file
ui.template_library     - 1 file
ui.grid                 - 1 file
ui.commands             - 1 file
ui.template_io          - 1 file
ui.design_surface       - 1 file
ui.component_tree       - 1 file
ui.properties_panel     - 1 file
renderers.base_renderer - 1 file
renderers.desktop_renderer - 1 file
renderers.ankidroid_renderer - 1 file
```

---

## Import Resolution Strategy

### Priority 1: Create Core UI Components Module
```python
# ui/components.py
# This single file blocks 8 test files
# Must export:
- Component
- TextFieldComponent
- ImageFieldComponent
- HeadingComponent
- ContainerComponent
- DividerComponent
- ComponentType
```

### Priority 2: Create Template Converter Module
```python
# ui/template_converter.py
# Must export:
- TemplateConverter
- sanitize_html
- sanitize_css
- validate_field_name
```

### Priority 3: Create Constraints Module
```python
# ui/constraints.py
# Must export:
- Constraint
- ConstraintType
- ConstraintTarget
- ConstraintHelper
- ConstraintSet
```

### Priority 4: Create Design Surface Modules
```python
# ui/android_studio_dialog.py
- AndroidStudioDesignerDialog

# ui/design_surface.py
- DesignSurface

# ui/component_tree.py
- ComponentTree

# ui/properties_panel.py
- PropertiesPanel
```

### Priority 5: Create Layout & Selection Modules
```python
# ui/layout_strategies.py
- Grid layout strategies

# ui/multi_selection.py
- SelectionManager
- SelectionMode
- BulkOperations

# ui/template_library.py
- TemplateLibrary

# ui/grid.py
- Grid
- GridSettings
- SnapHelper

# ui/commands.py
- Command classes/functions

# ui/template_io.py
- TemplateExporter
- TemplateImporter
- TemplateSharing
```

### Priority 6: Create Renderers Module
```python
# renderers/base_renderer.py
- BaseRenderer

# renderers/desktop_renderer.py
- DesktopRenderer

# renderers/ankidroid_renderer.py
- AnkiDroidRenderer
```

---

## Impact Analysis

### If Not Fixed
```
Critical Test Failures:
- 22 test files cannot import
- test_renderers.py fails
- services/template_service.py fails to load
- Any code importing template_service.py fails

Impact:
- Full test suite cannot run
- UI functionality unavailable
- Renderer functionality unavailable
- Template service unavailable
```

### If Fixed (All Modules Created)
```
Test Suite Status: 100% importable
- 22 test files can import successfully
- 1 renderer test file can import successfully
- Services module fully functional
- All modules can be imported without errors
```

---

## Debugging Notes

### How to Check Import Status
```bash
# Check if ui module exists
python -c "import ui.components"  # FAILS currently
python -c "from ui import components"  # FAILS currently

# Check what's in ui/
ls -la ui/  # Shows: __init__.py, __pycache__/

# Check renderers
ls -la renderers/  # DOES NOT EXIST
```

### How to Verify Fixes
```bash
# After creating modules:
python -c "from ui.components import Component"  # Should work
python -c "from renderers.base_renderer import BaseRenderer"  # Should work
pytest tests/unit/test_components.py -v  # Should run
```

---

## File Creation Checklist

### ui/ Module Files to Create
- [ ] `ui/components.py`
- [ ] `ui/template_converter.py`
- [ ] `ui/constraints.py`
- [ ] `ui/layout_strategies.py`
- [ ] `ui/multi_selection.py`
- [ ] `ui/template_library.py`
- [ ] `ui/grid.py`
- [ ] `ui/commands.py`
- [ ] `ui/template_io.py`
- [ ] `ui/android_studio_dialog.py`
- [ ] `ui/design_surface.py`
- [ ] `ui/component_tree.py`
- [ ] `ui/properties_panel.py`

### renderers/ Module Files to Create
- [ ] `renderers/__init__.py`
- [ ] `renderers/base_renderer.py`
- [ ] `renderers/desktop_renderer.py`
- [ ] `renderers/ankidroid_renderer.py`

---

**Last Updated:** January 24, 2026  
**Status:** Analysis Complete  
**Action Required:** Create missing modules to unblock test suite
