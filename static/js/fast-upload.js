/**
 * Fast Excel Upload Handler
 * Provides optimized Excel file upload with better performance
 */

class FastUploadHandler {
    constructor() {
        this.uploadEndpoint = '/upload-fast';
        this.statusEndpoint = '/upload-status';
        this.isUploading = false;
        this.currentUploadId = null;
    }

    /**
     * Initialize fast upload functionality
     */
    init() {
        this.setupEventListeners();
        this.createFastUploadButton();
    }

    /**
     * Setup event listeners for fast upload
     */
    setupEventListeners() {
        // Listen for file input changes
        document.addEventListener('change', (e) => {
            if (e.target.id === 'fileInput' && e.target.files[0]) {
                this.handleFileSelection(e.target.files[0]);
            }
        });

        // Listen for drag and drop
        const uploadArea = document.querySelector('.upload-area');
        if (uploadArea) {
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('drag-over');
            });

            uploadArea.addEventListener('dragleave', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('drag-over');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('drag-over');
                
                const files = e.dataTransfer.files;
                if (files.length > 0 && files[0].type.includes('sheet')) {
                    this.handleFileSelection(files[0]);
                }
            });
        }
    }

    /**
     * Create fast upload button
     */
    createFastUploadButton() {
        const uploadContainer = document.querySelector('.modern-upload-bar');
        if (uploadContainer && !document.getElementById('fastUploadBtn')) {
            const fastUploadBtn = document.createElement('button');
            fastUploadBtn.id = 'fastUploadBtn';
            fastUploadBtn.className = 'btn btn-success btn-sm ms-2';
            fastUploadBtn.innerHTML = `
                <svg class="me-1" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path>
                </svg>
                Fast Upload
            `;
            fastUploadBtn.onclick = () => this.triggerFastUpload();
            uploadContainer.appendChild(fastUploadBtn);
        }
    }

    /**
     * Handle file selection
     */
    handleFileSelection(file) {
        if (!file.type.includes('sheet')) {
            this.showMessage('Please select an Excel file (.xlsx)', 'warning');
            return;
        }

        // Show file info
        this.showFileInfo(file);
        
        // Auto-upload if fast upload is enabled
        if (document.getElementById('fastUploadBtn')) {
            this.uploadFile(file);
        }
    }

    /**
     * Trigger fast upload
     */
    triggerFastUpload() {
        const fileInput = document.getElementById('fileInput');
        if (fileInput.files[0]) {
            this.uploadFile(fileInput.files[0]);
        } else {
            fileInput.click();
        }
    }

    /**
     * Upload file using fast endpoint
     */
    async uploadFile(file) {
        if (this.isUploading) {
            this.showMessage('Upload already in progress', 'info');
            return;
        }

        this.isUploading = true;
        this.showUploadProgress('Starting fast upload...');

        try {
            const formData = new FormData();
            formData.append('file', file);

            const startTime = performance.now();
            
            const response = await fetch(this.uploadEndpoint, {
                method: 'POST',
                body: formData
            });

            const uploadTime = performance.now() - startTime;
            const result = await response.json();

            if (response.ok && result.success) {
                this.currentUploadId = result.upload_id;
                this.showUploadProgress(`Upload completed in ${uploadTime.toFixed(0)}ms`);
                
                // Check status if upload ID provided
                if (result.upload_id) {
                    this.checkUploadStatus(result.upload_id);
                } else {
                    this.showMessage('File uploaded successfully!', 'success');
                    this.reloadPage();
                }
            } else {
                throw new Error(result.error || 'Upload failed');
            }

        } catch (error) {
            console.error('Upload error:', error);
            this.showMessage(`Upload failed: ${error.message}`, 'danger');
        } finally {
            this.isUploading = false;
        }
    }

    /**
     * Check upload status
     */
    async checkUploadStatus(uploadId) {
        try {
            const response = await fetch(`${this.statusEndpoint}/${uploadId}`);
            const result = await response.json();

            if (response.ok) {
                if (result.status === 'completed') {
                    this.showMessage('File processed successfully!', 'success');
                    this.reloadPage();
                } else if (result.status === 'error') {
                    throw new Error(result.error || 'Processing failed');
                } else {
                    // Still processing, check again
                    setTimeout(() => this.checkUploadStatus(uploadId), 1000);
                }
            } else {
                throw new Error('Failed to check upload status');
            }
        } catch (error) {
            console.error('Status check error:', error);
            this.showMessage(`Status check failed: ${error.message}`, 'warning');
        }
    }

    /**
     * Show file information
     */
    showFileInfo(file) {
        const fileInfo = document.getElementById('currentFileInfo');
        if (fileInfo) {
            const size = (file.size / 1024 / 1024).toFixed(2);
            fileInfo.innerHTML = `
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <polyline points="9 9 12 12 15 9"></polyline>
                </svg>
                <span>${file.name} (${size} MB)</span>
            `;
        }
    }

    /**
     * Show upload progress
     */
    showUploadProgress(message) {
        const uploadStatus = document.getElementById('uploadStatus');
        if (uploadStatus) {
            uploadStatus.innerHTML = `
                <div class="alert alert-info d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    ${message}
                </div>
            `;
        }
    }

    /**
     * Show message
     */
    showMessage(message, type = 'info') {
        const uploadStatus = document.getElementById('uploadStatus');
        if (uploadStatus) {
            uploadStatus.innerHTML = `
                <div class="alert alert-${type}">
                    ${message}
                </div>
            `;
        }

        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (uploadStatus) {
                uploadStatus.innerHTML = '';
            }
        }, 5000);
    }

    /**
     * Reload page to show updated data
     */
    reloadPage() {
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    }
}

// Initialize fast upload when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const fastUpload = new FastUploadHandler();
    fastUpload.init();
});

// Export for global access
window.FastUploadHandler = FastUploadHandler;
