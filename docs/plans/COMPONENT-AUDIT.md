# Component Library Audit: Anki Template Suitability Analysis

> **Purpose**: Identify and categorize components that are unnecessary or non-functional for Anki flashcard templates.
> **Date**: January 11, 2026

---

## Executive Summary

After reviewing all 209 components across the 04a-04f plan files, **approximately 85-95 components (~40-45%)** are inappropriate for Anki templates. These fall into three main categories:

1. **E-Commerce/Shopping** - No purpose in flashcards
2. **Social Media** - Not applicable to learning cards
3. **Dynamic/Interactive Features** - Anki has no support for state management, form submission, real databases
4. **System/Meta Components** - Debugging/maintenance tools not needed in templates

---

## Detailed Breakdown

### 1. COMMERCE COMPONENTS (16 components) - **REMOVE ALL**

**File**: `04d-COMPONENT-LIBRARY-SEARCH-COMMERCE.md`

These are entirely incompatible with Anki flashcards:

| Component | Reason to Remove |
|-----------|------------------|
| product-card | E-commerce specific; no product data in Anki |
| price-display | No pricing system in Anki templates |
| quantity-selector | No shopping cart in flashcards |
| cart-item | No purchasing functionality |
| cart-summary | No order management |
| rating-stars | Could work (display only), but "review-card" is better |
| promo-code | No discount system in Anki |
| wishlist-button | No wishlist functionality in Anki |
| stock-status | Not applicable to flashcards |
| product-variants | No variant selection in templates |
| review-card | Product reviews; could be repurposed as "Comment Card" in social section |

**Recommendation**: Remove all 11 commerce components entirely.

---

### 2. SOCIAL MEDIA COMPONENTS (13 components) - **REMOVE MOST**

**File**: `04e-COMPONENT-LIBRARY-SOCIAL-CHARTS.md`

These assume social network features that don't exist in Anki:

| Component | Keep? | Reason |
|-----------|-------|--------|
| profile-card | ❌ | Anki doesn't support user profiles |
| social-stats | ❌ | No follower/post statistics in Anki |
| post-card | ❌ | Feed functionality not in Anki |
| comment | ⚠️ | Could work as generic text block (low value) |
| comment-input | ❌ | No form submission to backend |
| share-buttons | ❌ | No sharing mechanism in Anki |
| reaction-bar | ❌ | No reaction system in flashcards |
| follow-button | ❌ | No user management |
| user-list-item | ❌ | No user directory in Anki |
| notification-item | ⚠️ | Could be repurposed for Anki notifications |
| activity-item | ❌ | No activity feed in Anki |

**Recommendation**: Remove 10 components; repurpose 1-2 into generic messaging components.

---

### 3. SEARCH & FILTER COMPONENTS (10 components) - **REMOVE MOST**

**File**: `04d-COMPONENT-LIBRARY-SEARCH-COMMERCE.md`

These assume backend search/filtering that Anki doesn't provide:

| Component | Keep? | Reason |
|-----------|-------|--------|
| search-bar | ❌ | No search backend in Anki templates |
| search-with-button | ❌ | No form submission; button does nothing |
| filter-chips | ❌ | No filtering mechanism; purely visual |
| filter-panel | ❌ | Selects/dropdowns with no backend |
| sort-dropdown | ❌ | No sorting backend |
| tag-input | ⚠️ | Could work for Anki tag display (already have `anki-field`) |
| active-filters | ❌ | No active filtering state |
| autocomplete | ❌ | No data source for suggestions |
| results-count | ❌ | No search results in Anki |

**Recommendation**: Remove all 9 components. If needed, tags can be displayed with simpler components.

---

### 4. DATA VISUALIZATION / CHARTS (16 components) - **CONDITIONAL KEEP**

**File**: `04e-COMPONENT-LIBRARY-SOCIAL-CHARTS.md`

Charts have **limited but valid use** in Anki (e.g., mathematics, statistics templates):

