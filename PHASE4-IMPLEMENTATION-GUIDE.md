# Phase 4 Implementation Guide - Critical Issues

**Date:** January 17, 2026  
**Scope:** Detailed implementation strategies for high-priority Phase 4 issues

---

## Overview

This document provides concrete implementation strategies for the 4 critical Phase 4 issues:
1. **Issue #15:** Component Search & Discovery
2. **Issue #17:** Template Validation & Warnings
3. **Issue #8.1:** Backup & Version Management
4. **Issue #40:** Data Loss Prevention

Each includes architecture, code examples, and integration points.

---

## Issue #15: Component Search Implementation

### Architecture

**Data Structure:**
```javascript
// In blocks/index.js - Create search index
const componentIndex = {
  'anki-field': {
    label: 'Anki Field',
    category: 'Anki Special',
    tags: ['field', 'data', 'anki'],
    description: 'Insert an Anki card field',
    icon: 'fa fa-bookmark',
    keywords: 'field question answer front back'
  },
  'layout-container': {
    label: 'Container',
    category: 'Layout & Structure',
    tags: ['layout', 'container', 'wrapper'],
    description: 'A container for organizing content',
    icon: 'fa fa-square',
    keywords: 'container box wrapper div'
  },
  // ... 110 more components
};

// Search function
function searchComponents(query) {
  const results = Object.entries(componentIndex)
    .filter(([id, comp]) => {
      const searchText = `${comp.label} ${comp.category} ${comp.tags.join(' ')} ${comp.keywords}`.toLowerCase();
      return searchText.includes(query.toLowerCase());
    })
    .map(([id, comp]) => ({ id, ...comp }))
    .sort((a, b) => {
      // Rank by label match first
      if (a.label.toLowerCase().startsWith(query.toLowerCase())) return -1;
      return 0;
    });
  
  return results;
}
```

**UI Component:**
```html
<!-- In web/index.html - Add search to blocks panel -->
<div class="blocks-container">
  <div class="blocks-search">
    <input 
      type="text" 
      id="blocks-search" 
      class="blocks-search__input"
      placeholder="Search 112 components..."
      aria-label="Search components"
    >
    <button class="blocks-search__clear" title="Clear search">×</button>
  </div>
  
  <div class="blocks-search__results" style="display:none;">
    <!-- Results rendered here -->
  </div>
  
  <div class="blocks-search__original">
    <!-- Original blocks panel (shown when no search) -->
  </div>
</div>
```

**CSS:**
```css
.blocks-search {
  display: flex;
  gap: 8px;
  padding: 8px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.blocks-search__input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 14px;
}

.blocks-search__input::placeholder {
  color: var(--text-secondary);
}

.blocks-search__input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(77, 171, 247, 0.1);
}

.blocks-search__clear {
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 16px;
  transition: color 0.2s;
}

.blocks-search__clear:hover {
  color: var(--text-primary);
}

.blocks-search__results {
  overflow-y: auto;
  max-height: 300px;
}

.blocks-search-result {
  padding: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.blocks-search-result:hover {
  background: var(--bg-hover);
}
```

**JavaScript Implementation:**
```javascript
// In designer.js - Add after blocks registration
function initializeComponentSearch() {
  const searchInput = document.getElementById('blocks-search');
  const searchResults = document.querySelector('.blocks-search__results');
  const originalBlocks = document.querySelector('.blocks-search__original');
  
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.trim();
    
    if (!query) {
      // Show original blocks
      searchResults.style.display = 'none';
      originalBlocks.style.display = '';
      return;
    }
    
    // Search
    const results = searchComponents(query);
    
    if (results.length === 0) {
      searchResults.innerHTML = `
        <div class="blocks-search-empty">
          No components found. Try:
          <ul>
            <li>Different keywords</li>
            <li>Browse all components</li>
            <li>Check documentation</li>
          </ul>
        </div>
      `;
    } else {
      searchResults.innerHTML = results.map(comp => `
        <div class="blocks-search-result" data-id="${comp.id}">
          <div class="blocks-search-result__label">
            <span class="blocks-search-result__icon">
              <i class="${comp.icon}"></i>
            </span>
            <span>${comp.label}</span>
          </div>
          <div class="blocks-search-result__category">${comp.category}</div>
          <div class="blocks-search-result__description">${comp.description}</div>
        </div>
      `).join('');
      
      // Add click handlers
      searchResults.querySelectorAll('.blocks-search-result').forEach(el => {
        el.addEventListener('click', () => {
          const id = el.dataset.id;
          const block = editor.BlockManager.get(id);
          if (block) {
            editor.addComponent(block.content);
            searchInput.value = '';
            searchResults.style.display = 'none';
            originalBlocks.style.display = '';
          }
        });
      });
    }
    
    // Show results
    searchResults.style.display = '';
    originalBlocks.style.display = 'none';
  });
  
  // Clear button
  document.querySelector('.blocks-search__clear').addEventListener('click', () => {
    searchInput.value = '';
    searchResults.style.display = 'none';
    originalBlocks.style.display = '';
  });
}
```

