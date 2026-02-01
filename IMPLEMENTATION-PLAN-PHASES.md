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

## ADDON GOAL & VISION

### Purpose
The **Anki Template Designer** provides a visual editor for modifying Anki note type templates using drag-and-drop.

### Core Workflow
1. **Open Dialog** → Auto-loads last edited template (or first available)
2. **Select Template** → Dropdown to switch between note type templates
3. **Edit Visually** → Drag components, edit properties in GrapeJS
4. **Save Changes** → Persist to Anki note type
5. **Preview** → See card rendering with sample data

### Key Design Decisions
- **NO "Create Template" button** - Templates are tied to Anki note types
- **NO "New" or "Open" buttons** - Use dropdown selector instead
- **Auto-load last template** - Seamless workflow continuation
- **Direct Anki integration** - Changes save to note type system

### Required UI Actions (7 total)
| Action | Control | Description |
|--------|---------|-------------|
| **Select Template** | Dropdown | Switch between Anki templates |
| **Save** | Button | Save changes to Anki |
| **Undo** | Button | Undo last action |
| **Redo** | Button | Redo action |
| **Preview** | Button | Show card rendering |
| **Export** | Button | Export HTML/CSS |
| **Settings** | Button | Open preferences |

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
    const templateId = document.getElementById('templateSelector').value;
    
    const template = {
        id: templateId,
        html: html,
        css: css,
        components: components
    };
    
    bridge.saveTemplate(JSON.stringify(template), function(response) {
        try {
            const result = JSON.parse(response);
            if (result.success) {
                showToast('Saved to Anki note type');
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

#### 1.4: Template Selector & Auto-Load
```javascript
function initTemplateSelector() {
    if (!bridge) return;
    
    bridge.listTemplates(function(response) {
        try {
            const result = JSON.parse(response);
            const templates = result.data || [];
            const select = document.getElementById('templateSelector');
            
            // Populate dropdown
            select.innerHTML = '';
            templates.forEach(t => {
                const option = document.createElement('option');
                option.value = t.id;
                option.textContent = t.name;
                select.appendChild(option);
            });
            
            // Auto-load: last opened or first available
            const lastOpened = localStorage.getItem('lastOpenedTemplate');
            const templateId = lastOpened && templates.find(t => t.id === lastOpened)
                ? lastOpened 
                : templates[0]?.id;
            
            if (templateId) {
                select.value = templateId;
                loadTemplate(templateId);
            }
        } catch (e) {
            console.error('Template list error:', e);
        }
    });
}

function loadTemplate(templateId) {
    if (!bridge || !editor) return;
    
    bridge.loadTemplate(templateId, function(response) {
        try {
            const result = JSON.parse(response);
            if (result.success) {
                const template = result.data;
                editor.setComponents(template.components || []);
                editor.setStyle(template.css || '');
                localStorage.setItem('lastOpenedTemplate', templateId);
                showToast('Template loaded');
            } else {
                showErrorToast(result);
            }
        } catch (e) {
            console.error('Load error:', e);
        }
    });
}

// Wire dropdown change event
document.getElementById('templateSelector').addEventListener('change', function() {
    loadTemplate(this.value);
});
```

**Effort:** 4 hours  
**Risk:** Medium  
**Dependency:** GrapeJS, Bridge, Template service

**Phase 1 Testing:**
```
[ ] GrapeJS editor visible in canvas
[ ] Template dropdown populated with Anki note types
[ ] Last opened template auto-loads on dialog open
[ ] Can switch templates via dropdown
[ ] Can drag components from sidebar to canvas
[ ] Can edit component properties
[ ] Save persists to Anki note type
[ ] Editor state persists (browser local storage for last opened)
```

---

### PHASE 2: Template Workflow (1 day)

#### 2.1: Undo/Redo Integration
```javascript
// GrapeJS has built-in undo manager
let previousState = '';

editor.on('change:all', function() {
    const state = editor.getHtml();
    if (previousState !== state) {
        window.pushUndoState(previousState, state, 'Editor change');
        previousState = state;
    }
});

// Connect undo/redo buttons
document.getElementById('btnUndo').addEventListener('click', function() {
    editor.UndoManager.undo();
    bridge.undo(response => console.log('Undo:', response));
});

document.getElementById('btnRedo').addEventListener('click', function() {
    editor.UndoManager.redo();
    bridge.redo(response => console.log('Redo:', response));
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

#### 2.2: Export Template
```javascript
document.getElementById('btnExport').addEventListener('click', function() {
    if (!editor) return;
    
    const html = editor.getHtml();
    const css = editor.getCss();
    
    // Create downloadable file
    const fullHtml = `<!DOCTYPE html>
<html>
<head>
    <style>${css}</style>
</head>
<body>${html}</body>
</html>`;
    
    const blob = new Blob([fullHtml], {type: 'text/html'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'template-export.html';
    a.click();
    URL.revokeObjectURL(url);
    
    showToast('Template exported');
});
```

**Effort:** 2 hours  
**Risk:** Low  
**Dependency:** Editor content

#### 2.3: Preview System
```javascript
document.getElementById('btnPreview').addEventListener('click', function() {
    if (!editor) return;
    
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
    
    showToast('Preview opened');
});
```

**Effort:** 2 hours  
**Risk:** Low  
**Dependency:** Editor content

**Phase 2 Testing:**
```
[ ] Undo reverts last change
[ ] Redo restores undone change
[ ] Export downloads HTML file
[ ] Preview opens in new window
[ ] Preview shows correct HTML/CSS
```

---

### PHASE 3: Component System (2-3 days)

#### 3.0: Component Library Cleanup
Before adding new components, clean up unsuitable ones:

```javascript
// REMOVE these blocks - not compatible with Anki:
const blocksToRemove = [
    'modal-container',  // Modals don't work in Anki cards
    'drawer',           // Navigation drawer irrelevant
    'tab-container',    // Requires JavaScript
    'tabs-nav',         // Requires JavaScript
    'accordion',        // JavaScript-dependent
    'stepper',          // Multi-step flows irrelevant
    'masonry',          // Too complex for flashcards
    'frame'             // Device mockup confuses purpose
];

// In layout.js, remove these block registrations
```

**Effort:** 2 hours  
**Risk:** Low  
**Dependency:** None

#### 3.1: Add Missing Container Block
```javascript
// Add to layout.js
bm.add('container', {
    label: 'Container',
    category,
    content: {
        tagName: 'div',
        classes: ['atd-container'],
        style: {
            'max-width': '800px',
            margin: '0 auto',
            padding: '16px'
        },
        components: []
    }
});
```

**Effort:** 30 minutes  
**Risk:** Low

#### 3.2: Anki-Specific Components
Create new category for Anki template syntax:

```javascript
// Create anki-blocks.js
export function registerAnkiBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Anki Fields';
    
    // Field Placeholder
    bm.add('anki-field', {
        label: 'Field',
        category,
        content: {
            tagName: 'span',
            classes: ['anki-field'],
            content: '{{FieldName}}',
            editable: true,
            style: {
                'background-color': '#e3f2fd',
                padding: '2px 6px',
                'border-radius': '4px',
                'font-family': 'monospace'
            }
        }
    });
    
    // Cloze Deletion
    bm.add('cloze', {
        label: 'Cloze',
        category,
        content: {
            tagName: 'span',
            classes: ['anki-cloze'],
            content: '{{c1::answer}}',
            editable: true,
            style: {
                'background-color': '#fff3e0',
                padding: '2px 6px',
                'border-radius': '4px',
                'font-family': 'monospace'
            }
        }
    });
    
    // Hint Field
    bm.add('hint-field', {
        label: 'Hint',
        category,
        content: {
            tagName: 'a',
            classes: ['anki-hint'],
            content: '{{hint:FieldName}}',
            style: {
                color: '#1976d2',
                cursor: 'pointer',
                'text-decoration': 'underline'
            }
        }
    });
    
    // Type Answer
    bm.add('type-answer', {
        label: 'Type Answer',
        category,
        content: {
            tagName: 'div',
            classes: ['anki-type-answer'],
            content: '{{type:FieldName}}',
            style: {
                padding: '8px',
                border: '1px solid #ccc',
                'border-radius': '4px',
                'font-family': 'monospace'
            }
        }
    });
    
    // Tags Display
    bm.add('tags-display', {
        label: 'Tags',
        category,
        content: {
            tagName: 'div',
            classes: ['anki-tags'],
            content: '{{Tags}}',
            style: {
                'font-size': '12px',
                color: '#666'
            }
        }
    });
}
```

**Effort:** 4 hours  
**Risk:** Low  
**Dependency:** GrapeJS initialized

#### 3.3: Properties Panel
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

**Phase 3 Testing:**
```
[ ] Component library populated
[ ] Can drag any component
[ ] Properties panel appears on selection
[ ] Can edit properties
[ ] Changes appear in editor
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
    if (e.ctrlKey && e.code === 'KeyZ' && !e.shiftKey) {
        e.preventDefault();
        document.getElementById('btnUndo').click();
    }
    if ((e.ctrlKey && e.code === 'KeyY') || (e.ctrlKey && e.shiftKey && e.code === 'KeyZ')) {
        e.preventDefault();
        document.getElementById('btnRedo').click();
    }
    if (e.ctrlKey && e.code === 'KeyP') {
        e.preventDefault();
        document.getElementById('btnPreview').click();
    }
    if (e.ctrlKey && e.code === 'KeyE') {
        e.preventDefault();
        document.getElementById('btnExport').click();
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
[ ] Ctrl+Z undoes
[ ] Ctrl+Y redoes
[ ] Ctrl+P opens preview
[ ] Ctrl+E exports
[ ] Errors show as toasts
```

---

## IMPLEMENTATION ORDER

### Week 1 (5 days)
- **Day 1:** Phase 1.1 + 1.2 (GrapeJS integration)
- **Day 2:** Phase 1.3 + 1.4 (Save button + Template selector/auto-load)
- **Day 3:** Phase 2 (Undo/Redo, Export, Preview)
- **Day 4:** Phase 3.1 + 3.2 (Components + properties panel)
- **Day 5:** Phase 4 (Settings + keyboard shortcuts)

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
- [ ] Template dropdown shows Anki note types
- [ ] Last opened template auto-loads on dialog open
- [ ] User can switch templates via dropdown
- [ ] User can drag components to canvas
- [ ] User can save template to Anki note type
- [ ] "Last opened" state persists

### After Phase 2:
- [ ] User can undo/redo changes
- [ ] User can export template as HTML
- [ ] User can preview template
- [ ] Keyboard shortcuts work (Ctrl+S, Ctrl+Z, Ctrl+Y)

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
3. **Add template selector dropdown to toolbar**
4. **Initialize editor in JavaScript**
5. **Implement auto-load of last template**
6. **Test in Anki**

**Time to first working editor with auto-load:** 6-8 hours

---

**Generated:** February 1, 2026  
**Status:** Ready for implementation  
**Next Review:** After Phase 1 completion
