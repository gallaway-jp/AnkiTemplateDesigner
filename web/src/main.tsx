/**
 * Main application entry point
 * Initializes React app, Craft.js, i18n, and Python bridge
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/globals.css';
import { initI18n } from './i18n/config';
import { createLogger } from './utils/logger';
import { bridge } from './services/pythonBridge';
// Import i18n bridge modules - they will create global objects when imported
// These must be imported AFTER i18n/config is loaded but we import them here
// and they execute immediately when this file loads
import './i18n/vanilla-js-bridge';
import './i18n/component-guide-i18n';
import './i18n/error-messages-i18n';

const errorLogger = createLogger('GlobalError');

function setupGlobalErrorReporting() {
  window.addEventListener('error', (event) => {
    const message = event.message || 'Unhandled error';
    const details = {
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      stack: (event.error as Error | undefined)?.stack,
    };
    errorLogger.error(message, details);
    bridge.logClientEvent('error', message, details).catch(() => undefined);
  });

  window.addEventListener('unhandledrejection', (event) => {
    const reason = event.reason as Error | string;
    const message = reason instanceof Error ? reason.message : String(reason);
    const details = {
      stack: reason instanceof Error ? reason.stack : undefined,
    };
    errorLogger.error(`Unhandled promise rejection: ${message}`, details);
    bridge.logClientEvent('error', `Unhandled promise rejection: ${message}`, details).catch(() => undefined);
  });
}

async function main() {
  setupGlobalErrorReporting();
  // Initialize i18n framework before rendering app
  try {
    // Initialize i18next framework
    await initI18n();
    console.log('✅ i18n initialized');
    console.log('✅ window.i18nBridge:', typeof window.i18nBridge !== 'undefined');
    console.log('✅ window.i18nComponentGuide:', typeof window.i18nComponentGuide !== 'undefined');
    console.log('✅ window.i18nErrors:', typeof window.i18nErrors !== 'undefined');
  } catch (error) {
    console.error('❌ Failed to initialize i18n:', error);
    // Continue with default English if i18n fails
  }

  // Initialize root
  const root = document.getElementById('root');
  if (!root) {
    throw new Error('Root element not found');
  }

  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}

main();
