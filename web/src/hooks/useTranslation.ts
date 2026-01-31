/**
 * useTranslation Hook
 * 
 * React hook for accessing translation functions and language management.
 * Provides:
 * - Translation function `t()` for accessing translated strings
 * - Current language getter/setter
 * - Available languages list
 * - RTL detection
 */

import { useTranslation as useI18nextTranslation } from 'react-i18next';
import i18next from '../i18n/config';
import { SUPPORTED_LANGUAGES, getCurrentLanguageConfig, isRTLLanguage } from '../i18n/config';

export interface TranslationOptions {
  count?: number;
  context?: string;
  defaultValue?: string;
  [key: string]: any;
}

/**
 * Custom useTranslation hook that extends react-i18next
 */
export function useTranslation(namespace?: string | string[]) {
  const { t: i18nT, i18n } = useI18nextTranslation(namespace);

  /**
   * Enhanced translation function
   * Usage:
   *   t('key')
   *   t('key', { interpolation: 'value' })
   *   t('key', { count: 5 }) // pluralization
   */
  const t = (key: string, options?: TranslationOptions | string) => {
    if (typeof options === 'string') {
      // Backward compatibility: t('key', 'namespace')
      return i18nT(key, { ns: options });
    }
    return i18nT(key, options);
  };

  /**
   * Get available languages
   */
  const getAvailableLanguages = () => {
    return Object.entries(SUPPORTED_LANGUAGES).map(([code, config]) => ({
      code,
      ...config,
    }));
  };

  /**
   * Get current language
   */
  const getCurrentLanguage = () => {
    return i18next.language.split('-')[0];
  };

  /**
   * Change language
   */
  const changeLanguage = async (lang: string) => {
    try {
      await i18next.changeLanguage(lang);
      localStorage.setItem('ankiDesignerLanguage', lang);
      return true;
    } catch (error) {
      console.error(`Failed to change language to ${lang}:`, error);
      return false;
    }
  };

  /**
   * Get current language config (name, RTL, region)
   */
  const getCurrentLanguageConfig = () => {
    return getCurrentLanguageConfig();
  };

  /**
   * Check if current language is RTL
   */
  const isRTL = () => {
    return isRTLLanguage();
  };

  /**
   * Pluralize a key based on count
   * Usage: tPlural('items', count)
   * Looks for keys like: 'items_one', 'items_other'
   */
  const tPlural = (key: string, count: number, options?: TranslationOptions) => {
    return t(key, { ...options, count });
  };

  /**
   * Get all translations for a namespace
   */
  const getNamespace = (namespace: string) => {
    return i18n.getResourceBundle(i18next.language, namespace);
  };

  return {
    t,
    tPlural,
    i18n,
    isInitialized: i18n.isInitialized,
    isLoading: i18n.isLoading,
    currentLanguage: getCurrentLanguage(),
    changeLanguage,
    availableLanguages: getAvailableLanguages(),
    languageConfig: getCurrentLanguageConfig(),
    isRTL,
    getNamespace,
  };
}

/**
 * Hook for language switching without translation
 * Useful for components that only need language management
 */
export function useLanguage() {
  const { currentLanguage, changeLanguage, availableLanguages, languageConfig, isRTL } =
    useTranslation();

  return {
    currentLanguage,
    changeLanguage,
    availableLanguages,
    languageConfig,
    isRTL,
  };
}

/**
 * Hook for getting translations in a specific namespace
 */
export function useNamespace(namespace: string) {
  const { t, getNamespace } = useTranslation(namespace);

  return {
    t,
    namespace: getNamespace(namespace),
  };
}
