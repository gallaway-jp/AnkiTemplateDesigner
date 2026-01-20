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
        this.restoreLayoutState();
        this.setupLayoutListeners();
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

                <!-- Theme Section -->
                <div class="customization-section">
                    <h4>Theme Settings</h4>
                    <div class="customization-group">
                        <label class="customization-label">
                            <span>Select Theme:</span>
                            <select id="theme-selector" class="customization-select">
                                <option value="Light">☀️ Light</option>
                                <option value="Dark">🌙 Dark</option>
                                <option value="High Contrast">🔆 High Contrast</option>
                                <option value="Sepia">📖 Sepia</option>
                            </select>
                        </label>
                    </div>
                    <div class="customization-preview">
                        <h5>Live Preview:</h5>
                        <div id="theme-preview" class="theme-preview">
                            <div class="preview-sample">
                                <span class="preview-text">Sample Text</span>
                                <button class="preview-button">Sample Button</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Field Defaults Section -->
                <div class="customization-section">
                    <h4>Field Defaults</h4>
                    <div class="customization-group">
                        <button id="configure-field-defaults" class="button-secondary" style="width: 100%; margin-bottom: 10px;">
                            ⚙ Configure Field Defaults
                        </button>
                        <p class="section-help">Set default field type, validation rules, and attributes for new fields</p>
                    </div>
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

        // Theme selector with live preview
        const themeSelector = panel.querySelector('#theme-selector');
        if (themeSelector) {
            themeSelector.addEventListener('change', (e) => {
                const themeName = e.target.value;
                this.applyTheme(themeName);
                this.updateThemePreview(themeName);
                this.config.theme = themeName;
                
                // Persist to window.bridge if available
                if (window.bridge && window.bridge.saveThemePreference) {
                    window.bridge.saveThemePreference(themeName);
                }
                
                showToast(`Theme changed to "${themeName}"`, 'success', 2000);
            });
        }

        // Field defaults button
        const configFieldDefaultsBtn = panel.querySelector('#configure-field-defaults');
        if (configFieldDefaultsBtn) {
            configFieldDefaultsBtn.addEventListener('click', () => {
                this.configureFieldDefaults();
            });
        }

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
     * Apply a theme by name
     */
    applyTheme(themeName) {
        const themes = {
            'Light': {
                backgroundColor: '#FFFFFF',
                textColor: '#1E1E1E',
                accentColor: '#0078D4',
                panelBackground: '#F5F5F5',
                borderColor: '#E0E0E0'
            },
            'Dark': {
                backgroundColor: '#1E1E1E',
                textColor: '#FFFFFF',
                accentColor: '#00D4FF',
                panelBackground: '#252526',
                borderColor: '#3E3E3E'
            },
            'High Contrast': {
                backgroundColor: '#000000',
                textColor: '#FFFFFF',
                accentColor: '#FFFF00',
                panelBackground: '#1A1A1A',
                borderColor: '#FFFFFF'
            },
            'Sepia': {
                backgroundColor: '#F5E6D3',
                textColor: '#5C4033',
                accentColor: '#8B4513',
                panelBackground: '#FBF5ED',
                borderColor: '#C5A880'
            }
        };

        const theme = themes[themeName];
        if (!theme) return;

        const root = document.documentElement;
        root.style.setProperty('--bg-color', theme.backgroundColor);
        root.style.setProperty('--text-color', theme.textColor);
        root.style.setProperty('--accent-color', theme.accentColor);
        root.style.setProperty('--panel-bg', theme.panelBackground);
        root.style.setProperty('--border-color', theme.borderColor);
        
        document.body.setAttribute('data-theme', themeName);
    }

    /**
     * Update theme preview display
     */
    updateThemePreview(themeName) {
        const preview = document.querySelector('#theme-preview');
        if (!preview) return;

        const themes = {
            'Light': { bg: '#FFFFFF', text: '#1E1E1E', accent: '#0078D4' },
            'Dark': { bg: '#1E1E1E', text: '#FFFFFF', accent: '#00D4FF' },
            'High Contrast': { bg: '#000000', text: '#FFFFFF', accent: '#FFFF00' },
            'Sepia': { bg: '#F5E6D3', text: '#5C4033', accent: '#8B4513' }
        };

        const theme = themes[themeName];
        if (!theme) return;

        preview.style.backgroundColor = theme.bg;
        preview.style.color = theme.text;

        const button = preview.querySelector('.preview-button');
        if (button) {
            button.style.backgroundColor = theme.accent;
            button.style.color = theme.bg;
        }
    }

    /**
     * Configure field defaults with detailed settings
     */
    configureFieldDefaults() {
        const modal = document.createElement('div');
        modal.className = 'field-defaults-modal';
        modal.innerHTML = `
            <div class="modal-overlay">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Field Defaults Configuration</h3>
                        <button class="modal-close" aria-label="Close">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="field-defaults-section">
                            <h4>Default Field Type</h4>
                            <div class="field-defaults-group">
                                <label class="field-default-option">
                                    <input type="radio" name="default-type" value="text" checked>
                                    <span>Text (default)</span>
                                </label>
                                <label class="field-default-option">
                                    <input type="radio" name="default-type" value="number">
                                    <span>Number</span>
                                </label>
                                <label class="field-default-option">
                                    <input type="radio" name="default-type" value="date">
                                    <span>Date</span>
                                </label>
                                <label class="field-default-option">
                                    <input type="radio" name="default-type" value="checkbox">
                                    <span>Checkbox</span>
                                </label>
                                <label class="field-default-option">
                                    <input type="radio" name="default-type" value="dropdown">
                                    <span>Dropdown</span>
                                </label>
                            </div>
                        </div>

                        <div class="field-defaults-section">
                            <h4>Field Attributes</h4>
                            <div class="field-defaults-group">
                                <label class="field-default-checkbox">
                                    <input type="checkbox" id="field-required">
                                    <span>Required by default</span>
                                </label>
                                <label class="field-default-checkbox">
                                    <input type="checkbox" id="field-unique">
                                    <span>Enforce unique values</span>
                                </label>
                                <label class="field-default-checkbox">
                                    <input type="checkbox" id="field-searchable">
                                    <span>Searchable by default</span>
                                </label>
                            </div>
                        </div>

                        <div class="field-defaults-section">
                            <h4>Validation Rules</h4>
                            <div class="field-defaults-group">
                                <label class="field-default-label">
                                    <span>Min Length (0 = no limit):</span>
                                    <input type="number" id="field-min-length" value="0" min="0">
                                </label>
                                <label class="field-default-label">
                                    <span>Max Length (0 = no limit):</span>
                                    <input type="number" id="field-max-length" value="0" min="0">
                                </label>
                                <label class="field-default-label">
                                    <span>Default Value:</span>
                                    <input type="text" id="field-default-value" placeholder="Leave empty for no default">
                                </label>
                            </div>
                        </div>

                        <div class="field-defaults-preview">
                            <h4>Preview</h4>
                            <p id="preview-text" class="preview-description">Text field, optional, no length restrictions</p>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="button-secondary modal-cancel">Cancel</button>
                        <button class="button-primary modal-save">Save Defaults</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Event handlers
        const typeRadios = modal.querySelectorAll('input[name="default-type"]');
        const preview = modal.querySelector('#preview-text');

        const updatePreview = () => {
            const type = modal.querySelector('input[name="default-type"]:checked')?.value || 'text';
            const required = modal.querySelector('#field-required').checked;
            const unique = modal.querySelector('#field-unique').checked;
            const searchable = modal.querySelector('#field-searchable').checked;
            const minLen = modal.querySelector('#field-min-length').value;
            const maxLen = modal.querySelector('#field-max-length').value;
            const defaultVal = modal.querySelector('#field-default-value').value;

            let previewText = `${type} field, ${required ? 'required' : 'optional'}`;
            if (unique) previewText += ', unique values enforced';
            if (searchable) previewText += ', searchable';
            if (minLen > 0 || maxLen > 0) previewText += `, length: ${minLen || 'any'}-${maxLen || 'any'}`;
            if (defaultVal) previewText += `, default: "${defaultVal}"`;

            preview.textContent = previewText;
        };

        typeRadios.forEach(radio => {
            radio.addEventListener('change', updatePreview);
        });

        modal.querySelectorAll('input, select').forEach(el => {
            if (el.type !== 'radio') {
                el.addEventListener('change', updatePreview);
                el.addEventListener('input', updatePreview);
            }
        });

        // Save handler
        modal.querySelector('.modal-save').addEventListener('click', () => {
            const defaults = {
                type: modal.querySelector('input[name="default-type"]:checked').value,
                required: modal.querySelector('#field-required').checked,
                unique: modal.querySelector('#field-unique').checked,
                searchable: modal.querySelector('#field-searchable').checked,
                minLength: parseInt(modal.querySelector('#field-min-length').value) || 0,
                maxLength: parseInt(modal.querySelector('#field-max-length').value) || 0,
                defaultValue: modal.querySelector('#field-default-value').value
            };

            this.config.fieldDefaults = defaults;

            // Persist to bridge if available
            if (window.bridge && window.bridge.saveFieldDefaults) {
                window.bridge.saveFieldDefaults(JSON.stringify(defaults));
            }

            localStorage.setItem('field-defaults', JSON.stringify(defaults));
            showToast('Field defaults saved successfully', 'success', 3000);
            modal.remove();
        });

        // Cancel handler
        modal.querySelector('.modal-cancel').addEventListener('click', () => {
            modal.remove();
        });

        modal.querySelector('.modal-close').addEventListener('click', () => {
            modal.remove();
        });

        // Update preview on load
        updatePreview();
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
     * Setup layout change listeners to persist state
     */
    setupLayoutListeners() {
        // Listen for panel resize events
        window.addEventListener('resize', () => {
            this.saveLayoutState();
        }, { passive: true });

        // Listen for GrapeJS panel resize via MutationObserver
        const panels = document.querySelectorAll('[class*="panel"]');
        panels.forEach(panel => {
            new ResizeObserver(() => {
                this.saveLayoutState();
            }).observe(panel);
        });

        // Listen for panel toggle/collapse events
        document.addEventListener('panel:toggle', (e) => {
            const panelName = e.detail?.panelName;
            if (panelName) {
                this.savePanelState(panelName, e.detail?.isVisible);
            }
        });

        console.log('[UICustomization] Layout listeners configured');
    }

    /**
     * Save current layout state (panel dimensions, visibility)
     */
    saveLayoutState() {
        try {
            const layoutState = {
                panels: {},
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                },
                timestamp: Date.now()
            };

            // Capture panel states
            document.querySelectorAll('[class*="panel"]').forEach(panel => {
                const rect = panel.getBoundingClientRect();
                const panelId = panel.id || panel.className;
                
                layoutState.panels[panelId] = {
                    width: rect.width,
                    height: rect.height,
                    hidden: panel.offsetParent === null,
                    style: {
                        display: window.getComputedStyle(panel).display
                    }
                };
            });

            localStorage.setItem('designer-layout-state', JSON.stringify(layoutState));
            console.log('[UICustomization] Layout state saved');
        } catch (e) {
            console.error('[UICustomization] Error saving layout state:', e);
        }
    }

    /**
     * Restore layout state from saved state
     */
    restoreLayoutState() {
        try {
            const saved = localStorage.getItem('designer-layout-state');
            if (!saved) return;

            const layoutState = JSON.parse(saved);
            
            // Only restore if viewport is similar
            const viewportMatch = Math.abs(
                layoutState.viewport.width - window.innerWidth
            ) < 50; // Allow 50px difference

            if (viewportMatch) {
                Object.entries(layoutState.panels).forEach(([panelId, state]) => {
                    const panel = document.getElementById(panelId) || 
                                 document.querySelector(`.${panelId}`);
                    
                    if (panel) {
                        // Restore hidden state
                        if (state.hidden) {
                            panel.style.display = 'none';
                        } else if (state.style.display) {
                            panel.style.display = state.style.display;
                        }

                        // Restore dimensions
                        if (state.width) panel.style.width = state.width + 'px';
                        if (state.height) panel.style.height = state.height + 'px';
                    }
                });

                console.log('[UICustomization] Layout state restored');
            }
        } catch (e) {
            console.error('[UICustomization] Error restoring layout state:', e);
        }
    }

    /**
     * Save individual panel visibility state
     */
    savePanelState(panelName, isVisible) {
        try {
            const panelStates = JSON.parse(localStorage.getItem('designer-panel-states') || '{}');
            panelStates[panelName] = {
                visible: isVisible,
                timestamp: Date.now()
            };
            localStorage.setItem('designer-panel-states', JSON.stringify(panelStates));
        } catch (e) {
            console.error('[UICustomization] Error saving panel state:', e);
        }
    }

    /**
     * Show save feedback with spinner and confirmation
     */
    showSaveIndicator() {
        // Create save indicator element
        let saveIndicator = document.getElementById('save-indicator');
        if (!saveIndicator) {
            saveIndicator = document.createElement('div');
            saveIndicator.id = 'save-indicator';
            saveIndicator.className = 'save-indicator';
            document.body.appendChild(saveIndicator);
        }

        // Show spinner phase
        saveIndicator.innerHTML = `
            <div class="save-indicator-spinner"></div>
            <span>Saving...</span>
        `;
        saveIndicator.classList.add('visible');

        // After 300ms, show checkmark
        setTimeout(() => {
            saveIndicator.innerHTML = `
                <div class="save-indicator-checkmark">✓</div>
                <span>Saved</span>
            `;
            saveIndicator.classList.add('success');

            // After 1s, hide
            setTimeout(() => {
                saveIndicator.classList.remove('visible', 'success');
            }, 1000);
        }, 300);
    }

    /**
     * Persist settings change with feedback
     */
    persistSettingChange(settingName, settingValue) {
        try {
            // Update config
            const keys = settingName.split('.');
            let obj = this.config;
            for (let i = 0; i < keys.length - 1; i++) {
                obj = obj[keys[i]];
            }
            obj[keys[keys.length - 1]] = settingValue;

            // Save to localStorage
            this.saveConfig();

            // Show feedback
            this.showSaveIndicator();

            console.log(`[UICustomization] Setting saved: ${settingName} = ${settingValue}`);
        } catch (e) {
            console.error('[UICustomization] Error persisting setting:', e);
        }
    }


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

    /**
     * Save current configuration as a named preset
     * @param {string} presetName - Name for the preset
     * @param {string} description - Optional description
     */
    savePreset(presetName, description = '') {
        try {
            const presets = this.loadPresets();
            const preset = {
                name: presetName,
                description,
                config: JSON.parse(JSON.stringify(this.config)),
                createdAt: new Date().toISOString(),
                version: '1.0'
            };

            presets[presetName] = preset;
            localStorage.setItem('anki-designer-presets', JSON.stringify(presets));
            showToast(`Preset "${presetName}" saved successfully!`, 'success', 3000);
            console.log('[UICustomization] Preset saved:', presetName);
        } catch (err) {
            showToast('Failed to save preset', 'error', 3000);
            console.error('[UICustomization] Save preset error:', err);
        }
    }

    /**
     * Load a saved preset by name
     * @param {string} presetName - Name of the preset
     */
    loadPreset(presetName) {
        try {
            const presets = this.loadPresets();
            const preset = presets[presetName];

            if (!preset) {
                showToast(`Preset "${presetName}" not found`, 'warning', 3000);
                return false;
            }

            this.config = JSON.parse(JSON.stringify(preset.config));
            this.saveConfig();
            this.applyConfiguration();
            showToast(`Preset "${presetName}" loaded successfully!`, 'success', 3000);
            console.log('[UICustomization] Preset loaded:', presetName);
            return true;
        } catch (err) {
            showToast('Failed to load preset', 'error', 3000);
            console.error('[UICustomization] Load preset error:', err);
            return false;
        }
    }

    /**
     * Delete a saved preset
     * @param {string} presetName - Name of the preset to delete
     */
    deletePreset(presetName) {
        try {
            const presets = this.loadPresets();
            delete presets[presetName];
            localStorage.setItem('anki-designer-presets', JSON.stringify(presets));
            showToast(`Preset "${presetName}" deleted`, 'success', 3000);
            console.log('[UICustomization] Preset deleted:', presetName);
        } catch (err) {
            showToast('Failed to delete preset', 'error', 3000);
            console.error('[UICustomization] Delete preset error:', err);
        }
    }

    /**
     * Load all presets from localStorage
     * @returns {object} Object with preset names as keys
     */
    loadPresets() {
        try {
            const saved = localStorage.getItem('anki-designer-presets');
            return saved ? JSON.parse(saved) : {};
        } catch (e) {
            console.error('[UICustomization] Error loading presets:', e);
            return {};
        }
    }

    /**
     * Get list of all available presets
     * @returns {array} Array of preset names with metadata
     */
    getPresetsList() {
        const presets = this.loadPresets();
        return Object.values(presets).sort((a, b) => 
            new Date(b.createdAt) - new Date(a.createdAt)
        );
    }

    /**
     * Export a specific preset as JSON file
     * @param {string} presetName - Name of the preset
     */
    exportPreset(presetName) {
        try {
            const presets = this.loadPresets();
            const preset = presets[presetName];

            if (!preset) {
                showToast(`Preset "${presetName}" not found`, 'warning', 3000);
                return;
            }

            const json = JSON.stringify(preset, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `preset-${presetName}-${preset.version}.json`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);

            showToast(`Preset "${presetName}" exported!`, 'success', 3000);
            console.log('[UICustomization] Preset exported:', presetName);
        } catch (err) {
            showToast('Failed to export preset', 'error', 3000);
            console.error('[UICustomization] Export preset error:', err);
        }
    }

    /**
     * Import a preset from JSON file
     * @param {File} file - JSON preset file
     */
    importPreset(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const preset = JSON.parse(e.target.result);

                // Validate preset structure
                if (!preset.name || !preset.config || !preset.version) {
                    showToast('Invalid preset file format', 'error', 3000);
                    return;
                }

                const presets = this.loadPresets();
                presets[preset.name] = preset;
                localStorage.setItem('anki-designer-presets', JSON.stringify(presets));

                showToast(`Preset "${preset.name}" imported successfully!`, 'success', 3000);
                console.log('[UICustomization] Preset imported:', preset.name);
            } catch (err) {
                showToast('Failed to import preset', 'error', 3000);
                console.error('[UICustomization] Import preset error:', err);
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
