"""
Tests for Collaboration Engine (Issue #55)

Comprehensive test suite with 43+ tests covering:
- Real-time synchronization and conflict resolution
- Version control integration
- Team and permission management
- Activity logging and comments
- Integration tests
"""

import unittest
import time
import threading
from services.collaboration_engine import (
    RealtimeSync, VersionControl, TeamManager, ActivityLog,
    CollaborationEngine, Change, User, Comment, Activity,
    PermissionType, ActivityType
)


# ============================================================================
# RealtimeSync Tests
# ============================================================================

class TestRealtimeSync(unittest.TestCase):
    """Tests for real-time synchronization"""

    def setUp(self):
        self.sync = RealtimeSync('template_1', conflict_strategy='merge')

    def test_apply_remote_change(self):
        """Test applying remote change"""
        change_data = {
            'user_id': 'user1',
            'operation': 'insert',
            'position': 0,
            'content': 'Hello'
        }
        result = self.sync.apply_remote_change(change_data)
        self.assertTrue(result)

    def test_apply_invalid_change(self):
        """Test applying invalid change"""
        change_data = {}  # Missing required fields
        result = self.sync.apply_remote_change(change_data)
        self.assertFalse(result)

    def test_get_local_changes(self):
        """Test getting local changes"""
        change = Change(
            change_id='change1',
            user_id='user1',
            operation='insert',
            position=0,
            content='text',
            timestamp=time.time(),
            version=0
        )
        self.sync.queue_change(change)
        changes = self.sync.get_local_changes()
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].change_id, 'change1')

    def test_sync_changes(self):
        """Test synchronizing changes"""
        remote_changes = [
            {
                'user_id': 'user2',
                'operation': 'insert',
                'position': 0,
                'content': 'Remote'
            }
        ]
        success, conflicts = self.sync.sync_changes(remote_changes)
        self.assertTrue(success)
        self.assertEqual(conflicts, 0)

    def test_sync_with_conflicts(self):
        """Test sync with conflicting changes"""
        # Queue local change
        local_change = Change(
            change_id='local1',
            user_id='user1',
            operation='insert',
            position=5,
            content='local',
            timestamp=time.time(),
            version=0
        )
        self.sync.queue_change(local_change)
        
        # Sync overlapping remote change
        remote_changes = [
            {
                'user_id': 'user2',
                'operation': 'insert',
                'position': 5,
                'content': 'remote'
            }
        ]
        success, conflicts = self.sync.sync_changes(remote_changes)
        self.assertTrue(success)
        self.assertGreater(conflicts, 0)

    def test_transform_change(self):
        """Test operational transformation"""
        change1 = Change('id1', 'user1', 'insert', 0, 'a', time.time(), 0)
        change2 = Change('id2', 'user2', 'insert', 5, 'b', time.time(), 0)
        
        transformed = self.sync.transform_change(change1, change2)
        self.assertIsNotNone(transformed)
        self.assertEqual(transformed.change_id, 'id2')

    def test_resolve_conflict_merge(self):
        """Test conflict resolution (merge)"""
        local = Change('id1', 'user1', 'insert', 0, 'local', time.time(), 0)
        remote = Change('id2', 'user2', 'insert', 0, 'remote', time.time(), 0)
        
        resolved = self.sync.resolve_conflict(local, remote, 'merge')
        self.assertIsNotNone(resolved)
        self.assertIn('local', resolved.content)
        self.assertIn('remote', resolved.content)

    def test_resolve_conflict_replace(self):
        """Test conflict resolution (replace)"""
        local = Change('id1', 'user1', 'insert', 0, 'local', time.time(), 0)
        remote = Change('id2', 'user2', 'insert', 0, 'remote', time.time(), 0)
        
        resolved = self.sync.resolve_conflict(local, remote, 'replace')
        self.assertEqual(resolved.change_id, 'id2')

    def test_set_user_presence(self):
        """Test setting user presence"""
        presence_data = {
            'username': 'user1',
            'cursor_position': [5, 10],
            'status': 'editing'
        }
        self.sync.set_user_presence('user1', presence_data)
        users = self.sync.get_active_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].user_id, 'user1')

    def test_get_active_users(self):
        """Test getting active users"""
        self.sync.set_user_presence('user1', {
            'username': 'user1',
            'cursor_position': [0, 0]
        })
        self.sync.set_user_presence('user2', {
            'username': 'user2',
            'cursor_position': [10, 5]
        })
        
        users = self.sync.get_active_users()
        self.assertEqual(len(users), 2)

    def test_queue_and_flush_changes(self):
        """Test queueing and flushing changes"""
        change = Change(
            change_id='change1',
            user_id='user1',
            operation='insert',
            position=0,
            content='text',
            timestamp=time.time(),
            version=0
        )
        self.sync.queue_change(change)
        
        pending = self.sync.get_pending_changes()
        self.assertEqual(len(pending), 1)
        
        flushed = self.sync.flush_changes()
        self.assertEqual(len(flushed), 1)
        
        pending = self.sync.get_pending_changes()
        self.assertEqual(len(pending), 0)

    def test_get_sync_stats(self):
        """Test getting sync statistics"""
        self.sync.set_user_presence('user1', {'username': 'user1'})
        stats = self.sync.get_sync_stats()
        
        self.assertIsNotNone(stats)
        self.assertGreaterEqual(stats.active_users, 1)
        self.assertEqual(stats.total_conflicts, 0)


