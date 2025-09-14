// Toast fallback: define Toast if not present
if (typeof Toast === 'undefined') {
  window.Toast = {
    show: (type, msg) => {
      if (type === 'error') {
        alert('Error: ' + msg);
      } else {
        alert(msg);
      }
    }
  };
}

// Classic types that should show "Lineage" instead of "Brand"
const CLASSIC_TYPES = [
    "flower", "pre-roll", "concentrate", "infused pre-roll", 
    "solventless concentrate", "vape cartridge"
];

// Add this near the top of the file, before any code that uses it
// Product type normalization mapping (same as backend TYPE_OVERRIDES)
const PRODUCT_TYPE_OVERRIDES = {
  "all-in-one": "vape cartridge",
  "rosin": "concentrate",
  "mini buds": "flower",
  "bud": "flower",
  "pre-roll": "pre-roll",
  "alcohol/ethanol extract": "rso/co2 tankers",
  "Alcohol/Ethanol Extract": "rso/co2 tankers",
  "alcohol ethanol extract": "rso/co2 tankers",
  "Alcohol Ethanol Extract": "rso/co2 tankers",
  "c02/ethanol extract": "rso/co2 tankers",
  "CO2 Concentrate": "rso/co2 tankers",
  "co2 concentrate": "rso/co2 tankers"
};

// Function to normalize product types (same as backend)
function normalizeProductType(productType) {
  if (!productType) return productType;
  const normalized = PRODUCT_TYPE_OVERRIDES[productType.toLowerCase()];
  return normalized || productType;
}

const VALID_PRODUCT_TYPES = [
  "flower", "pre-roll", "infused pre-roll", "concentrate", "solventless concentrate", "vape cartridge",
  "edible (solid)", "edible (liquid)", "high cbd edible liquid", "tincture", "topical", "capsule", "paraphernalia",
  "rso/co2 tankers"
];

const debounce = (func, delay) => {
    let timeoutId;
    return function(...args) {
        const context = this;
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            func.apply(context, args);
        }, delay);
    };
};

// Application Loading Splash Manager
const AppLoadingSplash = {
    loadingSteps: [
        { text: 'Initializing application...', progress: 10 },
        { text: 'Loading templates...', progress: 25 },
        { text: 'Preparing interface...', progress: 40 },
        { text: 'Loading product data...', progress: 60 },
        { text: 'Processing tags...', progress: 75 },
        { text: 'Setting up filters...', progress: 90 },
        { text: 'Almost ready...', progress: 95 },
        { text: 'Welcome to AGT Designer!', progress: 100 }
    ],
    currentStep: 0,
    isVisible: true,
    autoAdvanceInterval: null,

    show() {
        this.isVisible = true;
        this.currentStep = 0;
        
        const splash = document.getElementById('appLoadingSplash');
        const mainContent = document.getElementById('mainContent');
        
        if (splash) {
            splash.style.display = 'flex';
            splash.classList.remove('fade-out');
        }
        
        if (mainContent) {
            mainContent.classList.remove('loaded');
            mainContent.style.opacity = '0';
        }
        
        this.updateProgress(0, 'Initializing application...');
        console.log('Splash screen shown');
    },

    updateProgress(progress, text) {
        const fillElement = document.getElementById('appLoadingFill');
        const textElement = document.getElementById('appLoadingText');
        const statusElement = document.getElementById('appLoadingStatus');
        
        if (fillElement) {
            fillElement.style.width = `${progress}%`;
        }
        
        if (textElement) {
            textElement.style.opacity = '0';
            setTimeout(() => {
                textElement.textContent = text;
                textElement.style.opacity = '1';
            }, 150);
        }
        
        if (statusElement) {
            statusElement.textContent = this.getStatusText(progress);
        }
        
        // Log progress for debugging
        console.log(`Splash progress: ${progress}% - ${text}`);
    },

    getStatusText(progress) {
        if (progress < 25) return 'Initializing';
        if (progress < 50) return 'Loading';
        if (progress < 75) return 'Processing';
        if (progress < 100) return 'Finalizing';
        return 'Ready';
    },

    nextStep() {
        if (this.currentStep < this.loadingSteps.length - 1) {
            this.currentStep++;
            const step = this.loadingSteps[this.currentStep];
            this.updateProgress(step.progress, step.text);
        }
    },

    complete() {
        this.updateProgress(100, 'Welcome to AGT Designer!');
        setTimeout(() => {
            this.hide();
        }, 1000);
    },

    hide() {
        this.isVisible = false;
        this.stopAutoAdvance();
        
        const splash = document.getElementById('appLoadingSplash');
        const mainContent = document.getElementById('mainContent');
        
        if (splash) {
            splash.classList.add('fade-out');
            setTimeout(() => {
                splash.style.display = 'none';
            }, 500);
        }
        
        if (mainContent) {
            setTimeout(() => {
                mainContent.classList.add('loaded');
                mainContent.style.opacity = '1';
            }, 100);
        }
        
        console.log('Splash screen hidden');
    },

    // Auto-advance steps for visual feedback
    startAutoAdvance() {
        this.stopAutoAdvance(); // Clear any existing interval
        this.autoAdvanceInterval = setInterval(() => {
            if (this.isVisible && this.currentStep < this.loadingSteps.length - 2) {
                this.nextStep();
            }
        }, 800);
    },

    stopAutoAdvance() {
        if (this.autoAdvanceInterval) {
            clearInterval(this.autoAdvanceInterval);
            this.autoAdvanceInterval = null;
        }
    },

    // Emergency hide function for debugging
    emergencyHide() {
        console.log('Emergency hiding splash screen');
        this.isVisible = false;
        this.stopAutoAdvance();
        
        const splash = document.getElementById('appLoadingSplash');
        const mainContent = document.getElementById('mainContent');
        
        if (splash) {
            splash.style.display = 'none';
        }
        
        if (mainContent) {
            mainContent.style.opacity = '1';
            mainContent.classList.add('loaded');
        }
    }
};

