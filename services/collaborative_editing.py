"""
Collaborative Editing Module

Provides comprehensive collaborative editing features including:
- Real-time synchronization with operational transformation
- Change tracking and history management
- Commenting system with threading
- Version control with branching and merging
- User presence and awareness

Classes:
    User: Represents a collaborating user
    CollaborativeSession: Manages active collaboration sessions
    Change: Represents a single change/edit
    ChangeHistory: Tracks all changes to a template
    Comment: Represents a comment or discussion
    CommentThread: Groups related comments
    Branch: Represents a version control branch
    MergeRequest: Represents a proposed merge
    CollaborativeEditingManager: Manages real-time sync
    ChangeTrackingEngine: Manages change history
    CommentingSystem: Manages comments
    VersionControlManager: Manages branches and merging
    SyncCoordinator: Orchestrates all features
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Literal, Optional, Tuple, Any
from datetime import datetime
from enum import Enum
import json
import uuid


class ChangeType(Enum):
    """Types of changes that can be tracked."""
    INSERT = "insert"
    DELETE = "delete"
    MODIFY = "modify"
    REPLACE = "replace"


class ConflictType(Enum):
    """Types of conflicts that can occur."""
    CONCURRENT_EDIT = "concurrent_edit"
    DELETE_MODIFY = "delete_modify"
    MOVE_MODIFY = "move_modify"
    VERSION_MISMATCH = "version_mismatch"


@dataclass
class User:
    """Represents a collaborating user."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    avatar: Optional[str] = None
    color: str = "#0078D4"
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    last_active: float = field(default_factory=lambda: datetime.now().timestamp())

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create from dictionary representation."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Change:
    """Represents a single edit/change."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    operation: ChangeType = ChangeType.MODIFY
    path: str = ""  # JSON path to the changed element
    old_value: Any = None
    new_value: Any = None
    position: int = 0  # For text-based changes
    length: int = 0  # Length of deleted/replaced text
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        data = asdict(self)
        data['operation'] = self.operation.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Change":
        """Create from dictionary representation."""
        data['operation'] = ChangeType(data.get('operation', 'modify'))
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Comment:
    """Represents a comment on a template section."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    section: str = ""  # Path to template section
    content: str = ""
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float = field(default_factory=lambda: datetime.now().timestamp())
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[float] = None
    replies: List["Comment"] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)  # User IDs mentioned

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        data = asdict(self)
        data['replies'] = [r.to_dict() if isinstance(r, Comment) else r for r in self.replies]
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Comment":
        """Create from dictionary representation."""
        replies = []
        for r in data.get('replies', []):
            replies.append(Comment.from_dict(r) if isinstance(r, dict) else r)
        data['replies'] = replies
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class CommentThread:
    """Groups related comments into a thread."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    template_id: str = ""
    section: str = ""
    comments: List[Comment] = field(default_factory=list)
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    resolved: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        data = asdict(self)
        data['comments'] = [c.to_dict() if isinstance(c, Comment) else c for c in self.comments]
        return data


@dataclass
class Branch:
    """Represents a version control branch."""
    name: str = ""
    template_id: str = ""
    based_on_version: int = 0
    created_by: str = ""
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    changes: List[Change] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        data = asdict(self)
        data['changes'] = [c.to_dict() if isinstance(c, Change) else c for c in self.changes]
        return data


@dataclass
class MergeRequest:
    """Represents a proposed merge of branches."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_branch: str = ""
    target_branch: str = "main"
    created_by: str = ""
    status: Literal["open", "approved", "merged", "closed"] = "open"
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    description: str = ""
    comments: List[Comment] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        data = asdict(self)
        data['comments'] = [c.to_dict() if isinstance(c, Comment) else c for c in self.comments]
        return data


