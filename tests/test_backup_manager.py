"""
Tests for Backup Manager (Issue #56)

Comprehensive test suite with 35+ tests covering:
- Full and incremental backup strategies
- Point-in-time recovery
- Automated scheduling
- Backup verification
- Integration tests
"""

import unittest
import time
import threading
import tempfile
import os
import shutil
from services.backup_manager import (
    BackupManager, BackupStrategy, FullBackupStrategy, IncrementalBackupStrategy,
    RecoveryManager, SchedulingSystem, Backup, BackupStats, RecoveryPoint,
    BackupType, BackupStatus
)


class TestBackupManager(unittest.TestCase):
    """Tests for backup manager"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backup_mgr = BackupManager(self.temp_dir)
        self.templates = [
            {'id': 'template1', 'name': 'Template 1', 'content': 'Content 1' * 100},
            {'id': 'template2', 'name': 'Template 2', 'content': 'Content 2' * 100},
        ]

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_create_full_backup(self):
        """Test creating full backup"""
        backup_id = self.backup_mgr.create_backup('full', self.templates)
        self.assertIsNotNone(backup_id)
        
        backup = self.backup_mgr.get_backup(backup_id)
        self.assertIsNotNone(backup)
        self.assertEqual(backup.backup_type, 'full')
        self.assertEqual(backup.template_count, 2)

    def test_create_incremental_backup(self):
        """Test creating incremental backup"""
        # First full backup
        full_id = self.backup_mgr.create_backup('full', self.templates)
        self.assertIsNotNone(full_id)
        
        # Then incremental
        incr_id = self.backup_mgr.create_backup('incremental', self.templates[:1])
        self.assertIsNotNone(incr_id)
        
        incr_backup = self.backup_mgr.get_backup(incr_id)
        self.assertEqual(incr_backup.backup_type, 'incremental')
        self.assertEqual(incr_backup.parent_backup_id, full_id)

    def test_list_backups(self):
        """Test listing backups"""
        id1 = self.backup_mgr.create_backup('full', self.templates)
        time.sleep(0.01)  # Ensure different timestamps
        id2 = self.backup_mgr.create_backup('full', self.templates)
        
        backups = self.backup_mgr.list_backups()
        self.assertGreaterEqual(len(backups), 2)

    def test_list_backups_with_limit(self):
        """Test listing with limit"""
        for i in range(5):
            self.backup_mgr.create_backup('full', self.templates)
        
        backups = self.backup_mgr.list_backups(limit=3)
        self.assertEqual(len(backups), 3)

    def test_get_backup(self):
        """Test getting backup details"""
        backup_id = self.backup_mgr.create_backup('full', self.templates)
        backup = self.backup_mgr.get_backup(backup_id)
        
        self.assertIsNotNone(backup)
        self.assertEqual(backup.backup_id, backup_id)

    def test_delete_backup(self):
        """Test deleting backup"""
        backup_id = self.backup_mgr.create_backup('full', self.templates)
        result = self.backup_mgr.delete_backup(backup_id)
        self.assertTrue(result)
        
        backup = self.backup_mgr.get_backup(backup_id)
        self.assertIsNone(backup)

    def test_delete_nonexistent_backup(self):
        """Test deleting non-existent backup"""
        result = self.backup_mgr.delete_backup('nonexistent')
        self.assertFalse(result)

    def test_backup_with_encryption(self):
        """Test encrypted backup"""
        backup_id = self.backup_mgr.create_backup(
            'full',
            self.templates,
            encryption=True
        )
        self.assertIsNotNone(backup_id)

    def test_backup_size_calculation(self):
        """Test backup size is calculated"""
        backup_id = self.backup_mgr.create_backup('full', self.templates)
        backup = self.backup_mgr.get_backup(backup_id)
        
        self.assertGreater(backup.total_size, 0)
        self.assertGreater(backup.compressed_size, 0)
        self.assertLess(backup.compressed_size, backup.total_size)

    def test_backup_checksum(self):
        """Test backup checksum"""
        backup_id = self.backup_mgr.create_backup('full', self.templates)
        backup = self.backup_mgr.get_backup(backup_id)
        
        self.assertIsNotNone(backup.checksum)
        self.assertEqual(len(backup.checksum), 64)  # SHA256 hex

    def test_get_backup_stats(self):
        """Test backup statistics"""
        self.backup_mgr.create_backup('full', self.templates)
        self.backup_mgr.create_backup('full', self.templates)
        
        stats = self.backup_mgr.get_backup_stats()
        self.assertEqual(stats.total_backups, 2)
        self.assertGreater(stats.total_size, 0)


class TestRecoveryManager(unittest.TestCase):
    """Tests for recovery management"""

    def setUp(self):
        self.recovery_mgr = RecoveryManager()
        self.templates = [
            {'id': 'template1', 'name': 'Template 1'},
            {'id': 'template2', 'name': 'Template 2'},
        ]

    def test_create_recovery_point(self):
        """Test creating recovery point"""
        point_id = self.recovery_mgr.create_recovery_point(
            'backup1',
            ['template1', 'template2'],
            'Test point'
        )
        self.assertIsNotNone(point_id)

    def test_get_recovery_points(self):
        """Test getting recovery points"""
        self.recovery_mgr.create_recovery_point('backup1', ['t1', 't2'])
        self.recovery_mgr.create_recovery_point('backup2', ['t3'])
        
        points = self.recovery_mgr.get_recovery_points()
        self.assertEqual(len(points), 2)

    def test_verify_recovery_point(self):
        """Test verifying recovery point"""
        self.recovery_mgr.create_recovery_point('backup1', ['t1'])
        
        valid, msg = self.recovery_mgr.verify_recovery_point('backup1')
        self.assertTrue(valid)

    def test_verify_nonexistent_point(self):
        """Test verifying non-existent point"""
        valid, msg = self.recovery_mgr.verify_recovery_point('nonexistent')
        self.assertFalse(valid)

    def test_get_point_in_time(self):
        """Test point-in-time recovery"""
        now = time.time()
        self.recovery_mgr.create_recovery_point('backup1', ['t1'])
        
        point = self.recovery_mgr.get_point_in_time(now)
        self.assertIsNotNone(point)

    def test_restore_to_point(self):
        """Test restore to recovery point"""
        self.recovery_mgr.create_recovery_point('backup1', ['t1', 't2'])
        result = self.recovery_mgr.restore_to_point('backup1', '/target')
        self.assertTrue(result)


class TestBackupScheduling(unittest.TestCase):
    """Tests for backup scheduling"""

    def setUp(self):
        self.scheduler = SchedulingSystem()

    def test_create_schedule(self):
        """Test creating schedule"""
        schedule_id = self.scheduler.create_schedule('full', 24)
        self.assertIsNotNone(schedule_id)

    def test_get_schedules(self):
        """Test getting schedules"""
        self.scheduler.create_schedule('full', 24)
        self.scheduler.create_schedule('incremental', 6)
        
        schedules = self.scheduler.get_schedules()
        self.assertEqual(len(schedules), 2)

    def test_update_schedule(self):
        """Test updating schedule"""
        schedule_id = self.scheduler.create_schedule('full', 24)
        result = self.scheduler.update_schedule(
            schedule_id,
            interval_hours=12
        )
        self.assertTrue(result)

    def test_delete_schedule(self):
        """Test deleting schedule"""
        schedule_id = self.scheduler.create_schedule('full', 24)
        result = self.scheduler.delete_schedule(schedule_id)
        self.assertTrue(result)
        
        schedules = self.scheduler.get_schedules()
        self.assertEqual(len(schedules), 0)

    def test_schedule_with_encryption(self):
        """Test creating encrypted schedule"""
        schedule_id = self.scheduler.create_schedule(
            'full',
            24,
            encryption=True
        )
        schedule = self.scheduler.get_schedules()[0]
        self.assertTrue(schedule.encryption_enabled)

    def test_log_execution(self):
        """Test logging schedule execution"""
        schedule_id = self.scheduler.create_schedule('full', 24)
        self.scheduler.log_execution(schedule_id, True, 1234.5)
        
        history = self.scheduler.get_execution_history(schedule_id)
        self.assertEqual(len(history), 1)
        self.assertTrue(history[0]['success'])

    def test_execution_history_filtering(self):
        """Test filtering execution history"""
        id1 = self.scheduler.create_schedule('full', 24)
        id2 = self.scheduler.create_schedule('incremental', 6)
        
        self.scheduler.log_execution(id1, True, 100)
        self.scheduler.log_execution(id2, True, 200)
        
        history1 = self.scheduler.get_execution_history(id1)
        self.assertEqual(len(history1), 1)


class TestBackupStorage(unittest.TestCase):
    """Tests for backup storage"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backup_mgr = BackupManager(self.temp_dir)
        self.templates = [
            {'id': 't1', 'content': 'Content 1' * 50}
        ]

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_local_storage(self):
        """Test local storage"""
        backup_id = self.backup_mgr.create_backup('full', self.templates)
        self.assertIsNotNone(backup_id)
        
        backup_dir = os.path.join(self.temp_dir, backup_id)
        self.assertTrue(os.path.exists(backup_dir))

    def test_export_backup(self):
        """Test exporting backup"""
        backup_id = self.backup_mgr.create_backup('full', self.templates)
        export_path = tempfile.gettempdir()
        
        exported = self.backup_mgr.export_backup(backup_id, export_path, 'zip')
        self.assertIsNotNone(exported)

    def test_import_backup(self):
        """Test importing backup"""
        # Create and export
        backup_id = self.backup_mgr.create_backup('full', self.templates)
        export_dir = tempfile.mkdtemp()
        
        try:
            exported = self.backup_mgr.export_backup(backup_id, export_dir, 'zip')
            
            # Import
            imported_id = self.backup_mgr.import_backup(exported)
            self.assertIsNotNone(imported_id)
        finally:
            if os.path.exists(export_dir):
                shutil.rmtree(export_dir)