const TagManager = {
    state: {
        selectedTags: new Set(),
        persistentSelectedTags: new Set(), // New: persistent selected tags independent of filters
        initialized: false,
        filters: {},
        loading: false,
        brandCategories: new Map(),  // Add this for storing brand subcategories
        originalTags: [], // Store original tags separately
        originalFilterOptions: {}, // Store original filter options to preserve order
        lineageColors: {
            'SATIVA': 'var(--lineage-sativa)',
            'INDICA': 'var(--lineage-indica)',
            'HYBRID': 'var(--lineage-hybrid)',
            'HYBRID/SATIVA': 'var(--lineage-hybrid-sativa)',
            'HYBRID/INDICA': 'var(--lineage-hybrid-indica)',
            'CBD': 'var(--lineage-cbd)',
            'PARA': 'var(--lineage-para)',
            'MIXED': 'var(--lineage-mixed)',
            'CBD_BLEND': 'var(--lineage-cbd)'
        },
        filterCache: null,
        updateAvailableTagsTimer: null // Add timer tracking
    },

    // Function to update brand filter label based on product type
    updateBrandFilterLabel() {
        const brandFilterLabel = document.querySelector('label[for="brandFilter"]');
        if (brandFilterLabel) {
            brandFilterLabel.textContent = 'Brand';
            brandFilterLabel.setAttribute('aria-label', 'Brand Filter');
        }
    },

    updateFilters(filters) {
        if (!filters) return;
        
        // Debug log for filters
        console.log('Updating filters with:', filters);
        
        // Store original filter options to preserve order
        if (!this.state.originalFilterOptions.vendor) {
            this.state.originalFilterOptions = { ...filters };
        }
        
        // Map of filter types to their HTML IDs (matching backend field names)
        const filterFieldMap = {
            vendor: 'vendorFilter',
            brand: 'brandFilter',
            productType: 'productTypeFilter', // Backend now returns 'productType'
            lineage: 'lineageFilter',
            weight: 'weightFilter'
            // Removed strain since there's no strainFilter dropdown in the HTML
        };
        
        // Update each filter dropdown
        Object.entries(filterFieldMap).forEach(([filterType, filterId]) => {
            const filterElement = document.getElementById(filterId);
            
            if (!filterElement) {
                console.warn(`Filter element not found: ${filterId}`);
                return;
            }
            
            // Get values for this filter type
            const fieldValues = filters[filterType] || [];
            const values = new Set();
            fieldValues.forEach(value => {
                if (value && value.trim() !== '') {
                    values.add(value.trim());
                }
            });
            
            // Sort values alphabetically for consistent ordering
            const sortedValues = Array.from(values).sort((a, b) => {
                // Special handling for lineage to maintain logical order
                if (filterType === 'lineage') {
                    const lineageOrder = ['SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA', 'CBD', 'CBD_BLEND', 'MIXED', 'PARA'];
                    const aIndex = lineageOrder.indexOf(a.toUpperCase());
                    const bIndex = lineageOrder.indexOf(b.toUpperCase());
                    if (aIndex !== -1 && bIndex !== -1) {
                        return aIndex - bIndex;
                    }
                }
                return a.localeCompare(b);
            });
            
            console.log(`Updating ${filterId} with values:`, sortedValues);
            
            // Special debug for weight filter
            if (filterType === 'weight') {
                console.log('Weight filter values (first 10):', sortedValues.slice(0, 10));
            }
            
            // Store current value
            const currentValue = filterElement.value;
            
            // Update the dropdown options with special formatting for RSO/CO2 Tanker
            filterElement.innerHTML = `
                <option value="">All</option>
                ${sortedValues.map(value => {
                    // Apply special font formatting for RSO/CO2 Tanker
                    if (value === 'rso/co2 tankers') {
                        return `<option value="${value}" style="font-weight: bold; font-style: italic; color: #a084e8;">RSO/CO2 Tanker</option>`;
                    }
                    return `<option value="${value}">${value}</option>`;
                }).join('')}
            `;
            
            // Try to restore the previous selection if it's still valid
            if (currentValue && sortedValues.includes(currentValue)) {
                filterElement.value = currentValue;
            } else {
                filterElement.value = '';
            }
        });
    },

    async updateFilterOptions() {
        try {
            // Get current filter values
            const currentFilters = {
                vendor: document.getElementById('vendorFilter')?.value || '',
                brand: document.getElementById('brandFilter')?.value || '',
                productType: document.getElementById('productTypeFilter')?.value || '',
                lineage: document.getElementById('lineageFilter')?.value || '',
                weight: document.getElementById('weightFilter')?.value || ''
            };

            // Only update filter options if we have original options
            if (!this.state.originalFilterOptions.vendor) {
                console.log('No original filter options available, skipping update');
                return;
            }

            // Get the currently filtered tags to determine available options
            const tagsToFilter = this.state.originalTags.length > 0 ? this.state.originalTags : this.state.tags;
            
            // Apply current filters to get the subset of tags that would be shown
            const filteredTags = tagsToFilter.filter(tag => {
                // Check vendor filter - only apply if not empty and not "All"
                if (currentFilters.vendor && currentFilters.vendor.trim() !== '' && currentFilters.vendor.toLowerCase() !== 'all') {
                    const tagVendor = (tag.vendor || '').trim();
                    if (tagVendor.toLowerCase() !== currentFilters.vendor.toLowerCase()) {
                        return false;
                    }
                }
                
                // Check brand filter - only apply if not empty and not "All"
                if (currentFilters.brand && currentFilters.brand.trim() !== '' && currentFilters.brand.toLowerCase() !== 'all') {
                    const tagBrand = (tag.productBrand || '').trim();
                    if (tagBrand.toLowerCase() !== currentFilters.brand.toLowerCase()) {
                        return false;
                    }
                }
                
                // Check product type filter - only apply if not empty and not "All"
                if (currentFilters.productType && currentFilters.productType.trim() !== '' && currentFilters.productType.toLowerCase() !== 'all') {
                    const tagProductType = (tag.productType || '').trim();
                    if (tagProductType.toLowerCase() !== currentFilters.productType.toLowerCase()) {
                        return false;
                    }
                }
                
                // Check lineage filter - only apply if not empty and not "All"
                if (currentFilters.lineage && currentFilters.lineage.trim() !== '' && currentFilters.lineage.toLowerCase() !== 'all') {
                    const tagLineage = (tag.lineage || '').trim();
                    if (tagLineage.toLowerCase() !== currentFilters.lineage.toLowerCase()) {
                        return false;
                    }
                }
                
                // Check weight filter - only apply if not empty and not "All"
                if (currentFilters.weight && currentFilters.weight.trim() !== '' && currentFilters.weight.toLowerCase() !== 'all') {
                    const tagWeightWithUnits = (tag.weightWithUnits || tag.weight || tag.WeightUnits || '').toString().trim().toLowerCase();
                    const filterWeight = currentFilters.weight.toString().trim().toLowerCase();
                    if (tagWeightWithUnits !== filterWeight) {
                        return false;
                    }
                }
                
                return true;
            });

            // Extract available options from filtered tags
            const availableOptions = {
                vendor: new Set(),
                brand: new Set(),
                productType: new Set(),
                lineage: new Set(),
                weight: new Set()
            };

            filteredTags.forEach(tag => {
                if (tag.vendor) availableOptions.vendor.add(tag.vendor.trim());
                if (tag.productBrand) availableOptions.brand.add(tag.productBrand.trim());
                if (tag.productType) availableOptions.productType.add(tag.productType.trim());
                if (tag.lineage) availableOptions.lineage.add(tag.lineage.trim());
                if (tag.weightWithUnits || tag.WeightUnits || tag.weight) {
                    // Always use the combined value for display and filtering
                    const combined = (tag.weightWithUnits || tag.WeightUnits || tag.weight).toString().trim();
                    if (combined) availableOptions.weight.add(combined);
                }
            });

            // Update each filter dropdown with available options
            const filterFieldMap = {
                vendor: 'vendorFilter',
                brand: 'brandFilter',
                productType: 'productTypeFilter',
                lineage: 'lineageFilter',
                weight: 'weightFilter'
            };

            Object.entries(filterFieldMap).forEach(([filterType, filterId]) => {
                const filterElement = document.getElementById(filterId);
                if (!filterElement) {
                    return;
                }

                const currentValue = filterElement.value;
                const newOptions = Array.from(availableOptions[filterType]);
                
                // Sort options consistently
                const sortedOptions = [...newOptions].sort((a, b) => {
                    // Special handling for lineage to maintain logical order
                    if (filterType === 'lineage') {
                        const lineageOrder = ['SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA', 'CBD', 'CBD_BLEND', 'MIXED', 'PARA'];
                        const aIndex = lineageOrder.indexOf(a.toUpperCase());
                        const bIndex = lineageOrder.indexOf(b.toUpperCase());
                        if (aIndex !== -1 && bIndex !== -1) {
                            return aIndex - bIndex;
                        }
                    }
                    return a.localeCompare(b);
                });
                
                // Only update if options have actually changed
                const currentOptions = Array.from(filterElement.options).map(opt => opt.value).filter(v => v !== '');
                const optionsChanged = currentOptions.length !== sortedOptions.length || 
                                     !currentOptions.every((opt, i) => opt === sortedOptions[i]);
                
                if (optionsChanged) {
                    // Create new options HTML with special formatting for RSO/CO2 Tanker
                    const optionsHtml = `
                        <option value="">All</option>
                        ${sortedOptions.map(value => {
                            // Apply special font formatting for RSO/CO2 Tanker
                            if (value === 'rso/co2 tankers') {
                                return `<option value="${value}" style="font-weight: bold; font-style: italic; color: #a084e8;">RSO/CO2 Tanker</option>`;
                            }
                            return `<option value="${value}">${value}</option>`;
                        }).join('')}
                    `;
                    
                    // Update the dropdown options
                    filterElement.innerHTML = optionsHtml;
                    
                    // Try to restore the previous selection if it's still valid
                    if (currentValue && sortedOptions.includes(currentValue)) {
                        filterElement.value = currentValue;
                    } else {
                        filterElement.value = '';
                    }
                }
            });

        } catch (error) {
            console.error('Error updating filter options:', error);
        }
    },

    applyFilters() {
        // Get current filter values
        const vendorFilter = document.getElementById('vendorFilter')?.value || '';
        const brandFilter = document.getElementById('brandFilter')?.value || '';
        const productTypeFilter = document.getElementById('productTypeFilter')?.value || '';
        const lineageFilter = document.getElementById('lineageFilter')?.value || '';
        const weightFilter = document.getElementById('weightFilter')?.value || '';
        
        // Store current filters in state for use by updateSelectedTags
        this.state.filters = {
            vendor: vendorFilter,
            brand: brandFilter,
            productType: productTypeFilter,
            lineage: lineageFilter,
            weight: weightFilter
        };
        
        // Create a filter key for caching
        const filterKey = `${vendorFilter}|${brandFilter}|${productTypeFilter}|${lineageFilter}|${weightFilter}`;
        
        // Check if we have cached results for this exact filter combination
        if (this.state.filterCache && this.state.filterCache.key === filterKey) {
            // Always pass original tags to preserve persistent selections
            this.debouncedUpdateAvailableTags(this.state.originalTags, this.state.filterCache.result);
            this.renderActiveFilters();
            return;
        }
        
        // Filter the tags based on current filter values using original tags
        const tagsToFilter = this.state.originalTags.length > 0 ? this.state.originalTags : this.state.tags;
        
        const filteredTags = tagsToFilter.filter(tag => {
            // Check vendor filter - only apply if not empty and not "All"
            if (vendorFilter && vendorFilter.trim() !== '' && vendorFilter.toLowerCase() !== 'all') {
                const tagVendor = (tag.vendor || '').trim();
                if (tagVendor.toLowerCase() !== vendorFilter.toLowerCase()) {
                    return false;
                }
            }
            
            // Check brand filter - only apply if not empty and not "All"
            if (brandFilter && brandFilter.trim() !== '' && brandFilter.toLowerCase() !== 'all') {
                const tagBrand = (tag.productBrand || '').trim();
                if (tagBrand.toLowerCase() !== brandFilter.toLowerCase()) {
                    return false;
                }
            }
            
            // Check product type filter - only apply if not empty and not "All"
            if (productTypeFilter && productTypeFilter.trim() !== '' && productTypeFilter.toLowerCase() !== 'all') {
                const tagProductType = (tag.productType || tag['Product Type*'] || '').trim();
                const normalizedTagProductType = normalizeProductType(tagProductType);
                if (normalizedTagProductType.toLowerCase() !== productTypeFilter.toLowerCase()) {
                    return false;
                }
            }
            
            // Check lineage filter - only apply if not empty and not "All"
            if (lineageFilter && lineageFilter.trim() !== '' && lineageFilter.toLowerCase() !== 'all') {
                const tagLineage = (tag.lineage || '').trim();
                if (tagLineage.toLowerCase() !== lineageFilter.toLowerCase()) {
                    return false;
                }
            }
            
            // Check weight filter - only apply if not empty and not "All"
            if (weightFilter && weightFilter.trim() !== '' && weightFilter.toLowerCase() !== 'all') {
                const tagWeightWithUnits = (tag.weightWithUnits || tag.weight || tag.WeightUnits || '').toString().trim().toLowerCase();
                const filterWeight = weightFilter.toString().trim().toLowerCase();
                if (tagWeightWithUnits !== filterWeight) {
                    return false;
                }
            }
            
            return true;
        });
        
        // Cache the results
        this.state.filterCache = {
            key: filterKey,
            result: filteredTags
        };
        
        // Always pass original tags to preserve persistent selections, with filtered tags for display
        this.debouncedUpdateAvailableTags(this.state.originalTags, filteredTags);
        
        // Update selected tags to also respect the current filters
        const selectedTagObjects = Array.from(this.state.persistentSelectedTags).map(name => {
            // First try to find in current tags (filtered view)
            let foundTag = this.state.tags.find(t => t['Product Name*'] === name);
            // If not found in current tags, try original tags
            if (!foundTag) {
                foundTag = this.state.originalTags.find(t => t['Product Name*'] === name);
            }
            // If still not found, create a minimal tag object (for JSON matched items)
            if (!foundTag) {
                console.warn(`Tag not found in state: ${name}, creating minimal tag object`);
                foundTag = {
                    'Product Name*': name,
                    'Product Brand': 'Unknown',
                    'Vendor': 'Unknown',
                    'Product Type*': 'Unknown',
                    'Lineage': 'MIXED'
                };
            }
            return foundTag;
        }).filter(Boolean);
        
        this.updateSelectedTags(selectedTagObjects);
        this.renderActiveFilters();
    },

    handleSearch(listId, searchInputId) {
        const searchInput = document.getElementById(searchInputId);
        const searchTerm = searchInput.value.toLowerCase().trim();

        // Choose which tags to filter
        let tags = [];
        if (listId === 'availableTags') {
            tags = this.state.originalTags || [];
        } else if (listId === 'selectedTags') {
            tags = Array.from(this.state.selectedTags).map(name =>
                this.state.originalTags.find(t => t['Product Name*'] === name)
            ).filter(Boolean);
        }

        if (!searchTerm) {
            // Restore full list
            if (listId === 'availableTags') {
                this.debouncedUpdateAvailableTags(this.state.originalTags, null);
            } else if (listId === 'selectedTags') {
                this.updateSelectedTags(tags);
            }
            searchInput.classList.remove('search-active');
            return;
        }

        // Filter tags: only match product name
        const filteredTags = tags.filter(tag => {
            const tagName = tag['Product Name*'] || '';
            return tagName.toLowerCase().includes(searchTerm);
        });

        // Update the list with only matching tags
        if (listId === 'availableTags') {
            this.debouncedUpdateAvailableTags(this.state.originalTags, filteredTags);
        } else if (listId === 'selectedTags') {
            this.updateSelectedTags(filteredTags);
        }
        searchInput.classList.add('search-active');
    },

    extractBrand(tag) {
        // Try to get brand from Product Brand field first
        let brand = tag.productBrand || tag.brand || '';
        
        // If no brand found, try to extract from product name
        if (!brand) {
            const productName = tag['Product Name*'] || tag.ProductName || tag.Description || '';
            // Look for "by [Brand]" pattern
            const byMatch = productName.match(/by\s+([A-Za-z0-9\s]+)(?:\s|$)/i);
            if (byMatch) {
                brand = byMatch[1].trim();
            }
        }
        
        // If still no brand found, try to use the vendor as the brand
        if (!brand && tag.vendor) {
            brand = tag.vendor.trim();
        }
        
        return brand;
    },

    // Helper function to capitalize vendor names properly
    capitalizeVendorName(vendor) {
        if (!vendor) return '';
        
        // Handle common vendor name patterns
        const vendorLower = vendor.toLowerCase();
        
        // Known vendor name mappings
        const vendorMappings = {
            '1555 industrial llc': '1555 Industrial LLC',
            'dcz holdings inc': 'DCZ Holdings Inc.',
            'jsm llc': 'JSM LLC',
            'harmony farms': 'Harmony Farms',
            'hustler\'s ambition': 'Hustler\'s Ambition',
            'mama j\'s': 'Mama J\'s'
        };
        
        // Check if we have a known mapping
        if (vendorMappings[vendorLower]) {
            return vendorMappings[vendorLower];
        }
        
        // General capitalization for unknown vendors
        return vendor.split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');
    },

    // Helper function to capitalize brand names properly
    capitalizeBrandName(brand) {
        if (!brand) return '';
        
        // Handle common brand name patterns
        const brandLower = brand.toLowerCase();
        
        // Known brand name mappings
        const brandMappings = {
            'dank czar': 'Dank Czar',
            'omega': 'Omega',
            'airo pro': 'Airo Pro',
            'mama j\'s': 'Mama J\'s'
        };
        
        // Check if we have a known mapping
        if (brandMappings[brandLower]) {
            return brandMappings[brandLower];
        }
        
        // General capitalization for unknown brands
        return brand.split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');
    },

    organizeBrandCategories(tags) {
        const vendorGroups = new Map();
        let skippedTags = 0;
        
        // Debug: Log the first few tags to see their structure
        if (tags.length > 0) {
            console.log('First tag structure:', tags[0]);
            console.log('Available keys in first tag:', Object.keys(tags[0]));
        }
        
<<<<<<< HEAD
        tags.forEach(tag => {
            // Use the correct field names from the tag object - check multiple possible field names
            let vendor = tag.vendor || tag['Vendor'] || tag['Vendor/Supplier*'] || tag['Vendor/Supplier'] || '';
            let brand = tag.productBrand || tag['Product Brand'] || tag['ProductBrand'] || this.extractBrand(tag) || '';
            const rawProductType = tag.productType || tag['Product Type*'] || tag['Product Type'] || '';
            const normalizedProductType = normalizeProductType(rawProductType.trim());
            const productType = VALID_PRODUCT_TYPES.includes(normalizedProductType.toLowerCase())
              ? normalizedProductType.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(' ')
              : 'Unknown Type';
            const lineage = tag.lineage || tag['Lineage'] || 'MIXED';
            const weight = tag.weight || tag['Weight*'] || tag['Weight'] || tag['WeightUnits'] || '';
            const weightWithUnits = tag.weightWithUnits || weight || tag['WeightUnits'] || '';
=======
        tags.forEach((tag, index) => {
            try {
                // Debug logging for first few tags
                if (index < 3) {
                    console.log(`Processing tag ${index + 1}:`, {
                        tagKeys: Object.keys(tag),
                        vendor: tag.vendor || tag['Vendor'] || tag['Vendor/Supplier*'] || tag['Vendor/Supplier'] || '',
                        brand: tag.productBrand || tag['Product Brand'] || tag['ProductBrand'] || '',
                        weight: tag.weight || tag['Weight*'] || tag['Weight'] || tag['WeightUnits'] || '',
                        weightWithUnits: tag.weightWithUnits || tag.weight || tag['WeightUnits'] || ''
                    });
                }
                
                // Use the correct field names from the tag object - check multiple possible field names
                let vendor = tag.vendor || tag['Vendor'] || tag['Vendor/Supplier*'] || tag['Vendor/Supplier'] || '';
                let brand = tag.productBrand || tag['Product Brand'] || tag['ProductBrand'] || this.extractBrand(tag) || '';
                const rawProductType = tag.productType || tag['Product Type*'] || tag['Product Type'] || '';
                const normalizedProductType = normalizeProductType((rawProductType || '').trim());
                const productType = VALID_PRODUCT_TYPES.includes(normalizedProductType.toLowerCase())
                  ? normalizedProductType.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(' ')
                  : 'Unknown Type';
                const lineage = tag.lineage || tag['Lineage'] || 'MIXED';
                const weight = tag.weight || tag['Weight*'] || tag['Weight'] || tag['WeightUnits'] || '';
                const weightWithUnits = tag.weightWithUnits || weight || tag['WeightUnits'] || '';
>>>>>>> 1374859 (Refactor: Use only unified get_font_size for all Ratio font sizing; deprecate legacy ratio font size functions)

            // If no vendor found, try to extract from product name
            if (!vendor) {
                const productName = tag['Product Name*'] || tag.ProductName || tag.Description || '';
                // Look for "by [Brand]" pattern
                const byMatch = productName.match(/by\s+([A-Za-z0-9\s]+)(?:\s|$)/i);
                if (byMatch) {
                    vendor = byMatch[1].trim();
                }
            }

            // If still no vendor, use brand as vendor
            if (!vendor && brand) {
                vendor = brand;
            }

            // If still no vendor, use a default
            if (!vendor) {
                vendor = 'Unknown Vendor';
            }

            // Normalize the tag data
            const normalizedTag = {
                ...tag,
<<<<<<< HEAD
                vendor: this.capitalizeVendorName(vendor.trim()),
                brand: this.capitalizeBrandName(brand.trim()),
                productType: productType,
                lineage: (lineage || '').trim().toUpperCase(), // always uppercase for color
                weight: weight.trim(),
                weightWithUnits: weightWithUnits.trim(),
=======
                vendor: this.capitalizeVendorName((vendor || '').trim()),
                brand: this.capitalizeBrandName((brand || '').trim()),
                productType: productType,
                lineage: (lineage || '').trim().toUpperCase(), // always uppercase for color
                weight: (weight || '').toString().trim(),
                weightWithUnits: (weightWithUnits || '').toString().trim(),
>>>>>>> 1374859 (Refactor: Use only unified get_font_size for all Ratio font sizing; deprecate legacy ratio font size functions)
                displayName: tag['Product Name*'] || tag.ProductName || tag.Description || 'Unknown Product'
            };

            // Always create vendor group (even if vendor === brand)
            if (!vendorGroups.has(normalizedTag.vendor)) {
                vendorGroups.set(normalizedTag.vendor, new Map());
            }
            const brandGroups = vendorGroups.get(normalizedTag.vendor);

            // Always create brand group under vendor (even if vendor === brand)
            if (!brandGroups.has(normalizedTag.brand)) {
                brandGroups.set(normalizedTag.brand, new Map());
            }
            const productTypeGroups = brandGroups.get(normalizedTag.brand);

            // Create product type group if it doesn't exist
            if (!productTypeGroups.has(normalizedTag.productType)) {
                productTypeGroups.set(normalizedTag.productType, new Map());
            }
            const weightGroups = productTypeGroups.get(normalizedTag.productType);

            // Create weight group if it doesn't exist - use weightWithUnits as the key
            if (!weightGroups.has(normalizedTag.weightWithUnits)) {
                weightGroups.set(normalizedTag.weightWithUnits, []);
            }
            weightGroups.get(normalizedTag.weightWithUnits).push(normalizedTag);
<<<<<<< HEAD
=======
            } catch (error) {
                console.error('Error processing tag:', tag, error);
                skippedTags++;
            }
>>>>>>> 1374859 (Refactor: Use only unified get_font_size for all Ratio font sizing; deprecate legacy ratio font size functions)
        });

        if (skippedTags > 0) {
            console.info(`Skipped ${skippedTags} tags due to missing vendor information`);
        }

        return vendorGroups;
    },

    // Debounced version of updateAvailableTags to prevent multiple rapid calls
    debouncedUpdateAvailableTags: debounce(function(originalTags, filteredTags = null) {
        // Show action splash for tag population
        this.showActionSplash('Populating tags...');
        
        // Use requestAnimationFrame to ensure the splash shows before heavy DOM work
        requestAnimationFrame(() => {
            this._updateAvailableTags(originalTags, filteredTags);
            
            // Hide splash after a short delay to ensure smooth transition
            setTimeout(() => {
                this.hideActionSplash();
            }, 100);
        });
    }, 100),

    // Internal function that actually updates the available tags
    _updateAvailableTags(originalTags, filteredTags = null) {
        if (!originalTags || !Array.isArray(originalTags)) {
            console.warn('updateAvailableTags called with invalid originalTags:', originalTags);
            return;
        }
        
<<<<<<< HEAD
=======
        console.log('_updateAvailableTags called with:', {
            originalTagsCount: originalTags.length,
            filteredTagsCount: filteredTags ? filteredTags.length : 'null',
            sampleTag: originalTags[0]
        });
        
>>>>>>> 1374859 (Refactor: Use only unified get_font_size for all Ratio font sizing; deprecate legacy ratio font size functions)
        console.time('updateAvailableTags');
        
        const container = document.getElementById('availableTags');
        if (!container) {
            console.error('availableTags container not found');
            return;
        }

        // Store original tags in state for later use
        this.state.originalTags = [...originalTags];
        
        // Use filtered tags for display if provided, otherwise use original tags
        let tagsToDisplay = filteredTags || originalTags;
        
        // Filter out selected tags from available tags display
        const selectedTagNames = new Set(this.state.persistentSelectedTags);
        tagsToDisplay = tagsToDisplay.filter(tag => !selectedTagNames.has(tag['Product Name*']));
        
        this.state.tags = [...tagsToDisplay];
        
        // Store original tags if this is the first time loading
        if (this.state.originalTags.length === 0) {
            this.state.originalTags = [...originalTags];
        }
        
        // Store the select all containers before clearing
        const selectAllAvailableContainer = container.querySelector('.select-all-container');
        const selectAllAvailableCheckbox = document.getElementById('selectAllAvailable');
        
        // Clear existing content but preserve the select all container
        container.innerHTML = '';
        
        // Re-add the select all container if it existed
        if (selectAllAvailableContainer) {
            container.insertBefore(selectAllAvailableContainer, container.firstChild);
        } else {
            // Create select all container if it doesn't exist
            const selectAllContainer = document.createElement('div');
            selectAllContainer.className = 'd-flex align-items-center gap-3 mb-2';
            selectAllContainer.innerHTML = `
                <label class="d-flex align-items-center gap-2 cursor-pointer mb-0 select-all-container">
                    <input type="checkbox" id="selectAllAvailable" class="custom-checkbox">
                    <span class="text-secondary fw-semibold">Select All Available</span>
                </label>
            `;
            container.insertBefore(selectAllContainer, container.firstChild);
        }

        // Add global select all checkbox - only add event listener once
        const topSelectAll = document.getElementById('selectAllAvailable');
        console.log('Select All Available checkbox found:', topSelectAll);
        if (topSelectAll && !topSelectAll.hasAttribute('data-listener-added')) {
            console.log('Adding event listener to Select All Available checkbox');
            topSelectAll.setAttribute('data-listener-added', 'true');
            topSelectAll.addEventListener('change', (e) => {
                console.log('Select All Available checkbox changed:', e.target.checked);
                const isChecked = e.target.checked;
                const tagCheckboxes = document.querySelectorAll('#availableTags .tag-checkbox');
                console.log('Found available tag checkboxes:', tagCheckboxes.length);
                tagCheckboxes.forEach(checkbox => {
                    checkbox.checked = isChecked;
                    const tag = this.state.tags.find(t => t['Product Name*'] === checkbox.value);
                    if (tag) {
                        if (isChecked) {
                            this.state.persistentSelectedTags.add(tag['Product Name*']);
                        } else {
                            this.state.persistentSelectedTags.delete(tag['Product Name*']);
                        }
                    }
                });
                // Update the regular selectedTags set to match persistent ones
                this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                
                // Update the selected tags display
                const selectedTagObjects = Array.from(this.state.persistentSelectedTags).map(name =>
                    this.state.tags.find(t => t['Product Name*'] === name)
                ).filter(Boolean);
                this.updateSelectedTags(selectedTagObjects);
                
                // Efficiently update available tags display
                this.efficientlyUpdateAvailableTagsDisplay();
            });
        }

        // If no tags, just return
        if (tagsToDisplay.length === 0) {
            return;
        }

        // Assign a unique tagId to each tag (use index for uniqueness)
        tagsToDisplay.forEach((tag, idx) => {
            tag.tagId = tag['Product Name*'] + '___' + idx;
        });

        // Organize tags into hierarchical groups
        const groupedTags = this.organizeBrandCategories(tagsToDisplay);

        // Sort vendors alphabetically
        const sortedVendors = Array.from(groupedTags.entries())
            .sort(([a], [b]) => (a || '').localeCompare(b || ''));

        // Create vendor sections
        sortedVendors.forEach(([vendor, brandGroups]) => {
            const vendorSection = document.createElement('div');
            vendorSection.className = 'vendor-section mb-3';
            // Remove vendor label
            // Create vendor header with integrated checkbox
            const vendorHeader = document.createElement('h5');
            vendorHeader.className = 'vendor-header mb-2 d-flex align-items-center';
            
            const vendorCheckbox = document.createElement('input');
            vendorCheckbox.type = 'checkbox';
            vendorCheckbox.className = 'select-all-checkbox me-2';
            vendorCheckbox.addEventListener('change', (e) => {
                const isChecked = e.target.checked;
                // Select all descendant checkboxes (including subcategories and tags)
                const checkboxes = vendorSection.querySelectorAll('input[type="checkbox"]');
                checkboxes.forEach(checkbox => {
                    checkbox.checked = isChecked;
                    // Only update persistentSelectedTags for tag-checkboxes
                    if (checkbox.classList.contains('tag-checkbox')) {
                        const tag = this.state.tags.find(t => t['Product Name*'] === checkbox.value);
                        if (tag) {
                            if (isChecked) {
                                this.state.persistentSelectedTags.add(tag['Product Name*']);
                            } else {
                                this.state.persistentSelectedTags.delete(tag['Product Name*']);
                            }
                        }
                    }
                });
                // Update the regular selectedTags set to match persistent ones
                this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                
                // Update the selected tags display
                const selectedTagObjects = Array.from(this.state.persistentSelectedTags).map(name =>
                    this.state.tags.find(t => t['Product Name*'] === name)
                ).filter(Boolean);
                this.updateSelectedTags(selectedTagObjects);
                
                // Use efficient update instead of rebuilding entire DOM
                this.efficientlyUpdateAvailableTagsDisplay();
            });
            vendorHeader.appendChild(vendorCheckbox);
            vendorHeader.appendChild(document.createTextNode(vendor));
            vendorSection.appendChild(vendorHeader);

            // Create brand sections
            const sortedBrands = Array.from(brandGroups.entries())
                .sort(([a], [b]) => (a || '').localeCompare(b || ''));

            sortedBrands.forEach(([brand, productTypeGroups]) => {
                const brandSection = document.createElement('div');
                brandSection.className = 'brand-section ms-3 mb-2';
                // Remove brand label
                // Create brand header with integrated checkbox
                const brandHeader = document.createElement('h6');
                brandHeader.className = 'brand-header mb-2 d-flex align-items-center';
                
                const brandCheckbox = document.createElement('input');
                brandCheckbox.type = 'checkbox';
                brandCheckbox.className = 'select-all-checkbox me-2';
                brandCheckbox.addEventListener('change', (e) => {
                    const isChecked = e.target.checked;
                    // Select all descendant checkboxes (including subcategories and tags)
                    const checkboxes = brandSection.querySelectorAll('input[type="checkbox"]');
                    checkboxes.forEach(checkbox => {
                        checkbox.checked = isChecked;
                        // Only update persistentSelectedTags for tag-checkboxes
                        if (checkbox.classList.contains('tag-checkbox')) {
                            const tag = this.state.tags.find(t => t['Product Name*'] === checkbox.value);
                            if (tag) {
                                if (isChecked) {
                                    this.state.persistentSelectedTags.add(tag['Product Name*']);
                                } else {
                                    this.state.persistentSelectedTags.delete(tag['Product Name*']);
                                }
                            }
                        }
                    });
                    // Update the regular selectedTags set to match persistent ones
                    this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                    
                    // Update the selected tags display
                    const selectedTagObjects = Array.from(this.state.persistentSelectedTags).map(name =>
                        this.state.tags.find(t => t['Product Name*'] === name)
                    ).filter(Boolean);
                    this.updateSelectedTags(selectedTagObjects);
                    
                    // Use efficient update instead of rebuilding entire DOM
                    this.efficientlyUpdateAvailableTagsDisplay();
                });
                brandHeader.appendChild(brandCheckbox);
                brandHeader.appendChild(document.createTextNode(brand));
                brandSection.appendChild(brandHeader);

                // Create product type sections
                const sortedProductTypes = Array.from(productTypeGroups.entries())
                    .sort(([a], [b]) => (a || '').localeCompare(b || ''));

                sortedProductTypes.forEach(([productType, weightGroups]) => {
                    const productTypeSection = document.createElement('div');
                    productTypeSection.className = 'product-type-section ms-3 mb-2';
                    // Remove type label
                    // Create product type header
                    const typeHeader = document.createElement('div');
                    typeHeader.className = 'product-type-header mb-2 d-flex align-items-center';
                    
                    const productTypeCheckbox = document.createElement('input');
                    productTypeCheckbox.type = 'checkbox';
                    productTypeCheckbox.className = 'select-all-checkbox me-2';
                    productTypeCheckbox.addEventListener('change', (e) => {
                        const isChecked = e.target.checked;
                        // Select all descendant checkboxes (including subcategories and tags)
                        const checkboxes = productTypeSection.querySelectorAll('input[type="checkbox"]');
                        checkboxes.forEach(checkbox => {
                            checkbox.checked = isChecked;
                            // Only update persistentSelectedTags for tag-checkboxes
                            if (checkbox.classList.contains('tag-checkbox')) {
                                const tag = this.state.tags.find(t => t['Product Name*'] === checkbox.value);
                                if (tag) {
                                    if (isChecked) {
                                        this.state.persistentSelectedTags.add(tag['Product Name*']);
                                    } else {
                                        this.state.persistentSelectedTags.delete(tag['Product Name*']);
                                    }
                                }
                            }
                        });
                        // Update the regular selectedTags set to match persistent ones
                        this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                        
                        // Update the selected tags display
                        const selectedTagObjects = Array.from(this.state.persistentSelectedTags).map(name =>
                            this.state.tags.find(t => t['Product Name*'] === name)
                        ).filter(Boolean);
                        this.updateSelectedTags(selectedTagObjects);
                        
                        // Use efficient update instead of rebuilding entire DOM
                        this.efficientlyUpdateAvailableTagsDisplay();
                    });
                    typeHeader.appendChild(productTypeCheckbox);
                    typeHeader.appendChild(document.createTextNode(productType));
                    productTypeSection.appendChild(typeHeader);

                    // Create weight sections
                    const sortedWeights = Array.from(weightGroups.entries())
                        .sort(([a], [b]) => (a || '').localeCompare(b || ''));

                    sortedWeights.forEach(([weight, tags]) => {
                        const weightSection = document.createElement('div');
                        weightSection.className = 'weight-section ms-3 mb-1';
                        // Remove weight label
                        // Create weight header
                        const weightHeader = document.createElement('div');
                        weightHeader.className = 'weight-header mb-1 d-flex align-items-center';
                        
                        const weightCheckbox = document.createElement('input');
                        weightCheckbox.type = 'checkbox';
                        weightCheckbox.className = 'select-all-checkbox me-2';
                        weightCheckbox.addEventListener('change', (e) => {
                            const isChecked = e.target.checked;
                            // Select all descendant checkboxes (including subcategories and tags)
                            const checkboxes = weightSection.querySelectorAll('input[type="checkbox"]');
                            checkboxes.forEach(checkbox => {
                                checkbox.checked = isChecked;
                                // Only update persistentSelectedTags for tag-checkboxes
                                if (checkbox.classList.contains('tag-checkbox')) {
                                    const tag = this.state.tags.find(t => t['Product Name*'] === checkbox.value);
                                    if (tag) {
                                        if (isChecked) {
                                            this.state.persistentSelectedTags.add(tag['Product Name*']);
                                        } else {
                                            this.state.persistentSelectedTags.delete(tag['Product Name*']);
                                        }
                                    }
                                }
                            });
                            // Update the regular selectedTags set to match persistent ones
                            this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                            
                            // Update the selected tags display
                            const selectedTagObjects = Array.from(this.state.persistentSelectedTags).map(name =>
                                this.state.tags.find(t => t['Product Name*'] === name)
                            ).filter(Boolean);
                            this.updateSelectedTags(selectedTagObjects);
                            
                            // Use efficient update instead of rebuilding entire DOM
                            this.efficientlyUpdateAvailableTagsDisplay();
                        });
                        weightHeader.appendChild(weightCheckbox);
                        weightHeader.appendChild(document.createTextNode(weight));
                        weightSection.appendChild(weightHeader);
                        // Always render tags as leaf nodes - sort alphabetically by product name
                        if (tags && tags.length > 0) {
                            // Sort tags alphabetically by product name
                            const sortedTags = tags.sort((a, b) => {
                                const nameA = (a['Product Name*'] || a.ProductName || a.Description || '').toLowerCase();
                                const nameB = (b['Product Name*'] || b.ProductName || b.Description || '').toLowerCase();
                                return nameA.localeCompare(nameB);
                            });
                            
                            sortedTags.forEach(tag => {
                                const tagElement = this.createTagElement(tag);
                                tagElement.querySelector('.tag-checkbox').checked = this.state.persistentSelectedTags.has(tag['Product Name*']);
                                weightSection.appendChild(tagElement);
                            });
                        }
                        productTypeSection.appendChild(weightSection);
                    });
                    brandSection.appendChild(productTypeSection);
                });
                vendorSection.appendChild(brandSection);
            });
            container.appendChild(vendorSection);
        });

        this.updateTagCount('available', tagsToDisplay.length);
        console.timeEnd('updateAvailableTags');
        
        // Reinitialize drag and drop for new tags
        if (window.dragAndDropManager) {
            window.dragAndDropManager.reinitializeTagDragAndDrop();
        }
    },

    createTagElement(tag) {
        // Create the row container
        const row = document.createElement('div');
        row.className = 'tag-row d-flex align-items-center';

        // Checkbox (leftmost)
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'tag-checkbox me-2';
        checkbox.value = tag['Product Name*'];
        checkbox.checked = this.state.persistentSelectedTags.has(tag['Product Name*']);
        checkbox.addEventListener('change', (e) => this.handleTagSelection(e, tag));

        // Tag entry (colored)
        const tagElement = document.createElement('div');
        tagElement.className = 'tag-item d-flex align-items-center p-1 mb-1';
        
        // Add special styling for JSON matched tags
        if (tag.Source === 'JSON Match') {
          tagElement.classList.add('json-matched-tag');
          tagElement.style.border = '2px solid #28a745';
          tagElement.style.backgroundColor = 'rgba(40, 167, 69, 0.1)';
          tagElement.style.borderRadius = '8px';
        }
        
        // Set data-lineage attribute for CSS coloring
        const lineage = tag.lineage || tag.Lineage || 'MIXED';
        if (lineage) {
          console.log(`Setting lineage for ${tag['Product Name*']}: ${lineage} -> ${lineage.toUpperCase()}`);
          tagElement.dataset.lineage = lineage.toUpperCase();
        } else {
          console.log(`No lineage found for ${tag['Product Name*']}, using MIXED`);
          tagElement.dataset.lineage = 'MIXED';
        }
        tagElement.dataset.tagId = tag.tagId;
        tagElement.dataset.vendor = tag.vendor;
        tagElement.dataset.brand = tag.brand;
        tagElement.dataset.productType = tag.productType;
        tagElement.dataset.weight = tag.weight;

        // Make the entire tag element clickable to toggle checkbox
        tagElement.style.cursor = 'pointer';
        tagElement.addEventListener('click', (e) => {
            // Don't trigger if clicking on the checkbox itself or lineage dropdown
            if (e.target === checkbox || e.target.classList.contains('lineage-select') || 
                e.target.closest('.lineage-select')) {
                return;
            }
            // Toggle the checkbox
            checkbox.checked = !checkbox.checked;
            // Trigger the change event
            checkbox.dispatchEvent(new Event('change', { bubbles: true }));
        });

        const tagInfo = document.createElement('div');
        tagInfo.className = 'tag-info flex-grow-1 d-flex align-items-center';
        const tagName = document.createElement('div');
        tagName.className = 'tag-name d-inline-block me-2';
        // Use displayName with fallback
        let displayName = tag.displayName || tag['Product Name*'] || tag.ProductName || tag.Description || 'Unnamed Product';
        // Remove 'by ...' up to the hyphen
        let cleanedName = displayName.replace(/ by [^-]+(?= -)/i, '');
        cleanedName = cleanedName.replace(/-/g, '\u2011');
        tagName.textContent = cleanedName;
        tagInfo.appendChild(tagName);
        
        // Add JSON match indicator if this tag came from JSON matching
        if (tag.Source === 'JSON Match') {
          const jsonBadge = document.createElement('span');
          jsonBadge.className = 'badge bg-success me-2';
          jsonBadge.style.fontSize = '0.7rem';
          jsonBadge.style.padding = '2px 6px';
          jsonBadge.textContent = 'JSON';
          jsonBadge.title = 'This item was matched from JSON data';
          tagInfo.appendChild(jsonBadge);
        }
        // Create lineage dropdown
        const lineageSelect = document.createElement('select');
        lineageSelect.className = 'form-select form-select-sm lineage-select lineage-dropdown lineage-dropdown-mini';
        lineageSelect.style.height = '28px';
        lineageSelect.style.backgroundColor = 'rgba(255, 255, 255, 0.15)';
        lineageSelect.style.border = '1px solid rgba(255, 255, 255, 0.2)';
        lineageSelect.style.borderRadius = '6px';
        lineageSelect.style.cursor = 'pointer';
        lineageSelect.style.color = '#fff';
        lineageSelect.style.backdropFilter = 'blur(10px)';
        lineageSelect.style.transition = 'all 0.2s ease';
        lineageSelect.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
        // Style the dropdown options
        const style = document.createElement('style');
        style.textContent = `
            .lineage-select option {
                background-color: rgba(30, 30, 30, 0.95);
                color: #fff;
                padding: 8px;
            }
            .lineage-select:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-color: rgba(255, 255, 255, 0.3);
            }
            .lineage-select:focus {
                background-color: rgba(255, 255, 255, 0.25);
                border-color: rgba(255, 255, 255, 0.4);
                box-shadow: 0 0 0 0.2rem rgba(255, 255, 255, 0.1);
            }
        `;
        document.head.appendChild(style);
        // Add lineage options
        const uniqueLineages = [
            { value: 'SATIVA', label: 'S' },
            { value: 'INDICA', label: 'I' },
            { value: 'HYBRID', label: 'H' },
            { value: 'HYBRID/INDICA', label: 'H/I' },
            { value: 'HYBRID/SATIVA', label: 'H/S' },
            { value: 'CBD', label: 'CBD' },
            { value: 'PARA', label: 'P' },
            { value: 'MIXED', label: 'THC' }
        ];
        uniqueLineages.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.value;
            optionElement.textContent = option.label;
            if ((lineage === option.value) || (option.value === 'CBD' && lineage === 'CBD_BLEND')) {
                optionElement.selected = true;
            }
            lineageSelect.appendChild(optionElement);
        });
        lineageSelect.value = lineage;
        if (tag.productType === 'Paraphernalia' || tag['Product Type*'] === 'Paraphernalia') {
            lineageSelect.disabled = true;
            lineageSelect.style.opacity = '0.7';
        }
        lineageSelect.addEventListener('change', async (e) => {
            const newLineage = e.target.value;
            const prevValue = lineage;
            lineageSelect.disabled = true;
            // Show temporary 'Saving...' option
            const savingOption = document.createElement('option');
            savingOption.value = '';
            savingOption.textContent = 'Saving...';
            savingOption.selected = true;
            savingOption.disabled = true;
            lineageSelect.appendChild(savingOption);
            try {
                await this.updateLineageOnBackend(tag['Product Name*'], newLineage);
                // On success, update tag lineage in state
                tag.lineage = newLineage;
                tag.Lineage = newLineage;
                lineageSelect.value = newLineage;
                // Update the data-lineage attribute
                tagElement.dataset.lineage = newLineage.toUpperCase();
            } catch (err) {
                // On error, revert to previous value
                lineageSelect.value = prevValue;
                console.error('Failed to update lineage');
            } finally {
                // Remove 'Saving...' option and re-enable
                Array.from(lineageSelect.options).forEach(opt => { if (opt.textContent === 'Saving...') opt.remove(); });
                lineageSelect.disabled = false;
            }
        });
        tagElement.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            if (window.lineageEditor) {
                window.lineageEditor.openEditor(tag['Product Name*'], tag.lineage);
            }
        });
        tagInfo.appendChild(lineageSelect);
        tagElement.appendChild(checkbox);
        tagElement.appendChild(tagInfo);
        row.appendChild(tagElement);
        return row;
    },

    getLineageBadgeLabel(lineage) {
        const map = {
            'SATIVA': 'S',
            'INDICA': 'I',
            'HYBRID': 'H',
            'HYBRID/SATIVA': 'H/S',
            'HYBRID/INDICA': 'H/I',
            'CBD': 'CBD',
            'PARA': 'P',
            'MIXED': 'THC',
            'CBD_BLEND': 'CBD'
        };
        return map[(lineage || '').toUpperCase()] || '';
    },

    handleTagSelection(e, tag) {
        const isChecked = e.target.checked;
        console.log('Tag selection changed:', tag['Product Name*'], 'checked:', isChecked);
        
        if (isChecked) {
            this.state.persistentSelectedTags.add(tag['Product Name*']);
        } else {
            this.state.persistentSelectedTags.delete(tag['Product Name*']);
        }
        
        // Update the regular selectedTags set to match persistent ones
        this.state.selectedTags = new Set(this.state.persistentSelectedTags);
        
        console.log('Persistent selected tags after change:', Array.from(this.state.persistentSelectedTags));
        
        // Update the selected tags display with ALL persistent selected tags
        const selectedTagObjects = Array.from(this.state.persistentSelectedTags).map(name => {
            // First try to find in current tags (filtered view)
            let foundTag = this.state.tags.find(t => t['Product Name*'] === name);
            // If not found in current tags, try original tags
            if (!foundTag) {
                foundTag = this.state.originalTags.find(t => t['Product Name*'] === name);
            }
            return foundTag;
        }).filter(Boolean);
        
        this.updateSelectedTags(selectedTagObjects);
        
        // If tag was checked in available list, hide it from available display
        if (isChecked && e.target.closest('#availableTags')) {
            const tagElement = e.target.closest('.tag-item');
            if (tagElement) {
                tagElement.style.display = 'none';
            }
        }
        
        // If tag was unchecked in selected list, show it in available display
        if (!isChecked && e.target.closest('#selectedTags')) {
            // Find and show the tag in available list
            const availableTagElement = document.querySelector(`#availableTags .tag-checkbox[value="${tag['Product Name*']}"]`);
            if (availableTagElement) {
                const tagElement = availableTagElement.closest('.tag-item');
                if (tagElement) {
                    tagElement.style.display = 'block';
                }
            }
        }
    },

    updateTagLineage(tag, lineage) {
        // Update the lineage in the tag object
        tag.lineage = lineage;
        
        // Update the color based on the new lineage
        const newColor = this.getLineageColor(lineage);
        this.updateTagColor(tag, newColor);
    },

    handleLineageChange(tagName, newLineage) {
        const tag = this.state.tags.find(t => t['Product Name*'] === tagName);
        if (tag) {
            // Update the lineage in the tag object
            tag.lineage = newLineage;
            
            // Update the color based on the new lineage
            const newColor = this.getLineageColor(newLineage);
            this.updateTagColor(tag, newColor);
            
            // Send update to backend
            this.updateLineageOnBackend(tagName, newLineage);
        }
    },

    async updateLineageOnBackend(tagName, newLineage) {
        try {
            const payload = {
                tag_name: tagName,
                "Product Name*": tagName,
                lineage: newLineage
            };
            const response = await fetch('/api/update-lineage', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to update lineage');
            }

            // Update the tag in original tags as well
            const originalTag = this.state.originalTags.find(t => t['Product Name*'] === tagName);
            if (originalTag) {
                originalTag.lineage = newLineage;
            }

            // Refresh the tag lists in the GUI
                            this.debouncedUpdateAvailableTags(this.state.originalTags, this.state.tags);
            this.updateSelectedTags(
                Array.from(this.state.selectedTags).map(name =>
                    this.state.tags.find(t => t['Product Name*'] === name)
                ).filter(Boolean)
            );

        } catch (error) {
            console.error('Error updating lineage:', error);
            if (window.Toast) {
                console.error('Failed to update lineage:', error.message);
            }
        }
    },

    updateSelectedTags(tags) {
        if (!tags || !Array.isArray(tags)) {
            console.warn('updateSelectedTags called with invalid tags:', tags);
            tags = [];
        }
        
        console.time('updateSelectedTags');
        console.log('updateSelectedTags called with tags:', tags);
        const container = document.getElementById('selectedTags');
        if (!container) {
            console.error('Selected tags container not found');
            return;
        }

        // Clear existing content
        container.innerHTML = '';

        // For JSON matched items, we want to keep them even if they don't exist in Excel data
        // So we'll be more permissive with validation
        const validTags = [];
        const invalidTags = [];
        
        for (const tag of tags) {
            if (tag && tag['Product Name*']) {
                // Check if this tag exists in the original tags (Excel data)
                const existsInExcel = this.state.originalTags.some(excelTag => 
                    excelTag['Product Name*'] === tag['Product Name*']
                );
                
                if (existsInExcel) {
                    validTags.push(tag);
                } else {
                    // For JSON matched items, we'll keep them but mark them as "external"
                    console.log(`Tag not found in Excel data (likely JSON matched): ${tag['Product Name*']}`);
                    // Don't add to invalidTags - we'll keep these
                    validTags.push(tag);
                }
            }
        }

        // Update the regular selectedTags set to match persistent ones
        this.state.selectedTags = new Set(this.state.persistentSelectedTags);

        // Use all tags for display (including JSON matched ones)
        tags = validTags;
        
        // Apply the same filtering rules as available tags
        const currentFilters = this.state.filters || {};
        const filteredTags = tags.filter(tag => {
            // Check vendor filter - only apply if not empty and not "All"
            if (currentFilters.vendor && currentFilters.vendor.trim() !== '' && currentFilters.vendor.toLowerCase() !== 'all') {
                const tagVendor = (tag.vendor || tag['Vendor'] || '').trim();
                if (tagVendor.toLowerCase() !== currentFilters.vendor.toLowerCase()) {
                    return false;
                }
            }
            
            // Check brand filter - only apply if not empty and not "All"
            if (currentFilters.brand && currentFilters.brand.trim() !== '' && currentFilters.brand.toLowerCase() !== 'all') {
                const tagBrand = (tag.productBrand || tag['Product Brand'] || '').trim();
                if (tagBrand.toLowerCase() !== currentFilters.brand.toLowerCase()) {
                    return false;
                }
            }
            
            // Check product type filter - only apply if not empty and not "All"
            if (currentFilters.productType && currentFilters.productType.trim() !== '' && currentFilters.productType.toLowerCase() !== 'all') {
                const tagProductType = (tag.productType || tag['Product Type*'] || '').trim();
                if (tagProductType.toLowerCase() !== currentFilters.productType.toLowerCase()) {
                    return false;
                }
            }
            
            // Check lineage filter - only apply if not empty and not "All"
            if (currentFilters.lineage && currentFilters.lineage.trim() !== '' && currentFilters.lineage.toLowerCase() !== 'all') {
                const tagLineage = (tag.lineage || tag['Lineage'] || '').trim();
                if (tagLineage.toLowerCase() !== currentFilters.lineage.toLowerCase()) {
                    return false;
                }
            }
            
            // Check weight filter - only apply if not empty and not "All"
            if (currentFilters.weight && currentFilters.weight.trim() !== '' && currentFilters.weight.toLowerCase() !== 'all') {
                const tagWeightWithUnits = (tag.weightWithUnits || tag.weight || tag['Weight*'] || '').toString().trim().toLowerCase();
                const filterWeight = currentFilters.weight.toString().trim().toLowerCase();
                if (tagWeightWithUnits !== filterWeight) {
                    return false;
                }
            }
            
            return true;
        });
        
        // Use filtered tags for display
        tags = filteredTags;
        
        // Store the select all containers before clearing
        const selectAllSelectedContainer = container.querySelector('.select-all-container');
        
        // Clear existing content but preserve the select all container
        container.innerHTML = '';
        
        // Re-add the select all container if it existed
        if (selectAllSelectedContainer) {
            container.appendChild(selectAllSelectedContainer);
        } else {
            // Create select all container if it doesn't exist
            const selectAllContainer = document.createElement('div');
            selectAllContainer.className = 'd-flex align-items-center gap-3 mb-2';
            selectAllContainer.innerHTML = `
                <label class="d-flex align-items-center gap-2 cursor-pointer mb-0 select-all-container">
                    <input type="checkbox" id="selectAllSelected" class="custom-checkbox">
                    <span class="text-secondary fw-semibold">SELECT ALL</span>
                </label>
            `;
            container.appendChild(selectAllContainer);
        }

        // Add global select all checkbox
        const topSelectAll = document.getElementById('selectAllSelected');
        if (topSelectAll && !topSelectAll.hasAttribute('data-listener-added')) {
            topSelectAll.setAttribute('data-listener-added', 'true');
            topSelectAll.addEventListener('change', (e) => {
                const isChecked = e.target.checked;
                const tagCheckboxes = document.querySelectorAll('#selectedTags .tag-checkbox');
                tagCheckboxes.forEach(checkbox => {
                    checkbox.checked = isChecked;
                    const tag = this.state.tags.find(t => t['Product Name*'] === checkbox.value);
                    if (tag) {
                        if (isChecked) {
                            this.state.persistentSelectedTags.add(tag['Product Name*']);
                        } else {
                            this.state.persistentSelectedTags.delete(tag['Product Name*']);
                        }
                    }
                });
                // Update the regular selectedTags set to match persistent ones
                this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                
                this.updateSelectedTags(Array.from(this.state.persistentSelectedTags).map(name =>
                    this.state.tags.find(t => t['Product Name*'] === name)
                ).filter(Boolean));
                
                // Rebuild available tags display to reflect selection changes
                const updatedAvailableTags = this.state.originalTags.filter(tag => 
                    !this.state.persistentSelectedTags.has(tag['Product Name*'])
                );
                this._updateAvailableTags(this.state.originalTags, updatedAvailableTags);
            });
        }

        // Handle new tags being passed in (e.g., from JSON matching)
        // Add new tags to persistentSelectedTags without clearing existing ones
        if (tags.length > 0) {
            console.log('Adding new tags to persistentSelectedTags:', tags);
            tags.forEach(tag => {
                if (tag && tag['Product Name*']) {
                    this.state.persistentSelectedTags.add(tag['Product Name*']);
                }
            });
            // Update the regular selectedTags set to match persistent ones
            this.state.selectedTags = new Set(this.state.persistentSelectedTags);
        }

        // Always use ALL persistent selected tags for display, regardless of what was passed
        const allPersistentTags = Array.from(this.state.persistentSelectedTags).map(name => {
            // First try to find in current tags (filtered view)
            let foundTag = this.state.tags.find(t => t['Product Name*'] === name);
            // If not found in current tags, try original tags
            if (!foundTag) {
                foundTag = this.state.originalTags.find(t => t['Product Name*'] === name);
            }
            // If still not found, create a minimal tag object (for JSON matched items)
            if (!foundTag) {
                console.warn(`Tag not found in state: ${name}, creating minimal tag object`);
                foundTag = {
                    'Product Name*': name,
                    'Product Brand': 'Unknown',
                    'Vendor': 'Unknown',
                    'Product Type*': 'Unknown',
                    'Lineage': 'MIXED'
                };
            }
            return foundTag;
        }).filter(Boolean);

        // If no persistent tags, just return
        if (!allPersistentTags || allPersistentTags.length === 0) {
            console.log('No persistent tags to display in selected tags');
            this.updateTagCount('selected', 0);
            console.timeEnd('updateSelectedTags');
            return;
        }

        // Use the persistent tags for display
        const fullTags = allPersistentTags;

        // Organize tags into hierarchical groups
        const groupedTags = this.organizeBrandCategories(fullTags);
        console.log('Grouped tags:', groupedTags);

        // Sort vendors alphabetically
        const sortedVendors = Array.from(groupedTags.entries())
            .sort(([a], [b]) => (a || '').localeCompare(b || ''));

        // Create vendor sections
        sortedVendors.forEach(([vendor, brandGroups]) => {
            console.log('Processing vendor:', vendor, 'with brand groups:', brandGroups);
            
            const vendorSection = document.createElement('div');
            vendorSection.className = 'vendor-section mb-3';
            
            // Remove vendor label
            // Create vendor header with integrated checkbox
            const vendorHeader = document.createElement('h5');
            vendorHeader.className = 'vendor-header mb-2 d-flex align-items-center';
            
            const vendorCheckbox = document.createElement('input');
            vendorCheckbox.type = 'checkbox';
            vendorCheckbox.className = 'select-all-checkbox me-2';
            vendorCheckbox.addEventListener('change', (e) => {
                const isChecked = e.target.checked;
                // Select all descendant checkboxes (including subcategories and tags)
                const checkboxes = vendorSection.querySelectorAll('input[type="checkbox"]');
                checkboxes.forEach(checkbox => {
                    checkbox.checked = isChecked;
                    // Only update persistentSelectedTags for tag-checkboxes
                    if (checkbox.classList.contains('tag-checkbox')) {
                        const tag = this.state.tags.find(t => t['Product Name*'] === checkbox.value);
                        if (tag) {
                            if (isChecked) {
                                this.state.persistentSelectedTags.add(tag['Product Name*']);
                            } else {
                                this.state.persistentSelectedTags.delete(tag['Product Name*']);
                            }
                        }
                    }
                });
                // Update the regular selectedTags set to match persistent ones
                this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                
                this.updateSelectedTags(Array.from(this.state.persistentSelectedTags).map(name =>
                    this.state.tags.find(t => t['Product Name*'] === name)
                ).filter(Boolean));
                
                // Rebuild available tags display to reflect selection changes
                const updatedAvailableTags = this.state.originalTags.filter(tag => 
                    !this.state.persistentSelectedTags.has(tag['Product Name*'])
                );
                this._updateAvailableTags(this.state.originalTags, updatedAvailableTags);
            });
            
            vendorHeader.appendChild(vendorCheckbox);
            vendorHeader.appendChild(document.createTextNode(vendor));
            vendorSection.appendChild(vendorHeader);

            // Create brand sections
            const sortedBrands = Array.from(brandGroups.entries())
                .sort(([a], [b]) => (a || '').localeCompare(b || ''));

            sortedBrands.forEach(([brand, productTypeGroups]) => {
                const brandSection = document.createElement('div');
                brandSection.className = 'brand-section ms-3 mb-2';
                
                // Remove brand label
                // Create brand header with integrated checkbox
                const brandHeader = document.createElement('h6');
                brandHeader.className = 'brand-header mb-2 d-flex align-items-center';
                
                const brandCheckbox = document.createElement('input');
                brandCheckbox.type = 'checkbox';
                brandCheckbox.className = 'select-all-checkbox me-2';
                brandCheckbox.addEventListener('change', (e) => {
                    const isChecked = e.target.checked;
                    // Select all descendant checkboxes (including subcategories and tags)
                    const checkboxes = brandSection.querySelectorAll('input[type="checkbox"]');
                    checkboxes.forEach(checkbox => {
                        checkbox.checked = isChecked;
                        // Only update persistentSelectedTags for tag-checkboxes
                        if (checkbox.classList.contains('tag-checkbox')) {
                            const tag = this.state.tags.find(t => t['Product Name*'] === checkbox.value);
                            if (tag) {
                                if (isChecked) {
                                    this.state.persistentSelectedTags.add(tag['Product Name*']);
                                } else {
                                    this.state.persistentSelectedTags.delete(tag['Product Name*']);
                                }
                            }
                        }
                    });
                    // Update the regular selectedTags set to match persistent ones
                    this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                    
                    this.updateSelectedTags(Array.from(this.state.persistentSelectedTags).map(name =>
                        this.state.tags.find(t => t['Product Name*'] === name)
                    ).filter(Boolean));
                });
                
                brandHeader.appendChild(brandCheckbox);
                brandHeader.appendChild(document.createTextNode(brand));
                brandSection.appendChild(brandHeader);

                // Create product type sections
                const sortedProductTypes = Array.from(productTypeGroups.entries())
                    .sort(([a], [b]) => (a || '').localeCompare(b || ''));

                sortedProductTypes.forEach(([productType, weightGroups]) => {
                    const productTypeSection = document.createElement('div');
                    productTypeSection.className = 'product-type-section ms-3 mb-2';
                    
                    // Remove type label
                    // Create product type header
                    const typeHeader = document.createElement('div');
                    typeHeader.className = 'product-type-header mb-2 d-flex align-items-center';
                    
                    const productTypeCheckbox = document.createElement('input');
                    productTypeCheckbox.type = 'checkbox';
                    productTypeCheckbox.className = 'select-all-checkbox me-2';
                    productTypeCheckbox.addEventListener('change', (e) => {
                        const isChecked = e.target.checked;
                        // Select all descendant checkboxes (including subcategories and tags)
                        const checkboxes = productTypeSection.querySelectorAll('input[type="checkbox"]');
                        checkboxes.forEach(checkbox => {
                            checkbox.checked = isChecked;
                            // Only update persistentSelectedTags for tag-checkboxes
                            if (checkbox.classList.contains('tag-checkbox')) {
                                const tag = this.state.tags.find(t => t['Product Name*'] === checkbox.value);
                                if (tag) {
                                    if (isChecked) {
                                        this.state.persistentSelectedTags.add(tag['Product Name*']);
                                    } else {
                                        this.state.persistentSelectedTags.delete(tag['Product Name*']);
                                    }
                                }
                            }
                        });
                        // Update the regular selectedTags set to match persistent ones
                        this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                        
                        this.updateSelectedTags(Array.from(this.state.persistentSelectedTags).map(name =>
                            this.state.tags.find(t => t['Product Name*'] === name)
                        ).filter(Boolean));
                    });
                    
                    typeHeader.appendChild(productTypeCheckbox);
                    typeHeader.appendChild(document.createTextNode(productType));
                    productTypeSection.appendChild(typeHeader);

                    // Create weight sections
                    const sortedWeights = Array.from(weightGroups.entries())
                        .sort(([a], [b]) => (a || '').localeCompare(b || ''));

                    sortedWeights.forEach(([weight, tags]) => {
                        const weightSection = document.createElement('div');
                        weightSection.className = 'weight-section ms-3 mb-1';
                        
                        // Remove weight label
                        // Create weight header
                        const weightHeader = document.createElement('div');
                        weightHeader.className = 'weight-header mb-1 d-flex align-items-center';
                        
                        const weightCheckbox = document.createElement('input');
                        weightCheckbox.type = 'checkbox';
                        weightCheckbox.className = 'select-all-checkbox me-2';
                        weightCheckbox.addEventListener('change', (e) => {
                            const isChecked = e.target.checked;
                            // Select all descendant checkboxes (including subcategories and tags)
                            const checkboxes = weightSection.querySelectorAll('input[type="checkbox"]');
                            checkboxes.forEach(checkbox => {
                                checkbox.checked = isChecked;
                                // Only update persistentSelectedTags for tag-checkboxes
                                if (checkbox.classList.contains('tag-checkbox')) {
                                    const tag = this.state.tags.find(t => t['Product Name*'] === checkbox.value);
                                    if (tag) {
                                        if (isChecked) {
                                            this.state.persistentSelectedTags.add(tag['Product Name*']);
                                        } else {
                                            this.state.persistentSelectedTags.delete(tag['Product Name*']);
                                        }
                                    }
                                }
                            });
                            // Update the regular selectedTags set to match persistent ones
                            this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                            
                            // Update the selected tags display
                            const selectedTagObjects = Array.from(this.state.persistentSelectedTags).map(name =>
                                this.state.tags.find(t => t['Product Name*'] === name)
                            ).filter(Boolean);
                            this.updateSelectedTags(selectedTagObjects);
                            
                            // Use efficient update instead of rebuilding entire DOM
                            this.efficientlyUpdateAvailableTagsDisplay();
                        });
                        
                        weightHeader.appendChild(weightCheckbox);
                        weightHeader.appendChild(document.createTextNode(weight));
                        weightSection.appendChild(weightHeader);
                        
                        // Always render tags as leaf nodes - sort alphabetically by product name
                        if (tags && tags.length > 0) {
                            // Sort tags alphabetically by product name
                            const sortedTags = tags.sort((a, b) => {
                                const nameA = (a['Product Name*'] || a.ProductName || a.Description || '').toLowerCase();
                                const nameB = (b['Product Name*'] || b.ProductName || b.Description || '').toLowerCase();
                                return nameA.localeCompare(nameB);
                            });
                            
                            sortedTags.forEach(tag => {
                                const tagElement = this.createTagElement(tag);
                                tagElement.querySelector('.tag-checkbox').checked = this.state.persistentSelectedTags.has(tag['Product Name*']);
                                weightSection.appendChild(tagElement);
                            });
                        }
                        productTypeSection.appendChild(weightSection);
                    });

                    brandSection.appendChild(productTypeSection);
                });

                vendorSection.appendChild(brandSection);
            });

            container.appendChild(vendorSection);
        });

        this.updateTagCount('selected', fullTags.length);
        console.timeEnd('updateSelectedTags');

        // After rendering, update all select-all checkboxes to reflect the state of their descendant tag checkboxes
        // Helper to set select-all checkbox state
        function updateSelectAllCheckboxState(section) {
            const selectAll = section.querySelector('.select-all-checkbox');
            if (!selectAll) return;
            const tagCheckboxes = section.querySelectorAll('.tag-checkbox');
            if (tagCheckboxes.length === 0) {
                selectAll.checked = false;
                selectAll.indeterminate = false;
                return;
            }
            const checkedCount = Array.from(tagCheckboxes).filter(cb => cb.checked).length;
            if (checkedCount === tagCheckboxes.length) {
                selectAll.checked = true;
                selectAll.indeterminate = false;
            } else if (checkedCount === 0) {
                selectAll.checked = false;
                selectAll.indeterminate = false;
            } else {
                selectAll.checked = false;
                selectAll.indeterminate = true;
            }
        }
        // Update all group-level select all checkboxes
        container.querySelectorAll('.vendor-section, .brand-section, .product-type-section, .weight-section').forEach(section => {
            updateSelectAllCheckboxState(section);
        });
        // Update the top-level select all
        updateSelectAllCheckboxState(container);
        
        // Reinitialize drag and drop for new tags
        if (window.dragAndDropManager) {
            window.dragAndDropManager.reinitializeTagDragAndDrop();
        }
    },

    updateTagCount(type, count) {
        const countElement = document.getElementById(`${type}TagsCount`);
        if (countElement) {
            countElement.textContent = `(${count})`;
        }
    },

    addCheckboxListeners(containerId) {
        document.querySelectorAll(`${containerId} input[type="checkbox"]`).forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                if (this.checked) {
                    TagManager.state.persistentSelectedTags.add(this.value);
                } else {
                    TagManager.state.persistentSelectedTags.delete(this.value);
                }
                // Update the regular selectedTags set to match persistent ones
                TagManager.state.selectedTags = new Set(TagManager.state.persistentSelectedTags);
                TagManager.updateTagCheckboxes();
            });
        });
    },

    updateTagCheckboxes() {
        // Update available tags checkboxes
        document.querySelectorAll('#availableTags input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = TagManager.state.persistentSelectedTags.has(checkbox.value);
        });
    },

    async fetchAndUpdateAvailableTags() {
        try {
            console.log('Fetching available tags...');
            const timestamp = Date.now();
            const response = await fetch(`/api/available-tags?t=${timestamp}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const tags = await response.json();
            
            if (!tags || !Array.isArray(tags) || tags.length === 0) {
                console.error('No tags loaded from backend or invalid response format');
                return false;
            }
            
            console.log(`Fetched ${tags.length} available tags`);
            
            // Debug: Check lineage data for first few tags
            console.log('Sample lineage data:');
            tags.slice(0, 5).forEach(tag => {
                console.log(`  ${tag['Product Name*']}: lineage=${tag.lineage}, Lineage=${tag.Lineage}`);
            });
            
            this.state.tags = tags;
            this.state.originalTags = [...tags]; // Store original tags for validation
            
            // Only validate selected tags if we don't have JSON matched tags
            // This prevents clearing tags that were just added via JSON matching
            if (this.state.persistentSelectedTags.size === 0) {
                this.validateSelectedTags();
            } else {
                console.log('Skipping selected tags validation to preserve JSON matched tags');
            }
            
            this._updateAvailableTags(tags);
            return true;
        } catch (error) {
            console.error('Error fetching available tags:', error);
            return false;
        }
    },

    async fetchAndUpdateSelectedTags() {
        try {
            console.log('Fetching selected tags...');
            const timestamp = Date.now();
            const response = await fetch(`/api/selected-tags?t=${timestamp}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const selectedTags = await response.json();
            
            if (!selectedTags || !Array.isArray(selectedTags)) {
                console.warn('No selected tags found - data may not be loaded yet');
                this.updateSelectedTags([]);
                return true;
            }
            
            console.log(`Fetched ${selectedTags.length} selected tags`);
            this.updateSelectedTags(selectedTags);
            return true;
        } catch (error) {
            console.error('Error fetching selected tags:', error);
            this.updateSelectedTags([]);
            return false;
        }
    },

    async fetchAndPopulateFilters() {
        try {
            // Use the filter options API with cache refresh and timestamp to ensure updated weight formatting
            const timestamp = Date.now();
            const response = await fetch(`/api/filter-options?refresh=true&t=${timestamp}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            if (!response.ok) {
                throw new Error('Failed to fetch filter options');
            }
            const filterOptions = await response.json();
            console.log('Fetched filter options:', filterOptions);
            this.updateFilters(filterOptions);
        } catch (error) {
            console.error('Error fetching filter options:', error);
            alert('Failed to load filter options');
        }
    },

    async downloadExcel() {
        // Collect filter values from dropdowns (adjust IDs as needed)
        const filters = {
            vendor: document.getElementById('vendorFilter')?.value || null,
            brand: document.getElementById('brandFilter')?.value || null,
            productType: document.getElementById('productTypeFilter')?.value || null,
            lineage: document.getElementById('lineageFilter')?.value || null,
            weight: document.getElementById('weightFilter')?.value || null,
        };

        // Remove null/empty values
        Object.keys(filters).forEach(key => {
            if (!filters[key] || filters[key] === '') {
                delete filters[key];
            }
        });

        // Collect selected tags from the persistent selected tags
        const allTags = Array.from(this.state.persistentSelectedTags);

        try {
            const response = await fetch('/api/download-processed-excel', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    filters,
                    selected_tags: allTags
                })
            });
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to download Excel');
            }
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            // Let the server set the filename via Content-Disposition header
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error downloading Excel:', error);
            alert(error.message || 'Failed to download Excel');
        }
    },

    // Initialize the tag manager
    init() {
        console.log('TagManager initialized');
        
        // Show application splash screen
        AppLoadingSplash.show();
        AppLoadingSplash.startAutoAdvance();
        
        // Initialize empty state first
        this.initializeEmptyState();
        AppLoadingSplash.nextStep(); // Templates loaded
        
        // Check if there's already data loaded (e.g., from a previous session or default file)
        this.checkForExistingData();
        
        // Ensure all filters default to 'All' on page load
        this.state.filters = {
            vendor: 'All',
            brand: 'All',
            productType: 'All',
            lineage: 'All',
            weight: 'All'
        };
        // Set each filter dropdown to 'All' (or '')
        const filterIds = ['vendorFilter', 'brandFilter', 'productTypeFilter', 'lineageFilter', 'weightFilter'];
        filterIds.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = '';
        });
        // Show all tags by default
        this.applyFilters();
        
        // Add filter change event listeners for cascading filters after filters are populated
        setTimeout(() => {
            this.setupFilterEventListeners();
        }, 500);
        
        // Update table header if TagsTable is available
        setTimeout(() => {
            // Also update table header if TagsTable is available
            if (typeof TagsTable !== 'undefined' && TagsTable.updateTableHeader) {
                TagsTable.updateTableHeader();
            }
        }, 100);

        // JSON matching is now handled by the modal - removed old above-tags-list logic
    },

    // Show a simple loading indicator
    showLoadingIndicator() {
        const availableTagsContainer = document.getElementById('availableTags');
        if (availableTagsContainer) {
            availableTagsContainer.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2 text-muted">Loading product data...</p>
                </div>
            `;
        }
    },

    // Hide loading indicator
    hideLoadingIndicator() {
        const availableTagsContainer = document.getElementById('availableTags');
        if (availableTagsContainer) {
            // Check if we have any tags loaded
            if (this.state.tags && this.state.tags.length > 0) {
                // Data is loaded, no need to show upload prompt
                return;
            }
            
            // No data loaded, show upload prompt
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
        }
    },

    // Initialize with empty state to prevent undefined errors
    initializeEmptyState() {
        console.log('Initializing empty state...');
        
        // Initialize with empty arrays to prevent undefined errors
        this.state.tags = [];
        this.state.originalTags = [];
        this.state.selectedTags = new Set();
        this.state.persistentSelectedTags = new Set();
        
        // Clear any persistent storage
        if (window.localStorage) {
            localStorage.removeItem('selectedTags');
            localStorage.removeItem('selected_tags');
        }
        if (window.sessionStorage) {
            sessionStorage.removeItem('selectedTags');
            sessionStorage.removeItem('selected_tags');
        }
        
        // Update UI with empty state
        this.debouncedUpdateAvailableTags([], null);
        this.updateSelectedTags([]);
        
        // Initialize filters with empty options
        const emptyFilters = {
            vendor: [],
            brand: [],
            productType: [],
            lineage: [],
            weight: []
        };
        this.updateFilters(emptyFilters);
        
        console.log('Empty state initialized');
    },

    // Check if there's existing data and load it
    async checkForExistingData() {
        console.log('Checking for existing data...');
        
        try {
            // Use the new initial-data endpoint for faster loading
            const response = await fetch('/api/initial-data');
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.available_tags && Array.isArray(data.available_tags) && data.available_tags.length > 0) {
                    console.log(`Found ${data.available_tags.length} existing tags, loading data...`);
                    
                    // Update splash progress for data loading
                    AppLoadingSplash.updateProgress(60, 'Loading product data...');
                    
                    // Show action splash for initial tag population
                    this.showActionSplash('Loading product tags...');
                    
                    // Update available tags
                    AppLoadingSplash.updateProgress(75, 'Processing tags...');
                    this.debouncedUpdateAvailableTags(data.available_tags, null);
                    
                    // Don't restore selected tags on page reload - start with empty selection
                    AppLoadingSplash.updateProgress(85, 'Initializing selections...');
                    this.state.persistentSelectedTags = new Set();
                    this.state.selectedTags = new Set();
                    this.updateSelectedTags([]);
                    
                    // Update filters
                    AppLoadingSplash.updateProgress(90, 'Setting up filters...');
                    this.updateFilters(data.filters || {
                        vendor: [],
                        brand: [],
                        productType: [],
                        lineage: [],
                        weight: []
                    });
                    
                    // Update file info text to show the loaded filename
                    if (data.filename) {
                        const fileInfoText = document.getElementById('fileInfoText');
                        if (fileInfoText) {
                            fileInfoText.textContent = data.filename;
                        }
                    }
                    
                    // Complete splash loading
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                    
                    // Hide action splash after a short delay to ensure smooth transition
                    setTimeout(() => {
                        this.hideActionSplash();
                    }, 200);
                    
                    console.log('Initial data loaded successfully');
                    return;
                } else {
                    console.log('No initial data available:', data.message || 'No data found');
                    // Complete splash loading even if no data
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                }
            }
        } catch (error) {
            console.log('Error loading initial data:', error.message);
            // Complete splash loading on error
            AppLoadingSplash.stopAutoAdvance();
            AppLoadingSplash.complete();
        }
        
        console.log('No existing data found, waiting for file upload...');
        // Complete splash loading if no data found
        AppLoadingSplash.stopAutoAdvance();
        AppLoadingSplash.complete();
    },

    // Debounced version of the label generation logic
    debouncedGenerate: debounce(async function() {
        // Check if tags are loaded before attempting generation
        if (!this.state.tags || !Array.isArray(this.state.tags) || this.state.tags.length === 0) {
            console.error('Cannot generate: No tags loaded. Please upload a file first.');
            return;
        }
        
        console.time('debouncedGenerate');
        const generateBtn = document.getElementById('generateBtn');
        const splashModal = document.getElementById('generationSplashModal');
        const splashCanvas = document.getElementById('generation-splash-canvas');
        
        try {
            // Get checked tags from persistent selected tags
            const checkedTags = Array.from(this.state.persistentSelectedTags);
            if (checkedTags.length === 0) {
                console.error('Please select at least one tag to generate');
                return;
            }
            
            // Get template, scale, and format info
            const templateType = document.getElementById('templateSelect')?.value || 'horizontal';
            const scaleFactor = parseFloat(document.getElementById('scaleInput')?.value) || 1.0;
            
            // Show enhanced generation splash
            this.showEnhancedGenerationSplash(checkedTags.length, templateType);
            
            // Disable button and show loading spinner
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...';
            // Always use DOCX generation
            const apiEndpoint = '/api/generate';
            
            const response = await fetch(apiEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    selected_tags: checkedTags,
                    template_type: templateType,
                    scale_factor: scaleFactor
                })
            });
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to generate labels');
            }
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            // Let the server set the filename via Content-Disposition header
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error generating labels:', error);
        } finally {
            // Hide enhanced generation splash
            this.hideEnhancedGenerationSplash();
            generateBtn.disabled = false;
            generateBtn.innerHTML = 'Generate Tags';
            console.timeEnd('debouncedGenerate');
        }
    }, 2000), // 2-second debounce delay

    updateTagColor(tag, color) {
        const tagElement = document.querySelector(`[data-tag-id="${tag.id}"]`);
        if (tagElement) {
            // Update the color in the tag object
            tag.color = color;
            
            // Update the color in the UI
            tagElement.style.backgroundColor = color;
            
            // Update the color in the tag list
            const tagListItem = document.querySelector(`[data-tag-id="${tag.id}"]`);
            if (tagListItem) {
                tagListItem.style.backgroundColor = color;
            }
            
            // Update the color in the tag editor if it's open
            const tagEditor = document.getElementById('tagEditor');
            if (tagEditor && tagEditor.dataset.tagId === tag.id) {
                const colorInput = tagEditor.querySelector('#tagColor');
                if (colorInput) {
                    colorInput.value = color;
                }
            }
        }
    },

    getLineageColor(lineage) {
        return this.state.lineageColors[lineage] || 'var(--lineage-mixed)';
    },

    async moveToSelected() {
        // Get checked tags in availableTags
        const checked = Array.from(document.querySelectorAll('#availableTags input[type="checkbox"].tag-checkbox:checked')).map(cb => cb.value);
        if (checked.length === 0) {
            console.error('No tags selected to move');
            return;
        }
        
        try {
            // Show action splash for better UX
            this.showActionSplash('Moving tags to selected...');
            
            // Add tags to persistent selected tags (independent of filters)
            checked.forEach(tagName => {
                this.state.persistentSelectedTags.add(tagName);
            });
            
            // Update the regular selectedTags set to match persistent ones
            this.state.selectedTags = new Set(this.state.persistentSelectedTags);
            
            // Get the full tag objects for the selected tags
            const selectedTagObjects = Array.from(this.state.persistentSelectedTags).map(name =>
                this.state.tags.find(t => t['Product Name*'] === name)
            ).filter(Boolean);
            
            // Update the selected tags display
            this.updateSelectedTags(selectedTagObjects);
            
            // Hide selected tags from available tags display for better performance
            checked.forEach(tagName => {
                const tagElement = document.querySelector(`#availableTags .tag-checkbox[value="${tagName}"]`);
                if (tagElement) {
                    const tagItem = tagElement.closest('.tag-item');
                    if (tagItem) {
                        tagItem.style.display = 'none';
                    }
                }
            });
            
            // Successfully moved tags to selected
            console.log(`Moved ${checked.length} tags to selected list. Total selected: ${this.state.persistentSelectedTags.size}`);
        } catch (error) {
            console.error('Failed to move tags:', error.message);
        } finally {
            // Hide action splash
            setTimeout(() => {
                this.hideActionSplash();
            }, 300);
        }
    },

    async moveToAvailable() {
        // Get checked tags in selectedTags
        const checked = Array.from(document.querySelectorAll('#selectedTags input[type="checkbox"].tag-checkbox:checked')).map(cb => cb.value);
        if (checked.length === 0) {
            console.error('No tags selected to move');
            return;
        }
        
        try {
            // Show action splash for better UX
            this.showActionSplash('Moving tags to available...');
            
            // Remove tags from persistent selected tags
            checked.forEach(tagName => {
                this.state.persistentSelectedTags.delete(tagName);
            });
            
            // Update the regular selectedTags set to match persistent ones
            this.state.selectedTags = new Set(this.state.persistentSelectedTags);
            
            // Get the full tag objects for the remaining selected tags
            const selectedTagObjects = Array.from(this.state.persistentSelectedTags).map(name =>
                this.state.tags.find(t => t['Product Name*'] === name)
            ).filter(Boolean);
            
            // Update the selected tags display
            this.updateSelectedTags(selectedTagObjects);
            
            // Get the tag objects for the moved back tags and add them to available tags
            const movedBackTags = checked.map(tagName => 
                this.state.originalTags.find(t => t['Product Name*'] === tagName)
            ).filter(Boolean);
            
            // Show moved back tags in available tags display for better performance
            checked.forEach(tagName => {
                const tagElement = document.querySelector(`#availableTags .tag-checkbox[value="${tagName}"]`);
                if (tagElement) {
                    const tagItem = tagElement.closest('.tag-item');
                    if (tagItem) {
                        tagItem.style.display = 'block';
                    }
                }
            });
            
            // Successfully moved tags to available
            console.log(`Moved ${checked.length} tags to available list. Total selected: ${this.state.persistentSelectedTags.size}`);
        } catch (error) {
            console.error('Failed to move tags:', error.message);
        } finally {
            // Hide action splash
            setTimeout(() => {
                this.hideActionSplash();
            }, 300);
        }
    },

    // Helper functions removed - now using _updateAvailableTags for proper tag management

    async undoMove() {
        try {
            // Show loading splash
            this.showActionSplash('Undoing last action...');
            
            // Call the backend API to undo the last move
            const response = await fetch('/api/undo-move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    // Update the persistent selected tags with the restored state
                    this.state.persistentSelectedTags = new Set(data.selected_tags);
                    this.state.selectedTags = new Set(data.selected_tags);
                    
                    // Update the selected tags display immediately
                    this.updateSelectedTags(data.selected_tags.map(tagName => 
                        this.state.tags.find(t => t['Product Name*'] === tagName)
                    ).filter(Boolean));
                    
                    // Update available tags with optimized approach
                    this.updateAvailableTagsOptimized(data.available_tags);
                    
                    console.log('Undo completed - restored previous state');
                } else {
                    console.error('Failed to undo move:', data.error);
                }
            } else {
                const errorData = await response.json();
                if (response.status === 400 && errorData.error === 'Nothing to undo') {
                    console.log('Nothing to undo');
                } else {
                    console.error('Failed to undo move on server:', errorData.error);
                }
            }
        } catch (error) {
            console.error('Failed to undo move:', error.message);
        } finally {
            // Hide loading splash
            this.hideActionSplash();
        }
    },

    async clearSelected() {
        try {
            // Show loading splash
            this.showActionSplash('Clearing selected tags...');
            
            // Call the backend API to clear selected tags
            const response = await fetch('/api/clear-filters', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Clear persistent selected tags
                this.state.persistentSelectedTags.clear();
                this.state.selectedTags.clear();
                
                // Update the selected tags display immediately
                this.updateSelectedTags([]);
                
                // Update available tags with optimized approach
                this.updateAvailableTagsOptimized(data.available_tags || this.state.originalTags);
                
                console.log('Cleared all selected tags');
            } else {
                console.error('Failed to clear selected tags on server');
            }
        } catch (error) {
            console.error('Failed to clear selected tags:', error.message);
        } finally {
            // Hide loading splash
            this.hideActionSplash();
        }
    },

    showExcelLoadingSplash(filename) {
        const splash = document.getElementById('excelLoadingSplash');
        const filenameElement = document.getElementById('excelLoadingFilename');
        const statusElement = document.getElementById('excelLoadingStatus');
        const progressFill = document.getElementById('excelLoadingFill');
        
        if (splash && filenameElement && statusElement && progressFill) {
            filenameElement.textContent = filename;
            statusElement.textContent = 'Initializing...';
            progressFill.style.width = '0%';
            splash.style.display = 'flex';
            
            // Start progress animation
            this.excelLoadingProgress = 0;
            this.excelLoadingInterval = setInterval(() => {
                this.excelLoadingProgress += Math.random() * 15;
                if (this.excelLoadingProgress > 90) {
                    this.excelLoadingProgress = 90; // Don't go to 100% until actually done
                }
                progressFill.style.width = this.excelLoadingProgress + '%';
            }, 500);
        }
    },

    hideExcelLoadingSplash() {
        const splash = document.getElementById('excelLoadingSplash');
        const progressFill = document.getElementById('excelLoadingFill');
        
        if (splash && progressFill) {
            // Complete the progress bar
            progressFill.style.width = '100%';
            
            // Clear the progress interval
            if (this.excelLoadingInterval) {
                clearInterval(this.excelLoadingInterval);
                this.excelLoadingInterval = null;
            }
            
            // Hide splash after a short delay
            setTimeout(() => {
                splash.style.display = 'none';
                progressFill.style.width = '0%';
            }, 500);
        }
    },

    updateExcelLoadingStatus(status) {
        const statusElement = document.getElementById('excelLoadingStatus');
        if (statusElement) {
            statusElement.textContent = status;
        }
    },

    // Action splash screen for clear/undo operations
    showActionSplash(message) {
        // Create splash if it doesn't exist
        let splash = document.getElementById('actionSplash');
        if (!splash) {
            splash = document.createElement('div');
            splash.id = 'actionSplash';
            splash.className = 'action-splash';
            splash.innerHTML = `
                <div class="action-splash-content">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <div class="action-splash-message">${message}</div>
                </div>
            `;
            document.body.appendChild(splash);
        } else {
            const messageElement = splash.querySelector('.action-splash-message');
            if (messageElement) {
                messageElement.textContent = message;
            }
        }
        
        splash.style.display = 'flex';
    },

    hideActionSplash() {
        const splash = document.getElementById('actionSplash');
        if (splash) {
            splash.style.display = 'none';
        }
    },

    showEnhancedGenerationSplash(labelCount, templateType) {
        const splashModal = document.getElementById('generationSplashModal');
        const splashCanvas = document.getElementById('generation-splash-canvas');
        
        if (!splashModal || !splashCanvas) {
            console.warn('Generation splash elements not found');
            return;
        }
        
        // Show the modal
        splashModal.style.display = 'flex';
        
        // Set up canvas
        splashCanvas.width = 500;
        splashCanvas.height = 350;
        const ctx = splashCanvas.getContext('2d');
        
        if (!ctx) {
            console.warn('Canvas context not available');
            return;
        }
        
        // Start animation
        let frame = 0;
        let progress = 0;
        const totalFrames = 300; // 5 seconds at 60fps
        
        const animate = () => {
            // Clear canvas
            ctx.clearRect(0, 0, splashCanvas.width, splashCanvas.height);
            
            // Draw background gradient
            const gradient = ctx.createLinearGradient(0, 0, 0, splashCanvas.height);
            gradient.addColorStop(0, 'rgba(30, 20, 40, 0.95)');
            gradient.addColorStop(1, 'rgba(50, 30, 70, 0.95)');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, splashCanvas.width, splashCanvas.height);
            
            // Draw animated background pattern
            for (let i = 0; i < 20; i++) {
                const x = (frame * 0.5 + i * 30) % (splashCanvas.width + 60) - 30;
                const y = (i * 25) % splashCanvas.height;
                const size = 2 + Math.sin(frame * 0.1 + i) * 1;
                
                ctx.fillStyle = `rgba(160, 132, 232, ${0.1 + Math.sin(frame * 0.05 + i) * 0.05})`;
                ctx.beginPath();
                ctx.arc(x, y, size, 0, Math.PI * 2);
                ctx.fill();
            }
            
            // Draw title
            ctx.fillStyle = '#a084e8';
            ctx.font = 'bold 28px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('LABEL MAKER', splashCanvas.width / 2, 80);
            
            // Draw subtitle
            ctx.fillStyle = '#ffffff';
            ctx.font = '18px Arial';
            ctx.fillText('Generating Labels...', splashCanvas.width / 2, 120);
            
            // Draw animated dots
            const dots = '...';
            const dotOffset = Math.sin(frame * 0.2) * 5;
            ctx.fillText(dots, splashCanvas.width / 2 + 140 + dotOffset, 120);
            
            // Draw progress bar background
            ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
            ctx.fillRect(50, 200, splashCanvas.width - 100, 20);
            
            // Draw progress bar fill
            progress = Math.min(frame / totalFrames, 1);
            const progressWidth = (splashCanvas.width - 100) * progress;
            
            const progressGradient = ctx.createLinearGradient(50, 200, 50 + progressWidth, 200);
            progressGradient.addColorStop(0, '#667eea');
            progressGradient.addColorStop(1, '#764ba2');
            ctx.fillStyle = progressGradient;
            ctx.fillRect(50, 200, progressWidth, 20);
            
            // Draw progress text
            ctx.fillStyle = '#ffffff';
            ctx.font = '14px Arial';
            ctx.fillText(`${Math.round(progress * 100)}%`, splashCanvas.width / 2, 240);
            
            // Draw details
            ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
            ctx.font = '12px Arial';
            ctx.fillText(`Template: ${templateType.toUpperCase()}`, splashCanvas.width / 2, 270);
            ctx.fillText(`Labels: ${labelCount}`, splashCanvas.width / 2, 285);
            
            // Draw animated border
            const borderProgress = (frame * 0.02) % 1;
            ctx.strokeStyle = '#a084e8';
            ctx.lineWidth = 2;
            ctx.setLineDash([10, 5]);
            ctx.lineDashOffset = -frame * 0.5;
            ctx.strokeRect(10, 10, splashCanvas.width - 20, splashCanvas.height - 20);
            
            frame++;
            
            // Continue animation if modal is still visible
            if (splashModal.style.display !== 'none') {
                requestAnimationFrame(animate);
            }
        };
        
        // Start the animation
        animate();
        
        // Store animation reference for cleanup
        this._generationAnimation = animate;
    },

    hideEnhancedGenerationSplash() {
        const splashModal = document.getElementById('generationSplashModal');
        if (splashModal) {
            splashModal.style.display = 'none';
        }
        
        // Clear animation reference
        this._generationAnimation = null;
    },

    // Optimized version of updateAvailableTags that skips complex DOM manipulation
    updateAvailableTagsOptimized(availableTags) {
        if (!availableTags || !Array.isArray(availableTags)) {
            console.warn('updateAvailableTagsOptimized called with invalid availableTags:', availableTags);
            return;
        }
        
        console.time('updateAvailableTagsOptimized');
        
        // Show action splash for optimized tag updates
        this.showActionSplash('Updating tags...');
        
        // Use requestAnimationFrame for smooth performance
        requestAnimationFrame(() => {
            // Filter out selected tags from available tags for better UX
            const selectedTagNames = new Set(this.state.persistentSelectedTags);
            const filteredAvailableTags = availableTags.filter(tag => !selectedTagNames.has(tag['Product Name*']));
            
            // Update state with filtered tags
            this.state.tags = [...filteredAvailableTags];
            
            // Rebuild the available tags display with filtered tags
            this._updateAvailableTags(this.state.originalTags, filteredAvailableTags);
            
            console.timeEnd('updateAvailableTagsOptimized');
            
            // Hide splash after a short delay
            setTimeout(() => {
                this.hideActionSplash();
            }, 50);
        });
    },

    // Efficient helper to update available tags display without DOM rebuilding
    efficientlyUpdateAvailableTagsDisplay() {
        const selectedTagNames = new Set(this.state.persistentSelectedTags);
        const availableTagElements = document.querySelectorAll('#availableTags .tag-item');
        
        availableTagElements.forEach(tagElement => {
            const checkbox = tagElement.querySelector('.tag-checkbox');
            if (checkbox) {
                const tagName = checkbox.value;
                if (selectedTagNames.has(tagName)) {
                    tagElement.style.display = 'none';
                } else {
                    tagElement.style.display = 'block';
                }
            }
        });
        
        // Update select all checkbox states after hiding/showing tags
        this.updateSelectAllCheckboxes();
    },

    // Update select all checkboxes state
    updateSelectAllCheckboxes() {
        const availableCheckboxes = document.querySelectorAll('#availableTags .tag-checkbox:not([style*="display: none"])');
        const checkedCheckboxes = document.querySelectorAll('#availableTags .tag-checkbox:checked:not([style*="display: none"])');
        
        // Update global select all
        const selectAllAvailable = document.getElementById('selectAllAvailable');
        if (selectAllAvailable && availableCheckboxes.length > 0) {
            selectAllAvailable.checked = checkedCheckboxes.length === availableCheckboxes.length;
            selectAllAvailable.indeterminate = checkedCheckboxes.length > 0 && checkedCheckboxes.length < availableCheckboxes.length;
        }
        
        // Update vendor and brand select all checkboxes
        const vendorSections = document.querySelectorAll('#availableTags .vendor-section');
        vendorSections.forEach(vendorSection => {
            const vendorCheckboxes = vendorSection.querySelectorAll('.tag-checkbox:not([style*="display: none"])');
            const vendorChecked = vendorSection.querySelectorAll('.tag-checkbox:checked:not([style*="display: none"])');
            const vendorSelectAll = vendorSection.querySelector('.select-all-checkbox');
            
            if (vendorSelectAll && vendorCheckboxes.length > 0) {
                vendorSelectAll.checked = vendorChecked.length === vendorCheckboxes.length;
                vendorSelectAll.indeterminate = vendorChecked.length > 0 && vendorChecked.length < vendorCheckboxes.length;
            }
        });
        
        const brandSections = document.querySelectorAll('#availableTags .brand-section');
        brandSections.forEach(brandSection => {
            const brandCheckboxes = brandSection.querySelectorAll('.tag-checkbox:not([style*="display: none"])');
            const brandChecked = brandSection.querySelectorAll('.tag-checkbox:checked:not([style*="display: none"])');
            const brandSelectAll = brandSection.querySelector('.select-all-checkbox');
            
            if (brandSelectAll && brandCheckboxes.length > 0) {
                brandSelectAll.checked = brandChecked.length === brandCheckboxes.length;
                brandSelectAll.indeterminate = brandChecked.length > 0 && brandChecked.length < brandCheckboxes.length;
            }
        });
    },

    async uploadFile(file) {
        const maxRetries = 2;
        let retryCount = 0;
        
        while (retryCount <= maxRetries) {
            try {
                console.log(`Starting file upload (attempt ${retryCount + 1}):`, file.name, 'Size:', file.size, 'bytes');
                
                // Show Excel loading splash screen
                this.showExcelLoadingSplash(file.name);
                
                // Show loading state
                this.updateUploadUI(`Uploading ${file.name}...`);
                
                const formData = new FormData();
                formData.append('file', file);
                
                console.log('Sending upload request...');
                
                // Create AbortController for timeout
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
                
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData,
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                console.log('Upload response status:', response.status);
                
                let data;
                try {
                    data = await response.json();
                    console.log('Upload response data:', data);
                } catch (jsonError) {
                    console.error('Error parsing JSON response:', jsonError);
                    throw new Error('Invalid server response');
                }
                
                if (response.ok && data.filename) {
                    // Poll for processing status
                    this.updateUploadUI(`Processing ${file.name}...`);
                    await this.pollUploadStatusAndUpdateUI(data.filename, file.name);
                    return; // Success, exit retry loop
                } else if (response.ok) {
                    // Fallback for legacy response
                    this.updateUploadUI(file.name, 'File uploaded successfully', 'success');
                    // File uploaded successfully
                    return; // Success, exit retry loop
                } else {
                    console.error('Upload failed:', data.error);
                    this.hideExcelLoadingSplash();
                    this.updateUploadUI('No file selected');
                    console.error('Upload failed:', data.error);
                    return; // Don't retry on server errors
                }
            } catch (error) {
                console.error(`Upload error (attempt ${retryCount + 1}):`, error);
                
                if (retryCount === maxRetries) {
                    // Final attempt failed
                    this.hideExcelLoadingSplash();
                    this.updateUploadUI('No file selected');
                    let errorMessage = 'Upload failed';
                    if (error.name === 'AbortError') {
                        errorMessage = 'Upload timed out - please try again';
                    } else if (error.message.includes('Failed to fetch')) {
                        errorMessage = 'Network error - please check your connection';
                    } else if (error.message.includes('Invalid server response')) {
                        errorMessage = 'Server error - please try again';
                    } else if (error.message) {
                        errorMessage = error.message;
                    }
                    console.error('Upload error:', errorMessage);
                    return;
                } else {
                    // Retry after a short delay
                    console.log(`Retrying upload in 2 seconds... (${retryCount + 1}/${maxRetries})`);
                    this.updateUploadUI(`Retrying upload... (${retryCount + 1}/${maxRetries})`);
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
            }
            
            retryCount++;
        }
    },

    async pollUploadStatusAndUpdateUI(filename, displayName) {
        console.log(`Polling upload status for: ${filename}`);
        
        const maxAttempts = 120; // 6 minutes max (3 seconds * 120 = 6 minutes)
        let attempts = 0;
        let consecutiveErrors = 0;
        const maxConsecutiveErrors = 3;
        
        while (attempts < maxAttempts) {
            try {
                const response = await fetch(`/api/upload-status?filename=${encodeURIComponent(filename)}`);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                const status = data.status;
                const age = data.age_seconds || 0;
                const totalFiles = data.total_processing_files || 0;
                
                console.log(`Upload status: ${status} (age: ${age}s, total files: ${totalFiles})`);
                consecutiveErrors = 0; // Reset error counter on successful response
                
                if (status === 'ready' || status === 'done') {
                    // File is ready for basic operations
                    this.hideExcelLoadingSplash();
                    this.updateUploadUI(displayName, 'File ready!', 'success');
                    // Toast.show('success', 'File uploaded and ready!'); // Removed notification
                    
                    // Load the data - ensure all operations complete successfully
                    // Force a small delay to ensure backend processing is complete
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    
                    // Show action splash for upload completion
                    this.showActionSplash('Finalizing upload...');
                    
                    // Clear any cached data to force fresh data from backend
                    try {
                        await fetch('/api/clear-cache', { method: 'POST' });
                        console.log('Cleared backend cache after upload');
                    } catch (cacheError) {
                        console.warn('Failed to clear cache:', cacheError);
                    }
                    
                    const availableTagsLoaded = await this.fetchAndUpdateAvailableTags();
                    const selectedTagsLoaded = await this.fetchAndUpdateSelectedTags();
                    await this.fetchAndPopulateFilters();
                    
                    // Force refresh lineage colors by re-rendering tags
                    if (availableTagsLoaded && this.state.tags && this.state.tags.length > 0) {
                        console.log('Forcing lineage color refresh after upload...');
                        this._updateAvailableTags(this.state.tags);
                    }
                    
                    if (!availableTagsLoaded) {
                        console.error('Failed to load available tags after upload');
                        console.error('Failed to load product data. Please try refreshing the page.');
                        return;
                    }
                    
                    console.log('Upload processing complete');
                    return;
                } else if (status === 'processing') {
                    // Still processing, show progress
                    this.updateUploadUI(`Processing ${displayName}...`);
                    this.updateExcelLoadingStatus('Processing Excel data...');
                    
                } else if (status === 'not_found') {
                    // File not found in processing status - might be a race condition
                    console.warn(`File not found in processing status: ${filename} (age: ${age}s, total files: ${totalFiles})`);
                    
                    // If we've had a successful 'ready' status before, the file might have been processed
                    // Try to load the data anyway to see if it's available
                    if (attempts > 5) {
                        console.log('Attempting to load data despite not_found status...');
                        try {
                            const availableTagsLoaded = await this.fetchAndUpdateAvailableTags();
                            if (availableTagsLoaded && this.state.tags && this.state.tags.length > 0) {
                                console.log('Data loaded successfully despite not_found status');
                                this.hideExcelLoadingSplash();
                                this.updateUploadUI(displayName, 'File ready!', 'success');
                                return;
                            }
                        } catch (loadError) {
                            console.warn('Failed to load data despite not_found status:', loadError);
                        }
                    }
                    
                    if (attempts < 20) { // Give it more attempts for race conditions (increased from 15)
                        this.updateUploadUI(`Processing ${displayName}...`);
                        this.updateExcelLoadingStatus('Waiting for processing to start...');
                    } else {
                        this.hideExcelLoadingSplash();
                        this.updateUploadUI('Upload failed', 'File processing status lost', 'error');
                        console.error('Upload failed: Processing status lost. Please try again.');
                        return;
                    }
                    
                } else {
                    console.warn(`Unknown status: ${status}`);
                }
                
            } catch (error) {
                console.error('Error polling upload status:', error);
                consecutiveErrors++;
                
                if (consecutiveErrors >= maxConsecutiveErrors) {
                    this.hideExcelLoadingSplash();
                    this.updateUploadUI('Upload failed', 'Network error', 'error');
                    console.error('Upload failed: Network error. Please try again.');
                    return;
                }
                
                // Continue polling but with longer delay on errors
                await new Promise(resolve => setTimeout(resolve, 3000));
                continue;
            }
            
            attempts++;
            await new Promise(resolve => setTimeout(resolve, 3000)); // Poll every 3 seconds
        }
        
        // Timeout
        this.hideExcelLoadingSplash();
        this.updateUploadUI('Upload timed out', 'Processing took too long', 'error');
                            console.error('Upload timed out. Please try again.');
    },

    updateUploadUI(fileName, statusMessage, statusType) {
        const currentFileInfo = document.getElementById('currentFileInfo');
        const fileInfoText = document.getElementById('fileInfoText');
        
        if (currentFileInfo) {
            // Keep the default filename instead of showing the uploaded file name
            // Only show status messages, not the uploaded filename
            if (statusMessage && statusType) {
                // Show status message temporarily
                const originalText = currentFileInfo.textContent;
                currentFileInfo.textContent = statusMessage;
                currentFileInfo.classList.add(statusType);
                setTimeout(() => {
                    currentFileInfo.textContent = originalText;
                    currentFileInfo.classList.remove(statusType);
                }, 3000);
            } else if (statusMessage && !statusType) {
                // This is likely an error or "No file selected" message
                currentFileInfo.textContent = statusMessage;
            }
            // Don't update the filename for successful uploads - keep the default filename
        }
        
        // Update the file info text if a filename is provided
        if (fileName && fileInfoText) {
            fileInfoText.textContent = fileName;
        }
    },

    moveToSelected: function(tagsToMove) {
        tagsToMove.forEach(tag => {
            // Remove from available, add to selected
            // (implement your logic here)
            this.state.selectedTags.add(tag);
            // Optionally, remove from availableTags set/list
        });
        // Refresh UI
        this.fetchAndUpdateAvailableTags();
        this.fetchAndUpdateSelectedTags();
    },

    onTagsLoaded: function(tags) {
        TagsTable.updateTagsList('availableTags', tags);
        autocheckAllAvailableTags();
    },

    setupFilterEventListeners() {
        const filterIds = ['vendorFilter', 'brandFilter', 'productTypeFilter', 'lineageFilter', 'weightFilter'];
        
        console.log('Setting up filter event listeners...');
        
        // Create a debounced version of the filter update function
        const debouncedFilterUpdate = debounce(async (filterType, value) => {
            console.log('Filter changed:', filterType, value);
            
            // Update table header if TagsTable is available
            if (filterType === 'productType' && typeof TagsTable !== 'undefined' && TagsTable.updateTableHeader) {
                TagsTable.updateTableHeader();
            }
            
            // Update filter options for cascading behavior
            await this.updateFilterOptions();
            
            // Apply the filters to the tag lists
            this.applyFilters();
            this.renderActiveFilters();
        }, 150); // 150ms debounce delay
        
        filterIds.forEach(filterId => {
            const filterElement = document.getElementById(filterId);
            console.log(`Filter element ${filterId}:`, filterElement);
            
            if (filterElement) {
                filterElement.addEventListener('change', (event) => {
                    const filterType = this.getFilterTypeFromId(filterId);
                    const value = event.target.value;
                    
                    // For immediate feedback, apply filters right away
                    this.applyFilters();
                    
                    // Then debounce the cascading filter updates
                    debouncedFilterUpdate(filterType, value);
                });
                console.log(`Event listener attached to ${filterId}`);
            } else {
                console.warn(`Filter element ${filterId} not found`);
            }
        });
    },

    getFilterTypeFromId(filterId) {
        const idToType = {
            'vendorFilter': 'vendor',
            'brandFilter': 'brand',
            'productTypeFilter': 'productType',
            'lineageFilter': 'lineage',
            'weightFilter': 'weight'
        };
        return idToType[filterId] || filterId;
    },

    // Add this function to render active filters above the Available list
    renderActiveFilters() {
        const filterIds = [
            { id: 'vendorFilter', label: 'Vendor' },
            { id: 'brandFilter', label: 'Brand' },
            { id: 'productTypeFilter', label: 'Type' },
            { id: 'lineageFilter', label: 'Lineage' },
            { id: 'weightFilter', label: 'Weight' }
        ];
        let container = document.getElementById('activeFiltersContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'activeFiltersContainer';
            container.style.display = 'flex';
            container.style.gap = '0.5rem';
            container.style.marginBottom = '0.5rem';
            container.style.alignItems = 'center';
            container.style.flexWrap = 'wrap';
            const availableTags = document.getElementById('availableTags');
            if (availableTags && availableTags.parentNode) {
                availableTags.parentNode.insertBefore(container, availableTags);
            }
        }
        container.innerHTML = '';
        
        // Add "Clear All Filters" button if any filters are active
        const activeFilters = filterIds.filter(({ id }) => {
            const select = document.getElementById(id);
            return select && select.value && select.value !== '' && select.value.toLowerCase() !== 'all';
        });
        
        if (activeFilters.length > 0) {
            const clearAllBtn = document.createElement('button');
            clearAllBtn.textContent = 'Clear All Filters';
            clearAllBtn.style.background = 'rgba(255,255,255,0.1)';
            clearAllBtn.style.border = '1px solid rgba(255,255,255,0.3)';
            clearAllBtn.style.borderRadius = '6px';
            clearAllBtn.style.padding = '4px 8px';
            clearAllBtn.style.fontSize = '0.8em';
            clearAllBtn.style.color = '#fff';
            clearAllBtn.style.cursor = 'pointer';
            clearAllBtn.style.marginRight = '0.5rem';
            clearAllBtn.addEventListener('click', () => {
                this.clearAllFilters();
            });
            container.appendChild(clearAllBtn);
        }
        
        filterIds.forEach(({ id, label }) => {
            const select = document.getElementById(id);
            if (select && select.value && select.value !== '' && select.value.toLowerCase() !== 'all') {
                const filterDiv = document.createElement('div');
                filterDiv.style.display = 'flex';
                filterDiv.style.alignItems = 'center';
                filterDiv.style.background = 'rgba(255,255,255,0.08)';
                filterDiv.style.borderRadius = '8px';
                filterDiv.style.padding = '2px 8px';
                filterDiv.style.fontSize = '0.85em';
                filterDiv.style.color = '#fff';
                filterDiv.style.fontWeight = '500';
                filterDiv.style.gap = '0.25em';
                filterDiv.innerHTML = `${label}: ${select.value}`;
                const closeBtn = document.createElement('span');
                closeBtn.textContent = '×';
                closeBtn.style.cursor = 'pointer';
                closeBtn.style.marginLeft = '4px';
                closeBtn.style.fontSize = '1em';
                closeBtn.setAttribute('aria-label', `Clear ${label} filter`);
                closeBtn.addEventListener('click', () => {
                    select.value = '';
                    // Trigger change event to update filters
                    select.dispatchEvent(new Event('change', { bubbles: true }));
                });
                filterDiv.appendChild(closeBtn);
                container.appendChild(filterDiv);
            }
        });
    },

    // Add function to clear all filters at once
    clearAllFilters() {
        console.log('Clearing all filters...');
        
        const filterIds = ['vendorFilter', 'brandFilter', 'productTypeFilter', 'lineageFilter', 'weightFilter'];
        
        // Clear each filter dropdown
        filterIds.forEach(filterId => {
            const filterElement = document.getElementById(filterId);
            if (filterElement) {
                filterElement.value = '';
            }
        });
        
        // Apply the cleared filters
        this.applyFilters();
        this.renderActiveFilters();
        
        // Show success message
        if (window.Toast) {
            window.Toast.show('All filters cleared successfully', 'success');
        }
        
        // Add visual feedback to the button
        const clearBtn = document.getElementById('clearFiltersBtn');
        if (clearBtn) {
            clearBtn.style.transform = 'scale(0.95)';
            setTimeout(() => {
                clearBtn.style.transform = 'scale(1)';
            }, 150);
        }
        
        console.log('All filters cleared successfully');
    },

    // Emergency function to clear stuck upload UI
    forceClearUploadUI() {
        console.log('Force clearing upload UI state...');
        
        // Hide any loading splash
        this.hideExcelLoadingSplash();
        
        // Clear the file info display
        const currentFileInfo = document.getElementById('currentFileInfo');
        const fileInfoText = document.getElementById('fileInfoText');
        
        if (currentFileInfo) {
            currentFileInfo.textContent = 'No file selected';
            currentFileInfo.className = ''; // Remove any status classes
        }
        
        if (fileInfoText) {
            fileInfoText.textContent = '';
        }
        
        // Force refresh the data
        this.fetchAndUpdateAvailableTags();
        this.fetchAndUpdateSelectedTags();
        this.fetchAndPopulateFilters();
        
        console.log('Upload UI state cleared');
    },

    // Validate and clean up selected tags against current Excel data
    validateSelectedTags() {
        // Add safeguard to prevent clearing tags that were just added via JSON matching
        const hasJsonMatchedTags = this.state.persistentSelectedTags.size > 0;
        
        if (!this.state.originalTags || this.state.originalTags.length === 0) {
            // No Excel data loaded, but don't clear if we have JSON matched tags
            if (!hasJsonMatchedTags) {
                this.state.persistentSelectedTags.clear();
                this.state.selectedTags.clear();
            } else {
                console.log('Preserving JSON matched tags even though no Excel data is loaded yet');
            }
            return;
        }

        // Create case-insensitive lookup maps
        const validProductNamesLower = new Map();
        this.state.originalTags.forEach(tag => {
            const name = tag['Product Name*'];
            if (name) {
                validProductNamesLower.set(name.toLowerCase(), name); // Store original case
            }
        });

        const invalidTags = [];
        const validTags = [];
        const correctedTags = new Set();

        // Check each selected tag with case-insensitive comparison
        for (const tagName of this.state.persistentSelectedTags) {
            const tagNameLower = tagName.toLowerCase();
            const originalName = validProductNamesLower.get(tagNameLower);
            
            if (originalName) {
                // Tag exists, use the original case from Excel data
                validTags.push(originalName);
                correctedTags.add(originalName);
            } else {
                invalidTags.push(tagName);
            }
        }

        // Only clear and update if we actually found invalid tags
        if (invalidTags.length > 0) {
            // Remove invalid tags and update with corrected case
            this.state.persistentSelectedTags.clear();
            correctedTags.forEach(tagName => {
                this.state.persistentSelectedTags.add(tagName);
            });

            // Update the regular selectedTags set
            this.state.selectedTags = new Set(this.state.persistentSelectedTags);

            // Show warning if invalid tags were found
            console.warn(`Removed ${invalidTags.length} tags that don't exist in current Excel data:`, invalidTags);
            if (window.Toast) {
                window.Toast.show(`Removed ${invalidTags.length} tags that don't exist in current data`, 'warning');
            }

            // Update the UI to reflect the cleaned selections
            const validTagObjects = validTags.map(name => 
                this.state.originalTags.find(t => t['Product Name*'] === name)
            ).filter(Boolean);
            
            this.updateSelectedTags(validTagObjects);
        }
    },
};

