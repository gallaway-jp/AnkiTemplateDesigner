/**
 * StyleProvider Component
 * Injects global styles and theme CSS variables into the document
 * Supports dynamic theme switching
 */

import React, { useEffect } from 'react';
import { useUiStore } from '../stores';
import { lightTheme, darkTheme, generateThemeCSS, type Theme } from './theme';
import { globalStyles } from './global';

interface StyleProviderProps {
  children: React.ReactNode;
}

/**
 * Inject theme variables into DOM
 */
const injectThemeVariables = (theme: Theme): void => {
  const root = document.documentElement;
  const cssText = generateThemeCSS(theme);

  // Remove existing style tag if present
  let styleTag = document.getElementById('theme-variables');
  if (styleTag) {
    styleTag.remove();
  }

  // Create and inject new style tag
  styleTag = document.createElement('style');
  styleTag.id = 'theme-variables';
  styleTag.textContent = `:root {\n  ${cssText}\n}`;
  document.head.appendChild(styleTag);

  // Set data attribute for CSS selectors
  root.setAttribute('data-theme', theme.mode);
};

/**
 * Inject global styles into DOM
 */
const injectGlobalStyles = (): void => {
  let styleTag = document.getElementById('global-styles');
  if (!styleTag) {
    styleTag = document.createElement('style');
    styleTag.id = 'global-styles';
    styleTag.textContent = globalStyles;
    document.head.appendChild(styleTag);
  }
};

/**
 * StyleProvider Component
 * Wraps the app to provide theme and global styles
 */
export const StyleProvider: React.FC<StyleProviderProps> = ({ children }) => {
  const theme = useUiStore((state) => state.theme);

  useEffect(() => {
    // Inject global styles once on mount
    injectGlobalStyles();

    // Inject theme variables when theme changes
    const selectedTheme = theme === 'dark' ? darkTheme : lightTheme;
    injectThemeVariables(selectedTheme);

    // Persist theme preference
    localStorage.setItem('app-theme', theme);
  }, [theme]);

  return <>{children}</>;
};

/**
 * Utility to get current theme
 */
export const getTheme = (): Theme => {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  return isDark ? darkTheme : lightTheme;
};

/**
 * Utility to apply inline styles from component style strings
 */
export const applyStyles = (styleString: string): React.CSSProperties => {
  const styles: React.CSSProperties = {};
  const declarations = styleString.split(';');

  declarations.forEach((decl) => {
    const [property, value] = decl.split(':');
    if (property && value) {
      const camelCaseProperty = property
        .trim()
        .replace(/-([a-z])/g, (g) => g[1].toUpperCase());
      styles[camelCaseProperty as any] = value.trim();
    }
  });

  return styles;
};

/**
 * Initialize theme from localStorage on app startup
 */
export const initializeTheme = (): void => {
  const savedTheme = localStorage.getItem('app-theme') as 'light' | 'dark' | null;
  
  if (savedTheme) {
    // Set theme in store
    const store = useUiStore.getState();
    if (savedTheme !== store.theme) {
      store.setTheme(savedTheme);
    }
  } else {
    // Auto-detect system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (prefersDark) {
      const store = useUiStore.getState();
      store.setTheme('dark');
    }
  }
};

/**
 * Watch for system theme changes
 */
export const watchSystemTheme = (): (() => void) => {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

  const handleChange = (e: MediaQueryListEvent): void => {
    const store = useUIStore.getState();
    const savedTheme = localStorage.getItem('app-theme');

    // Only apply if user hasn't set a preference
    if (!savedTheme) {
      store.setTheme(e.matches ? 'dark' : 'light');
    }
  };

  // Modern API
  if (mediaQuery.addEventListener) {
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }

  // Fallback for older browsers
  mediaQuery.addListener(handleChange);
  return () => mediaQuery.removeListener(handleChange);
};

/**
 * React Hook for using theme
 */
export const useTheme = () => {
  const theme = useUiStore((state) => state.theme);
  const setTheme = useUiStore((state) => state.setTheme);
  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  return {
    theme,
    setTheme,
    toggleTheme,
    isDark: theme === 'dark',
    isLight: theme === 'light',
    colors: theme === 'dark' ? darkTheme.colors : lightTheme.colors,
  };
};

/**
 * Styled component helper
 * Usage: const StyledButton = createStyledComponent('button', buttonStyles);
 */
export const createStyledComponent = (
  tag: keyof React.JSX.IntrinsicElements,
  styles: string
) => {
  return React.forwardRef<
    any,
    React.HTMLAttributes<HTMLElement> & { children?: React.ReactNode }
  >(({ style, ...props }, ref) => {
    const Element = tag as any;
    const combinedStyles = {
      ...applyStyles(styles),
      ...style,
    };

    return <Element ref={ref} style={combinedStyles} {...props} />;
  });
};

export default StyleProvider;
