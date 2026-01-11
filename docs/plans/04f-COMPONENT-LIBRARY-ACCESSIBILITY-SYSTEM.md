# 04f - Component Library: Accessibility, System, Motion & Advanced

> **Purpose**: Define GrapeJS blocks for Accessibility, System, Motion, and Advanced/Specialized components.
> **Target Agent**: Claude Haiku 4.5 chat agent in VS Code
> **Date**: January 11, 2026

---

## 12. Accessibility Components

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
    });
}
```

---

## 13. System Components

### `web/blocks/system.js`

```javascript
/**
 * System & Utility Component Blocks
 */

export function registerSystemBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'System';
    
    // Loading Overlay
    bm.add('loading-overlay', {
        label: 'Loading Overlay',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-loading-overlay'],
            style: { position: 'fixed', top: '0', left: '0', right: '0', bottom: '0', background: 'rgba(255,255,255,0.9)', display: 'flex', 'flex-direction': 'column', 'align-items': 'center', 'justify-content': 'center', 'z-index': '9999' },
            components: [
                { tagName: 'div', content: '⟳', style: { 'font-size': '48px', color: '#1976d2', 'margin-bottom': '16px' } },
                { tagName: 'p', content: 'Loading...', style: { margin: '0', color: '#666' } }
            ]
        }
    });
    
    // Maintenance Page
    bm.add('maintenance-page', {
        label: 'Maintenance Page',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-maintenance'],
            style: { 'min-height': '400px', display: 'flex', 'flex-direction': 'column', 'align-items': 'center', 'justify-content': 'center', 'text-align': 'center', padding: '40px' },
            components: [
                { tagName: 'div', content: '🔧', style: { 'font-size': '64px', 'margin-bottom': '24px' } },
                { tagName: 'h1', content: 'Under Maintenance', style: { margin: '0 0 16px' } },
                { tagName: 'p', content: 'We\'re making some improvements. Please check back soon.', style: { color: '#666', 'max-width': '400px' } }
            ]
        }
    });
    
    // 404 Error Page
    bm.add('error-404', {
        label: '404 Page',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-404'],
            style: { 'min-height': '400px', display: 'flex', 'flex-direction': 'column', 'align-items': 'center', 'justify-content': 'center', 'text-align': 'center', padding: '40px' },
            components: [
                { tagName: 'h1', content: '404', style: { 'font-size': '96px', margin: '0', color: '#e0e0e0' } },
                { tagName: 'h2', content: 'Page Not Found', style: { margin: '0 0 16px' } },
                { tagName: 'p', content: 'The page you\'re looking for doesn\'t exist.', style: { color: '#666', 'margin-bottom': '24px' } },
                { tagName: 'a', content: 'Go Home', attributes: { href: '#' }, style: { padding: '12px 24px', background: '#1976d2', color: '#fff', 'text-decoration': 'none', 'border-radius': '6px' } }
            ]
        }
    });
    
    // Cookie Consent Banner
    bm.add('cookie-banner', {
        label: 'Cookie Banner',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-cookie-banner'],
            style: { position: 'fixed', bottom: '0', left: '0', right: '0', padding: '16px 20px', background: '#333', color: '#fff', display: 'flex', 'align-items': 'center', 'justify-content': 'space-between', 'flex-wrap': 'wrap', gap: '12px' },
            components: [
                { tagName: 'p', content: 'We use cookies to improve your experience. By continuing, you agree to our cookie policy.', style: { margin: '0', flex: '1' } },
                { tagName: 'div', style: { display: 'flex', gap: '8px' }, components: [
                    { tagName: 'button', content: 'Accept', style: { padding: '8px 16px', border: 'none', 'border-radius': '4px', background: '#4caf50', color: '#fff', cursor: 'pointer' } },
                    { tagName: 'button', content: 'Decline', style: { padding: '8px 16px', border: '1px solid #fff', 'border-radius': '4px', background: 'transparent', color: '#fff', cursor: 'pointer' } }
                ]}
            ]
        }
    });
    
    // Offline Indicator
    bm.add('offline-indicator', {
        label: 'Offline Indicator',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-offline'],
            style: { display: 'flex', 'align-items': 'center', 'justify-content': 'center', gap: '8px', padding: '8px 16px', background: '#ff9800', color: '#fff' },
            components: [
                { tagName: 'span', content: '📡' },
                { tagName: 'span', content: 'You are currently offline' }
            ]
        }
    });
    
    // Version Badge
    bm.add('version-badge', {
        label: 'Version Badge',
        category,
        content: {
            tagName: 'span',
            classes: ['atd-version'],
            content: 'v2.1.0',
            style: { padding: '4px 8px', background: '#e3f2fd', color: '#1976d2', 'border-radius': '4px', 'font-size': '12px', 'font-family': 'monospace' }
        }
    });
    
    // Debug Panel
    bm.add('debug-panel', {
        label: 'Debug Panel',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-debug'],
            style: { padding: '16px', background: '#1e1e1e', color: '#d4d4d4', 'border-radius': '8px', 'font-family': 'monospace', 'font-size': '13px' },
            components: [
                { tagName: 'div', style: { display: 'flex', 'justify-content': 'space-between', 'margin-bottom': '12px' }, components: [{ tagName: 'span', content: 'DEBUG PANEL', style: { color: '#ff9800' } }, { tagName: 'button', content: '✕', style: { border: 'none', background: 'none', color: '#fff', cursor: 'pointer' } }] },
                { tagName: 'pre', content: '{\n  "user": "john_doe",\n  "session": "abc123",\n  "timestamp": "2024-01-11T10:30:00Z"\n}', style: { margin: '0', 'white-space': 'pre-wrap' } }
            ]
        }
    });
    
    // Print Area
    bm.add('print-area', {
        label: 'Print Area',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-print-area'],
            attributes: { 'data-printable': 'true' },
            style: { padding: '20px', border: '2px dashed #999', 'border-radius': '8px' },
            components: [
                { tagName: 'p', content: '🖨️ This content will be included when printing.', style: { margin: '0', color: '#666' } }
            ]
        }
    });
}
```

---

## 14. Motion & Animation Components

### `web/blocks/motion.js`

```javascript
/**
 * Motion & Animation Component Blocks
 * These provide visual structure for animated elements.
 * Actual animations should be added via CSS or JavaScript.
 */

