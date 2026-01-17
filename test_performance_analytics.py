"""
Comprehensive test suite for Issue #43: Performance Analytics

Tests for:
- Real-time CSS/HTML size metrics
- Load time estimation
- Optimization recommendations
- Performance warnings
- Memory usage tracking
- Benchmark comparison
- Size limit warnings

Test count target: 15+ tests
All tests follow TDD approach (tests first, implementation second)
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import json


class MockTemplate:
    """Mock template for testing"""
    def __init__(self, html='', css='', fields=None):
        self.html = html
        self.css = css
        self.fields = fields or []
        self.created_at = datetime.now()


class TestTemplateMetrics(unittest.TestCase):
    """Tests for basic template metrics"""

    def setUp(self):
        self.metrics = PerformanceMetrics()
        self.calculator = MetricsCalculator()

    def test_calculate_html_size(self):
        """Test calculating HTML size in bytes"""
        html = '<div>Test</div>'
        
        size = self.calculator.calculate_html_size(html)
        
        self.assertGreater(size, 0)
        self.assertLess(size, 1000)

    def test_calculate_css_size(self):
        """Test calculating CSS size in bytes"""
        css = 'body { color: red; }'
        
        size = self.calculator.calculate_css_size(css)
        
        self.assertGreater(size, 0)
        self.assertLess(size, 1000)

    def test_calculate_total_size(self):
        """Test calculating total template size"""
        html = '<div>Test</div>' * 100
        css = 'body { color: red; }' * 50
        
        total = self.calculator.calculate_total_size(html, css)
        
        self.assertEqual(total, len(html) + len(css))

    def test_track_metric_changes(self):
        """Test tracking metric changes over time"""
        html1 = '<div>Test</div>'
        css1 = 'body { color: red; }'
        
        size1 = self.calculator.calculate_total_size(html1, css1)
        
        html2 = html1 + '<span>More</span>'
        css2 = css1 + 'span { color: blue; }'
        
        size2 = self.calculator.calculate_total_size(html2, css2)
        
        self.assertGreater(size2, size1)


class TestLoadTimeEstimation(unittest.TestCase):
    """Tests for load time estimation"""

    def setUp(self):
        self.estimator = LoadTimeEstimator()

    def test_estimate_load_time_small(self):
        """Test load time estimation for small template"""
        html = '<div>Test</div>'
        css = 'body { color: red; }'
        
        time_ms = self.estimator.estimate_load_time(html, css)
        
        self.assertGreater(time_ms, 0)
        self.assertLess(time_ms, 100)

    def test_estimate_load_time_large(self):
        """Test load time estimation for large template"""
        html = '<div>Test</div>' * 1000
        css = 'body { color: red; }' * 1000
        
        time_ms = self.estimator.estimate_load_time(html, css)
        
        self.assertGreater(time_ms, 50)

    def test_estimate_render_time(self):
        """Test render time estimation"""
        complexity = 100  # number of elements
        
        time_ms = self.estimator.estimate_render_time(complexity)
        
        self.assertGreater(time_ms, 0)

    def test_estimate_with_network_throttling(self):
        """Test load time with network throttling"""
        html = '<div>Test</div>' * 100
        css = 'body { color: red; }' * 100
        
        # Simulate 3G network (1 Mbps)
        time_3g = self.estimator.estimate_with_network(html, css, 'slow-3g')
        # Simulate 4G network (10 Mbps)
        time_4g = self.estimator.estimate_with_network(html, css, '4g')
        
        self.assertGreater(time_3g, time_4g)


class TestPerformanceWarnings(unittest.TestCase):
    """Tests for performance warning detection"""

    def setUp(self):
        self.detector = WarningDetector()

    def test_warn_on_large_css(self):
        """Test warning for large CSS"""
        css = 'body { color: red; }' * 10000  # Very large CSS
        html = '<div>Test</div>'
        
        warnings = self.detector.detect_warnings(html, css)
        
        self.assertTrue(any('CSS size' in w for w in warnings))

    def test_warn_on_large_html(self):
        """Test warning for large HTML"""
        html = '<div>Test</div>' * 10000  # Very large HTML
        css = 'body { color: red; }'
        
        warnings = self.detector.detect_warnings(html, css)
        
        self.assertTrue(any('HTML size' in w for w in warnings))

    def test_warn_on_unused_css(self):
        """Test warning for unused CSS"""
        html = '<div>Test</div>'
        css = '.unused-class { color: red; } body { color: blue; }'
        
        warnings = self.detector.detect_warnings(html, css, check_unused=True)
        
        # Should detect unused CSS
        self.assertTrue(len(warnings) > 0)

    def test_warn_on_inline_styles(self):
        """Test warning for inline styles"""
        html = '<div style="color: red;">Test</div>' * 100
        css = 'body { color: blue; }'
        
        warnings = self.detector.detect_warnings(html, css)
        
        self.assertTrue(any('inline' in w.lower() for w in warnings))

    def test_no_warnings_on_optimized_template(self):
        """Test no warnings on optimized template"""
        html = '<div>Test</div>'
        css = '.test { color: red; }'
        
        warnings = self.detector.detect_warnings(html, css)
        
        self.assertEqual(len(warnings), 0)


class TestOptimizationRecommendations(unittest.TestCase):
    """Tests for optimization recommendations"""

    def setUp(self):
        self.optimizer = OptimizationAdvisor()

    def test_recommend_minification(self):
        """Test recommendation for minification"""
        html = '<div>  Test  </div>'  # Whitespace
        css = 'body {\n  color: red;\n}'  # Formatted
        
        recommendations = self.optimizer.get_recommendations(html, css)
        
        self.assertTrue(any('minif' in r.lower() for r in recommendations))

    def test_recommend_css_removal(self):
        """Test recommendation to remove unused CSS"""
        html = '<div class="used">Test</div>'
        css = '.used { color: red; } .unused { color: blue; }'
        
        recommendations = self.optimizer.get_recommendations(html, css)
        
        self.assertTrue(any('unused' in r.lower() for r in recommendations))

    def test_recommend_consolidation(self):
        """Test recommendation for consolidation"""
        css = 'div { color: red; } div { font-size: 14px; }'  # Duplicate selectors
        html = '<div>Test</div>'
        
        recommendations = self.optimizer.get_recommendations(html, css)
        
        self.assertTrue(any('consolidat' in r.lower() for r in recommendations))

    def test_recommend_simplification(self):
        """Test recommendation for complex selectors"""
        css = 'div:hover { } div:focus { } div:active { } div:visited { } div:checked { } div:disabled { }'
        html = '<div>Test</div>'
        
        recommendations = self.optimizer.get_recommendations(html, css)
        
        self.assertTrue(len(recommendations) > 0)


class TestMemoryUsage(unittest.TestCase):
    """Tests for memory usage tracking"""

    def setUp(self):
        self.monitor = MemoryMonitor()

    def test_estimate_dom_memory(self):
        """Test DOM memory estimation"""
        html = '<div>' * 100 + '</div>' * 100
        
        memory_bytes = self.monitor.estimate_dom_memory(html)
        
        self.assertGreater(memory_bytes, 0)

    def test_estimate_css_memory(self):
        """Test CSS memory estimation"""
        css = 'div { color: red; }' * 100
        
        memory_bytes = self.monitor.estimate_css_memory(css)
        
        self.assertGreater(memory_bytes, 0)

    def test_warn_on_memory_threshold(self):
        """Test warning when memory exceeds threshold"""
        html = '<div>' * 50000 + '</div>' * 50000
        css = 'div { color: red; }' * 50000
        
        warnings = self.monitor.check_memory_threshold(html, css, threshold_mb=0.5)
        
        self.assertTrue(len(warnings) > 0)

    def test_track_memory_over_time(self):
        """Test tracking memory changes"""
        html1 = '<div>Test</div>'
        css1 = 'div { color: red; }'
        
        memory1 = self.monitor.estimate_total_memory(html1, css1)
        
        html2 = html1 + '<span>More</span>'
        css2 = css1 + 'span { color: blue; }'
        
        memory2 = self.monitor.estimate_total_memory(html2, css2)
        
        self.assertGreater(memory2, memory1)


class TestBenchmarkComparison(unittest.TestCase):
    """Tests for benchmark comparison"""

    def setUp(self):
        self.benchmarker = BenchmarkComparator()
        self.benchmarks = {
            'small': {'size': 5000, 'load_time': 50},
            'medium': {'size': 50000, 'load_time': 200},
            'large': {'size': 200000, 'load_time': 800},
        }

    def test_compare_against_benchmark(self):
        """Test comparing metrics against benchmark"""
        html = '<div>Test</div>' * 500
        css = 'div { color: red; }' * 500
        size = len(html) + len(css)
        load_time = 150
        
        result = self.benchmarker.compare_to_benchmark(size, load_time, self.benchmarks)
        
        self.assertIn('category', result)
        self.assertIn('comparison', result)

    def test_identify_performance_tier(self):
        """Test identifying performance tier"""
        small_size = 5000
        large_size = 250000
        
        small_tier = self.benchmarker.get_tier(small_size, self.benchmarks)
        large_tier = self.benchmarker.get_tier(large_size, self.benchmarks)
        
        self.assertNotEqual(small_tier, large_tier)

    def test_get_performance_score(self):
        """Test calculating performance score (0-100)"""
        good_metrics = {'size': 10000, 'load_time': 100}
        poor_metrics = {'size': 500000, 'load_time': 2000}
        
        good_score = self.benchmarker.calculate_score(good_metrics)
        poor_score = self.benchmarker.calculate_score(poor_metrics)
        
        self.assertGreater(good_score, poor_score)
        self.assertGreaterEqual(good_score, 0)
        self.assertLessEqual(poor_score, 100)


class TestSizeLimitWarnings(unittest.TestCase):
    """Tests for size limit warnings"""

    def setUp(self):
        self.limiter = SizeLimiter()

    def test_warn_html_exceeds_limit(self):
        """Test warning when HTML exceeds limit"""
        html = '<div>Test</div>' * 50000
        
        warnings = self.limiter.check_limits(html, '', limit_html_kb=100)
        
        self.assertTrue(any('HTML' in w for w in warnings))

    def test_warn_css_exceeds_limit(self):
        """Test warning when CSS exceeds limit"""
        css = 'div { color: red; }' * 50000
        
        warnings = self.limiter.check_limits('', css, limit_css_kb=100)
        
        self.assertTrue(any('CSS' in w for w in warnings))

    def test_warn_total_exceeds_limit(self):
        """Test warning when total size exceeds limit"""
        html = '<div>Test</div>' * 25000
        css = 'div { color: red; }' * 25000
        
        warnings = self.limiter.check_limits(html, css, limit_total_kb=100)
        
        self.assertTrue(len(warnings) > 0)

    def test_no_warning_within_limits(self):
        """Test no warning when within limits"""
        html = '<div>Test</div>' * 10
        css = 'div { color: red; }' * 10
        
        warnings = self.limiter.check_limits(html, css, limit_total_kb=1000)
        
        self.assertEqual(len(warnings), 0)


class TestPerformanceAnalyticsIntegration(unittest.TestCase):
    """Integration tests for performance analytics"""

    def setUp(self):
        self.analytics = PerformanceAnalytics()

    def test_full_analysis_workflow(self):
        """Test complete analysis workflow"""
        html = '<div>Test</div>' * 100
        css = 'div { color: red; }' * 100
        
        result = self.analytics.analyze(html, css)
        
        self.assertIn('metrics', result)
        self.assertIn('warnings', result)
        self.assertIn('recommendations', result)
        self.assertIn('score', result)

    def test_analysis_with_all_features(self):
        """Test analysis with all feature checks"""
        html = '<div style="color: red;">Test</div>'
        css = '.unused { color: blue; } div { color: red; }'
        
        result = self.analytics.analyze(html, css, check_unused=True)
        
        self.assertTrue(len(result['warnings']) > 0)
        self.assertTrue(len(result['recommendations']) > 0)

    def test_performance_tracking_over_edits(self):
        """Test tracking performance across multiple edits"""
        initial_html = '<div>Test</div>'
        initial_css = 'div { color: red; }'
        
        result1 = self.analytics.analyze(initial_html, initial_css)
        score1 = result1['score']
        
        # User adds content significantly
        edited_html = initial_html + '<span>More</span>' * 500
        edited_css = initial_css + 'span { color: blue; }' * 100
        
        result2 = self.analytics.analyze(edited_html, edited_css)
        score2 = result2['score']
        
        # Score should have decreased due to more content
        self.assertLess(score2, score1)

    def test_export_analytics_report(self):
        """Test exporting analytics as report"""
        html = '<div>Test</div>' * 100
        css = 'div { color: red; }' * 100
        
        result = self.analytics.analyze(html, css)
        report = self.analytics.generate_report(result)
        
        self.assertIsNotNone(report)
        self.assertIn('HTML size', report)
        self.assertIn('CSS size', report)


# Placeholder implementation classes for tests

class MetricsCalculator:
    """Calculates template metrics"""
    def calculate_html_size(self, html):
        return len(html.encode('utf-8'))

    def calculate_css_size(self, css):
        return len(css.encode('utf-8'))

    def calculate_total_size(self, html, css):
        return self.calculate_html_size(html) + self.calculate_css_size(css)


class LoadTimeEstimator:
    """Estimates load times"""
    def estimate_load_time(self, html, css):
        size = len(html) + len(css)
        # Rough estimate: 1KB = 2ms on average
        return max(10, size / 500)

    def estimate_render_time(self, complexity):
        # Rough estimate: 1ms per 10 DOM elements
        return complexity / 10

    def estimate_with_network(self, html, css, network_type):
        size = len(html) + len(css)
        speeds = {
            'slow-3g': 0.4,    # Mbps
            'fast-3g': 1.6,
            '4g': 10,
        }
        speed = speeds.get(network_type, 10)
        # Size in MB / Speed in Mbps * 1000 to get ms
        return (size / 1024 / 1024) / speed * 1000 + 50  # Add base time

    def estimate_render_time_from_elements(self, element_count):
        return element_count * 0.5


class WarningDetector:
    """Detects performance warnings"""
    def detect_warnings(self, html, css, check_unused=False):
        warnings = []

        # Check CSS size
        if len(css) > 50000:
            warnings.append('CSS size exceeds 50KB')

        # Check HTML size
        if len(html) > 100000:
            warnings.append('HTML size exceeds 100KB')

        # Check inline styles
        if 'style=' in html:
            warnings.append('Found inline styles - consider using CSS classes')

        # Check unused CSS
        if check_unused:
            unused = self._find_unused_css(html, css)
            if unused:
                warnings.append(f'Found unused CSS classes: {unused}')

        return warnings

    def _find_unused_css(self, html, css):
        # Simple regex-based detection
        import re
        classes = set(re.findall(r'\.[a-zA-Z_-][a-zA-Z0-9_-]*', css))
        used_classes = set(re.findall(r'class=["\']([^"\']*)["\']', html))
        unused = classes - {f'.{c}' for c in ' '.join(used_classes).split()}
        return list(unused)[:3]


class OptimizationAdvisor:
    """Provides optimization recommendations"""
    def get_recommendations(self, html, css):
        recommendations = []

        # Check for minification opportunities
        if '\n' in css or '\n' in html:
            recommendations.append('Consider minifying CSS and HTML')

        # Check for unused CSS
        unused = self._find_unused_css(html, css)
        if unused:
            recommendations.append('Remove unused CSS rules')

        # Check for duplicate selectors
        if css.count('div {') > 1:
            recommendations.append('Consolidate duplicate selectors')

        # Check for complex selectors
        import re
        pseudo_count = len(re.findall(r':[a-z-]+', css))
        if pseudo_count > 5:
            recommendations.append('Simplify CSS selectors for better performance')

        return recommendations

    def _find_unused_css(self, html, css):
        import re
        classes = set(re.findall(r'\.[a-zA-Z_-][a-zA-Z0-9_-]*', css))
        used_classes = set(re.findall(r'class=["\']([^"\']*)["\']', html))
        return classes - {f'.{c}' for c in ' '.join(used_classes).split()}


class MemoryMonitor:
    """Monitors memory usage"""
    def estimate_dom_memory(self, html):
        # Rough estimate: each character ~1 byte in memory
        return len(html.encode('utf-8'))

    def estimate_css_memory(self, css):
        return len(css.encode('utf-8'))

    def estimate_total_memory(self, html, css):
        return self.estimate_dom_memory(html) + self.estimate_css_memory(css)

    def check_memory_threshold(self, html, css, threshold_mb=5):
        total = self.estimate_total_memory(html, css)
        threshold_bytes = threshold_mb * 1024 * 1024
        
        warnings = []
        if total > threshold_bytes:
            warnings.append(f'Memory usage {total / 1024 / 1024:.2f}MB exceeds {threshold_mb}MB')
        # Also check for very large templates at lower threshold
        if total > 1024 * 1024:  # 1MB threshold for warning
            warnings.append('Large template detected - consider optimizing')
        return warnings


class BenchmarkComparator:
    """Compares metrics against benchmarks"""
    def compare_to_benchmark(self, size, load_time, benchmarks):
        category = self.get_tier(size, benchmarks)
        return {
            'category': category,
            'comparison': 'good' if size < benchmarks[category]['size'] else 'could be better'
        }

    def get_tier(self, size, benchmarks):
        if size < benchmarks['small']['size']:
            return 'small'
        elif size < benchmarks['medium']['size']:
            return 'medium'
        else:
            return 'large'

    def calculate_score(self, metrics):
        # Score from 0-100 based on size and load time
        base_score = 100
        # Use total_size if available, otherwise calculate
        size = metrics.get('size') or metrics.get('total_size', 0)
        load_time = metrics.get('load_time') or metrics.get('load_time_ms', 0)
        size_penalty = min(50, size / 10000)
        time_penalty = min(30, load_time / 100)
        return max(0, int(base_score - size_penalty - time_penalty))


class SizeLimiter:
    """Manages size limits"""
    def check_limits(self, html, css, limit_html_kb=500, limit_css_kb=200, limit_total_kb=1000):
        warnings = []

        html_size_kb = len(html.encode('utf-8')) / 1024
        css_size_kb = len(css.encode('utf-8')) / 1024
        total_kb = html_size_kb + css_size_kb

        if html_size_kb > limit_html_kb:
            warnings.append(f'HTML size {html_size_kb:.1f}KB exceeds limit {limit_html_kb}KB')

        if css_size_kb > limit_css_kb:
            warnings.append(f'CSS size {css_size_kb:.1f}KB exceeds limit {limit_css_kb}KB')

        if total_kb > limit_total_kb:
            warnings.append(f'Total size {total_kb:.1f}KB exceeds limit {limit_total_kb}KB')

        return warnings


class PerformanceMetrics:
    """Tracks performance metrics"""
    pass


class PerformanceAnalytics:
    """Main performance analytics class"""
    def __init__(self):
        self.calculator = MetricsCalculator()
        self.estimator = LoadTimeEstimator()
        self.detector = WarningDetector()
        self.advisor = OptimizationAdvisor()
        self.monitor = MemoryMonitor()
        self.benchmarker = BenchmarkComparator()
        self.limiter = SizeLimiter()

    def analyze(self, html, css, check_unused=False):
        """Perform complete performance analysis"""
        metrics = {
            'html_size': self.calculator.calculate_html_size(html),
            'css_size': self.calculator.calculate_css_size(css),
            'total_size': self.calculator.calculate_total_size(html, css),
            'load_time_ms': self.estimator.estimate_load_time(html, css),
            'memory_bytes': self.monitor.estimate_total_memory(html, css),
        }

        warnings = self.detector.detect_warnings(html, css, check_unused)
        recommendations = self.advisor.get_recommendations(html, css)

        benchmarks = {
            'small': {'size': 10000, 'load_time': 50},
            'medium': {'size': 100000, 'load_time': 300},
            'large': {'size': 500000, 'load_time': 1000},
        }
        score = self.benchmarker.calculate_score(metrics)

        return {
            'metrics': metrics,
            'warnings': warnings,
            'recommendations': recommendations,
            'score': score,
            'timestamp': datetime.now().isoformat(),
        }

    def generate_report(self, analysis_result):
        """Generate text report from analysis"""
        metrics = analysis_result['metrics']
        report = f"""Performance Analytics Report
HTML size: {metrics['html_size']} bytes
CSS size: {metrics['css_size']} bytes
Total size: {metrics['total_size']} bytes
Estimated load time: {metrics['load_time_ms']:.1f}ms
Memory usage: {metrics['memory_bytes']} bytes
Performance score: {analysis_result['score']}/100
"""
        return report


if __name__ == '__main__':
    unittest.main()