// Expose TagManager to global scope
window.TagManager = TagManager;
window.updateAvailableTags = TagManager.debouncedUpdateAvailableTags.bind(TagManager);
window.updateFilters = TagManager.updateFilters.bind(TagManager);

function attachSelectedTagsCheckboxListeners() {
    const container = document.getElementById('selectedTags');
    if (!container) return;

    // Parent checkboxes
    container.querySelectorAll('.select-all-checkbox').forEach(parentCheckbox => {
        parentCheckbox.disabled = false;
        const newCheckbox = parentCheckbox.cloneNode(true);
        parentCheckbox.parentNode.replaceChild(newCheckbox, parentCheckbox);

        newCheckbox.addEventListener('change', function(e) {
            console.log('Parent checkbox clicked in selected tags', this);
            const isChecked = e.target.checked;
            // Find the closest section (vendor, brand, product type, or weight)
            const parentSection = newCheckbox.closest('.vendor-section, .brand-section, .product-type-section, .weight-section');
            if (!parentSection) {
                console.warn('No parent section found for parent checkbox in selected tags', this);
                return;
            }
            const checkboxes = parentSection.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
                if (checkbox.classList.contains('tag-checkbox')) {
                    const tag = TagManager.state.tags.find(t => t['Product Name*'] === checkbox.value);
                    if (tag) {
                        if (isChecked) {
                            TagManager.state.selectedTags.add(tag['Product Name*']);
                        } else {
                            TagManager.state.selectedTags.delete(tag['Product Name*']);
                        }
                    }
                }
            });
            TagManager.updateSelectedTags(Array.from(TagManager.state.selectedTags).map(name =>
                TagManager.state.tags.find(t => t['Product Name*'] === name)
            ));
        });
        console.log('Attached parent checkbox listener in selected tags', newCheckbox);
    });

    // Child tag checkboxes
    container.querySelectorAll('input[type="checkbox"].tag-checkbox').forEach(checkbox => {
        const newCheckbox = checkbox.cloneNode(true);
        checkbox.parentNode.replaceChild(newCheckbox, checkbox);

        newCheckbox.addEventListener('change', function() {
            if (this.checked) {
                TagManager.state.selectedTags.add(this.value);
            } else {
                TagManager.state.selectedTags.delete(this.value);
            }
            // Only update selected tags panel
            TagManager.updateSelectedTags(Array.from(TagManager.state.selectedTags).map(name =>
                TagManager.state.tags.find(t => t['Product Name*'] === name)
            ));
        });
    });
}

