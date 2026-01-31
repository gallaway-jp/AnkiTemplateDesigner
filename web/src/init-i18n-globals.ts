/**
 * Initialize i18n globals immediately for both React and standalone use
 * This runs before the React app loads, ensuring globals are available
 */

import i18next from './i18n/config';

// Initialize vanilla JS bridge
async function initializeGlobals() {
  try {
    // Initialize i18next
    await i18next.init({
      fallbackLng: 'en',
      ns: ['common', 'components', 'errors', 'validation', 'templates', 'messages'],
      defaultNS: 'common',
      interpolation: {
        escapeValue: false
      }
    });

    // Import bridge modules after i18next is ready
    const bridgeModule = await import('./i18n/vanilla-js-bridge');
    const componentGuideModule = await import('./i18n/component-guide-i18n');
    const errorMessagesModule = await import('./i18n/error-messages-i18n');

    console.log('✅ i18n globals initialized');
    console.log('window.i18nBridge:', typeof window.i18nBridge !== 'undefined');
    console.log('window.i18nComponentGuide:', typeof window.i18nComponentGuide !== 'undefined');
    console.log('window.i18nErrors:', typeof window.i18nErrors !== 'undefined');

    return true;
  } catch (error) {
    console.error('Failed to initialize i18n globals:', error);
    return false;
  }
}

// Run immediately if in browser
if (typeof window !== 'undefined') {
  initializeGlobals();
}

export default initializeGlobals;
