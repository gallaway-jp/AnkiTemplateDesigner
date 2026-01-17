/**
 * Issue #41: Multi-Project Manager
 * 
 * Manages multiple template projects with localStorage persistence.
 * Provides CRUD operations, favorites, recent projects, and cloning.
 * 
 * Features:
 * - Create/list/delete/rename projects
 * - Toggle favorites
 * - Track recent projects
 * - Clone projects
 * - Search/filter
 * - Import/export
 */

class ProjectManager {
    /**
     * Initialize Project Manager with localStorage
     */
    constructor() {
        this.storageKey = 'atd_projects';
        this.recentKey = 'atd_recent_projects';
        this.currentKey = 'atd_current_project';
        
        this.projects = this.loadProjects();
        this.recentProjects = this.loadRecent();
        this.currentProject = this.loadCurrent();
        
        console.log('[ProjectManager] Initialized with', this.projects.length, 'projects');
    }
    
    /**
     * Create a new project
     * @param {string} name - Project name
     * @param {object} templateData - Optional template data
     * @returns {object} Created project
     */
    createProject(name, templateData = null) {
        const project = {
            id: this.generateId(),
            name: name || 'Untitled Project',
            created: new Date().toISOString(),
            modified: new Date().toISOString(),
            isFavorite: false,
            data: templateData || {}
        };
        
        this.projects.push(project);
        this.setCurrentProject(project.id);
        this.save();
        
        console.log('[ProjectManager] Created project:', project.id);
        this.emit('projectCreated', { project });
        
        return project;
    }
    
    /**
     * Get a project by ID
     * @param {string} projectId - Project ID
     * @returns {object|null} Project or null
     */
    getProject(projectId) {
        return this.projects.find(p => p.id === projectId) || null;
    }
    
    /**
     * List all projects (sorted by modified date)
     * @returns {array} Projects
     */
    listProjects() {
        return [...this.projects].sort((a, b) => 
            new Date(b.modified) - new Date(a.modified)
        );
    }
    
    /**
     * Delete a project
     * @param {string} projectId - Project ID
     * @returns {boolean} Success
     */
    deleteProject(projectId) {
        const index = this.projects.findIndex(p => p.id === projectId);
        if (index === -1) return false;
        
        this.projects.splice(index, 1);
        
        // Update current project if needed
        if (this.currentProject === projectId) {
            this.currentProject = this.projects.length > 0 ? this.projects[0].id : null;
        }
        
        // Remove from recent
        this.recentProjects = this.recentProjects.filter(id => id !== projectId);
        
        this.save();
        console.log('[ProjectManager] Deleted project:', projectId);
        this.emit('projectDeleted', { projectId });
        
        return true;
    }
    
    /**
     * Rename a project
     * @param {string} projectId - Project ID
     * @param {string} newName - New name
     * @returns {boolean} Success
     */
    renameProject(projectId, newName) {
        const project = this.getProject(projectId);
        if (!project) return false;
        
        project.name = newName;
        project.modified = new Date().toISOString();
        this.save();
        
        console.log('[ProjectManager] Renamed project:', projectId);
        this.emit('projectRenamed', { projectId, newName });
        
        return true;
    }
    
    /**
     * Toggle favorite status
     * @param {string} projectId - Project ID
     * @returns {boolean} New favorite status
     */
    toggleFavorite(projectId) {
        const project = this.getProject(projectId);
        if (!project) return false;
        
        project.isFavorite = !project.isFavorite;
        project.modified = new Date().toISOString();
        this.save();
        
        console.log('[ProjectManager] Toggled favorite:', projectId, project.isFavorite);
        this.emit('favoriteToggled', { projectId, isFavorite: project.isFavorite });
        
        return project.isFavorite;
    }
    
    /**
     * Get all favorite projects
     * @returns {array} Favorite projects
     */
    getFavorites() {
        return this.projects.filter(p => p.isFavorite);
    }
    
    /**
     * Set current active project
     * @param {string} projectId - Project ID
     * @returns {boolean} Success
     */
    setCurrentProject(projectId) {
        if (!this.getProject(projectId)) return false;
        
        this.currentProject = projectId;
        this.updateRecent(projectId);
        this.saveCurrentProject();
        
        console.log('[ProjectManager] Set current project:', projectId);
        this.emit('projectSwitched', { projectId });
        
        return true;
    }
    
    /**
     * Get current project
     * @returns {object|null} Current project
     */
    getCurrentProject() {
        return this.getProject(this.currentProject);
    }
    
    /**
     * Get recent projects
     * @param {number} limit - Max number of projects (default 5)
     * @returns {array} Recent projects
     */
    getRecent(limit = 5) {
        return this.recentProjects
            .slice(0, limit)
            .map(id => this.getProject(id))
            .filter(p => p !== null);
    }
    
    /**
     * Clone a project
     * @param {string} projectId - Project ID to clone
     * @param {string} newName - Name for cloned project
     * @returns {object|null} Cloned project
     */
    cloneProject(projectId, newName = null) {
        const original = this.getProject(projectId);
        if (!original) return null;
        
        const cloned = {
            id: this.generateId(),
            name: newName || `${original.name} (Copy)`,
            created: new Date().toISOString(),
            modified: new Date().toISOString(),
            isFavorite: false,
            data: JSON.parse(JSON.stringify(original.data)) // Deep copy
        };
        
        this.projects.push(cloned);
        this.setCurrentProject(cloned.id);
        this.save();
        
        console.log('[ProjectManager] Cloned project:', projectId, 'to', cloned.id);
        this.emit('projectCloned', { originalId: projectId, clonedProject: cloned });
        
        return cloned;
    }
    
