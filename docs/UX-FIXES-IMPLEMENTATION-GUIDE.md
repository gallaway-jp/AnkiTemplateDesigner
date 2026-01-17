# UX Fixes - Implementation Guide

This document provides code snippets and step-by-step instructions for implementing the most impactful UX improvements.

---

## 1. RESPONSIVE DIALOG SIZING ⭐ Priority: HIGH

**Problem:** Dialog may not fit on smaller monitors (1366x768)

**File:** `gui/designer_dialog.py`

**Changes:**

Replace the `__init__` method's sizing logic:

```python
def __init__(self, parent=None):
    """Initialize designer dialog.
    
    Args:
        parent: Parent widget (defaults to Anki main window if available)
    """
    super().__init__(parent or mw)
    self.setWindowTitle("Anki Template Designer")
    
    # Make dialog resizable, minimizable, and maximizable
    self.setWindowFlags(
        Qt.WindowType.Window |
        Qt.WindowType.WindowMinimizeButtonHint |
        Qt.WindowType.WindowMaximizeButtonHint |
        Qt.WindowType.WindowCloseButtonHint
    )
    
    # NEW: Calculate optimal size based on available screen space
    self._set_optimal_size()
    
    # ... rest of init code ...

def _set_optimal_size(self):
    """Calculate and set optimal dialog size based on available screen."""
    screen = self.screen()
    available_geom = screen.availableGeometry()
    
    # Use 85-90% of available space
    # Minimum 1200x800, Maximum available
    width = max(
        self.MIN_WIDTH,
        min(1400, int(available_geom.width() * 0.90))
    )
    height = max(
        self.MIN_HEIGHT,
        min(900, int(available_geom.height() * 0.85))
    )
    
    self.resize(QSize(width, height))
    
    # Center dialog on screen
    center_point = available_geom.center()
    self.move(
        center_point.x() - width // 2,
        center_point.y() - height // 2
    )
    
    print(f"[Designer] Dialog sized to {width}x{height}")
    print(f"[Designer] Screen: {available_geom.width()}x{available_geom.height()}")
```

**Testing:**
- Test on 1366x768 monitor - dialog should fit
- Test on 1920x1080 - should use ~90% of space
- Test on 4K - should max out at 1400x900

---

## 2. LOADING PROGRESS FEEDBACK ⭐ Priority: HIGH

**Problem:** Users don't know what's happening during 3-5 second startup

**Files:** 
- `web/index.html` - Update HTML
- `web/designer.css` - Update styles
- `web/designer.js` - Add progress tracking

### Step 1: Update HTML (web/index.html)

Replace the loading section (lines 50-56):

```html
<!-- Loading Indicator with Progress -->
<div id="loading" class="loading-overlay">
    <div class="loading-container">
        <h2>Loading Template Designer</h2>
        
        <!-- Progress bar -->
        <div class="progress-bar-container">
            <div id="progress-bar" class="progress-bar"></div>
            <span id="progress-text" class="progress-text">0%</span>
        </div>
        
        <!-- Status message -->
        <p id="loading-status" class="loading-status">Initializing...</p>
        
        <!-- Visual spinner -->
        <div class="spinner"></div>
    </div>
</div>
```

### Step 2: Update CSS (web/designer.css)

Add new styles (add to end of file):

```css
/* Loading Overlay Styles */
.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--bg-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
}

.loading-container {
    text-align: center;
    max-width: 400px;
    padding: 40px;
    background: var(--bg-secondary);
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.loading-container h2 {
    margin-bottom: 30px;
    color: var(--text-primary);
    font-size: 24px;
}

.progress-bar-container {
    position: relative;
    width: 100%;
    height: 8px;
    background: var(--bg-tertiary);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 15px;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #4CAF50, #66BB6A);
    width: 0%;
    transition: width 0.3s ease;
    border-radius: 4px;
}

.progress-text {
    display: block;
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: 8px;
}

.loading-status {
    color: var(--text-primary);
    font-size: 14px;
    margin-top: 20px;
    height: 20px;
    min-height: 20px;
}

.spinner {
    border: 4px solid var(--bg-tertiary);
    border-top: 4px solid #4CAF50;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    animation: spin 1s linear infinite;
    margin: 20px auto 0;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.loading-overlay.hidden {
    display: none;
}
```

### Step 3: Update JavaScript (web/designer.js)

Replace the initialization function with progress tracking:

