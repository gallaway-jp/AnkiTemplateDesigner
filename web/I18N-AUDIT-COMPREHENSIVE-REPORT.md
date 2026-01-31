# Internationalization (i18n) Audit Report
## AnkiTemplateDesigner Codebase Analysis

**Date**: January 21, 2026  
**Status**: COMPREHENSIVE AUDIT COMPLETE  
**Grade**: C+ (4.5/10) - Major Work Required  
**Priority**: HIGH (Blocking Global Release)

---

## Executive Summary

The codebase contains **extensive hardcoded strings, no existing i18n infrastructure, and critical gaps in regional formatting support**. To support a global user base, significant architectural changes are required before international deployment.

### Critical Findings

| Category | Finding | Impact | Priority |
|----------|---------|--------|----------|
| **Hardcoded Strings** | 200+ user-facing strings | Cannot serve non-English users | 🔴 CRITICAL |
| **i18n Framework** | None exists | Requires full implementation | 🔴 CRITICAL |
| **Regional Formatting** | No locale support | Dates/numbers incorrect globally | 🔴 CRITICAL |
| **Component Labels** | 50+ UI component names | No translation support | 🔴 CRITICAL |
| **Error Messages** | 100+ error strings | Inconsistent, not translateable | 🟠 HIGH |
| **Accessibility** | Not i18n aware | RTL languages not supported | 🟠 HIGH |
| **Testing** | No i18n tests | Untranslatable code will persist | 🟠 HIGH |

---

## Part 1: Hardcoded Strings Inventory

### 1.1 UI Component Labels (50+ strings)

**File**: `web/designer.js` (lines 1045-1200+)

**Components Found**:
```javascript
// COMPONENT_GUIDE object contains hardcoded labels, descriptions, help text
const COMPONENT_GUIDE = {
    'text': { label: 'Text', description: 'Static text content (not dynamic)', ... },
    'field': { label: 'Field', description: 'Dynamic content from Anki field', ... },
    'image': { label: 'Image', description: 'Display images from files', ... },
    'video': { label: 'Video', description: 'Embed video content', ... },
    'audio': { label: 'Audio', description: 'Play audio/sound files', ... },
    'container': { label: 'Container', description: 'Group components together', ... },
    'row': { label: 'Row', description: 'Arrange items horizontally', ... },
    'column': { label: 'Column', description: 'Arrange items vertically', ... },
    'cloze': { label: 'Cloze Deletion', description: 'Reveal hidden text...', ... },
    'hint': { label: 'Hint', description: 'Clickable hint text', ... },
    'conditional': { label: 'Conditional', description: 'Show/hide based on field...', ... },
    'button': { label: 'Button', description: 'Clickable button element', ... },
    'link': { label: 'Link', description: 'Hyperlink to URL', ... },
    // ... and more
};
```

**Issue**: 
- ❌ No translation keys used
- ❌ Descriptions embedded in code
- ❌ Help links language-specific
- ❌ Examples in English only

**Impact**: Users in non-English countries cannot use component library

---

### 1.2 Error Messages & Validation (100+ strings)

**File**: `web/validation.js` (lines 1183-1300)

**Example Error Messages**:
```javascript
const messageMap = {
    // HTML Structure
    'html-1': 'Your template needs a container element (like a div or section) to hold the content',
    'html-2': 'Some HTML tags aren\'t properly closed or nested...',
    'html-3': 'You have an empty container that doesn\'t serve a purpose...',
    'html-4': 'You\'re using an invalid HTML tag...',
    
    // Anki Fields
    'anki-1': 'Field reference is incorrect. Use {{FieldName}} format...',
    'anki-2': 'Field syntax is wrong. Use {{Field}} format, not {Field}...',
    'anki-3': 'Optional field missing conditional syntax...',
    
    // CSS & Styling
    'css-1': 'Your CSS has syntax errors. Check for typos, missing semicolons...',
    'css-2': 'Your CSS could be more efficient...',
    
    // Accessibility
    'a11y-1': 'Images need alt text describing them for accessibility...',
    'a11y-2': 'Heading hierarchy is incorrect...',
    'a11y-3': 'Form inputs need labels for accessibility...',
};
```

