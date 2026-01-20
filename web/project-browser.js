/**
 * Issue #41: Project Browser UI
 * 
 * User interface for browsing, searching, and managing projects.
 * Provides views for:
 * - Project list
 * - Recent projects
 * - Favorites
 * - Search interface
 */

class ProjectBrowser {
    /**
     * Initialize Project Browser UI
     * @param {HTMLElement} container - Container element
     * @param {ProjectManager} manager - ProjectManager instance
     */
    constructor(container, manager) {
        this.container = container;
        this.manager = manager;
        this.currentView = 'list';
        this.searchQuery = '';
        this.lastProjectIds = new Set(); // Track projects for highlighting new ones
        this.newlyAddedProjects = new Set(); // Projects added in current session
        this.isRefreshingFromProjectChange = false; // Flag to prevent search loss
        
        this.render();
        this.attachEventListeners();
        
        // Listen for project manager events with special handling
        document.addEventListener('projects:projectCreated', (e) => {
            this.handleProjectCreated(e);
        });
        document.addEventListener('projects:projectDeleted', () => {
            this.handleProjectDeleted();
        });
        document.addEventListener('projects:projectRenamed', () => {
            this.handleProjectRenamed();
        });
        document.addEventListener('projects:favoriteToggled', () => {
            this.refresh();
        });
        document.addEventListener('projects:projectSwitched', () => {
            this.refresh();
        });
        document.addEventListener('projects:projectCloned', (e) => {
            this.handleProjectCloned(e);
        });
        
        console.log('[ProjectBrowser] Initialized');
    }
    
