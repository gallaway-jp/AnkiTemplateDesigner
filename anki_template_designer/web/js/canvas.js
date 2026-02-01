/**
 * Canvas Management
 * Drag and drop, canvas operations
 */

let draggedComponent = null;

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
        
        // Create component element
        const element = createComponentElement(component);
        
        // Add to canvas
        const emptyMessage = canvas.querySelector('.canvas-empty');
        if (emptyMessage) {
            emptyMessage.remove();
        }
        
        canvas.appendChild(element);
        
        window.debugUtils.showErrorToast(
            'Component Added',
            `Added ${component.label} to canvas`,
            'success'
        );
        
    } catch (error) {
        console.error('Drop failed:', error);
        window.debugUtils.handleError(error, 'Canvas Drop');
    }
}

function createComponentElement(component) {
    const element = document.createElement('div');
    element.className = 'canvas-component';
    element.style.cssText = `
        padding: 16px;
        margin: 8px;
        background: white;
        border: 2px dashed #3498db;
        border-radius: 4px;
        cursor: pointer;
    `;
    
    element.innerHTML = `
        <div style="font-weight: 600; color: #2c3e50; margin-bottom: 8px;">
            ${component.label}
        </div>
        <div style="font-size: 12px; color: #7f8c8d;">
            Type: ${component.type}
        </div>
    `;
    
    // Make selectable
    element.addEventListener('click', () => {
        selectComponent(element, component);
    });
    
    return element;
}

function selectComponent(element, component) {
    // Remove previous selection
    document.querySelectorAll('.canvas-component').forEach(el => {
        el.style.borderColor = '#3498db';
        el.style.borderStyle = 'dashed';
    });
    
    // Highlight selected
    element.style.borderColor = '#e74c3c';
    element.style.borderStyle = 'solid';
    
    console.log('Component selected:', component);
    
    // Update properties panel
    updatePropertiesPanel(component);
}

function updatePropertiesPanel(component) {
    const propertiesContent = document.querySelector('.properties-content');
    if (!propertiesContent) return;
    
    propertiesContent.innerHTML = `
        <div style="margin-bottom: 16px;">
            <div style="font-weight: 600; margin-bottom: 8px;">Component Type</div>
            <div style="color: #666;">${component.label}</div>
        </div>
        <div style="margin-bottom: 16px;">
            <div style="font-weight: 600; margin-bottom: 8px;">Data Type</div>
            <div style="color: #666; font-family: monospace; font-size: 12px;">${component.type}</div>
        </div>
        <div style="padding: 12px; background: #f8f9fa; border-radius: 4px; font-size: 12px; color: #666;">
            Component properties and styling options will appear here.
        </div>
    `;
}

// Export functions
window.canvasModule = {
    initializeCanvas,
    onDragStart,
    onDragEnd,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    createComponentElement,
    selectComponent,
    updatePropertiesPanel
};
