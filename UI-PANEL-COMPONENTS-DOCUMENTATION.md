# UI Panel Components Documentation

## Overview

The UI Panel system consists of three complementary components that form the core editing interface:

- **PropertiesPanel**: Property editing for selected blocks
- **LayersPanel**: Component hierarchy and selection
- **BlocksPanel**: Block library and drag-drop interface

## Architecture

### Component Hierarchy
```
EditorLayout
├── BlocksPanel (left sidebar)
│   ├── BlocksCategory
│   │   └── BlockItem (draggable)
│   └── BlocksPanel Footer (stats)
├── Canvas (center)
│   └── Craft.js Editor
└── SidePanel
    ├── LayersPanel (top-right)
    │   └── LayerItem (tree view)
    └── PropertiesPanel (bottom-right)
        ├── PropertyInput
        ├── StyleEditor
        └── ConstraintsEditor
```

## Panel Components

### PropertiesPanel

**Purpose**: Display and edit properties of the selected block

**Features**:
- Component information display
- Block property editing
- Inline style editor
- Constraints configuration
- Advanced properties
- Collapsible sections

**Key Methods**:
- `handlePropertyChange(name, value)`: Update block property
- `handleStyleChange(styles)`: Update inline styles
- `handleConstraintChange(constraints)`: Update drag constraints
- `toggleSection(section)`: Collapse/expand sections

**State**:
- `properties`: PropertyField[] - Editable properties
- `styles`: Record<string, string> - Inline styles
- `constraints`: string[] - Drag constraints
- `componentInfo`: Component name and type
- `collapsed`: Record<string, boolean> - Section states

**Props**:
- `className?: string` - Custom CSS class

**Example**:
```tsx
<PropertiesPanel className="right-panel" />
```

---

### LayersPanel

**Purpose**: Display and navigate the component hierarchy

**Features**:
- Component tree visualization
- Layer selection
- Layer renaming
- Layer deletion
- Expand/collapse controls
- Search and filtering
- Statistics display

**Key Methods**:
- `buildLayerTree(nodeId, depth)`: Build tree from Craft.js nodes
- `handleSelect(id)`: Select a layer
- `handleToggle(id)`: Expand/collapse layer
- `handleRename(id, name)`: Rename layer
- `handleDelete(id)`: Delete layer
- `handleExpandAll()`: Expand all layers
- `handleCollapseAll()`: Collapse all layers

**State**:
- `layerTree`: LayerNode | null - Component hierarchy
- `expanded`: Record<string, boolean> - Expansion state
- `searchFilter`: string - Filter query
- `stats`: { total, selected } - Layer statistics

**Props**:
- `className?: string` - Custom CSS class

**Example**:
```tsx
<LayersPanel className="layers-sidebar" />
```

---

### BlocksPanel

**Purpose**: Display available blocks and enable drag-drop

**Features**:
- Block categorization
- Category expansion/collapse
- Block search and filtering
- Drag-drop support
- Block descriptions
- Category statistics
- Expand/collapse all

**Key Methods**:
- `initializeCategories()`: Load blocks from registry
- `handleBlockDrag(block)`: Handle drag initiation
- `handleCategoryToggle(category)`: Expand/collapse category
- `handleExpandAll()`: Expand all categories
- `handleCollapseAll()`: Collapse all categories

**State**:
- `categories`: string[] - Available categories
- `blocksByCategory`: Map<string, CraftBlock[]> - Blocks by category
- `filter`: string - Search filter
- `loading`: boolean - Loading state
- `expandedCategories`: Record<string, boolean> - Category expansion
- `stats`: { total, categories } - Block statistics

**Props**:
- `className?: string` - Custom CSS class

**Example**:
```tsx
<BlocksPanel className="blocks-sidebar" />
```

---

## Supporting Components

### PropertyInput

Single property input field supporting multiple types.

**Types**:
- `text`: Text input
- `number`: Numeric input
- `checkbox`: Boolean checkbox
- `select`: Dropdown select
- `color`: Color picker
- `range`: Slider input
- `textarea`: Multi-line text

**Props**:
```typescript
interface PropertyInputProps {
  field: PropertyField;
  onChange: (value: any) => void;
  disabled?: boolean;
}
```

### StyleEditor

Visual CSS style editor with syntax support.

**Features**:
- CSS property syntax
- Semicolon-separated rules
- Error handling
- Real-time preview

**Props**:
```typescript
interface StyleEditorProps {
  styles: Record<string, string>;
  onChange: (styles: Record<string, string>) => void;
}
```

### ConstraintsEditor

Drag constraint configuration interface.

