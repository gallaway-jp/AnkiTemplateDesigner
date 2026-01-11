# Anki Template Constraints & Requirements

> **Purpose**: Document technical constraints and requirements for Anki template generation
> **Date**: January 11, 2026
> **Status**: ✅ VERIFIED - AnkiDroidJS API v0.0.4 validated against source code
> **See Also**: [ANKIJSAPI-VERIFICATION.md](ANKIJSAPI-VERIFICATION.md) for complete API documentation

---

## Overview

This document outlines the technical constraints and requirements for generating Anki-compatible templates from GrapeJS designs. Understanding these constraints is critical for proper template export and compatibility.

---

## 1. Anki Template Environment

### JavaScript Execution Context

**Templates run in a restricted WebView environment**:

- ✅ **Inline JavaScript**: `<script>` tags and inline event handlers work
- ✅ **Standard DOM API**: `document.querySelector`, `addEventListener`, etc.
- ❌ **External JavaScript**: Cannot load external `.js` files via `<script src>`
- ❌ **Network Requests**: No `fetch()`, `XMLHttpRequest`, or external API calls during card display
- ❌ **Modern ES6+ Features**: Limited support (depends on Anki/platform version)

**Supported JavaScript Patterns**:
```html
<!-- ✅ WORKS: Inline script -->
<script>
function showAnswer() {
    document.getElementById('answer').style.display = 'block';
}
</script>

<!-- ✅ WORKS: Inline event handler -->
<button onclick="showAnswer()">Show Answer</button>

<!-- ❌ FAILS: External script -->
<script src="https://cdn.example.com/library.js"></script>

<!-- ❌ FAILS: Network request -->
<script>
fetch('/api/data').then(r => r.json()); // Will fail
</script>
```

### CSS Constraints

**Templates can use CSS in three ways**:

1. ✅ **Note Type CSS**: CSS defined in the note type (global to all cards)
2. ✅ **Inline `<style>` tags**: CSS in the template itself
3. ✅ **Inline styles**: `style` attribute on elements
4. ❌ **External stylesheets**: No `<link rel="stylesheet" href="...">` 

**Supported CSS Patterns**:
```html
<!-- ✅ WORKS: Inline style tag -->
<style>
.card { background: #fff; }
@media (max-width: 768px) {
    .card { padding: 10px; }
}
</style>

<!-- ✅ WORKS: Inline styles -->
<div style="background: #f0f0f0; padding: 16px;">

<!-- ❌ FAILS: External stylesheet -->
<link rel="stylesheet" href="https://cdn.example.com/styles.css">

<!-- ❌ FAILS: @import in style tag -->
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto');
</style>
```

### Asset References

**Media files must be in Anki's media folder**:

- ✅ **Relative paths**: `<img src="image.jpg">` (file must be in media folder)
- ✅ **Anki field syntax**: `<img src="{{Front:Image}}">` (references card field)
- ❌ **External URLs**: `<img src="https://example.com/image.jpg">` (blocked in AnkiDroid, may fail in desktop)
- ❌ **Data URIs**: Limited support, very large data URIs may cause issues

---

## 2. Platform Differences

### Anki Desktop (Windows/Mac/Linux)

- **WebView**: QtWebEngine (Chromium-based)
- **JavaScript**: Modern ES6+ mostly supported
- **CSS**: Full CSS3 support including Grid, Flexbox, animations
- **Media**: Local files from media folder

### AnkiMobile (iOS)

- **WebView**: WKWebView (Safari-based)
- **JavaScript**: ES6+ supported with Safari limitations
- **CSS**: Full CSS3 support
- **Media**: Local files, external resources blocked by default

### AnkiDroid (Android)

- **WebView**: Android System WebView (varies by OS version)
- **JavaScript**: ES6 support varies (Android 5+ = limited, Android 7+ = better)
- **CSS**: CSS3 support varies by Android version
- **Media**: Local files only, strict security policies

**Recommendation**: Target ES5 JavaScript for maximum compatibility across all platforms.

---

## 3. AnkiDroidJS API Integration

### ✅ VERIFIED API Surface

**Source**: AnkiDroid JS API for Desktop v0.0.4 (MIT License)  
**Repository**: https://github.com/infinyte7/AnkiDroid-API-Desktop  
**Verification Date**: January 11, 2026  
**Full Documentation**: See [ANKIJSAPI-VERIFICATION.md](ANKIJSAPI-VERIFICATION.md)

### Required Initialization

