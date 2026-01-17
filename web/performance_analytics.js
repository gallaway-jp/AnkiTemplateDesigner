/**
 * Performance Analytics Module (JavaScript/Frontend)
 * 
 * Provides real-time CSS/HTML size metrics, load time estimation,
 * performance warnings, and optimization recommendations.
 */

class PerformanceAnalytics {
    constructor() {
        this.metricsHistory = [];
        this.baselineMetrics = null;
        this.currentMetrics = null;
        this.performanceScore = 100;
        
        // Thresholds
        this.thresholds = {
            htmlSize: 50 * 1024,      // 50KB
            cssSize: 50 * 1024,       // 50KB
            totalSize: 100 * 1024,    // 100KB
            loadTime: 1000,           // 1000ms
            loadTimeCritical: 2000,   // 2000ms
            memory: 100,              // 100MB
            memoryCritical: 200,      // 200MB
        };
        
        // Cached DOM references
        this.dashboardContainer = null;
        this.metricsPanel = null;
        this.warningsPanel = null;
        this.recommendationsPanel = null;
    }
    
    /**
     * Record performance metrics snapshot
     */
    recordMetrics(htmlSize, cssSize, totalSize, loadTimeMs, memoryMb) {
        const metrics = {
            htmlSize: htmlSize,
            cssSize: cssSize,
            totalSize: totalSize,
            loadTimeMs: loadTimeMs,
            memoryUsageMb: memoryMb,
            timestamp: new Date().toISOString(),
        };
        
        this.metricsHistory.push(metrics);
        this.currentMetrics = metrics;
        this.updatePerformanceScore();
        
        return metrics;
    }
    
    /**
     * Set baseline metrics for comparison
     */
    setBaseline(metrics) {
        this.baselineMetrics = metrics || this.currentMetrics;
    }
    
    /**
     * Get latest metrics snapshot
     */
    getLatestMetrics() {
        return this.currentMetrics;
    }
    
    /**
     * Get metrics history
     */
    getMetricsHistory() {
        return this.metricsHistory;
    }
    
    /**
     * Check for performance issues
     */
    checkPerformanceWarnings() {
        const warnings = [];
        const metrics = this.currentMetrics;
        
        if (!metrics) {
            return warnings;
        }
        
        // Check HTML size
        if (metrics.htmlSize > this.thresholds.htmlSize) {
            const severity = metrics.htmlSize > this.thresholds.htmlSize * 2 ? "critical" : "warning";
            warnings.push({
                message: `HTML size (${this.formatBytes(metrics.htmlSize)}) exceeds recommended limit`,
                severity: severity,
                metricType: "html_size",
                currentValue: metrics.htmlSize,
                threshold: this.thresholds.htmlSize,
            });
        }
        
        // Check CSS size
        if (metrics.cssSize > this.thresholds.cssSize) {
            const severity = metrics.cssSize > this.thresholds.cssSize * 2 ? "critical" : "warning";
            warnings.push({
                message: `CSS size (${this.formatBytes(metrics.cssSize)}) exceeds recommended limit`,
                severity: severity,
                metricType: "css_size",
                currentValue: metrics.cssSize,
                threshold: this.thresholds.cssSize,
            });
        }
        
        // Check total size
        if (metrics.totalSize > this.thresholds.totalSize) {
            const severity = metrics.totalSize > this.thresholds.totalSize * 2 ? "critical" : "warning";
            warnings.push({
                message: `Total size (${this.formatBytes(metrics.totalSize)}) exceeds recommended limit`,
                severity: severity,
                metricType: "total_size",
                currentValue: metrics.totalSize,
                threshold: this.thresholds.totalSize,
            });
        }
        
        // Check load time
        if (metrics.loadTimeMs > this.thresholds.loadTimeCritical) {
            warnings.push({
                message: `Load time (${metrics.loadTimeMs}ms) is critically slow`,
                severity: "critical",
                metricType: "load_time_ms",
                currentValue: metrics.loadTimeMs,
                threshold: this.thresholds.loadTimeCritical,
            });
        } else if (metrics.loadTimeMs > this.thresholds.loadTime) {
            warnings.push({
                message: `Load time (${metrics.loadTimeMs}ms) is slow`,
                severity: "warning",
                metricType: "load_time_ms",
                currentValue: metrics.loadTimeMs,
                threshold: this.thresholds.loadTime,
            });
        }
        
        // Check memory
        if (metrics.memoryUsageMb > this.thresholds.memoryCritical) {
            warnings.push({
                message: `Memory usage (${metrics.memoryUsageMb}MB) is critically high`,
                severity: "critical",
                metricType: "memory_usage_mb",
                currentValue: metrics.memoryUsageMb,
                threshold: this.thresholds.memoryCritical,
            });
        } else if (metrics.memoryUsageMb > this.thresholds.memory) {
            warnings.push({
                message: `Memory usage (${metrics.memoryUsageMb}MB) is high`,
                severity: "warning",
                metricType: "memory_usage_mb",
                currentValue: metrics.memoryUsageMb,
                threshold: this.thresholds.memory,
            });
        }
        
        return warnings;
    }
    
