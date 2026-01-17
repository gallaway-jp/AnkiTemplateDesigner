/**
 * Panel Synchronization UI Controller (Issue #53)
 * 
 * Manages UI updates for panel synchronization and consistency.
 */

class PanelSyncUI {
    constructor() {
        this.syncIndicator = null;
        this.consistencyIndicator = null;
        this.panelStates = new Map();
        this.isSyncing = false;
        this.lastSyncTime = null;
        
        this.initializeUI();
    }

    initializeUI() {
        this.createSyncIndicator();
        this.createConsistencyIndicator();
        this.attachEventHandlers();
    }

    createSyncIndicator() {
        /**Create sync status indicator.*/
        this.syncIndicator = document.createElement('div');
        this.syncIndicator.id = 'panel-sync-indicator';
        this.syncIndicator.className = 'panel-sync-indicator';
        this.syncIndicator.innerHTML = `
            <span class="sync-status-icon">⟳</span>
            <span class="sync-status-text">Synced</span>
        `;
        document.body.appendChild(this.syncIndicator);
    }

    createConsistencyIndicator() {
        /**Create consistency status display.*/
        this.consistencyIndicator = document.createElement('div');
        this.consistencyIndicator.id = 'consistency-indicator';
        this.consistencyIndicator.className = 'consistency-indicator';
        this.consistencyIndicator.innerHTML = `
            <span class="consistency-icon">✓</span>
            <span class="consistency-text">All panels consistent</span>
        `;
        document.body.appendChild(this.consistencyIndicator);
    }

    attachEventHandlers() {
        /**Attach event handlers.*/
        this.syncIndicator.addEventListener('click', () => {
            this.showSyncDetails();
        });
        
        this.consistencyIndicator.addEventListener('click', () => {
            this.showConsistencyDetails();
        });
    }

    updateSyncStatus(isSync ing) {
        /**
         * Update sync indicator.
         * 
         * @param {boolean} isSyncing - Whether syncing
         */
        this.isSyncing = isSyncing;
        
        if (isSyncing) {
            this.syncIndicator.classList.add('syncing');
            this.syncIndicator.querySelector('.sync-status-text').textContent = 'Syncing...';
        } else {
            this.syncIndicator.classList.remove('syncing');
            this.syncIndicator.querySelector('.sync-status-text').textContent = 'Synced';
            this.lastSyncTime = new Date();
        }
    }

    updateConsistencyStatus(isConsistent, dirtyPanels) {
        /**
         * Update consistency indicator.
         * 
         * @param {boolean} isConsistent - All panels consistent
         * @param {Array} dirtyPanels - List of inconsistent panels
         */
        if (isConsistent) {
            this.consistencyIndicator.classList.remove('inconsistent');
            this.consistencyIndicator.querySelector('.consistency-text').textContent = 'All panels consistent';
        } else {
            this.consistencyIndicator.classList.add('inconsistent');
            this.consistencyIndicator.querySelector('.consistency-text').textContent = `${dirtyPanels.length} panels need sync`;
        }
    }

    updatePanelState(panelType, state) {
        /**
         * Update panel state display.
         * 
         * @param {string} panelType - Panel type
         * @param {Object} state - Panel state
         */
        this.panelStates.set(panelType, state);
        
        const panelElement = document.querySelector(`[data-panel-type="${panelType}"]`);
        if (panelElement) {
            if (state.dirty) {
                panelElement.classList.add('panel-dirty');
            } else {
                panelElement.classList.remove('panel-dirty');
            }
            
            if (state.focused) {
                document.querySelectorAll('[data-panel-type]').forEach(el => {
                    el.classList.remove('panel-focused');
                });
                panelElement.classList.add('panel-focused');
            }
        }
    }

    showSyncDetails() {
        /**Show sync details dialog.*/
        const dialog = document.createElement('div');
        dialog.className = 'sync-details-dialog';
        dialog.innerHTML = `
            <div class="dialog-header">
                <h3>Panel Synchronization</h3>
                <button class="close-btn">×</button>
            </div>
            <div class="dialog-content">
                <div class="sync-info">
                    <p><strong>Status:</strong> ${this.isSyncing ? 'Syncing...' : 'Idle'}</p>
                    <p><strong>Last Sync:</strong> ${this.lastSyncTime ? this.lastSyncTime.toLocaleTimeString() : 'Never'}</p>
                </div>
                <div class="panel-list">
                    <h4>Panel States</h4>
                    ${Array.from(this.panelStates.entries()).map(([type, state]) => `
                        <div class="panel-item ${state.dirty ? 'dirty' : 'clean'}">
                            <span class="panel-name">${type}</span>
                            <span class="panel-status">${state.dirty ? '⚠ Dirty' : '✓ Clean'}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        dialog.querySelector('.close-btn').addEventListener('click', () => {
            dialog.remove();
        });
        
        dialog.addEventListener('click', (e) => {
            if (e.target === dialog) dialog.remove();
        });
    }

    showConsistencyDetails() {
        /**Show consistency details.*/
        const dialog = document.createElement('div');
        dialog.className = 'consistency-dialog';
        dialog.innerHTML = `
            <div class="dialog-header">
                <h3>Consistency Check</h3>
                <button class="close-btn">×</button>
            </div>
            <div class="dialog-content">
                <div class="consistency-status">
                    <div class="status-item">
                        <span class="status-label">Total Panels:</span>
                        <span class="status-value">${this.panelStates.size}</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Consistent:</span>
                        <span class="status-value clean">${Array.from(this.panelStates.values()).filter(s => !s.dirty).length}</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Dirty:</span>
                        <span class="status-value dirty">${Array.from(this.panelStates.values()).filter(s => s.dirty).length}</span>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        dialog.querySelector('.close-btn').addEventListener('click', () => {
            dialog.remove();
        });
    }

    notifySyncEvent(eventType, data) {
        /**
         * Notify of sync event.
         * 
         * @param {string} eventType - Event type
         * @param {Object} data - Event data
         */
        const notification = document.createElement('div');
        notification.className = `sync-notification ${eventType}`;
        notification.innerHTML = `
            <span class="icon">⟳</span>
            <span class="message">${data.message || eventType}</span>
        `;
        
        document.querySelector('#panel-sync-indicator').appendChild(notification);
        
        setTimeout(() => notification.remove(), 3000);
    }

    emitEvent(eventName, data) {
        /**Emit custom event.*/
        const event = new CustomEvent(`panelsync:${eventName}`, { detail: data });
        document.dispatchEvent(event);
    }

    on(eventName, callback) {
        /**Listen for events.*/
        document.addEventListener(`panelsync:${eventName}`, (e) => {
            callback(e.detail);
        });
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = PanelSyncUI;
}