**CRITICAL**: The API requires initialization with a developer contract:

```javascript
// Must initialize before using any API methods
const api = AnkiDroidJS.init({
    version: '0.0.3',  // Required: API contract version
    developer: 'your-email@example.com'  // Required: Developer contact
});

// Now API methods are available
await api.ankiShowAnswer();
await api.ankiMarkCard();
```

**Without initialization**: API will throw error: `"AnkiDroidJS: Developer contact required in contract"`

### Verified API Methods (56 total)

#### Card Information (20 methods)
```javascript
await api.ankiGetNewCardCount()      // New cards remaining
await api.ankiGetLrnCardCount()      // Learning cards remaining
await api.ankiGetRevCardCount()      // Review cards remaining
await api.ankiGetETA()               // Estimated time (minutes)
await api.ankiGetCardMark()          // Card marked status
await api.ankiGetCardFlag()          // Flag color (0-7)
await api.ankiGetNextTime1()         // Next interval for ease 1-4
await api.ankiGetCardId()            // Card ID
await api.ankiGetCardNid()           // Note ID
await api.ankiGetDeckName()          // Current deck name
// + 10 more (see ANKIJSAPI-VERIFICATION.md)
```

#### Card Actions (9 methods)
```javascript
await api.ankiMarkCard()             // Toggle marked status
await api.ankiToggleFlag(1)          // Set flag (0-7 or "red"/"blue"/etc.)
await api.ankiBuryCard()             // Bury until tomorrow
await api.ankiBuryNote()             // Bury all cards from note
await api.ankiSuspendCard()          // Suspend card
await api.ankiSuspendNote()          // Suspend all cards from note
await api.ankiResetProgress()        // Reset card to new state
await api.ankiSearchCard('query')    // Open browser with search
await api.ankiSetCardDue(5)          // Set due date (days from today)
```

#### Reviewer Control (6 methods)
```javascript
await api.ankiIsDisplayingAnswer()   // Check if answer showing
await api.ankiShowAnswer()           // Flip to answer side
await api.ankiAnswerEase1()          // Answer "Again"
await api.ankiAnswerEase2()          // Answer "Hard"
await api.ankiAnswerEase3()          // Answer "Good"
await api.ankiAnswerEase4()          // Answer "Easy"
await api.ankiGetDebugInfo()         // Reviewer state info

// Alternative names for compatibility:
await api.buttonAnswerEase1()        // Same as ankiAnswerEase1
// Also: showAnswer() global function override
```

#### Text-to-Speech (7 methods)
```javascript
await api.ankiTtsSpeak('Hello', 0)   // Speak text (queueMode: 0=replace, 1=queue)
await api.ankiTtsStop()              // Stop TTS
await api.ankiTtsSetLanguage('en-US') // Set language
await api.ankiTtsSetSpeechRate(1.0)  // Set rate (0.5-2.0)
await api.ankiTtsSetPitch(1.0)       // Set pitch
await api.ankiTtsIsSpeaking()        // Check if speaking
await api.ankiTtsFieldModifierIsAvailable() // Check TTS field support
```

#### UI Control (8 methods)
```javascript
await api.ankiIsInNightMode()        // Check night mode
await api.ankiShowToast('Hello!', true) // Show toast (text, shortLength)
await api.ankiIsInFullscreen()       // Check fullscreen
await api.ankiIsTopbarShown()        // Check topbar visibility
await api.ankiEnableHorizontalScrollbar(true) // Toggle H scrollbar
await api.ankiEnableVerticalScrollbar(true)   // Toggle V scrollbar
await api.ankiShowNavigationDrawer() // Show nav drawer
await api.ankiShowOptionsMenu()      // Show options menu
```

#### Tag Management (3 methods)
```javascript
await api.ankiGetNoteTags()          // Returns: ['tag1', 'tag2']
await api.ankiAddTagToNote('difficult') // Add single tag
await api.ankiSetNoteTags(['a', 'b']) // Replace all tags
```

#### Utilities (1 method)
```javascript
await api.ankiIsActiveNetworkMetered() // Check if network metered
```

### Methods NOT Available

These assumed methods **do NOT exist** in the API:

❌ `playAudio()` - **Use HTML5 `<audio>` element instead**
❌ `flipCard()` - **Use `ankiShowAnswer()` instead**
❌ `getCurrentCardId()` - **Use `ankiGetCardId()` instead**
❌ Speech-to-text methods - **Not supported on desktop**

### Audio Playback (HTML5)

