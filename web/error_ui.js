/**
 * Error Messages UI Controller (Issue #51)
 * 
 * Professional error display, recovery suggestions, and error management UI.
 */

class ErrorMessagesUI {
    constructor() {
        this.currentErrorId = null;
        this.errorPanel = null;
        this.notificationContainer = null;
        this.errorHistoryPanel = null;
        this.filterLevel = 'all';
        this.isMinimized = false;
        
        this.initializeUI();
    }

    initializeUI() {
        /**
         * Initialize error UI components.
         */
        this.createErrorPanel();
        this.createNotificationContainer();
        this.createErrorHistory();
        this.attachEventHandlers();
    }

    createErrorPanel() {
        /**
         * Create main error panel.
         */
        this.errorPanel = document.createElement('div');
        this.errorPanel.id = 'error-panel';
        this.errorPanel.className = 'error-panel hidden';
        this.errorPanel.innerHTML = `
            <div class="error-header">
                <div class="error-title">
                    <span class="error-icon" id="error-icon"></span>
                    <span id="error-message">No errors</span>
                </div>
                <div class="error-controls">
                    <button class="error-minimize-btn" id="minimize-error" title="Minimize">−</button>
                    <button class="error-close-btn" id="close-error" title="Close">×</button>
                </div>
            </div>
            <div class="error-content" id="error-content">
                <div class="error-details">
                    <p class="error-description" id="error-description"></p>
                    <div class="error-context" id="error-context"></div>
                </div>
                <div class="error-suggestions">
                    <h4>Recovery Options</h4>
                    <div class="suggestions-list" id="suggestions-list"></div>
                </div>
                <div class="error-actions">
                    <button class="btn btn-primary" id="apply-recovery">Apply Suggestion</button>
                    <button class="btn btn-secondary" id="view-details">Details</button>
                    <button class="btn btn-secondary" id="mark-resolved">Mark Resolved</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(this.errorPanel);
    }

    createNotificationContainer() {
        /**
         * Create toast notification container.
         */
        this.notificationContainer = document.createElement('div');
        this.notificationContainer.id = 'error-notifications';
        this.notificationContainer.className = 'error-notifications';
        document.body.appendChild(this.notificationContainer);
    }

    createErrorHistory() {
        /**
         * Create error history panel.
         */
        this.errorHistoryPanel = document.createElement('div');
        this.errorHistoryPanel.id = 'error-history';
        this.errorHistoryPanel.className = 'error-history-panel';
        this.errorHistoryPanel.innerHTML = `
            <div class="history-header">
                <h3>Error History</h3>
                <div class="history-controls">
                    <select id="severity-filter" class="filter-select">
                        <option value="all">All Severities</option>
                        <option value="info">Info</option>
                        <option value="warning">Warning</option>
                        <option value="error">Error</option>
                        <option value="critical">Critical</option>
                    </select>
                    <button class="btn btn-small" id="clear-history">Clear</button>
                </div>
            </div>
            <div class="history-list" id="history-list"></div>
        `;
        
        document.body.appendChild(this.errorHistoryPanel);
    }

    attachEventHandlers() {
        /**
         * Attach event handlers to UI elements.
         */
        document.getElementById('close-error').addEventListener('click', () => this.hideError());
        document.getElementById('minimize-error').addEventListener('click', () => this.toggleMinimize());
        document.getElementById('clear-history').addEventListener('click', () => this.clearHistory());
        document.getElementById('severity-filter').addEventListener('change', (e) => {
            this.filterLevel = e.target.value;
            this.updateHistoryDisplay();
        });
        document.getElementById('mark-resolved').addEventListener('click', () => {
            this.emitEvent('mark-resolved', { errorId: this.currentErrorId });
        });
    }

    displayError(errorData) {
        /**
         * Display error message to user.
         * 
         * @param {Object} errorData - Error data from system
         */
        this.currentErrorId = errorData.id;
        
        // Update main display
        const icon = this.getSeverityIcon(errorData.severity);
        document.getElementById('error-icon').innerHTML = icon;
        document.getElementById('error-icon').className = `error-icon severity-${errorData.severity}`;
        document.getElementById('error-message').textContent = errorData.message;
        document.getElementById('error-description').textContent = errorData.message;
        
        // Display context information
        const contextDiv = document.getElementById('error-context');
        contextDiv.innerHTML = '';
        if (Object.keys(errorData.context).length > 0) {
            const contextHtml = Object.entries(errorData.context)
                .map(([key, value]) => `<div class="context-item"><span class="context-key">${key}:</span> <span class="context-value">${value}</span></div>`)
                .join('');
            contextDiv.innerHTML = `<div class="context-info">${contextHtml}</div>`;
        }
        
        // Display recovery suggestions
        this.displaySuggestions(errorData.recovery_suggestions || []);
        
        // Update styling
        this.errorPanel.className = `error-panel severity-${errorData.severity}`;
        this.errorPanel.classList.remove('hidden');
        
        // Show notification
        this.showNotification(errorData.message, errorData.severity);
        
        // Add to history
        this.addToHistory(errorData);
    }

    displaySuggestions(suggestions) {
        /**
         * Display recovery suggestions.
         * 
         * @param {Array} suggestions - Recovery suggestions
         */
        const list = document.getElementById('suggestions-list');
        list.innerHTML = '';
        
        if (suggestions.length === 0) {
            list.innerHTML = '<p class="no-suggestions">No recovery options available</p>';
            return;
        }
        
        suggestions.forEach((suggestion, index) => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            if (suggestion.is_automatic) div.classList.add('automatic');
            
            div.innerHTML = `
                <div class="suggestion-radio">
                    <input type="radio" name="recovery-option" value="${suggestion.id}" ${index === 0 ? 'checked' : ''} id="sug-${suggestion.id}">
                </div>
                <div class="suggestion-content">
                    <label for="sug-${suggestion.id}" class="suggestion-title">${suggestion.title}</label>
                    <p class="suggestion-description">${suggestion.description}</p>
                    ${suggestion.is_automatic ? '<span class="auto-badge">Automatic</span>' : ''}
                </div>
            `;
            
            list.appendChild(div);
        });
    }

    getSeverityIcon(severity) {
        /**
         * Get icon for severity level.
         */
        const icons = {
            'info': 'ℹ',
            'warning': '⚠',
            'error': '✕',
            'critical': '⚡'
        };
        return icons[severity] || '●';
    }

    showNotification(message, severity = 'info', duration = 5000) {
        /**
         * Show toast notification.
         * 
         * @param {string} message - Notification message
         * @param {string} severity - Severity level
         * @param {number} duration - Duration in ms
         */
        const notification = document.createElement('div');
        notification.className = `error-notification severity-${severity}`;
        notification.innerHTML = `
            <span class="notification-icon">${this.getSeverityIcon(severity)}</span>
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        `;
        
        this.notificationContainer.appendChild(notification);
        
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
        
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, duration);
        }
    }

    hideError() {
        /**
         * Hide error panel.
         */
        this.errorPanel.classList.add('hidden');
        this.currentErrorId = null;
    }

    toggleMinimize() {
        /**
         * Toggle error panel minimization.
         */
        this.isMinimized = !this.isMinimized;
        const content = this.errorPanel.querySelector('.error-content');
        if (this.isMinimized) {
            content.style.display = 'none';
            this.errorPanel.classList.add('minimized');
        } else {
            content.style.display = 'block';
            this.errorPanel.classList.remove('minimized');
        }
    }

    addToHistory(errorData) {
        /**
         * Add error to history.
         */
        const historyList = document.getElementById('history-list');
        
        const item = document.createElement('div');
        item.className = `history-item severity-${errorData.severity}`;
        item.innerHTML = `
            <div class="history-item-header">
                <span class="history-icon">${this.getSeverityIcon(errorData.severity)}</span>
                <span class="history-time">${new Date(errorData.timestamp).toLocaleTimeString()}</span>
                <span class="history-status ${errorData.is_resolved ? 'resolved' : 'unresolved'}">
                    ${errorData.is_resolved ? '✓ Resolved' : 'Unresolved'}
                </span>
            </div>
            <div class="history-item-message">${errorData.message}</div>
        `;
        
        item.addEventListener('click', () => {
            this.emitEvent('error-selected', { errorId: errorData.id });
        });
        
        historyList.insertBefore(item, historyList.firstChild);
        
        // Limit history display
        while (historyList.children.length > 20) {
            historyList.removeChild(historyList.lastChild);
        }
    }

    updateHistoryDisplay() {
        /**
         * Update history based on current filter.
         */
        const items = document.querySelectorAll('.history-item');
        items.forEach(item => {
            if (this.filterLevel === 'all' || item.classList.contains(`severity-${this.filterLevel}`)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    clearHistory() {
        /**
         * Clear error history display.
         */
        document.getElementById('history-list').innerHTML = '';
        this.emitEvent('clear-history', {});
    }

    getSelectedSuggestion() {
        /**
         * Get currently selected recovery suggestion.
         */
        const selected = document.querySelector('input[name="recovery-option"]:checked');
        return selected ? selected.value : null;
    }

    displayStatistics(stats) {
        /**
         * Display error statistics.
         */
        const statsDiv = document.createElement('div');
        statsDiv.className = 'error-statistics';
        statsDiv.innerHTML = `
            <div class="stat-item">
                <span class="stat-label">Total Errors:</span>
                <span class="stat-value">${stats.total_errors}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Resolved:</span>
                <span class="stat-value resolved">${stats.resolved_errors}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Unresolved:</span>
                <span class="stat-value unresolved">${stats.unresolved_errors}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Critical:</span>
                <span class="stat-value critical">${stats.critical_count}</span>
            </div>
        `;
        
        this.showNotification('Statistics updated', 'info', 3000);
    }

    emitEvent(eventName, data) {
        /**
         * Emit custom event.
         */
        const event = new CustomEvent(`error-ui:${eventName}`, { detail: data });
        document.dispatchEvent(event);
    }

    on(eventName, callback) {
        /**
         * Listen for UI events.
         */
        document.addEventListener(`error-ui:${eventName}`, (e) => {
            callback(e.detail);
        });
    }

    reset() {
        /**
         * Reset UI to initial state.
         */
        this.hideError();
        this.currentErrorId = null;
        this.isMinimized = false;
        document.getElementById('history-list').innerHTML = '';
        this.notificationContainer.innerHTML = '';
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ErrorMessagesUI;
}
