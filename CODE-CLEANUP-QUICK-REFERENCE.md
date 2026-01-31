# Quick Reference: Code Cleanup Issues

## 🔴 CRITICAL ISSUES (Blocks Execution)

### Missing `ui/` Module
- **Impact:** 22+ test files fail
- **Missing Files:** 13 submodules needed
  ```
  ui/components.py (PRIMARY - 8 imports)
  ui/template_converter.py (6 imports)
  ui/constraints.py (4 imports)
  ui/layout_strategies.py
  ui/multi_selection.py
  ui/template_library.py
  ui/grid.py
  ui/commands.py
  ui/template_io.py
  ui/android_studio_dialog.py
  ui/design_surface.py
  ui/component_tree.py
  ui/properties_panel.py
  ```

### Missing `renderers/` Module
- **Impact:** 1 test file fails (test_renderers.py)
- **Missing Files:** 3 submodules
  ```
  renderers/base_renderer.py
  renderers/desktop_renderer.py
  renderers/ankidroid_renderer.py
  ```

---

## 🟠 HIGH PRIORITY (Organization)

### Duplicate Test Files in Root
**Move to organized structure:**
```
test_anki_integration.py              → tests/unit/
test_backup_manager.py                → tests/ (consolidate with existing)
test_component_library.py             → tests/unit/
test_component_search.py              → tests/unit/
test_dlp.py                          → tests/unit/
test_in_anki.py                      → tests/unit/
test_projects.py                     → tests/ (consolidate with existing)
test_template_validation.py          → tests/unit/
```

---

## 🟡 MEDIUM PRIORITY (Unused Code)

### Unused Fixture
- `tests/fixtures/sample_data.py` - 141 lines, 0 imports anywhere

### Potentially Unused Utilities
- `utils/note_utils.py` - No imports found
- `utils/template_utils.py` - Exported but possibly unused

---

## ✅ VERIFIED WORKING

### All Services (24 total)
✓ Every service module has tests and is actively imported

### Core Infrastructure
✓ config/, core/, gui/, hooks/, examples/, utils/ (mostly)

### External Dependencies
✓ PyQt6, pytest, aqt (Anki) - all properly available

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Critical broken imports | 25 |
| Files with broken imports | 18 |
| Duplicate/orphaned root test files | 8 |
| Missing module directories | 2 |
| Missing UI submodules | 13 |
| Missing renderer submodules | 3 |
| Unused fixtures | 1 |
| All services (✓ used) | 24 |
| Potentially unused utilities | 2 |

---

## Action Items (Priority Order)

### Immediate
- [ ] Review full analysis in `UNUSED-AND-BROKEN-CODE-ANALYSIS.md`
- [ ] Create or stub missing `ui/` submodules
- [ ] Create or stub missing `renderers/` submodules

### Short-term
- [ ] Consolidate duplicate test files
- [ ] Move root test files to tests/ hierarchy
- [ ] Remove or document `tests/fixtures/sample_data.py`

### Long-term
- [ ] Verify/remove unused utilities
- [ ] Establish test organization standards
- [ ] Implement full UI module functionality

---

## Files Ready for Review
- **Full Report:** `UNUSED-AND-BROKEN-CODE-ANALYSIS.md` (12 sections, 400+ lines)
- **This Summary:** `CODE-CLEANUP-QUICK-REFERENCE.md`
