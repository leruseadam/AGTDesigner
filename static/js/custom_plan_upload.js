// Custom Plan Upload Frontend
// Optimized for 6 web workers, 20GB disk, Postgres database
(function() {
    'use strict';
    
    // Override the upload function for custom plan
    if (typeof TagManager !== 'undefined' && TagManager.prototype.uploadFile) {
        const originalUploadFile = TagManager.prototype.uploadFile;
        
        TagManager.prototype.uploadFile = function(file) {
            console.log('🚀 Using CUSTOM PLAN upload mode');
            
            const formData = new FormData();
            formData.append('file', file);
            
            // Show custom plan UI
            this.showUploadProgress('Custom plan mode: Processing with 6 web workers...');
            
            return fetch('/upload-custom-plan', {
                method: 'POST',
                body: formData,
                timeout: 60000  // 60 second timeout for custom plan
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('🚀 Custom plan upload result:', data);
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Show success message with plan specs
                this.showUploadSuccess(`🚀 Custom plan upload complete in ${data.processing_time}s! Processed ${data.total_products} products with 6 web workers.`);
                
                // Refresh tags immediately
                if (this.refreshTagLists) {
                    this.refreshTagLists();
                } else {
                    this.loadTags();
                }
                
                return data;
            })
            .catch(error => {
                console.error('🚀 Custom plan upload failed:', error);
                // Try parallel upload as fallback
                console.log('🚀 Trying parallel upload...');
                return this.tryParallelUpload(file);
            });
        };
        
        // Add parallel upload fallback
        TagManager.prototype.tryParallelUpload = function(file) {
            const formData = new FormData();
            formData.append('file', file);
            
            this.showUploadProgress('Parallel mode: Using multiple workers...');
            
            return fetch('/upload-parallel', {
                method: 'POST',
                body: formData,
                timeout: 90000  // 90 second timeout for parallel processing
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('⚡ Parallel upload result:', data);
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                this.showUploadSuccess(`⚡ Parallel upload complete in ${data.processing_time}s! Processed ${data.chunks_processed} chunks.`);
                this.loadTags();
                
                return data;
            })
            .catch(error => {
                console.error('⚡ Parallel upload failed:', error);
                this.showUploadError(`Both custom plan and parallel upload failed: ${error.message}`);
                throw error;
            });
        };
        
        console.log('🚀 Custom plan upload mode activated');
        console.log('📊 Plan specs: 6 web workers, 20GB disk, Postgres enabled');
    }
})();
