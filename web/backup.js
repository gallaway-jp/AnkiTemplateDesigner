/**
 * Backup Manager System for Anki Template Designer
 * Provides automatic backup, version history, restore, and comparison functionality
 * 
 * Features:
 * - Automatic backups on component changes with debounce
 * - Version history with timestamps (up to 50 snapshots)
 * - Quick restore to previous version
 * - Compare two versions side-by-side
 * - Backup export/import for sharing and external storage
 * - Local storage persistence
 * - UI panel for backup management
 * - Storage quota monitoring
 * 
 * Usage:
 * const manager = new BackupManager(editor, { maxSnapshots: 50, autoSaveInterval: 3000 });
 * manager.createBackup(metadata);
 * manager.restoreVersion(versionId);
 * manager.compareVersions(id1, id2);
 */

class BackupManager {
    constructor(editor, options = {}) {
        this.editor = editor;
        this.maxSnapshots = options.maxSnapshots || 50;
        this.autoSaveInterval = options.autoSaveInterval || 3000;
        this.storageKey = 'ankiTemplateBackups';
        this.metadataKey = 'ankiTemplateBackupMetadata';
        
        this.backups = this.loadBackups();
        this.metadata = this.loadMetadata();
        this.lastBackupTime = 0;
        this.pendingBackup = false;
        this.saveTimeout = null;
        
        this.setupEditorListeners();
    }
    
    /**
     * Setup listeners for editor changes
     */
    setupEditorListeners() {
        if (!this.editor) return;
        
        // Listen for component changes
        this.editor.on('component:update', () => {
            this.scheduleAutoBackup();
        });
        
        this.editor.on('block:remove', () => {
            this.scheduleAutoBackup();
        });
        
        this.editor.on('block:clone', () => {
            this.scheduleAutoBackup();
        });
        
        // Listen for canvas changes
        this.editor.on('change:device', () => {
            this.scheduleAutoBackup();
        });
    }
    
    /**
     * Schedule auto-backup with debounce
     */
    scheduleAutoBackup() {
        if (this.saveTimeout) {
            clearTimeout(this.saveTimeout);
        }
        
        this.pendingBackup = true;
        this.saveTimeout = setTimeout(() => {
            this.createAutoBackup();
        }, this.autoSaveInterval);
    }
    
    /**
     * Create automatic backup of current state
     */
    createAutoBackup() {
        if (!this.pendingBackup) return;
        this.pendingBackup = false;
        
        const html = this.editor ? this.editor.getHtml() : '';
        const css = this.editor ? this.editor.getCss() : '';
        
        return this.createBackup({
            type: 'auto',
            description: 'Automatic backup',
            html,
            css,
            timestamp: Date.now(),
            device: this.editor ? this.editor.getDevice() : 'desktop'
        });
    }
    
    /**
     * Create manual backup of current state
     * @param {string} description - User-provided description
     */
    createManualBackup(description = 'Manual backup') {
        const html = this.editor ? this.editor.getHtml() : '';
        const css = this.editor ? this.editor.getCss() : '';
        
        return this.createBackup({
            type: 'manual',
            description,
            html,
            css,
            timestamp: Date.now(),
            device: this.editor ? this.editor.getDevice() : 'desktop'
        });
    }
    
    /**
     * Create a backup snapshot
     * @param {object} metadata - Backup metadata
     */
    createBackup(metadata = {}) {
        const id = this.generateId();
        const timestamp = metadata.timestamp || Date.now();
        
        const backup = {
            id,
            ...metadata,
            timestamp,
            created: new Date(timestamp).toISOString(),
            size: 0
        };
        
        // Calculate size
        const serialized = JSON.stringify(backup);
        backup.size = new Blob([serialized]).size;
        
        // Add to beginning of list (most recent first)
        this.backups.unshift(backup);
        
        // Enforce max snapshots limit
        if (this.backups.length > this.maxSnapshots) {
            this.backups = this.backups.slice(0, this.maxSnapshots);
        }
        
        // Save to storage
        this.saveBackups();
        this.lastBackupTime = timestamp;
        
        return backup;
    }
    
