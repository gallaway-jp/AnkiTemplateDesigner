/**
 * Workspace Customization Module
 * 
 * Provides client-side workspace customization including:
 * - Layout management and panel positioning
 * - Theme application and switching
 * - Keyboard shortcut binding and management
 * - Preset loading and saving
 * 
 * Classes:
 * - WorkspaceUI: Main UI management class
 * - LayoutController: Handles layout switching and panel resizing
 * - ThemeController: Applies themes and manages colors
 * - ShortcutRegistry: Manages keyboard bindings
 * - PresetLoader: Handles preset loading and application
 */

class LayoutController {
  constructor() {
    this.currentLayout = 'Horizontal';
    this.panels = {
      editor: { position: 'left', width: 40 },
      preview: { position: 'center', width: 30 },
      properties: { position: 'right', width: 30 }
    };
    this.layouts = {
      'Horizontal': {
        template: '1fr 1fr 1fr',
        direction: 'row',
        panels: { editor: { width: 40 }, preview: { width: 30 }, properties: { width: 30 } }
      },
      'Vertical': {
        template: '1fr 1fr',
        direction: 'column',
        panels: { editor: { height: 60 }, preview: { height: 40 }, properties: { height: 40 } }
      },
      'Minimalist': {
        template: '1fr 1fr',
        direction: 'row',
        panels: { editor: { width: 60 }, preview: { width: 40 }, properties: { visible: false } }
      },
      'Wide': {
        template: '1fr',
        direction: 'row',
        panels: { editor: { height: 80 }, preview: { height: 20 }, properties: { height: 20 } }
      }
    };
  }

  /**
   * Apply a layout by name
   * @param {string} layoutName - Name of layout to apply
   * @returns {boolean} Success status
   */
  applyLayout(layoutName) {
    if (!this.layouts[layoutName]) {
      console.error(`Layout '${layoutName}' not found`);
      return false;
    }

    this.currentLayout = layoutName;
    const layout = this.layouts[layoutName];
    const container = document.querySelector('.workspace-container');
    
    if (container) {
      container.style.gridTemplateColumns = layout.direction === 'row' ? layout.template : 'auto';
      container.style.gridTemplateRows = layout.direction === 'column' ? layout.template : 'auto';
      container.style.gridAutoFlow = layout.direction;
    }

    this._applyPanelSettings(layout.panels);
    return true;
  }

  /**
   * Apply panel visibility and sizing settings
   * @private
   */
  _applyPanelSettings(panelSettings) {
    for (const [panelName, settings] of Object.entries(panelSettings)) {
      const panelElement = document.querySelector(`.panel-${panelName}`);
      if (!panelElement) continue;

      if (settings.visible === false) {
        panelElement.style.display = 'none';
      } else {
        panelElement.style.display = '';
        if (settings.width) panelElement.style.width = `${settings.width}%`;
        if (settings.height) panelElement.style.height = `${settings.height}%`;
      }
    }
  }

  /**
   * Get current layout name
   * @returns {string} Current layout name
   */
  getCurrentLayout() {
    return this.currentLayout;
  }

  /**
   * Get all available layouts
   * @returns {string[]} Array of layout names
   */
  getAvailableLayouts() {
    return Object.keys(this.layouts);
  }

  /**
   * Create custom layout
   * @param {string} name - Layout name
   * @param {string} template - CSS grid template
   * @param {string} direction - Grid direction (row|column)
   * @returns {boolean} Success status
   */
  createCustomLayout(name, template, direction = 'row') {
    if (this.layouts[name]) {
      console.error(`Layout '${name}' already exists`);
      return false;
    }
    this.layouts[name] = { template, direction, panels: {} };
    return true;
  }

