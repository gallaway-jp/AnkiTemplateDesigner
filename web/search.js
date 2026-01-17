/**
 * Component Search System for GrapeJS
 * Provides fast, intuitive search across 112+ components
 * 
 * Features:
 * - Fuzzy matching algorithm
 * - Category filtering
 * - Search history
 * - Real-time results (no debounce needed)
 * - Keyboard navigation (Arrow keys, Enter)
 */

/**
 * Search Index - Maps component IDs to metadata
 * Built from block manager data
 */
class ComponentSearchIndex {
    constructor() {
        this.index = [];
        this.categories = new Set();
        this.categoryMap = new Map();
    }
    
    /**
     * Build search index from editor blocks
     * @param {object} editor - GrapeJS editor instance
     */
    buildIndex(editor) {
        const blockManager = editor.BlockManager;
        this.index = [];
        this.categoryMap.clear();
        this.categories.clear();
        
        // Get all blocks
        const blocks = blockManager.getAll();
        
        blocks.forEach(block => {
            const id = block.id;
            const label = block.attributes?.label || block.id;
            const category = block.attributes?.category || 'Other';
            const description = block.attributes?.description || '';
            const tags = block.attributes?.tags || [];
            
            // Normalize searchable text
            const searchText = `${label} ${category} ${description} ${tags.join(' ')}`.toLowerCase();
            
            // Add to index
            this.index.push({
                id,
                label,
                category,
                description,
                tags: Array.isArray(tags) ? tags : [],
                searchText,
                popularity: 0 // Track usage for ranking
            });
            
            // Track categories
            this.categories.add(category);
            
            if (!this.categoryMap.has(category)) {
                this.categoryMap.set(category, []);
            }
            this.categoryMap.get(category).push(id);
        });
        
        console.log(`[Search] Indexed ${this.index.length} components in ${this.categories.size} categories`);
    }
    
    /**
     * Fuzzy matching algorithm - scores text similarity
     * @param {string} query - Search query
     * @param {string} text - Text to match against
     * @returns {number} Similarity score 0-1, higher is better
     */
    fuzzyScore(query, text) {
        query = query.toLowerCase();
        text = text.toLowerCase();
        
        if (query === text) return 1; // Exact match
        if (text.includes(query)) return 0.9; // Substring match
        
        let score = 0;
        let lastIndex = -1;
        let matchCount = 0;
        
        // Score based on how many characters match in order
        for (let i = 0; i < query.length; i++) {
            const char = query[i];
            const index = text.indexOf(char, lastIndex + 1);
            
            if (index === -1) {
                return 0; // Character not found
            }
            
            matchCount++;
            
            // Consecutive matches score higher
            if (index === lastIndex + 1) {
                score += 0.2;
            } else {
                score += 0.1;
            }
            
            lastIndex = index;
        }
        
        // Normalize: all characters matched
        return Math.min(1, score * (query.length / text.length));
    }
    
    /**
     * Search for components
     * @param {string} query - Search query
     * @param {object} options - Search options
     * @returns {array} Sorted array of matching components
     */
    search(query, options = {}) {
        const {
            category = null,
            limit = 100,
            minScore = 0.3
        } = options;
        
        if (!query || query.trim().length === 0) {
            // Return all components or filtered by category
            let results = this.index;
            if (category) {
                results = results.filter(c => c.category === category);
            }
            return results.slice(0, limit);
        }
        
        // Score and filter results
        const results = this.index
            .map(item => {
                const score = this.fuzzyScore(query, item.searchText);
                return { ...item, score };
            })
            .filter(item => {
                if (item.score < minScore) return false;
                if (category && item.category !== category) return false;
                return true;
            })
            .sort((a, b) => {
                // Sort by score (descending), then by label (ascending)
                if (a.score !== b.score) {
                    return b.score - a.score;
                }
                return a.label.localeCompare(b.label);
            })
            .slice(0, limit);
        
        return results;
    }
    
    /**
     * Get all categories
     * @returns {array} Sorted category names
     */
    getCategories() {
        return Array.from(this.categories).sort();
    }
    
    /**
     * Track component usage for popularity ranking
     * @param {string} componentId - Component ID used
     */
    trackUsage(componentId) {
        const item = this.index.find(c => c.id === componentId);
        if (item) {
            item.popularity++;
        }
    }
}

/**
 * Component Search UI Manager
 * Handles search input, results display, and filtering
 */
class ComponentSearchUI {
    constructor(blockManager, searchIndex) {
        this.blockManager = blockManager;
        this.searchIndex = searchIndex;
        this.searchInput = null;
        this.searchContainer = null;
        this.currentQuery = '';
        this.searchHistory = [];
        this.selectedIndex = -1;
        this.maxHistoryItems = 10;
        
        // Load search history from localStorage
        this.loadSearchHistory();
    }
    
