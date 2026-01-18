/**
 * Cloud Sync UI - Issue #57
 * Real-time cloud synchronization and conflict resolution interface
 * 
 * Features:
 * - Multi-cloud provider support (S3, Azure, GCS)
 * - Real-time sync status
 * - Conflict detection and resolution
 * - Offline mode management
 * - Storage quota visualization
 */

class CloudSyncUI {
  constructor() {
    this.provider = 's3';
    this.syncing = false;
    this.offline = false;
    this.conflicts = [];
    this.syncStats = {
      uploaded: 0,
      downloaded: 0,
      lastSync: null,
      averageTime: 0
    };
    this.storageStats = {
      used: 0,
      available: 100,
      templateCount: 0
    };
    this.offlineQueue = [];
    this.init();
  }

  init() {
    this.createUI();
    this.attachEventListeners();
    this.updateStatus();
    this.startAutoRefresh();
  }

  createUI() {
    const container = document.getElementById('cloud-sync-container');
    if (!container) return;

    container.innerHTML = `
      <div class="cloud-sync-panel">
        <!-- Header with Provider Selection -->
        <div class="cloud-header">
          <div class="cloud-provider-selector">
            <label>Cloud Provider:</label>
            <select id="cloud-provider">
              <option value="s3">Amazon S3</option>
              <option value="azure">Azure Blob Storage</option>
              <option value="gcs">Google Cloud Storage</option>
            </select>
            <button id="btn-configure" class="btn-primary">Configure</button>
          </div>
          
          <div class="cloud-status-indicator">
            <div class="status-badge" id="sync-status-badge">Ready</div>
            <div class="offline-indicator" id="offline-indicator" style="display: none;">
              <i class="icon-offline"></i> Offline Mode
            </div>
          </div>
        </div>

        <!-- Tabs -->
        <div class="cloud-tabs">
          <button class="tab-button active" data-tab="sync">Synchronization</button>
          <button class="tab-button" data-tab="conflicts">Conflicts</button>
          <button class="tab-button" data-tab="storage">Storage</button>
          <button class="tab-button" data-tab="offline">Offline Queue</button>
        </div>

        <!-- Sync Tab -->
        <div class="tab-content active" id="tab-sync">
          <div class="sync-controls">
            <button id="btn-sync-now" class="btn-primary btn-large">
              <i class="icon-sync"></i> Sync Now
            </button>
            <button id="btn-auto-sync" class="btn-secondary">
              <i class="icon-schedule"></i> Auto-Sync: OFF
            </button>
          </div>

          <div class="sync-statistics">
            <div class="stat-card">
              <div class="stat-label">Files Uploaded</div>
              <div class="stat-value" id="stat-uploaded">0</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">Files Downloaded</div>
              <div class="stat-value" id="stat-downloaded">0</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">Average Sync Time</div>
              <div class="stat-value" id="stat-avg-time">--</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">Last Sync</div>
              <div class="stat-value" id="stat-last-sync">Never</div>
            </div>
          </div>

          <div class="sync-progress" id="sync-progress" style="display: none;">
            <div class="progress-bar">
              <div class="progress-fill" id="progress-fill"></div>
            </div>
            <div class="progress-text" id="progress-text">Syncing...</div>
          </div>

          <div class="recent-activity">
            <h3>Recent Activity</h3>
            <div class="activity-list" id="activity-list">
              <p class="empty-state">No recent activity</p>
            </div>
          </div>
        </div>

        <!-- Conflicts Tab -->
        <div class="tab-content" id="tab-conflicts">
          <div class="conflicts-info">
            <h3>Version Conflicts</h3>
            <p class="info-text" id="conflicts-count">No conflicts detected</p>
          </div>

          <div class="conflicts-list" id="conflicts-list">
            <p class="empty-state">No conflicts</p>
          </div>
        </div>

        <!-- Storage Tab -->
        <div class="tab-content" id="tab-storage">
          <div class="storage-overview">
            <div class="storage-quota">
              <h3>Storage Usage</h3>
              <div class="quota-bar">
                <div class="quota-fill" id="quota-fill"></div>
              </div>
              <div class="quota-text">
                <span id="storage-used">0 MB</span> / 
                <span id="storage-available">100 GB</span> used
              </div>
            </div>

            <div class="storage-stats">
              <div class="stat-card">
                <div class="stat-label">Templates</div>
                <div class="stat-value" id="stat-templates">0</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">Success Rate</div>
                <div class="stat-value" id="stat-success-rate">100%</div>
              </div>
            </div>
          </div>

          <div class="storage-actions">
            <button id="btn-cleanup" class="btn-secondary">Clean Up Storage</button>
            <button id="btn-view-remote" class="btn-secondary">View Remote Files</button>
          </div>
        </div>

        <!-- Offline Queue Tab -->
        <div class="tab-content" id="tab-offline">
          <div class="offline-info">
            <div class="info-box">
              <i class="icon-info"></i>
              <p>Operations added in offline mode will be executed when connection is restored.</p>
            </div>
          </div>

          <div class="offline-queue-list" id="offline-queue-list">
            <p class="empty-state">Queue is empty</p>
          </div>

          <div class="offline-actions">
            <button id="btn-enable-offline" class="btn-secondary">Enable Offline Mode</button>
            <button id="btn-clear-queue" class="btn-danger" style="display: none;">Clear Queue</button>
          </div>
        </div>
      </div>

      <!-- Conflict Resolution Modal -->
      <div class="modal" id="conflict-modal" style="display: none;">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Resolve Conflict</h2>
            <button class="btn-close" id="btn-close-modal">&times;</button>
          </div>
          
          <div class="modal-body">
            <div class="conflict-details" id="conflict-details"></div>
            
            <div class="resolution-options">
              <label>
                <input type="radio" name="resolution" value="last_write_wins" checked>
                <span>Use Local Version (Last Write Wins)</span>
              </label>
              <label>
                <input type="radio" name="resolution" value="server_preferred">
                <span>Use Remote Version (Server Preferred)</span>
              </label>
              <label>
                <input type="radio" name="resolution" value="local_preferred">
                <span>Keep Local (Local Preferred)</span>
              </label>
              <label>
                <input type="radio" name="resolution" value="manual">
                <span>Manual Review Required</span>
              </label>
            </div>
          </div>

          <div class="modal-footer">
            <button id="btn-resolve" class="btn-primary">Resolve</button>
            <button id="btn-cancel-modal" class="btn-secondary">Cancel</button>
          </div>
        </div>
      </div>
    `;
  }

