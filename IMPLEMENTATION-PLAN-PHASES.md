# ADDON COMPLETION ACTION PLAN
**Created:** February 1, 2026  
**Status:** Ready for Implementation

---

## SITUATION

After comprehensive audit, we have discovered:

✅ **Excellent Backend** - All services complete and tested  
✅ **Complete Bridge API** - 38 methods ready to be called  
⚠️ **Basic Frontend** - HTML/JS skeleton with no integration  

**Current State:** 42% feature complete (backend heavy, frontend light)

---

## RECOMMENDATION

**DO NOT START PLAN 20 YET** (Onboarding System)

Reason: An onboarding system for a non-functional addon is useless. Instead, we must:

1. **Complete the frontend** (what users see)
2. **Wire backend to frontend** (make it work)
3. **Test end-to-end** (verify functionality)
4. **Then** add onboarding

---

## IMPLEMENTATION ROADMAP

### PHASE 1: GrapeJS Editor Integration (2 days)
**Goal:** Get a working template editor in the canvas

#### 1.1: Add GrapeJS Library
```html
<!-- Add to index.html <head> -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/grapesjs@latest/dist/css/grapes.min.css">
<script src="https://cdn.jsdelivr.net/npm/grapesjs@latest/dist/grapes.min.js"></script>
```

**Effort:** 30 minutes  
**Risk:** Low  
**Dependency:** None

#### 1.2: Initialize Editor
```javascript
// In index.html script section
let editor = null;

function initEditor() {
    if (!window.grapesjs) {
        console.error('GrapeJS not loaded');
        return;
    }
    
    editor = grapesjs.init({
        container: '#canvas',
        components: [],
        blocks: [
            {
                id: 'text',
                label: 'Text',
                content: '<div>Text Block</div>'
            },
            // ... more blocks
        ],
        storageManager: {
            id: 'grapesjs-demo',
            type: 'local',
            autoload: true,
            autosave: true,
            stepsBeforeSave: 3,
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initWebChannel();
    initToolbar();
    // Add this:
    initEditor();  // Initialize after WebChannel ready
});
```

**Effort:** 1 day  
**Risk:** Medium (GrapeJS is complex)  
**Dependency:** GrapeJS loaded

#### 1.3: Connect Save Button
```javascript
function saveTemplate() {
    if (!bridge || !editor) {
        alert('Not ready yet');
        return;
    }
    
    const html = editor.getHtml();
    const css = editor.getCss();
    const components = editor.getComponents();
    
    const template = {
        name: "Current Template",
        html: html,
        css: css,
        components: components
    };
    
    bridge.saveTemplate(JSON.stringify(template), function(response) {
        try {
            const result = JSON.parse(response);
            if (result.success) {
                showToast('Saved successfully');
                setStatusLeft('Saved');
            } else {
                showErrorToast(result);
            }
        } catch (e) {
            console.error('Save error:', e);
        }
    });
}

// Update button handler:
document.getElementById('btnSave').addEventListener('click', saveTemplate);
```

**Effort:** 4 hours  
**Risk:** Low  
**Dependency:** Editor initialized, Bridge ready

#### 1.4: Connect Load Button
```javascript
function loadTemplate(templateId) {
    if (!bridge || !editor) return;
    
    bridge.loadTemplate(templateId, function(response) {
        try {
            const result = JSON.parse(response);
            if (result.success) {
                const template = result.data;
                editor.setComponents(template.components || []);
                editor.setStyle(template.css || '');
                showToast('Template loaded');
            } else {
                showErrorToast(result);
            }
        } catch (e) {
            console.error('Load error:', e);
        }
    });
}

// Update open button:
document.getElementById('btnOpen').addEventListener('click', function() {
    bridge.listTemplates(function(response) {
        try {
            const templates = JSON.parse(response);
            // Show dialog to pick template
            // Then call loadTemplate(id)
        } catch (e) {
            console.error(e);
        }
    });
});
```

**Effort:** 4 hours  
**Risk:** Medium  
**Dependency:** GrapeJS, Bridge, Dialog system

**Phase 1 Testing:**
```
[ ] GrapeJS editor visible in canvas
[ ] Can drag components from sidebar to canvas
[ ] Can edit component properties
[ ] Save creates file
[ ] Load restores components
[ ] Editor state persists (browser local storage)
```

---

### PHASE 2: Template Workflow (1 day)

#### 2.1: New Template Dialog
```javascript
function createNewTemplate() {
    const name = prompt('Template name:');
    if (!name) return;
    
    bridge.createTemplate(name, function(response) {
        try {
            const result = JSON.parse(response);
            if (result.success) {
                editor.setComponents([]);
                editor.setStyle('');
                setStatusLeft('New: ' + name);
            }
        } catch (e) {
            console.error(e);
        }
    });
}

document.getElementById('btnNew').addEventListener('click', createNewTemplate);
```

