# Plan 05: Testing Instructions

## Quick Start

### For Testing in Anki (UI Validation)

1. **Close Anki completely** if it's running
   ```
   Close Anki window completely (not minimized)
   ```

2. **Restart Anki 25.07.5**
   ```
   Launch Anki normally
   ```

3. **Open Template Designer**
   ```
   Click Tools menu → "Template Designer"
   OR press Ctrl+Shift+T
   ```

4. **Verify the 3-Panel Layout**
   - **Top**: Dark header with "Anki Template Designer" title
     - Should show status "Connected" 
     - Version should show "v2.0.0"
   
   - **Second row**: Gray toolbar with 8 buttons
     - Group 1: "New", "Open", "Save" (Save in blue)
     - Group 2: "Undo", "Redo"
     - Group 3: "Preview", "Export"
     - Small "?" button on right
   
   - **Main area split into 3 panels**:
     - **LEFT (240px)**: White sidebar titled "Components"
       - Section: Layout (Container, Row, Column)
       - Section: Text (Text, Heading)
       - Section: Anki Fields (Field, Cloze)
       - Section: Media (Image, Audio)
     
     - **CENTER**: Gray canvas area with white editor box
       - Shows message "Drag components here to start building"
       - Document icon in center
     
     - **RIGHT (280px)**: White panel titled "Properties"
       - Shows "Select a component to edit"
   
   - **Bottom**: Light gray status bar
     - Left shows "Ready"
     - Right shows "v2.0.0"

5. **Test Interactions**
   
   **Test Toolbar Buttons**:
   - Click "New" → status bar left should change to "New"
   - Click "Save" → status bar left should change to "Saved"
   - Click "Undo" → status bar left should change to "Undo"
   - Click "Help" → status bar left should change to "Help"
   
   **Test Drag-Drop**:
   - Click and drag "Container" from sidebar to canvas
   - Canvas border should turn blue while dragging
   - When dropped, should show message in canvas:
     ```
     Component "container" added.
     Full implementation in later steps.
     ```
   - Status bar should show "Added: container"
   - Try dragging other components (Text, Field, Image, etc.)

6. **Check Console** (Optional - for developers)
   - Open browser DevTools: F12
   - Console tab should show no errors
   - Should see messages like "UI shell loaded"

### For Running Tests (With Anki Closed)

1. **Close Anki completely** (must not be running)

2. **Run all UI tests**:
   ```powershell
   cd d:\Development\Python\AnkiTemplateDesigner
   python -m pytest tests/ui/ -v
   ```

3. **Run specific test**:
   ```powershell
   python -m pytest tests/ui/test_designer_dialog_ui.py::TestDesignerDialogUI::test_dialog_creation -v
   ```

4. **If tests hang**:
   - You probably still have Anki running
   - Close Anki completely
   - Ctrl+C to stop pytest
   - Run again

## Expected Results

### Visual Checklist
- [ ] Header with gradient blue background
- [ ] "Anki Template Designer" title visible
- [ ] "Connected" status badge visible
- [ ] Version "v2.0.0" in header right
- [ ] Gray toolbar with buttons visible
- [ ] Sidebar with "Components" header
- [ ] 4 component sections visible
- [ ] Central canvas area visible
- [ ] Properties panel on right
- [ ] Status bar at bottom
- [ ] All text readable and properly formatted

### Functional Checklist
- [ ] Dialog opens without errors
- [ ] No console errors (F12)
- [ ] Status bar updates when buttons clicked
- [ ] Toolbar buttons are clickable
- [ ] Components can be dragged from sidebar
- [ ] Canvas shows visual feedback (blue border) on drag
- [ ] Components can be dropped on canvas
- [ ] Canvas message updates after drop
- [ ] Status bar shows drop action

## Troubleshooting

### UI not showing / Still seeing old interface
- Make sure Anki is completely closed
- Restart Anki
- Clear Anki cache: `%APPDATA%\Anki2\cache/` (optional)
- Try opening Template Designer again

### Tests hanging/frozen
- Close Anki completely
- Press Ctrl+C to stop pytest
- Verify Anki is not running (TaskManager)
- Run tests again

### Toolbar buttons don't update status
- Refresh page: F5 in QWebEngine (Ctrl+R)
- Close and reopen Template Designer
- Check browser console (F12) for errors

### Drag-drop not working
- Try single component first (Container)
- Make sure mouse fully over canvas area before releasing
- Check console (F12) for drag-drop errors

## Success Criteria

Plan 05 is **COMPLETE** when:
1. ✅ Dialog opens without errors
2. ✅ All 3 panels visible (sidebar, canvas, properties)
3. ✅ All UI elements visible (header, toolbar, status bar)
4. ✅ Components list shows 4 sections with 8 items
5. ✅ Toolbar buttons are clickable and update status
6. ✅ Drag-drop works (can drag component and drop on canvas)
7. ✅ No console errors
8. ✅ Tests pass (with Anki closed)

## Notes

- Bridge version shows "v2.0.0" - this is from Python backend
- Loading overlay should disappear after page loads (within 1-2 seconds)
- All icons are Unicode emoji (no images needed)
- Canvas starts empty with placeholder message
- Plan 06 will add actual component rendering when user confirms this works

---

**Questions or Issues?** Check [PLAN-05-ISSUE-RESOLUTION.md](PLAN-05-ISSUE-RESOLUTION.md) for details on the HTML deployment fix.
