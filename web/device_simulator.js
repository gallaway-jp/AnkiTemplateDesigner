/**
 * Device Simulator Module (JavaScript/Frontend)
 * 
 * Provides device simulation, responsive design testing, viewport emulation,
 * and performance metrics collection by device type.
 */

class DeviceSimulator {
    constructor() {
        this.currentDevice = null;
        this.orientation = "portrait";
        this.zoomLevel = 1.0;
        this.networkType = "full_speed";
        this.metricsHistory = [];
        this.customDevices = [];
        
        // Predefined devices
        this.devices = this.initializePredefinedDevices();
    }
    
    /**
     * Initialize predefined device profiles
     */
    initializePredefinedDevices() {
        return {
            mobile: [
                { name: "iPhone 12", width: 390, height: 844, dpr: 2.0, os: "iOS 14", notch: true },
                { name: "iPhone 13 Pro", width: 390, height: 844, dpr: 2.0, os: "iOS 15", notch: true },
                { name: "Samsung Galaxy S21", width: 360, height: 800, dpr: 2.0, os: "Android 11", notch: true },
                { name: "Google Pixel 6", width: 412, height: 915, dpr: 2.75, os: "Android 12", notch: true },
            ],
            tablet: [
                { name: "iPad (10.2\")", width: 810, height: 1080, dpr: 2.0, os: "iPadOS 15", notch: false },
                { name: "iPad Pro (12.9\")", width: 1024, height: 1366, dpr: 2.0, os: "iPadOS 15", notch: false },
                { name: "Samsung Galaxy Tab S7", width: 800, height: 1280, dpr: 2.0, os: "Android 11", notch: false },
            ],
            desktop: [
                { name: "MacBook 13\"", width: 1440, height: 900, dpr: 2.0, os: "macOS", notch: false },
                { name: "Desktop 1920x1080", width: 1920, height: 1080, dpr: 1.0, os: "Windows 11", notch: false },
                { name: "4K Monitor", width: 3840, height: 2160, dpr: 1.0, os: "Linux", notch: false },
            ],
        };
    }
    
    /**
     * Get all available devices
     */
    getAvailableDevices() {
        const allDevices = [];
        for (const category in this.devices) {
            allDevices.push(...this.devices[category]);
        }
        allDevices.push(...this.customDevices);
        return allDevices;
    }
    
    /**
     * Find device by name
     */
    findDevice(name) {
        const allDevices = this.getAvailableDevices();
        return allDevices.find(d => d.name === name);
    }
    
    /**
     * Select device by name
     */
    selectDevice(name) {
        const device = this.findDevice(name);
        if (device) {
            this.currentDevice = { ...device };
            this.orientation = "portrait";
            return true;
        }
        return false;
    }
    
    /**
     * Add custom device profile
     */
    addCustomDevice(name, type, width, height, dpr = 1.0, os = "Custom") {
        const device = {
            name,
            type,
            width,
            height,
            dpr,
            os,
            notch: type === "mobile",
        };
        this.customDevices.push(device);
        return device;
    }
    
    /**
     * Remove custom device
     */
    removeCustomDevice(name) {
        const index = this.customDevices.findIndex(d => d.name === name);
        if (index > -1) {
            this.customDevices.splice(index, 1);
            return true;
        }
        return false;
    }
    
    /**
     * Rotate device (portrait ↔ landscape)
     */
    rotateDevice() {
        if (!this.currentDevice) {
            return null;
        }
        this.orientation = this.orientation === "portrait" ? "landscape" : "portrait";
        return this.getViewport();
    }
    
    /**
     * Get current viewport dimensions
     */
    getViewport() {
        if (!this.currentDevice) {
            return null;
        }
        
        const device = this.currentDevice;
        let width, height;
        
        if (this.orientation === "landscape") {
            width = device.height;
            height = device.width;
        } else {
            width = device.width;
            height = device.height;
        }
        
        return {
            width,
            height,
            dpr: device.dpr,
            zoom: this.zoomLevel,
            orientation: this.orientation,
            deviceName: device.name,
            notch: device.notch || false,
        };
    }
    
    /**
     * Set zoom level (0.5 - 2.0)
     */
    setZoomLevel(level) {
        this.zoomLevel = Math.max(0.5, Math.min(2.0, level));
    }
    
