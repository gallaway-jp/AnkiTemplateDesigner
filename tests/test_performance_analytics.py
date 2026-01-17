"""
Test suite for Performance Analytics module.

This module tests:
- Real-time CSS/HTML size metrics
- Load time estimation
- Optimization recommendations
- Performance warnings
- Memory usage tracking
- Benchmark comparisons
- Size limit warnings
"""

import json
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.performance_analytics import (
    PerformanceAnalytics,
    PerformanceMetrics,
    PerformanceWarning,
    OptimizationRecommendation,
    PerformanceTrend,
)


class TestPerformanceMetrics(unittest.TestCase):
    """Test PerformanceMetrics data class."""

    def test_metrics_initialization(self):
        """Test that metrics can be initialized with valid values."""
        metrics = PerformanceMetrics(
            html_size=1024,
            css_size=512,
            total_size=1536,
            load_time_ms=250,
            memory_usage_mb=45.5,
        )
        self.assertEqual(metrics.html_size, 1024)
        self.assertEqual(metrics.css_size, 512)
        self.assertEqual(metrics.total_size, 1536)
        self.assertEqual(metrics.load_time_ms, 250)
        self.assertEqual(metrics.memory_usage_mb, 45.5)

    def test_metrics_timestamp(self):
        """Test that metrics include timestamp."""
        before = datetime.now()
        metrics = PerformanceMetrics(
            html_size=1024,
            css_size=512,
            total_size=1536,
            load_time_ms=250,
            memory_usage_mb=45.5,
        )
        after = datetime.now()
        self.assertGreaterEqual(metrics.timestamp, before)
        self.assertLessEqual(metrics.timestamp, after)

    def test_metrics_to_dict(self):
        """Test that metrics can be converted to dictionary."""
        metrics = PerformanceMetrics(
            html_size=1024,
            css_size=512,
            total_size=1536,
            load_time_ms=250,
            memory_usage_mb=45.5,
        )
        data = metrics.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["html_size"], 1024)
        self.assertEqual(data["css_size"], 512)


class TestPerformanceWarning(unittest.TestCase):
    """Test PerformanceWarning data class."""

    def test_warning_initialization(self):
        """Test that warnings can be initialized."""
        warning = PerformanceWarning(
            message="Template size exceeds 50KB",
            severity="warning",
            metric_type="total_size",
            current_value=65536,
            threshold=51200,
        )
        self.assertEqual(warning.message, "Template size exceeds 50KB")
        self.assertEqual(warning.severity, "warning")
        self.assertEqual(warning.metric_type, "total_size")

    def test_warning_severity_levels(self):
        """Test different severity levels."""
        severities = ["info", "warning", "error", "critical"]
        for severity in severities:
            warning = PerformanceWarning(
                message="Test",
                severity=severity,
                metric_type="test",
                current_value=100,
                threshold=50,
            )
            self.assertEqual(warning.severity, severity)

    def test_warning_to_dict(self):
        """Test that warnings can be converted to dictionary."""
        warning = PerformanceWarning(
            message="Test warning",
            severity="warning",
            metric_type="load_time",
            current_value=500,
            threshold=400,
        )
        data = warning.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["message"], "Test warning")
        self.assertEqual(data["severity"], "warning")


class TestOptimizationRecommendation(unittest.TestCase):
    """Test OptimizationRecommendation data class."""

    def test_recommendation_initialization(self):
        """Test that recommendations can be initialized."""
        rec = OptimizationRecommendation(
            suggestion="Minify CSS to reduce size",
            expected_impact_percent=15,
            priority="high",
            implementation_effort="low",
        )
        self.assertEqual(rec.suggestion, "Minify CSS to reduce size")
        self.assertEqual(rec.expected_impact_percent, 15)

    def test_recommendation_impact_levels(self):
        """Test different impact levels."""
        impacts = ["low", "medium", "high", "critical"]
        for impact in impacts:
            rec = OptimizationRecommendation(
                suggestion="Test",
                expected_impact_percent=impact,
                priority="medium",
                implementation_effort="low",
            )
            self.assertEqual(rec.expected_impact_percent, impact)

    def test_recommendation_to_dict(self):
        """Test that recommendations can be converted to dictionary."""
        rec = OptimizationRecommendation(
            suggestion="Remove unused CSS classes",
            expected_impact_percent="medium",
            priority="medium",
            implementation_effort="medium",
        )
        data = rec.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["suggestion"], "Remove unused CSS classes")


