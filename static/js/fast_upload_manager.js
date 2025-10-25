// Excel Upload Performance Optimization for Frontend
// This script optimizes the frontend upload experience for better performance

class FastUploadManager {
    constructor() {
        this.uploadInProgress = false;
        this.chunkSize = 1024 * 1024; // 1MB chunks
        this.maxFileSize = 50 * 1024 * 1024; // 50MB max
        this.uploadTimeout = 30000; // 30 seconds timeout
    }

    async uploadFile(file, progressCallback = null) {
        if (this.uploadInProgress) {
            console.log('🚫 Upload already in progress');
            return { success: false, error: 'Upload already in progress' };
        }

        this.uploadInProgress = true;
        const startTime = Date.now();

        try {
            // Validate file
            if (!this.validateFile(file)) {
                return { success: false, error: 'Invalid file' };
            }

            console.log(`🚀 Starting fast upload: ${file.name} (${(file.size / 1024 / 1024).toFixed(1)}MB)`);

            // Choose upload strategy based on file size
            if (file.size > 10 * 1024 * 1024) { // 10MB threshold
                return await this.uploadLargeFile(file, progressCallback);
            } else {
                return await this.uploadSmallFile(file, progressCallback);
            }

        } catch (error) {
            console.error('❌ Upload error:', error);
            return { success: false, error: error.message };
        } finally {
            this.uploadInProgress = false;
            const duration = Date.now() - startTime;
            console.log(`⏱️ Upload completed in ${duration}ms`);
        }
    }

    validateFile(file) {
        // File type validation
        const allowedTypes = [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel'
        ];
        
        if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.xlsx')) {
            console.error('❌ Invalid file type:', file.type);
            return false;
        }

        // File size validation
        if (file.size > this.maxFileSize) {
            console.error(`❌ File too large: ${(file.size / 1024 / 1024).toFixed(1)}MB (max: ${this.maxFileSize / 1024 / 1024}MB)`);
            return false;
        }

        if (file.size === 0) {
            console.error('❌ Empty file');
            return false;
        }

        return true;
    }

    async uploadSmallFile(file, progressCallback) {
        const formData = new FormData();
        formData.append('file', file);

        // Use fast upload endpoint
        const response = await this.makeRequest('/upload-fast', {
            method: 'POST',
            body: formData,
            timeout: this.uploadTimeout
        });

        if (progressCallback) {
            progressCallback(100);
        }

        return response;
    }

    async uploadLargeFile(file, progressCallback) {
        // For large files, use progressive upload
        const formData = new FormData();
        formData.append('file', file);

        const response = await this.makeRequest('/upload-progressive', {
            method: 'POST',
            body: formData,
            timeout: this.uploadTimeout * 2 // Longer timeout for large files
        });

        if (progressCallback) {
            progressCallback(100);
        }

        return response;
    }

    async makeRequest(url, options) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), options.timeout || this.uploadTimeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return { success: true, data };

        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('Upload timeout - file may be too large');
            }
            
            throw error;
        }
    }

    // Performance monitoring
    logPerformance(operation, duration, details = '') {
        console.log(`📊 Performance: ${operation} took ${duration}ms ${details}`);
        
        // Send to analytics if available
        if (window.gtag) {
            window.gtag('event', 'upload_performance', {
                'operation': operation,
                'duration': duration,
                'details': details
            });
        }
    }
}

// Enhanced upload progress display
class UploadProgressDisplay {
    constructor() {
        this.progressContainer = null;
        this.progressBar = null;
        this.statusText = null;
        this.createProgressUI();
    }

    createProgressUI() {
        // Create progress container
        this.progressContainer = document.createElement('div');
        this.progressContainer.id = 'fast-upload-progress';
        this.progressContainer.style.cssText = `
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
            display: none;
        `;

        // Create progress bar
        this.progressBar = document.createElement('div');
        this.progressBar.style.cssText = `
            width: 100%;
            height: 20px;
            background-color: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 16px;
        `;

        const progressFill = document.createElement('div');
        progressFill.id = 'progress-fill';
        progressFill.style.cssText = `
            height: 100%;
            background: linear-gradient(90deg, #007bff, #0056b3);
            width: 0%;
            transition: width 0.3s ease;
        `;

        this.progressBar.appendChild(progressFill);

        // Create status text
        this.statusText = document.createElement('div');
        this.statusText.id = 'upload-status';
        this.statusText.style.cssText = `
            text-align: center;
            font-size: 16px;
            color: #333;
            margin-bottom: 8px;
        `;

        // Create cancel button
        const cancelButton = document.createElement('button');
        cancelButton.textContent = 'Cancel';
        cancelButton.style.cssText = `
            background: #dc3545;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 8px;
        `;
        cancelButton.onclick = () => this.hide();

        // Assemble UI
        this.progressContainer.appendChild(this.statusText);
        this.progressContainer.appendChild(this.progressBar);
        this.progressContainer.appendChild(cancelButton);

        document.body.appendChild(this.progressContainer);
    }

    show(message = 'Uploading...') {
        this.statusText.textContent = message;
        this.progressContainer.style.display = 'block';
    }

    updateProgress(percent, message = null) {
        const progressFill = document.getElementById('progress-fill');
        if (progressFill) {
            progressFill.style.width = `${percent}%`;
        }
        
        if (message) {
            this.statusText.textContent = message;
        }
    }

    hide() {
        this.progressContainer.style.display = 'none';
        this.updateProgress(0);
    }
}

// Initialize fast upload system
const fastUploadManager = new FastUploadManager();
const uploadProgressDisplay = new UploadProgressDisplay();

// Override default upload behavior
function enhanceUploadPerformance() {
    const fileInput = document.getElementById('databaseFile');
    if (!fileInput) return;

    // Remove existing event listeners
    const newFileInput = fileInput.cloneNode(true);
    fileInput.parentNode.replaceChild(newFileInput, fileInput);

    // Add enhanced upload handler
    newFileInput.addEventListener('change', async function(e) {
        const file = e.target.files[0];
        if (!file) return;

        console.log(`🚀 Enhanced upload starting for: ${file.name}`);

        // Show progress
        uploadProgressDisplay.show('Preparing upload...');

        try {
            // Upload with progress tracking
            const result = await fastUploadManager.uploadFile(file, (progress) => {
                uploadProgressDisplay.updateProgress(progress, `Uploading... ${progress}%`);
            });

            if (result.success) {
                uploadProgressDisplay.updateProgress(100, 'Upload complete!');
                
                // Hide progress after delay
                setTimeout(() => {
                    uploadProgressDisplay.hide();
                }, 2000);

                // Handle success
                if (window.handleUploadSuccess) {
                    window.handleUploadSuccess(result.data);
                } else {
                    // Fallback success handling - DON'T reload automatically
                    console.log('✅ Upload successful:', result.data);
                    // Removed automatic reload to prevent unwanted refreshes
                    // Users can manually refresh if needed
                }
            } else {
                uploadProgressDisplay.hide();
                alert(`Upload failed: ${result.error}`);
            }

        } catch (error) {
            uploadProgressDisplay.hide();
            console.error('❌ Upload error:', error);
            alert(`Upload error: ${error.message}`);
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enhanceUploadPerformance);
} else {
    enhanceUploadPerformance();
}

console.log('🚀 Fast Upload Manager initialized');
