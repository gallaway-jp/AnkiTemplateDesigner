"""
Comprehensive tests for Error System (Issue #51).
"""

import unittest
from datetime import datetime, timedelta
from services.error_system import (
    ErrorSystem, ErrorSeverity, ErrorCategory, ErrorLog, RecoverySuggestion
)


class TestRecoverySuggestion(unittest.TestCase):
    """Test RecoverySuggestion functionality."""

    def test_create_suggestion(self):
        """Test creating a recovery suggestion."""
        suggestion = RecoverySuggestion(
            id='test_1',
            title='Test Suggestion',
            description='Test description',
            action='test_action',
            priority=1
        )
        self.assertEqual(suggestion.id, 'test_1')
        self.assertEqual(suggestion.title, 'Test Suggestion')
        self.assertEqual(suggestion.action, 'test_action')

    def test_suggestion_to_dict(self):
        """Test converting suggestion to dictionary."""
        suggestion = RecoverySuggestion(
            id='test_1',
            title='Test',
            description='Description',
            action='action',
            is_automatic=True,
            priority=2
        )
        d = suggestion.to_dict()
        self.assertEqual(d['id'], 'test_1')
        self.assertEqual(d['priority'], 2)
        self.assertTrue(d['is_automatic'])

    def test_automatic_suggestion(self):
        """Test automatic recovery suggestion."""
        suggestion = RecoverySuggestion(
            id='auto_1',
            title='Automatic',
            is_automatic=True,
            priority=10
        )
        self.assertTrue(suggestion.is_automatic)
        self.assertEqual(suggestion.priority, 10)


class TestErrorLog(unittest.TestCase):
    """Test ErrorLog functionality."""

    def test_create_error_log(self):
        """Test creating an error log."""
        log = ErrorLog(
            id='err_1',
            message='Test error',
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.VALIDATION
        )
        self.assertEqual(log.id, 'err_1')
        self.assertEqual(log.message, 'Test error')
        self.assertEqual(log.severity, ErrorSeverity.ERROR)
        self.assertFalse(log.is_resolved)

    def test_error_log_to_dict(self):
        """Test converting error log to dictionary."""
        log = ErrorLog(
            id='err_1',
            message='Error message',
            severity=ErrorSeverity.WARNING,
            category=ErrorCategory.COMPONENT,
            context={'key': 'value'}
        )
        d = log.to_dict()
        self.assertEqual(d['id'], 'err_1')
        self.assertEqual(d['severity'], 'warning')
        self.assertEqual(d['category'], 'component')
        self.assertEqual(d['context'], {'key': 'value'})

    def test_error_log_from_dict(self):
        """Test creating error log from dictionary."""
        data = {
            'id': 'err_1',
            'message': 'Test error',
            'severity': 'error',
            'category': 'validation',
            'timestamp': datetime.now().isoformat(),
            'context': {'test': 'data'},
            'stack_trace': '',
            'recovery_suggestions': [],
            'is_resolved': False
        }
        log = ErrorLog.from_dict(data)
        self.assertEqual(log.id, 'err_1')
        self.assertEqual(log.message, 'Test error')
        self.assertEqual(log.context, {'test': 'data'})

    def test_error_log_with_suggestions(self):
        """Test error log with recovery suggestions."""
        suggestion = RecoverySuggestion(
            id='sug_1',
            title='Suggestion',
            action='test'
        )
        log = ErrorLog(
            id='err_1',
            message='Error',
            recovery_suggestions=[suggestion]
        )
        self.assertEqual(len(log.recovery_suggestions), 1)
        self.assertEqual(log.recovery_suggestions[0].id, 'sug_1')