    /**
     * Set network type for throttling
     */
    setNetworkType(type) {
        const validTypes = ["full_speed", "fast_4g", "slow_4g", "slow_3g", "slow_2g"];
        if (validTypes.includes(type)) {
            this.networkType = type;
        }
    }
    
    /**
     * Get network speed characteristics
     */
    getNetworkCharacteristics() {
        const characteristics = {
            full_speed: { downlink: 100, uplink: 50, latency: 0, loss: 0 },
            fast_4g: { downlink: 16, uplink: 4, latency: 50, loss: 0.1 },
            slow_4g: { downlink: 4, uplink: 3, latency: 100, loss: 0.5 },
            slow_3g: { downlink: 1.6, uplink: 0.768, latency: 400, loss: 2 },
            slow_2g: { downlink: 0.4, uplink: 0.1, latency: 1000, loss: 5 },
        };
        return characteristics[this.networkType] || characteristics.full_speed;
    }
    
    /**
     * Record device performance metrics
     */
    recordMetrics(loadTimeMs, memoryMb, cpuPercent, batteryPercent) {
        if (!this.currentDevice) {
            throw new Error("No device selected");
        }
        
        const metrics = {
            deviceName: this.currentDevice.name,
            deviceType: this.currentDevice.type,
            loadTimeMs,
            memoryMb,
            cpuPercent,
            batteryPercent,
            networkType: this.networkType,
            timestamp: new Date().toISOString(),
        };
        
        this.metricsHistory.push(metrics);
        return metrics;
    }
    
    /**
     * Get metrics history
     */
    getMetricsHistory() {
        return this.metricsHistory;
    }
    
    /**
     * Compare performance between two devices
     */
    compareDevices(name1, name2) {
        const metrics1 = this.getLatestDeviceMetrics(name1);
        const metrics2 = this.getLatestDeviceMetrics(name2);
        
        if (!metrics1 || !metrics2) {
            return null;
        }
        
        const loadDiff = ((metrics2.loadTimeMs - metrics1.loadTimeMs) / metrics1.loadTimeMs) * 100;
        const memDiff = ((metrics2.memoryMb - metrics1.memoryMb) / metrics1.memoryMb) * 100;
        
        return {
            device1: { name: name1, loadTime: metrics1.loadTimeMs, memory: metrics1.memoryMb },
            device2: { name: name2, loadTime: metrics2.loadTimeMs, memory: metrics2.memoryMb },
            loadTimeDiff: loadDiff,
            memoryDiff: memDiff,
            faster: metrics1.loadTimeMs < metrics2.loadTimeMs ? name1 : name2,
        };
    }
    
    /**
     * Validate responsive design
     */
    validateResponsiveDesign(htmlContent, cssContent) {
        const issues = [];
        
        if (!this.currentDevice) {
            return issues;
        }
        
        // Check for viewport meta tag
        if (!htmlContent.includes("viewport")) {
            issues.push({
                type: "viewport",
                severity: "warning",
                message: "Missing viewport meta tag for mobile optimization",
                device: this.currentDevice.name,
            });
        }
        
        // Check for media queries
        if (!cssContent.includes("@media")) {
            if (this.currentDevice.type !== "desktop") {
                issues.push({
                    type: "breakpoint",
                    severity: "warning",
                    message: "No media queries found. Add breakpoints for responsive design.",
                    device: this.currentDevice.name,
                });
            }
        }
        
        // Check for flexible layout
        if (!cssContent.includes("max-width") && !cssContent.includes("width: 100%")) {
            issues.push({
                type: "layout",
                severity: "info",
                message: "Consider using max-width for flexible layouts",
                device: this.currentDevice.name,
            });
        }
        
        // Check touch target sizes
        if (this.currentDevice.type === "mobile" || this.currentDevice.type === "tablet") {
            if (cssContent.includes("button") && !cssContent.includes("min-height: 48px")) {
                issues.push({
                    type: "touch",
                    severity: "info",
                    message: "Ensure touch targets are at least 48x48 pixels",
                    device: this.currentDevice.name,
                });
            }
        }
        
        return issues;
    }
    
