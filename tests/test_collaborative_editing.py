"""
Unit Tests for Collaborative Editing Module

Tests all components of the collaborative editing system:
- Real-time session management
- Change tracking and history
- Commenting and discussions
- Version control and branching
- Change synchronization

Test Classes:
    TestCollaborativeSession: Session management
    TestChangeTracking: Change history
    TestCommentingSystem: Comments and threads
    TestVersionControl: Branching and merging
    TestCollaborativeSync: Real-time synchronization
"""

import unittest
from datetime import datetime
from services.collaborative_editing import (
    User, Change, ChangeType, Comment, CommentThread,
    CollaborativeSession, Branch, MergeRequest,
    ChangeTrackingEngine, CommentingSystem, VersionControlManager,
    CollaborativeEditingManager, SyncCoordinator
)


class TestCollaborativeSession(unittest.TestCase):
    """Test collaborative session management."""
    
    def setUp(self):
        self.manager = CollaborativeEditingManager()
        self.session = self.manager.create_session("template_1")

    def test_create_session(self):
        """Test creating a collaboration session."""
        self.assertIsNotNone(self.session.id)
        self.assertEqual(self.session.template_id, "template_1")
        self.assertTrue(self.session.active)

    def test_add_user_to_session(self):
        """Test adding user to session."""
        user = User(name="Alice", email="alice@example.com")
        success, msg = self.manager.add_user_to_session(self.session.id, user)
        self.assertTrue(success)
        self.assertIn(user.id, self.session.users)

    def test_remove_user_from_session(self):
        """Test removing user from session."""
        user = User(name="Bob", email="bob@example.com")
        self.manager.add_user_to_session(self.session.id, user)
        success, msg = self.manager.remove_user_from_session(self.session.id, user.id)
        self.assertTrue(success)
        self.assertNotIn(user.id, self.session.users)

    def test_session_state_management(self):
        """Test session state."""
        user1 = User(name="User1")
        user2 = User(name="User2")
        self.manager.add_user_to_session(self.session.id, user1)
        self.manager.add_user_to_session(self.session.id, user2)
        
        self.assertEqual(len(self.session.users), 2)
        success, msg = self.manager.end_session(self.session.id)
        self.assertTrue(success)
        self.assertFalse(self.session.active)


class TestChangeTracking(unittest.TestCase):
    """Test change tracking and history."""
    
    def setUp(self):
        self.engine = ChangeTrackingEngine("template_1")

    def test_record_change(self):
        """Test recording a change."""
        change = self.engine.record_change(
            "user1", ChangeType.INSERT, "css.body",
            old_value="", new_value=".container { }"
        )
        self.assertIsNotNone(change.id)
        self.assertEqual(change.operation, ChangeType.INSERT)
        self.assertEqual(len(self.engine.changes), 1)

    def test_get_change_history(self):
        """Test retrieving change history."""
        for i in range(3):
            self.engine.record_change(f"user{i}", ChangeType.INSERT, f"path_{i}", None, f"value_{i}")
        
        history = self.engine.get_change_history()
        self.assertEqual(len(history), 3)

    def test_generate_diff(self):
        """Test generating diffs between versions."""
        self.engine.record_change("user1", ChangeType.INSERT, "css", None, "body { }")
        v1 = self.engine.current_version
        self.engine.record_change("user2", ChangeType.MODIFY, "css", "body { }", "body { color: blue; }")
        v2 = self.engine.current_version
        
        diff = self.engine.generate_diff(0, v2)
        self.assertIn("changes", diff)
        self.assertEqual(diff["from_version"], 0)
        self.assertEqual(diff["to_version"], v2)
        self.assertEqual(len(diff["changes"]), 2)

    def test_revert_to_version(self):
        """Test reverting to a previous version."""
        self.engine.record_change("user1", ChangeType.INSERT, "html", None, "<p>Test</p>")
        v1 = self.engine.current_version
        self.engine.record_change("user2", ChangeType.DELETE, "html", "<p>Test</p>", None)
        
        success, msg = self.engine.revert_to_version(v1)
        self.assertTrue(success)
        self.assertGreater(self.engine.current_version, v1)

    def test_get_change_summary(self):
        """Test getting change summary."""
        self.engine.record_change("user1", ChangeType.INSERT, "path1", None, "value1")
        self.engine.record_change("user2", ChangeType.INSERT, "path2", None, "value2")
        self.engine.record_change("user1", ChangeType.MODIFY, "path1", "value1", "value1_modified")
        
        summary = self.engine.get_change_summary()
        self.assertEqual(summary["total_changes"], 3)
        self.assertEqual(summary["by_user"]["user1"], 2)
        self.assertEqual(summary["by_user"]["user2"], 1)


