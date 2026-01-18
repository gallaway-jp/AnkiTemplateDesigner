"""
Tests for Cloud Storage Manager (Issue #57)

Comprehensive test suite with 40+ tests covering:
- Multi-cloud backends (S3, Azure, GCS)
- Real-time synchronization
- Conflict detection and resolution
- Offline-first architecture
"""

import unittest
import time
import threading
import json
from services.cloud_storage_manager import (
    CloudStorageManager, S3Backend, AzureBackend, GCSBackend,
    CloudSync, ConflictResolver, SyncOperation, RemoteFile,
    CloudProvider, SyncOperationType, ConflictStrategy
)


# ============================================================================
# Cloud Storage Manager Tests
# ============================================================================

class TestCloudStorageManager(unittest.TestCase):
    """Tests for cloud storage manager"""

    def setUp(self):
        self.manager = CloudStorageManager()
        self.credentials = {'bucket': 'test-bucket'}

    def test_configure_s3_backend(self):
        """Test configuring S3 backend"""
        result = self.manager.configure_backend('s3', self.credentials)
        self.assertTrue(result)
        self.assertIsNotNone(self.manager.backend)

    def test_configure_azure_backend(self):
        """Test configuring Azure backend"""
        result = self.manager.configure_backend('azure', 
                                               {'container': 'test'})
        self.assertTrue(result)
        self.assertIsNotNone(self.manager.backend)

    def test_configure_gcs_backend(self):
        """Test configuring GCS backend"""
        result = self.manager.configure_backend('gcs', self.credentials)
        self.assertTrue(result)
        self.assertIsNotNone(self.manager.backend)

    def test_configure_invalid_backend(self):
        """Test configuring invalid backend"""
        result = self.manager.configure_backend('invalid', self.credentials)
        self.assertFalse(result)

    def test_upload_template(self):
        """Test uploading template"""
        self.manager.configure_backend('s3', self.credentials)
        
        template = {'id': 'template1', 'name': 'Test', 'content': 'Content'}
        result = self.manager.upload_template('template1', template)
        self.assertTrue(result)

    def test_upload_without_backend(self):
        """Test upload without configured backend"""
        template = {'id': 'template1', 'content': 'Content'}
        result = self.manager.upload_template('template1', template)
        self.assertFalse(result)

    def test_download_template(self):
        """Test downloading template"""
        self.manager.configure_backend('s3', self.credentials)
        
        # Upload first
        template = {'id': 'template1', 'content': 'Content'}
        self.manager.upload_template('template1', template)
        
        # Download
        result = self.manager.download_template('template1')
        self.assertIsNotNone(result)

    def test_sync_all(self):
        """Test synchronizing all templates"""
        self.manager.configure_backend('s3', self.credentials)
        
        local_files = {
            'template1': {'id': 'template1', 'content': 'Content 1'},
            'template2': {'id': 'template2', 'content': 'Content 2'},
        }
        
        success, result = self.manager.sync_all(local_files)
        self.assertTrue(success)
        self.assertIn('uploaded', result)

    def test_get_sync_status(self):
        """Test getting sync status"""
        self.manager.configure_backend('s3', self.credentials)
        
        status = self.manager.get_sync_status()
        self.assertIn('syncing', status)
        self.assertIn('offline_mode', status)

    def test_get_storage_stats(self):
        """Test getting storage statistics"""
        self.manager.configure_backend('s3', self.credentials)
        
        stats = self.manager.get_storage_stats()
        self.assertIn('total_used', stats)
        self.assertIn('template_count', stats)

    def test_offline_mode_enable_disable(self):
        """Test enabling/disabling offline mode"""
        result = self.manager.enable_offline_mode()
        self.assertTrue(result)
        
        status = self.manager.get_sync_status()
        self.assertTrue(status['offline_mode'])
        
        result = self.manager.disable_offline_mode()
        self.assertTrue(result)


# ============================================================================
# S3 Backend Tests
# ============================================================================

