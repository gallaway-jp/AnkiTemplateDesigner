# Anki Template Designer — Component Reference

This document describes every component and block available in the visual editor,
what it does, how it behaves, and what properties / traits it exposes.

---

## Anki Components

These are Anki-specific template syntax elements. When exported, they produce
Anki mustache-style tags (`{{...}}`).

### {{Field}}
| Property | Value |
|----------|-------|
| **Block label** | `{{Field}}` |
| **Component type** | `anki-field` |
| **Tag** | `<span>` |
| **Droppable** | No |

**Purpose**: Inserts an Anki field reference. Renders `{{FieldName}}` in the
exported template, which Anki replaces with the field's content at review time.

**Traits (editable in right panel)**:
| Trait | Type | Default | Description |
|-------|------|---------|-------------|
| Field Name | text | `Front` | The name of the Anki note field to display (e.g. `Front`, `Back`, `Extra`). |

**Canvas display**: Shows as an inline badge with the field syntax, e.g. `{{Front}}`.
Updates live when the trait is changed.

**Exported HTML**: `{{Front}}` (or whatever field name is set)

---

### Cloze
| Property | Value |
|----------|-------|
| **Block label** | `Cloze` |
| **Component type** | `anki-cloze` |
| **Tag** | `<span>` |
| **Droppable** | No |

**Purpose**: Creates a cloze deletion. Renders `{{c1::answer}}` syntax that Anki
uses for cloze-type notes.

**Traits**:
| Trait | Type | Default | Description |
|-------|------|---------|-------------|
| Cloze # | text | `1` | The cloze index number (1, 2, 3, ...). |
| Text | text | `answer` | The text to be hidden/revealed. |

**Canvas display**: `{{c1::answer}}` — updates live.

**Exported HTML**: `{{c1::answer}}`

---

### Hint
| Property | Value |
|----------|-------|
| **Block label** | `Hint` |
| **Component type** | `anki-hint` |
| **Tag** | `<span>` |
| **Droppable** | No |

**Purpose**: Inserts a hint field. Anki renders this as a clickable "show hint"
link that reveals the field content when clicked.

**Traits**:
| Trait | Type | Default | Description |
|-------|------|---------|-------------|
| Hint Field | text | `Extra` | The field whose content is shown as a hint. |

**Canvas display**: `{{hint:Extra}}` — updates live.

**Exported HTML**: `{{hint:Extra}}`

---

### Type Answer
| Property | Value |
|----------|-------|
| **Block label** | `Type Answer` |
| **Component type** | `anki-type-answer` |
| **Tag** | `<span>` |
| **Droppable** | No |

**Purpose**: Adds a type-in-the-answer input. Anki shows a text input on the
front side and compares the typed answer with the field value on the back side.

**Traits**:
| Trait | Type | Default | Description |
|-------|------|---------|-------------|
| Compare Field | text | `Front` | The field to compare the typed answer against. |

**Canvas display**: `{{type:Front}}` — updates live.

**Exported HTML**: `{{type:Front}}`

---

### Conditional
| Property | Value |
|----------|-------|
| **Block label** | `Conditional` |
| **Component type** | `anki-conditional` |
| **Tag** | `<div>` |
| **Droppable** | Yes |

**Purpose**: Wraps content in an Anki conditional section. The inner content is
only shown if the referenced field is non-empty (normal) or empty (negated).

**Traits**:
| Trait | Type | Default | Description |
|-------|------|---------|-------------|
| Field Name | text | `Extra` | The field to check. |
| Negate | checkbox | `false` | If checked, content is shown only when the field is **empty**. |

**Canvas display**: A dashed purple container. Other components can be dragged
into it.

**Exported HTML**:
- Normal: `{{#Extra}}...content...{{/Extra}}`
- Negated: `{{^Extra}}...content...{{/Extra}}`

---

### Tags
| Property | Value |
|----------|-------|
| **Block label** | `Tags` |
| **Component type** | `anki-tags` |
| **Tag** | `<span>` |
| **Droppable** | No |