---

## Issue #17: Template Validation Implementation

### Architecture

**Validation Engine:**
```javascript
// In web/validators/template-validator.js
class TemplateValidator {
  constructor(editor) {
    this.editor = editor;
    this.issues = [];
  }
  
  validate(projectData) {
    this.issues = [];
    
    // Check required fields
    this.checkRequiredFields(projectData);
    
    // Check Anki syntax
    this.checkAnkiSyntax(projectData);
    
    // Check CSS validity
    this.checkCSSValidity(projectData);
    
    // Check accessibility
    this.checkAccessibility(projectData);
    
    // Check performance
    this.checkPerformance(projectData);
    
    return {
      valid: this.issues.every(i => i.severity !== 'error'),
      errors: this.issues.filter(i => i.severity === 'error'),
      warnings: this.issues.filter(i => i.severity === 'warning'),
      all: this.issues
    };
  }
  
  checkRequiredFields(projectData) {
    const hasField = projectData.components?.some(c => 
      c.attributes?.['data-anki-field']
    );
    
    if (!hasField) {
      this.issues.push({
        id: 'NO_FIELDS',
        severity: 'error',
        message: 'Template must use at least one Anki field',
        hint: 'Add an Anki Field block from the Blocks panel',
        component: null
      });
    }
  }
  
  checkAnkiSyntax(projectData) {
    projectData.components?.forEach((comp, idx) => {
      if (comp.type === 'anki-cloze') {
        const text = comp.content;
        if (!text || text.trim().length === 0) {
          this.issues.push({
            id: 'EMPTY_CLOZE',
            severity: 'error',
            message: 'Cloze block must have content',
            hint: 'Add text or a field to the Cloze block',
            component: idx
          });
        }
      }
    });
  }
  
  checkCSSValidity(projectData) {
    // Parse CSS from projectData.css
    try {
      const css = projectData.css || '';
      // Basic CSS parsing
      if (css.includes('{') && !css.includes('}')) {
        this.issues.push({
          id: 'INVALID_CSS',
          severity: 'error',
          message: 'CSS has syntax errors',
          hint: 'Check your CSS - missing closing brace }',
          component: null
        });
      }
    } catch (e) {
      this.issues.push({
        id: 'CSS_ERROR',
        severity: 'error',
        message: 'CSS parsing error: ' + e.message,
        hint: 'Review your CSS for syntax errors',
        component: null
      });
    }
  }
  
  checkAccessibility(projectData) {
    projectData.components?.forEach((comp, idx) => {
      // Check for images without alt text
      if (comp.tagName === 'img' && !comp.attributes?.alt) {
        this.issues.push({
          id: 'MISSING_ALT_TEXT',
          severity: 'warning',
          message: 'Image missing alt text',
          hint: 'Add alt text for accessibility',
          component: idx
        });
      }
      
      // Check for buttons without labels
      if (comp.tagName === 'button' && !comp.content) {
        this.issues.push({
          id: 'UNLABELED_BUTTON',
          severity: 'warning',
          message: 'Button has no label text',
          hint: 'Add text or aria-label to button',
          component: idx
        });
      }
    });
  }
  
  checkPerformance(projectData) {
    const cssSize = (projectData.css || '').length;
    const htmlSize = (projectData.html || '').length;
    
    if (cssSize > 50000) {
      this.issues.push({
        id: 'LARGE_CSS',
        severity: 'warning',
        message: 'CSS is very large (50KB+)',
        hint: 'Consider simplifying styles',
        component: null
      });
    }
    
    if (htmlSize > 100000) {
      this.issues.push({
        id: 'LARGE_HTML',
        severity: 'warning',
        message: 'HTML is very large (100KB+)',
        hint: 'Consider removing unused components',
        component: null
      });
    }
  }
}
```

**UI Component - Validation Panel:**
```html
<!-- New tab in right sidebar -->
<div class="validation-panel" style="display:none;">
  <div class="validation-header">
    <h3>Template Validation</h3>
    <span class="validation-count">3 issues</span>
  </div>
  
  <div class="validation-list">
    <!-- Issues rendered here -->
  </div>
</div>
```

