/**
 * UI Customization Manager
 * Allows users to customize interface layout, panel visibility, and toolbar configuration
 */

export class UICustomizationManager {
    constructor(editor) {
        this.editor = editor;
        this.config = this.loadConfig();
        this.settingsPanel = null;
        this.init();
    }

    /**
     * Initialize customization system
     */
    init() {
        this.setupSettingsPanel();
        this.applyConfiguration();
        console.log('[UICustomization] Manager initialized');
    }

    /**
     * Load configuration from localStorage
     */
    loadConfig() {
        try {
            const saved = localStorage.getItem('anki-designer-ui-config');
            if (saved) {
                const config = JSON.parse(saved);
                console.log('[UICustomization] Loaded configuration:', config);
                return config;
            }
        } catch (e) {
            console.error('[UICustomization] Error loading config:', e);
        }

        // Return default configuration
        return {
            panelsVisible: {
                blocks: true,
                layers: true,
                styles: true,
                traits: true,
                history: true
            },
            toolbarButtons: {
                save: true,
                export: true,
                preview: true,
                validate: true,
                undo: true,
                redo: true,
                devices: true
            },
            layout: {
                rightPanelWidth: 300,
                leftPanelWidth: 250,
                theme: 'light',
                compactMode: false
            }
        };
    }

    /**
     * Save configuration to localStorage
     */
    saveConfig() {
        try {
            localStorage.setItem('anki-designer-ui-config', JSON.stringify(this.config));
            console.log('[UICustomization] Configuration saved');
        } catch (e) {
            console.error('[UICustomization] Error saving config:', e);
        }
    }

    /**
     * Apply configuration to the UI
     */
    applyConfiguration() {
        // Apply panel visibility
        this.applyPanelVisibility();

        // Apply toolbar button visibility
        this.applyToolbarVisibility();

        // Apply layout preferences
        this.applyLayoutPreferences();

        console.log('[UICustomization] Configuration applied');
    }

    /**
     * Apply panel visibility settings
     */
    applyPanelVisibility() {
        const { panelsVisible } = this.config;

        Object.entries(panelsVisible).forEach(([panelName, isVisible]) => {
            const panelElement = document.querySelector(
                `.${panelName}-container, [data-panel="${panelName}"]`
            );

            if (panelElement) {
                panelElement.style.display = isVisible ? '' : 'none';
                panelElement.setAttribute('aria-hidden', !isVisible ? 'true' : 'false');
            }
        });
    }

    /**
     * Apply toolbar button visibility
     */
    applyToolbarVisibility() {
        const { toolbarButtons } = this.config;

        Object.entries(toolbarButtons).forEach(([buttonName, isVisible]) => {
            const buttonElement = document.querySelector(
                `[data-action="${buttonName}"], [data-button="${buttonName}"]`
            );

            if (buttonElement) {
                buttonElement.style.display = isVisible ? '' : 'none';
                buttonElement.setAttribute('aria-hidden', !isVisible ? 'true' : 'false');
            }
        });
    }

    /**
     * Apply layout preferences
     */
    applyLayoutPreferences() {
        const { layout } = this.config;

        // Apply theme
        document.body.setAttribute('data-theme', layout.theme);

        // Apply compact mode
        if (layout.compactMode) {
            document.body.classList.add('compact-mode');
        } else {
            document.body.classList.remove('compact-mode');
        }

        // Apply panel widths
        const rightPanel = document.querySelector('.panel__right');
        if (rightPanel) {
            rightPanel.style.width = layout.rightPanelWidth + 'px';
        }
    }

