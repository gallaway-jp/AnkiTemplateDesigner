# Plan 05: Basic UI Shell

## Objective
Create the complete UI shell with sidebar, canvas, and properties panel layout - matching the `test_addon_minimal` design.

---

## Prerequisites
- [ ] Plans 01-04 completed and tested
- [ ] Bridge communication working
- [ ] Dialog loads and connects

---

## Step 5.1: Create Complete UI Layout

### Task
Implement the full three-panel layout (sidebar, canvas, properties) with styling.

### Implementation

Replace **anki_template_designer/web/index.html** with:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' qrc:; style-src 'self' 'unsafe-inline';">
    <title>Anki Template Designer</title>
    <style>
        /* ===== CSS Reset & Base ===== */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html, body {
            width: 100%;
            height: 100%;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            background: #f5f5f5;
            color: #333;
        }

        /* ===== App Container ===== */
        #app {
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        /* ===== Header ===== */
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 12px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            z-index: 100;
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .header h1 {
            font-size: 18px;
            font-weight: 600;
            letter-spacing: -0.5px;
        }

        .header-status {
            font-size: 11px;
            opacity: 0.8;
            padding: 4px 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
        }

        .header-actions {
            display: flex;
            gap: 8px;
        }

        /* ===== Toolbar ===== */
        .toolbar {
            background: #ecf0f1;
            padding: 8px 16px;
            border-bottom: 1px solid #ddd;
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
        }

        .toolbar-group {
            display: flex;
            gap: 4px;
            padding-right: 12px;
            border-right: 1px solid #ddd;
        }

        .toolbar-group:last-child {
            border-right: none;
        }

        .toolbar-btn {
            padding: 6px 12px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            color: #555;
            transition: all 0.15s ease;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .toolbar-btn:hover {
            background: #fff;
            border-color: #999;
            color: #333;
        }

        .toolbar-btn:active {
            transform: translateY(1px);
        }

        .toolbar-btn.primary {
            background: #3498db;
            border-color: #2980b9;
            color: white;
        }

        .toolbar-btn.primary:hover {
            background: #2980b9;
        }

        /* ===== Main Container ===== */
        .main-container {
            display: flex;
            flex: 1;
            overflow: hidden;
        }

        /* ===== Sidebar (Components Panel) ===== */
        .sidebar {
            width: 240px;
            background: white;
            border-right: 1px solid #ddd;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .sidebar-header {
            padding: 12px 16px;
            border-bottom: 1px solid #eee;
            font-weight: 600;
            font-size: 13px;
            color: #555;
            background: #fafafa;
        }

        .sidebar-content {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
        }

        .component-section {
            margin-bottom: 20px;
        }

        .component-section-title {
            font-size: 11px;
            font-weight: 600;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
            padding-bottom: 6px;
            border-bottom: 1px solid #eee;
        }

        .component-item {
            padding: 10px 12px;
            background: #f9f9f9;
            border: 1px solid #eee;
            border-radius: 6px;
            margin-bottom: 8px;
            cursor: grab;
            font-size: 13px;
            color: #555;
            transition: all 0.15s ease;
            user-select: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .component-item:hover {
            background: #f0f7ff;
            border-color: #3498db;
            color: #2980b9;
        }

        .component-item:active {
            cursor: grabbing;
        }

        .component-icon {
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            opacity: 0.7;
        }

        /* ===== Canvas Area ===== */
        .canvas-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #e8e8e8;
            overflow: hidden;
        }

        .canvas-wrapper {
            flex: 1;
            overflow: auto;
            padding: 24px;
            display: flex;
            justify-content: center;
        }

        .canvas {
            background: white;
            min-width: 600px;
            min-height: 400px;
            max-width: 900px;
            width: 100%;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            position: relative;
        }

        .canvas-empty {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            color: #999;
            font-size: 14px;
            text-align: center;
            padding: 40px;
        }

        .canvas-empty-icon {
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.3;
        }

        /* ===== Properties Panel ===== */
        .properties-panel {
            width: 280px;
            background: white;
            border-left: 1px solid #ddd;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .properties-header {
            padding: 12px 16px;
            border-bottom: 1px solid #eee;
            font-weight: 600;
            font-size: 13px;
            color: #555;
            background: #fafafa;
        }

        .properties-content {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
        }

        .property-group {
            margin-bottom: 20px;
        }

        .property-group-title {
            font-size: 11px;
            font-weight: 600;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
        }

        .property-row {
            margin-bottom: 12px;
        }

        .property-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 4px;
            display: block;
        }

        .property-input {
            width: 100%;
            padding: 8px 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 13px;
            font-family: inherit;
            transition: border-color 0.15s;
        }

        .property-input:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52,152,219,0.1);
        }

        .property-input[type="color"] {
            height: 36px;
            padding: 4px;
            cursor: pointer;
        }

        .property-select {
            width: 100%;
            padding: 8px 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 13px;
            background: white;
            cursor: pointer;
        }

        .no-selection {
            color: #999;
            text-align: center;
            padding: 40px 20px;
            font-size: 13px;
        }

        /* ===== Footer / Status Bar ===== */
        .status-bar {
            background: #f8f8f8;
            border-top: 1px solid #ddd;
            padding: 6px 16px;
            font-size: 11px;
            color: #888;
            display: flex;
            justify-content: space-between;
        }

        /* ===== Loading State ===== */
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255,255,255,0.95);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .loading-spinner {
            text-align: center;
        }

        .loading-spinner::before {
            content: '';
            display: block;
            width: 40px;
            height: 40px;
            margin: 0 auto 16px;
            border: 3px solid #eee;
            border-top-color: #3498db;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        .loading-text {
            font-size: 14px;
            color: #666;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .hidden {
            display: none !important;
        }

        /* ===== Scrollbar Styling ===== */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }

        ::-webkit-scrollbar-thumb {
            background: #ccc;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #aaa;
        }
    </style>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