    /**
     * Initialize search UI in blocks container
     */
    initialize() {
        const container = document.querySelector('.blocks-container');
        if (!container) {
            console.warn('[Search] Blocks container not found');
            return;
        }
        
        // Create search container
        this.searchContainer = document.createElement('div');
        this.searchContainer.className = 'component-search';
        this.searchContainer.innerHTML = `
            <div class="search-input-wrapper">
                <input 
                    type="text" 
                    class="search-input" 
                    placeholder="Search components..."
                    aria-label="Search components"
                >
                <button class="search-clear" title="Clear search" aria-label="Clear search">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M2 2L14 14M14 2L2 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </button>
            </div>
            <div class="search-stats"></div>
            <div class="search-results"></div>
            <div class="search-history-hint"></div>
        `;
        
        // Insert before existing blocks
        container.insertBefore(this.searchContainer, container.firstChild);
        
        // Get references
        this.searchInput = this.searchContainer.querySelector('.search-input');
        this.clearBtn = this.searchContainer.querySelector('.search-clear');
        this.statsEl = this.searchContainer.querySelector('.search-stats');
        this.resultsEl = this.searchContainer.querySelector('.search-results');
        this.historyHintEl = this.searchContainer.querySelector('.search-history-hint');
        
        // Bind events
        this.searchInput.addEventListener('input', (e) => this.handleInput(e));
        this.searchInput.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.searchInput.addEventListener('focus', (e) => this.handleFocus(e));
        this.searchInput.addEventListener('blur', (e) => this.handleBlur(e));
        this.clearBtn.addEventListener('click', () => this.clearSearch());
        
        // Hide search UI initially (show only when blocks panel is visible)
        this.hide();
    }
    
    /**
     * Show search UI
     */
    show() {
        if (this.searchContainer) {
            this.searchContainer.style.display = 'block';
        }
    }
    
    /**
     * Hide search UI
     */
    hide() {
        if (this.searchContainer) {
            this.searchContainer.style.display = 'none';
        }
    }
    
    /**
     * Handle search input
     */
    handleInput(event) {
        this.currentQuery = event.target.value.trim();
        this.selectedIndex = -1;
        
        if (this.currentQuery.length === 0) {
            this.showAllBlocks();
            this.updateStats('All components shown');
            this.showHistoryHint();
        } else {
            this.performSearch();
            this.addToHistory(this.currentQuery);
        }
    }
    
    /**
     * Handle keyboard navigation
     */
    handleKeydown(event) {
        const keys = {
            'ArrowDown': () => this.selectNextResult(),
            'ArrowUp': () => this.selectPrevResult(),
            'Enter': () => this.activateSelectedResult(),
            'Escape': () => this.clearSearch(),
        };
        
        if (keys[event.key]) {
            event.preventDefault();
            keys[event.key]();
        }
    }
    
    /**
     * Handle search input focus
     */
    handleFocus(event) {
        if (this.currentQuery.length === 0 && this.searchHistory.length > 0) {
            this.showHistoryHint();
        }
    }
    
    /**
     * Handle search input blur
     */
    handleBlur(event) {
        // Delay to allow result selection
        setTimeout(() => {
            this.historyHintEl.innerHTML = '';
        }, 200);
    }
    
    /**
     * Perform search and update UI
     */
    performSearch() {
        const results = this.searchIndex.search(this.currentQuery);
        
        if (results.length === 0) {
            this.updateStats(`No results for "${this.currentQuery}"`);
            this.hideAllBlocks();
            this.resultsEl.innerHTML = '<div class="search-no-results">No components found</div>';
            return;
        }
        
        // Update stats
        this.updateStats(`${results.length} component${results.length !== 1 ? 's' : ''} found`);
        
        // Group results by category
        const byCategory = new Map();
        results.forEach(item => {
            if (!byCategory.has(item.category)) {
                byCategory.set(item.category, []);
            }
            byCategory.get(item.category).push(item);
        });
        
        // Update block visibility
        const visibleIds = results.map(r => r.id);
        this.filterBlocks(visibleIds);
        
        // Show results summary in results area
        let html = '<div class="search-results-summary">';
        byCategory.forEach((items, category) => {
            html += `<div class="search-category">
                <div class="search-category-name">${category}</div>
                <div class="search-category-items">${items.length}</div>
            </div>`;
        });
        html += '</div>';
        
        this.resultsEl.innerHTML = html;
    }
    
    /**
     * Show all blocks (clear search)
     */
    showAllBlocks() {
        const blocks = document.querySelectorAll('.gjs-block');
        blocks.forEach(block => {
            block.style.display = '';
        });
        
        const categories = document.querySelectorAll('.gjs-block-category');
        categories.forEach(cat => {
            cat.style.display = '';
        });
        
        this.resultsEl.innerHTML = '';
    }
    
    /**
     * Hide all blocks
     */
    hideAllBlocks() {
        const blocks = document.querySelectorAll('.gjs-block');
        blocks.forEach(block => {
            block.style.display = 'none';
        });
        
        const categories = document.querySelectorAll('.gjs-block-category');
        categories.forEach(cat => {
            cat.style.display = 'none';
        });
    }
    