export function registerMotionBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Motion';
    
    // Fade Container
    bm.add('fade-container', {
        label: 'Fade Container',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-fade'],
            attributes: { 'data-animation': 'fade' },
            style: { padding: '20px', background: '#f5f5f5', 'border-radius': '8px', border: '1px dashed #1976d2' },
            components: [{ tagName: 'p', content: 'Content will fade in/out', style: { margin: '0', color: '#666' } }]
        }
    });
    
    // Slide Container
    bm.add('slide-container', {
        label: 'Slide Container',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-slide'],
            attributes: { 'data-animation': 'slide', 'data-direction': 'left' },
            style: { padding: '20px', background: '#e3f2fd', 'border-radius': '8px', border: '1px dashed #1976d2' },
            components: [{ tagName: 'p', content: 'Content will slide in', style: { margin: '0', color: '#1976d2' } }]
        }
    });
    
    // Scale Container
    bm.add('scale-container', {
        label: 'Scale Container',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-scale'],
            attributes: { 'data-animation': 'scale' },
            style: { padding: '20px', background: '#fff3e0', 'border-radius': '8px', border: '1px dashed #ff9800' },
            components: [{ tagName: 'p', content: 'Content will scale up/down', style: { margin: '0', color: '#ff9800' } }]
        }
    });
    
    // Rotate Container
    bm.add('rotate-container', {
        label: 'Rotate Container',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-rotate'],
            attributes: { 'data-animation': 'rotate' },
            style: { width: '100px', height: '100px', display: 'flex', 'align-items': 'center', 'justify-content': 'center', background: '#e8f5e9', 'border-radius': '8px', border: '1px dashed #4caf50' },
            components: [{ tagName: 'span', content: '🔄', style: { 'font-size': '32px' } }]
        }
    });
    
    // Bounce Effect
    bm.add('bounce-element', {
        label: 'Bounce Element',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-bounce'],
            attributes: { 'data-animation': 'bounce' },
            style: { display: 'inline-block', padding: '16px 24px', background: '#1976d2', color: '#fff', 'border-radius': '8px' },
            components: [{ tagName: 'span', content: 'Bouncing Element' }]
        }
    });
    
    // Pulse Effect
    bm.add('pulse-element', {
        label: 'Pulse Element',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-pulse'],
            attributes: { 'data-animation': 'pulse' },
            style: { width: '60px', height: '60px', 'border-radius': '50%', background: '#d32f2f', display: 'flex', 'align-items': 'center', 'justify-content': 'center' },
            components: [{ tagName: 'span', content: '❤️', style: { 'font-size': '24px' } }]
        }
    });
    
    // Shake Effect
    bm.add('shake-element', {
        label: 'Shake Element',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-shake'],
            attributes: { 'data-animation': 'shake' },
            content: '⚠️ Shake on Error',
            style: { padding: '12px 24px', border: '2px solid #d32f2f', 'border-radius': '8px', background: '#fff', color: '#d32f2f', cursor: 'pointer' }
        }
    });
    
    // Stagger Group
    bm.add('stagger-group', {
        label: 'Stagger Group',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-stagger-group'],
            attributes: { 'data-animation': 'stagger', 'data-delay': '100' },
            style: { display: 'flex', gap: '8px' },
            components: [
                { tagName: 'div', classes: ['atd-stagger-item'], style: { width: '50px', height: '50px', background: '#1976d2', 'border-radius': '8px' } },
                { tagName: 'div', classes: ['atd-stagger-item'], style: { width: '50px', height: '50px', background: '#42a5f5', 'border-radius': '8px' } },
                { tagName: 'div', classes: ['atd-stagger-item'], style: { width: '50px', height: '50px', background: '#90caf9', 'border-radius': '8px' } },
                { tagName: 'div', classes: ['atd-stagger-item'], style: { width: '50px', height: '50px', background: '#bbdefb', 'border-radius': '8px' } }
            ]
        }
    });
    
    // Parallax Container
    bm.add('parallax', {
        label: 'Parallax',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-parallax'],
            attributes: { 'data-parallax': 'true', 'data-speed': '0.5' },
            style: { height: '200px', background: 'linear-gradient(135deg, #1976d2, #42a5f5)', display: 'flex', 'align-items': 'center', 'justify-content': 'center', color: '#fff' },
            components: [{ tagName: 'h2', content: 'Parallax Section', style: { margin: '0' } }]
        }
    });
    
    // Reveal on Scroll
    bm.add('scroll-reveal', {
        label: 'Scroll Reveal',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-scroll-reveal'],
            attributes: { 'data-reveal': 'true', 'data-threshold': '0.5' },
            style: { padding: '40px', background: '#f5f5f5', 'border-radius': '12px', 'text-align': 'center' },
            components: [
                { tagName: 'h3', content: 'Revealed on Scroll', style: { margin: '0 0 8px' } },
                { tagName: 'p', content: 'This content appears when scrolled into view.', style: { margin: '0', color: '#666' } }
            ]
        }
    });
}
```

---

## 15. Advanced & Specialized Components

### `web/blocks/advanced.js`

```javascript
/**
 * Advanced & Specialized Component Blocks
 * These are complex or niche components for specific use cases.
 */

