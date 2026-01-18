/**
 * Plugin Manager UI - Issue #58
 * Interface for managing plugins, viewing marketplace, and configuration
 */

class PluginManagerUI {
  constructor() {
    this.plugins = [];
    this.marketplace = [];
    this.selectedTab = 'installed';
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
          <div class="marketplace-list" id="marketplace-list">
            <p class="empty-state">Loading marketplace...</p>
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
    document.getElementById('search-installed')?.addEventListener('input', (e) => this.filterPlugins(e.target.value, 'installed'));
    document.getElementById('search-marketplace')?.addEventListener('input', (e) => this.filterPlugins(e.target.value, 'marketplace'));

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
    // Simulate plugin data
    this.plugins = [
      {
        id: 'syntax.highlighter',
        name: 'Advanced Syntax Highlighter',
        version: '1.2.0',
        author: 'Plugin Dev',
        description: 'Enhanced syntax highlighting with theme support',
        enabled: true,
        rating: 4.8,
        downloads: 1250,
      },
      {
        id: 'export.pdf',
        name: 'PDF Export',
        version: '2.0.1',
        author: 'Export Team',
        description: 'Professional PDF export with templates',
        enabled: true,
        rating: 4.5,
        downloads: 890,
      },
      {
        id: 'ai.assistant',
        name: 'AI Assistant',
        version: '1.0.0',
        author: 'AI Lab',
        description: 'AI-powered template suggestions',
        enabled: false,
        rating: 4.2,
        downloads: 450,
      },
    ];

    this.marketplace = [
      ...this.plugins,
      {
        id: 'theme.dark',
        name: 'Dark Theme Pro',
        version: '1.5.0',
        author: 'Design Team',
        description: 'Premium dark theme with customization',
        enabled: false,
        rating: 4.9,
        downloads: 3200,
      },
    ];

    this.updateUI();
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
    const list = document.getElementById('marketplace-list');
    if (!list) return;

    list.innerHTML = this.marketplace.map(plugin => `
      <div class="marketplace-card">
        <div class="card-header">
          <h4>${plugin.name}</h4>
          <span class="rating-badge">${plugin.rating}/5</span>
        </div>
        <p class="card-description">${plugin.description}</p>
        <div class="card-stats">
          <span>${plugin.downloads} downloads</span>
          <span>${plugin.author}</span>
        </div>
        <button class="btn-primary" onclick="pluginUI.installPlugin('${plugin.id}')">
          ${this.plugins.some(p => p.id === plugin.id) ? 'Installed' : 'Install'}
        </button>
      </div>
    `).join('');
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
        p.description.toLowerCase().includes(query.toLowerCase())
      );

    const containerId = type === 'installed' ? 'installed-list' : 'marketplace-list';
    const container = document.getElementById(containerId);
    if (!container) return;

    if (filtered.length === 0) {
      container.innerHTML = '<p class="empty-state">No plugins found</p>';
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
    }
  }

  closeModal() {
    document.getElementById('plugin-modal').style.display = 'none';
  }
}

let pluginUI;
document.addEventListener('DOMContentLoaded', () => {
  pluginUI = new PluginManagerUI();
});
