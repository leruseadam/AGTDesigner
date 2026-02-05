// FORCE REFRESH AFTER UPLOAD - Aggressive fix for upload not refreshing
// Add this to browser console to force page refresh after upload

console.log("🔧 FORCE REFRESH FIX: Will refresh page after upload completion");

// Override all upload functions to force page refresh
if (typeof TagManager !== 'undefined') {
    // Store original upload function
    TagManager.originalUploadFile = TagManager.uploadFile;
    
    // Replace with force refresh version
    TagManager.uploadFile = async function(file) {
        try {
            console.log(`🚀 Starting UPLOAD WITH FORCE REFRESH:`, file.name);
            
            // Show Excel loading splash screen
            this.showExcelLoadingSplash(file.name);
            
            // Show loading state
            this.updateUploadUI(`Uploading ${file.name}...`);
            
            const formData = new FormData();
            formData.append('file', file);
            
            console.log('🚀 Sending upload request...');
            
            // Use optimized endpoint
            const response = await fetch('/upload-optimized', {
                method: 'POST',
                body: formData
            });
            
            console.log('✅ Upload response status:', response.status);
            
            const data = await response.json();
            console.log('✅ Upload response:', data);
            
            if (!response.ok) {
                throw new Error(data.error || 'Upload failed');
            }
            
            if (data.success) {
                console.log('✅ Upload successful:', data.message);
                
                // Hide loading splash
                this.hideExcelLoadingSplash();
                
                if (data.processing) {
                    console.log('🔄 Processing in background, will refresh when ready...');
                    
                    // Start polling with force refresh on completion
                    this.pollWithForceRefresh(file.name, data.filename);
                } else {
                    console.log(`✅ Processed immediately: ${data.rows_processed} rows`);
                    
                    // FORCE REFRESH IMMEDIATELY
                    setTimeout(() => {
                        console.log('🔄 FORCING PAGE REFRESH after immediate processing...');
                        window.location.reload();
                    }, 2000);
                }
                
                return data;
            } else {
                throw new Error(data.error || 'Upload failed');
            }
            
        } catch (error) {
            console.error('❌ Upload error:', error);
            
            // Hide loading splash
            this.hideExcelLoadingSplash();
            
            // Show error message
            this.updateUploadUI(`❌ Upload failed: ${error.message}`);
            
            throw error;
        }
    };
    
    // Add polling function with force refresh
    TagManager.pollWithForceRefresh = async function(displayName, filename) {
        console.log(`🔄 Polling for completion: ${filename}`);
        
        let attempts = 0;
        const maxAttempts = 120; // 2 minutes
        
        while (attempts < maxAttempts) {
            try {
                const response = await fetch(`/api/upload-status?filename=${encodeURIComponent(filename)}`);
                const data = await response.json();
                
                console.log(`📊 Upload status (attempt ${attempts + 1}): ${data.status}`);
                
                if (data.status === 'ready' || data.status === 'done') {
                    console.log(`✅ File ready: ${filename}`);
                    
                    // Hide loading splash
                    this.hideExcelLoadingSplash();
                    
                    // FORCE PAGE REFRESH
                    setTimeout(() => {
                        console.log('🔄 FORCING PAGE REFRESH after background processing...');
                        window.location.reload();
                    }, 2000);
                    
                    return;
                }
                
                // Continue polling
                attempts++;
                await new Promise(resolve => setTimeout(resolve, 1000));
                
            } catch (error) {
                console.error(`❌ Polling error:`, error);
                attempts++;
                await new Promise(resolve => setTimeout(resolve, 2000));
            }
        }
        
        // Timeout - still refresh
        console.warn('⏰ Polling timeout, refreshing anyway...');
        this.hideExcelLoadingSplash();
        
        setTimeout(() => {
            console.log('🔄 FORCING PAGE REFRESH after timeout...');
            window.location.reload();
        }, 2000);
    };
    
    console.log("✅ Upload function replaced with force refresh version");
}

// Also override enhanced-ui.js handleFiles
if (typeof handleFiles !== 'undefined') {
    const originalHandleFiles = handleFiles;
    
    handleFiles = async function(files) {
        console.log('🔧 Enhanced handleFiles with FORCE REFRESH');
        
        const file = files[0];
        if (!file) return;
        
        console.log('Starting upload with force refresh:', file.name);
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/upload-optimized', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            console.log('Upload response:', data);
            
            if (response.ok && data.success) {
                console.log('✅ Upload successful:', data.message);
                
                if (data.processing) {
                    console.log('🔄 Processing in background, will refresh when ready...');
                    
                    // Start polling with force refresh
                    let attempts = 0;
                    const pollInterval = setInterval(async () => {
                        try {
                            const statusResponse = await fetch(`/api/upload-status?filename=${encodeURIComponent(data.filename)}`);
                            const statusData = await statusResponse.json();
                            
                            console.log('Processing status:', statusData.status);
                            
                            if (statusData.status === 'ready') {
                                clearInterval(pollInterval);
                                console.log('✅ Processing complete, forcing page refresh...');
                                
                                setTimeout(() => {
                                    console.log('🔄 FORCING PAGE REFRESH...');
                                    window.location.reload();
                                }, 2000);
                            }
                            
                        } catch (error) {
                            console.error('Polling error:', error);
                        }
                        
                        attempts++;
                        if (attempts > 120) { // 2 minutes timeout
                            clearInterval(pollInterval);
                            console.log('⏰ Timeout, forcing refresh anyway...');
                            setTimeout(() => {
                                console.log('🔄 FORCING PAGE REFRESH after timeout...');
                                window.location.reload();
                            }, 2000);
                        }
                    }, 1000);
                    
                } else {
                    console.log(`✅ Processed immediately: ${data.rows_processed} rows`);
                    
                    // FORCE REFRESH IMMEDIATELY
                    setTimeout(() => {
                        console.log('🔄 FORCING PAGE REFRESH after immediate processing...');
                        window.location.reload();
                    }, 2000);
                }
            } else {
                throw new Error(data.error || 'Upload failed');
            }
            
        } catch (error) {
            console.error('❌ Upload error:', error);
            alert(`Upload failed: ${error.message}`);
        }
    };
    
    console.log("✅ Enhanced handleFiles with force refresh installed");
}

console.log("🎉 FORCE REFRESH FIX APPLIED!");
console.log("Upload will now force page refresh after completion - no more manual refresh needed!");