```javascript
// Define initialization steps
const INIT_STEPS = [
    { step: 1, message: 'Loading GrapeJS library...' },
    { step: 2, message: 'Creating editor instance...' },
    { step: 3, message: 'Configuring editor...' },
    { step: 4, message: 'Loading component library...' },
    { step: 5, message: 'Setting up traits...' },
    { step: 6, message: 'Registering devices...' },
    { step: 7, message: 'Loading Anki plugin...' },
    { step: 8, message: 'Initializing components...' },
    { step: 9, message: 'Ready!' }
];

/**
 * Update progress bar and status message
 */
function updateProgress(step, totalSteps) {
    const percent = Math.round((step / totalSteps) * 100);
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const statusText = document.getElementById('loading-status');
    
    if (progressBar) progressBar.style.width = percent + '%';
    if (progressText) progressText.textContent = percent + '%';
    if (statusText && step <= INIT_STEPS.length) {
        statusText.textContent = INIT_STEPS[step - 1].message;
    }
    
    console.log(`[Progress] Step ${step}/${totalSteps}: ${percent}%`);
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.classList.add('hidden');
    }
}

/**
 * Initialize the GrapeJS editor with progress tracking
 */
function initializeEditor() {
    console.log('[Designer] Starting initialization...');
    
    try {
        // Step 1: Check GrapeJS
        updateProgress(1, INIT_STEPS.length);
        
        if (typeof grapesjs === 'undefined') {
            console.error('[Designer] GrapeJS library not loaded!');
            showError('GrapeJS library failed to load. Please refresh the page.');
            return;
        }
        
        // Step 2: Create editor
        updateProgress(2, INIT_STEPS.length);
        
        window.editor = grapesjs.init({
            container: '#gjs',
            height: '100%',
            width: 'auto',
            storageManager: false
        });
        
        // Step 3: Configure managers
        updateProgress(3, INIT_STEPS.length);
        
        try {
            editor.LayerManager.getConfig().appendTo = '.layers-container';
            editor.BlockManager.getConfig().appendTo = '.blocks-container';
            editor.StyleManager.getConfig().appendTo = '.styles-container';
            editor.TraitManager.getConfig().appendTo = '.traits-container';
        } catch (e) {
            console.warn('[Designer] Manager configuration warning:', e.message);
        }
        
        // Step 4-6: Setup devices and plugins
        updateProgress(4, INIT_STEPS.length);
        
        try {
            editor.setDevice('Desktop');
            const desktopDevice = editor.Devices.get('desktop') || 
                                  editor.addDevice('Desktop', { width: '' });
            const mobileDevice = editor.Devices.get('mobile') || 
                                 editor.addDevice('Mobile', { width: '320px', widthMedia: '480px' });
        } catch (e) {
            console.warn('[Designer] Device configuration warning:', e.message);
        }
        
        updateProgress(6, INIT_STEPS.length);
        
        // Step 7-8: Register customizations
        updateProgress(7, INIT_STEPS.length);
        
        try {
            if (typeof ankiPlugin === 'function') {
                ankiPlugin(editor);
            }
        } catch (e) {
            console.warn('[Designer] Plugin warning:', e.message);
        }
        
        updateProgress(8, INIT_STEPS.length);
        
        // Schedule registration after delay
        setTimeout(() => {
            registerCustomizations(editor);
            updateProgress(9, INIT_STEPS.length);
            
            // Hide loading after a brief moment
            setTimeout(() => {
                hideLoading();
            }, 300);
            
        }, 100);
        
        console.log('[Designer] Initialization sequence started');
        
    } catch (error) {
        console.error('[Designer] Initialization failed:', error);
        showError('Failed to initialize editor: ' + error.message);
        hideLoading();
    }
}
```

**Testing:**
- Open developer console and watch progress
- Verify loading spinner shows steps
- Verify progress bar fills to 100%
- Verify overlay hides when done

---

## 3. FIRST-TIME USER ONBOARDING ⭐ Priority: HIGH (CRITICAL)

**Problem:** New users have no guidance on how to use the tool

**File:** `web/index.html`

### Step 1: Add Welcome Overlay

Add this HTML after the `</body>` closing tag (before script tags):

