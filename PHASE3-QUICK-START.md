# Phase 3 Quick Start - Drag-and-Drop & Templates

## What's New in Phase 3

### Services
- **blockInstantiator.ts** - Create block instances with unique IDs
- **templateLoader.ts** - Load templates from HTML/JSON files
- **templateExporter.ts** - Export to HTML, CSS, JSON, Anki formats

### Components
- **AnkiBlocks.tsx** - 7 Anki-specific block types
- **AnkiBlocks.css** - Professional styling for Anki blocks
- **CraftEditor** - Enhanced with drag-drop support
- **BlocksPanel** - Improved drag mechanics

### Tests
- **dragDrop.test.ts** - 30+ comprehensive integration tests

## Basic Usage

### 1. Create a Block

```typescript
import { createBlockInstance } from '@/services/blockInstantiator';

// Create from definition
const block = createBlockInstance('layout-vstack');

// With custom props
const block = createBlockInstance('data-heading', {
  text: 'My Title',
  level: 'h1'
});

// With children
const child = createBlockInstance('data-paragraph');
const parent = createBlockInstance('layout-container', {}, [child]);
```

### 2. Create from Drop Event

```typescript
import { createBlockFromDropEvent } from '@/services/blockInstantiator';

// Drop at position (100, 200)
const instance = createBlockFromDropEvent('layout-vstack', 100, 200);
// instance.metadata.position = { x: 100, y: 200 }
```

### 3. Validate Block

```typescript
import { validateBlockInstance } from '@/services/blockInstantiator';

const validation = validateBlockInstance(block);
if (validation.valid) {
  console.log('Block is valid');
} else {
  console.log('Errors:', validation.errors);
}
```

### 4. Export Template

```typescript
import { 
  exportToHtml, 
  exportToCss, 
  exportToJson,
  exportToAnkiTemplate 
} from '@/services/templateExporter';

// To HTML
const html = exportToHtml(block);

// To CSS
const css = exportToCss(block);

// To JSON
const json = exportToJson(block);

// To Anki format
const anki = exportToAnkiTemplate(block, 'Front');
```

### 5. Load Template

```typescript
import { 
  loadTemplateFromHtml,
  loadTemplateFromJson,
  loadTemplateFromFile 
} from '@/services/templateLoader';

// From HTML string
const template = loadTemplateFromHtml('<div>...</div>');

// From JSON string
const template = loadTemplateFromJson('{"id": "..."}');

// From file (async)
const file = /* from input */;
const template = await loadTemplateFromFile(file);

// Validate compatibility
const { compatible, missing } = validateTemplateCompatibility(template);
```

### 6. Anki Blocks

```typescript
import { 
  AnkiField,
  AnkiCloze,
  AnkiHint,
  AnkiConditional,
  registerAnkiBlocks
} from '@/components/AnkiBlocks';

// Blocks are auto-registered
registerAnkiBlocks();

// Create Anki field block
const field = createBlockInstance('anki-field', {
  fieldName: 'Front',
  fallback: 'No content'
});
```

## Drag-and-Drop Flow

### In BlocksPanel

```typescript
// Block items are draggable
const handleDragStart = (e: React.DragEvent<HTMLDivElement>) => {
  e.dataTransfer.effectAllowed = 'copy';
  e.dataTransfer.setData('application/block-name', blockName);
};
```

### In CraftEditor Canvas

```typescript
// Canvas accepts drops
const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
  e.preventDefault();
  
  const blockName = e.dataTransfer.getData('application/block-name');
  const dropX = e.clientX - canvasRect.left;
  const dropY = e.clientY - canvasRect.top;
  
  const instance = createBlockFromDropEvent(blockName, dropX, dropY);
  // Add instance to Craft.js editor
};

const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
  e.preventDefault();
  canvas.classList.add('canvas-drag-over'); // Visual feedback
};
```

## Visual Feedback

### CSS Classes

```css
/* When dragging over canvas */
.canvas-drag-over {
  background: linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(33, 150, 243, 0.05) 100%);
  border: 2px dashed #2196f3;
}

/* Anki blocks */
.anki-field { border-left: 3px solid #3f51b5; }
.anki-cloze { border-left: 3px solid #ff9800; }
.anki-hint { border-left: 3px solid #4caf50; }
.anki-conditional { border-left: 3px solid #f44336; }
```

