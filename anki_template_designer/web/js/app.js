/**
 * Main Application
 * Initialization and event handlers
 */

// Template Management
let currentTemplateId = null;
let hasUnsavedChanges = false;
let loadedTemplates = [];

// Side Management (Front/Back)
let currentSide = 'front'; // 'front', 'back', or 'preview'
let templateSideState = {}; // { [templateId]: { front: {...}, back: {...} } }

// Initialize side state for a template
function initializeSideState(templateId) {
    if (!templateSideState[templateId]) {
        templateSideState[templateId] = {
            front: {
                components: [],
                selectedComponent: null,
                history: [],
                historyIndex: -1
            },
            back: {
                components: [],
                selectedComponent: null,
                history: [],
                historyIndex: -1
            }
        };
    }
    return templateSideState[templateId];
}

// Save current side state before switching
function saveSideState() {
    if (!currentTemplateId) return;
    
    const state = initializeSideState(currentTemplateId);
    const sideState = state[currentSide];
    
    // Save current canvas components and selection
    if (window.designCanvas) {
        sideState.components = window.designCanvas.getComponents?.() || [];
        sideState.selectedComponent = window.designCanvas.getSelected?.() || null;
    }
    
    console.log(`[saveSideState] Saved ${currentSide} state for ${currentTemplateId}`);
}

// Load side state after switching
function loadSideState() {
    if (!currentTemplateId) return;
    
    const state = initializeSideState(currentTemplateId);
    const sideState = state[currentSide];
    
    // Load components and selection into canvas
    if (window.designCanvas) {
        window.designCanvas.setComponents?.(sideState.components || []);
        if (sideState.selectedComponent) {
            window.designCanvas.selectComponent?.(sideState.selectedComponent);
        }
    }
    
    console.log(`[loadSideState] Loaded ${currentSide} state for ${currentTemplateId}`);
}

