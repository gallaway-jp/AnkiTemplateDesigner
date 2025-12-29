# Android Studio-Style UI Builder - Implementation Summary

## Overview

The Anki Template Designer has been redesigned to follow Android Studio's Layout Designer architecture, providing a professional, industry-standard visual editing experience.

## New Architecture

### Inspired by Android Studio Designer

Based on analysis of Android Studio's designer source code at `com.android.tools.idea.uibuilder`, the new implementation adopts these key architectural patterns:

1. **DesignSurface** - Central canvas with zoom, pan, and grid support
2. **Component Tree** - Hierarchical view of all components
3. **Properties Panel** - Context-sensitive attribute editor
4. **Three-Panel Layout** - Industry-standard workspace organization

## New Components

### 1. Component Tree (`ui/component_tree.py`)

**Features:**
- Hierarchical display of all template components
- Drag-to-reorder support (within same parent)
- Right-click context menu (Delete, Duplicate, Move Up/Down)
- Selection synchronization with design surface
- Expand/Collapse all functionality
- Visual feedback for selected components

**Key Classes:**
- `ComponentTree`: Main widget managing the tree view
- `ComponentTreeItem`: Tree item wrapper for components

**Architecture Pattern:**
- Similar to Android Studio's `NlComponentTreeDefinition`
- Provides structural overview of the template hierarchy

### 2. Design Surface (`ui/design_surface.py`)

**Features:**
- **Zoom Controls:** Slider, +/-, presets (25%-200%), Zoom to Fit
- **Pan Support:** Middle-mouse or Alt+Drag to pan the canvas
- **Grid System:** Toggle-able 8px grid for alignment
- **Visual Rendering:** Component-aware rendering with proper styling
- **Interactive Selection:** Click to select, visual selection feedback
- **Keyboard Support:** Ctrl+Wheel to zoom

**Key Classes:**
- `DesignSurface`: Main widget with toolbar and controls
- `DesignSurfaceCanvas`: Actual canvas with painting and interaction

**Architecture Pattern:**
- Based on Android Studio's `DesignSurface` and `SceneView`
- Supports zoom levels from 10% to 400%
- Proper coordinate transformation for accurate selection

**Rendering:**
- Component-specific visualization (text fields, images, dividers, etc.)
- Selection highlights with blue border
- Background colors and borders from component properties
- Grid overlay for alignment assistance

### 3. Android Studio Dialog (`ui/android_studio_dialog.py`)

**Layout:**
```
┌────────────────────────────────────────────────────────────┐
│ Toolbar: [Mode: Design ▼] [Side: Front ▼] [Save] [Preview]│
├──────────┬─────────────────────────┬───────────────────────┤
│          │                         │                       │
│ Palette  │   Design Surface        │  Properties Panel     │
│ -------  │                         │                       │
│ • Text   │  [Zoom, Pan, Grid]      │  • Selected Component │
│ • Image  │                         │  • Layout             │
│ • Divider│  ┌──────────────────┐   │  • Text               │
│ • Heading│  │  Component 1     │   │  • Spacing            │
│ • Box    │  └──────────────────┘   │  • Background         │
│ • Cond.  │  ┌──────────────────┐   │                       │
│          │  │  Component 2     │   │                       │
│ -------  │  └──────────────────┘   │                       │
│          │                         │                       │
│ Tree     │                         │                       │
│ • Comp 1 │                         │                       │
│ • Comp 2 │                         │                       │
│          │                         │                       │
└──────────┴─────────────────────────┴───────────────────────┘
│ Status: Ready                       Components: 2          │
└────────────────────────────────────────────────────────────┘
```

**Features:**
- **Three-Panel Layout:** Palette/Tree (20%) | Design Surface (55%) | Properties (25%)
- **Mode Switcher:** Design / Code / Split view
- **Side Switcher:** Front / Back template editing
- **Toolbar Actions:** Save to Anki, Refresh Preview, Settings
- **Status Bar:** Current status and component count
- **Bidirectional Sync:** Design ↔ Code automatic synchronization

**Key Methods:**
- `on_tree_selection_changed()`: Syncs tree → surface → properties
- `on_surface_selection_changed()`: Syncs surface → tree → properties
- `on_structure_changed()`: Updates all panels when structure changes
- `sync_design_to_code()`: Converts components to HTML/CSS
- `sync_code_to_design()`: Parses HTML/CSS to components

## Enhanced Features

### Component Palette Integration

- Double-click palette items to add components
- Automatic component creation with sensible defaults
- Immediate selection and property editing

### Visual Component Rendering

Each component type has specialized rendering:

- **Text Field:** Shows `{{ FieldName }}` placeholder
- **Image Field:** Shows `[Image: FieldName]` placeholder
- **Divider:** Renders as horizontal line
- **Heading:** Larger, bold text
- **Container:** Dashed border with label
- **Conditional:** Shows `{{# Field }} ... {{/ Field }}`

### Selection Model

- Single selection mode
- Click on surface → updates tree + properties
- Click on tree → updates surface + properties
- Visual feedback on all panels

## File Structure

```
ui/
├── component_tree.py           # NEW: Component hierarchy tree
├── design_surface.py           # NEW: Zoom/pan canvas
├── android_studio_dialog.py   # NEW: Main dialog (Android Studio style)
├── designer_dialog.py          # EXISTING: Old dialog (kept for compatibility)
├── visual_builder.py           # EXISTING: Original visual builder
├── components.py               # EXISTING: Component definitions
├── properties_panel.py         # EXISTING: Properties editor
├── template_converter.py       # EXISTING: HTML/CSS conversion
├── preview_widget.py           # EXISTING: Preview rendering
└── editor_widget.py            # EXISTING: Code editor
```

