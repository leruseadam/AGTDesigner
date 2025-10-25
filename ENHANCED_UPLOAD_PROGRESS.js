/**
 * ENHANCED UPLOAD PROGRESS - Real-time Excel processing feedback
 * Provides detailed progress tracking with visual feedback and time estimates
 */

class EnhancedUploadProgress {
    constructor() {
        this.currentFilename = null;
        this.progressInterval = null;
        this.progressElement = null;
        this.statusElement = null;
        this.isPolling = false;
        
        // Progress tracking
        this.startTime = null;
        this.lastProgress = 0;
        this.stuckCounter = 0;
        
        // UI Elements
        this.progressBar = null;
        this.progressText = null;
        this.stageText = null;
        this.timeEstimate = null;
        
        // Initialize UI
        this.createProgressUI();
    }
    
    createProgressUI() {
        // Create enhanced progress container
        const progressHtml = `
            <div id="enhanced-progress-container" class="progress-container" style="display: none;">
                <div class="progress-header">
                    <h4 id="progress-title">Processing Excel File</h4>
                    <button id="progress-cancel" class="btn-cancel" onclick="cancelProcessing()">×</button>
                </div>
                
                <div class="progress-main">
                    <div class="progress-bar-container">
                        <div id="progress-bar" class="progress-bar">
                            <div id="progress-fill" class="progress-fill"></div>
                            <div id="progress-text" class="progress-text">0%</div>
                        </div>
                    </div>
                    
                    <div class="progress-details">
                        <div id="stage-text" class="stage-text">Initializing...</div>
                        <div class="progress-stats">
                            <span id="rows-processed">0 rows processed</span>
                            <span id="time-estimate" class="time-estimate"></span>
                        </div>
                    </div>
                    
                    <div id="strategy-info" class="strategy-info" style="display: none;">
                        <small>Using <span id="strategy-name">optimized</span> processing strategy</small>
                    </div>
                </div>
                
                <div id="progress-log" class="progress-log" style="display: none;">
                    <div class="log-header">
                        <span>Processing Log</span>
                        <button onclick="toggleProgressLog()">Toggle</button>
                    </div>
                    <div id="log-content" class="log-content"></div>
                </div>
            </div>
        `;
        
        // Add to page if not exists
        if (!document.getElementById('enhanced-progress-container')) {
            const uploadSection = document.querySelector('.upload-section') || document.body;
            uploadSection.insertAdjacentHTML('afterbegin', progressHtml);
        }
        
        // Cache UI elements
        this.progressElement = document.getElementById('enhanced-progress-container');
        this.progressBar = document.getElementById('progress-fill');
        this.progressText = document.getElementById('progress-text');
        this.stageText = document.getElementById('stage-text');
        this.timeEstimate = document.getElementById('time-estimate');
        this.rowsProcessed = document.getElementById('rows-processed');
        this.strategyInfo = document.getElementById('strategy-info');
        this.strategyName = document.getElementById('strategy-name');
        this.logContent = document.getElementById('log-content');
    }
    
    startProgress(filename) {
        console.log('🚀 Enhanced progress tracking started for:', filename);
        
        this.currentFilename = filename;
        this.startTime = Date.now();
        this.lastProgress = 0;
        this.stuckCounter = 0;
        this.isPolling = true;
        
        // Show progress UI
        this.showProgress();
        
        // Start polling for progress
        this.startProgressPolling();
        
        // Add styles if needed
        this.addProgressStyles();
    }
    
    showProgress() {
        if (this.progressElement) {
            this.progressElement.style.display = 'block';
            this.progressElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    hideProgress() {
        if (this.progressElement) {
            this.progressElement.style.display = 'none';
        }
        this.stopProgressPolling();
    }
    
    startProgressPolling() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        // CPU-aware polling interval
        const pollingInterval = (window.CPUOptimizer && window.CPUOptimizer.isHighCPU()) ? 3000 : 1000;
        
        // Poll with adaptive interval for progress updates
        this.progressInterval = setInterval(() => {
            // Skip polling if CPU usage is high
            if (window.CPUOptimizer && window.CPUOptimizer.isHighCPU()) {
                console.log("🔄 Skipping progress polling due to high CPU usage");
                return;
            }
            this.fetchProgress();
        }, pollingInterval);
        
        // Immediate first fetch
        this.fetchProgress();
    }
    
    stopProgressPolling() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        this.isPolling = false;
    }
    