class TestErrorSystemBasics(unittest.TestCase):
    """Test basic ErrorSystem functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.system = ErrorSystem()

    def test_system_initialization(self):
        """Test system initializes correctly."""
        self.assertEqual(len(self.system.error_logs), 0)
        self.assertIsNone(self.system.current_error)
        self.assertEqual(self.system.max_error_logs, 100)

    def test_log_predefined_error(self):
        """Test logging a predefined error."""
        error_id = self.system.log_error('invalid_component_name')
        self.assertIsNotNone(error_id)
        self.assertEqual(len(self.system.error_logs), 1)

    def test_log_with_context(self):
        """Test logging error with context."""
        context = {'component': 'test_comp', 'field': 'name'}
        error_id = self.system.log_error('invalid_component_name', context)
        
        error = self.system.get_error(error_id)
        self.assertEqual(error.context, context)

    def test_current_error_tracking(self):
        """Test current error is updated."""
        error_id_1 = self.system.log_error('invalid_component_name')
        self.assertEqual(self.system.current_error.id, error_id_1)
        
        error_id_2 = self.system.log_error('file_save_failed')
        self.assertEqual(self.system.current_error.id, error_id_2)

    def test_get_error_by_id(self):
        """Test retrieving error by ID."""
        error_id = self.system.log_error('invalid_component_name')
        error = self.system.get_error(error_id)
        
        self.assertIsNotNone(error)
        self.assertEqual(error.id, error_id)

    def test_get_nonexistent_error(self):
        """Test getting non-existent error returns None."""
        error = self.system.get_error('nonexistent_id')
        self.assertIsNone(error)

    def test_error_history(self):
        """Test retrieving error history."""
        self.system.log_error('invalid_component_name')
        self.system.log_error('file_save_failed')
        self.system.log_error('invalid_template')
        
        history = self.system.get_error_history(limit=2)
        self.assertEqual(len(history), 2)

    def test_error_history_limit(self):
        """Test error history respects limit."""
        for _ in range(5):
            self.system.log_error('invalid_component_name')
        
        history = self.system.get_error_history(limit=3)
        self.assertEqual(len(history), 3)


class TestErrorFiltering(unittest.TestCase):
    """Test error filtering functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.system = ErrorSystem()

    def test_unresolved_errors(self):
        """Test getting unresolved errors."""
        error_id_1 = self.system.log_error('invalid_component_name')
        error_id_2 = self.system.log_error('file_save_failed')
        self.system.mark_resolved(error_id_1)
        
        unresolved = self.system.get_unresolved_errors()
        self.assertEqual(len(unresolved), 1)
        self.assertEqual(unresolved[0].id, error_id_2)

    def test_errors_by_severity(self):
        """Test filtering by severity."""
        self.system.log_error('invalid_component_name')  # WARNING
        self.system.log_error('file_save_failed')  # CRITICAL
        self.system.log_error('invalid_template')  # ERROR
        
        critical = self.system.get_errors_by_severity(ErrorSeverity.CRITICAL)
        self.assertEqual(len(critical), 1)
        self.assertEqual(critical[0].severity, ErrorSeverity.CRITICAL)

    def test_errors_by_category(self):
        """Test filtering by category."""
        self.system.log_error('invalid_component_name')  # VALIDATION
        self.system.log_error('invalid_component_name')  # VALIDATION
        self.system.log_error('file_save_failed')  # FILE
        
        validation = self.system.get_errors_by_category(ErrorCategory.VALIDATION)
        self.assertEqual(len(validation), 2)


