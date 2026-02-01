# Front/Back Tab Interface Implementation - Summary

## What Was Implemented

### 1. UI Components
- **Side Tabs Bar** - New UI section with three tabs:
  - 📄 **Front** - Edit front side (question/prompt)
  - 📄 **Back** - Edit back side (answer)
  - 👁 **Preview** - View both sides together (placeholder for future)
- **Side Info Display** - Shows current active side and mode
- **Visual Feedback** - Active tab highlighted with blue border and shadow

### 2. State Management
Created per-template, per-side state tracking:
```javascript
templateSideState = {
  [templateId]: {
    front: {
      components: [],           // Component tree for front
      selectedComponent: null,  // Currently selected component
      history: [],             // Undo/redo history
      historyIndex: -1
    },
    back: {
      components: [],
      selectedComponent: null,
      history: [],
      historyIndex: -1
    }
  }
}
```

### 3. Core Functions
- **`initializeSideState(templateId)`** - Create state object for a template
- **`saveSideState()`** - Save current side's components and selection
- **`loadSideState()`** - Load components and selection for a side
- **`switchSide(side)`** - Switch between front/back/preview
- **`updateSideTabUI()`** - Update which tab appears active
- **`updateSideInfo()`** - Update the side information display

### 4. Workflow
When user clicks a tab:
1. **Save** current side's state (components, selection, history)
2. **Update** currentSide variable
3. **Load** new side's state into canvas
4. **Refresh** UI (tabs, info text)

When user switches templates:
1. **Initialize** side state for new template
2. **Reset** to front side automatically
3. **Load** front side components
4. **Update** all UI elements

## CSS Styling

Added comprehensive tab bar styling:
- **Tab buttons** - Clean, minimal design with hover states
- **Active state** - Blue bottom border and shadow effect
- **Side info** - Right-aligned, italicized helper text
- **Responsive** - Wraps on smaller screens

## Integration Points

### Template Selection
- When user selects a template, automatically initialize side state
- Reset to "front" side to avoid confusion
- Update tab UI and info display

### Canvas Module
The implementation expects these optional methods on `window.designCanvas`:
- `getComponents()` - Return current component tree
- `setComponents(components)` - Load component tree
- `getSelected()` - Return selected component
- `selectComponent(component)` - Select a component

**Note:** If these methods don't exist yet, the tab switching will still work but won't preserve component state. This can be implemented later.

### Future Enhancements
1. **Keyboard Shortcuts**
   - `Ctrl+1` - Switch to front
   - `Ctrl+2` - Switch to back
   - `Ctrl+3` - Switch to preview

2. **Preview Mode**
   - Show both front and back simultaneously
   - Split view or stacked view
   - Interactive preview with "Show Answer" button

3. **{{FrontSide}} Component**
   - Special component only available in back template
   - Automatically includes front template content
   - Visual indicator that back depends on front

4. **Per-Side Validation**
   - Warn if front template is empty
   - Warn if back template doesn't reference {{FrontSide}}
   - Suggest template structure best practices

5. **CSS Management**
   - Decide: Share CSS between front/back or separate?
   - Currently assumed shared (one CSS editor)
   - Could extend to per-side CSS if needed

## Files Modified

### HTML
- **`index.html`** - Added side-tabs section with three buttons and info display

### CSS
- **`designer.css`** - Added `.side-tabs`, `.side-tab`, `.side-info` styles and tab bar layout

### JavaScript
- **`app.js`**
  - Added state variables: `currentSide`, `templateSideState`
  - Added functions: `initializeSideState()`, `saveSideState()`, `loadSideState()`
  - Added functions: `switchSide()`, `updateSideTabUI()`, `updateSideInfo()`
  - Added function: `initializeSideTabs()`
  - Updated `loadTemplate()` to initialize side state
  - Updated `initializeApp()` to call `initializeSideTabs()`

## Testing Checklist

- [ ] Restart Anki and load Template Designer
- [ ] Select a template from dropdown
- [ ] Verify Front tab is active by default
- [ ] Click Back tab - verify UI updates and shows "Back Side (Answer)"
- [ ] Click Front tab again - verify UI updates
- [ ] Select a different template - verify Front tab is active
- [ ] Open browser console - check for no JavaScript errors
- [ ] Verify tab highlighting works correctly (blue border on active)
- [ ] Verify side info text updates

## Known Limitations

1. **Component Persistence** - Currently stores reference to components, but actual canvas integration depends on canvas module implementation
2. **Preview Mode** - Tab exists but doesn't do anything yet (placeholder for future)
3. **Keyboard Shortcuts** - Not yet implemented for side switching
4. **History Management** - State structure includes history arrays, but actual undo/redo per side not yet implemented

## Notes

- The implementation is **non-breaking** - doesn't interfere with existing functionality
- Tab state is **per-template** - each template remembers which side you were on
- Tabs **reset to front** when loading a new template (prevents confusion)
- UI is **responsive** - tabs wrap on smaller screens
- Code is **well-commented** - easy to understand and extend

## Next Steps

1. **Test in Anki** - Verify tabs appear and switch correctly
2. **Implement Canvas Integration** - Connect to actual component management if needed
3. **Add Preview Mode** - Show both sides with split view or stacked layout
4. **Add {{FrontSide}} Component** - Special component for back template
5. **Add Keyboard Shortcuts** - Ctrl+1/2/3 for switching sides
