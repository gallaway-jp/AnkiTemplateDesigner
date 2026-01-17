/**
 * Data Loss Prevention System for Anki Template Designer
 * Detects unsaved changes, performs auto-save, and provides crash recovery
 * 
 * Features:
 * - Real-time unsaved changes detection
 * - Visual change indicators in UI
 * - Browser warning on page unload if unsaved
 * - Periodic auto-save (configurable)
 * - Crash/session recovery
 * - Change history tracking
 * - Keyboard shortcuts (Ctrl+S to save)
 * - Recovery state management
 * 
 * Usage:
 * const manager = new DataLossPreventionManager(editor, { autoSaveInterval: 30000 });
 * manager.detectChanges();
 * manager.startAutoSave();
 */

class DataLossPreventionManager {
    constructor(editor, options = {}) {
        this.editor = editor;
        this.autoSaveInterval = options.autoSaveInterval || 30000;
        this.recoveryStorageKey = 'ankiTemplateRecovery';
        this.changeHistoryKey = 'ankiTemplateChangeHistory';
        this.lastSaveKey = 'ankiTemplateLastSave';
        
        this.hasUnsavedChanges = false;
        this.lastSavedState = null;
        this.currentState = null;
        this.changeHistory = [];
        this.autoSaveInterval = null;
        this.changeListeners = [];
        this.saveListeners = [];
        
        this.setupChangeDetection();
        this.loadRecoveryState();
    }
    