  /**
   * Resize a panel
   * @param {string} panelName - Panel to resize
   * @param {number} size - New size percentage
   * @param {string} dimension - 'width' or 'height'
   */
  resizePanel(panelName, size, dimension = 'width') {
    const panelElement = document.querySelector(`.panel-${panelName}`);
    if (panelElement) {
      panelElement.style[dimension] = `${size}%`;
      this.panels[panelName][dimension] = size;
    }
  }
}


class ThemeController {
  constructor() {
    this.currentTheme = 'Light';
    this.themes = {
      'Light': {
        backgroundColor: '#FFFFFF',
        textColor: '#1E1E1E',
        accentColor: '#0078D4',
        secondaryColor: '#50E6FF',
        borderColor: '#E0E0E0',
        panelBackground: '#F5F5F5',
        isDark: false
      },
      'Dark': {
        backgroundColor: '#1E1E1E',
        textColor: '#FFFFFF',
        accentColor: '#00D4FF',
        secondaryColor: '#646695',
        borderColor: '#3E3E3E',
        panelBackground: '#252526',
        isDark: true
      },
      'High Contrast': {
        backgroundColor: '#000000',
        textColor: '#FFFFFF',
        accentColor: '#FFFF00',
        secondaryColor: '#00FFFF',
        borderColor: '#FFFFFF',
        panelBackground: '#1A1A1A',
        isDark: true
      },
      'Sepia': {
        backgroundColor: '#F5E6D3',
        textColor: '#5C4033',
        accentColor: '#8B4513',
        secondaryColor: '#D2A679',
        borderColor: '#C5A880',
        panelBackground: '#FBF5ED',
        isDark: false
      }
    };
  }

  /**
   * Apply a theme by name
   * @param {string} themeName - Name of theme to apply
   * @returns {boolean} Success status
   */
  applyTheme(themeName) {
    if (!this.themes[themeName]) {
      console.error(`Theme '${themeName}' not found`);
      return false;
    }

    this.currentTheme = themeName;
    const theme = this.themes[themeName];
    const root = document.documentElement;

    root.style.setProperty('--bg-color', theme.backgroundColor);
    root.style.setProperty('--text-color', theme.textColor);
    root.style.setProperty('--accent-color', theme.accentColor);
    root.style.setProperty('--secondary-color', theme.secondaryColor);
    root.style.setProperty('--border-color', theme.borderColor);
    root.style.setProperty('--panel-bg', theme.panelBackground);

    document.body.setAttribute('data-theme', themeName);
    return true;
  }

  /**
   * Get current theme name
   * @returns {string} Current theme name
   */
  getCurrentTheme() {
    return this.currentTheme;
  }

  /**
   * Get all available themes
   * @returns {string[]} Array of theme names
   */
  getAvailableThemes() {
    return Object.keys(this.themes);
  }

  /**
   * Create custom theme
   * @param {string} name - Theme name
   * @param {object} colors - Color configuration
   * @returns {boolean} Success status
   */
  createCustomTheme(name, colors) {
    if (this.themes[name]) {
      console.error(`Theme '${name}' already exists`);
      return false;
    }
    this.themes[name] = colors;
    return true;
  }

  /**
   * Get theme colors
   * @param {string} themeName - Theme name
   * @returns {object} Theme colors object
   */
  getTheme(themeName) {
    return this.themes[themeName] || null;
  }
}


class ShortcutRegistry {
  constructor() {
    this.shortcuts = {};
    this.keyBindings = {};
    this._initializeDefaultShortcuts();
  }

