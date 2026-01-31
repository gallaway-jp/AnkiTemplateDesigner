/**
 * i18n Bridge for Vanilla JavaScript
 * 
 * Provides a simple interface for using i18next in vanilla JavaScript files
 * (without React). This allows designer.js, validation.js, etc. to access
 * translations and locale formatting without needing React components.
 */

import i18next from './config';

let isInitialized = false;

/**
 * Initialize i18n for vanilla JS usage
 * i18next is already initialized in config.ts, this just marks readiness
 */
async function initializeI18n() {
    if (isInitialized) {
        return i18next;
    }

    try {
        if (!i18next) {
            console.warn('i18next not available. Translations unavailable.');
            return null;
        }

        isInitialized = true;
        return i18next;
    } catch (error) {
        console.error('Failed to initialize i18n bridge:', error);
        return null;
    }
}

/**
 * Get the i18next instance
 */
function getI18n() {
    return i18next;
}

/**
 * Check if i18n is initialized
 */
function isI18nInitialized() {
    return isInitialized && i18next;
}

/**
 * Translate a key
 * Usage: t('components.text.label') or t('errors.html-1')
 */
function t(key, options) {
    if (!i18next) {
        console.warn(`Translation requested but i18next not available: ${key}`);
        return key;
    }

    try {
        const result = i18next.t(key, options);
        return result || key;
    } catch (error) {
        console.warn(`Translation error for key: ${key}`, error);
        return key;
    }
}

/**
 * Change language
 */
async function changeLanguage(lang) {
    if (!i18next) {
        console.warn('i18next not initialized');
        return false;
    }

    try {
        await i18next.changeLanguage(lang);
        localStorage.setItem('ankiDesignerLanguage', lang);
        updateDocumentDirection();
        return true;
    } catch (error) {
        console.error(`Failed to change language to ${lang}:`, error);
        return false;
    }
}

/**
 * Get current language
 */
function getCurrentLanguage() {
    if (!i18next) return 'en';
    return i18next.language.split('-')[0];
}

/**
 * Get list of available languages
 */
function getAvailableLanguages() {
    return [
        { code: 'en', name: 'English', nativeName: 'English', rtl: false },
        { code: 'es', name: 'Spanish', nativeName: 'Español', rtl: false },
        { code: 'de', name: 'German', nativeName: 'Deutsch', rtl: false },
        { code: 'fr', name: 'French', nativeName: 'Français', rtl: false },
        { code: 'zh', name: 'Chinese', nativeName: '中文', rtl: false },
        { code: 'ja', name: 'Japanese', nativeName: '日本語', rtl: false },
        { code: 'ar', name: 'Arabic', nativeName: 'العربية', rtl: true },
        { code: 'he', name: 'Hebrew', nativeName: 'עברית', rtl: true }
    ];
}

/**
 * Check if current language is RTL
 */
function isRTLLanguage() {
    const lang = getCurrentLanguage();
    return ['ar', 'he'].includes(lang);
}

/**
 * Update document direction based on current language
 */
function updateDocumentDirection() {
    const htmlElement = document.documentElement;
    const isRTL = isRTLLanguage();
    
    if (isRTL) {
        htmlElement.setAttribute('dir', 'rtl');
        document.body.dir = 'rtl';
    } else {
        htmlElement.setAttribute('dir', 'ltr');
        document.body.dir = 'ltr';
    }
    
    const lang = getCurrentLanguage();
    htmlElement.setAttribute('lang', lang);
}

/**
 * Format date according to current language
 */
function formatDate(date) {
    const lang = getCurrentLanguage();
    const region = getRegionForLanguage(lang);
    const locale = `${lang}-${region}`;

    try {
        return new Intl.DateTimeFormat(locale, { dateStyle: 'long' }).format(new Date(date));
    } catch (error) {
        return new Date(date).toLocaleDateString();
    }
}

/**
 * Format date and time according to current language
 */
function formatDateTime(date) {
    const lang = getCurrentLanguage();
    const region = getRegionForLanguage(lang);
    const locale = `${lang}-${region}`;

    try {
        return new Intl.DateTimeFormat(locale, { 
            dateStyle: 'long', 
            timeStyle: 'medium' 
        }).format(new Date(date));
    } catch (error) {
        return new Date(date).toString();
    }
}

/**
 * Format number according to current language
 */
function formatNumber(num) {
    const lang = getCurrentLanguage();
    const region = getRegionForLanguage(lang);
    const locale = `${lang}-${region}`;

    try {
        return new Intl.NumberFormat(locale).format(num);
    } catch (error) {
        return num.toString();
    }
}

/**
 * Format currency according to current language
 */
function formatCurrency(amount, currency = 'USD') {
    const lang = getCurrentLanguage();
    const region = getRegionForLanguage(lang);
    const locale = `${lang}-${region}`;

    try {
        return new Intl.NumberFormat(locale, {
            style: 'currency',
            currency
        }).format(amount);
    } catch (error) {
        return `${currency} ${amount}`;
    }
}

/**
 * Get region for a language code
 */
function getRegionForLanguage(lang) {
    const regions = {
        'en': 'US',
        'es': 'ES',
        'de': 'DE',
        'fr': 'FR',
        'zh': 'CN',
        'ja': 'JP',
        'ar': 'SA',
        'he': 'IL'
    };
    return regions[lang] || 'US';
}

// Export for global usage
if (typeof window !== 'undefined') {
    window.i18nBridge = {
        initializeI18n,
        getI18n,
        isI18nInitialized,
        t,
        changeLanguage,
        getCurrentLanguage,
        getAvailableLanguages,
        isRTLLanguage,
        updateDocumentDirection,
        formatDate,
        formatDateTime,
        formatNumber,
        formatCurrency
    };
}

export default {
    initializeI18n,
    getI18n,
    isI18nInitialized,
    t,
    changeLanguage,
    getCurrentLanguage,
    getAvailableLanguages,
    isRTLLanguage,
    updateDocumentDirection,
    formatDate,
    formatDateTime,
    formatNumber,
    formatCurrency
};

