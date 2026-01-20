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
        this.audioAlertsEnabled = localStorage.getItem('perf-audio-alerts') !== 'false';
        
        this.charts = new Map();
        this.metrics = {
            cacheHitRatio: [],
            asyncPending: [],
            renderFPS: [],
            operationLatency: []
        };
        
        // Audio context for generating tones
        this.audioContext = null;
        
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
                        <button class="perf-btn perf-export-json" title="Export as JSON">
                            <span class="perf-icon">📥</span>
                        </button>
                        <button class="perf-btn perf-export-csv" title="Export as CSV">
                            <span class="perf-icon">📊</span>
                        </button>
                        <button class="perf-btn perf-toggle-audio" title="Toggle audio alerts">
                            <span class="perf-icon">🔊</span>
                        </button>
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
        const exportJsonBtn = this.container.querySelector('.perf-export-json');
        const exportCsvBtn = this.container.querySelector('.perf-export-csv');
        const audioBtn = this.container.querySelector('.perf-toggle-audio');

        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hide());
        }

        if (detailsBtn) {
            detailsBtn.addEventListener('click', () => this.toggleDetails());
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetMetrics());
        }

        if (exportJsonBtn) {
            exportJsonBtn.addEventListener('click', () => this.exportAsJSON());
        }

        if (exportCsvBtn) {
            exportCsvBtn.addEventListener('click', () => this.exportAsCSV());
        }

        if (audioBtn) {
            audioBtn.addEventListener('click', () => this.toggleAudioAlerts());
            this.updateAudioButtonUI(audioBtn);
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

            // Check performance and trigger audio alert if needed
            const metrics = {
                renderFPS: this.metrics.renderFPS[this.metrics.renderFPS.length - 1]?.value || 60,
                operationLatency: this.metrics.operationLatency[this.metrics.operationLatency.length - 1]?.value || 0,
                cacheHitRatio: cacheStats.hit_ratio || 1
            };
            this.checkAndAlertIfNeeded(metrics);
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
        const violations = healthStatus.threshold_violations || 0;
        
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

        // Highlight metrics that exceed thresholds
        this.highlightThresholdViolations(this.metrics);

        // Update threshold violations
        this.updateViolationsDisplay(healthStatus);
        
        // Update recent operations
        this.updateOperationsDisplay(healthStatus);
    }

    /**
     * Highlight metrics that exceed thresholds
     */
    highlightThresholdViolations(metrics) {
        const thresholds = {
            fps: 30,
            latency: 500,
            cacheHitRatio: 50
        };

        const currentFPS = metrics?.renderFPS?.slice(-1)[0] || 60;
        const currentLatency = metrics?.operationLatency?.slice(-1)[0] || 0;
        const cacheRatio = metrics?.cacheHitRatio?.slice(-1)[0] || 100;

        // FPS violation
        const fpElement = document.getElementById('perf-render-fps') || 
                         this.container.querySelector('[data-metric="fps"]');
        if (fpElement) {
            if (currentFPS < thresholds.fps) {
                fpElement.classList.add('metric-violation');
                fpElement.setAttribute('data-violation', `⚠️ Below ${thresholds.fps} FPS`);
            } else {
                fpElement.classList.remove('metric-violation');
                fpElement.removeAttribute('data-violation');
            }
        }

        // Latency violation
        const latencyElement = document.getElementById('perf-op-latency') || 
                              this.container.querySelector('[data-metric="latency"]');
        if (latencyElement) {
            if (currentLatency > thresholds.latency) {
                latencyElement.classList.add('metric-violation');
                latencyElement.setAttribute('data-violation', `⚠️ Above ${thresholds.latency}ms`);
            } else {
                latencyElement.classList.remove('metric-violation');
                latencyElement.removeAttribute('data-violation');
            }
        }

        // Cache hit ratio violation
        const cacheElement = document.getElementById('perf-cache-hit') || 
                            this.container.querySelector('[data-metric="cache"]');
        if (cacheElement) {
            if (cacheRatio < thresholds.cacheHitRatio) {
                cacheElement.classList.add('metric-violation');
                cacheElement.setAttribute('data-violation', `⚠️ Below ${thresholds.cacheHitRatio}%`);
            } else {
                cacheElement.classList.remove('metric-violation');
                cacheElement.removeAttribute('data-violation');
            }
        }

        // Update violation badge count
        const violations = [
            currentFPS < thresholds.fps,
            currentLatency > thresholds.latency,
            cacheRatio < thresholds.cacheHitRatio
        ].filter(v => v).length;

        if (violations > 0) {
            const badge = this.container.querySelector('.violation-badge') || 
                         this.createViolationBadge();
            badge.textContent = violations;
            badge.style.display = 'block';
        } else {
            const badge = this.container.querySelector('.violation-badge');
            if (badge) badge.style.display = 'none';
        }
    }

    /**
     * Create violation badge if needed
     */
    createViolationBadge() {
        let badge = this.container.querySelector('.violation-badge');
        if (badge) return badge;

        badge = document.createElement('div');
        badge.className = 'violation-badge';
        
        const header = this.container.querySelector('.dashboard-header');
        if (header) {
            header.appendChild(badge);
        }

        return badge;
    }

    /**
     * Detect performance bottlenecks based on metrics
     */
    detectBottlenecks(metrics) {
        const bottlenecks = [];

        // Extract current metrics
        const currentFPS = metrics?.renderFPS?.slice(-1)[0] || 60;
        const currentLatency = metrics?.operationLatency?.slice(-1)[0] || 0;
        const cacheRatio = metrics?.cacheHitRatio?.slice(-1)[0] || 100;
        const asyncPending = metrics?.asyncPending?.slice(-1)[0] || 0;

        // FPS Bottleneck Detection
        if (currentFPS < 30) {
            bottlenecks.push({
                name: 'Low Frame Rate',
                severity: 'critical',
                metric_value: `${currentFPS.toFixed(0)} FPS (target: 60)`,
                description: 'Rendering performance is below 30 FPS, which impacts user experience',
                impact_level: 'Critical',
                suggestion: 'Reduce DOM complexity, optimize CSS, or simplify animations'
            });
        } else if (currentFPS < 45) {
            bottlenecks.push({
                name: 'Reduced Frame Rate',
                severity: 'warning',
                metric_value: `${currentFPS.toFixed(0)} FPS`,
                description: 'Frame rate is below optimal 60 FPS',
                impact_level: 'Medium',
                suggestion: 'Consider optimizing layout or reducing animation complexity'
            });
        }

        // Latency Bottleneck Detection
        if (currentLatency > 500) {
            bottlenecks.push({
                name: 'High Operation Latency',
                severity: 'critical',
                metric_value: `${currentLatency.toFixed(0)}ms (target: <200ms)`,
                description: 'Template operations are taking too long to complete',
                impact_level: 'Critical',
                suggestion: 'Profile operations to find slow code paths; consider caching or debouncing'
            });
        } else if (currentLatency > 200) {
            bottlenecks.push({
                name: 'Elevated Latency',
                severity: 'warning',
                metric_value: `${currentLatency.toFixed(0)}ms`,
                description: 'Operation latency is higher than optimal',
                impact_level: 'Medium',
                suggestion: 'Look for unnecessary computations or DOM operations'
            });
        }

        // Cache Hit Ratio Bottleneck
        if (cacheRatio < 50) {
            bottlenecks.push({
                name: 'Low Cache Hit Ratio',
                severity: 'warning',
                metric_value: `${cacheRatio.toFixed(1)}% (target: >80%)`,
                description: 'Cache efficiency is low - many operations are redundant',
                impact_level: 'Medium',
                suggestion: 'Implement or improve caching strategy for repeated operations'
            });
        }

        // Async Pending Operations
        if (asyncPending > 5) {
            bottlenecks.push({
                name: 'Async Operation Queue',
                severity: 'warning',
                metric_value: `${asyncPending} pending operations`,
                description: 'Multiple async operations are queued and not processing in parallel',
                impact_level: 'Low',
                suggestion: 'Consider batch processing or parallel execution where possible'
            });
        }

        return bottlenecks;
    }

    updateBottlenecksDisplay(healthStatus) {
        const bottlenecksList = this.container.querySelector('#perf-bottlenecks');
        if (!bottlenecksList) return;

        try {
            // Get bottleneck data - try backend first, then auto-detect
            let bottlenecks = [];
            
            if (window.bridge && window.bridge.getPerformanceBottlenecks) {
                const backendBottlenecks = window.bridge.getPerformanceBottlenecks();
                if (backendBottlenecks && backendBottlenecks.length > 0) {
                    bottlenecks = backendBottlenecks;
                }
            }
            
            // If no backend bottlenecks, auto-detect from metrics
            if (bottlenecks.length === 0) {
                const detectedBottlenecks = this.detectBottlenecks(this.metrics);
                bottlenecks = detectedBottlenecks;
            }
                
            if (!bottlenecks || bottlenecks.length === 0) {
                bottlenecksList.innerHTML = '<p class="perf-empty">✓ No bottlenecks detected</p>';
                return;
            }

            let html = '';
            bottlenecks.forEach((bottleneck, index) => {
                const severity = bottleneck.severity || 'info';
                const icon = severity === 'critical' ? '🔴' : severity === 'warning' ? '🟡' : '🔵';
                html += `
                    <div class="perf-bottleneck-item perf-severity-${severity}">
                        <div class="perf-bottleneck-header">
                            <span class="perf-bottleneck-icon">${icon}</span>
                            <span class="perf-bottleneck-name">${bottleneck.name || 'Unknown'}</span>
                            <span class="perf-bottleneck-metric">${bottleneck.metric_value || 'N/A'}</span>
                        </div>
                        <div class="perf-bottleneck-details">
                            <span class="perf-bottleneck-desc">${bottleneck.description || ''}</span>
                            ${bottleneck.suggestion ? `<span class="perf-bottleneck-suggestion">💡 ${bottleneck.suggestion}</span>` : ''}
                            <span class="perf-bottleneck-impact">Impact: ${bottleneck.impact_level || 'Medium'}</span>
                        </div>
                    </div>
                `;
            });
            bottlenecksList.innerHTML = html;
        } catch (error) {
            console.error('Error updating bottlenecks display:', error);
            bottlenecksList.innerHTML = '<p class="perf-empty">Error loading bottlenecks</p>';
        }
    }

    updateViolationsDisplay(healthStatus) {
        const violationsList = this.container.querySelector('#perf-violations');
        if (!violationsList) return;

        try {
            // Get violations from bridge if available
            if (window.bridge && window.bridge.getThresholdViolations) {
                const violations = window.bridge.getThresholdViolations();
                
                if (!violations || violations.length === 0) {
                    violationsList.innerHTML = '<p class="perf-empty">No violations</p>';
                    return;
                }

                let html = '';
                violations.forEach((violation, index) => {
                    const severity = violation.severity || 'warning';
                    const icon = severity === 'critical' ? '🔴' : '🟡';
                    html += `
                        <div class="perf-violation-item perf-severity-${severity}">
                            <div class="perf-violation-header">
                                <span class="perf-violation-icon">${icon}</span>
                                <span class="perf-violation-metric">${violation.metric || 'Unknown'}</span>
                                <span class="perf-violation-value">${violation.current_value || 'N/A'} / ${violation.threshold || 'N/A'}</span>
                            </div>
                            <div class="perf-violation-bar">
                                <div class="perf-violation-fill" style="width: ${Math.min(100, (violation.current_value / violation.threshold) * 100)}%"></div>
                            </div>
                        </div>
                    `;
                });
                violationsList.innerHTML = html;
            } else {
                violationsList.innerHTML = '<p class="perf-empty">Threshold violation detection unavailable</p>';
            }
        } catch (error) {
            console.error('Error updating violations display:', error);
            violationsList.innerHTML = '<p class="perf-empty">Error loading violations</p>';
        }
    }

    updateOperationsDisplay(healthStatus) {
        const operationsList = this.container.querySelector('#perf-operations');
        if (!operationsList) return;

        try {
            // Get recent operations from bridge if available
            if (window.bridge && window.bridge.getRecentOperations) {
                const operations = window.bridge.getRecentOperations();
                
                if (!operations || operations.length === 0) {
                    operationsList.innerHTML = '<p class="perf-empty">No recent operations</p>';
                    return;
                }

                let html = '';
                operations.slice(0, 10).forEach((op, index) => {
                    const status = op.status || 'pending';
                    const icon = status === 'completed' ? '✅' : status === 'failed' ? '❌' : '⏳';
                    const duration = op.duration_ms ? `${op.duration_ms}ms` : 'pending';
                    html += `
                        <div class="perf-operation-item perf-op-${status}">
                            <div class="perf-operation-header">
                                <span class="perf-operation-icon">${icon}</span>
                                <span class="perf-operation-name">${op.name || 'Unknown'}</span>
                                <span class="perf-operation-time">${duration}</span>
                            </div>
                            <div class="perf-operation-timestamp">
                                <span class="perf-timestamp-text">${op.timestamp || ''}</span>
                            </div>
                        </div>
                    `;
                });
                operationsList.innerHTML = html;
            } else {
                operationsList.innerHTML = '<p class="perf-empty">Recent operations tracking unavailable</p>';
            }
        } catch (error) {
            console.error('Error updating operations display:', error);
            operationsList.innerHTML = '<p class="perf-empty">Error loading operations</p>';
        }
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

    // ========== Audio Alerts ==========

    toggleAudioAlerts() {
        this.audioAlertsEnabled = !this.audioAlertsEnabled;
        localStorage.setItem('perf-audio-alerts', this.audioAlertsEnabled);
        
        const audioBtn = this.container.querySelector('.perf-toggle-audio');
        if (audioBtn) {
            this.updateAudioButtonUI(audioBtn);
        }
    }

    updateAudioButtonUI(audioBtn) {
        if (this.audioAlertsEnabled) {
            audioBtn.classList.add('audio-enabled');
            audioBtn.title = 'Audio alerts enabled - Click to disable';
        } else {
            audioBtn.classList.remove('audio-enabled');
            audioBtn.title = 'Audio alerts disabled - Click to enable';
        }
    }

    playAlertSound(type = 'warning') {
        if (!this.audioAlertsEnabled) return;

        try {
            // Initialize audio context on first use
            if (!this.audioContext) {
                const AudioContext = window.AudioContext || window.webkitAudioContext;
                if (!AudioContext) return;
                this.audioContext = new AudioContext();
            }

            const ctx = this.audioContext;
            const now = ctx.currentTime;

            // Create oscillator for tone
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);

            // Set volume (quiet to not startle user)
            gain.gain.setValueAtTime(0.2, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.5);

            // Set frequency based on alert type
            const frequencies = {
                'warning': 880,    // A5 - moderate warning
                'critical': 1320,  // E6 - high alert
                'info': 440,       // A4 - gentle notification
                'success': 523     // C5 - positive confirmation
            };

            osc.frequency.setValueAtTime(frequencies[type] || 880, now);

            // Play tone
            osc.start(now);
            osc.stop(now + 0.3);
        } catch (err) {
            console.warn('[Performance] Could not play audio alert:', err);
        }
    }

    checkAndAlertIfNeeded(metrics) {
        if (!this.audioAlertsEnabled) return;

        // Check for critical performance issues
        const fps = metrics.renderFPS;
        const latency = metrics.operationLatency;
        const cacheRatio = metrics.cacheHitRatio;

        if (fps < 30) {
            this.playAlertSound('critical');
        } else if (latency > 500) {
            this.playAlertSound('warning');
        } else if (cacheRatio < 0.5) {
            this.playAlertSound('warning');
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

    // ========== Export Methods ==========

    exportAsJSON() {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
        const data = {
            exportDate: new Date().toISOString(),
            metrics: this.getMetricsSummary(),
            timeline: {
                cacheHitRatio: this.metrics.cacheHitRatio,
                asyncPending: this.metrics.asyncPending,
                renderFPS: this.metrics.renderFPS,
                operationLatency: this.metrics.operationLatency
            },
            summary: {
                avgCacheHitRatio: this.calculateAverage(this.metrics.cacheHitRatio),
                avgAsyncPending: this.calculateAverage(this.metrics.asyncPending),
                avgRenderFPS: this.calculateAverage(this.metrics.renderFPS),
                avgOperationLatency: this.calculateAverage(this.metrics.operationLatency),
                maxOperationLatency: Math.max(...this.metrics.operationLatency, 0),
                minRenderFPS: Math.min(...this.metrics.renderFPS, 0)
            }
        };

        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        this.downloadFile(blob, `performance-report-${timestamp}.json`);
        this.showExportToast('Performance report exported as JSON');
    }

    exportAsCSV() {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
        const rows = [];

        // Header row
        rows.push(['Timestamp', 'Cache Hit Ratio (%)', 'Async Pending (ops)', 'Render FPS', 'Operation Latency (ms)'].join(','));

        // Data rows - merge all metric arrays
        const maxLength = Math.max(
            this.metrics.cacheHitRatio.length,
            this.metrics.asyncPending.length,
            this.metrics.renderFPS.length,
            this.metrics.operationLatency.length
        );

        for (let i = 0; i < maxLength; i++) {
            const row = [
                new Date(Date.now() - (maxLength - i) * this.refreshRateMs).toISOString(),
                (this.metrics.cacheHitRatio[i] || '').toString(),
                (this.metrics.asyncPending[i] || '').toString(),
                (this.metrics.renderFPS[i] || '').toString(),
                (this.metrics.operationLatency[i] || '').toString()
            ];
            rows.push(row.join(','));
        }

        // Add summary section
        rows.push(''); // Blank line
        rows.push('Summary Statistics');
        rows.push(['Metric', 'Value'].join(','));
        rows.push(['Average Cache Hit Ratio (%)', this.calculateAverage(this.metrics.cacheHitRatio).toFixed(2)].join(','));
        rows.push(['Average Async Pending (ops)', this.calculateAverage(this.metrics.asyncPending).toFixed(2)].join(','));
        rows.push(['Average Render FPS', this.calculateAverage(this.metrics.renderFPS).toFixed(2)].join(','));
        rows.push(['Average Operation Latency (ms)', this.calculateAverage(this.metrics.operationLatency).toFixed(2)].join(','));
        rows.push(['Max Operation Latency (ms)', Math.max(...this.metrics.operationLatency, 0).toFixed(2)].join(','));
        rows.push(['Min Render FPS', Math.min(...this.metrics.renderFPS, Infinity).toFixed(2)].join(','));

        const csv = rows.join('\n');
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        this.downloadFile(blob, `performance-report-${timestamp}.csv`);
        this.showExportToast('Performance report exported as CSV');
    }

    calculateAverage(values) {
        if (values.length === 0) return 0;
        return values.reduce((sum, val) => sum + (typeof val === 'number' ? val : 0), 0) / values.length;
    }

    downloadFile(blob, filename) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    showExportToast(message) {
        const toast = document.createElement('div');
        toast.className = 'perf-export-toast';
        toast.textContent = '✓ ' + message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PerformanceDashboardUI;
}
