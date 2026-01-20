/**
 * Selection Clarity UI Controller (Issue #52)
 * 
 * Visual feedback for selected elements with highlighting, breadcrumbs,
 * focus indicators, and multi-selection support.
 */

class SelectionClarityUI {
    constructor() {
        this.selectionPanel = null;
        this.breadcrumbContainer = null;
        this.selectedItemsList = null;
        this.focusIndicator = null;
        this.highlightColor = '#4CAF50';
        this.highlightedElements = new Set();
        
        this.initializeUI();
    }

    initializeUI() {
        this.createSelectionPanel();
        this.createBreadcrumbContainer();
        this.createHighlightContainer();
        this.attachEventHandlers();
    }

    createSelectionPanel() {
        /**
         * Create selection info panel.
         */
        this.selectionPanel = document.createElement('div');
        this.selectionPanel.id = 'selection-panel';
        this.selectionPanel.className = 'selection-panel';
        this.selectionPanel.innerHTML = `
            <div class="selection-header">
                <h4>Selection Info</h4>
                <span class="selection-count">0 selected</span>
            </div>
            <div class="selection-content">
                <div class="breadcrumbs-container" id="breadcrumbs"></div>
                <div class="selected-items" id="selected-items"></div>
                <div class="selection-actions">
                    <button class="btn btn-small" id="clear-selection">Clear</button>
                    <button class="btn btn-small" id="invert-selection">Invert</button>
                </div>
            </div>
        `;
        document.body.appendChild(this.selectionPanel);
    }

    createBreadcrumbContainer() {
        /**
         * Create breadcrumb navigation.
         */
        this.breadcrumbContainer = document.getElementById('breadcrumbs');
    }

    createHighlightContainer() {
        /**
         * Create highlight overlay container.
         */
        const container = document.createElement('div');
        container.id = 'selection-highlights';
        container.className = 'selection-highlights';
        document.body.appendChild(container);
    }

    attachEventHandlers() {
        /**
         * Attach event handlers.
         */
        document.getElementById('clear-selection').addEventListener('click', () => {
            this.emitEvent('clear-selection', {});
        });
        document.getElementById('invert-selection').addEventListener('click', () => {
            this.emitEvent('invert-selection', {});
        });
    }

    displaySelection(selectedItems, activeItem) {
        /**
         * Display selected items.
         * 
         * @param {Array} selectedItems - Selected items array
         * @param {string} activeItem - Active item ID
         */
        // Update count
        document.querySelector('.selection-count').textContent = `${selectedItems.length} selected`;
        
        // Update items list
        const itemsList = document.getElementById('selected-items');
        itemsList.innerHTML = '';
        
        selectedItems.forEach(item => {
            const div = document.createElement('div');
            div.className = `selection-item ${item.id === activeItem ? 'active' : ''}`;
            div.innerHTML = `
                <span class="item-name">${item.name}</span>
                <span class="item-type">${item.type}</span>
                <button class="item-remove" data-id="${item.id}" title="Remove item">× Remove</button>
            `;
            
            div.querySelector('.item-remove').addEventListener('click', () => {
                this.emitEvent('deselect-item', { itemId: item.id });
            });
            
            div.addEventListener('click', (e) => {
                if (!e.target.classList.contains('item-remove')) {
                    this.emitEvent('set-active-item', { itemId: item.id });
                }
            });
            
            itemsList.appendChild(div);
        });
        
        // Apply visual highlights
        this.applyHighlights(selectedItems);
    }

    displayBreadcrumbs(breadcrumbs) {
        /**
         * Display breadcrumb path.
         * 
         * @param {Array} breadcrumbs - Breadcrumb items
         */
        this.breadcrumbContainer.innerHTML = '';
        
        if (breadcrumbs.length === 0) {
            return;
        }
        
        breadcrumbs.forEach((crumb, index) => {
            const div = document.createElement('div');
            div.className = 'breadcrumb-item';
            div.innerHTML = `
                <button class="breadcrumb-link" data-id="${crumb.id}">${crumb.name}</button>
                ${index < breadcrumbs.length - 1 ? '<span class="breadcrumb-separator">/</span>' : ''}
            `;
            
            div.querySelector('.breadcrumb-link').addEventListener('click', () => {
                this.emitEvent('navigate-breadcrumb', { breadcrumbId: crumb.id });
            });
            
            this.breadcrumbContainer.appendChild(div);
        });
    }

    applyHighlights(selectedItems) {
        /**
         * Apply visual highlights to selected items.
         */
        // Clear previous highlights
        this.highlightedElements.forEach(el => {
            if (el.parentElement) {
                el.classList.remove('selection-highlight');
                el.style.borderColor = '';
            }
        });
        this.highlightedElements.clear();
        
        // Apply new highlights
        selectedItems.forEach(item => {
            const element = document.querySelector(`[data-component-id="${item.id}"]`);
            if (element) {
                element.classList.add('selection-highlight');
                element.style.borderColor = this.highlightColor;
                this.highlightedElements.add(element);
            }
        });
    }

    showFocusIndicator(itemId) {
        /**
         * Show focus indicator on item.
         */
        document.querySelectorAll('.selection-item').forEach(el => {
            el.classList.toggle('active', el.getAttribute('data-id') === itemId);
        });
    }

    setHighlightColor(color) {
        /**
         * Change highlight color.
         */
        this.highlightColor = color;
        this.highlightedElements.forEach(el => {
            el.style.borderColor = color;
        });
    }

    updateSelectionMode(mode) {
        /**
         * Update UI for selection mode.
         */
        this.selectionPanel.setAttribute('data-mode', mode);
    }

    showSelectionStats(stats) {
        /**
         * Show selection statistics.
         */
        const statsDiv = document.createElement('div');
        statsDiv.className = 'selection-stats';
        statsDiv.innerHTML = `
            <div class="stat">Total: ${stats.total_selected}</div>
            <div class="stat">Mode: ${stats.selection_mode}</div>
            <div class="stat">State: ${stats.selection_state}</div>
        `;
        
        const existing = this.selectionPanel.querySelector('.selection-stats');
        if (existing) existing.remove();
        this.selectionPanel.appendChild(statsDiv);
    }

    emitEvent(eventName, data) {
        /**
         * Emit custom event.
         */
        const event = new CustomEvent(`selection:${eventName}`, { detail: data });
        document.dispatchEvent(event);
    }

    on(eventName, callback) {
        /**
         * Listen for UI events.
         */
        document.addEventListener(`selection:${eventName}`, (e) => {
            callback(e.detail);
        });
    }

    reset() {
        /**
         * Reset UI to initial state.
         */
        document.getElementById('selected-items').innerHTML = '';
        document.querySelector('.selection-count').textContent = '0 selected';
        this.breadcrumbContainer.innerHTML = '';
        this.highlightedElements.clear();
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SelectionClarityUI;
}
