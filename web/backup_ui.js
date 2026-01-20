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
                            <div class="form-group">
                                <label>Timezone</label>
                                <select class="schedule-timezone">
                                    <option value="UTC">UTC</option>
                                    <option value="America/New_York">Eastern Time</option>
                                    <option value="America/Chicago">Central Time</option>
                                    <option value="America/Denver">Mountain Time</option>
                                    <option value="America/Los_Angeles">Pacific Time</option>
                                    <option value="Europe/London">London (GMT)</option>
                                    <option value="Europe/Paris">Central European Time</option>
                                    <option value="Asia/Tokyo">Japan Standard Time</option>
                                    <option value="Asia/Shanghai">China Standard Time</option>
                                    <option value="Asia/Singapore">Singapore Time</option>
                                    <option value="Australia/Sydney">Australian Eastern Time</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Time of Day (24-hour format)</label>
                                <input type="time" class="schedule-time" value="02:00">
                            </div>
                            <button class="backup-btn-primary">Create Schedule</button>
                        </div>

                        <div class="schedule-list"></div>
                    </div>

                    <!-- Recovery Tab -->
                    <div class="backup-section" data-section="recovery">
                        <div class="recovery-filters">
                            <div class="filter-group">
                                <input type="text" class="recovery-search" placeholder="Search recovery points...">
                            </div>
                            <div class="filter-group">
                                <label>Date Range:</label>
                                <input type="date" class="recovery-date-from">
                                <span>to</span>
                                <input type="date" class="recovery-date-to">
                            </div>
                            <div class="filter-group">
                                <label>Type:</label>
                                <select class="recovery-type-filter">
                                    <option value="">All Types</option>
                                    <option value="full">Full Backup</option>
                                    <option value="incremental">Incremental</option>
                                </select>
                            </div>
                            <div class="filter-group">
                                <label>Status:</label>
                                <select class="recovery-status-filter">
                                    <option value="">All Status</option>
                                    <option value="success">Successful</option>
                                    <option value="failed">Failed</option>
                                    <option value="pending">Pending</option>
                                </select>
                            </div>
                            <button class="recovery-filter-reset">Reset Filters</button>
                        </div>
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
        primaryBtns[0]?.addEventListener('click', () => {
            this.showBackupProgress('full');
            this.emit('createFullBackup');
        });
        primaryBtns[1]?.addEventListener('click', () => {
            this.showBackupProgress('incremental');
            this.emit('createIncremental');
        });

        // Schedule creation
        const scheduleBtn = this.container.querySelector('.backup-section[data-section="schedule"] .backup-btn-primary');
        if (scheduleBtn) {
            scheduleBtn.addEventListener('click', () => this.createSchedule());
        }

        // Recovery point filters
        const searchInput = this.container.querySelector('.recovery-search');
        const typeFilter = this.container.querySelector('.recovery-type-filter');
        const statusFilter = this.container.querySelector('.recovery-status-filter');
        const dateFromInput = this.container.querySelector('.recovery-date-from');
        const dateToInput = this.container.querySelector('.recovery-date-to');
        const resetBtn = this.container.querySelector('.recovery-filter-reset');

        // Filter change listeners
        [searchInput, typeFilter, statusFilter, dateFromInput, dateToInput].forEach(el => {
            if (el) {
                el.addEventListener('change', () => this.applyRecoveryPointFilters());
                if (el.tagName === 'INPUT' && el.type === 'text') {
                    el.addEventListener('input', () => {
                        clearTimeout(this.filterDebounceTimer);
                        this.filterDebounceTimer = setTimeout(() => this.applyRecoveryPointFilters(), 300);
                    });
                }
            }
        });

        // Reset button
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetRecoveryPointFilters());
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

        // Load data for recovery tab when switched
        if (tabName === 'recovery') {
            this.loadRecoveryPoints();
        } else if (tabName === 'backups') {
            this.loadBackupStats();
        }
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

        list.querySelectorAll('.backup-verify-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const backupId = e.target.getAttribute('data-backup-id');
                this.showVerifyProgress(backupId);
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
                    <div class="schedule-header">
                        <span class="schedule-type">${schedule.backup_type === 'full' ? '💾 Full' : '📊 Incremental'}</span>
                        <span class="schedule-interval">Every ${schedule.interval_hours}h</span>
                        <span class="schedule-status ${schedule.enabled ? 'enabled' : 'disabled'}">
                            ${schedule.enabled ? '✓ Active' : '⏸ Inactive'}
                        </span>
                    </div>
                    <div class="schedule-details">
                        <span class="detail-item">Retention: ${schedule.retention_days} days</span>
                        <span class="detail-item">Next run: ${schedule.next_run ? new Date(schedule.next_run * 1000).toLocaleString() : 'Unknown'}</span>
                        <span class="detail-item">Last run: ${schedule.last_run ? new Date(schedule.last_run * 1000).toLocaleString() : 'Never'}</span>
                    </div>
                </div>
                <div class="schedule-actions">
                    <button class="schedule-toggle-btn" data-schedule-id="${schedule.schedule_id}" title="Toggle Schedule">
                        ${schedule.enabled ? '⏸' : '▶'}
                    </button>
                    <button class="schedule-edit-btn" data-schedule-id="${schedule.schedule_id}" title="Edit Schedule">
                        ✎
                    </button>
                    <button class="schedule-delete-btn" data-schedule-id="${schedule.schedule_id}" title="Delete Schedule">
                        🗑
                    </button>
                </div>
            </div>
        `).join('');

        // Attach event listeners
        list.querySelectorAll('.schedule-toggle-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const scheduleId = e.target.getAttribute('data-schedule-id');
                this.emit('toggleSchedule', { scheduleId });
            });
        });

        list.querySelectorAll('.schedule-edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const scheduleId = e.target.getAttribute('data-schedule-id');
                this.showScheduleEditModal(scheduleId);
            });
        });

        list.querySelectorAll('.schedule-delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const scheduleId = e.target.getAttribute('data-schedule-id');
                if (confirm('Delete this schedule? (Existing backups will not be deleted)')) {
                    this.emit('deleteSchedule', { scheduleId });
                    showToast('Schedule deleted', 'success', 3000);
                }
            });
        });
    }

    updateRecoveryPoints(points) {
        this.recoveryPoints = points;
        this.filteredRecoveryPoints = [...points];
        this.renderRecoveryPoints();
    }

    renderRecoveryPoints() {
        const list = this.container?.querySelector('.recovery-points');
        if (!list) return;

        if (this.filteredRecoveryPoints.length === 0) {
            list.innerHTML = '<p class="backup-empty">No recovery points available</p>';
            return;
        }

        list.innerHTML = this.filteredRecoveryPoints.map(point => `
            <div class="recovery-point" data-point-id="${point.backup_id}">
                <div class="point-status status-${point.status || 'success'}">
                    ${this.getStatusIcon(point.status)}
                </div>
                <div class="point-info">
                    <div class="point-time">${new Date(point.timestamp * 1000).toLocaleString()}</div>
                    <div class="point-description">${point.description}</div>
                    <div class="point-metadata">
                        <span class="point-type">${point.type || 'full'}</span>
                        <span class="point-templates">${point.template_count || 0} templates</span>
                        <span class="point-size">${(point.size_mb || 0).toFixed(1)} MB</span>
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
                this.selectRecoveryPoint(backupId);
            });
        });
    }

    getStatusIcon(status) {
        switch (status) {
            case 'success': return '✓';
            case 'failed': return '✗';
            case 'pending': return '⟳';
            default: return '○';
        }
    }

    applyRecoveryPointFilters() {
        const searchVal = this.container?.querySelector('.recovery-search')?.value.toLowerCase() || '';
        const typeVal = this.container?.querySelector('.recovery-type-filter')?.value || '';
        const statusVal = this.container?.querySelector('.recovery-status-filter')?.value || '';
        const dateFromVal = this.container?.querySelector('.recovery-date-from')?.value || '';
        const dateToVal = this.container?.querySelector('.recovery-date-to')?.value || '';

        this.filteredRecoveryPoints = this.recoveryPoints.filter(point => {
            // Search filter
            if (searchVal) {
                const searchFields = [
                    point.description || '',
                    point.backup_id || '',
                    (point.template_count || 0).toString()
                ].join(' ').toLowerCase();
                if (!searchFields.includes(searchVal)) return false;
            }

            // Type filter
            if (typeVal && (point.type || 'full') !== typeVal) {
                return false;
            }

            // Status filter
            if (statusVal && (point.status || 'success') !== statusVal) {
                return false;
            }

            // Date range filter
            if (dateFromVal || dateToVal) {
                const pointDate = new Date(point.timestamp * 1000).toISOString().split('T')[0];
                if (dateFromVal && pointDate < dateFromVal) return false;
                if (dateToVal && pointDate > dateToVal) return false;
            }

            return true;
        });

        this.renderRecoveryPoints();
    }

    resetRecoveryPointFilters() {
        this.container?.querySelector('.recovery-search').value = '';
        this.container?.querySelector('.recovery-type-filter').value = '';
        this.container?.querySelector('.recovery-status-filter').value = '';
        this.container?.querySelector('.recovery-date-from').value = '';
        this.container?.querySelector('.recovery-date-to').value = '';
        
        this.filteredRecoveryPoints = [...this.recoveryPoints];
        this.renderRecoveryPoints();
    }

    showBackupProgress(backupType) {
        const list = this.container?.querySelector('.backup-list');
        if (!list) return;

        const progressHtml = `
            <div class="backup-progress" id="backup-progress-${Date.now()}">
                <div class="progress-header">
                    <span class="progress-title">Creating ${backupType} backup...</span>
                    <span class="progress-cancel">✕</span>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar" style="width: 0%"></div>
                </div>
                <div class="progress-text">Starting...</div>
                <div class="progress-details">
                    <span class="progress-size">0 MB</span>
                    <span class="progress-speed">0 MB/s</span>
                </div>
            </div>
        `;

        // Insert at top of list
        list.insertAdjacentHTML('beforebegin', progressHtml);

        // Setup progress update listener
        const progressId = `backup-progress-${Date.now()}`;
        const progressEl = document.getElementById(progressId);

        // Simulate/listen for progress updates
        if (window.bridge && window.bridge.onBackupProgress) {
            window.bridge.onBackupProgress((progress) => {
                if (progressEl) {
                    const progressBar = progressEl.querySelector('.progress-bar');\n                    const progressText = progressEl.querySelector('.progress-text');
                    const progressSize = progressEl.querySelector('.progress-size');
                    const progressSpeed = progressEl.querySelector('.progress-speed');

                    if (progressBar) progressBar.style.width = `${progress.percent}%`;
                    if (progressText) progressText.textContent = progress.status || `${progress.percent}%`;
                    if (progressSize) progressSize.textContent = `${(progress.size_mb || 0).toFixed(1)} MB`;
                    if (progressSpeed) progressSpeed.textContent = `${(progress.speed_mb_s || 0).toFixed(1)} MB/s`;

                    // Remove when complete
                    if (progress.percent === 100 || progress.status === 'completed') {
                        setTimeout(() => {
                            if (progressEl.parentNode) progressEl.parentNode.removeChild(progressEl);\n                            showToast(`${backupType} backup completed successfully`, 'success', 4000);
                            // Reload backups
                            this.loadBackupStats();
                        }, 1000);
                    }
                }
            });
        }

        // Cancel button
        const cancelBtn = progressEl?.querySelector('.progress-cancel');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                if (window.bridge && window.bridge.cancelBackup) {
                    window.bridge.cancelBackup();
                }
                if (progressEl.parentNode) progressEl.parentNode.removeChild(progressEl);
                showToast('Backup cancelled', 'warning', 3000);
            });
        }
    }

    createSchedule() {
        const typeSelect = this.container?.querySelector('.schedule-type');
        const intervalInput = this.container?.querySelector('.schedule-interval');
        const retentionInput = this.container?.querySelector('.schedule-retention');
        const timezoneSelect = this.container?.querySelector('.schedule-timezone');
        const timeInput = this.container?.querySelector('.schedule-time');

        if (!typeSelect || !intervalInput || !retentionInput || !timezoneSelect || !timeInput) return;

        // Validate inputs
        const intervalHours = parseInt(intervalInput.value);
        const retentionDays = parseInt(retentionInput.value);
        const timezone = timezoneSelect.value;
        const timeOfDay = timeInput.value; // HH:MM format

        if (isNaN(intervalHours) || intervalHours < 1) {
            showToast('Interval must be at least 1 hour', 'error', 3000);
            return;
        }

        if (isNaN(retentionDays) || retentionDays < 1) {
            showToast('Retention must be at least 1 day', 'error', 3000);
            return;
        }

        // Emit event with validated data
        this.emit('createSchedule', {
            backup_type: typeSelect.value,
            interval_hours: intervalHours,
            retention_days: retentionDays,
            timezone: timezone,
            time_of_day: timeOfDay
        });

        // Show confirmation
        showToast(`Schedule created: ${typeSelect.value} backup every ${intervalHours}h at ${timeOfDay} ${timezone}`, 'success', 3000);
        
        // Reset form
        typeSelect.value = 'full';
        intervalInput.value = '24';
        retentionInput.value = '30';
        timezoneSelect.value = 'UTC';
        timeInput.value = '02:00';
    }

    refresh() {
        this.loadRecoveryPoints();
        this.loadBackupStats();
        this.emit('refresh');
    }

    loadRecoveryPoints() {
        if (!window.bridge || !window.bridge.getBackupList) {
            console.error('[BackupUI] Bridge not available for loading recovery points');
            return;
        }

        try {
            const backupsJson = window.bridge.getBackupList();
            const backups = JSON.parse(backupsJson);
            
            // Convert backups to recovery points
            const recoveryPoints = backups.map(backup => ({
                backup_id: backup.backup_id,
                timestamp: new Date(backup.timestamp).getTime() / 1000,
                description: `${backup.backup_type} backup - ${backup.template_count} templates`,
                template_ids: [],
                template_count: backup.template_count,
                size: backup.size,
                success: backup.success
            }));

            this.updateRecoveryPoints(recoveryPoints);
            showToast('Recovery points loaded', 'success', 2000);
        } catch (e) {
            console.error('[BackupUI] Error loading recovery points:', e);
            showToast('Failed to load recovery points', 'error', 3000);
        }
    }

    loadBackupStats() {
        if (!window.bridge || !window.bridge.getBackupStats) {
            console.error('[BackupUI] Bridge not available for loading stats');
            return;
        }

        try {
            const statsJson = window.bridge.getBackupStats();
            const stats = JSON.parse(statsJson);
            
            this.updateStats(stats);
            showToast('Backup statistics updated', 'success', 2000);
        } catch (e) {
            console.error('[BackupUI] Error loading backup stats:', e);
            showToast('Failed to load backup statistics', 'error', 3000);
        }
    }

    selectRecoveryPoint(backupId) {
        if (confirm('Restore this backup? This will overwrite your current templates.')) {
            this.restoreRecoveryPoint(backupId);
        }
    }

    restoreRecoveryPoint(backupId) {
        if (!window.bridge || !window.bridge.restoreBackup) {
            console.error('[BackupUI] Bridge not available for restoring backup');
            showToast('Restore functionality not available', 'error', 3000);
            return;
        }

        try {
            const success = window.bridge.restoreBackup(backupId);
            if (success) {
                showToast('Backup restored successfully. Templates reloaded.', 'success', 3000);
                // Reload recovery points list
                this.loadRecoveryPoints();
                // Emit event for UI to reload templates
                this.emit('backupRestored', { backupId });
            } else {
                showToast('Failed to restore backup', 'error', 3000);
            }
        } catch (e) {
            console.error('[BackupUI] Error restoring backup:', e);
            showToast('Error restoring backup: ' + e.message, 'error', 3000);
        }
    }

    showVerifyProgress(backupId) {
        // Create a progress container for verification
        const progressEl = document.createElement('div');
        progressEl.className = 'backup-verify-progress';
        progressEl.innerHTML = `
            <div class="backup-verify-modal">
                <div class="backup-verify-header">
                    <h4>Verifying Backup Integrity</h4>
                    <button class="backup-verify-close" aria-label="Close">✕</button>
                </div>
                <div class="backup-verify-content">
                    <div class="backup-verify-bar-container">
                        <div class="backup-verify-bar" id="verify-bar"></div>
                    </div>
                    <div class="backup-verify-status">
                        <span class="verify-status-text" id="verify-status">Starting verification...</span>
                        <span class="verify-status-percent" id="verify-percent">0%</span>
                    </div>
                    <div class="backup-verify-details" id="verify-details">
                        <p class="verify-detail-line">Checking archive integrity...</p>
                    </div>
                </div>
                <div class="backup-verify-footer">
                    <button class="backup-cancel-verify-btn">Cancel</button>
                    <button class="backup-verify-done-btn" style="display: none;">Done</button>
                </div>
            </div>
        `;

        // Add to container
        if (this.container) {
            this.container.appendChild(progressEl);
        } else {
            document.body.appendChild(progressEl);
        }

        // Get references to elements
        const closeBtn = progressEl.querySelector('.backup-verify-close');
        const cancelBtn = progressEl.querySelector('.backup-cancel-verify-btn');
        const doneBtn = progressEl.querySelector('.backup-verify-done-btn');
        const verifyBar = progressEl.querySelector('#verify-bar');
        const statusText = progressEl.querySelector('#verify-status');
        const percentText = progressEl.querySelector('#verify-percent');
        const detailsDiv = progressEl.querySelector('#verify-details');

        // Emit event to start verification
        this.emit('verifyBackup', { backupId });

        // Listen for verification progress
        if (window.bridge && window.bridge.onBackupVerifyProgress) {
            window.bridge.onBackupVerifyProgress((progress) => {
                if (progress && typeof progress.percent !== 'undefined') {
                    const percent = Math.min(100, progress.percent);
                    verifyBar.style.width = percent + '%';
                    percentText.textContent = percent + '%';
                    
                    if (progress.status) {
                        statusText.textContent = progress.status;
                    }

                    if (progress.detail) {
                        detailsDiv.innerHTML += `<p class="verify-detail-line">${progress.detail}</p>`;
                        // Scroll to bottom of details
                        detailsDiv.scrollTop = detailsDiv.scrollHeight;
                    }

                    // Check if verification completed
                    if (percent === 100) {
                        cancelBtn.style.display = 'none';
                        doneBtn.style.display = 'inline-block';
                        
                        // Show final result
                        if (progress.result === 'success') {
                            statusText.textContent = '✓ Backup verified successfully';
                            showToast('Backup verification passed', 'success', 3000);
                        } else if (progress.result === 'failed') {
                            statusText.textContent = '✗ Backup verification failed';
                            showToast('Backup verification failed: ' + (progress.error || 'Unknown error'), 'error', 5000);
                        }
                    }
                }
            });
        }

        // Close handlers
        closeBtn.addEventListener('click', () => {
            if (progressEl.parentNode) progressEl.parentNode.removeChild(progressEl);
        });

        cancelBtn.addEventListener('click', () => {
            if (window.bridge && window.bridge.cancelBackupVerify) {
                window.bridge.cancelBackupVerify();
            }
            if (progressEl.parentNode) progressEl.parentNode.removeChild(progressEl);
            showToast('Backup verification cancelled', 'warning', 3000);
        });

        doneBtn.addEventListener('click', () => {
            if (progressEl.parentNode) progressEl.parentNode.removeChild(progressEl);
        });
    }

    showScheduleEditModal(scheduleId) {
        // Find the schedule
        const schedule = this.schedules.find(s => s.schedule_id === scheduleId);
        if (!schedule) return;

        // Create modal
        const modal = document.createElement('div');
        modal.className = 'backup-schedule-modal';
        modal.innerHTML = `
            <div class="backup-modal-overlay">
                <div class="backup-modal-content">
                    <div class="backup-modal-header">
                        <h3>Edit Schedule</h3>
                        <button class="backup-modal-close" aria-label="Close">✕</button>
                    </div>
                    <div class="backup-modal-body">
                        <div class="form-group">
                            <label>Backup Type</label>
                            <select class="edit-schedule-type">
                                <option value="full" ${schedule.backup_type === 'full' ? 'selected' : ''}>Full Backup</option>
                                <option value="incremental" ${schedule.backup_type === 'incremental' ? 'selected' : ''}>Incremental</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Interval (hours)</label>
                            <input type="number" class="edit-schedule-interval" value="${schedule.interval_hours}" min="1">
                        </div>
                        <div class="form-group">
                            <label>Retention (days)</label>
                            <input type="number" class="edit-schedule-retention" value="${schedule.retention_days}" min="1">
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" class="edit-schedule-enabled" ${schedule.enabled ? 'checked' : ''}>
                                Enabled
                            </label>
                        </div>
                    </div>
                    <div class="backup-modal-footer">
                        <button class="backup-btn-secondary backup-modal-cancel">Cancel</button>
                        <button class="backup-btn-primary backup-modal-save">Save Changes</button>
                    </div>
                </div>
            </div>
        `;

        // Add to DOM
        if (this.container) {
            this.container.appendChild(modal);
        } else {
            document.body.appendChild(modal);
        }

        // Event handlers
        const closeBtn = modal.querySelector('.backup-modal-close');
        const cancelBtn = modal.querySelector('.backup-modal-cancel');
        const saveBtn = modal.querySelector('.backup-modal-save');

        const typeSelect = modal.querySelector('.edit-schedule-type');
        const intervalInput = modal.querySelector('.edit-schedule-interval');
        const retentionInput = modal.querySelector('.edit-schedule-retention');
        const enabledCheckbox = modal.querySelector('.edit-schedule-enabled');

        const closeModal = () => {
            if (modal.parentNode) modal.parentNode.removeChild(modal);
        };

        closeBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);

        saveBtn.addEventListener('click', () => {
            // Validate inputs
            const intervalHours = parseInt(intervalInput.value);
            const retentionDays = parseInt(retentionInput.value);

            if (isNaN(intervalHours) || intervalHours < 1) {
                showToast('Interval must be at least 1 hour', 'error', 3000);
                return;
            }

            if (isNaN(retentionDays) || retentionDays < 1) {
                showToast('Retention must be at least 1 day', 'error', 3000);
                return;
            }

            // Emit update event
            this.emit('updateSchedule', {
                scheduleId: scheduleId,
                backup_type: typeSelect.value,
                interval_hours: intervalHours,
                retention_days: retentionDays,
                enabled: enabledCheckbox.checked
            });

            showToast('Schedule updated', 'success', 3000);
            closeModal();
        });

        // Close on overlay click
        modal.querySelector('.backup-modal-overlay').addEventListener('click', (e) => {
            if (e.target === modal.querySelector('.backup-modal-overlay')) {
                closeModal();
            }
        });
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