export function registerAdvancedBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Advanced';
    
    // Custom HTML Block
    bm.add('custom-html', {
        label: 'Custom HTML',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-custom-html'],
            style: { padding: '20px', background: '#fafafa', 'border-radius': '8px', border: '1px dashed #999' },
            components: [
                { tagName: 'p', content: '<!-- Add your custom HTML here -->', style: { margin: '0', 'font-family': 'monospace', color: '#666' } }
            ]
        }
    });
    
    // Embed Container
    bm.add('embed-container', {
        label: 'Embed Container',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-embed'],
            style: { position: 'relative', 'padding-bottom': '56.25%', height: '0', overflow: 'hidden', background: '#000', 'border-radius': '8px' },
            components: [
                { tagName: 'div', style: { position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', color: '#fff' }, components: [{ tagName: 'p', content: 'Embed content here (iframe, video, etc.)', style: { margin: '0' } }] }
            ]
        }
    });
    
    // Script Placeholder
    bm.add('script-placeholder', {
        label: 'Script Placeholder',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-script-placeholder'],
            attributes: { 'data-script-id': '' },
            style: { padding: '16px', background: '#fff3e0', 'border-radius': '8px', border: '1px dashed #ff9800' },
            components: [
                { tagName: 'p', content: '⚠️ Script Placeholder - Configure script ID in properties', style: { margin: '0', color: '#e65100' } }
            ]
        }
    });
}
```

---

## Block Registration Summary

### `web/blocks/index.js`

```javascript
/**
 * Master Block Registration
 * Import and register all block categories
 */