    /**
     * Restore template to a specific version
     * @param {string} versionId - ID of version to restore
     * @returns {object} Restored backup
     */
    restoreVersion(versionId) {
        const backup = this.backups.find(b => b.id === versionId);
        if (!backup) {
            throw new Error(`Backup ${versionId} not found`);
        }
        
        if (!this.editor) {
            throw new Error('Editor not initialized');
        }
        
        // Set HTML content
        if (backup.html) {
            this.editor.setHtml(backup.html);
        }
        
        // Set CSS content
        if (backup.css) {
            this.editor.setCss(backup.css);
        }
        
        // Create restore marker
        this.createBackup({
            type: 'restore',
            description: `Restored from: ${backup.description}`,
            html: backup.html,
            css: backup.css,
            device: backup.device
        });
        
        return backup;
    }
    
    /**
     * Compare two versions
     * @param {string} id1 - First version ID
     * @param {string} id2 - Second version ID
     * @returns {object} Comparison result
     */
    compareVersions(id1, id2) {
        const backup1 = this.backups.find(b => b.id === id1);
        const backup2 = this.backups.find(b => b.id === id2);
        
        if (!backup1 || !backup2) {
            throw new Error('One or both backups not found');
        }
        
        const htmlDiff = this.computeDiff(backup1.html || '', backup2.html || '');
        const cssDiff = this.computeDiff(backup1.css || '', backup2.css || '');
        
        return {
            id1,
            id2,
            backup1: {
                id: backup1.id,
                created: backup1.created,
                description: backup1.description
            },
            backup2: {
                id: backup2.id,
                created: backup2.created,
                description: backup2.description
            },
            htmlDiff: {
                added: htmlDiff.added,
                removed: htmlDiff.removed,
                modified: htmlDiff.modified,
                similarity: htmlDiff.similarity
            },
            cssDiff: {
                added: cssDiff.added,
                removed: cssDiff.removed,
                modified: cssDiff.modified,
                similarity: cssDiff.similarity
            }
        };
    }
    
    /**
     * Simple diff computation between two strings
     * @private
     */
    computeDiff(str1, str2) {
        const lines1 = str1.split('\n');
        const lines2 = str2.split('\n');
        
        const added = lines2.filter(l => !lines1.includes(l)).length;
        const removed = lines1.filter(l => !lines2.includes(l)).length;
        const modified = Math.max(added, removed);
        
        const maxLen = Math.max(lines1.length, lines2.length);
        const similarity = maxLen > 0 ? Math.round((1 - modified / maxLen) * 100) : 100;
        
        return {
            added,
            removed,
            modified,
            similarity
        };
    }
    
    /**
     * Get all backups
     */
    getBackups() {
        return [...this.backups];
    }
    
    /**
     * Get backup by ID
     */
    getBackup(id) {
        return this.backups.find(b => b.id === id);
    }
    
    /**
     * Delete a backup
     */
    deleteBackup(id) {
        const index = this.backups.findIndex(b => b.id === id);
        if (index === -1) {
            throw new Error(`Backup ${id} not found`);
        }
        
        this.backups.splice(index, 1);
        this.saveBackups();
    }
    
    /**
     * Clear all backups
     */
    clearAllBackups() {
        this.backups = [];
        this.saveBackups();
    }
    
    /**
     * Export backups as JSON
     */
    exportBackups() {
        return {
            version: '1.0',
            exported: new Date().toISOString(),
            backups: this.backups,
            metadata: this.metadata
        };
    }
    
    /**
     * Import backups from JSON
     */
    importBackups(data) {
        if (!data.backups || !Array.isArray(data.backups)) {
            throw new Error('Invalid backup data format');
        }
        
        // Merge with existing backups (prevent duplicates)
        const ids = new Set(this.backups.map(b => b.id));
        const newBackups = data.backups.filter(b => !ids.has(b.id));
        
        this.backups = [...this.backups, ...newBackups].slice(0, this.maxSnapshots);
        this.saveBackups();
        
        return {
            imported: newBackups.length,
            total: this.backups.length
        };
    }
    
    /**
     * Get storage statistics
     */
    getStorageStats() {
        const total = this.backups.reduce((sum, b) => sum + (b.size || 0), 0);
        const count = this.backups.length;
        const oldest = this.backups[this.backups.length - 1];
        const newest = this.backups[0];
        
        try {
            const used = JSON.stringify(this.backups).length;
            const quota = 5242880; // 5MB typical quota
            const available = quota - used;
            const percentUsed = Math.round((used / quota) * 100);
            
            return {
                total,
                count,
                used,
                available,
                quota,
                percentUsed,
                oldest: oldest ? oldest.created : null,
                newest: newest ? newest.created : null
            };
        } catch {
            return {
                total,
                count,
                oldest: oldest ? oldest.created : null,
                newest: newest ? newest.created : null
            };
        }
    }
    