    async fetchProgress() {
        if (!this.currentFilename || !this.isPolling) {
            return;
        }
        
        try {
            const response = await fetch(`/api/processing-progress?filename=${encodeURIComponent(this.currentFilename)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const progressData = await response.json();
            this.updateProgressUI(progressData);
            
            // Check if processing is complete
            if (progressData.status === 'ready') {
                this.onProcessingComplete(progressData);
            } else if (progressData.status.startsWith('error')) {
                this.onProcessingError(progressData);
            }
            
        } catch (error) {
            console.warn('Progress fetch error:', error);
            this.handleProgressError(error);
        }
    }
    
    updateProgressUI(data) {
        const progress = Math.max(0, Math.min(100, data.progress || 0));
        const stage = data.stage || 'processing';
        const stageDescription = data.stage_description || 'Processing...';
        const rowsProcessed = data.rows_processed || 0;
        const processingTime = data.processing_time || 0;
        const estimatedTimeRemaining = data.estimated_time_remaining;
        
        // Update progress bar
        if (this.progressBar) {
            this.progressBar.style.width = `${progress}%`;
            
            // Animate progress bar
            this.progressBar.style.transition = 'width 0.5s ease-in-out';
            
            // Color based on progress
            if (progress < 25) {
                this.progressBar.style.backgroundColor = '#ffc107'; // Yellow - starting
            } else if (progress < 75) {
                this.progressBar.style.backgroundColor = '#17a2b8'; // Blue - processing
            } else if (progress < 100) {
                this.progressBar.style.backgroundColor = '#28a745'; // Green - nearly done
            } else {
                this.progressBar.style.backgroundColor = '#28a745'; // Green - complete
            }
        }
        
        // Update progress text
        if (this.progressText) {
            this.progressText.textContent = `${Math.round(progress)}%`;
        }
        
        // Update stage description
        if (this.stageText) {
            this.stageText.textContent = stageDescription;
            
            // Add stage-specific icons
            const stageIcon = this.getStageIcon(stage);
            this.stageText.innerHTML = `${stageIcon} ${stageDescription}`;
        }
        
        // Update rows processed
        if (this.rowsProcessed) {
            this.rowsProcessed.textContent = `${rowsProcessed.toLocaleString()} rows processed`;
        }
        
        // Update time estimate
        if (this.timeEstimate) {
            let timeText = '';
            
            if (estimatedTimeRemaining && estimatedTimeRemaining > 0) {
                if (estimatedTimeRemaining < 60) {
                    timeText = `~${Math.ceil(estimatedTimeRemaining)}s remaining`;
                } else {
                    const minutes = Math.ceil(estimatedTimeRemaining / 60);
                    timeText = `~${minutes}m remaining`;
                }
            } else if (processingTime > 0) {
                if (processingTime < 60) {
                    timeText = `${Math.ceil(processingTime)}s elapsed`;
                } else {
                    const minutes = Math.ceil(processingTime / 60);
                    timeText = `${minutes}m elapsed`;
                }
            }
            
            this.timeEstimate.textContent = timeText;
        }
        
        // Update strategy info
        if (data.optimization_active && this.strategyInfo) {
            this.strategyInfo.style.display = 'block';
            if (this.strategyName) {
                this.strategyName.textContent = data.strategy || 'optimized';
            }
        }
        
        // Check for stuck progress
        this.checkStuckProgress(progress);
        
        // Log progress update
        this.logProgress(data);
    }
    
    getStageIcon(stage) {
        const icons = {
            'analyzing': '🔍',
            'reading': '📖',
            'processing': '⚙️',
            'optimizing': '🚀',
            'finalizing': '✨',
            'complete': '✅',
            'error': '❌',
            'idle': '⏸️'
        };
        
        return icons[stage] || '📊';
    }
    
    checkStuckProgress(currentProgress) {
        if (currentProgress === this.lastProgress) {
            this.stuckCounter++;
            
            // If progress hasn't changed for 30 seconds, show warning
            if (this.stuckCounter > 30) {
                this.showStuckWarning();
            }
        } else {
            this.stuckCounter = 0;
            this.hideStuckWarning();
        }
        
        this.lastProgress = currentProgress;
    }
    
    showStuckWarning() {
        if (this.stageText && !this.stageText.textContent.includes('slow')) {
            this.stageText.innerHTML += ' <small style="color: orange;">(Processing may be slow for large files)</small>';
        }
    }
    
    hideStuckWarning() {
        // Remove warning text if it exists
        if (this.stageText) {
            this.stageText.innerHTML = this.stageText.innerHTML.replace(/ <small[^>]*>\(Processing may be slow[^<]*<\/small>/, '');
        }
    }
    
    onProcessingComplete(data) {
        console.log('✅ Processing complete:', data);
        
        // Update UI to show completion
        this.updateProgressUI({
            ...data,
            progress: 100,
            stage: 'complete',
            stage_description: `Complete! ${data.rows_processed?.toLocaleString()} rows loaded`
        });
        
        // Show success message
        this.showSuccessMessage(data);
        
        // Hide progress after delay
        setTimeout(() => {
            this.hideProgress();
            this.refreshPage();
        }, 3000);
    }
    
    onProcessingError(data) {
        console.error('❌ Processing error:', data);
        
        // Update UI to show error
        this.updateProgressUI({
            ...data,
            progress: 0,
            stage: 'error'
        });
        
        // Show error message
        this.showErrorMessage(data);
    }
    
    showSuccessMessage(data) {
        const message = `Excel processing completed successfully! ${data.rows_processed?.toLocaleString()} rows loaded.`;
        
        // Show browser notification if permitted
        this.showNotification('Processing Complete', message, 'success');
        
        // Update stage text with success
        if (this.stageText) {
            this.stageText.innerHTML = `✅ ${message}`;
            this.stageText.style.color = '#28a745';
        }
    }
    
    showErrorMessage(data) {
        const message = data.stage_description || 'Processing failed';
        
        // Show browser notification
        this.showNotification('Processing Failed', message, 'error');
        
        // Update stage text with error
        if (this.stageText) {
            this.stageText.innerHTML = `❌ ${message}`;
            this.stageText.style.color = '#dc3545';
        }
    }
    
    showNotification(title, message, type) {
        // Try browser notification
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: type === 'success' ? '/static/success-icon.png' : '/static/error-icon.png'
            });
        }
        
        // Fallback to console
        console.log(`${title}: ${message}`);
    }
    
    handleProgressError(error) {
        console.warn('Progress tracking error:', error);
        
        // Don't hide progress immediately - might be temporary network issue
        // Just show a subtle warning
        if (this.timeEstimate) {
            this.timeEstimate.textContent = '(Connection issue - retrying...)';
            this.timeEstimate.style.color = '#ffc107';
        }
    }
    
    logProgress(data) {
        if (!this.logContent) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = `[${timestamp}] ${data.stage_description} (${Math.round(data.progress)}%)`;
        
        // Add to log
        const logLine = document.createElement('div');
        logLine.className = 'log-line';
        logLine.textContent = logEntry;
        
        this.logContent.appendChild(logLine);
        
        // Keep only last 20 entries
        while (this.logContent.children.length > 20) {
            this.logContent.removeChild(this.logContent.firstChild);
        }
        
        // Auto-scroll to bottom
        this.logContent.scrollTop = this.logContent.scrollHeight;
    }
    
    refreshPage() {
        // Refresh the page to show updated data
        window.location.reload();
    }
    
    addProgressStyles() {
        // Add CSS styles if not already present
        if (document.getElementById('enhanced-progress-styles')) {
            return;
        }
        
        const styles = `
            <style id="enhanced-progress-styles">
            .progress-container {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                border: 2px solid #007bff;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.2);
                z-index: 10000;
                min-width: 400px;
                max-width: 500px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
            
            .progress-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 12px;
                border-bottom: 1px solid #e9ecef;
            }
            
            .progress-header h4 {
                margin: 0;
                color: #495057;
                font-size: 18px;
                font-weight: 600;
            }
            
            .btn-cancel {
                background: #dc3545;
                color: white;
                border: none;
                border-radius: 50%;
                width: 32px;
                height: 32px;
                cursor: pointer;
                font-size: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background 0.2s;
            }
            
            .btn-cancel:hover {
                background: #c82333;
            }
            
            .progress-bar-container {
                margin-bottom: 16px;
            }
            
            .progress-bar {
                position: relative;
                height: 24px;
                background: #e9ecef;
                border-radius: 12px;
                overflow: hidden;
                border: 1px solid #dee2e6;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #007bff, #0056b3);
                border-radius: 12px;
                transition: width 0.5s ease-in-out;
                position: relative;
                overflow: hidden;
            }
            
            .progress-fill::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
                animation: shimmer 2s infinite;
            }
            
            @keyframes shimmer {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
            }
            
            .progress-text {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: #495057;
                font-weight: 600;
                font-size: 12px;
                text-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            
            .stage-text {
                font-size: 14px;
                color: #6c757d;
                margin-bottom: 8px;
                font-weight: 500;
            }
            
            .progress-stats {
                display: flex;
                justify-content: space-between;
                font-size: 12px;
                color: #868e96;
            }
            
            .time-estimate {
                font-style: italic;
            }
            
            .strategy-info {
                margin-top: 12px;
                padding: 8px 12px;
                background: #e3f2fd;
                border-radius: 6px;
                font-size: 12px;
                color: #1976d2;
            }
            
            .progress-log {
                margin-top: 16px;
                border-top: 1px solid #e9ecef;
                padding-top: 16px;
            }
            
            .log-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
                font-size: 12px;
                font-weight: 600;
                color: #495057;
            }
            
            .log-content {
                max-height: 120px;
                overflow-y: auto;
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
                font-family: monospace;
            }
            
            .log-line {
                margin-bottom: 2px;
                color: #495057;
            }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }
}

// Global instance
let enhancedProgress = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    enhancedProgress = new EnhancedUploadProgress();
    
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
});

// Functions for integration with existing upload code
function startEnhancedProgress(filename) {
    if (enhancedProgress) {
        enhancedProgress.startProgress(filename);
    }
}

function stopEnhancedProgress() {
    if (enhancedProgress) {
        enhancedProgress.hideProgress();
    }
}

function cancelProcessing() {
    if (enhancedProgress) {
        enhancedProgress.hideProgress();
    }
    // Could add actual cancellation logic here
    console.log('Processing cancelled by user');
}

function toggleProgressLog() {
    const logContent = document.getElementById('log-content');
    if (logContent) {
        logContent.style.display = logContent.style.display === 'none' ? 'block' : 'none';
    }
}
