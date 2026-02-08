/**
 * QWebChannel bridge for Python <-> JavaScript communication.
 * Provides the same interface as before so the Python WebViewBridge
 * doesn't need changes.
 */

window.bridge = null;
window.bridgeReady = false;

/**
 * Initialize the QWebChannel connection to the Python backend.
 * @returns {Promise<object>} Resolves with the bridge object (or null if standalone).
 */
function initializeBridge() {
    return new Promise((resolve) => {
        // Check if we're inside Qt WebEngine
        if (typeof QWebChannel === 'undefined' || typeof qt === 'undefined') {
            console.warn('[ATD] QWebChannel not available – running standalone');
            window.bridgeReady = false;
            resolve(null);
            return;
        }

        try {
            new QWebChannel(qt.webChannelTransport, (channel) => {
                window.bridge = channel.objects.bridge;

                if (!window.bridge) {
                    console.warn('[ATD] Bridge object not found in channel');
                    resolve(null);
                    return;
                }

                window.bridgeReady = true;
                console.log('[ATD] Bridge connected');
                resolve(window.bridge);
            });
        } catch (err) {
            console.error('[ATD] QWebChannel init failed:', err);
            resolve(null);
        }
    });
}

/**
 * Send a message to the Python backend via the bridge.
 * Qt 6 QWebChannel returns slot results asynchronously via callback.
 *
 * @param {string} action  - Action identifier.
 * @param {object} payload - JSON-serialisable data.
 * @returns {Promise<object|null>}
 */
function bridgeCall(action, payload = {}) {
    if (!window.bridgeReady || !window.bridge) {
        console.warn(`[ATD] bridgeCall(${action}): bridge not ready`);
        return Promise.resolve(null);
    }

    return new Promise((resolve) => {
        try {
            window.bridge.handleAction(action, JSON.stringify(payload), (resultStr) => {
                try {
                    const parsed = typeof resultStr === 'string'
                        ? JSON.parse(resultStr)
                        : resultStr;
                    resolve(parsed);
                } catch (parseErr) {
                    console.error(`[ATD] bridgeCall(${action}) parse error:`, parseErr);
                    resolve(null);
                }
            });
        } catch (err) {
            console.error(`[ATD] bridgeCall(${action}) failed:`, err);
            resolve(null);
        }
    });
}

/**
 * Log to both browser console and Python backend.
 */
function bridgeLog(message) {
    console.log(message);
    if (window.bridge?.log) {
        window.bridge.log(message);
    }
}
