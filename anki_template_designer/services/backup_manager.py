"""
Backup and Recovery Manager.

Plan 14: Enterprise-grade backup and recovery system.
Provides full/incremental backups, scheduling, and recovery.
"""

import gzip
import hashlib
import json
import logging
import os
import shutil
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("anki_template_designer.services.backup_manager")


class BackupType(Enum):
    """Types of backups."""
    FULL = "full"
    INCREMENTAL = "incremental"


class BackupStatus(Enum):
    """Status of a backup operation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"


@dataclass
class Backup:
    """Represents a backup snapshot."""
    backup_id: str
    timestamp: float
    backup_type: str
    template_count: int = 0
    total_size: int = 0
    compressed_size: int = 0
    encryption: str = "none"
    checksum: str = ""
    parent_backup_id: Optional[str] = None
    status: str = "pending"
    description: str = ""
    template_ids: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "backupId": self.backup_id,
            "timestamp": self.timestamp,
            "backupType": self.backup_type,
            "templateCount": self.template_count,
            "totalSize": self.total_size,
            "compressedSize": self.compressed_size,
            "encryption": self.encryption,
            "checksum": self.checksum,
            "parentBackupId": self.parent_backup_id,
            "status": self.status,
            "description": self.description,
            "templateIds": self.template_ids,
            "formattedTime": datetime.fromtimestamp(self.timestamp).isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Backup":
        """Create from dictionary."""
        return cls(
            backup_id=data.get("backupId", data.get("backup_id", "")),
            timestamp=data.get("timestamp", 0),
            backup_type=data.get("backupType", data.get("backup_type", "full")),
            template_count=data.get("templateCount", data.get("template_count", 0)),
            total_size=data.get("totalSize", data.get("total_size", 0)),
            compressed_size=data.get("compressedSize", data.get("compressed_size", 0)),
            encryption=data.get("encryption", "none"),
            checksum=data.get("checksum", ""),
            parent_backup_id=data.get("parentBackupId", data.get("parent_backup_id")),
            status=data.get("status", "pending"),
            description=data.get("description", ""),
            template_ids=data.get("templateIds", data.get("template_ids", []))
        )


@dataclass
class BackupStats:
    """Statistics about backups."""
    total_backups: int = 0
    total_size: int = 0
    oldest_backup: Optional[float] = None
    newest_backup: Optional[float] = None
    avg_backup_duration_ms: float = 0.0
    success_rate: float = 100.0
    full_backups: int = 0
    incremental_backups: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "totalBackups": self.total_backups,
            "totalSize": self.total_size,
            "oldestBackup": self.oldest_backup,
            "newestBackup": self.newest_backup,
            "avgBackupDurationMs": self.avg_backup_duration_ms,
            "successRate": self.success_rate,
            "fullBackups": self.full_backups,
            "incrementalBackups": self.incremental_backups
        }


@dataclass
class RecoveryPoint:
    """A point-in-time recovery option."""
    timestamp: float
    backup_id: str
    template_ids: List[str]
    description: str
    is_available: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "backupId": self.backup_id,
            "templateIds": self.template_ids,
            "description": self.description,
            "isAvailable": self.is_available,
            "formattedTime": datetime.fromtimestamp(self.timestamp).isoformat()
        }


@dataclass
class BackupSchedule:
    """Backup schedule configuration."""
    schedule_id: str
    enabled: bool = True
    interval_hours: int = 24
    backup_type: str = "full"
    retention_days: int = 30
    max_retries: int = 3
    encryption_enabled: bool = False
    created_at: float = field(default_factory=time.time)
    last_run: Optional[float] = None
    next_run: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scheduleId": self.schedule_id,
            "enabled": self.enabled,
            "intervalHours": self.interval_hours,
            "backupType": self.backup_type,
            "retentionDays": self.retention_days,
            "maxRetries": self.max_retries,
            "encryptionEnabled": self.encryption_enabled,
            "createdAt": self.created_at,
            "lastRun": self.last_run,
            "nextRun": self.next_run
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BackupSchedule":
        """Create from dictionary."""
        return cls(
            schedule_id=data.get("scheduleId", data.get("schedule_id", "")),
            enabled=data.get("enabled", True),
            interval_hours=data.get("intervalHours", data.get("interval_hours", 24)),
            backup_type=data.get("backupType", data.get("backup_type", "full")),
            retention_days=data.get("retentionDays", data.get("retention_days", 30)),
            max_retries=data.get("maxRetries", data.get("max_retries", 3)),
            encryption_enabled=data.get("encryptionEnabled", data.get("encryption_enabled", False)),
            created_at=data.get("createdAt", data.get("created_at", time.time())),
            last_run=data.get("lastRun", data.get("last_run")),
            next_run=data.get("nextRun", data.get("next_run"))
        )


class BackupStorage:
    """Local filesystem storage backend for backups."""
    
    def __init__(self, backup_dir: str):
        """Initialize storage.
        
        Args:
            backup_dir: Directory for storing backups.
        """
        self._backup_dir = Path(backup_dir)
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        self._metadata_file = self._backup_dir / "backups.json"
        self._lock = threading.RLock()
    
    @property
    def backup_dir(self) -> Path:
        """Get backup directory path."""
        return self._backup_dir
    
    def save_backup_data(self, backup_id: str, data: bytes, compress: bool = True) -> Tuple[str, int]:
        """Save backup data to storage.
        
        Args:
            backup_id: Unique backup identifier.
            data: Raw backup data.
            compress: Whether to compress the data.
            
        Returns:
            Tuple of (file_path, compressed_size).
        """
        with self._lock:
            if compress:
                compressed = gzip.compress(data, compresslevel=6)
                file_path = self._backup_dir / f"{backup_id}.gz"
                file_path.write_bytes(compressed)
                return str(file_path), len(compressed)
            else:
                file_path = self._backup_dir / f"{backup_id}.bak"
                file_path.write_bytes(data)
                return str(file_path), len(data)
    
    def load_backup_data(self, backup_id: str) -> Optional[bytes]:
        """Load backup data from storage.
        
        Args:
            backup_id: Unique backup identifier.
            
        Returns:
            Backup data bytes or None if not found.
        """
        with self._lock:
            # Try compressed first
            gz_path = self._backup_dir / f"{backup_id}.gz"
            if gz_path.exists():
                compressed = gz_path.read_bytes()
                return gzip.decompress(compressed)
            
            # Try uncompressed
            bak_path = self._backup_dir / f"{backup_id}.bak"
            if bak_path.exists():
                return bak_path.read_bytes()
            
            return None
    
    def delete_backup_data(self, backup_id: str) -> bool:
        """Delete backup data from storage.
        
        Args:
            backup_id: Unique backup identifier.
            
        Returns:
            True if deleted, False if not found.
        """
        with self._lock:
            deleted = False
            for ext in [".gz", ".bak"]:
                path = self._backup_dir / f"{backup_id}{ext}"
                if path.exists():
                    path.unlink()
                    deleted = True
            return deleted
    
    def backup_exists(self, backup_id: str) -> bool:
        """Check if backup exists in storage.
        
        Args:
            backup_id: Unique backup identifier.
            
        Returns:
            True if backup exists.
        """
        gz_path = self._backup_dir / f"{backup_id}.gz"
        bak_path = self._backup_dir / f"{backup_id}.bak"
        return gz_path.exists() or bak_path.exists()
    
    def get_backup_size(self, backup_id: str) -> int:
        """Get size of backup file.
        
        Args:
            backup_id: Unique backup identifier.
            
        Returns:
            Size in bytes or 0 if not found.
        """
        for ext in [".gz", ".bak"]:
            path = self._backup_dir / f"{backup_id}{ext}"
            if path.exists():
                return path.stat().st_size
        return 0
    
    def save_metadata(self, backups: List[Backup]) -> None:
        """Save backup metadata to JSON file.
        
        Args:
            backups: List of backup metadata.
        """
        with self._lock:
            data = [b.to_dict() for b in backups]
            self._metadata_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    def load_metadata(self) -> List[Backup]:
        """Load backup metadata from JSON file.
        
        Returns:
            List of backup metadata.
        """
        with self._lock:
            if not self._metadata_file.exists():
                return []
            
            try:
                data = json.loads(self._metadata_file.read_text(encoding="utf-8"))
                return [Backup.from_dict(b) for b in data]
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error loading backup metadata: {e}")
                return []
    
    def get_total_size(self) -> int:
        """Get total size of all backups.
        
        Returns:
            Total size in bytes.
        """
        total = 0
        for path in self._backup_dir.glob("*"):
            if path.is_file() and path.suffix in [".gz", ".bak"]:
                total += path.stat().st_size
        return total


class RecoveryManager:
    """Manages backup recovery operations."""
    
    def __init__(self, storage: BackupStorage):
        """Initialize recovery manager.
        
        Args:
            storage: Backup storage backend.
        """
        self._storage = storage
        self._lock = threading.RLock()
        self._progress_callbacks: List[Callable[[str, float], None]] = []
    
    def add_progress_callback(self, callback: Callable[[str, float], None]) -> None:
        """Add recovery progress callback.
        
        Args:
            callback: Function(message, progress_pct) called during recovery.
        """
        self._progress_callbacks.append(callback)
    
    def remove_progress_callback(self, callback: Callable[[str, float], None]) -> None:
        """Remove recovery progress callback."""
        if callback in self._progress_callbacks:
            self._progress_callbacks.remove(callback)
    
    def _notify_progress(self, message: str, progress: float) -> None:
        """Notify all progress callbacks."""
        for cb in self._progress_callbacks:
            try:
                cb(message, progress)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")
    
    def restore_backup(self, backup: Backup, target_path: str,
                      template_ids: Optional[List[str]] = None) -> Tuple[bool, str]:
        """Restore a backup to target path.
        
        Args:
            backup: Backup to restore.
            target_path: Where to restore to.
            template_ids: Optional list of specific templates to restore.
            
        Returns:
            Tuple of (success, message).
        """
        with self._lock:
            try:
                self._notify_progress("Loading backup data...", 0)
                
                # Load backup data
                data = self._storage.load_backup_data(backup.backup_id)
                if data is None:
                    return False, f"Backup data not found: {backup.backup_id}"
                
                self._notify_progress("Parsing backup...", 20)
                
                # Parse backup JSON
                backup_content = json.loads(data.decode("utf-8"))
                templates = backup_content.get("templates", [])
                
                # Filter templates if specific ones requested
                if template_ids:
                    templates = [t for t in templates if t.get("id") in template_ids]
                
                self._notify_progress("Restoring templates...", 40)
                
                # Create target directory
                target = Path(target_path)
                target.mkdir(parents=True, exist_ok=True)
                
                # Restore each template
                restored_count = 0
                total = len(templates)
                for i, template in enumerate(templates):
                    template_id = template.get("id", f"template_{i}")
                    template_file = target / f"{template_id}.json"
                    template_file.write_text(json.dumps(template, indent=2), encoding="utf-8")
                    restored_count += 1
                    
                    progress = 40 + (50 * (i + 1) / max(total, 1))
                    self._notify_progress(f"Restored {restored_count}/{total}...", progress)
                
                self._notify_progress("Recovery complete", 100)
                return True, f"Restored {restored_count} templates to {target_path}"
                
            except json.JSONDecodeError as e:
                return False, f"Invalid backup data: {e}"
            except Exception as e:
                logger.error(f"Restore error: {e}")
                return False, f"Restore failed: {e}"
    
    def get_recovery_points(self, backups: List[Backup]) -> List[RecoveryPoint]:
        """Get available recovery points from backups.
        
        Args:
            backups: List of available backups.
            
        Returns:
            List of recovery points.
        """
        points = []
        for backup in backups:
            if backup.status in ["completed", "verified"]:
                point = RecoveryPoint(
                    timestamp=backup.timestamp,
                    backup_id=backup.backup_id,
                    template_ids=backup.template_ids,
                    description=backup.description or f"{backup.backup_type} backup",
                    is_available=self._storage.backup_exists(backup.backup_id)
                )
                points.append(point)
        
        # Sort by timestamp descending (newest first)
        points.sort(key=lambda p: p.timestamp, reverse=True)
        return points
    
    def verify_backup(self, backup: Backup) -> Tuple[bool, str]:
        """Verify backup integrity.
        
        Args:
            backup: Backup to verify.
            
        Returns:
            Tuple of (valid, message).
        """
        try:
            # Check if data exists
            if not self._storage.backup_exists(backup.backup_id):
                return False, "Backup file not found"
            
            # Load and verify checksum
            data = self._storage.load_backup_data(backup.backup_id)
            if data is None:
                return False, "Could not load backup data"
            
            # Verify checksum if available
            if backup.checksum:
                actual_checksum = hashlib.sha256(data).hexdigest()
                if actual_checksum != backup.checksum:
                    return False, f"Checksum mismatch: expected {backup.checksum}, got {actual_checksum}"
            
            # Verify JSON structure
            try:
                content = json.loads(data.decode("utf-8"))
                if "templates" not in content:
                    return False, "Invalid backup structure: missing templates"
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON: {e}"
            
            return True, "Backup verified successfully"
            
        except Exception as e:
            return False, f"Verification error: {e}"


class BackupScheduler:
    """Handles automated backup scheduling."""
    
    def __init__(self, backup_callback: Callable[[], Optional[str]]):
        """Initialize scheduler.
        
        Args:
            backup_callback: Function to call to create backup, returns backup_id.
        """
        self._backup_callback = backup_callback
        self._schedule: Optional[BackupSchedule] = None
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.RLock()
        self._running = False
        self._retry_count = 0
    
    @property
    def schedule(self) -> Optional[BackupSchedule]:
        """Get current schedule."""
        return self._schedule
    
    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running
    
    def set_schedule(self, schedule: BackupSchedule) -> None:
        """Set backup schedule.
        
        Args:
            schedule: Schedule configuration.
        """
        with self._lock:
            self._schedule = schedule
            if schedule.enabled:
                self._schedule_next()
    
    def start(self) -> bool:
        """Start the scheduler.
        
        Returns:
            True if started successfully.
        """
        with self._lock:
            if self._running:
                return True
            
            if self._schedule is None or not self._schedule.enabled:
                return False
            
            self._running = True
            self._schedule_next()
            return True
    
    def stop(self) -> None:
        """Stop the scheduler."""
        with self._lock:
            self._running = False
            if self._timer:
                self._timer.cancel()
                self._timer = None
    
    def _schedule_next(self) -> None:
        """Schedule next backup execution."""
        with self._lock:
            if not self._running or self._schedule is None:
                return
            
            # Cancel existing timer
            if self._timer:
                self._timer.cancel()
            
            # Calculate next run time
            interval_seconds = self._schedule.interval_hours * 3600
            self._schedule.next_run = time.time() + interval_seconds
            
            # Create timer
            self._timer = threading.Timer(interval_seconds, self._execute_backup)
            self._timer.daemon = True
            self._timer.start()
    
    def _execute_backup(self) -> None:
        """Execute scheduled backup."""
        with self._lock:
            if not self._running or self._schedule is None:
                return
            
            try:
                logger.info("Executing scheduled backup...")
                self._schedule.last_run = time.time()
                
                # Call backup function
                backup_id = self._backup_callback()
                
                if backup_id:
                    logger.info(f"Scheduled backup completed: {backup_id}")
                    self._retry_count = 0
                else:
                    raise Exception("Backup callback returned None")
                    
            except Exception as e:
                logger.error(f"Scheduled backup failed: {e}")
                self._retry_count += 1
                
                # Retry if under max retries
                if self._retry_count < self._schedule.max_retries:
                    logger.info(f"Retrying backup (attempt {self._retry_count + 1}/{self._schedule.max_retries})")
                    # Retry after 5 minutes
                    self._timer = threading.Timer(300, self._execute_backup)
                    self._timer.daemon = True
                    self._timer.start()
                    return
            
            # Schedule next regular backup
            self._schedule_next()
    
    def trigger_now(self) -> Optional[str]:
        """Trigger immediate backup.
        
        Returns:
            Backup ID if successful, None otherwise.
        """
        try:
            return self._backup_callback()
        except Exception as e:
            logger.error(f"Manual backup trigger failed: {e}")
            return None


class BackupManager:
    """Main backup and recovery orchestrator."""
    
    def __init__(self, backup_dir: str, templates_dir: Optional[str] = None):
        """Initialize backup manager.
        
        Args:
            backup_dir: Directory for storing backups.
            templates_dir: Directory containing templates to backup.
        """
        self._storage = BackupStorage(backup_dir)
        self._recovery = RecoveryManager(self._storage)
        self._scheduler = BackupScheduler(self._create_scheduled_backup)
        self._templates_dir = Path(templates_dir) if templates_dir else None
        
        self._backups: List[Backup] = []
        self._lock = threading.RLock()
        self._backup_durations: List[float] = []
        self._failed_count = 0
        self._success_count = 0
        
        self._progress_callbacks: List[Callable[[str, float], None]] = []
        
        # Load existing backup metadata
        self._backups = self._storage.load_metadata()
        
        logger.debug(f"BackupManager initialized with {len(self._backups)} existing backups")
    
    def add_progress_callback(self, callback: Callable[[str, float], None]) -> None:
        """Add backup progress callback."""
        self._progress_callbacks.append(callback)
        self._recovery.add_progress_callback(callback)
    
    def remove_progress_callback(self, callback: Callable[[str, float], None]) -> None:
        """Remove backup progress callback."""
        if callback in self._progress_callbacks:
            self._progress_callbacks.remove(callback)
        self._recovery.remove_progress_callback(callback)
    
    def _notify_progress(self, message: str, progress: float) -> None:
        """Notify all progress callbacks."""
        for cb in self._progress_callbacks:
            try:
                cb(message, progress)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")
    
    def set_templates_dir(self, templates_dir: str) -> None:
        """Set the templates directory.
        
        Args:
            templates_dir: Directory containing templates.
        """
        self._templates_dir = Path(templates_dir)
    
    def create_backup(self, backup_type: str = "full", 
                     description: str = "",
                     encrypt: bool = False) -> Optional[str]:
        """Create a new backup.
        
        Args:
            backup_type: "full" or "incremental".
            description: Optional description.
            encrypt: Whether to encrypt the backup.
            
        Returns:
            Backup ID if successful, None otherwise.
        """
        with self._lock:
            start_time = time.time()
            backup_id = f"backup_{int(start_time * 1000)}"
            
            try:
                self._notify_progress("Starting backup...", 0)
                
                # Create backup metadata
                backup = Backup(
                    backup_id=backup_id,
                    timestamp=start_time,
                    backup_type=backup_type,
                    status="in_progress",
                    description=description,
                    encryption="aes256" if encrypt else "none"
                )
                
                # Find parent for incremental
                if backup_type == "incremental":
                    parent = self._find_parent_backup()
                    if parent:
                        backup.parent_backup_id = parent.backup_id
                
                self._notify_progress("Collecting templates...", 10)
                
                # Collect templates to backup
                templates = self._collect_templates()
                backup.template_count = len(templates)
                backup.template_ids = [t.get("id", f"t{i}") for i, t in enumerate(templates)]
                
                self._notify_progress("Creating backup data...", 30)
                
                # Create backup content
                content = {
                    "version": "1.0",
                    "created": start_time,
                    "backup_type": backup_type,
                    "templates": templates,
                    "metadata": {
                        "description": description,
                        "parent_id": backup.parent_backup_id
                    }
                }
                
                # Serialize
                data = json.dumps(content, indent=2).encode("utf-8")
                backup.total_size = len(data)
                
                # Calculate checksum
                backup.checksum = hashlib.sha256(data).hexdigest()
                
                self._notify_progress("Compressing and saving...", 60)
                
                # Save to storage
                _, compressed_size = self._storage.save_backup_data(backup_id, data)
                backup.compressed_size = compressed_size
                
                # Mark completed
                backup.status = "completed"
                self._backups.append(backup)
                self._storage.save_metadata(self._backups)
                
                # Track stats
                duration_ms = (time.time() - start_time) * 1000
                self._backup_durations.append(duration_ms)
                self._success_count += 1
                
                self._notify_progress("Backup complete!", 100)
                
                logger.info(f"Backup created: {backup_id} ({backup.template_count} templates, "
                           f"{backup.compressed_size} bytes compressed)")
                
                return backup_id
                
            except Exception as e:
                logger.error(f"Backup failed: {e}")
                self._failed_count += 1
                
                # Mark failed
                backup.status = "failed"
                self._backups.append(backup)
                self._storage.save_metadata(self._backups)
                
                return None
    
    def _collect_templates(self) -> List[Dict[str, Any]]:
        """Collect templates for backup.
        
        Returns:
            List of template data dictionaries.
        """
        templates = []
        
        if self._templates_dir and self._templates_dir.exists():
            for path in self._templates_dir.glob("*.json"):
                try:
                    content = json.loads(path.read_text(encoding="utf-8"))
                    if "id" not in content:
                        content["id"] = path.stem
                    templates.append(content)
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Could not read template {path}: {e}")
        
        return templates
    
    def _find_parent_backup(self) -> Optional[Backup]:
        """Find most recent full backup for incremental.
        
        Returns:
            Parent backup or None.
        """
        full_backups = [b for b in self._backups 
                       if b.backup_type == "full" and b.status == "completed"]
        if full_backups:
            return max(full_backups, key=lambda b: b.timestamp)
        return None
    
    def _create_scheduled_backup(self) -> Optional[str]:
        """Create backup for scheduler.
        
        Returns:
            Backup ID if successful.
        """
        schedule = self._scheduler.schedule
        if schedule:
            return self.create_backup(
                backup_type=schedule.backup_type,
                description="Scheduled backup",
                encrypt=schedule.encryption_enabled
            )
        return self.create_backup(description="Scheduled backup")
    
    def restore_backup(self, backup_id: str, target_path: str,
                      template_ids: Optional[List[str]] = None) -> Tuple[bool, str]:
        """Restore a backup.
        
        Args:
            backup_id: ID of backup to restore.
            target_path: Where to restore to.
            template_ids: Optional specific templates to restore.
            
        Returns:
            Tuple of (success, message).
        """
        with self._lock:
            backup = self.get_backup(backup_id)
            if backup is None:
                return False, f"Backup not found: {backup_id}"
            
            return self._recovery.restore_backup(backup, target_path, template_ids)
    
    def list_backups(self, limit: int = 50, backup_type: Optional[str] = None) -> List[Backup]:
        """List available backups.
        
        Args:
            limit: Maximum number to return.
            backup_type: Optional filter by type.
            
        Returns:
            List of backups (newest first).
        """
        with self._lock:
            backups = self._backups.copy()
            
            if backup_type:
                backups = [b for b in backups if b.backup_type == backup_type]
            
            # Sort by timestamp descending
            backups.sort(key=lambda b: b.timestamp, reverse=True)
            
            return backups[:limit]
    
    def get_backup(self, backup_id: str) -> Optional[Backup]:
        """Get a specific backup by ID.
        
        Args:
            backup_id: Backup identifier.
            
        Returns:
            Backup or None if not found.
        """
        with self._lock:
            for backup in self._backups:
                if backup.backup_id == backup_id:
                    return backup
            return None
    
    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup.
        
        Args:
            backup_id: Backup to delete.
            
        Returns:
            True if deleted.
        """
        with self._lock:
            backup = self.get_backup(backup_id)
            if backup is None:
                return False
            
            # Delete data
            self._storage.delete_backup_data(backup_id)
            
            # Remove from list
            self._backups = [b for b in self._backups if b.backup_id != backup_id]
            self._storage.save_metadata(self._backups)
            
            logger.info(f"Backup deleted: {backup_id}")
            return True
    
    def verify_backup_integrity(self, backup_id: str) -> Tuple[bool, str]:
        """Verify a backup's integrity.
        
        Args:
            backup_id: Backup to verify.
            
        Returns:
            Tuple of (valid, message).
        """
        with self._lock:
            backup = self.get_backup(backup_id)
            if backup is None:
                return False, f"Backup not found: {backup_id}"
            
            valid, message = self._recovery.verify_backup(backup)
            
            if valid:
                backup.status = "verified"
                self._storage.save_metadata(self._backups)
            
            return valid, message
    
    def get_backup_stats(self) -> BackupStats:
        """Get backup statistics.
        
        Returns:
            BackupStats object.
        """
        with self._lock:
            completed = [b for b in self._backups if b.status in ["completed", "verified"]]
            
            stats = BackupStats(
                total_backups=len(completed),
                total_size=sum(b.compressed_size for b in completed),
                full_backups=len([b for b in completed if b.backup_type == "full"]),
                incremental_backups=len([b for b in completed if b.backup_type == "incremental"])
            )
            
            if completed:
                stats.oldest_backup = min(b.timestamp for b in completed)
                stats.newest_backup = max(b.timestamp for b in completed)
            
            if self._backup_durations:
                stats.avg_backup_duration_ms = sum(self._backup_durations) / len(self._backup_durations)
            
            total_attempts = self._success_count + self._failed_count
            if total_attempts > 0:
                stats.success_rate = (self._success_count / total_attempts) * 100
            
            return stats
    
    def get_recovery_points(self) -> List[RecoveryPoint]:
        """Get available recovery points.
        
        Returns:
            List of recovery points.
        """
        with self._lock:
            return self._recovery.get_recovery_points(self._backups)
    
    def schedule_backup(self, interval_hours: int = 24,
                       backup_type: str = "full",
                       retention_days: int = 30,
                       max_retries: int = 3,
                       encryption: bool = False) -> str:
        """Schedule automated backups.
        
        Args:
            interval_hours: Hours between backups.
            backup_type: Type of backup to create.
            retention_days: Days to retain backups.
            max_retries: Retry attempts on failure.
            encryption: Enable encryption.
            
        Returns:
            Schedule ID.
        """
        schedule_id = f"schedule_{int(time.time() * 1000)}"
        
        schedule = BackupSchedule(
            schedule_id=schedule_id,
            enabled=True,
            interval_hours=interval_hours,
            backup_type=backup_type,
            retention_days=retention_days,
            max_retries=max_retries,
            encryption_enabled=encryption
        )
        
        self._scheduler.set_schedule(schedule)
        self._scheduler.start()
        
        logger.info(f"Backup scheduled: every {interval_hours}h, type={backup_type}")
        return schedule_id
    
    def cancel_scheduled_backup(self) -> bool:
        """Cancel scheduled backups.
        
        Returns:
            True if cancelled.
        """
        self._scheduler.stop()
        logger.info("Backup schedule cancelled")
        return True
    
    def get_schedule(self) -> Optional[BackupSchedule]:
        """Get current backup schedule.
        
        Returns:
            Schedule or None.
        """
        return self._scheduler.schedule
    
    def apply_retention_policy(self) -> int:
        """Apply retention policy to delete old backups.
        
        Returns:
            Number of backups deleted.
        """
        with self._lock:
            schedule = self._scheduler.schedule
            if schedule is None:
                return 0
            
            retention_seconds = schedule.retention_days * 24 * 3600
            cutoff = time.time() - retention_seconds
            
            # Find backups to delete
            to_delete = [b for b in self._backups 
                        if b.timestamp < cutoff and b.status in ["completed", "verified"]]
            
            # Keep at least one full backup
            full_backups = [b for b in self._backups if b.backup_type == "full" 
                          and b.status in ["completed", "verified"]]
            if len(full_backups) <= 1:
                to_delete = [b for b in to_delete if b.backup_type != "full"]
            
            deleted = 0
            for backup in to_delete:
                if self.delete_backup(backup.backup_id):
                    deleted += 1
            
            if deleted > 0:
                logger.info(f"Retention policy: deleted {deleted} old backups")
            
            return deleted
    
    def export_backup(self, backup_id: str, export_path: str) -> Tuple[bool, str]:
        """Export a backup to a file.
        
        Args:
            backup_id: Backup to export.
            export_path: Where to export.
            
        Returns:
            Tuple of (success, message).
        """
        with self._lock:
            backup = self.get_backup(backup_id)
            if backup is None:
                return False, f"Backup not found: {backup_id}"
            
            try:
                data = self._storage.load_backup_data(backup_id)
                if data is None:
                    return False, "Backup data not found"
                
                export = Path(export_path)
                export.parent.mkdir(parents=True, exist_ok=True)
                
                # Write as zip with metadata
                export.write_bytes(gzip.compress(data))
                
                return True, f"Exported to {export_path}"
                
            except Exception as e:
                return False, f"Export failed: {e}"
    
    def import_backup(self, import_path: str) -> Tuple[Optional[str], str]:
        """Import a backup from file.
        
        Args:
            import_path: Path to backup file.
            
        Returns:
            Tuple of (backup_id or None, message).
        """
        with self._lock:
            try:
                import_file = Path(import_path)
                if not import_file.exists():
                    return None, f"File not found: {import_path}"
                
                # Read and decompress
                compressed = import_file.read_bytes()
                data = gzip.decompress(compressed)
                
                # Validate JSON
                content = json.loads(data.decode("utf-8"))
                if "templates" not in content:
                    return None, "Invalid backup: missing templates"
                
                # Create new backup record
                backup_id = f"imported_{int(time.time() * 1000)}"
                backup = Backup(
                    backup_id=backup_id,
                    timestamp=content.get("created", time.time()),
                    backup_type=content.get("backup_type", "full"),
                    template_count=len(content.get("templates", [])),
                    total_size=len(data),
                    checksum=hashlib.sha256(data).hexdigest(),
                    status="completed",
                    description=f"Imported from {import_file.name}"
                )
                
                # Save backup data
                _, compressed_size = self._storage.save_backup_data(backup_id, data)
                backup.compressed_size = compressed_size
                
                # Save metadata
                self._backups.append(backup)
                self._storage.save_metadata(self._backups)
                
                return backup_id, f"Imported {backup.template_count} templates"
                
            except gzip.BadGzipFile:
                return None, "Invalid backup file format"
            except json.JSONDecodeError as e:
                return None, f"Invalid backup content: {e}"
            except Exception as e:
                return None, f"Import failed: {e}"


# Global instance
_backup_manager: Optional[BackupManager] = None


def get_backup_manager() -> Optional[BackupManager]:
    """Get the global backup manager instance.
    
    Returns:
        BackupManager or None if not initialized.
    """
    return _backup_manager


def init_backup_manager(backup_dir: str, templates_dir: Optional[str] = None) -> BackupManager:
    """Initialize the global backup manager.
    
    Args:
        backup_dir: Directory for storing backups.
        templates_dir: Directory containing templates.
        
    Returns:
        Initialized BackupManager.
    """
    global _backup_manager
    _backup_manager = BackupManager(backup_dir, templates_dir)
    logger.debug("Backup manager initialized")
    return _backup_manager