function loadTemplates() {
    console.log('[loadTemplates] Starting template load...');
    
    return new Promise((resolve) => {
        console.log('[loadTemplates] Promise created');
        
        if (!window.bridge) {
            console.error('[loadTemplates] Bridge not available');
            resolve();
            return;
        }
        
        if (!window.bridge.getNoteTypes) {
            console.error('[loadTemplates] getNoteTypes method not available');
            resolve();
            return;
        }
        
        console.log('[loadTemplates] Calling bridge.getNoteTypes()');
        
        window.bridge.getNoteTypes((response) => {
            console.log('[loadTemplates] Got getNoteTypes response:', response);
            console.log('[loadTemplates] Response type:', typeof response);
            console.log('[loadTemplates] Response.noteTypes:', response?.noteTypes);
            console.log('[loadTemplates] Response.noteTypes type:', typeof response?.noteTypes);
            
            // Try multiple ways to extract noteTypes
            let noteTypes = [];
            
            // Method 1: Direct noteTypes property
            if (response && Array.isArray(response.noteTypes)) {
                noteTypes = response.noteTypes;
                console.log('[loadTemplates] Found noteTypes via direct property');
            }
            // Method 2: Check if response itself is the array
            else if (Array.isArray(response)) {
                noteTypes = response;
                console.log('[loadTemplates] Found noteTypes as direct array');
            }
            // Method 3: Check if response is a string that needs parsing
            else if (typeof response === 'string') {
                try {
                    const parsed = JSON.parse(response);
                    noteTypes = parsed.noteTypes || (Array.isArray(parsed) ? parsed : []);
                    console.log('[loadTemplates] Found noteTypes after parsing string');
                } catch (e) {
                    console.error('[loadTemplates] Failed to parse response string:', e);
                }
            }
            
            console.log(`[loadTemplates] Extracted ${noteTypes.length} note types`);
            
            if (!noteTypes || noteTypes.length === 0) {
                console.warn('[loadTemplates] No note types available, resolving promise');
                loadedTemplates = [];
                const select = document.getElementById('templateSelect');
                if (select) {
                    select.innerHTML = '<option value="">No note types - create a card type first</option>';
                }
                resolve();
                return;
            }
            
            // Collect all templates from all note types
            const allTemplates = [];
            let processedCount = 0;
            console.log(`[loadTemplates] Processing ${noteTypes.length} note types`);
            
            noteTypes.forEach((noteType, ntIndex) => {
                console.log(`[loadTemplates] [${ntIndex + 1}/${noteTypes.length}] Processing: ${noteType.name}`);
                
                if (!window.bridge.getNoteTypeTemplates) {
                    console.error('[loadTemplates] getNoteTypeTemplates method not available');
                    processedCount++;
                    if (processedCount === noteTypes.length) {
                        console.log('[loadTemplates] All note types processed, resolving');
                        finalize();
                    }
                    return;
                }
                
                window.bridge.getNoteTypeTemplates(noteType.id, (templatesResponse) => {
                    console.log(`[loadTemplates] Got templates for ${noteType.name}:`, templatesResponse);
                    
                    let templates = [];
                    
                    // Handle string response (parse JSON)
                    if (typeof templatesResponse === 'string') {
                        try {
                            const parsed = JSON.parse(templatesResponse);
                            templates = parsed.templates || (Array.isArray(parsed) ? parsed : []);
                            console.log(`[loadTemplates] Parsed string response, found ${templates.length} templates`);
                        } catch (e) {
                            console.error(`[loadTemplates] Failed to parse template response: ${e.message}`);
                        }
                    }
                    // Handle object response
                    else if (templatesResponse && templatesResponse.templates) {
                        templates = templatesResponse.templates;
                    }
                    // Handle direct array response
                    else if (Array.isArray(templatesResponse)) {
                        templates = templatesResponse;
                    }
                    
                    console.log(`[loadTemplates] Extracted ${templates.length} templates for ${noteType.name}`);
                    
                    if (templates && templates.length > 0) {
                        templates.forEach((template, templateIndex) => {
                            const templateObj = {
                                id: `${noteType.id}:${template.ordinal || templateIndex}`,
                                name: `[${noteType.name}] ${template.name}`,
                                noteTypeId: noteType.id,
                                noteTypeName: noteType.name,
                                templateName: template.name,
                                templateData: template
                            };
                            allTemplates.push(templateObj);
                            console.log(`[loadTemplates]   + Added: ${templateObj.name}`);
                        });
                    } else {
                        console.log(`[loadTemplates] No templates for ${noteType.name}`);
                    }
                    
                    processedCount++;
                    console.log(`[loadTemplates] Progress: ${processedCount}/${noteTypes.length}`);
                    
                    // When all note types are processed
                    if (processedCount === noteTypes.length) {
                        console.log('[loadTemplates] All note types processed');
                        finalize();
                    }
                });
            });
            
            function finalize() {
                console.log(`[loadTemplates] Finalizing: ${allTemplates.length} templates collected`);
                loadedTemplates = allTemplates;
                
                const select = document.getElementById('templateSelect');
                if (select) {
                    select.innerHTML = '';
                    
                    if (allTemplates.length > 0) {
                        allTemplates.forEach((template) => {
                            const option = document.createElement('option');
                            option.value = template.id;
                            option.textContent = template.name;
                            select.appendChild(option);
                            console.log(`[loadTemplates] Dropdown: added ${template.name}`);
                        });
                        
                        // Auto-load last template
                        console.log('[loadTemplates] Loading last template from config');
                        loadLastTemplate();
                    } else {
                        select.innerHTML = '<option value="">No templates available</option>';
                        console.log('[loadTemplates] No templates to display');
                    }
                } else {
                    console.error('[loadTemplates] Template select element not found');
                }
                
                // Resolve the promise when done
                console.log('[loadTemplates] Resolving promise');
                resolve();
            }
        });
    });
}

function loadLastTemplate() {
    if (window.bridge && window.bridge.getConfig) {
        window.bridge.getConfig((config) => {
            const lastTemplate = config.lastLoadedTemplate || (loadedTemplates[0]?.id);
            if (lastTemplate) {
                loadTemplate(lastTemplate);
            }
        });
    }
}

