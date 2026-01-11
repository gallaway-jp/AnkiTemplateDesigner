# Anki Testing Guide - Quick Reference

## Addon Installation Status
✅ **INSTALLED** - Addon copied to: `C:\Users\Colin\AppData\Roaming\Anki2\addons21\AnkiTemplateDesigner`

## Current Status
🚀 **Anki is starting** - Follow the steps below to test

---

## Quick Testing Steps

### 1️⃣ Verify Addon is Loaded (30 seconds)
```
✓ Open Anki (should be starting now)
✓ Go to: Tools > Add-ons
✓ Find "Anki Template Designer" in list
✓ Verify it's enabled (checked)
```

### 2️⃣ Open Designer Dialog (30 seconds)
```
✓ Click: Tools > Anki Template Designer
✓ Dialog opens (800x600 minimum)
✓ WebView component visible
```

### 3️⃣ Verify Editor Loads (1 minute)
```
✓ GrapeJS editor appears (not blank)
✓ Toolbar visible at top
✓ Blocks panel visible on left
✓ Canvas in center
✓ Properties panel on right
```

### 4️⃣ Check Block Categories (2 minutes)
Expand each category in blocks panel and count blocks:

- [ ] **Layout** - Should see ~25 blocks (Frame, Card, Grid, etc.)
- [ ] **Study Action Bar** - Should see 1 block
- [ ] **Inputs** - Should see ~13 blocks (Text Field, Checkbox, etc.)
- [ ] **Buttons** - Should see 5 blocks (Primary, Secondary, etc.)
- [ ] **Data** - Should see ~18 blocks (Heading, Paragraph, Table, etc.)
- [ ] **Feedback** - Should see ~14 blocks (Alert, Badge, Toast, etc.)
- [ ] **Overlays** - Should see 6 blocks (Modal, Drawer, etc.)
- [ ] **Animations** - Should see 3 blocks (Fade, Slide, etc.)
- [ ] **Accessibility** - Should see 5 blocks (SR-Only, etc.)
- [ ] **Anki Special** - Should see 3 blocks (Field, Cloze, Hint)

### 5️⃣ Test Drag & Drop (3 minutes)
```
✓ Drag "Frame" block to canvas → Should appear
✓ Drag "Heading" block into frame → Should nest inside
✓ Click heading → Should select (blue outline)
✓ Properties panel shows traits → Can edit
✓ Delete block (press Delete) → Should remove
```

### 6️⃣ Test Component Properties (2 minutes)
```
✓ Add "Text Field" block
✓ Select it
✓ Properties panel shows: required, pattern, minlength, maxlength
✓ Toggle "required" → Trait updates
```

### 7️⃣ Test Anki Special Blocks (2 minutes)
```
✓ Add "Anki Field" block
✓ Shows {{Front}} placeholder
✓ Properties show field dropdown
✓ Can select different field (if note type loaded)
```

---

## Run Automated Tests in Anki

Press **Shift+F1** in Anki to open Debug Console, then paste:

```python
import sys
from pathlib import Path
addon_dir = Path.home() / 'AppData/Roaming/Anki2/addons21/AnkiTemplateDesigner'
sys.path.insert(0, str(addon_dir))
exec(open(addon_dir / 'test_in_anki.py').read())
test_component_library()
```

Expected output: **5 tests passed**

---

## Expected Results Summary

| Test | Expected Result |
|------|----------------|
| Addon loads | ✓ Visible in Tools > Add-ons |
| Menu item | ✓ "Anki Template Designer" in Tools menu |
| Dialog opens | ✓ Large dialog (800x600+) |
| Editor loads | ✓ GrapeJS interface visible |
| Blocks visible | ✓ All 10 categories, ~93 blocks total |
| Drag & drop works | ✓ Can add blocks to canvas |
| Selection works | ✓ Click selects, shows blue outline |
| Properties work | ✓ Can modify component traits |
| Anki integration | ✓ Can access Anki fields |

---

## If Something Goes Wrong

**Addon not in list?**
```bash
# Reinstall
python install_addon.py install
# Then restart Anki
```

**Dialog doesn't open?**
- Check Anki console (Tools > Add-ons > View Files)
- Look for error messages
- Verify web/ directory exists in addon folder

**Editor blank/white screen?**
- Open browser dev tools (if available)
- Check for JavaScript errors
- Verify index.html exists: `C:\Users\Colin\AppData\Roaming\Anki2\addons21\AnkiTemplateDesigner\web\index.html`

**Blocks not appearing?**
- Check blocks/ directory exists
- Verify all 9 .js files present in blocks/
- Check browser console for module load errors

---

## Report Results

After testing, update [MANUAL-TEST-CHECKLIST.md](MANUAL-TEST-CHECKLIST.md) with:
- Which tests passed ✓
- Which tests failed ✗  
- Any errors encountered
- Screenshots (if issues found)

---

**Estimated Testing Time:** 10-15 minutes  
**Priority:** High (needed to verify component library works)  
**Status:** Ready to test (Anki should be running now)
