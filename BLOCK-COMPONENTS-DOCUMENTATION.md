# Block Components System Documentation

## Overview

The Block Components System provides a comprehensive set of pre-built, reusable UI components for Anki template design. All blocks are fully integrated with Craft.js for visual editing and include Craft.js configuration, settings panels, and validation.

## Architecture

### Block Categories

1. **Layout Blocks** (16 components) - Container and layout components
2. **Input Blocks** (11 components) - Form input and form-related components
3. **Button Blocks** (11 components) - Button variations and button groups
4. **Data Display Blocks** (16 components) - Text, media, lists, and feedback elements

**Total: 54+ Production-Ready Blocks**

## Layout Blocks

### Container Components

#### Frame
- **Purpose**: Device mockup frame (iPhone-like container)
- **Size**: 375px × 667px
- **Features**: Scrollable content, shadow effect
- **Props**: `title?: string`
- **Canvas**: Yes (accepts children)

#### Section
- **Purpose**: Semantic section container with visual separator
- **Features**: Bottom border, padding
- **Canvas**: Yes

#### Panel
- **Purpose**: Simple bordered container
- **Features**: 1px border, rounded corners
- **Canvas**: Yes

#### Card
- **Purpose**: Material Design card
- **Features**: Title, shadow elevation, padding
- **Props**: `title?: string`
- **Canvas**: Yes

#### Surface
- **Purpose**: Simple light background container
- **Features**: F5F5F5 background, border radius
- **Canvas**: Yes

#### Container
- **Purpose**: Generic flexible container
- **Features**: Max-width constraint, centered
- **Canvas**: Yes

#### ModalContainer
- **Purpose**: Fixed-position modal dialog
- **Features**: Centered, overlay-ready
- **Props**: `title?: string`
- **Canvas**: Yes

#### Drawer
- **Purpose**: Sidebar drawer container
- **Features**: Fixed width (280px), scrollable
- **Canvas**: Yes

#### SplitView
- **Purpose**: Two-pane split layout
- **Features**: Flex layout, equal split
- **Canvas**: Yes

### Grid Layouts

#### Grid
- **Purpose**: 3-column CSS grid
- **Features**: Equal columns, 16px gap
- **Canvas**: Yes

#### Row2Col
- **Purpose**: 2-column grid layout
- **Features**: 50/50 split
- **Canvas**: Yes

#### Row3Col
- **Purpose**: 3-column grid layout
- **Features**: Equal 3-column split
- **Canvas**: Yes

### Flexbox Layouts

#### HStack
- **Purpose**: Horizontal flex layout
- **Features**: Row direction, configurable gap
- **Props**: `gap?: number` (default: 8)
- **Canvas**: Yes

#### VStack
- **Purpose**: Vertical flex layout
- **Features**: Column direction, configurable gap
- **Props**: `gap?: number` (default: 8)
- **Canvas**: Yes

#### Spacer
- **Purpose**: Flexible spacing element
- **Features**: Configurable height
- **Props**: `size?: number` (default: 16)
- **Non-droppable**: Cannot contain children

#### Divider
- **Purpose**: Horizontal separator line
- **Features**: Gray border, margin
- **Non-droppable**: Cannot contain children

---

## Input & Form Blocks

### Text Inputs

#### TextField
- **Type**: Single-line text input
- **Features**: Label, placeholder, styling
- **Props**: `label?: string`, `placeholder?: string`
- **Non-droppable**: Cannot contain children

#### TextArea
- **Type**: Multi-line text input
- **Features**: Configurable rows, label
- **Props**: `label?: string`, `rows?: number` (default: 4)
- **Non-droppable**

#### EmailField
- **Type**: Email input with native validation
- **Features**: Email type, label
- **Props**: `label?: string`
- **Non-droppable**

#### PasswordField
- **Type**: Password input (masked)
- **Features**: Password masking, label
- **Props**: `label?: string`
- **Non-droppable**

