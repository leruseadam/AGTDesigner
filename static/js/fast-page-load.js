/**
 * Ultra-fast page load optimization v2.1.0
 * Makes initial data loading non-blocking and shows UI immediately
 * UPDATED: 2025-11-19 - Added cache checking and splash screen fixes
 */

(function() {
    'use strict';
    
    console.log('⚡ Fast page load optimization v2.1.0 enabled');
    
    // NOTE: Preserve cached tag lists even when no Excel file is present.
    // Previous behavior cleared sessionStorage when no file was uploaded which
    // caused the tag lists to disappear for users relying on cached data.
    // Keep localStorage/sessionStorage intact so cached tags remain available.
    const fileInfoText = document.getElementById('fileInfoText');
    const hasUploadedFile = fileInfoText && !fileInfoText.textContent.includes('No file uploaded');
    if (!hasUploadedFile) {
        console.log('ℹ️ No uploaded file detected - preserving cached tag lists for instant access');
        // Intentionally do not clear sessionStorage/localStorage here.
        // If a manual cache clear is required, use the explicit UI control instead.
    }
    
    // Store original checkForExistingData function
    let originalCheckForExistingData = null;
    
    // Wait for TagManager to be available
    function waitForTagManager() {
        return new Promise((resolve) => {
            const checkInterval = setInterval(() => {
                if (window.TagManager && TagManager.checkForExistingData) {
                    clearInterval(checkInterval);
                    resolve();
                }
            }, 10);
            
            // Timeout after 5 seconds
            setTimeout(() => {
                clearInterval(checkInterval);
                resolve();
            }, 5000);
        });
    }
    
    // Optimize the page load
    async function optimizePageLoad() {
        await waitForTagManager();
        
        if (!window.TagManager || !TagManager.checkForExistingData) {
            console.warn('⚠️ TagManager not available, skipping optimization');
            // Fallback: Try to load tags directly if TagManager.init exists
            if (window.TagManager && typeof window.TagManager.init === 'function') {
                console.log('⚠️ Attempting fallback tag load via TagManager.init()');
                try {
                    window.TagManager.init();
                } catch (fallbackError) {
                    console.error('⚠️ Fallback tag load failed:', fallbackError);
                }
            }
            return;
        }
        
        // Store original function
        originalCheckForExistingData = TagManager.checkForExistingData;
        
        // Replace with optimized version
        TagManager.checkForExistingData = async function() {
            console.log('⚡ Optimized checkForExistingData called');

            // CRITICAL FIX: If tags are already hydrated from cache (e.g., by inline script),
            // skip loading entirely and return immediately
            const alreadyHydrated = this.state && this.state.hydratedFromCache && this.state.tags && this.state.tags.length > 0;
            const tagsAlreadyRendered = document.getElementById('availableTags')?.querySelectorAll('.tag-item').length > 0;

            if (alreadyHydrated || tagsAlreadyRendered) {
                console.log(`✅ Tags already ${alreadyHydrated ? 'hydrated from cache' : 'rendered in DOM'} (${alreadyHydrated ? this.state.tags.length : 'rendered'} tags), skipping load`);
                // Still load selected tags and filters in background
                Promise.allSettled([
                    this.fetchAndUpdateSelectedTags ? this.fetchAndUpdateSelectedTags() : Promise.resolve(),
                    this.fetchAndPopulateFilters ? this.fetchAndPopulateFilters() : Promise.resolve()
                ]).catch(err => console.warn('Background load error:', err));
                return;
            }

            // CRITICAL FIX: Check for uploaded file FIRST before trying to load tags
            let hasFile = false;
            try {
                const fileResponse = await fetch('/api/current-file');
                if (fileResponse.ok) {
                    const fileData = await fileResponse.json();
                    if (fileData && fileData.success && fileData.has_file && fileData.filename) {
                        hasFile = true;
                        console.log(`📄 Found uploaded file: ${fileData.filename}`);
                        // Update file info
                        const fileInfoText = document.getElementById('fileInfoText');
                        if (fileInfoText) {
                            fileInfoText.textContent = fileData.filename;
                        }
                        const currentFileInfo = document.getElementById('currentFileInfo');
                        if (currentFileInfo) {
                            currentFileInfo.textContent = fileData.filename;
                        }
                    }
                }
            } catch (error) {
                console.log('Error checking for current file:', error);
            }
            
            // If no file exists, prefer cached tags (if available) before showing upload prompt
            const availableTagsContainer = document.getElementById('availableTags');
            if (!hasFile && availableTagsContainer) {
                console.log('📤 No file uploaded - checking cache before showing upload prompt');
                const cachedTags = this.loadAvailableTagsFromCache ? this.loadAvailableTagsFromCache() : null;
                if (cachedTags && Array.isArray(cachedTags) && cachedTags.length > 0) {
                    console.log(`⚡ INSTANT CACHE HIT (no file): ${cachedTags.length} tags available`);
                    const savedSelectedTags = [...(this.state.persistentSelectedTags || [])];
                    this.state.tags = [...cachedTags];
                    this.state.originalTags = [...cachedTags];
                    this.state.hydratedFromCache = true;

                    requestAnimationFrame(() => {
                        console.log('🎨 Rendering cached tags (no file)...');
                        if (this._updateAvailableTags) {
                            this._updateAvailableTags(cachedTags, null);
                        }

                        if (savedSelectedTags.length > 0) {
                            this.state.persistentSelectedTags = [...savedSelectedTags];
                            this.state.selectedTags = new Set(savedSelectedTags);
                            requestAnimationFrame(() => {
                                savedSelectedTags.forEach(tagName => {
                                    const checkboxes = document.querySelectorAll(`input[type="checkbox"][value="${CSS.escape(tagName)}"]`);
                                    checkboxes.forEach(cb => { if (!cb.checked) cb.checked = true; });
                                });
                                if (this.getSelectedTagObjects && this.updateSelectedTags) {
                                    const selectedTagObjects = this.getSelectedTagObjects();
                                    if (selectedTagObjects.length > 0) {
                                        this.updateSelectedTags(selectedTagObjects);
                                    }
                                }
                            });
                        }

                        if (this.hideActionSplash) {
                            this.hideActionSplash();
                        }
                        if (typeof AppLoadingSplash !== 'undefined' && AppLoadingSplash.isVisible) {
                            AppLoadingSplash.stopAutoAdvance();
                            AppLoadingSplash.complete();
                        }
                    });

                    // Background: fetch selected tags and filters
                    Promise.allSettled([
                        this.fetchAndUpdateSelectedTags ? this.fetchAndUpdateSelectedTags() : Promise.resolve(),
                        this.fetchAndPopulateFilters ? this.fetchAndPopulateFilters() : Promise.resolve()
                    ]).then(() => {
                        console.log('✅ Background: Selected tags and filters loaded (no file cached)');
                        if (savedSelectedTags.length > 0 && this.state.persistentSelectedTags.length === 0) {
                            this.state.persistentSelectedTags = [...savedSelectedTags];
                            this.state.selectedTags = new Set(savedSelectedTags);
                            if (this.getSelectedTagObjects && this.updateSelectedTags) {
                                const selectedTagObjects = this.getSelectedTagObjects();
                                if (selectedTagObjects.length > 0) {
                                    this.updateSelectedTags(selectedTagObjects);
                                }
                            }
                        }
                    }).catch(err => { console.warn('⚠️ Background load error (non-critical):', err); });

                    return; // Exit early - rendered cached tags
                }

                // No cache available - show upload prompt
                console.log('📤 No cache found - showing upload prompt');
                if (this.hideActionSplash) {
                    this.hideActionSplash();
                }
                availableTagsContainer.innerHTML = `
                    <div class="text-center py-5">
                        <div class="upload-prompt">
                            <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
                            <h5 class="text-muted">No product data loaded</h5>
                            <p class="text-muted">Upload an Excel file to get started</p>
                            <button class="btn btn-primary" onclick="document.getElementById('fileInput').click()">
                                <i class="fas fa-upload me-2"></i>Upload Excel File
                            </button>
                        </div>
                    </div>
                `;
                if (typeof AppLoadingSplash !== 'undefined' && AppLoadingSplash.isVisible) {
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                }
                return; // Exit early - no file, no tags to load
            }
            
            // File exists - proceed with loading tags
            // CRITICAL: Try cache FIRST for instant load
            console.log('🔍 Checking for cached tags...');
            const cachedTags = this.loadAvailableTagsFromCache ? this.loadAvailableTagsFromCache() : null;
            
            if (cachedTags && cachedTags.length > 0) {
                console.log(`⚡ INSTANT CACHE HIT: ${cachedTags.length} tags available`);
                // CRITICAL FIX: Preserve selected tags before rendering
                const savedSelectedTags = [...(this.state.persistentSelectedTags || [])];
                
                // Render cached tags IMMEDIATELY
                this.state.tags = [...cachedTags];
                this.state.originalTags = [...cachedTags];
                this.state.hydratedFromCache = true;
                
                // Use requestAnimationFrame for instant render
                requestAnimationFrame(() => {
                    console.log('🎨 Rendering cached tags...');
                    if (this._updateAvailableTags) {
                        this._updateAvailableTags(cachedTags, null);
                    }
                    console.log(`✅ INSTANT RENDER: ${cachedTags.length} tags displayed from cache`);
                    
                    // CRITICAL FIX: Restore selected tags after rendering
                    if (savedSelectedTags.length > 0) {
                        this.state.persistentSelectedTags = [...savedSelectedTags];
                        this.state.selectedTags = new Set(savedSelectedTags);
                        // Restore checkboxes
                        requestAnimationFrame(() => {
                            savedSelectedTags.forEach(tagName => {
                                const checkboxes = document.querySelectorAll(`input[type="checkbox"][value="${CSS.escape(tagName)}"]`);
                                checkboxes.forEach(cb => {
                                    if (!cb.checked) {
                                        cb.checked = true;
                                    }
                                });
                            });
                            // Restore selected tags display
                            if (this.getSelectedTagObjects && this.updateSelectedTags) {
                                const selectedTagObjects = this.getSelectedTagObjects();
                                if (selectedTagObjects.length > 0) {
                                    this.updateSelectedTags(selectedTagObjects);
                                }
                            }
                        });
                    }
                    
                    // Hide splash immediately
                    if (this.hideActionSplash) {
                        this.hideActionSplash();
                    }
                    if (typeof AppLoadingSplash !== 'undefined' && AppLoadingSplash.isVisible) {
                        AppLoadingSplash.stopAutoAdvance();
                        AppLoadingSplash.complete();
                    }
                });
                
                // Load selected tags and filters in background (non-blocking)
                console.log('📡 Background: Fetching selected tags and filters');
                Promise.allSettled([
                    this.fetchAndUpdateSelectedTags ? this.fetchAndUpdateSelectedTags() : Promise.resolve(),
                    this.fetchAndPopulateFilters ? this.fetchAndPopulateFilters() : Promise.resolve()
                ]).then(() => {
                    console.log('✅ Background: Selected tags and filters loaded');
                    // CRITICAL FIX: Ensure selected tags are still preserved after background fetch
                    if (savedSelectedTags.length > 0 && this.state.persistentSelectedTags.length === 0) {
                        this.state.persistentSelectedTags = [...savedSelectedTags];
                        this.state.selectedTags = new Set(savedSelectedTags);
                        if (this.getSelectedTagObjects && this.updateSelectedTags) {
                            const selectedTagObjects = this.getSelectedTagObjects();
                            if (selectedTagObjects.length > 0) {
                                this.updateSelectedTags(selectedTagObjects);
                            }
                        }
                    }
                }).catch(err => {
                    console.warn('⚠️ Background load error (non-critical):', err);
                });
                
                return; // Exit early - we have cached data
            }
            
            // No cache available - show loading UI
            console.log('⏳ No cache found - loading from server...');
            // CRITICAL FIX: Don't show splash if TagManager.init already showed it
            // Only show if we're not already initializing
            if (!this.state || !this.state.initialized) {
                if (typeof AppLoadingSplash !== 'undefined' && !AppLoadingSplash.isVisible) {
                    AppLoadingSplash.updateProgress(50, 'Loading tags...');
                }

                // Show loading splash while fetching (only if not already shown)
                if (this.showActionSplash && typeof this.showActionSplash === 'function') {
                    this.showActionSplash('Loading tags from server...');
                }
            }

            // OPTIMIZED: Try direct /api/available-tags FIRST (it's faster than /api/initial-data)
            // Then fall back to /api/initial-data if needed
            console.log('⚡ Trying fast /api/available-tags endpoint first...');
            let timeoutId = null;
            try {
                // CRITICAL FIX: Increased timeout to 30 seconds for large files
                // Large Excel files can take time to process, especially on first load
                const controller = new AbortController();
                timeoutId = setTimeout(() => {
                    controller.abort();
                    console.warn('⚠️ /api/available-tags timeout after 30 seconds, falling back...');
                }, 30000);
                
                const quickResponse = await fetch('/api/available-tags?fast_load=1', {
                    signal: controller.signal
                });
                if (timeoutId) {
                    clearTimeout(timeoutId);
                    timeoutId = null;
                }
                
                // CRITICAL FIX: Handle non-OK responses (including 503, 202) gracefully - fall through to fallback
                if (!quickResponse.ok || quickResponse.status === 503 || quickResponse.status === 202) {
                    // 503 = Service Unavailable (memory high, processing, etc.)
                    // 202 = Accepted (still processing or memory high - use fallback)
                    const statusText = quickResponse.statusText || 'Service unavailable';
                    console.warn(`⚠️ /api/available-tags returned ${quickResponse.status} (${statusText}), falling back to /api/initial-data`);
                    // Don't throw yet - try to parse response to get message
                    try {
                        const errorData = await quickResponse.json();
                        if (errorData.message) {
                            console.warn(`   Message: ${errorData.message}`);
                        }
                    } catch (e) {
                        // Ignore JSON parse errors
                    }
                    throw new Error(`Service unavailable (${quickResponse.status}: ${statusText})`);
                }
                
                if (quickResponse.ok) {
                    const quickData = await quickResponse.json();
                    if (quickData && quickData.tags && Array.isArray(quickData.tags) && quickData.tags.length > 0) {
                        console.log(`✅ Fast load successful: ${quickData.tags.length} tags from /api/available-tags`);

                        // Save to cache for next time
                        if (this.saveAvailableTagsToCache) {
                            this.saveAvailableTagsToCache(quickData.tags);
                        }

                        // Update state
                        this.state.tags = [...quickData.tags];
                        this.state.originalTags = [...quickData.tags];

                        // Render immediately
                        if (this._updateAvailableTags) {
                            this._updateAvailableTags(quickData.tags, null);
                        }

                        // Hide splash
                        if (this.hideActionSplash) {
                            this.hideActionSplash();
                        }
                        if (typeof AppLoadingSplash !== 'undefined' && AppLoadingSplash.isVisible) {
                            AppLoadingSplash.stopAutoAdvance();
                            AppLoadingSplash.complete();
                        }

                        // Load selected tags and filters in background
                        Promise.allSettled([
                            this.fetchAndUpdateSelectedTags ? this.fetchAndUpdateSelectedTags() : Promise.resolve(),
                            this.fetchAndPopulateFilters ? this.fetchAndPopulateFilters() : Promise.resolve()
                        ]).then(() => {
                            console.log('✅ Background: Selected tags and filters loaded');
                        }).catch(err => {
                            console.warn('⚠️ Background load error (non-critical):', err);
                        });

                        return; // Success! Exit early
                    }
                }
            } catch (quickError) {
                // Clear timeout if it was set
                if (timeoutId) {
                    clearTimeout(timeoutId);
                    timeoutId = null;
                }
                
                // CRITICAL FIX: Hide splash on timeout/error to prevent UI hang
                if (quickError.name === 'AbortError' || quickError.message?.includes('timeout')) {
                    console.warn('⚠️ Fast /api/available-tags timed out, falling back to /api/initial-data');
                    // Hide splash immediately on timeout
                    if (this.hideActionSplash) {
                        this.hideActionSplash();
                    }
                    if (typeof AppLoadingSplash !== 'undefined' && AppLoadingSplash.isVisible) {
                        AppLoadingSplash.stopAutoAdvance();
                        AppLoadingSplash.complete();
                    }
                } else {
                console.warn('⚠️ Fast /api/available-tags failed, falling back to /api/initial-data:', quickError);
                }
            }

            // FALLBACK: If /api/available-tags didn't work, try /api/initial-data with timeout
            try {
                console.log('⏳ Trying /api/initial-data as fallback...');
                // CRITICAL FIX: Increased timeout to 30 seconds for large files
                // Large Excel files need more time to process
                const fetchPromise = fetch('/api/initial-data?fast_load=1&stream=1');
                const timeoutPromise = new Promise((_, reject) =>
                    setTimeout(() => reject(new Error('Server timeout')), 30000)
                );

                let response;
                try {
                    response = await Promise.race([fetchPromise, timeoutPromise]);
                } catch (timeoutError) {
                    console.warn('⚠️ Server fetch timeout after 30 seconds, using fast fallback');
                    console.log('📊 Current state - tags:', this.state?.tags?.length || 0, 'hasExistingTags:', Array.isArray(this.state?.tags) && this.state.tags.length > 0);

                    // CRITICAL FIX: Don't restart - just hide splash and show error
                    if (this.hideActionSplash) {
                        this.hideActionSplash();
                    }
                    if (typeof AppLoadingSplash !== 'undefined' && AppLoadingSplash.isVisible) {
                        AppLoadingSplash.stopAutoAdvance();
                        AppLoadingSplash.complete();
                    }
                    // Only fallback if we have no tags at all
                    const hasExistingTags = Array.isArray(this.state?.tags) && this.state.tags.length > 0;
                    console.log('🔄 Attempting fallback to originalCheckForExistingData...', {
                        hasExistingTags,
                        hasFallbackFunction: !!originalCheckForExistingData
                    });
                    if (!hasExistingTags) {
                        // Try direct API call to /api/available-tags as last resort
                        console.log('⚡ Attempting direct /api/available-tags call as emergency fallback');
                        let emergencyTimeoutId = null;
                        try {
                            // CRITICAL FIX: Increased timeout to 45 seconds for emergency fallback
                            // Large files need more time, especially on slower connections
                            const emergencyController = new AbortController();
                            emergencyTimeoutId = setTimeout(() => {
                                emergencyController.abort();
                                console.warn('⚠️ Emergency /api/available-tags timeout after 45 seconds');
                            }, 45000);
                            
                            const directResponse = await fetch('/api/available-tags?nocache=1&fast_load=1', {
                                signal: emergencyController.signal
                            });
                            if (emergencyTimeoutId) {
                                clearTimeout(emergencyTimeoutId);
                                emergencyTimeoutId = null;
                            }
                            
                            if (directResponse.ok) {
                                const tagsData = await directResponse.json();
                                if (tagsData && tagsData.tags && Array.isArray(tagsData.tags) && tagsData.tags.length > 0) {
                                    console.log(`✅ Emergency fallback successful: loaded ${tagsData.tags.length} tags`);

                                    // Update state
                                    this.state.tags = [...tagsData.tags];
                                    this.state.originalTags = [...tagsData.tags];

                                    // Save to cache
                                    if (this.saveAvailableTagsToCache) {
                                        this.saveAvailableTagsToCache(tagsData.tags);
                                    }

                                    // Render immediately
                                    if (this._updateAvailableTags) {
                                        this._updateAvailableTags(tagsData.tags, null);
                                    }

                                    // Hide splash
                                    if (this.hideActionSplash) {
                                        this.hideActionSplash();
                                    }
                                    if (typeof AppLoadingSplash !== 'undefined' && AppLoadingSplash.isVisible) {
                                        AppLoadingSplash.stopAutoAdvance();
                                        AppLoadingSplash.complete();
                                    }

                                    return;
                                }
                            }
                        } catch (directError) {
                            // Clear timeout if it was set
                            if (emergencyTimeoutId) {
                                clearTimeout(emergencyTimeoutId);
                                emergencyTimeoutId = null;
                            }
                            
                            // CRITICAL FIX: Hide splash on timeout/error
                            if (directError.name === 'AbortError' || directError.message?.includes('timeout')) {
                                console.error('❌ Direct /api/available-tags fallback timed out');
                                if (this.hideActionSplash) {
                                    this.hideActionSplash();
                                }
                                if (typeof AppLoadingSplash !== 'undefined' && AppLoadingSplash.isVisible) {
                                    AppLoadingSplash.stopAutoAdvance();
                                    AppLoadingSplash.complete();
                                }
                            } else {
                            console.error('❌ Direct /api/available-tags fallback failed:', directError);
                            }
                        }

                        // If direct fallback failed, try originalCheckForExistingData with longer timeout
                        if (originalCheckForExistingData && typeof originalCheckForExistingData === 'function') {
                            console.log('⚡ Calling originalCheckForExistingData as final fallback');
                            try {
                                // Wrap in Promise.race with longer timeout
                                const originalPromise = originalCheckForExistingData.call(this);
                                const finalTimeoutPromise = new Promise((_, reject) =>
                                    setTimeout(() => reject(new Error('Final fallback timeout')), 60000)
                                );
                                await Promise.race([originalPromise, finalTimeoutPromise]);
                            } catch (finalError) {
                                console.error('❌ Final fallback also failed:', finalError);
                                // Show user-friendly error message
                                const availableTagsContainer = document.getElementById('availableTags');
                                if (availableTagsContainer && (!this.state?.tags || this.state.tags.length === 0)) {
                                    availableTagsContainer.innerHTML = `
                                        <div class="text-center py-5">
                                            <div class="alert alert-warning">
                                                <h5>Loading tags is taking longer than expected</h5>
                                                <p>Your file may be large. Please wait a moment and refresh the page, or try uploading again.</p>
                                                <button class="btn btn-primary mt-2" onclick="location.reload()">Refresh Page</button>
                                            </div>
                                        </div>
                                    `;
                                }
                            }
                        } else {
                            console.warn('⚠️ All fallbacks exhausted - no tags loaded');
                            // Show user-friendly error message
                            const availableTagsContainer = document.getElementById('availableTags');
                            if (availableTagsContainer && (!this.state?.tags || this.state.tags.length === 0)) {
                                availableTagsContainer.innerHTML = `
                                    <div class="text-center py-5">
                                        <div class="alert alert-warning">
                                            <h5>Unable to load tags</h5>
                                            <p>Please try refreshing the page or uploading your file again.</p>
                                            <button class="btn btn-primary mt-2" onclick="location.reload()">Refresh Page</button>
                                        </div>
                                    </div>
                                `;
                            }
                        }
                    } else {
                        console.warn('⚠️ Skipping fallback - already have tags');
                    }
                    return;
                }
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('⚡ Initial data response:', data);
                    
                    if (data.success && data.available_tags && Array.isArray(data.available_tags) && data.available_tags.length > 0) {
                        console.log(`⚡ Loaded ${data.available_tags.length} tags from server`);
                        
                        // Save to cache for next instant load
                        if (this.saveAvailableTagsToCache) {
                            this.saveAvailableTagsToCache(data.available_tags);
                            console.log(`💾 Cached ${data.available_tags.length} tags for next load`);
                        }
                        
                        // Update state immediately
                        this.state.tags = [...data.available_tags];
                        this.state.originalTags = [...data.available_tags];
                        
                        // Update UI with loaded data IMMEDIATELY (no debounce for initial load)
                        // Use _updateAvailableTags directly to avoid debounce delay
                        this._updateAvailableTags(data.available_tags, null);
                        
                        // Immediately check if tags are visible and hide splash
                        requestAnimationFrame(() => {
                            const container = document.getElementById('availableTags');
                            if (container) {
                                const tagItems = container.querySelectorAll('.tag-item');
                                if (tagItems.length > 0) {
                                    console.log(`⚡ Tags rendered (${tagItems.length} items), hiding splash immediately`);
                                    if (this.hideActionSplash) {
                                        this.hideActionSplash();
                                    }
                                    if (AppLoadingSplash && AppLoadingSplash.isVisible) {
                                        AppLoadingSplash.stopAutoAdvance();
                                        AppLoadingSplash.complete();
                                    }
                                }
                            }
                        });
                        
                        // Also ensure splash is hidden when tags appear (backup)
                        if (this._waitForTagsToAppear) {
                            this._waitForTagsToAppear();
                        }
                        
                        // Restore selected tags (non-blocking)
                        this.fetchAndUpdateSelectedTags().catch(err => {
                            console.warn('Error restoring selected tags:', err);
                        });
                        
                        // Update filters
                        this.updateFilters(data.filters || {
                            vendor: [],
                            brand: [],
                            productType: [],
                            lineage: [],
                            weight: []
                        }, true);
                        
                        // Update file info
                        if (data.filename) {
                            const fileInfoText = document.getElementById('fileInfoText');
                            if (fileInfoText) {
                                fileInfoText.textContent = data.filename;
                            }
                        }
                        
                        console.log('⚡ Background data loading complete');
                    } else {
                        console.warn('⚡ No initial data available:', data);
                        // Fallback to original checkForExistingData if available
                        if (originalCheckForExistingData && typeof originalCheckForExistingData === 'function') {
                            console.log('⚡ Falling back to original checkForExistingData');
                            try {
                                await originalCheckForExistingData.call(this);
                            } catch (fallbackError) {
                                console.error('⚡ Fallback failed:', fallbackError);
                                this.initializeEmptyState();
                            }
                        } else {
                            this.initializeEmptyState();
                        }
                    }
                } else {
                    console.error('⚡ Initial data endpoint error:', response.status, response.statusText);
                    // Fallback to original checkForExistingData if available
                    if (originalCheckForExistingData && typeof originalCheckForExistingData === 'function') {
                        console.log('⚡ Falling back to original checkForExistingData');
                        try {
                            await originalCheckForExistingData.call(this);
                        } catch (fallbackError) {
                            console.error('⚡ Fallback failed:', fallbackError);
                            this.initializeEmptyState();
                        }
                    } else {
                        this.initializeEmptyState();
                    }
                }
            } catch (error) {
                console.error('⚡ Initial data load error:', error);
                // Fallback to original checkForExistingData if available
                if (originalCheckForExistingData && typeof originalCheckForExistingData === 'function') {
                    console.log('⚡ Falling back to original checkForExistingData after error');
                    try {
                        await originalCheckForExistingData.call(this);
                    } catch (fallbackError) {
                        console.error('⚡ Fallback failed:', fallbackError);
                        this.initializeEmptyState();
                    }
                } else {
                    this.initializeEmptyState();
                }
            }
        };
        
        console.log('⚡ Page load optimization active');
    }
    
    // ULTRA-FAST RELOAD: Check cache immediately on script load (before DOM ready)
    // This allows instant tag display even before TagManager is fully initialized
    function earlyCacheCheck() {
        try {
            // Try to find any cached tags immediately
            const storageBackends = [];
            if (window.localStorage) storageBackends.push({ name: 'localStorage', storage: localStorage });
            if (window.sessionStorage) storageBackends.push({ name: 'sessionStorage', storage: sessionStorage });
            
            if (storageBackends.length > 0) {
                // Search for any valid cache keys
                const allKeys = [];
                for (const backend of storageBackends) {
                    for (let i = 0; i < backend.storage.length; i++) {
                        const key = backend.storage.key(i);
                        if (key && key.startsWith('agt_available_tags_')) {
                            allKeys.push({ key, storage: backend.storage });
                        }
                    }
                }
                
                if (allKeys.length > 0) {
                    console.log(`⚡ Early cache check: Found ${allKeys.length} potential cache keys`);
                    // Try to find a valid cache entry
                    for (const { key, storage } of allKeys) {
                        try {
                            const raw = storage.getItem(key);
                            if (raw) {
                                const payload = JSON.parse(raw);
                                if (payload && Array.isArray(payload.tags) && payload.tags.length > 0) {
                                    const age = Date.now() - (payload.timestamp || 0);
                                    const CACHE_TTL_MS = 10 * 60 * 1000; // 10 minutes
                                    if (age <= CACHE_TTL_MS) {
                                        console.log(`⚡ Early cache HIT: Found ${payload.tags.length} tags in ${storage === localStorage ? 'localStorage' : 'sessionStorage'}`);
                                        // Store in window for TagManager to pick up
                                        window._earlyCacheFound = { key, tags: payload.tags, storage: storage === localStorage ? 'localStorage' : 'sessionStorage' };
                                        break;
                                    }
                                }
                            }
                        } catch (e) {
                            continue;
                        }
                    }
                }
            }
        } catch (error) {
            console.warn('Early cache check failed:', error);
        }
    }
    
    // Run early cache check immediately
    earlyCacheCheck();
    
    // Run optimization when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', optimizePageLoad);
    } else {
        optimizePageLoad();
    }
})();

