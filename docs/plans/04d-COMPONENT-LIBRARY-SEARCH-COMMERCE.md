# 04d - Component Library: Search & Commerce

> **Status**: REMOVED
> **Updated**: Based on COMPONENT-AUDIT.md
> **Date**: January 11, 2026

---

## Removal Justification

All Search, Filter, and Commerce components have been removed as they are **not applicable to Anki card templates**.

### Search & Filter Components (REMOVED)
- Search Bar
- Search with Button
- Filter Chips
- Filter Panel
- Sort Dropdown
- Tag Input
- Active Filters Bar
- Autocomplete Dropdown
- Results Count

**Reason**: Anki templates display one card at a time in a controlled study session. Search/filter workflows are not relevant.

### Commerce Components (REMOVED)
- Product Card
- Price Display
- Quantity Selector
- Cart Item
- Cart Summary
- Rating Stars (for products)
- Promo Code Input
- Wishlist Button
- Stock Status
- Product Variants
- Review Card

**Reason**: Anki is an educational flashcard tool, not an e-commerce platform. No commerce features are needed.

---

## Alternative Patterns for Study Tools

If you need **search-like functionality** in templates, use:
- **Study Action Bar** (`04a`) with filter buttons for custom study modes
- **Dropdown** (`04b`) to show/hide content sections
- **Tabs** (`04a`) for organizing multi-section cards (Front/Back/Extra)

---

## Next Document

See [04e-COMPONENT-LIBRARY-SOCIAL-CHARTS.md](04e-COMPONENT-LIBRARY-SOCIAL-CHARTS.md) for remaining Social and Charts components.