## Integration Points

### 1. Entry Point Update

**File:** `template_designer.py`

Changed from:
```python
from .ui.designer_dialog import TemplateDesignerDialog
dialog = TemplateDesignerDialog(mw, note_type)
```

To:
```python
from .ui.android_studio_dialog import AndroidStudioDesignerDialog
dialog = AndroidStudioDesignerDialog(mw, note_type)
```

### 2. UI Package Exports

**File:** `ui/__init__.py`

Added exports:
- `AndroidStudioDesignerDialog`
- `ComponentTree`
- `DesignSurface`

## Usage Instructions

### For End Users

1. **Open Designer:** Tools → Template Designer (Visual Editor)
2. **Add Components:** 
   - Double-click items in Palette
   - Components appear in Tree and Surface
3. **Edit Properties:**
   - Click component in Tree or Surface
   - Edit in Properties Panel
4. **Arrange Components:**
   - Right-click in Tree for Move Up/Down
   - Or drag in Tree to reorder
5. **Zoom/Pan:**
   - Use zoom slider or +/- buttons
   - Alt+Drag or Middle-Mouse to pan
   - Ctrl+Wheel to zoom
6. **Switch Sides:**
   - Use Side dropdown to edit Front/Back
7. **Save:**
   - Click "Save to Anki" in toolbar

### For Developers

#### Adding New Component Types

1. Define in `components.py`
2. Add to palette in `visual_builder.py`
3. Add rendering in `design_surface.py` → `_draw_component_content()`
4. Add conversion in `template_converter.py`

#### Extending Interactions

1. Mouse handling: Override mouse events in `DesignSurfaceCanvas`
2. Keyboard shortcuts: Add to `AndroidStudioDesignerDialog.keyPressEvent()`
3. Context menus: Extend `ComponentTree.show_context_menu()`

## Architectural Patterns (from Android Studio)

### 1. Model-View Separation

- **Model:** Component tree structure (List[Component])
- **Views:** ComponentTree, DesignSurface, PropertiesPanel
- **Sync:** Callbacks ensure all views stay synchronized

### 2. Selection Model

- Central selection state in AndroidStudioDesignerDialog
- All panels notified of selection changes
- Single source of truth pattern

### 3. Coordinate Systems

```python
# Screen coordinates → Canvas coordinates
canvas_x = (screen_x - offset_x - pan_x) / zoom + canvas_origin_x
canvas_y = (screen_y - offset_y - pan_y) / zoom + canvas_origin_y
```

Similar to Android Studio's:
- `@SwingCoordinate` (screen)
- `@AndroidCoordinate` (design)

### 4. Layered Rendering

```
Layer 1: Background (white)
Layer 2: Grid (light gray)
Layer 3: Component backgrounds
Layer 4: Component borders
Layer 5: Component content
Layer 6: Selection overlays
```

## Benefits Over Previous Implementation

### Old Design (VisualTemplateBuilder)
- Single panel with palette + canvas + properties side-by-side
- No component tree
- No zoom/pan
- Limited visual feedback
- Simple drag-drop only

### New Design (AndroidStudioDesignerDialog)
- ✅ Professional three-panel layout
- ✅ Component tree for structure overview
- ✅ Zoom (10%-400%) and pan support
- ✅ Grid for alignment
- ✅ Enhanced visual rendering
- ✅ Synchronized selection across all panels
- ✅ Better component organization
- ✅ Industry-standard UX patterns

## Performance Considerations

### Rendering Optimization

- Component bounds cached during layout
- Only repaint on actual changes
- Efficient coordinate transformations
- Qt's built-in double-buffering

### Selection Optimization

- Guard flags prevent recursive updates (`self.updating`)
- Batch updates when structure changes
- Lazy preview refresh

## Future Enhancements

### Planned Features (from Android Studio analysis)

1. **Constraint System**
   - Snap-to-grid
   - Alignment guides
   - Smart suggestions

2. **Drag-and-Drop Refinement**
   - Drag from palette to surface
   - Visual drop indicators
   - Insertion position feedback

3. **Undo/Redo**
   - Command pattern implementation
   - History stack
   - Keyboard shortcuts (Ctrl+Z, Ctrl+Y)

4. **Multiple Selection**
   - Shift-click for multi-select
   - Bulk property editing
   - Group operations

5. **Layout Managers**
   - Auto-layout algorithms
   - Responsive sizing
   - Flexbox-like behavior

6. **Component Inspector**
   - Tabbed property sections (like Android Studio)
   - Advanced attributes
   - Quick access to common properties

## Testing

### Manual Test Checklist

- [ ] Open designer from Tools menu
- [ ] Load existing note type
- [ ] Add components via palette double-click
- [ ] Select components in tree
- [ ] Select components on surface
- [ ] Edit properties
- [ ] Reorder via tree drag-drop
- [ ] Reorder via context menu
- [ ] Delete components
- [ ] Duplicate components
- [ ] Zoom in/out
- [ ] Pan canvas
- [ ] Toggle grid
- [ ] Switch Front/Back
- [ ] Switch Design/Code modes
- [ ] Save to Anki
- [ ] Verify preview updates

### Known Limitations

1. Drag-and-drop from palette to surface not yet implemented (use double-click)
2. Split mode shows design only (full split view needs custom widget)
3. Undo/redo not yet implemented
4. No constraint-based layout (manual positioning only)
5. Canvas size is fixed (could be dynamic based on content)

## Conclusion

The new Android Studio-style UI builder provides a professional, intuitive interface for visual template editing. By adopting proven patterns from Android Studio's designer, it offers familiar interactions for developers while being accessible to non-technical users.

The modular architecture allows for easy extension and follows Qt best practices for maintainability and performance.
