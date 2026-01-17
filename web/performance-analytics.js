/**
 * Performance Analytics Module
 *
 * Real-time performance monitoring and optimization insights for templates:
 * - Live CSS/HTML size metrics
 * - Load time estimation
 * - Optimization recommendations
 * - Performance warnings
 * - Memory usage tracking
 * - Benchmark comparison
 * - Performance scoring (0-100)
 */

class PerformanceAnalytics {
  constructor() {
    this.metrics = null;
    this.history = [];
    this.updateInterval = null;
    this.listeners = new Map();
  }

  /**
   * Initialize performance analytics
   */
  initialize() {
    this.setupEventListeners();
    this.startMonitoring();
    this.dispatchEvent('initialized');
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    document.addEventListener('templateUpdated', (e) => this.onTemplateUpdated(e));
    document.addEventListener('htmlEdited', (e) => this.onHtmlEdited(e));
    document.addEventListener('cssEdited', (e) => this.onCssEdited(e));
  }

  /**
   * Start monitoring performance
   */
  startMonitoring() {
    this.updateInterval = setInterval(() => {
      this.updateMetrics();
    }, 1000); // Update every second
  }

  /**
   * Stop monitoring
   */
  stopMonitoring() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
  }

  /**
   * Calculate HTML size in bytes
   */
  calculateHtmlSize(html) {
    return new Blob([html]).size;
  }

  /**
   * Calculate CSS size in bytes
   */
  calculateCssSize(css) {
    return new Blob([css]).size;
  }

  /**
   * Calculate total size
   */
  calculateTotalSize(html, css) {
    return this.calculateHtmlSize(html) + this.calculateCssSize(css);
  }

  /**
   * Estimate load time in milliseconds
   */
  estimateLoadTime(html, css) {
    const size = this.calculateTotalSize(html, css);
    // Rough estimate: 1KB = 2ms
    return Math.max(10, size / 500);
  }

  /**
   * Estimate render time
   */
  estimateRenderTime(elementCount) {
    // Rough estimate: 0.5ms per element
    return elementCount * 0.5;
  }

  /**
   * Estimate DOM memory
   */
  estimateDomMemory(html) {
    const size = this.calculateHtmlSize(html);
    // Estimate based on compressed size
    return Math.ceil(size * 1.2);
  }

  /**
   * Get performance score (0-100)
   */
  calculatePerformanceScore(metrics) {
    let score = 100;

    // Penalize large size
    const sizePenalty = Math.min(50, metrics.total_size / 10000);
    score -= sizePenalty;

    // Penalize long load time
    const timePenalty = Math.min(30, metrics.load_time_ms / 100);
    score -= timePenalty;

    return Math.max(0, Math.round(score));
  }

  /**
   * Detect performance warnings
   */
  detectWarnings(html, css) {
    const warnings = [];

    // Check CSS size
    const cssSize = this.calculateCssSize(css);
    if (cssSize > 50000) {
      warnings.push({
        type: 'css_size',
        message: `CSS size exceeds 50KB (${(cssSize / 1024).toFixed(1)}KB)`,
        severity: 'warning',
      });
    }

    // Check HTML size
    const htmlSize = this.calculateHtmlSize(html);
    if (htmlSize > 100000) {
      warnings.push({
        type: 'html_size',
        message: `HTML size exceeds 100KB (${(htmlSize / 1024).toFixed(1)}KB)`,
        severity: 'error',
      });
    }

    // Check inline styles
    const inlineCount = (html.match(/style="/g) || []).length;
    if (inlineCount > 5) {
      warnings.push({
        type: 'inline_styles',
        message: `Found ${inlineCount} inline styles - consider using CSS classes`,
        severity: 'warning',
      });
    }

    // Check unused CSS
    const unusedCss = this.findUnusedCss(html, css);
    if (unusedCss.length > 0) {
      warnings.push({
        type: 'unused_css',
        message: `Found ${unusedCss.length} unused CSS classes`,
        severity: 'info',
      });
    }

    return warnings;
  }

  /**
   * Find unused CSS classes
   */
  findUnusedCss(html, css) {
    // Extract class selectors from CSS
    const cssClasses = new Set();
    const classPattern = /\.([a-zA-Z_-][a-zA-Z0-9_-]*)/g;
    let match;
    while ((match = classPattern.exec(css)) !== null) {
      cssClasses.add(match[1]);
    }

    // Extract used classes from HTML
    const usedClasses = new Set();
    const htmlClassPattern = /class="([^"]*)"/g;
    while ((match = htmlClassPattern.exec(html)) !== null) {
      match[1].split(' ').forEach(cls => usedClasses.add(cls));
    }

    // Find unused
    const unused = [];
    for (const cls of cssClasses) {
      if (!usedClasses.has(cls)) {
        unused.push(cls);
      }
    }

    return unused;
  }

  /**
   * Get optimization recommendations
   */
  getRecommendations(html, css) {
    const recommendations = [];

    // Minification check
    if (css.includes('\n') || css.includes('  ')) {
      recommendations.push({
        type: 'minification',
        suggestion: 'Consider minifying CSS and HTML',
        impact: 'medium',
      });
    }

    // Unused CSS
    const unusedCss = this.findUnusedCss(html, css);
    if (unusedCss.length > 0) {
      recommendations.push({
        type: 'unused_css',
        suggestion: `Remove ${unusedCss.length} unused CSS rules`,
        impact: 'high',
      });
    }

    // Duplicate selectors
    const selectorCount = (css.match(/\{/g) || []).length;
    const lines = css.split('\n');
    if (lines.length > selectorCount * 2) {
      recommendations.push({
        type: 'consolidation',
        suggestion: 'Consolidate related CSS rules',
        impact: 'medium',
      });
    }

    // Complex selectors
    const pseudoCount = (css.match(/:[a-z-]+/g) || []).length;
    if (pseudoCount > 5) {
      recommendations.push({
        type: 'selector_complexity',
        suggestion: 'Simplify CSS selectors for better performance',
        impact: 'low',
      });
    }

    return recommendations;
  }

  /**
   * Perform complete analysis
   */
  analyzeTemplate(html, css) {
    const metrics = {
      html_size: this.calculateHtmlSize(html),
      css_size: this.calculateCssSize(css),
      total_size: this.calculateTotalSize(html, css),
      load_time_ms: this.estimateLoadTime(html, css),
      memory_bytes: this.estimateDomMemory(html),
    };

    const warnings = this.detectWarnings(html, css);
    const recommendations = this.getRecommendations(html, css);
    const score = this.calculatePerformanceScore(metrics);

    return {
      metrics,
      warnings,
      recommendations,
      score,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Update metrics from current template
   */
  updateMetrics() {
    const htmlEditor = document.querySelector('[data-editor="html"]');
    const cssEditor = document.querySelector('[data-editor="css"]');

    if (!htmlEditor || !cssEditor) return;

    const html = htmlEditor.value || '';
    const css = cssEditor.value || '';

    const analysis = this.analyzeTemplate(html, css);
    this.metrics = analysis;

    // Track history (keep last 50 analyses)
    this.history.push(analysis);
    if (this.history.length > 50) {
      this.history.shift();
    }

    this.dispatchEvent('metricsUpdated', { metrics: analysis });
  }

  /**
   * Get performance trend
   */
  getPerformanceTrend() {
    if (this.history.length < 2) return 'stable';

    const current = this.history[this.history.length - 1];
    const previous = this.history[this.history.length - 2];

    if (current.score > previous.score) {
      return 'improving';
    } else if (current.score < previous.score) {
      return 'degrading';
    }
    return 'stable';
  }

  /**
   * Get average performance score
   */
  getAverageScore() {
    if (this.history.length === 0) return 100;
    const sum = this.history.reduce((acc, a) => acc + a.score, 0);
    return Math.round(sum / this.history.length);
  }

  /**
   * Format size for display
   */
  formatSize(bytes) {
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
  }

  /**
   * Format time for display
   */
  formatTime(ms) {
    if (ms < 1000) return `${ms.toFixed(0)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  }

  /**
   * Generate performance report
   */
  generateReport(analysis) {
    const { metrics, warnings, recommendations, score } = analysis;

    return `
Performance Report
==================
Overall Score: ${score}/100

Metrics:
- HTML Size: ${this.formatSize(metrics.html_size)}
- CSS Size: ${this.formatSize(metrics.css_size)}
- Total Size: ${this.formatSize(metrics.total_size)}
- Estimated Load Time: ${this.formatTime(metrics.load_time_ms)}
- Memory Usage: ${this.formatSize(metrics.memory_bytes)}

Warnings (${warnings.length}):
${warnings.map(w => `- [${w.severity}] ${w.message}`).join('\n')}

Recommendations (${recommendations.length}):
${recommendations.map(r => `- [${r.impact}] ${r.suggestion}`).join('\n')}
    `.trim();
  }

  /**
   * Listen to events
   */
  on(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType).push(callback);
  }

  /**
   * Dispatch custom event
   */
  dispatchEvent(eventType, detail = {}) {
    const event = new CustomEvent(`perf:${eventType}`, { detail });
    window.dispatchEvent(event);

    // Call registered listeners
    if (this.listeners.has(eventType)) {
      for (const callback of this.listeners.get(eventType)) {
        callback(detail);
      }
    }
  }

  /**
   * Handle template updated event
   */
  onTemplateUpdated(event) {
    this.updateMetrics();
  }

  /**
   * Handle HTML edited event
   */
  onHtmlEdited(event) {
    this.updateMetrics();
  }

  /**
   * Handle CSS edited event
   */
  onCssEdited(event) {
    this.updateMetrics();
  }

  /**
   * Destroy and cleanup
   */
  destroy() {
    this.stopMonitoring();
    this.listeners.clear();
    this.history = [];
  }
}

// Global instance
let performanceAnalytics = null;

/**
 * Get or create PerformanceAnalytics instance
 */
function getPerformanceAnalytics() {
  if (!performanceAnalytics) {
    performanceAnalytics = new PerformanceAnalytics();
    performanceAnalytics.initialize();
  }
  return performanceAnalytics;
}

/**
 * Initialize on DOM ready
 */
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    getPerformanceAnalytics();
  });
} else {
  getPerformanceAnalytics();
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { PerformanceAnalytics, getPerformanceAnalytics };
}
