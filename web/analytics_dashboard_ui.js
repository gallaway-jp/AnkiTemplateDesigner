"""Analytics Dashboard UI - JavaScript frontend."""

class AnalyticsDashboardUI {
    constructor(containerId = 'analytics-dashboard') {
        this.container = document.getElementById(containerId);
        this.data = null;
        this.currentTab = 'overview';
        this.init();
    }

    init() {
        this.render();
        this.attachEventListeners();
    }

    render() {
        if (!this.container) return;

        this.container.innerHTML = `
            <div class="analytics-dashboard">
                <header class="analytics-header">
                    <h1>Analytics & Intelligence</h1>
                    <div class="header-actions">
                        <button class="btn-refresh" id="refresh-analytics" title="Refresh data">
                            ⟳ Refresh
                        </button>
                        <button class="btn-export" id="export-analytics" title="Export analytics">
                            ⬇ Export
                        </button>
                    </div>
                </header>

                <div class="analytics-tabs">
                    <button class="tab-btn active" data-tab="overview">Overview</button>
                    <button class="tab-btn" data-tab="metrics">Metrics</button>
                    <button class="tab-btn" data-tab="insights">Insights</button>
                    <button class="tab-btn" data-tab="anomalies">Anomalies</button>
                    <button class="tab-btn" data-tab="settings">Settings</button>
                </div>

                <div class="analytics-content">
                    <!-- Overview Tab -->
                    <div id="tab-overview" class="tab-content active">
                        ${this.renderOverviewTab()}
                    </div>

                    <!-- Metrics Tab -->
                    <div id="tab-metrics" class="tab-content">
                        ${this.renderMetricsTab()}
                    </div>

                    <!-- Insights Tab -->
                    <div id="tab-insights" class="tab-content">
                        ${this.renderInsightsTab()}
                    </div>

                    <!-- Anomalies Tab -->
                    <div id="tab-anomalies" class="tab-content">
                        ${this.renderAnomaliesTab()}
                    </div>

                    <!-- Settings Tab -->
                    <div id="tab-settings" class="tab-content">
                        ${this.renderSettingsTab()}
                    </div>
                </div>
            </div>
        `;
    }

    renderOverviewTab() {
        return `
            <div class="overview-section">
                <h2>Dashboard Overview</h2>
                <div class="summary-cards">
                    <div class="summary-card">
                        <div class="card-title">Total Events</div>
                        <div class="card-value" id="total-events">0</div>
                        <div class="card-unit">events</div>
                    </div>
                    <div class="summary-card">
                        <div class="card-title">Avg Latency</div>
                        <div class="card-value" id="avg-latency">0</div>
                        <div class="card-unit">ms</div>
                    </div>
                    <div class="summary-card">
                        <div class="card-title">Error Rate</div>
                        <div class="card-value" id="error-rate">0</div>
                        <div class="card-unit">%</div>
                    </div>
                    <div class="summary-card">
                        <div class="card-title">Active Events</div>
                        <div class="card-value" id="active-events">0</div>
                        <div class="card-unit">types</div>
                    </div>
                </div>

                <div class="recent-insights">
                    <h3>Recent Insights</h3>
                    <div id="recent-insights-list" class="insights-list"></div>
                </div>
            </div>
        `;
    }

    renderMetricsTab() {
        return `
            <div class="metrics-section">
                <h2>Performance Metrics</h2>
                <div class="metrics-filters">
                    <label>
                        Time Period:
                        <select id="metric-period">
                            <option value="7">Last 7 days</option>
                            <option value="14">Last 14 days</option>
                            <option value="30">Last 30 days</option>
                        </select>
                    </label>
                    <label>
                        Aggregation:
                        <select id="metric-aggregation">
                            <option value="hourly">Hourly</option>
                            <option value="daily">Daily</option>
                            <option value="weekly">Weekly</option>
                        </select>
                    </label>
                </div>

                <div class="metrics-grid">
                    <div class="metric-card">
                        <h4>Latency Trend</h4>
                        <div id="latency-chart" class="metric-chart"></div>
                    </div>
                    <div class="metric-card">
                        <h4>Error Rate Trend</h4>
                        <div id="error-chart" class="metric-chart"></div>
                    </div>
                    <div class="metric-card">
                        <h4>Event Distribution</h4>
                        <div id="event-chart" class="metric-chart"></div>
                    </div>
                    <div class="metric-card">
                        <h4>Performance Percentiles</h4>
                        <div id="percentile-chart" class="metric-chart"></div>
                    </div>
                </div>

                <div class="metrics-table">
                    <h3>Detailed Metrics</h3>
                    <table id="metrics-table">
                        <thead>
                            <tr>
                                <th>Metric Name</th>
                                <th>Value</th>
                                <th>Unit</th>
                                <th>Timestamp</th>
                            </tr>
                        </thead>
                        <tbody id="metrics-tbody"></tbody>
                    </table>
                </div>
            </div>
        `;
    }