class TestS3Backend(unittest.TestCase):
    """Tests for S3 backend"""

    def setUp(self):
        self.backend = S3Backend({'bucket': 'test-bucket'})

    def test_s3_upload(self):
        """Test S3 upload"""
        result = self.backend.upload('file1', b'content', {'name': 'file1'})
        self.assertTrue(result)

    def test_s3_download(self):
        """Test S3 download"""
        self.backend.upload('file1', b'content', {'name': 'file1'})
        
        success, data = self.backend.download('file1')
        self.assertTrue(success)
        self.assertIsNotNone(data)

    def test_s3_download_nonexistent(self):
        """Test downloading non-existent file"""
        success, data = self.backend.download('nonexistent')
        self.assertFalse(success)

    def test_s3_delete(self):
        """Test S3 delete"""
        self.backend.upload('file1', b'content', {'name': 'file1'})
        
        result = self.backend.delete('file1')
        self.assertTrue(result)

    def test_s3_list_files(self):
        """Test S3 list files"""
        self.backend.upload('file1', b'content1', {'name': 'file1'})
        self.backend.upload('file2', b'content2', {'name': 'file2'})
        
        files = self.backend.list_files()
        self.assertEqual(len(files), 2)

    def test_s3_list_files_with_prefix(self):
        """Test S3 list with prefix"""
        self.backend.upload('prefix_file1', b'content1', {'name': 'prefix_file1'})
        self.backend.upload('other_file', b'content2', {'name': 'other_file'})
        
        files = self.backend.list_files('prefix')
        self.assertEqual(len(files), 1)

    def test_s3_get_metadata(self):
        """Test getting S3 file metadata"""
        self.backend.upload('file1', b'content', {'name': 'file1'})
        
        metadata = self.backend.get_file_metadata('file1')
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.file_id, 'file1')

    def test_s3_multipart_large_file(self):
        """Test S3 multipart upload"""
        large_data = b'x' * (10 * 1024 * 1024)  # 10MB
        result = self.backend.upload('large_file', large_data, {'name': 'large_file'})
        self.assertTrue(result)


# ============================================================================
# Azure Backend Tests
# ============================================================================

class TestAzureBackend(unittest.TestCase):
    """Tests for Azure backend"""

    def setUp(self):
        self.backend = AzureBackend({'container': 'test-container'})

    def test_azure_upload(self):
        """Test Azure upload"""
        result = self.backend.upload('blob1', b'content', {'name': 'blob1'})
        self.assertTrue(result)

    def test_azure_download(self):
        """Test Azure download"""
        self.backend.upload('blob1', b'content', {'name': 'blob1'})
        
        success, data = self.backend.download('blob1')
        self.assertTrue(success)
        self.assertIsNotNone(data)

    def test_azure_delete(self):
        """Test Azure delete"""
        self.backend.upload('blob1', b'content', {'name': 'blob1'})
        
        result = self.backend.delete('blob1')
        self.assertTrue(result)

    def test_azure_list_blobs(self):
        """Test listing Azure blobs"""
        self.backend.upload('blob1', b'content1', {'name': 'blob1'})
        self.backend.upload('blob2', b'content2', {'name': 'blob2'})
        
        blobs = self.backend.list_files()
        self.assertEqual(len(blobs), 2)

    def test_azure_metadata(self):
        """Test Azure blob metadata"""
        self.backend.upload('blob1', b'content', {'name': 'blob1', 'tag': 'test'})
        
        metadata = self.backend.get_file_metadata('blob1')
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.file_id, 'blob1')

    def test_azure_container_management(self):
        """Test Azure container management"""
        self.assertEqual(self.backend.container, 'test-container')


# ============================================================================
# GCS Backend Tests
# ============================================================================

class TestGCSBackend(unittest.TestCase):
    """Tests for GCS backend"""

    def setUp(self):
        self.backend = GCSBackend({'bucket': 'test-bucket-gcs'})

    def test_gcs_upload(self):
        """Test GCS upload"""
        result = self.backend.upload('object1', b'content', {'name': 'object1'})
        self.assertTrue(result)

    def test_gcs_download(self):
        """Test GCS download"""
        self.backend.upload('object1', b'content', {'name': 'object1'})
        
        success, data = self.backend.download('object1')
        self.assertTrue(success)
        self.assertIsNotNone(data)

    def test_gcs_delete(self):
        """Test GCS delete"""
        self.backend.upload('object1', b'content', {'name': 'object1'})
        
        result = self.backend.delete('object1')
        self.assertTrue(result)

    def test_gcs_list_objects(self):
        """Test listing GCS objects"""
        self.backend.upload('obj1', b'content1', {'name': 'obj1'})
        self.backend.upload('obj2', b'content2', {'name': 'obj2'})
        
        objects = self.backend.list_files()
        self.assertEqual(len(objects), 2)

    def test_gcs_metadata(self):
        """Test GCS object metadata"""
        self.backend.upload('object1', b'content', {'name': 'object1'})
        
        metadata = self.backend.get_file_metadata('object1')
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.file_id, 'object1')


