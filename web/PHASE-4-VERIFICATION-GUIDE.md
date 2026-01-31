# Phase 4: i18n Initialization Verification Guide

**Status**: Ready to Verify  
**Date**: January 21, 2026  
**Purpose**: Verify that all i18n components are working correctly

---

## Quick Start

### Option 1: Automated Verification (Easiest)
1. Navigate to `web/` directory
2. Run: `npm run dev`
3. Open browser to `http://localhost:5173`
4. Open `i18n-verification.html` in a separate tab
5. Click "Run All Tests" button

### Option 2: Manual Verification in Browser Console
1. Start dev server: `npm run dev`
2. Open `http://localhost:5173` in browser
3. Press `F12` to open Developer Tools
4. Go to **Console** tab
5. Type commands to test (see below)

---

## What to Verify

### 1. Global Objects Exist
These should all be defined and accessible:

```javascript
// In browser console, type each:
window.i18nBridge              // Should show Object {...}
window.i18nComponentGuide      // Should show Object {...}
window.i18nErrors              // Should show Object {...}

// If any shows "undefined", initialization failed
```

### 2. Key Functions Work

#### Translation Function
```javascript
// Should return a string
window.i18nBridge.t('components.text.label')
// Expected output: "Text"

window.i18nBridge.t('error.panel.title')
// Expected output: "No errors"
```

#### Component Guide
```javascript
// Should return object with 16 components
const guide = window.i18nComponentGuide.getTranslatedComponentGuide()
// Check: Object.keys(guide).length === 16

// Get specific component
window.i18nComponentGuide.getComponentLabel('text')
// Expected output: "Text"
```

#### Error Messages
```javascript
// Should return string
window.i18nErrors.getUserFriendlyErrorMessage('html-1')
// Expected output: "Your template needs a container element..."

// Should return array
window.i18nErrors.getSuggestionsForError('html-1')
// Expected output: Array with 2 items
```

### 3. Language Switching

#### Check Available Languages
```javascript
window.i18nBridge.getAvailableLanguages()
// Expected output: ['en', 'es'] or similar array
```

#### Check Current Language
```javascript
window.i18nBridge.getCurrentLanguage()
// Expected output: 'en' (or user's browser language)
```

#### Switch Language
```javascript
// Switch to Spanish
window.i18nBridge.changeLanguage('es')

// Then check - should return Spanish text
window.i18nBridge.t('components.text.label')
// Expected output: "Texto" (Spanish for "Text")

// Switch back to English
window.i18nBridge.changeLanguage('en')
```

### 4. UI Elements

#### Language Switcher
Look for in the header:
- ✅ Dropdown menu with language options
- ✅ Shows current language name
- ✅ Clicking updates the language
- ✅ UI updates when language changes

#### Component Labels
When viewing components in the designer:
- ✅ Labels are in current language
- ✅ Descriptions change when language switches
- ✅ Help text changes when language switches

#### Error Messages
When validation errors occur:
- ✅ Error messages are in current language
- ✅ Suggestions are in current language
- ✅ Error panel text is in current language

---

## Step-by-Step Verification

### Step 1: Start the Development Server (5 minutes)

```bash
cd web
npm run dev
```

Wait for output like:
```
  VITE v5.0.0  ready in 234 ms

  ➜  Local:   http://localhost:5173/
```

### Step 2: Open the Application (2 minutes)