# ============================================================================
# VersionControl Tests
# ============================================================================

class TestVersionControl(unittest.TestCase):
    """Tests for version control"""

    def setUp(self):
        self.vc = VersionControl('/repo')

    def test_create_commit(self):
        """Test creating a commit"""
        commit_hash = self.vc.create_commit(
            message='Initial commit',
            files=['template.html'],
            author_name='Test User',
            author_email='test@example.com'
        )
        self.assertIsNotNone(commit_hash)
        self.assertEqual(len(commit_hash), 12)

    def test_get_commit_history(self):
        """Test getting commit history"""
        self.vc.create_commit('commit1', ['file1.html'], 'User1', 'user1@test.com')
        self.vc.create_commit('commit2', ['file2.html'], 'User2', 'user2@test.com')
        
        history = self.vc.get_commit_history()
        self.assertEqual(len(history), 2)

    def test_get_commit_details(self):
        """Test getting commit details"""
        commit_hash = self.vc.create_commit(
            'commit',
            ['file.html'],
            'User',
            'user@test.com'
        )
        
        commit = self.vc.get_commit_details(commit_hash)
        self.assertIsNotNone(commit)
        self.assertEqual(commit.message, 'commit')

    def test_create_branch(self):
        """Test creating branch"""
        result = self.vc.create_branch('feature/test')
        self.assertTrue(result)

    def test_switch_branch(self):
        """Test switching branch"""
        self.vc.create_branch('develop')
        result = self.vc.switch_branch('develop')
        self.assertTrue(result)

    def test_merge_branch(self):
        """Test merging branches"""
        success, conflicts = self.vc.merge_branch('develop', 'main')
        self.assertTrue(success)
        self.assertIsInstance(conflicts, list)

    def test_get_current_branch(self):
        """Test getting current branch"""
        branch = self.vc.get_current_branch()
        self.assertIsNotNone(branch)
        self.assertIn(branch, ['main', 'develop', 'master'])

    def test_list_branches(self):
        """Test listing branches"""
        branches = self.vc.list_branches()
        self.assertIsInstance(branches, list)
        self.assertGreater(len(branches), 0)

    def test_revert_to_commit(self):
        """Test reverting to commit"""
        commit_hash = self.vc.create_commit(
            'to revert',
            ['file.html'],
            'User',
            'user@test.com'
        )
        result = self.vc.revert_to_commit(commit_hash)
        self.assertTrue(result)

    def test_get_diff(self):
        """Test getting diff"""
        hash1 = self.vc.create_commit('commit1', ['f1.html'], 'U', 'u@test.com')
        hash2 = self.vc.create_commit('commit2', ['f2.html'], 'U', 'u@test.com')
        
        diff = self.vc.get_diff(hash1, hash2)
        self.assertIsNotNone(diff)
        self.assertIn(hash1, diff)
        self.assertIn(hash2, diff)

    def test_get_commit_stats(self):
        """Test getting commit statistics"""
        self.vc.create_commit('c1', ['f1.html'], 'U', 'u@test.com')
        self.vc.create_commit('c2', ['f2.html'], 'U', 'u@test.com')
        
        stats = self.vc.get_commit_stats()
        self.assertEqual(stats['total_commits'], 2)
        self.assertGreater(stats['total_insertions'], 0)