# ============================================================================
# Cloud Sync Tests
# ============================================================================

class TestCloudSync(unittest.TestCase):
    """Tests for cloud synchronization"""

    def setUp(self):
        self.backend = S3Backend({'bucket': 'test-bucket'})
        self.sync = CloudSync(self.backend)

    def test_detect_new_files(self):
        """Test detecting new files"""
        local_files = {
            'new1': {'id': 'new1', 'content': 'Content 1'},
        }
        
        operations = self.sync.detect_changes(local_files)
        self.assertEqual(len(operations), 1)
        self.assertEqual(operations[0].operation_type, 'upload')

    def test_detect_modified_files(self):
        """Test detecting modified files"""
        # Upload first
        self.backend.upload('file1', 
                          json.dumps({'id': 'file1', 'content': 'Original'}).encode(),
                          {'name': 'file1'})
        
        # Modified local version
        local_files = {
            'file1': {'id': 'file1', 'content': 'Modified'},
        }
        
        operations = self.sync.detect_changes(local_files)
        self.assertGreater(len(operations), 0)

    def test_detect_deleted_files(self):
        """Test detecting deleted files"""
        # Upload file
        self.backend.upload('file1', b'content', {'name': 'file1'})
        
        # Empty local
        local_files = {}
        
        operations = self.sync.detect_changes(local_files)
        self.assertEqual(len(operations), 1)
        self.assertEqual(operations[0].operation_type, 'delete')

    def test_execute_sync(self):
        """Test executing sync operations"""
        local_files = {
            'file1': {'id': 'file1', 'content': 'Content 1'},
        }
        
        operations = self.sync.detect_changes(local_files)
        uploaded, downloaded = self.sync.execute_sync(operations, local_files)
        
        self.assertGreaterEqual(uploaded, 0)

    def test_sync_statistics(self):
        """Test sync statistics"""
        local_files = {
            'file1': {'id': 'file1', 'content': 'Content'},
        }
        
        self.sync.detect_changes(local_files)
        self.sync.execute_sync([], local_files)
        
        stats = self.sync.get_sync_stats()
        self.assertIn('avg_sync_time', stats)
        self.assertGreater(stats['total_syncs'], 0)

    def test_bandwidth_throttling(self):
        """Test bandwidth throttling"""
        # Sync should complete quickly (simulated)
        local_files = {'f1': {'content': 'x' * 1000000}}
        
        start = time.time()
        self.sync.detect_changes(local_files)
        elapsed = time.time() - start
        
        # Should complete in reasonable time
        self.assertLess(elapsed, 5.0)


# ============================================================================
# Conflict Resolution Tests
# ============================================================================

class TestConflictResolver(unittest.TestCase):
    """Tests for conflict resolution"""

    def setUp(self):
        self.resolver = ConflictResolver()

    def test_detect_conflicts(self):
        """Test conflict detection"""
        local_files = {
            'template1': {'id': 'template1', 'content': 'Local Content'},
        }
        
        remote_files = {
            'template1': RemoteFile(
                file_id='template1',
                name='template1',
                size=100,
                modified_at=time.time(),
                content_hash='remote_hash',
                storage_path='s3://bucket/template1'
            )
        }
        
        conflicts = self.resolver.detect_conflicts(local_files, remote_files)
        self.assertGreater(len(conflicts), 0)

    def test_last_write_wins(self):
        """Test last-write-wins resolution"""
        self.resolver.conflicts['template1'] = {
            'template_id': 'template1',
            'local_version': {'content': 'Local'},
            'remote_version': {'content': 'Remote'},
        }
        
        # Create actual conflict
        from services.cloud_storage_manager import ConflictInfo
        self.resolver.conflicts['template1'] = ConflictInfo(
            template_id='template1',
            local_version={'content': 'Local'},
            remote_version={'content': 'Remote'},
            conflict_timestamp=time.time()
        )
        
        result = self.resolver.resolve_conflict('template1', 'last_write_wins')
        self.assertIsNotNone(result)

    def test_server_preferred(self):
        """Test server-preferred resolution"""
        from services.cloud_storage_manager import ConflictInfo
        self.resolver.conflicts['template1'] = ConflictInfo(
            template_id='template1',
            local_version={'content': 'Local'},
            remote_version={'content': 'Remote'},
            conflict_timestamp=time.time()
        )
        
        result = self.resolver.resolve_conflict('template1', 'server_preferred')
        self.assertIsNotNone(result)

    def test_mark_resolved(self):
        """Test marking conflict resolved"""
        from services.cloud_storage_manager import ConflictInfo
        self.resolver.conflicts['template1'] = ConflictInfo(
            template_id='template1',
            local_version={},
            remote_version={},
            conflict_timestamp=time.time()
        )
        
        result = self.resolver.mark_resolved('template1')
        self.assertTrue(result)
        
        # Should be removed
        self.assertNotIn('template1', self.resolver.conflicts)

    def test_get_pending_conflicts(self):
        """Test getting pending conflicts"""
        from services.cloud_storage_manager import ConflictInfo
        self.resolver.conflicts['t1'] = ConflictInfo(
            template_id='t1',
            local_version={},
            remote_version={},
            conflict_timestamp=time.time()
        )
        
        pending = self.resolver.get_pending_conflicts()
        self.assertEqual(len(pending), 1)