</head>
<body>
    <div id="app">
        <!-- Loading Overlay -->
        <div class="loading-overlay" id="loadingOverlay">
            <div class="loading-spinner">
                <span class="loading-text">Loading editor...</span>
            </div>
        </div>

        <!-- Header -->
        <header class="header">
            <div class="header-left">
                <h1>Anki Template Designer</h1>
                <span class="header-status" id="status">Connecting...</span>
            </div>
            <div class="header-actions">
                <button class="toolbar-btn" id="btnHelp" title="Help">?</button>
            </div>
        </header>

        <!-- Toolbar -->
        <div class="toolbar">
            <div class="toolbar-group">
                <button class="toolbar-btn" id="btnNew" title="New Template">New</button>
                <button class="toolbar-btn" id="btnOpen" title="Open Template">Open</button>
                <button class="toolbar-btn primary" id="btnSave" title="Save Template">Save</button>
            </div>
            <div class="toolbar-group">
                <button class="toolbar-btn" id="btnUndo" title="Undo (Ctrl+Z)">Undo</button>
                <button class="toolbar-btn" id="btnRedo" title="Redo (Ctrl+Y)">Redo</button>
            </div>
            <div class="toolbar-group">
                <button class="toolbar-btn" id="btnPreview" title="Preview Template">Preview</button>
                <button class="toolbar-btn" id="btnExport" title="Export HTML">Export</button>
            </div>
        </div>

        <!-- Main Container -->
        <div class="main-container">
            <!-- Components Sidebar -->
            <aside class="sidebar">
                <div class="sidebar-header">Components</div>
                <div class="sidebar-content">
                    <div class="component-section">
                        <div class="component-section-title">Layout</div>
                        <div class="component-item" draggable="true" data-type="container">
                            <span class="component-icon">☐</span>
                            Container
                        </div>
                        <div class="component-item" draggable="true" data-type="row">
                            <span class="component-icon">⫿</span>
                            Row
                        </div>
                        <div class="component-item" draggable="true" data-type="column">
                            <span class="component-icon">⸾</span>
                            Column
                        </div>
                    </div>
                    
                    <div class="component-section">
                        <div class="component-section-title">Text</div>
                        <div class="component-item" draggable="true" data-type="text">
                            <span class="component-icon">T</span>
                            Text
                        </div>
                        <div class="component-item" draggable="true" data-type="heading">
                            <span class="component-icon">H</span>
                            Heading
                        </div>
                    </div>
                    
                    <div class="component-section">
                        <div class="component-section-title">Anki Fields</div>
                        <div class="component-item" draggable="true" data-type="field">
                            <span class="component-icon">{{</span>
                            Field
                        </div>
                        <div class="component-item" draggable="true" data-type="cloze">
                            <span class="component-icon">…</span>
                            Cloze
                        </div>
                    </div>
                    
                    <div class="component-section">
                        <div class="component-section-title">Media</div>
                        <div class="component-item" draggable="true" data-type="image">
                            <span class="component-icon">🖼</span>
                            Image
                        </div>
                        <div class="component-item" draggable="true" data-type="audio">
                            <span class="component-icon">🔊</span>
                            Audio
                        </div>
                    </div>
                </div>
            </aside>

            <!-- Canvas Area -->
            <main class="canvas-area">
                <div class="canvas-wrapper">
                    <div class="canvas" id="canvas">
                        <div class="canvas-empty">
                            <div class="canvas-empty-icon">📄</div>
                            <div>Drag components here to start building your template</div>
                        </div>
                    </div>
                </div>
            </main>

            <!-- Properties Panel -->
            <aside class="properties-panel">
                <div class="properties-header">Properties</div>
                <div class="properties-content" id="propertiesContent">
                    <div class="no-selection">
                        Select a component to edit its properties
                    </div>
                </div>
            </aside>
        </div>

        <!-- Status Bar -->
        <footer class="status-bar">
            <span id="statusLeft">Ready</span>
            <span id="statusRight">v2.0.0</span>
        </footer>
    </div>

    <script>
        // ===== Bridge Communication =====
        let bridge = null;
        let isConnected = false;

        document.addEventListener('DOMContentLoaded', function() {
            initWebChannel();
            initToolbar();
            initDragDrop();
        });

        function initWebChannel() {
            if (typeof QWebChannel === 'undefined') {
                console.warn('QWebChannel not available - running in standalone mode');
                updateStatus('Standalone');
                hideLoading();
                return;
            }

            new QWebChannel(qt.webChannelTransport, function(channel) {
                bridge = channel.objects.bridge;
                
                if (!bridge) {
                    console.error('Bridge not found');
                    updateStatus('Error');
                    hideLoading();
                    return;
                }

                isConnected = true;
                console.log('WebChannel connected');

                bridge.getVersion(function(response) {
                    try {
                        const data = JSON.parse(response);
                        updateStatus('Connected');
                        document.getElementById('statusRight').textContent = 'v' + data.version;
                    } catch (e) {
                        console.error('Version parse error:', e);
                    }
                });

                bridge.log('UI shell loaded');
                hideLoading();
            });
        }

        function updateStatus(text) {
            const status = document.getElementById('status');
            if (status) status.textContent = text;
        }

        function hideLoading() {
            const overlay = document.getElementById('loadingOverlay');
            if (overlay) overlay.classList.add('hidden');
        }

        // ===== Toolbar Actions =====
        function initToolbar() {
            document.getElementById('btnNew').addEventListener('click', onNew);
            document.getElementById('btnOpen').addEventListener('click', onOpen);
            document.getElementById('btnSave').addEventListener('click', onSave);
            document.getElementById('btnUndo').addEventListener('click', onUndo);
            document.getElementById('btnRedo').addEventListener('click', onRedo);
            document.getElementById('btnPreview').addEventListener('click', onPreview);
            document.getElementById('btnExport').addEventListener('click', onExport);
            document.getElementById('btnHelp').addEventListener('click', onHelp);
        }

        function onNew() {
            console.log('New template');
            setStatusLeft('New template created');
            // Will be implemented in later plans
        }

        function onOpen() {
            console.log('Open template');
            // Will be implemented in later plans
        }

        function onSave() {
            console.log('Save template');
            if (bridge) {
                bridge.handleAction('save_template', '{}', function(result) {
                    console.log('Save result:', result);
                    setStatusLeft('Template saved');
                });
            }
        }

        function onUndo() {
            console.log('Undo');
            setStatusLeft('Undo');
        }

        function onRedo() {
            console.log('Redo');
            setStatusLeft('Redo');
        }

        function onPreview() {
            console.log('Preview');
            setStatusLeft('Preview mode');
        }

        function onExport() {
            console.log('Export');
            setStatusLeft('Exporting...');
        }

        function onHelp() {
            console.log('Help');
            setStatusLeft('Opening help...');
        }

        function setStatusLeft(text) {
            const el = document.getElementById('statusLeft');
            if (el) el.textContent = text;
        }

        // ===== Drag & Drop =====
        function initDragDrop() {
            const canvas = document.getElementById('canvas');
            const components = document.querySelectorAll('.component-item');

            components.forEach(comp => {
                comp.addEventListener('dragstart', onDragStart);
                comp.addEventListener('dragend', onDragEnd);
            });

            canvas.addEventListener('dragover', onDragOver);
            canvas.addEventListener('drop', onDrop);
            canvas.addEventListener('dragleave', onDragLeave);
        }

        let draggedType = null;

        function onDragStart(e) {
            draggedType = e.target.dataset.type;
            e.target.style.opacity = '0.5';
            e.dataTransfer.effectAllowed = 'copy';
        }

        function onDragEnd(e) {
            e.target.style.opacity = '1';
            draggedType = null;
        }

        function onDragOver(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            document.getElementById('canvas').style.borderColor = '#3498db';
        }

        function onDragLeave(e) {
            document.getElementById('canvas').style.borderColor = '#ccc';
        }

        function onDrop(e) {
            e.preventDefault();
            document.getElementById('canvas').style.borderColor = '#ccc';
            
            if (draggedType) {
                console.log('Dropped component:', draggedType);
                setStatusLeft('Added: ' + draggedType);
                // Actual component creation will be in later plans
                
                // For now, show visual feedback
                const empty = document.querySelector('.canvas-empty');
                if (empty) {
                    empty.innerHTML = '<p style="padding: 20px; color: #666;">Component "' + draggedType + '" would be added here.<br><small>Full implementation in later steps.</small></p>';
                }
            }
        }

        // ===== Utilities =====
        window.editorReady = function() {
            return isConnected;
        };
    </script>
</body>
</html>
```

### Quality Checks

#### Security
- [ ] Content-Security-Policy updated for qrc:
- [ ] No external resources
- [ ] Event listeners instead of inline handlers
- [ ] No eval() or innerHTML with user data

#### Performance
- [ ] Minimal DOM queries (cached where needed)
- [ ] Efficient CSS (no expensive selectors)
- [ ] Animations use transform (GPU accelerated)

#### Best Practices
- [ ] Semantic HTML (header, main, aside, footer)
- [ ] BEM-like CSS naming
- [ ] Event delegation where appropriate

#### Maintainability
- [ ] CSS organized by component
- [ ] JavaScript functions clearly named
- [ ] Comments for sections

#### Documentation
- [ ] CSS sections commented
- [ ] JavaScript functions documented

#### Testing
- [ ] Works in standalone mode
- [ ] Drag and drop functional
- [ ] All buttons clickable

#### Accessibility
- [ ] Proper ARIA where needed
- [ ] Keyboard navigation (TODO: enhance later)
- [ ] Sufficient color contrast
- [ ] Button titles for tooltips

#### Scalability
- [ ] Easy to add more components
- [ ] Easy to add more toolbar actions

#### Compatibility
- [ ] Works in Qt WebEngine
- [ ] No browser-specific features

#### Error Handling
- [ ] Null checks on DOM queries
- [ ] Try-catch on JSON parsing

#### Complexity
- [ ] Simple event flow
- [ ] Clear visual hierarchy

#### Architecture
- [ ] Separation of structure/style/script

#### License
- [ ] N/A

#### Specification
- [ ] Matches test_addon_minimal design

---

## User Testing Checklist

### Visual Verification

1. [ ] Three-panel layout visible (sidebar, canvas, properties)
2. [ ] Header with title and status
3. [ ] Toolbar with all buttons
4. [ ] Status bar at bottom
5. [ ] Loading overlay appears then hides
6. [ ] Scrollbars styled correctly

### Interaction Testing

1. [ ] All toolbar buttons respond to click
2. [ ] Console shows button actions
3. [ ] Component items can be dragged
4. [ ] Canvas accepts drops
5. [ ] Status bar updates on actions
6. [ ] Help button works

### Responsive Testing

1. [ ] Window can be resized
2. [ ] Panels maintain proportions
3. [ ] Scrollbars appear when needed
4. [ ] Content doesn't overflow

### Bridge Testing

1. [ ] Status shows "Connected"
2. [ ] Version shown in status bar
3. [ ] Save button triggers bridge action

---

## Success Criteria

- [ ] All quality checks pass
- [ ] Full UI layout displays correctly
- [ ] All interactions work
- [ ] Bridge communication verified
- [ ] No console errors

---

## Next Step

After successful completion, proceed to [06-TEMPLATE-SERVICE.md](06-TEMPLATE-SERVICE.md).

---

## Notes/Issues

| Issue | Resolution | Date |
|-------|------------|------|
| | | |
