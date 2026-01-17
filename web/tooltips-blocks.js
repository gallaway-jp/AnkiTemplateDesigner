/**
 * Tooltip Utilities for Component Blocks
 * Helper functions to add tooltips to block items in the component panel
 */

/**
 * Create a block with tooltip support
 * @param {object} blockConfig - Standard GrapeJS block configuration
 * @param {string} tooltipText - Tooltip text for the block
 * @returns {object} Enhanced block configuration with tooltip
 */
export function createBlockWithTooltip(blockConfig, tooltipText) {
    return {
        ...blockConfig,
        tooltipText: tooltipText,
        // Custom render to add tooltip icon
        renderBlock(element) {
            const container = document.createElement('div');
            container.style.display = 'flex';
            container.style.alignItems = 'center';
            container.style.gap = '8px';
            
            // Add the default block content
            const label = document.createElement('span');
            label.textContent = blockConfig.label || blockConfig.id;
            container.appendChild(label);
            
            // Add tooltip icon
            const tooltipIcon = document.createElement('button');
            tooltipIcon.className = 'tooltip-trigger';
            tooltipIcon.setAttribute('type', 'button');
            tooltipIcon.setAttribute('title', tooltipText);
            tooltipIcon.style.marginLeft = 'auto';
            tooltipIcon.innerHTML = '?';
            tooltipIcon.addEventListener('click', (e) => {
                e.stopPropagation();
            });
            container.appendChild(tooltipIcon);
            
            return container;
        }
    };
}

/**
 * Add tooltip to block element in the component panel
 * @param {HTMLElement} blockElement - The block element in the panel
 * @param {string} tooltipText - Tooltip text to display
 */
export function addBlockTooltip(blockElement, tooltipText) {
    if (!blockElement) return;
    
    // Create tooltip container
    const container = document.createElement('div');
    container.className = 'tooltip-container';
    container.style.display = 'inline-block';
    container.style.position = 'relative';
    
    // Create tooltip trigger
    const trigger = document.createElement('button');
    trigger.className = 'tooltip-trigger';
    trigger.setAttribute('type', 'button');
    trigger.setAttribute('aria-label', `Help: ${tooltipText}`);
    trigger.style.marginLeft = '4px';
    trigger.style.width = '16px';
    trigger.style.height = '16px';
    trigger.style.fontSize = '10px';
    trigger.innerHTML = '?';
    
    // Create tooltip content
    const content = document.createElement('div');
    content.className = 'tooltip-content';
    content.setAttribute('role', 'tooltip');
    content.textContent = tooltipText;
    
    // Add to element
    blockElement.appendChild(trigger);
    blockElement.appendChild(content);
}

/**
 * Batch add tooltips to multiple block elements
 * @param {Array} tooltips - Array of {selector, text} objects
 */
export function addBlockTooltipsBatch(tooltips) {
    tooltips.forEach(({ selector, text }) => {
        const element = document.querySelector(selector);
        if (element) {
            addBlockTooltip(element, text);
        }
    });
}

/**
 * Initialize block tooltips after panel is rendered
 * @param {object} blockManager - GrapeJS BlockManager instance
 * @param {Array} tooltipConfig - Configuration for block tooltips
 */
export function initializeBlockTooltips(blockManager, tooltipConfig) {
    // Wait for blocks to be rendered
    setTimeout(() => {
        const blockPanels = document.querySelectorAll('[data-gjs-block]');
        
        blockPanels.forEach((blockEl) => {
            const blockId = blockEl.getAttribute('data-gjs-block');
            const tooltipData = tooltipConfig.find(t => t.id === blockId);
            
            if (tooltipData && !blockEl.querySelector('.tooltip-trigger')) {
                addBlockTooltip(blockEl, tooltipData.text);
            }
        });
    }, 500);
}

/**
 * Get default block tooltip configurations
 * Based on component type and category
 */
export const DEFAULT_BLOCK_TOOLTIPS = {
    // Basic Components
    'text-block': 'Static text that does not change - use for labels and headers',
    'field-block': 'Dynamic field content - shows data from Anki cards',
    'image-block': 'Display images from media files or base64 data',
    'video-block': 'Embed video content for multimedia cards',
    'audio-block': 'Play audio files - great for pronunciation guides',
    
    // Layout Components
    'container-block': 'Group components together - everything inside inherits styling',
    'row-block': 'Arrange items horizontally side-by-side',
    'column-block': 'Stack items vertically in a column',
    'grid-block': 'Create a flexible grid layout',
    'flexbox-block': 'Advanced flex layout for precise positioning',
    
    // Anki Features
    'cloze-block': 'Cloze deletion - hidden text revealed on click',
    'hint-block': 'Click to reveal hint text',
    'conditional-block': 'Show/hide content based on field content',
    'field-list-block': 'Display multiple fields in a list',
    
    // Interactive
    'button-block': 'Clickable button - style with colors and shapes',
    'link-block': 'Hyperlink to external URL',
    'button-group-block': 'Group multiple buttons together',
    
    // Visual Effects
    'badge-block': 'Small tag or label for categorization',
    'alert-block': 'Important notice or warning box',
    'separator-block': 'Horizontal divider line',
    'progress-block': 'Progress bar indicator',
    
    // Data Display
    'table-block': 'Display data in table format',
    'list-block': 'Display bulleted or numbered list',
    'card-block': 'Content card with optional shadow and border',
    
    // Forms
    'input-block': 'Text input field (note: limited in Anki review)',
    'checkbox-block': 'Checkbox for binary choices',
    'select-block': 'Dropdown menu for selecting options'
};

/**
 * Create tooltip helper for a block category
 */
export function getBlockCategoryTooltips(category) {
    const tooltips = {
        'Basic': 'Basic building blocks for simple content',
        'Layout': 'Components for organizing and arranging content',
        'Anki Special': 'Anki-specific features like cloze and fields',
        'Interactive': 'User interactive elements like buttons and links',
        'Visual': 'Visual effects and decorative elements',
        'Data': 'Components for displaying data and information',
        'Forms': 'Form elements for user input'
    };
    
    return tooltips[category] || null;
}