    /**
     * Generate unique ID
     * @private
     */
    generateId() {
        return `backup_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    /**
     * Save backups to localStorage
     * @private
     */
    saveBackups() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.backups));
        } catch (e) {
            console.warn('[Backup] Storage quota exceeded:', e);
            // Remove oldest backup and retry
            if (this.backups.length > 0) {
                this.backups.pop();
                this.saveBackups();
            }
        }
    }
    
    /**
     * Load backups from localStorage
     * @private
     */
    loadBackups() {
        try {
            const data = localStorage.getItem(this.storageKey);
            return data ? JSON.parse(data) : [];
        } catch {
            return [];
        }
    }
    
    /**
     * Save metadata to localStorage
     * @private
     */
    saveMetadata() {
        try {
            localStorage.setItem(this.metadataKey, JSON.stringify(this.metadata));
        } catch (e) {
            console.warn('[Backup] Failed to save metadata:', e);
        }
    }
    
    /**
     * Load metadata from localStorage
     * @private
     */
    loadMetadata() {
        try {
            const data = localStorage.getItem(this.metadataKey);
            return data ? JSON.parse(data) : {};
        } catch {
            return {};
        }
    }
}

/**
 * Backup UI Panel - Shows backup history and management
 */
class BackupUI {
    constructor(editor, backupManager) {
        this.editor = editor;
        this.manager = backupManager;
        this.panelElement = null;
        this.isVisible = false;
        this.currentTab = 'versions';
    }
    
    /**
     * Initialize the UI panel
     */
    initialize() {
        this.createPanel();
        this.setupEventListeners();
        this.updateDisplay();
    }
    
    /**
     * Create the backup panel HTML
     * @private
     */
    createPanel() {
        const panel = document.createElement('div');
        panel.id = 'backup-panel';
        panel.className = 'backup-panel';
        panel.innerHTML = `
            <div class="backup-header">
                <h3>Backups & History</h3>
                <button class="backup-close" aria-label="Close backup panel">×</button>
            </div>
            
            <div class="backup-tabs">
                <button class="backup-tab active" data-tab="versions" title="Backup history">
                    <span class="backup-icon">📋</span> Versions
                </button>
                <button class="backup-tab" data-tab="actions" title="Backup actions">
                    <span class="backup-icon">⚙️</span> Actions
                </button>
                <button class="backup-tab" data-tab="storage" title="Storage info">
                    <span class="backup-icon">💾</span> Storage
                </button>
            </div>
            
            <div class="backup-stats">
                <span class="backup-stat">Total: <strong id="backup-count">0</strong></span>
                <span class="backup-stat">Size: <strong id="backup-size">0 KB</strong></span>
            </div>
            
            <div class="backup-content">
                <!-- Versions Tab -->
                <div class="backup-content-tab active" data-tab="versions">
                    <div class="backup-list">
                        <div class="backup-empty">No backups yet. Changes will auto-save.</div>
                    </div>
                </div>
                
                <!-- Actions Tab -->
                <div class="backup-content-tab" data-tab="actions">
                    <div class="backup-actions">
                        <button class="backup-action-btn" id="backup-manual" title="Create manual backup">
                            📸 Create Manual Backup
                        </button>
                        <input type="text" class="backup-description" placeholder="Backup description (optional)">
                        
                        <button class="backup-action-btn" id="backup-export" title="Export backups as file">
                            📥 Export Backups
                        </button>
                        
                        <label class="backup-action-btn" title="Import backups from file">
                            📤 Import Backups
                            <input type="file" id="backup-import" accept=".json" style="display: none;">
                        </label>
                        
                        <button class="backup-action-btn backup-danger" id="backup-clear" title="Delete all backups">
                            🗑️ Clear All
                        </button>
                    </div>
                </div>
                
                <!-- Storage Tab -->
                <div class="backup-content-tab" data-tab="storage">
                    <div class="backup-storage">
                        <div class="backup-storage-item">
                            <span class="backup-storage-label">Total Backups:</span>
                            <span class="backup-storage-value" id="storage-count">0</span>
                        </div>
                        <div class="backup-storage-item">
                            <span class="backup-storage-label">Total Size:</span>
                            <span class="backup-storage-value" id="storage-total">0 KB</span>
                        </div>
                        <div class="backup-storage-item">
                            <span class="backup-storage-label">Oldest Backup:</span>
                            <span class="backup-storage-value" id="storage-oldest">None</span>
                        </div>
                        <div class="backup-storage-item">
                            <span class="backup-storage-label">Newest Backup:</span>
                            <span class="backup-storage-value" id="storage-newest">None</span>
                        </div>
                        <div class="backup-storage-bar">
                            <div class="backup-storage-used" id="storage-bar-used"></div>
                        </div>
                        <div class="backup-storage-text">
                            <span id="storage-used">0 KB</span> / <span id="storage-quota">5 MB</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(panel);
        this.panelElement = panel;
    }
    
