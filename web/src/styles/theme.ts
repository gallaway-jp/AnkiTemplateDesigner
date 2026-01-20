/**
 * Theme System - Global Theme Configuration
 * Supports light and dark modes with customizable colors
 * Provides theme tokens for consistent styling
 */

export type ThemeMode = 'light' | 'dark';

export interface ThemeColors {
  primary: string;
  primaryHover: string;
  primaryActive: string;
  secondary: string;
  success: string;
  warning: string;
  error: string;
  surface: string;
  surfaceHover: string;
  border: string;
  borderLight: string;
  text: string;
  textSecondary: string;
  textDisabled: string;
  background: string;
  backgroundAlt: string;
}

export interface ThemeSpacing {
  xs: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  '2xl': string;
  '3xl': string;
}

export interface ThemeRadius {
  none: string;
  sm: string;
  md: string;
  lg: string;
  full: string;
}

export interface ThemeShadows {
  none: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
}

export interface Theme {
  mode: ThemeMode;
  colors: ThemeColors;
  spacing: ThemeSpacing;
  radius: ThemeRadius;
  shadows: ThemeShadows;
  transitions: {
    fast: string;
    base: string;
    slow: string;
  };
}

// Light Theme
export const lightTheme: Theme = {
  mode: 'light',
  colors: {
    primary: '#3b82f6',
    primaryHover: '#2563eb',
    primaryActive: '#1d4ed8',
    secondary: '#8b5cf6',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    surface: '#ffffff',
    surfaceHover: '#f3f4f6',
    border: '#e5e7eb',
    borderLight: '#f3f4f6',
    text: '#1f2937',
    textSecondary: '#6b7280',
    textDisabled: '#9ca3af',
    background: '#f9fafb',
    backgroundAlt: '#f3f4f6',
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '2.5rem',
    '3xl': '3rem',
  },
  radius: {
    none: '0',
    sm: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    full: '9999px',
  },
  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
  },
  transitions: {
    fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
    base: '250ms cubic-bezier(0.4, 0, 0.2, 1)',
    slow: '350ms cubic-bezier(0.4, 0, 0.2, 1)',
  },
};

// Dark Theme
export const darkTheme: Theme = {
  mode: 'dark',
  colors: {
    primary: '#60a5fa',
    primaryHover: '#3b82f6',
    primaryActive: '#2563eb',
    secondary: '#a78bfa',
    success: '#34d399',
    warning: '#fbbf24',
    error: '#f87171',
    surface: '#1f2937',
    surfaceHover: '#111827',
    border: '#374151',
    borderLight: '#4b5563',
    text: '#f3f4f6',
    textSecondary: '#d1d5db',
    textDisabled: '#9ca3af',
    background: '#111827',
    backgroundAlt: '#1f2937',
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '2.5rem',
    '3xl': '3rem',
  },
  radius: {
    none: '0',
    sm: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    full: '9999px',
  },
  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.4)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.5)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.6)',
  },
  transitions: {
    fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
    base: '250ms cubic-bezier(0.4, 0, 0.2, 1)',
    slow: '350ms cubic-bezier(0.4, 0, 0.2, 1)',
  },
};

/**
 * Get CSS variable name from theme key
 */
export const getCSSVariable = (key: string): string => {
  return `var(--${key})`;
};

/**
 * Generate CSS custom properties from theme
 */
export const generateThemeCSS = (theme: Theme): string => {
  const vars: string[] = [];

  // Colors
  Object.entries(theme.colors).forEach(([key, value]) => {
    vars.push(`--color-${key}: ${value};`);
  });

  // Spacing
  Object.entries(theme.spacing).forEach(([key, value]) => {
    vars.push(`--spacing-${key}: ${value};`);
  });

  // Radius
  Object.entries(theme.radius).forEach(([key, value]) => {
    vars.push(`--radius-${key}: ${value};`);
  });

  // Shadows
  Object.entries(theme.shadows).forEach(([key, value]) => {
    vars.push(`--shadow-${key}: ${value};`);
  });

  // Transitions
  Object.entries(theme.transitions).forEach(([key, value]) => {
    vars.push(`--transition-${key}: ${value};`);
  });

  return vars.join('\n  ');
};

/**
 * Theme utilities for component styling
 */
export const themeUtils = {
  /**
   * Get color with optional opacity
   */
  getColor: (color: string, opacity?: number): string => {
    if (opacity !== undefined) {
      return `rgba(${color}, ${opacity})`;
    }
    return color;
  },

  /**
   * Get spacing value
   */
  getSpacing: (multiplier: number): string => {
    return `${multiplier * 0.25}rem`;
  },

  /**
   * Create focus styles
   */
  focusStyles: (): string => {
    return `
      outline: 2px solid transparent;
      outline-offset: 2px;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1), 0 0 0 5px rgb(59, 130, 246);
    `;
  },

  /**
   * Create transition shorthand
   */
  transition: (properties: string[] = ['all'], duration: string = '250ms'): string => {
    return properties.map((prop) => `${prop} ${duration} cubic-bezier(0.4, 0, 0.2, 1)`).join(', ');
  },
};