Audio is **not** handled by the API. Use standard HTML5:

```javascript
// ❌ WRONG - This method doesn't exist
await api.playAudio('sound.mp3');

// ✅ CORRECT - Use HTML5 Audio API
const audio = new Audio('https://example.com/sound.mp3');
audio.play();

// Or reference Anki field
const audio = new Audio('[sound:pronunciation.mp3]');
audio.play();
```

### Fallback Strategy (API not installed)

If AnkiDroidJS addon is not installed:

```javascript
// Standard Anki template JavaScript (no addon required)
<script>
function showAnswer() {
    // Toggle answer visibility
    var answer = document.getElementById('answer');
    if (answer) {
        answer.style.display = answer.style.display === 'none' ? 'block' : 'none';
    }
}

function playAudio(fieldName) {
    // Find audio elements in specified field
    var field = document.querySelector('[data-field="' + fieldName + '"]');
    if (field) {
        var audio = field.querySelector('audio');
        if (audio) audio.play();
    }
}

// Note: Card rating must use Anki's built-in buttons
// Custom rating buttons cannot trigger Anki's scheduling system
</script>
```

**Limitation**: Without AnkiJSApi, custom buttons **cannot** trigger Anki's rating system. Users must use Anki's built-in rating buttons (keyboard shortcuts or UI buttons).

---

## 4. Template Export Requirements

### GrapeJS to Anki Conversion

When exporting from GrapeJS to Anki templates:

1. **Extract Inline JavaScript**: Collect all `<script>` tags and inline handlers
2. **Consolidate CSS**: Merge component styles into single `<style>` block
3. **Process Assets**: Replace external URLs with media folder references
4. **Clean HTML**: Remove GrapeJS-specific attributes (`data-gjs-*`)
5. **Validate Compatibility**: Check for ES6+ features, external resources

### Required Transformations

```javascript
// BEFORE (GrapeJS output with old namespace)
<div data-gjs-type="study-action-bar" class="atd-study-action-bar">
    <button onclick="ankiapi.showAnswer()">Show</button>
</div>

// AFTER (Anki template with AnkiDroidJS API)
<script>
// Initialize AnkiDroidJS API
const api = AnkiDroidJS.init({
    version: '0.0.3',
    developer: 'template-designer@example.com'
});
</script>

<div class="atd-study-action-bar">
    <button onclick="api.ankiShowAnswer()">Show</button>
</div>

// WITH FALLBACK (if API not installed)
<script>
let api = null;
if (typeof AnkiDroidJS !== 'undefined') {
    api = AnkiDroidJS.init({
        version: '0.0.3',
        developer: 'template-designer@example.com'
    });
}

function showAnswer() {
    if (api) {
        api.ankiShowAnswer();
    } else {
        // Fallback: toggle answer visibility
        document.getElementById('answer').style.display = 'block';
    }
}
</script>

<div class="atd-study-action-bar">
    <button onclick="showAnswer()">Show</button>
</div>
```

### Anki Field Placeholders

**Standard Anki field syntax**:
```html
<!-- Basic field -->
{{Front}}
{{Back}}

<!-- Field with filters -->
{{text:Front}}           <!-- Strip HTML -->
{{hint:Definition}}      <!-- Show as hint -->
{{type:Answer}}          <!-- Type-in field -->

<!-- Conditional fields -->
{{#Field}}Content shown if field exists{{/Field}}
{{^Field}}Content shown if field is empty{{/Field}}
```

**GrapeJS Integration**:
```html
<!-- During design: Visual placeholder -->
<span class="anki-field-placeholder" data-anki-field="Front">
    {{Front}}
</span>

<!-- On export: Standard Anki syntax -->
{{Front}}
```

---

## 5. Best Practices for Template Generation

### JavaScript

1. **Use ES5 syntax** for maximum compatibility
2. **Use Promises** (AnkiDroidJS API is Promise-based, supported in Anki 2.1.50+)
3. **Check for AnkiDroidJS availability** before calling methods:
   ```javascript
   if (typeof AnkiDroidJS !== 'undefined') {
       const api = AnkiDroidJS.init({version: '0.0.3', developer: 'email'});
   }
   ```
4. **Provide fallbacks** for when API is not installed
5. **Minimize JavaScript complexity** (debugging in Anki is difficult)
6. **Always await API calls**: All AnkiDroidJS methods return Promises

### CSS