class TestPerformanceTrend(unittest.TestCase):
    """Test PerformanceTrend data class."""

    def test_trend_initialization(self):
        """Test that trends can be initialized."""
        trend = PerformanceTrend(
            metric_name="total_size",
            direction="improving",
            change_percent=-5.2,
            time_period="1_hour",
        )
        self.assertEqual(trend.metric_name, "total_size")
        self.assertEqual(trend.direction, "improving")

    def test_trend_directions(self):
        """Test different trend directions."""
        directions = ["improving", "stable", "degrading"]
        for direction in directions:
            trend = PerformanceTrend(
                metric_name="test",
                direction=direction,
                change_percent=0.5,
                time_period="1_hour",
            )
            self.assertEqual(trend.direction, direction)

    def test_trend_to_dict(self):
        """Test that trends can be converted to dictionary."""
        trend = PerformanceTrend(
            metric_name="load_time",
            direction="degrading",
            change_percent=10.5,
            time_period="24_hours",
        )
        data = trend.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["metric_name"], "load_time")


class TestPerformanceAnalyticsBasics(unittest.TestCase):
    """Test basic PerformanceAnalytics functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.analytics = PerformanceAnalytics()

    def test_initialization(self):
        """Test that PerformanceAnalytics initializes correctly."""
        self.assertIsNotNone(self.analytics)
        self.assertEqual(len(self.analytics.metrics_history), 0)

    def test_record_metrics(self):
        """Test that metrics can be recorded."""
        metrics = PerformanceMetrics(
            html_size=1024,
            css_size=512,
            total_size=1536,
            load_time_ms=250,
            memory_usage_mb=45.5,
        )
        self.analytics.record_metrics(metrics)
        self.assertEqual(len(self.analytics.metrics_history), 1)
        self.assertEqual(self.analytics.metrics_history[0], metrics)

    def test_multiple_metrics_recording(self):
        """Test that multiple metrics can be recorded."""
        for i in range(5):
            metrics = PerformanceMetrics(
                html_size=1000 + i * 100,
                css_size=500 + i * 50,
                total_size=1500 + i * 150,
                load_time_ms=250 + i * 10,
                memory_usage_mb=45.5 + i * 1.0,
            )
            self.analytics.record_metrics(metrics)
        self.assertEqual(len(self.analytics.metrics_history), 5)

    def test_get_latest_metrics(self):
        """Test retrieving the latest metrics."""
        metrics1 = PerformanceMetrics(
            html_size=1024,
            css_size=512,
            total_size=1536,
            load_time_ms=250,
            memory_usage_mb=45.5,
        )
        metrics2 = PerformanceMetrics(
            html_size=2048,
            css_size=1024,
            total_size=3072,
            load_time_ms=300,
            memory_usage_mb=50.0,
        )
        self.analytics.record_metrics(metrics1)
        self.analytics.record_metrics(metrics2)
        latest = self.analytics.get_latest_metrics()
        self.assertEqual(latest.html_size, 2048)

    def test_get_latest_metrics_empty(self):
        """Test retrieving latest metrics when none exist."""
        latest = self.analytics.get_latest_metrics()
        self.assertIsNone(latest)


class TestPerformanceAnalyticsSizeLimits(unittest.TestCase):
    """Test size limit checking in PerformanceAnalytics."""

    def setUp(self):
        """Set up test fixtures."""
        self.analytics = PerformanceAnalytics()

    def test_check_size_limits_within_limits(self):
        """Test that no warnings are generated when within limits."""
        metrics = PerformanceMetrics(
            html_size=10000,
            css_size=5000,
            total_size=15000,
            load_time_ms=250,
            memory_usage_mb=45.5,
        )
        self.analytics.record_metrics(metrics)
        warnings = self.analytics.check_performance_warnings()
        size_warnings = [w for w in warnings if w.metric_type in ["html_size", "css_size", "total_size"]]
        self.assertEqual(len(size_warnings), 0)

    def test_check_size_limits_html_exceeds(self):
        """Test warning when HTML size exceeds limit."""
        metrics = PerformanceMetrics(
            html_size=100000,  # Exceeds 50KB limit
            css_size=5000,
            total_size=105000,
            load_time_ms=250,
            memory_usage_mb=45.5,
        )
        self.analytics.record_metrics(metrics)
        warnings = self.analytics.check_performance_warnings()
        html_warnings = [w for w in warnings if w.metric_type == "html_size"]
        self.assertGreater(len(html_warnings), 0)

    def test_check_size_limits_css_exceeds(self):
        """Test warning when CSS size exceeds limit."""
        metrics = PerformanceMetrics(
            html_size=10000,
            css_size=100000,  # Exceeds 50KB limit
            total_size=110000,
            load_time_ms=250,
            memory_usage_mb=45.5,
        )
        self.analytics.record_metrics(metrics)
        warnings = self.analytics.check_performance_warnings()
        css_warnings = [w for w in warnings if w.metric_type == "css_size"]
        self.assertGreater(len(css_warnings), 0)

    def test_check_size_limits_total_exceeds(self):
        """Test warning when total size exceeds limit."""
        metrics = PerformanceMetrics(
            html_size=50000,
            css_size=50000,
            total_size=150000,  # Exceeds 100KB limit
            load_time_ms=250,
            memory_usage_mb=45.5,
        )
        self.analytics.record_metrics(metrics)
        warnings = self.analytics.check_performance_warnings()
        total_warnings = [w for w in warnings if w.metric_type == "total_size"]
        self.assertGreater(len(total_warnings), 0)


class TestPerformanceAnalyticsLoadTime(unittest.TestCase):
    """Test load time estimation in PerformanceAnalytics."""

    def setUp(self):
        """Set up test fixtures."""
        self.analytics = PerformanceAnalytics()

    def test_load_time_estimation_fast(self):
        """Test that fast load times don't generate warnings."""
        metrics = PerformanceMetrics(
            html_size=10000,
            css_size=5000,
            total_size=15000,
            load_time_ms=100,
            memory_usage_mb=45.5,
        )
        self.analytics.record_metrics(metrics)
        warnings = self.analytics.check_performance_warnings()
        load_warnings = [w for w in warnings if w.metric_type == "load_time_ms"]
        self.assertEqual(len(load_warnings), 0)

    def test_load_time_estimation_slow(self):
        """Test that slow load times generate warnings."""
        metrics = PerformanceMetrics(
            html_size=10000,
            css_size=5000,
            total_size=15000,
            load_time_ms=2000,  # Exceeds threshold
            memory_usage_mb=45.5,
        )
        self.analytics.record_metrics(metrics)
        warnings = self.analytics.check_performance_warnings()
        load_warnings = [w for w in warnings if w.metric_type == "load_time_ms"]
        self.assertGreater(len(load_warnings), 0)

    def test_estimate_load_time(self):
        """Test load time estimation calculation."""
        metrics = PerformanceMetrics(
            html_size=50000,
            css_size=25000,
            total_size=75000,
            load_time_ms=300,
            memory_usage_mb=50.0,
        )
        self.analytics.record_metrics(metrics)
        estimated_time = self.analytics.estimate_load_time(metrics)
        self.assertIsInstance(estimated_time, (int, float))
        self.assertGreater(estimated_time, 0)


