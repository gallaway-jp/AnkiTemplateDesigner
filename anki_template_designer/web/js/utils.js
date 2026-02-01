/**
 * Utility Functions
 * Debug console, error toasts, and logging helpers
 */

// Console capture and debug panel
window.debugMessages = [];

// Capture console methods
const originalConsole = {
    log: console.log,
    error: console.error,
    warn: console.warn,
    info: console.info
};

// Debug console functions
function createDebugConsole() {
    const debugConsole = document.getElementById('debugConsole');
    const debugOutput = document.getElementById('debugOutput');
    const debugClose = document.getElementById('debugClose');
    const debugCopy = document.getElementById('debugCopy');
    const debugClear = document.getElementById('debugClear');
    
    if (!debugConsole) {
        console.error('Debug console element not found');
        return;
    }
    
    if (debugClose) {
        debugClose.addEventListener('click', () => {
            debugConsole.classList.add('hidden');
        });
    }
    
    if (debugCopy) {
        debugCopy.addEventListener('click', () => {
            copyDebugToClipboard();
        });
    }
    
    if (debugClear) {
        debugClear.addEventListener('click', () => {
            clearDebugConsole();
        });
    }
    
    // Multiple keyboard shortcuts to toggle debug console
    document.addEventListener('keydown', (e) => {
        // Log all Ctrl+Alt or Ctrl+Shift key combinations for debugging
        if ((e.ctrlKey && e.altKey) || (e.ctrlKey && e.shiftKey)) {
            console.log(`[Debug Console] Key combination detected: Ctrl+${e.altKey ? 'Alt' : 'Shift'}+${e.key}`);
        }
        
        // Ctrl+Alt+D or Ctrl+Shift+D
        if ((e.ctrlKey && e.altKey && e.key.toLowerCase() === 'd') ||
            (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'd')) {
            console.log('[Debug Console] Toggle debug console');
            e.preventDefault();
            e.stopPropagation();
            debugConsole.classList.toggle('hidden');
            console.log('Debug console toggled');
        }
    });
    
    // Expose global toggle function for manual access
    window.toggleDebugConsole = () => {
        debugConsole.classList.toggle('hidden');
        console.log('Debug console toggled via window.toggleDebugConsole()');
    };
    
    console.log('Debug console initialized. Use Ctrl+Alt+D, Ctrl+Shift+D, or call window.toggleDebugConsole()');
}

function copyDebugToClipboard() {
    try {
        // Get all debug messages with formatting
        const debugOutput = document.getElementById('debugOutput');
        if (!debugOutput) {
            console.error('Debug output element not found');
            showErrorToast('Error', 'Debug output element not found', 'error');
            return;
        }
        
        // Get text content from all log entries
        const logEntries = debugOutput.querySelectorAll('div');
        const logText = Array.from(logEntries)
            .map(entry => entry.textContent)
            .join('\n');
        
        if (!logText) {
            showErrorToast('Debug Console', 'No debug messages to copy', 'info');
            return;
        }
        
        // Qt WebEngine has issues with the modern clipboard API Promise,
        // so we always use the fallback method which is more reliable
        fallbackCopyToClipboard(logText, logEntries.length);
    } catch (error) {
        console.error('Failed to copy debug log:', error);
        showErrorToast('Error', `Failed to copy: ${error.message}`, 'error');
    }
}

function fallbackCopyToClipboard(text, lineCount) {
    try {
        // Create temporary textarea
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.left = '-9999px';
        textarea.style.top = '-9999px';
        document.body.appendChild(textarea);
        
        // Select and copy
        textarea.focus();
        textarea.select();
        textarea.setSelectionRange(0, textarea.value.length);
        
        const successful = document.execCommand('copy');
        document.body.removeChild(textarea);
        
        if (successful) {
            showErrorToast('Copied', `${lineCount || text.split('\n').length} debug messages copied to clipboard`, 'success');
        } else {
            showErrorToast('Error', 'Failed to copy to clipboard - copy command not supported', 'error');
        }
    } catch (error) {
        console.error('Fallback copy failed:', error);
        showErrorToast('Error', `Clipboard not supported: ${error.message}`, 'error');
    }
}

function clearDebugConsole() {
    const debugOutput = document.getElementById('debugOutput');
    if (!debugOutput) {
        console.error('Debug output element not found');
        return;
    }
    
    debugOutput.innerHTML = '';
    showErrorToast('Cleared', 'Debug console cleared', 'info');
}

function addDebugMessage(message, type = 'log') {
    window.debugMessages.push({ message, type, timestamp: new Date() });
    
    const debugOutput = document.getElementById('debugOutput');
    if (debugOutput) {
        const logEntry = document.createElement('div');
        logEntry.className = `debug-${type}`;
        const timestamp = new Date().toLocaleTimeString();
        logEntry.textContent = `[${timestamp}] ${message}`;
        debugOutput.appendChild(logEntry);
        debugOutput.scrollTop = debugOutput.scrollHeight;
    }
}

// Override console methods
console.log = function(...args) {
    const message = args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
    ).join(' ');
    addDebugMessage(message, 'log');
    originalConsole.log.apply(console, args);
};

console.error = function(...args) {
    const message = args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
    ).join(' ');
    addDebugMessage(message, 'error');
    originalConsole.error.apply(console, args);
};

console.warn = function(...args) {
    const message = args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
    ).join(' ');
    addDebugMessage(message, 'warn');
    originalConsole.warn.apply(console, args);
};

console.info = function(...args) {
    const message = args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
    ).join(' ');
    addDebugMessage(message, 'info');
    originalConsole.info.apply(console, args);
};

// Error toast system
function showErrorToast(title, message, type = 'error', suggestion = '') {
    const container = document.getElementById('errorToastContainer');
    if (!container) {
        console.error('Error toast container not found');
        return;
    }
    
    const toast = document.createElement('div');
    toast.className = `error-toast ${type}`;
    
    const iconMap = {
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️',
        success: '✅'
    };
    
    toast.innerHTML = `
        <div class="error-toast-icon">${iconMap[type] || '❌'}</div>
        <div class="error-toast-content">
            <div class="error-toast-title">${title}</div>
            <div class="error-toast-message">${message}</div>
            ${suggestion ? `<div class="error-toast-suggestion">${suggestion}</div>` : ''}
        </div>
        <button class="error-toast-close">×</button>
    `;
    
    const closeBtn = toast.querySelector('.error-toast-close');
    closeBtn.addEventListener('click', () => {
        toast.classList.add('removing');
        setTimeout(() => toast.remove(), 300);
    });
    
    container.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.classList.add('removing');
            setTimeout(() => toast.remove(), 300);
        }
    }, 5000);
}

// Error handler
function handleError(error, context = 'Unknown') {
    console.error(`Error in ${context}:`, error);
    showErrorToast(
        'Error',
        error.message || 'An unknown error occurred',
        'error',
        context ? `Context: ${context}` : ''
    );
}

// Export functions
window.debugUtils = {
    createDebugConsole,
    addDebugMessage,
    showErrorToast,
    handleError,
    copyDebugToClipboard,
    clearDebugConsole
};
