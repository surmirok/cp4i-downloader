// CP4I Downloader - Web Interface JavaScript

// API Base URL
const API_BASE = '/api';

// Global state
let components = [];
let activeDownloads = [];
let downloadHistory = [];
let refreshInterval = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadComponents();
    loadDownloads();
    startAutoRefresh();
});

// Tab Management
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked button
    event.target.closest('.tab-btn').classList.add('active');
    
    // Refresh data for the tab
    if (tabName === 'active-downloads' || tabName === 'history') {
        loadDownloads();
    }
}

// Load Components
async function loadComponents() {
    try {
        const response = await fetch(`${API_BASE}/components`);
        const data = await response.json();
        components = data.components;
        
        const select = document.getElementById('component');
        select.innerHTML = '<option value="">Select a component...</option>';
        
        components.forEach(comp => {
            const option = document.createElement('option');
            option.value = comp.name;
            option.textContent = `${comp.description} (${comp.typical_size})`;
            option.dataset.component = JSON.stringify(comp);
            select.appendChild(option);
        });
    } catch (error) {
        showToast('Failed to load components', 'error');
        console.error(error);
    }
}

// Update Versions
function updateVersions() {
    const componentSelect = document.getElementById('component');
    const versionInput = document.getElementById('version');
    const versionDatalist = document.getElementById('version-list');
    const selectedOption = componentSelect.options[componentSelect.selectedIndex];
    
    if (!selectedOption.dataset.component) {
        versionDatalist.innerHTML = '';
        versionInput.value = '';
        document.getElementById('component-info').style.display = 'none';
        return;
    }
    
    const component = JSON.parse(selectedOption.dataset.component);
    
    // Update version datalist with suggestions
    versionDatalist.innerHTML = '';
    component.versions.forEach(version => {
        const option = document.createElement('option');
        option.value = version;
        versionDatalist.appendChild(option);
    });
    
    // Show component info
    const infoDiv = document.getElementById('component-info');
    const detailsDiv = document.getElementById('component-details');
    detailsDiv.innerHTML = `
        <div class="info-box">
            <p><strong>Component:</strong> ${component.description}</p>
            <p><strong>Name:</strong> ${component.name}</p>
            <p><strong>Typical Size:</strong> ${component.typical_size}</p>
            <p><strong>Suggested Versions:</strong> ${component.versions.join(', ')}</p>
            <p><em>Note: You can enter any version number manually</em></p>
        </div>
    `;
    infoDiv.style.display = 'block';
}

// Auto-fill name field when version is entered
document.addEventListener('DOMContentLoaded', () => {
    const versionInput = document.getElementById('version');
    const componentSelect = document.getElementById('component');
    const nameInput = document.getElementById('name');
    
    if (versionInput) {
        versionInput.addEventListener('input', () => {
            const selectedOption = componentSelect.options[componentSelect.selectedIndex];
            if (selectedOption && selectedOption.dataset.component && versionInput.value) {
                const component = JSON.parse(selectedOption.dataset.component);
                const shortName = component.name.replace('ibm-', '').replace('-operator', '');
                if (!nameInput.value || nameInput.value.startsWith(shortName)) {
                    nameInput.value = `${shortName}-${versionInput.value}`;
                }
            }
        });
    }
});

