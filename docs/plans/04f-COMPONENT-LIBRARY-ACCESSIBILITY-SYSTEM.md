# 04f - Component Library: Accessibility

> **Purpose**: Define GrapeJS blocks for Accessibility components.
> **Target Agent**: Claude Haiku 4.5 chat agent in VS Code
> **Date**: January 11, 2026
> **Updated**: Based on COMPONENT-AUDIT.md - removed System, Motion, and Advanced components

---

## Accessibility Components

### `web/blocks/accessibility.js`

```javascript
/**
 * Accessibility Component Blocks
 */

export function registerAccessibilityBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Accessibility';
    
    // Skip Link
    bm.add('skip-link', {
        label: 'Skip Link',
        category,
        content: {
            tagName: 'a',
            classes: ['atd-skip-link'],
            content: 'Skip to main content',
            attributes: { href: '#main-content' },
            style: { position: 'absolute', top: '-40px', left: '0', padding: '8px 16px', background: '#1976d2', color: '#fff', 'z-index': '9999', 'text-decoration': 'none' }
        }
    });
    
    // Screen Reader Only Text
    bm.add('sr-only', {
        label: 'SR-Only Text',
        category,
        content: {
            tagName: 'span',
            classes: ['atd-sr-only'],
            content: 'Screen reader only text',
            style: { position: 'absolute', width: '1px', height: '1px', padding: '0', margin: '-1px', overflow: 'hidden', clip: 'rect(0,0,0,0)', 'white-space': 'nowrap', border: '0' }
        }
    });
    
    // Live Region
    bm.add('live-region', {
        label: 'Live Region',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-live-region'],
            attributes: { 'aria-live': 'polite', 'aria-atomic': 'true' },
            style: { padding: '12px 16px', background: '#e3f2fd', 'border-radius': '8px', border: '1px dashed #1976d2' },
            components: [{ tagName: 'p', content: 'Live region: Content updates will be announced to screen readers.', style: { margin: '0' } }]
        }
    });
    
    // Focus Trap Container
    bm.add('focus-trap', {
        label: 'Focus Trap',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-focus-trap'],
            attributes: { 'data-focus-trap': 'true' },
            style: { padding: '20px', background: '#f5f5f5', 'border-radius': '12px', border: '2px solid #1976d2' },
            components: [
                { tagName: 'p', content: 'Focus is trapped within this container.', style: { margin: '0 0 16px' } },
                { tagName: 'button', content: 'Button 1', style: { 'margin-right': '8px', padding: '8px 16px', border: '1px solid #e0e0e0', 'border-radius': '4px', background: '#fff' } },
                { tagName: 'button', content: 'Button 2', style: { padding: '8px 16px', border: 'none', 'border-radius': '4px', background: '#1976d2', color: '#fff' } }
            ]
        }
    });
    
    // Accessible Form Field
    bm.add('accessible-field', {
        label: 'Accessible Field',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-accessible-field'],
            components: [
                { tagName: 'label', content: 'Email Address', attributes: { for: 'email-input' }, style: { display: 'block', 'margin-bottom': '4px', 'font-weight': '500' } },
                { tagName: 'input', attributes: { type: 'email', id: 'email-input', 'aria-describedby': 'email-hint', 'aria-required': 'true' }, style: { width: '100%', padding: '12px', border: '1px solid #e0e0e0', 'border-radius': '6px', 'box-sizing': 'border-box' } },
                { tagName: 'span', content: 'We\'ll never share your email.', attributes: { id: 'email-hint' }, style: { display: 'block', 'margin-top': '4px', color: '#666', 'font-size': '13px' } }
            ]
        }
    });
    
    // Error Message (Accessible)
    bm.add('accessible-error', {
        label: 'Error Message',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-error-message'],
            attributes: { role: 'alert', 'aria-live': 'assertive' },
            style: { display: 'flex', gap: '8px', padding: '12px 16px', background: '#ffebee', 'border-radius': '8px', color: '#c62828' },
            components: [
                { tagName: 'span', content: '⚠️', attributes: { 'aria-hidden': 'true' } },
                { tagName: 'span', content: 'Please enter a valid email address.' }
            ]
        }
    });
    
    // Landmark Region
    bm.add('landmark-main', {
        label: 'Main Landmark',
        category,
        content: {
            tagName: 'main',
            classes: ['atd-main'],
            attributes: { id: 'main-content', role: 'main' },
            style: { padding: '20px', background: '#fafafa', 'border-radius': '8px', border: '1px dashed #999' },
            components: [{ tagName: 'p', content: 'Main content area (landmark region)', style: { margin: '0', color: '#666' } }]
        }
    });
    
    // Navigation Landmark
    bm.add('landmark-nav', {
        label: 'Nav Landmark',
        category,
        content: {
            tagName: 'nav',
            classes: ['atd-nav'],
            attributes: { 'aria-label': 'Main navigation' },
            style: { padding: '16px', background: '#f5f5f5', 'border-radius': '8px' },
            components: [
                { tagName: 'ul', style: { display: 'flex', gap: '16px', 'list-style': 'none', padding: '0', margin: '0' }, components: [
                    { tagName: 'li', components: [{ tagName: 'a', content: 'Home', attributes: { href: '#' } }] },
                    { tagName: 'li', components: [{ tagName: 'a', content: 'About', attributes: { href: '#' } }] },
                    { tagName: 'li', components: [{ tagName: 'a', content: 'Contact', attributes: { href: '#' } }] }
                ]}
            ]
        }
    });
    
    // High Contrast Button
    bm.add('high-contrast-btn', {
        label: 'High Contrast Btn',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-high-contrast'],
            content: 'High Contrast Button',
            style: { padding: '12px 24px', border: '3px solid #000', 'border-radius': '8px', background: '#fff', color: '#000', 'font-weight': '700', 'font-size': '16px', cursor: 'pointer' }
        }
    });
    
    // Focus Indicator Demo
    bm.add('focus-indicator', {
        label: 'Focus Indicator',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-focus-demo'],
            content: 'Focus Me (Tab)',
            style: { padding: '12px 24px', border: '2px solid #1976d2', 'border-radius': '8px', background: '#fff', color: '#1976d2', cursor: 'pointer', outline: '3px solid transparent', 'outline-offset': '2px' }
        }
}
```