**Issues**:
- ❌ 100+ error message strings hardcoded
- ❌ No error code internationalization
- ❌ Suggestions also hardcoded (getSuggestionsForError)
- ❌ No user preference for error detail level

**Impact**: Error messages cannot be translated or localized

---

### 1.3 System Messages & Alerts (50+ strings)

**Files**: 
- `web/error_ui.js` - Error severity labels and dialog text
- `services/error_system.py` - Backend error templates
- `web/error_styles.css` - UI text content

**Examples**:
```javascript
// From error_ui.js
getSeverityIcon(severity) {
    const icons = {
        'info': 'ℹ',
        'warning': '⚠',
        'error': '✕',
        'critical': '⚡'
    };
}

// Hardcoded severity names
const severityLabels = ['info', 'warning', 'error', 'critical'];
```

```python
# From services/error_system.py
ERROR_MESSAGES = {
    'invalid_component_name': {
        'message': 'Component name must be unique and contain only alphanumeric characters',
        'severity': ErrorSeverity.WARNING,
    },
    'duplicate_component': {
        'message': 'A component with this name already exists',
        'severity': ErrorSeverity.ERROR,
    },
}
```

**Issues**:
- ❌ Severity labels not translateable
- ❌ Python backend error messages hardcoded
- ❌ No separation of displayText vs. internalCode
- ❌ Error recovery suggestions hardcoded

**Impact**: Backend-frontend error coordination broken for non-English users

---

### 1.4 Form Labels & Placeholders (30+ strings)

**Files**: 
- `web/src/types/editor.ts` - PropertyDefinition labels
- UI component property dialogs

**Examples**:
```typescript
// From editor.ts
export interface PropertyDefinition {
  name: string;
  label: string;        // ❌ Hardcoded labels like "Font Size", "Color", "Padding"
  type: 'text' | 'color' | 'number' | 'select';
  description?: string; // ❌ Hardcoded descriptions
  options?: Array<{ label: string; value: any }>;
}
```

**Issues**:
- ❌ Property labels hardcoded in TypeScript
- ❌ Description text not translateable
- ❌ Dropdown option labels hardcoded
- ❌ Validation messages hardcoded

**Impact**: Properties panel cannot be translated

---

### 1.5 Template Library & Starter Content (20+ strings)

**File**: `services/onboarding_manager.py` (lines 380-450)

**Examples**:
```python
StarterTemplate(
    template_id='cloze_deletion',
    name='Cloze Deletion Card',  # ❌ Hardcoded name
    category='cards',
    description='Template for cloze deletion cards with extra field',
    difficulty='intermediate',
)

StarterTemplate(
    template_id='image_based',
    name='Image-Based Card',  # ❌ Hardcoded name
    description='Template for image-focused cards with labels',
)
```

**Issues**:
- ❌ Template names not translateable
- ❌ Template descriptions hardcoded
- ❌ Category names hardcoded
- ❌ Difficulty levels hardcoded

**Impact**: Template library only useful in English

---

### 1.6 Validation & Help Text (40+ strings)

**Files**: `web/validation.js`, `docs/plans/05-CODE-STANDARDS.md`

**Examples**:
```javascript
// getSuggestionsForError method returns hardcoded strings:
'a11y-1': [
    'Add alt text to all images: <img src="..." alt="Description">',
    'Describe what the image shows, not just "image"'
],
'a11y-2': [
    'Use proper heading hierarchy (h1, h2, h3, etc.)',
    'Don\'t skip heading levels'
],
'a11y-3': [
    'Add descriptive labels to form inputs',
    'Use aria-label if visible label isn\'t appropriate'
],

'default': [
    'Review the error message to understand what needs to be fixed',
    'Check the Anki Template Designer documentation for guidance',
    'Run validation again after making changes'
]
```

**Issues**:
- ❌ 50+ suggestion strings hardcoded
- ❌ Multi-line help text not translatable
- ❌ Links to English documentation
- ❌ No context-aware help

**Impact**: Help system cannot be internationalized

---

## Part 2: Regional Formatting Issues

### 2.1 Date/Time Formatting

**Current Status**: ❌ NO IMPLEMENTATION