TagManager.state.selectedTags.clear();
TagManager.debouncedUpdateAvailableTags(TagManager.state.originalTags, TagManager.state.tags);
TagManager.updateSelectedTags([]);

console.log('Original tags:', TagManager.state.originalTags);

// Lineage abbreviation mapping (matching Python version)
const ABBREVIATED_LINEAGE = {
    "SATIVA": "S",
    "INDICA": "I", 
    "HYBRID": "H",
    "HYBRID/SATIVA": "H/S",
    "HYBRID/INDICA": "H/I",
    "CBD": "CBD",
    "CBD_BLEND": "CBD",
    "MIXED": "THC",
    "PARA": "P"
};

// When populating the lineage filter dropdown, use abbreviated lineage names
function populateLineageFilterOptions(options) {
  const lineageFilter = document.getElementById('lineageFilter');
  if (!lineageFilter) return;
  lineageFilter.innerHTML = '';
  const defaultOption = document.createElement('option');
  defaultOption.value = '';
  defaultOption.textContent = 'All Lineages';
  lineageFilter.appendChild(defaultOption);
  options.forEach(opt => {
    const option = document.createElement('option');
    option.value = opt;
    const displayName = ABBREVIATED_LINEAGE[opt] || opt;
    option.textContent = displayName;
    lineageFilter.appendChild(option);
  });
}

