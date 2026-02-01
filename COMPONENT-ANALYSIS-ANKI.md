# Component Analysis for Anki Template Designer

**Date:** February 1, 2026  
**Purpose:** Evaluate GrapeJS components for Anki template editing suitability

---

## GrapeJS Built-in Component Types

GrapeJS has these **built-in component types** (from official documentation):

| Type | Purpose | Anki Suitability |
|------|---------|------------------|
| `default` | Base component (div) | ✅ Essential |
| `wrapper` | Root canvas container | ✅ Essential (internal) |
| `text` | Editable text inline | ✅ Essential |
| `textnode` | Text without tag | ✅ Useful |
| `image` | `<img>` handling | ✅ Essential |
| `video` | Video embed | ⚠️ Limited (Anki has restrictions) |
| `link` | `<a>` elements | ✅ Useful |
| `label` | `<label>` elements | ⚠️ Limited use in Anki |
| `table` | `<table>` handling | ✅ Useful for data display |
| `thead/tbody/tfoot` | Table sections | ✅ Useful |
| `row` | `<tr>` elements | ✅ Useful |
| `cell` | `<td>/<th>` elements | ✅ Useful |
| `map` | Google Maps embed | ❌ Not suitable (external) |
| `script` | `<script>` elements | ⚠️ Limited (Anki JS restrictions) |
| `svg` | SVG elements | ✅ Useful for icons |
| `comment` | HTML comments | ⚠️ Minimal use |

**Key Insight:** GrapeJS does NOT have built-in "Container", "Stack", "Box", "Row", or "Column" components. These are **custom components** that projects create themselves.

---

## Current Project Component Inventory

### Layout Blocks (layout.js)

| Block ID | Label | Type | Anki Suitability | Notes |
|----------|-------|------|------------------|-------|
| `frame` | Frame | Container | ⚠️ Questionable | Device mockup - may confuse users |
| `section` | Section | Container | ✅ Keep | Semantic grouping |
| `panel` | Panel | Container | ✅ Keep | Bordered container |
| `card` | Card | Container | ✅ Keep | Visual card layout |
| `surface` | Surface | Container | ✅ Keep | Background container |
| `modal-container` | Modal Container | Container | ❌ Remove | Modals don't work in Anki |
| `drawer` | Drawer | Container | ❌ Remove | Navigation drawer irrelevant |
| `split-view` | Split View | Layout | ⚠️ Reconsider | Complex for flashcards |
| `accordion` | Accordion | Interactive | ⚠️ Limited | Requires JS, limited Anki support |
| `tab-container` | Tab Container | Interactive | ❌ Remove | Requires JS, doesn't work in Anki |
| `grid` | Grid | Layout | ✅ Keep | Useful for multi-column |
| `row-2-col` | 2 Columns | Layout | ✅ Keep | Common layout |
| `row-3-col` | 3 Columns | Layout | ✅ Keep | Common layout |
| `masonry` | Masonry | Layout | ❌ Remove | Too complex for flashcards |
| `h-stack` | H-Stack | Flexbox | ✅ Keep | Horizontal flex |
| `v-stack` | V-Stack | Flexbox | ✅ Keep | Vertical flex |
| `flow-layout` | Flow Layout | Flexbox | ✅ Keep | Wrap layout |
| `spacer` | Spacer | Spacing | ✅ Keep | Vertical space |
| `divider` | Divider | Spacing | ✅ Keep | Horizontal line |
| `padding-wrapper` | Padding Box | Spacing | ✅ Keep | Padding container |
| `margin-wrapper` | Margin Box | Spacing | ✅ Keep | Margin container |
| `center` | Center | Alignment | ✅ Keep | Center content |
| `tabs-nav` | Tabs | Navigation | ❌ Remove | Doesn't work in Anki |
| `stepper` | Stepper | Navigation | ❌ Remove | Irrelevant for flashcards |
| `anchor-link` | Anchor Link | Navigation | ⚠️ Limited | Internal links only |

---

## Missing Components Analysis

### Stack / Box Terminology

The user asked about "Stack" and "Box" components. Here's the clarification:

| Term | Our Equivalent | Status |
|------|---------------|--------|
| **Stack** (generic) | H-Stack + V-Stack | ✅ Already have |
| **HStack** | `h-stack` block | ✅ Exists |
| **VStack** | `v-stack` block | ✅ Exists |
| **Box** (generic container) | `surface`, `panel`, `padding-wrapper` | ✅ Already have alternatives |
| **Container** (centered max-width) | Custom `container` in LayoutBlocks.tsx | ✅ Exists in React components |

### What's Missing?

The current `layout.js` does NOT register a basic `container` block, though it exists in the React/Craft.js components. We should add it.

---

## Recommended Component Set for Anki

Based on Anki's rendering capabilities and flashcard UX:

### ✅ KEEP - Essential for Anki Templates

#### Containers (7)
| Block | Purpose | Why Keep |
|-------|---------|----------|
| `section` | Group content areas | Semantic organization |
| `panel` | Bordered content box | Visual grouping |
| `card` | Card-style container | Common flashcard pattern |
| `surface` | Background container | Subtle visual separation |
| `container` | Centered max-width box | **ADD THIS** - missing |
| `padding-wrapper` | Add padding | Layout control |
| `margin-wrapper` | Add margin | Layout control |