class TestBackupIntegrity(unittest.TestCase):
    """Tests for backup integrity"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backup_mgr = BackupManager(self.temp_dir)
        self.templates = [
            {'id': 't1', 'content': 'Test content'}
        ]

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_verify_backup_integrity(self):
        """Test backup verification"""
        backup_id = self.backup_mgr.create_backup('full', self.templates)
        valid, details = self.backup_mgr.verify_backup_integrity(backup_id)
        
        self.assertTrue(valid)
        self.assertEqual(details['backup_id'], backup_id)

    def test_verify_nonexistent_backup(self):
        """Test verifying non-existent backup"""
        valid, details = self.backup_mgr.verify_backup_integrity('nonexistent')
        self.assertFalse(valid)

    def test_backup_status_tracking(self):
        """Test backup status tracking"""
        backup_id = self.backup_mgr.create_backup('full', self.templates)
        backup = self.backup_mgr.get_backup(backup_id)
        
        self.assertEqual(backup.status, BackupStatus.COMPLETED.value)
        self.assertEqual(len(backup.checksum), 64)

    def test_cleanup_old_backups(self):
        """Test cleanup of old backups"""
        self.backup_mgr.create_backup('full', self.templates)
        
        # Mock old backup
        old_backup_id = f"old_backup_{int((time.time() - 40*24*3600) * 1000)}"
        old_backup = Backup(
            backup_id=old_backup_id,
            timestamp=time.time() - 40*24*3600,
            backup_type='full',
            template_count=1,
            total_size=1000,
            compressed_size=700,
            status='completed'
        )
        self.backup_mgr.backups[old_backup_id] = old_backup
        
        # Cleanup
        deleted = self.backup_mgr.cleanup_old_backups(retention_days=30)
        self.assertGreaterEqual(deleted, 1)


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backup_mgr = BackupManager(self.temp_dir)
        self.templates = [
            {'id': 'template1', 'name': 'T1', 'content': 'Content 1' * 100},
            {'id': 'template2', 'name': 'T2', 'content': 'Content 2' * 100},
        ]

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_complete_backup_restore_cycle(self):
        """Test complete backup and restore"""
        # Create backups
        full_id = self.backup_mgr.create_backup('full', self.templates)
        self.assertIsNotNone(full_id)
        
        # Verify
        valid, details = self.backup_mgr.verify_backup_integrity(full_id)
        self.assertTrue(valid)
        
        # Restore
        target_path = os.path.join(self.temp_dir, 'restore')
        result = self.backup_mgr.restore_backup(full_id, target_path)
        self.assertTrue(result)

    def test_disaster_recovery_workflow(self):
        """Test disaster recovery workflow"""
        # Initial backup
        backup1 = self.backup_mgr.create_backup('full', self.templates)
        
        # Create schedule
        schedule_id = self.backup_mgr.schedule_backup(24, 'incremental')
        self.assertIsNotNone(schedule_id)
        
        # Simulate incremental backup
        modified_templates = self.templates[:1]
        backup2 = self.backup_mgr.create_backup('incremental', modified_templates)
        
        # Get recovery points
        points = self.backup_mgr.get_recovery_points()
        self.assertEqual(len(points), 2)
        
        # Verify both backups
        for bid in [backup1, backup2]:
            valid, _ = self.backup_mgr.verify_backup_integrity(bid)
            self.assertTrue(valid)


class TestThreadSafety(unittest.TestCase):
    """Thread safety tests"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backup_mgr = BackupManager(self.temp_dir)
        self.templates = [{'id': 'template1', 'content': 'Content 1' * 50}]

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_concurrent_backups(self):
        """Test concurrent backup creation"""
        results = []

        def create_backup():
            backup_id = self.backup_mgr.create_backup('full', self.templates)
            results.append(backup_id is not None)

        threads = [threading.Thread(target=create_backup) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(results), 5)
        self.assertTrue(all(results))

    def test_concurrent_restore(self):
        """Test concurrent restore operations"""
        # Create backup first
        backup_id = self.backup_mgr.create_backup('full', self.templates)
        
        results = []

        def restore():
            target = os.path.join(self.temp_dir, f'restore_{len(results)}')
            result = self.backup_mgr.restore_backup(backup_id, target)
            results.append(result)

        threads = [threading.Thread(target=restore) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertTrue(all(results))


if __name__ == '__main__':
    unittest.main()
