# Phase 3: Translation Key Mapping

**Date**: January 21, 2026  
**Status**: ✅ Complete  
**Purpose**: Document all translation keys used by converted files

---

## Error Message Keys (error_ui.js, validation.js)

### Error Panel Keys (error_ui.js)
```javascript
error.panel.title         // "No errors"
error.panel.minimize      // "Minimize"
error.panel.close         // "Close"
error.panel.recovery      // "Recovery Options"
error.panel.apply         // "Apply Suggestion"
error.panel.details       // "Details"
error.panel.resolved      // "Mark Resolved"
```

### Error History Keys (error_ui.js)
```javascript
error.history.title           // "Error History"
error.history.allSeverities   // "All Severities"
error.history.info            // "Info"
error.history.warning         // "Warning"
error.history.error           // "Error"
error.history.critical        // "Critical"
error.history.clear           // "Clear"
```

### Error Message Keys (validation.js)
**Rule IDs** used in `getUserFriendlyErrorMessage()`:
```
html-1, html-2, html-3, html-4
anki-1, anki-2, anki-3
css-1, css-2
perf-1, perf-2
a11y-1, a11y-2, a11y-3
default
```

### Error Suggestions Keys (validation.js)
**Same rule IDs as above** used in `getSuggestionsForError()`

### Error Context Keys (validation.js)
```
anki-1, anki-2, anki-3
html-1, html-2
css-1
```

### Error Severity Keys (error_ui.js)
```
info, warning, error, critical
```

### Additional Keys (error_ui.js)
```javascript
error.suggestions.none       // "No recovery options available"
error.suggestions.automatic  // "Automatic"
```

---

## Component Guide Keys (designer.js)

Not explicitly using i18n keys in designer.js - instead uses helper function:
```javascript
window.i18nComponentGuide.getTranslatedComponentGuide()
```

This returns full component definitions with:
- `label` - Component type name
- `category` - Category (Basic, Media, Layout, etc.)
- `description` - Short description
- `help` - Longer help text
- `examples` - Array of example uses
- `moreLink` - Link to documentation

**Components Supported**: 16
```
text, field, image, video, audio
container, row, column
cloze, hint, conditional
button, link
badge, alert, separator
```

---

## Current Translation Coverage

### File: public/locales/en/errors.json
Expected keys:
```json
{
  "html-1": "Your template needs a container element...",
  "html-2": "Some HTML tags aren't properly closed...",
  ... (20+ keys)
  "error": { "panel": {...}, "history": {...}, "suggestions": {...} }
}
```

### File: public/locales/es/errors.json  
Spanish translations of all above keys

### File: public/locales/en/components.json
Expected keys for all 16 components with:
```json
{
  "text": {
    "label": "Text",
    "category": "Basic",
    "description": "...",
    "help": "...",
    "examples": [...],
    "moreLink": "..."
  }
  ... (15 more components)
}
```

### File: public/locales/es/components.json
Spanish translations of all 16 components

---

## Integration Map

### designer.js → i18nComponentGuide
```
getComponentGuide()
  └─ window.i18nComponentGuide.getTranslatedComponentGuide()
     └─ Returns 16 component definitions with translated labels
```

### validation.js → i18nErrors
```
getUserFriendlyMessage(error)
  └─ window.i18nErrors.getUserFriendlyErrorMessage(ruleId)
     └─ Returns translated error message

getErrorContext(error)
  └─ window.i18nErrors.getErrorContext(ruleId)
     └─ Returns translated context info

getSuggestionsForError(ruleId)
  └─ window.i18nErrors.getSuggestionsForError(ruleId)
     └─ Returns array of translated suggestions
```

### error_ui.js → i18nErrors
```
createErrorPanel()
  └─ window.i18nErrors.t('error.panel.*')
     └─ Returns translated UI strings

createErrorHistory()
  └─ window.i18nErrors.t('error.history.*')
     └─ Returns translated UI strings

displaySuggestions()
  └─ window.i18nErrors.t('error.suggestions.*')
     └─ Returns translated suggestion text
```

---

## Fallback Strategy

Each method contains fallback English text:

### designer.js
```javascript
if (typeof window.i18nComponentGuide !== 'undefined') {
  return window.i18nComponentGuide.getTranslatedComponentGuide();
}
// Fallback: 16 component definitions in English
return { text: {...}, field: {...}, ... };
```

### validation.js
```javascript
if (typeof window.i18nErrors !== 'undefined') {
  return window.i18nErrors.getUserFriendlyErrorMessage(error.ruleId);
}
// Fallback: messageMap with 20+ English messages
const messageMap = { 'html-1': '...', ... };
return messageMap[error.ruleId] || messageMap['default'];
```

