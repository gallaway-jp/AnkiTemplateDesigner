# Phase 4B: Language Switching Tests - Status & Instructions

**Date**: January 21, 2026  
**Status**: ✅ DEV SERVER RUNNING - READY FOR TESTING  
**Dev Server**: http://localhost:5173/  
**Test Page**: http://localhost:5173/i18n-verification.html  

---

## 🎉 Success! Dev Server is Running

### Current Status
✅ Node.js v24.13.0 installed successfully  
✅ npm dependencies installed  
✅ Vite dev server started on port 5173  
✅ i18n-verification.html accessible  
✅ Ready for Phase 4B language switching tests  

---

## What to Test in Phase 4B

### Test Objective
Verify that language switching works correctly and all UI text translates dynamically from English to Spanish and back.

### What Should Work
1. ✅ Language switcher appears in the header
2. ✅ Can click to switch between English and Spanish
3. ✅ All component labels translate
4. ✅ Error messages translate
5. ✅ UI text in error panels translates
6. ✅ Layout doesn't break when switching languages
7. ✅ No console errors appear

---

## How to Run Tests

### Option 1: Interactive Test Page (Recommended)

1. **Open in your browser**:
   - Visit: `http://localhost:5173/i18n-verification.html`
   - Wait for page to fully load

2. **Click "Run All Tests"** button
   - This will automatically test:
     - Global object existence (i18nBridge, i18nComponentGuide, i18nErrors)
     - Translation function calls
     - Language switching
     - Component guide access

3. **Verify all tests show ✅ green**:
   - If any show ❌ red, there's an issue
   - If any show ⏳ yellow, they're still running

4. **Expected Results**:
   ```
   ✅ i18nBridge exists
   ✅ i18nComponentGuide exists
   ✅ i18nErrors exists
   ✅ Translation function works
   ✅ Component guide works
   ✅ Error messages work
   ✅ Language switching works
   ```

### Option 2: Manual Browser Testing

1. **Open the main app**:
   - Visit: `http://localhost:5173/`
   - Wait for app to load

2. **Look for language switcher**:
   - Should be visible in the header
   - Usually top-right corner

3. **Check current language**:
   - Default should be English
   - Check component labels (should be in English)

4. **Switch to Spanish**:
   - Click language switcher
   - Select "Español"
   - Page should update

5. **Verify translations**:
   - Check that component labels have changed
   - Check that any error messages are in Spanish
   - Check that button labels are in Spanish
   - Check that headings are in Spanish

6. **Switch back to English**:
   - Click language switcher again
   - Select "English"
   - Everything should return to English

7. **Check for errors**:
   - Open browser console (F12)
   - Look for any red error messages
   - There should be no errors

### Option 3: Browser Console Testing

1. **Open browser console**:
   - Press F12 on Windows/Linux
   - Or Cmd+Option+I on Mac

2. **Check global objects**:
   ```javascript
   window.i18nBridge
   window.i18nComponentGuide
   window.i18nErrors
   window.COMPONENT_GUIDE
   ```
   - All should return objects
   - None should be undefined

3. **Test translation function**:
   ```javascript
   window.i18nBridge.t('common:appTitle')
   ```
   - Should return translated string

4. **Get current language**:
   ```javascript
   window.i18nBridge.getLanguage()
   ```
   - Should return 'en' or 'es' (or other language code)

5. **Switch language**:
   ```javascript
   window.i18nBridge.changeLanguage('es')
   ```
   - Page should update to Spanish
   - Verify by checking displayed text

6. **Switch back**:
   ```javascript
   window.i18nBridge.changeLanguage('en')
   ```
   - Page should update to English

7. **Test component guide**:
   ```javascript
   window.COMPONENT_GUIDE['text']
   ```
   - Should return object with component information
   - After changing language to Spanish, labels should be different

8. **Test error messages**:
   ```javascript
   window.i18nErrors.getUserFriendlyErrorMessage('html-1')
   ```
   - Should return error message
   - After changing language, message should be different

---

## Expected Behavior

### When Language is English
- Component labels: "Text", "Field", "Image", etc.
- Error messages: "Invalid HTML structure", etc.
- Buttons: "Save", "Cancel", "Apply", etc.
- Headers: "Template Designer", etc.

