/**
 * GrapeJS editor initialisation for the Anki Template Designer.
 *
 * Sets up the editor with:
 *  - Custom Anki component types & blocks
 *  - Style manager sectors relevant to card design
 *  - Layer manager, trait manager
 *  - Toolbar commands (save, undo/redo, export, device switching)
 *  - Python bridge integration
 */

/* ------------------------------------------------------------------ */
/*  State                                                              */
/* ------------------------------------------------------------------ */

let editor = null;
let currentSide = 'front';      // 'front' | 'back'
let currentTemplateId = null;
let hasUnsavedChanges = false;

// Stores per-template, per-side GrapeJS project data
// { [templateId]: { front: {...projectData}, back: {...projectData} } }
const sideState = {};

/* ------------------------------------------------------------------ */
/*  Editor init                                                        */
/* ------------------------------------------------------------------ */

function initEditor() {
    console.log('[ATD] Initialising GrapeJS editor...');

    if (typeof grapesjs === 'undefined') {
        console.error('[ATD] grapesjs is not loaded!');
        document.getElementById('statusLeft').textContent = 'Error: GrapeJS failed to load';
        return;
    }

    try {
        editor = grapesjs.init({
            container: '#gjs',
            height: '100%',
            width: 'auto',
            fromElement: true,
            storageManager: false,

            // Canvas defaults
            canvas: {
                styles: [],
                scripts: [],
            },

            // Panels – we use our own HTML containers
            panels: { defaults: [] },

            // Block manager – render into our left sidebar with auto-categorisation
            blockManager: {
                appendTo: '#blocks-container',
            },

            // Layer manager
            layerManager: {
                appendTo: '#layers-container',
            },

            // Selector + Style manager
            selectorManager: {
                appendTo: '#styles-container',
            },
            styleManager: {
                appendTo: '#styles-container',
                sectors: [
                    {
                        name: 'Typography',
                        open: true,
                        buildProps: [
                            'font-family', 'font-size', 'font-weight',
                            'letter-spacing', 'color', 'line-height',
                            'text-align', 'text-decoration', 'text-transform',
                        ],
                    },
                    {
                        name: 'Layout',
                        open: false,
                        buildProps: [
                            'display', 'position',
                            'flex-direction', 'justify-content',
                            'align-items', 'flex-wrap', 'flex-basis',
                            'order', 'gap',
                            'width', 'height', 'max-width', 'min-height',
                            'overflow',
                        ],
                    },
                    {
                        name: 'Spacing',
                        open: false,
                        buildProps: ['padding', 'margin'],
                    },
                    {
                        name: 'Background',
                        open: false,
                        buildProps: ['background-color', 'background-image', 'background-size'],
                    },
                    {
                        name: 'Borders',
                        open: false,
                        buildProps: [
                            'border-radius', 'border',
                            'box-shadow',
                        ],
                    },
                ],
            },

            // Trait manager
            traitManager: {
                appendTo: '#traits-container',
            },

            // Device presets
            deviceManager: {
                devices: [
                    { name: 'Desktop', width: '' },
                    { name: 'Tablet', width: '768px', widthMedia: '992px' },
                    { name: 'Mobile', width: '375px', widthMedia: '480px' },
                ],
            },
        });

        console.log('[ATD] GrapeJS core initialised');

        // Register custom Anki components and blocks
        registerAnkiComponents(editor);
        console.log('[ATD] Anki components registered');

        registerAnkiBlocks(editor);
        console.log('[ATD] Anki blocks registered');

        // Build toolbar buttons
        _buildToolbarPanels();

        // Build right-panel tab switcher
        _buildPanelSwitcher();

        // Set up side toggle (Front / Back)
        _setupSideToggle();

        // Track changes
        editor.on('component:add component:remove component:update style:change', () => {
            _markUnsaved();
        });

        // Inject canvas styles for layout placeholders and Anki badges
        _injectCanvasStyles();

        // Connect to Python bridge
        _connectBridge();

        _setStatus('Ready');
        console.log('[ATD] Editor fully initialised');

    } catch (err) {
        console.error('[ATD] Editor init failed:', err);
        _setStatus('Error: ' + err.message);
    }
}