1. **Use widely supported CSS** (Flexbox yes, Grid with caution)
2. **Include vendor prefixes** for older Android WebView
3. **Test responsive layouts** on mobile (AnkiDroid/AnkiMobile)
4. **Avoid complex animations** (may lag on mobile)
5. **Use relative units** (`em`, `rem`, `%`) instead of fixed pixels

### HTML

1. **Keep markup semantic** (aids accessibility)
2. **Use minimal nesting** (improves performance)
3. **Include ARIA attributes** for screen reader support
4. **Test on all platforms** (Desktop, iOS, Android)

### Assets

1. **Optimize images** (Anki syncs all media to mobile devices)
2. **Use appropriate formats** (JPEG for photos, PNG for graphics)
3. **Provide alt text** for accessibility
4. **Keep file sizes small** (large files slow sync)

---

## 6. Testing Strategy

### Validation Checklist

- [ ] **No external resources** (all CSS/JS inline or in media folder)
- [ ] **ES5 JavaScript** (arrow functions OK for Anki 2.1.50+, Promises supported)
- [ ] **Anki field syntax** valid (no unmatched `{{` or `}}`)
- [ ] **CSS compatibility** (tested on oldest target platform)
- [ ] **Media references** point to files in media folder
- [ ] **AnkiDroidJS API fallbacks** provided where used
- [ ] **AnkiDroidJS initialization** included if API methods used

### Platform Testing

1. **Anki Desktop**: Test on Windows, Mac, or Linux
2. **AnkiMobile**: Test on iPhone/iPad (requires paid app)
3. **AnkiDroid**: Test on Android device or emulator
4. **Multiple Anki Versions**: Test on 2.1.x and latest

### Template Validation

```python
# Validation script for template export
def validate_anki_template(html_content: str) -> List[str]:
    """Validate exported template against Anki constraints"""
    issues = []
    
    # Check for external resources
    if '<script src=' in html_content or '<link rel=' in html_content:
        issues.append('External resources detected (not supported)')
    
    # Check for modern JS features
    if '=>' in html_content or 'const ' in html_content or 'let ' in html_content:
        issues.append('Modern JavaScript detected (use ES5)')
    
    # Check for network requests
    if 'fetch(' in html_content or 'XMLHttpRequest' in html_content:
        issues.append('Network requests detected (not supported)')
    
    # Check for malformed Anki fields
    import re
    if re.search(r'\{\{[^}]*$', html_content) or re.search(r'^[^{]*\}\}', html_content):
        issues.append('Malformed Anki field syntax')
    
    return issues
```

---

## 7. Version Compatibility

### Anki Version Support

| Feature | Anki 2.1.0+ | Anki 2.1.50+ | AnkiMobile | AnkiDroid |
|---------|-------------|--------------|------------|-----------|
| ES5 JavaScript | ✅ | ✅ | ✅ | ✅ |
| ES6+ Features | ⚠️ Partial | ✅ | ✅ | ⚠️ Varies |
| Flexbox CSS | ✅ | ✅ | ✅ | ✅ |
| Grid CSS | ⚠️ Limited | ✅ | ✅ | ⚠️ Android 7+ |
| Custom Fonts | ✅ | ✅ | ✅ | ✅ |
| Audio/Video | ✅ | ✅ | ✅ | ✅ |
| `<svg>` | ✅ | ✅ | ✅ | ⚠️ Varies |

**Recommendation**: Target **Anki 2.1.50+** for modern features, provide fallbacks for older versions.

### AnkiDroidJS API Version Requirements

✅ **VERIFIED** against source code

**Current Version**: AnkiDroid JS API for Desktop v0.0.4  
**License**: MIT  
**Repository**: https://github.com/infinyte7/AnkiDroid-API-Desktop

**Minimum Anki Version**: 2.1.50+
- Uses internal methods `_showAnswer()` and `_answerCard()`
- Compatible with all scheduler versions (V1, V2, V3)

**API Contract Version**: 0.0.3 (required in `AnkiDroidJS.init()`)
- Version mismatch shows console warning but continues
- Forward compatible (newer API versions accepted)

**Installation**: Requires AnkiDroid JS API Desktop addon installed in Anki

**Compatibility Notes**:
- ✅ Desktop: Full support (Windows, Mac, Linux)
- ⚠️ AnkiMobile: May require different addon version
- ⚠️ AnkiDroid: Originally designed for Android, desktop port available
- ❌ Speech-to-text: Not supported on desktop (stubs only)

---

## 8. Security Considerations

### Content Security Policy (CSP)

Anki templates run with restricted CSP:

