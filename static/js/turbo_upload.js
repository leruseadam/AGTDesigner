
// Turbo upload frontend - matches local server speed
(function() {
    'use strict';
    
    // Override the upload function for turbo speed
    if (typeof TagManager !== 'undefined' && TagManager.prototype.uploadFile) {
        const originalUploadFile = TagManager.prototype.uploadFile;
        
        TagManager.prototype.uploadFile = function(file) {
            console.log('🏎️ Using TURBO upload mode');
            
            const formData = new FormData();
            formData.append('file', file);
            
            // Show turbo UI
            this.showUploadProgress('Turbo mode: Processing 20 rows...');
            
            return fetch('/upload-turbo', {
                method: 'POST',
                body: formData,
                timeout: 15000  // 15 second timeout
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('🏎️ Turbo upload result:', data);
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Show success message
                this.showUploadSuccess(`🏎️ Turbo upload complete in ${data.processing_time}s! Processed ${data.rows_processed} rows.`);
                
                // Load tags immediately
                this.loadTags();
                
                return data;
            })
            .catch(error => {
                console.error('🏎️ Turbo upload failed:', error);
                // Try instant mode as fallback
                console.log('🏎️ Trying instant mode...');
                return this.tryInstantUpload(file);
            });
        };
        
        // Add instant upload fallback
        TagManager.prototype.tryInstantUpload = function(file) {
            const formData = new FormData();
            formData.append('file', file);
            
            this.showUploadProgress('Instant mode: Just saving file...');
            
            return fetch('/upload-instant', {
                method: 'POST',
                body: formData,
                timeout: 10000  // 10 second timeout
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('⚡ Instant upload result:', data);
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                this.showUploadSuccess(`⚡ Instant upload complete in ${data.processing_time}s!`);
                this.loadTags();
                
                return data;
            })
            .catch(error => {
                console.error('⚡ Instant upload failed:', error);
                this.showUploadError(`Both turbo and instant upload failed: ${error.message}`);
                throw error;
            });
        };
        
        console.log('🏎️ Turbo upload mode activated');
    }
})();