/* ------------------------------------------------------------------ */
/*  Canvas style injection                                             */
/* ------------------------------------------------------------------ */

function _injectCanvasStyles() {
    // GrapeJS renders components inside an iframe.
    // We inject styles so layout placeholders and Anki badges render properly.
    const css = `
        /* Anki component badges */
        [data-gjs-type="anki-field"],
        [data-gjs-type="anki-cloze"],
        [data-gjs-type="anki-hint"],
        [data-gjs-type="anki-type-answer"],
        [data-gjs-type="anki-tags"],
        [data-gjs-type="anki-frontside"] {
            display: inline-block;
            padding: 4px 10px;
            margin: 2px;
            border-radius: 4px;
            font-family: "Fira Code", "Cascadia Code", monospace;
            font-size: 13px;
            background: rgba(137, 180, 250, 0.12);
            border: 1px dashed rgba(137, 180, 250, 0.4);
            color: #89b4fa;
            min-width: 60px;
            text-align: center;
        }
        [data-gjs-type="anki-conditional"] {
            display: block;
            padding: 8px 12px;
            margin: 4px 0;
            border-radius: 4px;
            background: rgba(203, 166, 247, 0.08);
            border: 1px dashed rgba(203, 166, 247, 0.35);
            min-height: 40px;
        }

        /* Layout placeholders */
        .atd-section { position: relative; }
        .atd-section:empty::after {
            content: 'Section \\2013  drop components here';
            display: block; padding: 16px; text-align: center;
            color: #999; font-size: 12px; font-style: italic;
        }
        .atd-row { position: relative; }
        .atd-row:empty::after {
            content: 'Row \\2013  drop columns here';
            display: block; padding: 16px; text-align: center;
            color: #999; font-size: 12px; font-style: italic;
        }
        .atd-col { position: relative; }
        .atd-col:empty::after {
            content: 'Column \\2013  drop content';
            display: block; padding: 8px; text-align: center;
            color: #999; font-size: 11px; font-style: italic;
        }
        .atd-container { position: relative; }
        .atd-container:empty::after {
            content: 'Container \\2013  drop content here';
            display: block; padding: 16px; text-align: center;
            color: #999; font-size: 12px; font-style: italic;
        }
        .atd-spacer {
            background: repeating-linear-gradient(
                45deg, transparent, transparent 4px,
                rgba(150, 150, 150, 0.08) 4px, rgba(150, 150, 150, 0.08) 8px
            );
        }
    `;

    // Wait for the canvas iframe to be ready, then inject
    editor.on('load', () => {
        try {
            const frame = editor.Canvas.getFrameEl();
            if (frame?.contentDocument) {
                const style = frame.contentDocument.createElement('style');
                style.textContent = css;
                frame.contentDocument.head.appendChild(style);
                console.log('[ATD] Canvas styles injected');
            }
        } catch (err) {
            console.warn('[ATD] Could not inject canvas styles:', err);
        }
    });
}

/* ------------------------------------------------------------------ */
/*  Toolbar                                                            */
/* ------------------------------------------------------------------ */

function _buildToolbarPanels() {
    const container = document.querySelector('.toolbar-actions');
    if (!container) return;

    let bordersActive = false;
    let currentDevice = 'Desktop';

    const _setActiveDevice = (device) => {
        currentDevice = device;
        editor.setDevice(device);
        ['device-d', 'device-t', 'device-m'].forEach((id) => {
            const b = document.getElementById(`btn-${id}`);
            if (b) b.classList.toggle('active',
                (id === 'device-d' && device === 'Desktop') ||
                (id === 'device-t' && device === 'Tablet') ||
                (id === 'device-m' && device === 'Mobile')
            );
        });
    };

    const _toggleBorders = () => {
        bordersActive = !bordersActive;
        if (bordersActive) {
            editor.runCommand('sw-visibility');
        } else {
            editor.stopCommand('sw-visibility');
        }
        const btn = document.getElementById('btn-borders');
        if (btn) btn.classList.toggle('active', bordersActive);
    };

    const buttons = [
        { id: 'save',       label: '💾 Save',    action: _saveTemplate },
        { id: 'undo',       label: '↶ Undo',     action: () => editor.UndoManager.undo() },
        { id: 'redo',       label: '↷ Redo',     action: () => editor.UndoManager.redo() },
        { id: 'export',     label: '📤 Export',   action: _showExport },
        { id: 'device-d',   label: '🖥',          action: () => _setActiveDevice('Desktop'), title: 'Desktop',        active: true },
        { id: 'device-t',   label: '⊟',           action: () => _setActiveDevice('Tablet'),  title: 'Tablet' },
        { id: 'device-m',   label: '📱',          action: () => _setActiveDevice('Mobile'),  title: 'Mobile' },
        { id: 'borders',    label: 'B',           action: _toggleBorders, title: 'Toggle borders' },
    ];

    buttons.forEach(({ id, label, action, title, active }) => {
        const btn = document.createElement('button');
        btn.className = 'toolbar-btn' + (active ? ' active' : '');
        btn.id = `btn-${id}`;
        btn.innerHTML = label;
        if (title) btn.title = title;
        btn.addEventListener('click', action);
        container.appendChild(btn);
    });
}

