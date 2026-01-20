"""Analytics data storage and export."""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from threading import RLock
from pathlib import Path
import os
from .event_collector import Event
from .metrics_analyzer import Metric


class AnalyticsStorage:
    """Handles analytics data persistence and export."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize analytics storage.
        
        Args:
            db_path: Path to SQLite database (default: analytics.db)
        """
        self.db_path = db_path or 'analytics.db'
        self.lock = RLock()
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database tables."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    user_id TEXT,
                    category TEXT NOT NULL,
                    data TEXT NOT NULL,
                    duration_ms REAL,
                    error TEXT,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp DATETIME NOT NULL,
                    unit TEXT,
                    tags TEXT,
                    percentile REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Insights table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS insights (
                    insight_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    severity TEXT,
                    confidence REAL,
                    timestamp DATETIME NOT NULL,
                    recommended_actions TEXT,
                    data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create indexes
            cursor.execute(
                'CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)'
            )
            cursor.execute(
                'CREATE INDEX IF NOT EXISTS idx_event_timestamp ON events(timestamp)'
            )
            cursor.execute(
                'CREATE INDEX IF NOT EXISTS idx_metric_name ON metrics(metric_name)'
            )
            cursor.execute(
                'CREATE INDEX IF NOT EXISTS idx_insight_category ON insights(category)'
            )

            conn.commit()
            conn.close()

    def save_event(self, event: Event) -> bool:
        """Save an event to database.
        
        Args:
            event: Event to save
            
        Returns:
            True if saved successfully
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO events
                    (event_id, event_type, timestamp, user_id, category, data, duration_ms, error, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.event_id,
                    event.event_type,
                    event.timestamp.isoformat(),
                    event.user_id,
                    event.category,
                    json.dumps(event.data),
                    event.duration_ms,
                    event.error,
                    json.dumps(event.metadata or {}),
                ))

                conn.commit()
                conn.close()
                return True

            except Exception:
                return False

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get an event by ID.
        
        Args:
            event_id: Event identifier
            
        Returns:
            Event dictionary or None
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute('SELECT * FROM events WHERE event_id = ?', (event_id,))
                row = cursor.fetchone()
                conn.close()

                if row:
                    return dict(row)
                return None

            except Exception:
                return None

    def query_events(
        self,
        event_type: Optional[str] = None,
        category: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Query events with filtering.
        
        Args:
            event_type: Filter by event type
            category: Filter by category
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum results
            
        Returns:
            List of event dictionaries
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                query = 'SELECT * FROM events WHERE 1=1'
                params = []

                if event_type:
                    query += ' AND event_type = ?'
                    params.append(event_type)

                if category:
                    query += ' AND category = ?'
                    params.append(category)

                if start_time:
                    query += ' AND timestamp >= ?'
                    params.append(start_time.isoformat())

                if end_time:
                    query += ' AND timestamp <= ?'
                    params.append(end_time.isoformat())

                query += ' ORDER BY timestamp DESC LIMIT ?'
                params.append(limit)

                cursor.execute(query, params)
                rows = cursor.fetchall()
                conn.close()

                return [dict(row) for row in rows]

            except Exception:
                return []

    def save_metric(self, metric: Metric) -> bool:
        """Save a metric to database.
        
        Args:
            metric: Metric to save
            
        Returns:
            True if saved successfully
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO metrics
                    (metric_name, value, timestamp, unit, tags, percentile)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    metric.metric_name,
                    metric.value,
                    metric.timestamp.isoformat(),
                    metric.unit,
                    json.dumps(metric.tags),
                    metric.percentile,
                ))

                conn.commit()
                conn.close()
                return True

            except Exception:
                return False

    def get_metrics(self, metric_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get metrics with optional filtering.
        
        Args:
            metric_names: Filter by metric names
            
        Returns:
            List of metric dictionaries
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                if metric_names:
                    placeholders = ','.join('?' * len(metric_names))
                    query = f'SELECT * FROM metrics WHERE metric_name IN ({placeholders}) ORDER BY timestamp DESC'
                    cursor.execute(query, metric_names)
                else:
                    cursor.execute('SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 1000')

                rows = cursor.fetchall()
                conn.close()

                return [dict(row) for row in rows]

            except Exception:
                return []

    def save_insight(self, insight_dict: Dict[str, Any]) -> bool:
        """Save an insight to database.
        
        Args:
            insight_dict: Insight dictionary
            
        Returns:
            True if saved successfully
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO insights
                    (insight_id, title, description, category, severity, confidence, timestamp, recommended_actions, data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    insight_dict.get('insight_id'),
                    insight_dict.get('title'),
                    insight_dict.get('description'),
                    insight_dict.get('category'),
                    insight_dict.get('severity'),
                    insight_dict.get('confidence'),
                    insight_dict.get('timestamp'),
                    json.dumps(insight_dict.get('recommended_actions', [])),
                    json.dumps(insight_dict.get('data', {})),
                ))

                conn.commit()
                conn.close()
                return True

            except Exception:
                return False

    def get_insights(
        self,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get insights with optional filtering.
        
        Args:
            category: Filter by category
            severity: Filter by severity
            limit: Maximum results
            
        Returns:
            List of insight dictionaries
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                query = 'SELECT * FROM insights WHERE 1=1'
                params = []

                if category:
                    query += ' AND category = ?'
                    params.append(category)

                if severity:
                    query += ' AND severity = ?'
                    params.append(severity)

                query += ' ORDER BY timestamp DESC LIMIT ?'
                params.append(limit)

                cursor.execute(query, params)
                rows = cursor.fetchall()
                conn.close()

                return [dict(row) for row in rows]

            except Exception:
                return []

    def delete_old_events(self, days: int) -> int:
        """Delete events older than specified days.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of deleted events
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cutoff = datetime.now() - timedelta(days=days)

                cursor.execute(
                    'DELETE FROM events WHERE timestamp < ?',
                    (cutoff.isoformat(),)
                )

                deleted = cursor.rowcount
                conn.commit()
                conn.close()

                return deleted

            except Exception:
                return 0

    def export_csv(self, filename: str, event_type: Optional[str] = None) -> bool:
        """Export events to CSV.
        
        Args:
            filename: Output filename
            event_type: Optional event type filter
            
        Returns:
            True if exported successfully
        """
        with self.lock:
            try:
                events = self.query_events(event_type=event_type, limit=100000)

                if not events:
                    return False

                import csv

                with open(filename, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=events[0].keys())
                    writer.writeheader()
                    writer.writerows(events)

                return True

            except Exception:
                return False

    def export_json(self, filename: str, include_events: bool = True) -> bool:
        """Export analytics to JSON.
        
        Args:
            filename: Output filename
            include_events: Whether to include events
            
        Returns:
            True if exported successfully
        """
        with self.lock:
            try:
                data = {
                    'exported_at': datetime.now().isoformat(),
                }

                if include_events:
                    data['events'] = self.query_events(limit=10000)

                data['metrics'] = self.get_metrics()
                data['insights'] = self.get_insights(limit=100)

                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2, default=str)

                return True

            except Exception:
                return False

    def get_database_size(self) -> int:
        """Get database file size in bytes.
        
        Returns:
            File size
        """
        try:
            return os.path.getsize(self.db_path)
        except Exception:
            return 0

    def cleanup_database(self) -> bool:
        """Run database cleanup operations.
        
        Returns:
            True if cleanup successful
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Analyze tables
                cursor.execute('ANALYZE')

                # Reindex
                cursor.execute('REINDEX')

                conn.commit()
                conn.close()

                return True

            except Exception:
                return False

    def vacuum_database(self) -> bool:
        """Vacuum database to optimize.
        
        Returns:
            True if vacuum successful
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('VACUUM')

                conn.commit()
                conn.close()

                return True

            except Exception:
                return False

    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics.
        
        Returns:
            Statistics dictionary
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('SELECT COUNT(*) FROM events')
                event_count = cursor.fetchone()[0]

                cursor.execute('SELECT COUNT(*) FROM metrics')
                metric_count = cursor.fetchone()[0]

                cursor.execute('SELECT COUNT(*) FROM insights')
                insight_count = cursor.fetchone()[0]

                conn.close()

                return {
                    'event_count': event_count,
                    'metric_count': metric_count,
                    'insight_count': insight_count,
                    'database_size_bytes': self.get_database_size(),
                    'database_path': self.db_path,
                }

            except Exception:
                return {}