  /**
   * Initialize default keyboard shortcuts
   * @private
   */
  _initializeDefaultShortcuts() {
    const defaults = [
      { action: 'save', key: 'ctrl+s', description: 'Save template' },
      { action: 'undo', key: 'ctrl+z', description: 'Undo last action' },
      { action: 'redo', key: 'ctrl+y', description: 'Redo last action' },
      { action: 'cut', key: 'ctrl+x', description: 'Cut selection' },
      { action: 'copy', key: 'ctrl+c', description: 'Copy selection' },
      { action: 'paste', key: 'ctrl+v', description: 'Paste from clipboard' },
      { action: 'selectall', key: 'ctrl+a', description: 'Select all' },
      { action: 'find', key: 'ctrl+f', description: 'Find in template' },
      { action: 'replace', key: 'ctrl+h', description: 'Find and replace' },
      { action: 'preview', key: 'ctrl+shift+p', description: 'Toggle preview' },
      { action: 'properties', key: 'ctrl+shift+i', description: 'Toggle properties' }
    ];

    for (const shortcut of defaults) {
      this.registerShortcut(shortcut.action, shortcut.key, shortcut.description);
    }
  }

  /**
   * Register a keyboard shortcut
   * @param {string} action - Action name
   * @param {string} keyCombo - Key combination (e.g., 'ctrl+s')
   * @param {string} description - Action description
   * @returns {boolean} Success status
   */
  registerShortcut(action, keyCombo, description = '') {
    const normalized = this._normalizeKeyCombo(keyCombo);
    this.shortcuts[action] = { key: normalized, description };
    this.keyBindings[normalized] = action;
    return true;
  }

  /**
   * Get shortcut for action
   * @param {string} action - Action name
   * @returns {object} Shortcut object or null
   */
  getShortcut(action) {
    return this.shortcuts[action] || null;
  }

  /**
   * Get action for key combination
   * @param {string} keyCombo - Key combination
   * @returns {string} Action name or null
   */
  getActionForKeys(keyCombo) {
    const normalized = this._normalizeKeyCombo(keyCombo);
    return this.keyBindings[normalized] || null;
  }

  /**
   * Normalize key combination to lowercase with sorted modifiers
   * @private
   * @param {string} keyCombo - Raw key combination
   * @returns {string} Normalized key combination
   */
  _normalizeKeyCombo(keyCombo) {
    const parts = keyCombo.split('+').map(p => p.toLowerCase().trim());
    const modifiers = parts.filter(p => ['ctrl', 'shift', 'alt', 'meta'].includes(p)).sort();
    const key = parts.find(p => !['ctrl', 'shift', 'alt', 'meta'].includes(p));
    return modifiers.length ? [...modifiers, key].join('+') : key;
  }

  /**
   * Bind keyboard listeners to document
   * @param {object} handlers - Object with action names as keys and callback functions as values
   */
  bindKeyListeners(handlers) {
    document.addEventListener('keydown', (event) => {
      const keys = [];
      if (event.ctrlKey || event.metaKey) keys.push('ctrl');
      if (event.shiftKey) keys.push('shift');
      if (event.altKey) keys.push('alt');
      keys.push(event.key.toLowerCase());

      const keyCombo = keys.join('+');
      const action = this.getActionForKeys(keyCobo);

      if (action && handlers[action]) {
        handlers[action](event);
      }
    });
  }

  /**
   * Get all shortcuts
   * @returns {object} All shortcuts map
   */
  getAllShortcuts() {
    return { ...this.shortcuts };
  }

  /**
   * Reset shortcuts to defaults
   */
  resetToDefaults() {
    this.shortcuts = {};
    this.keyBindings = {};
    this._initializeDefaultShortcuts();
  }
}


class PresetLoader {
  constructor(layoutController, themeController, shortcutRegistry) {
    this.layoutController = layoutController;
    this.themeController = themeController;
    this.shortcutRegistry = shortcutRegistry;
    this.presets = {};
    this._initializeBuiltinPresets();
  }

  /**
   * Initialize built-in presets
   * @private
   */
  _initializeBuiltinPresets() {
    this.presets = {
      'Minimal': {
        layout: 'Minimalist',
        theme: 'Light',
        description: 'Minimalist workspace with editor and preview'
      },
      'Developer': {
        layout: 'Horizontal',
        theme: 'Dark',
        description: 'Advanced workspace optimized for developers'
      },
      'Designer': {
        layout: 'Vertical',
        theme: 'Light',
        description: 'Workspace optimized for template design'
      },
      'Analyst': {
        layout: 'Wide',
        theme: 'High Contrast',
        description: 'Workspace optimized for analytics'
      }
    };
  }

