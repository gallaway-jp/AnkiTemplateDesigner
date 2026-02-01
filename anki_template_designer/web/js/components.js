/**
 * Component Definitions
 * Component data structures and initialization
 */

// Component data is defined inline in index.html
// This file provides utilities for working with components

function initializeComponents() {
    console.log('Initializing component system...');
    
    // Get all component items
    const componentItems = document.querySelectorAll('.component-item');
    console.log(`Found ${componentItems.length} component items`);
    
    // Make components draggable
    componentItems.forEach(item => {
        item.setAttribute('draggable', 'true');
        console.log(`Made draggable: ${item.textContent.trim()}`);
    });
    
    return componentItems.length;
}

function getComponentByType(type) {
    const item = document.querySelector(`[data-type="${type}"]`);
    if (!item) {
        console.warn(`Component not found: ${type}`);
        return null;
    }
    
    return {
        type: item.dataset.type,
        label: item.textContent.trim(),
        icon: item.querySelector('.component-icon')?.textContent || ''
    };
}

// Export functions
window.componentsModule = {
    initializeComponents,
    getComponentByType
};