class TestCommentingSystem(unittest.TestCase):
    """Test commenting and discussions."""
    
    def setUp(self):
        self.system = CommentingSystem()

    def test_create_comment(self):
        """Test creating a comment."""
        comment = self.system.create_comment(
            "user1", "template_1", "css.body", "This needs styling"
        )
        self.assertIsNotNone(comment.id)
        self.assertEqual(comment.content, "This needs styling")
        self.assertFalse(comment.resolved)

    def test_create_comment_thread(self):
        """Test creating a comment thread."""
        comment1 = self.system.create_comment("user1", "template_1", "css", "First comment")
        comment2 = self.system.create_comment("user2", "template_1", "css", "Second comment")
        
        thread = self.system.get_thread("template_1", "css")
        self.assertIsNotNone(thread)
        self.assertEqual(len(thread.comments), 2)

    def test_add_reply(self):
        """Test adding reply to comment."""
        comment = self.system.create_comment("user1", "template_1", "css", "Main comment")
        reply = self.system.add_reply(comment.id, "user2", "I agree")
        
        self.assertIsNotNone(reply)
        self.assertEqual(len(comment.replies), 1)
        self.assertEqual(comment.replies[0].content, "I agree")

    def test_resolve_comment(self):
        """Test resolving a comment."""
        comment = self.system.create_comment("user1", "template_1", "css", "Fix this")
        success, msg = self.system.resolve_comment(comment.id, "user2")
        
        self.assertTrue(success)
        resolved_comment = self.system.comments_by_id[comment.id]
        self.assertTrue(resolved_comment.resolved)
        self.assertEqual(resolved_comment.resolved_by, "user2")

    def test_mention_user_in_comment(self):
        """Test mentioning users in comments."""
        comment = self.system.create_comment(
            "user1", "template_1", "css", "Hey @user2 check this",
            mentions=["user2"]
        )
        self.assertIn("user2", comment.mentions)

    def test_get_unresolved_comments(self):
        """Test getting unresolved comments."""
        self.system.create_comment("user1", "template_1", "css", "Comment 1")
        comment2 = self.system.create_comment("user2", "template_1", "html", "Comment 2")
        self.system.resolve_comment(comment2.id, "user1")
        
        unresolved = self.system.get_unresolved_comments("template_1")
        self.assertEqual(len(unresolved), 1)


class TestVersionControl(unittest.TestCase):
    """Test version control features."""
    
    def setUp(self):
        self.vc = VersionControlManager("template_1")

    def test_create_branch(self):
        """Test creating a branch."""
        success, msg = self.vc.create_branch("feature/new-style", 0, "user1")
        self.assertTrue(success)
        self.assertIn("feature/new-style", self.vc.get_all_branches())

    def test_add_change_to_branch(self):
        """Test adding changes to a branch."""
        self.vc.create_branch("dev", 0, "user1")
        change = Change(user_id="user1", operation=ChangeType.INSERT, path="css", new_value=".new { }")
        
        success, msg = self.vc.add_change_to_branch("dev", change)
        self.assertTrue(success)
        self.assertEqual(len(self.vc.branches["dev"].changes), 1)

    def test_create_merge_request(self):
        """Test creating merge request."""
        self.vc.create_branch("feature", 0, "user1")
        success, msg = self.vc.create_merge_request("feature", "main", "user1", "Add new styles")
        
        self.assertTrue(success)
        self.assertEqual(len(self.vc.merge_requests), 1)

    def test_detect_conflicts(self):
        """Test conflict detection."""
        self.vc.create_branch("dev1", 0, "user1")
        self.vc.create_branch("dev2", 0, "user2")
        
        # Add conflicting changes to same path
        change1 = Change(user_id="user1", operation=ChangeType.MODIFY, path="css",
                        old_value="old", new_value="dev1_value")
        change2 = Change(user_id="user2", operation=ChangeType.MODIFY, path="css",
                        old_value="old", new_value="dev2_value")
        
        self.vc.add_change_to_branch("dev1", change1)
        self.vc.add_change_to_branch("dev2", change2)
        
        conflicts = self.vc.detect_conflicts("dev1", "dev2")
        self.assertGreater(len(conflicts), 0)

    def test_merge_branches_no_conflict(self):
        """Test merging branches without conflicts."""
        self.vc.create_branch("feature", 0, "user1")
        
        # Add non-conflicting changes
        change1 = Change(user_id="user1", operation=ChangeType.INSERT, path="css1", new_value="value1")
        change2 = Change(user_id="user1", operation=ChangeType.INSERT, path="css2", new_value="value2")
        
        self.vc.add_change_to_branch("feature", change1)
        self.vc.add_change_to_branch("feature", change2)
        
        success, mr_msg = self.vc.create_merge_request("feature", "main", "user1")
        self.assertTrue(success)
        
        # Get the created merge request ID
        mr_id = list(self.vc.merge_requests.keys())[0]
        mr_success, mr_msg = self.vc.merge_branches(mr_id)
        
        self.assertTrue(mr_success)
        self.assertEqual(self.vc.merge_requests[mr_id].status, "merged")


