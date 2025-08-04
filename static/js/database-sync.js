/**
 * Database Synchronization Module
 * Handles real-time database change notifications across all browser sessions
 */

class DatabaseSync {
    constructor() {
        this.pollingInterval = 5000; // 5 seconds
        this.isPolling = false;
        this.lastChangeCheck = 0;
        this.pendingChanges = [];
        this.changeHandlers = new Map();
        this.isInitialized = false;
        
        // Register default handlers
        this.registerDefaultHandlers();
    }
    
    /**
     * Initialize the database synchronization
     */
    async initialize() {
        if (this.isInitialized) return;
        
        try {
            // Start polling for changes
            this.startPolling();
            this.isInitialized = true;
            console.log('Database synchronization initialized');
        } catch (error) {
            console.error('Failed to initialize database synchronization:', error);
        }
    }
    
    /**
     * Start polling for database changes
     */
    startPolling() {
        if (this.isPolling) return;
        
        this.isPolling = true;
        this.pollForChanges();
        console.log('Started polling for database changes');
    }
    
    /**
     * Stop polling for database changes
     */
    stopPolling() {
        this.isPolling = false;
        console.log('Stopped polling for database changes');
    }
    
    /**
     * Poll for pending database changes
     */
    async pollForChanges() {
        if (!this.isPolling) return;
        
        try {
            const response = await fetch('/api/pending-changes');
            if (response.ok) {
                const data = await response.json();
                
                if (data.success && data.changes && data.changes.length > 0) {
                    console.log(`Received ${data.changes.length} pending changes`);
                    await this.processChanges(data.changes);
                }
            }
        } catch (error) {
            console.warn('Error polling for changes:', error);
        }
        
        // Schedule next poll
        setTimeout(() => this.pollForChanges(), this.pollingInterval);
    }
    
    /**
     * Process received database changes
     */
    async processChanges(changes) {
        for (const change of changes) {
            try {
                await this.handleChange(change);
            } catch (error) {
                console.error('Error processing change:', change, error);
            }
        }
    }
    
    /**
     * Handle a specific database change
     */
    async handleChange(change) {
        console.log('Processing change:', change);
        
        // Call registered handlers for this change type
        const handlers = this.changeHandlers.get(change.change_type) || [];
        for (const handler of handlers) {
            try {
                await handler(change);
            } catch (error) {
                console.error('Error in change handler:', error);
            }
        }
        
        // Handle specific change types
        switch (change.change_type) {
            case 'lineage_update':
                await this.handleLineageUpdate(change);
                break;
            case 'sovereign_lineage_set':
                await this.handleSovereignLineageSet(change);
                break;
            case 'strain_add':
                await this.handleStrainAdd(change);
                break;
            case 'product_update':
                await this.handleProductUpdate(change);
                break;
            case 'database_refresh':
                await this.handleDatabaseRefresh(change);
                break;
            default:
                console.log('Unknown change type:', change.change_type);
        }
    }
    
    /**
     * Handle lineage update changes
     */
    async handleLineageUpdate(change) {
        const { strain_name, old_lineage, new_lineage } = change.details;
        
        // Emit lineage update start event
        document.dispatchEvent(new CustomEvent('lineageUpdateStart', {
            detail: { strain_name, old_lineage, new_lineage }
        }));
        
        // Update UI if the strain is currently displayed
        this.updateStrainLineageInUI(strain_name, new_lineage);
        
        // Show notification to user
        this.showNotification(`Lineage updated: ${strain_name} (${old_lineage} → ${new_lineage})`);
        
        // Emit lineage update end event
        document.dispatchEvent(new CustomEvent('lineageUpdateEnd', {
            detail: { strain_name, old_lineage, new_lineage }
        }));
    }
    
