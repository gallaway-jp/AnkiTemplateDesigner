# i18n Implementation Action Guide
## Quick Reference for Fixing Internationalization Issues

**Date**: January 21, 2026  
**Status**: Ready for Implementation  
**Est. Effort**: 40-50 hours total

---

## Critical Issues at a Glance

| Issue | Files Affected | Fix Effort | Priority |
|-------|---|---|---|
| 50+ hardcoded UI labels | `designer.js` | 2h | 🔴 CRITICAL |
| 100+ error messages | `validation.js`, `error_ui.js`, `error_system.py` | 4h | 🔴 CRITICAL |
| No i18n framework | All files | 8h | 🔴 CRITICAL |
| Date formatting broken | All files | 2h | 🔴 CRITICAL |
| RTL languages unsupported | CSS, HTML, JS | 8h | 🔴 CRITICAL |
| No number localization | Validation, UI | 2h | 🟠 HIGH |
| No translation workflow | Project-wide | 4h | 🟠 HIGH |

---

## Phase 1: Framework Setup (2-3 days)

### Step 1: Install Dependencies

```bash
npm install i18next i18next-browser-languagedetector react-i18next
npm install --save-dev i18next-scanner  # For string extraction

# For date/time/number formatting (native browser API - no install needed)
# Uses Intl.DateTimeFormat, Intl.NumberFormat, Intl.ListFormat
```

### Step 2: Create i18n Config

**File**: `web/src/i18n/config.ts`

```typescript
import i18next from 'i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import { initReactI18next } from 'react-i18next';

// Import English translations
import commonEn from '../locales/en/common.json';
import componentsEn from '../locales/en/components.json';
import errorsEn from '../locales/en/errors.json';
import validationEn from '../locales/en/validation.json';

i18next
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    supportedLngs: ['en', 'es', 'fr', 'de', 'zh', 'ja', 'pt', 'ru', 'ar'],
    
    defaultNS: 'translation',
    ns: ['translation'],
    
    interpolation: {
      escapeValue: false, // React already handles XSS
    },
    
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },
    
    resources: {
      en: {
        translation: {
          common: commonEn,
          components: componentsEn,
          errors: errorsEn,
          validation: validationEn,
        },
      },
      // Add other languages as translations are completed
    },
  });

export default i18next;
```

### Step 3: Create Translation File Structure

```bash
mkdir -p web/src/locales/{en,es,fr,de,zh,ja,pt,ru,ar}
```

**File**: `web/src/locales/en/common.json`

```json
{
  "app": {
    "title": "Anki Template Designer",
    "version": "1.0.0"
  },
  "languages": {
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "zh": "中文",
    "ja": "日本語",
    "pt": "Português",
    "ru": "Русский",
    "ar": "العربية"
  },
  "buttons": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit",
    "add": "Add",
    "close": "Close",
    "ok": "OK",
    "apply": "Apply"
  },
  "messages": {
    "loading": "Loading...",
    "saving": "Saving...",
    "saved": "Saved successfully",
    "error": "An error occurred",
    "warning": "Warning",
    "success": "Success",
    "deleteConfirm": "Are you sure you want to delete this?"
  }
}
```

**File**: `web/src/locales/en/components.json`