| Component | Keep? | Use Case |
|-----------|-------|----------|
| bar-chart | ✅ | Math/statistics study |
| line-chart | ✅ | Trend visualization |
| pie-chart | ✅ | Proportional data display |
| donut-chart | ⚠️ | Duplicate of pie-chart; remove |
| stat-card | ✅ | Display metrics/KPIs |
| kpi-display | ⚠️ | Duplicate of stat-card; consolidate |
| sparkline | ✅ | Compact trend display |
| progress-gauge | ✅ | Goal/completion display |
| comparison-bar | ✅ | Side-by-side data comparison |
| data-table | ✅ | Tabular data (good alternative to HTML tables) |
| chart-legend | ✅ | Chart legend |
| timeline | ✅ | Historical/chronological data |

**Issue**: Most charts require **JavaScript rendering** (e.g., using Chart.js). Anki supports JS, but:
- Chart libraries must be referenced from CDN or included
- Complex state management issues
- Mobile rendering may be unreliable on AnkiDroid

**Recommendation**: **KEEP** but mark as "Advanced - Requires JS Library". Add documentation for Chart.js integration.

---

### 5. SYSTEM & META COMPONENTS (8 components) - **REMOVE MOST**

**File**: `04f-COMPONENT-LIBRARY-ACCESSIBILITY-SYSTEM.md`

These are debugging/development tools, not flashcard content:

| Component | Keep? | Reason |
|-----------|-------|--------|
| loading-overlay | ❌ | No loading states in Anki templates |
| maintenance-page | ❌ | Not a template component |
| error-404 | ❌ | Not applicable to Anki |
| cookie-banner | ❌ | No cookies/privacy in Anki |
| offline-indicator | ❌ | No online/offline switching |
| version-badge | ❌ | Not for flashcard content |
| debug-panel | ❌ | Developer tool, not user content |
| print-area | ⚠️ | Could be useful (e.g., `@media print`) |

**Recommendation**: Remove all except possibly `print-area` (which is just CSS annotation).

---

### 6. MOTION & ANIMATION COMPONENTS (6 components) - **CONDITIONAL KEEP**

**File**: `04f-COMPONENT-LIBRARY-ACCESSIBILITY-SYSTEM.md`

Animations have **limited but valid use** in Anki:

| Component | Keep? | Use Case |
|-----------|-------|----------|
| fade-container | ✅ | Reveal answer with fade |
| slide-container | ✅ | Slide transitions |
| scale-container | ⚠️ | Minor visual effect; low value |
| rotate-container | ⚠️ | Rarely used; low value |
| bounce-element | ❌ | Too playful for serious learning |
| pulse-element | ⚠️ | Could highlight important content |
| shake-element | ❌ | Distracting; bad UX |
| stagger-group | ✅ | Sequential animations |
| parallax | ❌ | No scroll parallax in Anki cards |
| scroll-reveal | ❌ | No scroll triggering in Anki |

**Issues**:
- Animations can reduce performance on AnkiDroid
- Over-animation hurts learning effectiveness
- Some animations (shake, bounce) have poor accessibility

**Recommendation**: **KEEP** only basic animations (fade, slide, stagger). Document performance implications.

---

### 7. ACCESSIBILITY COMPONENTS (10 components) - **MIXED**

**File**: `04f-COMPONENT-LIBRARY-ACCESSIBILITY-SYSTEM.md`

Most are **wrappers for HTML semantics**, not visual components:

| Component | Keep? | Reason |
|-----------|-------|--------|
| skip-link | ❌ | No navigation to skip in flashcards |
| sr-only | ✅ | Useful for screen reader-only content |
| live-region | ⚠️ | Screen reader announcements; limited use |
| focus-trap | ❌ | Not needed in simple card templates |
| accessible-field | ✅ | Good semantic wrapper |
| accessible-error | ✅ | Error message handling |
| landmark-main | ✅ | `<main>` semantic wrapper |
| landmark-nav | ❌ | Navigation landmarks not in flashcards |
| high-contrast-btn | ⚠️ | Button variant; already covered |
| focus-indicator | ✅ | Visual focus state |