    /**
     * Estimate load time based on size
     */
    estimateLoadTime(metrics) {
        if (!metrics) {
            return 0;
        }
        
        const baseTime = 50; // 50ms minimum
        const sizeFactor = metrics.totalSize / 1024; // ~1ms per KB
        const complexityFactor = (metrics.cssSize / 1024) * 0.5;
        
        let estimatedTime = baseTime + sizeFactor + complexityFactor;
        
        // Account for actual measured time
        if (metrics.loadTimeMs > 0) {
            estimatedTime = (metrics.loadTimeMs * 0.8) + (estimatedTime * 0.2);
        }
        
        return Math.max(estimatedTime, 10);
    }
    
    /**
     * Generate optimization recommendations
     */
    generateRecommendations() {
        const recommendations = [];
        const metrics = this.currentMetrics;
        
        if (!metrics) {
            return recommendations;
        }
        
        // HTML size recommendations
        if (metrics.htmlSize > this.thresholds.htmlSize) {
            recommendations.push({
                suggestion: "Consider splitting large HTML templates into smaller components",
                expectedImpact: "high",
                priority: "high",
                effort: "medium",
            });
            recommendations.push({
                suggestion: "Remove unused HTML elements and clean up whitespace",
                expectedImpact: "medium",
                priority: "high",
                effort: "low",
            });
        }
        
        // CSS size recommendations
        if (metrics.cssSize > this.thresholds.cssSize) {
            recommendations.push({
                suggestion: "Minify CSS to reduce file size",
                expectedImpact: "high",
                priority: "high",
                effort: "low",
            });
            recommendations.push({
                suggestion: "Remove unused CSS classes and selectors",
                expectedImpact: "medium",
                priority: "high",
                effort: "medium",
            });
        }
        
        // Load time recommendations
        if (metrics.loadTimeMs > this.thresholds.loadTime) {
            recommendations.push({
                suggestion: "Optimize CSS selectors for faster parsing",
                expectedImpact: "medium",
                priority: "high",
                effort: "medium",
            });
            recommendations.push({
                suggestion: "Defer loading of non-critical CSS and JavaScript",
                expectedImpact: "high",
                priority: "high",
                effort: "high",
            });
        }
        
        // Memory recommendations
        if (metrics.memoryUsageMb > this.thresholds.memory) {
            recommendations.push({
                suggestion: "Profile and optimize DOM manipulation code",
                expectedImpact: "medium",
                priority: "high",
                effort: "high",
            });
            recommendations.push({
                suggestion: "Implement lazy loading for images and heavy resources",
                expectedImpact: "high",
                priority: "high",
                effort: "high",
            });
        }
        
        // General recommendations
        recommendations.push({
            suggestion: "Enable gzip compression for better transport efficiency",
            expectedImpact: "high",
            priority: "medium",
            effort: "low",
        });
        
        return recommendations;
    }
    
    /**
     * Calculate performance trends
     */
    calculateTrends() {
        const trends = [];
        
        if (this.metricsHistory.length < 2) {
            return trends;
        }
        
        const previous = this.metricsHistory[this.metricsHistory.length - 2];
        const current = this.metricsHistory[this.metricsHistory.length - 1];
        
        // Total size trend
        const sizeChange = ((current.totalSize - previous.totalSize) / previous.totalSize) * 100;
        let direction = Math.abs(sizeChange) < 2 ? "stable" : (sizeChange > 0 ? "degrading" : "improving");
        
        trends.push({
            metricName: "total_size",
            direction: direction,
            changePercent: sizeChange,
            timePeriod: "recent",
        });
        
        // Load time trend
        if (previous.loadTimeMs > 0 && current.loadTimeMs > 0) {
            const timeChange = ((current.loadTimeMs - previous.loadTimeMs) / previous.loadTimeMs) * 100;
            direction = Math.abs(timeChange) < 5 ? "stable" : (timeChange > 0 ? "degrading" : "improving");
            
            trends.push({
                metricName: "load_time",
                direction: direction,
                changePercent: timeChange,
                timePeriod: "recent",
            });
        }
        
        // Memory trend
        const memChange = ((current.memoryUsageMb - previous.memoryUsageMb) / previous.memoryUsageMb) * 100;
        direction = Math.abs(memChange) < 3 ? "stable" : (memChange > 0 ? "degrading" : "improving");
        
        trends.push({
            metricName: "memory_usage",
            direction: direction,
            changePercent: memChange,
            timePeriod: "recent",
        });
        
        return trends;
    }
    
