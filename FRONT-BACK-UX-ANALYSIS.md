# Front vs Back Card UI Configuration - UX Analysis

## Current State

The application has a **single unified canvas** where users drag components to build template layouts. Currently, it doesn't distinguish between:
- **Front side** (question/prompt shown first)
- **Back side** (answer revealed after user selects "Show Answer")

## The Problem

In Anki's template system:
- Each template has **two separate HTML sections**:
  1. **Front template** - What's shown before the answer is revealed
  2. **Back template** - What's shown after the answer is revealed
  
The back template typically includes `{{FrontSide}}` to show the front content plus additional answer content.

Currently, the designer has **no way** to:
1. **Separate** front and back editing
2. **Switch** between front/back views while designing
3. **Preview** how the card looks on each side
4. **Manage** different component structures for each side

## Example: "Basic" Note Type

**Front Template (HTML):**
```html
{{Front}}
```
Shows only the front field.

**Back Template (HTML):**
```html
{{FrontSide}}
<hr id=answer>
{{Back}}
```
Shows the front side, then a divider, then the back field.

## Proposed Solutions

### Option 1: Tabs Interface (RECOMMENDED)
**Best UX - Explicit & Clear**

```
┌─ Template Selector ──────────────────────────┐
│ [Japanese Vocabulary Model ▼]                 │
└──────────────────────────────────────────────┘

┌─ Tab Bar ────────────────────────────────────┐
│  [Front Tab] [Back Tab] [Preview]            │
└──────────────────────────────────────────────┘

┌─ Canvas Area ────────────────────────────────┐
│                                              │
│  [Sidebar] [Canvas] [Properties]             │
│                                              │
│  (Front or Back content depends on tab)      │
│                                              │
└──────────────────────────────────────────────┘
```

**Advantages:**
- ✅ Clear visual separation
- ✅ Intuitive for users familiar with design tools
- ✅ Easy to implement in code
- ✅ Can show which side is "active"
- ✅ Room for "Preview" tab showing both sides

**Implementation:**
```javascript
// Tab structure
<div class="tab-bar">
  <button class="tab" data-side="front" onclick="switchSide('front')">
    📄 Front
  </button>
  <button class="tab" data-side="back" onclick="switchSide('back')">
    📄 Back
  </button>
  <button class="tab" data-mode="preview" onclick="switchMode('preview')">
    👁 Preview
  </button>
</div>

// State management
let currentSide = 'front'; // 'front' or 'back'
let frontComponents = [];
let backComponents = [];
```

---

### Option 2: Split View
**Advanced - Shows Both Simultaneously**

```
┌─ Template Selector ──────────────────────────┐

┌─ Front Side ─────────┬─ Back Side ──────────┐
│ [Sidebar|Canvas|Props] [Sidebar|Canvas|Props] │
│                       │                      │
│  Front components    │  Back components     │
│                       │                      │
└──────────────────────┴──────────────────────┘
```

**Advantages:**
- ✅ See both sides at once
- ✅ Direct comparison
- ✅ Easier to manage FrontSide relationship

**Disadvantages:**
- ❌ Very cramped interface
- ❌ Hard to see properties panels
- ❌ More complex code
- ❌ Overwhelming for users

---

### Option 3: Dropdown/Mode Selection
**Simple but Hidden**

```
┌─ Header ───────────────────────────────────┐
│ Template: [Japanese Vocab ▼] Side: [Front ▼] │
└────────────────────────────────────────────┘
```

**Disadvantages:**
- ❌ Easy to miss or forget which side you're editing
- ❌ Not discoverable to new users
- ❌ Takes up header space
- ❌ Less intuitive

---

## Recommended Implementation: Tabs

### Structure