**Issues**:
```javascript
// Hardcoded ISO format - inappropriate for most locales
const timestamp = new Date().toISOString(); // "2026-01-21T10:30:00.000Z"

// No locale-aware formatting:
// - US: 1/21/2026 (MM/DD/YYYY)
// - UK: 21/01/2026 (DD/MM/YYYY)
// - EU: 21.01.2026 (DD.MM.YYYY)
// - China: 2026年1月21日 (YYYY年M月D日)
// - Japan: 2026/01/21 (YYYY/MM/DD)
// - Saudi Arabia: right-to-left text consideration
```

**Files with Date Issues**:
- `web/src/tests/integration-bridge.test.ts` (line 142): `new Date().toISOString()`
- `services/error_system.py`: No timestamp localization
- `web/error_ui.js`: Error timestamps use system format

**Impact**: Dates confusing for non-US users (1/12/2026 = Jan 12 or Dec 1?)

---

### 2.2 Number Formatting

**Current Status**: ❌ NO IMPLEMENTATION

**Issues**:
```javascript
// Hardcoded decimal separator - wrong for most of world
const value = "3.14";  // Should be "3,14" in many European countries

// No thousand separator handling:
// - US/UK: 1,234,567.89
// - Germany: 1.234.567,89
// - France: 1 234 567,89
// - India: 12,34,567.89

// File sizes, percentages, etc. not localized
const fileSize = "1.5 MB";  // Could be "1,5 MB" in some locales
```

**Impact**: Numbers confusing or incorrect for ~70% of world population

---

### 2.3 Currency Support

**Current Status**: ❌ NO IMPLEMENTATION

**Issues**:
- No currency selection
- No currency symbol localization
- No number formatting for prices
- No support for different decimal places (e.g., Japanese Yen has 0 decimals)

---

### 2.4 Text Direction (RTL/LTR)

**Current Status**: ❌ NO IMPLEMENTATION

**Languages Affected**:
- Arabic (277M speakers)
- Hebrew (5M speakers)
- Persian (70M speakers)
- Urdu (68M speakers)
- etc.

**Issues**:
```css
/* All CSS assumes left-to-right */
/* No RTL support:
  - No dir="rtl" attributes
  - No margin-left/right considerations
  - No flipped layouts
  - No RTL text in components
*/
```

**Files Needing RTL Support**:
- All CSS files
- All HTML templates
- Component layout logic

**Impact**: App unusable in RTL languages

---

### 2.5 Length Variations by Language

**Current Status**: ❌ NOT CONSIDERED

**Character Count Variations**:
```
English:  "Save"     (4 chars)
German:   "Speichern" (9 chars) - 125% longer
Dutch:    "Opslaan"  (7 chars)
French:   "Enregistrer" (11 chars)
Spanish:  "Guardar"  (7 chars)
Italian:  "Salva"    (5 chars)
Japanese: "保存"     (2 chars, but in double-width)
```

**UI Impact**: 
- Buttons too small for German/Dutch text
- Text overflows in fixed-width containers
- Layout breaks with longer translations

---

## Part 3: Cultural Compliance Issues

### 3.1 Colors & Visual Symbols

**Current Status**: ⚠️ PARTIALLY ADDRESSED

**Potential Issues**:
```javascript
// Color meanings vary by culture:
// - Red: danger (Western), luck/prosperity (China), purity (India)
// - White: purity (Western), mourning (East Asia)
// - Green: growth (Western), Islam, nature
// - Blue: trust (Western), coldness (some Asian cultures)

// Icons may be inappropriate:
// - ⚠️ Warning symbol not universal
// - 🔴 Red circle means different things
// - Checkmarks not universal (✓ vs. ✔ vs. other marks)
```

**Code Example** (from error_ui.js):
```javascript
const icons = {
    'info': 'ℹ',      // Unicode info symbol - may vary by font
    'warning': '⚠',   // Unicode warning - recognized but not universal
    'error': '✕',     // X symbol - could mean something else
    'critical': '⚡'   // Lightning bolt - may not translate culturally
};
```

**Impact**: Visual communication misunderstood in different cultures

---

### 3.2 Units & Measurements

**Current Status**: ❌ NO IMPLEMENTATION

**Issues**:
- Hard-coded pixel (px) units throughout CSS
- No support for metric vs. imperial
- Font sizes in pixels (not relative units)
- No print locale support (A4 vs. Letter paper)