function hyphenNoBreakBeforeQuantity(text) {
    // Replace " - 1g" with " -\u00A01g"
    return text.replace(/ - (\d[\w.]*)/g, ' -\u00A0$1');
}

// Only add event listener if the button exists
const addSelectedTagsBtn = document.getElementById('addSelectedTagsBtn');
if (addSelectedTagsBtn) {
    addSelectedTagsBtn.addEventListener('click', function() {
        // Get all checked checkboxes in the available tags container
        const checked = document.querySelectorAll('#availableTags .tag-checkbox:checked');
        const tagsToMove = Array.from(checked).map(cb => cb.value);
        TagManager.moveToSelected(tagsToMove);
    });
}

function autocheckAllAvailableTags() {
  // Select all checkboxes in the available tags container
  document.querySelectorAll('#availableTags .tag-checkbox').forEach(cb => {
    cb.checked = true;
    // Optionally, update your state if needed:
    TagManager.state.selectedTags.add(cb.value);
  });
  // Optionally, update any UI or state that depends on checked tags
  TagManager.updateTagCheckboxes && TagManager.updateTagCheckboxes();
}

// Only update if filteredTags is defined
if (typeof filteredTags !== 'undefined' && filteredTags) {
    TagsTable.updateTagsList('availableTags', filteredTags);
}
autocheckAllAvailableTags();