```json
{
  "text": {
    "label": "Text",
    "description": "Static text content (not dynamic)",
    "help": "Use for labels, instructions, or static content. Text components display exactly what you type and do not change based on field data.",
    "examples": ["Labels", "Instructions", "Section headers"]
  },
  "field": {
    "label": "Field",
    "description": "Dynamic content from Anki field",
    "help": "Displays the content of an Anki field (front, back, extra, etc.). The actual value depends on what you enter in the card during review.",
    "examples": ["Card front", "Card back", "Extra info"]
  },
  "image": {
    "label": "Image",
    "description": "Display images from files",
    "help": "Shows images. You can reference images from your Anki collection media folder, or use base64 encoded data.",
    "examples": ["Photos", "Diagrams", "Flashcard images"]
  },
  "video": {
    "label": "Video",
    "description": "Embed video content",
    "help": "Plays video media. Supports common formats like MP4, WebM, and Ogg Theora.",
    "examples": ["Pronunciation guides", "Demonstrations", "Tutorials"]
  },
  "audio": {
    "label": "Audio",
    "description": "Play audio/sound files",
    "help": "Plays audio content. Perfect for pronunciation guides, vocabulary, language learning.",
    "examples": ["Pronunciation", "Language lessons", "Music"]
  },
  "container": {
    "label": "Container",
    "description": "Group components together",
    "help": "A box to organize other components. Use containers to create sections and control layout.",
    "examples": ["Header section", "Content area", "Footer"]
  },
  "row": {
    "label": "Row",
    "description": "Arrange items horizontally",
    "help": "Places items side-by-side in a row.",
    "examples": ["Two-column layout", "Buttons in a line", "Side-by-side images"]
  },
  "column": {
    "label": "Column",
    "description": "Arrange items vertically",
    "help": "Stacks items on top of each other.",
    "examples": ["Vertical list", "Stacked content", "Info blocks"]
  },
  "cloze": {
    "label": "Cloze Deletion",
    "description": "Reveal hidden text (fill-in-the-blank)",
    "help": "Creates a cloze deletion - text that is hidden until revealed.",
    "examples": ["Fill-in-the-blank questions", "Study with hints", "Progressive reveal"]
  },
  "hint": {
    "label": "Hint",
    "description": "Clickable hint text",
    "help": "Shows hint text that is revealed when clicked.",
    "examples": ["Hints", "Clues", "Study aids"]
  },
  "conditional": {
    "label": "Conditional",
    "description": "Show/hide based on field content",
    "help": "Shows or hides content based on whether a specific field has content.",
    "examples": ["Optional fields", "Extra info sections", "Conditional content"]
  },
  "button": {
    "label": "Button",
    "description": "Clickable button element",
    "help": "A button for user interaction.",
    "examples": ["Navigation", "Links", "Actions"]
  },
  "link": {
    "label": "Link",
    "description": "Hyperlink to URL",
    "help": "Creates a clickable link to a URL or external resource.",
    "examples": ["References", "Sources", "External links"]
  }
}
```

**File**: `web/src/locales/en/errors.json`

```json
{
  "html": {
    "missing_container": "Your template needs a container element (like a div or section) to hold the content",
    "unclosed_tags": "Some HTML tags aren't properly closed or nested. Make sure opening tags have matching closing tags.",
    "empty_container": "You have an empty container that doesn't serve a purpose. Consider removing it.",
    "invalid_tag": "You're using an invalid HTML tag. Use standard tags like div, span, p, section, etc."
  },
  "anki": {
    "invalid_field_reference": "Field reference is incorrect. Use {{FieldName}} format. Check that the field name matches exactly.",
    "field_syntax_error": "Field syntax is wrong. Use {{Field}} format, not {Field} or {{field}}",
    "missing_conditional_syntax": "Optional field missing conditional syntax. Use {{#FieldName}}content{{/FieldName}} for optional fields."
  },
  "css": {
    "syntax_error": "Your CSS has syntax errors. Check for typos, missing semicolons, or invalid properties.",
    "inefficient": "Your CSS could be more efficient. Consider using shorthand properties to reduce file size."
  },
  "accessibility": {
    "missing_alt_text": "Images need alt text describing them for accessibility.",
    "heading_hierarchy": "Heading hierarchy is incorrect. Use h1, h2, h3 in order without skipping levels.",
    "missing_labels": "Form inputs need labels for accessibility. Add <label> or aria-label attributes."
  },
  "performance": {
    "too_many_elements": "Your template has too many nested elements. Simplify the structure for better performance.",
    "absolute_units": "Use relative units (em, rem) instead of pixels for better responsive design."
  },
  "default": "There's an issue with your template. See the detailed error message below for specifics."
}
```

**File**: `web/src/locales/en/validation.json`