class TestPerformanceAnalyticsOptimization(unittest.TestCase):
    """Test optimization recommendations in PerformanceAnalytics."""

    def setUp(self):
        """Set up test fixtures."""
        self.analytics = PerformanceAnalytics()

    def test_generate_recommendations_no_issues(self):
        """Test that minimal recommendations are generated for good performance."""
        metrics = PerformanceMetrics(
            html_size=10000,
            css_size=5000,
            total_size=15000,
            load_time_ms=100,
            memory_usage_mb=30.0,
        )
        self.analytics.record_metrics(metrics)
        recommendations = self.analytics.generate_recommendations()
        # Should still have some general recommendations
        self.assertIsInstance(recommendations, list)

    def test_generate_recommendations_large_html(self):
        """Test recommendations when HTML is large."""
        metrics = PerformanceMetrics(
            html_size=80000,
            css_size=5000,
            total_size=85000,
            load_time_ms=400,
            memory_usage_mb=50.0,
        )
        self.analytics.record_metrics(metrics)
        recommendations = self.analytics.generate_recommendations()
        html_recs = [r for r in recommendations if "html" in r.suggestion.lower()]
        self.assertGreater(len(html_recs), 0)

    def test_generate_recommendations_large_css(self):
        """Test recommendations when CSS is large."""
        metrics = PerformanceMetrics(
            html_size=10000,
            css_size=80000,
            total_size=90000,
            load_time_ms=400,
            memory_usage_mb=50.0,
        )
        self.analytics.record_metrics(metrics)
        recommendations = self.analytics.generate_recommendations()
        css_recs = [r for r in recommendations if "css" in r.suggestion.lower()]
        self.assertGreater(len(css_recs), 0)

    def test_generate_recommendations_slow_load(self):
        """Test recommendations when load time is slow."""
        metrics = PerformanceMetrics(
            html_size=10000,
            css_size=5000,
            total_size=15000,
            load_time_ms=2000,  # Slow
            memory_usage_mb=100.0,
        )
        self.analytics.record_metrics(metrics)
        recommendations = self.analytics.generate_recommendations()
        load_recs = [r for r in recommendations if "load" in r.suggestion.lower() or "optimization" in r.suggestion.lower()]
        # Should have some performance-related recommendations
        self.assertGreater(len(recommendations), 0)