// Test function for Select All functionality
window.testSelectAll = function() {
  console.log('Testing Select All functionality...');
  
  // Test Available Select All
  const selectAllAvailable = document.getElementById('selectAllAvailable');
  console.log('Select All Available checkbox:', selectAllAvailable);
  if (selectAllAvailable) {
    console.log('Available checkbox checked state:', selectAllAvailable.checked);
    console.log('Available checkbox visible:', selectAllAvailable.offsetParent !== null);
    console.log('Available checkbox style:', window.getComputedStyle(selectAllAvailable));
    
    // Manually trigger the change event
    selectAllAvailable.checked = !selectAllAvailable.checked;
    selectAllAvailable.dispatchEvent(new Event('change', { bubbles: true }));
    console.log('Manually triggered Available change event');
  } else {
    console.error('Select All Available checkbox not found!');
  }
  
  // Test Selected Select All
  const selectAllSelected = document.getElementById('selectAllSelected');
  console.log('Select All Selected checkbox:', selectAllSelected);
  if (selectAllSelected) {
    console.log('Selected checkbox checked state:', selectAllSelected.checked);
    console.log('Selected checkbox visible:', selectAllSelected.offsetParent !== null);
    console.log('Selected checkbox style:', window.getComputedStyle(selectAllSelected));
    
    // Manually trigger the change event
    selectAllSelected.checked = !selectAllSelected.checked;
    selectAllSelected.dispatchEvent(new Event('change', { bubbles: true }));
    console.log('Manually triggered Selected change event');
  } else {
    console.error('Select All Selected checkbox not found!');
  }
};

