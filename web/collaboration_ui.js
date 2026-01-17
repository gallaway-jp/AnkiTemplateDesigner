/**
 * Collaboration UI Component (Issue #55)
 * 
 * Real-time collaboration interface with:
 * - User presence and cursor tracking
 * - Comments and discussions
 * - Version history browser
 * - Share and permission management
 */

class CollaborationUI {
    constructor(elementId = 'collaboration-container', options = {}) {
        this.container = document.getElementById(elementId);
        this.options = {
            updateInterval: 1000,
            maxComments: 50,
            ...options
        };
        
        this.collaborators = new Map();
        this.comments = [];
        this.syncStatus = {
            syncing: false,
            lastSync: null,
            conflicts: 0
        };
        
        this.listeners = {};
        this.updateTimer = null;
        
        this.init();
    }

    init() {
        this.createUI();
        this.attachEventListeners();
        this.startUpdates();
    }

    createUI() {
        if (!this.container) return;

        this.container.innerHTML = `
            <div class="collab-panel">
                <!-- Header -->
                <div class="collab-header">
                    <h3>Collaboration</h3>
                    <div class="collab-status">
                        <span class="collab-sync-indicator" title="Sync status">●</span>
                        <span class="collab-sync-text">Ready</span>
                    </div>
                </div>

                <!-- Tabs -->
                <div class="collab-tabs">
                    <button class="collab-tab active" data-tab="presence">
                        👥 Collaborators
                    </button>
                    <button class="collab-tab" data-tab="comments">
                        💬 Comments
                    </button>
                    <button class="collab-tab" data-tab="history">
                        📜 History
                    </button>
                    <button class="collab-tab" data-tab="share">
                        🔗 Share
                    </button>
                </div>

                <!-- Tab Content -->
                <div class="collab-content">
                    <!-- Presence Tab -->
                    <div class="collab-panel-content active" data-content="presence">
                        <div class="collab-presence">
                            <div class="collab-presence-list"></div>
                        </div>
                    </div>

                    <!-- Comments Tab -->
                    <div class="collab-panel-content" data-content="comments">
                        <div class="collab-comments">
                            <div class="collab-comment-input">
                                <textarea 
                                    class="collab-comment-text" 
                                    placeholder="Add a comment...">
                                </textarea>
                                <button class="collab-comment-submit">Post Comment</button>
                            </div>
                            <div class="collab-comments-list"></div>
                        </div>
                    </div>

                    <!-- History Tab -->
                    <div class="collab-panel-content" data-content="history">
                        <div class="collab-history">
                            <div class="collab-history-list"></div>
                        </div>
                    </div>

                    <!-- Share Tab -->
                    <div class="collab-panel-content" data-content="share">
                        <div class="collab-share">
                            <div class="collab-share-input">
                                <input 
                                    type="email" 
                                    class="collab-share-email" 
                                    placeholder="user@example.com">
                                <select class="collab-share-permission">
                                    <option value="view">View</option>
                                    <option value="edit">Edit</option>
                                    <option value="admin">Admin</option>
                                </select>
                                <button class="collab-share-button">Share</button>
                            </div>
                            <div class="collab-share-list"></div>
                        </div>
                    </div>
                </div>

                <!-- Footer -->
                <div class="collab-footer">
                    <small class="collab-last-sync">Last sync: just now</small>
                    <button class="collab-refresh-btn">⟲ Refresh</button>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        if (!this.container) return;

        // Tab switching
        this.container.querySelectorAll('.collab-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchTab(e.target));
        });

        // Comment submission
        const submitBtn = this.container.querySelector('.collab-comment-submit');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitComment());
        }

        // Share functionality
        const shareBtn = this.container.querySelector('.collab-share-button');
        if (shareBtn) {
            shareBtn.addEventListener('click', () => this.shareTemplate());
        }

        // Refresh
        const refreshBtn = this.container.querySelector('.collab-refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refresh());
        }

        // Comment text area - auto expand
        const commentText = this.container.querySelector('.collab-comment-text');
        if (commentText) {
            commentText.addEventListener('input', (e) => {
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 150) + 'px';
            });
        }
    }

    switchTab(tabElement) {
        if (!this.container) return;

        const tabName = tabElement.getAttribute('data-tab');
        
        // Update active tab
        this.container.querySelectorAll('.collab-tab').forEach(t => {
            t.classList.remove('active');
        });
        tabElement.classList.add('active');

        // Update active content
        this.container.querySelectorAll('.collab-panel-content').forEach(content => {
            content.classList.remove('active');
        });
        this.container.querySelector(`[data-content="${tabName}"]`).classList.add('active');

        this.emit('tabChanged', { tab: tabName });
    }

    updatePresence(collaborators) {
        this.collaborators = new Map(collaborators.map(c => [c.user_id, c]));
        this.renderPresence();
    }

    renderPresence() {
        const list = this.container?.querySelector('.collab-presence-list');
        if (!list) return;

        if (this.collaborators.size === 0) {
            list.innerHTML = '<p class="collab-empty">No active collaborators</p>';
            return;
        }

        list.innerHTML = Array.from(this.collaborators.values())
            .map(collab => `
                <div class="collab-presence-item">
                    <div class="collab-presence-avatar">${collab.username.charAt(0)}</div>
                    <div class="collab-presence-info">
                        <div class="collab-presence-name">${this.escapeHtml(collab.username)}</div>
                        <div class="collab-presence-cursor">
                            Cursor: (${collab.cursor_position[0]}, ${collab.cursor_position[1]})
                        </div>
                        <div class="collab-presence-status">${collab.status}</div>
                    </div>
                </div>
            `)
            .join('');
    }

    updateComments(comments) {
        this.comments = comments;
        this.renderComments();
    }

    renderComments() {
        const list = this.container?.querySelector('.collab-comments-list');
        if (!list) return;

        if (this.comments.length === 0) {
            list.innerHTML = '<p class="collab-empty">No comments yet</p>';
            return;
        }

        list.innerHTML = this.comments
            .slice(0, this.options.maxComments)
            .map(comment => `
                <div class="collab-comment ${comment.resolved ? 'resolved' : ''}">
                    <div class="collab-comment-header">
                        <span class="collab-comment-author">${this.escapeHtml(comment.user_id)}</span>
                        <span class="collab-comment-time">${this.formatTime(new Date(comment.created_at * 1000))}</span>
                        ${comment.resolved ? '<span class="collab-comment-resolved">✓ Resolved</span>' : ''}
                    </div>
                    <div class="collab-comment-text">${this.escapeHtml(comment.text)}</div>
                    ${comment.position ? `<div class="collab-comment-position">Line ${comment.position[0] + 1}</div>` : ''}
                    <div class="collab-comment-actions">
                        ${!comment.resolved ? `<button class="collab-resolve-btn" data-comment-id="${comment.comment_id}">Resolve</button>` : ''}
                    </div>
                </div>
            `)
            .join('');

        // Attach resolve buttons
        list.querySelectorAll('.collab-resolve-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const commentId = e.target.getAttribute('data-comment-id');
                this.emit('resolveComment', { commentId });
            });
        });
    }

    updateHistory(commits) {
        const list = this.container?.querySelector('.collab-history-list');
        if (!list) return;

        if (!commits || commits.length === 0) {
            list.innerHTML = '<p class="collab-empty">No commits yet</p>';
            return;
        }

        list.innerHTML = commits
            .map(commit => `
                <div class="collab-history-item">
                    <div class="collab-history-header">
                        <span class="collab-history-message">${this.escapeHtml(commit.message)}</span>
                        <span class="collab-history-hash" title="${commit.hash}">${commit.hash.substring(0, 7)}</span>
                    </div>
                    <div class="collab-history-meta">
                        <span class="collab-history-author">${this.escapeHtml(commit.author_name)}</span>
                        <span class="collab-history-time">${this.formatTime(new Date(commit.timestamp * 1000))}</span>
                        <span class="collab-history-stats">+${commit.insertions} -${commit.deletions}</span>
                    </div>
                </div>
            `)
            .join('');
    }

    updateSharedUsers(users) {
        const list = this.container?.querySelector('.collab-share-list');
        if (!list) return;

        if (!users || users.length === 0) {
            list.innerHTML = '<p class="collab-empty">Template not shared yet</p>';
            return;
        }

        list.innerHTML = users
            .map(user => `
                <div class="collab-share-item">
                    <div class="collab-share-user">
                        <span class="collab-share-name">${this.escapeHtml(user.username)}</span>
                        <span class="collab-share-email">${this.escapeHtml(user.email)}</span>
                    </div>
                    <div class="collab-share-permission-badge">${user.role}</div>
                    <button class="collab-unshare-btn" data-user-id="${user.user_id}">Remove</button>
                </div>
            `)
            .join('');

        // Attach unshare buttons
        list.querySelectorAll('.collab-unshare-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const userId = e.target.getAttribute('data-user-id');
                this.emit('unshareUser', { userId });
            });
        });
    }

    submitComment() {
        const textarea = this.container?.querySelector('.collab-comment-text');
        if (!textarea || !textarea.value.trim()) return;

        const text = textarea.value.trim();
        this.emit('commentAdded', { text });

        textarea.value = '';
        textarea.style.height = 'auto';
    }

    shareTemplate() {
        const emailInput = this.container?.querySelector('.collab-share-email');
        const permSelect = this.container?.querySelector('.collab-share-permission');

        if (!emailInput || !emailInput.value.trim()) return;

        const email = emailInput.value.trim();
        const permission = permSelect?.value || 'view';

        this.emit('templateShared', { email, permission });
        emailInput.value = '';
    }

    refresh() {
        this.updateSyncStatus('syncing');
        this.emit('refresh');
    }

    updateSyncStatus(status) {
        const indicator = this.container?.querySelector('.collab-sync-indicator');
        const statusText = this.container?.querySelector('.collab-sync-text');
        const lastSync = this.container?.querySelector('.collab-last-sync');

        if (status === 'syncing') {
            if (indicator) indicator.classList.add('syncing');
            if (statusText) statusText.textContent = 'Syncing...';
        } else if (status === 'synced') {
            if (indicator) {
                indicator.classList.remove('syncing');
                indicator.style.color = '#4CAF50';
            }
            if (statusText) statusText.textContent = 'Synced';
            if (lastSync) lastSync.textContent = `Last sync: ${this.formatTime(new Date())}`;
        } else if (status === 'error') {
            if (indicator) {
                indicator.classList.remove('syncing');
                indicator.style.color = '#f44336';
            }
            if (statusText) statusText.textContent = 'Sync error';
        }
    }

    startUpdates() {
        this.updateTimer = setInterval(() => {
            this.emit('updateRequested');
        }, this.options.updateInterval);
    }

    stopUpdates() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
    }

    show() {
        if (this.container) {
            this.container.style.display = 'block';
            this.startUpdates();
        }
    }

    hide() {
        if (this.container) {
            this.container.style.display = 'none';
            this.stopUpdates();
        }
    }

    toggle() {
        if (this.container) {
            if (this.container.style.display === 'none') {
                this.show();
            } else {
                this.hide();
            }
        }
    }

    getStatus() {
        return {
            visible: this.container?.style.display !== 'none',
            collaborators: this.collaborators.size,
            comments: this.comments.length,
            syncStatus: this.syncStatus
        };
    }

    // Utility methods
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatTime(date) {
        const now = new Date();
        const diff = now - date;

        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (seconds < 60) return 'just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days < 7) return `${days}d ago`;

        return date.toLocaleDateString();
    }

    // Event system
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    emit(event, data) {
        if (!this.listeners[event]) return;
        this.listeners[event].forEach(callback => callback(data));
    }

    destroy() {
        this.stopUpdates();
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CollaborationUI;
}
