
// Ultra-instant upload frontend - absolute minimum processing
(function() {
    'use strict';
    
    // Override the upload function for ultra-instant speed
    if (typeof TagManager !== 'undefined' && TagManager.prototype.uploadFile) {
        const originalUploadFile = TagManager.prototype.uploadFile;
        
        TagManager.prototype.uploadFile = function(file) {
            console.log('⚡ Using ULTRA-INSTANT upload mode');
            
            const formData = new FormData();
            formData.append('file', file);
            
            // Show ultra-instant UI
            this.showUploadProgress('Ultra-instant mode: Just saving file...');
            
            return fetch('/upload-ultra-instant', {
                method: 'POST',
                body: formData,
                timeout: 5000  // 5 second timeout
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('⚡ Ultra-instant upload result:', data);
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Show success message
                this.showUploadSuccess(`⚡ Ultra-instant upload complete in ${data.processing_time}s!`);
                
                // Refresh tags immediately
                if (window.TagManager && window.TagManager.refreshTagLists) {
                    window.TagManager.refreshTagLists();
                } else if (window.TagManager && window.TagManager.loadAvailableTags) {
                    window.TagManager.loadAvailableTags();
                } else if (this.loadTags) {
                    this.loadTags();
                }
                
                return data;
            })
            .catch(error => {
                console.error('⚡ Ultra-instant upload failed:', error);
                // Try zero mode as final fallback
                console.log('⚡ Trying zero mode...');
                return this.tryZeroUpload(file);
            });
        };
        
        // Add zero upload fallback
        TagManager.prototype.tryZeroUpload = function(file) {
            const formData = new FormData();
            formData.append('file', file);
            
            this.showUploadProgress('Zero mode: Absolute minimum...');
            
            return fetch('/upload-zero', {
                method: 'POST',
                body: formData,
                timeout: 3000  // 3 second timeout
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('🔥 Zero upload result:', data);
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                this.showUploadSuccess(`🔥 Zero upload complete in ${data.processing_time}s!`);
                if (window.TagManager && window.TagManager.refreshTagLists) {
                    window.TagManager.refreshTagLists();
                } else if (window.TagManager && window.TagManager.loadAvailableTags) {
                    window.TagManager.loadAvailableTags();
                } else if (this.loadTags) {
                    this.loadTags();
                }
                
                return data;
            })
            .catch(error => {
                console.error('🔥 Zero upload failed:', error);
                this.showUploadError(`All upload modes failed: ${error.message}`);
                throw error;
            });
        };
        
        console.log('⚡ Ultra-instant upload mode activated');
    }
})();