**Available Constraints**:
- `horizontal`: Fixed horizontal position
- `vertical`: Fixed vertical position
- `maxWidth`: Maximum width constraint
- `maxHeight`: Maximum height constraint
- `fixed`: Fixed position
- `aspectRatio`: Maintain aspect ratio

**Props**:
```typescript
interface ConstraintsEditorProps {
  constraints?: string[];
  onChange: (constraints: string[]) => void;
}
```

### BlocksCategory

Collapsible block category container.

**Props**:
```typescript
interface BlocksCategoryProps {
  category: string;
  blocks: CraftBlock[];
  onBlockDrag: (block: CraftBlock) => void;
  isExpanded: boolean;
  onToggle: (category: string) => void;
}
```

### BlockItem

Individual draggable block with preview.

**Features**:
- Drag-drop enabled
- Custom drag image
- Icon display
- Description tooltip
- Drag indicator

**Props**:
```typescript
interface BlockItemProps {
  block: CraftBlock;
  onDrag: () => void;
}
```

### LayerItem

Individual layer in component hierarchy.

**Features**:
- Expand/collapse toggle
- Selection highlight
- Rename in-place
- Delete with confirmation
- Hover actions
- Type icon
- Canvas badge

**Props**:
```typescript
interface LayerItemProps {
  node: LayerNode;
  onSelect: (id: string) => void;
  onToggle: (id: string) => void;
  onRename: (id: string, name: string) => void;
  onDelete: (id: string) => void;
  expanded: Record<string, boolean>;
  isDragging?: boolean;
}
```

---

## Integration Points

### With Craft.js

**Hooks Used**:
- `useEditor`: Access editor state and nodes
- `useNode`: Access current node in component context

**Events**:
- Selection changes trigger PropertiesPanel updates
- Node hierarchy changes trigger LayersPanel rebuild
- Block registry updates trigger BlocksPanel reload

### With Editor Store

**State Access**:
- `selectedNode`: Current selected block
- `template`: Current template
- `selectedNodeId`: ID of selected node

**Actions**:
- `setSelectedNode(node)`: Update selection
- `updateNode(id, props)`: Modify block properties
- `deleteNode(id)`: Remove block

### With Block Registry

**Methods**:
- `getAll()`: Get all blocks
- `getCategories()`: Get unique categories
- `getByCategory(category)`: Get blocks by category

---

## Styling & CSS

### CSS Classes

**PropertiesPanel**:
- `.properties-panel` - Main container
- `.property-field` - Individual field
- `.property-section` - Grouped section
- `.property-input` - Input element
- `.property-color-group` - Color picker group
- `.property-style-editor` - Style textarea

**LayersPanel**:
- `.layers-panel` - Main container
- `.layer-item` - Individual layer
- `.layer-item-toggle` - Expand/collapse button
- `.layer-item-label` - Layer name/type
- `.layer-item-actions` - Hover actions
- `.layers-panel-search` - Search input

**BlocksPanel**:
- `.blocks-panel` - Main container
- `.blocks-category` - Category container
- `.blocks-category-header` - Category header
- `.block-item` - Individual block
- `.block-item-content` - Block content
- `.blocks-panel-search` - Search input

---

## Data Types

### PropertyField

```typescript
interface PropertyField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'checkbox' | 'select' | 'color' | 'textarea' | 'range';
  value: any;
  options?: string[];
  min?: number;
  max?: number;
  step?: number;
}
```

### LayerNode

```typescript
interface LayerNode {
  id: string;
  name: string;
  type: string;
  children: LayerNode[];
  isSelected?: boolean;
  isHovered?: boolean;
  canDrop?: boolean;
  isCanvas?: boolean;
  depth: number;
}
```

### CraftBlock

```typescript
interface CraftBlock {
  name: string;
  label: string;
  category: string;
  icon?: string;
  description?: string;
  Component: React.FC<any>;
  craft?: CraftConfig;
  defaultProps?: Record<string, any>;
}
```

---

## Usage Examples

### Basic Layout

```tsx
import { PropertiesPanel, LayersPanel, BlocksPanel } from '@/components/Panels';

export function EditorLayout() {
  return (
    <div className="editor-container">
      <aside className="left-sidebar">
        <BlocksPanel />
      </aside>
      
      <main className="canvas-area">
        <Canvas />
      </main>
      
      <aside className="right-sidebar">
        <div className="panel-group">
          <LayersPanel className="panel layers-panel" />
          <PropertiesPanel className="panel properties-panel" />
        </div>
      </aside>
    </div>
  );
}
```

### Custom Integration