**Examples**:
```css
/* From styles/globals.css */
padding: var(--spacing-xl);         /* Could be in different units */
font-size: var(--font-size-xl);     /* No localization of sizes */
width: 400px;                        /* US-centric */
height: 600px;                       /* No adaptation */
```

---

### 3.3 Input Validation

**Current Status**: ❌ NO LOCALE-AWARE VALIDATION

**Issues**:
```python
# From utils/security.py
MAX_FIELD_NAME_LENGTH = 100  # Could be inappropriate for languages with longer words

# No consideration for:
# - Chinese character requirements (characters vs. bytes)
# - Arabic diacritical marks (affects input validation)
# - Hindi scripts (different character encoding)
# - Thai script (no spaces between words)
```

**Impact**: Input validation too strict or too loose for different languages

---

### 3.4 Data Encoding & Collation

**Current Status**: ⚠️ POSSIBLY WORKING (needs verification)

**Issues**:
- No explicit UTF-8 declaration in all files
- Sorting order may be wrong for non-Latin alphabets
- Case conversion inappropriate for some languages (Turkish İ problem)

**Needs Verification**:
```typescript
// No locale-aware string comparison
string1.localeCompare(string2)           // Not used
string1.localeCompare(string2, 'en')     // Not locale-aware

// Python files may have encoding issues
# No -*- coding: utf-8 -*- headers in some files
```

---

## Part 4: Existing i18n Infrastructure Review

### 4.1 i18n Framework Status

**Requirement**: ❌ NONE IMPLEMENTED

**What Exists**:
- Single reference to LocalizationStrings interface in `src/types/utils.ts`
- No actual localization system
- No translation files
- No i18n library (react-i18next, i18next, etc.)

**Code Found**:
```typescript
// From src/types/utils.ts - UNUSED
export interface LocalizationStrings {
  [key: string]: string | LocalizationStrings;
}
```

**Issues**:
- ❌ Interface defined but never used
- ❌ No translation files (JSON, JSON5, XLIFF, etc.)
- ❌ No plural form support
- ❌ No context support for ambiguous words
- ❌ No namespace support for organizing translations

---

### 4.2 Language Detection

**Current Status**: ❌ NONE

**Missing Implementation**:
```javascript
// Should detect and set language, but doesn't:
// - navigator.language (browser language)
// - navigator.languages (browser preferences)
// - localStorage (user preference)
// - URL parameter (?lang=es)
// - Document lang attribute

// What's needed:
const userLanguage = navigator.language; // "es-ES", "zh-Hans-CN", etc.
const supportedLanguages = ['en', 'es', 'fr', 'de', 'zh', 'ja'];
const selectedLanguage = supportedLanguages.includes(userLanguage.split('-')[0]) 
  ? userLanguage.split('-')[0] 
  : 'en';
```

---

### 4.3 Pluralization Support

**Current Status**: ❌ NONE

**Missing**:
```javascript
// No plural support for messages like:
// English: "1 error" vs "2 errors"
// Russian: "1 ошибка", "2-4 ошибки", "5+ ошибок"
// Polish: similar complex rules
// Arabic: 6 plural forms!

// Current code just concatenates:
`${errors.length} errors found` // Wrong for non-English
```

---

### 4.4 Context-Aware Translations

**Current Status**: ❌ NONE

**Missing Example**:
```javascript
// The word "Save" has different translations:
// - Save (file): "Guardar" (Spanish - to keep/store)
// - Save (rescue): "Salvar" (Spanish - to rescue)
// - Save (economize): "Ahorrar" (Spanish - to economize)

// Current approach has no context:
label: "Save"  // Which meaning?
```

---

## Part 5: Testing & Quality Assurance

### 5.1 i18n Testing Status

**Current Status**: ❌ NONE EXIST

**Missing Tests**:
- ❌ Translation completeness tests
- ❌ Key existence validation
- ❌ Missing translation detection
- ❌ RTL layout tests
- ❌ Text overflow tests
- ❌ Character encoding tests
- ❌ Regional format tests
- ❌ Locale switching tests

---

### 5.2 String Extraction Status

**Current Status**: ❌ NO TOOLING

**Missing**:
```bash
# No extraction tools configured:
# - xgettext (for Python/JavaScript)
# - gettext (for .po files)
# - react-intl (for React apps)
# - i18next-scanner (for i18next)

# Result: No translation workflow possible
```