```json
{
  "suggestions": {
    "html-1": ["Add a container element to wrap your content", "Use <div> or <section> as a wrapper"],
    "html-2": ["Check for missing closing tags", "Ensure all tags are properly nested"],
    "anki-1": ["Use {{FieldName}} format exactly", "Check for typos in field names"],
    "a11y-1": ["Add alt text: <img alt=\"Description\">", "Describe what the image shows clearly"]
  },
  "context": {
    "inField": "Error in template field '{field}'",
    "inComponent": "Error in component '{component}'",
    "onLine": "Issue on line {line}"
  }
}
```

### Step 4: Create useTranslation Hook

**File**: `web/src/hooks/useTranslation.ts`

```typescript
import { useTranslation as useI18nTranslation } from 'react-i18next';

export function useTranslation() {
  const { t, i18n } = useI18nTranslation();
  
  return {
    t,
    language: i18n.language,
    changeLanguage: (lang: string) => i18n.changeLanguage(lang),
    isRTL: ['ar', 'he', 'fa', 'ur'].includes(i18n.language),
  };
}
```

### Step 5: Create Locale Formatting Hook

**File**: `web/src/hooks/useLocaleFormat.ts`

```typescript
import { useTranslation } from './useTranslation';

export function useLocaleFormat() {
  const { language } = useTranslation();
  
  return {
    formatDate(date: Date, options?: Intl.DateTimeFormatOptions) {
      return new Intl.DateTimeFormat(language, options).format(date);
    },
    
    formatTime(date: Date, options?: Intl.DateTimeFormatOptions) {
      return new Intl.DateTimeFormat(language, {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        ...options,
      }).format(date);
    },
    
    formatDateTime(date: Date, options?: Intl.DateTimeFormatOptions) {
      return new Intl.DateTimeFormat(language, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        ...options,
      }).format(date);
    },
    
    formatNumber(num: number, options?: Intl.NumberFormatOptions) {
      return new Intl.NumberFormat(language, options).format(num);
    },
    
    formatCurrency(amount: number, currency = 'USD') {
      return new Intl.NumberFormat(language, {
        style: 'currency',
        currency,
      }).format(amount);
    },
    
    formatList(items: string[], options?: Intl.ListFormatOptions) {
      return new Intl.ListFormat(language, options).format(items);
    },
  };
}
```

---

## Phase 2: Update Component Files (1-2 days)

### Update: web/designer.js

**Before**:
```javascript
const COMPONENT_GUIDE = {
    'text': {
        label: 'Text',
        description: 'Static text content (not dynamic)',
        help: 'Use for labels, instructions, or static content...'
    }
};
```

**After**:
```typescript
import { useTranslation } from '@hooks/useTranslation';

export function useComponentGuide() {
    const { t } = useTranslation();
    
    return {
        'text': {
            label: t('components.text.label'),
            description: t('components.text.description'),
            help: t('components.text.help'),
            examples: [
                t('components.text.examples.0'),
                t('components.text.examples.1'),
                t('components.text.examples.2')
            ]
        },
        'field': {
            label: t('components.field.label'),
            description: t('components.field.description'),
            help: t('components.field.help'),
            examples: [
                t('components.field.examples.0'),
                t('components.field.examples.1'),
                t('components.field.examples.2')
            ]
        },
        // ... rest of components
    };
}

// Usage in component:
function ComponentList() {
    const guide = useComponentGuide();
    return (
        <div>
            {Object.entries(guide).map(([key, component]) => (
                <div key={key}>
                    <h3>{component.label}</h3>
                    <p>{component.description}</p>
                </div>
            ))}
        </div>
    );
}
```

### Update: web/validation.js

**Before**:
```javascript
getUserFriendlyMessage(error) {
    const messageMap = {
        'html-1': 'Your template needs a container element...',
        'anki-1': 'Field reference is incorrect...'
    };
    return messageMap[error.ruleId] || messageMap['default'];
}
```

