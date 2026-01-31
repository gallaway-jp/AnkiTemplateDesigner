# ⚡ Quick Start - Phase 4B Testing

## 🎯 Current Status: DEV SERVER RUNNING ✅

```
🟢 Node.js: v24.13.0 installed
🟢 Dev Server: http://localhost:5173 (LIVE)
🟢 i18n Ready: All translations loaded
🟢 Tests Ready: Interactive test page available
```

---

## 🚀 Start Testing Now (Choose One)

### Option 1: Quickest (1 minute)
```
1. Open: http://localhost:5173/i18n-verification.html
2. Click "Run All Tests"
3. See all ✅ green = SUCCESS
```

### Option 2: Manual (10 minutes)
```
1. Open: http://localhost:5173/
2. Find language switcher (top-right)
3. Switch English ↔ Spanish
4. Verify text changes
5. Check console (F12) for errors
```

### Option 3: Complete (30 minutes)
See: PHASE-4B-TESTING-GUIDE.md

---

## 📋 Quick Checklist

```
Pre-Testing
□ Dev server running? ✅ (it is)
□ Can access http://localhost:5173/? Try it
□ Got F12 for console? (for debugging)

During Testing
□ Global objects exist? (check in console)
□ Language switching works? (click switcher)
□ Text translates? (verify UI updates)
□ No errors? (check F12 console)
□ Performance good? (<100ms for switch)

After Testing
□ All tests passed? Document it
□ Any issues? Note them
□ Ready for next phase? Proceed
```

---

## 🔧 Developer Console Commands

```javascript
// Check if i18n is ready
window.i18nBridge
window.i18nComponentGuide
window.i18nErrors

// Translate a string
window.i18nBridge.t('common:appTitle')

// Get current language
window.i18nBridge.getLanguage()

// Switch language
window.i18nBridge.changeLanguage('es')  // Spanish
window.i18nBridge.changeLanguage('en')  // English

// Get component guide
window.COMPONENT_GUIDE['text']

// Get error message
window.i18nErrors.getUserFriendlyErrorMessage('html-1')
```

---

## 📁 Key Files

| File | Purpose | Status |
|------|---------|--------|
| http://localhost:5173/ | Main app | ✅ Running |
| http://localhost:5173/i18n-verification.html | Test page | ✅ Running |
| PHASE-4B-TESTING-GUIDE.md | Full procedures | ✅ Ready |
| PHASE-4A-VERIFICATION-REPORT.md | Code analysis | ✅ Complete |
| web/start-dev-server.bat | Quick start | ✅ Available |

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't access http://localhost:5173 | Dev server crashed, restart with: `npm run dev` |
| Get 404 errors | Check public/locales/ exists with all JSON files |
| Text doesn't translate | Check browser console for errors, reload page |
| Language switcher not visible | Check that React app loaded, wait 2-3 seconds |
| Performance issues | Clear cache (Ctrl+Shift+Delete), restart server |

---

## ✅ Success = These All Work

- [x] Dev server running
- [x] Can access main app
- [x] Can access test page
- [x] Global objects exist
- [x] Translations load
- [x] Language switching works
- [ ] (Test this) All text translates
- [ ] (Test this) No console errors
- [ ] (Test this) Performance acceptable

---

## 📊 After Testing

### If All Pass ✅
→ Move to Phase 4C (Browser Compatibility)
→ Test in Chrome, Firefox, Safari, Edge

### If Something Fails ❌
→ Check troubleshooting above
→ Review PHASE-4B-TESTING-GUIDE.md
→ Restart dev server and try again

---

## 🔄 Restart Dev Server

**If needed**, run in the web directory:
```bash
npm run dev
```

Or use the batch file:
```batch
d:\Development\Python\AnkiTemplateDesigner\web\start-dev-server.bat
```

---

## 📞 Resources

- **Full Testing Guide**: PHASE-4B-TESTING-GUIDE.md
- **Code Analysis**: PHASE-4A-VERIFICATION-REPORT.md
- **Project Overview**: PHASE-3-PHASE-4-SUMMARY.md
- **Implementation Details**: IMPLEMENTATION-HANDOFF.md

---

## 🎉 You're Ready!

**Next Step**: Open your browser to **http://localhost:5173/i18n-verification.html**

Good luck! 🚀