class TestPerformanceAnalyticsMemory(unittest.TestCase):
    """Test memory usage tracking in PerformanceAnalytics."""

    def setUp(self):
        """Set up test fixtures."""
        self.analytics = PerformanceAnalytics()

    def test_memory_tracking(self):
        """Test that memory usage is tracked."""
        metrics = PerformanceMetrics(
            html_size=10000,
            css_size=5000,
            total_size=15000,
            load_time_ms=250,
            memory_usage_mb=45.5,
        )
        self.analytics.record_metrics(metrics)
        latest = self.analytics.get_latest_metrics()
        self.assertEqual(latest.memory_usage_mb, 45.5)

    def test_memory_warning_high_usage(self):
        """Test warning when memory usage is high."""
        metrics = PerformanceMetrics(
            html_size=10000,
            css_size=5000,
            total_size=15000,
            load_time_ms=250,
            memory_usage_mb=200.0,  # High memory
        )
        self.analytics.record_metrics(metrics)
        warnings = self.analytics.check_performance_warnings()
        memory_warnings = [w for w in warnings if w.metric_type == "memory_usage_mb"]
        self.assertGreater(len(memory_warnings), 0)

    def test_memory_multiple_samples(self):
        """Test memory tracking across multiple samples."""
        memory_samples = [30.5, 35.0, 32.5, 38.0, 36.5]
        for mem in memory_samples:
            metrics = PerformanceMetrics(
                html_size=10000,
                css_size=5000,
                total_size=15000,
                load_time_ms=250,
                memory_usage_mb=mem,
            )
            self.analytics.record_metrics(metrics)
        self.assertEqual(len(self.analytics.metrics_history), 5)
        latest = self.analytics.get_latest_metrics()
        self.assertEqual(latest.memory_usage_mb, 36.5)