**Integration with Save:**
```javascript
// In designer.js - Override save
window.saveProject = function() {
  if (!editor) return;
  
  const projectData = editor.getProjectData();
  
  // Validate
  const validator = new TemplateValidator(editor);
  const result = validator.validate(projectData);
  
  // Show validation panel
  showValidationPanel(result);
  
  // If errors, prevent save
  if (!result.valid) {
    showToast('❌ ' + result.errors.length + ' errors found', 'error');
    // Highlight problematic components
    result.errors.forEach(issue => {
      if (issue.component !== null) {
        highlightComponent(issue.component);
      }
    });
    return;
  }
  
  // If only warnings, allow save
  if (result.warnings.length > 0) {
    showToast('⚠️ ' + result.warnings.length + ' warnings', 'warning');
  }
  
  // Save
  if (window.bridge) {
    window.bridge.saveProject(JSON.stringify(projectData));
  }
};
```

---

## Issue #8.1: Backup Manager Implementation

### Architecture

**Backup System:**
```javascript
// In web/backup-manager.js
class BackupManager {
  constructor(maxBackups = 20) {
    this.maxBackups = maxBackups;
    this.storageKey = 'anki_template_backups';
  }
  
  createBackup(projectData, name = null) {
    const backups = this.getBackups();
    
    const backup = {
      id: Date.now(),
      name: name || this.generateName(),
      timestamp: new Date().toISOString(),
      size: JSON.stringify(projectData).length,
      data: projectData
    };
    
    backups.unshift(backup);
    
    // Keep only maxBackups
    if (backups.length > this.maxBackups) {
      backups.pop();
    }
    
    localStorage.setItem(this.storageKey, JSON.stringify(backups));
    return backup;
  }
  
  getBackups() {
    const stored = localStorage.getItem(this.storageKey);
    return stored ? JSON.parse(stored) : [];
  }
  
  restoreBackup(backupId) {
    const backups = this.getBackups();
    const backup = backups.find(b => b.id === backupId);
    
    if (!backup) {
      throw new Error('Backup not found');
    }
    
    return backup.data;
  }
  
  deleteBackup(backupId) {
    const backups = this.getBackups();
    const filtered = backups.filter(b => b.id !== backupId);
    localStorage.setItem(this.storageKey, JSON.stringify(filtered));
  }
  
  exportBackup(backupId) {
    const backup = this.getBackups().find(b => b.id === backupId);
    if (!backup) return null;
    
    const json = JSON.stringify(backup.data, null, 2);
    return new Blob([json], { type: 'application/json' });
  }
  
  generateName() {
    const now = new Date();
    return now.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  }
}
```

**Backup Panel UI:**
```html
<div class="backup-panel" style="display:none;">
  <div class="backup-header">
    <h3>Template History</h3>
    <button class="backup-actions__new">New Backup</button>
  </div>
  
  <div class="backup-list">
    <!-- Backups rendered here -->
  </div>
  
  <div class="backup-info">
    <span>Using <strong>X KB</strong> of storage</span>
  </div>
</div>
```

**Integration:**
```javascript
// Auto-backup on every change
let autoBackupTimeout;
editor.on('component:update', () => {
  clearTimeout(autoBackupTimeout);
  autoBackupTimeout = setTimeout(() => {
    const backupManager = new BackupManager();
    backupManager.createBackup(editor.getProjectData());
    updateBackupPanel();
  }, 5000); // Wait 5 seconds after last change
});

function updateBackupPanel() {
  const backupManager = new BackupManager();
  const backups = backupManager.getBackups();
  const listEl = document.querySelector('.backup-list');
  
  listEl.innerHTML = backups.map(backup => `
    <div class="backup-item" data-id="${backup.id}">
      <div class="backup-item__name">${backup.name}</div>
      <div class="backup-item__time">${formatTime(backup.timestamp)}</div>
      <div class="backup-item__size">${formatSize(backup.size)}</div>
      <div class="backup-item__actions">
        <button class="btn-sm" data-action="restore">Restore</button>
        <button class="btn-sm" data-action="compare">Compare</button>
        <button class="btn-sm" data-action="export">Export</button>
        <button class="btn-sm" data-action="delete">Delete</button>
      </div>
    </div>
  `).join('');
  
  // Add event handlers
  listEl.querySelectorAll('[data-action]').forEach(btn => {
    btn.addEventListener('click', handleBackupAction);
  });
}
```

---

## Issue #40: Data Loss Prevention

### Architecture

