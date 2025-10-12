// Database Health Monitoring System
// Real-time monitoring and automatic recovery for database reliability

class DatabaseHealthMonitor {
    constructor() {
        this.isMonitoring = false;
        this.healthCheckInterval = 60000; // Check every 60 seconds
        this.intervalId = null;
        this.lastHealthStatus = null;
        this.consecutiveFailures = 0;
        this.maxAutoRecoveryAttempts = 3;
    }

    startMonitoring() {
        if (this.isMonitoring) {
            console.log('Health monitoring already active');
            return;
        }

        console.log('Starting database health monitoring...');
        this.isMonitoring = true;
        
        // Initial health check
        this.checkHealth();
        
        // Schedule periodic checks
        this.intervalId = setInterval(() => {
            this.checkHealth();
        }, this.healthCheckInterval);
    }

    stopMonitoring() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        this.isMonitoring = false;
        console.log('Database health monitoring stopped');
    }

    async checkHealth() {
        try {
            const response = await fetch('/api/database-health');
            const health = await response.json();
            
            this.lastHealthStatus = health;
            
            if (health.healthy) {
                this.consecutiveFailures = 0;
                this.updateHealthUI(health, 'healthy');
            } else {
                this.consecutiveFailures++;
                this.updateHealthUI(health, 'unhealthy');
                
                // Attempt automatic recovery if failures persist
                if (this.consecutiveFailures >= 2 && this.consecutiveFailures <= this.maxAutoRecoveryAttempts) {
                    console.error(`Database unhealthy (${this.consecutiveFailures} consecutive failures), attempting automatic recovery...`);
                    await this.attemptAutoRecovery();
                }
            }
            
        } catch (error) {
            console.error('Error checking database health:', error);
            this.updateHealthUI({ error: error.message }, 'error');
        }
    }

    async attemptAutoRecovery() {
        try {
            console.log('Attempting automatic database recovery...');
            
            // Try restoring from backup first
            const restoreResponse = await fetch('/api/database-restore', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            
            const result = await restoreResponse.json();
            
            if (result.success) {
                console.log('Database automatically recovered:', result.message);
                this.consecutiveFailures = 0;
                
                // Show success notification
                this.showNotification('Database automatically recovered', 'success');
                
                // Re-check health
                setTimeout(() => this.checkHealth(), 2000);
            } else {
                console.error('Auto-recovery failed:', result.error);
                
                // If restore failed and this is our last attempt, try emergency recovery
                if (this.consecutiveFailures >= this.maxAutoRecoveryAttempts) {
                    await this.emergencyRecovery();
                }
            }
            
        } catch (error) {
            console.error('Error during auto-recovery:', error);
        }
    }

    async emergencyRecovery() {
        try {
            console.warn('Attempting EMERGENCY database recovery...');
            
            const response = await fetch('/api/database-emergency-recovery', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log('Emergency recovery successful:', result.message);
                this.showNotification('Emergency recovery successful. Database has been reset.', 'warning');
                this.consecutiveFailures = 0;
            } else {
                console.error('Emergency recovery failed:', result.error);
                this.showNotification('CRITICAL: Database cannot be recovered. Please contact support.', 'error');
            }
            
        } catch (error) {
            console.error('Error during emergency recovery:', error);
            this.showNotification('CRITICAL: Emergency recovery failed. Please contact support.', 'error');
        }
    }

    async createManualBackup() {
        try {
            const response = await fetch('/api/database-backup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification(`Backup created: ${result.backup_path}`, 'success');
                return true;
            } else {
                this.showNotification(`Backup failed: ${result.error}`, 'error');
                return false;
            }
            
        } catch (error) {
            console.error('Error creating backup:', error);
            this.showNotification(`Backup error: ${error.message}`, 'error');
            return false;
        }
    }

    updateHealthUI(health, status) {
        // Update health indicator in UI
        const healthIndicator = document.getElementById('dbHealthIndicator');
        if (healthIndicator) {
            healthIndicator.className = `health-indicator health-${status}`;
            healthIndicator.title = health.message || health.error || 'Unknown status';
        }

        // Update detailed health panel if visible
        const healthPanel = document.getElementById('dbHealthPanel');
        if (healthPanel) {
            this.renderHealthPanel(healthPanel, health, status);
        }
    }

    renderHealthPanel(container, health, status) {
        const statusIcons = {
            'healthy': '<i class="bi bi-check-circle-fill text-success"></i>',
            'unhealthy': '<i class="bi bi-exclamation-triangle-fill text-danger"></i>',
            'error': '<i class="bi bi-x-circle-fill text-danger"></i>'
        };

        const statusLabels = {
            'healthy': '<span class="badge bg-success">Healthy</span>',
            'unhealthy': '<span class="badge bg-danger">Unhealthy</span>',
            'error': '<span class="badge bg-warning">Error</span>'
        };

        const html = `
            <div class="health-panel-header">
                ${statusIcons[status]} ${statusLabels[status]}
                <button class="btn btn-sm btn-outline-primary float-end" onclick="dbHealthMonitor.checkHealth()">
                    <i class="bi bi-arrow-clockwise"></i> Refresh
                </button>
            </div>
            <div class="health-panel-details">
                ${health.message ? `<p><strong>Message:</strong> ${health.message}</p>` : ''}
                ${health.error ? `<p class="text-danger"><strong>Error:</strong> ${health.error}</p>` : ''}
                ${health.db_size_mb !== undefined ? `<p><strong>Database Size:</strong> ${health.db_size_mb.toFixed(2)} MB</p>` : ''}
                ${health.backup_count !== undefined ? `<p><strong>Backups Available:</strong> ${health.backup_count}</p>` : ''}
                ${health.last_check ? `<p><small>Last Check: ${new Date(health.last_check).toLocaleString()}</small></p>` : ''}
            </div>
            <div class="health-panel-actions mt-3">
                <button class="btn btn-sm btn-primary" onclick="dbHealthMonitor.createManualBackup()">
                    <i class="bi bi-shield-check"></i> Create Backup
                </button>
                ${status !== 'healthy' ? `
                    <button class="btn btn-sm btn-warning ms-2" onclick="dbHealthMonitor.attemptAutoRecovery()">
                        <i class="bi bi-arrow-counterclockwise"></i> Attempt Recovery
                    </button>
                ` : ''}
            </div>
        `;

        container.innerHTML = html;
    }

    showNotification(message, type = 'info') {
        // Try to use existing toast system if available
        if (typeof showToast === 'function') {
            showToast(message, type);
            return;
        }

        // Fallback: Use Bootstrap toast if available
        const toastContainer = document.querySelector('.toast-container');
        if (toastContainer) {
            const toastHtml = `
                <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} border-0" role="alert">
                    <div class="d-flex">
                        <div class="toast-body">${message}</div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                    </div>
                </div>
            `;
            toastContainer.insertAdjacentHTML('beforeend', toastHtml);
            const toastElement = toastContainer.lastElementChild;
            const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
            toast.show();
            setTimeout(() => toastElement.remove(), 6000);
        } else {
            // Final fallback: console
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }

    getHealthStatus() {
        return this.lastHealthStatus;
    }

    isHealthy() {
        return this.lastHealthStatus && this.lastHealthStatus.healthy === true;
    }
}

// Global instance
const dbHealthMonitor = new DatabaseHealthMonitor();

// Start monitoring when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing database health monitoring...');
    dbHealthMonitor.startMonitoring();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DatabaseHealthMonitor, dbHealthMonitor };
}