    /**
     * Setup event listeners
     * @private
     */
    setupEventListeners() {
        // Close button
        this.panelElement.querySelector('.backup-close').addEventListener('click', () => {
            this.hide();
        });
        
        // Tab switching
        this.panelElement.querySelectorAll('.backup-tab').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.closest('.backup-tab').dataset.tab);
            });
        });
        
        // Manual backup
        this.panelElement.querySelector('#backup-manual').addEventListener('click', () => {
            const description = this.panelElement.querySelector('.backup-description').value || 'Manual backup';
            this.manager.createManualBackup(description);
            this.panelElement.querySelector('.backup-description').value = '';
            this.updateDisplay();
        });
        
        // Export
        this.panelElement.querySelector('#backup-export').addEventListener('click', () => {
            const data = this.manager.exportBackups();
            const json = JSON.stringify(data, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `anki-template-backups-${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);
        });
        
        // Import
        this.panelElement.querySelector('#backup-import').addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const data = JSON.parse(event.target.result);
                    const result = this.manager.importBackups(data);
                    alert(`Imported ${result.imported} backups. Total: ${result.total}`);
                    this.updateDisplay();
                } catch (err) {
                    alert(`Import failed: ${err.message}`);
                }
            };
            reader.readAsText(file);
            
            e.target.value = '';
        });
        
        // Clear all
        this.panelElement.querySelector('#backup-clear').addEventListener('click', () => {
            if (confirm('Delete all backups? This cannot be undone.')) {
                this.manager.clearAllBackups();
                this.updateDisplay();
            }
        });
    }
    
    /**
     * Switch active tab
     * @private
     */
    switchTab(tab) {
        this.currentTab = tab;
        
        // Update tab buttons
        this.panelElement.querySelectorAll('.backup-tab').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tab);
        });
        
        // Update content
        this.panelElement.querySelectorAll('.backup-content-tab').forEach(content => {
            content.classList.toggle('active', content.dataset.tab === tab);
        });
        
        // Update display if needed
        if (tab === 'versions') {
            this.updateVersionsList();
        } else if (tab === 'storage') {
            this.updateStorageInfo();
        }
    }
    
    /**
     * Update entire display
     * @private
     */
    updateDisplay() {
        const stats = this.manager.getStorageStats();
        
        // Update stats
        this.panelElement.querySelector('#backup-count').textContent = stats.count;
        this.panelElement.querySelector('#backup-size').textContent = 
            this.formatSize(stats.total);
        
        this.updateVersionsList();
        this.updateStorageInfo();
    }
    
    /**
     * Update versions list
     * @private
     */
    updateVersionsList() {
        const listContainer = this.panelElement.querySelector('.backup-list');
        const backups = this.manager.getBackups();
        
        if (backups.length === 0) {
            listContainer.innerHTML = '<div class="backup-empty">No backups yet. Changes will auto-save.</div>';
            return;
        }
        
        listContainer.innerHTML = backups.map((backup, index) => `
            <div class="backup-item" data-id="${backup.id}">
                <div class="backup-item-info">
                    <div class="backup-item-type">${backup.type === 'auto' ? '⏱️ Auto' : '📌 Manual'}</div>
                    <div class="backup-item-time">${this.formatTime(backup.created)}</div>
                    <div class="backup-item-desc">${backup.description}</div>
                    <div class="backup-item-size">${this.formatSize(backup.size)}</div>
                </div>
                <div class="backup-item-actions">
                    <button class="backup-restore" title="Restore this version">Restore</button>
                    ${index > 0 ? `<button class="backup-compare" title="Compare with current">Compare</button>` : ''}
                    <button class="backup-delete" title="Delete this backup">Delete</button>
                </div>
            </div>
        `).join('');
        
        // Add event listeners
        listContainer.querySelectorAll('.backup-restore').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.closest('.backup-item').dataset.id;
                try {
                    this.manager.restoreVersion(id);
                    alert('Version restored successfully');
                    this.updateDisplay();
                } catch (err) {
                    alert(`Restore failed: ${err.message}`);
                }
            });
        });
        
        listContainer.querySelectorAll('.backup-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.closest('.backup-item').dataset.id;
                if (confirm('Delete this backup?')) {
                    this.manager.deleteBackup(id);
                    this.updateDisplay();
                }
            });
        });
        
        listContainer.querySelectorAll('.backup-compare').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.closest('.backup-item').dataset.id;
                const latest = this.manager.getBackups()[0];
                try {
                    const result = this.manager.compareVersions(id, latest.id);
                    this.showComparisonResult(result);
                } catch (err) {
                    alert(`Compare failed: ${err.message}`);
                }
            });
        });
    }
    
    /**
     * Update storage information
     * @private
     */
    updateStorageInfo() {
        const stats = this.manager.getStorageStats();
        
        this.panelElement.querySelector('#storage-count').textContent = stats.count;
        this.panelElement.querySelector('#storage-total').textContent = 
            this.formatSize(stats.total);
        this.panelElement.querySelector('#storage-oldest').textContent = 
            stats.oldest ? this.formatTime(stats.oldest) : 'None';
        this.panelElement.querySelector('#storage-newest').textContent = 
            stats.newest ? this.formatTime(stats.newest) : 'None';
        
        if (stats.percentUsed !== undefined) {
            this.panelElement.querySelector('#storage-used').textContent = 
                this.formatSize(stats.used);
            this.panelElement.querySelector('#storage-quota').textContent = 
                this.formatSize(stats.quota);
            
            const bar = this.panelElement.querySelector('#storage-bar-used');
            bar.style.width = `${Math.min(stats.percentUsed, 100)}%`;
            bar.classList.toggle('backup-storage-warning', stats.percentUsed > 80);
            bar.classList.toggle('backup-storage-critical', stats.percentUsed > 95);
        }
    }
    
    /**
     * Show comparison result
     * @private
     */
    showComparisonResult(result) {
        const message = `
Comparison Results:

HTML Changes:
  + Added: ${result.htmlDiff.added} lines
  - Removed: ${result.htmlDiff.removed} lines
  Similarity: ${result.htmlDiff.similarity}%

CSS Changes:
  + Added: ${result.cssDiff.added} lines
  - Removed: ${result.cssDiff.removed} lines
  Similarity: ${result.cssDiff.similarity}%
        `;
        alert(message);
    }
    
    /**
     * Format file size
     * @private
     */
    formatSize(bytes) {
        if (!bytes) return '0 KB';
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / 1048576).toFixed(2)} MB`;
    }
    
    /**
     * Format time
     * @private
     */
    formatTime(isoString) {
        const date = new Date(isoString);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
    
    /**
     * Show the panel
     */
    show() {
        if (this.panelElement) {
            this.panelElement.style.display = 'flex';
            this.isVisible = true;
            this.updateDisplay();
        }
    }
    
    /**
     * Hide the panel
     */
    hide() {
        if (this.panelElement) {
            this.panelElement.style.display = 'none';
            this.isVisible = false;
        }
    }
    
    /**
     * Toggle panel visibility
     */
    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }
}

/**
 * Initialize backup system
 * Creates and manages BackupManager and BackupUI instances
 */
window.initializeBackupManager = function(editor) {
    const manager = new BackupManager(editor, {
        maxSnapshots: 50,
        autoSaveInterval: 3000
    });
    
    const ui = new BackupUI(editor, manager);
    ui.initialize();
    
    // Expose public API
    window.backupManager = {
        manager,
        ui,
        createBackup: (desc) => manager.createManualBackup(desc),
        restoreVersion: (id) => manager.restoreVersion(id),
        compareVersions: (id1, id2) => manager.compareVersions(id1, id2),
        getBackups: () => manager.getBackups(),
        getStats: () => manager.getStorageStats(),
        show: () => ui.show(),
        hide: () => ui.hide(),
        toggle: () => ui.toggle()
    };
    
    console.log('[Backup] System initialized with', manager.getBackups().length, 'backups');
};