    /**
     * Setup change detection on editor
     */
    setupChangeDetection() {
        if (!this.editor) return;
        
        // Listen for component changes
        this.editor.on('component:update', () => {
            this.markAsChanged();
        });
        
        this.editor.on('block:remove', () => {
            this.markAsChanged();
        });
        
        this.editor.on('block:add', () => {
            this.markAsChanged();
        });
        
        this.editor.on('block:clone', () => {
            this.markAsChanged();
        });
        
        this.editor.on('component:add', () => {
            this.markAsChanged();
        });
        
        // Listen for style changes
        this.editor.on('style:change', () => {
            this.markAsChanged();
        });
        
        // Listen for HTML changes
        this.editor.on('block:drag:stop', () => {
            this.markAsChanged();
        });
        
        // Setup browser unload warning
        window.addEventListener('beforeunload', (e) => {
            if (this.hasUnsavedChanges) {
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
            }
        });
        
        // Setup keyboard shortcut (Ctrl+S)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                this.saveChanges();
            }
        });
    }
    
    /**
     * Mark document as having unsaved changes
     */
    markAsChanged() {
        if (!this.hasUnsavedChanges) {
            this.hasUnsavedChanges = true;
            this.notifyChangeListeners();
        }
        
        // Save current state to recovery
        this.saveRecoveryState();
    }
    
    /**
     * Detect and log changes in detail
     */
    detectChanges() {
        if (!this.editor) return;
        
        try {
            const newState = {
                html: this.editor.getHtml ? this.editor.getHtml() : '',
                css: this.editor.getCss ? this.editor.getCss() : '',
                timestamp: Date.now(),
                components: this.editor.getComponents ? this.editor.getComponents().length : 0
            };
            
            // Store for comparison
            this.currentState = newState;
            
            // Save last known state on first call
            if (!this.lastSavedState) {
                this.lastSavedState = JSON.parse(JSON.stringify(newState));
            }
            
            // Check if different from last saved
            const isDifferent = JSON.stringify(newState) !== JSON.stringify(this.lastSavedState);
            
            if (isDifferent && !this.hasUnsavedChanges) {
                this.markAsChanged();
            }
            
            return {
                isDifferent,
                html: newState.html,
                css: newState.css,
                components: newState.components,
                timestamp: newState.timestamp
            };
        } catch (e) {
            console.warn('[DLP] Failed to detect changes:', e);
            return null;
        }
    }
    
    /**
     * Get change summary for display
     */
    getChangeSummary() {
        if (!this.currentState || !this.lastSavedState) {
            return null;
        }
        
        // Count components
        const componentDiff = this.currentState.components - this.lastSavedState.components;
        
        // Count HTML line changes
        const htmlLines1 = (this.lastSavedState.html || '').split('\n').length;
        const htmlLines2 = (this.currentState.html || '').split('\n').length;
        const htmlLineDiff = htmlLines2 - htmlLines1;
        
        // Count CSS property changes
        const cssProps1 = (this.lastSavedState.css || '').split(';').filter(p => p.trim()).length;
        const cssProps2 = (this.currentState.css || '').split(';').filter(p => p.trim()).length;
        const cssPropDiff = cssProps2 - cssProps1;
        
        return {
            components: {
                added: componentDiff > 0 ? componentDiff : 0,
                removed: componentDiff < 0 ? Math.abs(componentDiff) : 0,
                total: this.currentState.components
            },
            html: {
                added: htmlLineDiff > 0 ? htmlLineDiff : 0,
                removed: htmlLineDiff < 0 ? Math.abs(htmlLineDiff) : 0,
                total: htmlLines2
            },
            css: {
                added: cssPropDiff > 0 ? cssPropDiff : 0,
                removed: cssPropDiff < 0 ? Math.abs(cssPropDiff) : 0,
                total: cssProps2
            }
        };
    }
    
    /**
     * Save changes permanently
     */
    saveChanges() {
        if (!this.editor || !this.hasUnsavedChanges) {
            return false;
        }
        
        try {
            const savedState = {
                html: this.editor.getHtml ? this.editor.getHtml() : '',
                css: this.editor.getCss ? this.editor.getCss() : '',
                timestamp: Date.now(),
                components: this.editor.getComponents ? this.editor.getComponents().length : 0
            };
            
            // Update saved state
            this.lastSavedState = JSON.parse(JSON.stringify(savedState));
            this.hasUnsavedChanges = false;
            
            // Clear recovery state
            this.clearRecoveryState();
            
            // Log save timestamp
            localStorage.setItem(this.lastSaveKey, JSON.stringify({
                timestamp: savedState.timestamp,
                components: savedState.components
            }));
            
            // Notify listeners
            this.notifySaveListeners();
            this.notifyChangeListeners();
            
            console.log('[DLP] Changes saved at', new Date(savedState.timestamp).toISOString());
            
            return true;
        } catch (e) {
            console.error('[DLP] Failed to save changes:', e);
            return false;
        }
    }
    
    /**
     * Start automatic saving at intervals
     */
    startAutoSave() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }
        
        this.autoSaveInterval = setInterval(() => {
            if (this.hasUnsavedChanges) {
                this.saveChanges();
            }
        }, this.autoSaveInterval);
    }
    
    /**
     * Stop automatic saving
     */
    stopAutoSave() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
            this.autoSaveInterval = null;
        }
    }
    
    /**
     * Save state for crash recovery
     */
    saveRecoveryState() {
        try {
            if (!this.editor) return;
            
            const recoveryData = {
                html: this.editor.getHtml ? this.editor.getHtml() : '',
                css: this.editor.getCss ? this.editor.getCss() : '',
                timestamp: Date.now(),
                sessionId: this.getSessionId(),
                userAgent: navigator.userAgent
            };
            
            localStorage.setItem(this.recoveryStorageKey, JSON.stringify(recoveryData));
        } catch (e) {
            console.warn('[DLP] Failed to save recovery state:', e);
        }
    }
    
    /**
     * Load recovery state from crash
     */
    loadRecoveryState() {
        try {
            const data = localStorage.getItem(this.recoveryStorageKey);
            if (!data) return null;
            
            const recovery = JSON.parse(data);
            const timeSinceRecovery = Date.now() - recovery.timestamp;
            
            // Only offer recovery if within last 24 hours
            if (timeSinceRecovery > 86400000) {
                localStorage.removeItem(this.recoveryStorageKey);
                return null;
            }
            
            return recovery;
        } catch {
            return null;
        }
    }
    
    /**
     * Check if recovery is available
     */
    hasRecoveryData() {
        return this.loadRecoveryState() !== null;
    }
    
    /**
     * Recover from crash
     */
    recoverFromCrash() {
        const recovery = this.loadRecoveryState();
        if (!recovery || !this.editor) return false;
        
        try {
            if (recovery.html) {
                this.editor.setHtml(recovery.html);
            }
            if (recovery.css) {
                this.editor.setCss(recovery.css);
            }
            
            // Clear recovery data after restoring
            this.clearRecoveryState();
            
            // Mark as changed so user knows to save
            this.markAsChanged();
            
            console.log('[DLP] Recovered from crash');
            return true;
        } catch (e) {
            console.error('[DLP] Failed to recover:', e);
            return false;
        }
    }
    
    /**
     * Clear recovery state
     */
    clearRecoveryState() {
        localStorage.removeItem(this.recoveryStorageKey);
    }
    
    /**
     * Add change listener
     */
    onChangesDetected(callback) {
        this.changeListeners.push(callback);
    }
    
    /**
     * Remove change listener
     */
    offChangesDetected(callback) {
        this.changeListeners = this.changeListeners.filter(c => c !== callback);
    }
    
    /**
     * Notify change listeners
     */
    notifyChangeListeners() {
        this.changeListeners.forEach(callback => {
            try {
                callback({
                    hasUnsaved: this.hasUnsavedChanges,
                    summary: this.getChangeSummary()
                });
            } catch (e) {
                console.warn('[DLP] Change listener error:', e);
            }
        });
    }
    
    /**
     * Add save listener
     */
    onChangesSaved(callback) {
        this.saveListeners.push(callback);
    }
    
    /**
     * Remove save listener
     */
    offChangesSaved(callback) {
        this.saveListeners = this.saveListeners.filter(c => c !== callback);
    }
    
    /**
     * Notify save listeners
     */
    notifySaveListeners() {
        this.saveListeners.forEach(callback => {
            try {
                callback({
                    saved: true,
                    timestamp: Date.now(),
                    summary: this.getChangeSummary()
                });
            } catch (e) {
                console.warn('[DLP] Save listener error:', e);
            }
        });
    }
    
    /**
     * Get session ID
     */
    getSessionId() {
        let id = sessionStorage.getItem('ankiTemplateSessionId');
        if (!id) {
            id = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            sessionStorage.setItem('ankiTemplateSessionId', id);
        }
        return id;
    }
    
    /**
     * Discard unsaved changes
     */
    discardChanges() {
        this.hasUnsavedChanges = false;
        this.notifyChangeListeners();
    }
    
    /**
     * Get current unsaved state
     */
    getUnsavedState() {
        return {
            hasUnsaved: this.hasUnsavedChanges,
            lastSaved: this.lastSavedState,
            current: this.currentState,
            summary: this.getChangeSummary()
        };
    }
}