#### Grid Layouts (4)
| Block | Purpose | Why Keep |
|-------|---------|----------|
| `grid` | 3-column grid | Multi-item display |
| `row-2-col` | 2-column split | Question/answer layout |
| `row-3-col` | 3-column split | Comparison layouts |
| `flow-layout` | Wrap items | Tags, badges |

#### Flexbox (3)
| Block | Purpose | Why Keep |
|-------|---------|----------|
| `h-stack` | Horizontal stack | Inline elements |
| `v-stack` | Vertical stack | Stacked content |
| `center` | Center content | Alignment |

#### Spacing (2)
| Block | Purpose | Why Keep |
|-------|---------|----------|
| `spacer` | Vertical space | Breathing room |
| `divider` | Horizontal line | Visual separation |

**Total Essential Layouts: 16 blocks**

### ❌ REMOVE - Not Suitable for Anki

| Block | Reason |
|-------|--------|
| `frame` | Device mockup confuses purpose |
| `modal-container` | Modals don't work in Anki cards |
| `drawer` | Navigation patterns irrelevant |
| `tab-container` | Requires JavaScript, won't work |
| `tabs-nav` | Requires JavaScript, won't work |
| `accordion` | JavaScript-dependent behavior |
| `stepper` | Multi-step flows irrelevant |
| `masonry` | Overly complex for flashcards |
| `split-view` | Too complex, use columns instead |

**Remove: 9 blocks**

### ⚠️ RECONSIDER - Limited Use

| Block | Issue | Recommendation |
|-------|-------|----------------|
| `anchor-link` | Internal jumps only | Keep but rename to "Jump Link" |

---

## Anki-Specific Components to ADD

These components would be uniquely valuable for Anki template editing:

### 1. Anki Field Placeholder
```javascript
bm.add('anki-field', {
    label: 'Field',
    category: 'Anki',
    content: {
        tagName: 'span',
        classes: ['anki-field'],
        content: '{{FieldName}}',
        editable: true
    }
});
```

### 2. Cloze Deletion
```javascript
bm.add('cloze', {
    label: 'Cloze',
    category: 'Anki',
    content: {
        tagName: 'span',
        classes: ['anki-cloze'],
        content: '{{c1::answer}}',
        editable: true
    }
});
```

### 3. Hint Field
```javascript
bm.add('hint-field', {
    label: 'Hint',
    category: 'Anki',
    content: {
        tagName: 'span',
        classes: ['anki-hint'],
        content: '{{hint:FieldName}}'
    }
});
```

### 4. Type Answer Field
```javascript
bm.add('type-answer', {
    label: 'Type Answer',
    category: 'Anki',
    content: {
        tagName: 'div',
        classes: ['anki-type-answer'],
        content: '{{type:FieldName}}'
    }
});
```

### 5. Front/Back Conditional
```javascript
bm.add('front-side', {
    label: 'Front Only',
    category: 'Anki',
    content: {
        tagName: 'div',
        classes: ['anki-front-only'],
        content: '{{#FrontSide}}Content here{{/FrontSide}}'
    }
});
```

### 6. Tags Display
```javascript
bm.add('tags-display', {
    label: 'Tags',
    category: 'Anki',
    content: {
        tagName: 'div',
        classes: ['anki-tags'],
        content: '{{Tags}}'
    }
});
```

---

## Recommended Category Structure

### Final Block Categories for Anki Template Designer

```
📁 Anki Fields (NEW)
   ├── Field Placeholder
   ├── Cloze Deletion  
   ├── Hint Field
   ├── Type Answer
   ├── Conditional (Front/Back)
   └── Tags Display

📁 Layout & Structure
   ├── Section
   ├── Panel
   ├── Card
   ├── Surface
   ├── Container (ADD)
   ├── Padding Box
   └── Margin Box

📁 Grid & Columns
   ├── 2 Columns
   ├── 3 Columns
   ├── Grid (3×3)
   └── Flow Layout

📁 Flexbox
   ├── H-Stack
   ├── V-Stack
   └── Center

📁 Spacing
   ├── Spacer
   └── Divider

📁 Text & Typography (existing)
   ├── Heading
   ├── Paragraph
   ├── Bold
   ├── Italic
   ├── Code
   └── Quote

📁 Media (existing)
   ├── Image
   └── Audio (Anki-compatible)
```

---

## Action Items

### Immediate (Phase 1)
1. [ ] Add `container` block to layout.js
2. [ ] Remove unsuitable blocks (modal, drawer, tabs, stepper, masonry)
3. [ ] Rename `frame` or remove it

### Short-term (Phase 2)
4. [ ] Create Anki-specific blocks category
5. [ ] Implement Field Placeholder component
6. [ ] Implement Cloze Deletion component

### Medium-term (Phase 3)
7. [ ] Add Hint Field component
8. [ ] Add Type Answer component
9. [ ] Add Conditional blocks

---

## Summary

| Metric | Count |
|--------|-------|
| Current Layout Blocks | 25 |
| Keep | 16 |
| Remove | 9 |
| Add (Container) | 1 |
| Add (Anki-specific) | 6 |
| **Final Layout Blocks** | **17** |
| **New Anki Blocks** | **6** |
| **Total Recommended** | **23** |

The key insight is that GrapeJS provides HTML element types, not layout patterns. All layout components (Container, Stack, Box, Grid, etc.) are **custom implementations**. The current project already has most essential layouts. The main gaps are:

1. A basic `container` block (exists in React but not in GrapeJS blocks)
2. Anki-specific field/template syntax components

---

**Document Status:** Analysis Complete  
**Next Step:** Update implementation plans with these findings
