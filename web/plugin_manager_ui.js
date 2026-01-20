/**
 * Plugin Manager UI - Issue #58
 * Interface for managing plugins, viewing marketplace, and configuration
 */

class PluginManagerUI {
  constructor() {
    this.plugins = [];
    this.marketplace = [];
    this.selectedTab = 'installed';
    
    // Marketplace optimization
    this.marketplaceCache = null;
    this.marketplaceCacheTime = 0;
    this.cacheDuration = 5 * 60 * 1000; // 5 minutes
    
    // Pagination
    this.marketplacePageSize = 12;
    this.marketplaceCurrentPage = 1;
    this.marketplaceFiltered = [];
    
    this.init();
  }

  init() {
    this.createUI();
    this.attachEventListeners();
    this.loadPlugins();
  }

  createUI() {
    const container = document.getElementById('plugin-manager-container') || document.body;
    
    container.innerHTML = `
      <div class="plugin-manager-panel">
        <div class="plugin-header">
          <h2>Plugin Manager</h2>
          <div class="plugin-stats">
            <span id="plugin-count">0 plugins</span>
            <span class="divider">|</span>
            <span id="plugin-enabled">0 enabled</span>
          </div>
        </div>

        <div class="plugin-tabs">
          <button class="tab-button active" data-tab="installed">Installed</button>
          <button class="tab-button" data-tab="marketplace">Marketplace</button>
          <button class="tab-button" data-tab="settings">Settings</button>
        </div>

        <!-- Installed Plugins Tab -->
        <div class="tab-content active" id="tab-installed">
          <div class="plugin-search">
            <input type="text" id="search-installed" placeholder="Search plugins..." class="search-input">
          </div>
          <div class="plugin-filters">
            <div class="filter-group">
              <label>Status:</label>
              <select id="filter-status" class="filter-select">
                <option value="">All</option>
                <option value="enabled">Enabled</option>
                <option value="disabled">Disabled</option>
              </select>
            </div>
            <div class="filter-group">
              <label>Rating:</label>
              <select id="filter-rating" class="filter-select">
                <option value="">All</option>
                <option value="5">5 stars</option>
                <option value="4">4+ stars</option>
                <option value="3">3+ stars</option>
              </select>
            </div>
          </div>
          <div class="plugins-list" id="installed-list">
            <p class="empty-state">Loading plugins...</p>
          </div>
        </div>

        <!-- Marketplace Tab -->
        <div class="tab-content" id="tab-marketplace">
          <div class="marketplace-header">
            <h3>Plugin Marketplace</h3>
            <p class="info-text">Discover and install new plugins</p>
          </div>
          <div class="plugin-search">
            <input type="text" id="search-marketplace" placeholder="Search marketplace..." class="search-input">
          </div>
          <div class="plugin-filters">
            <div class="filter-group">
              <label>Category:</label>
              <select id="filter-category" class="filter-select">
                <option value="">All Categories</option>
                <option value="utility">Utility</option>
                <option value="ui">UI/UX</option>
                <option value="data">Data</option>
                <option value="integration">Integration</option>
              </select>
            </div>
            <div class="filter-group">
              <label>Rating:</label>
              <select id="filter-marketplace-rating" class="filter-select">
                <option value="">All</option>
                <option value="5">5 stars</option>
                <option value="4">4+ stars</option>
                <option value="3">3+ stars</option>
              </select>
            </div>
            <div class="filter-group">
              <label>Sort:</label>
              <select id="filter-sort" class="filter-select">
                <option value="downloads">Most Downloaded</option>
                <option value="rating">Highest Rated</option>
                <option value="newest">Newest</option>
              </select>
            </div>
          </div>
          <div class="marketplace-list" id="marketplace-list">
            <p class="empty-state">Loading marketplace...</p>
          </div>
          
          <!-- Pagination Controls -->
          <div class="marketplace-pagination" id="marketplace-pagination" style="display: none;">
            <button class="pagination-btn" id="pagination-prev">← Previous</button>
            <span class="pagination-info">
              Page <span id="current-page">1</span> of <span id="total-pages">1</span>
            </span>
            <button class="pagination-btn" id="pagination-next">Next →</button>
          </div>
        </div>

        <!-- Settings Tab -->
        <div class="tab-content" id="tab-settings">
          <div class="settings-section">
            <h3>Plugin Settings</h3>
            <div class="setting-item">
              <label>Auto-load plugins</label>
              <input type="checkbox" id="setting-autoload" checked>
            </div>
            <div class="setting-item">
              <label>Check for updates</label>
              <input type="checkbox" id="setting-updates" checked>
            </div>
            <div class="setting-item">
              <label>Plugin directory</label>
              <input type="text" id="setting-directory" value="./plugins" class="input-text">
            </div>
          </div>

          <div class="settings-section">
            <h3>System Information</h3>
            <div class="info-item">
              <span>Total plugins:</span>
              <span id="info-total">0</span>
            </div>
            <div class="info-item">
              <span>Enabled plugins:</span>
              <span id="info-enabled">0</span>
            </div>
            <div class="info-item">
              <span>Plugin API version:</span>
              <span>1.0.0</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Plugin Details Modal -->
      <div class="modal" id="plugin-modal" style="display: none;">
        <div class="modal-content">
          <div class="modal-header">
            <h2 id="modal-title"></h2>
            <button class="btn-close" id="btn-close-modal">&times;</button>
          </div>
          
          <div class="modal-body">
            <div id="plugin-details"></div>
            <div id="plugin-config" style="display: none;">
              <h3>Configuration</h3>
              <form id="config-form"></form>
            </div>
          </div>

          <div class="modal-footer">
            <button id="btn-plugin-action" class="btn-primary">Enable</button>
            <button id="btn-close-plugin" class="btn-secondary">Close</button>
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

    // Search
    document.getElementById('search-installed')?.addEventListener('input', (e) => this.applyFilters('installed'));
    document.getElementById('search-marketplace')?.addEventListener('input', (e) => this.applyFilters('marketplace'));

    // Installed filters
    document.getElementById('filter-status')?.addEventListener('change', () => this.applyFilters('installed'));
    document.getElementById('filter-rating')?.addEventListener('change', () => this.applyFilters('installed'));

    // Marketplace filters
    document.getElementById('filter-category')?.addEventListener('change', () => this.applyFilters('marketplace'));
    document.getElementById('filter-marketplace-rating')?.addEventListener('change', () => this.applyFilters('marketplace'));
    document.getElementById('filter-sort')?.addEventListener('change', () => this.applyFilters('marketplace'));

    // Pagination controls
    document.getElementById('pagination-prev')?.addEventListener('click', () => this.previousPage());
    document.getElementById('pagination-next')?.addEventListener('click', () => this.nextPage());

    // Modal
    document.getElementById('btn-close-modal')?.addEventListener('click', () => this.closeModal());
    document.getElementById('btn-close-plugin')?.addEventListener('click', () => this.closeModal());
  }

  switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
    
    document.getElementById(`tab-${tabName}`)?.classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');
    
    this.selectedTab = tabName;
  }

  loadPlugins() {
    // Fetch plugins from backend API
    if (window.bridge && window.bridge.getPlugins) {
      try {
        const pluginsJson = window.bridge.getPlugins();
        this.plugins = JSON.parse(pluginsJson);
      } catch (e) {
        console.error('Failed to load plugins:', e);
        // Fallback to empty list
        this.plugins = [];
      }
    } else {
      // Fallback for development without bridge
      this.plugins = [];
    }

    // Load marketplace with pagination
    this.loadMarketplaceData();
    this.updateUI();
  }

  loadMarketplaceData() {
    // Get marketplace data using caching system
    const data = this.getMarketplaceData();
    this.marketplace = data;
    this.marketplaceFiltered = data;
    this.marketplaceCurrentPage = 1;
  }

  updateUI() {
    this.updatePluginsList();
    this.updateMarketplaceList();
    this.updateStats();
  }

  updatePluginsList() {
    const list = document.getElementById('installed-list');
    if (!list) return;

    if (this.plugins.length === 0) {
      list.innerHTML = '<p class="empty-state">No plugins installed</p>';
      return;
    }

    list.innerHTML = this.plugins.map(plugin => `
      <div class="plugin-card ${plugin.enabled ? 'enabled' : ''}">
        <div class="plugin-card-header">
          <h4>${plugin.name}</h4>
          <span class="plugin-version">v${plugin.version}</span>
        </div>
        <p class="plugin-description">${plugin.description}</p>
        <div class="plugin-meta">
          <span class="author">By ${plugin.author}</span>
          <span class="rating">${plugin.rating}/5 (${plugin.downloads} downloads)</span>
        </div>
        <div class="plugin-actions">
          <button class="btn-toggle ${plugin.enabled ? 'enabled' : ''}" 
                  onclick="pluginUI.togglePlugin('${plugin.id}')">
            ${plugin.enabled ? 'Disable' : 'Enable'}
          </button>
          <button class="btn-secondary" onclick="pluginUI.showPluginDetails('${plugin.id}')">
            Details
          </button>
        </div>
      </div>
    `).join('');
  }

  updateMarketplaceList() {
    // Use pagination rendering for marketplace
    this.renderMarketplaceWithPagination();
  }

  updateStats() {
    const total = this.plugins.length;
    const enabled = this.plugins.filter(p => p.enabled).length;
    
    document.getElementById('plugin-count').textContent = `${total} plugins`;
    document.getElementById('plugin-enabled').textContent = `${enabled} enabled`;
    document.getElementById('info-total').textContent = total;
    document.getElementById('info-enabled').textContent = enabled;
  }

  togglePlugin(pluginId) {
    const plugin = this.plugins.find(p => p.id === pluginId);
    if (plugin) {
      plugin.enabled = !plugin.enabled;
      this.updateUI();
    }
  }

  showPluginDetails(pluginId) {
    const plugin = this.plugins.find(p => p.id === pluginId);
    if (!plugin) return;

    document.getElementById('modal-title').textContent = plugin.name;
    document.getElementById('plugin-details').innerHTML = `
      <div class="details-info">
        <p><strong>Version:</strong> ${plugin.version}</p>
        <p><strong>Author:</strong> ${plugin.author}</p>
        <p><strong>Description:</strong> ${plugin.description}</p>
        <p><strong>Rating:</strong> ${plugin.rating}/5</p>
        <p><strong>Downloads:</strong> ${plugin.downloads}</p>
      </div>
    `;

    const btn = document.getElementById('btn-plugin-action');
    btn.textContent = plugin.enabled ? 'Disable' : 'Enable';
    btn.onclick = () => {
      this.togglePlugin(pluginId);
      this.closeModal();
    };

    document.getElementById('plugin-modal').style.display = 'flex';
  }

  installPlugin(pluginId) {
    if (!this.plugins.find(p => p.id === pluginId)) {
      const marketplace = this.marketplace.find(p => p.id === pluginId);
      if (marketplace) {
        this.plugins.push(marketplace);
        this.updateUI();
      }
    }
  }

  filterPlugins(query, type) {
    const list = type === 'installed' ? this.plugins : this.marketplace;
    const filtered = query === '' ? list : 
      list.filter(p => 
        p.name.toLowerCase().includes(query.toLowerCase()) ||
        p.description.toLowerCase().includes(query.toLowerCase()) ||
        (p.author && p.author.toLowerCase().includes(query.toLowerCase()))
      );

    return filtered;
  }

  applyFilters(type) {
    const query = type === 'installed' 
      ? document.getElementById('search-installed')?.value || ''
      : document.getElementById('search-marketplace')?.value || '';

    let filtered = this.filterPlugins(query, type);

    if (type === 'installed') {
      // Apply status filter
      const statusFilter = document.getElementById('filter-status')?.value;
      if (statusFilter === 'enabled') {
        filtered = filtered.filter(p => p.enabled);
      } else if (statusFilter === 'disabled') {
        filtered = filtered.filter(p => !p.enabled);
      }

      // Apply rating filter
      const ratingFilter = parseFloat(document.getElementById('filter-rating')?.value || '0');
      if (ratingFilter > 0) {
        filtered = filtered.filter(p => (p.rating || 0) >= ratingFilter);
      }
    } else {
      // Marketplace filters
      const categoryFilter = document.getElementById('filter-category')?.value;
      if (categoryFilter) {
        filtered = filtered.filter(p => (p.category || '').toLowerCase() === categoryFilter.toLowerCase());
      }

      // Apply rating filter
      const ratingFilter = parseFloat(document.getElementById('filter-marketplace-rating')?.value || '0');
      if (ratingFilter > 0) {
        filtered = filtered.filter(p => (p.rating || 0) >= ratingFilter);
      }

      // Apply sorting
      const sortBy = document.getElementById('filter-sort')?.value || 'downloads';
      if (sortBy === 'downloads') {
        filtered.sort((a, b) => (b.downloads || 0) - (a.downloads || 0));
      } else if (sortBy === 'rating') {
        filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0));
      } else if (sortBy === 'newest') {
        filtered.sort((a, b) => new Date(b.published_date || 0) - new Date(a.published_date || 0));
      }

      // Reset to first page and apply pagination
      this.marketplaceFiltered = filtered;
      this.marketplaceCurrentPage = 1;
      this.renderMarketplaceWithPagination();
      return;
    }

    // Render filtered results
    const containerId = type === 'installed' ? 'installed-list' : 'marketplace-list';
    const container = document.getElementById(containerId);
    if (!container) return;

    if (filtered.length === 0) {
      container.innerHTML = '<p class="empty-state">No plugins found matching your filters</p>';
      return;
    }

    if (type === 'installed') {
      container.innerHTML = filtered.map(plugin => `
        <div class="plugin-card ${plugin.enabled ? 'enabled' : ''}">
          <div class="plugin-card-header">
            <h4>${plugin.name}</h4>
            <span class="plugin-version">v${plugin.version}</span>
          </div>
          <p class="plugin-description">${plugin.description}</p>
          <div class="plugin-meta">
            <span class="author">By ${plugin.author}</span>
            <span class="rating">${plugin.rating}/5</span>
          </div>
          <div class="plugin-actions">
            <button class="btn-toggle ${plugin.enabled ? 'enabled' : ''}" 
                    onclick="pluginUI.togglePlugin('${plugin.id}')">
              ${plugin.enabled ? 'Disable' : 'Enable'}
            </button>
            <button class="btn-secondary" onclick="pluginUI.showPluginDetails('${plugin.id}')">
              Details
            </button>
          </div>
        </div>
      `).join('');
    } else {
      container.innerHTML = filtered.map(plugin => `
        <div class="marketplace-card">
          <div class="card-header">
            <h4>${plugin.name}</h4>
            <span class="rating-badge">${plugin.rating}/5</span>
            ${plugin.category ? `<span class="category-badge">${plugin.category}</span>` : ''}
          </div>
          <p class="card-description">${plugin.description}</p>
          <div class="card-meta">
            <span>By ${plugin.author}</span>
            <span>${plugin.downloads} downloads</span>
          </div>
          <div class="card-actions">
            <button class="btn-primary" onclick="pluginUI.installPlugin('${plugin.id}')">
              ${this.plugins.some(p => p.id === plugin.id) ? 'Installed' : 'Install'}
            </button>
            <button class="btn-secondary" onclick="pluginUI.showPluginDetails('${plugin.id}')">
              View
            </button>
          </div>
        </div>
      `).join('');
    }
  }

  togglePlugin(pluginId) {
    const plugin = this.plugins.find(p => p.id === pluginId);
    if (!plugin) return;

    // Call backend API to toggle plugin state
    if (window.bridge && window.bridge.togglePlugin) {
      try {
        const success = window.bridge.togglePlugin(pluginId);
        if (success) {
          // Update local state
          plugin.enabled = !plugin.enabled;
          this.updateUI();
          
          const action = plugin.enabled ? 'enabled' : 'disabled';
          console.log(`[Plugin] ${plugin.name} ${action}`);
          showToast(`${plugin.name} ${action}`, 'success', 3000);
        } else {
          showToast(`Failed to toggle ${plugin.name}`, 'error', 3000);
        }
      } catch (e) {
        console.error('Failed to toggle plugin:', e);
        showToast(`Error toggling plugin: ${e.message}`, 'error', 3000);
      }
    } else {
      console.warn('Bridge not available for toggling plugin');
      showToast('Plugin manager not ready', 'error', 3000);
    }
  }

  showPluginDetails(pluginId) {
    const plugin = this.plugins.find(p => p.id === pluginId) || this.marketplace.find(p => p.id === pluginId);
    if (!plugin) return;

    const modal = document.getElementById('plugin-modal');
    if (!modal) return;

    // Set modal title
    const title = document.getElementById('modal-title');
    if (title) title.textContent = plugin.name;

    // Set plugin details
    const details = document.getElementById('plugin-details');
    if (details) {
      details.innerHTML = `
        <div class="plugin-detail-view">
          <div class="detail-row">
            <span class="detail-label">Version:</span>
            <span class="detail-value">${plugin.version}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Author:</span>
            <span class="detail-value">${plugin.author}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Description:</span>
            <span class="detail-value">${plugin.description}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Status:</span>
            <span class="detail-value">${plugin.enabled ? 'Enabled' : 'Disabled'}</span>
          </div>
          ${plugin.rating ? `
            <div class="detail-row">
              <span class="detail-label">Rating:</span>
              <span class="detail-value">${plugin.rating}/5</span>
            </div>
          ` : ''}
        </div>
      `;
    }

    // Set action button
    const actionBtn = document.getElementById('btn-plugin-action');
    if (actionBtn) {
      actionBtn.textContent = plugin.enabled ? 'Disable' : 'Enable';
      actionBtn.onclick = () => {
        this.togglePlugin(pluginId);
        this.closeModal();
      };
    }

    // Show modal
    modal.style.display = 'block';
  }

  installPlugin(pluginId) {
    const plugin = this.marketplace.find(p => p.id === pluginId);
    if (!plugin) return;

    if (window.bridge && window.bridge.installPlugin) {
      try {
        const success = window.bridge.installPlugin(pluginId);
        if (success) {
          // Add to installed list
          if (!this.plugins.find(p => p.id === pluginId)) {
            this.plugins.push({...plugin});
          }
          this.updateUI();
          showToast(`${plugin.name} installed`, 'success', 3000);
        } else {
          showToast(`Failed to install ${plugin.name}`, 'error', 3000);
        }
      } catch (e) {
        console.error('Failed to install plugin:', e);
        showToast(`Error installing plugin: ${e.message}`, 'error', 3000);
      }
    }
  }

  closeModal() {
    document.getElementById('plugin-modal').style.display = 'none';
  }

  /**
   * Get cached marketplace data or fetch fresh
   */
  getMarketplaceData() {
    const now = Date.now();
    if (this.marketplaceCache && (now - this.marketplaceCacheTime) < this.cacheDuration) {
      console.log('[PluginManager] Using cached marketplace data');
      return this.marketplaceCache;
    }

    // Fetch from bridge if available
    if (window.bridge && window.bridge.getMarketplacePlugins) {
      try {
        const marketplaceJson = window.bridge.getMarketplacePlugins();
        this.marketplaceCache = JSON.parse(marketplaceJson);
        this.marketplaceCacheTime = now;
        console.log('[PluginManager] Fetched fresh marketplace data:', this.marketplaceCache.length, 'plugins');
        return this.marketplaceCache;
      } catch (e) {
        console.error('Failed to load marketplace:', e);
        return [];
      }
    }

    return [];
  }

  /**
   * Navigate to next page
   */
  nextPage() {
    const totalPages = Math.ceil(this.marketplaceFiltered.length / this.marketplacePageSize);
    if (this.marketplaceCurrentPage < totalPages) {
      this.marketplaceCurrentPage++;
      this.renderMarketplaceWithPagination();
    }
  }

  /**
   * Navigate to previous page
   */
  previousPage() {
    if (this.marketplaceCurrentPage > 1) {
      this.marketplaceCurrentPage--;
      this.renderMarketplaceWithPagination();
    }
  }

  /**
   * Render marketplace with pagination
   */
  renderMarketplaceWithPagination() {
    const startIndex = (this.marketplaceCurrentPage - 1) * this.marketplacePageSize;
    const endIndex = startIndex + this.marketplacePageSize;
    const pageItems = this.marketplaceFiltered.slice(startIndex, endIndex);

    const list = document.getElementById('marketplace-list');
    if (!list) return;

    if (pageItems.length === 0) {
      list.innerHTML = '<p class="empty-state">No plugins found</p>';
      return;
    }

    list.innerHTML = pageItems.map(plugin => `
      <div class="marketplace-card">
        <div class="card-header">
          <h4>${plugin.name}</h4>
          <span class="rating-badge">${plugin.rating}/5</span>
          ${plugin.category ? `<span class="category-badge">${plugin.category}</span>` : ''}
        </div>
        <p class="card-description">${plugin.description}</p>
        <div class="card-meta">
          <span>By ${plugin.author}</span>
          <span>${plugin.downloads} downloads</span>
        </div>
        <div class="card-actions">
          <button class="btn-primary" onclick="pluginUI.installPlugin('${plugin.id}')">
            ${this.plugins.some(p => p.id === plugin.id) ? 'Installed' : 'Install'}
          </button>
          <button class="btn-secondary" onclick="pluginUI.showPluginDetails('${plugin.id}')">
            View
          </button>
        </div>
      </div>
    `).join('');

    // Update pagination controls
    const totalPages = Math.ceil(this.marketplaceFiltered.length / this.marketplacePageSize);
    const pagination = document.getElementById('marketplace-pagination');
    if (pagination) {
      pagination.style.display = totalPages > 1 ? 'flex' : 'none';
      document.getElementById('current-page').textContent = this.marketplaceCurrentPage;
      document.getElementById('total-pages').textContent = totalPages;

      // Disable buttons at boundaries
      document.getElementById('pagination-prev').disabled = this.marketplaceCurrentPage === 1;
      document.getElementById('pagination-next').disabled = this.marketplaceCurrentPage === totalPages;
    }
  }
}

let pluginUI;
document.addEventListener('DOMContentLoaded', () => {
  pluginUI = new PluginManagerUI();
});
