/**
 * Issue #49: Undo/Redo History System - Frontend UI
 * 
 * Complete JavaScript controller for managing undo/redo history panel,
 * including visual timeline, branching visualization, and history navigation.
 */

class HistoryPanelUI {
    /**
     * Initialize the history panel UI.
     * 
     * @param {HTMLElement} container - Container element for history panel
     * @param {Object} backendAPI - Backend API object with undo/redo methods
     */
    constructor(container, backendAPI = null) {
        this.container = container;
        this.backendAPI = backendAPI;
        
        this.currentBranch = null;
        this.actions = [];
        this.currentIndex = -1;
        this.branches = [];
        
        this.selectedAction = null;
        this.isExpanded = false;
        
        this.initialize();
    }

    /**
     * Initialize the history panel.
     */
    initialize() {
        this.createPanelStructure();
        this.setupEventListeners();
        this.registerKeyboardShortcuts();
    }

    /**
     * Create the history panel HTML structure.
     */
    createPanelStructure() {
        this.container.innerHTML = `
            <div class="history-panel">
                <div class="history-header">
                    <h3>History</h3>
                    <div class="history-controls">
                        <button class="undo-btn" title="Undo (Ctrl+Z)">↶</button>
                        <button class="redo-btn" title="Redo (Ctrl+Y)">↷</button>
                        <button class="branch-btn" title="Show branches">⎇</button>
                        <button class="clear-btn" title="Clear history">✕</button>
                    </div>
                </div>
                
                <div class="history-body">
                    <div class="history-timeline">
                        <div class="timeline-track"></div>
                        <div class="timeline-actions"></div>
                    </div>
                </div>
                
                <div class="history-info">
                    <div class="info-stats">
                        <span class="stat-item">
                            <span class="stat-label">Undo:</span>
                            <span class="undo-count">0</span>
                        </span>
                        <span class="stat-item">
                            <span class="stat-label">Redo:</span>
                            <span class="redo-count">0</span>
                        </span>
                    </div>
                </div>
                
                <div class="history-popup" style="display: none;">
                    <div class="popup-content"></div>
                </div>

                <div class="branch-panel" style="display: none;">
                    <div class="branch-header">
                        <h4>History Branches</h4>
                        <button class="close-branches">✕</button>
                    </div>
                    <div class="branch-tree"></div>
                </div>
            </div>
        `;

        this.undoBtn = this.container.querySelector('.undo-btn');
        this.redoBtn = this.container.querySelector('.redo-btn');
        this.branchBtn = this.container.querySelector('.branch-btn');
        this.clearBtn = this.container.querySelector('.clear-btn');
        
        this.timeline = this.container.querySelector('.timeline-actions');
        this.stats = this.container.querySelector('.history-info');
        this.popup = this.container.querySelector('.history-popup');
        this.popupContent = this.popup.querySelector('.popup-content');
        this.branchPanel = this.container.querySelector('.branch-panel');
        this.branchTree = this.branchPanel.querySelector('.branch-tree');
    }

    /**
     * Set up event listeners.
     */
    setupEventListeners() {
        this.undoBtn.addEventListener('click', () => this.undo());
        this.redoBtn.addEventListener('click', () => this.redo());
        this.branchBtn.addEventListener('click', () => this.toggleBranchPanel());
        this.clearBtn.addEventListener('click', () => this.clearHistory());

        this.container.querySelector('.close-branches')?.addEventListener('click', () => {
            this.toggleBranchPanel();
        });

        this.timeline.addEventListener('click', (e) => this.handleTimelineClick(e));
        this.timeline.addEventListener('mouseover', (e) => this.handleTimelineHover(e));
    }