# ============================================================================
# TeamManager Tests
# ============================================================================

class TestTeamManager(unittest.TestCase):
    """Tests for team management"""

    def setUp(self):
        self.team = TeamManager()

    def test_add_user(self):
        """Test adding user"""
        result = self.team.add_user('user1', 'User One', 'user1@test.com')
        self.assertTrue(result)

    def test_add_duplicate_user(self):
        """Test adding duplicate user"""
        self.team.add_user('user1', 'User One', 'user1@test.com')
        result = self.team.add_user('user1', 'Another', 'another@test.com')
        self.assertFalse(result)

    def test_get_user(self):
        """Test getting user"""
        self.team.add_user('user1', 'User One', 'user1@test.com')
        user = self.team.get_user('user1')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'User One')

    def test_list_users(self):
        """Test listing users"""
        self.team.add_user('user1', 'User One', 'user1@test.com')
        self.team.add_user('user2', 'User Two', 'user2@test.com')
        
        users = self.team.list_users()
        self.assertEqual(len(users), 2)

    def test_remove_user(self):
        """Test removing user"""
        self.team.add_user('user1', 'User One', 'user1@test.com')
        result = self.team.remove_user('user1')
        self.assertTrue(result)
        
        user = self.team.get_user('user1')
        self.assertIsNone(user)

    def test_update_user_role(self):
        """Test updating user role"""
        self.team.add_user('user1', 'User One', 'user1@test.com', 'editor')
        result = self.team.update_user_role('user1', 'admin')
        self.assertTrue(result)
        
        user = self.team.get_user('user1')
        self.assertEqual(user.role, 'admin')

    def test_can_edit(self):
        """Test edit permission check"""
        self.team.add_user('user1', 'User One', 'user1@test.com', 'admin')
        result = self.team.can_edit('user1', 'template1')
        self.assertTrue(result)

    def test_cannot_edit_without_permission(self):
        """Test cannot edit without permission"""
        self.team.add_user('user1', 'User One', 'user1@test.com', 'viewer')
        result = self.team.can_edit('user1', 'template1')
        self.assertFalse(result)

    def test_can_view(self):
        """Test view permission check"""
        self.team.add_user('user1', 'User One', 'user1@test.com', 'editor')
        self.team.grant_access('user1', 'template1', 'view')
        result = self.team.can_view('user1', 'template1')
        self.assertTrue(result)

    def test_grant_access(self):
        """Test granting access"""
        self.team.add_user('user1', 'User One', 'user1@test.com')
        result = self.team.grant_access('user1', 'template1', 'edit')
        self.assertTrue(result)

    def test_revoke_access(self):
        """Test revoking access"""
        self.team.add_user('user1', 'User One', 'user1@test.com')
        self.team.grant_access('user1', 'template1', 'edit')
        result = self.team.revoke_access('user1', 'template1')
        self.assertTrue(result)

    def test_get_team_stats(self):
        """Test getting team statistics"""
        self.team.add_user('user1', 'User One', 'user1@test.com')
        self.team.grant_access('user1', 'template1', 'view')
        
        stats = self.team.get_team_stats()
        self.assertEqual(stats.total_users, 1)
        self.assertGreaterEqual(stats.total_templates, 1)


# ============================================================================
# ActivityLog Tests
# ============================================================================