    /**
     * Handle sovereign lineage set changes
     */
    async handleSovereignLineageSet(change) {
        const { strain_name, sovereign_lineage } = change.details;
        
        // Emit lineage update start event
        document.dispatchEvent(new CustomEvent('lineageUpdateStart', {
            detail: { strain_name, sovereign_lineage }
        }));
        
        // Update UI if the strain is currently displayed
        this.updateStrainLineageInUI(strain_name, sovereign_lineage, true);
        
        // Show notification to user
        this.showNotification(`Sovereign lineage set: ${strain_name} → ${sovereign_lineage}`);
        
        // Emit lineage update end event
        document.dispatchEvent(new CustomEvent('lineageUpdateEnd', {
            detail: { strain_name, sovereign_lineage }
        }));
    }
    
    /**
     * Handle new strain additions
     */
    async handleStrainAdd(change) {
        const { strain_name } = change.details;
        
        // Refresh available tags to include new strain
        if (typeof TagManager !== 'undefined' && TagManager.refreshAvailableTags) {
            await TagManager.refreshAvailableTags();
        }
        
        // Show notification to user
        this.showNotification(`New strain added: ${strain_name}`);
    }
    
    /**
     * Handle product updates
     */
    async handleProductUpdate(change) {
        const { product_name } = change.details;
        
        // Refresh available tags to reflect product changes
        if (typeof TagManager !== 'undefined' && TagManager.refreshAvailableTags) {
            await TagManager.refreshAvailableTags();
        }
        
        // Show notification to user
        this.showNotification(`Product updated: ${product_name}`);
    }
    
    /**
     * Handle database refresh
     */
    async handleDatabaseRefresh(change) {
        const { reason } = change.details;
        
        // Refresh the entire application state
        if (typeof TagManager !== 'undefined' && TagManager.refreshAll) {
            await TagManager.refreshAll();
        }
        
        // Show notification to user
        this.showNotification(`Database refreshed: ${reason}`);
    }
    
    /**
     * Update strain lineage in the UI
     */
    updateStrainLineageInUI(strainName, newLineage, isSovereign = false) {
        // Find all elements that display this strain's lineage
        const lineageElements = document.querySelectorAll(`[data-strain="${strainName}"]`);
        
        for (const element of lineageElements) {
            const lineageDisplay = element.querySelector('.lineage-display');
            if (lineageDisplay) {
                lineageDisplay.textContent = newLineage;
                if (isSovereign) {
                    lineageDisplay.classList.add('sovereign-lineage');
                } else {
                    lineageDisplay.classList.remove('sovereign-lineage');
                }
            }
        }
    }
    
    /**
     * Show a notification to the user
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    /**
     * Register a handler for a specific change type
     */
    registerChangeHandler(changeType, handler) {
        if (!this.changeHandlers.has(changeType)) {
            this.changeHandlers.set(changeType, []);
        }
        this.changeHandlers.get(changeType).push(handler);
    }
    
    /**
     * Register default handlers
     */
    registerDefaultHandlers() {
        // Register handlers for common change types
        this.registerChangeHandler('lineage_update', (change) => {
            console.log('Lineage update detected:', change);
        });
        
        this.registerChangeHandler('database_refresh', (change) => {
            console.log('Database refresh detected:', change);
        });
    }
    
    /**
     * Get session statistics
     */
    async getSessionStats() {
        try {
            const response = await fetch('/api/session-stats');
            if (response.ok) {
                const data = await response.json();
                return data.stats;
            }
        } catch (error) {
            console.error('Error getting session stats:', error);
        }
        return null;
    }
    
    /**
     * Clear current session
     */
    async clearSession() {
        try {
            const response = await fetch('/api/clear-session', { method: 'POST' });
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    console.log('Session cleared successfully');
                    // Reload page to reset state
                    window.location.reload();
                }
            }
        } catch (error) {
            console.error('Error clearing session:', error);
        }
    }
    
    /**
     * Check if there are pending changes
     */
    async checkPendingChanges() {
        try {
            const response = await fetch('/api/status');
            if (response.ok) {
                const data = await response.json();
                return data.has_pending_changes || false;
            }
        } catch (error) {
            console.error('Error checking pending changes:', error);
        }
        return false;
    }
}

// Global instance
window.DatabaseSync = new DatabaseSync();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.DatabaseSync.initialize();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DatabaseSync;
} 