    /**
     * Setup settings panel in UI
     */
    setupSettingsPanel() {
        // Create settings panel if not exists
        if (document.getElementById('ui-customization-panel')) {
            this.settingsPanel = document.getElementById('ui-customization-panel');
            return;
        }

        const panel = document.createElement('div');
        panel.id = 'ui-customization-panel';
        panel.className = 'customization-panel hidden';
        panel.setAttribute('role', 'dialog');
        panel.setAttribute('aria-label', 'UI Customization Settings');
        panel.innerHTML = `
            <div class="customization-panel-header">
                <h3>Customize Interface</h3>
                <button class="customization-panel-close" aria-label="Close settings">&times;</button>
            </div>
            <div class="customization-panel-content">
                <!-- Panel Visibility Section -->
                <div class="customization-section">
                    <h4>Panel Visibility</h4>
                    <div class="customization-group">
                        <label class="customization-checkbox">
                            <input type="checkbox" data-panel-toggle="blocks" ${this.config.panelsVisible.blocks ? 'checked' : ''}>
                            <span>Show Blocks Panel</span>
                        </label>
                        <label class="customization-checkbox">
                            <input type="checkbox" data-panel-toggle="layers" ${this.config.panelsVisible.layers ? 'checked' : ''}>
                            <span>Show Layers Panel</span>
                        </label>
                        <label class="customization-checkbox">
                            <input type="checkbox" data-panel-toggle="styles" ${this.config.panelsVisible.styles ? 'checked' : ''}>
                            <span>Show Styles Panel</span>
                        </label>
                        <label class="customization-checkbox">
                            <input type="checkbox" data-panel-toggle="traits" ${this.config.panelsVisible.traits ? 'checked' : ''}>
                            <span>Show Settings Panel</span>
                        </label>
                        <label class="customization-checkbox">
                            <input type="checkbox" data-panel-toggle="history" ${this.config.panelsVisible.history ? 'checked' : ''}>
                            <span>Show History Panel</span>
                        </label>
                    </div>
                </div>

                <!-- Toolbar Buttons Section -->
                <div class="customization-section">
                    <h4>Toolbar Buttons</h4>
                    <div class="customization-group">
                        <label class="customization-checkbox">
                            <input type="checkbox" data-button-toggle="save" ${this.config.toolbarButtons.save ? 'checked' : ''}>
                            <span>Save Button</span>
                        </label>
                        <label class="customization-checkbox">
                            <input type="checkbox" data-button-toggle="export" ${this.config.toolbarButtons.export ? 'checked' : ''}>
                            <span>Export Button</span>
                        </label>
                        <label class="customization-checkbox">
                            <input type="checkbox" data-button-toggle="preview" ${this.config.toolbarButtons.preview ? 'checked' : ''}>
                            <span>Preview Button</span>
                        </label>
                        <label class="customization-checkbox">
                            <input type="checkbox" data-button-toggle="validate" ${this.config.toolbarButtons.validate ? 'checked' : ''}>
                            <span>Validate Button</span>
                        </label>
                        <label class="customization-checkbox">
                            <input type="checkbox" data-button-toggle="undo" ${this.config.toolbarButtons.undo ? 'checked' : ''}>
                            <span>Undo Button</span>
                        </label>
                        <label class="customization-checkbox">
                            <input type="checkbox" data-button-toggle="redo" ${this.config.toolbarButtons.redo ? 'checked' : ''}>
                            <span>Redo Button</span>
                        </label>
                    </div>
                </div>

                <!-- Layout Section -->
                <div class="customization-section">
                    <h4>Layout Options</h4>
                    <div class="customization-group">
                        <label class="customization-checkbox">
                            <input type="checkbox" data-layout-toggle="compactMode" ${this.config.layout.compactMode ? 'checked' : ''}>
                            <span>Compact Mode (smaller padding)</span>
                        </label>
                    </div>
                    
                    <label class="customization-label">
                        <span>Right Panel Width (px)</span>
                        <input type="number" id="right-panel-width" min="150" max="500" value="${this.config.layout.rightPanelWidth}">
                    </label>
                </div>

                <!-- Actions -->
                <div class="customization-actions">
                    <button id="reset-customization" class="button-secondary">Reset to Defaults</button>
                    <button id="save-customization" class="button-primary">Save Changes</button>
                </div>
            </div>
        `;

        document.body.appendChild(panel);

        // Setup event listeners
        this.setupEventListeners(panel);

        this.settingsPanel = panel;
    }