### When Language is Spanish
- Component labels: "Texto", "Campo", "Imagen", etc.
- Error messages: "Estructura HTML inválida", etc.
- Buttons: "Guardar", "Cancelar", "Aplicar", etc.
- Headers: "Diseñador de Plantillas", etc.

### Layout & Style
- No layout shifts
- No text overflow
- Proper spacing maintained
- Icons/images unchanged
- Colors unchanged

### Performance
- Language switch completes in <100ms
- No lag or freezing
- No missing text
- No broken styling

---

## Troubleshooting

### Issue: Dev server shows error
**Solution**: 
- Check that Node.js is still in PATH
- Restart the dev server with: `npm run dev`
- Check http://localhost:5173/ in browser

### Issue: i18n-verification.html shows errors
**Solution**:
- Check browser console for specific errors
- Reload page (F5)
- Clear browser cache (Ctrl+Shift+Delete)
- Check that all translation files exist

### Issue: Language switcher not visible
**Solution**:
- Check that LanguageSwitcher component is imported in main app
- Check browser console for errors
- Verify CSS is loading correctly

### Issue: Text doesn't change when switching language
**Solution**:
- Check browser console for "i18next is not initialized" error
- Verify translation files are being loaded
- Check that components are using i18n hooks correctly
- Restart dev server and reload page