**Effort:** 3 hours  
**Risk:** Low  
**Dependency:** Template service, Bridge ready

#### 2.2: Delete Template
```javascript
function deleteCurrentTemplate(templateId) {
    if (!confirm('Delete this template?')) return;
    
    bridge.deleteTemplate(templateId, function(response) {
        try {
            const result = JSON.parse(response);
            if (result.success) {
                editor.setComponents([]);
                showToast('Template deleted');
            }
        } catch (e) {
            console.error(e);
        }
    });
}
```

**Effort:** 2 hours  
**Risk:** Low  
**Dependency:** Bridge ready

#### 2.3: Undo/Redo Integration
```javascript
// GrapeJS has built-in undo manager
editor.UndoManager.add(state);  // Adds state

// Connect to Python undo:
editor.on('change:all', function() {
    const state = editor.getHtml();
    window.pushUndoState(previousState, state, 'Editor change');
    previousState = state;
});

// Listen for Python undo/redo:
bridge.messageReceived.connect(function(method, data) {
    if (method === 'undo' || method === 'redo') {
        const state = JSON.parse(data);
        editor.setComponents(state.components);
    }
});
```

**Effort:** 4 hours  
**Risk:** Medium (state sync is tricky)  
**Dependency:** GrapeJS, Python UndoManager

**Phase 2 Testing:**
```
[ ] Create new template
[ ] Edit and save
[ ] Open and continue editing
[ ] Delete template
[ ] Undo changes in editor
[ ] Redo changes
```

---

### PHASE 3: Component System (2-3 days)

#### 3.1: Component Definitions
```javascript
// Add to GrapeJS initialization
const components = {
    text: {
        label: 'Text',
        category: 'Basic',
        icon: 'T',
        content: '<div>Sample text</div>'
    },
    field: {
        label: 'Anki Field',
        category: 'Anki',
        icon: '{{',
        content: '<span>{{field}}</span>'
    },
    cloze: {
        label: 'Cloze Deletion',
        category: 'Anki',
        icon: '…',
        content: '<span>{{cloze:field}}</span>'
    },
    // ... more components
};

// Register with GrapeJS
Object.entries(components).forEach(([id, config]) => {
    editor.BlockManager.add(id, {
        label: config.label,
        category: config.category,
        content: config.content,
        attributes: { class: 'comp-' + id }
    });
});
```

**Effort:** 1 day  
**Risk:** Medium (lots of components)  
**Dependency:** GrapeJS initialized

#### 3.2: Properties Panel
```javascript
// When component selected in editor
editor.on('component:selected', function(component) {
    const props = component.attributes;
    
    // Generate property form
    let html = '<form>';
    Object.entries(props).forEach(([key, value]) => {
        html += `
            <div class="prop-group">
                <label>${key}</label>
                <input type="text" value="${value}" 
                    onchange="updateComponentProp('${key}', this.value)">
            </div>
        `;
    });
    html += '</form>';
    
    document.getElementById('propertiesContent').innerHTML = html;
});

function updateComponentProp(key, value) {
    const selected = editor.getSelected();
    if (selected) {
        selected.addAttributes({[key]: value});
    }
}
```

**Effort:** 1 day  
**Risk:** Low  
**Dependency:** GrapeJS, Selected component tracking

#### 3.3: Preview System
```javascript
document.getElementById('btnPreview').addEventListener('click', function() {
    const html = editor.getHtml();
    const css = editor.getCss();
    
    // Open preview window
    const previewWindow = window.open('', '_blank', 'width=800,height=600');
    previewWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <style>${css}</style>
        </head>
        <body>${html}</body>
        </html>
    `);
    previewWindow.document.close();
});
```

**Effort:** 2 hours  
**Risk:** Low  
**Dependency:** Editor content

**Phase 3 Testing:**
```
[ ] Component library populated
[ ] Can drag any component
[ ] Properties panel appears
[ ] Can edit properties
[ ] Changes appear in editor
[ ] Preview opens in new window
[ ] Preview shows correct HTML/CSS
```

---

### PHASE 4: Settings & Polish (1 day)

#### 4.1: Settings Dialog
```javascript
document.getElementById('btnSettings').addEventListener('click', function() {
    // Create modal dialog
    const dialog = `
        <div class="modal">
            <h2>Settings</h2>
            <label>
                Auto-save interval (seconds):
                <input type="number" id="autoSaveInterval" value="30">
            </label>
            <button onclick="saveSettings()">Save</button>
            <button onclick="closeModal()">Cancel</button>
        </div>
    `;
    
    // Show modal
    showModal(dialog);
});

