// FlowChain - Main Application JavaScript
'use strict';

const SCMApp = {
  init() {
    this.initSidebar();
    this.initTheme();
    this.initSearch();
    this.initWebSocket();
    this.initTooltips();
    this.initAlerts();
    this.initCharts();
  },

  // ─── SIDEBAR ───
  initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggle');
    const mobileToggle = document.getElementById('mobileSidebarToggle');
    const overlay = document.getElementById('sidebarOverlay');
    const mainContent = document.getElementById('mainContent');

    if (!sidebar) return;

    const collapsed = localStorage.getItem('sidebar_collapsed') === 'true';
    if (collapsed) sidebar.classList.add('collapsed');

    toggleBtn?.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      localStorage.setItem('sidebar_collapsed', sidebar.classList.contains('collapsed'));
    });

    mobileToggle?.addEventListener('click', () => {
      sidebar.classList.add('mobile-open');
      overlay.classList.add('active');
    });

    overlay?.addEventListener('click', () => {
      sidebar.classList.remove('mobile-open');
      overlay.classList.remove('active');
    });

    // Highlight active nav item
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-item').forEach(item => {
      const href = item.getAttribute('href');
      if (href && currentPath.startsWith(href) && href !== '/') {
        item.classList.add('active');
      }
    });
  },

  // ─── THEME ───
  initTheme() {
    const btn = document.getElementById('themeToggle');
    const icon = document.getElementById('themeIcon');
    const html = document.documentElement;

    const applyTheme = (theme) => {
      html.setAttribute('data-theme', theme);
      localStorage.setItem('scm_theme', theme);
      if (icon) {
        icon.className = theme === 'dark' ? 'bi bi-moon-stars-fill' : 'bi bi-sun-fill';
      }
    };

    const savedTheme = localStorage.getItem('scm_theme') || html.getAttribute('data-theme') || 'dark';
    applyTheme(savedTheme);

    btn?.addEventListener('click', () => {
      const current = html.getAttribute('data-theme');
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });
  },

  // ─── GLOBAL SEARCH ───
  initSearch() {
    const modal = document.getElementById('globalSearchModal');
    const input = document.getElementById('globalSearchInput');
    const results = document.getElementById('searchResults');
    let debounceTimer;

    const openSearch = () => {
      if (modal) {
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        setTimeout(() => input?.focus(), 150);
      }
    };

    // Open with Ctrl/Cmd+K
    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        openSearch();
      }
    });

    document.querySelectorAll('#globalSearch, .topbar-search').forEach(el => {
      el.addEventListener('click', openSearch);
    });

    input?.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      const query = e.target.value.trim();
      if (query.length < 2) {
        results.innerHTML = this.getSearchHint();
        return;
      }
      debounceTimer = setTimeout(() => this.performSearch(query, results), 300);
    });
  },

  async performSearch(query, resultsEl) {
    resultsEl.innerHTML = '<div class="text-center py-3"><div class="spinner-border spinner-border-sm text-primary"></div></div>';
    try {
      const res = await fetch(`/api/v1/products/?search=${encodeURIComponent(query)}&page_size=5`, {
        headers: { 'X-CSRFToken': window.SCM?.csrfToken || '' }
      });
      const data = await res.json();
      resultsEl.innerHTML = this.renderSearchResults(data.results || [], query);
    } catch {
      resultsEl.innerHTML = '<div class="text-center py-3 text-muted">Search failed. Try again.</div>';
    }
  },

  renderSearchResults(items, query) {
    if (!items.length) return `<div class="text-center py-3 text-muted">No results for "${query}"</div>`;
    return items.map(item => `
      <a href="/products/${item.id}/" class="search-result-item">
        <i class="bi bi-box-seam"></i>
        <div>
          <div class="fw-500">${item.name}</div>
          <small class="text-muted font-mono">${item.sku}</small>
        </div>
        <span class="badge-status badge-${item.status}">${item.status}</span>
      </a>`).join('');
  },

  getSearchHint() {
    return `<div class="search-hint">
      <div class="search-hint-item"><kbd>↑↓</kbd> Navigate</div>
      <div class="search-hint-item"><kbd>↵</kbd> Open</div>
      <div class="search-hint-item"><kbd>ESC</kbd> Close</div>
    </div>`;
  },

  // ─── WEBSOCKET (Real-time notifications) ───
  initWebSocket() {
    if (!window.SCM?.userId) return;
    const wsUrl = `ws://${window.location.host}/ws/notifications/`;

    const connect = () => {
      const ws = new WebSocket(wsUrl);

      ws.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.type === 'notification') this.showToastNotification(data);
        if (data.type === 'unread_count') this.updateNotifBadge(data.count);
      };

      ws.onclose = () => setTimeout(connect, 3000); // Auto-reconnect
      window.SCM.ws = ws;
    };

    try { connect(); } catch (e) { console.warn('WebSocket unavailable'); }
  },

  showToastNotification(data) {
    const container = document.getElementById('toast-container') || (() => {
      const el = document.createElement('div');
      el.id = 'toast-container';
      el.className = 'toast-container position-fixed bottom-0 end-0 p-3';
      el.style.zIndex = '9999';
      document.body.appendChild(el);
      return el;
    })();

    const icons = { low_stock: 'bi-exclamation-triangle text-warning', system: 'bi-gear text-info' };
    const icon = icons[data.notification_type] || 'bi-bell text-primary';

    const toast = document.createElement('div');
    toast.className = 'toast show';
    toast.style.cssText = 'background:var(--bg-card);border:1px solid var(--border-color);color:var(--text-primary);min-width:300px;border-radius:10px;';
    toast.innerHTML = `
      <div class="toast-header" style="background:var(--bg-secondary);border-bottom:1px solid var(--border-color);">
        <i class="bi ${icon} me-2"></i>
        <strong class="me-auto">${data.title}</strong>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
      </div>
      <div class="toast-body">${data.message}</div>`;

    container.appendChild(toast);
    setTimeout(() => toast.remove(), 6000);
  },

  updateNotifBadge(count) {
    document.querySelectorAll('.notif-badge').forEach(el => {
      el.textContent = count;
      el.style.display = count > 0 ? 'flex' : 'none';
    });
  },

  // ─── TOOLTIPS ───
  initTooltips() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
      new bootstrap.Tooltip(el);
    });
  },

  // ─── AUTO-DISMISS ALERTS ───
  initAlerts() {
    setTimeout(() => {
      document.querySelectorAll('.scm-alert').forEach(el => {
        const bsAlert = bootstrap.Alert.getInstance(el);
        if (bsAlert) bsAlert.close();
        else el.remove();
      });
    }, 5000);
  },

  // ─── CHART UTILITIES ───
  initCharts() {
    window.SCMCharts = {};
  },

  createLineChart(elementId, title, series, categories, opts = {}) {
    const options = {
      series,
      chart: { type: 'area', height: 300, toolbar: { show: false }, background: 'transparent', fontFamily: 'Inter, sans-serif' },
      colors: opts.colors || ['#388bfd', '#3fb950', '#d29922', '#f85149'],
      stroke: { curve: 'smooth', width: 2 },
      fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.3, opacityTo: 0, stops: [0, 100] } },
      xaxis: { categories, labels: { style: { colors: '#8b949e', fontSize: '11px' } }, axisBorder: { show: false }, axisTicks: { show: false } },
      yaxis: { labels: { style: { colors: '#8b949e', fontSize: '11px' } } },
      grid: { borderColor: '#30363d', strokeDashArray: 3 },
      legend: { labels: { colors: '#8b949e' } },
      tooltip: { theme: 'dark' },
      dataLabels: { enabled: false },
      ...opts,
    };
    const chart = new ApexCharts(document.getElementById(elementId), options);
    chart.render();
    window.SCMCharts[elementId] = chart;
    return chart;
  },

  createDonutChart(elementId, labels, series, opts = {}) {
    const options = {
      series,
      chart: { type: 'donut', height: 280, background: 'transparent', fontFamily: 'Inter, sans-serif' },
      labels,
      colors: opts.colors || ['#388bfd', '#3fb950', '#d29922', '#f85149', '#a371f7', '#39d5d0'],
      plotOptions: { pie: { donut: { size: '70%', labels: { show: true, total: { show: true, label: 'Total', color: '#8b949e' } } } } },
      legend: { position: 'bottom', labels: { colors: '#8b949e' } },
      dataLabels: { enabled: false },
      tooltip: { theme: 'dark' },
      ...opts,
    };
    const chart = new ApexCharts(document.getElementById(elementId), options);
    chart.render();
    window.SCMCharts[elementId] = chart;
    return chart;
  },

  createBarChart(elementId, series, categories, opts = {}) {
    const options = {
      series,
      chart: { type: 'bar', height: 300, toolbar: { show: false }, background: 'transparent', fontFamily: 'Inter, sans-serif' },
      colors: opts.colors || ['#388bfd'],
      plotOptions: { bar: { borderRadius: 4, columnWidth: '55%' } },
      xaxis: { categories, labels: { style: { colors: '#8b949e', fontSize: '11px' } }, axisBorder: { show: false }, axisTicks: { show: false } },
      yaxis: { labels: { style: { colors: '#8b949e', fontSize: '11px' } } },
      grid: { borderColor: '#30363d', strokeDashArray: 3 },
      tooltip: { theme: 'dark' },
      dataLabels: { enabled: false },
      ...opts,
    };
    const chart = new ApexCharts(document.getElementById(elementId), options);
    chart.render();
    window.SCMCharts[elementId] = chart;
    return chart;
  },

  // ─── API HELPERS ───
  async apiGet(url, params = {}) {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${url}?${query}`, { headers: { 'Accept': 'application/json' } });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  },

  async apiPost(url, data) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': window.SCM?.csrfToken || '' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  },

  // ─── FORMAT HELPERS ───
  formatCurrency(amount) {
    const sym = window.SCM?.currencySymbol || '₹';
    return `${sym}${Number(amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  },

  formatNumber(num) {
    if (num >= 1e7) return (num / 1e7).toFixed(1) + 'Cr';
    if (num >= 1e5) return (num / 1e5).toFixed(1) + 'L';
    if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
    return num.toString();
  },
};

document.addEventListener('DOMContentLoaded', () => SCMApp.init());
window.SCMApp = SCMApp;
