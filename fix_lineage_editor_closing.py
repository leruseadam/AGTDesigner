#!/usr/bin/env python3
"""
Fix for lineage editor modal closing immediately
"""

import os
import shutil

def backup_current_files():
    """Backup current lineage editor files."""
    backup_dir = "backup_lineage_editor"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        'static/js/lineage-editor.js',
        'static/js/main.js',
        'templates/index.html'
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, f"{backup_dir}/{os.path.basename(file)}.backup")
            print(f"✅ Backed up {file}")

def create_fixed_lineage_editor():
    """Create a fixed version of the lineage editor that prevents immediate closing."""
    
    fixed_js = '''/**
 * Fixed Strain Lineage Editor
 * Prevents modal from closing immediately
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
        this.userRequestedClose = false;
        this.modalState = 'closed';
        this.preventClose = false;
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
            this.modalElement.addEventListener('hide.bs.modal', (e) => {
                console.log('StrainLineageEditor: Modal hide event');
                // Prevent automatic hiding if we\'re in the middle of an operation
                if (this.isLoading || this.modalState === 'opening' || this.preventClose) {
                    e.preventDefault();
                    console.log('StrainLineageEditor: Prevented modal hide during loading/opening');
                    return false;
                }
            });

            this.modalElement.addEventListener('hidden.bs.modal', (e) => {
                console.log('StrainLineageEditor: Modal hidden event');
                this.cleanup();
            });

            this.modalElement.addEventListener('shown.bs.modal', (e) => {
                console.log('StrainLineageEditor: Modal shown event');
                this.onModalShown();
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

        this.eventListenersAdded = true;
    }

    async openEditor(strainName, currentLineage) {
        console.log('StrainLineageEditor: Opening editor for', strainName, currentLineage);
        
        try {
            this.currentStrain = strainName;
            this.currentLineage = currentLineage;
            this.isLoading = true;
            this.preventClose = true;
            this.modalState = 'opening';

            // Wait for initialization
            await this.waitForInitialization();
            
            // Load editor content
            await this.loadEditorContent();
            
            // Show modal
            this.showModal();
            
        } catch (error) {
            console.error('StrainLineageEditor: Error opening editor:', error);
            this.handleError('Failed to open lineage editor: ' + error.message);
        }
    }

    async waitForInitialization() {
        let attempts = 0;
        while (!this.isInitialized && attempts < 10) {
            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }
        
        if (!this.isInitialized) {
            throw new Error('Editor failed to initialize');
        }
    }

    async loadEditorContent() {
        console.log('StrainLineageEditor: Loading editor content...');
        
        try {
            // Ensure product database is enabled
            await this.ensureProductDatabaseEnabled();
            
            // Get strain product count
            const productCount = await this.getStrainProductCount(this.currentStrain);
            
            // Create editor HTML
            const editorHTML = this.createEditorHTML(productCount);
            
            // Update modal content
            const contentDiv = document.getElementById('lineageEditorContent');
            if (contentDiv) {
                contentDiv.innerHTML = editorHTML;
                this.initializeFormElements();
            }
            
        } catch (error) {
            console.error('StrainLineageEditor: Error loading content:', error);
            throw error;
        }
    }

    async ensureProductDatabaseEnabled() {
        try {
            const response = await fetch('/api/product-db/status');
            const data = await response.json();
            
            if (!data.enabled) {
                console.log('StrainLineageEditor: Enabling product database...');
                await fetch('/api/product-db/enable', { method: 'POST' });
            }
        } catch (error) {
            console.warn('StrainLineageEditor: Could not check/enable product database:', error);
        }
    }

    async getStrainProductCount(strainName) {
        try {
            const response = await fetch('/api/get-strain-product-count', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ strain_name: strainName })
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.count || 0;
            }
        } catch (error) {
            console.warn('StrainLineageEditor: Could not get strain product count:', error);
        }
        
        return 0;
    }

    createEditorHTML(productCount) {
        return `
            <div class="mb-3">
                <label class="form-label"><strong>Strain:</strong> ${this.escapeHtml(this.currentStrain)}</label>
            </div>
            <div class="mb-3">
                <label class="form-label"><strong>Current Lineage:</strong> ${this.escapeHtml(this.currentLineage || 'None')}</label>
            </div>
            <div class="mb-3">
                <label class="form-label"><strong>Products with this strain:</strong> ${productCount}</label>
            </div>
            <div class="mb-3">
                <label for="lineageSelect" class="form-label">Select New Lineage:</label>
                <select class="form-select" id="lineageSelect">
                    <option value="">-- Select Lineage --</option>
                    <option value="SATIVA">SATIVA</option>
                    <option value="INDICA">INDICA</option>
                    <option value="HYBRID">HYBRID</option>
                    <option value="HYBRID/SATIVA">HYBRID/SATIVA</option>
                    <option value="HYBRID/INDICA">HYBRID/INDICA</option>
                    <option value="CBD">CBD</option>
                    <option value="CBD_BLEND">CBD_BLEND</option>
                    <option value="MIXED">MIXED</option>
                    <option value="PARA">PARA</option>
                </select>
            </div>
            <div class="mb-3">
                <label for="customLineage" class="form-label">Or Enter Custom Lineage:</label>
                <input type="text" class="form-control" id="customLineage" placeholder="Enter custom lineage...">
            </div>
        `;
    }

    initializeFormElements() {
        // Set current lineage in select
        const lineageSelect = document.getElementById('lineageSelect');
        if (lineageSelect && this.currentLineage) {
            lineageSelect.value = this.currentLineage;
        }
    }

    showModal() {
        console.log('StrainLineageEditor: Showing modal...');
        
        if (this.modal) {
            try {
                this.modal.show();
                console.log('StrainLineageEditor: Bootstrap modal.show() completed');
            } catch (error) {
                console.error('StrainLineageEditor: Error in Bootstrap modal.show():', error);
            }
        } else {
            console.log('StrainLineageEditor: Using fallback modal');
            if (this.modalElement) {
                this.modalElement.style.display = 'block';
                this.modalElement.classList.add('show');
                this.onModalShown();
            }
        }
    }

    onModalShown() {
        console.log('StrainLineageEditor: Modal shown');
        this.isLoading = false;
        this.preventClose = false;
        this.modalState = 'open';
        document.body.style.overflow = 'hidden';
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
            this.handleError('Failed to save changes: ' + error.message);
            
            // Re-enable save button
            const saveButton = document.getElementById('saveStrainLineageBtn');
            if (saveButton) {
                saveButton.disabled = false;
                saveButton.textContent = 'Save Changes';
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
            throw new Error('Failed to save lineage');
        }
        
        return await response.json();
    }

    closeModal() {
        console.log('StrainLineageEditor: Closing modal...');
        this.userRequestedClose = true;
        this.preventClose = false;
        
        if (this.modal) {
            this.modal.hide();
        } else if (this.modalElement) {
            this.modalElement.style.display = 'none';
            this.modalElement.classList.remove('show');
            this.cleanup();
        }
    }

    cleanup() {
        console.log('StrainLineageEditor: Cleaning up...');
        this.isLoading = false;
        this.preventClose = false;
        this.modalState = 'closed';
        this.userRequestedClose = false;
        document.body.style.overflow = '';
    }

    handleError(message) {
        console.error('StrainLineageEditor Error:', message);
        alert('Error: ' + message);
    }

    showSuccess(message) {
        console.log('StrainLineageEditor Success:', message);
        // You could show a toast notification here instead of alert
        alert(message);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the editor when the script loads
if (typeof window !== 'undefined') {
    window.strainLineageEditor = new StrainLineageEditor();
    window.strainLineageEditor.init();
}
'''
    
    with open('static/js/lineage-editor.js', 'w') as f:
        f.write(fixed_js)
    
    print("✅ Created fixed lineage-editor.js")