function saveSettings() {
    const interval = document.getElementById('autoSaveInterval').value;
    bridge.setConfig('autoSaveInterval', interval, function(response) {
        showToast('Settings saved');
        closeModal();
    });
}
```

**Effort:** 4 hours  
**Risk:** Low  
**Dependency:** Config service (ready), Modal UI

#### 4.2: Keyboard Shortcuts
```javascript
// Wire actual shortcuts (bridges ready!)
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.code === 'KeyS') {
        e.preventDefault();
        saveTemplate();
    }
    if (e.ctrlKey && e.code === 'KeyN') {
        e.preventDefault();
        createNewTemplate();
    }
    if (e.ctrlKey && e.code === 'KeyO') {
        e.preventDefault();
        document.getElementById('btnOpen').click();
    }
});

// Also wire to plugin system for customization
// bridge.handleShortcut('save');
```

**Effort:** 2 hours  
**Risk:** Low  
**Dependency:** Shortcuts manager (ready)

#### 4.3: Error Recovery
```javascript
// Already have toast system, just need to use it
bridge.messageReceived.connect(function(method, data) {
    if (method === 'errorOccurred') {
        const error = JSON.parse(data);
        showErrorToast(error);
    }
});

// Also handle JS errors
window.onerror = function(message, source, line, col, error) {
    console.error('Error:', message);
    bridge.reportError(message, {
        source: source,
        line: line,
        column: col
    });
};
```

**Effort:** 2 hours  
**Risk:** Low  
**Dependency:** Error handler (ready)

**Phase 4 Testing:**
```
[ ] Settings dialog opens
[ ] Can change settings
[ ] Settings persist
[ ] Ctrl+S saves template
[ ] Ctrl+N creates new
[ ] Ctrl+O opens template
[ ] Errors show as toasts
```

---

## IMPLEMENTATION ORDER

### Week 1 (5 days)
- **Day 1:** Phase 1.1 + 1.2 (GrapeJS integration)
- **Day 2:** Phase 1.3 + 1.4 (Save/Load flow)
- **Day 3:** Phase 2 (Template operations)
- **Day 4:** Phase 3.1 + 3.2 (Components + properties)
- **Day 5:** Phase 3.3 + Phase 4 (Preview + Polish)

### Week 2 (3 days)
- **Day 1:** Testing, bug fixes, performance
- **Day 2:** User acceptance testing in Anki
- **Day 3:** Documentation, cleanup

### Week 3 (3 days)
- **Day 1-3:** Plan 20 - Onboarding System (now it makes sense!)

---

## SUCCESS CRITERIA

### After Phase 1:
- [ ] User can see GrapeJS editor
- [ ] User can drag components to canvas
- [ ] User can save template to disk
- [ ] User can load template from disk

### After Phase 2:
- [ ] User can create new template
- [ ] User can manage multiple templates
- [ ] User can undo/redo changes
- [ ] Keyboard shortcuts work

### After Phase 3:
- [ ] User can edit component properties
- [ ] Preview shows live result
- [ ] Component library is complete
- [ ] All Anki-specific components available

### After Phase 4:
- [ ] User can customize settings
- [ ] Errors are handled gracefully
- [ ] Workflow is smooth and intuitive
- [ ] All unit tests pass

---

## RISK ASSESSMENT

| Phase | Risk | Mitigation |
|-------|------|-----------|
| Phase 1 | Medium (GrapeJS complexity) | Start small, test incrementally |
| Phase 2 | Low (APIs ready) | Use existing bridge methods |
| Phase 3 | Medium (lots of components) | Use modular structure, test each |
| Phase 4 | Low (mostly wiring) | Rely on existing systems |

---

## GO/NO-GO DECISION

**Current Status:** Ready to proceed ✅

- Backend complete ✅
- Bridge implemented ✅
- HTML skeleton ready ✅
- Test suite passing ✅
- Architecture sound ✅

**Recommendation:** BEGIN PHASE 1 IMMEDIATELY

**Not Recommended:** Starting Plan 20 (Onboarding) without Phase 1-4

---

## RESOURCE REQUIREMENTS

- **Developer:** 1 (can parallelize if needed)
- **Time:** ~11 days total
- **Libraries:** GrapeJS (free, MIT license)
- **Infrastructure:** None additional
- **Testing:** Manual in Anki

---

## NEXT IMMEDIATE STEPS

1. **Create feature branch:** `feature/grapesjs-integration`
2. **Add GrapeJS library to index.html**
3. **Initialize editor in JavaScript**
4. **Test GrapeJS editor loads**
5. **Commit and test in Anki**

**Time to first working editor:** 4-6 hours

---

**Generated:** February 1, 2026  
**Status:** Ready for implementation  
**Next Review:** After Phase 1 completion