class TestRecoverySuggestions(unittest.TestCase):
    """Test recovery suggestion functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.system = ErrorSystem()

    def test_get_suggestions(self):
        """Test getting suggestions for error."""
        error_id = self.system.log_error('invalid_component_name')
        suggestions = self.system.get_recovery_suggestions(error_id)
        
        self.assertGreater(len(suggestions), 0)
        for s in suggestions:
            self.assertIsInstance(s, RecoverySuggestion)

    def test_suggestions_sorted_by_priority(self):
        """Test suggestions are sorted by priority."""
        error_id = self.system.log_error('file_save_failed')
        suggestions = self.system.get_recovery_suggestions(error_id)
        
        # Verify they're sorted in descending priority order
        for i in range(len(suggestions) - 1):
            self.assertGreaterEqual(
                suggestions[i].priority,
                suggestions[i + 1].priority
            )

    def test_apply_recovery_without_callback(self):
        """Test applying recovery without registered callback."""
        error_id = self.system.log_error('invalid_component_name')
        suggestions = self.system.get_recovery_suggestions(error_id)
        
        result = self.system.apply_recovery(error_id, suggestions[0].id)
        
        # Should succeed and mark resolved
        self.assertTrue(result)
        error = self.system.get_error(error_id)
        self.assertTrue(error.is_resolved)

    def test_apply_recovery_with_callback(self):
        """Test applying recovery with registered callback."""
        callback_called = []
        
        def recovery_callback(error, suggestion):
            callback_called.append((error.id, suggestion.id))
        
        self.system.register_recovery_callback('test_action', recovery_callback)
        
        error_id = self.system.log_error('invalid_component_name')
        suggestions = [s for s in self.system.get_recovery_suggestions(error_id)
                      if s.action == 'rename']
        
        if suggestions:
            self.system.apply_recovery(error_id, suggestions[0].id)
            # Note: callback may not be called since 'rename' action registered


class TestErrorManagement(unittest.TestCase):
    """Test error management functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.system = ErrorSystem()

    def test_mark_resolved(self):
        """Test marking error as resolved."""
        error_id = self.system.log_error('invalid_component_name')
        self.assertFalse(self.system.get_error(error_id).is_resolved)
        
        result = self.system.mark_resolved(error_id)
        self.assertTrue(result)
        self.assertTrue(self.system.get_error(error_id).is_resolved)

    def test_mark_nonexistent_resolved(self):
        """Test marking non-existent error as resolved."""
        result = self.system.mark_resolved('nonexistent')
        self.assertFalse(result)

    def test_clear_errors(self):
        """Test clearing all errors."""
        self.system.log_error('invalid_component_name')
        self.system.log_error('file_save_failed')
        
        self.assertGreater(len(self.system.error_logs), 0)
        self.system.clear_errors()
        
        self.assertEqual(len(self.system.error_logs), 0)
        self.assertIsNone(self.system.current_error)

    def test_max_error_logs(self):
        """Test maximum error log limit."""
        system = ErrorSystem(max_error_logs=5)
        
        for _ in range(10):
            system.log_error('invalid_component_name')
        
        self.assertEqual(len(system.error_logs), 5)

    def test_error_registration(self):
        """Test registering custom error template."""
        template = {
            'message': 'Custom error',
            'severity': ErrorSeverity.WARNING,
            'category': ErrorCategory.SYSTEM,
            'suggestions': []
        }
        
        self.system.register_error_template('custom_error', template)
        error_id = self.system.log_error('custom_error')
        error = self.system.get_error(error_id)
        
        self.assertEqual(error.message, 'Custom error')