class TestCollaborativeSync(unittest.TestCase):
    """Test collaborative synchronization."""
    
    def setUp(self):
        self.manager = CollaborativeEditingManager()
        self.session = self.manager.create_session("template_1")
        self.user = User(name="Alice", email="alice@test.com")
        self.manager.add_user_to_session(self.session.id, self.user)

    def test_broadcast_change_to_users(self):
        """Test broadcasting changes to users."""
        change = Change(user_id=self.user.id, operation=ChangeType.INSERT,
                       path="css", new_value=".new { }")
        success, msg = self.manager.apply_change(self.session.id, change)
        
        self.assertTrue(success)
        self.assertEqual(len(self.session.changes), 1)

    def test_update_cursor_position(self):
        """Test updating user cursor positions."""
        self.manager.update_cursor_position(self.user.id, 10, 5)
        
        cursors = self.manager.get_active_cursors()
        self.assertIn(self.user.id, cursors)
        self.assertEqual(cursors[self.user.id]["line"], 10)
        self.assertEqual(cursors[self.user.id]["column"], 5)

    def test_presence_awareness(self):
        """Test presence awareness."""
        user1 = User(name="User1")
        user2 = User(name="User2")
        
        self.manager.add_user_to_session(self.session.id, user1)
        self.manager.add_user_to_session(self.session.id, user2)
        
        self.assertEqual(len(self.session.users), 3)  # Alice + User1 + User2

    def test_offline_change_queue(self):
        """Test queueing changes when offline."""
        change1 = Change(user_id=self.user.id, operation=ChangeType.INSERT, path="css")
        change2 = Change(user_id=self.user.id, operation=ChangeType.MODIFY, path="html")
        
        self.manager.queue_offline_change(self.session.id, change1)
        self.manager.queue_offline_change(self.session.id, change2)
        
        success, count = self.manager.sync_offline_changes(self.session.id)
        self.assertTrue(success)
        self.assertEqual(count, 2)


class TestSyncCoordinator(unittest.TestCase):
    """Test synchronization coordination."""
    
    def setUp(self):
        self.coordinator = SyncCoordinator()

    def test_initialize_template(self):
        """Test initializing template collaboration."""
        self.coordinator.initialize_template("template_1")
        self.assertIn("template_1", self.coordinator.tracking_engines)
        self.assertIn("template_1", self.coordinator.version_control)

    def test_create_collaboration_session(self):
        """Test creating collaboration session."""
        user = User(name="Bob", email="bob@test.com")
        session = self.coordinator.create_collaboration_session("template_1", user)
        
        self.assertIsNotNone(session.id)
        self.assertEqual(session.template_id, "template_1")
        self.assertIn(user.id, session.users)

    def test_record_change_in_coordinator(self):
        """Test recording change through coordinator."""
        change = self.coordinator.record_change(
            "template_1", "user1", ChangeType.INSERT, "css", None, "body { }"
        )
        self.assertIsNotNone(change.id)

    def test_add_comment_in_coordinator(self):
        """Test adding comment through coordinator."""
        comment = self.coordinator.add_comment(
            "template_1", "user1", "css", "Needs improvement"
        )
        self.assertIsNotNone(comment.id)

    def test_get_template_summary(self):
        """Test getting template collaboration summary."""
        user = User(name="Developer")
        self.coordinator.create_collaboration_session("template_1", user)
        self.coordinator.record_change("template_1", "user1", ChangeType.INSERT, "css", None, "style")
        self.coordinator.add_comment("template_1", "user1", "html", "Comment")
        
        summary = self.coordinator.get_template_summary("template_1")
        self.assertIn("changes", summary)
        self.assertIn("threads", summary)
        self.assertGreater(summary["threads"], 0)


if __name__ == "__main__":
    unittest.main()