```html
<!-- Welcome/Onboarding Overlay -->
<div id="welcome-overlay" class="welcome-overlay hidden">
    <div class="welcome-modal">
        <button id="close-welcome" class="close-button">✕</button>
        
        <h2>Welcome to Anki Template Designer! 👋</h2>
        
        <div class="welcome-content">
            <p class="intro-text">
                Create beautiful Anki card templates with a visual drag-and-drop builder.
                No coding required!
            </p>
            
            <div class="quick-start-steps">
                <h3>Quick Start Guide:</h3>
                
                <div class="step">
                    <div class="step-number">1</div>
                    <div class="step-content">
                        <p><strong>Find Components</strong></p>
                        <p>Expand categories in the left panel to see available components</p>
                    </div>
                </div>
                
                <div class="step">
                    <div class="step-number">2</div>
                    <div class="step-content">
                        <p><strong>Drag to Canvas</strong></p>
                        <p>Drag components from the left panel to the canvas in the center</p>
                    </div>
                </div>
                
                <div class="step">
                    <div class="step-number">3</div>
                    <div class="step-content">
                        <p><strong>Customize Properties</strong></p>
                        <p>Select a component and edit its properties in the right panel</p>
                    </div>
                </div>
                
                <div class="step">
                    <div class="step-number">4</div>
                    <div class="step-content">
                        <p><strong>Save & Export</strong></p>
                        <p>Click the Save button to save your template</p>
                    </div>
                </div>
            </div>
            
            <div class="help-links">
                <p>Need more help?</p>
                <a href="#" onclick="showHelp('keyboard')">Keyboard Shortcuts</a> • 
                <a href="#" onclick="showHelp('components')">Component Guide</a>
            </div>
            
            <div class="welcome-footer">
                <label class="checkbox-label">
                    <input type="checkbox" id="show-welcome-again">
                    Show this again next time
                </label>
                <button id="get-started" class="button-primary">Get Started!</button>
            </div>
        </div>
    </div>
</div>
```

### Step 2: Add Welcome Styles

Add to `web/designer.css`:

```css
/* Welcome Overlay */
.welcome-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    animation: fadeIn 0.3s ease;
}

.welcome-overlay.hidden {
    display: none;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.welcome-modal {
    background: var(--bg-primary);
    border-radius: 12px;
    padding: 40px;
    max-width: 600px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    position: relative;
    animation: slideUp 0.3s ease;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.close-button {
    position: absolute;
    top: 15px;
    right: 15px;
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: var(--text-secondary);
    padding: 5px;
}

.close-button:hover {
    color: var(--text-primary);
}

.welcome-modal h2 {
    color: var(--text-primary);
    margin-bottom: 15px;
    font-size: 28px;
}

.intro-text {
    color: var(--text-secondary);
    margin-bottom: 30px;
    font-size: 16px;
    line-height: 1.6;
}

.quick-start-steps {
    margin: 30px 0;
}

.quick-start-steps h3 {
    color: var(--text-primary);
    margin-bottom: 20px;
    font-size: 18px;
}

.step {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid var(--border-color);
}

.step:last-child {
    border-bottom: none;
}

.step-number {
    background: #4CAF50;
    color: white;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    flex-shrink: 0;
}

.step-content p {
    margin: 0;
    color: var(--text-primary);
}

.step-content p:first-child {
    font-weight: 600;
    margin-bottom: 5px;
}

.step-content p:last-child {
    color: var(--text-secondary);
    font-size: 14px;
}

.help-links {
    text-align: center;
    margin: 25px 0;
    padding: 15px;
    background: var(--bg-secondary);
    border-radius: 6px;
    color: var(--text-secondary);
}

.help-links a {
    color: #4CAF50;
    text-decoration: none;
    font-weight: 500;
}

.help-links a:hover {
    text-decoration: underline;
}

.welcome-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 25px;
    padding-top: 20px;
    border-top: 1px solid var(--border-color);
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    color: var(--text-secondary);
    font-size: 14px;
}

.checkbox-label input {
    cursor: pointer;
}

.button-primary {
    background: #4CAF50;
    color: white;
    border: none;
    padding: 10px 24px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
}

.button-primary:hover {
    background: #66BB6A;
}

.button-primary:active {
    background: #2E7D32;
}
```

### Step 3: Add Welcome Logic

Add to `web/designer.js` (after defineINIT_STEPS):