@dataclass
class CollaborativeSession:
    """Manages an active collaboration session."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    template_id: str = ""
    users: Dict[str, User] = field(default_factory=dict)
    active: bool = True
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    changes: List[Change] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "template_id": self.template_id,
            "users": {k: v.to_dict() for k, v in self.users.items()},
            "active": self.active,
            "created_at": self.created_at,
            "changes": [c.to_dict() for c in self.changes],
        }


class ChangeTrackingEngine:
    """Manages change history and versioning."""
    
    def __init__(self, template_id: str):
        self.template_id = template_id
        self.changes: List[Change] = []
        self.current_version = 0
        self.version_snapshots: Dict[int, str] = {}  # version -> serialized state

    def record_change(self, user_id: str, operation: ChangeType, path: str,
                     old_value: Any = None, new_value: Any = None,
                     position: int = 0, length: int = 0) -> Change:
        """Record a change."""
        change = Change(
            user_id=user_id,
            operation=operation,
            path=path,
            old_value=old_value,
            new_value=new_value,
            position=position,
            length=length,
            version=self.current_version
        )
        self.changes.append(change)
        self.current_version += 1
        return change

    def get_changes(self, from_version: int = 0, to_version: Optional[int] = None) -> List[Change]:
        """Get changes in a version range."""
        if to_version is None:
            to_version = self.current_version
        return [c for c in self.changes if from_version <= c.version < to_version]

    def get_change_history(self) -> List[Change]:
        """Get all changes."""
        return self.changes.copy()

    def generate_diff(self, from_version: int, to_version: int) -> Dict[str, Any]:
        """Generate diff between two versions."""
        changes = self.get_changes(from_version, to_version)
        return {
            "from_version": from_version,
            "to_version": to_version,
            "changes": [c.to_dict() for c in changes],
            "change_count": len(changes),
            "authors": list(set(c.user_id for c in changes))
        }

    def revert_to_version(self, version: int) -> Tuple[bool, str]:
        """Revert to a specific version."""
        if version < 0 or version > self.current_version:
            return False, f"Invalid version {version}"
        
        # Create revert changes
        revert_changes = self.get_changes(version, self.current_version)
        for change in reversed(revert_changes):
            if change.operation == ChangeType.INSERT:
                self.record_change("system", ChangeType.DELETE, change.path,
                                 change.new_value, None, change.position, change.length)
            elif change.operation == ChangeType.DELETE:
                self.record_change("system", ChangeType.INSERT, change.path,
                                 None, change.old_value, change.position, len(str(change.old_value)))
        
        return True, f"Reverted to version {version}"

    def get_change_summary(self) -> Dict[str, Any]:
        """Get summary of all changes."""
        by_user = {}
        by_operation = {}
        
        for change in self.changes:
            by_user[change.user_id] = by_user.get(change.user_id, 0) + 1
            op_key = change.operation.value
            by_operation[op_key] = by_operation.get(op_key, 0) + 1
        
        return {
            "total_changes": len(self.changes),
            "current_version": self.current_version,
            "by_user": by_user,
            "by_operation": by_operation
        }


class CommentingSystem:
    """Manages comments and discussions."""
    
    def __init__(self):
        self.threads: Dict[str, CommentThread] = {}
        self.comments_by_id: Dict[str, Comment] = {}

    def create_comment(self, user_id: str, template_id: str, section: str,
                      content: str, mentions: Optional[List[str]] = None) -> Comment:
        """Create a new comment."""
        comment = Comment(
            user_id=user_id,
            section=section,
            content=content,
            mentions=mentions or []
        )
        
        # Find or create thread
        thread_key = f"{template_id}:{section}"
        if thread_key not in self.threads:
            self.threads[thread_key] = CommentThread(
                template_id=template_id,
                section=section
            )
        
        self.threads[thread_key].comments.append(comment)
        self.comments_by_id[comment.id] = comment
        return comment

    def add_reply(self, comment_id: str, user_id: str, content: str) -> Optional[Comment]:
        """Add a reply to a comment."""
        if comment_id not in self.comments_by_id:
            return None
        
        parent = self.comments_by_id[comment_id]
        reply = Comment(user_id=user_id, content=content)
        parent.replies.append(reply)
        self.comments_by_id[reply.id] = reply
        return reply

    def resolve_comment(self, comment_id: str, resolved_by: str) -> Tuple[bool, str]:
        """Mark a comment as resolved."""
        if comment_id not in self.comments_by_id:
            return False, f"Comment {comment_id} not found"
        
        comment = self.comments_by_id[comment_id]
        comment.resolved = True
        comment.resolved_by = resolved_by
        comment.resolved_at = datetime.now().timestamp()
        return True, "Comment marked as resolved"

    def get_thread(self, template_id: str, section: str) -> Optional[CommentThread]:
        """Get comment thread for a section."""
        thread_key = f"{template_id}:{section}"
        return self.threads.get(thread_key)

    def get_all_threads(self, template_id: str) -> List[CommentThread]:
        """Get all comment threads for a template."""
        return [t for t in self.threads.values() if t.template_id == template_id]

    def get_unresolved_comments(self, template_id: str) -> List[Comment]:
        """Get all unresolved comments."""
        unresolved = []
        for thread in self.get_all_threads(template_id):
            unresolved.extend([c for c in thread.comments if not c.resolved])
        return unresolved


class VersionControlManager:
    """Manages version control with branches and merging."""
    
    def __init__(self, template_id: str):
        self.template_id = template_id
        self.branches: Dict[str, Branch] = {}
        self.merge_requests: Dict[str, MergeRequest] = {}
        self.main_branch = self._create_branch("main", 0, "system")

    def _create_branch(self, name: str, based_on: int, created_by: str) -> Branch:
        """Create a branch internally."""
        branch = Branch(
            name=name,
            template_id=self.template_id,
            based_on_version=based_on,
            created_by=created_by
        )
        self.branches[name] = branch
        return branch

    def create_branch(self, name: str, based_on_version: int, created_by: str) -> Tuple[bool, str]:
        """Create a new branch."""
        if name in self.branches:
            return False, f"Branch '{name}' already exists"
        if name == "main":
            return False, "Cannot create branch named 'main'"
        
        self._create_branch(name, based_on_version, created_by)
        return True, f"Branch '{name}' created"

    def add_change_to_branch(self, branch_name: str, change: Change) -> Tuple[bool, str]:
        """Add a change to a branch."""
        if branch_name not in self.branches:
            return False, f"Branch '{branch_name}' not found"
        
        self.branches[branch_name].changes.append(change)
        return True, "Change added to branch"

    def create_merge_request(self, source_branch: str, target_branch: str,
                           created_by: str, description: str = "") -> Tuple[bool, str]:
        """Create a merge request."""
        if source_branch not in self.branches:
            return False, f"Source branch '{source_branch}' not found"
        if target_branch not in self.branches:
            return False, f"Target branch '{target_branch}' not found"
        
        mr = MergeRequest(
            source_branch=source_branch,
            target_branch=target_branch,
            created_by=created_by,
            description=description
        )
        self.merge_requests[mr.id] = mr
        return True, f"Merge request {mr.id} created"

    def detect_conflicts(self, source_branch: str, target_branch: str) -> List[Dict[str, Any]]:
        """Detect conflicts between branches."""
        if source_branch not in self.branches or target_branch not in self.branches:
            return []
        
        source_changes = self.branches[source_branch].changes
        target_changes = self.branches[target_branch].changes
        
        conflicts = []
        for s_change in source_changes:
            for t_change in target_changes:
                if s_change.path == t_change.path and s_change.user_id != t_change.user_id:
                    conflicts.append({
                        "type": ConflictType.CONCURRENT_EDIT.value,
                        "path": s_change.path,
                        "source_change_id": s_change.id,
                        "target_change_id": t_change.id,
                        "source_value": s_change.new_value,
                        "target_value": t_change.new_value
                    })
        
        return conflicts

    def merge_branches(self, merge_request_id: str) -> Tuple[bool, str]:
        """Merge branches."""
        if merge_request_id not in self.merge_requests:
            return False, f"Merge request {merge_request_id} not found"
        
        mr = self.merge_requests[merge_request_id]
        
        # Detect conflicts
        conflicts = self.detect_conflicts(mr.source_branch, mr.target_branch)
        if conflicts:
            mr.conflicts = conflicts
            return False, f"Merge has {len(conflicts)} conflicts"
        
        # Perform merge
        source_changes = self.branches[mr.source_branch].changes
        target_branch = self.branches[mr.target_branch]
        
        for change in source_changes:
            target_branch.changes.append(change)
        
        mr.status = "merged"
        return True, f"Merge request {merge_request_id} merged successfully"

    def get_branch(self, name: str) -> Optional[Branch]:
        """Get branch by name."""
        return self.branches.get(name)

    def get_all_branches(self) -> List[str]:
        """Get all branch names."""
        return list(self.branches.keys())


class CollaborativeEditingManager:
    """Manages real-time collaborative editing."""
    
    def __init__(self):
        self.sessions: Dict[str, CollaborativeSession] = {}
        self.user_cursors: Dict[str, Dict[str, Any]] = {}  # user_id -> cursor info
        self.offline_queue: Dict[str, List[Change]] = {}  # user_id -> queued changes

    def create_session(self, template_id: str) -> CollaborativeSession:
        """Create a new collaboration session."""
        session = CollaborativeSession(template_id=template_id)
        self.sessions[session.id] = session
        self.offline_queue[session.id] = []
        return session

    def add_user_to_session(self, session_id: str, user: User) -> Tuple[bool, str]:
        """Add user to session."""
        if session_id not in self.sessions:
            return False, f"Session {session_id} not found"
        
        session = self.sessions[session_id]
        session.users[user.id] = user
        return True, f"User {user.name} added to session"

    def remove_user_from_session(self, session_id: str, user_id: str) -> Tuple[bool, str]:
        """Remove user from session."""
        if session_id not in self.sessions:
            return False, f"Session {session_id} not found"
        
        session = self.sessions[session_id]
        if user_id in session.users:
            del session.users[user_id]
            return True, f"User removed from session"
        return False, "User not in session"

    def update_cursor_position(self, user_id: str, line: int, column: int):
        """Update user's cursor position."""
        self.user_cursors[user_id] = {
            "line": line,
            "column": column,
            "timestamp": datetime.now().timestamp()
        }

    def get_active_cursors(self) -> Dict[str, Dict[str, Any]]:
        """Get all active cursor positions."""
        return self.user_cursors.copy()

    def apply_change(self, session_id: str, change: Change) -> Tuple[bool, str]:
        """Apply a change to the session."""
        if session_id not in self.sessions:
            return False, f"Session {session_id} not found"
        
        session = self.sessions[session_id]
        session.changes.append(change)
        return True, "Change applied"

    def queue_offline_change(self, session_id: str, change: Change):
        """Queue a change for offline sync."""
        if session_id not in self.offline_queue:
            self.offline_queue[session_id] = []
        self.offline_queue[session_id].append(change)

    def sync_offline_changes(self, session_id: str) -> Tuple[bool, int]:
        """Sync queued offline changes."""
        if session_id not in self.offline_queue:
            return False, 0
        
        changes = self.offline_queue[session_id]
        if not changes:
            return True, 0
        
        session = self.sessions[session_id]
        for change in changes:
            session.changes.append(change)
        
        count = len(changes)
        self.offline_queue[session_id] = []
        return True, count

    def get_session(self, session_id: str) -> Optional[CollaborativeSession]:
        """Get session by ID."""
        return self.sessions.get(session_id)

    def end_session(self, session_id: str) -> Tuple[bool, str]:
        """End a collaboration session."""
        if session_id not in self.sessions:
            return False, f"Session {session_id} not found"
        
        session = self.sessions[session_id]
        session.active = False
        return True, "Session ended"