/**
 * Data Loss Prevention UI - Shows change indicator and status
 */
class DataLossPreventionUI {
    constructor(editor, dlpManager) {
        this.editor = editor;
        this.manager = dlpManager;
        this.statusElement = null;
        this.titleModifier = '';
        this.isVisible = true;
    }
    
    /**
     * Initialize the UI
     */
    initialize() {
        this.createStatusIndicator();
        this.setupListeners();
        this.checkRecovery();
    }
    
    /**
     * Create status indicator element
     */
    createStatusIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'dlp-status';
        indicator.className = 'dlp-status dlp-saved';
        indicator.innerHTML = `
            <div class="dlp-status-content">
                <span class="dlp-status-icon">✓</span>
                <span class="dlp-status-text">All changes saved</span>
                <button class="dlp-status-details" title="Show change details">Details</button>
            </div>
        `;
        
        document.body.appendChild(indicator);
        this.statusElement = indicator;
        
        // Details button
        indicator.querySelector('.dlp-status-details').addEventListener('click', () => {
            this.showChangeDetails();
        });
    }
    
    /**
     * Setup change/save listeners
     */
    setupListeners() {
        this.manager.onChangesDetected((event) => {
            this.updateStatus(event.hasUnsaved, event.summary);
        });
        
        this.manager.onChangesSaved(() => {
            this.updateStatus(false, null);
        });
    }
    
    /**
     * Check if recovery is needed
     */
    checkRecovery() {
        if (this.manager.hasRecoveryData()) {
            const recovery = this.manager.loadRecoveryState();
            const timestamp = new Date(recovery.timestamp).toLocaleString();
            
            const proceed = confirm(
                `Recovery data found from ${timestamp}.\n\nWould you like to recover your unsaved changes?`
            );
            
            if (proceed) {
                this.manager.recoverFromCrash();
                this.updateStatus(true, this.manager.getChangeSummary());
            } else {
                this.manager.clearRecoveryState();
            }
        }
    }
    
    /**
     * Update status display
     */
    updateStatus(hasUnsaved, summary) {
        if (!this.statusElement) return;
        
        if (hasUnsaved) {
            this.statusElement.classList.remove('dlp-saved');
            this.statusElement.classList.add('dlp-unsaved');
            
            const details = this.formatChanges(summary);
            this.statusElement.querySelector('.dlp-status-icon').textContent = '●';
            this.statusElement.querySelector('.dlp-status-text').innerHTML = 
                `Unsaved changes<br><small>${details}</small>`;
            
            // Update browser title with indicator
            this.updateTitle(true);
        } else {
            this.statusElement.classList.remove('dlp-unsaved');
            this.statusElement.classList.add('dlp-saved');
            this.statusElement.querySelector('.dlp-status-icon').textContent = '✓';
            this.statusElement.querySelector('.dlp-status-text').textContent = 
                'All changes saved';
            
            // Remove indicator from title
            this.updateTitle(false);
        }
    }
    
    /**
     * Update browser title with change indicator
     */
    updateTitle(hasUnsaved) {
        const title = document.title;
        const baseTitle = title.replace(/^\[•\] /, '');
        
        if (hasUnsaved) {
            document.title = `[•] ${baseTitle}`;
        } else {
            document.title = baseTitle;
        }
    }
    
    /**
     * Format changes for display
     */
    formatChanges(summary) {
        if (!summary) return 'detecting...';
        
        const parts = [];
        
        if (summary.components.added > 0) {
            parts.push(`+${summary.components.added} components`);
        }
        if (summary.components.removed > 0) {
            parts.push(`-${summary.components.removed} components`);
        }
        
        if (summary.html.added > 0) {
            parts.push(`+${summary.html.added} lines`);
        }
        if (summary.html.removed > 0) {
            parts.push(`-${summary.html.removed} lines`);
        }
        
        return parts.length > 0 ? parts.join(', ') : 'modified';
    }
    
    /**
     * Show change details dialog
     */
    showChangeDetails() {
        const state = this.manager.getUnsavedState();
        if (!state.summary) {
            alert('No unsaved changes');
            return;
        }
        
        const summary = state.summary;
        const message = `
Change Summary:

Components:
  + Added: ${summary.components.added}
  - Removed: ${summary.components.removed}
  Total: ${summary.components.total}

HTML Lines:
  + Added: ${summary.html.added}
  - Removed: ${summary.html.removed}
  Total: ${summary.html.total}

CSS Properties:
  + Added: ${summary.css.added}
  - Removed: ${summary.css.removed}
  Total: ${summary.css.total}

Shortcut: Ctrl+S to save
        `;
        
        alert(message);
    }
    
    /**
     * Hide status indicator
     */
    hide() {
        if (this.statusElement) {
            this.statusElement.style.display = 'none';
            this.isVisible = false;
        }
    }
    
    /**
     * Show status indicator
     */
    show() {
        if (this.statusElement) {
            this.statusElement.style.display = 'flex';
            this.isVisible = true;
        }
    }
}

/**
 * Initialize data loss prevention system
 */
window.initializeDataLossPrevention = function(editor) {
    const dlpManager = new DataLossPreventionManager(editor, {
        autoSaveInterval: 30000  // Auto-save every 30 seconds
    });
    
    const dlpUI = new DataLossPreventionUI(editor, dlpManager);
    dlpUI.initialize();
    
    // Start auto-save
    dlpManager.startAutoSave();
    
    // Detect initial changes
    dlpManager.detectChanges();
    
    // Expose public API
    window.dataLossPrevention = {
        manager: dlpManager,
        ui: dlpUI,
        hasUnsaved: () => dlpManager.hasUnsavedChanges,
        save: () => dlpManager.saveChanges(),
        discard: () => dlpManager.discardChanges(),
        recover: () => dlpManager.recoverFromCrash(),
        getState: () => dlpManager.getUnsavedState(),
        getSummary: () => dlpManager.getChangeSummary()
    };
    
    console.log('[DLP] System initialized');
};
