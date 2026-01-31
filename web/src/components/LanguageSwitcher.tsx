/**
 * LanguageSwitcher Component
 * 
 * Dropdown component for switching between available languages
 * Displays language names and manages language changes
 */

import React, { useState } from 'react';
import { useLanguage } from '../hooks/useTranslation';
import '../styles/language-switcher.css';

export function LanguageSwitcher() {
  const { currentLanguage, changeLanguage, availableLanguages, isRTL } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);

  const currentLang = availableLanguages.find(lang => lang.code === currentLanguage);

  const handleLanguageChange = async (langCode: string) => {
    await changeLanguage(langCode);
    setIsOpen(false);
  };

  return (
    <div className="language-switcher">
      <button
        className="language-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle language selection"
        aria-expanded={isOpen}
        title={`Current language: ${currentLang?.name}`}
      >
        <span className="language-code">{currentLanguage.toUpperCase()}</span>
        <span className="language-icon">🌐</span>
      </button>

      {isOpen && (
        <div className={`language-menu ${isRTL() ? 'rtl' : 'ltr'}`}>
          {availableLanguages.map(lang => (
            <button
              key={lang.code}
              className={`language-option ${lang.code === currentLanguage ? 'active' : ''}`}
              onClick={() => handleLanguageChange(lang.code)}
              aria-label={`Switch to ${lang.name}`}
              title={lang.nativeName}
            >
              <span className="language-name">{lang.name}</span>
              <span className="language-native">{lang.nativeName}</span>
              {lang.code === currentLanguage && <span className="checkmark">✓</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default LanguageSwitcher;
