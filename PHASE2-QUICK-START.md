# Phase 2: Quick Start Guide

## What's New in Phase 2

Phase 2 introduces the **Craft.js Editor** with a complete block library, panel system, and block management service.

## Key Components

### 1. CraftEditor Component
Main editor component that wraps Craft.js:

```tsx
import { CraftEditor } from '@/components/CraftEditor';

export function App() {
  return <CraftEditor className="editor-instance" />;
}
```

### 2. Block Library (45+ blocks)

#### Import blocks by category:
```tsx
import {
  // Layout blocks
  Frame, Card, Panel, HStack, VStack,
  // Input blocks
  TextField, CheckBox, SelectInput,
  // Button blocks
  PrimaryButton, SecondaryButton,
  // Data blocks
  Heading, Paragraph, Image
} from '@/components/Blocks';
```

#### Or get all blocks at once:
```tsx
import * as Blocks from '@/components/Blocks';
```

### 3. Block Registry Service

Initialize all blocks on app startup:
```typescript
import { initializeBlocks, blockRegistry } from '@/services/blockRegistry';

async function setupEditor() {
  // Initialize all blocks
  await initializeBlocks();
  
  // Get all blocks
  const allBlocks = blockRegistry.getAll();
  
  // Get blocks by category
  const layoutBlocks = blockRegistry.getByCategory('Layout & Structure');
  
  // Get resolver for Craft.js
  const resolver = blockRegistry.getResolver();
}
```

### 4. UI Panels

#### BlocksPanel
Shows all available blocks organized by category:
```tsx
import { BlocksPanel } from '@/components/Panels';

<BlocksPanel />
```

#### PropertiesPanel
Edit properties of selected elements:
```tsx
import { PropertiesPanel } from '@/components/Panels';

<PropertiesPanel />
```

#### LayersPanel
View DOM hierarchy:
```tsx
import { LayersPanel } from '@/components/Panels';

<LayersPanel />
```

## Building a Layout

### 1. Container Structure
```tsx
<Frame>
  <VStack>
    <Heading text="Welcome" />
    <Paragraph text="This is a test" />
  </VStack>
</Frame>
```

### 2. Form Layout
```tsx
<Card title="Login Form">
  <FormGroup title="Credentials">
    <TextField label="Email" placeholder="you@example.com" />
    <PasswordField label="Password" />
    <PrimaryButton label="Sign In" />
  </FormGroup>
</Card>
```

### 3. Multi-Column Layout
```tsx
<Row3Col>
  <Card title="Card 1" />
  <Card title="Card 2" />
  <Card title="Card 3" />
</Row3Col>
```

## State Management

Access editor state via Zustand store:
```typescript
import { editorStore } from '@/stores';

// Watch selected node
const selectedNode = editorStore((state) => state.selectedNode);

// Update template
editorStore.setState((state) => ({
  ...state,
  template: newTemplate
}));

// Check if dirty
const isDirty = editorStore((state) => state.isDirty);
```

## Block Categories

### Layout & Structure (15 blocks)
- **Containers**: Frame, Section, Panel, Card, Surface, Modal, Drawer
- **Grid**: Grid, Row2Col, Row3Col
- **Flexbox**: HStack, VStack, Container
- **Spacing**: Spacer, Divider

### Inputs & Forms (11 blocks)
- **Text**: TextField, TextArea, PasswordField, EmailField
- **Selection**: CheckBox, RadioButton, SelectInput, ToggleSwitch
- **Advanced**: RangeSlider, FileInput
- **Container**: FormGroup

### Buttons & Actions (11 blocks)
- **Variants**: Primary, Secondary, Destructive, Success, Warning
- **Styles**: Link, Text, Outline
- **Special**: IconButton, FloatingActionButton
- **Container**: ButtonGroup

### Data Display (17 blocks)
- **Text**: Heading, Paragraph, Caption, Label, CodeBlock, InlineCode, Blockquote
- **Lists**: UnorderedList, OrderedList, DefinitionList
- **Media**: Image, Video, HorizontalRule
- **Feedback**: Badge, Chip, Alert

## Styling

All components use CSS variables for theming:

```css
/* Dark theme variables */
--bg-primary: #1a1a2e
--bg-secondary: #16213e
--text-primary: #ffffff
--text-secondary: #b0b0b0
--accent-primary: #1976d2
--border-color: #2a2a4e
```

## Running Tests

```bash
# Run editor tests
npm test -- craftEditor.test.ts

# Run all tests
npm test

# Watch mode
npm test -- --watch
```

## Next Steps (Phase 3)

1. **Connect drag-and-drop** - Implement canvas drop handlers
2. **Load templates** - Parse HTML and load into canvas
3. **Save templates** - Serialize canvas to HTML/CSS
4. **Anki blocks** - Add Anki-specific block types
5. **Python integration** - Connect to backend

## File Structure

```
web/src/
├── components/
│   ├── CraftEditor.tsx              # Main editor
│   ├── Blocks/                      # 45+ block components
│   │   ├── LayoutBlocks.tsx
│   │   ├── InputBlocks.tsx
│   │   ├── ButtonBlocks.tsx
│   │   ├── DataBlocks.tsx
│   │   └── index.ts
│   └── Panels/                      # UI panels
│       ├── BlocksPanel.tsx
│       ├── PropertiesPanel.tsx
│       ├── LayersPanel.tsx
│       └── index.ts
├── services/
│   └── blockRegistry.ts             # Block management
├── styles/
│   ├── CraftEditor.css
│   ├── BlocksPanel.css
│   ├── PropertiesPanel.css
│   └── LayersPanel.css
└── tests/
    └── craftEditor.test.ts          # Tests
```

## Troubleshooting

### Blocks not loading?
```typescript
// Make sure to initialize
import { initializeBlocks } from '@/services/blockRegistry';
await initializeBlocks();
```

### Editor not showing?
```typescript
// Check loading state
const { isLoading, error } = editorStore.getState();
if (error) console.error(error);
```

### Properties not updating?
```typescript
// Make sure panel is subscribed to store
const selectedNode = editorStore((state) => state.selectedNode);
```

## API Reference

### blockRegistry
```typescript
// Registration
register(block: CraftBlock): void
registerMany(blocks: CraftBlock[]): void

// Retrieval
get(name: string): CraftBlock | undefined
getAll(): CraftBlock[]
getByCategory(category: string): CraftBlock[]
getCategories(): string[]

// Resolution
getResolver(): Record<string, React.ComponentType>

// Diagnostics
getStats(): { totalBlocks; categories; byCategory }
clear(): void
```

### initializeBlocks()
```typescript
// Async function that loads all blocks
await initializeBlocks()

// Throws if blocks fail to load
```

## Best Practices

1. **Always initialize** - Call `initializeBlocks()` on app startup
2. **Use categories** - Organize blocks by category for users
3. **Provide defaults** - Set sensible defaultProps on blocks
4. **Handle selection** - Use `selectedNode` from store for properties
5. **Respect isCanvas** - Only allow drops in canvas containers

---

For more details, see [PHASE2-COMPLETION.md](./PHASE2-COMPLETION.md)
