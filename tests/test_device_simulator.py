"""
Test suite for Device Simulator module.

Tests:
- Device profile management
- Device selection and switching
- Orientation switching
- Viewport simulation
- Zoom level control
- Network throttling
- Performance metrics per device
- Responsive design validation
- Device comparison
"""

import unittest
from datetime import datetime
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.device_simulator import (
    DeviceProfile,
    DeviceSimulator,
    DeviceType,
    Orientation,
    NetworkType,
    PerformanceMetricsPerDevice,
    ResponsiveDesignIssue,
    DeviceProfileDatabase,
)


class TestDeviceProfile(unittest.TestCase):
    """Test DeviceProfile class."""

    def test_device_initialization(self):
        """Test device profile initialization."""
        device = DeviceProfile(
            name="Test Phone",
            device_type="mobile",
            width=360,
            height=800,
            dpr=2.0,
            os="Android 11",
        )
        self.assertEqual(device.name, "Test Phone")
        self.assertEqual(device.width, 360)
        self.assertEqual(device.height, 800)
        self.assertEqual(device.dpr, 2.0)

    def test_device_portrait_viewport(self):
        """Test portrait viewport dimensions."""
        device = DeviceProfile(
            name="Test Device",
            device_type="mobile",
            width=390,
            height=844,
            dpr=2.0,
        )
        viewport = device.get_viewport("portrait")
        self.assertEqual(viewport["width"], 390)
        self.assertEqual(viewport["height"], 844)
        self.assertEqual(viewport["dpr"], 2.0)

    def test_device_landscape_viewport(self):
        """Test landscape viewport dimensions (rotated)."""
        device = DeviceProfile(
            name="Test Device",
            device_type="mobile",
            width=390,
            height=844,
            dpr=2.0,
        )
        viewport = device.get_viewport("landscape")
        self.assertEqual(viewport["width"], 844)
        self.assertEqual(viewport["height"], 390)
        self.assertEqual(viewport["dpr"], 2.0)

    def test_device_to_dict(self):
        """Test device conversion to dictionary."""
        device = DeviceProfile(
            name="Test Device",
            device_type="mobile",
            width=360,
            height=800,
            dpr=1.5,
        )
        data = device.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["name"], "Test Device")
        self.assertEqual(data["width"], 360)


class TestDeviceProfileDatabase(unittest.TestCase):
    """Test DeviceProfileDatabase."""

    def test_get_predefined_devices(self):
        """Test retrieving predefined devices."""
        devices = DeviceProfileDatabase.get_predefined_devices()
        self.assertGreater(len(devices), 0)
        self.assertEqual(len(devices), 10)  # 4 mobile + 3 tablet + 3 desktop

    def test_mobile_devices_exist(self):
        """Test that mobile devices are in database."""
        devices = DeviceProfileDatabase.get_predefined_devices()
        mobile_devices = [d for d in devices if d.device_type == "mobile"]
        self.assertGreaterEqual(len(mobile_devices), 3)

    def test_tablet_devices_exist(self):
        """Test that tablet devices are in database."""
        devices = DeviceProfileDatabase.get_predefined_devices()
        tablet_devices = [d for d in devices if d.device_type == "tablet"]
        self.assertGreaterEqual(len(tablet_devices), 2)

    def test_desktop_devices_exist(self):
        """Test that desktop devices are in database."""
        devices = DeviceProfileDatabase.get_predefined_devices()
        desktop_devices = [d for d in devices if d.device_type == "desktop"]
        self.assertGreaterEqual(len(desktop_devices), 2)

    def test_device_has_required_properties(self):
        """Test that devices have required properties."""
        devices = DeviceProfileDatabase.get_predefined_devices()
        for device in devices:
            self.assertIsNotNone(device.name)
            self.assertGreater(device.width, 0)
            self.assertGreater(device.height, 0)
            self.assertGreater(device.dpr, 0)


