# Anki Template Constraints & Requirements

> **Purpose**: Document technical constraints and requirements for Anki template generation
> **Date**: January 11, 2026
> **Status**: ⚠️ VERIFICATION REQUIRED - AnkiJSApi methods need validation against actual source

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

## 3. AnkiJSApi Integration

### ⚠️ VERIFICATION REQUIRED

**Status**: The following AnkiJSApi methods are **ASSUMED** based on plan documentation but **NOT VERIFIED** against actual source code.

**Source**: These methods are documented in `02-ARCHITECTURE.md` but the actual AnkiJSApi addon at `D:\Development\Python\AnkiJSApi` (outside this workspace) has not been validated.

### Assumed API Surface

```javascript
// ⚠️ UNVERIFIED - Assumed to exist based on 02-ARCHITECTURE.md

// Card Actions
ankiapi.showAnswer()        // Show answer side
ankiapi.flipCard()          // Flip between front/back
ankiapi.markCard()          // Toggle marked status
ankiapi.suspendCard()       // Suspend card
ankiapi.buryCard()          // Bury card

// Rating Actions
ankiapi.rateAgain()         // Rate as Again
ankiapi.rateHard()          // Rate as Hard
ankiapi.rateGood()          // Rate as Good
ankiapi.rateEasy()          // Rate as Easy

// Audio Actions
ankiapi.playAudio('field:Audio')  // Play audio from field
ankiapi.replayAudio()             // Replay all audio
ankiapi.pauseAudio()              // Pause playback
ankiapi.recordAudio()             // Record audio (if supported)

// Navigation
ankiapi.undoAction()              // Undo last action
ankiapi.editNote()                // Open note editor
ankiapi.showDeckOverview()        // Show deck overview

// Display
ankiapi.toggleNightMode()         // Toggle night mode
ankiapi.zoomIn()                  // Increase zoom
ankiapi.zoomOut()                 // Decrease zoom

// Timer
ankiapi.startTimer()              // Start timer
ankiapi.stopTimer()               // Stop timer
ankiapi.resetTimer()              // Reset timer

// Custom
ankiapi.runCustomJS(code)         // Run custom JavaScript
ankiapi.showHint()                // Show hint
ankiapi.hideElement(selector)     // Hide element
ankiapi.showElement(selector)     // Show element
ankiapi.toggleElement(selector)   // Toggle visibility
```

### Required Verification Steps

**TODO**: Validate against actual AnkiJSApi source code

1. Access `D:\Development\Python\AnkiJSApi` repository
2. Review actual API implementation
3. Verify method names and signatures
4. Check which methods are available in different Anki versions
5. Update this documentation with actual API surface
6. Update `02-ARCHITECTURE.md` with verified methods
7. Update `COMPONENT-AUDIT.md` example code with verified methods

### Fallback Strategy (if AnkiJSApi not available)

If AnkiJSApi is not installed or methods differ:

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
// BEFORE (GrapeJS output)
<div data-gjs-type="study-action-bar" class="atd-study-action-bar">
    <button onclick="ankiapi.showAnswer()">Show</button>
</div>

// AFTER (Anki template)
<div class="atd-study-action-bar">
    <button onclick="showAnswer()">Show</button>
</div>
<script>
function showAnswer() {
    if (typeof ankiapi !== 'undefined') {
        ankiapi.showAnswer(); // Use AnkiJSApi if available
    } else {
        // Fallback implementation
        document.getElementById('answer').style.display = 'block';
    }
}
</script>
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
2. **Avoid async/await** (not supported in older Anki versions)
3. **Check for AnkiJSApi availability** before calling methods
4. **Provide fallbacks** for when AnkiJSApi is not installed
5. **Minimize JavaScript complexity** (debugging in Anki is difficult)

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
- [ ] **ES5 JavaScript** (no arrow functions, const/let, async/await)
- [ ] **Anki field syntax** valid (no unmatched `{{` or `}}`)
- [ ] **CSS compatibility** (tested on oldest target platform)
- [ ] **Media references** point to files in media folder
- [ ] **AnkiJSApi fallbacks** provided where used

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

### AnkiJSApi Version

⚠️ **UNKNOWN** - Version compatibility needs verification against actual addon.

**TODO**:
- Check minimum Anki version required by AnkiJSApi
- Verify which methods are available in each version
- Document breaking changes between versions

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

### Issue: AnkiJSApi methods not found

**Causes**:
- AnkiJSApi addon not installed
- Addon disabled
- Incorrect method name

**Solutions**:
- Install AnkiJSApi addon
- Enable addon in Anki preferences
- Verify method name against actual API
- Provide fallback implementation

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