**Purpose**: Displays the note's tags. Anki replaces this with a space-separated
list of the card's tags.

**Traits**: None.

**Canvas display**: `{{Tags}}`

**Exported HTML**: `{{Tags}}`

---

### FrontSide
| Property | Value |
|----------|-------|
| **Block label** | `FrontSide` |
| **Component type** | `anki-frontside` |
| **Tag** | `<div>` |
| **Droppable** | No |

**Purpose**: Used on the **back template** to include the entire front template
content. This avoids duplicating the front layout on the back.

**Traits**: None.

**Canvas display**: `{{FrontSide}}`

**Exported HTML**: `{{FrontSide}}`

---

## Layout Components

These components provide structural containers for organizing content.
They are droppable — you can drag other components into them.

### Section
| Property | Value |
|----------|-------|
| **Block label** | `Section` |
| **Component type** | `atd-section` |
| **Tag** | `<section>` |
| **Droppable** | Yes |

**Purpose**: A generic section container. Can be set to block, flex, or grid
display mode via its traits.

**Traits**:
| Trait | Type | Default | Options | Description |
|-------|------|---------|---------|-------------|
| Display | select | `block` | Block, Flex, Grid | The CSS display mode. |
| Direction | select | `column` | Vertical, Horizontal | Flex/grid direction (only applies when display is Flex or Grid). |
| Gap | text | *(empty)* | — | Space between children (e.g. `12px`). |

**Default style**: `padding: 16px; min-height: 60px`

**Canvas display**: Empty sections show placeholder text "Section — drop
components here".

---

### 2 Columns / 3 Columns
| Property | Value |
|----------|-------|
| **Block label** | `2 Columns` / `3 Columns` |
| **Component types** | `atd-row` (parent) + `atd-column` (children) |
| **Droppable** | Yes (both row and columns) |

**Purpose**: Pre-built multi-column layouts using flexbox. The row is a flex
container; each column is a flex child.

**Row traits** (`atd-row`):
| Trait | Type | Default | Options | Description |
|-------|------|---------|---------|-------------|
| Direction | select | `row` | Horizontal, Vertical | Flex direction. |
| Justify | select | `flex-start` | Start, Center, End, Space Between, Space Around | Main axis alignment. |
| Align | select | `stretch` | Stretch, Start, Center, End | Cross axis alignment. |
| Wrap | select | `nowrap` | No Wrap, Wrap | Whether children wrap. |
| Gap | text | `12px` | — | Space between columns. |

**Column traits** (`atd-column`):
| Trait | Type | Default | Description |
|-------|------|---------|-------------|
| Flex | text | `1` | CSS flex shorthand (e.g. `1`, `2`, `0 0 200px`). |

**Default styles**:
- Row: `display: flex; gap: 12px; min-height: 60px`
- Column: `flex: 1; min-height: 60px; padding: 8px`

**Canvas display**: Empty columns show placeholder text.

---

### Container
| Property | Value |
|----------|-------|
| **Block label** | `Container` |
| **Component type** | `atd-container` |
| **Tag** | `<div>` |
| **Droppable** | Yes |

**Purpose**: A centered, max-width-constrained wrapper. Useful for keeping card
content from stretching too wide on desktop.

**Traits**:
| Trait | Type | Default | Description |
|-------|------|---------|-------------|
| Max Width | text | `800px` | Maximum width (e.g. `800px`, `90%`). |

**Default style**: `max-width: 800px; margin: 0 auto; padding: 16px; min-height: 60px`

**Canvas display**: Empty containers show placeholder text.

---

### Divider
| Property | Value |
|----------|-------|
| **Block label** | `Divider` |
| **Component type** | `atd-divider` |
| **Tag** | `<hr>` |
| **Droppable** | No |

**Purpose**: A horizontal rule for visual separation between sections.

**Traits**:
| Trait | Type | Default | Options | Description |
|-------|------|---------|---------|-------------|
| Style | select | `solid` | Solid, Dashed, Dotted | Line style. |
| Color | text | `#ccc` | — | Line color. |

