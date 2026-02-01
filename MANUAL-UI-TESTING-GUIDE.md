# Manual UI Testing Guide - Component System

**Objective**: Verify the component system implementation works correctly in GrapeJS editor  
**Status**: Ready to Test  
**Expected Blocks**: 23 total across 7 categories

---

## Test Environment Setup

### Prerequisites
- Anki installed and running
- Template Designer addon installed
- layout.js and anki-blocks.js files updated
- No build errors

### Start Testing
1. Open Anki application
2. Open any note type or deck
3. Open Template Designer dialog
4. Locate "Blocks" panel on the left sidebar

---

## Category & Block Verification

### ✓ Category 1: Anki Fields (6 blocks)

**Expected Blocks** (all should appear with distinctive styling):

| Block | Visual | Syntax | Purpose |
|-------|--------|--------|---------|
| Field | Blue bg | `{{FieldName}}` | Field reference |
| Cloze | Orange bg | `{{c1::answer}}` | Cloze deletion |
| Hint | Link style | `{{hint:FieldName}}` | Hint field |
| Type Answer | Gray box | `{{type:FieldName}}` | Type check |
| Conditional | Purple border | `{{#FrontSide}}...{{/FrontSide}}` | Conditional |
| Tags | Gray italic | `{{Tags}}` | Tags display |

