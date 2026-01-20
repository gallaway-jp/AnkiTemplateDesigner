"""Tests for analytics system."""

import unittest
from datetime import datetime, timedelta
from typing import List
import tempfile
import os
from services.analytics_manager import AnalyticsManager
from services.analytics import (
    EventCollector,
    Event,
    MetricsAnalyzer,
    TemplateIntelligence,
    AnomalyDetector,
    InsightGenerator,
    AnalyticsStorage,
)


class TestEventCollector(unittest.TestCase):
    """Tests for EventCollector."""

    def setUp(self):
        """Set up test fixtures."""
        self.collector = EventCollector(user_id='test_user')

    def test_track_event(self):
        """Test tracking a single event."""
        event_id = self.collector.track(
            event_type='template_opened',
            category='user_action',
            data={'template_id': 'tpl_1'},
            duration_ms=50.0,
        )

        self.assertNotEqual(event_id, '')
        self.assertEqual(self.collector.get_event_count(), 1)

    def test_batch_events(self):
        """Test batching events."""
        for i in range(5):
            self.collector.track(
                event_type='component_added',
                category='designer_action',
                data={'component': f'comp_{i}'},
            )

        batch = self.collector.batch_events(size=3)
        self.assertEqual(len(batch), 3)
        self.assertEqual(self.collector.get_queue_size(), 2)

    def test_event_filtering(self):
        """Test event filtering."""
        self.collector.set_filter('template_opened', False)

        event_id = self.collector.track(
            event_type='template_opened',
            category='user_action',
        )

        self.assertEqual(event_id, '')
        self.assertEqual(self.collector.get_event_count(), 0)

    def test_event_sampling(self):
        """Test event sampling rate."""
        self.collector.set_sampling_rate(0.5)

        tracked = 0
        for _ in range(100):
            event_id = self.collector.track(
                event_type='component_added',
                category='designer_action',
            )
            if event_id:
                tracked += 1

        # Should be approximately 50 (with some variance)
        self.assertGreater(tracked, 20)
        self.assertLess(tracked, 80)

    def test_flush_events(self):
        """Test flushing events."""
        for i in range(10):
            self.collector.track(
                event_type='component_added',
                category='designer_action',
            )

        flushed = self.collector.flush_events()
        self.assertEqual(flushed, 10)
        self.assertEqual(self.collector.get_queue_size(), 0)

    def test_peek_events(self):
        """Test peeking at events without removing."""
        for i in range(5):
            self.collector.track(
                event_type='component_added',
                category='designer_action',
            )

        events = self.collector.peek_events(size=3)
        self.assertEqual(len(events), 3)
        self.assertEqual(self.collector.get_queue_size(), 5)