class TestPerformanceAnalyticsTrends(unittest.TestCase):
    """Test trend analysis in PerformanceAnalytics."""

    def setUp(self):
        """Set up test fixtures."""
        self.analytics = PerformanceAnalytics()

    def test_calculate_trend_improving(self):
        """Test trend calculation when metrics are improving."""
        # Add first metric
        metrics1 = PerformanceMetrics(
            html_size=20000,
            css_size=10000,
            total_size=30000,
            load_time_ms=400,
            memory_usage_mb=60.0,
        )
        self.analytics.record_metrics(metrics1)
        
        # Add second metric (improved)
        metrics2 = PerformanceMetrics(
            html_size=18000,
            css_size=9000,
            total_size=27000,
            load_time_ms=350,
            memory_usage_mb=55.0,
        )
        self.analytics.record_metrics(metrics2)
        
        trends = self.analytics.calculate_trends()
        self.assertGreater(len(trends), 0)
        # Should show improving trend
        improving_trends = [t for t in trends if t.direction == "improving"]
        self.assertGreater(len(improving_trends), 0)

    def test_calculate_trend_degrading(self):
        """Test trend calculation when metrics are degrading."""
        # Add first metric
        metrics1 = PerformanceMetrics(
            html_size=10000,
            css_size=5000,
            total_size=15000,
            load_time_ms=200,
            memory_usage_mb=40.0,
        )
        self.analytics.record_metrics(metrics1)
        
        # Add second metric (degraded)
        metrics2 = PerformanceMetrics(
            html_size=15000,
            css_size=8000,
            total_size=23000,
            load_time_ms=350,
            memory_usage_mb=55.0,
        )
        self.analytics.record_metrics(metrics2)
        
        trends = self.analytics.calculate_trends()
        degrading_trends = [t for t in trends if t.direction == "degrading"]
        self.assertGreater(len(degrading_trends), 0)

    def test_calculate_trend_stable(self):
        """Test trend calculation when metrics are stable."""
        # Add metrics with minimal changes
        for i in range(3):
            metrics = PerformanceMetrics(
                html_size=10000,
                css_size=5000,
                total_size=15000,
                load_time_ms=250,
                memory_usage_mb=45.0,
            )
            self.analytics.record_metrics(metrics)
        
        trends = self.analytics.calculate_trends()
        stable_trends = [t for t in trends if t.direction == "stable"]
        self.assertGreater(len(stable_trends), 0)


class TestPerformanceAnalyticsComparison(unittest.TestCase):
    """Test benchmark comparison in PerformanceAnalytics."""

    def setUp(self):
        """Set up test fixtures."""
        self.analytics = PerformanceAnalytics()

    def test_compare_with_baseline(self):
        """Test comparison with baseline metrics."""
        baseline = PerformanceMetrics(
            html_size=10000,
            css_size=5000,
            total_size=15000,
            load_time_ms=250,
            memory_usage_mb=45.0,
        )
        self.analytics.set_baseline(baseline)
        
        current = PerformanceMetrics(
            html_size=11000,
            css_size=5500,
            total_size=16500,
            load_time_ms=275,
            memory_usage_mb=48.0,
        )
        
        comparison = self.analytics.compare_with_baseline(current)
        self.assertIsInstance(comparison, dict)
        self.assertIn("total_size_diff_percent", comparison)

    def test_baseline_improvement(self):
        """Test when metrics improve from baseline."""
        baseline = PerformanceMetrics(
            html_size=20000,
            css_size=10000,
            total_size=30000,
            load_time_ms=400,
            memory_usage_mb=60.0,
        )
        self.analytics.set_baseline(baseline)
        
        improved = PerformanceMetrics(
            html_size=15000,
            css_size=8000,
            total_size=23000,
            load_time_ms=300,
            memory_usage_mb=50.0,
        )
        
        comparison = self.analytics.compare_with_baseline(improved)
        # Total size should show improvement (negative percentage)
        self.assertLess(comparison["total_size_diff_percent"], 0)