**Test Steps**:
- [ ] Verify all 6 blocks appear
- [ ] Verify "Anki Fields" category label visible
- [ ] Field block has light blue (#e3f2fd) background
- [ ] Cloze block has light orange (#ffe0b2) background
- [ ] Hint block shows blue link styling
- [ ] Type Answer block shows gray bordered box
- [ ] Conditional block shows purple dashed border
- [ ] Tags block shows gray italic text

---

### ✓ Category 2: Layout & Structure (7 blocks)

**Expected Blocks**:
1. Section - semantic container
2. Panel - bordered container
3. Card - elevated container with shadow
4. Surface - light background container
5. Container - centered max-width wrapper
6. Padding Box - adds padding
7. Margin Box - adds margin
8. Anchor Link - page anchor/link

**Test Steps**:
- [ ] Verify all 7 blocks appear
- [ ] Section block has bottom border divider
- [ ] Panel block shows border and rounded corners
- [ ] Card block shows shadow elevation
- [ ] Surface block shows light gray background
- [ ] Container block is labeled "Container"
- [ ] Padding Box block is labeled "Padding Box"
- [ ] Margin Box block is labeled "Margin Box"
- [ ] Anchor Link shows link styling

---

### ✓ Category 3: Grid & Columns (4 blocks)

**Expected Blocks**:
1. Grid - 3-column layout
2. 2 Columns - 2-column row layout
3. 3 Columns - 3-column row layout
4. Flow Layout - auto-wrapping grid

**Test Steps**:
- [ ] Verify all 4 blocks appear
- [ ] Grid block shows 3-column default
- [ ] "2 Columns" block appears (not "Row2Col")
- [ ] "3 Columns" block appears (not "Row3Col")
- [ ] Flow Layout block shows wrapping grid style

---

### ✓ Category 4: Flexbox (3 blocks)

**Expected Blocks**:
1. H-Stack - horizontal flex layout
2. V-Stack - vertical flex layout
3. Center - centered flex layout

**Test Steps**:
- [ ] Verify all 3 blocks appear
- [ ] H-Stack block labeled "H-Stack"
- [ ] V-Stack block labeled "V-Stack"
- [ ] Center block labeled "Center"

---

### ✓ Category 5: Spacing (2 blocks)

**Expected Blocks**:
1. Spacer - vertical spacing element
2. Divider - horizontal separator line

**Test Steps**:
- [ ] Verify both blocks appear
- [ ] Spacer block is present
- [ ] Divider block is present

---

### ✓ Category 6 & 7: Text & Typography + Media (existing)

**Expected**: These categories should already exist from before  
**Test**: Verify these categories still appear unchanged

---

## Verify Removed Blocks (Should NOT appear)

| Block | Reason Removed |
|-------|----------------|
| Frame | Device mockup, not needed |
| Modal Container | Modals not supported by Anki |
| Drawer | Sidebar drawers not supported |
| Split View | Complex JS-dependent layout |
| Accordion | Requires JavaScript |
| Tab Container | Requires JavaScript |
| Stepper | Requires JavaScript |
| Masonry | Better alternatives available |
| Tabs Navigation | Requires JavaScript |

**Test Steps**:
- [ ] Search "Frame" - NOT FOUND ✓
- [ ] Search "Modal" - NOT FOUND ✓
- [ ] Search "Drawer" - NOT FOUND ✓
- [ ] Search "Split" - NOT FOUND ✓
- [ ] Search "Accordion" - NOT FOUND ✓
- [ ] Search "Tab" - NOT FOUND ✓ (except in text blocks if they exist)
- [ ] Search "Stepper" - NOT FOUND ✓
- [ ] Search "Masonry" - NOT FOUND ✓

---

## Drag & Drop Testing

### Test 1: Drag Anki Field Block

**Steps**:
1. Find "Field" block in "Anki Fields" category
2. Drag onto canvas
3. Observe styling (should show blue background with {{FieldName}} text)
4. Verify text is monospace font
5. Release mouse

**Expected Result**: Blue-styled field block appears on canvas

---

### Test 2: Drag Cloze Block

**Steps**:
1. Find "Cloze" block in "Anki Fields" category
2. Drag onto canvas
3. Observe styling (should show orange background)
4. Verify shows {{c1::answer}} text
5. Release mouse

**Expected Result**: Orange-styled cloze block appears on canvas

---

### Test 3: Drag Container Block

**Steps**:
1. Find "Container" block in "Layout & Structure" category
2. Drag onto canvas
3. Observe it creates a container element
4. Verify it shows "Container content" placeholder

**Expected Result**: Container block with centered max-width appears

---

### Test 4: Nest Anki Block in Container

**Steps**:
1. Have Container on canvas from Test 3
2. Drag "Field" block onto the container
3. Drop inside container

**Expected Result**: Field block nests inside container, blue styling visible

---

## Template Save/Load Testing

### Test 5: Save Template with Anki Blocks

**Steps**:
1. Create template with several blocks:
   - Container (outer)
   - Section (inside container)
   - Field block for {{Front}}
   - Card (inner section)
   - Cloze block for {{c1::answer}}
2. Click "Save Template" button
3. Verify no errors in console
4. Check browser DevTools (F12) for errors

**Expected Result**: Template saves without errors

---

### Test 6: Load Saved Template

**Steps**:
1. After saving, reload the template
2. Verify all blocks reappear
3. Verify styling preserved (blue field, orange cloze)
4. Verify nesting preserved

**Expected Result**: Template loads correctly with all blocks in place

---

## Preview & Export Testing

### Test 7: Preview in Anki

**Steps**:
1. Create template with blocks
2. Click "Preview" or "Export" button (depends on implementation)
3. View rendered template

**Expected Result**: Template renders correctly in Anki format

---

## Troubleshooting Checklist

### If Anki Fields Category Missing

**Possible Causes**:
1. anki-blocks.js not found
2. Import statement broken in layout.js
3. registerAnkiBlocks not called

**Fix**:
```javascript
// Check line 11 in layout.js
import { registerAnkiBlocks } from './anki-blocks.js';

// Check line 15 in layout.js
registerAnkiBlocks(editor);
```

### If Removed Blocks Still Appear

**Possible Causes**:
1. layout.js not saved properly
2. Browser cache not cleared
3. Old blocks registered elsewhere

**Fix**:
1. Verify layout.js has been updated (line 320 should be the end)
2. Hard refresh browser (Ctrl+Shift+R)
3. Search workspace for other block registrations

### If Anki Block Styling Missing

**Possible Causes**:
1. Inline styles not applied
2. GrapeJS not using full style object
3. CSS classes conflicting

**Fix**:
1. Check browser DevTools element inspector
2. Verify inline styles in anki-blocks.js exist
3. Look for console errors in DevTools

### If Blocks Don't Appear in Categories

**Possible Causes**:
1. Category strings don't match exactly
2. BlockManager not initialized
3. Register function not called

**Fix**:
1. Verify exact category strings in documentation match code:
   - "Anki Fields"
   - "Layout & Structure"
   - "Grid & Columns"
   - "Flexbox"
   - "Spacing"
2. Check editor.BlockManager is available
3. Verify registerLayoutBlocks called on page load

---

## Performance Testing

### Test Load Time

**Steps**:
1. Open Template Designer
2. Open DevTools Network tab
3. Refresh page
4. Measure time to blocks panel rendering

**Expected**: Blocks appear within 2-3 seconds

---

## Browser Compatibility

**Test Browsers**:
- [ ] Chrome/Chromium (should work)
- [ ] Firefox (verify grid/flexbox support)
- [ ] Safari (if macOS)
- [ ] Anki WebView (primary target)

---

## Final Checklist

Before declaring testing complete:

- [ ] All 23 blocks visible
- [ ] 7 categories organized correctly
- [ ] No removed blocks present
- [ ] Anki blocks have distinctive styling
- [ ] Can drag blocks onto canvas
- [ ] Can nest blocks
- [ ] Can save template with blocks
- [ ] Can load saved template
- [ ] No console errors (F12)
- [ ] Can preview in Anki format
- [ ] No performance issues

---

## Test Results Log

**Tester**: _______________  
**Date**: _______________  
**Browser**: _______________  
**Anki Version**: _______________  

### Results Summary

| Test | Status | Notes |
|------|--------|-------|
| Anki Fields (6 blocks) | ✓ / ✗ / ? | |
| Layout & Structure (7 blocks) | ✓ / ✗ / ? | |
| Grid & Columns (4 blocks) | ✓ / ✗ / ? | |
| Flexbox (3 blocks) | ✓ / ✗ / ? | |
| Spacing (2 blocks) | ✓ / ✗ / ? | |
| Removed blocks absent | ✓ / ✗ / ? | |
| Drag & drop working | ✓ / ✗ / ? | |
| Save/Load working | ✓ / ✗ / ? | |
| Styling correct | ✓ / ✗ / ? | |
| No console errors | ✓ / ✗ / ? | |

### Issues Found

(List any issues discovered during testing)

1. ...
2. ...
3. ...

### Recommendations

(List any recommendations for improvement)

1. ...
2. ...
3. ...

---

## Next Steps After Testing

If all tests pass:
1. Proceed to Phase 2: Property Editors
2. Implement field name customization
3. Add cloze number selector
4. Create conditional block editor

If issues found:
1. Document issue details
2. Check troubleshooting guide
3. Fix code issues
4. Re-run relevant tests

---

**Testing Complete**: __________  
**Status**: ⚠ PENDING / ✓ PASSED / ✗ FAILED