class TestActivityLog(unittest.TestCase):
    """Tests for activity logging"""

    def setUp(self):
        self.log = ActivityLog()

    def test_log_change(self):
        """Test logging change"""
        activity_id = self.log.log_change(
            'user1',
            'template1',
            'edit',
            {'old': 'value1', 'new': 'value2'}
        )
        self.assertIsNotNone(activity_id)

    def test_get_template_activity(self):
        """Test getting template activity"""
        self.log.log_change('user1', 'template1', 'edit', {})
        self.log.log_change('user2', 'template1', 'comment', {})
        
        activity = self.log.get_template_activity('template1')
        self.assertEqual(len(activity), 2)

    def test_get_user_activity(self):
        """Test getting user activity"""
        self.log.log_change('user1', 'template1', 'edit', {})
        self.log.log_change('user1', 'template2', 'edit', {})
        
        activity = self.log.get_user_activity('user1')
        self.assertEqual(len(activity), 2)

    def test_add_comment(self):
        """Test adding comment"""
        comment_id = self.log.add_comment('user1', 'template1', 'Great work!')
        self.assertIsNotNone(comment_id)

    def test_add_comment_with_position(self):
        """Test adding positioned comment"""
        comment_id = self.log.add_comment(
            'user1',
            'template1',
            'Fix this line',
            position=(5, 10)
        )
        comments = self.log.get_comments('template1')
        self.assertEqual(comments[0].position, (5, 10))

    def test_get_comments(self):
        """Test getting comments"""
        self.log.add_comment('user1', 'template1', 'Comment 1')
        self.log.add_comment('user2', 'template1', 'Comment 2')
        
        comments = self.log.get_comments('template1')
        self.assertEqual(len(comments), 2)

    def test_resolve_comment(self):
        """Test resolving comment"""
        comment_id = self.log.add_comment('user1', 'template1', 'Fix needed')
        result = self.log.resolve_comment(comment_id)
        self.assertTrue(result)
        
        comments = self.log.get_comments('template1')
        self.assertTrue(comments[0].resolved)

    def test_create_notification(self):
        """Test creating notification"""
        result = self.log.create_notification(
            'user1',
            'edit',
            {'actor_id': 'user2', 'template_id': 'template1'}
        )
        self.assertTrue(result)

    def test_get_notifications(self):
        """Test getting notifications"""
        self.log.create_notification('user1', 'edit', {'actor_id': 'user2'})
        self.log.create_notification('user1', 'comment', {'actor_id': 'user3'})
        
        notifs = self.log.get_notifications('user1')
        self.assertEqual(len(notifs), 2)

    def test_mark_notification_read(self):
        """Test marking notification read"""
        self.log.create_notification('user1', 'edit', {'actor_id': 'user2'})
        notifs = self.log.get_notifications('user1')
        
        result = self.log.mark_notification_read(notifs[0].notification_id)
        self.assertTrue(result)
        
        notifs = self.log.get_notifications('user1')
        self.assertTrue(notifs[0].read)


# ============================================================================
# CollaborationEngine Integration Tests
# ============================================================================

