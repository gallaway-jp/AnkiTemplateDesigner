/**
 * Performance Dashboard UI (Issue #54)
 * 
 * Real-time visualization of performance metrics including:
 * - Cache statistics (hit ratio, size, efficiency)
 * - Async operation tracking (queue, execution, statistics)
 * - Render performance (FPS, latency)
 * - Performance alerts and bottleneck detection
 */

class PerformanceDashboardUI {
    constructor(containerSelector, performanceOptimizer) {
        this.container = document.querySelector(containerSelector);
        this.optimizer = performanceOptimizer;
        
        this.updateInterval = null;
        this.refreshRateMs = 1000;
        this.isVisible = false;
        
        this.charts = new Map();
        this.metrics = {
            cacheHitRatio: [],
            asyncPending: [],
            renderFPS: [],
            operationLatency: []
        };
        
        this.init();
    }

    // ========== Initialization ==========

    init() {
        if (!this.container) {
            console.warn('Performance dashboard container not found');
            return;
        }

        this.createDashboard();
        this.attachEventListeners();
        this.startUpdates();
    }

    createDashboard() {
        const html = `
            <div class="performance-dashboard">
                <!-- Header -->
                <div class="perf-header">
                    <h2 class="perf-title">Performance Dashboard</h2>
                    <div class="perf-controls">
                        <button class="perf-btn perf-toggle-details" title="Toggle Details">
                            <span class="perf-icon">⚙</span>
                        </button>
                        <button class="perf-btn perf-reset-metrics" title="Reset Metrics">
                            <span class="perf-icon">↻</span>
                        </button>
                        <button class="perf-btn perf-close" title="Close">
                            <span class="perf-icon">✕</span>
                        </button>
                    </div>
                </div>

                <!-- Status Bar -->
                <div class="perf-status-bar">
                    <div class="perf-status-item">
                        <span class="perf-label">Cache Hit Ratio:</span>
                        <span class="perf-value" id="perf-hit-ratio">--</span>
                    </div>
                    <div class="perf-status-item">
                        <span class="perf-label">Pending Operations:</span>
                        <span class="perf-value" id="perf-pending-ops">--</span>
                    </div>
                    <div class="perf-status-item">
                        <span class="perf-label">Frame Rate:</span>
                        <span class="perf-value" id="perf-fps">--</span>
                    </div>
                    <div class="perf-status-item">
                        <span class="perf-label">Status:</span>
                        <span class="perf-value perf-status-healthy" id="perf-status">Healthy</span>
                    </div>
                </div>

                <!-- Metrics Cards -->
                <div class="perf-metrics-grid">
                    <!-- Cache Card -->
                    <div class="perf-card perf-card-cache">
                        <h3 class="perf-card-title">Cache Performance</h3>
                        <div class="perf-card-content">
                            <div class="perf-metric">
                                <span class="perf-metric-label">Hit Ratio:</span>
                                <span class="perf-metric-value" id="perf-cache-hit">0%</span>
                            </div>
                            <div class="perf-metric">
                                <span class="perf-metric-label">Memory Used:</span>
                                <span class="perf-metric-value" id="perf-cache-memory">0 MB</span>
                            </div>
                            <div class="perf-metric">
                                <span class="perf-metric-label">Entries:</span>
                                <span class="perf-metric-value" id="perf-cache-entries">0</span>
                            </div>
                            <div class="perf-metric">
                                <span class="perf-metric-label">Avg Retrieval:</span>
                                <span class="perf-metric-value" id="perf-cache-retrieval">0ms</span>
                            </div>
                        </div>
                    </div>

                    <!-- Async Card -->
                    <div class="perf-card perf-card-async">
                        <h3 class="perf-card-title">Async Operations</h3>
                        <div class="perf-card-content">
                            <div class="perf-metric">
                                <span class="perf-metric-label">Pending:</span>
                                <span class="perf-metric-value" id="perf-async-pending">0</span>
                            </div>
                            <div class="perf-metric">
                                <span class="perf-metric-label">Completed:</span>
                                <span class="perf-metric-value" id="perf-async-completed">0</span>
                            </div>
                            <div class="perf-metric">
                                <span class="perf-metric-label">Avg Wait:</span>
                                <span class="perf-metric-value" id="perf-async-wait">0ms</span>
                            </div>
                            <div class="perf-metric">
                                <span class="perf-metric-label">Avg Execution:</span>
                                <span class="perf-metric-value" id="perf-async-exec">0ms</span>
                            </div>
                        </div>
                    </div>

                    <!-- Rendering Card -->
                    <div class="perf-card perf-card-render">
                        <h3 class="perf-card-title">Rendering Performance</h3>
                        <div class="perf-card-content">
                            <div class="perf-metric">
                                <span class="perf-metric-label">Avg FPS:</span>
                                <span class="perf-metric-value" id="perf-render-fps">60</span>
                            </div>
                            <div class="perf-metric">
                                <span class="perf-metric-label">Avg Latency:</span>
                                <span class="perf-metric-value" id="perf-render-latency">0ms</span>
                            </div>
                            <div class="perf-metric">
                                <span class="perf-metric-label">Virtual Scroll:</span>
                                <span class="perf-metric-value" id="perf-virtual-scroll">Enabled</span>
                            </div>
                            <div class="perf-metric">
                                <span class="perf-metric-label">DOM Nodes:</span>
                                <span class="perf-metric-value" id="perf-dom-nodes">0</span>
                            </div>
                        </div>
                    </div>

                    <!-- Health Card -->
                    <div class="perf-card perf-card-health">
                        <h3 class="perf-card-title">System Health</h3>
                        <div class="perf-card-content">
                            <div class="perf-health-indicator">
                                <div class="perf-health-bar" id="perf-health-bar"></div>
                                <span class="perf-health-text" id="perf-health-text">Healthy</span>
                            </div>
                            <div class="perf-threshold-alerts" id="perf-alerts">
                                <span class="perf-alert-none">No alerts</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Details Panel (Initially Hidden) -->
                <div class="perf-details-panel" id="perf-details" style="display: none;">
                    <h3 class="perf-details-title">Performance Details</h3>
                    
                    <div class="perf-section">
                        <h4>Bottlenecks</h4>
                        <div class="perf-bottleneck-list" id="perf-bottlenecks">
                            <p class="perf-empty">No bottlenecks detected</p>
                        </div>
                    </div>

                    <div class="perf-section">
                        <h4>Threshold Violations</h4>
                        <div class="perf-violations-list" id="perf-violations">
                            <p class="perf-empty">No violations</p>
                        </div>
                    </div>

                    <div class="perf-section">
                        <h4>Recent Operations</h4>
                        <div class="perf-operations-list" id="perf-operations">
                            <p class="perf-empty">No recent operations</p>
                        </div>
                    </div>
                </div>

                <!-- Footer -->
                <div class="perf-footer">
                    <span class="perf-timestamp" id="perf-timestamp">Updated: --:--:--</span>
                    <span class="perf-version">Performance Optimizer v1.0</span>
                </div>
            </div>
        `;

        this.container.innerHTML = html;
    }