**Recommendation**: **KEEP** semantic wrappers; consolidate accessibility variants into main components.

---

### 8. NAVIGATION COMPONENTS (15 components) - **REMOVE MOST**

**File**: `04a-COMPONENT-LIBRARY-LAYOUT.md`

Most navigation assumes app/website context, not flashcards:

| Component | Keep? | Reason |
|-----------|-------|--------|
| top-nav | ❌ | No top navigation bar in Anki cards |
| bottom-nav | ❌ | No bottom nav in flashcards |
| sidebar-nav | ❌ | No sidebars in card templates |
| breadcrumbs | ❌ | No navigation hierarchy in cards |
| tabs-nav | ⚠️ | Could work for front/back or card variants |
| stepper | ⚠️ | Could show progress (step 1 of 5) |
| pagination | ❌ | No multi-page cards in Anki |
| back-button | ⚠️ | Anki has built-in back button |
| hamburger-menu | ❌ | No menus in flashcards |
| overflow-menu | ❌ | No action menu in templates |
| tree-nav | ❌ | No hierarchical navigation in cards |
| anchor-link | ⚠️ | Could link to sections within card |
| floating-nav | ❌ | No persistent floating UI |
| nav-rail | ❌ | Side rail navigation not applicable |

**Recommendation**: Remove 11 components; keep only `tabs-nav` and `stepper` as conditional-display helpers.

---

### 9. INPUT/FORM COMPONENTS (25 components) - **MOSTLY REMOVE**

**File**: `04b-COMPONENT-LIBRARY-INPUTS.md`

Forms for user input mostly don't make sense in read-only flashcard templates:

| Component | Keep? | Reason |
|-----------|-------|--------|
| text-field | ⚠️ | Display-only variants could work |
| text-area | ❌ | Input elements not actionable in Anki |
| password-field | ❌ | No authentication in Anki |
| number-input | ❌ | No calculation backend |
| search-field | ❌ | No search functionality |
| email-input | ❌ | No form submission |
| url-input | ❌ | No link validation backend |
| phone-input | ❌ | No form submission |
| checkbox | ❌ | No state persistence |
| radio-button | ❌ | No selection state |
| toggle-switch | ❌ | No state toggling in Anki |
| dropdown | ❌ | Selection with no effect |
| segmented-control | ❌ | Selection UI with no backend |
| chip-selector | ❌ | Tag selection with no backend |
| date-picker | ⚠️ | Could display dates (use text field) |
| time-picker | ❌ | No time selection purpose |
| color-picker | ❌ | No color selection in cards |
| file-upload | ❌ | No file operations in Anki |
| slider | ❌ | No continuous input |
| range-slider | ❌ | No range selection |
| rating-input | ❌ | No rating submission |
| form | ❌ | No forms in Anki templates |
| field-group | ✅ | Container component; useful |
| helper-text | ✅ | Explanatory text; useful |
| error-message | ⚠️ | Conditional error display (limited use) |

**Alternative approach**: Instead of interactive form components, use:
- Simple text display components
- Conditional components for showing/hiding
- Button-like elements styled with Anki behaviors

**Recommendation**: Remove 20+ form input components; keep only layout/text helpers.

---

### 10. BUTTON VARIANTS (13 components) - **CONSOLIDATE**

**File**: `04b-COMPONENT-LIBRARY-INPUTS.md`

Too many button variants; only 3-4 needed:

| Component | Keep? | Consolidation |
|-----------|-------|----------------|
| primary-button | ✅ | Main action button |
| secondary-button | ✅ | Alternative action |
| tertiary-button | ⚠️ | Merge with secondary |
| icon-button | ✅ | Icon-only button |
| fab | ⚠️ | Floating action button; merge with primary |
| text-button | ⚠️ | Variant of primary; remove |
| ghost-button | ⚠️ | Outline variant; merge with secondary |
| destructive-button | ✅ | Danger action (delete) |
| loading-button | ⚠️ | Anki has no async; merge with primary |
| split-button | ❌ | No dropdown menus in Anki |
| toggle-button | ⚠️ | No state toggling; remove |
| button-group | ✅ | Container for buttons |
| link-button | ✅ | Styled link |