  /**
   * Load a preset by name
   * @param {string} presetName - Name of preset to load
   * @returns {boolean} Success status
   */
  loadPreset(presetName) {
    if (!this.presets[presetName]) {
      console.error(`Preset '${presetName}' not found`);
      return false;
    }

    const preset = this.presets[presetName];
    this.layoutController.applyLayout(preset.layout);
    this.themeController.applyTheme(preset.theme);
    return true;
  }

  /**
   * Create a preset from current state
   * @param {string} name - Preset name
   * @param {string} description - Preset description
   * @returns {boolean} Success status
   */
  createPreset(name, description = '') {
    if (this.presets[name]) {
      console.error(`Preset '${name}' already exists`);
      return false;
    }

    this.presets[name] = {
      layout: this.layoutController.getCurrentLayout(),
      theme: this.themeController.getCurrentTheme(),
      description
    };
    return true;
  }

  /**
   * Delete a preset
   * @param {string} name - Preset name
   * @returns {boolean} Success status
   */
  deletePreset(name) {
    if (!this.presets[name]) {
      console.error(`Preset '${name}' not found`);
      return false;
    }
    delete this.presets[name];
    return true;
  }

  /**
   * Export preset as JSON string
   * @param {string} name - Preset name
   * @returns {string|null} JSON string or null if not found
   */
  exportPreset(name) {
    if (!this.presets[name]) return null;
    return JSON.stringify(this.presets[name], null, 2);
  }

  /**
   * Import preset from JSON string
   * @param {string} jsonStr - JSON preset data
   * @returns {boolean} Success status
   */
  importPreset(jsonStr) {
    try {
      const preset = JSON.parse(jsonStr);
      if (!preset.name) {
        console.error('Preset must have a name property');
        return false;
      }
      this.presets[preset.name] = preset;
      return true;
    } catch (error) {
      console.error('Error importing preset:', error);
      return false;
    }
  }

  /**
   * Get all preset names
   * @returns {string[]} Array of preset names
   */
  getPresetNames() {
    return Object.keys(this.presets);
  }

  /**
   * Get preset details
   * @param {string} name - Preset name
   * @returns {object} Preset object or null
   */
  getPreset(name) {
    return this.presets[name] || null;
  }
}


class WorkspaceUI {
  constructor() {
    this.layoutController = new LayoutController();
    this.themeController = new ThemeController();
    this.shortcutRegistry = new ShortcutRegistry();
    this.presetLoader = new PresetLoader(
      this.layoutController,
      this.themeController,
      this.shortcutRegistry
    );
    this._initialized = false;
  }

  /**
   * Initialize workspace UI
   */
  initialize() {
    if (this._initialized) return;

    this._createLayoutControls();
    this._createThemeControls();
    this._createPresetControls();
    this._applyDefaultState();
    this._setupListeners();

    this._initialized = true;
  }

  /**
   * Create layout control UI
   * @private
   */
  _createLayoutControls() {
    const container = document.querySelector('.workspace-controls');
    if (!container) return;

    const layoutDiv = document.createElement('div');
    layoutDiv.className = 'control-group layout-controls';
    layoutDiv.innerHTML = '<label>Layout:</label>';

    const select = document.createElement('select');
    select.id = 'layout-selector';
    for (const layout of this.layoutController.getAvailableLayouts()) {
      const option = document.createElement('option');
      option.value = layout;
      option.textContent = layout;
      select.appendChild(option);
    }

    select.addEventListener('change', (e) => {
      this.layoutController.applyLayout(e.target.value);
    });

    layoutDiv.appendChild(select);
    container.appendChild(layoutDiv);
  }