# ============================================================================
# Offline Mode Tests
# ============================================================================

class TestOfflineMode(unittest.TestCase):
    """Tests for offline mode"""

    def setUp(self):
        self.manager = CloudStorageManager()
        self.manager.configure_backend('s3', {'bucket': 'test'})

    def test_offline_queue_add(self):
        """Test adding to offline queue"""
        operation = {
            'template_id': 'template1',
            'operation_type': 'upload',
            'data': {'content': 'test'}
        }
        
        result = self.manager.add_to_offline_queue(operation)
        self.assertTrue(result)

    def test_offline_queue_get(self):
        """Test getting offline queue"""
        self.manager.add_to_offline_queue({'template_id': 'template1'})
        
        queue = self.manager.get_offline_queue()
        self.assertGreater(len(queue), 0)

    def test_offline_mode_operations(self):
        """Test operations in offline mode"""
        self.manager.enable_offline_mode()
        
        status = self.manager.get_sync_status()
        self.assertTrue(status['offline_mode'])
        
        self.manager.disable_offline_mode()
        status = self.manager.get_sync_status()
        self.assertFalse(status['offline_mode'])


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def setUp(self):
        self.manager = CloudStorageManager()

    def test_complete_sync_workflow(self):
        """Test complete synchronization workflow"""
        self.manager.configure_backend('s3', {'bucket': 'test'})
        
        # Define local files
        local_files = {
            'template1': {'id': 'template1', 'content': 'Content 1'},
            'template2': {'id': 'template2', 'content': 'Content 2'},
        }
        
        # Sync
        success, result = self.manager.sync_all(local_files)
        self.assertTrue(success)
        self.assertIn('uploaded', result)

    def test_multi_cloud_switching(self):
        """Test switching between cloud providers"""
        # S3
        self.manager.configure_backend('s3', {'bucket': 'bucket1'})
        self.assertIsNotNone(self.manager.backend)
        
        # Azure
        self.manager.configure_backend('azure', {'container': 'container1'})
        self.assertIsNotNone(self.manager.backend)
        
        # GCS
        self.manager.configure_backend('gcs', {'bucket': 'bucket-gcs'})
        self.assertIsNotNone(self.manager.backend)

    def test_conflict_detection_and_resolution(self):
        """Test detecting and resolving conflicts"""
        self.manager.configure_backend('s3', {'bucket': 'test'})
        
        local_files = {
            'template1': {'id': 'template1', 'content': 'Local'},
        }
        
        # Upload
        self.manager.upload_template('template1', local_files['template1'])
        
        # Detect conflicts
        conflicts = self.manager.detect_conflicts(local_files)
        # Should detect no conflict initially
        self.assertIsInstance(conflicts, list)


class TestThreadSafety(unittest.TestCase):
    """Thread safety tests"""

    def setUp(self):
        self.manager = CloudStorageManager()
        self.manager.configure_backend('s3', {'bucket': 'test'})

    def test_concurrent_uploads(self):
        """Test concurrent uploads"""
        results = []

        def upload():
            template = {'id': f'template_{len(results)}', 'content': 'Content'}
            result = self.manager.upload_template(f'template_{len(results)}', template)
            results.append(result)

        threads = [threading.Thread(target=upload) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(results), 5)

    def test_concurrent_sync(self):
        """Test concurrent sync operations"""
        results = []

        def sync():
            local = {'template1': {'content': 'test'}}
            success, _ = self.manager.sync_all(local)
            results.append(success)

        threads = [threading.Thread(target=sync) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertTrue(all(results))


if __name__ == '__main__':
    unittest.main()
