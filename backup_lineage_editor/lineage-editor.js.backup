/**
 * Robust Strain Lineage Editor
 * Completely rewritten for maximum stability and reliability
 */
class StrainLineageEditor {
    constructor() {
        this.isInitialized = false;
        this.isLoading = false;
        this.currentStrain = null;
        this.currentLineage = null;
        this.modal = null;
        this.modalElement = null;
        this.eventListenersAdded = false;
        this.mutationObserver = null;
        this.retryCount = 0;
        this.maxRetries = 3;
        this.userRequestedClose = false;
        this.modalState = 'closed'; // 'closed', 'opening', 'open', 'closing'
    }

    init() {
        console.log('StrainLineageEditor: Initializing...');
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeEditor());
        } else {
            this.initializeEditor();
        }
    }

    initializeEditor() {
        try {
            console.log('StrainLineageEditor: DOM ready, initializing editor...');
            
            // Check if modal element already exists
            this.modalElement = document.getElementById('strainLineageEditorModal');
            
            if (!this.modalElement) {
                console.log('StrainLineageEditor: Modal element not found, creating...');
                this.createModalElement();
            } else {
                console.log('StrainLineageEditor: Modal element found, reusing existing');
            }

            // Initialize Bootstrap modal with enhanced configuration
            if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined') {
                this.modal = new bootstrap.Modal(this.modalElement, {
                    backdrop: 'static',
                    keyboard: false,
                    focus: true
                });
                
                // Add enhanced event listeners
                this.setupEventListeners();
                this.setupMutationObserver();
                this.isInitialized = true;
                console.log('StrainLineageEditor: Successfully initialized');
            } else {
                console.error('StrainLineageEditor: Bootstrap not available');
                this.createFallbackModal();
            }
        } catch (error) {
            console.error('StrainLineageEditor: Initialization error:', error);
            this.createFallbackModal();
        }
    }

    createModalElement() {
        console.log('StrainLineageEditor: Creating modal element...');
        
        const modalHTML = `
            <div class="modal fade" id="strainLineageEditorModal" tabindex="-1" aria-labelledby="strainLineageEditorModalLabel" aria-hidden="true" data-bs-backdrop="static" data-bs-keyboard="false">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="strainLineageEditorModalLabel">Edit Strain Lineage</h5>
                            <button type="button" class="btn-close" id="lineageEditorCloseBtn" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div id="lineageEditorContent">
                                <div class="text-center">
                                    <div class="spinner-border" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                    <p class="mt-2">Loading lineage editor...</p>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" id="lineageEditorCancelBtn">Cancel</button>
                            <button type="button" class="btn btn-primary" id="saveStrainLineageBtn">Save Changes</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.modalElement = document.getElementById('strainLineageEditorModal');
    }

    createFallbackModal() {
        console.log('StrainLineageEditor: Creating fallback modal...');
        
        // Create a simple modal without Bootstrap
        const modalHTML = `
            <div id="strainLineageEditorModal" class="fallback-modal" style="display: none;">
                <div class="fallback-modal-backdrop"></div>
                <div class="fallback-modal-dialog">
                    <div class="fallback-modal-content">
                        <div class="fallback-modal-header">
                            <h5>Edit Strain Lineage</h5>
                            <button type="button" class="fallback-modal-close" id="lineageEditorCloseBtn">&times;</button>
                        </div>
                        <div class="fallback-modal-body" id="lineageEditorContent">
                            <div class="text-center">
                                <p>Loading lineage editor...</p>
                            </div>
                        </div>
                        <div class="fallback-modal-footer">
                            <button type="button" class="btn btn-secondary" id="lineageEditorCancelBtn">Cancel</button>
                            <button type="button" class="btn btn-primary" id="saveStrainLineageBtn">Save Changes</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.modalElement = document.getElementById('strainLineageEditorModal');
        this.setupFallbackStyles();
        this.setupEventListeners();
        this.setupMutationObserver();
        this.isInitialized = true;
    }

    setupFallbackStyles() {
        const styles = `
            <style>
                .fallback-modal {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: 9999;
                }
                .fallback-modal-backdrop {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.5);
                }
                .fallback-modal-dialog {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    width: 90%;
                    max-width: 600px;
                    max-height: 90%;
                }
                .fallback-modal-content {
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                }
                .fallback-modal-header {
                    padding: 15px 20px;
                    border-bottom: 1px solid #dee2e6;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .fallback-modal-body {
                    padding: 20px;
                    max-height: 400px;
                    overflow-y: auto;
                }
                .fallback-modal-footer {
                    padding: 15px 20px;
                    border-top: 1px solid #dee2e6;
                    text-align: right;
                }
                .fallback-modal-close {
                    background: none;
                    border: none;
                    font-size: 24px;
                    cursor: pointer;
                }
            </style>
        `;
        
        if (!document.getElementById('fallback-modal-styles')) {
            const styleElement = document.createElement('div');
            styleElement.id = 'fallback-modal-styles';
            styleElement.innerHTML = styles;
            document.head.appendChild(styleElement);
        }
    }

    setupEventListeners() {
        if (this.eventListenersAdded || !this.modalElement) return;

        console.log('StrainLineageEditor: Setting up event listeners...');

        // Save button
        const saveButton = document.getElementById('saveStrainLineageBtn');
        if (saveButton) {
            saveButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.saveChanges();
            });
        }

        // Close button (X)
        const closeButton = document.getElementById('lineageEditorCloseBtn');
        if (closeButton) {
            closeButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.userRequestedClose = true;
                this.closeModal();
            });
        }

        // Cancel button
        const cancelButton = document.getElementById('lineageEditorCancelBtn');
        if (cancelButton) {
            cancelButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.userRequestedClose = true;
                this.closeModal();
            });
        }

        // Modal events for Bootstrap modal
        if (this.modal) {
            this.modalElement.addEventListener('hidden.bs.modal', (e) => {
                console.log('StrainLineageEditor: Modal hidden event');
                this.cleanup();
            });

            this.modalElement.addEventListener('shown.bs.modal', (e) => {
                console.log('StrainLineageEditor: Modal shown event');
                this.onModalShown();
            });

            this.modalElement.addEventListener('hide.bs.modal', (e) => {
                console.log('StrainLineageEditor: Modal hide event');
                // Prevent automatic hiding if we're in the middle of an operation
                if (this.isLoading || this.modalState === 'opening') {
                    e.preventDefault();
                    console.log('StrainLineageEditor: Prevented modal hide during loading/opening');
                }
            });

            // Additional Bootstrap modal events for stability
            this.modalElement.addEventListener('show.bs.modal', (e) => {
                console.log('StrainLineageEditor: Modal show event');
                this.modalState = 'opening';
            });

            this.modalElement.addEventListener('shown.bs.modal', (e) => {
                console.log('StrainLineageEditor: Modal shown event');
                this.modalState = 'open';
            });

            this.modalElement.addEventListener('hide.bs.modal', (e) => {
                console.log('StrainLineageEditor: Modal hide event');
                this.modalState = 'closing';
            });

            this.modalElement.addEventListener('hidden.bs.modal', (e) => {
                console.log('StrainLineageEditor: Modal hidden event');
                this.modalState = 'closed';
                this.cleanup();
            });
        }

        // Prevent clicks on backdrop from closing modal
        this.modalElement.addEventListener('click', (e) => {
            if (e.target === this.modalElement) {
                e.preventDefault();
                e.stopPropagation();
                console.log('StrainLineageEditor: Prevented backdrop click');
            }
        });

        // Additional stability measures to prevent background animation interference
        this.modalElement.addEventListener('focusout', (e) => {
            // Prevent focus loss from closing modal
            e.preventDefault();
            e.stopPropagation();
            console.log('StrainLineageEditor: Prevented focus loss');
        });

        // Prevent any animation-related events from affecting the modal
        this.modalElement.addEventListener('animationstart', (e) => {
            e.preventDefault();
            e.stopPropagation();
        });

        this.modalElement.addEventListener('animationend', (e) => {
            e.preventDefault();
            e.stopPropagation();
        });

        this.modalElement.addEventListener('transitionstart', (e) => {
            e.preventDefault();
            e.stopPropagation();
        });

        this.modalElement.addEventListener('transitionend', (e) => {
            e.preventDefault();
            e.stopPropagation();
        });

        // Prevent any CSS animation interference
        this.modalElement.addEventListener('webkitAnimationStart', (e) => {
            e.preventDefault();
            e.stopPropagation();
        });

        this.modalElement.addEventListener('webkitAnimationEnd', (e) => {
            e.preventDefault();
            e.stopPropagation();
        });

        // Prevent any transition interference
        this.modalElement.addEventListener('webkitTransitionStart', (e) => {
            e.preventDefault();
            e.stopPropagation();
        });

        this.modalElement.addEventListener('webkitTransitionEnd', (e) => {
            e.preventDefault();
            e.stopPropagation();
        });

        // Global event listeners to prevent modal interference
        document.addEventListener('keydown', (e) => {
            if (this.modalState === 'open' && e.key === 'Escape') {
                e.preventDefault();
                e.stopPropagation();
                console.log('StrainLineageEditor: Prevented escape key');
            }
        });

        // Prevent any scroll events from affecting the modal
        this.modalElement.addEventListener('scroll', (e) => {
            e.stopPropagation();
        });

        // Prevent any wheel events from affecting the modal
        this.modalElement.addEventListener('wheel', (e) => {
            e.stopPropagation();
        });

        this.eventListenersAdded = true;
        console.log('StrainLineageEditor: Event listeners setup complete');
    }

    setupMutationObserver() {
        if (this.mutationObserver) {
            this.mutationObserver.disconnect();
        }

        // Monitor for DOM changes that might affect the modal
        this.mutationObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    const target = mutation.target;
                    if (target === this.modalElement && this.modalState === 'open') {
                        // Ensure modal stays visible
                        if (target.style.display === 'none') {
                            console.log('StrainLineageEditor: Restored modal visibility after DOM change');
                            target.style.display = 'block';
                        }
                    }
                }
            });
        });

        if (this.modalElement) {
            this.mutationObserver.observe(this.modalElement, {
                attributes: true,
                attributeFilter: ['style', 'class']
            });
        }

        console.log('StrainLineageEditor: Mutation observer setup complete');
    }

    async openEditor(strainName, currentLineage) {
        console.log('StrainLineageEditor: Opening editor for', strainName, currentLineage);
        console.log('StrainLineageEditor: Current modal state:', this.modalState);
        console.log('StrainLineageEditor: Is loading:', this.isLoading);
        console.log('StrainLineageEditor: User requested close:', this.userRequestedClose);
        
        if (this.isLoading) {
            console.log('StrainLineageEditor: Already loading, ignoring request');
            return;
        }

        try {
            this.isLoading = true;
            this.currentStrain = strainName;
            this.currentLineage = currentLineage;
            this.userRequestedClose = false;

            // Ensure product database is enabled for lineage editor functionality
            await this.ensureProductDatabaseEnabled();

            // Wait for initialization if needed
            await this.waitForInitialization();

            // Load editor content
            await this.loadEditorContent();

            // Show modal
            this.showModal();

        } catch (error) {
            console.error('StrainLineageEditor: Error opening editor:', error);
            this.handleError('Failed to open lineage editor. Please try again.');
        } finally {
            this.isLoading = false;
        }
    }

    async waitForInitialization() {
        let attempts = 0;
        const maxAttempts = 10;
        
        while (!this.isInitialized && attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }
        
        if (!this.isInitialized) {
            throw new Error('Failed to initialize lineage editor');
        }
    }

    async loadEditorContent() {
        console.log('StrainLineageEditor: Loading editor content...');
        
        try {
            const contentElement = document.getElementById('lineageEditorContent');
            if (!contentElement) {
                throw new Error('Content element not found');
            }

            // Get product count for this strain
            const productCount = await this.getStrainProductCount(this.currentStrain);

            // Create editor HTML
            const editorHTML = this.createEditorHTML(productCount);
            contentElement.innerHTML = editorHTML;

            // Initialize form elements
            this.initializeFormElements();

        } catch (error) {
            console.error('StrainLineageEditor: Error loading content:', error);
            const contentElement = document.getElementById('lineageEditorContent');
            if (contentElement) {
                contentElement.innerHTML = `
                    <div class="alert alert-danger">
                        <strong>Error loading editor:</strong> ${error.message}
                        <button class="btn btn-sm btn-outline-danger ms-2" onclick="window.strainLineageEditor.retryLoad()">Retry</button>
                    </div>
                `;
            }
            throw error;
        }
    }

    async ensureProductDatabaseEnabled() {
        try {
            // Check if product database is enabled
            const statusResponse = await fetch('/api/product-db/status');
            if (statusResponse.ok) {
                const statusData = await statusResponse.json();
                if (!statusData.enabled) {
                    console.log('StrainLineageEditor: Enabling product database...');
                    const enableResponse = await fetch('/api/product-db/enable', {
                        method: 'POST'
                    });
                    if (enableResponse.ok) {
                        console.log('StrainLineageEditor: Product database enabled successfully');
                    } else {
                        console.warn('StrainLineageEditor: Failed to enable product database');
                    }
                }
            }
        } catch (error) {
            console.warn('StrainLineageEditor: Error checking/enabling product database:', error);
        }
    }

    async getStrainProductCount(strainName) {
        try {
            const response = await fetch('/api/get-strain-product-count', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ strain_name: strainName })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            return data.count || 0;
        } catch (error) {
            console.warn('StrainLineageEditor: Error getting product count:', error);
            return 0;
        }
    }

    createEditorHTML(productCount) {
        return `
            <div class="strain-lineage-editor">
                <h6>Editing lineage for strain: <strong>${this.escapeHtml(this.currentStrain)}</strong></h6>
                <p class="text-muted">This will affect <strong>${productCount}</strong> products in the database.</p>
                
                <div class="mb-3">
                    <label for="lineageSelect" class="form-label">Select Lineage:</label>
                    <select class="form-select" id="lineageSelect">
                        <option value="">-- Select Lineage --</option>
                        <option value="SATIVA" ${this.currentLineage === 'SATIVA' ? 'selected' : ''}>SATIVA</option>
                        <option value="INDICA" ${this.currentLineage === 'INDICA' ? 'selected' : ''}>INDICA</option>
                        <option value="HYBRID" ${this.currentLineage === 'HYBRID' ? 'selected' : ''}>HYBRID</option>
                        <option value="HYBRID/SATIVA" ${this.currentLineage === 'HYBRID/SATIVA' ? 'selected' : ''}>HYBRID/SATIVA</option>
                        <option value="HYBRID/INDICA" ${this.currentLineage === 'HYBRID/INDICA' ? 'selected' : ''}>HYBRID/INDICA</option>
                        <option value="CBD" ${this.currentLineage === 'CBD' ? 'selected' : ''}>CBD</option>
                        <option value="CBD_BLEND" ${this.currentLineage === 'CBD_BLEND' ? 'selected' : ''}>CBD_BLEND</option>
                        <option value="MIXED" ${this.currentLineage === 'MIXED' ? 'selected' : ''}>MIXED</option>
                        <option value="PARA" ${this.currentLineage === 'PARA' ? 'selected' : ''}>PARA</option>
                    </select>
                </div>
                
                <div class="mb-3">
                    <label for="customLineage" class="form-label">Or enter custom lineage:</label>
                    <input type="text" class="form-control" id="customLineage" placeholder="Enter custom lineage...">
                </div>
                
                <div class="alert alert-info">
                    <strong>Note:</strong> This change will update the lineage for all products with the strain "${this.escapeHtml(this.currentStrain)}" in the database.
                </div>
            </div>
        `;
    }

    initializeFormElements() {
        const lineageSelect = document.getElementById('lineageSelect');
        const customLineage = document.getElementById('customLineage');

        if (lineageSelect) {
            lineageSelect.addEventListener('change', () => {
                if (customLineage) {
                    customLineage.value = '';
                }
            });
        }

        if (customLineage) {
            customLineage.addEventListener('input', () => {
                if (lineageSelect) {
                    lineageSelect.value = '';
                }
            });
        }
    }

    showModal() {
        console.log('StrainLineageEditor: Showing modal...');
        console.log('StrainLineageEditor: Modal instance exists:', !!this.modal);
        console.log('StrainLineageEditor: Modal element exists:', !!this.modalElement);
        console.log('StrainLineageEditor: Current modal state:', this.modalState);
        
        // Force modal to be visible
        if (this.modalElement) {
            console.log('StrainLineageEditor: Forcing modal visibility');
            this.modalElement.style.display = 'block';
            this.modalElement.classList.add('show');
            this.modalElement.setAttribute('aria-hidden', 'false');
            console.log('StrainLineageEditor: Modal visibility forced');
        }
        
        if (this.modal) {
            // Bootstrap modal
            console.log('StrainLineageEditor: Using Bootstrap modal.show()');
            try {
                this.modal.show();
                console.log('StrainLineageEditor: Bootstrap modal.show() completed');
            } catch (error) {
                console.error('StrainLineageEditor: Error in Bootstrap modal.show():', error);
            }
        } else {
            // Fallback modal
            console.log('StrainLineageEditor: Using fallback modal');
            if (this.modalElement) {
                this.modalElement.style.display = 'block';
                this.onModalShown();
                console.log('StrainLineageEditor: Fallback modal shown');
            }
        }
        
        // Verify modal is actually visible after a short delay
        setTimeout(() => {
            const isVisible = this.modalElement && this.modalElement.classList.contains('show');
            console.log('StrainLineageEditor: Modal visibility verification:', isVisible);
            if (!isVisible) {
                console.log('StrainLineageEditor: Modal not visible, forcing again');
                this.forceModalVisibility();
            }
        }, 200);
    }
    
    forceModalVisibility() {
        console.log('StrainLineageEditor: Force modal visibility called');
        if (this.modalElement) {
            this.modalElement.style.display = 'block';
            this.modalElement.classList.add('show');
            this.modalElement.setAttribute('aria-hidden', 'false');
            console.log('StrainLineageEditor: Modal visibility forced successfully');
        } else {
            console.error('StrainLineageEditor: Modal element not found for force visibility');
        }
    }

    onModalShown() {
        console.log('StrainLineageEditor: Modal shown');
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        this.modalState = 'open';
    }

    async saveChanges() {
        console.log('StrainLineageEditor: Saving changes...');
        
        const lineageSelect = document.getElementById('lineageSelect');
        const customLineage = document.getElementById('customLineage');
        
        if (!lineageSelect || !customLineage) {
            this.handleError('Form elements not found');
            return;
        }

        const newLineage = lineageSelect.value || customLineage.value.trim();
        
        if (!newLineage) {
            this.handleError('Please select or enter a lineage');
            return;
        }

        try {
            // Show saving state
            const saveButton = document.getElementById('saveStrainLineageBtn');
            if (saveButton) {
                saveButton.disabled = true;
                saveButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Saving...';
            }

            // Save lineage
            await this.saveLineage(newLineage);
            
            // Show success message
            this.showSuccess('Lineage updated successfully!');
            
            // Close modal after delay
            setTimeout(() => {
                this.closeModal();
            }, 1500);
            
        } catch (error) {
            console.error('StrainLineageEditor: Error saving changes:', error);
            this.handleError('Failed to save changes. Please try again.');
        } finally {
            // Reset save button
            const saveButton = document.getElementById('saveStrainLineageBtn');
            if (saveButton) {
                saveButton.disabled = false;
                saveButton.innerHTML = 'Save Changes';
            }
        }
    }

    async saveLineage(newLineage) {
        const response = await fetch('/api/set-strain-lineage', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                strain_name: this.currentStrain,
                lineage: newLineage
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.error || 'Unknown error');
        }
    }

    closeModal() {
        console.log('StrainLineageEditor: Closing modal...');
        console.log('StrainLineageEditor: User requested close:', this.userRequestedClose);
        console.log('StrainLineageEditor: Current modal state:', this.modalState);
        console.log('StrainLineageEditor: Stack trace:', new Error().stack);
        
        this.userRequestedClose = true;
        this.modalState = 'closing';
        
        if (this.modal) {
            console.log('StrainLineageEditor: Using Bootstrap modal.hide()');
            this.modal.hide();
        } else {
            console.log('StrainLineageEditor: Using fallback modal hide');
            if (this.modalElement) {
                this.modalElement.style.display = 'none';
                this.cleanup();
            }
        }
    }

    cleanup() {
        console.log('StrainLineageEditor: Cleaning up...');
        
        // Reset state
        this.isLoading = false;
        this.currentStrain = null;
        this.currentLineage = null;
        this.userRequestedClose = false;
        this.modalState = 'closed';
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Dispose mutation observer
        if (this.mutationObserver) {
            this.mutationObserver.disconnect();
            console.log('StrainLineageEditor: Mutation observer disposed');
        }
    }

    retryLoad() {
        console.log('StrainLineageEditor: Retrying load...');
        this.retryCount = 0;
        this.loadEditorContent();
    }

    handleError(message) {
        console.error('StrainLineageEditor Error:', message);
        const contentElement = document.getElementById('lineageEditorContent');
        if (contentElement) {
            contentElement.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Error:</strong> ${message}
                    <button class="btn btn-sm btn-outline-danger ms-2" onclick="window.strainLineageEditor.retryLoad()">Retry</button>
                </div>
            `;
        }
    }

    showSuccess(message) {
        const contentElement = document.getElementById('lineageEditorContent');
        if (contentElement) {
            contentElement.innerHTML = `
                <div class="alert alert-success">
                    <strong>Success!</strong> ${message}
                </div>
            `;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global instance
window.strainLineageEditor = new StrainLineageEditor();

// Static initialization method
StrainLineageEditor.init = function() {
    if (!window.strainLineageEditor) {
        window.strainLineageEditor = new StrainLineageEditor();
    }
    window.strainLineageEditor.init();
    return window.strainLineageEditor;
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        StrainLineageEditor.init();
    });
} else {
    StrainLineageEditor.init();
}