// Start Download
async function startDownload(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = {
        component: form.component.value,
        version: form.version.value,
        name: form.name.value,
        filter: form.filter.value || null,
        dry_run: form.dry_run.checked,
        home_dir: form.home_dir.value,
        final_registry: form.final_registry.value,
        registry_auth_file: form.registry_auth_file.value,
        entitlement_key: form.entitlement_key.value
    };
    
    // Validate required fields (entitlement_key is optional)
    if (!formData.home_dir || !formData.final_registry || !formData.registry_auth_file) {
        showToast('Please fill in required configuration fields (home_dir, final_registry, registry_auth_file)', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/downloads`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(`Download started: ${formData.name}`, 'success');
            
            // Don't reset the form to preserve configuration values
            // Only clear download-specific fields
            try {
                form.component.value = '';
                form.version.value = '';
                form.name.value = '';
                form.filter.value = '';
                form.dry_run.checked = false;
                document.getElementById('component-info').style.display = 'none';
                showTab('active-downloads');
                loadDownloads();
            } catch (uiError) {
                // Log UI update errors but don't show error toast since download started successfully
                console.error('UI update error after successful download start:', uiError);
            }
        } else {
            showToast(data.error || 'Failed to start download', 'error');
        }
    } catch (error) {
        showToast('Failed to start download', 'error');
        console.error(error);
    }
}

// Load Downloads
async function loadDownloads() {
    try {
        const response = await fetch(`${API_BASE}/downloads`);
        const data = await response.json();
        
        activeDownloads = data.active || [];
        downloadHistory = data.history || [];
        
        renderActiveDownloads();
        renderHistory();
        updateActiveCount();
    } catch (error) {
        console.error('Failed to load downloads:', error);
    }
}

// Render Active Downloads
function renderActiveDownloads() {
    const container = document.getElementById('active-downloads-list');
    
    if (activeDownloads.length === 0) {
        container.innerHTML = '<p class="empty-state">No active downloads</p>';
        return;
    }
    
    container.innerHTML = activeDownloads.map(download => `
        <div class="download-item status-${download.status}">
            <div class="download-header">
                <div class="download-title">
                    <i class="fas fa-cube"></i> ${download.component} v${download.version}
                </div>
                <span class="download-status status-${download.status}">
                    ${download.status}
                </span>
            </div>
            
            <div class="download-info">
                <div><i class="fas fa-folder"></i> <strong>Name:</strong> ${download.name}</div>
                <div><i class="fas fa-clock"></i> <strong>Started:</strong> ${formatDateTime(download.start_time)}</div>
                <div><i class="fas fa-hashtag"></i> <strong>PID:</strong> ${download.pid || 'N/A'}</div>
            </div>
            
            ${download.status === 'running' ? `
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${download.progress || 50}%"></div>
                </div>
                <p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 5px;">
                    Progress: ${download.progress || 50}%
                </p>
            ` : ''}
            
            <div class="download-actions">
                <button class="btn btn-small btn-secondary" onclick="showDownloadDetails('${download.id}')">
                    <i class="fas fa-info-circle"></i> Details
                </button>
                ${download.status === 'running' ? `
                    <button class="btn btn-small btn-danger" onclick="stopDownload('${download.id}')">
                        <i class="fas fa-stop"></i> Stop
                    </button>
                ` : ''}
                ${download.status === 'failed' ? `
                    <button class="btn btn-small btn-primary" onclick="retryDownload('${download.id}')">
                        <i class="fas fa-redo"></i> Retry
                    </button>
                ` : ''}
                ${download.status !== 'running' ? `
                    <button class="btn btn-small btn-secondary" onclick="dismissDownload('${download.id}')">
                        <i class="fas fa-times"></i> Dismiss
                    </button>
                ` : ''}
            </div>
        </div>
    `).join('');
}

// Render History
function renderHistory() {
    const container = document.getElementById('history-list');
    
    if (downloadHistory.length === 0) {
        container.innerHTML = '<p class="empty-state">No download history</p>';
        return;
    }
    
    container.innerHTML = downloadHistory.map(download => `
        <div class="download-item status-${download.status}">
            <div class="download-header">
                <div class="download-title">
                    <i class="fas fa-cube"></i> ${download.component} v${download.version}
                </div>
                <span class="download-status status-${download.status}">
                    ${download.status}
                </span>
            </div>
            
            <div class="download-info">
                <div><i class="fas fa-folder"></i> <strong>Name:</strong> ${download.name}</div>
                <div><i class="fas fa-clock"></i> <strong>Started:</strong> ${formatDateTime(download.start_time)}</div>
                <div><i class="fas fa-check-circle"></i> <strong>Ended:</strong> ${formatDateTime(download.end_time)}</div>
            </div>
            
            <div class="download-actions">
                <button class="btn btn-small btn-secondary" onclick="viewLogs('${download.id}')">
                    <i class="fas fa-file-alt"></i> View Logs
                </button>
                <button class="btn btn-small btn-secondary" onclick="viewReport('${download.id}')">
                    <i class="fas fa-chart-bar"></i> View Report
                </button>
                ${download.status === 'completed' ? `
                    <button class="btn btn-small btn-primary" onclick="retryDownload('${download.id}')">
                        <i class="fas fa-download"></i> Re-download
                    </button>
                ` : ''}
                ${download.status === 'failed' || download.status === 'dismissed' ? `
                    <button class="btn btn-small btn-primary" onclick="retryDownload('${download.id}')">
                        <i class="fas fa-redo"></i> Retry
                    </button>
                ` : ''}
            </div>
        </div>
    `).join('');
}

// Update Active Count Badge
function updateActiveCount() {
    const badge = document.getElementById('active-count');
    const count = activeDownloads.filter(d => d.status === 'running').length;
    badge.textContent = count;
    badge.style.display = count > 0 ? 'inline-block' : 'none';
}

// Show Download Details
async function showDownloadDetails(downloadId) {
    const modal = document.getElementById('download-details-modal');
    const content = document.getElementById('download-details-content');
    
    modal.classList.add('active');
    content.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/downloads/${downloadId}`);
        const data = await response.json();
        
        if (response.ok) {
            content.innerHTML = `
                <div class="info-box">
                    <h3><i class="fas fa-cube"></i> ${data.component} v${data.version}</h3>
                    <p><strong>Status:</strong> <span class="download-status status-${data.status}">${data.status}</span></p>
                    <p><strong>Name:</strong> ${data.name}</p>
                    <p><strong>Started:</strong> ${formatDateTime(data.start_time)}</p>
                    ${data.end_time ? `<p><strong>Ended:</strong> ${formatDateTime(data.end_time)}</p>` : ''}
                    <p><strong>PID:</strong> ${data.pid || 'N/A'}</p>
                </div>
                
                ${data.log_tail && data.log_tail.length > 0 ? `
                    <h3 class="mt-20"><i class="fas fa-terminal"></i> Recent Log Output</h3>
                    <div class="code-block">${data.log_tail.join('')}</div>
                ` : ''}
                
                ${data.progress && data.progress.summary ? `
                    <h3 class="mt-20"><i class="fas fa-chart-line"></i> Progress Summary</h3>
                    <div class="code-block">${data.progress.summary}</div>
                ` : ''}
            `;
        } else {
            content.innerHTML = `<div class="error-box">${data.error}</div>`;
        }
    } catch (error) {
        content.innerHTML = '<div class="error-box">Failed to load download details</div>';
        console.error(error);
    }
}

