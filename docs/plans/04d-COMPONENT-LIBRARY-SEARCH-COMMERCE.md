# 04d - Component Library: Search & Commerce

> **Purpose**: Define GrapeJS blocks for Search, Filter, and Commerce components.
> **Target Agent**: Claude Haiku 4.5 chat agent in VS Code
> **Date**: January 11, 2026

---

## 8. Search & Filter Components

### `web/blocks/search.js`

```javascript
/**
 * Search & Filter Component Blocks
 */

export function registerSearchBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Search & Filter';
    
    // Search Bar
    bm.add('search-bar', {
        label: 'Search Bar',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-search-bar'],
            style: { display: 'flex', 'align-items': 'center', gap: '8px', padding: '8px 16px', background: '#f5f5f5', 'border-radius': '24px' },
            components: [
                { tagName: 'span', content: '🔍', style: { color: '#666' } },
                { tagName: 'input', attributes: { type: 'text', placeholder: 'Search...' }, style: { flex: '1', border: 'none', background: 'none', outline: 'none', 'font-size': '16px' } }
            ]
        }
    });
    
    // Search with Button
    bm.add('search-with-button', {
        label: 'Search + Button',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-search-combo'],
            style: { display: 'flex', 'border-radius': '8px', overflow: 'hidden', border: '1px solid #e0e0e0' },
            components: [
                { tagName: 'input', attributes: { type: 'text', placeholder: 'Search...' }, style: { flex: '1', padding: '12px 16px', border: 'none', outline: 'none', 'font-size': '16px' } },
                { tagName: 'button', content: 'Search', style: { padding: '12px 24px', border: 'none', background: '#1976d2', color: '#fff', cursor: 'pointer', 'font-weight': '500' } }
            ]
        }
    });
    
    // Filter Chips
    bm.add('filter-chips', {
        label: 'Filter Chips',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-filter-chips'],
            style: { display: 'flex', 'flex-wrap': 'wrap', gap: '8px' },
            components: [
                { tagName: 'button', content: 'All', style: { padding: '8px 16px', border: 'none', 'border-radius': '20px', background: '#1976d2', color: '#fff', cursor: 'pointer' } },
                { tagName: 'button', content: 'Category 1', style: { padding: '8px 16px', border: '1px solid #e0e0e0', 'border-radius': '20px', background: '#fff', cursor: 'pointer' } },
                { tagName: 'button', content: 'Category 2', style: { padding: '8px 16px', border: '1px solid #e0e0e0', 'border-radius': '20px', background: '#fff', cursor: 'pointer' } },
                { tagName: 'button', content: 'Category 3', style: { padding: '8px 16px', border: '1px solid #e0e0e0', 'border-radius': '20px', background: '#fff', cursor: 'pointer' } }
            ]
        }
    });
    
    // Filter Panel
    bm.add('filter-panel', {
        label: 'Filter Panel',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-filter-panel'],
            style: { padding: '20px', background: '#fff', 'border-radius': '12px', border: '1px solid #e0e0e0' },
            components: [
                { tagName: 'h4', content: 'Filters', style: { margin: '0 0 16px', 'font-size': '16px' } },
                { tagName: 'div', style: { 'margin-bottom': '16px' }, components: [
                    { tagName: 'label', content: 'Category', style: { display: 'block', 'margin-bottom': '8px', 'font-weight': '500' } },
                    { tagName: 'select', style: { width: '100%', padding: '10px', border: '1px solid #e0e0e0', 'border-radius': '6px' }, components: [
                        { tagName: 'option', content: 'All Categories' },
                        { tagName: 'option', content: 'Option 1' },
                        { tagName: 'option', content: 'Option 2' }
                    ]}
                ]},
                { tagName: 'div', style: { 'margin-bottom': '16px' }, components: [
                    { tagName: 'label', content: 'Price Range', style: { display: 'block', 'margin-bottom': '8px', 'font-weight': '500' } },
                    { tagName: 'input', attributes: { type: 'range' }, style: { width: '100%' } }
                ]},
                { tagName: 'button', content: 'Apply Filters', style: { width: '100%', padding: '12px', border: 'none', 'border-radius': '6px', background: '#1976d2', color: '#fff', cursor: 'pointer' } }
            ]
        }
    });
    
    // Sort Dropdown
    bm.add('sort-dropdown', {
        label: 'Sort Dropdown',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-sort'],
            style: { display: 'flex', 'align-items': 'center', gap: '8px' },
            components: [
                { tagName: 'label', content: 'Sort by:', style: { 'font-weight': '500' } },
                { tagName: 'select', style: { padding: '8px 12px', border: '1px solid #e0e0e0', 'border-radius': '6px', background: '#fff' }, components: [
                    { tagName: 'option', content: 'Newest' },
                    { tagName: 'option', content: 'Oldest' },
                    { tagName: 'option', content: 'Price: Low to High' },
                    { tagName: 'option', content: 'Price: High to Low' }
                ]}
            ]
        }
    });
    
    // Tag Input
    bm.add('tag-input', {
        label: 'Tag Input',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-tag-input'],
            style: { display: 'flex', 'flex-wrap': 'wrap', gap: '8px', padding: '8px', border: '1px solid #e0e0e0', 'border-radius': '8px', 'min-height': '48px' },
            components: [
                { tagName: 'span', style: { display: 'flex', 'align-items': 'center', gap: '4px', padding: '4px 8px', background: '#e3f2fd', 'border-radius': '4px' }, components: [{ tagName: 'span', content: 'Tag 1' }, { tagName: 'button', content: '×', style: { border: 'none', background: 'none', cursor: 'pointer' } }] },
                { tagName: 'span', style: { display: 'flex', 'align-items': 'center', gap: '4px', padding: '4px 8px', background: '#e3f2fd', 'border-radius': '4px' }, components: [{ tagName: 'span', content: 'Tag 2' }, { tagName: 'button', content: '×', style: { border: 'none', background: 'none', cursor: 'pointer' } }] },
                { tagName: 'input', attributes: { type: 'text', placeholder: 'Add tag...' }, style: { flex: '1', 'min-width': '100px', border: 'none', outline: 'none' } }
            ]
        }
    });
    
    // Active Filters Bar
    bm.add('active-filters', {
        label: 'Active Filters',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-active-filters'],
            style: { display: 'flex', 'flex-wrap': 'wrap', 'align-items': 'center', gap: '8px' },
            components: [
                { tagName: 'span', content: 'Active filters:', style: { 'font-weight': '500' } },
                { tagName: 'span', style: { display: 'flex', 'align-items': 'center', gap: '4px', padding: '4px 12px', background: '#f5f5f5', 'border-radius': '20px' }, components: [{ tagName: 'span', content: 'Category: Books' }, { tagName: 'button', content: '×', style: { border: 'none', background: 'none', cursor: 'pointer' } }] },
                { tagName: 'span', style: { display: 'flex', 'align-items': 'center', gap: '4px', padding: '4px 12px', background: '#f5f5f5', 'border-radius': '20px' }, components: [{ tagName: 'span', content: 'Price: $10-$50' }, { tagName: 'button', content: '×', style: { border: 'none', background: 'none', cursor: 'pointer' } }] },
                { tagName: 'button', content: 'Clear all', style: { color: '#1976d2', border: 'none', background: 'none', cursor: 'pointer', 'text-decoration': 'underline' } }
            ]
        }
    });
    
    // Autocomplete Dropdown
    bm.add('autocomplete', {
        label: 'Autocomplete',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-autocomplete'],
            style: { position: 'relative' },
            components: [
                { tagName: 'input', attributes: { type: 'text', placeholder: 'Type to search...' }, style: { width: '100%', padding: '12px 16px', border: '1px solid #e0e0e0', 'border-radius': '8px' } },
                { tagName: 'div', classes: ['atd-autocomplete-dropdown'], style: { position: 'absolute', top: '100%', left: '0', right: '0', background: '#fff', 'border-radius': '0 0 8px 8px', 'box-shadow': '0 4px 12px rgba(0,0,0,0.1)', 'z-index': '10' }, components: [
                    { tagName: 'div', content: 'Suggestion 1', style: { padding: '10px 16px', cursor: 'pointer' } },
                    { tagName: 'div', content: 'Suggestion 2', style: { padding: '10px 16px', cursor: 'pointer' } },
                    { tagName: 'div', content: 'Suggestion 3', style: { padding: '10px 16px', cursor: 'pointer' } }
                ]}
            ]
        }
    });
    
    // Results Count
    bm.add('results-count', {
        label: 'Results Count',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-results-count'],
            style: { color: '#666' },
            components: [
                { tagName: 'span', content: 'Showing ' },
                { tagName: 'strong', content: '1-20' },
                { tagName: 'span', content: ' of ' },
                { tagName: 'strong', content: '156' },
                { tagName: 'span', content: ' results' }
            ]
        }
    });
}
```

