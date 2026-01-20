/**
 * Issue #50: Keyboard Shortcuts Manager - Frontend UI
 * 
 * Complete JavaScript controller for managing keyboard shortcuts,
 * conflict detection, and customization interface.
 */

class ShortcutsUI {
    /**
     * Initialize the shortcuts UI.
     * 
     * @param {HTMLElement} container - Container element
     * @param {Object} backendAPI - Backend API object
     */
    constructor(container, backendAPI = null) {
        this.container = container;
        this.backendAPI = backendAPI;
        
        this.currentProfile = null;
        this.shortcuts = [];
        this.allProfiles = [];
        this.conflicts = [];
        
        this.initialize();
    }

    /**
     * Initialize the shortcuts UI.
     */
    initialize() {
        this.createStructure();
        this.setupEventListeners();
    }

    /**
     * Create the UI structure.
     */
    createStructure() {
        this.container.innerHTML = `
            <div class="shortcuts-manager">
                <div class="shortcuts-header">
                    <h3>Keyboard Shortcuts</h3>
                    <div class="profile-selector">
                        <select class="profile-select"></select>
                        <button class="new-profile-btn" title="Create new shortcut profile">+ New Profile</button>
                    </div>
                </div>
                
                <div class="shortcuts-toolbar">
                    <input type="text" class="shortcuts-search" placeholder="Search shortcuts...">
                    <select class="category-filter">
                        <option value="">All Categories</option>
                        <option value="edit">Edit</option>
                        <option value="view">View</option>
                        <option value="navigation">Navigation</option>
                        <option value="file">File</option>
                        <option value="help">Help</option>
                    </select>
                    <button class="reset-btn">Reset to Defaults</button>
                </div>
                
                <div class="shortcuts-list"></div>
                
                <div class="conflicts-panel" style="display: none;">
                    <h4>Conflicts Detected</h4>
                    <div class="conflicts-list"></div>
                </div>
            </div>
        `;

        this.profileSelect = this.container.querySelector('.profile-select');
        this.newProfileBtn = this.container.querySelector('.new-profile-btn');
        this.searchInput = this.container.querySelector('.shortcuts-search');
        this.categoryFilter = this.container.querySelector('.category-filter');
        this.resetBtn = this.container.querySelector('.reset-btn');
        this.shortcutsList = this.container.querySelector('.shortcuts-list');
        this.conflictsPanel = this.container.querySelector('.conflicts-panel');
    }

    /**
     * Set up event listeners.
     */
    setupEventListeners() {
        this.newProfileBtn.addEventListener('click', () => this.createNewProfile());
        this.profileSelect.addEventListener('change', () => this.switchProfile());
        this.searchInput.addEventListener('input', () => this.filterShortcuts());
        this.categoryFilter.addEventListener('change', () => this.filterShortcuts());
        this.resetBtn.addEventListener('click', () => this.resetToDefaults());
    }

    /**
     * Update the shortcuts list display.
     * 
     * @param {Array} shortcuts - Array of shortcut objects
     * @param {Array} profiles - Array of profile objects
     */
    updateShortcuts(shortcuts, profiles) {
        this.shortcuts = shortcuts;
        this.allProfiles = profiles;
        
        this.updateProfileSelector();
        this.renderShortcuts();
    }

    /**
     * Update the profile selector dropdown.
     */
    updateProfileSelector() {
        this.profileSelect.innerHTML = '';
        this.allProfiles.forEach(profile => {
            const option = document.createElement('option');
            option.value = profile.id;
            option.textContent = profile.name;
            this.profileSelect.appendChild(option);
        });
    }