```javascript
/**
 * Initialize welcome overlay on first load
 */
function initializeWelcome() {
    const welcomeOverlay = document.getElementById('welcome-overlay');
    const closeBtn = document.getElementById('close-welcome');
    const getStartedBtn = document.getElementById('get-started');
    const showAgainCheckbox = document.getElementById('show-welcome-again');
    
    // Check if user has seen welcome before
    const hasSeenWelcome = localStorage.getItem('ankidesigner_welcome_seen');
    
    // Show welcome if not seen before
    if (!hasSeenWelcome) {
        welcomeOverlay.classList.remove('hidden');
    }
    
    // Close welcome
    function closeWelcome() {
        welcomeOverlay.classList.add('hidden');
        
        // Save preference
        const showAgain = showAgainCheckbox?.checked ?? false;
        if (!showAgain) {
            localStorage.setItem('ankidesigner_welcome_seen', 'true');
        }
    }
    
    closeBtn?.addEventListener('click', closeWelcome);
    getStartedBtn?.addEventListener('click', closeWelcome);
    
    // Close on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !welcomeOverlay.classList.contains('hidden')) {
            closeWelcome();
        }
    });
}

// Call after editor loads
// Add to hideLoading() function:
setTimeout(() => {
    hideLoading();
    initializeWelcome();  // NEW LINE
}, 300);
```

**Testing:**
- Open designer for first time - welcome should show
- Click "Get Started" - overlay should close
- Check "Show again" - overlay should show next time
- Press Escape - overlay should close
- Looks good on different screen sizes

---

## 4. BETTER ERROR MESSAGES ⭐ Priority: HIGH

**File:** `gui/webview_bridge.py`

Replace the `saveProject` method:

```python
@pyqtSlot(str)
def saveProject(self, grapejs_json: str):
    """Called by JS when user saves the project.
    
    Args:
        grapejs_json: GrapeJS project data as JSON string
    """
    if self._save_callback:
        try:
            # Parse JSON
            data = json.loads(grapejs_json)
            
            # Validate template structure
            errors = self._validate_template_data(data)
            if errors:
                error_message = self._format_error_message(errors)
                self.showError(error_message)
                return
            
            # Proceed with save
            self._save_callback(data)
            
        except json.JSONDecodeError as e:
            self.showError(
                f"Invalid template data:\n\n"
                f"The template couldn't be saved due to a data format error.\n"
                f"Error: {e}\n\n"
                f"Try:\n"
                f"• Refresh the page and try again\n"
                f"• Check the browser console for more details"
            )
        except Exception as e:
            self.showError(
                f"Unexpected error while saving:\n\n"
                f"{str(e)}\n\n"
                f"Please try again or contact support if the problem persists."
            )

def _validate_template_data(self, data: dict) -> list:
    """Validate template structure and return list of errors."""
    errors = []
    
    # Check required fields
    if not data:
        errors.append("Template data is empty")
        return errors
    
    # Check for components
    components = data.get('components', [])
    if not components:
        errors.append("Template must have at least one component")
    
    # Check for HTML
    html = data.get('html', '')
    if not html:
        errors.append("Template must have HTML content")
    
    # Check for Anki field syntax errors
    if '{{' in html:
        # Count opening and closing braces
        opening_braces = html.count('{{')
        closing_braces = html.count('}}')
        if opening_braces != closing_braces:
            errors.append(
                f"Mismatched Anki field references: "
                f"{opening_braces} opening '{{{{' but {closing_braces} closing '}}}}'\n"
                f"• Check all field references have matching closing braces"
            )
    
    # Check for common issues
    if '<%' in html or '%>' in html:
        errors.append(
            "Template uses old-style template syntax (<% %>)\n"
            "• Use Anki field references instead: {{FieldName}}"
        )
    
    return errors

def _format_error_message(self, errors: list) -> str:
    """Format error messages for display to user."""
    if not errors:
        return "Unknown error"
    
    if len(errors) == 1:
        return f"Cannot save template:\n\n{errors[0]}"
    
    error_list = "\n\n".join(f"• {e}" for e in errors)
    return f"Cannot save template:\n\n{error_list}\n\nFix these issues and try again."
```

**Add to imports:**
```python
from typing import Callable, Any, Optional, List
```

**Testing:**
- Try to save empty template - should show "must have component" error
- Try to save with mismatched {{ }} - should show specific error
- Try to save with {{FieldName}} - should show success
- Check that error messages guide users to solutions

---

## 5. KEYBOARD SHORTCUTS REFERENCE ⭐ Priority: MEDIUM

**File:** `web/designer.js`

Add this function:

