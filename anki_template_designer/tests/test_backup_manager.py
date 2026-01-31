"""
Tests for backup and recovery manager.

Plan 14: Tests for backup, recovery, scheduling, and integrity.
"""

import gzip
import json
import os
import tempfile
import threading
import time
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from anki_template_designer.services.backup_manager import (
    Backup,
    BackupStats,
    BackupStatus,
    BackupType,
    BackupSchedule,
    BackupStorage,
    BackupManager,
    RecoveryManager,
    RecoveryPoint,
    BackupScheduler,
    get_backup_manager,
    init_backup_manager
)


class TestBackup:
    """Tests for Backup dataclass."""
    
    def test_default_values(self):
        """Test default backup values."""
        backup = Backup(backup_id="test1", timestamp=1000.0, backup_type="full")
        assert backup.backup_id == "test1"
        assert backup.status == "pending"
        assert backup.encryption == "none"
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        backup = Backup(
            backup_id="test1",
            timestamp=1000.0,
            backup_type="full",
            template_count=5
        )
        d = backup.to_dict()
        assert d["backupId"] == "test1"
        assert d["templateCount"] == 5
        assert "formattedTime" in d
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "backupId": "test1",
            "timestamp": 1000.0,
            "backupType": "incremental",
            "templateCount": 10
        }
        backup = Backup.from_dict(data)
        assert backup.backup_id == "test1"
        assert backup.backup_type == "incremental"
        assert backup.template_count == 10


class TestBackupStats:
    """Tests for BackupStats dataclass."""
    
    def test_default_values(self):
        """Test default stats values."""
        stats = BackupStats()
        assert stats.total_backups == 0
        assert stats.success_rate == 100.0
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        stats = BackupStats(
            total_backups=5,
            total_size=10000,
            success_rate=95.0
        )
        d = stats.to_dict()
        assert d["totalBackups"] == 5
        assert d["successRate"] == 95.0


class TestBackupSchedule:
    """Tests for BackupSchedule dataclass."""
    
    def test_default_values(self):
        """Test default schedule values."""
        schedule = BackupSchedule(schedule_id="s1")
        assert schedule.enabled is True
        assert schedule.interval_hours == 24
        assert schedule.retention_days == 30
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        schedule = BackupSchedule(
            schedule_id="s1",
            interval_hours=12,
            backup_type="incremental"
        )
        d = schedule.to_dict()
        assert d["scheduleId"] == "s1"
        assert d["intervalHours"] == 12
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "scheduleId": "s1",
            "intervalHours": 6,
            "retentionDays": 7
        }
        schedule = BackupSchedule.from_dict(data)
        assert schedule.interval_hours == 6
        assert schedule.retention_days == 7


class TestBackupStorage:
    """Tests for BackupStorage class."""
    
    @pytest.fixture
    def storage(self, tmp_path):
        """Create storage with temp directory."""
        return BackupStorage(str(tmp_path / "backups"))
    
    def test_save_and_load_compressed(self, storage):
        """Test saving and loading compressed data."""
        data = b"test backup data"
        path, size = storage.save_backup_data("backup1", data, compress=True)
        
        assert storage.backup_exists("backup1")
        loaded = storage.load_backup_data("backup1")
        assert loaded == data
    
    def test_save_uncompressed(self, storage):
        """Test saving uncompressed data."""
        data = b"test backup data"
        path, size = storage.save_backup_data("backup2", data, compress=False)
        
        assert storage.backup_exists("backup2")
        assert size == len(data)
    
    def test_delete_backup(self, storage):
        """Test deleting backup data."""
        storage.save_backup_data("backup1", b"data")
        assert storage.backup_exists("backup1")
        
        result = storage.delete_backup_data("backup1")
        assert result is True
        assert not storage.backup_exists("backup1")
    
    def test_delete_nonexistent(self, storage):
        """Test deleting nonexistent backup."""
        result = storage.delete_backup_data("nonexistent")
        assert result is False
    
    def test_get_backup_size(self, storage):
        """Test getting backup size."""
        data = b"x" * 1000
        storage.save_backup_data("backup1", data, compress=False)
        
        size = storage.get_backup_size("backup1")
        assert size == 1000
    
    def test_save_and_load_metadata(self, storage):
        """Test saving and loading metadata."""
        backups = [
            Backup(backup_id="b1", timestamp=1000.0, backup_type="full"),
            Backup(backup_id="b2", timestamp=2000.0, backup_type="incremental")
        ]
        storage.save_metadata(backups)
        
        loaded = storage.load_metadata()
        assert len(loaded) == 2
        assert loaded[0].backup_id == "b1"
        assert loaded[1].backup_type == "incremental"
    
    def test_load_empty_metadata(self, storage):
        """Test loading when no metadata exists."""
        loaded = storage.load_metadata()
        assert loaded == []
    
    def test_get_total_size(self, storage):
        """Test getting total storage size."""
        storage.save_backup_data("b1", b"x" * 100, compress=False)
        storage.save_backup_data("b2", b"y" * 200, compress=False)
        
        total = storage.get_total_size()
        assert total == 300


