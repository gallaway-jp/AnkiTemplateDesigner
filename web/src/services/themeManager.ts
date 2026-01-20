/**
 * Theme System - Phase 5 Task 6
 * Dark/light theme toggle, customizable color schemes, CSS editing
 */

import { logger } from '@/utils/logger';

// ============================================================================
// Types & Interfaces
// ============================================================================

/**
 * Theme mode
 */
export type ThemeMode = 'light' | 'dark' | 'auto';

/**
 * Color palette
 */
export interface ColorPalette {
  primary: string;
  primaryLight: string;
  primaryDark: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  surfaceAlt: string;
  border: string;
  text: string;
  textSecondary: string;
  textTertiary: string;
  success: string;
  warning: string;
  error: string;
  info: string;
}

/**
 * Theme configuration
 */
export interface ThemeConfig {
  mode: ThemeMode;
  light: ColorPalette;
  dark: ColorPalette;
  customCSS: string;
  fontFamily: string;
  fontSize: number; // base font size in px
  borderRadius: number; // border radius in px
}

/**
 * Theme preset
 */
export interface ThemePreset {
  id: string;
  name: string;
  description: string;
  config: ThemeConfig;
  isDefault: boolean;
  author?: string;
}

/**
 * CSS variable mapping
 */
export interface CSSVariableMap {
  [key: string]: string;
}

// ============================================================================
// Default Themes
// ============================================================================

const DEFAULT_LIGHT_PALETTE: ColorPalette = {
  primary: '#007AFF',
  primaryLight: '#5AC8FF',
  primaryDark: '#0051D5',
  secondary: '#5856D6',
  accent: '#FF9500',
  background: '#FFFFFF',
  surface: '#F5F5F5',
  surfaceAlt: '#EEEEEE',
  border: '#E0E0E0',
  text: '#212121',
  textSecondary: '#757575',
  textTertiary: '#BDBDBD',
  success: '#4CAF50',
  warning: '#FFC107',
  error: '#F44336',
  info: '#2196F3',
};

const DEFAULT_DARK_PALETTE: ColorPalette = {
  primary: '#64B5F6',
  primaryLight: '#90CAF9',
  primaryDark: '#1976D2',
  secondary: '#BA68C8',
  accent: '#FFB74D',
  background: '#121212',
  surface: '#1E1E1E',
  surfaceAlt: '#2A2A2A',
  border: '#404040',
  text: '#FFFFFF',
  textSecondary: '#B0B0B0',
  textTertiary: '#808080',
  success: '#81C784',
  warning: '#FFD54F',
  error: '#EF5350',
  info: '#64B5F6',
};

const DEFAULT_CONFIG: ThemeConfig = {
  mode: 'auto',
  light: DEFAULT_LIGHT_PALETTE,
  dark: DEFAULT_DARK_PALETTE,
  customCSS: '',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif',
  fontSize: 14,
  borderRadius: 4,
};

// ============================================================================
// Theme Manager
// ============================================================================

export class ThemeManager {
  private currentMode: ThemeMode = 'auto';
  private themes: Map<string, ThemePreset> = new Map();
  private currentThemeId: string = 'default-light';
  private config: ThemeConfig = { ...DEFAULT_CONFIG };
  private cssElement: HTMLStyleElement | null = null;
  private storageKey = 'anki-template-theme';
  private mediaQueryList: MediaQueryList | null = null;

  /**
   * Initialize theme system
   */
  initialize(): void {
    try {
      // Load from storage
      this.loadFromStorage();

      // Setup CSS element
      this.setupCSSElement();

      // Setup auto mode listener
      if (typeof window !== 'undefined') {
        this.mediaQueryList = window.matchMedia('(prefers-color-scheme: dark)');
        if (this.mediaQueryList.addEventListener) {
          this.mediaQueryList.addEventListener('change', () => this.applyTheme());
        } else if (this.mediaQueryList.addListener) {
          this.mediaQueryList.addListener(() => this.applyTheme());
        }
      }

      // Initialize default themes
      this.initializeDefaultThemes();

      // Apply theme
      this.applyTheme();

      logger.info('[Theme] System initialized');
    } catch (error) {
      logger.error('[Theme] Initialization failed', error);
    }
  }