    /**
     * Search projects by name
     * @param {string} query - Search query
     * @returns {array} Matching projects
     */
    searchProjects(query) {
        const q = query.toLowerCase();
        return this.projects.filter(p => 
            p.name.toLowerCase().includes(q)
        );
    }
    
    /**
     * Export project as JSON
     * @param {string} projectId - Project ID
     * @returns {string|null} JSON string
     */
    exportProject(projectId) {
        const project = this.getProject(projectId);
        if (!project) return null;
        
        return JSON.stringify(project, null, 2);
    }
    
    /**
     * Import project from JSON
     * @param {string} jsonData - JSON string
     * @param {string} newName - Optional new name
     * @returns {object|null} Imported project
     */
    importProject(jsonData, newName = null) {
        try {
            const project = JSON.parse(jsonData);
            
            // Validate required fields
            if (!project.data || typeof project.data !== 'object') {
                throw new Error('Invalid project data');
            }
            
            // Create new project with imported data
            const imported = {
                id: this.generateId(),
                name: newName || project.name || 'Imported Project',
                created: new Date().toISOString(),
                modified: new Date().toISOString(),
                isFavorite: false,
                data: JSON.parse(JSON.stringify(project.data))
            };
            
            this.projects.push(imported);
            this.setCurrentProject(imported.id);
            this.save();
            
            console.log('[ProjectManager] Imported project:', imported.id);
            this.emit('projectImported', { project: imported });
            
            return imported;
        } catch (error) {
            console.error('[ProjectManager] Import failed:', error.message);
            return null;
        }
    }
    
    /**
     * Update project template data
     * @param {string} projectId - Project ID
     * @param {object} templateData - Template data
     * @returns {boolean} Success
     */
    updateProjectData(projectId, templateData) {
        const project = this.getProject(projectId);
        if (!project) return false;
        
        project.data = templateData;
        project.modified = new Date().toISOString();
        this.save();
        
        console.log('[ProjectManager] Updated project data:', projectId);
        this.emit('projectDataUpdated', { projectId });
        
        return true;
    }
    
    /**
     * Get statistics about projects
     * @returns {object} Statistics
     */
    getStatistics() {
        return {
            totalProjects: this.projects.length,
            favorites: this.getFavorites().length,
            recent: this.recentProjects.length,
            currentProject: this.currentProject
        };
    }
    
    // ======================================================================
    // PRIVATE METHODS
    // ======================================================================
    
    /**
     * Generate unique project ID
     * @private
     * @returns {string} Project ID
     */
    generateId() {
        return `proj_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    /**
     * Update recent projects list
     * @private
     * @param {string} projectId - Project ID
     */
    updateRecent(projectId) {
        // Remove if exists
        this.recentProjects = this.recentProjects.filter(id => id !== projectId);
        // Add to beginning
        this.recentProjects.unshift(projectId);
        // Keep only 5
        this.recentProjects = this.recentProjects.slice(0, 5);
        this.saveRecent();
    }
    
    /**
     * Save projects to localStorage
     * @private
     */
    save() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.projects));
        } catch (error) {
            console.error('[ProjectManager] Save failed:', error.message);
        }
    }
    
    /**
     * Load projects from localStorage
     * @private
     * @returns {array} Projects
     */
    loadProjects() {
        try {
            const data = localStorage.getItem(this.storageKey);
            return data ? JSON.parse(data) : [];
        } catch (error) {
            console.error('[ProjectManager] Load failed:', error.message);
            return [];
        }
    }
    
    /**
     * Save recent projects list
     * @private
     */
    saveRecent() {
        try {
            localStorage.setItem(this.recentKey, JSON.stringify(this.recentProjects));
        } catch (error) {
            console.error('[ProjectManager] Save recent failed:', error.message);
        }
    }
    
    /**
     * Load recent projects list
     * @private
     * @returns {array} Recent project IDs
     */
    loadRecent() {
        try {
            const data = localStorage.getItem(this.recentKey);
            return data ? JSON.parse(data) : [];
        } catch (error) {
            console.error('[ProjectManager] Load recent failed:', error.message);
            return [];
        }
    }
    
    /**
     * Save current project ID
     * @private
     */
    saveCurrentProject() {
        try {
            if (this.currentProject) {
                localStorage.setItem(this.currentKey, this.currentProject);
            }
        } catch (error) {
            console.error('[ProjectManager] Save current failed:', error.message);
        }
    }
    
    /**
     * Load current project ID
     * @private
     * @returns {string|null} Current project ID
     */
    loadCurrent() {
        try {
            return localStorage.getItem(this.currentKey) || null;
        } catch (error) {
            console.error('[ProjectManager] Load current failed:', error.message);
            return null;
        }
    }
    
    /**
     * Event emission system
     * @private
     */
    emit(eventName, data) {
        const event = new CustomEvent(`projects:${eventName}`, { detail: data });
        document.dispatchEvent(event);
    }
}

/**
 * Initialize global project manager
 */
function initializeProjectManager() {
    if (typeof window !== 'undefined' && !window.projectManager) {
        window.projectManager = new ProjectManager();
        console.log('[ProjectManager] Global instance created');
        
        // Log initial state
        const stats = window.projectManager.getStatistics();
        console.log('[ProjectManager] Current state:', stats);
    }
}

// Initialize on load if not in test environment
if (typeof module === 'undefined' || !module.exports) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeProjectManager);
    } else {
        initializeProjectManager();
    }
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ProjectManager, initializeProjectManager };
}
