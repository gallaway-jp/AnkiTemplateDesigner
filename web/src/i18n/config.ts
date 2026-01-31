/**
 * i18n Configuration
 * 
 * Initializes i18next with language detection, namespaces, and fallback language.
 * Supports:
 * - Automatic language detection (browser, localStorage, query parameters)
 * - Namespace-based organization of translations
 * - Fallback to English if language not available
 * - RTL language support
 */

import i18next from 'i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import { initReactI18next } from 'react-i18next';

// Dynamic import for HttpBackend (only needed in production)
let HttpBackend: any = null;

// Language detection options
const detectionOptions = {
  order: ['localStorage', 'navigator', 'querystring', 'htmlTag'],
  caches: ['localStorage'],
  lookupLocalStorage: 'ankiDesignerLanguage',
  lookupQuerystring: 'lang',
};

// Supported languages and their RTL status
export const SUPPORTED_LANGUAGES = {
  en: { name: 'English', rtl: false, region: 'US' },
  es: { name: 'Español', rtl: false, region: 'ES' },
  de: { name: 'Deutsch', rtl: false, region: 'DE' },
  fr: { name: 'Français', rtl: false, region: 'FR' },
  zh: { name: '中文 (Simplified)', rtl: false, region: 'CN' },
  ja: { name: '日本語', rtl: false, region: 'JP' },
  ar: { name: 'العربية', rtl: true, region: 'SA' },
  he: { name: 'עברית', rtl: true, region: 'IL' },
};

/**
 * Get the current language configuration
 */
export function getCurrentLanguageConfig() {
  const lang = i18next.language.split('-')[0];
  return SUPPORTED_LANGUAGES[lang as keyof typeof SUPPORTED_LANGUAGES] || SUPPORTED_LANGUAGES.en;
}

/**
 * Check if current language is RTL
 */
export function isRTLLanguage(): boolean {
  return getCurrentLanguageConfig().rtl;
}

/**
 * Initialize i18next
 */
export async function initI18n() {
  // In development, we'll load translations directly without HttpBackend
  const i18nConfig: any = {
    fallbackLng: 'en',
    fallbackNS: 'common',
    ns: ['common', 'components', 'errors', 'validation', 'templates', 'messages'],
    defaultNS: 'common',
    detection: detectionOptions,
    interpolation: {
      escapeValue: false, // React handles XSS protection
      formatSeparator: ',',
    },
    returnEmptyString: false,
    returnNull: false,
    react: {
      useSuspense: false,
      transEmptyNodeValue: '',
    },
  };

  // Always use direct resource loading (works better with Vite)
  const enCommon = await import('../../public/locales/en/common.json');
  const enComponents = await import('../../public/locales/en/components.json');
  const enErrors = await import('../../public/locales/en/errors.json');
  const enValidation = await import('../../public/locales/en/validation.json');
  const enTemplates = await import('../../public/locales/en/templates.json');
  const enMessages = await import('../../public/locales/en/messages.json');
  
  const esCommon = await import('../../public/locales/es/common.json');
  const esComponents = await import('../../public/locales/es/components.json');
  const esErrors = await import('../../public/locales/es/errors.json');
  const esValidation = await import('../../public/locales/es/validation.json');
  const esTemplates = await import('../../public/locales/es/templates.json');
  const esMessages = await import('../../public/locales/es/messages.json');

  i18nConfig.resources = {
    en: {
      common: enCommon.default,
      components: enComponents.default,
      errors: enErrors.default,
      validation: enValidation.default,
      templates: enTemplates.default,
      messages: enMessages.default,
    },
    es: {
      common: esCommon.default,
      components: esComponents.default,
      errors: esErrors.default,
      validation: esValidation.default,
      templates: esTemplates.default,
      messages: esMessages.default,
    },
  };

  let instance = i18next;

  instance = instance
    .use(LanguageDetector)
    .use(initReactI18next);

  await instance.init(i18nConfig);

  // Set HTML dir attribute for RTL languages
  updateDocumentDirection();

  // Listen for language changes
  instance.on('languageChanged', updateDocumentDirection);

  return instance;
}

/**
 * Update document direction based on current language
 */
function updateDocumentDirection() {
  const htmlElement = document.documentElement;
  if (isRTLLanguage()) {
    htmlElement.setAttribute('dir', 'rtl');
    htmlElement.setAttribute('lang', i18next.language);
    document.body.dir = 'rtl';
  } else {
    htmlElement.setAttribute('dir', 'ltr');
    htmlElement.setAttribute('lang', i18next.language);
    document.body.dir = 'ltr';
  }
}

export default i18next;