### error_ui.js
```javascript
const t = (key) => {
  if (typeof window.i18nErrors !== 'undefined') {
    return window.i18nErrors.t(key);
  }
  // Fallback: English translations map
  const translations = { 'error.panel.title': 'No errors', ... };
  return translations[key] || key;
};
```

---

## Adding New Translations

### To add a new error message:

1. **Add to error_ui.js or validation.js fallback**:
```javascript
const messageMap = {
  'new-error-id': 'Your new error message'
};
```

2. **Add to translation files**:
```javascript
// public/locales/en/errors.json
{ "new-error-id": "Your new error message" }

// public/locales/es/errors.json
{ "new-error-id": "Tu nuevo mensaje de error" }
```

3. **Use in code**:
```javascript
const message = this.getUserFriendlyMessage({ ruleId: 'new-error-id' });
```

### To add new component:

1. **Add to designer.js getComponentGuide() fallback**:
```javascript
'my-component': {
  label: 'My Component',
  category: 'Custom',
  description: '...',
  help: '...',
  examples: [...],
  moreLink: '...'
}
```

2. **Add to translation files**:
```javascript
// public/locales/en/components.json
{ "my-component": {...} }

// public/locales/es/components.json
{ "my-component": {...} }
```

---

## Testing Translation Keys

### In Browser Console

```javascript
// Test component guide
window.i18nComponentGuide.getTranslatedComponentGuide()
// Should return 16 components with translated labels

// Test error messages
window.i18nErrors.getUserFriendlyErrorMessage('html-1')
// Should return translated error message

// Test panel text
window.i18nErrors.t('error.panel.title')
// Should return translated panel title

// Check current language
window.i18nBridge.getCurrentLanguage()
// Should return 'en' or 'es'

// Test language switch
window.i18nBridge.changeLanguage('es')
// Translations should update
```

---

## Translation File Structure

### English Namespace: errors
Location: `public/locales/en/errors.json`
Keys: 40+ error-related strings

### Spanish Namespace: errors
Location: `public/locales/es/errors.json`
Keys: 40+ error-related strings (translated)

### English Namespace: components
Location: `public/locales/en/components.json`
Keys: 16 component definitions × 5 properties = 80+ keys

### Spanish Namespace: components
Location: `public/locales/es/components.json`
Keys: 16 component definitions × 5 properties = 80+ keys (translated)

---

## Key Naming Convention

### Error Panel Keys
Prefix: `error.panel.*`
- `error.panel.title` - Header text
- `error.panel.minimize` - Button tooltip
- `error.panel.close` - Button tooltip
- `error.panel.recovery` - Section header
- `error.panel.apply` - Button label
- `error.panel.details` - Button label
- `error.panel.resolved` - Button label

### Error History Keys
Prefix: `error.history.*`
- `error.history.title` - Panel header
- `error.history.allSeverities` - Filter option
- `error.history.info` - Severity level
- `error.history.warning` - Severity level
- `error.history.error` - Severity level
- `error.history.critical` - Severity level
- `error.history.clear` - Button label

### Error Message Keys
Format: `{category}-{number}`
- `html-1`, `html-2`, `html-3`, `html-4` - HTML structure errors
- `anki-1`, `anki-2`, `anki-3` - Anki field errors
- `css-1`, `css-2` - CSS errors
- `perf-1`, `perf-2` - Performance warnings
- `a11y-1`, `a11y-2`, `a11y-3` - Accessibility warnings
- `default` - Generic fallback

### Suggestion Keys
Prefix: `error.suggestions.*`
- `error.suggestions.none` - No suggestions available
- `error.suggestions.automatic` - Auto-fix badge

---

## Verification Checklist

After implementing Phase 3:

- [ ] All error.panel.* keys exist in translation files
- [ ] All error.history.* keys exist in translation files
- [ ] All error rule IDs (html-1, anki-1, etc.) in translation files
- [ ] All error.suggestions.* keys in translation files
- [ ] All 16 component definitions in components.json
- [ ] Spanish translations exist for all keys
- [ ] Fallback text in designer.js matches English files
- [ ] Fallback text in validation.js matches English files
- [ ] Fallback text in error_ui.js matches English files
- [ ] No console errors when switching language

---

## Summary

**Total Translation Keys**: 80+
**Files Modified**: 3
**Supported Languages**: 2 (EN, ES) + framework for 6 more
**Fallback Strategy**: ✅ In place
**Status**: ✅ Complete and ready for testing

---

Last Updated: January 21, 2026  
Status: Phase 3 Complete ✅