**After**:
```typescript
import { useTranslation } from '@hooks/useTranslation';

export function useValidationMessages() {
    const { t } = useTranslation();
    
    return {
        getUserFriendlyMessage(ruleId: string) {
            return t(`errors.${ruleId}`, {
                defaultValue: t('errors.default')
            });
        },
        
        getSuggestions(ruleId: string) {
            const key = `validation.suggestions.${ruleId}`;
            const suggestions = t(key, { returnObjects: true });
            return Array.isArray(suggestions) ? suggestions : [];
        }
    };
}
```

### Update: web/error_ui.js

**Before**:
```javascript
getSeverityIcon(severity) {
    const icons = {
        'info': 'ℹ',
        'warning': '⚠',
        'error': '✕',
        'critical': '⚡'
    };
    return icons[severity];
}
```

**After**:
```typescript
import { useTranslation } from '@hooks/useTranslation';

export function useErrorUI() {
    const { t } = useTranslation();
    
    const severityConfig = {
        info: { icon: 'ℹ', label: t('messages.info') },
        warning: { icon: '⚠', label: t('messages.warning') },
        error: { icon: '✕', label: t('messages.error') },
        critical: { icon: '⚡', label: t('messages.error') }
    };
    
    return {
        getSeverityIcon(severity: string) {
            return severityConfig[severity]?.icon || '●';
        },
        
        getSeverityLabel(severity: string) {
            return severityConfig[severity]?.label || severity;
        }
    };
}
```

---

## Phase 3: Add Regional Formatting (1 day)

### Update Timestamp Usage

**Before**:
```typescript
const timestamp = new Date().toISOString();
```

**After**:
```typescript
import { useLocaleFormat } from '@hooks/useLocaleFormat';

// In component:
function ErrorDisplay({ error }) {
    const { formatDateTime } = useLocaleFormat();
    
    return (
        <div>
            <p>{error.message}</p>
            <small>{formatDateTime(new Date(error.timestamp))}</small>
        </div>
    );
}
```

### Update Number Display

**Before**:
```javascript
`${errors.length} errors found`
```

**After**:
```typescript
import { useTranslation } from '@hooks/useTranslation';

function ValidationResults({ errors }) {
    const { t, language } = useTranslation();
    const { formatNumber } = useLocaleFormat();
    
    return (
        <p>
            {t('validation.errorsFound', {
                count: errors.length,
                number: formatNumber(errors.length)
            })}
        </p>
    );
}
```

---

## Phase 4: RTL Support (1-2 days)

### Update HTML

```html
<!-- src/index.html -->
<!DOCTYPE html>
<html id="app-root" lang="en" dir="ltr">
<head>
    <meta charset="UTF-8">
    <script>
        // Set RTL immediately on load
        const rtlLangs = ['ar', 'he', 'fa', 'ur'];
        const lang = localStorage.getItem('i18nextLng') || navigator.language.split('-')[0];
        if (rtlLangs.includes(lang)) {
            document.documentElement.dir = 'rtl';
            document.documentElement.lang = lang;
        }
    </script>
</head>
<body>
    <div id="root"></div>
</body>
</html>
```

### Update CSS for RTL

**web/src/styles/rtl.css**:

```css
/* Logical properties work for both LTR and RTL */
:root[dir="rtl"] {
    --margin-start: var(--margin-right);
    --margin-end: var(--margin-left);
    --padding-start: var(--padding-right);
    --padding-end: var(--padding-left);
}

:root[dir="ltr"] {
    --margin-start: var(--margin-left);
    --margin-end: var(--margin-right);
    --padding-start: var(--padding-left);
    --padding-end: var(--padding-right);
}

/* All components should use logical properties */
.container {
    margin-inline-start: 20px;     /* margin-left in LTR, margin-right in RTL */
    padding-inline-start: 10px;    /* padding-left in LTR, padding-right in RTL */
    text-align: start;             /* text-align: left in LTR, right in RTL */
}

.row {
    display: flex;
    flex-direction: row;
    direction: inherit;            /* Inherit from parent RTL setting */
}

/* Fallback for older browsers */
@supports not (margin-inline-start: 0) {
    [dir="rtl"] .container {
        margin-right: 20px;
        margin-left: 0;
        padding-right: 10px;
        padding-left: 0;
        text-align: right;
    }
}
```