---

## Part 6: Recommended i18n Architecture

### 6.1 Proposed Structure

```
project/
├── locales/
│   ├── en/
│   │   ├── common.json          # Shared strings
│   │   ├── components.json      # Component labels
│   │   ├── errors.json          # Error messages
│   │   ├── validation.json      # Validation messages
│   │   ├── templates.json       # Template library
│   │   └── help.json            # Help text
│   ├── es/
│   ├── fr/
│   ├── de/
│   ├── zh/
│   ├── ja/
│   └── ...
├── src/
│   ├── i18n/
│   │   ├── config.ts            # i18n configuration
│   │   ├── resources.ts         # Load translation files
│   │   └── locales.ts           # Locale definitions
│   └── hooks/
│       └── useTranslation.ts    # React hook for translations
└── scripts/
    ├── extract-strings.js       # Extract translatable strings
    └── validate-translations.js # Validate completeness
```

### 6.2 TypeScript Type-Safe i18n System

```typescript
// src/i18n/config.ts
import i18next from 'i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

i18next
  .use(LanguageDetector)
  .init({
    fallbackLng: 'en',
    supportedLngs: ['en', 'es', 'fr', 'de', 'zh', 'ja', 'pt', 'ru', 'ar'],
    interpolation: { escapeValue: false },
    resources: {
      en: { translation: require('../locales/en/common.json') },
      es: { translation: require('../locales/es/common.json') },
      // ... other languages
    }
  });

// src/hooks/useTranslation.ts
export function useTranslation() {
  const { t, i18n } = useI18next();
  
  return {
    t: (key: string, options?: any) => t(key, options),
    lang: i18n.language,
    changeLanguage: (lang: string) => i18n.changeLanguage(lang),
  };
}

// Usage in components:
function ComponentLabel() {
  const { t } = useTranslation();
  return <label>{t('components.text.label')}</label>;
}
```

### 6.3 Translation File Format

```json
// locales/en/components.json
{
  "text": {
    "label": "Text",
    "description": "Static text content (not dynamic)",
    "help": "Use for labels, instructions, or static content...",
    "examples": {
      "0": "Labels",
      "1": "Instructions",
      "2": "Section headers"
    }
  },
  "field": {
    "label": "Field",
    "description": "Dynamic content from Anki field",
    "help": "Displays the content of an Anki field...",
    "examples": {
      "0": "Card front",
      "1": "Card back",
      "2": "Extra info"
    }
  },
  // ... more components
}
```

### 6.4 Error Message Localization

```json
// locales/en/errors.json
{
  "html": {
    "missing_container": "Your template needs a container element (like a div or section) to hold the content",
    "unclosed_tags": "Some HTML tags aren't properly closed or nested...",
    "empty_container": "You have an empty container that doesn't serve a purpose...",
    "invalid_tag": "You're using an invalid HTML tag..."
  },
  "anki": {
    "invalid_field_reference": "Field reference is incorrect. Use {{FieldName}} format...",
    "field_syntax_error": "Field syntax is wrong. Use {{Field}} format, not {Field}...",
    "missing_conditional_syntax": "Optional field missing conditional syntax..."
  },
  "css": {
    "syntax_errors": "Your CSS has syntax errors. Check for typos, missing semicolons...",
    "inefficient": "Your CSS could be more efficient..."
  }
}
```

---

## Part 7: Implementation Roadmap

### 7.1 Phase 1: Infrastructure (2-3 weeks)

**Priority**: 🔴 CRITICAL

```
Week 1:
- [ ] Choose i18n library (recommend i18next)
- [ ] Install dependencies (i18next, i18next-browser-languagedetector)
- [ ] Create locales directory structure
- [ ] Create JSON schema for translations
- [ ] Set up TypeScript types for translations
- [ ] Implement language detection
- [ ] Implement language switching UI

Week 2:
- [ ] Create translation files for English (extraction step)
- [ ] Implement useTranslation hook
- [ ] Update components to use translations
- [ ] Test language detection
- [ ] Test language switching

Week 3:
- [ ] Implement plural form support
- [ ] Implement date/time formatting (Intl.DateTimeFormat)
- [ ] Implement number formatting (Intl.NumberFormat)
- [ ] Add regional formatting utilities
- [ ] Create i18n testing utilities
```