  /**
   * Initialize default themes
   */
  private initializeDefaultThemes(): void {
    this.registerTheme({
      id: 'default-light',
      name: 'Default Light',
      description: 'Clean light theme',
      config: {
        ...DEFAULT_CONFIG,
        mode: 'light',
        light: DEFAULT_LIGHT_PALETTE,
      },
      isDefault: true,
    });

    this.registerTheme({
      id: 'default-dark',
      name: 'Default Dark',
      description: 'Clean dark theme',
      config: {
        ...DEFAULT_CONFIG,
        mode: 'dark',
        dark: DEFAULT_DARK_PALETTE,
      },
      isDefault: true,
    });

    // High contrast light
    this.registerTheme({
      id: 'high-contrast-light',
      name: 'High Contrast Light',
      description: 'High contrast light theme for accessibility',
      config: {
        ...DEFAULT_CONFIG,
        mode: 'light',
        light: {
          ...DEFAULT_LIGHT_PALETTE,
          primary: '#0000EE',
          text: '#000000',
          background: '#FFFFFF',
        },
      },
      isDefault: true,
    });

    // High contrast dark
    this.registerTheme({
      id: 'high-contrast-dark',
      name: 'High Contrast Dark',
      description: 'High contrast dark theme for accessibility',
      config: {
        ...DEFAULT_CONFIG,
        mode: 'dark',
        dark: {
          ...DEFAULT_DARK_PALETTE,
          primary: '#FFFF00',
          text: '#FFFFFF',
          background: '#000000',
        },
      },
      isDefault: true,
    });
  }

  /**
   * Setup CSS element
   */
  private setupCSSElement(): void {
    if (typeof document === 'undefined') return;

    if (this.cssElement) {
      this.cssElement.remove();
    }

    this.cssElement = document.createElement('style');
    this.cssElement.id = 'anki-template-theme';
    this.cssElement.type = 'text/css';
    document.head.appendChild(this.cssElement);
  }

  /**
   * Register theme preset
   */
  registerTheme(preset: ThemePreset): { success: boolean; message: string } {
    try {
      this.themes.set(preset.id, preset);
      logger.info(`[Theme] Registered theme: ${preset.name}`);
      return {
        success: true,
        message: `Registered theme: ${preset.name}`,
      };
    } catch (error) {
      logger.error('[Theme] Failed to register theme', error);
      return {
        success: false,
        message: 'Failed to register theme',
      };
    }
  }

  /**
   * Set active theme
   */
  setTheme(themeId: string): { success: boolean; message: string } {
    try {
      const theme = this.themes.get(themeId);
      if (!theme) {
        return { success: false, message: `Theme not found: ${themeId}` };
      }

      this.currentThemeId = themeId;
      this.config = { ...theme.config };
      this.currentMode = theme.config.mode;

      this.applyTheme();
      this.persistToStorage();

      logger.info(`[Theme] Set theme to: ${theme.name}`);

      return {
        success: true,
        message: `Theme set to: ${theme.name}`,
      };
    } catch (error) {
      logger.error('[Theme] Failed to set theme', error);
      return {
        success: false,
        message: 'Failed to set theme',
      };
    }
  }

  /**
   * Set theme mode (light/dark/auto)
   */
  setThemeMode(mode: ThemeMode): void {
    this.currentMode = mode;
    this.config.mode = mode;
    this.applyTheme();
    this.persistToStorage();
    logger.info(`[Theme] Set theme mode to: ${mode}`);
  }

  /**
   * Update color palette
   */
  updateColorPalette(isDark: boolean, updates: Partial<ColorPalette>): { success: boolean; message: string } {
    try {
      const palette = isDark ? this.config.dark : this.config.light;
      Object.assign(palette, updates);
      this.applyTheme();
      this.persistToStorage();

      return {
        success: true,
        message: 'Color palette updated',
      };
    } catch (error) {
      logger.error('[Theme] Failed to update palette', error);
      return {
        success: false,
        message: 'Failed to update color palette',
      };
    }
  }

  /**
   * Update custom CSS
   */
  setCustomCSS(css: string): { success: boolean; message: string } {
    try {
      this.config.customCSS = css;
      this.applyTheme();
      this.persistToStorage();

      logger.info('[Theme] Updated custom CSS');

      return {
        success: true,
        message: 'Custom CSS updated',
      };
    } catch (error) {
      logger.error('[Theme] Failed to update custom CSS', error);
      return {
        success: false,
        message: 'Failed to update custom CSS',
      };
    }
  }

  /**
   * Update typography settings
   */
  updateTypography(updates: { fontFamily?: string; fontSize?: number; borderRadius?: number }): void {
    if (updates.fontFamily) this.config.fontFamily = updates.fontFamily;
    if (updates.fontSize) this.config.fontSize = updates.fontSize;
    if (updates.borderRadius) this.config.borderRadius = updates.borderRadius;

    this.applyTheme();
    this.persistToStorage();
  }

  /**
   * Apply theme to DOM
   */
  private applyTheme(): void {
    if (typeof document === 'undefined') return;

    if (!this.cssElement) {
      this.setupCSSElement();
    }

    // Determine if dark mode
    const isDark = this.currentMode === 'dark' || 
                   (this.currentMode === 'auto' && this.mediaQueryList?.matches);

    const palette = isDark ? this.config.dark : this.config.light;

    // Generate CSS variables
    const cssVars = this.generateCSSVariables(palette);

    // Build stylesheet
    let css = ':root {\n';
    for (const [key, value] of Object.entries(cssVars)) {
      css += `  ${key}: ${value};\n`;
    }
    css += `  --font-family: ${this.config.fontFamily};\n`;
    css += `  --font-size: ${this.config.fontSize}px;\n`;
    css += `  --border-radius: ${this.config.borderRadius}px;\n`;
    css += '}\n\n';

    // Add custom CSS
    css += this.config.customCSS;

    // Apply to element
    if (this.cssElement) {
      this.cssElement.textContent = css;
    }

    // Update document class
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    if (isDark) {
      document.documentElement.classList.add('dark-theme');
      document.documentElement.classList.remove('light-theme');
    } else {
      document.documentElement.classList.add('light-theme');
      document.documentElement.classList.remove('dark-theme');
    }

    logger.debug(`[Theme] Applied ${isDark ? 'dark' : 'light'} theme`);
  }