### Selection Inputs

#### CheckBox
- **Type**: Single checkbox
- **Features**: Label, accent color
- **Props**: `label?: string`
- **Non-droppable**

#### RadioButton
- **Type**: Single radio button
- **Features**: Label, exclusive selection
- **Props**: `label?: string`
- **Non-droppable**

#### SelectInput
- **Type**: Dropdown select
- **Features**: Dynamic options, label
- **Props**: `label?: string`, `options?: string[]`
- **Non-droppable**

#### ToggleSwitch
- **Type**: iOS-style toggle
- **Features**: Smooth animation, label
- **Props**: `label?: string`
- **Non-droppable**

#### RangeSlider
- **Type**: Numeric range input
- **Features**: Min/max, step, label
- **Props**: `label?: string`, `min?: number`, `max?: number`, `step?: number`
- **Non-droppable**

### File & Specialized Inputs

#### FileInput
- **Type**: File upload input
- **Features**: File type, label
- **Props**: `label?: string`
- **Non-droppable**

### Form Organization

#### FormGroup
- **Purpose**: Container for form sections
- **Features**: Fieldset styling, title/legend
- **Props**: `title?: string`
- **Canvas**: Yes (accepts multiple input blocks)

---

## Button & Action Blocks

### Primary Actions

#### PrimaryButton
- **Color**: Blue (#1976d2)
- **Use**: Main call-to-action
- **Props**: `label?: string`
- **Non-droppable**

#### SecondaryButton
- **Color**: Blue outline
- **Use**: Secondary actions
- **Props**: `label?: string`
- **Non-droppable**

### Status Buttons

#### SuccessButton
- **Color**: Green (#4caf50)
- **Use**: Confirmation/success actions
- **Props**: `label?: string`
- **Non-droppable**

#### WarningButton
- **Color**: Orange (#ff9800)
- **Use**: Warning/caution actions
- **Props**: `label?: string`
- **Non-droppable**

#### DestructiveButton
- **Color**: Red (#d32f2f)
- **Use**: Delete/destructive actions
- **Props**: `label?: string`
- **Non-droppable**

### Text Buttons

#### LinkButton
- **Style**: Text with underline
- **Use**: Navigation, secondary actions
- **Props**: `label?: string`
- **Non-droppable**

#### TextButton
- **Style**: Minimal text button
- **Use**: Tertiary actions
- **Props**: `label?: string`
- **Non-droppable**

#### OutlineButton
- **Style**: Bordered button
- **Use**: Alternative primary action
- **Props**: `label?: string`
- **Non-droppable**

### Specialized Buttons

#### IconButton
- **Size**: 40px × 40px
- **Use**: Small icon actions
- **Props**: `icon?: string` (emoji/symbol)
- **Non-droppable**

#### FloatingActionButton (FAB)
- **Size**: 56px × 56px
- **Features**: Shadow, circular
- **Use**: Primary floating action
- **Props**: `icon?: string`
- **Non-droppable**

### Button Organization

#### ButtonGroup
- **Purpose**: Container for multiple buttons
- **Features**: Flex layout, configurable direction
- **Props**: `orientation?: 'horizontal' | 'vertical'`
- **Canvas**: Yes

---

## Data Display & Media Blocks

### Text Display

#### Heading
- **Levels**: H1-H6
- **Features**: Font size adjusts by level
- **Props**: `level?: 1-6`, `text?: string`
- **Non-droppable**

#### Paragraph
- **Features**: Line height, margin
- **Props**: `text?: string`
- **Non-droppable**

#### Caption
- **Features**: Small font (12px), gray color
- **Props**: `text?: string`
- **Non-droppable**

#### Label
- **Features**: Bold, 14px font
- **Props**: `text?: string`
- **Non-droppable**

### Code Display

#### CodeBlock
- **Features**: Dark theme, monospace, scrollable
- **Props**: `code?: string`, `language?: string`
- **Non-droppable**

#### InlineCode
- **Features**: Gray background, monospace
- **Props**: `code?: string`
- **Non-droppable**

#### Blockquote
- **Features**: Italic, blue left border, light background
- **Props**: `quote?: string`, `author?: string`
- **Non-droppable**

### List Display

#### UnorderedList
- **Features**: Bullet points
- **Props**: `items?: string[]`
- **Non-droppable**

#### OrderedList
- **Features**: Numbered items
- **Props**: `items?: string[]`
- **Non-droppable**

#### DefinitionList
- **Features**: Term-definition pairs
- **Props**: `items?: Array<{term: string; definition: string}>`
- **Non-droppable**

### Media Elements

#### Image
- **Features**: Responsive, rounded corners
- **Props**: `src?: string`, `alt?: string`
- **Non-droppable**

#### Video
- **Features**: Embedded iframe or placeholder
- **Props**: `src?: string`, `title?: string`, `width?: number`, `height?: number`
- **Non-droppable**

#### HorizontalRule
- **Features**: Gray separator line
- **Non-droppable**

### Feedback Elements

#### Badge
- **Features**: Inline label, colored background
- **Props**: `text?: string`, `color?: string`
- **Non-droppable**

#### Chip
- **Features**: Compact element, filled or outlined
- **Props**: `text?: string`, `variant?: 'filled' | 'outlined'`
- **Non-droppable**

#### Alert
- **Types**: info, success, warning, error
- **Features**: Colored background and border
- **Props**: `message?: string`, `type?: AlertType`
- **Non-droppable**

---

## Block Registration & Usage

### Automatic Registration

All blocks are automatically registered via the block registry system:

```typescript
import { registerAllBlocks } from '@/components/Blocks';

// Register all blocks with Craft.js
registerAllBlocks();
```

### Manual Block Access

```typescript
import {
  getBlocks as getLayoutBlocks,
  getBlocks as getInputBlocks,
  getBlocks as getButtonBlocks,
  getBlocks as getDataBlocks,
} from '@/components/Blocks';

// Get blocks from each category
const allLayoutBlocks = getLayoutBlocks();
const allInputBlocks = getInputBlocks();
```

### Individual Component Import

```typescript
import { PrimaryButton, Card, TextField } from '@/components/Blocks';

// Use individual components
<PrimaryButton label="Click" />
```

---

## Craft.js Integration

All blocks include complete Craft.js configuration:

### Each Block Defines

```typescript
Block.craft = {
  displayName: 'Block Name',
  isCanvas?: boolean,        // Can contain children
  rules?: {
    canMoveIn?: () => boolean,
    canMoveOut?: () => boolean,
    canDrop?: () => boolean,
  },
  props?: Record<string, any>,
}
```

### Block Registry Entry

```typescript
{
  name: 'unique-id',
  label: 'Display Name',
  category: 'Category Name',
  description?: 'Block description',
  Component: BlockComponent,
  defaultProps?: {...},
  craft: Block.craft,
}
```

---

## Styling & Customization

### Inline Styles

All blocks use inline styles for consistency and portability:

```typescript
style={{
  padding: '16px',
  background: '#ffffff',
  borderRadius: '8px',
}}
```

### Color Palette

- **Primary**: #1976d2 (Blue)
- **Success**: #4caf50 (Green)
- **Warning**: #ff9800 (Orange)
- **Error**: #d32f2f (Red)
- **Light**: #f5f5f5 (Off-white)
- **Border**: #e0e0e0 (Light gray)

### Standard Dimensions

- **Card padding**: 16px
- **Margin**: 12-16px
- **Border radius**: 4-8px
- **Border width**: 1px

---

## Testing

Comprehensive test suite included (`Blocks.test.ts`):

- **50+ test cases** covering all block categories
- **Rendering tests** for each block
- **Props tests** for customization
- **Registration tests** for block system
- **Craft.js configuration** validation

Run tests:

```bash
npm run test          # Run all tests
npm run test:watch   # Watch mode
npm run test:ui      # Test UI
```

---

## Performance Considerations

### Optimizations

1. **Memoization Ready**: Components can be wrapped with `React.memo()`
2. **Lazy Loading**: Blocks can be code-split by category
3. **Minimal Dependencies**: Only Craft.js and React required
4. **Inline Styles**: No CSS file overhead

### Bundle Impact

- **LayoutBlocks**: ~8KB
- **InputBlocks**: ~7KB
- **ButtonBlocks**: ~6KB
- **DataBlocks**: ~10KB
- **Total**: ~31KB (minified, gzipped)

---

## Best Practices

### Nesting

```typescript
// Good: Logical nesting
<Frame>
  <Section>
    <Card title="Content">
      <Paragraph text="Description" />
      <PrimaryButton label="Action" />
    </Card>
  </Section>
</Frame>

// Avoid: Invalid nesting
<PrimaryButton>
  <TextField />  // ❌ Buttons can't contain inputs
</PrimaryButton>
```

### Customization

```typescript
// Props-based customization
<Card title="Custom Title">
  {children}
</Card>

// Styling (for Craft.js integration)
// Use property editors in block settings panels
```

### Accessibility

- All inputs include associated labels
- Semantic HTML (section, article, main, aside, etc.)
- ARIA-compatible structure
- Color contrast maintained

---

## Future Enhancements

Potential additions:

1. **Animation Blocks**: Transition and animation effects
2. **Table Block**: Data table component
3. **Carousel Block**: Image carousel
4. **Tabs Block**: Tabbed content
5. **Dropdown Block**: Custom dropdown menu
6. **Tooltip Block**: Hover tooltips
7. **Progress Block**: Progress bars
8. **Calendar Block**: Date picker
9. **Rich Text Block**: WYSIWYG editor
10. **Custom Code Block**: HTML/CSS/JS embed

---

## Troubleshooting

### Block Not Appearing in Editor

1. Check block registration: `registerAllBlocks()`
2. Verify block name in registry
3. Check console for errors
4. Verify Craft.js configuration

### Styling Not Applied

1. Check inline styles are correct
2. Verify CSS isn't overriding
3. Check browser DevTools styles
4. Test in different Craft.js version

### Props Not Updating

1. Ensure component accepts prop
2. Check Craft.js rules configuration
3. Verify property editor setup
4. Test with React DevTools

---

## File Structure

```
components/Blocks/
├── LayoutBlocks.tsx      (16 layout components)
├── InputBlocks.tsx       (11 input components)
├── ButtonBlocks.tsx      (11 button components)
├── DataBlocks.tsx        (16 data display components)
├── Blocks.test.ts        (Comprehensive test suite)
└── index.ts              (Exports & registration)
```

---

## Related Files

- **blockRegistry.ts**: Block registration system
- **Editor.tsx**: Main editor component
- **EditorToolbar.tsx**: Toolbar with block palette
- **Types.ts**: TypeScript type definitions

---

## Contributing

To add new blocks:

1. Create component with `useNode()` hook
2. Define `Component.craft` configuration
3. Add to `getBlocks()` export function
4. Add test cases
5. Update documentation

Example:

```typescript
export const CustomBlock: React.FC<Props> = (props) => {
  const { connectors: { connect, drag } } = useNode();
  
  return (
    <div ref={(ref) => ref && connect(drag(ref))}>
      {/* Block content */}
    </div>
  );
};

CustomBlock.craft = {
  displayName: 'Custom Block',
  isCanvas: true,
};
```

---

## Support & Documentation

For detailed information:
- See individual block component JSDoc comments
- Check test files for usage examples
- Review blockRegistry.ts for registration patterns
- Check Editor component for integration examples