class TestDeviceSimulator(unittest.TestCase):
    """Test DeviceSimulator main class."""

    def setUp(self):
        """Set up test fixtures."""
        self.simulator = DeviceSimulator()

    def test_initialization(self):
        """Test simulator initialization."""
        self.assertIsNone(self.simulator.current_device)
        self.assertEqual(self.simulator.orientation, "portrait")
        self.assertEqual(len(self.simulator.devices), 10)

    def test_select_device(self):
        """Test device selection."""
        success = self.simulator.select_device("iPhone 12")
        self.assertTrue(success)
        self.assertIsNotNone(self.simulator.current_device)
        self.assertEqual(self.simulator.current_device.name, "iPhone 12")

    def test_select_nonexistent_device(self):
        """Test selecting non-existent device."""
        success = self.simulator.select_device("Nonexistent Device")
        self.assertFalse(success)
        self.assertIsNone(self.simulator.current_device)

    def test_rotate_device(self):
        """Test device rotation."""
        self.simulator.select_device("iPhone 12")
        self.assertEqual(self.simulator.orientation, "portrait")
        
        viewport = self.simulator.rotate_device()
        self.assertEqual(self.simulator.orientation, "landscape")
        self.assertEqual(viewport["width"], 844)
        self.assertEqual(viewport["height"], 390)
        
        self.simulator.rotate_device()
        self.assertEqual(self.simulator.orientation, "portrait")

    def test_rotate_without_device(self):
        """Test rotation fails when no device selected."""
        result = self.simulator.rotate_device()
        self.assertIsNone(result)

    def test_get_current_viewport(self):
        """Test getting current viewport."""
        self.simulator.select_device("iPad Pro (12.9\")")
        viewport = self.simulator.get_current_viewport()
        self.assertIsNotNone(viewport)
        self.assertEqual(viewport["width"], 1024)
        self.assertEqual(viewport["height"], 1366)
        self.assertEqual(viewport["orientation"], "portrait")

    def test_get_viewport_no_device(self):
        """Test getting viewport when no device selected."""
        viewport = self.simulator.get_current_viewport()
        self.assertIsNone(viewport)

    def test_add_custom_device(self):
        """Test adding custom device."""
        device = self.simulator.add_custom_device(
            name="Custom Phone",
            device_type="mobile",
            width=480,
            height=854,
            dpr=1.5,
        )
        self.assertIsNotNone(device)
        self.assertEqual(device.name, "Custom Phone")
        self.assertEqual(len(self.simulator.custom_devices), 1)

    def test_select_custom_device(self):
        """Test selecting custom device."""
        self.simulator.add_custom_device(
            name="My Device",
            device_type="tablet",
            width=600,
            height=900,
        )
        success = self.simulator.select_device("My Device")
        self.assertTrue(success)
        self.assertEqual(self.simulator.current_device.name, "My Device")

    def test_remove_custom_device(self):
        """Test removing custom device."""
        self.simulator.add_custom_device(
            name="Temp Device",
            device_type="mobile",
            width=320,
            height=640,
        )
        self.assertEqual(len(self.simulator.custom_devices), 1)
        
        success = self.simulator.remove_custom_device("Temp Device")
        self.assertTrue(success)
        self.assertEqual(len(self.simulator.custom_devices), 0)

    def test_remove_nonexistent_device(self):
        """Test removing non-existent custom device."""
        success = self.simulator.remove_custom_device("Nonexistent")
        self.assertFalse(success)

    def test_set_zoom_level(self):
        """Test zoom level control."""
        self.simulator.set_zoom_level(1.5)
        self.assertEqual(self.simulator.zoom_level, 1.5)

    def test_zoom_level_boundaries(self):
        """Test zoom level clamping."""
        self.simulator.set_zoom_level(0.2)  # Below 0.5
        self.assertEqual(self.simulator.zoom_level, 0.5)
        
        self.simulator.set_zoom_level(3.0)  # Above 2.0
        self.assertEqual(self.simulator.zoom_level, 2.0)

    def test_set_network_type(self):
        """Test network type setting."""
        self.simulator.set_network_type("slow_4g")
        self.assertEqual(self.simulator.network_type, "slow_4g")

    def test_get_network_characteristics_full_speed(self):
        """Test full speed network characteristics."""
        self.simulator.set_network_type("full_speed")
        chars = self.simulator.get_network_characteristics()
        self.assertEqual(chars["downlink_mbps"], 100.0)
        self.assertEqual(chars["latency_ms"], 0)

    def test_get_network_characteristics_4g(self):
        """Test 4G network characteristics."""
        self.simulator.set_network_type("slow_4g")
        chars = self.simulator.get_network_characteristics()
        self.assertEqual(chars["downlink_mbps"], 4.0)
        self.assertGreater(chars["latency_ms"], 0)

    def test_get_network_characteristics_2g(self):
        """Test 2G network characteristics."""
        self.simulator.set_network_type("slow_2g")
        chars = self.simulator.get_network_characteristics()
        self.assertEqual(chars["downlink_mbps"], 0.4)
        self.assertGreater(chars["latency_ms"], 0)