---

## Removed Components

The following components are **NOT** needed for Anki templates:

### System Components (REMOVED)
- Loading Overlay
- Maintenance Page
- 404 Error Page
- Cookie Consent Banner
- Offline Indicator
- Version Badge
- Debug Panel
- Print Area

**Reason**: These are for web applications and admin interfaces, not flashcard templates.

### Motion & Animation Components (REMOVED)
- Fade Container
- Slide Container
- Scale Container
- Rotate Container
- Bounce Element
- Pulse Effect
- Shake Effect
- Stagger Group
- Parallax Container
- Scroll Reveal
- All animation utilities

**Reason**: While CSS animations can be useful, dedicated animation containers are not needed. Use CSS animations directly on components instead.

### Advanced Components (REMOVED)
- Custom HTML Block
- Embed Container
- Script Placeholder

**Reason**: These are development utilities, not user-facing components. Templates should use concrete components.

---

## Recommendations for Study Templates

### For Visual Feedback:
Use **Accessibility components** (high-contrast buttons, focus indicators) combined with simple CSS transitions.

### For Progress Tracking:
Use **Charts** (04e) to display study statistics.

### For Interaction:
Use **Buttons** (04b) bound to AnkiJSApi behaviors with proper accessibility attributes.

---

## Component Registry

Update the master block registration in `web/blocks/index.js`:

```javascript
/**
 * Master Block Registration
 * Import and register block categories (Updated for Anki)
 */

import { registerStudyActionBarBlocks } from './layout.js';         // 04a: Study-specific bar
import { registerInputBlocks } from './inputs.js';                   // 04b: Consolidate: 3 + 4 + 3 + 3 + 5
import { registerDataBlocks } from './data.js';                       // 04c: Data display, feedback, overlays
import { registerChartBlocks } from './charts.js';                   // 04e: Charts & visualization
import { registerAccessibilityBlocks } from './accessibility.js';    // 04f: Accessibility only

/**
 * Register all blocks with the GrapeJS editor
 * @param {Object} editor - GrapeJS editor instance
 */
export function registerAllBlocks(editor) {
    registerStudyActionBarBlocks(editor);
    registerInputBlocks(editor);
    registerDataBlocks(editor);
    registerChartBlocks(editor);
    registerAccessibilityBlocks(editor);
    
    console.log('[ATD] All Anki-optimized blocks registered successfully');
}
```

---

## Summary: Anki Component Library

**Final Count: 112 Components across 5 files**

| Document | Components | Count |
|----------|-----------|-------|
| 04a | Study Action Bar, Layout, Tabs, Stepper, Anchor Link | 5 |
| 04b | Text/Textarea/Password + Checkbox/Radio/Toggle/Dropdown + Date/Slider/Rating + Form/FieldGroup/Required + Btn Variants | 18 |
| 04c | Data Display, Feedback, Overlays | ~45 |
| 04e | Charts & Visualization | 13 |
| 04f | Accessibility | 10 |
| **Total** | | **~112** |

**Removed: 97 components**
- Search & Filter (9)
- Commerce (11)
- Social (11)
- System (8)
- Motion (10)
- Advanced (3)
- Redundant inputs/buttons (45+)