**Unsaved Changes Indicator:**
```javascript
// Track unsaved changes
let hasUnsavedChanges = false;

editor.on('component:add', () => {
  hasUnsavedChanges = true;
  updateSaveIndicator();
});

editor.on('component:update', () => {
  hasUnsavedChanges = true;
  updateSaveIndicator();
});

editor.on('component:remove', () => {
  hasUnsavedChanges = true;
  updateSaveIndicator();
});

// On successful save
window.bridge.on('save:success', () => {
  hasUnsavedChanges = false;
  updateSaveIndicator();
});

function updateSaveIndicator() {
  const indicator = document.querySelector('.save-indicator');
  if (hasUnsavedChanges) {
    indicator.classList.add('unsaved');
    indicator.title = 'Unsaved changes';
  } else {
    indicator.classList.remove('unsaved');
    indicator.title = 'All changes saved';
  }
}
```

**Browser Unload Warning:**
```javascript
// Warn before closing with unsaved changes
window.addEventListener('beforeunload', (e) => {
  if (hasUnsavedChanges) {
    e.preventDefault();
    e.returnValue = '';
    return '';
  }
});

// Warn before destructive actions
function deleteComponent() {
  if (!editor.getSelected()) return;
  
  showConfirmDialog({
    title: 'Delete Component?',
    message: 'This cannot be undone.',
    confirmText: 'Delete',
    cancelText: 'Cancel',
    onConfirm: () => {
      editor.getSelected().remove();
    }
  });
}
```

**Visual Indicator:**
```css
.save-indicator {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--success-color);
  margin-right: 8px;
  transition: background 0.3s;
}

.save-indicator.unsaved {
  background: var(--warning-color);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}
```

---

## Integration Checklist

### For Issue #15 (Component Search)
- [ ] Create search index from all registered blocks
- [ ] Add search input to blocks panel
- [ ] Implement search/filter function
- [ ] Add search styling and animations
- [ ] Keyboard navigation (arrows, Enter, Escape)
- [ ] Mobile responsive search
- [ ] Accessibility testing (screen reader, ARIA labels)
- [ ] Performance testing with 112 components

### For Issue #17 (Template Validation)
- [ ] Create validator class with all rule checks
- [ ] Add validation panel UI
- [ ] Hook validator to save button
- [ ] Highlight problematic components
- [ ] Show error/warning toast notifications
- [ ] Add helpful hints for each error
- [ ] Test with invalid templates
- [ ] Accessibility testing

### For Issue #8.1 (Backup Manager)
- [ ] Create backup manager class
- [ ] Add backup panel UI
- [ ] Hook auto-backup to editor changes
- [ ] Implement restore functionality
- [ ] Test localStorage limits
- [ ] Add compare feature
- [ ] Add export functionality
- [ ] Performance test with 20 backups

### For Issue #40 (Data Loss Prevention)
- [ ] Add unsaved changes tracking
- [ ] Add save indicator UI
- [ ] Hook beforeunload warning
- [ ] Add confirmation dialogs
- [ ] Test with large templates
- [ ] Test on various browsers
- [ ] Accessibility testing

---

## Testing Strategy

**Unit Tests:**
- Validator rule functions
- Backup CRUD operations
- Search algorithm
- Unsaved changes tracking

**Integration Tests:**
- Save with validation
- Backup creation on changes
- Restore from backup
- Search and drag component

**E2E Tests:**
- Complete user workflow with validation
- Undo/redo with backup recovery
- Component search and drag
- Data loss prevention

**Performance Tests:**
- Search with 112 components
- Validation of large templates
- Storage with 20 backups
- Backup restoration speed

---

## Success Criteria

✅ **Issue #15 Complete When:**
- Search finds any component < 100ms
- Users can find component without scrolling
- Keyboard navigation works smoothly
- Works on mobile and desktop

✅ **Issue #17 Complete When:**
- All validation rules pass tests
- Errors prevent save (as designed)
- Warnings allow save with hint
- Error messages are clear to users

✅ **Issue #8.1 Complete When:**
- Backups created automatically
- Users can restore any backup
- Compare shows differences
- Export downloads valid JSON

✅ **Issue #40 Complete When:**
- Unsaved indicator visible
- Warning shows before closing
- Confirmation prevents accidents
- No data loss in any scenario

---

## Estimated Timeline

- **Component Search:** 2-3 days
- **Template Validation:** 3-4 days
- **Backup Manager:** 3-4 days
- **Data Loss Prevention:** 2-3 days
- **Testing & Polish:** 2-3 days

**Total Phase 4:** ~2-3 weeks of development