    renderInsightsTab() {
        return `
            <div class="insights-section">
                <h2>Intelligence Insights</h2>
                <div class="insights-filters">
                    <label>
                        Category:
                        <select id="insight-category">
                            <option value="">All</option>
                            <option value="performance">Performance</option>
                            <option value="usage">Usage</option>
                            <option value="recommendations">Recommendations</option>
                            <option value="anomalies">Anomalies</option>
                        </select>
                    </label>
                    <label>
                        Severity:
                        <select id="insight-severity">
                            <option value="">All</option>
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                        </select>
                    </label>
                </div>

                <div id="insights-container" class="insights-container">
                    <p class="loading">Loading insights...</p>
                </div>
            </div>
        `;
    }

    renderAnomaliesTab() {
        return `
            <div class="anomalies-section">
                <h2>Detected Anomalies</h2>
                <div class="anomaly-stats">
                    <div class="stat-item">
                        <span class="stat-label">Critical</span>
                        <span class="stat-value" id="critical-count">0</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">High</span>
                        <span class="stat-value" id="high-count">0</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Medium</span>
                        <span class="stat-value" id="medium-count">0</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Low</span>
                        <span class="stat-value" id="low-count">0</span>
                    </div>
                </div>

                <div id="anomalies-container" class="anomalies-container">
                    <p class="loading">Loading anomalies...</p>
                </div>
            </div>
        `;
    }