async function handleJsonPasteInput(input) {
    let jsonText = input.trim();
    let json;
    // If input looks like a URL, fetch the JSON
    if (jsonText.startsWith('http')) {
        try {
            const response = await fetch(jsonText);
            jsonText = await response.text();
        } catch (e) {
            console.error('Failed to fetch JSON from URL.');
            return;
        }
    }
    try {
        json = JSON.parse(jsonText);
    } catch (e) {
        console.error('Invalid JSON format. Please paste valid JSON.');
        return;
    }
    // ... continue with your matching logic ...
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Show splash screen immediately
    AppLoadingSplash.show();
    
    // Initialize TagManager (which will handle the splash loading)
    TagManager.init();
    
    // Initialize sticky filter bar behavior
    initializeStickyFilterBar();

    // Add event listener for the clear button
    const clearButton = document.getElementById('clear-filters-btn');
    if (clearButton) {
        clearButton.addEventListener('click', function() {
            if (window.TagManager && TagManager.clearSelected) {
                TagManager.clearSelected();
            }
        });
        console.log('Clear button event listener attached');
    } else {
        console.error('Clear button not found');
    }

    // Add event listener for the undo button
    const undoButton = document.getElementById('undo-move-btn');
    if (undoButton) {
        undoButton.addEventListener('click', function() {
            if (window.TagManager && TagManager.undoMove) {
                TagManager.undoMove();
            }
        });
        console.log('Undo button event listener attached');
    } else {
        console.error('Undo button not found');
    }

    // Note: Select All event listeners are now handled in the TagManager._updateAvailableTags and updateSelectedTags methods
    // to ensure proper state management and prevent duplicate listeners
    
    // Fallback: ensure splash screen completes even if there are issues
    setTimeout(() => {
        if (AppLoadingSplash.isVisible) {
            console.log('Fallback: completing splash screen after timeout');
            AppLoadingSplash.stopAutoAdvance();
            AppLoadingSplash.complete();
        }
    }, 10000); // 10 second fallback
});