```javascript
/**
 * Keyboard shortcuts configuration and handling
 */
const KEYBOARD_SHORTCUTS = {
    'ctrl+z': {
        name: 'Undo',
        description: 'Undo last change',
        action: 'undo'
    },
    'ctrl+shift+z': {
        name: 'Redo',
        description: 'Redo last undone change',
        action: 'redo'
    },
    'ctrl+s': {
        name: 'Save',
        description: 'Save template to Anki',
        action: 'save'
    },
    'ctrl+e': {
        name: 'Export',
        description: 'Export template as HTML/CSS',
        action: 'export'
    },
    'delete': {
        name: 'Delete',
        description: 'Delete selected component',
        action: 'delete'
    },
    'escape': {
        name: 'Deselect',
        description: 'Deselect current component',
        action: 'deselect'
    },
    '?': {
        name: 'Help',
        description: 'Show keyboard shortcuts',
        action: 'help'
    }
};

/**
 * Setup keyboard shortcut handling
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Build shortcut string
        const parts = [];
        if (e.ctrlKey || e.metaKey) parts.push('ctrl');
        if (e.shiftKey) parts.push('shift');
        if (e.altKey) parts.push('alt');
        parts.push(e.key.toLowerCase());
        
        const shortcut = parts.join('+');
        const handler = KEYBOARD_SHORTCUTS[shortcut];
        
        if (handler) {
            e.preventDefault();
            handleKeyboardAction(handler.action);
        }
    });
}

/**
 * Handle keyboard shortcut actions
 */
function handleKeyboardAction(action) {
    if (!editor) return;
    
    switch (action) {
        case 'undo':
            editor.UndoManager?.undo?.();
            break;
        case 'redo':
            editor.UndoManager?.redo?.();
            break;
        case 'save':
            window.bridge?.saveProject?.(JSON.stringify(editor.getProjectData?.()));
            break;
        case 'export':
            window.bridge?.exportTemplate?.('html', JSON.stringify(editor.getProjectData?.()));
            break;
        case 'delete':
            editor.getSelected()?.remove?.();
            break;
        case 'deselect':
            editor.selectRemove?.();
            break;
        case 'help':
            showKeyboardHelp();
            break;
    }
}

/**
 * Show keyboard shortcuts help dialog
 */
function showKeyboardHelp() {
    const shortcuts = Object.entries(KEYBOARD_SHORTCUTS)
        .map(([keys, info]) => `${keys.toUpperCase()}: ${info.description}`)
        .join('\n');
    
    const helpText = 'Keyboard Shortcuts:\n\n' + shortcuts;
    alert(helpText);  // TODO: Replace with styled modal dialog
}

// Call this during initialization
// Add to registerCustomizations function:
setupKeyboardShortcuts();
```

**Add tooltip hints to toolbar buttons:**

Add to `web/index.html` in the toolbar section:

```html
<button data-action="undo" title="Undo (Ctrl+Z)">↶ Undo</button>
<button data-action="redo" title="Redo (Ctrl+Shift+Z)">↷ Redo</button>
<button data-action="save" title="Save (Ctrl+S)">💾 Save</button>
<button data-action="export" title="Export (Ctrl+E)">📄 Export</button>
<button data-action="help" title="Help (?)">❓ Help</button>
```

**Testing:**
- Press Ctrl+Z - should undo
- Press Ctrl+S - should save
- Press ? - should show shortcuts
- Hover buttons - tooltips should appear
- Mobile: shortcuts still work with Ctrl

---

## Implementation Priority & Effort

| # | Feature | Effort | Impact | Recommended |
|---|---------|--------|--------|------------|
| 1 | Responsive dialog sizing | 30 min | HIGH | ⭐ DO FIRST |
| 2 | Loading progress feedback | 1 hour | HIGH | ⭐ DO FIRST |
| 3 | First-time onboarding | 2 hours | CRITICAL | ⭐⭐ DO FIRST |
| 4 | Better error messages | 1.5 hours | MEDIUM | ⭐ DO FIRST |
| 5 | Keyboard shortcuts | 1 hour | MEDIUM | ⭐ DO FIRST |

**Total effort for all 5 fixes:** ~5-6 hours

---

## Testing Checklist

After implementing each fix:

- [ ] No console errors
- [ ] Functionality works as described
- [ ] Works on small screens (1366x768)
- [ ] Works on large screens (4K)
- [ ] Keyboard navigation works
- [ ] Mobile/touch friendly where applicable
- [ ] Dark mode looks good
- [ ] Light mode looks good

---

## Quick Command to Apply

```bash
# After making changes, run tests
cd d:\Development\Python\AnkiTemplateDesigner
python run_ui_tests.py --fast

# Check for errors
python -m pytest tests/ui -k "not slow" -v
```

---

**Next Steps:**
1. Implement fixes in order of priority
2. Test after each change
3. Run UI tests to ensure nothing broke
4. Update UX-ASSESSMENT-REPORT.md with completion status