    /**
     * Render device preview
     */
    renderPreview(containerId, contentHtml = "") {
        const container = document.getElementById(containerId);
        if (!container || !this.currentDevice) {
            return;
        }
        
        const viewport = this.getViewport();
        const hasNotch = viewport.notch && this.orientation === "portrait";
        const notchHeight = hasNotch ? 30 : 0;
        
        const html = `
            <div class="device-frame" style="
                width: ${viewport.width * this.zoomLevel}px;
                height: ${viewport.height * this.zoomLevel}px;
                aspect-ratio: ${viewport.width}/${viewport.height};
            ">
                ${hasNotch ? '<div class="device-notch"></div>' : ''}
                <div class="device-viewport" style="margin-top: ${notchHeight}px;">
                    ${contentHtml || '<div class="viewport-placeholder">Preview Content</div>'}
                </div>
            </div>
            <div class="device-info">
                <div class="device-name">${this.currentDevice.name}</div>
                <div class="device-specs">${viewport.width}x${viewport.height} @ ${viewport.dpr}x</div>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    /**
     * Generate device report
     */
    generateReport() {
        if (!this.currentDevice) {
            return null;
        }
        
        const viewport = this.getViewport();
        const avgLoadTime = this.metricsHistory.length > 0
            ? this.metricsHistory.reduce((sum, m) => sum + m.loadTimeMs, 0) / this.metricsHistory.length
            : 0;
        const avgMemory = this.metricsHistory.length > 0
            ? this.metricsHistory.reduce((sum, m) => sum + m.memoryMb, 0) / this.metricsHistory.length
            : 0;
        
        return {
            timestamp: new Date().toISOString(),
            device: { ...this.currentDevice },
            viewport,
            network: this.getNetworkCharacteristics(),
            metricsCount: this.metricsHistory.length,
            averageLoadTime: avgLoadTime.toFixed(2),
            averageMemory: avgMemory.toFixed(1),
        };
    }
    
    /**
     * Export to JSON
     */
    exportToJSON() {
        return JSON.stringify({
            currentDevice: this.currentDevice,
            orientation: this.orientation,
            zoomLevel: this.zoomLevel,
            networkType: this.networkType,
            customDevices: this.customDevices,
            metricsHistory: this.metricsHistory,
        }, null, 2);
    }
    
    /**
     * Helper: get latest metrics for device
     */
    getLatestDeviceMetrics(deviceName) {
        const matching = this.metricsHistory.filter(m => m.deviceName === deviceName);
        return matching.length > 0 ? matching[matching.length - 1] : null;
    }
}

// Device Profile Manager
class DeviceProfileManager {
    constructor(simulator) {
        this.simulator = simulator;
    }
    
    /**
     * Get all device categories
     */
    getDeviceCategories() {
        return Object.keys(this.simulator.devices);
    }
    
    /**
     * Get devices by category
     */
    getDevicesByCategory(category) {
        return this.simulator.devices[category] || [];
    }
    
    /**
     * Get all devices
     */
    getAllDevices() {
        return this.simulator.getAvailableDevices();
    }
    
    /**
     * Export profiles
     */
    exportProfiles() {
        return JSON.stringify(this.getAllDevices(), null, 2);
    }
}

// Viewport Simulator
class ViewportSimulator {
    constructor(simulator) {
        this.simulator = simulator;
    }
    
    /**
     * Apply viewport to element
     */
    applyViewport(element) {
        const viewport = this.simulator.getViewport();
        if (!viewport) return;
        
        element.style.width = viewport.width * this.simulator.zoomLevel + "px";
        element.style.height = viewport.height * this.simulator.zoomLevel + "px";
        element.style.zoom = this.simulator.zoomLevel;
    }
    
    /**
     * Get computed media query
     */
    getActiveMediaQueries() {
        const viewport = this.simulator.getViewport();
        if (!viewport) return [];
        
        const queries = [];
        if (viewport.width <= 600) queries.push("mobile");
        else if (viewport.width <= 1024) queries.push("tablet");
        else queries.push("desktop");
        
        if (viewport.width < viewport.height) queries.push("portrait");
        else if (viewport.width > viewport.height) queries.push("landscape");
        
        return queries;
    }
    
    /**
     * Get layout metrics
     */
    getLayoutMetrics(element) {
        const viewport = this.simulator.getViewport();
        if (!element || !viewport) return null;
        
        return {
            viewportWidth: viewport.width,
            viewportHeight: viewport.height,
            elementWidth: element.offsetWidth,
            elementHeight: element.offsetHeight,
            dpr: viewport.dpr,
            zoomLevel: this.simulator.zoomLevel,
        };
    }
}

// Export for use in module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DeviceSimulator, DeviceProfileManager, ViewportSimulator };
}