/* ------------------------------------------------------------------ */
/*  Right-panel tab switcher                                           */
/* ------------------------------------------------------------------ */

function _buildPanelSwitcher() {
    const container = document.getElementById('panelSwitcher');
    if (!container) return;

    const tabs = [
        { id: 'styles', label: 'Styles',  target: '#styles-container' },
        { id: 'traits', label: 'Traits',  target: '#traits-container' },
        { id: 'layers', label: 'Layers',  target: '#layers-container' },
    ];

    tabs.forEach(({ id, label, target }, i) => {
        const btn = document.createElement('button');
        btn.className = 'switcher-btn' + (i === 0 ? ' active' : '');
        btn.textContent = label;
        btn.dataset.target = target;
        btn.addEventListener('click', () => {
            // Toggle visibility
            tabs.forEach((t) => {
                const el = document.querySelector(t.target);
                if (el) el.style.display = t.target === target ? '' : 'none';
            });
            container.querySelectorAll('.switcher-btn').forEach((b) => b.classList.remove('active'));
            btn.classList.add('active');
        });
        container.appendChild(btn);
    });

    // Initially show only styles panel
    document.getElementById('traits-container').style.display = 'none';
    document.getElementById('layers-container').style.display = 'none';
}

/* ------------------------------------------------------------------ */
/*  Side toggle (Front / Back)                                         */
/* ------------------------------------------------------------------ */

function _setupSideToggle() {
    const toggle = document.getElementById('sideToggle');
    if (!toggle) return;

    toggle.querySelectorAll('.side-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
            const side = btn.dataset.side;
            if (side === currentSide) return;

            // Save current side state
            _saveSideState();

            // Switch
            currentSide = side;
            toggle.querySelectorAll('.side-btn').forEach((b) => b.classList.remove('active'));
            btn.classList.add('active');

            // Load new side state
            _loadSideState();

            bridgeLog(`Switched to ${side} side`);
        });
    });
}

const STANDALONE_KEY = '__standalone__';

function _saveSideState() {
    if (!editor) return;
    const key = currentTemplateId || STANDALONE_KEY;
    if (!sideState[key]) {
        sideState[key] = { front: null, back: null };
    }
    sideState[key][currentSide] = editor.getProjectData();
}

function _loadSideState() {
    if (!editor) return;
    const key = currentTemplateId || STANDALONE_KEY;
    const data = sideState[key]?.[currentSide];
    if (data) {
        editor.loadProjectData(data);
    } else {
        editor.DomComponents.clear();
        editor.CssComposer.clear();
    }
}

/* ------------------------------------------------------------------ */
/*  Unsaved indicator                                                  */
/* ------------------------------------------------------------------ */

function _markUnsaved() {
    hasUnsavedChanges = true;
    const dot = document.getElementById('unsavedDot');
    if (dot) dot.classList.remove('hidden');
}

function _clearUnsaved() {
    hasUnsavedChanges = false;
    const dot = document.getElementById('unsavedDot');
    if (dot) dot.classList.add('hidden');
}

/* ------------------------------------------------------------------ */
/*  Save                                                               */
/* ------------------------------------------------------------------ */