    /**
     * Render the project browser UI
     */
    render() {
        this.container.innerHTML = `
            <div class="project-browser">
                <!-- Header -->
                <div class="browser-header">
                    <h2 class="browser-title">Projects</h2>
                    <button class="btn-create-project" title="Create new project (Ctrl+N)">
                        <span class="icon">➕</span>
                        New
                    </button>
                </div>
                
                <!-- Tabs -->
                <div class="browser-tabs">
                    <button class="tab-btn active" data-tab="list">
                        <span class="icon">📋</span> All
                    </button>
                    <button class="tab-btn" data-tab="recent">
                        <span class="icon">⏱️</span> Recent
                    </button>
                    <button class="tab-btn" data-tab="favorites">
                        <span class="icon">⭐</span> Favorites
                    </button>
                </div>
                
                <!-- Search -->
                <div class="browser-search">
                    <input 
                        type="text" 
                        class="search-input" 
                        placeholder="Search projects..."
                        aria-label="Search projects"
                    >
                    <span class="search-icon">🔍</span>
                </div>
                
                <!-- Project List -->
                <div class="project-list" role="list">
                    <!-- Projects rendered here -->
                </div>
                
                <!-- Empty State -->
                <div class="empty-state" style="display: none;">
                    <span class="empty-icon">📭</span>
                    <p>No projects yet</p>
                    <button class="btn-create-project secondary">Create Your First Project</button>
                </div>
                
                <!-- Statistics -->
                <div class="browser-stats">
                    <div class="stat">
                        <span class="stat-label">Total Projects</span>
                        <span class="stat-value projects-count">0</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Favorites</span>
                        <span class="stat-value favorites-count">0</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Create project buttons
        this.container.querySelectorAll('.btn-create-project').forEach(btn => {
            btn.addEventListener('click', () => this.createProject());
        });
        
        // Tab switching
        this.container.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.currentView = e.currentTarget.dataset.tab;
                this.updateTabs();
                this.refresh();
            });
        });
        
        // Search with debouncing to maintain query during list updates
        const searchInput = this.container.querySelector('.search-input');
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            this.searchQuery = e.target.value;
            
            // Clear existing timeout
            if (searchTimeout) {
                clearTimeout(searchTimeout);
            }
            
            // Debounce the search refresh
            searchTimeout = setTimeout(() => {
                this.refresh();
            }, 300);
        });
    }
    
    /**
     * Refresh the project list
     */
    refresh() {
        this.renderProjectList();
        this.updateStats();
    }
    
    /**
     * Render the project list based on current view
     */
    renderProjectList() {
        let projects = [];
        
        // Get projects based on current view
        if (this.currentView === 'recent') {
            projects = this.manager.getRecent(10);
        } else if (this.currentView === 'favorites') {
            projects = this.manager.getFavorites();
        } else {
            projects = this.manager.listProjects();
        }
        
        // Apply search filter
        if (this.searchQuery) {
            projects = projects.filter(p => 
                p.name.toLowerCase().includes(this.searchQuery.toLowerCase())
            );
        }
        
        const listContainer = this.container.querySelector('.project-list');
        const emptyState = this.container.querySelector('.empty-state');
        
        if (projects.length === 0) {
            listContainer.innerHTML = '';
            emptyState.style.display = 'block';
            return;
        }
        
        emptyState.style.display = 'none';
        
        // Track current projects for future comparisons
        const currentIds = new Set(projects.map(p => p.id));
        
        listContainer.innerHTML = projects.map(project => {
            const isNew = this.newlyAddedProjects.has(project.id);
            const newBadgeHtml = isNew ? `<span class="new-project-badge" title="New project added">NEW</span>` : '';
            
            return `
            <div class="project-item ${this.isCurrentProject(project.id) ? 'active' : ''} ${isNew ? 'newly-added' : ''}" 
                 data-project-id="${project.id}" 
                 role="listitem">
                
                <!-- Main content -->
                <div class="project-content" style="flex: 1;">
                    <!-- Name and favorite -->
                    <div class="project-header">
                        <h3 class="project-name">
                            ${this.escapeHtml(project.name)}
                            ${newBadgeHtml}
                        </h3>
                        <button class="btn-favorite" 
                                data-project-id="${project.id}"
                                title="${project.isFavorite ? 'Remove from favorites' : 'Add to favorites'}"
                                aria-pressed="${project.isFavorite}">
                            <span class="icon">${project.isFavorite ? '⭐' : '☆'}</span>
                        </button>
                    </div>
                    
                    <!-- Metadata -->
                    <div class="project-meta">
                        <span class="meta-item">
                            <span class="meta-label">Modified:</span>
                            <span class="meta-value" title="${project.modified}">
                                ${this.formatDate(project.modified)}
                            </span>
                        </span>
                        <span class="meta-item">
                            <span class="meta-label">Created:</span>
                            <span class="meta-value" title="${project.created}">
                                ${this.formatDate(project.created)}
                            </span>
                        </span>
                    </div>
                </div>
                
                <!-- Actions -->
                <div class="project-actions">
                    <button class="btn-action btn-open" 
                            data-project-id="${project.id}"
                            title="Open project">
                        📂 Open
                    </button>
                    <button class="btn-action btn-rename" 
                            data-project-id="${project.id}"
                            title="Rename project">
                        ✏️
                    </button>
                    <button class="btn-action btn-clone" 
                            data-project-id="${project.id}"
                            title="Clone project">
                        📋
                    </button>
                    <button class="btn-action btn-export" 
                            data-project-id="${project.id}"
                            title="Export as JSON">
                        💾
                    </button>
                    <button class="btn-action btn-delete" 
                            data-project-id="${project.id}"
                            title="Delete project">
                        🗑️
                    </button>
                </div>
            </div>
        `;}).join('');
        
        // Attach action listeners
        this.attachProjectActions();
        
        // Clear new project indicators after a delay
        this.scheduleNewProjectIndicatorClear();
        
        // Update last seen project IDs
        this.lastProjectIds = currentIds;
    }
    
    /**
     * Attach event listeners to project actions
     */
    attachProjectActions() {
        // Open project
        this.container.querySelectorAll('.btn-open').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const projectId = e.currentTarget.dataset.projectId;
                this.openProject(projectId);
            });
        });
        
        // Favorite toggle
        this.container.querySelectorAll('.btn-favorite').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const projectId = e.currentTarget.dataset.projectId;
                this.manager.toggleFavorite(projectId);
            });
        });
        
        // Rename
        this.container.querySelectorAll('.btn-rename').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const projectId = e.currentTarget.dataset.projectId;
                this.renameProject(projectId);
            });
        });
        
        // Clone
        this.container.querySelectorAll('.btn-clone').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const projectId = e.currentTarget.dataset.projectId;
                this.cloneProject(projectId);
            });
        });
        
        // Export
        this.container.querySelectorAll('.btn-export').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const projectId = e.currentTarget.dataset.projectId;
                this.exportProject(projectId);
            });
        });
        
        // Delete
        this.container.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const projectId = e.currentTarget.dataset.projectId;
                this.deleteProject(projectId);
            });
        });
    }
    
    /**
     * Update active tab
     */
    updateTabs() {
        this.container.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === this.currentView);
        });
    }
    
    /**
     * Create a new project
     */
    createProject() {
        const name = prompt('Project name:');
        if (name === null) return; // Cancel
        
        const trimmedName = name.trim() || 'Untitled Project';
        
        try {
            showToast(`Creating project "${trimmedName}"...`, 'info', 2000);
            this.manager.createProject(trimmedName);
            showToast(`✓ Project "${trimmedName}" created successfully!`, 'success', 3000);
            this.refresh();
        } catch (error) {
            console.error('[ProjectBrowser] Error creating project:', error);
            showToast(`✗ Failed to create project: ${error.message}`, 'error', 4000);
        }
    }
    
    /**
     * Open a project
     * @param {string} projectId - Project ID
     */
    openProject(projectId) {
        try {
            const project = this.manager.getProject(projectId);
            showToast(`Opening project "${project?.name}"...`, 'info', 2000);
            
            const success = this.manager.setCurrentProject(projectId);
            if (success) {
                console.log('[ProjectBrowser] Opened project:', projectId);
                showToast(`✓ Opened "${project?.name}"`, 'success', 2000);
                this.emit('projectOpened', { projectId });
                this.refresh();
            } else {
                showToast(`✗ Failed to open project`, 'error', 3000);
            }
        } catch (error) {
            console.error('[ProjectBrowser] Error opening project:', error);
            showToast(`✗ Error: ${error.message}`, 'error', 4000);
        }
    }
    
    /**
     * Rename a project
     * @param {string} projectId - Project ID
     */
    renameProject(projectId) {
        const project = this.manager.getProject(projectId);
        if (!project) {
            showToast('Project not found', 'error', 3000);
            return;
        }
        
        const newName = prompt('New project name:', project.name);
        if (newName === null) return; // Cancel
        
        const trimmedName = newName.trim() || project.name;
        
        try {
            showToast(`Renaming project to "${trimmedName}"...`, 'info', 2000);
            this.manager.renameProject(projectId, trimmedName);
            showToast(`✓ Project renamed to "${trimmedName}"`, 'success', 3000);
            this.refresh();
        } catch (error) {
            console.error('[ProjectBrowser] Error renaming project:', error);
            showToast(`✗ Failed to rename: ${error.message}`, 'error', 4000);
        }
    }
    
    /**
     * Clone a project
     * @param {string} projectId - Project ID
     */
    cloneProject(projectId) {
        const project = this.manager.getProject(projectId);
        if (!project) {
            showToast('Project not found', 'error', 3000);
            return;
        }
        
        const newName = prompt('Clone name:', `${project.name} (Copy)`);
        if (newName === null) return; // Cancel
        
        const trimmedName = newName.trim();
        
        try {
            showToast(`Creating clone "${trimmedName}"...`, 'info', 2000);
            this.manager.cloneProject(projectId, trimmedName);
            showToast(`✓ Project cloned to "${trimmedName}"`, 'success', 3000);
            this.refresh();
        } catch (error) {
            console.error('[ProjectBrowser] Error cloning project:', error);
            showToast(`✗ Failed to clone: ${error.message}`, 'error', 4000);
        }
    }
    
    /**
     * Export a project
     * @param {string} projectId - Project ID
     */
    exportProject(projectId) {
        try {
            const project = this.manager.getProject(projectId);
            showToast(`Exporting project "${project?.name}"...`, 'info', 2000);
            
            const jsonData = this.manager.exportProject(projectId);
            if (!jsonData) {
                showToast('Failed to export project', 'error', 3000);
                return;
            }
            
            const blob = new Blob([jsonData], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `${project?.name || projectId}.json`;
            a.click();
            
            URL.revokeObjectURL(url);
            
            console.log('[ProjectBrowser] Exported project:', projectId);
            showToast(`✓ Project "${project?.name}" exported successfully!`, 'success', 3000);
        } catch (error) {
            console.error('[ProjectBrowser] Error exporting project:', error);
            showToast(`✗ Export failed: ${error.message}`, 'error', 4000);
        }
    }
    
    /**
     * Delete a project with confirmation
     * @param {string} projectId - Project ID
     */
    deleteProject(projectId) {
        const project = this.manager.getProject(projectId);
        if (!project) {
            showToast('Project not found', 'error', 3000);
            return;
        }
        
        // Show confirmation dialog
        const confirmed = confirm(`🗑️ Delete "${project.name}"?\n\nThis action cannot be undone. All templates and data will be permanently deleted.`);
        if (!confirmed) {
            return; // User cancelled
        }
        
        try {
            showToast(`Deleting project "${project.name}"...`, 'warning', 2000);
            this.manager.deleteProject(projectId);
            showToast(`✓ Project "${project.name}" deleted`, 'success', 3000);
            this.refresh();
        } catch (error) {
            console.error('[ProjectBrowser] Error deleting project:', error);
            showToast(`✗ Failed to delete: ${error.message}`, 'error', 4000);
        }
    }
    
    /**
     * Handle project creation event
     * @param {CustomEvent} e - Event with project details
     */
    handleProjectCreated(e) {
        const projectId = e.detail?.projectId;
        if (projectId) {
            this.newlyAddedProjects.add(projectId);
        }
        // Maintain search query and refresh
        this.refresh();
    }
    
    /**
     * Handle project deletion event
     */
    handleProjectDeleted() {
        // Clear new project indicators if deleted project was new
        this.newlyAddedProjects.clear();
        this.refresh();
    }
    
    /**
     * Handle project rename event
     */
    handleProjectRenamed() {
        // Keep search query, just refresh the display
        this.refresh();
    }
    
    /**
     * Handle project clone event
     * @param {CustomEvent} e - Event with cloned project details
     */
    handleProjectCloned(e) {
        const projectId = e.detail?.projectId;
        if (projectId) {
            this.newlyAddedProjects.add(projectId);
        }
        // Maintain search query and refresh
        this.refresh();
    }
    
    /**
     * Schedule clearing of new project indicators after delay
     */
    scheduleNewProjectIndicatorClear() {
        // Clear after 5 seconds or when user interacts with list
        setTimeout(() => {
            this.newlyAddedProjects.clear();
            // Re-render without "new" badges
            this.renderProjectList();
        }, 5000);
    }
    
    /**
     * Update statistics display
     */
    updateStats() {
        const stats = this.manager.getStatistics();
        this.container.querySelector('.projects-count').textContent = stats.totalProjects;
        this.container.querySelector('.favorites-count').textContent = stats.favorites;
    }
    
    /**
     * Check if project is current
     * @param {string} projectId - Project ID
     * @returns {boolean}
     */
    isCurrentProject(projectId) {
        return this.manager.currentProject === projectId;
    }
    
    /**
     * Format date for display
     * @param {string} isoDate - ISO date string
     * @returns {string} Formatted date
     */
    formatDate(isoDate) {
        try {
            const date = new Date(isoDate);
            const now = new Date();
            const diff = now - date;
            const minutes = Math.floor(diff / 60000);
            const hours = Math.floor(minutes / 60);
            const days = Math.floor(hours / 24);
            
            if (minutes < 1) return 'Just now';
            if (minutes < 60) return `${minutes}m ago`;
            if (hours < 24) return `${hours}h ago`;
            if (days < 7) return `${days}d ago`;
            
            return date.toLocaleDateString();
        } catch (error) {
            return isoDate;
        }
    }
    
    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Emit custom event
     * @param {string} eventName - Event name
     * @param {object} data - Event data
     */
    emit(eventName, data) {
        const event = new CustomEvent(`projectBrowser:${eventName}`, { detail: data });
        document.dispatchEvent(event);
    }
}

/**
 * Initialize project browser when DOM is ready
 */
function initializeProjectBrowser() {
    if (typeof window !== 'undefined' && window.projectManager) {
        const container = document.getElementById('project-browser');
        if (container && !window.projectBrowser) {
            window.projectBrowser = new ProjectBrowser(container, window.projectManager);
            console.log('[ProjectBrowser] UI initialized');
        }
    }
}

// Initialize on DOM ready
if (typeof module === 'undefined' || !module.exports) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeProjectBrowser);
    } else {
        initializeProjectBrowser();
    }
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ProjectBrowser, initializeProjectBrowser };
}
