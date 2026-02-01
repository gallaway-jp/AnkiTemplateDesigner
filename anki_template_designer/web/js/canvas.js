/**
 * Canvas Management
 * Drag and drop, canvas operations, component selection
 */

let draggedComponent = null;
let selectedComponent = null;
let componentIdCounter = 0;

function initializeCanvas() {
    console.log('Initializing canvas...');
    
    const canvas = document.getElementById('designCanvas');
    if (!canvas) {
        console.error('Canvas element not found');
        return false;
    }
    
    // Set up canvas event listeners
    canvas.addEventListener('dragover', handleDragOver);
    canvas.addEventListener('dragleave', handleDragLeave);
    canvas.addEventListener('drop', handleDrop);
    canvas.addEventListener('click', handleCanvasClick);
    
    console.log('Canvas initialized successfully');
    return true;
}

function onDragStart(event) {
    const target = event.currentTarget;
    draggedComponent = {
        type: target.dataset.type,
        label: target.textContent.trim()
    };
    
    console.log('Drag started:', draggedComponent);
    event.dataTransfer.effectAllowed = 'copy';
    event.dataTransfer.setData('text/plain', JSON.stringify(draggedComponent));
}

function onDragEnd(event) {
    console.log('Drag ended');
    draggedComponent = null;
}

function handleDragOver(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'copy';
    
    // Visual feedback
    const canvas = event.currentTarget;
    if (!canvas.classList.contains('drag-over')) {
        canvas.style.background = '#f0f7ff';
        canvas.classList.add('drag-over');
    }
}

function handleDragLeave(event) {
    const canvas = event.currentTarget;
    
    // Only remove highlight if actually leaving canvas
    if (event.target === canvas) {
        canvas.style.background = '';
        canvas.classList.remove('drag-over');
    }
}

function handleDrop(event) {
    event.preventDefault();
    
    const canvas = event.currentTarget;
    canvas.style.background = '';
    canvas.classList.remove('drag-over');
    
    try {
        const data = event.dataTransfer.getData('text/plain');
        const component = JSON.parse(data);
        
        console.log('Component dropped:', component);
        
        // Create unique ID for this component
        const componentId = `component-${componentIdCounter++}`;
        component.id = componentId;
        
        // Create component element
        const element = createComponentElement(component);
        
        // Add to canvas
        const emptyMessage = canvas.querySelector('.canvas-empty');
        if (emptyMessage) {
            emptyMessage.remove();
        }
        
        canvas.appendChild(element);
        
        // Auto-select the new component
        selectComponent(element, component);
        
        // Mark changes as unsaved
        if (typeof markUnsavedChanges === 'function') {
            markUnsavedChanges();
        }
        
        // Sync with bridge
        syncCanvasStateToBridge();
        
        window.debugUtils?.showErrorToast(
            'Component Added',
            `Added ${component.label} to canvas`,
            'success'
        );
        
    } catch (error) {
        console.error('Drop failed:', error);
        window.debugUtils?.handleError(error, 'Canvas Drop');
    }
}

function handleCanvasClick(event) {
    // Check if clicking a component directly
    const componentEl = event.target.closest('.canvas-component');
    if (componentEl && componentEl.dataset.componentId) {
        // Component will handle its own selection
        return;
    }
    
    // Click on empty canvas - deselect
    if (event.target.id === 'designCanvas') {
        deselectComponent();
    }
}

