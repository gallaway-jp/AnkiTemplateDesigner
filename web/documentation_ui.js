/**
 * Issue #48: Documentation System - Frontend
 * 
 * Manages in-app help dialogs, tooltips, context menu, and documentation browser.
 * Features: Help dialog, tooltips, context menu, searchable documentation browser.
 */

class DocumentationUI {
    /**
     * Initialize the documentation UI system.
     */
    constructor() {
        this.help_visible = false;
        this.tooltips_active = {};
        this.api_base = '/api';
        this.init_ui();
        this.setup_keyboard_shortcuts();
    }

    /**
     * Initialize UI elements.
     */
    init_ui() {
        this.create_help_dialog();
        this.create_tooltips_system();
        this.create_context_menu();
        this.setup_event_listeners();
        this.setup_help_button();
    }

    /**
     * Create the help dialog.
     */
    create_help_dialog() {
        const dialog = document.createElement('div');
        dialog.id = 'help-dialog';
        dialog.className = 'help-dialog hidden';
        dialog.innerHTML = `
            <div class="help-content">
                <div class="help-header">
                    <h2>Documentation</h2>
                    <button class="close-btn" aria-label="Close help">&times;</button>
                </div>
                <div class="help-body">
                    <div class="help-sidebar">
                        <div class="search-box">
                            <input type="text" class="help-search-input" placeholder="Search documentation...">
                            <button class="search-btn" aria-label="Search">🔍</button>
                        </div>
                        <div class="help-toc">
                            <div class="toc-section">
                                <h4>Categories</h4>
                                <ul class="category-list"></ul>
                            </div>
                            <div class="toc-section">
                                <h4>Bookmarks</h4>
                                <ul class="bookmark-list"></ul>
                            </div>
                            <div class="toc-section">
                                <h4>Recent</h4>
                                <ul class="recent-list"></ul>
                            </div>
                        </div>
                    </div>
                    <div class="help-main">
                        <div class="article-view">
                            <div class="article-header">
                                <h3 class="article-title"></h3>
                                <button class="bookmark-btn" data-action="bookmark" title="Bookmark this article">⭐</button>
                                <button class="helpful-btn" data-action="mark-helpful" title="Mark as helpful">👍</button>
                            </div>
                            <div class="article-body"></div>
                            <div class="article-footer">
                                <div class="article-links">
                                    <button class="prev-article-btn" data-action="prev-article">← Previous</button>
                                    <button class="next-article-btn" data-action="next-article">Next →</button>
                                </div>
                            </div>
                        </div>
                        <div class="search-results hidden">
                            <div class="search-results-header">
                                <h4>Search Results</h4>
                                <button class="close-search-btn" data-action="close-search">&times;</button>
                            </div>
                            <div class="search-results-list"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(dialog);
    }

    /**
     * Create tooltips system.
     */
    create_tooltips_system() {
        const container = document.createElement('div');
        container.id = 'tooltips-container';
        container.className = 'tooltips-container';
        document.body.appendChild(container);
        
        // Load tooltips from backend and initialize
        this.initialize_tooltips();
    }

    /**
     * Create context menu (right-click).
     */
    create_context_menu() {
        const menu = document.createElement('div');
        menu.id = 'help-context-menu';
        menu.className = 'context-menu hidden';
        menu.innerHTML = `
            <div class="context-menu-content">
                <button class="context-menu-item" data-action="search-help">
                    <span class="icon">🔍</span>
                    <span class="label">Search Documentation</span>
                </button>
                <button class="context-menu-item" data-action="context-help">
                    <span class="icon">❓</span>
                    <span class="label">Learn About This</span>
                </button>
                <hr>
                <button class="context-menu-item" data-action="open-docs">
                    <span class="icon">📖</span>
                    <span class="label">Open Documentation</span>
                </button>
            </div>
        `;
        document.body.appendChild(menu);
    }

    /**
     * Setup event listeners.
     */
    setup_event_listeners() {
        document.addEventListener('click', (e) => this.handle_click(e));
        document.addEventListener('contextmenu', (e) => this.handle_context_menu(e));
        document.addEventListener('mouseover', (e) => this.handle_tooltip_trigger(e, 'hover'));
        document.addEventListener('mouseout', (e) => this.handle_tooltip_hide(e));
    }

    /**
     * Setup keyboard shortcuts.
     */
    setup_keyboard_shortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'F1' || (e.ctrlKey && e.key === 'h')) {
                e.preventDefault();
                this.toggle_help_dialog();
            }
            if (e.key === 'Escape' && this.help_visible) {
                this.close_help_dialog();
            }
        });
    }

    /**
     * Setup help button in UI.
     */
    setup_help_button() {
        // Add help button to navbar if exists
        const navbar = document.querySelector('[data-component="navbar"]');
        if (navbar) {
            const help_btn = document.createElement('button');
            help_btn.className = 'help-button';
            help_btn.innerHTML = '❓';
            help_btn.title = 'Open help (F1)';
            help_btn.addEventListener('click', () => this.toggle_help_dialog());
            navbar.appendChild(help_btn);
        }
    }

    /**
     * Initialize tooltips from backend.
     */
    async initialize_tooltips() {
        try {
            const response = await fetch(`${this.api_base}/documentation/tooltips`);
            const data = await response.json();
            
            if (data.success && data.tooltips) {
                data.tooltips.forEach(tooltip_data => {
                    this.register_tooltip(tooltip_data);
                });
            }
        } catch (error) {
            console.error('Error loading tooltips:', error);
        }
    }

    /**
     * Register a tooltip.
     */
    register_tooltip(tooltip_data) {
        const element = document.getElementById(tooltip_data.element_id);
        if (element) {
            element.setAttribute('data-tooltip-id', tooltip_data.tooltip_id);
            element.setAttribute('data-tooltip-title', tooltip_data.title);
            element.setAttribute('data-tooltip-content', tooltip_data.content);
            element.setAttribute('data-tooltip-position', tooltip_data.position);
            element.setAttribute('data-tooltip-delay', tooltip_data.delay_ms);
        }
    }

    /**
     * Handle tooltip trigger (hover).
     */
    handle_tooltip_trigger(e, trigger_type) {
        const element = e.target.closest('[data-tooltip-id]');
        if (element && trigger_type === 'hover') {
            const tooltip_id = element.getAttribute('data-tooltip-id');
            const delay = parseInt(element.getAttribute('data-tooltip-delay') || 300);
            
            if (!this.tooltips_active[tooltip_id]) {
                setTimeout(() => {
                    this.show_tooltip(element, tooltip_id);
                }, delay);
            }
        }
    }

    /**
     * Handle tooltip hide.
     */
    handle_tooltip_hide(e) {
        const element = e.target.closest('[data-tooltip-id]');
        if (element) {
            const tooltip_id = element.getAttribute('data-tooltip-id');
            this.hide_tooltip(tooltip_id);
        }
    }

    /**
     * Show tooltip.
     */
    show_tooltip(element, tooltip_id) {
        if (this.tooltips_active[tooltip_id]) return;
        
        const title = element.getAttribute('data-tooltip-title');
        const content = element.getAttribute('data-tooltip-content');
        const position = element.getAttribute('data-tooltip-position') || 'top';
        
        const tooltip = document.createElement('div');
        tooltip.className = `tooltip tooltip-${position}`;
        tooltip.id = `tooltip-${tooltip_id}`;
        tooltip.innerHTML = `
            <div class="tooltip-title">${title}</div>
            <div class="tooltip-content">${content}</div>
            <div class="tooltip-arrow"></div>
        `;
        
        const container = document.getElementById('tooltips-container');
        container.appendChild(tooltip);
        
        // Position tooltip
        this.position_tooltip(tooltip, element);
        
        this.tooltips_active[tooltip_id] = true;
    }

    /**
     * Hide tooltip.
     */
    hide_tooltip(tooltip_id) {
        const tooltip = document.getElementById(`tooltip-${tooltip_id}`);
        if (tooltip) {
            tooltip.remove();
            delete this.tooltips_active[tooltip_id];
        }
    }

    /**
     * Position tooltip near element.
     */
    position_tooltip(tooltip, element) {
        const rect = element.getBoundingClientRect();
        const position = tooltip.className.match(/tooltip-(\w+)/)[1];
        
        let top = 0, left = 0;
        const offset = 10;
        
        switch (position) {
            case 'top':
                top = rect.top - tooltip.offsetHeight - offset;
                left = rect.left + (rect.width - tooltip.offsetWidth) / 2;
                break;
            case 'bottom':
                top = rect.bottom + offset;
                left = rect.left + (rect.width - tooltip.offsetWidth) / 2;
                break;
            case 'left':
                top = rect.top + (rect.height - tooltip.offsetHeight) / 2;
                left = rect.left - tooltip.offsetWidth - offset;
                break;
            case 'right':
                top = rect.top + (rect.height - tooltip.offsetHeight) / 2;
                left = rect.right + offset;
                break;
        }
        
        tooltip.style.top = `${top}px`;
        tooltip.style.left = `${left}px`;
    }

    /**
     * Handle context menu (right-click).
     */
    handle_context_menu(e) {
        // Show context menu on right-click
        const menu = document.getElementById('help-context-menu');
        menu.style.top = `${e.clientY}px`;
        menu.style.left = `${e.clientX}px`;
        menu.classList.remove('hidden');
        
        e.preventDefault();
    }

    /**
     * Handle button clicks.
     */
    handle_click(e) {
        const action = e.target.closest('[data-action]')?.dataset.action;
        
        // Close context menu if clicking outside
        if (action !== 'search-help' && action !== 'context-help' && action !== 'open-docs') {
            document.getElementById('help-context-menu').classList.add('hidden');
        }
        
        switch (action) {
            case 'search-help':
                this.toggle_help_dialog();
                this.focus_search();
                break;
            case 'context-help':
                this.show_contextual_help(e.target);
                break;
            case 'open-docs':
                this.toggle_help_dialog();
                break;
            case 'bookmark':
                this.toggle_bookmark(e.target);
                break;
            case 'mark-helpful':
                this.mark_article_helpful();
                break;
            case 'prev-article':
                this.navigate_article('prev');
                break;
            case 'next-article':
                this.navigate_article('next');
                break;
            case 'close-search':
                this.close_search_results();
                break;
        }
    }

    /**
     * Toggle help dialog visibility.
     */
    toggle_help_dialog() {
        const dialog = document.getElementById('help-dialog');
        if (dialog.classList.contains('hidden')) {
            this.open_help_dialog();
        } else {
            this.close_help_dialog();
        }
    }

    /**
     * Open help dialog.
     */
    async open_help_dialog() {
        const dialog = document.getElementById('help-dialog');
        dialog.classList.remove('hidden');
        this.help_visible = true;
        
        // Load table of contents
        await this.load_table_of_contents();
        
        // Load first article
        await this.load_article('getting_started_1');
    }

    /**
     * Close help dialog.
     */
    close_help_dialog() {
        const dialog = document.getElementById('help-dialog');
        dialog.classList.add('hidden');
        this.help_visible = false;
    }

    /**
     * Load table of contents.
     */
    async load_table_of_contents() {
        try {
            const response = await fetch(`${this.api_base}/documentation/toc`);
            const data = await response.json();
            
            if (data.success && data.toc) {
                const category_list = document.querySelector('.category-list');
                category_list.innerHTML = '';
                
                for (const [category, articles] of Object.entries(data.toc)) {
                    articles.forEach(title => {
                        const item = document.createElement('li');
                        item.innerHTML = `<a href="#" data-category="${category}">${title}</a>`;
                        item.querySelector('a').addEventListener('click', (e) => {
                            e.preventDefault();
                            this.search(title);
                        });
                        category_list.appendChild(item);
                    });
                }
            }
        } catch (error) {
            console.error('Error loading table of contents:', error);
        }
    }

    /**
     * Load article.
     */
    async load_article(article_id) {
        try {
            const response = await fetch(`${this.api_base}/documentation/articles/${article_id}`);
            const data = response.json();
            
            if (data.success && data.article) {
                const article = data.article;
                document.querySelector('.article-title').textContent = article.title;
                document.querySelector('.article-body').innerHTML = this.format_article_content(article.content);
                
                // Update bookmark button
                const bookmark_btn = document.querySelector('.bookmark-btn');
                if (article.bookmarked) {
                    bookmark_btn.classList.add('bookmarked');
                } else {
                    bookmark_btn.classList.remove('bookmarked');
                }
            }
        } catch (error) {
            console.error('Error loading article:', error);
        }
    }

    /**
     * Format article content (markdown-like).
     */
    format_article_content(content) {
        let html = content
            .replace(/```\n([\s\S]*?)\n```/g, '<pre><code>$1</code></pre>')
            .replace(/^### (.*?)$/gm, '<h3>$1</h3>')
            .replace(/^## (.*?)$/gm, '<h2>$1</h2>')
            .replace(/^# (.*?)$/gm, '<h1>$1</h1>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/^- (.*?)$/gm, '<li>$1</li>');
        
        return `<p>${html}</p>`;
    }

    /**
     * Search documentation.
     */
    async search(query) {
        try {
            const response = await fetch(`${this.api_base}/documentation/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.success && data.results) {
                this.show_search_results(data.results);
            }
        } catch (error) {
            console.error('Error searching:', error);
        }
    }

    /**
     * Show search results.
     */
    show_search_results(results) {
        document.querySelector('.article-view').classList.add('hidden');
        document.querySelector('.search-results').classList.remove('hidden');
        
        const results_list = document.querySelector('.search-results-list');
        results_list.innerHTML = '';
        
        results.forEach(result => {
            const item = document.createElement('div');
            item.className = 'search-result-item';
            item.innerHTML = `
                <h4>${result.title}</h4>
                <p class="category">${result.category}</p>
                <p class="excerpt">${result.excerpt}</p>
                <a href="#" class="read-more" data-article-id="${result.article_id}">Read More →</a>
            `;
            
            item.querySelector('.read-more').addEventListener('click', (e) => {
                e.preventDefault();
                this.load_article(result.article_id);
                this.close_search_results();
            });
            
            results_list.appendChild(item);
        });
    }

    /**
     * Close search results.
     */
    close_search_results() {
        document.querySelector('.article-view').classList.remove('hidden');
        document.querySelector('.search-results').classList.add('hidden');
    }

    /**
     * Toggle bookmark.
     */
    toggle_bookmark(btn) {
        btn.classList.toggle('bookmarked');
        // Send to backend
    }

    /**
     * Mark article as helpful.
     */
    mark_article_helpful() {
        const btn = document.querySelector('.helpful-btn');
        btn.classList.add('voted');
        btn.textContent = '✓ Helpful';
        
        // Disable further voting
        btn.disabled = true;
    }

    /**
     * Navigate between articles.
     */
    navigate_article(direction) {
        // Implementation would track current article and navigate
        console.log(`Navigate ${direction}`);
    }

    /**
     * Show contextual help for element.
     */
    show_contextual_help(element) {
        const context = element.closest('[data-help-topic]');
        if (context) {
            const topic = context.getAttribute('data-help-topic');
            this.open_help_dialog();
            this.search(topic);
        }
    }

    /**
     * Focus search input.
     */
    focus_search() {
        document.querySelector('.help-search-input').focus();
        document.querySelector('.help-search-input').select();
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.documentation_ui = new DocumentationUI();
});