class TestPerformanceMetricsPerDevice(unittest.TestCase):
    """Test performance metrics recording."""

    def setUp(self):
        """Set up test fixtures."""
        self.simulator = DeviceSimulator()

    def test_record_metrics_with_device(self):
        """Test recording metrics with selected device."""
        self.simulator.select_device("iPhone 12")
        metrics = self.simulator.record_device_metrics(
            load_time_ms=250.0,
            memory_mb=45.5,
            cpu_percent=25.0,
            battery_percent=5.0,
        )
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.device_name, "iPhone 12")
        self.assertEqual(metrics.load_time_ms, 250.0)
        self.assertEqual(len(self.simulator.metrics_history), 1)

    def test_record_metrics_without_device(self):
        """Test recording metrics fails without device selected."""
        with self.assertRaises(ValueError):
            self.simulator.record_device_metrics(250.0, 45.0, 25.0, 5.0)

    def test_multiple_metrics_recording(self):
        """Test recording multiple metrics."""
        self.simulator.select_device("iPad (10.2\")")
        
        for i in range(5):
            self.simulator.record_device_metrics(
                load_time_ms=300 + i * 10,
                memory_mb=60.0 + i * 2,
                cpu_percent=20.0 + i,
                battery_percent=4.0 + i * 0.5,
            )
        
        self.assertEqual(len(self.simulator.metrics_history), 5)

    def test_metrics_to_dict(self):
        """Test metrics conversion to dictionary."""
        self.simulator.select_device("Samsung Galaxy S21")
        metrics = self.simulator.record_device_metrics(200.0, 40.0, 15.0, 3.0)
        data = metrics.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["device_name"], "Samsung Galaxy S21")
        self.assertEqual(data["load_time_ms"], 200.0)

    def test_get_metrics_history(self):
        """Test retrieving metrics history."""
        self.simulator.select_device("Desktop 1920x1080")
        
        self.simulator.record_device_metrics(100.0, 25.0, 10.0, 1.0)
        self.simulator.record_device_metrics(110.0, 26.0, 12.0, 1.2)
        
        history = self.simulator.get_metrics_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].load_time_ms, 100.0)
        self.assertEqual(history[1].load_time_ms, 110.0)


class TestDeviceComparison(unittest.TestCase):
    """Test device performance comparison."""

    def setUp(self):
        """Set up test fixtures."""
        self.simulator = DeviceSimulator()

    def test_compare_two_devices(self):
        """Test comparing performance between devices."""
        # Record metrics for device 1
        self.simulator.select_device("iPhone 12")
        self.simulator.record_device_metrics(250.0, 45.0, 25.0, 5.0)
        
        # Record metrics for device 2
        self.simulator.select_device("Desktop 1920x1080")
        self.simulator.record_device_metrics(150.0, 30.0, 15.0, 2.0)
        
        comparison = self.simulator.compare_device_performance("iPhone 12", "Desktop 1920x1080")
        self.assertIsNotNone(comparison)
        self.assertEqual(comparison["faster_device"], "Desktop 1920x1080")

    def test_compare_without_metrics(self):
        """Test comparison when one device has no metrics."""
        comparison = self.simulator.compare_device_performance("iPhone 12", "iPad Pro (12.9\")")
        self.assertEqual(len(comparison), 0)