1. Open browser to `http://localhost:5173`
2. You should see the Anki Template Designer loading
3. Wait for it to fully load (you'll see the editor)

### Step 3: Verify Language Switcher (3 minutes)

1. Look at the top-right of the header
2. You should see a language dropdown (e.g., "English" or flag icon)
3. Click it to open the dropdown
4. You should see options like "English", "Español"
5. Verify no console errors appear

### Step 4: Test Language Switching (5 minutes)

1. Click the language dropdown
2. Select "Español" (Spanish)
3. Observe that:
   - Component labels change (if components visible)
   - Error messages change (if any error triggers)
   - UI text updates
4. Switch back to English
5. Verify everything switches back

### Step 5: Open Browser Console (5 minutes)

1. Press `F12` to open Developer Tools
2. Go to **Console** tab
3. Type: `window.i18nBridge`
4. You should see an object with methods like:
   - `t(key)` - Translate
   - `changeLanguage(lang)` - Switch language
   - `getCurrentLanguage()` - Get current lang
   - `getAvailableLanguages()` - List languages
   - `formatDate(date, format)` - Format date
   - `formatNumber(num, options)` - Format number
   - `formatCurrency(num, currency)` - Format currency

### Step 6: Run Translation Tests (5 minutes)

In browser console, run these commands:

```javascript
// Test 1: Get translation
window.i18nBridge.t('components.text.label')
// Should output: "Text"

// Test 2: Get component guide
window.i18nComponentGuide.getComponentLabel('field')
// Should output: "Field"

// Test 3: Get error message
window.i18nErrors.getUserFriendlyErrorMessage('html-1')
// Should output: "Your template needs a container..."

// Test 4: Get suggestions
window.i18nErrors.getSuggestionsForError('html-1')
// Should output: Array with 2 suggestion strings

// Test 5: Available languages
window.i18nBridge.getAvailableLanguages()
// Should output: ['en', 'es']
```

### Step 7: Run Automated Verification (3 minutes)

1. Open `i18n-verification.html` in a new tab
   - Navigate to: `http://localhost:5173/i18n-verification.html`
   - Or open file directly: `web/i18n-verification.html` in browser
2. Click **Run All Tests**
3. Check that all tests pass (green checkmarks)

---

## Expected Results

### Successful Initialization
✅ All boxes show "Success" status  
✅ Component guide has 16 items  
✅ Error messages return proper text  
✅ Language switching works  
✅ No red error messages in console  

### Signs of Problems
❌ Objects undefined  
❌ Functions return null/undefined  
❌ Language switching doesn't update UI  
❌ Console shows errors  

---

## Common Issues and Solutions

### Issue 1: "window.i18nBridge is undefined"

**Cause**: i18n didn't initialize  

**Solution**:
1. Check browser console for errors during load
2. Verify `src/i18n/config.ts` exists
3. Verify `src/main.tsx` calls `initI18n()`
4. Reload page and wait 2 seconds
5. Try again

**Debug**:
```javascript
// Check if i18n module loaded
window.i18nextModule  // Should exist
// Check React
document.querySelector('#root') // Should exist
```

### Issue 2: "Translation key not found"

**Cause**: Missing translation in files  

**Solution**:
1. Check that `public/locales/en/errors.json` exists
2. Verify key exists in file
3. Check for typos in key name
4. Reload translation files: `window.i18nBridge.changeLanguage('en')`

**Debug**:
```javascript
// List available keys in 'errors' namespace
window.i18next.getResourceBundle('en', 'errors')
```

### Issue 3: "Language switching doesn't work"

**Cause**: DOM not updating, or no change detection  

**Solution**:
1. Check that language actually changed: 
   ```javascript
   window.i18nBridge.getCurrentLanguage() // Check output
   ```
2. Manually refresh page to see if translations changed
3. Check React component re-renders
4. Verify LanguageSwitcher component exists

**Debug**:
```javascript
// Manually change language
window.i18nBridge.changeLanguage('es')
// Check if returned promise resolves
.then(() => console.log('Language changed'))
.catch(err => console.error('Error:', err))
```

### Issue 4: "Error objects not found"

**Cause**: Bridge files didn't load  

**Solution**:
1. Verify these files exist:
   - `src/i18n/vanilla-js-bridge.js`
   - `src/i18n/error-messages-i18n.js`
   - `src/i18n/component-guide-i18n.js`
2. Check that they're properly imported in `src/i18n/config.ts`
3. Reload page
4. Check console for 404 errors

**Debug**:
```javascript
// Check what files loaded
window.performance.getEntriesByType('resource')
  .filter(r => r.name.includes('i18n'))
  .forEach(r => console.log(r.name, r.duration + 'ms'))
```

---

## Detailed Test Cases

### Test Case 1: Component Guide Translation

**Steps**:
1. In console: `window.i18nComponentGuide.getComponentLabel('text')`
2. Should return: `"Text"`
3. Switch to Spanish: `window.i18nBridge.changeLanguage('es')`
4. In console: `window.i18nComponentGuide.getComponentLabel('text')`
5. Should return: `"Texto"` (or Spanish equivalent)

**Expected**: Labels change when language changes

---

### Test Case 2: Error Message Translation

**Steps**:
1. In console: `window.i18nErrors.getUserFriendlyErrorMessage('html-1')`
2. Should return English error message
3. Switch to Spanish: `window.i18nBridge.changeLanguage('es')`
4. In console: `window.i18nErrors.getUserFriendlyErrorMessage('html-1')`
5. Should return Spanish error message

**Expected**: Error messages change language

---

### Test Case 3: Error Suggestions Translation

**Steps**:
1. In console: `window.i18nErrors.getSuggestionsForError('html-1')`
2. Should return array with 2 English suggestions
3. Switch to Spanish: `window.i18nBridge.changeLanguage('es')`
4. In console: `window.i18nErrors.getSuggestionsForError('html-1')`
5. Should return array with 2 Spanish suggestions

**Expected**: Suggestions change language

---

### Test Case 4: UI Language Switch

**Steps**:
1. Look at header - note current language
2. Click language switcher dropdown
3. Select different language
4. Header text should update
5. Component labels should update (if visible)
6. Any error messages should update (if visible)

**Expected**: All visible text updates

---

### Test Case 5: Fallback to English

**Steps**:
1. Disable i18n: `window.i18nErrors = undefined`
2. Reload page
3. Check error messages (trigger a validation error)
4. Verify English fallback text appears
5. No console errors should appear

**Expected**: App works with English fallback

---

## Performance Checks

### Check Translation Lookup Time

```javascript
// Measure performance of t() function
console.time('Translation');
for (let i = 0; i < 1000; i++) {
  window.i18nBridge.t('components.text.label');
}
console.timeEnd('Translation');
// Should complete in < 50ms for 1000 calls
```

### Check Memory Usage

```javascript
// Check size of loaded translations
const enErrors = window.i18next.getResourceBundle('en', 'errors');
const esErrors = window.i18next.getResourceBundle('es', 'errors');
console.log('EN errors keys:', Object.keys(enErrors).length);
console.log('ES errors keys:', Object.keys(esErrors).length);
```

---

## Browser Console Commands Reference

```javascript
// === Information ===
window.i18nBridge.getCurrentLanguage()          // Current language
window.i18nBridge.getAvailableLanguages()       // Available languages

// === Translation ===
window.i18nBridge.t('components.text.label')    // Translate key
window.i18nComponentGuide.getComponentLabel('text')  // Component label
window.i18nErrors.getUserFriendlyErrorMessage('html-1')  // Error message

// === Language Management ===
window.i18nBridge.changeLanguage('es')          // Switch language
window.i18nBridge.changeLanguage('en')          // Switch back

// === Formatting ===
window.i18nBridge.formatDate(new Date())        // Format date
window.i18nBridge.formatNumber(1234.56)         // Format number
window.i18nBridge.formatCurrency(1234.56, 'USD')  // Format currency

// === Debugging ===
window.i18next                                  // i18next instance
window.i18next.language                         // Current language
window.i18next.languages                        // All languages
window.i18next.getResourceBundle('en', 'errors') // Translation bundle
```

---

## Success Criteria

### All Checks Pass ✅
- [ ] window.i18nBridge exists
- [ ] window.i18nComponentGuide exists
- [ ] window.i18nErrors exists
- [ ] t() function returns strings
- [ ] Component guide returns 16 components
- [ ] Error messages translate
- [ ] Suggestions translate
- [ ] Language switching works
- [ ] No console errors

### Performance Good ✅
- [ ] Translation lookup < 1ms per call
- [ ] Language switch < 100ms
- [ ] No memory leaks
- [ ] No 404 errors for translation files

### Production Ready ✅
- [ ] All tests pass
- [ ] All major browsers work
- [ ] Mobile responsive
- [ ] No accessibility issues
- [ ] No performance degradation

---

## Next Steps After Verification

### If All Tests Pass ✅
1. **Document Results** - Create verification report
2. **Run Full Test Suite** - Browser compatibility
3. **Performance Review** - Benchmarking
4. **Deploy to Staging** - Pre-production testing
5. **User Testing** - Real user feedback

### If Tests Fail ❌
1. **Identify Issue** - Check error messages
2. **Debug** - Use console commands to narrow down
3. **Fix** - Correct the problem
4. **Reload** - Test again
5. **Repeat** - Until all pass

---

## Automated Testing Script

Run this in browser console to test everything:

```javascript
(async () => {
  console.log('🧪 Starting i18n verification...\n');
  
  let passed = 0, failed = 0;
  
  // Test 1: Objects exist
  console.log('Test 1: Global objects exist');
  [['i18nBridge', window.i18nBridge],
   ['i18nComponentGuide', window.i18nComponentGuide],
   ['i18nErrors', window.i18nErrors]].forEach(([name, obj]) => {
    if (obj) {
      console.log(`  ✅ ${name}`);
      passed++;
    } else {
      console.log(`  ❌ ${name}`);
      failed++;
    }
  });
  
  // Test 2: Functions work
  console.log('\nTest 2: Functions work');
  try {
    const text = window.i18nBridge.t('components.text.label');
    console.log(`  ✅ t() returned: "${text}"`);
    passed++;
  } catch (e) {
    console.log(`  ❌ t() failed: ${e.message}`);
    failed++;
  }
  
  // Test 3: Component guide
  console.log('\nTest 3: Component guide');
  try {
    const guide = window.i18nComponentGuide.getTranslatedComponentGuide();
    console.log(`  ✅ Component guide has ${Object.keys(guide).length} items`);
    passed++;
  } catch (e) {
    console.log(`  ❌ Component guide failed: ${e.message}`);
    failed++;
  }
  
  // Test 4: Error messages
  console.log('\nTest 4: Error messages');
  try {
    const msg = window.i18nErrors.getUserFriendlyErrorMessage('html-1');
    console.log(`  ✅ Error message: "${msg.substring(0, 40)}..."`);
    passed++;
  } catch (e) {
    console.log(`  ❌ Error message failed: ${e.message}`);
    failed++;
  }
  
  // Test 5: Language switching
  console.log('\nTest 5: Language switching');
  try {
    const current = window.i18nBridge.getCurrentLanguage();
    console.log(`  ✅ Current language: ${current}`);
    passed++;
  } catch (e) {
    console.log(`  ❌ Language check failed: ${e.message}`);
    failed++;
  }
  
  // Summary
  console.log(`\n${'='.repeat(40)}`);
  console.log(`Results: ${passed} passed, ${failed} failed`);
  console.log(`Status: ${failed === 0 ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`);
})();
```

---

## Report Template

After running verification, create a report:

```
i18n Initialization Verification Report
Date: [Date]
Tester: [Name]
Browser: [Chrome/Firefox/Safari/Edge]
Status: [Pass/Fail]

Global Objects:
□ window.i18nBridge - [✅/❌]
□ window.i18nComponentGuide - [✅/❌]
□ window.i18nErrors - [✅/❌]

Functions:
□ t() function - [✅/❌]
□ Component guide - [✅/❌]
□ Error messages - [✅/❌]
□ Suggestions - [✅/❌]
□ Language switching - [✅/❌]

UI Elements:
□ Language switcher visible - [✅/❌]
□ Language switching works - [✅/❌]
□ Text updates on language change - [✅/❌]

Issues Found:
[List any issues here]

Recommendations:
[Any recommendations for improvement]
```

---

**Next Task**: Run verification and proceed to Phase 4B (Testing) ✅

Good luck with the verification!