  /**
   * Generate CSS variables from palette
   */
  private generateCSSVariables(palette: ColorPalette): CSSVariableMap {
    return {
      '--color-primary': palette.primary,
      '--color-primary-light': palette.primaryLight,
      '--color-primary-dark': palette.primaryDark,
      '--color-secondary': palette.secondary,
      '--color-accent': palette.accent,
      '--color-background': palette.background,
      '--color-surface': palette.surface,
      '--color-surface-alt': palette.surfaceAlt,
      '--color-border': palette.border,
      '--color-text': palette.text,
      '--color-text-secondary': palette.textSecondary,
      '--color-text-tertiary': palette.textTertiary,
      '--color-success': palette.success,
      '--color-warning': palette.warning,
      '--color-error': palette.error,
      '--color-info': palette.info,
    };
  }

  /**
   * Get current configuration
   */
  getConfig(): ThemeConfig {
    return { ...this.config };
  }

  /**
   * Get current mode
   */
  getCurrentMode(): ThemeMode {
    return this.currentMode;
  }

  /**
   * Get effective mode (resolves 'auto')
   */
  getEffectiveMode(): 'light' | 'dark' {
    if (this.currentMode !== 'auto') return this.currentMode;
    return this.mediaQueryList?.matches ? 'dark' : 'light';
  }

  /**
   * Get all registered themes
   */
  getAllThemes(): ThemePreset[] {
    return Array.from(this.themes.values());
  }

  /**
   * Get theme by ID
   */
  getTheme(themeId: string): ThemePreset | null {
    return this.themes.get(themeId) ?? null;
  }

  /**
   * Get current theme
   */
  getCurrentTheme(): ThemePreset | null {
    return this.themes.get(this.currentThemeId) ?? null;
  }

  /**
   * Persist to storage
   */
  private persistToStorage(): void {
    try {
      const data = {
        currentThemeId: this.currentThemeId,
        currentMode: this.currentMode,
        config: this.config,
      };
      localStorage.setItem(this.storageKey, JSON.stringify(data));
    } catch (error) {
      logger.warn('[Theme] Failed to persist to storage', error);
    }
  }

  /**
   * Load from storage
   */
  private loadFromStorage(): void {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        const data = JSON.parse(stored);
        this.currentThemeId = data.currentThemeId;
        this.currentMode = data.currentMode;
        this.config = data.config;
        logger.info('[Theme] Loaded from storage');
      }
    } catch (error) {
      logger.warn('[Theme] Failed to load from storage, using defaults', error);
    }
  }

  /**
   * Reset to default theme
   */
  resetToDefault(): void {
    this.config = { ...DEFAULT_CONFIG };
    this.currentThemeId = 'default-light';
    this.currentMode = 'auto';
    this.applyTheme();
    this.persistToStorage();
    logger.info('[Theme] Reset to default theme');
  }

  /**
   * Export current theme as preset
   */
  exportTheme(name: string, description: string): ThemePreset {
    const id = `custom-${Date.now()}`;
    return {
      id,
      name,
      description,
      config: { ...this.config },
      isDefault: false,
      author: 'User',
    };
  }

  /**
   * Get CSS for export
   */
  getExportedCSS(): string {
    const isDark = this.getEffectiveMode() === 'dark';
    const palette = isDark ? this.config.dark : this.config.light;
    const cssVars = this.generateCSSVariables(palette);

    let css = ':root {\n';
    for (const [key, value] of Object.entries(cssVars)) {
      css += `  ${key}: ${value};\n`;
    }
    css += `  --font-family: ${this.config.fontFamily};\n`;
    css += `  --font-size: ${this.config.fontSize}px;\n`;
    css += `  --border-radius: ${this.config.borderRadius}px;\n`;
    css += '}\n\n';
    css += this.config.customCSS;

    return css;
  }

  /**
   * Get theme statistics
   */
  getThemeStats(): { totalThemes: number; customThemes: number; builtInThemes: number } {
    const total = this.themes.size;
    const builtIn = Array.from(this.themes.values()).filter(t => t.isDefault).length;

    return {
      totalThemes: total,
      customThemes: total - builtIn,
      builtInThemes: builtIn,
    };
  }
}

// ============================================================================
// Export Singleton Instance
// ============================================================================

export const themeManager = new ThemeManager();

// Default export
export default themeManager;