    /**
     * Filter blocks to show only matching IDs
     * @param {array} visibleIds - Array of component IDs to show
     */
    filterBlocks(visibleIds) {
        const blocks = document.querySelectorAll('.gjs-block');
        const visibleSet = new Set(visibleIds);
        const visibleCategories = new Set();
        
        blocks.forEach(block => {
            const id = block.getAttribute('data-gjs-type') || block.getAttribute('data-gjs-block-id');
            if (visibleSet.has(id)) {
                block.style.display = '';
                // Get parent category
                const category = block.closest('.gjs-block-category');
                if (category) {
                    visibleCategories.add(category);
                }
            } else {
                block.style.display = 'none';
            }
        });
        
        // Hide categories with no visible blocks
        const categories = document.querySelectorAll('.gjs-block-category');
        categories.forEach(cat => {
            if (visibleCategories.has(cat)) {
                cat.style.display = '';
            } else {
                cat.style.display = 'none';
            }
        });
    }
    
    /**
     * Clear search
     */
    clearSearch() {
        this.currentQuery = '';
        this.searchInput.value = '';
        this.selectedIndex = -1;
        this.showAllBlocks();
        this.updateStats('');
        this.resultsEl.innerHTML = '';
        this.searchInput.focus();
    }
    
    /**
     * Update search stats display
     */
    updateStats(message) {
        this.statsEl.textContent = message;
        if (message) {
            this.statsEl.style.display = 'block';
        } else {
            this.statsEl.style.display = 'none';
        }
    }
    
    /**
     * Show search history hint
     */
    showHistoryHint() {
        if (this.searchHistory.length === 0) {
            this.historyHintEl.innerHTML = '';
            return;
        }
        
        const recent = this.searchHistory.slice(0, 5);
        let html = '<div class="search-history"><div class="search-history-label">Recent searches:</div>';
        recent.forEach(term => {
            html += `<button class="search-history-item" data-term="${term}">${term}</button>`;
        });
        html += '</div>';
        
        this.historyHintEl.innerHTML = html;
        
        // Bind history item clicks
        this.historyHintEl.querySelectorAll('.search-history-item').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.searchInput.value = e.target.dataset.term;
                this.handleInput({ target: this.searchInput });
            });
        });
    }
    
    /**
     * Add query to search history
     */
    addToHistory(query) {
        if (!this.searchHistory.includes(query)) {
            this.searchHistory.unshift(query);
            if (this.searchHistory.length > this.maxHistoryItems) {
                this.searchHistory.pop();
            }
            this.saveSearchHistory();
        }
    }
    
    /**
     * Save search history to localStorage
     */
    saveSearchHistory() {
        try {
            localStorage.setItem('atd-search-history', JSON.stringify(this.searchHistory));
        } catch (e) {
            console.warn('[Search] Failed to save search history:', e);
        }
    }
    
    /**
     * Load search history from localStorage
     */
    loadSearchHistory() {
        try {
            const saved = localStorage.getItem('atd-search-history');
            if (saved) {
                this.searchHistory = JSON.parse(saved);
            }
        } catch (e) {
            console.warn('[Search] Failed to load search history:', e);
        }
    }
    
    /**
     * Select next result in search
     */
    selectNextResult() {
        const results = this.resultsEl.querySelectorAll('.search-results-item');
        if (results.length === 0) return;
        
        this.selectedIndex = Math.min(this.selectedIndex + 1, results.length - 1);
        this.updateSelectedResult();
    }
    
    /**
     * Select previous result in search
     */
    selectPrevResult() {
        const results = this.resultsEl.querySelectorAll('.search-results-item');
        if (results.length === 0) return;
        
        this.selectedIndex = Math.max(this.selectedIndex - 1, 0);
        this.updateSelectedResult();
    }
    
    /**
     * Update visual selection of result
     */
    updateSelectedResult() {
        const results = this.resultsEl.querySelectorAll('.search-results-item');
        results.forEach((r, i) => {
            r.classList.toggle('selected', i === this.selectedIndex);
        });
    }
    
    /**
     * Activate selected result
     */
    activateSelectedResult() {
        const selected = this.resultsEl.querySelector('.search-results-item.selected');
        if (selected) {
            selected.click();
        }
    }
}

/**
 * Initialize component search system
 * @param {object} editor - GrapeJS editor instance
 */
window.initializeComponentSearch = function(editor) {
    console.log('[Search] Initializing component search system');
    
    try {
        // Create search index
        const searchIndex = new ComponentSearchIndex();
        searchIndex.buildIndex(editor);
        
        // Create search UI
        const searchUI = new ComponentSearchUI(editor.BlockManager, searchIndex);
        searchUI.initialize();
        searchUI.show();
        
        // Store globally for debugging
        window.componentSearch = {
            index: searchIndex,
            ui: searchUI
        };
        
        console.log('[Search] Component search initialized successfully');
        
        // Track block usage
        editor.on('block:drag:stop', (e) => {
            const blockId = e.block?.id;
            if (blockId) {
                searchIndex.trackUsage(blockId);
            }
        });
        
        return { searchIndex, searchUI };
    } catch (error) {
        console.error('[Search] Failed to initialize:', error);
        return null;
    }
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ComponentSearchIndex,
        ComponentSearchUI
    };
}