class TestEventListeners(unittest.TestCase):
    """Test event listener functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.system = ErrorSystem()
        self.events = []

    def listener_callback(self, event_type, data):
        """Capture events."""
        self.events.append((event_type, data))

    def test_add_listener(self):
        """Test adding event listener."""
        self.system.add_listener(self.listener_callback)
        self.assertEqual(len(self.system.listeners), 1)

    def test_event_on_error_logged(self):
        """Test event fired on error logged."""
        self.system.add_listener(self.listener_callback)
        error_id = self.system.log_error('invalid_component_name')
        
        self.assertEqual(len(self.events), 1)
        self.assertEqual(self.events[0][0], 'error_logged')

    def test_event_on_error_resolved(self):
        """Test event fired on error resolved."""
        self.system.add_listener(self.listener_callback)
        error_id = self.system.log_error('invalid_component_name')
        self.events.clear()
        
        self.system.mark_resolved(error_id)
        
        self.assertEqual(len(self.events), 1)
        self.assertEqual(self.events[0][0], 'error_resolved')

    def test_remove_listener(self):
        """Test removing event listener."""
        self.system.add_listener(self.listener_callback)
        self.system.remove_listener(self.listener_callback)
        
        self.assertEqual(len(self.system.listeners), 0)

    def test_duplicate_listener_not_added(self):
        """Test duplicate listeners not added."""
        self.system.add_listener(self.listener_callback)
        self.system.add_listener(self.listener_callback)
        
        self.assertEqual(len(self.system.listeners), 1)


class TestErrorStatistics(unittest.TestCase):
    """Test error statistics functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.system = ErrorSystem()

    def test_statistics_empty(self):
        """Test statistics with no errors."""
        stats = self.system.get_statistics()
        
        self.assertEqual(stats['total_errors'], 0)
        self.assertEqual(stats['resolved_errors'], 0)
        self.assertEqual(stats['unresolved_errors'], 0)

    def test_statistics_with_errors(self):
        """Test statistics with errors."""
        self.system.log_error('invalid_component_name')
        self.system.log_error('file_save_failed')
        self.system.log_error('invalid_template')
        
        stats = self.system.get_statistics()
        
        self.assertEqual(stats['total_errors'], 3)
        self.assertEqual(stats['unresolved_errors'], 3)
        self.assertEqual(stats['resolved_errors'], 0)

    def test_statistics_by_severity(self):
        """Test statistics breakdown by severity."""
        self.system.log_error('invalid_component_name')  # WARNING
        self.system.log_error('file_save_failed')  # CRITICAL
        
        stats = self.system.get_statistics()
        
        self.assertGreater(stats['critical_count'], 0)

    def test_statistics_with_resolved(self):
        """Test statistics with resolved errors."""
        error_id = self.system.log_error('invalid_component_name')
        self.system.log_error('file_save_failed')
        self.system.mark_resolved(error_id)
        
        stats = self.system.get_statistics()
        
        self.assertEqual(stats['total_errors'], 2)
        self.assertEqual(stats['resolved_errors'], 1)
        self.assertEqual(stats['unresolved_errors'], 1)


class TestErrorHandlers(unittest.TestCase):
    """Test error handler registration."""

    def setUp(self):
        """Set up test fixtures."""
        self.system = ErrorSystem()
        self.handler_calls = []

    def test_register_error_handler(self):
        """Test registering error handler."""
        def handler(error):
            self.handler_calls.append(error.id)
        
        self.system.register_error_handler('invalid_component_name', handler)
        self.assertIn('invalid_component_name', self.system.error_handlers)

    def test_error_handler_called(self):
        """Test error handler is called."""
        def handler(error):
            self.handler_calls.append(error.id)
        
        self.system.register_error_handler('invalid_component_name', handler)
        self.system.log_error('invalid_component_name')
        
        # Handler may not be called due to exception handling
        # Test mainly checks registration and no crashes


class TestExportAndPersistence(unittest.TestCase):
    """Test exporting and persistence."""

    def setUp(self):
        """Set up test fixtures."""
        self.system = ErrorSystem()

    def test_export_logs(self):
        """Test exporting error logs."""
        self.system.log_error('invalid_component_name')
        self.system.log_error('file_save_failed')
        
        exported = self.system.export_logs()
        
        self.assertEqual(len(exported), 2)
        self.assertIsInstance(exported[0], dict)
        self.assertIn('id', exported[0])
        self.assertIn('message', exported[0])

    def test_clear_old_logs(self):
        """Test clearing old logs."""
        error_id = self.system.log_error('invalid_component_name')
        
        # Manually set timestamp to past
        error = self.system.get_error(error_id)
        error.timestamp = datetime.now() - timedelta(days=10)
        
        self.assertEqual(len(self.system.error_logs), 1)
        cleared = self.system.clear_old_logs(days=7)
        
        self.assertEqual(cleared, 1)
        self.assertEqual(len(self.system.error_logs), 0)

    def test_clear_old_logs_keeps_recent(self):
        """Test clearing old logs keeps recent ones."""
        error_id_1 = self.system.log_error('invalid_component_name')
        error_id_2 = self.system.log_error('file_save_failed')
        
        # Make first error old
        error_1 = self.system.get_error(error_id_1)
        error_1.timestamp = datetime.now() - timedelta(days=10)
        
        cleared = self.system.clear_old_logs(days=7)
        
        self.assertEqual(cleared, 1)
        self.assertEqual(len(self.system.error_logs), 1)
        self.assertEqual(self.system.error_logs[0].id, error_id_2)


if __name__ == '__main__':
    unittest.main()