function loadTemplate(templateId) {
    // Warn about unsaved changes
    if (hasUnsavedChanges) {
        const confirmed = confirm('You have unsaved changes. Loading a different template will discard them. Continue?');
        if (!confirmed) return;
    }
    
    console.log('Loading template:', templateId);
    
    // Find the template in loadedTemplates
    const templateObj = loadedTemplates.find(t => t.id === templateId);
    if (!templateObj) {
        console.error('Template not found in loaded templates:', templateId);
        window.debugUtils.showErrorToast('Error', 'Template not found', 'error');
        return;
    }
    
    // Use the template data directly
    console.log('Template object found:', templateObj);
    currentTemplateId = templateId;
    hasUnsavedChanges = false;
    updateUnsavedIndicator();
    
    // Initialize side state for this template
    initializeSideState(templateId);
    currentSide = 'front'; // Reset to front side
    loadSideState();
    updateSideTabUI();
    updateSideInfo();
    
    // Update dropdown selection
    const select = document.getElementById('templateSelect');
    if (select) {
        select.value = templateId;
    }
    
    // Save as last loaded
    if (window.bridge && window.bridge.setConfig) {
        window.bridge.setConfig('lastLoadedTemplate', templateId, () => {
            console.log('Last template saved to config');
        });
    }
    
    // Update undo/redo button states
    updateHistoryButtonStates();
    
    // Success notification
    window.debugUtils.showErrorToast('Loaded', `Template "${templateObj.name}" loaded`, 'success');
}

function updateUnsavedIndicator() {
    const indicator = document.getElementById('unsavedIndicator');
    if (indicator) {
        if (hasUnsavedChanges) {
            indicator.classList.remove('hidden');
        } else {
            indicator.classList.add('hidden');
        }
    }
}

// Switch between front/back/preview sides
function switchSide(side) {
    if (side === currentSide) return; // Already on this side
    
    console.log(`[switchSide] Switching from ${currentSide} to ${side}`);
    
    // Save current side state
    saveSideState();
    
    // Update current side
    currentSide = side;
    
    // Load new side state
    if (side !== 'preview') {
        loadSideState();
    }
    
    // Update UI
    updateSideTabUI();
    updateSideInfo();
    
    console.log(`[switchSide] Now on ${side} side`);
}

