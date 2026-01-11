"""
Manual Testing Checklist for Anki Template Designer

This checklist should be completed by testing in the actual Anki environment.
Run through these steps after starting Anki.

PREREQUISITES:
- Anki installed at: C:\Users\Colin\AppData\Local\Programs\Anki
- Addon installed in Anki's addon directory
- Anki closed before starting

===============================================================================
MANUAL TEST CHECKLIST
===============================================================================

## 1. Addon Installation ⏳

[ ] 1.1. Start Anki
[ ] 1.2. Check Tools menu for "Anki Template Designer" option
[ ] 1.3. Verify no errors in Anki console (Tools > Add-ons > View Files)

## 2. Designer Dialog Launch ⏳

[ ] 2.1. Click Tools > Anki Template Designer
[ ] 2.2. Dialog opens without errors
[ ] 2.3. Dialog has title "Anki Template Designer"
[ ] 2.4. Dialog size is at least 800x600
[ ] 2.5. Dialog is centered on screen

## 3. Editor Loading ⏳

[ ] 3.1. WebView component visible in dialog
[ ] 3.2. GrapeJS editor loads (no white screen)
[ ] 3.3. Editor toolbar visible at top
[ ] 3.4. Blocks panel visible on left
[ ] 3.5. No JavaScript errors in console

## 4. Component Blocks Visible ⏳

### Layout Category
[ ] 4.1. "Layout" category visible in blocks panel
[ ] 4.2. Can see blocks: Frame, Section, Card, Grid, H-Stack, V-Stack
[ ] 4.3. Block icons and labels display correctly

### Study Action Bar Category
[ ] 4.4. "Study Action Bar" category visible
[ ] 4.5. Study Action Bar block available

### Input Category
[ ] 4.6. "Inputs" category visible
[ ] 4.7. Can see blocks: Text Field, Text Area, Checkbox, Dropdown

### Button Category
[ ] 4.8. "Buttons" category visible
[ ] 4.9. Can see blocks: Primary Button, Secondary Button, Icon Button

### Data Category
[ ] 4.10. "Data" category visible
[ ] 4.11. Can see blocks: Heading, Paragraph, List, Table, Image

### Feedback Category
[ ] 4.12. "Feedback" category visible
[ ] 4.13. Can see blocks: Alert, Badge, Progress Bar, Tooltip

### Overlays Category
[ ] 4.14. "Overlays" category visible
[ ] 4.15. Can see blocks: Modal, Drawer, Popover

### Animations Category
[ ] 4.16. "Animations" category visible
[ ] 4.17. Can see blocks: Fade Container, Slide Container

### Accessibility Category
[ ] 4.18. "Accessibility" category visible
[ ] 4.19. Can see blocks: Screen Reader Only, Accessible Field

### Anki Special Category
[ ] 4.20. "Anki Special" category visible
[ ] 4.21. Can see blocks: Anki Field, Anki Cloze, Anki Hint

## 5. Drag and Drop Functionality ⏳

[ ] 5.1. Drag "Frame" block to canvas
[ ] 5.2. Frame appears in canvas
[ ] 5.3. Frame can be selected (blue outline)
[ ] 5.4. Frame can be resized
[ ] 5.5. Drag "Heading" block into frame
[ ] 5.6. Heading appears inside frame
[ ] 5.7. Heading text is editable (click to edit)
[ ] 5.8. Can drag "Paragraph" block next to heading
[ ] 5.9. Can rearrange blocks by dragging
[ ] 5.10. Can delete blocks (select and press Delete key)

## 6. Component Properties/Traits ⏳

[ ] 6.1. Select a block in canvas
[ ] 6.2. Properties panel visible on right
[ ] 6.3. Component traits shown in properties panel
[ ] 6.4. Can modify text content
[ ] 6.5. Can change styles (color, font, etc.)
[ ] 6.6. Changes reflect immediately in canvas

### Anki Field Traits
[ ] 6.7. Add Anki Field block to canvas
[ ] 6.8. Select Anki Field block
[ ] 6.9. Traits panel shows "Field" dropdown
[ ] 6.10. Can select different Anki fields (if note type loaded)

### Input Validation Traits
[ ] 6.11. Add Text Field block
[ ] 6.12. Select Text Field
[ ] 6.13. Traits show: required, pattern, minlength, maxlength
[ ] 6.14. Can toggle "required" checkbox
[ ] 6.15. Can enter pattern validation regex

## 7. Editor Toolbar Functions ⏳

[ ] 7.1. View Code button works (shows HTML)
[ ] 7.2. Preview button works (shows preview mode)
[ ] 7.3. Undo button works (Ctrl+Z)
[ ] 7.4. Redo button works (Ctrl+Y)
[ ] 7.5. Clear canvas button works (removes all blocks)

## 8. Save/Load Functionality ⏳

[ ] 8.1. Create a simple template (Frame + Heading + Paragraph)
[ ] 8.2. Click Save button
[ ] 8.3. Template saves without errors
[ ] 8.4. Close dialog
[ ] 8.5. Reopen designer
[ ] 8.6. Click Load button
[ ] 8.7. Saved template appears in list
[ ] 8.8. Click template to load
[ ] 8.9. Template loads correctly in canvas

## 9. Export Functionality ⏳

[ ] 9.1. Create/load a template
[ ] 9.2. Click Export button
[ ] 9.3. HTML export works
[ ] 9.4. CSS export works
[ ] 9.5. Exported code is valid

## 10. Performance ⏳

[ ] 10.1. Dialog opens in <2 seconds
[ ] 10.2. Editor loads in <3 seconds
[ ] 10.3. Blocks drag smoothly (no lag)
[ ] 10.4. No memory leaks (can open/close multiple times)
[ ] 10.5. Can add 20+ blocks without slowdown

## 11. Error Handling ⏳

[ ] 11.1. Invalid HTML doesn't crash editor
[ ] 11.2. Invalid CSS doesn't crash editor
[ ] 11.3. Network errors handled gracefully
[ ] 11.4. No uncaught JavaScript exceptions

## 12. Responsive Design ⏳

[ ] 12.1. Dialog can be resized
[ ] 12.2. Canvas adapts to window size
[ ] 12.3. Panels remain usable when window is small
[ ] 12.4. Can enter fullscreen mode

## 13. Keyboard Shortcuts ⏳

[ ] 13.1. Ctrl+Z undos last action
[ ] 13.2. Ctrl+Y redos action
[ ] 13.3. Delete key removes selected block
[ ] 13.4. Escape key deselects block
[ ] 13.5. Ctrl+C copies block
[ ] 13.6. Ctrl+V pastes block

## 14. Integration with Anki ⏳

[ ] 14.1. Can access Anki note types
[ ] 14.2. Can access Anki fields from current note type
[ ] 14.3. Template can be applied to note type
[ ] 14.4. Changes sync with Anki card templates

## 15. Special Blocks Testing ⏳

### Anki Field Block
[ ] 15.1. Drag Anki Field to canvas
[ ] 15.2. Shows placeholder {{Front}}
[ ] 15.3. Can select different field from dropdown
[ ] 15.4. Field name updates in canvas

### Anki Cloze Block
[ ] 15.5. Drag Anki Cloze to canvas
[ ] 15.6. Shows cloze syntax {{c1::text}}
[ ] 15.7. Can edit cloze number

### Study Action Bar
[ ] 15.8. Drag Study Action Bar to canvas
[ ] 15.9. Shows default buttons (Show Answer, Mark, Flag)
[ ] 15.10. Can configure button placement
[ ] 15.11. Responsive design works (mobile view)

## 16. Complex Template Testing ⏳

[ ] 16.1. Create complex nested structure:
         - Frame
           - Grid (2 columns)
             - Column 1: Heading + Paragraph + Image
             - Column 2: Anki Field + Button
[ ] 16.2. All nesting works correctly
[ ] 16.3. Can select nested elements
[ ] 16.4. Can rearrange nested elements
[ ] 16.5. Save and reload preserves structure

## 17. Browser Compatibility ⏳

[ ] 17.1. Works in Anki's WebView (Qt WebEngine)
[ ] 17.2. All JavaScript features work
[ ] 17.3. All CSS features render correctly
[ ] 17.4. No browser-specific errors

===============================================================================
RESULTS SUMMARY
===============================================================================

Total Tests: 94
Passed: ___
Failed: ___
Skipped: ___

Issues Found:
1. _______________________________________________________________
2. _______________________________________________________________
3. _______________________________________________________________

Performance Notes:
- Dialog open time: _____ seconds
- Editor load time: _____ seconds
- Average drag latency: _____ ms

System Info:
- Anki Version: _________________
- OS: Windows ___
- Python Version: _______________
- Qt Version: ___________________

Tested By: _____________________
Date: __________________________
Time Spent: ____________________

===============================================================================
NEXT STEPS
===============================================================================

If all tests pass:
[ ] Mark addon as ready for beta testing
[ ] Create user documentation
[ ] Create tutorial video
[ ] Prepare for release

If tests fail:
[ ] Document all issues in GitHub issues
[ ] Prioritize critical bugs
[ ] Fix and retest
[ ] Update this checklist

===============================================================================