- ❌ **eval()** and **new Function()** blocked
- ❌ **Inline event handlers** may be blocked in strict CSP
- ❌ **External resources** blocked in mobile apps

**Workaround**: Use `addEventListener` instead of inline handlers in strict CSP mode.

```javascript
// ❌ May fail in strict CSP
<button onclick="doSomething()">Click</button>

// ✅ CSP-safe
<button id="my-btn">Click</button>
<script>
document.getElementById('my-btn').addEventListener('click', function() {
    doSomething();
});
</script>
```

### User Data Protection

- ✅ **Local storage**: Limited or unavailable (varies by platform)
- ✅ **Session storage**: Same as localStorage
- ⚠️ **Cookies**: Not persistent across cards
- ❌ **IndexedDB**: Not supported

**Recommendation**: Store persistent data in Anki fields, not browser storage.

---

## 9. Performance Considerations

### Template Size

- **Recommended**: < 50KB per template (HTML + CSS + inline JS)
- **Maximum**: < 200KB (larger templates may lag on mobile)
- **Assets**: Keep individual images < 500KB

### Rendering Performance

- **Minimize DOM complexity**: < 500 elements per card
- **Reduce reflows**: Avoid frequent style changes
- **Optimize selectors**: Use IDs and classes, avoid complex selectors
- **Lazy load**: Don't load all content immediately on mobile

### Animation Performance

```css
/* ✅ FAST: Use transform and opacity */
.animated {
    transition: transform 0.3s, opacity 0.3s;
    will-change: transform, opacity;
}

/* ❌ SLOW: Avoid animating layout properties */
.slow-animated {
    transition: width 0.3s, height 0.3s, margin 0.3s;
}
```

---

## 10. Troubleshooting Common Issues

### Issue: JavaScript not executing

**Causes**:
- Syntax error in script
- Script placed after closing `</html>`
- CSP blocking execution

**Solutions**:
- Validate JavaScript syntax
- Place `<script>` inside `<body>`
- Use addEventListener instead of inline handlers

### Issue: Styles not applied

**Causes**:
- CSS selector conflicts with Anki's default styles
- Invalid CSS syntax
- Platform-specific CSS limitations

**Solutions**:
- Use specific selectors with `.atd-` prefix
- Validate CSS syntax
- Test on target platform

### Issue: Images not loading

**Causes**:
- File not in media folder
- Incorrect file reference
- File name mismatch (case-sensitive on some platforms)

**Solutions**:
- Verify file is in Anki media folder
- Use exact file name (case-sensitive)
- Check file extension is correct

### Issue: AnkiDroidJS API methods not found

**Causes**:
- AnkiDroid JS API Desktop addon not installed
- Addon disabled or incompatible version
- Incorrect method name (old `ankiapi.*` namespace)
- Missing initialization (no `AnkiDroidJS.init()` call)
- Missing developer contract in initialization

**Solutions**:
- Install **AnkiDroid JS API for Desktop v0.0.4** addon
- Enable addon in Anki preferences
- Update method names from old `ankiapi.*` to new `api.*` pattern
- Add initialization code:
  ```javascript
  const api = AnkiDroidJS.init({
      version: '0.0.3',
      developer: 'your-email@example.com'
  });
  ```
- Verify method name against [ANKIJSAPI-VERIFICATION.md](ANKIJSAPI-VERIFICATION.md)
- Provide fallback implementation for when addon not installed

---

## 11. Next Steps

### Required Actions

1. ✅ **Validate AnkiJSApi Methods**: Access `D:\Development\Python\AnkiJSApi` and verify all assumed methods
2. ✅ **Test on Platforms**: Validate templates on Desktop, iOS, Android
3. ✅ **Create Fallbacks**: Implement non-AnkiJSApi alternatives for core features
4. ✅ **Update Documentation**: Revise 02-ARCHITECTURE.md with verified API
5. ✅ **Build Validator**: Implement template validation script
6. ✅ **Add Tests**: Create integration tests for template export

### Future Enhancements

- **Template Library**: Pre-built templates for common use cases
- **Platform Detection**: Auto-adapt templates to platform capabilities
- **Performance Profiling**: Measure template rendering performance
- **Accessibility Audit**: Ensure WCAG compliance
- **Dark Mode Support**: Automatic dark mode styles for Anki night mode

---

**Document Status**: ⚠️ DRAFT - Requires AnkiJSApi verification
**Last Updated**: January 11, 2026
**Next Review**: After AnkiJSApi source code validation