    /**
     * Setup event listeners for the customization panel
     */
    setupEventListeners(panel) {
        // Close button
        panel.querySelector('.customization-panel-close')?.addEventListener('click', () => {
            this.hideSettings();
        });

        // Panel toggles
        panel.querySelectorAll('[data-panel-toggle]').forEach((checkbox) => {
            checkbox.addEventListener('change', (e) => {
                const panelName = e.target.getAttribute('data-panel-toggle');
                this.config.panelsVisible[panelName] = e.target.checked;
            });
        });

        // Button toggles
        panel.querySelectorAll('[data-button-toggle]').forEach((checkbox) => {
            checkbox.addEventListener('change', (e) => {
                const buttonName = e.target.getAttribute('data-button-toggle');
                this.config.toolbarButtons[buttonName] = e.target.checked;
            });
        });

        // Layout toggles
        panel.querySelectorAll('[data-layout-toggle]').forEach((checkbox) => {
            checkbox.addEventListener('change', (e) => {
                const layoutOption = e.target.getAttribute('data-layout-toggle');
                this.config.layout[layoutOption] = e.target.checked;
            });
        });

        // Right panel width
        const widthInput = panel.querySelector('#right-panel-width');
        if (widthInput) {
            widthInput.addEventListener('change', (e) => {
                this.config.layout.rightPanelWidth = parseInt(e.target.value);
                this.applyLayoutPreferences();
            });
        }

        // Reset button
        panel.querySelector('#reset-customization')?.addEventListener('click', () => {
            this.resetToDefaults();
        });

        // Save button
        panel.querySelector('#save-customization')?.addEventListener('click', () => {
            this.applyConfiguration();
            this.saveConfig();
            this.hideSettings();
            showToast('UI customization saved!', 'success', 3000);
        });

        // Close on escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !panel.classList.contains('hidden')) {
                this.hideSettings();
            }
        });
    }

    /**
     * Show customization settings panel
     */
    showSettings() {
        if (this.settingsPanel) {
            this.settingsPanel.classList.remove('hidden');
        }
    }

    /**
     * Hide customization settings panel
     */
    hideSettings() {
        if (this.settingsPanel) {
            this.settingsPanel.classList.add('hidden');
        }
    }

    /**
     * Toggle customization panel visibility
     */
    toggleSettings() {
        if (this.settingsPanel?.classList.contains('hidden')) {
            this.showSettings();
        } else {
            this.hideSettings();
        }
    }

    /**
     * Reset to default configuration
     */
    resetToDefaults() {
        if (confirm('Are you sure you want to reset to default layout?')) {
            localStorage.removeItem('anki-designer-ui-config');
            this.config = this.loadConfig();
            this.applyConfiguration();
            this.setupSettingsPanel(); // Refresh the panel
            showToast('Reset to default layout', 'info', 3000);
            console.log('[UICustomization] Reset to defaults');
        }
    }

    /**
     * Set panel visibility
     */
    setPanelVisibility(panelName, isVisible) {
        this.config.panelsVisible[panelName] = isVisible;
        this.applyPanelVisibility();
        this.saveConfig();
    }

    /**
     * Set toolbar button visibility
     */
    setButtonVisibility(buttonName, isVisible) {
        this.config.toolbarButtons[buttonName] = isVisible;
        this.applyToolbarVisibility();
        this.saveConfig();
    }

    /**
     * Set right panel width
     */
    setRightPanelWidth(width) {
        this.config.layout.rightPanelWidth = width;
        this.applyLayoutPreferences();
        this.saveConfig();
    }

    /**
     * Get current configuration
     */
    getConfig() {
        return JSON.parse(JSON.stringify(this.config));
    }

    /**
     * Export configuration
     */
    exportConfig() {
        const dataStr = JSON.stringify(this.config, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `anki-designer-ui-config-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(url);
    }

    /**
     * Import configuration
     */
    importConfig(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const config = JSON.parse(e.target.result);
                this.config = config;
                this.saveConfig();
                this.applyConfiguration();
                showToast('Configuration imported successfully!', 'success', 3000);
                console.log('[UICustomization] Configuration imported');
            } catch (err) {
                showToast('Failed to import configuration', 'error', 3000);
                console.error('[UICustomization] Import error:', err);
            }
        };
        reader.readAsText(file);
    }
}

// Export singleton
let customizationManager = null;

export function initializeUICustomization(editor) {
    if (!customizationManager) {
        customizationManager = new UICustomizationManager(editor);
        window.customizationManager = customizationManager;
    }
    return customizationManager;
}

export function getUICustomizationManager() {
    return customizationManager;
}