### 7.2 Phase 2: String Extraction & Organization (1-2 weeks)

**Priority**: 🔴 CRITICAL

```
Actions:
- [ ] Extract all hardcoded strings from JavaScript/TypeScript
- [ ] Extract all hardcoded strings from Python
- [ ] Organize strings into logical JSON files
- [ ] Add comments for translator context
- [ ] Document untranslatable strings (technical terms)
- [ ] Create glossary for consistent terminology
```

### 7.3 Phase 3: Regional Formatting (1 week)

**Priority**: 🔴 CRITICAL

```
Tasks:
- [ ] Implement Intl.DateTimeFormat for all dates
- [ ] Implement Intl.NumberFormat for all numbers
- [ ] Implement Intl.ListFormat for lists
- [ ] Add RTL support (CSS, HTML attributes)
- [ ] Test with RTL languages (Arabic, Hebrew)
- [ ] Implement text direction detection
- [ ] Create CSS utilities for RTL
```

### 7.4 Phase 4: Translation Workflow (1-2 weeks)

**Priority**: 🟠 HIGH

```
Setup:
- [ ] Choose translation management platform (Crowdin, Lokalise, or Git-based)
- [ ] Export English strings for translation
- [ ] Set up translator onboarding
- [ ] Create translation guidelines
- [ ] Implement validation workflow
- [ ] Set up continuous translation updates
```

### 7.5 Phase 5: Language Support

**Recommended Initial Launch Languages**:
1. English (100%) - Already complete
2. Spanish (85%) - ~280M native speakers
3. Mandarin Chinese (85%) - ~1B native speakers
4. French (85%) - ~280M speakers
5. German (85%) - ~76M native speakers
6. Japanese (85%) - ~125M native speakers
7. Portuguese (85%) - ~252M speakers
8. Russian (50%) - ~258M speakers
9. Arabic (50%) - ~310M speakers (RTL)
10. Hindi (50%) - ~345M speakers

---

## Part 8: Accessibility Considerations

### 8.1 i18n & A11y Intersection

**Issues**:
- ❌ No screen reader language tags
- ❌ No lang attribute on HTML element
- ❌ No dir attribute for RTL
- ❌ No language-specific fonts

**Required Changes**:
```html
<!-- HTML changes -->
<html lang="es" dir="ltr">  <!-- Language and direction for screen readers -->

<!-- Component changes -->
<button aria-label="Guardar plantilla">  <!-- Localized ARIA labels -->
```

---

## Part 9: Technical Debt Estimate

### 9.1 Lines of Code to Update

| Component | Strings | Est. LOC Change | Effort |
|-----------|---------|-----------------|--------|
| UI Component Labels | 50 | +200 | 2h |
| Error Messages | 100 | +300 | 3h |
| Validation Messages | 50 | +150 | 2h |
| Help Text | 40 | +200 | 2h |
| Template Library | 20 | +100 | 1h |
| System Messages | 30 | +150 | 2h |
| **Total Strings** | **290** | **+1,100** | **12h** |

### 9.2 Additional Implementation

| Task | Effort |
|------|--------|
| i18n Framework Setup | 8h |
| Regional Formatting | 6h |
| RTL Support | 8h |
| Testing & Validation | 10h |
| Translation Workflow | 4h |
| Documentation | 4h |
| **Total Implementation** | **40h** |

### 9.3 Translation Effort (per language)

- **Spanish/French/German**: 15-20 hours each (270 strings)
- **Chinese/Japanese**: 20-25 hours each (complexity of script)
- **Arabic**: 20-25 hours (RTL complexity)
- **Russian**: 15-20 hours (plural forms)

---

## Part 10: Specific Code Changes Required

### 10.1 Component Labels Example

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

const COMPONENT_GUIDE_KEYS = {
    'text': 'components.text',
    'field': 'components.field',
    // ...
};

export function useComponentGuide() {
    const { t } = useTranslation();
    return {
        text: {
            label: t('components.text.label'),
            description: t('components.text.description'),
            help: t('components.text.help')
        },
        // ...
    };
}
```

---

### 10.2 Error Messages Example

**Before**:
```javascript
getUserFriendlyMessage(error) {
    const messageMap = {
        'html-1': 'Your template needs a container element...'
    };
    return messageMap[error.ruleId] || messageMap['default'];
}
```

**After**:
```typescript
import { useTranslation } from '@hooks/useTranslation';