### Update App Component

```typescript
// src/App.tsx
import { useTranslation } from '@hooks/useTranslation';
import { useEffect } from 'react';

export function App() {
    const { language } = useTranslation();
    const rtlLanguages = ['ar', 'he', 'fa', 'ur'];
    const isRTL = rtlLanguages.includes(language);
    
    useEffect(() => {
        const root = document.documentElement;
        root.dir = isRTL ? 'rtl' : 'ltr';
        root.lang = language;
    }, [language, isRTL]);
    
    return (
        <div className="app" dir={isRTL ? 'rtl' : 'ltr'}>
            {/* Your app content */}
        </div>
    );
}
```

---

## Phase 5: Add Language Switcher (0.5 day)

```typescript
// src/components/LanguageSwitcher.tsx
import { useTranslation } from '@hooks/useTranslation';

export function LanguageSwitcher() {
    const { language, changeLanguage, t } = useTranslation();
    
    const languages = [
        { code: 'en', name: 'English' },
        { code: 'es', name: 'Español' },
        { code: 'fr', name: 'Français' },
        { code: 'de', name: 'Deutsch' },
        { code: 'zh', name: '中文' },
        { code: 'ja', name: '日本語' },
        { code: 'ar', name: 'العربية' },
    ];
    
    return (
        <select 
            value={language} 
            onChange={(e) => changeLanguage(e.target.value)}
            aria-label={t('labels.language')}
        >
            {languages.map(lang => (
                <option key={lang.code} value={lang.code}>
                    {lang.name}
                </option>
            ))}
        </select>
    );
}
```

---

## String Extraction Script

**scripts/extract-strings.js**:

```javascript
const fs = require('fs');
const path = require('path');

function extractStrings() {
    const strings = {};
    
    // Extract from JS/TS files
    const srcDir = path.join(__dirname, '../web/src');
    const files = fs.readdirSync(srcDir, { recursive: true });
    
    files.forEach(file => {
        if (!file.endsWith('.ts') && !file.endsWith('.tsx')) return;
        
        const content = fs.readFileSync(path.join(srcDir, file), 'utf8');
        
        // Find t('key') patterns
        const matches = content.matchAll(/t\(['"`]([^'"`]+)['"` ])/g);
        for (const match of matches) {
            const key = match[1];
            strings[key] = key; // Use key as placeholder value
        }
    });
    
    // Write extracted strings
    fs.writeFileSync(
        path.join(__dirname, '../web/src/locales/en/extracted.json'),
        JSON.stringify(strings, null, 2)
    );
    
    console.log(`Extracted ${Object.keys(strings).length} translation keys`);
}

extractStrings();
```

---

## Testing Checklist

- [ ] Language switching works without page reload
- [ ] All UI strings translate correctly
- [ ] Error messages display in selected language
- [ ] Dates format per locale (1/21 vs 21/1 vs 21.1)
- [ ] Numbers format per locale (1,234.56 vs 1.234,56)
- [ ] RTL layout correct for Arabic/Hebrew
- [ ] No text overflow in RTL layout
- [ ] Font supports all Unicode characters
- [ ] Help links work in translated pages
- [ ] Component guide translates completely

---

## Next Steps

1. ✅ **Choose i18n library**: i18next recommended
2. ✅ **Install dependencies**
3. ✅ **Create folder structure**
4. ✅ **Extract English strings** to JSON files
5. ✅ **Implement useTranslation hooks**
6. ✅ **Update components** to use translations
7. ✅ **Add RTL support** for Arabic/Hebrew
8. ✅ **Implement language selector**
9. ⏳ **Translate to first language** (Spanish or Chinese)
10. ⏳ **Test thoroughly** with real translations
11. ⏳ **Set up translation workflow** (Crowdin, etc.)

---

**Status**: Ready to implement  
**Estimated Timeline**: 5-8 weeks to production i18n  
**Next Priority**: Phase 1 Framework Setup