class TestRecoveryManager:
    """Tests for RecoveryManager class."""
    
    @pytest.fixture
    def recovery(self, tmp_path):
        """Create recovery manager."""
        storage = BackupStorage(str(tmp_path / "backups"))
        return RecoveryManager(storage), storage
    
    def test_restore_backup(self, recovery, tmp_path):
        """Test restoring a backup."""
        manager, storage = recovery
        
        # Create backup data
        content = {
            "templates": [
                {"id": "t1", "name": "Template 1"},
                {"id": "t2", "name": "Template 2"}
            ]
        }
        data = json.dumps(content).encode("utf-8")
        storage.save_backup_data("backup1", data)
        
        backup = Backup(
            backup_id="backup1",
            timestamp=time.time(),
            backup_type="full",
            status="completed"
        )
        
        target = tmp_path / "restore"
        success, message = manager.restore_backup(backup, str(target))
        
        assert success is True
        assert (target / "t1.json").exists()
        assert (target / "t2.json").exists()
    
    def test_restore_selective(self, recovery, tmp_path):
        """Test selective template restore."""
        manager, storage = recovery
        
        content = {
            "templates": [
                {"id": "t1", "name": "Template 1"},
                {"id": "t2", "name": "Template 2"},
                {"id": "t3", "name": "Template 3"}
            ]
        }
        storage.save_backup_data("backup1", json.dumps(content).encode())
        
        backup = Backup(backup_id="backup1", timestamp=time.time(), 
                       backup_type="full", status="completed")
        
        target = tmp_path / "restore"
        success, _ = manager.restore_backup(backup, str(target), template_ids=["t2"])
        
        assert success
        assert not (target / "t1.json").exists()
        assert (target / "t2.json").exists()
        assert not (target / "t3.json").exists()
    
    def test_restore_missing_backup(self, recovery, tmp_path):
        """Test restoring nonexistent backup."""
        manager, storage = recovery
        
        backup = Backup(backup_id="missing", timestamp=time.time(), backup_type="full")
        success, message = manager.restore_backup(backup, str(tmp_path / "restore"))
        
        assert success is False
        assert "not found" in message
    
    def test_verify_backup_valid(self, recovery):
        """Test verifying valid backup."""
        manager, storage = recovery
        
        content = {"templates": [{"id": "t1"}]}
        data = json.dumps(content).encode()
        storage.save_backup_data("backup1", data)
        
        import hashlib
        checksum = hashlib.sha256(data).hexdigest()
        backup = Backup(backup_id="backup1", timestamp=time.time(),
                       backup_type="full", checksum=checksum)
        
        valid, message = manager.verify_backup(backup)
        assert valid is True
    
    def test_verify_backup_checksum_mismatch(self, recovery):
        """Test verification with wrong checksum."""
        manager, storage = recovery
        
        storage.save_backup_data("backup1", json.dumps({"templates": []}).encode())
        backup = Backup(backup_id="backup1", timestamp=time.time(),
                       backup_type="full", checksum="wrongchecksum")
        
        valid, message = manager.verify_backup(backup)
        assert valid is False
        assert "Checksum mismatch" in message
    
    def test_get_recovery_points(self, recovery):
        """Test getting recovery points."""
        manager, storage = recovery
        
        backups = [
            Backup(backup_id="b1", timestamp=1000.0, backup_type="full", 
                  status="completed", template_ids=["t1"]),
            Backup(backup_id="b2", timestamp=2000.0, backup_type="incremental",
                  status="completed", template_ids=["t2"]),
            Backup(backup_id="b3", timestamp=3000.0, backup_type="full",
                  status="failed")  # Should be excluded
        ]
        
        points = manager.get_recovery_points(backups)
        assert len(points) == 2
        assert points[0].backup_id == "b2"  # Newest first
    
    def test_progress_callback(self, recovery, tmp_path):
        """Test progress callback during restore."""
        manager, storage = recovery
        
        content = {"templates": [{"id": "t1"}]}
        storage.save_backup_data("backup1", json.dumps(content).encode())
        
        progress_calls = []
        manager.add_progress_callback(lambda msg, pct: progress_calls.append((msg, pct)))
        
        backup = Backup(backup_id="backup1", timestamp=time.time(),
                       backup_type="full", status="completed")
        manager.restore_backup(backup, str(tmp_path / "restore"))
        
        assert len(progress_calls) > 0
        assert progress_calls[-1][1] == 100  # Final progress is 100%


