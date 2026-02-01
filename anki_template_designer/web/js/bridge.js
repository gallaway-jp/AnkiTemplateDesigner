/**
 * WebViewBridge Communication
 * QWebChannel connection to Python backend
 */

window.bridge = null;
window.bridgeReady = false;

function initializeBridge() {
    return new Promise((resolve, reject) => {
        console.log('Initializing QWebChannel...');
        
        if (typeof QWebChannel === 'undefined') {
            const error = 'QWebChannel not available';
            console.error(error);
            reject(new Error(error));
            return;
        }
        
        try {
            new QWebChannel(qt.webChannelTransport, function(channel) {
                console.log('QWebChannel created, accessing bridge...');
                
                window.bridge = channel.objects.bridge;
                
                if (!window.bridge) {
                    const error = 'Bridge object not found in channel';
                    console.error(error);
                    reject(new Error(error));
                    return;
                }
                
                window.bridgeReady = true;
                console.log('Bridge connected successfully');
                console.log('Bridge methods:', Object.keys(window.bridge).filter(k => typeof window.bridge[k] === 'function'));
                
                resolve(window.bridge);
            });
        } catch (error) {
            console.error('QWebChannel initialization failed:', error);
            reject(error);
        }
    });
}

// Test bridge connection
async function testBridge() {
    if (!window.bridge) {
        console.warn('Bridge not initialized');
        return false;
    }
    
    try {
        console.log('Testing bridge connection...');
        
        // Test a simple method if available
        if (typeof window.bridge.get_templates === 'function') {
            await new Promise((resolve, reject) => {
                window.bridge.get_templates((result) => {
                    console.log('Bridge test successful, templates:', result);
                    resolve(result);
                });
            });
        }
        
        return true;
    } catch (error) {
        console.error('Bridge test failed:', error);
        return false;
    }
}

// Export functions
window.bridgeModule = {
    initializeBridge,
    testBridge
};