class TestMetricsAnalyzer(unittest.TestCase):
    """Tests for MetricsAnalyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = MetricsAnalyzer()
        self.now = datetime.now()

    def test_analyze_events(self):
        """Test analyzing events to compute metrics."""
        events = [
            Event(
                event_type='render',
                timestamp=self.now,
                event_id='e1',
                user_id='u1',
                category='performance',
                data={},
                duration_ms=100.0,
            ),
            Event(
                event_type='render',
                timestamp=self.now,
                event_id='e2',
                user_id='u1',
                category='performance',
                data={},
                duration_ms=150.0,
            ),
        ]

        metrics = self.analyzer.analyze_events(events)
        self.assertIn('latency_mean', metrics)
        self.assertAlmostEqual(metrics['latency_mean'].value, 125.0)

    def test_percentile_calculation(self):
        """Test percentile calculations."""
        values = list(range(1, 101))  # 1-100

        percentiles = self.analyzer.calculate_percentiles(
            values,
            [25, 50, 75, 95],
        )

        self.assertIn(25, percentiles)
        self.assertIn(50, percentiles)
        self.assertIn(75, percentiles)
        self.assertIn(95, percentiles)

    def test_time_series_metrics(self):
        """Test time-series metric computation."""
        events = []
        for hour in range(3):
            for i in range(5):
                events.append(Event(
                    event_type='render',
                    timestamp=self.now - timedelta(hours=3-hour) + timedelta(minutes=i*10),
                    event_id=f'e_{hour}_{i}',
                    user_id='u1',
                    category='performance',
                    data={},
                    duration_ms=100.0 + i*10,
                ))

        ts = self.analyzer.get_time_series_metrics(
            events=events,
            metric_name='latency_mean',
            aggregation='hourly',
        )

        self.assertIsNotNone(ts)
        self.assertEqual(len(ts.values), 3)

    def test_get_aggregate(self):
        """Test aggregate metric calculation."""
        events = [
            Event(
                event_type='render',
                timestamp=self.now,
                event_id='e1',
                user_id='u1',
                category='performance',
                data={},
                duration_ms=100.0,
            ),
            Event(
                event_type='render',
                timestamp=self.now,
                event_id='e2',
                user_id='u1',
                category='performance',
                data={},
                duration_ms=200.0,
            ),
        ]

        mean = self.analyzer.get_aggregate(events, 'latency', 'mean')
        self.assertEqual(mean, 150.0)

        total = self.analyzer.get_aggregate(events, 'latency', 'sum')
        self.assertEqual(total, 300.0)


class TestTemplateIntelligence(unittest.TestCase):
    """Tests for TemplateIntelligence."""

    def setUp(self):
        """Set up test fixtures."""
        self.intelligence = TemplateIntelligence()
        self.now = datetime.now()

    def test_template_analysis(self):
        """Test analyzing template."""
        events = [
            Event(
                event_type='template_opened',
                timestamp=self.now,
                event_id='e1',
                user_id='u1',
                category='user_action',
                data={'template_id': 'tpl_1'},
            ),
            Event(
                event_type='component_added',
                timestamp=self.now,
                event_id='e2',
                user_id='u1',
                category='designer_action',
                data={'template_id': 'tpl_1', 'component_type': 'text'},
            ),
            Event(
                event_type='component_added',
                timestamp=self.now,
                event_id='e3',
                user_id='u1',
                category='designer_action',
                data={'template_id': 'tpl_1', 'component_type': 'button'},
            ),
        ]

        analysis = self.intelligence.analyze_template('tpl_1', events)
        self.assertEqual(analysis['template_id'], 'tpl_1')
        self.assertEqual(analysis['event_count'], 3)
        self.assertEqual(analysis['modification_count'], 2)

    def test_component_popularity(self):
        """Test component popularity ranking."""
        events = [
            Event(
                event_type='component_added',
                timestamp=self.now,
                event_id='e1',
                user_id='u1',
                category='designer_action',
                data={'component_type': 'text'},
            ),
            Event(
                event_type='component_added',
                timestamp=self.now,
                event_id='e2',
                user_id='u1',
                category='designer_action',
                data={'component_type': 'text'},
            ),
            Event(
                event_type='component_added',
                timestamp=self.now,
                event_id='e3',
                user_id='u1',
                category='designer_action',
                data={'component_type': 'button'},
            ),
        ]

        for event in events:
            self.intelligence.analyze_template('tpl_1', [event])

        popularity = self.intelligence.get_component_popularity()
        self.assertIn('text', popularity)
        self.assertEqual(popularity['text'], 2)

    def test_usage_patterns(self):
        """Test usage pattern extraction."""
        events = [
            Event(
                event_type='template_opened',
                timestamp=self.now,
                event_id='e1',
                user_id='u1',
                category='user_action',
                data={'template_id': 'tpl_1'},
            ),
            Event(
                event_type='template_saved',
                timestamp=self.now,
                event_id='e2',
                user_id='u1',
                category='user_action',
                data={'template_id': 'tpl_1'},
            ),
        ]

        self.intelligence.analyze_template('tpl_1', events)
        patterns = self.intelligence.get_usage_patterns('tpl_1')

        self.assertIn('template_id', patterns)
        self.assertIn('modification_frequency', patterns)

    def test_skill_classification(self):
        """Test user skill level classification."""
        # Beginner: many undos
        beginner_events = [
            Event(
                event_type='undo_executed',
                timestamp=self.now - timedelta(minutes=i),
                event_id=f'e_{i}',
                user_id='u1',
                category='designer_action',
                data={},
            )
            for i in range(40)
        ]

        skill = self.intelligence.classify_user_skill_level(beginner_events)
        self.assertEqual(skill, 'beginner')

        # Advanced: many modifications, few undos
        advanced_events = [
            Event(
                event_type='component_added',
                timestamp=self.now - timedelta(minutes=i),
                event_id=f'e_{i}',
                user_id='u1',
                category='designer_action',
                data={},
            )
            for i in range(60)
        ]

        skill = self.intelligence.classify_user_skill_level(advanced_events)
        self.assertEqual(skill, 'advanced')

    def test_complexity_calculation(self):
        """Test template complexity scoring."""
        complexity = self.intelligence.calculate_template_complexity('tpl_1', component_count=10)
        self.assertEqual(complexity, 50.0)

        complexity = self.intelligence.calculate_template_complexity('tpl_2', component_count=20)
        self.assertEqual(complexity, 100.0)


class TestAnomalyDetector(unittest.TestCase):
    """Tests for AnomalyDetector."""

    def setUp(self):
        """Set up test fixtures."""
        self.detector = AnomalyDetector()
        self.now = datetime.now()

    def test_statistical_anomalies(self):
        """Test Z-score anomaly detection."""
        normal_duration = 100.0
        events = [
            Event(
                event_type='render',
                timestamp=self.now - timedelta(minutes=i),
                event_id=f'e_{i}',
                user_id='u1',
                category='performance',
                data={},
                duration_ms=normal_duration,
            )
            for i in range(20)
        ]

        # Add anomaly
        events.append(Event(
            event_type='render',
            timestamp=self.now,
            event_id='e_anomaly',
            user_id='u1',
            category='performance',
            data={},
            duration_ms=500.0,
        ))

        anomalies = self.detector.detect_statistical_anomalies(events)
        self.assertGreater(len(anomalies), 0)
        self.assertEqual(anomalies[0].anomaly_type, 'statistical')

    def test_temporal_anomalies(self):
        """Test temporal anomaly detection."""
        events = []

        # Normal event frequency
        for hour in range(10):
            for i in range(5):
                events.append(Event(
                    event_type='component_added',
                    timestamp=self.now - timedelta(hours=hour) + timedelta(minutes=i*10),
                    event_id=f'e_{hour}_{i}',
                    user_id='u1',
                    category='designer_action',
                    data={},
                ))

        # Spike in one hour
        for i in range(50):
            events.append(Event(
                event_type='component_added',
                timestamp=self.now - timedelta(hours=5) + timedelta(seconds=i*30),
                event_id=f'e_spike_{i}',
                user_id='u1',
                category='designer_action',
                data={},
            ))

        anomalies = self.detector.detect_temporal_anomalies(events)
        self.assertGreater(len(anomalies), 0)

    def test_error_spike_detection(self):
        """Test error spike detection."""
        events = [
            Event(
                event_type='operation',
                timestamp=self.now - timedelta(hours=i),
                event_id=f'e_{i}',
                user_id='u1',
                category='performance',
                data={},
                error=None,
            )
            for i in range(20)
        ]

        # Add error spike
        for i in range(15):
            events.append(Event(
                event_type='operation',
                timestamp=self.now - timedelta(hours=2) + timedelta(seconds=i*10),
                event_id=f'e_error_{i}',
                user_id='u1',
                category='performance',
                data={},
                error=f'Error {i}',
            ))

        anomalies = self.detector.detect_error_spike(events)
        self.assertGreater(len(anomalies), 0)

    def test_is_anomalous(self):
        """Test anomalous value check."""
        baseline = [100.0, 105.0, 95.0, 110.0, 90.0]
        self.detector.set_baseline('latency', baseline)

        is_anom, z_score = self.detector.is_anomalous('latency', 100.0)
        self.assertFalse(is_anom)

        is_anom, z_score = self.detector.is_anomalous('latency', 1000.0)
        self.assertTrue(is_anom)


class TestInsightGenerator(unittest.TestCase):
    """Tests for InsightGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = InsightGenerator()
        self.now = datetime.now()

    def test_generate_all_insights(self):
        """Test generating all insight types."""
        events = [
            Event(
                event_type='render',
                timestamp=self.now,
                event_id=f'e_{i}',
                user_id='u1',
                category='performance',
                data={},
                duration_ms=100.0 + i*50,
            )
            for i in range(20)
        ]

        insights = self.generator.generate_all_insights(events)
        self.assertGreater(len(insights), 0)

    def test_performance_insights(self):
        """Test generating performance insights."""
        # High latency events
        events = [
            Event(
                event_type='render',
                timestamp=self.now,
                event_id=f'e_{i}',
                user_id='u1',
                category='performance',
                data={},
                duration_ms=600.0 + i*100,
            )
            for i in range(10)
        ]

        insights = self.generator.generate_performance_insights(events)
        self.assertGreater(len(insights), 0)
        self.assertTrue(any(i.category == 'performance' for i in insights))

    def test_usage_insights(self):
        """Test generating usage insights."""
        events = [
            Event(
                event_type='template_opened',
                timestamp=self.now - timedelta(minutes=i),
                event_id=f'e_{i}',
                user_id='u1',
                category='user_action',
                data={'template_id': 'tpl_1'},
            )
            for i in range(150)
        ]

        insights = self.generator.generate_usage_insights(events)
        self.assertGreater(len(insights), 0)

    def test_recommendations(self):
        """Test generating recommendations."""
        events = [
            Event(
                event_type='component_added',
                timestamp=self.now - timedelta(minutes=i),
                event_id=f'e_{i}',
                user_id='u1',
                category='designer_action',
                data={},
            )
            for i in range(70)
        ]

        insights = self.generator.generate_recommendations(events)
        self.assertGreater(len(insights), 0)
        self.assertTrue(any(i.category == 'recommendations' for i in insights))

    def test_get_actionable_insights(self):
        """Test getting actionable insights."""
        events = [
            Event(
                event_type='render',
                timestamp=self.now,
                event_id=f'e_{i}',
                user_id='u1',
                category='performance',
                data={},
                duration_ms=600.0,
            )
            for i in range(10)
        ]

        self.generator.generate_all_insights(events)
        actionable = self.generator.get_actionable_insights()

        self.assertGreater(len(actionable), 0)
        self.assertTrue(all(i.confidence >= 0.8 for i in actionable))