**Recommendation**: Consolidate to 5 button types: Primary, Secondary, Tertiary, Icon, Destructive.

---

## Components to Remove (Summary)

### Category: Remove Entirely
- All 11 **Commerce** components (product, cart, pricing, etc.)
- 10 **Social Media** components (profiles, followers, posts, etc.)
- 9 **Search/Filter** components (search bars, filters, autocomplete, etc.)
- 8 **System/Meta** components (debug panels, loaders, offline indicators, etc.)
- 11 **Navigation** components (top nav, hamburger, breadcrumbs, etc.)
- 20+ **Form Input** components (text fields, checkboxes, dropdowns, etc.)
- 8 **Button Variants** (consolidate to 5 types)

**Total to Remove: ~67-75 components**

---

## Components to Keep / Repurpose

### Keep with Minor Adjustments:
- **Charts** (16 components) - Mark as "Advanced" requiring Chart.js
- **Data Display** (15 components) - All useful for flashcards
- **Layout/Structure** (20 components) - Core foundation
- **Text & Typography** (8 components) - Essential
- **Feedback/Status** (10 components) - Badges, alerts, progress bars
- **Accessibility Wrappers** (6 components) - Semantic HTML
- **Basic Animations** (3 components) - Fade, slide, stagger

**Total to Keep: ~100-110 components**

---

## Revised Component Count by Category

| Category | Original | Revised | Change |
|----------|----------|---------|--------|
| Layout & Navigation | 37 | 25 | -12 |
| Inputs & Forms | 50 | 12 | -38 |
| Data Display | 47 | 42 | -5 |
| Search & Commerce | 20 | 0 | -20 |
| Social & Charts | 24 | 18 | -6 |
| Accessibility & System | 31 | 13 | -18 |
| **TOTAL** | **209** | **110** | **-99** |

---

## Implementation Priority

### Phase 1: Remove (Immediate)
1. Delete all commerce components (11)
2. Delete all social media components (10)
3. Delete all search/filter components (9)
4. Delete form input components except text/helper (35)
5. Delete system/debugging components (8)

### Phase 2: Consolidate (Near-term)
1. Consolidate button variants (8 → 5)
2. Consolidate navigation components (15 → 4)
3. Consolidate motion components (6 → 3)

### Phase 3: Mark Advanced (Documentation)
1. Mark charts as requiring Chart.js
2. Add AnkiJSApi behavior documentation
3. Add animation performance warnings

---

## Updated Block Categories

### Proposed Revised Categories

```javascript
const categories = {
    // Core content
    layout: { label: 'Layout & Structure', order: 1, open: true },
    typography: { label: 'Text & Typography', order: 2, open: true },
    
    // Data display
    data: { label: 'Data Display', order: 3, open: false },
    charts: { label: 'Charts (Advanced)', order: 4, open: false },
    
    // UI elements
    buttons: { label: 'Buttons', order: 5, open: false },
    inputs: { label: 'Inputs', order: 6, open: false },
    feedback: { label: 'Feedback & Status', order: 7, open: false },
    overlays: { label: 'Overlays & Popups', order: 8, open: false },
    
    // Enhanced functionality
    animations: { label: 'Animations', order: 9, open: false },
    accessibility: { label: 'Accessibility', order: 10, open: false },
    
    // Anki specific
    anki: { label: 'Anki Special', order: 0, open: true }
};
```

---

## Recommendations Summary

1. **Remove ~99 components** that assume non-Anki features (commerce, social, advanced forms, etc.)
2. **Consolidate ~15 components** that are redundant variants
3. **Keep ~95 components** that work for flashcard templates
4. **Document** which components require external JS libraries (charts, animations)
5. **Create simpler component set** focused on learning card use cases

This reduces cognitive load for users and focuses the library on practical Anki template needs.
