# UI Features Quick-Start Guide

Welcome to the enhanced Anki Template Designer! This guide walks you through the new features we've implemented.

---

## The 3-Panel Editor Layout

The editor is now organized into three resizable panels:

```
┌─────────────────────────────────────────────────────────────────┐
│ Anki Template Designer │ ↶ ↷ │ 💾 Save │ 👁 Preview │ ⚙️ Settings │
├──────────┬────────────────────────────────────┬─────────────────┤
│          │                                    │                 │
│ Blocks   │  Canvas Area                       │  Properties     │
│ (Layers) │  (Drag blocks here)               │  (Edit props)   │
│          │                                    │                 │
│          │                                    │                 │
└──────────┴────────────────────────────────────┴─────────────────┘
```

### Left Panel - Blocks (Component Hierarchy)
- Shows all available components organized by category
- Drag-and-drop blocks onto the canvas
- Search and filter components
- Expand/collapse categories

### Center Panel - Canvas
- Visual editing area where you design your template
- Drag blocks from the left panel to create layout
- Click to select blocks
- Use keyboard shortcuts for editing

### Right Panel - Properties
- Edit properties of the selected block
- Change styles with CSS
- Configure constraints and layout
- View advanced block information

---

## Creating Your First Template

### Step 1: Add Components
1. Find a component in the left panel (e.g., "Container")
2. Drag it onto the center canvas area
3. A notification will confirm it was added
4. The block appears on canvas with a blue dashed border

### Step 2: Select & Edit
1. Click the block on the canvas to select it
2. The block will highlight with a green glowing border
3. The right panel shows its properties
4. Edit properties, styles, or constraints
5. Changes apply immediately to the canvas

### Step 3: Delete or Duplicate
- **Delete**: Select a block and press Delete
- **Duplicate**: Select a block and press Ctrl+D (or Cmd+D on Mac)
- Changes are tracked and can be undone

### Step 4: Save Your Work
1. Click the **💾 Save** button in the toolbar
2. Your template is persisted to the backend
3. The toolbar shows "Saved" status

---

## Using Keyboard Shortcuts

All shortcuts work in the editor:

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` / `Cmd+S` | Save Template |
| `Ctrl+Z` / `Cmd+Z` | Undo |
| `Ctrl+Shift+Z` / `Cmd+Shift+Z` | Redo |
| `Ctrl+Y` / `Cmd+Y` | Redo (alternate) |
| `Delete` | Delete selected block |
| `Ctrl+D` / `Cmd+D` | Duplicate selected block |
| `Escape` | Deselect block |
| `Ctrl+P` / `Cmd+P` | Toggle Preview |

---

## Editing Block Properties

### Property Types

**Text Properties**
- Text input fields for content, placeholders, labels, etc.
- Type freely and press Enter or blur to apply

**Numeric Properties**
- Number spinners for width, height, padding, etc.
- Use arrow keys or type values directly

**Boolean Properties**
- Checkboxes for toggles (disabled, required, etc.)
- Click to toggle on/off

**Select Properties**
- Dropdown menus for predefined options
- Useful for variants, types, sizes, etc.

**Color Properties**
- Color picker with hex display
- Click the color swatch to open picker
- Shows hex value for reference

**Style Properties**
- CSS editor for custom styles
- Enter CSS as `property: value; property: value;`
- Example: `color: #000; font-size: 14px; padding: 8px;`

### Common Properties by Component

**Text Component**
- `content`: Text to display
- `variant`: Style variant (primary, secondary, etc.)
- `color`: Text color

**Button Component**
- `label`: Button text
- `disabled`: Disable button
- `variant`: Button style

**Input Component**
- `placeholder`: Input hint text
- `type`: Input type (text, email, number, etc.)
- `required`: Mark as required
- `disabled`: Disable input

**Image Component**
- `src`: Image source URL
- `alt`: Alt text for accessibility
- `width`: Image width
- `height`: Image height

---

## Configuring Styles

The **Styles** section in the Properties panel lets you add inline CSS:

1. Click the "Styles" header to expand the section
2. Enter CSS properties in the textarea
3. Format: `property: value; property: value;`
4. Examples:
   ```css
   color: #ff0000;
   font-size: 16px;
   padding: 10px;
   background: rgba(0, 0, 0, 0.1);
   border-radius: 4px;
   ```

---

## Managing Undo/Redo

The toolbar shows undo/redo controls:

- **↶ Undo button** - Reverts your last action
- **↷ Redo button** - Restores a reverted action
- Buttons disable when no history available

Every change creates a new history point:
- Add/delete blocks
- Edit properties
- Change styles
- Modify constraints

You can undo all the way to an empty canvas.

---

## Settings & Preferences

Click **⚙️ Settings** in the toolbar to open the Settings modal.