```tsx
// Adding custom block handlers
<BlocksPanel 
  onBlockSelect={(block) => {
    console.log(`Block selected: ${block.label}`);
    // Custom logic here
  }}
/>

// Custom property editor
<PropertiesPanel 
  onPropertyChange={(name, value) => {
    console.log(`Property changed: ${name} = ${value}`);
    // Custom update logic
  }}
/>
```

---

## Testing

### Test Coverage

**PropertiesPanel** (10+ tests):
- Rendering and empty state
- Property input handling
- Style editor functionality
- Constraints editor
- Section collapse/expand

**LayersPanel** (10+ tests):
- Layer tree rendering
- Search and filtering
- Selection handling
- Expand/collapse functionality
- Layer statistics

**BlocksPanel** (15+ tests):
- Category display and toggle
- Block rendering
- Search functionality
- Drag-drop setup
- Loading states
- Statistics display

### Running Tests

```bash
# Run all panel tests
npm test -- Panels.test.ts

# Run specific panel tests
npm test -- PropertiesPanel

# Run with coverage
npm test -- --coverage Panels.test.ts
```

### Example Test

```typescript
it('filters blocks based on search query', async () => {
  render(<BlocksPanel />);
  const user = userEvent.setup();

  const searchInput = screen.getByPlaceholderText(/Search blocks/i);
  await user.type(searchInput, 'Button');
  
  expect(screen.getByText('Primary Button')).toBeInTheDocument();
});
```

---

## Keyboard Shortcuts

| Action | Shortcut | Panel |
|--------|----------|-------|
| Expand all | Ctrl+E | Layers/Blocks |
| Collapse all | Ctrl+Shift+E | Layers/Blocks |
| Delete layer | Del | Layers |
| Rename layer | F2 | Layers |
| Search focus | Ctrl+F | Any |
| Clear search | Esc | Any |
| Next property | Tab | Properties |

---

## Performance Considerations

### Optimization Techniques

1. **Memoization**: Property inputs use React.memo for shallow comparison
2. **Lazy Loading**: Categories load on demand, blocks virtualized for large lists
3. **Debouncing**: Search input debounced to 300ms
4. **Ref Optimization**: useCallback prevents unnecessary re-renders

### Best Practices

```typescript
// Use useCallback for handlers
const handleSelect = useCallback((id: string) => {
  // Selection logic
}, [dependencies]);

// Use useMemo for expensive computations
const filteredItems = useMemo(() => {
  return items.filter(i => i.category === selectedCategory);
}, [items, selectedCategory]);

// Minimize re-renders with proper key props
{items.map(item => (
  <Item key={item.id} {...item} />
))}
```

---

## Accessibility

### ARIA Labels

```tsx
<input
  aria-label="Search blocks"
  placeholder="Search blocks..."
  role="searchbox"
/>
```

### Keyboard Navigation

- All interactive elements are keyboard accessible
- Tab order follows logical flow
- Focus indicators visible
- Semantic HTML elements used

### Screen Reader Support

- Meaningful labels on all inputs
- Role attributes for custom components
- Status messages announced
- Error messages descriptive

---

## Troubleshooting

### Common Issues

**Q: Panels not updating when block selected?**  
A: Ensure editor store is properly connected and setSelectedNode is called.

**Q: Drag-drop not working?**  
A: Check BlocksPanel dataTransfer setup and canvas drop handler implementation.

**Q: Layer tree not building?**  
A: Verify Craft.js nodes have proper parent/child relationships.

**Q: Search filtering too slow?**  
A: Implement debouncing or use virtualization for large datasets.

**Q: Properties not saving?**  
A: Check handlePropertyChange is properly updating editor store and Craft.js state.

---

## Future Enhancements

- [ ] Custom property field types (slider, toggle, date picker)
- [ ] Property grouping and validation
- [ ] Batch operations on multiple layers
- [ ] Layer locking and visibility toggle
- [ ] Undo/redo for layer operations
- [ ] Context menu on layers
- [ ] Advanced constraints UI
- [ ] Responsive preview in properties
- [ ] Theme customization panel
- [ ] Component favorites/recents

---

## Related Files

- [BlocksPanel.tsx](BlocksPanel.tsx) - Block library component
- [LayersPanel.tsx](LayersPanel.tsx) - Layer hierarchy component
- [PropertiesPanel.tsx](PropertiesPanel.tsx) - Property editor component
- [Panels.test.ts](Panels.test.ts) - Test suite (35+ tests)
- [index.ts](index.ts) - Panel exports

---

**Last Updated**: January 21, 2026  
**Version**: 1.0.0  
**Status**: Production Ready ✅