    renderSettingsTab() {
        return `
            <div class="settings-section">
                <h2>Analytics Settings</h2>

                <div class="settings-group">
                    <h3>Analytics Collection</h3>
                    <label class="setting-item">
                        <input type="checkbox" id="enable-analytics" checked>
                        <span>Enable analytics collection</span>
                    </label>
                    <label class="setting-item">
                        <span>Event Sampling Rate</span>
                        <input type="range" id="sampling-rate" min="0" max="100" value="100" step="10">
                        <span id="sampling-rate-display">100%</span>
                    </label>
                </div>

                <div class="settings-group">
                    <h3>Data Retention</h3>
                    <label class="setting-item">
                        <span>Retain data for (days)</span>
                        <input type="number" id="retention-days" min="1" max="365" value="90">
                    </label>
                    <button class="btn-secondary" id="cleanup-old-data">
                        Clean Up Old Data
                    </button>
                </div>

                <div class="settings-group">
                    <h3>Data Export</h3>
                    <button class="btn-secondary" id="export-json">
                        Export as JSON
                    </button>
                    <button class="btn-secondary" id="export-csv">
                        Export as CSV
                    </button>
                </div>

                <div class="settings-group">
                    <h3>System Info</h3>
                    <div id="system-info" class="info-display"></div>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // Refresh button
        const refreshBtn = document.getElementById('refresh-analytics');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }

        // Export button
        const exportBtn = document.getElementById('export-analytics');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.showExportMenu());
        }

        // Settings listeners
        const samplingRate = document.getElementById('sampling-rate');
        if (samplingRate) {
            samplingRate.addEventListener('change', (e) => {
                document.getElementById('sampling-rate-display').textContent = e.target.value + '%';
                this.updateSamplingRate(parseInt(e.target.value));
            });
        }

        const retentionDays = document.getElementById('retention-days');
        if (retentionDays) {
            retentionDays.addEventListener('change', (e) => {
                this.updateRetentionDays(parseInt(e.target.value));
            });
        }

        const exportJson = document.getElementById('export-json');
        if (exportJson) {
            exportJson.addEventListener('click', () => this.exportData('json'));
        }

        const exportCsv = document.getElementById('export-csv');
        if (exportCsv) {
            exportCsv.addEventListener('click', () => this.exportData('csv'));
        }

        const cleanupBtn = document.getElementById('cleanup-old-data');
        if (cleanupBtn) {
            cleanupBtn.addEventListener('click', () => this.cleanupOldData());
        }
    }

    switchTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });

        // Deactivate all buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Show selected tab
        const tabElement = document.getElementById(`tab-${tabName}`);
        if (tabElement) {
            tabElement.classList.add('active');
        }

        // Activate button
        event.target.classList.add('active');
        this.currentTab = tabName;

        // Load tab-specific data
        if (tabName === 'overview') {
            this.loadDashboardData();
        } else if (tabName === 'metrics') {
            this.loadMetrics();
        } else if (tabName === 'insights') {
            this.loadInsights();
        } else if (tabName === 'anomalies') {
            this.loadAnomalies();
        } else if (tabName === 'settings') {
            this.loadSystemInfo();
        }
    }

    refreshData() {
        console.log('[Analytics] Refreshing data...');
        this.loadDashboardData();
    }

    loadDashboardData() {
        // Fetch dashboard data from backend API
        if (!window.bridge || !window.bridge.getAnalyticsDashboardData) {
            console.warn('[Analytics] Bridge not available');
            return;
        }

        try {
            const dataJson = window.bridge.getAnalyticsDashboardData();
            const data = JSON.parse(dataJson);
            
            // Update summary cards
            document.getElementById('total-events').textContent = data.total_events || 0;
            document.getElementById('avg-latency').textContent = (data.avg_latency || 0).toFixed(2);
            document.getElementById('error-rate').textContent = (data.error_rate || 0).toFixed(1);
            document.getElementById('active-events').textContent = data.active_events || 0;
            
            // Update recent insights
            this.updateRecentInsights(data.recent_insights || []);
            
            console.log('[Analytics] Dashboard data loaded');
        } catch (e) {
            console.error('[Analytics] Failed to load dashboard data:', e);
            showToast('Failed to load analytics data', 'error', 3000);
        }
    }

    updateRecentInsights(insights) {
        const container = document.getElementById('recent-insights-list');
        if (!container) return;

        if (!insights || insights.length === 0) {
            container.innerHTML = '<p class="empty-state">No insights available</p>';
            return;
        }

        container.innerHTML = insights.map(insight => `
            <div class="insight-item">
                <div class="insight-header">
                    <h4>${insight.title}</h4>
                    <span class="insight-severity ${insight.severity}">${insight.severity}</span>
                </div>
                <p class="insight-description">${insight.description}</p>
            </div>
        `).join('');
    }

    loadMetrics() {
        console.log('[Analytics] Loading metrics...');
        
        if (!window.bridge || !window.bridge.getAnalyticsMetrics) {
            console.warn('[Analytics] Bridge not available');
            return;
        }

        try {
            // Get metrics for selected period and aggregation
            const period = document.getElementById('metric-period')?.value || '7';
            const aggregation = document.getElementById('metric-aggregation')?.value || 'daily';
            
            const metricsJson = window.bridge.getAnalyticsMetrics('latency', `${period}d`);
            const metrics = JSON.parse(metricsJson);
            
            // Update metrics table (simplified - real implementation would render charts)
            const tableContainer = document.getElementById('metrics-table');
            if (tableContainer) {
                tableContainer.innerHTML = `<tr><td colspan="4">Metrics loaded for ${period} days (${aggregation})</td></tr>`;
            }
            
            console.log('[Analytics] Metrics loaded');
        } catch (e) {
            console.error('[Analytics] Failed to load metrics:', e);
        }
    }

    loadInsights() {
        console.log('[Analytics] Loading insights...');
        
        if (!window.bridge || !window.bridge.getAnalyticsInsights) {
            console.warn('[Analytics] Bridge not available');
            return;
        }

        try {
            const insightsJson = window.bridge.getAnalyticsInsights();
            const insights = JSON.parse(insightsJson);
            
            // Render insights in tab
            const container = document.getElementById('tab-insights');
            if (container) {
                const content = `
                    <div class="insights-section">
                        <h2>Performance Insights</h2>
                        <div class="insights-list">
                            ${insights.length === 0 ? '<p class="empty-state">No insights available</p>' :
                              insights.map(insight => `
                                <div class="insight-card">
                                    <div class="insight-header">
                                        <h3>${insight.title}</h3>
                                        <span class="severity-badge ${insight.severity}">${insight.severity}</span>
                                    </div>
                                    <p class="insight-description">${insight.description}</p>
                                    <div class="insight-category">Category: ${insight.category}</div>
                                </div>
                            `).join('')
                            }
                        </div>
                    </div>
                `;
                container.innerHTML = content;
            }
            
            console.log('[Analytics] Insights loaded:', insights.length);
        } catch (e) {
            console.error('[Analytics] Failed to load insights:', e);
        }
    }

    loadAnomalies() {
        console.log('[Analytics] Loading anomalies...');
        
        if (!window.bridge || !window.bridge.getAnalyticsAnomalies) {
            console.warn('[Analytics] Bridge not available');
            return;
        }

        try {
            const anomaliesJson = window.bridge.getAnalyticsAnomalies();
            const anomalies = JSON.parse(anomaliesJson);
            
            // Render anomalies in tab
            const container = document.getElementById('tab-anomalies');
            if (container) {
                const content = `
                    <div class="anomalies-section">
                        <h2>Detected Anomalies</h2>
                        <div class="anomalies-list">
                            ${anomalies.length === 0 ? '<p class="empty-state">No anomalies detected</p>' :
                              anomalies.map(anomaly => `
                                <div class="anomaly-card">
                                    <div class="anomaly-header">
                                        <h3>${anomaly.metric_name}</h3>
                                        <span class="severity-badge ${anomaly.severity}">${anomaly.severity}</span>
                                    </div>
                                    <p class="anomaly-description">${anomaly.description}</p>
                                    <div class="anomaly-details">
                                        <span>Expected: ${anomaly.expected_value.toFixed(2)}</span>
                                        <span>Actual: ${anomaly.actual_value.toFixed(2)}</span>
                                    </div>
                                </div>
                            `).join('')
                            }
                        </div>
                    </div>
                `;
                container.innerHTML = content;
            }
            
            console.log('[Analytics] Anomalies loaded:', anomalies.length);
        } catch (e) {
            console.error('[Analytics] Failed to load anomalies:', e);
        }
    }

    loadSystemInfo() {
        console.log('Loading system info...');
        // Load system information
    }

    updateSamplingRate(rate) {
        if (!window.bridge || !window.bridge.updateAnalyticsSamplingRate) {
            console.warn('[Analytics] Bridge not available for updating sampling rate');
            showToast('Settings not available', 'error', 3000);
            return;
        }

        try {
            const success = window.bridge.updateAnalyticsSamplingRate(rate);
            if (success) {
                console.log(`[Analytics] Sampling rate updated to ${rate}%`);
                showToast(`Sampling rate set to ${rate}%`, 'success', 3000);
            } else {
                showToast('Failed to update sampling rate', 'error', 3000);
            }
        } catch (e) {
            console.error('[Analytics] Error updating sampling rate:', e);
            showToast(`Error: ${e.message}`, 'error', 3000);
        }
    }

    updateRetentionDays(days) {
        if (!window.bridge || !window.bridge.updateAnalyticsRetention) {
            console.warn('[Analytics] Bridge not available for updating retention');
            showToast('Settings not available', 'error', 3000);
            return;
        }

        try {
            const success = window.bridge.updateAnalyticsRetention(days);
            if (success) {
                console.log(`[Analytics] Retention updated to ${days} days`);
                showToast(`Retention set to ${days} days`, 'success', 3000);
            } else {
                showToast('Failed to update retention', 'error', 3000);
            }
        } catch (e) {
            console.error('[Analytics] Error updating retention:', e);
            showToast(`Error: ${e.message}`, 'error', 3000);
        }
    }

    exportData(format) {
        console.log(`Exporting data as ${format}`);
        // Trigger export
    }

    cleanupOldData() {
        if (!confirm('Delete all analytics data older than the retention period? This cannot be undone.')) {
            return;
        }

        if (!window.bridge || !window.bridge.cleanupAnalyticsData) {
            console.warn('[Analytics] Bridge not available for cleanup');
            showToast('Cleanup not available', 'error', 3000);
            return;
        }

        try {
            showToast('Cleaning up old data...', 'info', 3000);
            const result = window.bridge.cleanupAnalyticsData();
            if (result) {
                console.log('[Analytics] Cleanup completed');
                showToast('Old data cleaned up successfully', 'success', 3000);
                // Reload dashboard to show updated stats
                this.loadDashboardData();
            } else {
                showToast('Cleanup failed', 'error', 3000);
            }
        } catch (e) {
            console.error('[Analytics] Error during cleanup:', e);
            showToast(`Error: ${e.message}`, 'error', 3000);
        }
    }

    showExportMenu() {
        // Create export menu
        const menu = document.createElement('div');
        menu.className = 'export-menu';
        menu.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            min-width: 150px;
        `;
        
        const options = [
            { format: 'json', label: 'JSON' },
            { format: 'csv', label: 'CSV' },
            { format: 'pdf', label: 'PDF Report' }
        ];
        
        menu.innerHTML = options.map(opt => `
            <button data-format="${opt.format}" style="
                display: block;
                width: 100%;
                padding: 10px 15px;
                border: none;
                background: transparent;
                text-align: left;
                cursor: pointer;
                border-bottom: 1px solid var(--border-color);
            ">${opt.label}</button>
        `).join('');
        
        // Add click handlers
        menu.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const format = e.target.getAttribute('data-format');
                this.exportData(format);
                document.body.removeChild(menu);
            });
            btn.addEventListener('mouseover', (e) => {
                e.target.style.background = 'var(--bg-tertiary)';
            });
            btn.addEventListener('mouseout', (e) => {
                e.target.style.background = 'transparent';
            });
        });
        
        document.body.appendChild(menu);
        
        // Close menu on outside click
        const closeMenu = (e) => {
            if (!menu.contains(e.target)) {
                document.body.removeChild(menu);
                document.removeEventListener('click', closeMenu);
            }
        };
        setTimeout(() => document.addEventListener('click', closeMenu), 0);
    }

    exportData(format) {
        if (!window.bridge || !window.bridge.exportAnalyticsData) {
            console.warn('[Analytics] Bridge not available for export');
            showToast('Export not available', 'error', 3000);
            return;
        }

        try {
            showToast(`Exporting as ${format.toUpperCase()}...`, 'info', 3000);
            const data = window.bridge.exportAnalyticsData(format);
            if (data) {
                // Create download link
                const link = document.createElement('a');
                const timestamp = new Date().toISOString().slice(0, 10);
                const filename = `analytics-${timestamp}.${format === 'pdf' ? 'pdf' : format}`;
                
                if (format === 'json') {
                    const blob = new Blob([data], { type: 'application/json' });
                    link.href = URL.createObjectURL(blob);
                } else if (format === 'csv') {
                    const blob = new Blob([data], { type: 'text/csv' });
                    link.href = URL.createObjectURL(blob);
                } else if (format === 'pdf') {
                    // PDF would typically be a buffer or base64 encoded
                    const blob = new Blob([data], { type: 'application/pdf' });
                    link.href = URL.createObjectURL(blob);
                }
                
                link.download = filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                console.log(`[Analytics] Exported as ${format}`);
                showToast(`Exported as ${filename}`, 'success', 4000);
            } else {
                showToast('No data to export', 'warning', 3000);
            }
        } catch (e) {
            console.error('[Analytics] Error exporting data:', e);
            showToast(`Error: ${e.message}`, 'error', 3000);
        }
    }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.analyticsDashboard = new AnalyticsDashboardUI();
    });
} else {
    window.analyticsDashboard = new AnalyticsDashboardUI();
}