// Update side tab active states
function updateSideTabUI() {
    document.querySelectorAll('.side-tab').forEach(tab => {
        const tabSide = tab.getAttribute('data-side') || tab.getAttribute('data-mode');
        if (tabSide === currentSide) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
}

// Update side info display
function updateSideInfo() {
    const infoEl = document.getElementById('sideInfo');
    if (!infoEl) return;
    
    const labels = {
        'front': 'Front Side (Question)',
        'back': 'Back Side (Answer)',
        'preview': 'Preview Mode'
    };
    
    infoEl.textContent = labels[currentSide] || 'Unknown';
}

function markUnsavedChanges() {
    hasUnsavedChanges = true;
    updateUnsavedIndicator();
}

function markChangesAsSaved() {
    hasUnsavedChanges = false;
    updateUnsavedIndicator();
}

// Settings Modal Functions
function openSettingsModal() {
    const modal = document.getElementById('settingsModal');
    if (modal) {
        modal.classList.remove('hidden');
        loadCurrentSettings();
    }
}

function closeSettingsModal() {
    const modal = document.getElementById('settingsModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function loadCurrentSettings() {
    // Load settings from bridge
    if (window.bridge && window.bridge.getConfig) {
        window.bridge.getConfig((config) => {
            console.log('Loaded config:', config);
            document.getElementById('autoSaveCheckbox').checked = config.autoSave !== false;
            document.getElementById('autoSaveInterval').value = config.autoSaveIntervalSeconds || 30;
            document.getElementById('themeSelect').value = config.theme || 'system';
            document.getElementById('logLevelSelect').value = config.logLevel || 'INFO';
        });
    }
}

function saveSettings() {
    const autoSave = document.getElementById('autoSaveCheckbox').checked;
    const autoSaveInterval = parseInt(document.getElementById('autoSaveInterval').value) || 30;
    const theme = document.getElementById('themeSelect').value;
    const logLevel = document.getElementById('logLevelSelect').value;
    
    const settings = {
        autoSave: autoSave,
        autoSaveIntervalSeconds: autoSaveInterval,
        theme: theme,
        logLevel: logLevel
    };
    
    console.log('Saving settings:', settings);
    
    if (window.bridge && window.bridge.setConfig) {
        // Save each setting
        const settingsToSave = [
            { key: 'autoSave', value: String(autoSave) },
            { key: 'autoSaveIntervalSeconds', value: String(autoSaveInterval) },
            { key: 'theme', value: theme },
            { key: 'logLevel', value: logLevel }
        ];
        
        let saved = 0;
        settingsToSave.forEach((setting) => {
            window.bridge.setConfig(setting.key, setting.value, (result) => {
                saved++;
                if (saved === settingsToSave.length) {
                    window.debugUtils.showErrorToast('Settings', 'Settings saved successfully', 'success');
                    closeSettingsModal();
                }
            });
        });
    } else {
        window.debugUtils.showErrorToast('Error', 'Bridge not ready', 'error');
    }
}

// Toolbar button handlers
function handleSave() {
    console.log('Save clicked');
    
    if (!currentTemplateId) {
        window.debugUtils.showErrorToast('No Template', 'Select or create a template first', 'warning');
        return;
    }
    
    if (window.bridge && window.bridge.save_template) {
        window.debugUtils.showErrorToast('Save', 'Saving template...', 'info');
        window.bridge.save_template((result) => {
            console.log('Save result:', result);
            markChangesAsSaved();
            window.debugUtils.showErrorToast('Saved', 'Template saved successfully', 'success');
        });
    } else {
        window.debugUtils.showErrorToast('Error', 'Bridge not ready', 'error');
    }
}

function handleUndo() {
    console.log('Undo clicked');
    
    if (window.bridge && window.bridge.undo) {
        window.bridge.undo(() => {
            console.log('Undo performed');
            window.debugUtils.showErrorToast('Undo', 'Last action undone', 'info');
            updateHistoryButtonStates();
        });
    } else {
        window.debugUtils.showErrorToast('Error', 'Undo not available', 'error');
    }
}

function handleRedo() {
    console.log('Redo clicked');
    
    if (window.bridge && window.bridge.redo) {
        window.bridge.redo(() => {
            console.log('Redo performed');
            window.debugUtils.showErrorToast('Redo', 'Last action redone', 'info');
            updateHistoryButtonStates();
        });
    } else {
        window.debugUtils.showErrorToast('Error', 'Redo not available', 'error');
    }
}

function updateHistoryButtonStates() {
    if (window.bridge && window.bridge.getHistoryState) {
        window.bridge.getHistoryState((state) => {
            const undoBtn = document.getElementById('undoBtn');
            const redoBtn = document.getElementById('redoBtn');
            
            if (undoBtn) {
                undoBtn.disabled = !state.canUndo;
                undoBtn.style.opacity = state.canUndo ? '1' : '0.5';
            }
            
            if (redoBtn) {
                redoBtn.disabled = !state.canRedo;
                redoBtn.style.opacity = state.canRedo ? '1' : '0.5';
            }
            
            console.log('History state updated:', state);
        });
    }
}

function handlePreview() {
    console.log('Preview clicked');
    
    if (!currentTemplateId) {
        window.debugUtils.showErrorToast('No Template', 'Select or create a template first', 'warning');
        return;
    }
    
    openPreviewModal();
}

function openPreviewModal() {
    const modal = document.getElementById('previewModal');
    if (modal) {
        modal.classList.remove('hidden');
        loadPreview();
    }
}

function closePreviewModal() {
    const modal = document.getElementById('previewModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

let currentCardSide = 0; // 0 = front, 1 = back

function switchCardSide() {
    currentCardSide = currentCardSide === 0 ? 1 : 0;
    loadPreview();
}

function refreshPreview() {
    loadPreview();
}

function loadPreview() {
    if (!currentTemplateId) {
        console.warn('No template selected for preview');
        showPreviewContent('<div style="color: #e74c3c;">No template selected</div>');
        return;
    }
    
    console.log('Loading preview for template:', currentTemplateId);
    
    showPreviewContent('<div style="text-align: center; padding: 40px; color: #999;">Loading preview...</div>');
    
    // Get sample data
    if (window.bridge && window.bridge.getSampleData) {
        window.bridge.getSampleData(currentTemplateId, (sampleData) => {
            console.log('Sample data:', sampleData);
            
            // Render preview
            if (window.bridge && window.bridge.renderPreview) {
                window.bridge.renderPreview(currentTemplateId, currentCardSide, sampleData, (html) => {
                    console.log('Preview rendered');
                    showPreviewContent(html || '<div style="color: #999;">No preview available</div>');
                });
            }
        });
    }
}

function showPreviewContent(html) {
    const content = document.getElementById('previewContent');
    if (content) {
        content.innerHTML = `<div class="preview-content">${html}</div>`;
    }
}

function handleExport() {
    console.log('Export clicked');
    
    if (!currentTemplateId) {
        window.debugUtils.showErrorToast('No Template', 'Select or create a template first', 'warning');
        return;
    }
    
    openExportModal();
}

function openExportModal() {
    const modal = document.getElementById('exportModal');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

function closeExportModal() {
    const modal = document.getElementById('exportModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function performExport() {
    if (!currentTemplateId) {
        window.debugUtils.showErrorToast('Export', 'No template selected', 'error');
        return;
    }
    
    const format = document.querySelector('input[name="exportFormat"]:checked')?.value || 'html';
    const includeCss = document.getElementById('exportIncludeCss')?.checked || false;
    const includeMetadata = document.getElementById('exportIncludeMetadata')?.checked || false;
    
    console.log('Exporting template:', {
        templateId: currentTemplateId,
        format: format,
        includeCss: includeCss,
        includeMetadata: includeMetadata
    });
    
    if (format === 'html') {
        exportAsHtml(includeCss);
    } else if (format === 'json') {
        exportAsJson(includeCss, includeMetadata);
    }
    
    closeExportModal();
}

function exportAsHtml(includeCss) {
    if (!window.bridge || !window.bridge.getCurrentTemplate) {
        window.debugUtils.showErrorToast('Export', 'Bridge not available', 'error');
        return;
    }
    
    window.bridge.getCurrentTemplate(currentTemplateId, (template) => {
        if (!template) {
            window.debugUtils.showErrorToast('Export', 'Failed to get template', 'error');
            return;
        }
        
        let htmlContent = '';
        
        // Add CSS if requested
        if (includeCss && template.css) {
            htmlContent += '<!-- Template CSS -->\n';
            htmlContent += '<style>\n';
            htmlContent += template.css + '\n';
            htmlContent += '</style>\n\n';
        }
        
        // Add front side
        htmlContent += '<!-- Front Side -->\n';
        htmlContent += '<div class="card-front">\n';
        htmlContent += template.frontSide || '<p>Front side template</p>\n';
        htmlContent += '</div>\n\n';
        
        // Add back side
        htmlContent += '<!-- Back Side -->\n';
        htmlContent += '<div class="card-back">\n';
        htmlContent += template.backSide || '<p>Back side template</p>\n';
        htmlContent += '</div>\n';
        
        const filename = `${template.name || currentTemplateId}_template.html`;
        downloadFile(filename, htmlContent, 'text/html');
        
        window.debugUtils.showErrorToast('Export', `Exported as HTML: ${filename}`, 'success');
    });
}

function exportAsJson(includeCss, includeMetadata) {
    if (!window.bridge || !window.bridge.getCurrentTemplate) {
        window.debugUtils.showErrorToast('Export', 'Bridge not available', 'error');
        return;
    }
    
    window.bridge.getCurrentTemplate(currentTemplateId, (template) => {
        if (!template) {
            window.debugUtils.showErrorToast('Export', 'Failed to get template', 'error');
            return;
        }
        
        const exportData = {
            templateId: currentTemplateId,
            name: template.name,
            type: 'template',
            frontSide: template.frontSide,
            backSide: template.backSide
        };
        
        if (includeCss) {
            exportData.css = template.css;
        }
        
        if (includeMetadata) {
            exportData.metadata = {
                exportDate: new Date().toISOString(),
                exportedBy: 'Anki Template Designer',
                version: template.version || '1.0'
            };
        }
        
        const jsonContent = JSON.stringify(exportData, null, 2);
        const filename = `${template.name || currentTemplateId}_template.json`;
        downloadFile(filename, jsonContent, 'application/json');
        
        window.debugUtils.showErrorToast('Export', `Exported as JSON: ${filename}`, 'success');
    });
}

function downloadFile(filename, content, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function handleSettings() {
    console.log('Settings clicked');
    openSettingsModal();
}

function handleDebug() {
    console.log('Debug button clicked');
    if (typeof window.toggleDebugConsole === 'function') {
        window.toggleDebugConsole();
    } else {
        const debugConsole = document.getElementById('debugConsole');
        if (debugConsole) {
            debugConsole.classList.toggle('hidden');
        }
    }
}

// Initialize all toolbar buttons
function initializeToolbar() {
    console.log('Initializing toolbar...');
    
    const buttons = {
        'saveBtn': handleSave,
        'undoBtn': handleUndo,
        'redoBtn': handleRedo,
        'previewBtn': handlePreview,
        'exportBtn': handleExport,
        'settingsBtn': handleSettings,
        'debugBtn': handleDebug
    };
    
    for (const [id, handler] of Object.entries(buttons)) {
        const btn = document.getElementById(id);
        if (btn) {
            btn.addEventListener('click', handler);
            console.log(`Attached handler to ${id}`);
        } else {
            console.warn(`Button not found: ${id}`);
        }
    }
}

// Initialize template selection
async function initializeTemplateSelection() {
    console.log('Initializing template selection...');
    
    const templateSelect = document.getElementById('templateSelect');
    if (templateSelect) {
        templateSelect.addEventListener('change', (e) => {
            if (e.target.value) {
                loadTemplate(e.target.value);
            } else {
                // No template selected - warn user
                if (loadedTemplates.length === 0) {
                    window.debugUtils.showErrorToast('No Templates', 'Create a card type with templates in Anki first', 'warning');
                }
            }
        });
    }
    
    // Load available templates and wait for completion
    await loadTemplates();
    
    console.log('✓ Template selection initialized');
}

// Initialize side tabs (Front/Back/Preview)
async function initializeSideTabs() {
    console.log('Initializing side tabs...');
    
    const sideTabs = document.querySelectorAll('.side-tab');
    
    sideTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            const side = e.target.getAttribute('data-side');
            const mode = e.target.getAttribute('data-mode');
            const target = side || mode;
            
            if (target) {
                switchSide(target);
            }
        });
    });
    
    // Initialize UI
    updateSideTabUI();
    updateSideInfo();
    
    console.log('✓ Side tabs initialized');
}

// Initialize drag and drop on component items
function initializeDragAndDrop() {
    console.log('Initializing drag and drop...');
    
    const componentItems = document.querySelectorAll('.component-item');
    componentItems.forEach(item => {
        item.addEventListener('dragstart', window.canvasModule.onDragStart);
        item.addEventListener('dragend', window.canvasModule.onDragEnd);
    });
    
    console.log(`Drag and drop initialized for ${componentItems.length} components`);
}

// Initialize keyboard shortcuts
function initializeKeyboardShortcuts() {
    console.log('[Keyboard Shortcuts] Initializing keyboard shortcuts...');
    
    document.addEventListener('keydown', (e) => {
        // Ctrl+S - Save
        if (e.ctrlKey && e.key === 's') {
            console.log('[Keyboard Shortcuts] Ctrl+S detected - Save');
            e.preventDefault();
            handleSave();
        }
        
        // Ctrl+Z - Undo
        if (e.ctrlKey && !e.shiftKey && e.key === 'z') {
            console.log('[Keyboard Shortcuts] Ctrl+Z detected - Undo');
            e.preventDefault();
            handleUndo();
        }
        
        // Ctrl+Y or Ctrl+Shift+Z - Redo
        if ((e.ctrlKey && e.key === 'y') || (e.ctrlKey && e.shiftKey && e.key === 'z')) {
            console.log('[Keyboard Shortcuts] Ctrl+Y or Ctrl+Shift+Z detected - Redo');
            e.preventDefault();
            handleRedo();
        }
        
        // Ctrl+P - Preview
        if (e.ctrlKey && e.key === 'p') {
            console.log('[Keyboard Shortcuts] Ctrl+P detected - Preview');
            e.preventDefault();
            handlePreview();
        }
        
        // Ctrl+E - Export
        if (e.ctrlKey && e.key === 'e') {
            console.log('[Keyboard Shortcuts] Ctrl+E detected - Export');
            e.preventDefault();
            handleExport();
        }
    });
    
    console.log('✓ Keyboard shortcuts initialized');
}

// Initialize error handling
function initializeErrorHandling() {
    console.log('Initializing error handling...');
    
    // Global error handler for uncaught exceptions
    window.addEventListener('error', (event) => {
        console.error('Uncaught error:', event.error);
        
        const errorMsg = event.error?.message || String(event.message);
        const errorSource = event.filename || 'unknown';
        const errorLine = event.lineno || '?';
        
        window.debugUtils.handleError(
            event.error || new Error(errorMsg),
            `${errorSource}:${errorLine}`
        );
        
        // Also send to bridge for logging
        if (window.bridge && window.bridge.reportError) {
            window.bridge.reportError('JavaScript Error', {
                message: errorMsg,
                source: errorSource,
                line: errorLine,
                stack: event.error?.stack || 'No stack trace'
            });
        }
    });
    
    // Global unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled promise rejection:', event.reason);
        
        const errorMsg = event.reason?.message || String(event.reason);
        
        window.debugUtils.handleError(
            event.reason instanceof Error ? event.reason : new Error(errorMsg),
            'Unhandled Promise Rejection'
        );
        
        // Prevent browser default handling
        event.preventDefault();
        
        // Send to bridge
        if (window.bridge && window.bridge.reportError) {
            window.bridge.reportError('Unhandled Promise', {
                message: errorMsg,
                reason: event.reason
            });
        }
    });
    
    console.log('✓ Error handling initialized');
}

// Helper function to hide loading overlay
// Main initialization
async function initializeApp() {
    console.log('=== Anki Template Designer Starting ===');
    console.log('Version: 1.0.0');
    console.log('Press Ctrl+Alt+D to toggle debug console');
    
    try {
        // Initialize debug console FIRST
        window.debugUtils.createDebugConsole();
        console.log('✓ Debug console ready');
        
        // Initialize keyboard shortcuts IMMEDIATELY (before any blocking operations)
        // This allows Ctrl+Alt+D to work even while loading
        initializeKeyboardShortcuts();
        console.log('✓ Keyboard shortcuts initialized (available immediately)');
        
        // Initialize bridge
        console.log('Initializing bridge...');
        await window.bridgeModule.initializeBridge();
        console.log('✓ Bridge connected');
        
        // Test bridge
        await window.bridgeModule.testBridge();
        console.log('✓ Bridge test passed');
        
        // Initialize UI components
        window.componentsModule.initializeComponents();
        console.log('✓ Components initialized');
        
        window.canvasModule.initializeCanvas();
        console.log('✓ Canvas initialized');
        
        window.propertiesModule.initializePropertiesPanel();
        console.log('✓ Properties panel initialized');
        
        initializeToolbar();
        console.log('✓ Toolbar initialized');
        
        // Initialize template selection and wait for templates to load
        await initializeTemplateSelection();
        
        // Initialize side tabs (Front/Back/Preview)
        await initializeSideTabs();
        
        initializeDragAndDrop();
        console.log('✓ Drag and drop initialized');
        
        initializeErrorHandling();
        
        // Update undo/redo button states
        updateHistoryButtonStates();
        
        console.log('=== Application Ready ===');
        
        window.debugUtils.showErrorToast(
            'Ready',
            'Anki Template Designer is ready to use',
            'success',
            'Drag components from the sidebar to the canvas'
        );
        
        // Notify that editor is ready
        if (typeof window.editorReady === 'function') {
            window.editorReady();
        }
        
    } catch (error) {
        console.error('Initialization failed:', error);
        window.debugUtils.handleError(error, 'Application Initialization');
    }
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// Signal that editor is ready (called from Python)
window.editorReady = function() {
    console.log('editorReady callback triggered');
};