import { registerLayoutBlocks } from './layout.js';
import { registerNavigationBlocks } from './navigation.js';
import { registerInputBlocks } from './inputs.js';
import { registerButtonBlocks } from './buttons.js';
import { registerDataBlocks } from './data.js';
import { registerFeedbackBlocks } from './feedback.js';
import { registerOverlayBlocks } from './overlays.js';
import { registerSearchBlocks } from './search.js';
import { registerCommerceBlocks } from './commerce.js';
import { registerSocialBlocks } from './social.js';
import { registerChartBlocks } from './charts.js';
import { registerAccessibilityBlocks } from './accessibility.js';
import { registerSystemBlocks } from './system.js';
import { registerMotionBlocks } from './motion.js';
import { registerAdvancedBlocks } from './advanced.js';

/**
 * Register all blocks with the GrapeJS editor
 * @param {Object} editor - GrapeJS editor instance
 */
export function registerAllBlocks(editor) {
    registerLayoutBlocks(editor);
    registerNavigationBlocks(editor);
    registerInputBlocks(editor);
    registerButtonBlocks(editor);
    registerDataBlocks(editor);
    registerFeedbackBlocks(editor);
    registerOverlayBlocks(editor);
    registerSearchBlocks(editor);
    registerCommerceBlocks(editor);
    registerSocialBlocks(editor);
    registerChartBlocks(editor);
    registerAccessibilityBlocks(editor);
    registerSystemBlocks(editor);
    registerMotionBlocks(editor);
    registerAdvancedBlocks(editor);
    
    console.log('[ATD] All blocks registered successfully');
}
```

---

## Component Count Summary

| Document | Category | Count |
|----------|----------|-------|
| 04a | Layout & Structure | 22 |
| 04a | Navigation | 15 |
| 04b | Basic Inputs | 8 |
| 04b | Selection Inputs | 10 |
| 04b | Advanced Inputs | 11 |
| 04b | Form Structure | 8 |
| 04b | Buttons & Actions | 13 |
| 04c | Data Display | 20 |
| 04c | Feedback & Status | 16 |
| 04c | Overlays & Popups | 11 |
| 04d | Search & Filter | 9 |
| 04d | Commerce | 11 |
| 04e | Social | 11 |
| 04e | Charts & Data | 13 |
| 04f | Accessibility | 10 |
| 04f | System | 8 |
| 04f | Motion | 10 |
| 04f | Advanced | 3 |
| **Total** | | **209** |

---

## Next Document

See [05-CODE-STANDARDS.md](05-CODE-STANDARDS.md) for code review standards and quality guidelines.