class TestPerformanceAnalyticsExport(unittest.TestCase):
    """Test export functionality in PerformanceAnalytics."""

    def setUp(self):
        """Set up test fixtures."""
        self.analytics = PerformanceAnalytics()

    def test_export_to_json(self):
        """Test exporting analytics to JSON format."""
        metrics = PerformanceMetrics(
            html_size=10000,
            css_size=5000,
            total_size=15000,
            load_time_ms=250,
            memory_usage_mb=45.5,
        )
        self.analytics.record_metrics(metrics)
        
        json_data = self.analytics.export_to_json()
        self.assertIsInstance(json_data, str)
        # Should be valid JSON
        parsed = json.loads(json_data)
        self.assertIsInstance(parsed, dict)

    def test_export_report(self):
        """Test generating a comprehensive report."""
        metrics = PerformanceMetrics(
            html_size=10000,
            css_size=5000,
            total_size=15000,
            load_time_ms=250,
            memory_usage_mb=45.5,
        )
        self.analytics.record_metrics(metrics)
        
        report = self.analytics.generate_report()
        self.assertIsInstance(report, dict)
        self.assertIn("metrics", report)
        self.assertIn("warnings", report)
        self.assertIn("recommendations", report)


class TestPerformanceAnalyticsIntegration(unittest.TestCase):
    """Integration tests for PerformanceAnalytics."""

    def test_full_workflow(self):
        """Test complete analytics workflow."""
        analytics = PerformanceAnalytics()
        
        # Record initial metrics
        metrics1 = PerformanceMetrics(
            html_size=15000,
            css_size=8000,
            total_size=23000,
            load_time_ms=300,
            memory_usage_mb=50.0,
        )
        analytics.record_metrics(metrics1)
        
        # Set baseline
        analytics.set_baseline(metrics1)
        
        # Record improved metrics
        metrics2 = PerformanceMetrics(
            html_size=12000,
            css_size=7000,
            total_size=19000,
            load_time_ms=250,
            memory_usage_mb=45.0,
        )
        analytics.record_metrics(metrics2)
        
        # Get warnings
        warnings = analytics.check_performance_warnings()
        
        # Get recommendations
        recommendations = analytics.generate_recommendations()
        
        # Calculate trends
        trends = analytics.calculate_trends()
        
        # Generate report
        report = analytics.generate_report()
        
        self.assertEqual(len(analytics.metrics_history), 2)
        self.assertIsInstance(warnings, list)
        self.assertIsInstance(recommendations, list)
        self.assertIsInstance(trends, list)
        self.assertIsInstance(report, dict)

    def test_performance_degradation_detection(self):
        """Test detection of performance degradation."""
        analytics = PerformanceAnalytics()
        
        # Good initial performance
        good_metrics = PerformanceMetrics(
            html_size=10000,
            css_size=5000,
            total_size=15000,
            load_time_ms=200,
            memory_usage_mb=40.0,
        )
        analytics.record_metrics(good_metrics)
        analytics.set_baseline(good_metrics)
        
        # Degraded performance - values that trigger critical warnings
        bad_metrics = PerformanceMetrics(
            html_size=150000,  # > HTML_SIZE_WARNING * 3 = 150KB
            css_size=160000,   # > CSS_SIZE_WARNING * 3 = 150KB
            total_size=310000, # > TOTAL_SIZE_WARNING * 2 = 200KB
            load_time_ms=2500, # > LOAD_TIME_CRITICAL = 2000ms
            memory_usage_mb=250.0, # > MEMORY_CRITICAL = 200MB
        )
        analytics.record_metrics(bad_metrics)
        
        warnings = analytics.check_performance_warnings()
        self.assertGreater(len(warnings), 0)
        
        # Should have critical warnings
        critical_warnings = [w for w in warnings if w.severity == "critical"]
        self.assertGreater(len(critical_warnings), 0)


if __name__ == "__main__":
    unittest.main()