class TestAnalyticsStorage(unittest.TestCase):
    """Tests for AnalyticsStorage."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.storage = AnalyticsStorage(db_path=self.db_path)
        self.now = datetime.now()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_load_event(self):
        """Test saving and loading events."""
        event = Event(
            event_type='test_event',
            timestamp=self.now,
            event_id='test_id',
            user_id='u1',
            category='test',
            data={'key': 'value'},
        )

        saved = self.storage.save_event(event)
        self.assertTrue(saved)

        loaded = self.storage.get_event('test_id')
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded['event_type'], 'test_event')

    def test_query_events(self):
        """Test querying events."""
        for i in range(5):
            event = Event(
                event_type='test_event',
                timestamp=self.now - timedelta(hours=i),
                event_id=f'test_id_{i}',
                user_id='u1',
                category='test',
                data={},
            )
            self.storage.save_event(event)

        events = self.storage.query_events()
        self.assertEqual(len(events), 5)

    def test_export_json(self):
        """Test JSON export."""
        event = Event(
            event_type='test_event',
            timestamp=self.now,
            event_id='test_id',
            user_id='u1',
            category='test',
            data={},
        )
        self.storage.save_event(event)

        export_path = os.path.join(self.temp_dir, 'export.json')
        success = self.storage.export_json(export_path)

        self.assertTrue(success)
        self.assertTrue(os.path.exists(export_path))

    def test_delete_old_events(self):
        """Test deleting old events."""
        # Add old event
        old_event = Event(
            event_type='old',
            timestamp=datetime.now() - timedelta(days=100),
            event_id='old_id',
            user_id='u1',
            category='test',
            data={},
        )
        self.storage.save_event(old_event)

        # Add recent event
        recent_event = Event(
            event_type='recent',
            timestamp=self.now,
            event_id='recent_id',
            user_id='u1',
            category='test',
            data={},
        )
        self.storage.save_event(recent_event)

        deleted = self.storage.delete_old_events(days=30)
        self.assertEqual(deleted, 1)

    def test_database_stats(self):
        """Test getting database statistics."""
        event = Event(
            event_type='test',
            timestamp=self.now,
            event_id='id_1',
            user_id='u1',
            category='test',
            data={},
        )
        self.storage.save_event(event)

        stats = self.storage.get_stats()
        self.assertIn('event_count', stats)
        self.assertEqual(stats['event_count'], 1)


class TestAnalyticsManager(unittest.TestCase):
    """Tests for AnalyticsManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.manager = AnalyticsManager(db_path=self.db_path)
        self.now = datetime.now()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_track_event(self):
        """Test tracking events."""
        event_id = self.manager.track_event(
            event_type='test_event',
            category='test',
            data={'key': 'value'},
        )

        self.assertNotEqual(event_id, '')

    def test_get_metrics(self):
        """Test getting metrics."""
        for i in range(10):
            self.manager.track_event(
                event_type='render',
                category='performance',
                duration_ms=100.0 + i*10,
            )

        metrics = self.manager.get_metrics(days=1)
        self.assertGreater(len(metrics), 0)

    def test_get_insights(self):
        """Test getting insights."""
        for i in range(30):
            self.manager.track_event(
                event_type='render',
                category='performance',
                duration_ms=600.0,
            )

        insights = self.manager.get_insights(days=1)
        self.assertGreater(len(insights), 0)

    def test_generate_report(self):
        """Test report generation."""
        for i in range(20):
            self.manager.track_event(
                event_type='test',
                category='test',
                duration_ms=100.0,
            )

        report = self.manager.generate_report(report_type='summary', days=1)
        self.assertIn('event_count', report)
        self.assertGreater(report['event_count'], 0)

    def test_dashboard_data(self):
        """Test getting dashboard data."""
        for i in range(15):
            self.manager.track_event(
                event_type='test',
                category='test',
            )

        dashboard = self.manager.get_dashboard_data()
        self.assertIn('summary', dashboard)
        self.assertIn('metrics', dashboard)
        self.assertIn('insights', dashboard)

    def test_analytics_enabled_disable(self):
        """Test enabling/disabling analytics."""
        self.assertTrue(self.manager.is_analytics_enabled())

        self.manager.set_analytics_enabled(False)
        self.assertFalse(self.manager.is_analytics_enabled())

        event_id = self.manager.track_event(
            event_type='test',
            category='test',
        )
        self.assertEqual(event_id, '')

    def test_retention_policy(self):
        """Test retention policy configuration."""
        success = self.manager.set_retention_days(60)
        self.assertTrue(success)

        success = self.manager.set_retention_days(-1)
        self.assertFalse(success)

    def test_sampling_rate(self):
        """Test event sampling configuration."""
        success = self.manager.set_event_sampling_rate(0.5)
        self.assertTrue(success)

        success = self.manager.set_event_sampling_rate(1.5)
        self.assertFalse(success)

    def test_statistics(self):
        """Test getting system statistics."""
        stats = self.manager.get_statistics()
        self.assertIn('event_collector', stats)
        self.assertIn('storage', stats)
        self.assertIn('configuration', stats)


class TestThreadSafety(unittest.TestCase):
    """Tests for thread safety."""

    def test_concurrent_event_tracking(self):
        """Test concurrent event tracking."""
        import threading

        manager = AnalyticsManager()

        def track_events(count):
            for i in range(count):
                manager.track_event(
                    event_type='concurrent_test',
                    category='test',
                )

        threads = [
            threading.Thread(target=track_events, args=(50,))
            for _ in range(4)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should have tracked 200 events (4 threads * 50 events)
        events = manager.query_events(days=1)
        self.assertGreaterEqual(len(events), 190)


if __name__ == '__main__':
    unittest.main()