def create_fixed_main_js():
    """Create a fixed version of main.js that properly handles lineage editor calls."""
    
    # Read the current main.js file
    with open('static/js/main.js', 'r') as f:
        content = f.read()
    
    # Replace the lineage editor call with a more robust version
    old_call = '''window.strainLineageEditor.openEditor(strainName, currentLineage);'''
    new_call = '''// Enhanced lineage editor call with error handling
                try {
                    if (window.strainLineageEditor && typeof window.strainLineageEditor.openEditor === 'function') {
                        window.strainLineageEditor.openEditor(strainName, currentLineage);
                    } else {
                        console.error('StrainLineageEditor not properly initialized');
                        alert('Lineage editor not available. Please refresh the page and try again.');
                    }
                } catch (error) {
                    console.error('Error opening lineage editor:', error);
                    alert('Error opening lineage editor. Please try again.');
                }'''
    
    if old_call in content:
        content = content.replace(old_call, new_call)
        print("✅ Updated lineage editor call in main.js")
    else:
        print("⚠️  Could not find lineage editor call in main.js")
    
    # Write back the updated content
    with open('static/js/main.js', 'w') as f:
        f.write(content)

def main():
    """Main fix function."""
    print("🔧 Lineage Editor Closing Fix")
    print("=" * 40)
    
    try:
        # Backup current files
        backup_current_files()
        
        # Apply fixes
        create_fixed_lineage_editor()
        create_fixed_main_js()
        
        print("\n" + "=" * 40)
        print("✅ Lineage editor fix complete!")
        print("\n📋 Key fixes applied:")
        print("1. Added preventClose flag to prevent automatic closing")
        print("2. Enhanced event listeners to prevent backdrop clicks")
        print("3. Improved error handling and initialization")
        print("4. Added proper cleanup and state management")
        print("5. Enhanced main.js call with error handling")
        
        print("\n📋 Next steps:")
        print("1. Reload your web app in PythonAnywhere")
        print("2. Test the lineage editor")
        print("3. Check browser console for any remaining errors")
        
        print("\n🔧 If you need to revert:")
        print("cp backup_lineage_editor/lineage-editor.js.backup static/js/lineage-editor.js")
        print("cp backup_lineage_editor/main.js.backup static/js/main.js")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 