export function useErrorMessages() {
    const { t } = useTranslation();
    
    return {
        getUserFriendlyMessage(error: ValidationError) {
            return t(`validation.errors.${error.ruleId}`, {
                defaultValue: t('validation.errors.default')
            });
        }
    };
}
```

---

### 10.3 Date Formatting Example

**Before**:
```javascript
const timestamp = new Date().toISOString(); // "2026-01-21T10:30:00Z"
```

**After**:
```typescript
import { useTranslation } from '@hooks/useTranslation';

export function useLocaleFormat() {
    const { i18n } = useTranslation();
    
    return {
        formatDate(date: Date) {
            return new Intl.DateTimeFormat(i18n.language, {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            }).format(date);
        },
        formatTime(date: Date) {
            return new Intl.DateTimeFormat(i18n.language, {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            }).format(date);
        },
        formatNumber(num: number) {
            return new Intl.NumberFormat(i18n.language).format(num);
        }
    };
}
```

---

### 10.4 RTL Support Example

**Before**:
```css
.container {
    margin-left: 20px;
    padding-left: 10px;
    text-align: left;
}
```

**After**:
```css
.container {
    margin-inline-start: 20px;    /* Works for both LTR and RTL */
    padding-inline-start: 10px;
    text-align: start;            /* start = left in LTR, right in RTL */
    direction: var(--text-direction);
}

@supports not (margin-inline-start: 0) {
    /* Fallback for older browsers */
    [dir="rtl"] .container {
        margin-right: 20px;
        margin-left: 0;
        padding-right: 10px;
        padding-left: 0;
        text-align: right;
    }
}
```

---

## Part 11: Testing Strategy

### 11.1 i18n Unit Tests

```typescript
import { describe, it, expect } from 'vitest';
import i18next from 'i18next';