    /**
     * Render the shortcuts list.
     */
    renderShortcuts() {
        this.shortcutsList.innerHTML = '';

        if (this.shortcuts.length === 0) {
            this.shortcutsList.innerHTML = '<div class="empty-shortcuts">No shortcuts found</div>';
            return;
        }

        this.shortcuts.forEach(shortcut => {
            const item = document.createElement('div');
            item.className = 'shortcut-item';
            
            item.innerHTML = `
                <div class="shortcut-info">
                    <div class="shortcut-name">${shortcut.name}</div>
                    <div class="shortcut-description">${shortcut.description}</div>
                    <div class="shortcut-category">${shortcut.category}</div>
                </div>
                <div class="shortcut-input">
                    <input type="text" 
                           class="shortcut-keys" 
                           value="${shortcut.keys}"
                           data-shortcut-id="${shortcut.id}"
                           ${shortcut.is_customizable ? '' : 'disabled'}>
                    <button class="shortcut-reset" data-shortcut-id="${shortcut.id}" 
                            title="Reset to default"
                            ${shortcut.is_customizable ? '' : 'disabled'}>↻ Reset</button>
                </div>
                <div class="shortcut-actions">
                    <label class="toggle-switch">
                        <input type="checkbox" ${shortcut.is_enabled ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                </div>
            `;

            // Add event listeners
            const input = item.querySelector('.shortcut-keys');
            const toggle = item.querySelector('input[type="checkbox"]');
            const resetBtn = item.querySelector('.shortcut-reset');

            input.addEventListener('change', (e) => this.updateShortcut(shortcut.id, e.target.value));
            toggle.addEventListener('change', (e) => this.toggleShortcut(shortcut.id, e.target.checked));
            resetBtn.addEventListener('click', () => this.resetShortcut(shortcut.id));

            this.shortcutsList.appendChild(item);
        });
    }

    /**
     * Update a shortcut's key binding.
     * 
     * @param {string} shortcutId - Shortcut ID
     * @param {string} keys - New key binding
     */
    updateShortcut(shortcutId, keys) {
        if (this.backendAPI && typeof this.backendAPI.updateShortcut === 'function') {
            const success = this.backendAPI.updateShortcut(shortcutId, keys);
            if (!success) {
                this.showConflictError();
                // Revert to original
                const shortcut = this.shortcuts.find(s => s.id === shortcutId);
                if (shortcut) {
                    document.querySelector(`[data-shortcut-id="${shortcutId}"]`).value = shortcut.keys;
                }
            }
        }
    }

    /**
     * Toggle shortcut enabled/disabled.
     * 
     * @param {string} shortcutId - Shortcut ID
     * @param {boolean} enabled - Is enabled
     */
    toggleShortcut(shortcutId, enabled) {
        if (this.backendAPI) {
            if (enabled) {
                this.backendAPI.enableShortcut?.(shortcutId);
            } else {
                this.backendAPI.disableShortcut?.(shortcutId);
            }
        }
    }

    /**
     * Reset a shortcut to default.
     * 
     * @param {string} shortcutId - Shortcut ID
     */
    resetShortcut(shortcutId) {
        if (this.backendAPI && typeof this.backendAPI.resetShortcut === 'function') {
            this.backendAPI.resetShortcut(shortcutId);
            const shortcut = this.shortcuts.find(s => s.id === shortcutId);
            if (shortcut) {
                document.querySelector(`[data-shortcut-id="${shortcutId}"]`).value = shortcut.keys;
            }
        }
    }

    /**
     * Filter shortcuts by search and category.
     */
    filterShortcuts() {
        const query = this.searchInput.value.toLowerCase();
        const category = this.categoryFilter.value;

        this.shortcutsList.querySelectorAll('.shortcut-item').forEach(item => {
            const name = item.querySelector('.shortcut-name').textContent.toLowerCase();
            const desc = item.querySelector('.shortcut-description').textContent.toLowerCase();
            const cat = item.querySelector('.shortcut-category').textContent.toLowerCase();
            const keys = item.querySelector('.shortcut-keys').value.toLowerCase();

            const matchesQuery = !query || name.includes(query) || desc.includes(query) || keys.includes(query);
            const matchesCategory = !category || cat === category;

            item.style.display = (matchesQuery && matchesCategory) ? '' : 'none';
        });
    }

    /**
     * Create a new profile.
     */
    createNewProfile() {
        const name = prompt('Enter profile name:');
        if (name && this.backendAPI) {
            this.backendAPI.createProfile?.(name);
        }
    }

    /**
     * Switch to a different profile.
     */
    switchProfile() {
        const profileId = this.profileSelect.value;
        if (this.backendAPI) {
            this.backendAPI.switchProfile?.(profileId);
        }
    }

    /**
     * Reset all shortcuts to defaults.
     */
    resetToDefaults() {
        if (confirm('Reset all shortcuts to defaults?')) {
            if (this.backendAPI) {
                this.backendAPI.resetToDefaults?.();
                this.renderShortcuts();
            }
        }
    }

    /**
     * Show conflict error message.
     */
    showConflictError() {
        const conflictsList = this.container.querySelector('.conflicts-list');
        conflictsList.innerHTML = '<div class="conflict-message">This key combination is already in use</div>';
        this.conflictsPanel.style.display = 'block';
        
        setTimeout(() => {
            this.conflictsPanel.style.display = 'none';
        }, 4000);
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ShortcutsUI;
}
