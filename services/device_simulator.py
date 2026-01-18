"""
Device Simulator Module

Provides device simulation, responsive design testing, viewport emulation,
and performance metrics tracking by device type.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import json


class DeviceType(Enum):
    """Device classification."""
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"
    CUSTOM = "custom"


class Orientation(Enum):
    """Device orientation."""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class NetworkType(Enum):
    """Network speed simulation."""
    FULL_SPEED = "full_speed"
    FAST_4G = "fast_4g"
    SLOW_4G = "slow_4g"
    SLOW_3G = "slow_3g"
    SLOW_2G = "slow_2g"


@dataclass
class DeviceProfile:
    """Device specification and capabilities."""
    
    name: str
    device_type: str  # mobile, tablet, desktop, custom
    width: int  # Width in pixels
    height: int  # Height in pixels
    dpr: float = 1.0  # Device pixel ratio
    os: str = "Unknown"  # Operating system
    has_notch: bool = False
    has_touch: bool = True
    timestamp: datetime = field(default_factory=datetime.now)
    capabilities: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["device_type"] = self.device_type
        return data
    
    def get_viewport(self, orientation: str = "portrait") -> Dict[str, int]:
        """Get viewport dimensions for orientation."""
        if orientation == "landscape":
            return {
                "width": self.height,
                "height": self.width,
                "dpr": self.dpr,
            }
        return {
            "width": self.width,
            "height": self.height,
            "dpr": self.dpr,
        }


@dataclass
class PerformanceMetricsPerDevice:
    """Performance metrics for a specific device."""
    
    device_name: str
    device_type: str
    load_time_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    battery_impact_percent: float
    network_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    optimization_suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class ResponsiveDesignIssue:
    """Issue found during responsive design validation."""
    
    issue_type: str  # breakpoint, media_query, layout, touch_target
    severity: str  # info, warning, error
    message: str
    device_name: str
    location: str  # CSS line/selector
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class DeviceProfileDatabase:
    """Predefined device profiles."""
    
    @staticmethod
    def get_predefined_devices() -> List[DeviceProfile]:
        """Get all predefined device profiles."""
        devices = [
            # Mobile Devices
            DeviceProfile(
                name="iPhone 12",
                device_type="mobile",
                width=390,
                height=844,
                dpr=2.0,
                os="iOS 14",
                has_notch=True,
                has_touch=True,
                capabilities={
                    "max_touch_points": 5,
                    "orientation_lock": False,
                    "face_id": True,
                }
            ),
            DeviceProfile(
                name="iPhone 13 Pro",
                device_type="mobile",
                width=390,
                height=844,
                dpr=2.0,
                os="iOS 15",
                has_notch=True,
                has_touch=True,
                capabilities={
                    "max_touch_points": 5,
                    "dynamic_island": True,
                    "always_on_display": True,
                }
            ),
            DeviceProfile(
                name="Samsung Galaxy S21",
                device_type="mobile",
                width=360,
                height=800,
                dpr=2.0,
                os="Android 11",
                has_notch=True,
                has_touch=True,
                capabilities={
                    "max_touch_points": 10,
                    "under_display_camera": True,
                }
            ),
            DeviceProfile(
                name="Google Pixel 6",
                device_type="mobile",
                width=412,
                height=915,
                dpr=2.75,
                os="Android 12",
                has_notch=True,
                has_touch=True,
                capabilities={
                    "max_touch_points": 10,
                    "tensor_processor": True,
                }
            ),
            # Tablet Devices
            DeviceProfile(
                name="iPad (10.2\")",
                device_type="tablet",
                width=810,
                height=1080,
                dpr=2.0,
                os="iPadOS 15",
                has_notch=False,
                has_touch=True,
                capabilities={
                    "max_touch_points": 5,
                    "split_view": True,
                    "external_keyboard": True,
                }
            ),
            DeviceProfile(
                name="iPad Pro (12.9\")",
                device_type="tablet",
                width=1024,
                height=1366,
                dpr=2.0,
                os="iPadOS 15",
                has_notch=False,
                has_touch=True,
                capabilities={
                    "max_touch_points": 5,
                    "split_view": True,
                    "lidar_sensor": True,
                }
            ),
            DeviceProfile(
                name="Samsung Galaxy Tab S7",
                device_type="tablet",
                width=800,
                height=1280,
                dpr=2.0,
                os="Android 11",
                has_notch=False,
                has_touch=True,
                capabilities={
                    "max_touch_points": 10,
                    "s_pen": True,
                }
            ),
            # Desktop Devices
            DeviceProfile(
                name="MacBook 13\"",
                device_type="desktop",
                width=1440,
                height=900,
                dpr=2.0,
                os="macOS Monterey",
                has_notch=False,
                has_touch=False,
                capabilities={
                    "trackpad": True,
                    "mouse": True,
                    "keyboard": True,
                }
            ),
            DeviceProfile(
                name="Desktop 1920x1080",
                device_type="desktop",
                width=1920,
                height=1080,
                dpr=1.0,
                os="Windows 11",
                has_notch=False,
                has_touch=False,
                capabilities={
                    "mouse": True,
                    "keyboard": True,
                    "high_refresh_rate": False,
                }
            ),
            DeviceProfile(
                name="4K Monitor",
                device_type="desktop",
                width=3840,
                height=2160,
                dpr=1.0,
                os="Linux",
                has_notch=False,
                has_touch=False,
                capabilities={
                    "mouse": True,
                    "keyboard": True,
                    "high_refresh_rate": True,
                }
            ),
        ]
        return devices


class DeviceSimulator:
    """Main device simulation engine."""
    
    def __init__(self):
        """Initialize device simulator."""
        self.current_device: Optional[DeviceProfile] = None
        self.orientation: str = "portrait"
        self.devices: List[DeviceProfile] = DeviceProfileDatabase.get_predefined_devices()
        self.custom_devices: List[DeviceProfile] = []
        self.metrics_history: List[PerformanceMetricsPerDevice] = []
        self.zoom_level: float = 1.0
        self.network_type: str = "full_speed"
    
    def get_available_devices(self) -> List[DeviceProfile]:
        """Get all available devices."""
        return self.devices + self.custom_devices
    
    def select_device(self, name: str) -> bool:
        """Select device by name."""
        all_devices = self.get_available_devices()
        for device in all_devices:
            if device.name == name:
                self.current_device = device
                self.orientation = "portrait"
                return True
        return False
    
    def add_custom_device(self, name: str, device_type: str, width: int, 
                         height: int, dpr: float = 1.0, os: str = "Custom") -> DeviceProfile:
        """Add custom device profile."""
        device = DeviceProfile(
            name=name,
            device_type=device_type,
            width=width,
            height=height,
            dpr=dpr,
            os=os,
            has_touch=(device_type in ["mobile", "tablet"]),
        )
        self.custom_devices.append(device)
        return device
    
    def remove_custom_device(self, name: str) -> bool:
        """Remove custom device profile."""
        for i, device in enumerate(self.custom_devices):
            if device.name == name:
                self.custom_devices.pop(i)
                return True
        return False
    
    def rotate_device(self) -> Optional[Dict[str, int]]:
        """Rotate device orientation."""
        if not self.current_device:
            return None
        
        self.orientation = "landscape" if self.orientation == "portrait" else "portrait"
        return self.current_device.get_viewport(self.orientation)
    
    def get_current_viewport(self) -> Optional[Dict[str, Any]]:
        """Get current viewport dimensions."""
        if not self.current_device:
            return None
        
        viewport = self.current_device.get_viewport(self.orientation)
        viewport["zoom"] = self.zoom_level
        viewport["orientation"] = self.orientation
        viewport["device_name"] = self.current_device.name
        return viewport
    
    def set_zoom_level(self, level: float) -> None:
        """Set viewport zoom level (0.5 - 2.0)."""
        self.zoom_level = max(0.5, min(2.0, level))
    
    def set_network_type(self, network_type: str) -> None:
        """Set network speed simulation."""
        valid_types = [e.value for e in NetworkType]
        if network_type in valid_types:
            self.network_type = network_type
    
    def get_network_characteristics(self) -> Dict[str, Any]:
        """Get network speed characteristics."""
        characteristics = {
            "full_speed": {
                "downlink_mbps": 100.0,
                "uplink_mbps": 50.0,
                "latency_ms": 0,
                "packet_loss_percent": 0,
            },
            "fast_4g": {
                "downlink_mbps": 16.0,
                "uplink_mbps": 4.0,
                "latency_ms": 50,
                "packet_loss_percent": 0.1,
            },
            "slow_4g": {
                "downlink_mbps": 4.0,
                "uplink_mbps": 3.0,
                "latency_ms": 100,
                "packet_loss_percent": 0.5,
            },
            "slow_3g": {
                "downlink_mbps": 1.6,
                "uplink_mbps": 0.768,
                "latency_ms": 400,
                "packet_loss_percent": 2.0,
            },
            "slow_2g": {
                "downlink_mbps": 0.4,
                "uplink_mbps": 0.1,
                "latency_ms": 1000,
                "packet_loss_percent": 5.0,
            },
        }
        return characteristics.get(self.network_type, characteristics["full_speed"])
    
    def record_device_metrics(self, load_time_ms: float, memory_mb: float,
                             cpu_percent: float, battery_percent: float) -> PerformanceMetricsPerDevice:
        """Record performance metrics for current device."""
        if not self.current_device:
            raise ValueError("No device selected")
        
        metrics = PerformanceMetricsPerDevice(
            device_name=self.current_device.name,
            device_type=self.current_device.device_type,
            load_time_ms=load_time_ms,
            memory_usage_mb=memory_mb,
            cpu_usage_percent=cpu_percent,
            battery_impact_percent=battery_percent,
            network_type=self.network_type,
        )
        self.metrics_history.append(metrics)
        return metrics
    
    def get_metrics_history(self) -> List[PerformanceMetricsPerDevice]:
        """Get all recorded metrics."""
        return self.metrics_history
    
    def compare_device_performance(self, device1_name: str, device2_name: str) -> Dict[str, Any]:
        """Compare performance between two devices."""
        metrics1 = self._get_latest_device_metrics(device1_name)
        metrics2 = self._get_latest_device_metrics(device2_name)
        
        if not metrics1 or not metrics2:
            return {}
        
        return {
            "device1": {
                "name": device1_name,
                "load_time": metrics1.load_time_ms,
                "memory": metrics1.memory_usage_mb,
            },
            "device2": {
                "name": device2_name,
                "load_time": metrics2.load_time_ms,
                "memory": metrics2.memory_usage_mb,
            },
            "load_time_diff_percent": self._calc_diff_percent(metrics1.load_time_ms, metrics2.load_time_ms),
            "memory_diff_percent": self._calc_diff_percent(metrics1.memory_usage_mb, metrics2.memory_usage_mb),
            "faster_device": device1_name if metrics1.load_time_ms < metrics2.load_time_ms else device2_name,
        }
    
    def validate_responsive_design(self, css_content: str) -> List[ResponsiveDesignIssue]:
        """Validate CSS for responsive design issues."""
        issues = []
        
        if not self.current_device:
            return issues
        
        # Check for common responsive design issues
        
        # 1. Missing viewport meta tag warning
        if "viewport" not in css_content.lower():
            issues.append(ResponsiveDesignIssue(
                issue_type="viewport",
                severity="warning",
                message="Consider adding viewport meta tag for mobile optimization",
                device_name=self.current_device.name,
                location="HTML head",
            ))
        
        # 2. Check for fixed width containers (simple heuristic)
        if "width: 100%" in css_content or "width: 100%;" in css_content:
            pass  # Good
        elif "max-width:" in css_content:
            pass  # Good
        else:
            issues.append(ResponsiveDesignIssue(
                issue_type="layout",
                severity="warning",
                message="Consider using max-width for flexible layouts",
                device_name=self.current_device.name,
                location="CSS",
            ))
        
        # 3. Check for media queries
        if "@media" not in css_content:
            if self.current_device.device_type != "desktop":
                issues.append(ResponsiveDesignIssue(
                    issue_type="breakpoint",
                    severity="warning",
                    message="No media queries found. Add breakpoints for responsive design.",
                    device_name=self.current_device.name,
                    location="CSS",
                ))
        
        # 4. Touch target size check (48px minimum)
        if "button" in css_content.lower() or "a {" in css_content:
            if "padding" not in css_content and "min-height: 48px" not in css_content:
                issues.append(ResponsiveDesignIssue(
                    issue_type="touch_target",
                    severity="info",
                    message="Ensure touch targets are at least 48x48 pixels",
                    device_name=self.current_device.name,
                    location="Button/Link styles",
                ))
        
        return issues
    
    def generate_device_report(self) -> Dict[str, Any]:
        """Generate comprehensive device testing report."""
        if not self.current_device:
            return {}
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "device": self.current_device.to_dict(),
            "current_viewport": self.get_current_viewport(),
            "network": self.get_network_characteristics(),
            "zoom_level": self.zoom_level,
            "orientation": self.orientation,
            "metrics_summary": {
                "total_tests": len(self.metrics_history),
                "average_load_time": self._calc_average_metric("load_time_ms"),
                "average_memory": self._calc_average_metric("memory_usage_mb"),
                "average_cpu": self._calc_average_metric("cpu_usage_percent"),
            }
        }
        return report
    
    def export_to_json(self) -> str:
        """Export device simulator state to JSON."""
        data = {
            "current_device": self.current_device.to_dict() if self.current_device else None,
            "orientation": self.orientation,
            "zoom_level": self.zoom_level,
            "network_type": self.network_type,
            "custom_devices": [d.to_dict() for d in self.custom_devices],
            "metrics_history": [m.to_dict() for m in self.metrics_history],
        }
        return json.dumps(data, indent=2, default=str)
    
    def _get_latest_device_metrics(self, device_name: str) -> Optional[PerformanceMetricsPerDevice]:
        """Get latest metrics for a specific device."""
        matching = [m for m in self.metrics_history if m.device_name == device_name]
        return matching[-1] if matching else None
    
    def _calc_diff_percent(self, val1: float, val2: float) -> float:
        """Calculate percentage difference."""
        if val1 == 0:
            return 0.0
        return ((val2 - val1) / val1) * 100
    
    def _calc_average_metric(self, metric_name: str) -> float:
        """Calculate average metric value."""
        if not self.metrics_history:
            return 0.0
        
        values = [getattr(m, metric_name) for m in self.metrics_history if hasattr(m, metric_name)]
        return sum(values) / len(values) if values else 0.0