**Default style**: `border: none; border-top: 1px solid #ccc; margin: 12px 0`

---

### Spacer
| Property | Value |
|----------|-------|
| **Block label** | `Spacer` |
| **Component type** | `atd-spacer` |
| **Tag** | `<div>` |
| **Droppable** | No |

**Purpose**: An empty block that adds vertical space between elements.

**Traits**:
| Trait | Type | Default | Description |
|-------|------|---------|-------------|
| Height | text | `24px` | The spacer height (e.g. `24px`, `2em`). |

**Default style**: `height: 24px`

**Canvas display**: Shows a subtle diagonal stripe pattern so it's visible in
the editor.

---

## Basic HTML Components

Standard HTML elements for content.

### Text
| Property | Value |
|----------|-------|
| **Block label** | `Text` |
| **Component type** | `text` (GrapeJS built-in) |
| **Tag** | `<div>` |
| **Droppable** | No (inline editable) |

**Purpose**: An editable text block. Double-click to edit the text content
directly in the canvas.

**Traits**: Standard GrapeJS text traits (id, title).

---

### Heading
| Property | Value |
|----------|-------|
| **Block label** | `Heading` |
| **Tag** | `<h2>` |

**Purpose**: A heading element. Content is editable in the canvas. Change the
heading level via the Style panel or by editing the tag.

---

### Image
| Property | Value |
|----------|-------|
| **Block label** | `Image` |
| **Component type** | `image` (GrapeJS built-in) |

**Purpose**: An image element. When dropped, GrapeJS opens an image picker.

**Traits**: `src` (image URL), `alt` (alternative text), `title`.

---

### Link
| Property | Value |
|----------|-------|
| **Block label** | `Link` |
| **Component type** | `link` (GrapeJS built-in) |
| **Tag** | `<a>` |

**Purpose**: A hyperlink. Content is editable.

**Traits**: `href` (URL), `target` (`_blank`, `_self`, etc.), `title`.

---

### List
| Property | Value |
|----------|-------|
| **Block label** | `List` |
| **Tag** | `<ul>` |

**Purpose**: An unordered list with three items. Items are editable in the canvas.

---

## Right Panel Tabs

### Styles
Shows CSS style properties for the selected component, organized in sectors:
- **Typography**: font-family, font-size, font-weight, letter-spacing, color,
  line-height, text-align, text-decoration, text-transform
- **Layout**: display, position, flex-direction, justify-content, align-items,
  flex-wrap, flex-basis, order, gap, width, height, max-width, min-height, overflow
- **Spacing**: padding, margin
- **Background**: background-color, background-image, background-size
- **Borders**: border-radius, border, box-shadow

### Traits
Shows component-specific properties. For Anki components this includes field
names, cloze indices, etc. For layout components this includes display mode,
flex direction, gap, and other layout controls.

### Layers
Shows the component tree hierarchy, similar to a DOM inspector. Click any layer
to select that component in the canvas.

---

## Toolbar Buttons

| Button | Action | Notes |
|--------|--------|-------|
| 💾 Save | Saves the current template to Anki | Requires bridge connection |
| ↶ Undo | Undoes the last editor action | Also Ctrl+Z |
| ↷ Redo | Redoes the last undone action | Also Ctrl+Shift+Z |
| 📤 Export | Opens a modal with the full HTML+CSS output | |
| 🖥 Desktop | Switches canvas to full-width desktop view | Shows active state |
| ⊟ Tablet | Switches canvas to 768px tablet view | Shows active state |
| 📱 Mobile | Switches canvas to 375px mobile view | Shows active state |
| B (Borders) | Toggles component border outlines in canvas | Toggles on/off with active state |

## Front / Back Toggle

Switches between front and back template editing. Each side maintains its own
independent GrapeJS project state (components, styles, layout). Switching sides
saves the current state and restores the other side. Works in standalone mode
even without a template loaded.
