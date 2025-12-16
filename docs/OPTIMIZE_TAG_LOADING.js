// OPTIMIZATION: Fast tag loading for large datasets
// Add this to the frontend to implement lazy loading and pagination

// 1. Lazy Loading Implementation
function implementLazyTagLoading() {
    console.log("🚀 Implementing lazy tag loading...");
    
    // Load tags in batches of 100
    const BATCH_SIZE = 100;
    let currentBatch = 0;
    let allTags = [];
    
    function loadNextBatch() {
        const start = currentBatch * BATCH_SIZE;
        const end = start + BATCH_SIZE;
        
        console.log(`📦 Loading batch ${currentBatch + 1} (${start}-${end})...`);
        
        fetch('/api/available-tags-lite')
            .then(response => response.json())
            .then(data => {
                if (data.tags && data.tags.length > 0) {
                    allTags = data.tags;
                    
                    // Display first batch immediately
                    if (currentBatch === 0) {
                        updateTagDisplay(allTags.slice(0, BATCH_SIZE));
                    }
                    
                    // Load remaining batches in background
                    if (allTags.length > BATCH_SIZE) {
                        setTimeout(() => {
                            loadRemainingBatches(allTags, BATCH_SIZE);
                        }, 500);
                    }
                }
            })
            .catch(error => {
                console.error("❌ Batch loading failed:", error);
            });
    }
    
    function loadRemainingBatches(tags, batchSize) {
        let batchIndex = 1;
        
        function loadBatch() {
            const start = batchIndex * batchSize;
            const end = start + batchSize;
            
            if (start < tags.length) {
                console.log(`📦 Loading background batch ${batchIndex + 1}...`);
                
                // Append to display
                appendTagsToDisplay(tags.slice(start, end));
                
                batchIndex++;
                
                // Load next batch after a short delay
                setTimeout(loadBatch, 200);
            } else {
                console.log("✅ All batches loaded!");
            }
        }
        
        loadBatch();
    }
    
    // Start loading
    loadNextBatch();
}

// 2. Virtual Scrolling for Large Tag Lists
function implementVirtualScrolling() {
    console.log("🚀 Implementing virtual scrolling...");
    
    const container = document.querySelector('.tags-container');
    if (!container) return;
    
    const ITEM_HEIGHT = 40; // Height of each tag item
    const VISIBLE_ITEMS = 20; // Number of visible items
    const BUFFER_SIZE = 5; // Extra items to render for smooth scrolling
    
    let scrollTop = 0;
    let allTags = [];
    
    function updateVisibleItems() {
        const startIndex = Math.max(0, Math.floor(scrollTop / ITEM_HEIGHT) - BUFFER_SIZE);
        const endIndex = Math.min(allTags.length, startIndex + VISIBLE_ITEMS + BUFFER_SIZE * 2);
        
        // Clear container
        container.innerHTML = '';
        
        // Add spacer for items above visible area
        const topSpacer = document.createElement('div');
        topSpacer.style.height = `${startIndex * ITEM_HEIGHT}px`;
        container.appendChild(topSpacer);
        
        // Add visible items
        for (let i = startIndex; i < endIndex; i++) {
            const tagElement = createTagElement(allTags[i]);
            container.appendChild(tagElement);
        }
        
        // Add spacer for items below visible area
        const bottomSpacer = document.createElement('div');
        bottomSpacer.style.height = `${(allTags.length - endIndex) * ITEM_HEIGHT}px`;
        container.appendChild(bottomSpacer);
    }
    
    // Listen for scroll events
    container.addEventListener('scroll', () => {
        scrollTop = container.scrollTop;
        updateVisibleItems();
    });
}

