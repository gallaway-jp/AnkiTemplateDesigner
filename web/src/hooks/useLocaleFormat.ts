/**
 * useLocaleFormat Hook
 * 
 * React hook for locale-aware formatting of dates, times, numbers, and currencies.
 * Uses the Intl API for proper internationalization support.
 */

import { useMemo } from 'react';
import { useTranslation } from './useTranslation';

export interface DateFormatOptions {
  style?: 'full' | 'long' | 'medium' | 'short';
  dateStyle?: 'full' | 'long' | 'medium' | 'short';
  timeStyle?: 'full' | 'long' | 'medium' | 'short';
  includeTime?: boolean;
}

export interface NumberFormatOptions {
  style?: 'decimal' | 'percent' | 'currency';
  currency?: string;
  minimumFractionDigits?: number;
  maximumFractionDigits?: number;
  useGrouping?: boolean;
}

/**
 * Custom hook for locale-aware formatting
 */
export function useLocaleFormat() {
  const { currentLanguage, languageConfig } = useTranslation();

  // Create locale string from language and region
  const locale = useMemo(() => {
    const region = languageConfig?.region || 'US';
    return `${currentLanguage}-${region}`;
  }, [currentLanguage, languageConfig]);

  /**
   * Format a date/time value
   * 
   * Examples:
   *   formatDateTime(new Date()) -> "1/21/2026, 10:30:00 AM" (en-US)
   *   formatDateTime(new Date(), { style: 'short' }) -> "1/21/26, 10:30 AM"
   *   formatDate(new Date()) -> "January 21, 2026" (en-US)
   *   formatTime(new Date()) -> "10:30:00 AM"
   */
  const formatDateTime = (date: Date, options?: DateFormatOptions): string => {
    try {
      const opts: Intl.DateTimeFormatOptions = {};

      if (options?.style) {
        // Legacy style option
        const styleMap = {
          full: { dateStyle: 'full' as const, timeStyle: 'long' as const },
          long: { dateStyle: 'long' as const, timeStyle: 'medium' as const },
          medium: { dateStyle: 'medium' as const, timeStyle: 'medium' as const },
          short: { dateStyle: 'short' as const, timeStyle: 'short' as const },
        };
        const mapped = styleMap[options.style];
        Object.assign(opts, mapped);
      }

      if (options?.dateStyle) opts.dateStyle = options.dateStyle;
      if (options?.timeStyle) opts.timeStyle = options.timeStyle;

      if (!opts.dateStyle && !opts.timeStyle) {
        opts.dateStyle = 'medium';
        opts.timeStyle = 'medium';
      }

      return new Intl.DateTimeFormat(locale, opts).format(date);
    } catch (error) {
      console.error('Error formatting date:', error);
      return date.toString();
    }
  };

  /**
   * Format only the date part
   */
  const formatDate = (date: Date, style: 'full' | 'long' | 'medium' | 'short' = 'long'): string => {
    try {
      const opts: Intl.DateTimeFormatOptions = { dateStyle: style };
      return new Intl.DateTimeFormat(locale, opts).format(date);
    } catch (error) {
      console.error('Error formatting date:', error);
      return date.toLocaleDateString(locale);
    }
  };

  /**
   * Format only the time part
   */
  const formatTime = (date: Date, style: 'full' | 'long' | 'medium' | 'short' = 'medium'): string => {
    try {
      const opts: Intl.DateTimeFormatOptions = { timeStyle: style };
      return new Intl.DateTimeFormat(locale, opts).format(date);
    } catch (error) {
      console.error('Error formatting time:', error);
      return date.toLocaleTimeString(locale);
    }
  };

  /**
   * Format a number with locale-aware decimal and thousand separators
   * 
   * Examples:
   *   formatNumber(1234.56) -> "1,234.56" (en-US)
   *   formatNumber(1234.56, { style: 'currency', currency: 'EUR' }) -> "€1,234.56" (en-US)
   *   formatNumber(0.75, { style: 'percent' }) -> "75%"
   */
  const formatNumber = (value: number, options?: NumberFormatOptions): string => {
    try {
      const opts: Intl.NumberFormatOptions = {
        useGrouping: options?.useGrouping !== false,
      };

      if (options?.style) opts.style = options.style;
      if (options?.currency) opts.currency = options.currency;
      if (options?.minimumFractionDigits !== undefined) {
        opts.minimumFractionDigits = options.minimumFractionDigits;
      }
      if (options?.maximumFractionDigits !== undefined) {
        opts.maximumFractionDigits = options.maximumFractionDigits;
      }

      return new Intl.NumberFormat(locale, opts).format(value);
    } catch (error) {
      console.error('Error formatting number:', error);
      return value.toString();
    }
  };

  /**
   * Format a currency value
   * 
   * Examples:
   *   formatCurrency(1234.56, 'USD') -> "$1,234.56" (en-US)
   *   formatCurrency(1234.56, 'EUR') -> "€1,234.56" (en-US)
   */
  const formatCurrency = (value: number, currency: string = 'USD'): string => {
    return formatNumber(value, {
      style: 'currency',
      currency,
      minimumFractionDigits: getCurrencyDecimalPlaces(currency),
      maximumFractionDigits: getCurrencyDecimalPlaces(currency),
    });
  };

  /**
   * Format a percentage
   */
  const formatPercent = (value: number, decimals: number = 0): string => {
    return formatNumber(value, {
      style: 'percent',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  };

  /**
   * Format a list of items with locale-aware formatting
   * 
   * Examples:
   *   formatList(['Apple', 'Banana', 'Orange']) -> "Apple, Banana, and Orange" (en-US)
   *   formatList(['Apple', 'Banana', 'Orange']) -> "Apple, Banana y Orange" (es-ES)
   */
  const formatList = (items: string[], type: 'conjunction' | 'disjunction' = 'conjunction'): string => {
    try {
      return new Intl.ListFormat(locale, { type }).format(items);
    } catch (error) {
      console.error('Error formatting list:', error);
      const conjunction = type === 'conjunction' ? ' and ' : ' or ';
      return items.join(', ').replace(/, ([^,]*)$/, conjunction + '$1');
    }
  };

  /**
   * Format relative time (e.g., "2 days ago", "in 3 weeks")
   */
  const formatRelativeTime = (
    value: number,
    unit: Intl.RelativeTimeFormatUnit = 'second',
    style: 'long' | 'short' | 'narrow' = 'long'
  ): string => {
    try {
      return new Intl.RelativeTimeFormat(locale, { style }).format(value, unit);
    } catch (error) {
      console.error('Error formatting relative time:', error);
      return `${value} ${unit} ago`;
    }
  };

  /**
   * Get plural form of a word (if supported by locale)
   */
  const getPluralRules = (type: 'cardinal' | 'ordinal' = 'cardinal') => {
    try {
      return new Intl.PluralRules(locale, { type });
    } catch (error) {
      console.error('Error getting plural rules:', error);
      return null;
    }
  };

  /**
   * Get collation for sorting strings
   */
  const getCollator = (options?: Intl.CollatorOptions) => {
    try {
      return new Intl.Collator(locale, options);
    } catch (error) {
      console.error('Error getting collator:', error);
      return null;
    }
  };

  /**
   * Sort an array of strings with locale-aware collation
   */
  const sortStrings = (strings: string[], options?: Intl.CollatorOptions): string[] => {
    const collator = getCollator(options);
    if (!collator) return strings;
    return [...strings].sort((a, b) => collator.compare(a, b));
  };

  return {
    locale,
    formatDateTime,
    formatDate,
    formatTime,
    formatNumber,
    formatCurrency,
    formatPercent,
    formatList,
    formatRelativeTime,
    getPluralRules,
    getCollator,
    sortStrings,
  };
}

/**
 * Helper function to get decimal places for a currency
 */
function getCurrencyDecimalPlaces(currency: string): number {
  // Standard decimal places for currencies
  const decimalPlaces: Record<string, number> = {
    // 0 decimal places
    'AED': 0, 'AFN': 0, 'ALL': 0, 'AMD': 0, 'ANG': 0, 'AOA': 0, 'ARS': 0, 'AUD': 0,
    'AWG': 0, 'AZN': 0, 'BAM': 0, 'BBD': 0, 'BDT': 0, 'BGN': 0, 'BHD': 3, 'BIF': 0,
    'BMD': 0, 'BND': 0, 'BOB': 0, 'BRL': 0, 'BSD': 0, 'BTC': 8, 'BTN': 0, 'BWP': 0,
    'BYN': 0, 'BZD': 0, 'CAD': 0, 'CDF': 0, 'CHF': 0, 'CLF': 4, 'CLP': 0, 'CNY': 0,
    'COP': 0, 'CRC': 0, 'CUC': 0, 'CUP': 0, 'CVE': 0, 'CZK': 0, 'DJF': 0, 'DKK': 0,
    'DOP': 0, 'DZD': 0, 'EGP': 0, 'ERN': 0, 'ETB': 0, 'EUR': 0, 'FJD': 0, 'FKP': 0,
    'GBP': 0, 'GEL': 0, 'GHS': 0, 'GIP': 0, 'GMD': 0, 'GNF': 0, 'GTQ': 0, 'GYD': 0,
    'HKD': 0, 'HNL': 0, 'HRK': 0, 'HTG': 0, 'HUF': 0, 'IDR': 0, 'ILS': 0, 'INR': 0,
    'IQD': 3, 'IRR': 0, 'ISK': 0, 'JMD': 0, 'JOD': 3, 'JPY': 0, 'KES': 0, 'KGS': 0,
    'KHR': 0, 'KMF': 0, 'KPW': 0, 'KRW': 0, 'KWD': 3, 'KYD': 0, 'KZT': 0, 'LAK': 0,
    'LBP': 0, 'LKR': 0, 'LRD': 0, 'LSL': 0, 'LYD': 3, 'MAD': 0, 'MDL': 0, 'MGA': 0,
    'MKD': 0, 'MMK': 0, 'MNT': 0, 'MOP': 0, 'MRU': 0, 'MUR': 0, 'MVR': 0, 'MWK': 0,
    'MXN': 0, 'MYR': 0, 'MZN': 0, 'NAD': 0, 'NGN': 0, 'NIO': 0, 'NOK': 0, 'NPR': 0,
    'NZD': 0, 'OMR': 3, 'PAB': 0, 'PEN': 0, 'PGK': 0, 'PHP': 0, 'PKR': 0, 'PLN': 0,
    'PYG': 0, 'QAR': 0, 'RON': 0, 'RSD': 0, 'RUB': 0, 'RWF': 0, 'SAR': 0, 'SBD': 0,
    'SCR': 0, 'SDG': 0, 'SEK': 0, 'SGD': 0, 'SHP': 0, 'SLL': 0, 'SOS': 0, 'SRD': 0,
    'SSP': 0, 'STN': 0, 'SYP': 0, 'SZL': 0, 'THB': 0, 'TJS': 0, 'TMT': 0, 'TND': 3,
    'TOP': 0, 'TRY': 0, 'TTD': 0, 'TWD': 0, 'TZS': 0, 'UAH': 0, 'UGX': 0, 'USD': 0,
    'UYU': 0, 'UZS': 0, 'VES': 0, 'VND': 0, 'VUV': 0, 'WST': 0, 'XAF': 0, 'XAG': 0,
    'XAU': 0, 'XBA': 0, 'XBB': 0, 'XBC': 0, 'XBD': 0, 'XCD': 0, 'XDR': 0, 'XOF': 0,
    'XPD': 0, 'XPF': 0, 'XPT': 0, 'XSU': 0, 'XTS': 0, 'XUA': 0, 'XXX': 0, 'YER': 0,
    'ZAR': 0, 'ZMW': 0, 'ZWL': 0,
  };
  return decimalPlaces[currency] || 2; // Default to 2 decimal places
}