function syncCanvasStateToBridge() {
    console.log('Syncing canvas state to bridge...');
    
    const canvas = document.getElementById('designCanvas');
    if (!canvas || !window.bridge || !window.bridge.updateTemplate) {
        console.warn('Cannot sync: canvas or bridge not ready');
        return;
    }
    
    // Get all components on canvas
    const components = [];
    canvas.querySelectorAll('.canvas-component').forEach((element, index) => {
        const type = element.dataset.type || 'unknown';
        const label = element.dataset.label || 'Component';
        const id = element.dataset.componentId || `component-${index}`;
        components.push({
            id: id,
            type: type,
            label: label,
            position: index
        });
    });
    
    console.log(`Syncing ${components.length} components`);
    
    // Get current template ID
    if (typeof currentTemplateId === 'undefined' || !currentTemplateId) {
        console.warn('No current template selected');
        return;
    }
    
    // Build template HTML from components
    const templateHTML = components
        .map(c => `<!-- ${c.label} (${c.type}) -->\n<div data-type="${c.type}">${c.label}</div>`)
        .join('\n');
    
    // Send to bridge
    window.bridge.updateTemplate(
        currentTemplateId,
        0,  // card side (0=front, 1=back)
        templateHTML,
        '',  // CSS (empty for now)
        () => {
            console.log('Canvas state synced to bridge');
        }
    );
}

function createComponentElement(component) {
    const element = document.createElement('div');
    element.className = 'canvas-component';
    element.dataset.componentId = component.id;
    element.dataset.type = component.type;
    element.dataset.label = component.label;
    
    // Initialize with some default styling
    element.style.cssText = `
        padding: 16px;
        margin: 8px;
        background: white;
        border: 2px dashed #3498db;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.2s ease;
    `;
    
    element.innerHTML = `
        <div class="canvas-component-label">${component.label}</div>
        <div class="canvas-component-type">Type: ${component.type}</div>
    `;
    
    // Make selectable
    element.addEventListener('click', (e) => {
        e.stopPropagation();
        selectComponent(element, component);
    });
    
    return element;
}

function selectComponent(element, component) {
    // Store selected component
    selectedComponent = component;
    
    // Remove previous selection
    document.querySelectorAll('.canvas-component').forEach(el => {
        el.style.borderColor = '#3498db';
        el.style.borderStyle = 'dashed';
        el.style.boxShadow = 'none';
    });
    
    // Highlight selected
    element.style.borderColor = '#e74c3c';
    element.style.borderStyle = 'solid';
    element.style.boxShadow = '0 0 0 3px rgba(231, 76, 60, 0.15)';
    
    console.log('Component selected:', component);
    
    // Update properties panel using the enhanced properties module
    if (window.propertiesModule && window.propertiesModule.showComponentProperties) {
        window.propertiesModule.showComponentProperties(component);
    }
}

function deselectComponent() {
    selectedComponent = null;
    
    // Remove all selections
    document.querySelectorAll('.canvas-component').forEach(el => {
        el.style.borderColor = '#3498db';
        el.style.borderStyle = 'dashed';
        el.style.boxShadow = 'none';
    });
    
    // Clear properties panel
    if (window.propertiesModule && window.propertiesModule.clearPropertiesPanel) {
        window.propertiesModule.clearPropertiesPanel();
    }
    
    console.log('Component deselected');
}

function deleteSelectedComponent() {
    if (!selectedComponent) {
        console.warn('No component selected for deletion');
        return;
    }
    
    const element = document.querySelector(`[data-component-id="${selectedComponent.id}"]`);
    if (element) {
        element.remove();
        console.log(`Deleted component: ${selectedComponent.label}`);
        
        // Clear selection
        deselectComponent();
        
        // Sync changes
        syncCanvasStateToBridge();
        
        // Mark as unsaved
        if (typeof markUnsavedChanges === 'function') {
            markUnsavedChanges();
        }
    }
}

function getCanvasComponents() {
    const canvas = document.getElementById('designCanvas');
    if (!canvas) return [];
    
    const components = [];
    canvas.querySelectorAll('.canvas-component').forEach(element => {
        components.push({
            id: element.dataset.componentId,
            type: element.dataset.type,
            label: element.dataset.label
        });
    });
    
    return components;
}

// Export functions
window.canvasModule = {
    initializeCanvas,
    onDragStart,
    onDragEnd,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleCanvasClick,
    createComponentElement,
    selectComponent,
    deselectComponent,
    deleteSelectedComponent,
    syncCanvasStateToBridge,
    getCanvasComponents
};
