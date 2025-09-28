
// Smart-fast upload frontend - processes all data efficiently
(function() {
    'use strict';
    
    // Override the upload function for smart-fast processing
    if (typeof TagManager !== 'undefined' && TagManager.prototype.uploadFile) {
        const originalUploadFile = TagManager.prototype.uploadFile;
        
        TagManager.prototype.uploadFile = function(file) {
            console.log('🧠 Using SMART-FAST upload mode');
            
            const formData = new FormData();
            formData.append('file', file);
            
            // Show smart-fast UI
            this.showUploadProgress('Smart-fast mode: Processing all products efficiently...');
            
            return fetch('/upload-smart-fast', {
                method: 'POST',
                body: formData,
                timeout: 30000  // 30 second timeout
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('🧠 Smart-fast upload result:', data);
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Show success message
                this.showUploadSuccess(`🧠 Smart-fast upload complete in ${data.processing_time}s! Processed ${data.total_products} products.`);
                
                // Load tags immediately
                this.loadTags();
                
                return data;
            })
            .catch(error => {
                console.error('🧠 Smart-fast upload failed:', error);
                // Try batch smart as fallback
                console.log('🧠 Trying batch smart mode...');
                return this.tryBatchSmartUpload(file);
            });
        };
        
        // Add batch smart upload fallback
        TagManager.prototype.tryBatchSmartUpload = function(file) {
            const formData = new FormData();
            formData.append('file', file);
            
            this.showUploadProgress('Batch smart mode: Processing in chunks...');
            
            return fetch('/upload-batch-smart', {
                method: 'POST',
                body: formData,
                timeout: 45000  // 45 second timeout
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('📦 Batch smart upload result:', data);
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                this.showUploadSuccess(`📦 Batch smart upload complete in ${data.processing_time}s! Processed ${data.total_products} products in ${data.batches_processed} batches.`);
                this.loadTags();
                
                return data;
            })
            .catch(error => {
                console.error('📦 Batch smart upload failed:', error);
                this.showUploadError(`Both smart upload modes failed: ${error.message}`);
                throw error;
            });
        };
        
        console.log('🧠 Smart-fast upload mode activated');
    }
})();