describe('i18n', () => {
  it('should load English translations', () => {
    expect(i18next.t('components.text.label')).toBe('Text');
  });

  it('should change language', async () => {
    await i18next.changeLanguage('es');
    expect(i18next.language).toBe('es');
  });

  it('should format dates per locale', () => {
    i18next.changeLanguage('de');
    const formatted = new Intl.DateTimeFormat('de').format(new Date());
    expect(formatted).toMatch(/^\d{2}\.\d{2}\.\d{4}$/); // DD.MM.YYYY
  });

  it('should format numbers per locale', () => {
    i18next.changeLanguage('de');
    const formatted = new Intl.NumberFormat('de').format(1234.56);
    expect(formatted).toBe('1.234,56');
  });

  it('should handle plural forms', () => {
    i18next.changeLanguage('en');
    expect(i18next.t('errors.count', { count: 1 })).toContain('error');
    expect(i18next.t('errors.count', { count: 2 })).toContain('errors');
  });
});
```

### 11.2 RTL Testing

```typescript
describe('RTL Support', () => {
  it('should render RTL layout for Arabic', () => {
    i18next.changeLanguage('ar');
    const html = document.documentElement;
    expect(html.dir).toBe('rtl');
    expect(html.lang).toBe('ar');
  });

  it('should not overflow text in RTL', () => {
    // Render component with Arabic text
    // Measure max-width to ensure no overflow
  });

  it('should flip layout-critical margins/padding', () => {
    // CSS should use margin-inline-start, not margin-left
  });
});
```

---

## Part 12: Quick Reference: Hardcoded Strings Summary

### By File and Count

| File | Count | Type | Status |
|------|-------|------|--------|
| `web/designer.js` | 50+ | Component labels | 🔴 Critical |
| `web/validation.js` | 100+ | Error messages | 🔴 Critical |
| `web/error_ui.js` | 30+ | UI labels | 🔴 Critical |
| `services/error_system.py` | 40+ | Error messages | 🔴 Critical |
| `services/onboarding_manager.py` | 20+ | Template data | 🔴 Critical |
| `web/src/types/editor.ts` | 30+ | Property labels | 🔴 Critical |
| `web/error_styles.css` | 10+ | Text content | 🟠 High |
| Various test files | 20+ | Test data | 🟡 Medium |
| **TOTAL** | **~300** | Mixed | **CRITICAL** |

---

## Part 13: Recommendations & Prioritization

### 13.1 Must-Do Before Global Release

1. 🔴 **Implement i18n Framework** (i18next recommended)
2. 🔴 **Extract All Hardcoded Strings**
3. 🔴 **Add Regional Formatting** (Intl API)
4. 🔴 **Implement RTL Support**
5. 🔴 **Translate to Spanish/Chinese** (largest markets)
6. 🔴 **Create Translation Workflow**
7. 🔴 **Add i18n Tests**

### 13.2 Should-Do in Phase 2

1. 🟠 **Translate to 5+ More Languages**
2. 🟠 **Cultural Compliance Review**
3. 🟠 **Locale-Specific Testing**
4. 🟠 **Font & Text Rendering Optimization**
5. 🟠 **Right-to-Left Complete Testing**

### 13.3 Nice-to-Have

1. 🟡 **User Locale Preferences**
2. 🟡 **Contextual Help in User Language**
3. 🟡 **Professional Translation Memory**
4. 🟡 **Language-Specific Error Recovery**

---

## Part 14: Conclusion

### Summary Table

| Aspect | Status | Grade | Impact |
|--------|--------|-------|--------|
| **Hardcoded Strings** | ❌ None extracted | F | 🔴 CRITICAL |
| **i18n Framework** | ❌ None installed | F | 🔴 CRITICAL |
| **Regional Formatting** | ❌ No support | F | 🔴 CRITICAL |
| **RTL Languages** | ❌ Unsupported | F | 🔴 CRITICAL |
| **Translation Workflow** | ❌ None exists | F | 🔴 CRITICAL |
| **Testing** | ❌ No i18n tests | F | 🟠 HIGH |
| **Documentation** | ❌ None exists | F | 🟠 HIGH |

### Overall i18n Readiness Score

**Grade**: C+ (4.5/10) - MAJOR WORK REQUIRED

**Blockers for Global Release**:
- ✗ Cannot serve non-English users
- ✗ Dates/numbers format incorrectly
- ✗ RTL languages completely broken
- ✗ No translation infrastructure

### Effort Estimate

| Phase | Duration | Priority |
|-------|----------|----------|
| Infrastructure | 2-3 weeks | 🔴 CRITICAL |
| String Extraction | 1-2 weeks | 🔴 CRITICAL |
| Regional Formatting | 1 week | 🔴 CRITICAL |
| Translation Workflow | 1-2 weeks | 🔴 CRITICAL |
| **Total Minimum** | **5-8 weeks** | **BLOCKING** |

### Recommendation

**DO NOT RELEASE** to international markets without completing Phase 1 & 2 of the i18n roadmap. The lack of translation infrastructure and regional formatting support will result in:
- User confusion (dates, numbers)
- Accessibility issues (RTL languages unusable)
- Professional appearance damage
- Regulatory compliance issues (some countries)

---

## Appendix A: Sample Translation JSON Files

### Common Translations
```json
{
  "app": {
    "title": "Anki Template Designer",
    "description": "Create beautiful Anki card templates without coding",
    "version": "1.0.0"
  },
  "buttons": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit",
    "add": "Add",
    "close": "Close",
    "back": "Back",
    "next": "Next"
  },
  "messages": {
    "success": "Success!",
    "error": "An error occurred",
    "warning": "Warning",
    "info": "Information",
    "loading": "Loading...",
    "saving": "Saving...",
    "deleting": "Deleting..."
  }
}
```

---

## Appendix B: i18n Libraries Comparison

| Library | Pros | Cons | Recommendation |
|---------|------|------|-----------------|
| **i18next** | Mature, flexible, plugins, large community | Learning curve | ✅ RECOMMENDED |
| **react-intl** | Built for React, FormattedMessage | React-only | Good for React components |
| **Vue I18n** | Built for Vue | Vue-only | Good for Vue components |
| **gettext** | Industry standard, simple | Lacks features | Legacy systems |
| **Fluent** | Modern, powerful | Newer, smaller community | Future-proof |

---

**Report Completed**: January 21, 2026  
**Next Action**: Implement Phase 1 Infrastructure  
**Status**: READY FOR DEVELOPMENT