class TestCollaborationEngine(unittest.TestCase):
    """Integration tests for collaboration engine"""

    def setUp(self):
        self.engine = CollaborationEngine('template1', 'user1')

    def test_apply_change(self):
        """Test applying change"""
        change_data = {
            'user_id': 'user1',
            'operation': 'insert',
            'position': 0,
            'content': 'New content'
        }
        result = self.engine.apply_change(change_data)
        self.assertTrue(result)

    def test_sync_with_peers(self):
        """Test sync with peers"""
        success, changes = self.engine.sync_with_peers()
        self.assertTrue(success)
        self.assertIsInstance(changes, list)

    def test_get_active_collaborators(self):
        """Test getting active collaborators"""
        self.engine.realtime_sync.set_user_presence(
            'user1',
            {'username': 'User One', 'cursor_position': [0, 0]}
        )
        collaborators = self.engine.get_active_collaborators()
        self.assertGreater(len(collaborators), 0)

    def test_commit_changes(self):
        """Test committing changes"""
        commit_hash = self.engine.commit_changes('Updated template')
        self.assertIsNotNone(commit_hash)

    def test_get_history(self):
        """Test getting history"""
        self.engine.commit_changes('commit1')
        self.engine.commit_changes('commit2')
        
        history = self.engine.get_history()
        self.assertEqual(len(history), 2)

    def test_share_template(self):
        """Test sharing template"""
        self.engine.team_manager.add_user('user2', 'User Two', 'user2@test.com')
        result = self.engine.share_template('user2', 'view')
        self.assertTrue(result)

    def test_get_collaborators(self):
        """Test getting collaborators"""
        self.engine.team_manager.add_user('user2', 'User Two', 'user2@test.com')
        self.engine.share_template('user2')
        
        collaborators = self.engine.get_collaborators()
        self.assertEqual(len(collaborators), 1)

    def test_add_comment(self):
        """Test adding comment"""
        comment_id = self.engine.add_comment('Great template!')
        self.assertIsNotNone(comment_id)

    def test_get_comments(self):
        """Test getting comments"""
        self.engine.add_comment('Comment 1')
        self.engine.add_comment('Comment 2')
        
        comments = self.engine.get_comments()
        self.assertEqual(len(comments), 2)

    def test_resolve_comment(self):
        """Test resolving comment"""
        comment_id = self.engine.add_comment('Fix needed')
        result = self.engine.resolve_comment(comment_id)
        self.assertTrue(result)

    def test_set_collaborator_permission(self):
        """Test setting collaborator permission"""
        self.engine.team_manager.add_user('user2', 'User Two', 'user2@test.com')
        result = self.engine.set_collaborator_permission('user2', 'edit')
        self.assertTrue(result)

    def test_get_collaboration_stats(self):
        """Test getting collaboration stats"""
        stats = self.engine.get_collaboration_stats()
        self.assertIn('sync_stats', stats)
        self.assertIn('team_stats', stats)
        self.assertIn('commit_stats', stats)

    def test_get_sync_status(self):
        """Test getting sync status"""
        status = self.engine.get_sync_status()
        self.assertIn('total_changes', status)
        self.assertIn('pending_changes', status)
        self.assertIn('active_users', status)


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration(unittest.TestCase):
    """Full integration tests"""

    def test_complete_collaboration_workflow(self):
        """Test complete collaboration workflow"""
        # Initialize
        engine = CollaborationEngine('template1', 'user1')
        engine.team_manager.add_user('user2', 'User Two', 'user2@test.com')
        
        # Apply changes
        engine.apply_change({
            'user_id': 'user1',
            'operation': 'insert',
            'position': 0,
            'content': 'Template content'
        })
        
        # Share template
        engine.share_template('user2', 'edit')
        
        # Add comment
        comment_id = engine.add_comment('Good start')
        
        # Commit
        commit_hash = engine.commit_changes('Initial version')
        
        # Verify
        self.assertIsNotNone(commit_hash)
        comments = engine.get_comments()
        self.assertEqual(len(comments), 1)
        
        history = engine.get_history()
        self.assertEqual(len(history), 1)

    def test_multi_user_synchronization(self):
        """Test multi-user synchronization"""
        engine = CollaborationEngine('template1', 'user1')
        
        # Simulate multiple users
        engine.realtime_sync.set_user_presence('user1', {
            'username': 'User One',
            'cursor_position': [0, 0]
        })
        engine.realtime_sync.set_user_presence('user2', {
            'username': 'User Two',
            'cursor_position': [5, 10]
        })
        
        # Get active collaborators
        collaborators = engine.get_active_collaborators()
        self.assertEqual(len(collaborators), 2)
        
        # Verify stats
        stats = engine.get_sync_status()
        self.assertEqual(stats['active_users'], 2)


class TestThreadSafety(unittest.TestCase):
    """Tests for thread safety"""

    def test_concurrent_changes(self):
        """Test concurrent change application"""
        engine = CollaborationEngine('template1', 'user1')
        results = []

        def apply_changes(user_id):
            for i in range(10):
                result = engine.apply_change({
                    'user_id': user_id,
                    'operation': 'insert',
                    'position': i,
                    'content': f'content_{i}'
                })
                results.append(result)

        threads = [
            threading.Thread(target=apply_changes, args=('user1',)),
            threading.Thread(target=apply_changes, args=('user2',))
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(results), 20)
        self.assertTrue(all(results))

    def test_concurrent_comments(self):
        """Test concurrent comment addition"""
        log = ActivityLog()
        results = []

        def add_comments(user_id):
            for i in range(10):
                result = log.add_comment(user_id, 'template1', f'Comment {i}')
                results.append(result is not None)

        threads = [
            threading.Thread(target=add_comments, args=('user1',)),
            threading.Thread(target=add_comments, args=('user2',))
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(results), 20)
        self.assertTrue(all(results))
        
        comments = log.get_comments('template1')
        self.assertEqual(len(comments), 20)


if __name__ == '__main__':
    unittest.main()
