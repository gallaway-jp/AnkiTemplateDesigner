/**
 * Backup Management UI (Issue #56)
 * 
 * Backup and recovery interface with:
 * - Backup creation and management
 * - Recovery point browser
 * - Schedule management
 * - Progress tracking
 */

class BackupUI {
    constructor(elementId = 'backup-container') {
        this.container = document.getElementById(elementId);
        this.backups = [];
        this.schedules = [];
        this.recoveryPoints = [];
        
        this.listeners = {};
        this.init();
    }

    init() {
        this.createUI();
        this.attachEventListeners();
    }

    createUI() {
        if (!this.container) return;

        this.container.innerHTML = `
            <div class="backup-panel">
                <!-- Header -->
                <div class="backup-header">
                    <h3>Backup & Recovery</h3>
                    <button class="backup-refresh-btn">⟲ Refresh</button>
                </div>

                <!-- Tabs -->
                <div class="backup-tabs">
                    <button class="backup-tab active" data-tab="backups">
                        💾 Backups
                    </button>
                    <button class="backup-tab" data-tab="schedule">
                        ⏰ Schedule
                    </button>
                    <button class="backup-tab" data-tab="recovery">
                        ⤴️ Recovery
                    </button>
                </div>

                <!-- Content -->
                <div class="backup-content">
                    <!-- Backups Tab -->
                    <div class="backup-section active" data-section="backups">
                        <div class="backup-controls">
                            <button class="backup-btn-primary">Create Full Backup</button>
                            <button class="backup-btn-secondary">Create Incremental</button>
                        </div>
                        
                        <div class="backup-stats">
                            <div class="stat-card">
                                <div class="stat-value">0</div>
                                <div class="stat-label">Total Backups</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">0 MB</div>
                                <div class="stat-label">Total Size</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">0%</div>
                                <div class="stat-label">Success Rate</div>
                            </div>
                        </div>

                        <div class="backup-list">
                            <div class="backup-empty">No backups yet</div>
                        </div>
                    </div>

                    <!-- Schedule Tab -->
                    <div class="backup-section" data-section="schedule">
                        <div class="schedule-form">
                            <div class="form-group">
                                <label>Backup Type</label>
                                <select class="schedule-type">
                                    <option value="full">Full Backup</option>
                                    <option value="incremental">Incremental</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Interval (hours)</label>
                                <input type="number" class="schedule-interval" value="24" min="1">
                            </div>
                            <div class="form-group">
                                <label>Retention (days)</label>
                                <input type="number" class="schedule-retention" value="30" min="1">
                            </div>
                            <button class="backup-btn-primary">Create Schedule</button>
                        </div>

                        <div class="schedule-list"></div>
                    </div>

                    <!-- Recovery Tab -->
                    <div class="backup-section" data-section="recovery">
                        <div class="recovery-points"></div>
                    </div>
                </div>

                <!-- Footer -->
                <div class="backup-footer">
                    <small>Last updated: just now</small>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        if (!this.container) return;

        // Tab switching
        this.container.querySelectorAll('.backup-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchTab(e.target));
        });

        // Refresh button
        const refreshBtn = this.container.querySelector('.backup-refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refresh());
        }

        // Primary buttons
        const primaryBtns = this.container.querySelectorAll('.backup-btn-primary');
        primaryBtns[0]?.addEventListener('click', () => this.emit('createFullBackup'));
        primaryBtns[1]?.addEventListener('click', () => this.emit('createIncremental'));

        // Schedule creation
        const scheduleBtn = this.container.querySelector('.backup-section[data-section="schedule"] .backup-btn-primary');
        if (scheduleBtn) {
            scheduleBtn.addEventListener('click', () => this.createSchedule());
        }
    }

    switchTab(tabElement) {
        if (!this.container) return;

        const tabName = tabElement.getAttribute('data-tab');

        // Update tabs
        this.container.querySelectorAll('.backup-tab').forEach(t => {
            t.classList.remove('active');
        });
        tabElement.classList.add('active');

        // Update sections
        this.container.querySelectorAll('.backup-section').forEach(s => {
            s.classList.remove('active');
        });
        this.container.querySelector(`[data-section="${tabName}"]`).classList.add('active');
    }

    updateBackups(backups) {
        this.backups = backups;
        this.renderBackups();
    }

    renderBackups() {
        const list = this.container?.querySelector('.backup-list');
        if (!list) return;

        if (this.backups.length === 0) {
            list.innerHTML = '<div class="backup-empty">No backups yet</div>';
            return;
        }

        list.innerHTML = this.backups.map(backup => `
            <div class="backup-item">
                <div class="backup-item-header">
                    <span class="backup-type ${backup.backup_type}">
                        ${backup.backup_type.toUpperCase()}
                    </span>
                    <span class="backup-status ${backup.status}">
                        ${backup.status}
                    </span>
                </div>
                <div class="backup-item-info">
                    <div class="info-row">
                        <span class="label">ID:</span>
                        <span class="value" title="${backup.backup_id}">
                            ${backup.backup_id.substring(0, 16)}...
                        </span>
                    </div>
                    <div class="info-row">
                        <span class="label">Time:</span>
                        <span class="value">${new Date(backup.timestamp * 1000).toLocaleString()}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Size:</span>
                        <span class="value">${this.formatBytes(backup.compressed_size)}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Templates:</span>
                        <span class="value">${backup.template_count}</span>
                    </div>
                </div>
                <div class="backup-item-actions">
                    <button class="backup-restore-btn" data-backup-id="${backup.backup_id}">
                        Restore
                    </button>
                    <button class="backup-verify-btn" data-backup-id="${backup.backup_id}">
                        Verify
                    </button>
                    <button class="backup-delete-btn" data-backup-id="${backup.backup_id}">
                        Delete
                    </button>
                </div>
            </div>
        `).join('');

        // Attach actions
        list.querySelectorAll('.backup-restore-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const backupId = e.target.getAttribute('data-backup-id');
                this.emit('restoreBackup', { backupId });
            });
        });

        list.querySelectorAll('.backup-delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const backupId = e.target.getAttribute('data-backup-id');
                if (confirm('Delete this backup?')) {
                    this.emit('deleteBackup', { backupId });
                }
            });
        });
    }

    updateStats(stats) {
        const cards = this.container?.querySelectorAll('.stat-card');
        if (cards && cards.length >= 3) {
            cards[0].querySelector('.stat-value').textContent = stats.total_backups;
            cards[1].querySelector('.stat-value').textContent = this.formatBytes(stats.total_size);
            cards[2].querySelector('.stat-value').textContent = stats.success_rate.toFixed(1) + '%';
        }
    }

    updateSchedules(schedules) {
        this.schedules = schedules;
        this.renderSchedules();
    }

    renderSchedules() {
        const list = this.container?.querySelector('.schedule-list');
        if (!list) return;

        if (this.schedules.length === 0) {
            list.innerHTML = '<p class="backup-empty">No schedules configured</p>';
            return;
        }

        list.innerHTML = this.schedules.map(schedule => `
            <div class="schedule-item">
                <div class="schedule-info">
                    <span class="schedule-type">${schedule.backup_type}</span>
                    <span>Every ${schedule.interval_hours}h</span>
                    <span class="schedule-status ${schedule.enabled ? 'enabled' : 'disabled'}">
                        ${schedule.enabled ? '✓ Active' : 'Inactive'}
                    </span>
                </div>
                <div class="schedule-actions">
                    <button class="schedule-delete-btn" data-schedule-id="${schedule.schedule_id}">
                        Remove
                    </button>
                </div>
            </div>
        `).join('');

        list.querySelectorAll('.schedule-delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const scheduleId = e.target.getAttribute('data-schedule-id');
                this.emit('deleteSchedule', { scheduleId });
            });
        });
    }

    updateRecoveryPoints(points) {
        this.recoveryPoints = points;
        this.renderRecoveryPoints();
    }

    renderRecoveryPoints() {
        const list = this.container?.querySelector('.recovery-points');
        if (!list) return;

        if (this.recoveryPoints.length === 0) {
            list.innerHTML = '<p class="backup-empty">No recovery points available</p>';
            return;
        }

        list.innerHTML = this.recoveryPoints.map(point => `
            <div class="recovery-point">
                <div class="point-info">
                    <div class="point-time">${new Date(point.timestamp * 1000).toLocaleString()}</div>
                    <div class="point-description">${point.description}</div>
                    <div class="point-templates">
                        ${point.template_ids.length} templates
                    </div>
                </div>
                <div class="point-actions">
                    <button class="recovery-restore-btn" data-backup-id="${point.backup_id}">
                        Restore to Point
                    </button>
                </div>
            </div>
        `).join('');

        list.querySelectorAll('.recovery-restore-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const backupId = e.target.getAttribute('data-backup-id');
                this.emit('restoreToPoint', { backupId });
            });
        });
    }

    createSchedule() {
        const typeSelect = this.container?.querySelector('.schedule-type');
        const intervalInput = this.container?.querySelector('.schedule-interval');
        const retentionInput = this.container?.querySelector('.schedule-retention');

        if (!typeSelect || !intervalInput || !retentionInput) return;

        this.emit('createSchedule', {
            backup_type: typeSelect.value,
            interval_hours: parseInt(intervalInput.value),
            retention_days: parseInt(retentionInput.value)
        });
    }

    refresh() {
        this.emit('refresh');
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i];
    }

    show() {
        if (this.container) this.container.style.display = 'block';
    }

    hide() {
        if (this.container) this.container.style.display = 'none';
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
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = BackupUI;
}