// Stop Download
async function stopDownload(downloadId) {
    if (!confirm('Are you sure you want to stop this download?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/downloads/${downloadId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Download stopped', 'success');
            loadDownloads();
        } else {
            showToast(data.error || 'Failed to stop download', 'error');
        }
    } catch (error) {
        showToast('Failed to stop download', 'error');
        console.error(error);
    }
}

// Retry Download - Use original configuration directly
async function retryDownload(downloadId) {
    try {
        // First try to find in local downloadHistory (faster)
        let download = null;
        for (const hist of downloadHistory) {
            if (hist.id === downloadId) {
                download = hist;
                break;
            }
        }
        
        // If not found locally, fetch from API
        if (!download) {
            const response = await fetch(`${API_BASE}/downloads`);
            const data = await response.json();
            
            for (const hist of data.history) {
                if (hist.id === downloadId) {
                    download = hist;
                    break;
                }
            }
        }
        
        if (!download) {
            showToast('Download not found', 'error');
            console.error('Download not found:', downloadId);
            return;
        }
        
        console.log('Retrying download with original configuration:', download);
        
        // Use original configuration from history
        const retryData = {
            home_dir: download.home_dir || '/opt/cp4i',
            final_registry: download.final_registry || 'registry.example.com:5000',
            registry_auth_file: download.registry_auth_file || '/root/.docker/config.json',
            entitlement_key: download.entitlement_key || ''
        };
        
        // Start retry directly with original configuration
        const response = await fetch(`${API_BASE}/downloads/${downloadId}/retry`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(retryData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Download retry started with original configuration', 'success');
            loadDownloads();
        } else {
            showToast(data.error || 'Failed to retry download', 'error');
        }
    } catch (error) {
        showToast('Failed to retry download', 'error');
        console.error(error);
    }
}

// Dismiss Download
async function dismissDownload(downloadId) {
    if (!confirm('Are you sure you want to dismiss this download from the list?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/downloads/${downloadId}`, {
            method: 'PATCH'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Download dismissed', 'success');
            loadDownloads();
        } else {
            showToast(data.error || 'Failed to dismiss download', 'error');
        }
    } catch (error) {
        showToast('Failed to dismiss download', 'error');
        console.error(error);
    }
}

// View Logs
async function viewLogs(downloadId) {
    const modal = document.getElementById('download-details-modal');
    const content = document.getElementById('download-details-content');
    
    modal.classList.add('active');
    content.innerHTML = '<div class="loading">Loading logs...</div>';
    
    try {
        // Find the download in history to get home_dir and name
        let download = null;
        for (const hist of downloadHistory) {
            if (hist.id === downloadId) {
                download = hist;
                break;
            }
        }
        
        if (!download) {
            content.innerHTML = '<div class="error-box">Download not found</div>';
            return;
        }
        
        const homeDir = download.home_dir || '/opt/cp4i';
        const name = download.name;
        
        const response = await fetch(`${API_BASE}/logs/${name}?home_dir=${encodeURIComponent(homeDir)}`);
        const data = await response.json();
        
        if (response.ok) {
            content.innerHTML = `
                <h3><i class="fas fa-file-alt"></i> Download Logs: ${name}</h3>
                <div class="code-block">${data.logs}</div>
            `;
        } else {
            content.innerHTML = `<div class="error-box">${data.error}</div>`;
        }
    } catch (error) {
        content.innerHTML = '<div class="error-box">Failed to load logs</div>';
        console.error(error);
    }
}

// View Report
async function viewReport(downloadId) {
    const modal = document.getElementById('download-details-modal');
    const content = document.getElementById('download-details-content');
    
    modal.classList.add('active');
    content.innerHTML = '<div class="loading">Loading report...</div>';
    
    try {
        // Find the download in history to get home_dir and name
        let download = null;
        for (const hist of downloadHistory) {
            if (hist.id === downloadId) {
                download = hist;
                break;
            }
        }
        
        if (!download) {
            content.innerHTML = '<div class="error-box">Download not found</div>';
            return;
        }
        
        const homeDir = download.home_dir || '/opt/cp4i';
        const name = download.name;
        
        const response = await fetch(`${API_BASE}/reports/${name}?home_dir=${encodeURIComponent(homeDir)}`);
        const data = await response.json();
        
        if (response.ok) {
            content.innerHTML = `
                <h3><i class="fas fa-chart-bar"></i> Summary Report: ${name}</h3>
                <div class="code-block">${data.report}</div>
            `;
        } else {
            content.innerHTML = `<div class="error-box">${data.error}</div>`;
        }
    } catch (error) {
        content.innerHTML = '<div class="error-box">Failed to load report</div>';
        console.error(error);
    }
}

// Show System Info
async function showSystemInfo() {
    const modal = document.getElementById('system-info-modal');
    const content = document.getElementById('system-info-content');

    modal.classList.add('active');
    content.innerHTML = '<div class="loading">Loading system information...</div>';

    try {
        // Get home_dir from form if available
        const homeDirInput = document.getElementById('home-dir');
        const homeDir = homeDirInput ? homeDirInput.value : '/opt/cp4i';
        
        const response = await fetch(`${API_BASE}/system/info?home_dir=${encodeURIComponent(homeDir)}`);
        const data = await response.json();
        
        if (response.ok) {
            const prereqsHtml = Object.entries(data.prerequisites)
                .map(([tool, installed]) => `
                    <div style="display: flex; align-items: center; gap: 10px; margin: 5px 0;">
                        <i class="fas fa-${installed ? 'check-circle' : 'times-circle'}" 
                           style="color: ${installed ? 'var(--success-color)' : 'var(--danger-color)'}"></i>
                        <strong>${tool}:</strong> ${installed ? 'Installed' : 'Not Found'}
                    </div>
                `).join('');
            
            content.innerHTML = `
                <div class="info-box">
                    <h3><i class="fas fa-server"></i> System Configuration</h3>
                    <p><strong>Home Directory:</strong> ${data.home_dir}</p>
                    <p><strong>Script Path:</strong> ${data.script_path}</p>
                </div>
                
                <h3 class="mt-20"><i class="fas fa-hdd"></i> Disk Space</h3>
                <div class="code-block">${data.disk_info}</div>
                
                <h3 class="mt-20"><i class="fas fa-check-circle"></i> Prerequisites</h3>
                <div class="info-box">
                    ${prereqsHtml}
                </div>
            `;
        } else {
            content.innerHTML = `<div class="error-box">${data.error}</div>`;
        }
    } catch (error) {
        content.innerHTML = '<div class="error-box">Failed to load system information</div>';
        console.error(error);
    }
}

// Show Configuration
async function showConfig() {
    const modal = document.getElementById('config-modal');
    modal.classList.add('active');
    loadConfig();
}

// Load Configuration
async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/config`);
        const data = await response.json();
        
        document.getElementById('config-content').value = data.config || '';
    } catch (error) {
        showToast('Failed to load configuration', 'error');
        console.error(error);
    }
}

// Save Configuration
async function saveConfig(event) {
    event.preventDefault();
    
    const content = document.getElementById('config-content').value;
    
    try {
        const response = await fetch(`${API_BASE}/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ config: content })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Configuration saved successfully', 'success');
            closeModal('config-modal');
        } else {
            showToast(data.error || 'Failed to save configuration', 'error');
        }
    } catch (error) {
        showToast('Failed to save configuration', 'error');
        console.error(error);
    }
}

// Validate Prerequisites
async function validatePrerequisites() {
    try {
        const response = await fetch(`${API_BASE}/validate`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.valid) {
            showToast('All prerequisites validated successfully', 'success');
        } else {
            showToast('Some prerequisites are missing. Check system info.', 'warning');
        }
    } catch (error) {
        showToast('Failed to validate prerequisites', 'error');
        console.error(error);
    }
}

// Close Modal
function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Close modal on background click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});

// Show Toast Notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    }[type] || 'info-circle';
    
    toast.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Format DateTime
function formatDateTime(isoString) {
    if (!isoString) return 'N/A';
    const date = new Date(isoString);
    return date.toLocaleString();
}

// Auto-refresh
function startAutoRefresh() {
    refreshInterval = setInterval(() => {
        if (document.querySelector('#active-downloads.active') || 
            document.querySelector('#history.active')) {
            loadDownloads();
        }
    }, 10000); // Refresh every 10 seconds
}

// Stop auto-refresh on page unload
window.addEventListener('beforeunload', () => {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});

// Made with Bob
