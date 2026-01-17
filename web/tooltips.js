/**
 * Tooltip Utility Module
 * Provides functionality for creating and managing inline tooltips
 */

export class TooltipManager {
    constructor() {
        this.tooltips = new Map();
        this.isMouseOverTooltip = false;
    }

    /**
     * Create a tooltip for an element
     * @param {HTMLElement} element - The element to attach the tooltip to
     * @param {string} text - The tooltip text
     * @param {Object} options - Tooltip options
     */
    createTooltip(element, text, options = {}) {
        const {
            position = 'top',
            theme = 'light',
            delay = 200,
            maxWidth = 240
        } = options;

        // Create container
        const container = document.createElement('div');
        container.className = 'tooltip-container';

        // Create trigger button
        const trigger = document.createElement('button');
        trigger.className = 'tooltip-trigger';
        trigger.setAttribute('aria-label', `Help: ${text}`);
        trigger.setAttribute('type', 'button');
        trigger.innerHTML = '?';
        trigger.setAttribute('data-tooltip-trigger', 'true');

        // Create tooltip content
        const content = document.createElement('div');
        content.className = 'tooltip-content';
        if (theme === 'dark') {
            content.classList.add('dark-theme');
        }
        content.setAttribute('role', 'tooltip');
        content.textContent = text;
        content.style.maxWidth = `${maxWidth}px`;

        // Add to container
        container.appendChild(trigger);
        container.appendChild(content);

        // Insert before element or inside it
        if (options.insertBefore) {
            element.parentNode.insertBefore(container, element);
        } else {
            element.appendChild(container);
        }

        // Store reference
        const tooltipId = `tooltip-${Date.now()}-${Math.random()}`;
        this.tooltips.set(tooltipId, {
            element,
            container,
            trigger,
            content,
            position,
            delay
        });

        return tooltipId;
    }

    /**
     * Add tooltip to button or control
     * @param {HTMLElement} element - The button element
     * @param {string} text - Tooltip text
     * @param {Object} options - Additional options
     */
    addTooltip(element, text, options = {}) {
        // Create wrapper if needed
        let container = element.closest('.tooltip-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'tooltip-container';
            element.parentNode.insertBefore(container, element);
            container.appendChild(element);
        }

        // Create trigger if not exists
        let trigger = container.querySelector('.tooltip-trigger');
        if (!trigger) {
            trigger = document.createElement('button');
            trigger.className = 'tooltip-trigger';
            trigger.setAttribute('type', 'button');
            trigger.setAttribute('aria-label', `Help: ${text}`);
            trigger.innerHTML = '?';
            container.appendChild(trigger);
        }

        // Create content
        let content = container.querySelector('.tooltip-content');
        if (!content) {
            content = document.createElement('div');
            content.className = 'tooltip-content';
            content.setAttribute('role', 'tooltip');
            container.appendChild(content);
        }

        content.textContent = text;

        // Apply theme
        if (options.theme === 'dark') {
            content.classList.add('dark-theme');
        }

        return container;
    }

    /**
     * Remove tooltip
     * @param {string} tooltipId - The tooltip ID to remove
     */
    removeTooltip(tooltipId) {
        const tooltip = this.tooltips.get(tooltipId);
        if (tooltip) {
            tooltip.container.remove();
            this.tooltips.delete(tooltipId);
        }
    }

    /**
     * Update tooltip text
     * @param {string} tooltipId - The tooltip ID
     * @param {string} newText - New tooltip text
     */
    updateTooltip(tooltipId, newText) {
        const tooltip = this.tooltips.get(tooltipId);
        if (tooltip) {
            tooltip.content.textContent = newText;
        }
    }

    /**
     * Show tooltip programmatically
     * @param {string} tooltipId - The tooltip ID
     */
    show(tooltipId) {
        const tooltip = this.tooltips.get(tooltipId);
        if (tooltip) {
            tooltip.content.style.visibility = 'visible';
            tooltip.content.style.opacity = '1';
        }
    }

    /**
     * Hide tooltip programmatically
     * @param {string} tooltipId - The tooltip ID
     */
    hide(tooltipId) {
        const tooltip = this.tooltips.get(tooltipId);
        if (tooltip) {
            tooltip.content.style.visibility = 'hidden';
            tooltip.content.style.opacity = '0';
        }
    }

    /**
     * Add tooltips in batch from configuration
     * @param {Array} config - Array of tooltip configurations
     */
    addMultiple(config) {
        const ids = [];
        for (const { element, text, options } of config) {
            const id = this.createTooltip(element, text, options);
            ids.push(id);
        }
        return ids;
    }

    /**
     * Clear all tooltips
     */
    clearAll() {
        this.tooltips.forEach((tooltip) => {
            tooltip.container.remove();
        });
        this.tooltips.clear();
    }
}

// Export singleton instance
export const tooltipManager = new TooltipManager();

/**
 * Helper function to create a tooltip helper icon
 * @param {string} text - Tooltip text
 * @param {Object} options - Options
 * @returns {HTMLElement} The tooltip container
 */
export function createTooltipIcon(text, options = {}) {
    const container = document.createElement('span');
    container.className = 'tooltip-container';

    const trigger = document.createElement('button');
    trigger.className = 'tooltip-trigger';
    trigger.setAttribute('type', 'button');
    trigger.setAttribute('aria-label', `Help: ${text}`);
    trigger.innerHTML = '?';

    const content = document.createElement('div');
    content.className = 'tooltip-content';
    if (options.theme === 'dark') {
        content.classList.add('dark-theme');
    }
    content.setAttribute('role', 'tooltip');
    content.textContent = text;

    if (options.maxWidth) {
        content.style.maxWidth = `${options.maxWidth}px`;
    }

    container.appendChild(trigger);
    container.appendChild(content);

    return container;
}

/**
 * Initialize tooltips for all elements with data-tooltip attribute
 */
export function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach((element) => {
        const text = element.getAttribute('data-tooltip');
        const position = element.getAttribute('data-tooltip-position') || 'top';
        const theme = element.getAttribute('data-tooltip-theme') || 'light';

        tooltipManager.addTooltip(element, text, { position, theme });
    });
}

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTooltips);
} else {
    initializeTooltips();
}