    attachEventListeners() {
        const closeBtn = this.container.querySelector('.perf-close');
        const detailsBtn = this.container.querySelector('.perf-toggle-details');
        const resetBtn = this.container.querySelector('.perf-reset-metrics');

        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hide());
        }

        if (detailsBtn) {
            detailsBtn.addEventListener('click', () => this.toggleDetails());
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetMetrics());
        }
    }

    // ========== Updates ==========

    startUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        this.updateInterval = setInterval(() => {
            this.updateMetrics();
        }, this.refreshRateMs);

        // Initial update
        this.updateMetrics();
    }

    stopUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    updateMetrics() {
        if (!this.isVisible) {
            return;
        }

        try {
            // Get metrics from optimizer
            const cacheStats = this.optimizer.get_cache_stats();
            const asyncStats = this.optimizer.get_async_stats();
            const healthStatus = this.optimizer.get_health_status();

            this.updateCacheMetrics(cacheStats);
            this.updateAsyncMetrics(asyncStats);
            this.updateHealthStatus(healthStatus);
            this.updateTimestamp();
        } catch (error) {
            console.error('Error updating performance metrics:', error);
        }
    }

    updateCacheMetrics(cacheStats) {
        const hitRatioPct = Math.round(cacheStats.hit_ratio * 100);
        this.setElementText('perf-hit-ratio', `${hitRatioPct}%`);
        this.setElementText('perf-cache-hit', `${hitRatioPct}%`);
        this.setElementText('perf-cache-memory', `${cacheStats.memory_usage_mb.toFixed(2)} MB`);
        this.setElementText('perf-cache-entries', String(cacheStats.total_entries));
        this.setElementText('perf-cache-retrieval', `${cacheStats.avg_retrieval_ms.toFixed(2)}ms`);

        // Record metric
        this.metrics.cacheHitRatio.push({
            timestamp: Date.now(),
            value: cacheStats.hit_ratio
        });
    }

    updateAsyncMetrics(asyncStats) {
        this.setElementText('perf-pending-ops', String(asyncStats.current_pending_count));
        this.setElementText('perf-async-pending', String(asyncStats.current_pending_count));
        this.setElementText('perf-async-completed', String(asyncStats.total_completed));
        this.setElementText('perf-async-wait', `${asyncStats.avg_wait_time_ms.toFixed(2)}ms`);
        this.setElementText('perf-async-exec', `${asyncStats.avg_execution_time_ms.toFixed(2)}ms`);

        // Record metric
        this.metrics.asyncPending.push({
            timestamp: Date.now(),
            value: asyncStats.current_pending_count
        });
    }

    updateHealthStatus(healthStatus) {
        const cacheHealth = healthStatus.cache_health;
        const asyncHealth = healthStatus.async_health;
        const violations = healthStatus.threshold_violations;
        
        // Determine overall status
        const statusElement = this.container.querySelector('#perf-status');
        let statusClass = 'perf-status-healthy';
        let statusText = 'Healthy';

        if (violations > 0) {
            statusClass = 'perf-status-warning';
            statusText = `Warning (${violations} violations)`;
        }

        if (asyncHealth.failure_rate > 0.1 || cacheHealth.memory_usage_pct > 90) {
            statusClass = 'perf-status-critical';
            statusText = 'Critical';
        }

        statusElement.className = `perf-value ${statusClass}`;
        statusElement.textContent = statusText;

        // Update health bar
        const healthBar = this.container.querySelector('#perf-health-bar');
        const healthScore = Math.max(0, 100 - (violations * 20));
        healthBar.style.width = `${Math.max(0, healthScore)}%`;

        // Update health text
        this.setElementText('perf-health-text', statusText);
    }

    updateTimestamp() {
        const now = new Date();
        const time = now.toLocaleTimeString();
        this.setElementText('perf-timestamp', `Updated: ${time}`);
    }

    // ========== UI Interactions ==========

    show() {
        if (this.container) {
            this.container.style.display = 'block';
            this.isVisible = true;
            this.startUpdates();
        }
    }

    hide() {
        if (this.container) {
            this.container.style.display = 'none';
            this.isVisible = false;
            this.stopUpdates();
        }
    }

    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }

    toggleDetails() {
        const detailsPanel = this.container.querySelector('#perf-details');
        if (detailsPanel) {
            const isHidden = detailsPanel.style.display === 'none';
            detailsPanel.style.display = isHidden ? 'block' : 'none';
        }
    }

    resetMetrics() {
        if (this.optimizer.reset_all_metrics) {
            this.optimizer.reset_all_metrics();
            this.metrics = {
                cacheHitRatio: [],
                asyncPending: [],
                renderFPS: [],
                operationLatency: []
            };
            this.updateMetrics();
        }
    }

    // ========== Utility Methods ==========

    setElementText(elementId, text) {
        const element = this.container.querySelector(`#${elementId}`);
        if (element) {
            element.textContent = text;
        }
    }

    getMetricsSummary() {
        return {
            cacheHitRatio: this.metrics.cacheHitRatio,
            asyncPending: this.metrics.asyncPending,
            renderFPS: this.metrics.renderFPS,
            operationLatency: this.metrics.operationLatency
        };
    }

    exportMetrics(format = 'json') {
        const summary = this.getMetricsSummary();
        
        if (format === 'json') {
            return JSON.stringify(summary, null, 2);
        }

        return String(summary);
    }

    // ========== Event Emission ==========

    on(event, callback) {
        if (!this.listeners) {
            this.listeners = new Map();
        }

        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }

        this.listeners.get(event).push(callback);
    }

    emit(event, data) {
        if (!this.listeners || !this.listeners.has(event)) {
            return;
        }

        this.listeners.get(event).forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`Error in ${event} handler:`, error);
            }
        });
    }

    // ========== Public API ==========

    setRefreshRate(milliseconds) {
        this.refreshRateMs = milliseconds;
        this.stopUpdates();
        this.startUpdates();
    }

    getStatus() {
        return {
            visible: this.isVisible,
            refreshRate: this.refreshRateMs,
            metrics: this.getMetricsSummary()
        };
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PerformanceDashboardUI;
}