  /**
   * Create theme control UI
   * @private
   */
  _createThemeControls() {
    const container = document.querySelector('.workspace-controls');
    if (!container) return;

    const themeDiv = document.createElement('div');
    themeDiv.className = 'control-group theme-controls';
    themeDiv.innerHTML = '<label>Theme:</label>';

    const select = document.createElement('select');
    select.id = 'theme-selector';
    for (const theme of this.themeController.getAvailableThemes()) {
      const option = document.createElement('option');
      option.value = theme;
      option.textContent = theme;
      select.appendChild(option);
    }

    select.addEventListener('change', (e) => {
      this.themeController.applyTheme(e.target.value);
    });

    themeDiv.appendChild(select);
    container.appendChild(themeDiv);
  }

  /**
   * Create preset control UI
   * @private
   */
  _createPresetControls() {
    const container = document.querySelector('.workspace-controls');
    if (!container) return;

    const presetDiv = document.createElement('div');
    presetDiv.className = 'control-group preset-controls';
    presetDiv.innerHTML = '<label>Preset:</label>';

    const select = document.createElement('select');
    select.id = 'preset-selector';
    for (const preset of this.presetLoader.getPresetNames()) {
      const option = document.createElement('option');
      option.value = preset;
      option.textContent = preset;
      select.appendChild(option);
    }

    select.addEventListener('change', (e) => {
      this.presetLoader.loadPreset(e.target.value);
      this._updateControls();
    });

    const saveBtn = document.createElement('button');
    saveBtn.textContent = 'Save Preset';
    saveBtn.addEventListener('click', () => {
      const name = prompt('Preset name:');
      if (name) {
        this.presetLoader.createPreset(name);
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name;
        select.appendChild(option);
      }
    });

    presetDiv.appendChild(select);
    presetDiv.appendChild(saveBtn);
    container.appendChild(presetDiv);
  }

  /**
   * Apply default workspace state
   * @private
   */
  _applyDefaultState() {
    this.layoutController.applyLayout('Horizontal');
    this.themeController.applyTheme('Light');
  }

  /**
   * Setup event listeners
   * @private
   */
  _setupListeners() {
    // Keyboard shortcuts
    this.shortcutRegistry.bindKeyListeners({
      'preview': () => document.querySelector('.panel-preview')?.classList.toggle('hidden'),
      'properties': () => document.querySelector('.panel-properties')?.classList.toggle('hidden')
    });
  }

  /**
   * Update control values to match current state
   * @private
   */
  _updateControls() {
    const layoutSelect = document.querySelector('#layout-selector');
    if (layoutSelect) {
      layoutSelect.value = this.layoutController.getCurrentLayout();
    }

    const themeSelect = document.querySelector('#theme-selector');
    if (themeSelect) {
      themeSelect.value = this.themeController.getCurrentTheme();
    }
  }

  /**
   * Get current workspace state
   * @returns {object} Workspace state object
   */
  getWorkspaceState() {
    return {
      layout: this.layoutController.getCurrentLayout(),
      theme: this.themeController.getCurrentTheme(),
      shortcuts: this.shortcutRegistry.getAllShortcuts(),
      presets: this.presetLoader.getPresetNames()
    };
  }

  /**
   * Save workspace state to localStorage
   */
  saveToLocalStorage() {
    const state = this.getWorkspaceState();
    localStorage.setItem('workspaceState', JSON.stringify(state));
  }

  /**
   * Restore workspace state from localStorage
   */
  restoreFromLocalStorage() {
    const saved = localStorage.getItem('workspaceState');
    if (saved) {
      try {
        const state = JSON.parse(saved);
        this.layoutController.applyLayout(state.layout);
        this.themeController.applyTheme(state.theme);
        this._updateControls();
      } catch (error) {
        console.error('Error restoring workspace state:', error);
      }
    }
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    WorkspaceUI,
    LayoutController,
    ThemeController,
    ShortcutRegistry,
    PresetLoader
  };
}