---

## 9. Commerce Components

### `web/blocks/commerce.js`

```javascript
/**
 * Commerce Component Blocks
 */

export function registerCommerceBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Commerce';
    
    // Product Card
    bm.add('product-card', {
        label: 'Product Card',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-product-card'],
            style: { background: '#fff', 'border-radius': '12px', overflow: 'hidden', 'box-shadow': '0 2px 8px rgba(0,0,0,0.1)' },
            components: [
                { tagName: 'img', attributes: { src: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="200"%3E%3Crect fill="%23e0e0e0" width="300" height="200"/%3E%3C/svg%3E' }, style: { width: '100%', 'aspect-ratio': '4/3', 'object-fit': 'cover' } },
                { tagName: 'div', style: { padding: '16px' }, components: [
                    { tagName: 'h3', content: 'Product Name', style: { margin: '0 0 8px', 'font-size': '16px' } },
                    { tagName: 'p', content: '$99.00', style: { margin: '0 0 12px', 'font-size': '18px', 'font-weight': '600', color: '#1976d2' } },
                    { tagName: 'button', content: 'Add to Cart', style: { width: '100%', padding: '10px', border: 'none', 'border-radius': '6px', background: '#1976d2', color: '#fff', cursor: 'pointer' } }
                ]}
            ]
        }
    });
    
    // Price Display
    bm.add('price-display', {
        label: 'Price Display',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-price'],
            style: { display: 'flex', 'align-items': 'baseline', gap: '8px' },
            components: [
                { tagName: 'span', content: '$79.00', style: { 'font-size': '24px', 'font-weight': '700', color: '#1976d2' } },
                { tagName: 'span', content: '$99.00', style: { 'font-size': '16px', color: '#999', 'text-decoration': 'line-through' } },
                { tagName: 'span', content: '20% OFF', style: { padding: '2px 8px', background: '#c8e6c9', color: '#2e7d32', 'border-radius': '4px', 'font-size': '12px', 'font-weight': '600' } }
            ]
        }
    });
    
    // Quantity Selector
    bm.add('quantity-selector', {
        label: 'Quantity Selector',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-quantity'],
            style: { display: 'inline-flex', 'align-items': 'center', border: '1px solid #e0e0e0', 'border-radius': '8px', overflow: 'hidden' },
            components: [
                { tagName: 'button', content: '−', style: { width: '40px', height: '40px', border: 'none', background: '#f5f5f5', cursor: 'pointer', 'font-size': '18px' } },
                { tagName: 'input', attributes: { type: 'number', value: '1', min: '1' }, style: { width: '60px', height: '40px', border: 'none', 'text-align': 'center', 'font-size': '16px' } },
                { tagName: 'button', content: '+', style: { width: '40px', height: '40px', border: 'none', background: '#f5f5f5', cursor: 'pointer', 'font-size': '18px' } }
            ]
        }
    });
    
    // Cart Item
    bm.add('cart-item', {
        label: 'Cart Item',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-cart-item'],
            style: { display: 'flex', gap: '16px', padding: '16px', 'border-bottom': '1px solid #e0e0e0' },
            components: [
                { tagName: 'img', attributes: { src: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="80" height="80"%3E%3Crect fill="%23e0e0e0" width="80" height="80"/%3E%3C/svg%3E' }, style: { width: '80px', height: '80px', 'border-radius': '8px', 'object-fit': 'cover' } },
                { tagName: 'div', style: { flex: '1' }, components: [
                    { tagName: 'h4', content: 'Product Name', style: { margin: '0 0 4px' } },
                    { tagName: 'p', content: 'Size: M, Color: Blue', style: { margin: '0', color: '#666', 'font-size': '14px' } }
                ]},
                { tagName: 'div', style: { 'text-align': 'right' }, components: [
                    { tagName: 'p', content: '$49.00', style: { margin: '0 0 8px', 'font-weight': '600' } },
                    { tagName: 'button', content: 'Remove', style: { border: 'none', background: 'none', color: '#d32f2f', cursor: 'pointer', 'font-size': '14px' } }
                ]}
            ]
        }
    });
    
    // Cart Summary
    bm.add('cart-summary', {
        label: 'Cart Summary',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-cart-summary'],
            style: { padding: '20px', background: '#f5f5f5', 'border-radius': '12px' },
            components: [
                { tagName: 'h3', content: 'Order Summary', style: { margin: '0 0 16px' } },
                { tagName: 'div', style: { display: 'flex', 'justify-content': 'space-between', 'margin-bottom': '8px' }, components: [{ tagName: 'span', content: 'Subtotal' }, { tagName: 'span', content: '$147.00' }] },
                { tagName: 'div', style: { display: 'flex', 'justify-content': 'space-between', 'margin-bottom': '8px' }, components: [{ tagName: 'span', content: 'Shipping' }, { tagName: 'span', content: '$5.00' }] },
                { tagName: 'div', style: { display: 'flex', 'justify-content': 'space-between', 'margin-bottom': '8px' }, components: [{ tagName: 'span', content: 'Tax' }, { tagName: 'span', content: '$12.00' }] },
                { tagName: 'hr', style: { margin: '12px 0', border: 'none', 'border-top': '1px solid #e0e0e0' } },
                { tagName: 'div', style: { display: 'flex', 'justify-content': 'space-between', 'font-weight': '700', 'font-size': '18px' }, components: [{ tagName: 'span', content: 'Total' }, { tagName: 'span', content: '$164.00' }] },
                { tagName: 'button', content: 'Checkout', style: { width: '100%', 'margin-top': '16px', padding: '14px', border: 'none', 'border-radius': '8px', background: '#1976d2', color: '#fff', 'font-size': '16px', cursor: 'pointer' } }
            ]
        }
    });
    
    // Rating Stars
    bm.add('rating-stars', {
        label: 'Rating Stars',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-rating'],
            style: { display: 'flex', 'align-items': 'center', gap: '4px' },
            components: [
                { tagName: 'span', content: '★', style: { color: '#ffc107', 'font-size': '20px' } },
                { tagName: 'span', content: '★', style: { color: '#ffc107', 'font-size': '20px' } },
                { tagName: 'span', content: '★', style: { color: '#ffc107', 'font-size': '20px' } },
                { tagName: 'span', content: '★', style: { color: '#ffc107', 'font-size': '20px' } },
                { tagName: 'span', content: '☆', style: { color: '#e0e0e0', 'font-size': '20px' } },
                { tagName: 'span', content: '(128)', style: { 'margin-left': '8px', color: '#666' } }
            ]
        }
    });
    
    // Promo Code Input
    bm.add('promo-code', {
        label: 'Promo Code',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-promo-code'],
            style: { display: 'flex', gap: '8px' },
            components: [
                { tagName: 'input', attributes: { type: 'text', placeholder: 'Enter promo code' }, style: { flex: '1', padding: '12px', border: '1px solid #e0e0e0', 'border-radius': '6px' } },
                { tagName: 'button', content: 'Apply', style: { padding: '12px 24px', border: 'none', 'border-radius': '6px', background: '#333', color: '#fff', cursor: 'pointer' } }
            ]
        }
    });
    
    // Wishlist Button
    bm.add('wishlist-button', {
        label: 'Wishlist Button',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-wishlist-btn'],
            style: { display: 'flex', 'align-items': 'center', gap: '8px', padding: '10px 16px', border: '1px solid #e0e0e0', 'border-radius': '8px', background: '#fff', cursor: 'pointer' },
            components: [
                { tagName: 'span', content: '♡' },
                { tagName: 'span', content: 'Add to Wishlist' }
            ]
        }
    });
    
    // Stock Status
    bm.add('stock-status', {
        label: 'Stock Status',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-stock'],
            style: { display: 'flex', 'align-items': 'center', gap: '8px' },
            components: [
                { tagName: 'span', style: { width: '10px', height: '10px', 'border-radius': '50%', background: '#4caf50' } },
                { tagName: 'span', content: 'In Stock', style: { color: '#4caf50', 'font-weight': '500' } }
            ]
        }
    });
    
    // Product Variants
    bm.add('product-variants', {
        label: 'Product Variants',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-variants'],
            components: [
                { tagName: 'div', style: { 'margin-bottom': '16px' }, components: [
                    { tagName: 'label', content: 'Size', style: { display: 'block', 'margin-bottom': '8px', 'font-weight': '500' } },
                    { tagName: 'div', style: { display: 'flex', gap: '8px' }, components: [
                        { tagName: 'button', content: 'S', style: { width: '40px', height: '40px', border: '1px solid #e0e0e0', 'border-radius': '8px', background: '#fff', cursor: 'pointer' } },
                        { tagName: 'button', content: 'M', style: { width: '40px', height: '40px', border: '2px solid #1976d2', 'border-radius': '8px', background: '#e3f2fd', cursor: 'pointer' } },
                        { tagName: 'button', content: 'L', style: { width: '40px', height: '40px', border: '1px solid #e0e0e0', 'border-radius': '8px', background: '#fff', cursor: 'pointer' } }
                    ]}
                ]},
                { tagName: 'div', components: [
                    { tagName: 'label', content: 'Color', style: { display: 'block', 'margin-bottom': '8px', 'font-weight': '500' } },
                    { tagName: 'div', style: { display: 'flex', gap: '8px' }, components: [
                        { tagName: 'button', style: { width: '32px', height: '32px', 'border-radius': '50%', background: '#333', border: '2px solid #1976d2', cursor: 'pointer' } },
                        { tagName: 'button', style: { width: '32px', height: '32px', 'border-radius': '50%', background: '#1976d2', border: '2px solid transparent', cursor: 'pointer' } },
                        { tagName: 'button', style: { width: '32px', height: '32px', 'border-radius': '50%', background: '#f44336', border: '2px solid transparent', cursor: 'pointer' } }
                    ]}
                ]}
            ]
        }
    });
    
    // Review Card
    bm.add('review-card', {
        label: 'Review Card',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-review'],
            style: { padding: '16px', background: '#f5f5f5', 'border-radius': '12px' },
            components: [
                { tagName: 'div', style: { display: 'flex', 'align-items': 'center', gap: '12px', 'margin-bottom': '12px' }, components: [
                    { tagName: 'div', content: 'JD', style: { width: '40px', height: '40px', 'border-radius': '50%', background: '#1976d2', color: '#fff', display: 'flex', 'align-items': 'center', 'justify-content': 'center', 'font-weight': '600' } },
                    { tagName: 'div', components: [{ tagName: 'strong', content: 'John Doe' }, { tagName: 'span', content: ' • 2 days ago', style: { color: '#666' } }] }
                ]},
                { tagName: 'div', content: '★★★★☆', style: { color: '#ffc107', 'margin-bottom': '8px' } },
                { tagName: 'p', content: 'Great product! Exactly as described. Would definitely recommend to others.', style: { margin: '0', color: '#333' } }
            ]
        }
    });
}
```

---

## Next Document

See [04e-COMPONENT-LIBRARY-SOCIAL-CHARTS.md](04e-COMPONENT-LIBRARY-SOCIAL-CHARTS.md) for Social and Charts components.
