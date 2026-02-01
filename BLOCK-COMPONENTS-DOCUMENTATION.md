# Block Components System Documentation

## Overview

The Block Components System provides a comprehensive set of pre-built, reusable UI components specifically designed for Anki template editing. All blocks are optimized for flashcard rendering and user experience, accounting for Anki's limitations and capabilities.

## Architecture

### Block Categories (Updated February 1, 2026)

1. **Anki Fields** (6 components) - Anki template syntax and field references
2. **Layout & Structure** (7 components) - Containers and semantic layout
3. **Grid & Columns** (4 components) - Multi-column CSS Grid layouts
4. **Flexbox** (3 components) - Flexible stack layouts
5. **Spacing** (2 components) - Spacing and dividers
6. **Text & Typography** (existing) - Headings, paragraphs, formatting
7. **Media** (existing) - Images, audio, videos

**Total: 23 Core Blocks (Anki-optimized)**

---

## Anki Fields Blocks (NEW)

Anki-specific components for template syntax and field references. These blocks help users visually build templates using Anki's template language.

### Field Placeholder

**Purpose**: Insert reference to Anki field  
**Syntax**: `{{FieldName}}`  
**Usage**: Displays field value on card from the note  
**Canvas**: Yes (editable)  
**Visual Styling**: Blue background (#e3f2fd) to indicate field reference  
**Example**: `{{Front}}`, `{{Back}}`, `{{Extra}}`

### Cloze Deletion

**Purpose**: Cloze deletion syntax  
**Syntax**: `{{c1::answer}}`  
**Usage**: Hide text that appears on back of card only  
**Canvas**: Yes (editable)  
**Visual Styling**: Orange background (#ffe0b2) to indicate cloze  
**Multiple Cloze**: Use c1, c2, c3 for multiple deletions on same card  
**Example**: `{{c1::Berlin}}` clozes "Berlin" on first card

### Hint Field

**Purpose**: Hint text (hidden until clicked by user)  
**Syntax**: `{{hint:FieldName}}`  
**Usage**: Show/hide hint on card during review  
**Canvas**: Yes  
**Visual Styling**: Blue link style to indicate interactive element  
**Example**: `{{hint:Pronunciation}}`

### Type Answer

**Purpose**: Type-in-the-answer field  
**Syntax**: `{{type:FieldName}}`  
**Usage**: Require user to type answer to check against field  
**Canvas**: Yes  
**Visual Styling**: Bordered box with monospace font to indicate input  
**Example**: `{{type:Answer}}`

### Conditional (Front/Back)

**Purpose**: Conditional content display  
**Syntax**: `{{#FrontSide}}...{{/FrontSide}}` or `{{#Back}}...{{/Back}}`  
**Usage**: Show content only on front side or back side  
**Canvas**: Yes (accepts children)  
**Visual Styling**: Conditional indicator with label  
**Example**: `{{#FrontSide}}<div>Question</div>{{/FrontSide}}`

### Tags Display

**Purpose**: Display note tags  
**Syntax**: `{{Tags}}`  
**Usage**: Show tags on card (for organization/filtering)  
**Canvas**: Yes  
**Visual Styling**: Small gray text  
**Example**: `Tags: {{Tags}}`

---

## Layout & Structure Blocks

Container and semantic layout components designed for Anki's rendering constraints.

### Section

**Purpose**: Semantic section container with visual separator  
**Features**: Bottom border divider, padding  
**Canvas**: Yes (accepts children)  
**Use Cases**: Divide template into logical sections

### Panel

**Purpose**: Simple bordered container  
**Features**: 1px border, rounded corners (4px), subtle shadow  
**Canvas**: Yes (accepts children)  
**Use Cases**: Group related content

### Card

**Purpose**: Material Design card container  
**Features**: White background, shadow elevation, rounded corners  
**Canvas**: Yes (accepts children)  
**Use Cases**: Highlighted content areas

### Surface

**Purpose**: Simple light background container  
**Features**: Light gray background (#f5f5f5), border radius  
**Canvas**: Yes (accepts children)  
**Use Cases**: Subtle content backgrounds

### Container

**Purpose**: Generic flexible container  
**Features**: Max-width constraint (800px), centered alignment  
**Canvas**: Yes (accepts children)  
**Use Cases**: Wrap content for consistent width across cards

### Padding Box

**Purpose**: Add padding around content  
**Features**: 16px padding on all sides  
**Canvas**: Yes (accepts children)  
**Use Cases**: Add spacing around nested content

### Margin Box

**Purpose**: Add margin around content  
**Features**: 16px margin on all sides  
**Canvas**: Yes (accepts children)  
**Use Cases**: Add spacing between components

---

## Grid & Columns Blocks

Multi-column layouts using CSS Grid (fully compatible with Anki).

### Grid

**Purpose**: 3-column CSS grid layout  
**Features**: Equal column widths, 16px gap  
**Canvas**: Yes (accepts children)  
**Use Cases**: Display 3 items side-by-side

### Row 2-Column

**Purpose**: 2-column grid layout  
**Features**: 50/50 split, responsive  
**Canvas**: Yes (accepts children)  
**Use Cases**: Two-pane layouts, side-by-side content

### Row 3-Column

**Purpose**: 3-column grid layout  
**Features**: Equal 3-column split, responsive  
**Canvas**: Yes (accepts children)  
**Use Cases**: Three-pane layouts, multiple items

### Flow Layout

**Purpose**: Auto-wrapping grid layout  
**Features**: Flexible columns that wrap, 16px gap  
**Canvas**: Yes (accepts children)  
**Use Cases**: Responsive multi-item displays

---

## Flexbox Blocks

Flexible stack layouts for dynamic spacing and alignment.

### Horizontal Stack (H-Stack)

**Purpose**: Horizontal flex layout  
**Features**: Row direction, configurable gap  
**Canvas**: Yes (accepts children)  
**Use Cases**: Arrange items horizontally

### Vertical Stack (V-Stack)

**Purpose**: Vertical flex layout  
**Features**: Column direction, configurable gap  
**Canvas**: Yes (accepts children)  
**Use Cases**: Stack items vertically

### Center

**Purpose**: Center content both horizontally and vertically  
**Features**: Flex centering, configurable dimensions  
**Canvas**: Yes (accepts children)  
**Use Cases**: Centered layouts for emphasis

---

## Spacing Blocks

Spacing and dividers for visual separation.

### Spacer

**Purpose**: Flexible spacing element  
**Features**: Configurable height (default: 16px)  
**Non-droppable**: Cannot contain children  
**Use Cases**: Add vertical space between elements

### Divider

**Purpose**: Horizontal separator line  
**Features**: Gray border, margin-adjusted  
**Non-droppable**: Cannot contain children  
**Use Cases**: Visual separation between sections

---

## Block Registration & GrapeJS Integration

All blocks are registered with GrapeJS BlockManager using the block definition pattern:

```javascript
editor.BlockManager.add('block-id', {
  label: 'Block Name',
  category: 'Category Name',
  content: {
    type: 'component-name',
  },
  attributes: {
    class: 'block-class',
  },
});
```

### Category Names (for organizing UI blocks panel)

- `Anki Fields` - All 6 Anki-specific blocks
- `Layout & Structure` - All 7 container blocks
- `Grid & Columns` - All 4 grid blocks
- `Flexbox` - All 3 flex stack blocks
- `Spacing` - All 2 spacing blocks
- `Text & Typography` - Text elements
- `Media` - Images, audio, videos

---

## Block File Structure

```
web/blocks/
├── layout.js        (16 layout/grid/flex/spacing blocks)
├── anki-blocks.js   (6 Anki field blocks)
└── index.js         (Registration orchestration)
```

### layout.js (16 blocks)

Registers all layout, grid, flexbox, and spacing blocks with GrapeJS.

**Blocks Registered**:
1. section
2. panel
3. card
4. surface
5. container
6. padding-wrapper
7. margin-wrapper
8. grid
9. row-2-col
10. row-3-col
11. flow-layout
12. h-stack
13. v-stack
14. center
15. spacer
16. divider

### anki-blocks.js (6 blocks)

Registers all Anki-specific template syntax blocks with GrapeJS.

**Blocks Registered**:
1. anki-field
2. cloze
3. hint-field
4. type-answer
5. conditional
6. tags-display

---

## Visual Styling

### Anki Field Blocks Color Scheme

To help users quickly recognize template syntax:

- **Field**: Light blue (#e3f2fd) background
- **Cloze**: Light orange (#ffe0b2) background
- **Hint**: Link blue (#1976d2) text
- **Type Answer**: Bordered gray (#e0e0e0) box
- **Conditional**: Purple border (#9c27b0)
- **Tags**: Light gray (#bdbdbd) text

### Standard Container Styling

- **Padding**: 16px (panels, cards, surfaces)
- **Border Radius**: 4px (panels, cards)
- **Border**: 1px solid #e0e0e0 (panels)
- **Shadow**: 0 2px 4px rgba(0,0,0,0.1) (cards)
- **Gap** (grids/flex): 16px

---

## Component Properties

### Canvas Components

All layout, grid, and flexbox blocks support:
- **accept**: 'text', 'image', 'link', 'video', 'other blocks'
- **Can contain**: Other blocks or text elements
- **Default content**: None (user defines)

### Non-Canvas Components

Spacer and Divider:
- **Cannot contain**: Children elements
- **Are leaf nodes**: Cannot be parent containers

---

## Browser Compatibility

All blocks use standard CSS that works in:
- Anki's built-in card viewer (WebKit)
- Modern browsers (Chrome, Firefox, Safari)
- Mobile browsers

**Special consideration**: Avoid JavaScript-dependent blocks (all current blocks use CSS only).

---

## Performance

### Bundle Size

- **layout.js**: ~4KB
- **anki-blocks.js**: ~2KB
- **Total block definitions**: ~6KB (minified)

### Runtime Performance

- No JavaScript required for block rendering
- Pure CSS layouts (Grid, Flexbox)
- Minimal DOM overhead
- Fast template rendering in Anki

---

## Best Practices

### Nesting

```html
<!-- Good: Logical nesting -->
<div class="container">
  <section>
    <div class="card">
      <p>Question: {{Front}}</p>
      <p>Answer: {{Back}}</p>
    </div>
  </section>
</div>

<!-- Good: Grid with content -->
<div class="grid">
  <div>{{c1::Term1}}</div>
  <div>{{c2::Term2}}</div>
  <div>{{c3::Term3}}</div>
</div>
```

### Anki-Specific Guidelines

1. **Use Field blocks** to reference note fields
2. **Use Cloze blocks** for deletions (not manual text)
3. **Use Conditional** for front/back-side-only content
4. **Avoid JavaScript** - Anki doesn't support it in templates
5. **Use CSS Grid/Flexbox** for responsive layouts

### Content Organization

- Use Sections to divide front and back content
- Use Panels or Cards for visually distinct content
- Use Spacers for consistent spacing between elements
- Use H-Stack or V-Stack for flexible alignment

---

## Troubleshooting

### Block Not Appearing in Editor

1. Verify block is registered in layout.js or anki-blocks.js
2. Check category matches expected name
3. Verify HTML structure is valid
4. Check browser console for errors

### Styling Not Applied

1. Verify CSS classes exist and are correct
2. Check for conflicting styles in Anki
3. Test with inline styles instead of classes
4. Verify units are correct (px, %)

### Content Not Rendering in Anki

1. Verify block uses CSS only (no JavaScript)
2. Check HTML tags are Anki-compatible
3. Verify field names match actual note fields
4. Test exported template directly in Anki

---

## Related Documentation

- **LAYOUT-CLEANUP-CHECKLIST.md**: Detailed cleanup process and verification steps
- **COMPONENT-ANALYSIS-ANKI.md**: Analysis of GrapeJS components and Anki suitability
- **IMPLEMENTATION-PLAN-PHASES.md**: Roadmap for implementing component system

---

## Version History

**February 1, 2026 - Complete Rebuild**
- Removed 9 unsuitable blocks (modal, drawer, split-view, accordion, tabs, stepper, masonry, frame)
- Added 6 Anki-specific template syntax blocks
- Added Container block for consistency
- Restructured documentation around Anki-specific use cases
- Reduced total blocks from 54+ to 23 core blocks

---

## Contributing

To add new blocks:

1. Define block in layout.js or anki-blocks.js
2. Follow naming pattern: lowercase with hyphens (e.g., `anki-field`)
3. Add to correct category
4. Provide meaningful label and default content
5. Document in BLOCK-COMPONENTS-DOCUMENTATION.md
6. Verify compatibility with Anki rendering
7. Test in Template Designer UI

---

## Support

For questions about blocks:
- Check block properties in this documentation
- Review LAYOUT-CLEANUP-CHECKLIST.md for implementation details
- See COMPONENT-ANALYSIS-ANKI.md for design rationale
- Test blocks in Template Designer UI with live preview