class TestResponsiveDesignValidation(unittest.TestCase):
    """Test responsive design validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.simulator = DeviceSimulator()

    def test_validate_with_media_queries(self):
        """Test validation with proper media queries."""
        self.simulator.select_device("iPhone 12")
        css = """
        @media (max-width: 600px) {
            .container { width: 100%; }
        }
        """
        issues = self.simulator.validate_responsive_design(css)
        # Should have no breakpoint issues
        breakpoint_issues = [i for i in issues if i.issue_type == "breakpoint"]
        self.assertEqual(len(breakpoint_issues), 0)

    def test_validate_missing_media_queries(self):
        """Test validation without media queries."""
        self.simulator.select_device("iPhone 12")
        css = ".container { width: 500px; }"
        issues = self.simulator.validate_responsive_design(css)
        # Should have breakpoint issue
        breakpoint_issues = [i for i in issues if i.issue_type == "breakpoint"]
        self.assertGreater(len(breakpoint_issues), 0)

    def test_validate_touch_targets(self):
        """Test touch target validation."""
        self.simulator.select_device("Samsung Galaxy S21")
        css = "button { width: 20px; height: 20px; }"
        issues = self.simulator.validate_responsive_design(css)
        # Should have touch target issue
        touch_issues = [i for i in issues if i.issue_type == "touch_target"]
        self.assertGreater(len(touch_issues), 0)

    def test_validate_flexible_layout(self):
        """Test validation with flexible layout."""
        self.simulator.select_device("iPad (10.2\")")
        css = ".container { max-width: 960px; margin: 0 auto; }"
        issues = self.simulator.validate_responsive_design(css)
        # Should have few or no layout issues
        layout_issues = [i for i in issues if i.issue_type == "layout"]
        # Might have some but not critical
        self.assertLessEqual(len(layout_issues), 1)

    def test_validate_without_device(self):
        """Test validation without selected device."""
        css = "body { margin: 0; }"
        issues = self.simulator.validate_responsive_design(css)
        self.assertEqual(len(issues), 0)


class TestDeviceSimulatorReporting(unittest.TestCase):
    """Test device simulator reporting."""

    def setUp(self):
        """Set up test fixtures."""
        self.simulator = DeviceSimulator()

    def test_generate_device_report(self):
        """Test device report generation."""
        self.simulator.select_device("iPhone 12")
        self.simulator.record_device_metrics(250.0, 45.0, 25.0, 5.0)
        
        report = self.simulator.generate_device_report()
        self.assertIsNotNone(report)
        self.assertEqual(report["device"]["name"], "iPhone 12")
        self.assertIn("metrics_summary", report)
        self.assertGreater(report["metrics_summary"]["total_tests"], 0)

    def test_export_to_json(self):
        """Test JSON export."""
        self.simulator.select_device("iPad Pro (12.9\")")
        self.simulator.add_custom_device("Custom", "mobile", 400, 800)
        self.simulator.record_device_metrics(300.0, 50.0, 30.0, 6.0)
        
        json_str = self.simulator.export_to_json()
        data = json.loads(json_str)
        self.assertIsNotNone(data)
        self.assertEqual(data["current_device"]["name"], "iPad Pro (12.9\")")
        self.assertEqual(len(data["custom_devices"]), 1)
        self.assertEqual(len(data["metrics_history"]), 1)


class TestDeviceSimulatorIntegration(unittest.TestCase):
    """Integration tests for device simulator."""

    def test_full_workflow(self):
        """Test complete device simulation workflow."""
        simulator = DeviceSimulator()
        
        # 1. Select device
        simulator.select_device("Samsung Galaxy S21")
        self.assertIsNotNone(simulator.current_device)
        
        # 2. Rotate device
        simulator.rotate_device()
        self.assertEqual(simulator.orientation, "landscape")
        
        # 3. Set network
        simulator.set_network_type("slow_4g")
        self.assertEqual(simulator.network_type, "slow_4g")
        
        # 4. Record metrics
        metrics = simulator.record_device_metrics(350.0, 55.0, 40.0, 8.0)
        self.assertIsNotNone(metrics)
        
        # 5. Validate responsive design
        css = "@media (max-width: 600px) { .btn { min-height: 48px; } }"
        issues = simulator.validate_responsive_design(css)
        self.assertIsInstance(issues, list)
        
        # 6. Generate report
        report = simulator.generate_device_report()
        self.assertIsNotNone(report)
        self.assertEqual(report["orientation"], "landscape")

    def test_multi_device_testing(self):
        """Test testing multiple devices."""
        simulator = DeviceSimulator()
        devices_to_test = ["iPhone 12", "iPad (10.2\")", "Desktop 1920x1080"]
        
        for device_name in devices_to_test:
            simulator.select_device(device_name)
            simulator.record_device_metrics(100.0 + len(device_name), 40.0, 20.0, 4.0)
        
        self.assertEqual(len(simulator.metrics_history), 3)
        reports = [simulator.compare_device_performance(devices_to_test[i], devices_to_test[i+1]) 
                  for i in range(len(devices_to_test) - 1)]
        self.assertEqual(len(reports), 2)


if __name__ == "__main__":
    unittest.main()