### Appearance Tab
- **Theme**: Choose Light, Dark, or System (follows OS setting)
- **Language**: Select your preferred language

### Editor Tab
- **Autosave**: Automatically save changes (recommended enabled)
- **Autosave Interval**: How often to save (5s to 5min)
- **Export Format**: Default format for exporting templates (JSON/HTML/Craft.js)
- **Grid Snap**: Snap blocks to grid when moving (recommended)
- **Grid Size**: How many pixels per grid unit
- **Show Grid**: Display grid overlay on canvas

### Advanced Tab
- **Keyboard Shortcuts**: Enable/disable keyboard shortcuts
- **Shortcuts Reference**: View all available shortcuts

Changes are saved automatically when you click "Save Settings".

---

## Resizing Panels

The dividers between panels can be dragged to resize:

- **Between Blocks and Canvas**: Drag left/right to widen or narrow the component panel
- **Between Canvas and Properties**: Drag left/right to change properties panel width

Minimums are enforced to keep everything usable.

---

## Preview Mode

Click **👁 Preview** to see a side-by-side preview of your template:

- Shows how the template renders
- Stays synchronized with canvas changes
- Click again to hide preview

---

## Template Operations

### Save Template
1. Click **💾 Save** or press Ctrl+S
2. Template is persisted to backend
3. Status shows "Saved"

### Load Template
1. Use the template loader (in top menu)
2. Select a template from your library
3. Canvas loads with the template's blocks
4. Properties panel ready for editing

### Export Template
1. After saving, use the export function
2. Choose export format (JSON/HTML/Craft.js)
3. File downloads to your computer

---

## Best Practices

### Organization
- Group related components in containers
- Use descriptive names for blocks
- Keep nesting depth reasonable (3-4 levels max)

### Performance
- Don't create hundreds of blocks in one template
- Use autosave to avoid losing work
- Regularly save important changes

### Accessibility
- Use semantic components (headings, paragraphs, etc.)
- Add alt text to images
- Use proper color contrast
- Label form inputs

### Styling
- Keep styles organized and consistent
- Use CSS variables when possible
- Avoid inline styles for complex layouts
- Test with different zoom levels

---

## Troubleshooting

### Block Not Selected
- Click directly on the block element
- Try clicking the center of the block
- Check that the block is on the canvas (not hidden)

### Properties Don't Update
- Make sure the block is selected (green border visible)
- Try refreshing the page if stuck
- Check browser console for errors

### Undo Not Working
- Make sure you've made changes to undo
- Check undo button isn't grayed out
- Try using keyboard shortcut instead

### Save Failed
- Check internet connection
- Verify backend bridge is connected
- Check browser console for error messages
- Try saving again

### Drag-Drop Not Working
- Make sure source block is draggable
- Try dragging to the center of canvas
- Check browser allows drag-drop (not blocked)
- Refresh page if stuck

---

## Keyboard Navigation

All toolbar buttons are keyboard accessible:

1. Press `Tab` to move between buttons
2. Press `Enter` or `Space` to activate
3. Use Alt+key for button shortcuts:
   - Alt+Z: Undo
   - Alt+Y: Redo
   - Alt+S: Save
   - Alt+P: Preview
   - Alt+Shift+S: Settings

---

## Next Steps

Now that you understand the UI:

1. **Create a Template**: Try building a simple layout
2. **Explore Components**: Drag different blocks to see what they do
3. **Customize Properties**: Edit styles and properties
4. **Save & Export**: Practice saving and exporting your work
5. **Undo & Redo**: Experiment with history features

---

## Tips & Tricks

### Pro Tips
- **Duplicate for Speed**: Make one component perfect, then duplicate and modify
- **Keyboard Workflow**: Use keyboard shortcuts for faster editing
- **Autosave Peace of Mind**: Enable autosave so you never lose work
- **Grid Snapping**: Use grid snap for aligned layouts
- **Preview Often**: Switch to preview mode to check your work

### Common Patterns
- Container > Rows > Columns > Content
- Card > [Title, Description, Actions]
- Form > [Inputs, Labels, Submit]
- Hero > [Background, Overlay, Content]

---

## Getting Help

If you need help:

1. Check this guide for the feature you're using
2. Look at the keyboard shortcuts reference in Settings
3. Check tooltips (hover over buttons for hints)
4. Review the component descriptions in the Blocks panel
5. Check browser console for error messages

---

## Summary

The Anki Template Designer now provides a complete visual editing experience:

✅ Easy drag-and-drop component creation  
✅ Detailed property editing  
✅ Full undo/redo history  
✅ Keyboard shortcuts for power users  
✅ Customizable appearance and behavior  
✅ Auto-save for peace of mind  

Happy designing! 🎨
