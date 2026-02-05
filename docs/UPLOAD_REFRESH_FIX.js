// UPLOAD REFRESH FIX - Force data refresh after upload
// Add this to browser console to fix upload not refreshing

console.log("🔧 UPLOAD REFRESH FIX: Adding automatic refresh after upload");

// Override the upload completion logic to force refresh
if (typeof TagManager !== 'undefined') {
    // Store original polling function
    TagManager.originalPollUploadStatusAndUpdateUI = TagManager.pollUploadStatusAndUpdateUI;
    
    // Replace with enhanced version
    TagManager.pollUploadStatusAndUpdateUI = async function(filename, displayName) {
        console.log(`🔧 Enhanced polling for: ${filename}`);
        
        const maxAttempts = 120;
        let attempts = 0;
        let consecutiveErrors = 0;
        const maxConsecutiveErrors = 5;
        
        while (attempts < maxAttempts) {
            try {
                const response = await fetch(`/api/upload-status?filename=${encodeURIComponent(filename)}`);
                const data = await response.json();
                const status = data.status;
                
                console.log(`📊 Upload status (attempt ${attempts + 1}): ${status}`);
                
                consecutiveErrors = 0; // Reset error counter on successful response
                
                if (status === 'ready' || status === 'done') {
                    console.log(`✅ File ready: ${filename}`);
                    this.hideExcelLoadingSplash();
                    this.updateUploadUI(displayName, 'File ready!', 'success');
                    
                    // Wait for backend to fully process
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    
                    // FORCE COMPLETE REFRESH
                    console.log(`🔄 FORCING COMPLETE DATA REFRESH...`);
                    
                    try {
                        // Clear any cached data
                        await fetch('/api/clear-cache', { method: 'POST' });
                        console.log('✅ Backend cache cleared');
                    } catch (cacheError) {
                        console.warn('⚠️ Cache clear failed:', cacheError);
                    }
                    
                    // Force refresh all data
                    console.log(`🔄 Refreshing all application data...`);
                    
                    // Method 1: Complete data refresh
                    if (this.checkForExistingData) {
                        await this.checkForExistingData();
                        console.log('✅ Complete data refresh completed');
                    }
                    
                    // Method 2: Individual refreshes as backup
                    setTimeout(async () => {
                        console.log(`🔄 Backup refresh in 3 seconds...`);
                        await new Promise(resolve => setTimeout(resolve, 3000));
                        
                        if (this.fetchAndUpdateAvailableTags) {
                            await this.fetchAndUpdateAvailableTags();
                            console.log('✅ Available tags refreshed');
                        }
                        
                        if (this.fetchAndUpdateSelectedTags) {
                            await this.fetchAndUpdateSelectedTags();
                            console.log('✅ Selected tags refreshed');
                        }
                        
                        // Force UI update
                        if (this.applyFilters) {
                            this.applyFilters();
                            console.log('✅ Filters reapplied');
                        }
                    }, 1000);
                    
                    return; // Exit polling loop
                }
                
                // Continue polling
                attempts++;
                await new Promise(resolve => setTimeout(resolve, 1000));
                
            } catch (error) {
                consecutiveErrors++;
                console.error(`❌ Polling error (${consecutiveErrors}/${maxConsecutiveErrors}):`, error);
                
                if (consecutiveErrors >= maxConsecutiveErrors) {
                    console.error('❌ Too many consecutive errors, stopping polling');
                    this.hideExcelLoadingSplash();
                    this.updateUploadUI(displayName, 'Upload failed', 'error');
                    return;
                }
                
                attempts++;
                await new Promise(resolve => setTimeout(resolve, 2000));
            }
        }
        
        // Timeout
        console.warn('⏰ Polling timeout reached');
        this.hideExcelLoadingSplash();
        this.updateUploadUI(displayName, 'Upload timeout', 'warning');
    };
    
    console.log("✅ Enhanced upload polling installed");
}

// Also override the main upload function
if (typeof handleFiles !== 'undefined') {
    const originalHandleFiles = handleFiles;
    
    handleFiles = async function(files) {
        console.log('🔧 Enhanced handleFiles with auto-refresh');
        
        const file = files[0];
        if (!file) return;
        
        console.log('Starting enhanced upload:', file.name);
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/upload-optimized', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            console.log('Enhanced upload response:', data);
            
            if (response.ok && data.success) {
                console.log('✅ Upload successful:', data.message);
                
                if (data.processing) {
                    console.log('🔄 Processing in background...');
                    // Use enhanced polling
                    if (typeof TagManager !== 'undefined' && TagManager.pollUploadStatusAndUpdateUI) {
                        TagManager.pollUploadStatusAndUpdateUI(data.filename, file.name);
                    }
                } else {
                    console.log(`✅ Processed immediately: ${data.rows_processed} rows`);
                    
                    // Force immediate refresh
                    setTimeout(async () => {
                        console.log('🔄 Forcing immediate refresh...');
                        
                        if (typeof TagManager !== 'undefined') {
                            if (TagManager.checkForExistingData) {
                                await TagManager.checkForExistingData();
                                console.log('✅ Immediate refresh completed');
                            }
                        }
                    }, 1000);
                }
            } else {
                throw new Error(data.error || 'Upload failed');
            }
            
        } catch (error) {
            console.error('❌ Enhanced upload error:', error);
            alert(`Upload failed: ${error.message}`);
        }
    };
    
    console.log("✅ Enhanced handleFiles installed");
}

console.log("🎉 UPLOAD REFRESH FIX APPLIED!");
console.log("Upload will now automatically refresh data without requiring page refresh");
