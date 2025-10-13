// QUICK UPLOAD FIX - Use optimized endpoint
// Add this to browser console to fix upload immediately

console.log("🔧 QUICK UPLOAD FIX: Switching to optimized endpoint");

// Override the upload function to use the optimized endpoint
if (typeof TagManager !== 'undefined') {
    // Store original upload function
    TagManager.originalUploadFile = TagManager.uploadFile;
    
    // Replace with optimized upload
    TagManager.uploadFile = async function(file) {
        try {
            console.log(`🚀 Starting OPTIMIZED upload:`, file.name, 'Size:', file.size, 'bytes');
            
            // Show Excel loading splash screen
            this.showExcelLoadingSplash(file.name);
            
            // Show loading state
            this.updateUploadUI(`Uploading ${file.name} (optimized mode)...`);
            
            const formData = new FormData();
            formData.append('file', file);
            
            console.log('🚀 Sending optimized upload request...');
            
            // Use optimized endpoint
            const response = await fetch('/upload-optimized', {
                method: 'POST',
                body: formData
            });
            
            console.log('✅ Optimized upload response status:', response.status);
            
            const data = await response.json();
            console.log('✅ Optimized upload response:', data);
            
            if (!response.ok) {
                throw new Error(data.error || 'Upload failed');
            }
            
            if (data.success) {
                // Success!
                this.updateUploadUI(`✅ ${file.name} uploaded successfully!`);
                console.log(`✅ Upload successful: ${data.message}`);
                
                // Hide loading splash
                this.hideExcelLoadingSplash();
                
                // Refresh data
                await this.checkForExistingData();
                
                // Show success message
                if (data.processing) {
                    console.log('🔄 File processing in background...');
                    this.updateUploadUI(`🔄 Processing ${file.name} in background...`);
                    
                    // Poll for completion
                    this.pollForProcessingCompletion(file.name);
                } else {
                    console.log(`✅ File processed immediately: ${data.rows_processed} rows`);
                    this.updateUploadUI(`✅ ${file.name} processed successfully!`);
                }
                
                return data;
            } else {
                throw new Error(data.error || 'Upload failed');
            }
            
        } catch (error) {
            console.error('❌ Optimized upload error:', error);
            
            // Hide loading splash
            this.hideExcelLoadingSplash();
            
            // Show error message
            this.updateUploadUI(`❌ Upload failed: ${error.message}`);
            
            throw error;
        }
    };
    
    console.log("✅ Upload function replaced with optimized version");
}

// Also override enhanced-ui.js upload function
if (typeof handleFiles !== 'undefined') {
    const originalHandleFiles = handleFiles;
    
    handleFiles = async function(files) {
        console.log('🔧 Using optimized upload in handleFiles');
        
        const file = files[0];
        if (!file) return;
        
        console.log('Starting optimized upload:', file.name);
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/upload-optimized', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            console.log('Optimized upload response:', data);
            
            if (response.ok && data.success) {
                console.log('✅ Upload successful:', data.message);
                
                if (data.processing) {
                    console.log('🔄 Processing in background...');
                    // Start polling for completion
                    pollForProcessingCompletion(data.filename);
                } else {
                    console.log(`✅ Processed immediately: ${data.rows_processed} rows`);
                    // Refresh the page to show new data
                    location.reload();
                }
            } else {
                throw new Error(data.error || 'Upload failed');
            }
            
        } catch (error) {
            console.error('❌ Upload error:', error);
            alert(`Upload failed: ${error.message}`);
        }
    };
    
    console.log("✅ handleFiles function replaced with optimized version");
}

// Helper function to poll for processing completion
function pollForProcessingCompletion(filename) {
    console.log(`🔄 Polling for processing completion: ${filename}`);
    
    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/upload-status?filename=${encodeURIComponent(filename)}`);
            const data = await response.json();
            
            console.log('Processing status:', data);
            
            if (data.status === 'ready') {
                clearInterval(pollInterval);
                console.log('✅ Processing complete!');
                
                // Refresh the page to show new data
                location.reload();
            } else if (data.status === 'error') {
                clearInterval(pollInterval);
                console.error('❌ Processing failed:', data.error);
                alert(`Processing failed: ${data.error}`);
            }
            
        } catch (error) {
            console.error('❌ Polling error:', error);
        }
    }, 2000); // Poll every 2 seconds
    
    // Stop polling after 5 minutes
    setTimeout(() => {
        clearInterval(pollInterval);
        console.log('⏰ Polling timeout - processing may still be in progress');
    }, 300000);
}

console.log("🎉 QUICK UPLOAD FIX APPLIED!");
console.log("Upload will now use the /upload-optimized endpoint");