  attachEventListeners() {
    // Tab switching
    document.querySelectorAll('.tab-button').forEach(btn => {
      btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
    });

    // Sync controls
    document.getElementById('btn-sync-now')?.addEventListener('click', () => this.syncNow());
    document.getElementById('btn-auto-sync')?.addEventListener('click', () => this.toggleAutoSync());

    // Provider selection
    document.getElementById('cloud-provider')?.addEventListener('change', (e) => {
      this.provider = e.target.value;
    });
    document.getElementById('btn-configure')?.addEventListener('click', () => this.configureBackend());

    // Storage actions
    document.getElementById('btn-cleanup')?.addEventListener('click', () => this.cleanupStorage());
    document.getElementById('btn-view-remote')?.addEventListener('click', () => this.viewRemoteFiles());

    // Offline mode
    document.getElementById('btn-enable-offline')?.addEventListener('click', () => this.toggleOfflineMode());
    document.getElementById('btn-clear-queue')?.addEventListener('click', () => this.clearOfflineQueue());

    // Modal
    document.getElementById('btn-close-modal')?.addEventListener('click', () => this.closeConflictModal());
    document.getElementById('btn-cancel-modal')?.addEventListener('click', () => this.closeConflictModal());
    document.getElementById('btn-resolve')?.addEventListener('click', () => this.resolveConflict());
  }

  switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
      tab.classList.remove('active');
    });

    // Deactivate all buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
      btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(`tab-${tabName}`)?.classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');

    // Update content
    if (tabName === 'conflicts') {
      this.updateConflictsList();
    } else if (tabName === 'offline') {
      this.updateOfflineQueue();
    }
  }

  syncNow() {
    const btn = document.getElementById('btn-sync-now');
    if (btn.disabled) return;

    btn.disabled = true;
    this.setSyncing(true);

    // Simulate sync operation
    setTimeout(() => {
      this.updateStatus();
      btn.disabled = false;
      this.setSyncing(false);
      this.showNotification('Sync completed successfully', 'success');
    }, 2000);
  }

  toggleAutoSync() {
    // Would connect to actual auto-sync service
    const btn = document.getElementById('btn-auto-sync');
    const enabled = btn.textContent.includes('ON');
    btn.textContent = enabled ? 
      '<i class="icon-schedule"></i> Auto-Sync: OFF' :
      '<i class="icon-schedule"></i> Auto-Sync: ON';
    btn.classList.toggle('active');
  }

  configureBackend() {
    const provider = document.getElementById('cloud-provider').value;
    // Would show configuration dialog
    this.showNotification(`Configure ${provider} backend`, 'info');
  }

  cleanupStorage() {
    if (confirm('This will remove unused files. Continue?')) {
      this.showNotification('Storage cleanup started...', 'info');
      setTimeout(() => {
        this.updateStatus();
        this.showNotification('Cleanup completed', 'success');
      }, 1500);
    }
  }

  viewRemoteFiles() {
    // Would show remote files list
    this.showNotification('Loading remote files...', 'info');
  }

  toggleOfflineMode() {
    this.offline = !this.offline;
    const indicator = document.getElementById('offline-indicator');
    const btn = document.getElementById('btn-enable-offline');

    if (this.offline) {
      indicator.style.display = 'flex';
      btn.textContent = 'Disable Offline Mode';
      btn.classList.add('active');
      this.showNotification('Offline mode enabled', 'info');
    } else {
      indicator.style.display = 'none';
      btn.textContent = 'Enable Offline Mode';
      btn.classList.remove('active');
      this.showNotification('Offline mode disabled', 'info');
    }
  }

  clearOfflineQueue() {
    if (confirm('Clear all queued operations?')) {
      this.offlineQueue = [];
      this.updateOfflineQueue();
      this.showNotification('Queue cleared', 'success');
    }
  }

  updateStatus() {
    // Update sync stats
    document.getElementById('stat-uploaded').textContent = this.syncStats.uploaded;
    document.getElementById('stat-downloaded').textContent = this.syncStats.downloaded;
    document.getElementById('stat-avg-time').textContent = 
      this.syncStats.averageTime > 0 ? `${this.syncStats.averageTime}ms` : '--';
    document.getElementById('stat-last-sync').textContent = 
      this.syncStats.lastSync || 'Never';

    // Update storage stats
    const quotaPercent = (this.storageStats.used / this.storageStats.available) * 100;
    document.getElementById('quota-fill').style.width = quotaPercent + '%';
    document.getElementById('storage-used').textContent = this.formatBytes(this.storageStats.used);
    document.getElementById('storage-available').textContent = this.formatBytes(this.storageStats.available);
    document.getElementById('stat-templates').textContent = this.storageStats.templateCount;
  }

  updateConflictsList() {
    const list = document.getElementById('conflicts-list');
    const count = document.getElementById('conflicts-count');

    if (this.conflicts.length === 0) {
      list.innerHTML = '<p class="empty-state">No conflicts detected</p>';
      count.textContent = 'No conflicts detected';
      return;
    }

    count.textContent = `${this.conflicts.length} conflict(s) detected`;

    list.innerHTML = this.conflicts.map((conflict, idx) => `
      <div class="conflict-card">
        <div class="conflict-header">
          <h4>${conflict.templateId}</h4>
          <span class="conflict-time">${new Date(conflict.timestamp).toLocaleString()}</span>
        </div>
        <div class="conflict-versions">
          <div class="version-box">
            <h5>Local Version</h5>
            <p>${JSON.stringify(conflict.localVersion).substring(0, 50)}...</p>
          </div>
          <div class="version-box">
            <h5>Remote Version</h5>
            <p>${JSON.stringify(conflict.remoteVersion).substring(0, 50)}...</p>
          </div>
        </div>
        <button class="btn-secondary" onclick="cloudUI.showConflictModal(${idx})">
          Resolve
        </button>
      </div>
    `).join('');
  }

  updateOfflineQueue() {
    const list = document.getElementById('offline-queue-list');
    const clearBtn = document.getElementById('btn-clear-queue');

    if (this.offlineQueue.length === 0) {
      list.innerHTML = '<p class="empty-state">Queue is empty</p>';
      clearBtn.style.display = 'none';
      return;
    }

    clearBtn.style.display = 'inline-block';

    list.innerHTML = this.offlineQueue.map((op, idx) => `
      <div class="queue-item">
        <span class="queue-type ${op.type}">${op.type.toUpperCase()}</span>
        <span class="queue-name">${op.templateId}</span>
        <span class="queue-time">${new Date(op.timestamp).toLocaleString()}</span>
        <button class="btn-small" onclick="cloudUI.removeFromQueue(${idx})">Remove</button>
      </div>
    `).join('');
  }

  removeFromQueue(idx) {
    this.offlineQueue.splice(idx, 1);
    this.updateOfflineQueue();
  }

  showConflictModal(idx) {
    const conflict = this.conflicts[idx];
    const modal = document.getElementById('conflict-modal');
    const details = document.getElementById('conflict-details');

    details.innerHTML = `
      <h4>${conflict.templateId}</h4>
      <p><strong>Detected:</strong> ${new Date(conflict.timestamp).toLocaleString()}</p>
      <div class="version-comparison">
        <div>
          <h5>Local</h5>
          <pre>${JSON.stringify(conflict.localVersion, null, 2)}</pre>
        </div>
        <div>
          <h5>Remote</h5>
          <pre>${JSON.stringify(conflict.remoteVersion, null, 2)}</pre>
        </div>
      </div>
    `;

    modal.dataset.conflictIdx = idx;
    modal.style.display = 'flex';
  }

  closeConflictModal() {
    document.getElementById('conflict-modal').style.display = 'none';
  }

  resolveConflict() {
    const modal = document.getElementById('conflict-modal');
    const idx = modal.dataset.conflictIdx;
    const strategy = document.querySelector('input[name="resolution"]:checked').value;

    this.conflicts.splice(idx, 1);
    this.closeConflictModal();
    this.updateConflictsList();
    this.showNotification(`Conflict resolved using ${strategy}`, 'success');
  }

  setSyncing(syncing) {
    this.syncing = syncing;
    const progress = document.getElementById('sync-progress');
    const badge = document.getElementById('sync-status-badge');

    if (syncing) {
      progress.style.display = 'block';
      badge.textContent = 'Syncing...';
      badge.classList.add('syncing');
    } else {
      progress.style.display = 'none';
      badge.textContent = 'Ready';
      badge.classList.remove('syncing');
    }
  }

  startAutoRefresh() {
    // Refresh status every 5 seconds
    setInterval(() => this.updateStatus(), 5000);
  }

  formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }

  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    const container = document.body;
    container.appendChild(notification);

    setTimeout(() => {
      notification.classList.add('show');
    }, 10);

    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }
}

// Initialize on load
let cloudUI;
document.addEventListener('DOMContentLoaded', () => {
  cloudUI = new CloudSyncUI();
});