## Instance Structure

```typescript
interface BlockInstance {
  id: string;                              // Unique ID
  name: string;                            // Block name: 'layout-vstack'
  type: string;                            // Component type
  props: Record<string, any>;              // Component props
  children: BlockInstance[];               // Nested blocks
  styles?: Record<string, string>;         // Inline CSS
  attributes?: Record<string, string>;     // HTML attributes
  metadata?: {
    createdAt: number;                     // Creation timestamp
    position?: { x: number; y: number };   // Canvas position
    size?: { width: number; height: number }; // Dimensions
  };
}
```

## Testing

```bash
# Run all tests
npm test

# Run specific test file
npm test dragDrop.test.ts

# With coverage
npm test -- --coverage
```

## Common Patterns

### Create Template Structure

```typescript
// Create root
const root = createBlockInstance('layout-frame', { title: 'My Template' });

// Add header
const header = createBlockInstance('layout-section');
const heading = createBlockInstance('data-heading', { text: 'Title' });
header.children = [heading];

// Add content
const content = createBlockInstance('layout-vstack');
const para = createBlockInstance('data-paragraph', { text: 'Content' });
content.children = [para];

// Assemble
root.children = [header, content];
```

### Export Complete Package

```typescript
import { exportAsPackage } from '@/services/templateExporter';

// Export template as downloadable ZIP
await exportAsPackage(template, 'my-template');
// Downloads: my-template.json with HTML, CSS, JSON
```

### Import and Validate

```typescript
import { loadTemplateFromFile, validateTemplateCompatibility } from '@/services/templateLoader';

const file = /* from file input */;
const template = await loadTemplateFromFile(file);

const { compatible, missing } = validateTemplateCompatibility(template);
if (!compatible) {
  console.warn('Missing blocks:', missing);
  // Handle missing blocks...
}
```

### Duplicate Block with Children

```typescript
import { duplicateBlockInstance } from '@/services/blockInstantiator';

// Original block with children
const original = createBlockInstance('layout-container', {}, [
  createBlockInstance('data-heading')
]);

// Create copy with new ID
const copy = duplicateBlockInstance(original);
// copy.id !== original.id
// copy.children[0].id !== original.children[0].id
```

## Performance Tips

### For Large Templates

1. **Lazy load blocks**: Use async block initialization
2. **Virtualize lists**: For large block lists in BlocksPanel
3. **Debounce saves**: Don't export on every change
4. **Cache registry**: Block registry is a singleton

### Optimizations Already In Place

✅ Block registry is cached  
✅ Instance validation is fast  
✅ JSON serialization is efficient  
✅ HTML generation is optimized  

## Debugging

### Enable Detailed Logging

```typescript
import { logger } from '@/utils/logger';

// See all block instantiation events
logger.debug('Block created:', { id, name, props });

// See drag-drop events
logger.debug('Drag over canvas:', { x, y });
logger.info('Block dropped:', { blockName, position });
```

### Validate Block Tree

```typescript
import { validateBlockInstance, getBlockTreeStats } from '@/services/blockInstantiator';

// Check validity
const { valid, errors } = validateBlockInstance(block);

// Get statistics
const stats = getBlockTreeStats(block);
// { totalBlocks: 15, maxDepth: 5, blockTypes: {...} }
```

## Troubleshooting

### Block Won't Drop
- Check block name is in registry: `blockRegistry.get(blockName)`
- Ensure DataTransfer has 'application/block-name' key
- Check canvas ref is available

### Export Has No Styles
- Ensure `instance.styles` object is populated
- Check CSS class names match selector format
- Verify styles object has valid CSS properties

### Template Won't Load
- Use `validateTemplateCompatibility()` to check blocks
- Enable debug logging to see what's failing
- Check HTML format matches expected structure

### Performance Issues
- Use `getBlockTreeStats()` to find deep nesting
- Avoid creating large trees without structure
- Cache exported results when possible

## Next Steps

After Phase 3:
1. Implement Craft.js node rendering (Phase 4)
2. Add real-time Python backend sync (Phase 5)
3. Optimize performance for large templates
4. Add undo/redo system
5. Implement template preview

---

**Quick Reference**: Use `blockInstantiator.ts` for creation, `templateExporter.ts` for export, `templateLoader.ts` for import, and `AnkiBlocks.tsx` for Anki-specific types.