    /**
     * Compare with baseline metrics
     */
    compareWithBaseline(currentMetrics) {
        if (!this.baselineMetrics) {
            return null;
        }
        
        const baseline = this.baselineMetrics;
        
        return {
            htmlSizeDiff: this.calcDiffPercent(baseline.htmlSize, currentMetrics.htmlSize),
            cssSizeDiff: this.calcDiffPercent(baseline.cssSize, currentMetrics.cssSize),
            totalSizeDiff: this.calcDiffPercent(baseline.totalSize, currentMetrics.totalSize),
            loadTimeDiff: this.calcDiffPercent(baseline.loadTimeMs, currentMetrics.loadTimeMs),
            memoryDiff: this.calcDiffPercent(baseline.memoryUsageMb, currentMetrics.memoryUsageMb),
        };
    }
    
    /**
     * Render performance dashboard
     */
    renderDashboard(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container with id "${containerId}" not found`);
            return;
        }
        
        this.dashboardContainer = container;
        
        const html = `
            <div class="performance-dashboard">
                <div class="perf-header">
                    <h3 class="perf-title">Performance Analytics</h3>
                    <div class="perf-score">
                        <div class="perf-score-value">${this.performanceScore.toFixed(0)}</div>
                        <div class="perf-score-label">Performance Score</div>
                    </div>
                </div>
                
                <div id="metrics-panel" class="perf-metrics"></div>
                
                <div id="warnings-panel" class="perf-warnings"></div>
                
                <div id="recommendations-panel" class="perf-recommendations"></div>
                
                <div id="trends-panel" class="perf-trends"></div>
            </div>
        `;
        
        container.innerHTML = html;
        
        this.metricsPanel = container.querySelector("#metrics-panel");
        this.warningsPanel = container.querySelector("#warnings-panel");
        this.recommendationsPanel = container.querySelector("#recommendations-panel");
        
        this.updateDashboard();
    }
    
    /**
     * Update dashboard with current data
     */
    updateDashboard() {
        if (!this.dashboardContainer) {
            return;
        }
        
        const metrics = this.currentMetrics;
        if (!metrics) {
            return;
        }
        
        // Update metrics
        this.updateMetricsPanel();
        
        // Update warnings
        this.updateWarningsPanel();
        
        // Update recommendations
        this.updateRecommendationsPanel();
        
        // Update trends
        this.updateTrendsPanel();
    }
    
    /**
     * Update metrics panel
     */
    updateMetricsPanel() {
        if (!this.metricsPanel || !this.currentMetrics) {
            return;
        }
        
        const m = this.currentMetrics;
        
        const html = `
            <div class="perf-metric">
                <div class="metric-label">HTML Size</div>
                <div class="metric-value">${this.formatBytes(m.htmlSize)}</div>
            </div>
            <div class="perf-metric">
                <div class="metric-label">CSS Size</div>
                <div class="metric-value">${this.formatBytes(m.cssSize)}</div>
            </div>
            <div class="perf-metric">
                <div class="metric-label">Total Size</div>
                <div class="metric-value">${this.formatBytes(m.totalSize)}</div>
            </div>
            <div class="perf-metric">
                <div class="metric-label">Load Time</div>
                <div class="metric-value">${m.loadTimeMs}</div>
                <div class="metric-unit">ms</div>
            </div>
            <div class="perf-metric">
                <div class="metric-label">Memory</div>
                <div class="metric-value">${m.memoryUsageMb.toFixed(1)}</div>
                <div class="metric-unit">MB</div>
            </div>
        `;
        
        this.metricsPanel.innerHTML = html;
    }
    
    /**
     * Update warnings panel
     */
    updateWarningsPanel() {
        if (!this.warningsPanel) {
            return;
        }
        
        const warnings = this.checkPerformanceWarnings();
        
        if (warnings.length === 0) {
            this.warningsPanel.innerHTML = '<div class="empty-state">✓ No performance issues detected</div>';
            return;
        }
        
        const html = `
            <div class="warnings-header">⚠ Performance Warnings (${warnings.length})</div>
            ${warnings.map(w => `
                <div class="perf-warning ${w.severity}">
                    <div class="warning-icon">${this.getSeverityIcon(w.severity)}</div>
                    <div class="warning-content">
                        <div class="warning-message">${w.message}</div>
                        <div class="warning-severity">${w.severity.toUpperCase()}</div>
                    </div>
                </div>
            `).join('')}
        `;
        
        this.warningsPanel.innerHTML = html;
    }
    
    /**
     * Update recommendations panel
     */
    updateRecommendationsPanel() {
        if (!this.recommendationsPanel) {
            return;
        }
        
        const recommendations = this.generateRecommendations();
        
        if (recommendations.length === 0) {
            this.recommendationsPanel.innerHTML = '';
            return;
        }
        
        const html = `
            <div class="recommendations-header">💡 Optimization Recommendations</div>
            ${recommendations.map(r => `
                <div class="perf-recommendation">
                    <div class="rec-icon">→</div>
                    <div class="rec-content">
                        <div class="rec-suggestion">${r.suggestion}</div>
                        <div class="rec-impact">Impact: ${r.expectedImpact}</div>
                    </div>
                </div>
            `).join('')}
        `;
        
        this.recommendationsPanel.innerHTML = html;
    }
    
    /**
     * Update trends panel
     */
    updateTrendsPanel() {
        if (!this.dashboardContainer) {
            return;
        }
        
        const trendsPanel = this.dashboardContainer.querySelector("#trends-panel");
        if (!trendsPanel) {
            return;
        }
        
        const trends = this.calculateTrends();
        
        if (trends.length === 0) {
            trendsPanel.innerHTML = '';
            return;
        }
        
        const html = trends.map(t => `
            <div class="perf-trend">
                <div class="trend-icon ${t.direction}">${this.getTrendIcon(t.direction)}</div>
                <div class="trend-label">${t.metricName}</div>
                <div class="trend-value">${t.changePercent > 0 ? '+' : ''}${t.changePercent.toFixed(1)}%</div>
            </div>
        `).join('');
        
        trendsPanel.innerHTML = html || '';
    }
    
    /**
     * Export report to JSON
     */
    exportToJSON() {
        const report = {
            timestamp: new Date().toISOString(),
            performanceScore: this.performanceScore,
            metrics: this.currentMetrics,
            warnings: this.checkPerformanceWarnings(),
            recommendations: this.generateRecommendations(),
            trends: this.calculateTrends(),
            baselineComparison: this.baselineMetrics ? this.compareWithBaseline(this.currentMetrics) : null,
        };
        
        return JSON.stringify(report, null, 2);
    }
    
    /**
     * Update overall performance score
     */
    updatePerformanceScore() {
        if (!this.currentMetrics) {
            this.performanceScore = 100;
            return;
        }
        
        let score = 100;
        const m = this.currentMetrics;
        
        // Deduct for size violations
        if (m.htmlSize > this.thresholds.htmlSize) {
            score -= Math.min(20, (m.htmlSize - this.thresholds.htmlSize) / 1024);
        }
        if (m.cssSize > this.thresholds.cssSize) {
            score -= Math.min(20, (m.cssSize - this.thresholds.cssSize) / 1024);
        }
        if (m.totalSize > this.thresholds.totalSize) {
            score -= Math.min(20, (m.totalSize - this.thresholds.totalSize) / 1024);
        }
        
        // Deduct for load time
        if (m.loadTimeMs > this.thresholds.loadTime) {
            score -= Math.min(15, (m.loadTimeMs - this.thresholds.loadTime) / 100);
        }
        
        // Deduct for memory
        if (m.memoryUsageMb > this.thresholds.memory) {
            score -= Math.min(15, (m.memoryUsageMb - this.thresholds.memory) / 10);
        }
        
        this.performanceScore = Math.max(0, Math.min(100, score));
    }
    
    /**
     * Helper: format bytes
     */
    formatBytes(bytes) {
        if (bytes < 1024) return bytes + "B";
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + "KB";
        return (bytes / (1024 * 1024)).toFixed(1) + "MB";
    }
    
    /**
     * Helper: calculate percentage difference
     */
    calcDiffPercent(baseline, current) {
        if (baseline === 0) return 0;
        return ((current - baseline) / baseline) * 100;
    }
    
    /**
     * Helper: get severity icon
     */
    getSeverityIcon(severity) {
        const icons = {
            "info": "ℹ",
            "warning": "⚠",
            "error": "✕",
            "critical": "⚠",
        };
        return icons[severity] || "•";
    }
    
    /**
     * Helper: get trend icon
     */
    getTrendIcon(direction) {
        const icons = {
            "improving": "↓",
            "stable": "→",
            "degrading": "↑",
        };
        return icons[direction] || "→";
    }
}

// Export for use in module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PerformanceAnalytics;
}