class TestBackupScheduler:
    """Tests for BackupScheduler class."""
    
    def test_schedule_backup(self):
        """Test setting up a schedule."""
        callback = Mock(return_value="backup_id")
        scheduler = BackupScheduler(callback)
        
        schedule = BackupSchedule(
            schedule_id="s1",
            interval_hours=1,
            enabled=True
        )
        scheduler.set_schedule(schedule)
        
        assert scheduler.schedule is not None
        assert scheduler.schedule.schedule_id == "s1"
    
    def test_start_stop(self):
        """Test starting and stopping scheduler."""
        callback = Mock(return_value="backup_id")
        scheduler = BackupScheduler(callback)
        
        schedule = BackupSchedule(schedule_id="s1", interval_hours=24)
        scheduler.set_schedule(schedule)
        
        assert scheduler.start() is True
        assert scheduler.is_running is True
        
        scheduler.stop()
        assert scheduler.is_running is False
    
    def test_trigger_now(self):
        """Test triggering immediate backup."""
        callback = Mock(return_value="immediate_backup")
        scheduler = BackupScheduler(callback)
        
        result = scheduler.trigger_now()
        
        assert result == "immediate_backup"
        callback.assert_called_once()
    
    def test_start_without_schedule(self):
        """Test starting without a schedule."""
        scheduler = BackupScheduler(Mock())
        assert scheduler.start() is False