    /**
     * Register keyboard shortcuts.
     */
    registerKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                if (e.key === 'z') {
                    e.preventDefault();
                    this.undo();
                } else if (e.key === 'y') {
                    e.preventDefault();
                    this.redo();
                }
            }
        });
    }

    /**
     * Update history display with actions.
     * 
     * @param {Array} actions - Array of action objects
     * @param {number} currentIndex - Current position in history
     */
    updateHistory(actions, currentIndex) {
        this.actions = actions;
        this.currentIndex = currentIndex;
        
        this.renderTimeline();
        this.updateStats();
        this.updateButtons();
    }

    /**
     * Render the timeline with action nodes.
     */
    renderTimeline() {
        this.timeline.innerHTML = '';

        if (this.actions.length === 0) {
            this.timeline.innerHTML = '<div class="empty-timeline">No history yet</div>';
            return;
        }

        // Create timeline nodes
        this.actions.forEach((action, index) => {
            const node = document.createElement('div');
            node.className = 'timeline-node';
            node.dataset.index = index;
            node.dataset.actionId = action.id || index;
            
            if (index <= this.currentIndex) {
                node.classList.add('past');
            } else {
                node.classList.add('future');
            }

            if (index === this.currentIndex) {
                node.classList.add('current');
            }

            // Action type icon
            const icon = this.getActionTypeIcon(action.action_type || action.type);
            node.innerHTML = `
                <div class="node-icon" title="${action.action_type || action.type}">
                    ${icon}
                </div>
                <div class="node-label">${action.description || 'Action'}</div>
            `;

            node.addEventListener('click', () => this.selectAction(index, action));
            node.addEventListener('dblclick', () => this.jumpToAction(index));

            this.timeline.appendChild(node);
        });

        // Add timeline track
        if (this.actions.length > 0) {
            const currentNode = this.timeline.querySelector('.timeline-node.current');
            if (currentNode) {
                const offset = currentNode.offsetLeft + 15;
                this.container.querySelector('.timeline-track').style.width = offset + 'px';
            }
        }
    }

    /**
     * Get icon for action type.
     * 
     * @param {string} actionType - The action type
     * @returns {string} HTML icon
     */
    getActionTypeIcon(actionType) {
        const icons = {
            'component_add': '⊕',
            'component_remove': '⊖',
            'component_move': '⇄',
            'component_resize': '⟷',
            'property_change': '✎',
            'constraint_add': '⊟',
            'constraint_remove': '⊞',
            'style_change': '🎨',
            'layout_change': '⊞',
            'template_edit': '✎',
            'custom': '●'
        };
        return icons[actionType] || '●';
    }

    /**
     * Handle timeline click.
     * 
     * @param {Event} e - Click event
     */
    handleTimelineClick(e) {
        const node = e.target.closest('.timeline-node');
        if (node) {
            const index = parseInt(node.dataset.index);
            const action = this.actions[index];
            this.selectAction(index, action);
        }
    }

    /**
     * Handle timeline hover.
     * 
     * @param {Event} e - Hover event
     */
    handleTimelineHover(e) {
        const node = e.target.closest('.timeline-node');
        if (node) {
            const index = parseInt(node.dataset.index);
            const action = this.actions[index];
            this.showActionPreview(node, action);
        }
    }

    /**
     * Select an action.
     * 
     * @param {number} index - Action index
     * @param {Object} action - Action object
     */
    selectAction(index, action) {
        this.selectedAction = action;

        // Update UI
        this.timeline.querySelectorAll('.timeline-node').forEach(node => {
            node.classList.remove('selected');
        });
        this.timeline.querySelector(`[data-index="${index}"]`).classList.add('selected');

        // Show details
        this.showActionDetails(action);
    }

    /**
     * Show action preview tooltip.
     * 
     * @param {HTMLElement} node - Timeline node
     * @param {Object} action - Action object
     */
    showActionPreview(node, action) {
        const rect = node.getBoundingClientRect();
        
        this.popupContent.innerHTML = `
            <div class="action-preview">
                <div class="action-type">${action.action_type || action.type}</div>
                <div class="action-desc">${action.description || 'No description'}</div>
                ${action.timestamp ? `<div class="action-time">${this.formatTime(action.timestamp)}</div>` : ''}
            </div>
        `;

        this.popup.style.left = (rect.left + rect.width / 2) + 'px';
        this.popup.style.top = (rect.top - 10) + 'px';
        this.popup.style.display = 'block';
    }

    /**
     * Show detailed action information.
     * 
     * @param {Object} action - Action object
     */
    showActionDetails(action) {
        const details = `
            <div class="action-details">
                <div class="detail-row">
                    <span class="detail-label">Type:</span>
                    <span class="detail-value">${action.action_type || action.type}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Description:</span>
                    <span class="detail-value">${action.description || '-'}</span>
                </div>
                ${action.target_id ? `
                    <div class="detail-row">
                        <span class="detail-label">Target:</span>
                        <span class="detail-value">${action.target_id}</span>
                    </div>
                ` : ''}
                ${action.affected_components && action.affected_components.length > 0 ? `
                    <div class="detail-row">
                        <span class="detail-label">Affected:</span>
                        <span class="detail-value">${action.affected_components.join(', ')}</span>
                    </div>
                ` : ''}
            </div>
        `;

        // Update details panel if it exists, otherwise show in popup
        const detailsPanel = this.container.querySelector('.action-details');
        if (detailsPanel) {
            detailsPanel.innerHTML = details;
        }
    }

    /**
     * Jump to specific action in history.
     * 
     * @param {number} index - Target index
     */
    jumpToAction(index) {
        const diff = index - this.currentIndex;
        
        if (diff > 0) {
            for (let i = 0; i < diff; i++) {
                this.redo();
            }
        } else if (diff < 0) {
            for (let i = 0; i < -diff; i++) {
                this.undo();
            }
        }
    }

    /**
     * Perform undo operation.
     */
    undo() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.updateHistory(this.actions, this.currentIndex);
            
            if (this.backendAPI && typeof this.backendAPI.undo === 'function') {
                this.backendAPI.undo();
            }
        }
    }

    /**
     * Perform redo operation.
     */
    redo() {
        if (this.currentIndex < this.actions.length - 1) {
            this.currentIndex++;
            this.updateHistory(this.actions, this.currentIndex);
            
            if (this.backendAPI && typeof this.backendAPI.redo === 'function') {
                this.backendAPI.redo();
            }
        }
    }

    /**
     * Clear entire history.
     */
    clearHistory() {
        if (confirm('Clear all history? This cannot be undone.')) {
            this.actions = [];
            this.currentIndex = -1;
            this.renderTimeline();
            this.updateStats();
            this.updateButtons();
            
            if (this.backendAPI && typeof this.backendAPI.clearHistory === 'function') {
                this.backendAPI.clearHistory();
            }
        }
    }

    /**
     * Update statistics display.
     */
    updateStats() {
        const undoCount = this.currentIndex + 1;
        const redoCount = this.actions.length - this.currentIndex - 1;

        this.stats.querySelector('.undo-count').textContent = undoCount;
        this.stats.querySelector('.redo-count').textContent = redoCount;
    }

    /**
     * Update button states.
     */
    updateButtons() {
        this.undoBtn.disabled = this.currentIndex < 0;
        this.redoBtn.disabled = this.currentIndex >= this.actions.length - 1;
        this.clearBtn.disabled = this.actions.length === 0;
    }

    /**
     * Toggle branch panel visibility.
     */
    toggleBranchPanel() {
        const isVisible = this.branchPanel.style.display === 'block';
        this.branchPanel.style.display = isVisible ? 'none' : 'block';

        if (!isVisible) {
            this.renderBranchTree();
        }
    }

    /**
     * Render branch tree visualization.
     */
    renderBranchTree() {
        if (!this.backendAPI || typeof this.backendAPI.getBranchTree !== 'function') {
            this.branchTree.innerHTML = '<div class="no-branches">No branch information available</div>';
            return;
        }

        const tree = this.backendAPI.getBranchTree();
        this.branchTree.innerHTML = this.renderBranchNode(tree);
    }

    /**
     * Render a single branch node.
     * 
     * @param {Object} node - Branch node
     * @returns {string} HTML
     */
    renderBranchNode(node) {
        const isCurrent = node.is_current || false;
        const children = node.children || [];

        let html = `
            <div class="branch-node ${isCurrent ? 'current' : ''}">
                <div class="branch-info">
                    <span class="branch-name">${node.name}</span>
                    <span class="branch-depth">${node.depth || 0} actions</span>
                </div>
        `;

        if (children.length > 0) {
            html += '<div class="branch-children">';
            children.forEach(child => {
                html += this.renderBranchNode(child);
            });
            html += '</div>';
        }

        html += '</div>';
        return html;
    }

    /**
     * Format timestamp for display.
     * 
     * @param {string|Date} timestamp - Timestamp to format
     * @returns {string} Formatted time
     */
    formatTime(timestamp) {
        if (typeof timestamp === 'string') {
            timestamp = new Date(timestamp);
        }

        const now = new Date();
        const diff = now - timestamp;

        if (diff < 60000) return 'just now';
        if (diff < 3600000) return Math.floor(diff / 60000) + 'm ago';
        if (diff < 86400000) return Math.floor(diff / 3600000) + 'h ago';

        return timestamp.toLocaleDateString();
    }

    /**
     * Get current history state.
     * 
     * @returns {Object} State object
     */
    getState() {
        return {
            actions: this.actions,
            currentIndex: this.currentIndex,
            selectedAction: this.selectedAction
        };
    }

    /**
     * Set history state.
     * 
     * @param {Object} state - State object
     */
    setState(state) {
        if (state.actions) {
            this.updateHistory(state.actions, state.currentIndex || -1);
        }
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HistoryPanelUI;
}
