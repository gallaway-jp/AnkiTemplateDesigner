"""Bridge for Python <-> JavaScript communication via QWebChannel."""

from typing import Callable, Any, Optional
import json

try:
    from aqt.qt import QObject, pyqtSlot, pyqtSignal
except ImportError:
    # Fallback for testing without Anki
    from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal


class WebViewBridge(QObject):
    """Bridge object exposed to JavaScript for bidirectional communication.
    
    JavaScript calls methods via: window.bridge.methodName(args)
    Python emits signals that JavaScript listens to.
    """
    
    # Signals (Python -> JavaScript)
    templateLoaded = pyqtSignal(str)        # Emit GrapeJS JSON to load
    fieldsUpdated = pyqtSignal(str)         # Emit available Anki fields
    behaviorsUpdated = pyqtSignal(str)      # Emit AnkiJSApi behaviors
    settingsUpdated = pyqtSignal(str)       # Emit editor settings
    
    def __init__(self, parent=None):
        """Initialize bridge with optional parent."""
        super().__init__(parent)
        self._save_callback: Optional[Callable] = None
        self._preview_callback: Optional[Callable] = None
        self._export_callback: Optional[Callable] = None
    
    # ========== JavaScript -> Python Slots ==========
    
    @pyqtSlot(str)
    def saveProject(self, grapejs_json: str):
        """Called by JS when user saves the project.
        
        Args:
            grapejs_json: GrapeJS project data as JSON string
        """
        if self._save_callback:
            try:
                # Notify JS that save is starting
                self._call_js('window.notifySaveStart()')
                
                # Parse JSON
                data = json.loads(grapejs_json)
                
                # Validate template structure
                errors = self._validate_template_data(data)
                if errors:
                    error_message = self._format_error_message(errors)
                    error_json = json.dumps(error_message)
                    self._call_js(f'window.notifySaveError({error_json})')
                    return
                
                # Proceed with save
                self._save_callback(data)
                
                # Notify JS of successful save
                template_name = data.get('name', 'Template')
                template_json = json.dumps(template_name)
                self._call_js(f'window.notifySaveSuccess({template_json})')
                
            except json.JSONDecodeError as e:
                error_msg = f"Invalid template data: {str(e)}"
                error_json = json.dumps(error_msg)
                self._call_js(f'window.notifySaveError({error_json})')
                self.showError(error_msg)
            except Exception as e:
                error_msg = f"Unexpected error while saving: {str(e)}"
                error_json = json.dumps(error_msg)
                self._call_js(f'window.notifySaveError({error_json})')
                self.showError(error_msg)
    
    def _validate_template_data(self, data: dict) -> list:
        """Validate template structure and return list of errors."""
        errors = []
        
        # Check if data is empty
        if not data:
            errors.append("Template data is empty")
            return errors
        
        # Check for components
        components = data.get('components', [])
        if not components:
            errors.append("Template must have at least one component")
        
        # Check for HTML
        html = data.get('html', '')
        if not html:
            errors.append("Template must have HTML content")
        
        # Check for Anki field syntax errors
        if '{{' in html:
            # Count opening and closing braces
            opening_braces = html.count('{{')
            closing_braces = html.count('}}')
            if opening_braces != closing_braces:
                errors.append(
                    f"Mismatched Anki field references: "
                    f"{opening_braces} opening '{{{{' but {closing_braces} closing '}}}}'\n"
                    f"• Check all field references have matching closing braces"
                )
        
        # Check for common issues
        if '<%' in html or '%>' in html:
            errors.append(
                "Template uses old-style template syntax (<% %>)\n"
                "• Use Anki field references instead: {{FieldName}}"
            )
        
        return errors
    
    def _format_error_message(self, errors: list) -> str:
        """Format error messages for display to user."""
        if not errors:
            return "Unknown error"
        
        if len(errors) == 1:
            return f"Cannot save template:\n\n{errors[0]}"
        
        error_list = "\n\n".join(f"• {e}" for e in errors)
        return f"Cannot save template:\n\n{error_list}\n\nFix these issues and try again."
    
    @pyqtSlot(str)
    def requestPreview(self, grapejs_json: str):
        """Called by JS to request a card preview.
        
        Args:
            grapejs_json: GrapeJS project data as JSON string
        """
        if self._preview_callback:
            try:
                data = json.loads(grapejs_json)
                self._preview_callback(data)
            except json.JSONDecodeError as e:
                self.showError(f"Invalid JSON: {e}")
    
    @pyqtSlot(str, str)
    def exportTemplate(self, format_type: str, grapejs_json: str):
        """Called by JS to export template.
        
        Args:
            format_type: Export format ('html', 'json', etc.)
            grapejs_json: GrapeJS project data as JSON string
        """
        if self._export_callback:
            try:
                data = json.loads(grapejs_json)
                self._export_callback(format_type, data)
            except json.JSONDecodeError as e:
                self.showError(f"Invalid JSON: {e}")
    
    @pyqtSlot(str)
    def log(self, message: str):
        """Called by JS for debug logging.
        
        Args:
            message: Log message from JavaScript
        """
        print(f"[GrapeJS] {message}")
    
    @pyqtSlot(str)
    def showError(self, message: str):
        """Called by JS to show error to user.
        
        Args:
            message: Error message to display
        """
        try:
            from aqt.utils import showWarning
            showWarning(message, title="Template Designer Error")
        except ImportError:
            # Fallback if Anki not available
            print(f"ERROR: {message}")
    
    @pyqtSlot(result=str)
    def getAnkiFields(self) -> str:
        """Called by JS to get available Anki fields.
        
        Returns:
            JSON string array of field names
        """
        # Placeholder - real implementation would query Anki
        fields = ["Front", "Back", "Extra", "Tags", "Type"]
        return json.dumps(fields)
    
    @pyqtSlot(result=str)
    def getAnkiBehaviors(self) -> str:
        """Called by JS to get AnkiJSApi behaviors.
        
        Returns:
            JSON string array of behavior objects
        """
        from ..services.ankijsapi_service import AnkiJSApiService
        service = AnkiJSApiService()
        behaviors = service.get_available_behaviors()
        return json.dumps(behaviors)
    
    def _call_js(self, js_code: str):
        """Execute JavaScript code from Python.
        
        Args:
            js_code: JavaScript code to execute
        """
        if self.parent() and hasattr(self.parent(), 'webview'):
            webview = self.parent().webview
            if webview:
                webview.page().runJavaScript(js_code)
    
    @pyqtSlot(result=str)
    def getPlugins(self) -> str:
        """Get list of installed plugins.
        
        Returns:
            JSON string array of plugin objects
        """
        try:
            from ..services.plugin_system import PluginManager
            manager = PluginManager()
            plugins = manager.list_plugins()
            
            # Convert PluginInfo objects to dicts
            plugin_dicts = []
            for p in plugins:
                plugin_dicts.append({
                    'id': p.plugin_id,
                    'name': p.name,
                    'version': p.version,
                    'author': p.author,
                    'description': p.description,
                    'enabled': p.enabled,
                    'rating': 4.5,  # Default rating
                    'downloads': 0,  # Default downloads
                })
            return json.dumps(plugin_dicts)
        except Exception as e:
            print(f"[Bridge] Error getting plugins: {e}")
            return json.dumps([])
    
    @pyqtSlot(str, result=bool)
    def togglePlugin(self, plugin_id: str) -> bool:
        """Toggle plugin enabled/disabled state.
        
        Args:
            plugin_id: ID of plugin to toggle
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from ..services.plugin_system import PluginManager
            manager = PluginManager()
            
            # Get current plugin state
            plugin = manager.registry.get_plugin(plugin_id)
            if not plugin:
                return False
            
            # Toggle state
            if plugin.enabled:
                success = manager.disable_plugin(plugin_id)
            else:
                success = manager.enable_plugin(plugin_id)
            
            return success
        except Exception as e:
            print(f"[Bridge] Error toggling plugin: {e}")
            return False
    
    @pyqtSlot(str, result=bool)
    def installPlugin(self, plugin_id: str) -> bool:
        """Install a plugin from marketplace.
        
        Args:
            plugin_id: ID of plugin to install
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from ..services.plugin_system import PluginManager
            manager = PluginManager()
            
            # Load and initialize plugin
            success = manager.load_plugin(plugin_id)
            return success
        except Exception as e:
            print(f"[Bridge] Error installing plugin: {e}")
            return False
    
    @pyqtSlot(result=str)
    def getAnalyticsDashboardData(self) -> str:
        """Get analytics dashboard data.
        
        Returns:
            JSON string with dashboard metrics
        """
        try:
            from ..services.analytics_manager import AnalyticsManager
            manager = AnalyticsManager()
            data = manager.get_dashboard_data()
            return json.dumps(data)
        except Exception as e:
            print(f"[Bridge] Error getting analytics data: {e}")
            return json.dumps({
                'total_events': 0,
                'avg_latency': 0,
                'error_rate': 0,
                'active_events': 0,
                'recent_insights': []
            })
    
    @pyqtSlot(str, str, result=str)
    def getAnalyticsMetrics(self, metric_name: str, time_range: str) -> str:
        """Get specific analytics metrics.
        
        Args:
            metric_name: Name of metric to retrieve
            time_range: Time range for metrics (e.g., '7d', '30d')
            
        Returns:
            JSON string with metrics data
        """
        try:
            from ..services.analytics_manager import AnalyticsManager
            manager = AnalyticsManager()
            metrics = manager.get_metrics([metric_name], time_range)
            return json.dumps(metrics)
        except Exception as e:
            print(f"[Bridge] Error getting metrics: {e}")
            return json.dumps({})
    
    @pyqtSlot(result=str)
    def getAnalyticsInsights(self) -> str:
        """Get analytics insights.
        
        Returns:
            JSON string with insights data
        """
        try:
            from ..services.analytics_manager import AnalyticsManager
            manager = AnalyticsManager()
            insights = manager.get_insights()
            
            # Convert Insight objects to dicts
            insights_dicts = []
            for insight in insights:
                insights_dicts.append({
                    'insight_id': insight.insight_id,
                    'title': insight.title,
                    'description': insight.description,
                    'category': insight.category,
                    'severity': insight.severity,
                    'confidence': insight.confidence,
                })
            return json.dumps(insights_dicts)
        except Exception as e:
            print(f"[Bridge] Error getting insights: {e}")
            return json.dumps([])
    
    @pyqtSlot(result=str)
    def getAnalyticsAnomalies(self) -> str:
        """Get detected anomalies.
        
        Returns:
            JSON string with anomalies data
        """
        try:
            from ..services.analytics_manager import AnalyticsManager
            manager = AnalyticsManager()
            anomalies = manager.detect_anomalies()
            
            # Convert Anomaly objects to dicts
            anomalies_dicts = []
            for anomaly in anomalies:
                anomalies_dicts.append({
                    'anomaly_id': anomaly.anomaly_id,
                    'anomaly_type': anomaly.anomaly_type,
                    'severity': anomaly.severity,
                    'metric_name': anomaly.metric_name,
                    'expected_value': anomaly.expected_value,
                    'actual_value': anomaly.actual_value,
                    'description': anomaly.description,
                })
            return json.dumps(anomalies_dicts)
        except Exception as e:
            print(f"[Bridge] Error getting anomalies: {e}")
            return json.dumps([])
    
    @pyqtSlot(result=str)
    def getCloudSyncConflicts(self) -> str:
        """Get pending cloud sync conflicts.
        
        Returns:
            JSON string with conflicts data
        """
        try:
            from ..services.cloud_storage_manager import CloudStorageManager
            manager = CloudStorageManager()
            conflicts = manager.get_pending_conflicts()
            
            # Convert conflict objects to dicts
            conflicts_dicts = []
            for conflict in conflicts:
                conflicts_dicts.append({
                    'template_id': conflict.get('template_id', ''),
                    'template_name': conflict.get('template_name', ''),
                    'local_version': conflict.get('local_version', ''),
                    'remote_version': conflict.get('remote_version', ''),
                    'local_timestamp': conflict.get('local_timestamp', ''),
                    'remote_timestamp': conflict.get('remote_timestamp', ''),
                    'conflict_type': conflict.get('conflict_type', 'modified'),
                })
            return json.dumps(conflicts_dicts)
        except Exception as e:
            print(f"[Bridge] Error getting conflicts: {e}")
            return json.dumps([])
    
    @pyqtSlot(str, str, result=bool)
    def resolveCloudConflict(self, template_id: str, resolution: str) -> bool:
        """Resolve a cloud sync conflict.
        
        Args:
            template_id: ID of conflicted template
            resolution: Resolution method ('keep_local', 'keep_remote', 'merge')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from ..services.cloud_storage_manager import CloudStorageManager
            manager = CloudStorageManager()
            success = manager.resolve_conflict(template_id, resolution)
            return success
        except Exception as e:
            print(f"[Bridge] Error resolving conflict: {e}")
            return False
    
    @pyqtSlot(result=str)
    def getBackupList(self) -> str:
        """Get list of available backup recovery points.
        
        Returns:
            JSON string with list of backups
        """
        try:
            from ..services.backup_manager import BackupManager
            manager = BackupManager()
            backups = manager.list_backups()
            backups_dicts = [{
                'backup_id': b.backup_id,
                'timestamp': b.timestamp.isoformat() if hasattr(b.timestamp, 'isoformat') else str(b.timestamp),
                'size': b.size,
                'template_count': b.template_count,
                'backup_type': b.backup_type,
                'success': b.success,
            } for b in backups]
            return json.dumps(backups_dicts)
        except Exception as e:
            print(f"[Bridge] Error getting backup list: {e}")
            return json.dumps([])
    
    @pyqtSlot(str, result=bool)
    def restoreBackup(self, backup_id: str) -> bool:
        """Restore a backup.
        
        Args:
            backup_id: ID of backup to restore
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from ..services.backup_manager import BackupManager
            import tempfile
            manager = BackupManager()
            with tempfile.TemporaryDirectory() as temp_dir:
                success = manager.restore_backup(backup_id, temp_dir)
            return success
        except Exception as e:
            print(f"[Bridge] Error restoring backup: {e}")
            return False
    
    @pyqtSlot(result=str)
    def getBackupStats(self) -> str:
        """Get backup statistics.
        
        Returns:
            JSON string with backup stats
        """
        try:
            from ..services.backup_manager import BackupManager
            manager = BackupManager()
            stats = manager.get_backup_stats()
            stats_dict = {
                'total_backups': stats.total_backups if hasattr(stats, 'total_backups') else 0,
                'total_size': stats.total_size if hasattr(stats, 'total_size') else 0,
                'success_rate': stats.success_rate if hasattr(stats, 'success_rate') else 0,
            }
            return json.dumps(stats_dict)
        except Exception as e:
            print(f"[Bridge] Error getting backup stats: {e}")
            return json.dumps({
                'total_backups': 0,
                'total_size': 0,
                'success_rate': 0
            })
    
    # ========== Python API ==========
    
    def set_save_callback(self, callback: Callable[[dict], None]):
        """Set callback for save action.
        
        Args:
            callback: Function(grapejs_data: dict) -> None
        """
        self._save_callback = callback
    
    def set_preview_callback(self, callback: Callable[[dict], None]):
        """Set callback for preview action.
        
        Args:
            callback: Function(grapejs_data: dict) -> None
        """
        self._preview_callback = callback
    
    def set_export_callback(self, callback: Callable[[str, dict], None]):
        """Set callback for export action.
        
        Args:
            callback: Function(format_type: str, grapejs_data: dict) -> None
        """
        self._export_callback = callback
    
    def load_template(self, grapejs_json: dict):
        """Load a template into the editor.
        
        Args:
            grapejs_json: GrapeJS project data as dict
        """
        self.templateLoaded.emit(json.dumps(grapejs_json))
    
    def update_fields(self, fields: list):
        """Update available Anki fields in editor.
        
        Args:
            fields: List of field names
        """
        self.fieldsUpdated.emit(json.dumps(fields))
    
    def update_behaviors(self, behaviors: list):
        """Update available AnkiJSApi behaviors in editor.
        
        Args:
            behaviors: List of behavior dictionaries
        """
        self.behaviorsUpdated.emit(json.dumps(behaviors))