class TestBackupManager:
    """Tests for BackupManager class."""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """Create backup manager."""
        backup_dir = tmp_path / "backups"
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        
        # Create some template files
        (templates_dir / "template1.json").write_text(
            json.dumps({"id": "t1", "name": "Template 1"})
        )
        (templates_dir / "template2.json").write_text(
            json.dumps({"id": "t2", "name": "Template 2"})
        )
        
        return BackupManager(str(backup_dir), str(templates_dir))
    
    def test_create_full_backup(self, manager):
        """Test creating a full backup."""
        backup_id = manager.create_backup(backup_type="full", description="Test backup")
        
        assert backup_id is not None
        backup = manager.get_backup(backup_id)
        assert backup.backup_type == "full"
        assert backup.template_count == 2
        assert backup.status == "completed"
    
    def test_create_incremental_backup(self, manager):
        """Test creating incremental backup."""
        # First create a full backup
        full_id = manager.create_backup(backup_type="full")
        
        # Then create incremental
        incr_id = manager.create_backup(backup_type="incremental")
        
        incr_backup = manager.get_backup(incr_id)
        assert incr_backup.backup_type == "incremental"
        assert incr_backup.parent_backup_id == full_id
    
    def test_list_backups(self, manager):
        """Test listing backups."""
        manager.create_backup()
        manager.create_backup()
        manager.create_backup()
        
        backups = manager.list_backups(limit=2)
        assert len(backups) == 2
    
    def test_list_backups_by_type(self, manager):
        """Test listing backups filtered by type."""
        manager.create_backup(backup_type="full")
        manager.create_backup(backup_type="incremental")
        manager.create_backup(backup_type="full")
        
        full_backups = manager.list_backups(backup_type="full")
        assert len(full_backups) == 2
    
    def test_delete_backup(self, manager):
        """Test deleting a backup."""
        backup_id = manager.create_backup()
        assert manager.get_backup(backup_id) is not None
        
        result = manager.delete_backup(backup_id)
        assert result is True
        assert manager.get_backup(backup_id) is None
    
    def test_restore_backup(self, manager, tmp_path):
        """Test restoring a backup."""
        backup_id = manager.create_backup()
        
        restore_path = tmp_path / "restored"
        success, message = manager.restore_backup(backup_id, str(restore_path))
        
        assert success is True
        assert (restore_path / "t1.json").exists()
    
    def test_verify_backup_integrity(self, manager):
        """Test verifying backup integrity."""
        backup_id = manager.create_backup()
        
        valid, message = manager.verify_backup_integrity(backup_id)
        assert valid is True
        
        # Check status updated
        backup = manager.get_backup(backup_id)
        assert backup.status == "verified"
    
    def test_get_backup_stats(self, manager):
        """Test getting backup statistics."""
        manager.create_backup(backup_type="full")
        manager.create_backup(backup_type="incremental")
        
        stats = manager.get_backup_stats()
        assert stats.total_backups == 2
        assert stats.full_backups == 1
        assert stats.incremental_backups == 1
        assert stats.success_rate == 100.0
    
    def test_get_recovery_points(self, manager):
        """Test getting recovery points."""
        manager.create_backup()
        manager.create_backup()
        
        points = manager.get_recovery_points()
        assert len(points) == 2
    
    def test_schedule_backup(self, manager):
        """Test scheduling backups."""
        schedule_id = manager.schedule_backup(
            interval_hours=24,
            backup_type="full",
            retention_days=7
        )
        
        assert schedule_id is not None
        schedule = manager.get_schedule()
        assert schedule.interval_hours == 24
    
    def test_cancel_scheduled_backup(self, manager):
        """Test cancelling scheduled backup."""
        manager.schedule_backup(interval_hours=24)
        result = manager.cancel_scheduled_backup()
        assert result is True
    
    def test_export_backup(self, manager, tmp_path):
        """Test exporting a backup."""
        backup_id = manager.create_backup()
        export_path = tmp_path / "export" / "backup.gz"
        
        success, message = manager.export_backup(backup_id, str(export_path))
        
        assert success is True
        assert export_path.exists()
    
    def test_import_backup(self, manager, tmp_path):
        """Test importing a backup."""
        # Create an export
        backup_id = manager.create_backup()
        export_path = tmp_path / "export.gz"
        manager.export_backup(backup_id, str(export_path))
        
        # Import it
        new_id, message = manager.import_backup(str(export_path))
        
        assert new_id is not None
        assert "imported" in new_id.lower()
    
    def test_import_invalid_file(self, manager, tmp_path):
        """Test importing invalid file."""
        invalid_path = tmp_path / "invalid.gz"
        invalid_path.write_text("not a backup")
        
        result, message = manager.import_backup(str(invalid_path))
        assert result is None
    
    def test_backup_progress_callback(self, manager):
        """Test progress callback during backup."""
        progress_calls = []
        manager.add_progress_callback(lambda msg, pct: progress_calls.append((msg, pct)))
        
        manager.create_backup()
        
        assert len(progress_calls) > 0
        assert progress_calls[-1][1] == 100
    
    def test_concurrent_backups(self, manager):
        """Test thread safety with concurrent backups."""
        results = []
        
        def create_backup():
            backup_id = manager.create_backup()
            results.append(backup_id)
        
        threads = [threading.Thread(target=create_backup) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All backups should succeed
        assert len(results) == 3
        assert all(r is not None for r in results)
    
    def test_backup_compression(self, manager):
        """Test that backups are compressed."""
        backup_id = manager.create_backup()
        backup = manager.get_backup(backup_id)
        
        # Compressed should be smaller than raw
        assert backup.compressed_size < backup.total_size
    
    def test_backup_checksum(self, manager):
        """Test that backups have checksums."""
        backup_id = manager.create_backup()
        backup = manager.get_backup(backup_id)
        
        assert backup.checksum
        assert len(backup.checksum) == 64  # SHA-256 hex


class TestRetentionPolicy:
    """Tests for backup retention policies."""
    
    @pytest.fixture
    def manager_with_old_backups(self, tmp_path):
        """Create manager with old backups."""
        manager = BackupManager(str(tmp_path / "backups"), str(tmp_path / "templates"))
        
        # Create some "old" backups by manipulating timestamps
        for i in range(5):
            backup_id = manager.create_backup()
            backup = manager.get_backup(backup_id)
            # Make it appear old
            backup.timestamp = time.time() - (40 * 24 * 3600)  # 40 days old
        
        # Create a recent backup
        manager.create_backup()
        
        return manager
    
    def test_apply_retention_policy(self, manager_with_old_backups):
        """Test applying retention policy."""
        manager = manager_with_old_backups
        
        # Schedule with 30-day retention
        manager.schedule_backup(retention_days=30)
        
        # Apply policy
        deleted = manager.apply_retention_policy()
        
        # Old backups should be deleted (except one full backup)
        assert deleted >= 4


class TestGlobalFunctions:
    """Tests for global backup manager functions."""
    
    def test_init_and_get_backup_manager(self, tmp_path):
        """Test initializing and getting global manager."""
        manager = init_backup_manager(str(tmp_path / "backups"))
        
        assert manager is not None
        assert get_backup_manager() is manager