async function _saveTemplate() {
    if (!editor) return;
    _saveSideState();

    const html = editor.getHtml();
    const css = editor.getCss();
    const projectData = editor.getProjectData();

    const payload = {
        templateId: currentTemplateId,
        side: currentSide,
        html,
        css,
        projectData: JSON.stringify(projectData),
        allSides: JSON.stringify(sideState[currentTemplateId] || {}),
    };

    const result = await bridgeCall('save_template', payload);
    if (result?.success) {
        _clearUnsaved();
        _setStatus('Saved');
    } else {
        _setStatus('Save failed');
    }
}

/* ------------------------------------------------------------------ */
/*  Export                                                             */
/* ------------------------------------------------------------------ */

function _showExport() {
    if (!editor) return;
    const html = editor.getHtml();
    const css = editor.getCss();
    const full = `<style>\n${css}\n</style>\n${html}`;

    editor.Modal.setTitle('Export Template')
        .setContent(
            `<textarea style="width:100%;height:300px;font-family:monospace;font-size:13px;">${_escapeHtml(full)}</textarea>`
        )
        .open();
}

function _escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/* ------------------------------------------------------------------ */
/*  Status helpers                                                     */
/* ------------------------------------------------------------------ */

function _setStatus(text) {
    const el = document.getElementById('statusLeft');
    if (el) el.textContent = text;
}

function _setConnectionStatus(text, ok) {
    const el = document.getElementById('connectionStatus');
    if (!el) return;
    el.textContent = text;
    el.className = 'status-badge ' + (ok ? 'connected' : 'disconnected');
}

/* ------------------------------------------------------------------ */
/*  Bridge connection                                                  */
/* ------------------------------------------------------------------ */

async function _connectBridge() {
    try {
        const bridge = await initializeBridge();
        if (bridge) {
            _setConnectionStatus('Connected', true);

            // Load templates list
            const result = await bridgeCall('get_templates', {});
            if (result?.templates) {
                _populateTemplateSelector(result.templates);
            }

            // Load currently selected template
            const current = await bridgeCall('get_current_template', {});
            if (current?.templateId) {
                _loadTemplate(current.templateId, current);
            }
        } else {
            _setConnectionStatus('Standalone', false);
        }
    } catch (err) {
        console.error('Bridge connection failed:', err);
        _setConnectionStatus('Disconnected', false);
    }
}

function _populateTemplateSelector(templates) {
    const select = document.getElementById('templateSelect');
    if (!select) return;

    select.innerHTML = '';
    templates.forEach((t) => {
        const opt = document.createElement('option');
        opt.value = t.id || t.name;
        opt.textContent = t.name || t.id;
        select.appendChild(opt);
    });

    select.addEventListener('change', async () => {
        if (hasUnsavedChanges) {
            if (!confirm('You have unsaved changes. Switch template?')) {
                select.value = currentTemplateId;
                return;
            }
        }
        const result = await bridgeCall('load_template', { templateId: select.value });
        if (result) {
            _loadTemplate(select.value, result);
        }
    });
}

function _loadTemplate(templateId, data) {
    currentTemplateId = templateId;
    currentSide = 'front';

    // Reset side toggle
    document.querySelectorAll('.side-btn').forEach((b) => {
        b.classList.toggle('active', b.dataset.side === 'front');
    });

    // Load project data if available
    if (data?.projectData) {
        try {
            const parsed = typeof data.projectData === 'string'
                ? JSON.parse(data.projectData) : data.projectData;
            sideState[templateId] = parsed;
        } catch { /* ignore */ }
    }

    _loadSideState();
    _clearUnsaved();
    _setStatus(`Loaded: ${templateId}`);
    bridgeLog(`Template loaded: ${templateId}`);
}

/* ------------------------------------------------------------------ */
/*  Keyboard shortcuts                                                 */
/* ------------------------------------------------------------------ */

document.addEventListener('keydown', (e) => {
    // Ctrl+S = Save
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        _saveTemplate();
    }
    // Ctrl+Z = Undo (GrapeJS handles this, but just in case)
    // Ctrl+Shift+Z / Ctrl+Y = Redo
});

/* ------------------------------------------------------------------ */
/*  Boot                                                               */
/* ------------------------------------------------------------------ */

document.addEventListener('DOMContentLoaded', initEditor);
