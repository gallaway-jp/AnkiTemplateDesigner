/**
 * Global Styles - Application-wide styling
 * Includes responsive typography, layout, and utility classes
 */

import { lightTheme, darkTheme, generateThemeCSS } from './theme';

/**
 * Generate complete global stylesheet
 */
export const generateGlobalStyles = (): string => {
  return `
    /* ========================================
       RESET & BASE STYLES
       ======================================== */
    
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    html {
      font-size: 16px;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }

    /* Light Theme (Default) */
    :root {
      ${generateThemeCSS(lightTheme)}
      color-scheme: light;
    }

    /* Dark Theme */
    [data-theme="dark"] {
      ${generateThemeCSS(darkTheme)}
      color-scheme: dark;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
        'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
        sans-serif;
      font-size: 1rem;
      line-height: 1.5;
      color: var(--color-text);
      background-color: var(--color-background);
      transition: background-color var(--transition-base), color var(--transition-base);
    }

    /* ========================================
       TYPOGRAPHY
       ======================================== */

    h1 {
      font-size: 2.5rem;
      font-weight: 700;
      line-height: 1.2;
      letter-spacing: -0.02em;
      margin-bottom: var(--spacing-md);
    }

    h2 {
      font-size: 2rem;
      font-weight: 700;
      line-height: 1.25;
      letter-spacing: -0.01em;
      margin-bottom: var(--spacing-md);
    }

    h3 {
      font-size: 1.5rem;
      font-weight: 600;
      line-height: 1.33;
      margin-bottom: var(--spacing-sm);
    }

    h4 {
      font-size: 1.25rem;
      font-weight: 600;
      line-height: 1.4;
      margin-bottom: var(--spacing-sm);
    }

    h5 {
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.5;
      margin-bottom: var(--spacing-xs);
    }

    h6 {
      font-size: 0.875rem;
      font-weight: 600;
      line-height: 1.57;
      margin-bottom: var(--spacing-xs);
    }

    p {
      margin-bottom: var(--spacing-md);
    }

    a {
      color: var(--color-primary);
      text-decoration: none;
      transition: color var(--transition-fast);
    }

    a:hover {
      color: var(--color-primaryHover);
      text-decoration: underline;
    }

    a:active {
      color: var(--color-primaryActive);
    }

    /* ========================================
       FORM ELEMENTS
       ======================================== */

    input,
    textarea,
    select {
      font-family: inherit;
      font-size: inherit;
      color: inherit;
    }

    input[type="text"],
    input[type="email"],
    input[type="password"],
    input[type="number"],
    textarea,
    select {
      width: 100%;
      padding: var(--spacing-sm);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-md);
      background-color: var(--color-surface);
      color: var(--color-text);
      transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
    }

    input[type="text"]:focus,
    input[type="email"]:focus,
    input[type="password"]:focus,
    input[type="number"]:focus,
    textarea:focus,
    select:focus {
      outline: none;
      border-color: var(--color-primary);
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    input[type="text"]:disabled,
    input[type="email"]:disabled,
    input[type="password"]:disabled,
    input[type="number"]:disabled,
    textarea:disabled,
    select:disabled {
      background-color: var(--color-backgroundAlt);
      color: var(--color-textDisabled);
      cursor: not-allowed;
    }

    input[type="checkbox"],
    input[type="radio"] {
      accent-color: var(--color-primary);
      cursor: pointer;
    }

    /* ========================================
       BUTTONS
       ======================================== */

    button {
      font-family: inherit;
      font-size: inherit;
      cursor: pointer;
      border: none;
      padding: var(--spacing-sm) var(--spacing-md);
      border-radius: var(--radius-md);
      background-color: var(--color-primary);
      color: #ffffff;
      font-weight: 500;
      transition: all var(--transition-fast);
    }

    button:hover {
      background-color: var(--color-primaryHover);
      transform: translateY(-1px);
      box-shadow: var(--shadow-md);
    }

    button:active {
      background-color: var(--color-primaryActive);
      transform: translateY(0);
    }

    button:disabled {
      background-color: var(--color-backgroundAlt);
      color: var(--color-textDisabled);
      cursor: not-allowed;
      transform: none;
    }

    /* ========================================
       LAYOUT
       ======================================== */

    .container {
      width: 100%;
      max-width: 1280px;
      margin: 0 auto;
      padding: 0 var(--spacing-md);
    }

    .flex {
      display: flex;
    }

    .flex-col {
      flex-direction: column;
    }

    .flex-center {
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .grid {
      display: grid;
    }

    .gap-xs {
      gap: var(--spacing-xs);
    }

    .gap-sm {
      gap: var(--spacing-sm);
    }

    .gap-md {
      gap: var(--spacing-md);
    }

    .gap-lg {
      gap: var(--spacing-lg);
    }

    /* ========================================
       SPACING UTILITIES
       ======================================== */

    .p-xs {
      padding: var(--spacing-xs);
    }

    .p-sm {
      padding: var(--spacing-sm);
    }

    .p-md {
      padding: var(--spacing-md);
    }

    .p-lg {
      padding: var(--spacing-lg);
    }

    .m-xs {
      margin: var(--spacing-xs);
    }

    .m-sm {
      margin: var(--spacing-sm);
    }

    .m-md {
      margin: var(--spacing-md);
    }

    .m-lg {
      margin: var(--spacing-lg);
    }

    /* ========================================
       TEXT UTILITIES
       ======================================== */

    .text-center {
      text-align: center;
    }

    .text-right {
      text-align: right;
    }

    .text-left {
      text-align: left;
    }

    .text-sm {
      font-size: 0.875rem;
    }

    .text-base {
      font-size: 1rem;
    }

    .text-lg {
      font-size: 1.125rem;
    }

    .font-medium {
      font-weight: 500;
    }

    .font-semibold {
      font-weight: 600;
    }

    .font-bold {
      font-weight: 700;
    }

    .truncate {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    /* ========================================
       DISPLAY & VISIBILITY
       ======================================== */

    .hidden {
      display: none !important;
    }

    .block {
      display: block;
    }

    .inline-block {
      display: inline-block;
    }

    .opacity-50 {
      opacity: 0.5;
    }

    .opacity-75 {
      opacity: 0.75;
    }

    /* ========================================
       ANIMATIONS
       ======================================== */

    @keyframes fadeIn {
      from {
        opacity: 0;
      }
      to {
        opacity: 1;
      }
    }

    @keyframes slideIn {
      from {
        transform: translateX(-10px);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }

    @keyframes slideUp {
      from {
        transform: translateY(10px);
        opacity: 0;
      }
      to {
        transform: translateY(0);
        opacity: 1;
      }
    }

    @keyframes spin {
      from {
        transform: rotate(0deg);
      }
      to {
        transform: rotate(360deg);
      }
    }

    .animate-fadeIn {
      animation: fadeIn var(--transition-base);
    }

    .animate-slideIn {
      animation: slideIn var(--transition-base);
    }

    .animate-slideUp {
      animation: slideUp var(--transition-base);
    }

    .animate-spin {
      animation: spin 1s linear infinite;
    }

    /* ========================================
       RESPONSIVE
       ======================================== */

    @media (max-width: 768px) {
      html {
        font-size: 14px;
      }

      h1 {
        font-size: 2rem;
      }

      h2 {
        font-size: 1.5rem;
      }

      h3 {
        font-size: 1.25rem;
      }

      .container {
        padding: 0 var(--spacing-sm);
      }
    }

    @media (max-width: 480px) {
      html {
        font-size: 13px;
      }

      h1 {
        font-size: 1.75rem;
      }

      h2 {
        font-size: 1.25rem;
      }

      h3 {
        font-size: 1rem;
      }

      button {
        padding: var(--spacing-sm) var(--spacing-md);
        font-size: 0.875rem;
      }
    }

    /* ========================================
       SCROLLBAR STYLING
       ======================================== */

    ::-webkit-scrollbar {
      width: 8px;
      height: 8px;
    }

    ::-webkit-scrollbar-track {
      background: var(--color-background);
    }

    ::-webkit-scrollbar-thumb {
      background: var(--color-border);
      border-radius: var(--radius-full);
    }

    ::-webkit-scrollbar-thumb:hover {
      background: var(--color-borderLight);
    }
  `;
};

// Export as string for CSS injection
export const globalStyles = generateGlobalStyles();