// Global functions for debugging
window.AppLoadingSplash = AppLoadingSplash;
window.emergencyHideSplash = () => AppLoadingSplash.emergencyHide();

// Function to clear stuck uploads
async function clearStuckUploads() {
    try {
        console.log('Clearing stuck uploads...');
        const response = await fetch('/api/clear-upload-status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Upload status cleared:', result.message);
            
            // Show a toast notification
            if (window.Toast) {
                Toast.show('success', result.message);
            } else {
                alert(result.message);
            }
            
            // Refresh the page to reset the UI state
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            console.error('Failed to clear upload status:', response.statusText);
            alert('Failed to clear stuck uploads. Please try again.');
        }
    } catch (error) {
        console.error('Error clearing stuck uploads:', error);
        alert('Error clearing stuck uploads. Please try again.');
    }
}

// Initialize sticky filter bar behavior
function initializeStickyFilterBar() {
    const stickyFilterBar = document.querySelector('.sticky-filter-bar');
    const tagList = document.getElementById('availableTags');
    
    if (stickyFilterBar && tagList) {
        // Add scroll event listener to the tag list
        tagList.addEventListener('scroll', function() {
            const rect = stickyFilterBar.getBoundingClientRect();
            const cardHeader = document.querySelector('.card-header');
            
            if (cardHeader) {
                const headerRect = cardHeader.getBoundingClientRect();
                
                // Check if the filter bar should be sticky
                if (headerRect.bottom <= 0) {
                    stickyFilterBar.classList.add('is-sticky');
                } else {
                    stickyFilterBar.classList.remove('is-sticky');
                }
            }
        });
        
        // Also listen for window scroll for better cross-browser compatibility
        window.addEventListener('scroll', function() {
            const rect = stickyFilterBar.getBoundingClientRect();
            const cardHeader = document.querySelector('.card-header');
            
            if (cardHeader) {
                const headerRect = cardHeader.getBoundingClientRect();
                
                if (headerRect.bottom <= 0) {
                    stickyFilterBar.classList.add('is-sticky');
                } else {
                    stickyFilterBar.classList.remove('is-sticky');
                }
            }
        });
    }
}

function clearUIState() {
    // Clear selected tags
    if (window.TagManager && TagManager.clearSelected) TagManager.clearSelected();
    // Clear search fields
    document.querySelectorAll('input[type="text"]').forEach(el => el.value = '');
    // Reset filters
    document.querySelectorAll('select').forEach(el => el.selectedIndex = 0);
    // Clear checkboxes
    document.querySelectorAll('input[type="checkbox"]').forEach(el => el.checked = false);
    // Clear localStorage/sessionStorage
    if (window.localStorage) localStorage.clear();
    if (window.sessionStorage) sessionStorage.clear();
}

// Call clearUIState after export or upload success
// Example: after successful AJAX response for export/upload
// clearUIState();

// Removed conflicting file info text initialization - now handled by checkForExistingData()

// Global function to clear stuck upload UI (can be called from browser console)
window.clearStuckUploadUI = function() {
    if (typeof TagManager !== 'undefined' && TagManager.forceClearUploadUI) {
        TagManager.forceClearUploadUI();
        console.log('Stuck upload UI cleared via global function');
    } else {
        console.error('TagManager not available');
    }
};

// Global function to check upload status
window.checkUploadStatus = function(filename) {
    fetch(`/api/upload-status?filename=${encodeURIComponent(filename)}`)
        .then(response => response.json())
        .then(data => {
            console.log('Upload status:', data);
        })
        .catch(error => {
            console.error('Error checking upload status:', error);
        });
};