### Issue: Console shows 404 for translation files
**Solution**:
- Verify that public/locales/ directory exists
- Check that translation JSON files exist in:
  - public/locales/en/*.json
  - public/locales/es/*.json
- Restart dev server

### Issue: Some text doesn't translate
**Solution**:
- This is expected for certain parts (brand names, etc.)
- Check translation keys in:
  - public/locales/es/common.json
  - public/locales/es/components.json
  - public/locales/es/errors.json
- Verify keys are correctly mapped

---

## Sign-Off Checklist

After testing, verify all items:

- [ ] **Translation Files Loaded**
  - English translations loaded
  - Spanish translations loaded
  - No 404 errors in console

- [ ] **Global Objects Available**
  - window.i18nBridge exists and has methods
  - window.i18nComponentGuide exists and has methods
  - window.i18nErrors exists and has methods
  - window.COMPONENT_GUIDE works as property getter

- [ ] **Language Switching Works**
  - Can switch from English to Spanish
  - Can switch from Spanish to English
  - Page updates within 100ms

- [ ] **Text Translations Verified**
  - Component labels translate correctly
  - Error messages translate correctly
  - Button text translates correctly
  - Headers/titles translate correctly

- [ ] **UI Integrity Maintained**
  - No layout breaks
  - No text overflow
  - Proper spacing preserved
  - No visual glitches

- [ ] **No Console Errors**
  - No red error messages in console
  - No 404 errors for resources
  - No undefined variable errors
  - No i18n initialization errors

- [ ] **Performance Acceptable**
  - Language switch completes quickly (<100ms)
  - No lag or freezing
  - Page remains responsive
  - No memory leaks visible

---

## Test Results Template

### Test Execution Date: [DATE]
### Tested By: [YOUR NAME]
### Browser: [BROWSER NAME & VERSION]
### OS: [OPERATING SYSTEM]

#### Global Objects
- [ ] window.i18nBridge exists ✅/❌
- [ ] window.i18nComponentGuide exists ✅/❌
- [ ] window.i18nErrors exists ✅/❌
- [ ] window.COMPONENT_GUIDE is a property getter ✅/❌

#### Language Switching
- [ ] English to Spanish switch works ✅/❌
- [ ] Spanish to English switch works ✅/❌
- [ ] Switch completes in <100ms ✅/❌
- [ ] Page visibly updates after switch ✅/❌

#### Text Translation
- [ ] Component labels translate ✅/❌
- [ ] Error messages translate ✅/❌
- [ ] Button text translates ✅/❌
- [ ] Headers/titles translate ✅/❌

#### UI & Performance
- [ ] No layout breaks on language switch ✅/❌
- [ ] No text overflow issues ✅/❌
- [ ] No console errors ✅/❌
- [ ] Language switch is smooth and responsive ✅/❌

#### Summary
**Result**: PASS ✅ / FAIL ❌

**Issues Found**: [List any issues]

**Notes**: [Any additional observations]

---

## Next Steps After Phase 4B

### If All Tests Pass ✅
1. Proceed to Phase 4C: Browser Compatibility Testing
   - Test in Chrome, Firefox, Safari, Edge
   - Verify same results in all browsers

2. Proceed to Phase 4D: Performance Verification
   - Measure translation lookup time
   - Measure language switch time
   - Monitor memory usage

3. Proceed to Phase 4E: Production QA
   - Document all test results
   - Create sign-off report
   - Plan deployment

### If Tests Fail ❌
1. Check console for specific errors
2. Review translation file paths
3. Verify i18n initialization
4. Check component imports
5. Restart dev server and retry

---

## Resources Available

- **Verification Page**: http://localhost:5173/i18n-verification.html
- **Main App**: http://localhost:5173/
- **Dev Server Logs**: Check terminal running npm run dev
- **Translation Files**: web/public/locales/
- **i18n Config**: web/src/i18n/config.ts
- **Vanilla JS Bridge**: web/src/i18n/vanilla-js-bridge.js
- **Component Guide Helper**: web/src/i18n/component-guide-i18n.js
- **Error Messages Helper**: web/src/i18n/error-messages-i18n.js

---

## How the i18n System Works

### Architecture
1. **Frontend**: React app loads on http://localhost:5173/
2. **i18next**: Framework initializes on app load
3. **Translation Files**: Loaded from public/locales/
4. **Global Bridges**: Available at window.i18nBridge, window.i18nComponentGuide, window.i18nErrors
5. **Vanilla JS**: designer.js, validation.js, error_ui.js use global bridges

### Language Detection
- First checks localStorage (saved language preference)
- Then checks browser language
- Then checks URL parameters
- Defaults to English if no preference found

### Dynamic Translation
- Component labels translate via property getter
- Error messages translate via conditional i18n checks
- UI text translates via inline helpers
- All with English fallback

### Language Switching
- Click language switcher in header
- Calls window.i18nBridge.changeLanguage()
- i18next updates all translations
- React components re-render with new text
- Vanilla JS code uses new translation keys

---

## Success Metrics

| Metric | Expected | How to Verify |
|--------|----------|---------------|
| Page Loads | <2 seconds | Check browser timing |
| Translations Load | <100ms after page load | Check Network tab |
| Language Switch | <100ms | Time from click to visible change |
| No Errors | 0 console errors | Check F12 console |
| All Text Translates | 100% | Manually check all visible text |
| UI Integrity | No breaks | Check layout stays consistent |
| Browser Support | All modern browsers | Test in multiple browsers |

---

## Dev Server Management

### To Restart Dev Server
If needed, run in the web directory:
```bash
npm run dev
```

### To Stop Dev Server
- In the terminal running the server, press Ctrl+C
- Or close the terminal window

### To Access Dev Server
- Local: http://localhost:5173/
- Mobile/Network: Replace localhost with your computer's IP

### Dev Server Features
- Hot module reloading (changes appear instantly)
- Console logs visible in terminal
- Errors shown in console overlay
- Source maps for debugging

---

## Questions or Issues?

If you encounter problems:
1. Check the troubleshooting section above
2. Review the browser console (F12) for specific errors
3. Check if dev server is still running
4. Try restarting the dev server
5. Clear browser cache and reload

---

## Status Summary

✅ **Node.js**: Installed (v24.13.0)  
✅ **npm**: Dependencies installed  
✅ **Dev Server**: Running on port 5173  
✅ **Translation Files**: All present and accessible  
✅ **i18n Config**: Fixed and working  
✅ **Verification Page**: Ready at http://localhost:5173/i18n-verification.html  

**Phase 4B Ready**: YES ✅  
**Next Action**: Open browser to http://localhost:5173/i18n-verification.html and run tests  
**Time Estimate**: 30 minutes for complete testing  

---

**Last Updated**: January 21, 2026  
**Session**: Node.js installation and dev server startup  
**Next Phase**: Phase 4C - Browser Compatibility Testing (after Phase 4B passes)  