```html
<div class="designer-view">
  <!-- Template selector + info -->
  <div class="template-info">
    <select id="templateSelect">...</select>
    <span class="note-type-info">
      Note Type: {{noteTypeName}}, 
      Template: {{templateName}}
    </span>
  </div>

  <!-- Tab Bar -->
  <div class="side-tabs">
    <button class="tab-btn active" data-side="front">
      📄 Front
    </button>
    <button class="tab-btn" data-side="back">
      📄 Back
    </button>
    <button class="tab-btn" data-mode="preview">
      👁 Preview
    </button>
  </div>

  <!-- Content Area (changes based on active tab) -->
  <div class="main-container">
    <!-- Sidebar, Canvas, Properties -->
  </div>
</div>
```

### Data Structure

```javascript
// Template object with front and back
const template = {
  id: "1766752621177:Card 1",
  name: "[API Test Card] Card 1",
  noteTypeId: 1766752621177,
  noteTypeName: "API Test Card",
  templateName: "Card 1",
  templateData: {
    name: "Card 1",
    ordinal: 0,
    front: "<html>...",
    back: "<html>...",
    css: ".card { ... }"
  },
  // Designer state
  designerState: {
    front: {
      components: [],    // Component tree for front
      selected: null,    // Currently selected component
      history: []        // Undo/redo for front
    },
    back: {
      components: [],    // Component tree for back
      selected: null,
      history: []
    }
  }
};
```

### Key Features

1. **State Switching**
   ```javascript
   function switchSide(side) {
     currentSide = side; // 'front' or 'back'
     saveCurrentState(); // Save current side's components
     loadSideComponents(side); // Load the other side
     updateCanvas(); // Redraw
   }
   ```

2. **Preview Mode** - Show both front and back
   ```javascript
   function enterPreviewMode() {
     // Split canvas or show comparison
     // Render both front and back components
   }
   ```

3. **Undo/Redo Per Side**
   - Maintain separate history for each side
   - Or maintain global history with side tracking

4. **FrontSide Reference**
   - Special handling for {{FrontSide}} component
   - Only available in back template
   - Shows visual indicator that it includes front content

---

## CSS Implementation

```css
/* Tab Bar */
.side-tabs {
  display: flex;
  gap: 8px;
  padding: 8px 16px;
  background: #f0f0f0;
  border-bottom: 1px solid #ddd;
  z-index: 10;
}

.tab-btn {
  padding: 8px 16px;
  border: 1px solid transparent;
  border-radius: 4px 4px 0 0;
  background: transparent;
  cursor: pointer;
  font-weight: 500;
  color: #666;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  background: rgba(0,0,0,0.05);
  color: #333;
}

.tab-btn.active {
  background: white;
  color: #2c3e50;
  border: 1px solid #ddd;
  border-bottom-color: white;
  position: relative;
  z-index: 1;
}

/* Visual indicator for current side */
.canvas::before {
  content: attr(data-side);
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 8px;
  background: rgba(52, 152, 219, 0.1);
  border-radius: 4px;
  font-size: 12px;
  color: #3498db;
  font-weight: 500;
  text-transform: uppercase;
}
```

---

## Implementation Priority

### Phase 1 (MVP) - Essential
- [x] Template selection (DONE)
- [ ] Tabs for front/back switching
- [ ] Save front/back state separately
- [ ] Canvas shows which side is active

### Phase 2 - Enhancement
- [ ] Preview mode showing both sides
- [ ] {{FrontSide}} component for back template
- [ ] Side-specific validation (warnings if front is empty)

### Phase 3 - Polish
- [ ] Keyboard shortcuts to switch tabs
- [ ] Persistent tab selection per template
- [ ] Better FrontSide visualization

---

## User Flow Example

1. User selects "Japanese Vocabulary Model" template
2. "Front" tab is active by default
3. User drags components to build front (Word, Reading, etc.)
4. User clicks "Back" tab
5. Designer loads back-side components
6. User builds back side (adds Definition, Examples)
7. User adds {{FrontSide}} component to show front content
8. User clicks "Preview" to see full card
9. User saves the design

---

## Notes

- **Persistence**: Store front/back component state in `designerState` 
- **History**: Consider shared undo/redo or per-side history
- **Validation**: Warn if front side is empty
- **FrontSide**: Special component that only works in back template
- **CSS**: Share CSS between front and back (one global CSS editor)