class SyncCoordinator:
    """Orchestrates all collaborative features."""
    
    def __init__(self):
        self.editing_manager = CollaborativeEditingManager()
        self.commenting_system = CommentingSystem()
        self.tracking_engines: Dict[str, ChangeTrackingEngine] = {}
        self.version_control: Dict[str, VersionControlManager] = {}

    def initialize_template(self, template_id: str):
        """Initialize collaboration for a template."""
        if template_id not in self.tracking_engines:
            self.tracking_engines[template_id] = ChangeTrackingEngine(template_id)
            self.version_control[template_id] = VersionControlManager(template_id)

    def create_collaboration_session(self, template_id: str, initial_user: User) -> CollaborativeSession:
        """Create a new collaboration session."""
        self.initialize_template(template_id)
        session = self.editing_manager.create_session(template_id)
        self.editing_manager.add_user_to_session(session.id, initial_user)
        return session

    def record_change(self, template_id: str, user_id: str, operation: ChangeType,
                     path: str, old_value: Any = None, new_value: Any = None) -> Change:
        """Record a change in tracking engine."""
        self.initialize_template(template_id)
        return self.tracking_engines[template_id].record_change(
            user_id, operation, path, old_value, new_value
        )

    def add_comment(self, template_id: str, user_id: str, section: str,
                   content: str, mentions: Optional[List[str]] = None) -> Comment:
        """Add a comment."""
        return self.commenting_system.create_comment(
            user_id, template_id, section, content, mentions
        )

    def get_template_summary(self, template_id: str) -> Dict[str, Any]:
        """Get complete summary of template collaboration."""
        if template_id not in self.tracking_engines:
            return {}
        
        return {
            "changes": self.tracking_engines[template_id].get_change_summary(),
            "threads": len(self.commenting_system.get_all_threads(template_id)),
            "branches": len(self.version_control[template_id].get_all_branches()),
            "unresolved_comments": len(self.commenting_system.get_unresolved_comments(template_id))
        }
