/**
 * Collaborative Editing Module (JavaScript)
 * 
 * Client-side components for collaborative editing:
 * - Real-time change broadcasting
 * - Comment management and display
 * - Branch/merge visualization
 * - Presence awareness
 */

class CollaborativeEditor {
  constructor() {
    this.sessions = {};
    this.currentSession = null;
    this.activeUsers = {};
    this.changeBuffer = [];
  }

  createSession(templateId, userId) {
    const sessionId = 'session_' + Date.now();
    this.sessions[sessionId] = {
      id: sessionId,
      templateId,
      userId,
      users: { [userId]: { id: userId, active: true } },
      changes: [],
      createdAt: Date.now()
    };
    this.currentSession = sessionId;
    return sessionId;
  }

  addUserToSession(sessionId, userId, userName) {
    if (this.sessions[sessionId]) {
      this.sessions[sessionId].users[userId] = {
        id: userId,
        name: userName,
        active: true,
        lastSeen: Date.now()
      };
      this.activeUsers[userId] = userName;
      return true;
    }
    return false;
  }

  recordChange(operation, path, oldValue, newValue) {
    const change = {
      id: 'change_' + Date.now(),
      userId: this.sessions[this.currentSession]?.userId,
      operation,
      path,
      oldValue,
      newValue,
      timestamp: Date.now()
    };
    
    if (this.currentSession) {
      this.sessions[this.currentSession].changes.push(change);
    }
    this.changeBuffer.push(change);
    return change;
  }

  broadcastChange(change) {
    // Would send to server via WebSocket
    console.log('Broadcasting change:', change);
    return true;
  }

  getSessionUsers(sessionId) {
    return this.sessions[sessionId]?.users || {};
  }

  getChangeHistory(sessionId) {
    return this.sessions[sessionId]?.changes || [];
  }
}

class CommentUI {
  constructor() {
    this.comments = {};
    this.threads = {};
  }

  createComment(templateId, section, content, userId) {
    const threadKey = `${templateId}:${section}`;
    const commentId = 'comment_' + Date.now();
    
    const comment = {
      id: commentId,
      userId,
      section,
      content,
      createdAt: Date.now(),
      resolved: false,
      replies: []
    };
    
    this.comments[commentId] = comment;
    
    if (!this.threads[threadKey]) {
      this.threads[threadKey] = [];
    }
    this.threads[threadKey].push(comment);
    
    return comment;
  }

  addReply(commentId, content, userId) {
    if (this.comments[commentId]) {
      const reply = {
        id: 'reply_' + Date.now(),
        userId,
        content,
        createdAt: Date.now()
      };
      this.comments[commentId].replies.push(reply);
      return reply;
    }
    return null;
  }

  resolveComment(commentId, resolvedBy) {
    if (this.comments[commentId]) {
      this.comments[commentId].resolved = true;
      this.comments[commentId].resolvedBy = resolvedBy;
      return true;
    }
    return false;
  }

  renderCommentThread(templateId, section) {
    const threadKey = `${templateId}:${section}`;
    const comments = this.threads[threadKey] || [];
    
    return {
      section,
      commentCount: comments.length,
      unresolvedCount: comments.filter(c => !c.resolved).length,
      comments
    };
  }

  getUnresolvedComments(templateId) {
    return Object.values(this.comments).filter(c => !c.resolved);
  }
}

class VersionControlUI {
  constructor() {
    this.branches = { 'main': { name: 'main', basedOnVersion: 0, changes: [] } };
    this.mergeRequests = {};
    this.currentBranch = 'main';
  }

  createBranch(name, basedOnVersion, createdBy) {
    if (this.branches[name]) {
      return { success: false, message: `Branch '${name}' already exists` };
    }
    
    this.branches[name] = {
      name,
      basedOnVersion,
      createdBy,
      createdAt: Date.now(),
      changes: []
    };
    return { success: true, message: `Branch '${name}' created` };
  }

  switchBranch(name) {
    if (this.branches[name]) {
      this.currentBranch = name;
      return true;
    }
    return false;
  }

  createMergeRequest(sourceBranch, targetBranch, createdBy, description) {
    const mrId = 'mr_' + Date.now();
    this.mergeRequests[mrId] = {
      id: mrId,
      sourceBranch,
      targetBranch,
      createdBy,
      description,
      status: 'open',
      createdAt: Date.now(),
      comments: []
    };
    return mrId;
  }

  detectConflicts(sourceBranch, targetBranch) {
    // Simplified conflict detection
    const sourceChanges = this.branches[sourceBranch]?.changes || [];
    const targetChanges = this.branches[targetBranch]?.changes || [];
    
    const conflicts = [];
    for (const sc of sourceChanges) {
      for (const tc of targetChanges) {
        if (sc.path === tc.path && sc.userId !== tc.userId) {
          conflicts.push({
            path: sc.path,
            sourceValue: sc.newValue,
            targetValue: tc.newValue
          });
        }
      }
    }
    return conflicts;
  }

  mergeBranches(mrId) {
    if (!this.mergeRequests[mrId]) {
      return { success: false, message: 'Merge request not found' };
    }
    
    const mr = this.mergeRequests[mrId];
    const conflicts = this.detectConflicts(mr.sourceBranch, mr.targetBranch);
    
    if (conflicts.length > 0) {
      return { success: false, conflicts, message: `${conflicts.length} conflicts detected` };
    }
    
    mr.status = 'merged';
    return { success: true, message: 'Merge completed' };
  }

  getBranches() {
    return Object.keys(this.branches);
  }

  getMergeRequests() {
    return Object.values(this.mergeRequests);
  }
}

class PresenceIndicator {
  constructor() {
    this.activeUsers = {};
    this.cursorPositions = {};
  }

  updateUserPresence(userId, userName, status = 'active') {
    this.activeUsers[userId] = {
      id: userId,
      name: userName,
      status,
      lastSeen: Date.now(),
      color: this.generateUserColor(userId)
    };
  }

  updateCursorPosition(userId, line, column, section) {
    this.cursorPositions[userId] = {
      line,
      column,
      section,
      timestamp: Date.now()
    };
  }

  getActiveCursors() {
    return Object.entries(this.cursorPositions).map(([userId, cursor]) => ({
      userId,
      ...cursor,
      user: this.activeUsers[userId]
    }));
  }

  getActiveUsers() {
    const now = Date.now();
    const timeout = 30000; // 30 seconds
    
    return Object.values(this.activeUsers).filter(user => {
      return (now - user.lastSeen) < timeout;
    });
  }

  removeUser(userId) {
    delete this.activeUsers[userId];
    delete this.cursorPositions[userId];
  }

  generateUserColor(userId) {
    const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'];
    const hash = userId.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0);
    return colors[hash % colors.length];
  }
}

// Export classes
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    CollaborativeEditor,
    CommentUI,
    VersionControlUI,
    PresenceIndicator
  };
}