// 3. Progressive Loading with Progress Bar
function implementProgressiveLoading() {
    console.log("🚀 Implementing progressive loading...");
    
    // Show progress bar
    const progressBar = document.createElement('div');
    progressBar.innerHTML = `
        <div style="position: fixed; top: 0; left: 0; right: 0; background: #007bff; color: white; padding: 10px; text-align: center; z-index: 9999;">
            <div>Loading tags... <span id="progress-text">0%</span></div>
            <div style="background: #0056b3; height: 4px; margin-top: 5px;">
                <div id="progress-bar" style="background: white; height: 100%; width: 0%; transition: width 0.3s;"></div>
            </div>
        </div>
    `;
    document.body.appendChild(progressBar);
    
    let loadedTags = 0;
    const totalTags = 2190; // Estimated total
    
    function updateProgress(count) {
        loadedTags = count;
        const percentage = Math.min(100, (loadedTags / totalTags) * 100);
        
        document.getElementById('progress-text').textContent = `${Math.round(percentage)}%`;
        document.getElementById('progress-bar').style.width = `${percentage}%`;
        
        if (percentage >= 100) {
            setTimeout(() => {
                progressBar.remove();
            }, 1000);
        }
    }
    
    // Load tags progressively
    fetch('/api/available-tags')
        .then(response => response.json())
        .then(data => {
            if (data.tags) {
                // Simulate progressive loading
                let index = 0;
                const batchSize = 50;
                
                function loadBatch() {
                    const endIndex = Math.min(index + batchSize, data.tags.length);
                    
                    // Process batch
                    for (let i = index; i < endIndex; i++) {
                        // Add tag to display
                        addTagToDisplay(data.tags[i]);
                    }
                    
                    index = endIndex;
                    updateProgress(index);
                    
                    // Continue loading if more tags
                    if (index < data.tags.length) {
                        setTimeout(loadBatch, 50); // 50ms delay between batches
                    }
                }
                
                loadBatch();
            }
        });
}

// 4. Cache Management
function implementTagCaching() {
    console.log("🚀 Implementing tag caching...");
    
    const CACHE_KEY = 'tag_cache_v1';
    const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
    
    function getCachedTags() {
        try {
            const cached = localStorage.getItem(CACHE_KEY);
            if (cached) {
                const data = JSON.parse(cached);
                if (Date.now() - data.timestamp < CACHE_DURATION) {
                    console.log("✅ Using cached tags");
                    return data.tags;
                }
            }
        } catch (error) {
            console.warn("Cache read error:", error);
        }
        return null;
    }
    
    function setCachedTags(tags) {
        try {
            const data = {
                tags: tags,
                timestamp: Date.now()
            };
            localStorage.setItem(CACHE_KEY, JSON.stringify(data));
            console.log("✅ Tags cached");
        } catch (error) {
            console.warn("Cache write error:", error);
        }
    }
    
    // Check cache first
    const cachedTags = getCachedTags();
    if (cachedTags) {
        updateTagDisplay(cachedTags);
        return;
    }
    
    // Load from server and cache
    fetch('/api/available-tags')
        .then(response => response.json())
        .then(data => {
            if (data.tags) {
                setCachedTags(data.tags);
                updateTagDisplay(data.tags);
            }
        });
}

// 5. Main Optimization Function
function optimizeTagLoading() {
    console.log("🚀 Starting tag loading optimization...");
    
    // Choose optimization strategy based on dataset size
    const estimatedTags = 2190;
    
    if (estimatedTags > 1000) {
        // Large dataset - use progressive loading
        implementProgressiveLoading();
    } else if (estimatedTags > 500) {
        // Medium dataset - use lazy loading
        implementLazyTagLoading();
    } else {
        // Small dataset - use caching
        implementTagCaching();
    }
    
    // Always implement virtual scrolling for large lists
    if (estimatedTags > 200) {
        implementVirtualScrolling();
    }
}

// Helper functions
function updateTagDisplay(tags) {
    // Update the tag display with new tags
    console.log(`📝 Updating display with ${tags.length} tags`);
    // Implementation depends on your specific tag display code
}

function appendTagsToDisplay(tags) {
    // Append tags to existing display
    console.log(`📝 Appending ${tags.length} tags to display`);
    // Implementation depends on your specific tag display code
}

function addTagToDisplay(tag) {
    // Add a single tag to display
    // Implementation depends on your specific tag display code
}

function createTagElement(tag) {
    // Create DOM element for a tag
    const element = document.createElement('div');
    element.className = 'tag-item';
    element.textContent = tag.Description || tag.Product_Brand || 'Unknown';
    return element;
}

// Export for use
window.optimizeTagLoading = optimizeTagLoading;
