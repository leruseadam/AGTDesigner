// Detect Windows platform for optimizations
const isWindows = navigator.platform.toLowerCase().includes('win') ||
                 navigator.userAgent.toLowerCase().includes('windows');

// Centralized debug logging toggle
const TAG_MANAGER_DEBUG_ENABLED = Boolean(
    window.localStorage?.getItem('tagManagerDebug') === 'true' ||
    window.sessionStorage?.getItem('tagManagerDebug') === 'true' ||
    window.TAG_MANAGER_DEBUG === true
);

const verboseLog = (...args) => {
    if (TAG_MANAGER_DEBUG_ENABLED) {
        console.log(...args);
    }
};

const verboseWarn = (...args) => {
    if (TAG_MANAGER_DEBUG_ENABLED) {
        console.warn(...args);
    }
};

// Windows-specific performance optimizations
if (isWindows) {
    // Request continuous repainting for smoother animations
    requestAnimationFrame(function continuousRepaint() {
        requestAnimationFrame(continuousRepaint);
    });
    
    // Optimize DOM operations for Windows
    if (typeof document.documentElement.style.transition !== 'undefined') {
        // Reduce repaints
        document.body.style.transform = 'translateZ(0)';
        document.body.style.willChange = 'contents';
    }
    
    verboseLog('Windows performance optimizations enabled');
}

// Memory-optimized performance utilities
const performanceUtils = {
    // Memory-efficient debounce with cleanup - optimized for Windows
    debounce(func, wait) {
        let timeout;
        const optimizedWait = isWindows ? Math.max(wait * 0.5, 10) : wait; // Faster on Windows
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                timeout = null; // Help GC
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, optimizedWait);
        };
    },
    
    // Memory-efficient throttle - optimized for Windows
    throttle(func, limit) {
        let inThrottle;
        const optimizedLimit = isWindows ? Math.max(limit * 0.5, 10) : limit; // Faster on Windows
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, optimizedLimit);
            }
        }
    },
    
    // Memory-efficient DOM batching
    batchDOMUpdate(callback) {
        return requestAnimationFrame(() => {
            callback();
        });
    },
    
    // Memory monitoring
    startTiming: () => performance.now(),
    endTiming: (start, operation) => {
        const duration = performance.now() - start;
        if (duration > 16) {
            console.warn(`Performance: ${operation} took ${duration.toFixed(2)}ms`);
        }
        return duration;
    },
    
    // Memory cleanup utilities
    cleanup: {
        // Clear large objects
        clearLargeObjects(obj) {
            if (obj && typeof obj === 'object') {
                Object.keys(obj).forEach(key => {
                    if (obj[key] && typeof obj[key] === 'object' && obj[key].length > 1000) {
                        obj[key] = null;
                    }
                });
            }
        },
        
        // Force garbage collection if available
        forceGC() {
            if (window.gc) {
                window.gc();
            }
        }
    }
};

// Global error handler to prevent window from exiting
// Only log errors that are not syntax errors from cached/old files
window.addEventListener('error', function(event) {
    // Filter out common non-critical errors
    if (event.error && event.error.message) {
        const errorMsg = event.error.message.toLowerCase();
        // Skip "Unexpected end of input" errors which are often false positives from caching
        if (errorMsg.includes('unexpected end of input')) {
            console.warn('⚠️ Syntax error detected (likely browser cache issue) - ignoring:', errorMsg);
            event.preventDefault();
            return false;
        }
    }
    console.error('Global error caught:', event.error);
    console.error('Error at:', event.filename, 'line:', event.lineno, 'column:', event.colno);
    event.preventDefault();
    return false;
});

// Global unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    event.preventDefault();
});

// Toast fallback: define Toast if not present
if (typeof Toast === 'undefined') {
  window.Toast = {
    show: (type, msg) => {
      if (type === 'error') {
        alert('Error: ' + msg);
      } else {
        // Don't show alerts for success/info messages to prevent popups
        verboseLog(`Toast (${type}): ${msg}`);
      }
    },
    error: (msg, options) => {
      alert('Error: ' + msg);
    },
    success: (msg, options) => {
      verboseLog(`Toast (success): ${msg}`);
    },
    info: (msg, options) => {
      verboseLog(`Toast (info): ${msg}`);
    },
    warning: (msg, options) => {
      alert('Warning: ' + msg);
    }
  };
}

// Classic types that should show "Lineage" instead of "Brand"
const CLASSIC_TYPES = [
    "flower", "pre-roll", "concentrate", "infused pre-roll", 
    "solventless concentrate", "vape cartridge", "rso/co2 tankers"
];

// Add this near the top of the file, before any code that uses it
// Product type normalization mapping (same as backend TYPE_OVERRIDES)
const PRODUCT_TYPE_OVERRIDES = {
  "all-in-one": "vape cartridge",
  "rosin": "concentrate",
  "mini buds": "flower",
  "bud": "flower",
  "pre-roll": "pre-roll",
  "Pre-Roll": "pre-roll",  // Map title case to lowercase for filtering
  "Infused Pre-Roll": "infused pre-roll",  // Map title case to lowercase for filtering
  "infused pre-roll": "infused pre-roll",  // Map lowercase to lowercase for filtering
  "alcohol/ethanol extract": "rso/co2 tankers",
  "Alcohol/Ethanol Extract": "rso/co2 tankers",
  "alcohol ethanol extract": "rso/co2 tankers",
  "Alcohol Ethanol Extract": "rso/co2 tankers",
  "c02/ethanol extract": "rso/co2 tankers",
  "CO2 Concentrate": "rso/co2 tankers",
  "co2 concentrate": "rso/co2 tankers"
};

// Function to normalize product types (same as backend)

    // Detect if running on PythonAnywhere
    function isPythonAnywhere() {
        return window.location.hostname.includes('pythonanywhere.com');
    }
    
    // Choose upload endpoint based on environment
    function getUploadEndpoint() {
        if (isPythonAnywhere()) {
            return '/upload-pythonanywhere';
        } else {
            return '/upload';
        }
    }
function normalizeProductType(productType) {
  if (!productType) return productType;
  const normalized = PRODUCT_TYPE_OVERRIDES[productType.toLowerCase()];
  return normalized || productType;
}

function formatProductTypeLabel(value) {
  if (!value) return value;
  if (value === 'rso/co2 tankers') {
    return 'RSO/CO2 Tanker';
  }
  return value.split(' ').map(word => {
    if (word.includes('/')) {
      return word.toUpperCase();
    }
    if (word.includes('-')) {
      return word.split('-').map(segment => segment ? segment.charAt(0).toUpperCase() + segment.slice(1) : segment).join('-');
    }
    if (word === word.toUpperCase()) {
      return word;
    }
    return word.charAt(0).toUpperCase() + word.slice(1);
  }).join(' ');
}

// Global function to restore body scroll after modal closes
function restoreBodyScroll() {
  document.body.style.overflow = '';
  document.body.classList.remove('modal-open');
  document.body.style.paddingRight = '';
  document.body.style.pointerEvents = '';
}

// Function to open strain lineage editor
async function openStrainLineageEditor() {
  try {
    // Show loading state
    const loadingModal = document.createElement('div');
    loadingModal.className = 'modal fade';
    loadingModal.id = 'loadingModal';
    loadingModal.innerHTML = `
      <div class="modal-dialog modal-sm">
        <div class="modal-content">
          <div class="modal-body text-center">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading strains from database...</p>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(loadingModal);
    
    const loadingInstance = new bootstrap.Modal(loadingModal);
    loadingInstance.show();
    
    // Add timeout protection with shorter timeout
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => {
        // Ensure loading modal is hidden on timeout
        if (loadingInstance) {
          loadingInstance.hide();
        }
        if (loadingModal && loadingModal.parentNode) {
          loadingModal.parentNode.removeChild(loadingModal);
        }
        reject(new Error('Request timed out after 10 seconds'));
      }, 10000); // 10 second timeout
    });
    
    // Fetch all strains from the master database with timeout
    const fetchPromise = fetch('/api/get-all-strains');
    const response = await Promise.race([fetchPromise, timeoutPromise]);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch strains from database: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    
    // Hide loading modal and ensure it's completely removed
    if (loadingInstance) {
      loadingInstance.hide();
    }
    if (loadingModal && loadingModal.parentNode) {
      loadingModal.parentNode.removeChild(loadingModal);
    }
    
    // Ensure any remaining loading states are cleared
    const remainingLoadingModals = document.querySelectorAll('.modal[id*="loading"]');
    remainingLoadingModals.forEach(modal => {
      const instance = bootstrap.Modal.getInstance(modal);
      if (instance) {
        instance.hide();
      }
      if (modal.parentNode) {
        modal.parentNode.removeChild(modal);
      }
    });
    
    if (!data.success) {
      throw new Error(data.error || 'Failed to load strains');
    }
    
    const strains = data.strains;
    
    if (strains.length === 0) {
      alert('No strains found in the master database.');
      return;
    }
    
    // Clean up any existing strain selection modal first
    const existingModal = document.getElementById('strainSelectionModal');
    if (existingModal) {
      verboseLog('Removing existing strain selection modal');
      const existingModalInstance = bootstrap.Modal.getInstance(existingModal);
      if (existingModalInstance) {
        existingModalInstance.dispose();
      }
      existingModal.remove();
    }
    
    // Create a strain selection modal with search functionality
    verboseLog('Creating strain selection modal with', strains.length, 'strains');
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'strainSelectionModal';
    modal.setAttribute('data-bs-backdrop', 'static');
    modal.setAttribute('data-bs-keyboard', 'false');
    modal.innerHTML = `
      <div class="modal-backdrop fade show" style="z-index: 1050;"></div>
      <div class="modal-dialog modal-lg" style="z-index: 1055;">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Choose a strain to edit lineage for</h5>
            <button type="button" class="btn-close" id="strainSelectionCloseBtn" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p class="text-muted mb-3">Choose a strain to edit lineage for ALL products with that strain in the master database:</p>
            
            <!-- Search Box -->
            <div class="mb-3">
              <div class="input-group">
                <span class="input-group-text">
                  <i class="fas fa-search"></i>
                </span>
                <input type="text" class="form-control" id="strainSearchInput" 
                       placeholder="Search strains by name..." 
                       autocomplete="off">
                <button class="btn btn-outline-secondary" type="button" id="clearStrainSearch">
                  Clear
                </button>
              </div>
              <div class="form-text">
                <small class="text-muted">
                  <span id="strainSearchResults">Showing ${strains.length} strains</span>
                </small>
              </div>
            </div>
            
            <div class="list-group" id="strainListContainer">
              ${strains.map(strain => `
                <button type="button" class="list-group-item list-group-item-action strain-item" 
                        data-strain-name="${strain.strain_name.toLowerCase()}"
                        onclick="selectStrainForEditing('${strain.strain_name.replace(/'/g, "\\'")}', '${strain.current_lineage}')">
                  <div class="d-flex justify-content-between align-items-start">
                    <div>
                      <strong class="strain-name">${strain.strain_name}</strong>
                      <br>
                      <small class="text-muted">
                        Current: ${strain.current_lineage} | 
                        Products: ${strain.total_occurrences} | 
                        Last seen: ${new Date(strain.last_seen_date).toLocaleDateString()}
                      </small>
                    </div>
                    <span class="badge bg-primary">${strain.current_lineage}</span>
                  </div>
                </button>
              `).join('')}
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" id="strainSelectionCancelBtn">Cancel</button>
          </div>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    verboseLog('Modal added to DOM, modal element:', modal);
    
    // Add event listeners for close buttons
    const closeBtn = document.getElementById('strainSelectionCloseBtn');
    const cancelBtn = document.getElementById('strainSelectionCancelBtn');
    
    if (closeBtn) {
      closeBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        verboseLog('Strain selection close button clicked');
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
          modalInstance.hide();
        }
      });
    }
    
    if (cancelBtn) {
      cancelBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        verboseLog('Strain selection cancel button clicked');
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
          modalInstance.hide();
        }
      });
    }
    
    // Add search functionality
    const searchInput = document.getElementById('strainSearchInput');
    const clearSearchBtn = document.getElementById('clearStrainSearch');
    const strainItems = document.querySelectorAll('.strain-item');
    const resultsCounter = document.getElementById('strainSearchResults');
    
    // Search function
    function filterStrains(searchTerm) {
      const term = searchTerm.toLowerCase().trim();
      let visibleCount = 0;
      
      strainItems.forEach(item => {
        const strainName = item.getAttribute('data-strain-name');
        const strainNameElement = item.querySelector('.strain-name');
        const originalText = strainNameElement.textContent;
        
        if (term === '' || strainName.includes(term)) {
          item.style.display = 'block';
          visibleCount++;
          
          // Highlight matching text if there's a search term
          if (term !== '') {
            const regex = new RegExp(`(${term})`, 'gi');
            strainNameElement.innerHTML = originalText.replace(regex, '<mark>$1</mark>');
          } else {
            strainNameElement.innerHTML = originalText;
          }
        } else {
          item.style.display = 'none';
        }
      });
      
      // Update results counter
      resultsCounter.textContent = `Showing ${visibleCount} of ${strains.length} strains`;
      
      // Show "no results" message if needed
      if (visibleCount === 0 && term !== '') {
        const noResults = document.createElement('div');
        noResults.className = 'text-center text-muted py-3';
        noResults.innerHTML = `
          <i class="fas fa-search me-2"></i>
          No strains found matching "${searchTerm}"
        `;
        
        const container = document.getElementById('strainListContainer');
        const existingNoResults = container.querySelector('.no-results-message');
        if (!existingNoResults) {
          noResults.classList.add('no-results-message');
          container.appendChild(noResults);
        }
      } else {
        // Remove "no results" message if it exists
        const noResults = document.querySelector('.no-results-message');
        if (noResults) {
          noResults.remove();
        }
      }

      // Return boolean indicating whether any items are visible after filtering
      return visibleCount > 0;
    }
    
    // Event listeners for search
    if (searchInput) {
      // Create debounced filter function for better performance
      const debouncedFilter = performanceUtils.debounce((value) => {
        filterStrains(value);
      }, 150); // 150ms debounce
      
      searchInput.addEventListener('input', (e) => {
        const val = e.target.value;
        
        // Immediate visual feedback
        const hasTerm = val && val.trim().length > 0;
        searchInput.classList.toggle('search-active', !!hasTerm);
        
        // Debounced filtering for performance
        debouncedFilter(val);
      }, { passive: true });
      
      // Focus on search input when modal opens
      searchInput.focus();
      
      // Handle Enter key to select first visible strain
      searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          const firstVisible = document.querySelector('.strain-item[style*="block"], .strain-item:not([style*="none"])');
          if (firstVisible) {
            firstVisible.click();
          }
        }
      });
    }
    
    // Clear search button
    if (clearSearchBtn) {
      clearSearchBtn.addEventListener('click', () => {
        searchInput.value = '';
        filterStrains('');
        searchInput.classList.remove('search-active');
        searchInput.focus();
      });
    }
    
    // Ensure any remaining loading modals are completely hidden and removed
    const existingLoadingModals = document.querySelectorAll('.modal[id*="loading"]');
    verboseLog('Found existing loading modals:', existingLoadingModals.length);
    existingLoadingModals.forEach(loadingModal => {
      const instance = bootstrap.Modal.getInstance(loadingModal);
      if (instance) {
        verboseLog('Hiding loading modal instance');
        instance.hide();
      }
      if (loadingModal.parentNode) {
        verboseLog('Removing loading modal from DOM');
        loadingModal.parentNode.removeChild(loadingModal);
      }
    });
    
    // Show the modal with debugging
    verboseLog('Creating modal instance for strain selection');
    const modalInstance = new bootstrap.Modal(modal);
    verboseLog('Showing strain selection modal');
    modalInstance.show();
    
    // Add a small delay to ensure the modal is properly displayed
    setTimeout(() => {
      verboseLog('Modal should now be visible');
      // Ensure any loading spinners in the modal are removed
      const loadingSpinners = modal.querySelectorAll('.spinner-border, .spinner-grow');
      loadingSpinners.forEach(spinner => {
        spinner.remove();
      });
      
      // Force the modal to be visible if it's not
      if (!modal.classList.contains('show')) {
        verboseLog('Modal not visible, forcing show');
        modal.classList.add('show');
        modal.style.display = 'block';
        modal.setAttribute('aria-hidden', 'false');
      }
    }, 100);
    
    // Clean up modal when hidden
    modal.addEventListener('hidden.bs.modal', () => {
      verboseLog('Strain selection modal hidden, cleaning up');
      if (modal.parentNode) {
        document.body.removeChild(modal);
      }
      // Ensure body overflow is restored when modal is closed
      restoreBodyScroll();
    });
    
    // Add event listener for when modal is shown
    modal.addEventListener('shown.bs.modal', () => {
      verboseLog('Strain selection modal is now visible');
    });
    
  } catch (error) {
    console.error('Error opening strain lineage editor:', error);
    
    // Hide loading modal if it exists
    const loadingModal = document.getElementById('loadingModal');
    if (loadingModal) {
      const loadingInstance = bootstrap.Modal.getInstance(loadingModal);
      if (loadingInstance) {
        loadingInstance.hide();
      }
      document.body.removeChild(loadingModal);
    }
    
    // Show appropriate error message
    if (error.message === 'Request timed out') {
      alert('The request to load strains timed out. Please try again. If the problem persists, refresh the page.');
    } else {
      alert(`Failed to load strains: ${error.message}`);
    }
  }
}

// Function to select a strain for editing
function selectStrainForEditing(strainName, currentLineage) {
  verboseLog('selectStrainForEditing called with:', strainName, currentLineage);
  
  try {
    // Close the selection modal with proper cleanup
    const selectionModal = document.getElementById('strainSelectionModal');
    if (selectionModal) {
      verboseLog('Closing strain selection modal');
      const modalInstance = bootstrap.Modal.getInstance(selectionModal);
      if (modalInstance) {
        modalInstance.hide();
      }
      
      // Wait for modal to fully close before opening lineage editor
      setTimeout(() => {
        verboseLog('Strain selection modal closed, opening lineage editor');
        openLineageEditorForStrain(strainName, currentLineage);
      }, 300);
    } else {
      verboseLog('No strain selection modal found, opening lineage editor directly');
      openLineageEditorForStrain(strainName, currentLineage);
    }
  } catch (error) {
    console.error('Error in selectStrainForEditing:', error);
    alert('An unexpected error occurred. Please refresh the page and try again.');
  }
}

// Separate function to open lineage editor
function openLineageEditorForStrain(strainName, currentLineage) {
  verboseLog('openLineageEditorForStrain called with:', strainName, currentLineage);
  
  try {
    
    // Check if strain lineage editor is available
    if (window.strainLineageEditor) {
      verboseLog('Strain lineage editor is available, calling openEditor');
      try {
        // Enhanced lineage editor call with error handling
                try {
                    if (window.strainLineageEditor && typeof window.strainLineageEditor.openEditor === 'function') {
                        window.strainLineageEditor.openEditor(strainName, currentLineage);
                    } else {
                        console.error('StrainLineageEditor not properly initialized');
                        alert('Lineage editor not available. Please refresh the page and try again.');
                    }
                } catch (error) {
                    console.error('Error opening lineage editor:', error);
                    alert('Error opening lineage editor. Please try again.');
                }
        verboseLog('openEditor called successfully');
      } catch (error) {
        console.error('Error opening strain lineage editor:', error);
        alert('Error opening strain lineage editor. Please try again.');
        return;
      }
    } else {
      verboseLog('Strain lineage editor not available, attempting to initialize...');
      
      // Check if the modal element exists
      const modalElement = document.getElementById('strainLineageEditorModal');
      if (!modalElement) {
        console.error('strainLineageEditorModal element not found');
        alert('Strain Lineage Editor modal not found. Please refresh the page and try again.');
        return;
      }
      
      verboseLog('Modal element found, attempting to initialize StrainLineageEditor');
      
      // Try to initialize the editor
      try {
        if (typeof StrainLineageEditor !== 'undefined') {
          verboseLog('StrainLineageEditor class is available, initializing...');
          window.strainLineageEditor = StrainLineageEditor.init();
          verboseLog('StrainLineageEditor initialized');
          
          setTimeout(() => {
            if (window.strainLineageEditor) {
              verboseLog('Calling openEditor after initialization');
              try {
                // Enhanced lineage editor call with error handling
                try {
                    if (window.strainLineageEditor && typeof window.strainLineageEditor.openEditor === 'function') {
                        window.strainLineageEditor.openEditor(strainName, currentLineage);
                    } else {
                        console.error('StrainLineageEditor not properly initialized');
                        alert('Lineage editor not available. Please refresh the page and try again.');
                    }
                } catch (error) {
                    console.error('Error opening lineage editor:', error);
                    alert('Error opening lineage editor. Please try again.');
                }
                verboseLog('openEditor called successfully after initialization');
              } catch (openError) {
                console.error('Error calling openEditor after initialization:', openError);
                alert('Error opening strain lineage editor. Please try again.');
              }
            } else {
              console.error('strainLineageEditor still not available after initialization');
              alert('Failed to initialize Strain Lineage Editor. Please refresh the page and try again.');
            }
          }, 100);
        } else {
          console.error('StrainLineageEditor class not defined');
          alert('Strain Lineage Editor not loaded. Please refresh the page and try again.');
        }
      } catch (error) {
        console.error('Error initializing strain lineage editor:', error);
        alert('Failed to initialize Strain Lineage Editor. Please refresh the page and try again.');
      }
    }
  } catch (error) {
    console.error('Error in selectStrainForEditing:', error);
    alert('An unexpected error occurred. Please refresh the page and try again.');
  }
}

const VALID_PRODUCT_TYPES = [
  "flower", "pre-roll", "infused pre-roll", "concentrate", "solventless concentrate", "vape cartridge",
  "edible (solid)", "edible (liquid)", "high cbd edible liquid", "tincture", "topical", "capsule", "paraphernalia",
  "rso/co2 tankers"
];

// Mac-like ultra-fast debounce function
const debounce = (func, delay) => {
    let timeoutId;
    
    return function(...args) {
        const context = this;
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(context, args), delay);
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
        { text: 'Welcome to Auto Generating Tag Designer!', progress: 100 }
    ],
    currentStep: 0,
    isVisible: true,
    autoAdvanceInterval: null,

    show() {
        this.isVisible = true;
        this.currentStep = 0;
        // Emergency kill-switch: never let the splash sit indefinitely
        if (this._emergencyTimer) {
            clearTimeout(this._emergencyTimer);
        }
        this._emergencyTimer = setTimeout(() => {
            this.emergencyHide();
        }, 7000);
        
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
        verboseLog('Splash screen shown');
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
        verboseLog(`Splash progress: ${progress}% - ${text}`);
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
        this.updateProgress(100, 'Welcome to Auto Generating Tag Designer!');
        setTimeout(() => {
            this.hide();
        }, 1000);
    },

    hide() {
        this.isVisible = false;
        this.stopAutoAdvance();
        if (this._emergencyTimer) {
            clearTimeout(this._emergencyTimer);
            this._emergencyTimer = null;
        }
        
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
                if (window.scaleAppToFit) {
                    try { window.scaleAppToFit(); } catch (e) { console.warn('scaleAppToFit error', e); }
                }
            }, 100);
        }
        
        verboseLog('Splash screen hidden');
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
        verboseLog('Emergency hiding splash screen');
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
    CACHE_TTL_MS: 10 * 60 * 1000, // 10 minutes
    state: {
        selectedTags: new Set(),
        isProcessingDeselection: false, // Flag to prevent filter updates during deselection
        isClearing: false, // Flag to prevent multiple simultaneous clear operations
        persistentSelectedTags: [], // Array to maintain order
        initialized: false,
        filters: {},
        loading: false,
        isJsonMatchedSession: false,
        brandCategories: new Map(), // Memory-efficient Map
        originalTags: [], // Will be cleared when not needed
        originalFilterOptions: {}, // Minimal filter options
        lineageColors: {
            'SATIVA': 'var(--lineage-sativa)',
            'INDICA': 'var(--lineage-indica)',
            'HYBRID': 'var(--lineage-hybrid)',
            'HYBRID/SATIVA': 'var(--lineage-sativa)',  // Changed to sativa color
            'HYBRID/INDICA': 'var(--lineage-indica)',
            'CBD': 'var(--lineage-cbd)',
            'PARA': 'var(--lineage-para)',
            'MIXED': 'var(--lineage-mixed)',
            'CBD_BLEND': 'var(--lineage-cbd)'
        },
        filterCache: null, // Single cache entry
        updateAvailableTagsTimer: null,
        isSearching: false,
        initialDataAttempts: 0,
        initialDataRetryTimer: null,
        hydratedFromCache: false,
        forceFullAvailableTagRender: true,
        simplifiedAvailableTagsActive: false,
        // Memory optimization flags
        _memoryOptimized: true,
        _lastCleanup: Date.now()
    },
    SIMPLIFIED_RENDER_THRESHOLD: 900,
    initialDataRetryDelays: [1500, 3500, 6000, 10000],
    isGenerating: false, // Add generation lock flag

    getAvailableTagsCacheKey() {
        try {
            const store = (window.sessionStorage && (sessionStorage.getItem('selected_store') || sessionStorage.getItem('store'))) ||
                window.currentStore || 'default';
            const file = (window.sessionStorage && (sessionStorage.getItem('uploaded_filename') || sessionStorage.getItem('file_path'))) ||
                'nofile';
            const cacheKey = `agt_available_tags_${store}_${file}`;
            console.log('🔑 Cache key generated:', cacheKey, '{ store:', store, 'file:', file, '}');
            return cacheKey;
        } catch (error) {
            console.warn('Failed to build available-tags cache key:', error);
            return 'agt_available_tags_default';
        }
    },

    loadAvailableTagsFromCache() {
        try {
            console.log('💾 Attempting to load tags from cache...');
            if (!window.sessionStorage) {
                console.log('❌ No sessionStorage available');
                return null;
            }
            const cacheKey = this.getAvailableTagsCacheKey();
            const raw = sessionStorage.getItem(cacheKey);
            if (!raw) {
                console.log('❌ No cached data found for key:', cacheKey);
                return null;
            }
            console.log('✅ Found cached data, parsing...');
            const payload = JSON.parse(raw);
            if (!payload || !Array.isArray(payload.tags) || payload.tags.length === 0) {
                console.log('❌ Invalid cache payload:', payload);
                return null;
            }
            const age = Date.now() - payload.timestamp;
            const ageMinutes = (age / 60000).toFixed(1);
            console.log(`📅 Cache age: ${ageMinutes} minutes (max: ${this.CACHE_TTL_MS / 60000} minutes)`);
            if (payload.timestamp && age > this.CACHE_TTL_MS) {
                console.log('⏰ Cache expired, ignoring');
                return null;
            }
            console.log(`✅ Cache HIT: ${payload.tags.length} tags loaded`);
            
            // Verify cached tags have database lineage
            const sampleTag = payload.tags[0];
            if (sampleTag) {
                console.log('🔍 Sample cached tag lineage:', {
                    name: sampleTag['Product Name*'],
                    canonical_lineage: sampleTag.canonical_lineage,
                    currentLineage: sampleTag.currentLineage,
                    Lineage: sampleTag.Lineage
                });
            }
            
            return payload.tags;
        } catch (error) {
            console.warn('❌ Failed to load cache:', error);
            return null;
        }
    },

    saveAvailableTagsToCache(tags) {
        try {
            if (!window.sessionStorage || !Array.isArray(tags) || tags.length === 0) {
                console.log('⚠️ Cannot save cache:', !window.sessionStorage ? 'no sessionStorage' : 'invalid tags');
                return;
            }
            const payload = {
                timestamp: Date.now(),
                tags
            };
            const cacheKey = this.getAvailableTagsCacheKey();
            
            // Verify tags have database lineage before caching
            const sampleTag = tags[0];
            if (sampleTag) {
                console.log('💾 Saving to cache - sample tag lineage:', {
                    name: sampleTag['Product Name*'],
                    canonical_lineage: sampleTag.canonical_lineage,
                    currentLineage: sampleTag.currentLineage,
                    Lineage: sampleTag.Lineage
                });
            }
            
            sessionStorage.setItem(cacheKey, JSON.stringify(payload));
            console.log(`💾 Cached ${tags.length} tags with key: ${cacheKey}`);
        } catch (error) {
            console.warn('❌ Failed to save cache:', error);
        }
    },

    clearAvailableTagsCache() {
        try {
            if (window.sessionStorage) {
                sessionStorage.removeItem(this.getAvailableTagsCacheKey());
                verboseLog('Cleared available-tags cache');
            }
        } catch (error) {
            console.warn('Failed to clear available-tags cache:', error);
        }
    },

    hydrateAvailableTagsFromCache() {
        if (this.state.hydratedFromCache) {
            return false;
        }
        const cachedTags = this.loadAvailableTagsFromCache();
        if (cachedTags && cachedTags.length) {
            console.log(`⚡ INSTANT LOAD: Hydrating ${cachedTags.length} tags from cache`);
            this.state.hydratedFromCache = true;
            this.state.forceFullAvailableTagRender = true;
            this.state.simplifiedAvailableTagsActive = false;
            this.state.tags = [...cachedTags];
            this.state.originalTags = [...cachedTags];
            
            // CRITICAL FIX: Use requestAnimationFrame to ensure immediate render
            requestAnimationFrame(() => {
                this._updateAvailableTags(cachedTags, null);
                console.log(`✅ INSTANT LOAD: ${cachedTags.length} tags rendered from cache`);
                
                // Hide splash immediately when rendering from cache
                if (this.hideActionSplash) {
                    this.hideActionSplash();
                }
                if (typeof AppLoadingSplash !== 'undefined' && AppLoadingSplash.isVisible) {
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                }
            });
            return true;
        }
        return false;
    },

    resetSearchInputs() {
        try {
            const searchInputs = document.querySelectorAll('#availableTagsSearch, #selectedTagsSearch');
            searchInputs.forEach(input => {
                const hadValue = input.value && input.value.length;
                input.value = '';
                if (hadValue) {
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                }
            });
            verboseLog('Cleared primary search inputs');
        } catch (error) {
            console.warn('Failed to reset search inputs during clear:', error);
        }
    },

    // Helper function to find tags in selected tags list, preserving tags from multiple filters
    // CRITICAL FIX: Use originalTags first to find ALL selected tags, not just filtered ones
    getSelectedTagObjects() {
        return this.state.persistentSelectedTags.map(name => {
            // First try to find in originalTags (all tags regardless of filters)
            let tag = this.state.originalTags.find(t => t['Product Name*'] === name);
            // If not found in originalTags, try current tags (filtered view)
            if (!tag) {
                tag = this.state.tags.find(t => t['Product Name*'] === name);
            }
            // If still not found, create minimal tag object to preserve selection
            if (!tag) {
                verboseLog(`Warning: Selected tag '${name}' not found in state, creating minimal object`);
                tag = {
                    'Product Name*': name,
                    'Product Brand': 'Unknown',
                    'Vendor': 'Unknown',
                    'Product Type*': 'Unknown',
                    'Lineage': 'MIXED'
                };
            }
            return tag;
        }).filter(Boolean);
    },

    clearInitialDataRetry() {
        if (this.state.initialDataRetryTimer) {
            clearTimeout(this.state.initialDataRetryTimer);
            this.state.initialDataRetryTimer = null;
        }
        this.state.initialDataAttempts = 0;
    },

    scheduleInitialDataRetry(reason = 'unknown') {
        const delays = Array.isArray(this.initialDataRetryDelays) && this.initialDataRetryDelays.length > 0
            ? this.initialDataRetryDelays
            : [2000];
        const maxAttempts = delays.length + 1;
        const attemptsSoFar = this.state.initialDataAttempts || 0;

        if (attemptsSoFar >= maxAttempts) {
            console.warn(`[InitialData] Max attempts (${maxAttempts}) reached; not scheduling retry. Last reason: ${reason}`);
            return;
        }

        if (this.state.initialDataRetryTimer) {
            clearTimeout(this.state.initialDataRetryTimer);
            this.state.initialDataRetryTimer = null;
        }

        const delayIndex = Math.max(0, Math.min(attemptsSoFar - 1, delays.length - 1));
        const delay = delays[Math.max(0, delayIndex)] || 2000;
        const nextAttempt = attemptsSoFar + 1;

        verboseLog(`[InitialData] Scheduling retry ${nextAttempt}/${maxAttempts} in ${delay}ms (reason: ${reason})`);

        const self = this;
        this.state.initialDataRetryTimer = setTimeout(function() {
            self.state.initialDataRetryTimer = null;
            verboseLog(`[InitialData] Retrying initial data load (attempt ${(self.state.initialDataAttempts || 0) + 1}/${maxAttempts})`);
            self.checkForExistingData();
        }, delay);
    },

    refreshAfterStoreChange(storeValue) {
        verboseLog(`[STORE] Refreshing UI for store ${storeValue}`);
        try {
            this.state.selectedTags = new Set();
            this.state.persistentSelectedTags = [];
            this.state.tags = [];
            this.state.originalTags = [];
            this.state.isProcessingDeselection = false;
            this.state.loading = true;
            this.state.initialized = false;
            this.state.filterCache = null;

            const availableContainer = document.getElementById('availableTags');
            const selectedContainer = document.getElementById('selectedTags');
            if (availableContainer) availableContainer.innerHTML = '';
            if (selectedContainer) selectedContainer.innerHTML = '';

            if (typeof this.showActionSplash === 'function') {
                this.showActionSplash(`Loading ${storeValue.replace(/_/g, ' ')} tags...`);
            }

            this.clearInitialDataRetry();
            this.state.initialDataAttempts = 0;

            let loadPromise;
            if (typeof this.checkForExistingData === 'function') {
                loadPromise = this.checkForExistingData();
            } else {
                loadPromise = Promise.allSettled([
                    this.fetchAndUpdateAvailableTags(),
                    this.fetchAndUpdateSelectedTags(),
                    this.fetchAndPopulateFilters()
                ]);
            }

            return Promise.resolve(loadPromise)
                .catch(error => {
                    console.error('refreshAfterStoreChange failed', error);
                    verboseLog('refreshAfterStoreChange error:', error);
                    if (typeof this.checkForExistingData === 'function') {
                        return this.checkForExistingData();
                    }
                    return false;
                })
                .finally(() => {
                    if (typeof this.hideActionSplash === 'function') {
                        this.hideActionSplash();
                    }
                    if (typeof this.hideEnhancedGenerationSplash === 'function') {
                        this.hideEnhancedGenerationSplash();
                    }
                    this.state.loading = false;
                });
        } catch (err) {
            console.error('refreshAfterStoreChange encountered an exception', err);
            if (typeof this.hideActionSplash === 'function') {
                this.hideActionSplash();
            }
            this.state.loading = false;
            return Promise.resolve(false);
        }
    },

    // Function to update brand filter label based on product type
    updateBrandFilterLabel() {
        const brandFilterLabel = document.querySelector('label[for="brandFilter"]');
        if (brandFilterLabel) {
            brandFilterLabel.textContent = 'Brand';
            brandFilterLabel.setAttribute('aria-label', 'Brand Filter');
        }
    },

    saveSelectionState(actionType = 'checkbox_selection', extraPayload = {}) {
        try {
            const payload = JSON.stringify({
                action_type: actionType,
                ...extraPayload
            });
            
            if (navigator.sendBeacon) {
                const blob = new Blob([payload], { type: 'application/json' });
                navigator.sendBeacon('/api/save-selection-state', blob);
            } else {
                fetch('/api/save-selection-state', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: payload,
                    keepalive: true
                }).catch(error => {
                    console.warn('Failed to save selection state for undo (fetch):', error);
                });
            }
        } catch (error) {
            console.warn('Failed to save selection state for undo:', error);
        }
    },

    updateFilters(filters, preserveExistingValues = true) {
        if (!filters) return;
        
        // Debug log for filters
        verboseLog('Updating filters with:', filters, 'preserveExistingValues:', preserveExistingValues);
        
        // CRITICAL FIX: Check if all filters are empty and we're trying to preserve values
        // If so, skip the update to prevent clearing user's selections
        const allEmpty = Object.values(filters).every(arr => !arr || arr.length === 0);
        if (allEmpty && preserveExistingValues) {
            // Check if user has any filter selections
            const hasFilterSelections = Array.from(document.querySelectorAll('select[id*="Filter"]')).some(select => select.value && select.value.trim() !== '');
            if (hasFilterSelections) {
                verboseLog('⏭️ Skipping filter update - all filters empty but user has selections to preserve');
                return;
            }
        }
        
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
            weight: 'weightFilter',
            doh: 'dohFilter',
            highCbd: 'highCbdFilter'
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
            
            verboseLog(`Updating ${filterId} with values:`, sortedValues);
            
            // Special debug for weight filter
            if (filterType === 'weight') {
                verboseLog('Weight filter values (first 10):', sortedValues.slice(0, 10));
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
            
            // Handle value restoration based on preserveExistingValues parameter
            if (preserveExistingValues) {
                // Preserve existing value if it's still valid, or keep it even if not in current options
                if (currentValue && currentValue.trim() !== '') {
                    if (sortedValues.includes(currentValue)) {
                        // Value is still valid, restore it
                        filterElement.value = currentValue;
                    } else {
                        // Value is no longer in current options, but preserve it by adding it back
                        verboseLog(`Preserving filter value "${currentValue}" for ${filterId} even though it's not in current options`);
                        const option = document.createElement('option');
                        option.value = currentValue;
                        option.textContent = currentValue;
                        option.style.color = '#666'; // Gray out to indicate it's not currently available
                        filterElement.appendChild(option);
                        filterElement.value = currentValue;
                    }
                } else {
                    // CRITICAL FIX: Only clear filter if it's not a valid current value that the user selected
                    if (currentValue && currentValue.trim() !== '') {
                        verboseLog(`⚠️ Filter value "${currentValue}" not in sorted values, keeping it anyway`);
                        const option = document.createElement('option');
                        option.value = currentValue;
                        option.textContent = currentValue;
                        option.style.color = '#666';
                        filterElement.appendChild(option);
                        filterElement.value = currentValue;
                    } else {
                        filterElement.value = '';
                    }
                }
            } else {
                // Only restore if value is still valid (for explicit filter clearing)
                if (currentValue && sortedValues.includes(currentValue)) {
                    filterElement.value = currentValue;
                } else {
                    // CRITICAL FIX: Only clear filter if it's not a valid current value that the user selected
                    if (currentValue && currentValue.trim() !== '') {
                        verboseLog(`⚠️ Filter value "${currentValue}" not in sorted values (explicit), keeping it anyway`);
                        const option = document.createElement('option');
                        option.value = currentValue;
                        option.textContent = currentValue;
                        option.style.color = '#666';
                        filterElement.appendChild(option);
                        filterElement.value = currentValue;
                    } else {
                        filterElement.value = '';
                    }
                }
            }
        });
        
        // GUARANTEED FIX: Save current filter values to localStorage
        this.saveFiltersToStorage();
    },
    
    saveFiltersToStorage() {
        try {
            const filters = {
                vendor: document.getElementById('vendorFilter')?.value || '',
                brand: document.getElementById('brandFilter')?.value || '',
                productType: document.getElementById('productTypeFilter')?.value || '',
                lineage: document.getElementById('lineageFilter')?.value || '',
                weight: document.getElementById('weightFilter')?.value || '',
                doh: document.getElementById('dohFilter')?.value || '',
                highCbd: document.getElementById('highCbdFilter')?.value || ''
            };
            
            // Only save non-empty values (not 'All')
            const filtersToSave = {};
            Object.entries(filters).forEach(([key, value]) => {
                if (value && value.trim() !== '' && value !== 'All') {
                    filtersToSave[key] = value;
                }
            });
            
            if (Object.keys(filtersToSave).length > 0) {
                localStorage.setItem('agt_filters', JSON.stringify(filtersToSave));
                verboseLog('✅ Saved filters to localStorage:', filtersToSave);
            } else {
                // Clear saved filters if all are empty
                localStorage.removeItem('agt_filters');
            }
        } catch (error) {
            console.warn('Failed to save filters to localStorage:', error);
        }
    },
    
    loadFiltersFromStorage() {
        try {
            const saved = localStorage.getItem('agt_filters');
            if (saved) {
                const filters = JSON.parse(saved);
                verboseLog('✅ Loaded filters from localStorage:', filters);
                return filters;
            }
        } catch (error) {
            console.warn('Failed to load filters from localStorage:', error);
        }
        return null;
    },
    
    saveSelectedTagsToStorage() {
        try {
            if (this.state.persistentSelectedTags && this.state.persistentSelectedTags.length > 0) {
                localStorage.setItem('agt_selected_tags', JSON.stringify(this.state.persistentSelectedTags));
                verboseLog('✅ Saved selected tags to localStorage:', this.state.persistentSelectedTags.length);
            } else {
                localStorage.removeItem('agt_selected_tags');
            }
        } catch (error) {
            console.warn('Failed to save selected tags to localStorage:', error);
        }
    },
    
    loadSelectedTagsFromStorage() {
        try {
            const saved = localStorage.getItem('agt_selected_tags');
            if (saved) {
                const tags = JSON.parse(saved);
                if (Array.isArray(tags) && tags.length > 0) {
                    verboseLog('✅ Loaded selected tags from localStorage:', tags.length);
                    return tags;
                }
            }
        } catch (error) {
            console.warn('Failed to load selected tags from localStorage:', error);
        }
        return null;
    },

    async updateFilterOptions() {
        try {
            verboseLog('🔍 updateFilterOptions() called');
            console.trace('Call stack for updateFilterOptions');
            
            // CRITICAL FIX: Don't update filter options during tag deselection to prevent clearing user's filters
            if (this.state.isProcessingDeselection) {
                verboseLog('🚫 SKIPPING updateFilterOptions - currently processing deselection');
                return;
            }
            
            // Fast path: skip if no original options (Mac-like speed)
            if (!this.state.originalFilterOptions.vendor) {
                return;
            }
            
            // Get current filter values (minimal)
            const currentFilters = {
                vendor: document.getElementById('vendorFilter')?.value || '',
                brand: document.getElementById('brandFilter')?.value || '',
                productType: document.getElementById('productTypeFilter')?.value || '',
                lineage: document.getElementById('lineageFilter')?.value || '',
                weight: document.getElementById('weightFilter')?.value || '',
                doh: document.getElementById('dohFilter')?.value || '',
                highCbd: document.getElementById('highCbdFilter')?.value || ''
            };

            // Get the currently filtered tags to determine available options
            const tagsToFilter = this.state.originalTags.length > 0 ? this.state.originalTags : this.state.tags;
            
            // Check if only vendor filter is selected (no other filters)
            const hasVendorFilter = currentFilters.vendor && currentFilters.vendor.trim() !== '' && currentFilters.vendor.toLowerCase() !== 'all';
            const hasOtherFilters = Object.entries(currentFilters).some(([key, value]) => 
                key !== 'vendor' && value && value.trim() !== '' && value.toLowerCase() !== 'all'
            );
            
            // If only vendor filter is selected, don't limit dropdown options - use original tags
            const shouldLimitOptions = hasOtherFilters || !hasVendorFilter;
            
            // Apply current filters to get the subset of tags that would be shown
            const filteredTags = shouldLimitOptions ? tagsToFilter.filter(tag => {
                // Check vendor filter - only apply if not empty and not "All"
                if (currentFilters.vendor && currentFilters.vendor.trim() !== '' && currentFilters.vendor.toLowerCase() !== 'all') {
                    const tagVendor = (tag.Vendor || tag.vendor || '').toString().trim();
                    if (tagVendor.toLowerCase() !== currentFilters.vendor.toLowerCase()) {
                        return false;
                    }
                }
                
                // Check brand filter - only apply if not empty and not "All"
                if (currentFilters.brand && currentFilters.brand.trim() !== '' && currentFilters.brand.toLowerCase() !== 'all') {
                    const tagBrand = (tag['Product Brand'] || tag.productBrand || '').toString().trim();
                    if (tagBrand.toLowerCase() !== currentFilters.brand.toLowerCase()) {
                        return false;
                    }
                }
                
                // Check product type filter - only apply if not empty and not "All"
                if (currentFilters.productType && currentFilters.productType.trim() !== '' && currentFilters.productType.toLowerCase() !== 'all') {
                    const tagProductType = (tag['Product Type*'] || tag.productType || '').toString().trim();
                    const normalizedTagProductType = normalizeProductType(tagProductType);
                    if (normalizedTagProductType.toLowerCase() !== currentFilters.productType.toLowerCase()) {
                        return false;
                    }
                }
                
                // Check lineage filter - only apply if not empty and not "All"
                if (currentFilters.lineage && currentFilters.lineage.trim() !== '' && currentFilters.lineage.toLowerCase() !== 'all') {
                    const tagLineage = (tag.currentLineage || tag.canonical_lineage || tag.Lineage || tag.lineage || '').toString().trim();
                    if (tagLineage.toLowerCase() !== currentFilters.lineage.toLowerCase()) {
                        return false;
                    }
                }
                
                // Check weight filter - only apply if not empty and not "All"
                if (currentFilters.weight && currentFilters.weight.toString().trim() !== '' && currentFilters.weight.toString().toLowerCase() !== 'all') {
                    // Get the tag's weight in multiple possible formats
                    const tagWeight = (tag['Weight*'] || tag.weight || '').toString().trim();
                    const tagWeightWithUnits = (tag.weightWithUnits || tag.WeightUnits || '').toString().trim();
                    const tagUnits = (tag.Units || '').toString().trim();
                    
                    // Create a normalized weight string for comparison
                    let normalizedTagWeight = '';
                    if (tagWeight && tagUnits) {
                        normalizedTagWeight = `${tagWeight}${tagUnits}`.toLowerCase();
                    } else if (tagWeightWithUnits) {
                        normalizedTagWeight = tagWeightWithUnits.toLowerCase();
                    } else if (tagWeight) {
                        normalizedTagWeight = tagWeight.toLowerCase();
                    }
                    
                    const filterWeight = currentFilters.weight.toString().trim().toLowerCase();
                    
                    // Check if any of the weight representations match the filter
                    const weightMatches = [
                        normalizedTagWeight,
                        tagWeight.toLowerCase(),
                        tagWeightWithUnits.toLowerCase(),
                        tagUnits.toLowerCase()
                    ].some(weight => weight === filterWeight);
                    
                    if (!weightMatches) {
                        return false;
                    }
                }
                
                // Check DOH filter - only apply if not empty and not "All"
                if (currentFilters.doh && currentFilters.doh.trim() !== '' && currentFilters.doh.toLowerCase() !== 'all') {
                    const tagDoh = (tag.DOH || tag.doh || '').toString().trim().toUpperCase();
                    const filterDoh = currentFilters.doh.toString().trim().toUpperCase();
                    if (tagDoh !== filterDoh) {
                        return false;
                    }
                }
                
                // Check High CBD filter - only apply if not empty and not "All"
                if (currentFilters.highCbd && currentFilters.highCbd.trim() !== '' && currentFilters.highCbd.toLowerCase() !== 'all') {
                    const tagProductType = (tag.productType || tag['Product Type*'] || '').toString().trim().toLowerCase();
                    const isHighCbd = tagProductType.startsWith('high cbd');
                    
                    if (currentFilters.highCbd === 'High CBD Products' && !isHighCbd) {
                        return false;
                    } else if (currentFilters.highCbd === 'Non-High CBD Products' && isHighCbd) {
                        return false;
                    }
                }
                
                return true;
            }) : tagsToFilter;

            // Build hash for caching/comparison
            const tagsHash = [
                tagsToFilter.length,
                filteredTags.length,
                currentFilters.vendor || '',
                currentFilters.brand || '',
                currentFilters.productType || '',
                currentFilters.lineage || '',
                currentFilters.weight || '',
                currentFilters.doh || '',
                currentFilters.highCbd || ''
            ].join('|');
            
            // Extract available options from filtered tags
            const availableOptions = {
                vendor: new Set(),
                brand: new Set(),
                productType: new Set(),
                lineage: new Set(),
                weight: new Set(),
                doh: new Set(),
                highCbd: new Set()
            };

            // USER PREFERENCE: Always show ALL options for vendor, brand, productType, lineage, doh, highCbd
            // Only filter weight options based on selections
            // This makes it easier to change filters without going back to "All"
            
            // Use ORIGINAL tags for most filters (not filtered tags)
            const tagsForOptions = tagsToFilter; // Use full tag list
            
            // PERFORMANCE: Process tags efficiently - optimize CBD detection
            for (let i = 0; i < tagsForOptions.length; i++) {
                const tag = tagsForOptions[i];
                
                // Always add vendor options (show all vendors)
                const vendor = (tag.Vendor || tag.vendor || '').toString().trim();
                if (vendor) availableOptions.vendor.add(vendor);
                
                // Always add brand options (show all brands)
                const brand = (tag['Product Brand'] || tag.productBrand || '').toString().trim();
                if (brand) availableOptions.brand.add(brand);
                
                // Always add product type options (show all types)
                const productType = (tag['Product Type*'] || tag.productType || '').toString().trim();
                if (productType) {
                    const normalizedType = normalizeProductType(productType);
                    if (normalizedType) availableOptions.productType.add(normalizedType);
                }
                
                // Always add lineage options (show all lineages)
                const rawLineage = (tag.canonical_lineage || tag.currentLineage || tag.Lineage || tag.lineage || '').toString().trim();
                if (rawLineage) {
                    availableOptions.lineage.add(rawLineage);
                }
                
                // PERFORMANCE: Optimize CBD flag detection - single pass with early exit
                const nameLower = (tag['Product Name*'] || tag.ProductName || '').toString().toLowerCase();
                const typeLower = (tag['Product Type*'] || tag.productType || '').toString().toLowerCase();
                const hasCbdFlag = (rawLineage && (rawLineage.toLowerCase().includes('cbd') || rawLineage.toLowerCase().includes('cbg') || rawLineage.toLowerCase().includes('cbn') || rawLineage.toLowerCase().includes('cbc'))) ||
                    nameLower.includes('cbd') || nameLower.includes('cbg') || nameLower.includes('cbn') || nameLower.includes('cbc') ||
                    typeLower.includes('high cbd') || typeLower.includes('cbd');
                if (hasCbdFlag) {
                    availableOptions.lineage.add('CBD_BLEND');
                }
                
                // Always add DOH options (show all)
                const doh = (tag.DOH || tag.doh || '').toString().trim();
                if (doh) availableOptions.doh.add(doh);
                
                // Always add high CBD options (show all)
                if (typeLower.startsWith('high cbd')) {
                    availableOptions.highCbd.add('High CBD Products');
                } else if (typeLower) {
                    availableOptions.highCbd.add('Non-High CBD Products');
                }
            }
            
            // WEIGHT FILTER: Use filtered tags (user preference - weight should be context-aware)
            // Only show weights that are available given current filter selections
            for (let i = 0; i < filteredTags.length; i++) {
                const tag = filteredTags[i];
                // CRITICAL FIX: Check all possible weight field variations for options generation
                const combined = (tag.weightWithUnits || tag.WeightWithUnits || tag.WeightUnits || 
                                tag.CombinedWeight || tag['Weight*'] || tag.weight);
                if (combined) {
                    const combinedStr = combined.toString().trim();
                    if (combinedStr) availableOptions.weight.add(combinedStr);
                }
            }
            
            // PERFORMANCE: Cache the extracted options for future use
            this._cachedFilterOptions = availableOptions;
            this._cachedFilterOptionsHash = tagsHash;
            this._cachedFilterOptionsTagsLength = tagsToFilter.length;

            // PERFORMANCE: Defer DOM updates to next frame to avoid blocking
            requestAnimationFrame(() => {
                this._updateFilterDropdowns(availableOptions, currentFilters);
            });
        } catch (error) {
            console.error('Error updating filter options:', error);
        }
    },

    _applyCachedFilterOptions() {
        // Get current filter values
        const currentFilters = {
            vendor: document.getElementById('vendorFilter')?.value || '',
            brand: document.getElementById('brandFilter')?.value || '',
            productType: document.getElementById('productTypeFilter')?.value || '',
            lineage: document.getElementById('lineageFilter')?.value || '',
            weight: document.getElementById('weightFilter')?.value || '',
            doh: document.getElementById('dohFilter')?.value || '',
            highCbd: document.getElementById('highCbdFilter')?.value || ''
        };
        
        // Get filtered tags for weight filter
        const tagsToFilter = this.state.originalTags.length > 0 ? this.state.originalTags : this.state.tags;
        const hasVendorFilter = currentFilters.vendor && currentFilters.vendor.trim() !== '' && currentFilters.vendor.toLowerCase() !== 'all';
        const hasOtherFilters = Object.entries(currentFilters).some(([key, value]) => 
            key !== 'vendor' && value && value.trim() !== '' && value.toLowerCase() !== 'all'
        );
        const shouldLimitOptions = hasOtherFilters || !hasVendorFilter;
        
        // Apply filters to get weight options
        const filteredTags = shouldLimitOptions ? tagsToFilter.filter(tag => {
            if (currentFilters.vendor && currentFilters.vendor.trim() !== '' && currentFilters.vendor.toLowerCase() !== 'all') {
                const tagVendor = (tag.Vendor || tag.vendor || '').toString().trim();
                if (tagVendor.toLowerCase() !== currentFilters.vendor.toLowerCase()) return false;
            }
            if (currentFilters.brand && currentFilters.brand.trim() !== '' && currentFilters.brand.toLowerCase() !== 'all') {
                const tagBrand = (tag['Product Brand'] || tag.productBrand || '').toString().trim();
                if (tagBrand.toLowerCase() !== currentFilters.brand.toLowerCase()) return false;
            }
            if (currentFilters.productType && currentFilters.productType.trim() !== '' && currentFilters.productType.toLowerCase() !== 'all') {
                const tagProductType = (tag['Product Type*'] || tag.productType || '').toString().trim();
                const normalizedTagProductType = normalizeProductType(tagProductType);
                if (normalizedTagProductType.toLowerCase() !== currentFilters.productType.toLowerCase()) return false;
            }
            if (currentFilters.lineage && currentFilters.lineage.trim() !== '' && currentFilters.lineage.toLowerCase() !== 'all') {
                const tagLineage = (tag.canonical_lineage || tag.currentLineage || tag.Lineage || tag.lineage || '').toString().trim();
                if (tagLineage.toLowerCase() !== currentFilters.lineage.toLowerCase()) return false;
            }
            return true;
        }) : tagsToFilter;
        
        // Extract weight options from filtered tags
        const weightOptions = new Set();
        for (let i = 0; i < filteredTags.length; i++) {
            const tag = filteredTags[i];
            const combined = (tag.weightWithUnits || tag.WeightWithUnits || tag.WeightUnits || 
                            tag.CombinedWeight || tag['Weight*'] || tag.weight);
            if (combined) {
                const combinedStr = combined.toString().trim();
                if (combinedStr) weightOptions.add(combinedStr);
            }
        }
        
        const availableOptions = { ...this._cachedFilterOptions, weight: weightOptions };
        this._updateFilterDropdowns(availableOptions, currentFilters);
    },

    _updateFilterDropdowns(availableOptions, currentFilters) {
        const filterFieldMap = {
            vendor: 'vendorFilter',
            brand: 'brandFilter',
            productType: 'productTypeFilter',
            lineage: 'lineageFilter',
            weight: 'weightFilter',
            doh: 'dohFilter',
            highCbd: 'highCbdFilter'
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
                            const displayValue = filterType === 'productType' ? formatProductTypeLabel(value) : value;
                            if (filterType === 'productType' && value === 'rso/co2 tankers') {
                                return `<option value="${value}" style="font-weight: bold; font-style: italic; color: #a084e8;">${displayValue}</option>`;
                            }
                            return `<option value="${value}">${displayValue}</option>`;
                        }).join('')}
                    `;
                    
                    // Update the dropdown options
                    filterElement.innerHTML = optionsHtml;
                    
                    // Try to restore the previous selection if it's still valid
                    if (currentValue && sortedOptions.includes(currentValue)) {
                        filterElement.value = currentValue;
                    } else {
                        // CRITICAL FIX: Only clear filter if it's not a valid current value that the user selected
                        // Don't clear just because it's not in the filtered options - preserve user's intent
                        if (currentValue && currentValue.trim() !== '') {
                            verboseLog(`⚠️ Filter value "${currentValue}" not in filtered options, keeping it anyway`);
                            // Add the current value back if it's not empty and user has selected it
                            const option = document.createElement('option');
                            option.value = currentValue;
                            option.textContent = filterType === 'productType' ? formatProductTypeLabel(currentValue) : currentValue;
                            option.style.color = '#666'; // Gray out to indicate it's not currently available
                            filterElement.appendChild(option);
                            filterElement.value = currentValue;
                        } else {
                            filterElement.value = '';
                        }
                    }
                }
            });
    },

    applyFilters(immediate = false) {
        verboseLog(`🔍 applyFilters() called (immediate: ${immediate})`);
        // USER PREFERENCE: Scroll to top when filter is applied (don't preserve position)
        // Fast path: show all if no filters (Mac-like speed)
        const vendorFilter = document.getElementById('vendorFilter')?.value || '';
        const brandFilter = document.getElementById('brandFilter')?.value || '';
        const productTypeFilter = document.getElementById('productTypeFilter')?.value || '';
        const lineageFilter = document.getElementById('lineageFilter')?.value || '';
        const weightFilter = document.getElementById('weightFilter')?.value || '';
        const dohFilter = document.getElementById('dohFilter')?.value || '';
        const highCbdFilter = document.getElementById('highCbdFilter')?.value || '';
        
        verboseLog('🔍 Current filter values:', { vendorFilter, brandFilter, productTypeFilter, lineageFilter, weightFilter, dohFilter, highCbdFilter });
        
        // Check if all filters are "All" - show everything (fast path)
        const allFiltersAll = [vendorFilter, brandFilter, productTypeFilter, lineageFilter, weightFilter, dohFilter, highCbdFilter]
            .every(filter => !filter || filter.trim() === '' || filter.toLowerCase() === 'all');
        
        verboseLog('🔍 All filters empty?', allFiltersAll);
        
        if (allFiltersAll) {
            verboseLog('🔍 All filters empty - showing all tags');
            this.state.filterCache = null;
            // Use immediate update if requested, otherwise debounced
            if (immediate) {
                this._updateAvailableTags(this.state.originalTags, null);
            } else {
                this.debouncedUpdateAvailableTags(this.state.originalTags, null);
            }
            this.renderActiveFilters();
            // USER PREFERENCE: Scroll to top after clearing filters
            requestAnimationFrame(() => {
                this._scrollAvailableTagsToTop();
            });
            return;
        }
        
        // Create a unique key for the current filter combination
        const filterKey = [
            vendorFilter || '',
            brandFilter || '',
            productTypeFilter || '',
            lineageFilter || '',
            weightFilter || '',
            dohFilter || '',
            highCbdFilter || ''
        ].join('|');
        
        // Check if we have cached results for this exact filter combination
        if (this.state.filterCache && this.state.filterCache.key === filterKey) {
            // Always pass original tags to preserve persistent selections
            // Use immediate update if requested, otherwise debounced
            if (immediate) {
                this._updateAvailableTags(this.state.originalTags, this.state.filterCache.result);
            } else {
                this.debouncedUpdateAvailableTags(this.state.originalTags, this.state.filterCache.result);
            }
            this.renderActiveFilters();
            // USER PREFERENCE: Scroll to top after applying cached filter
            requestAnimationFrame(() => {
                this._scrollAvailableTagsToTop();
            });
            return;
        }
        
        // Filter the tags based on current filter values using original tags
        // Ensure we always use originalTags for filtering to preserve the full dataset
        const tagsToFilter = this.state.originalTags.length > 0 ? this.state.originalTags : this.state.tags;
        
        // If we don't have original tags, we can't filter properly
        if (this.state.originalTags.length === 0) {
            console.warn('No original tags available for filtering');
            return;
        }
        
        verboseLog('applyFilters - tagsToFilter length:', tagsToFilter.length);
        verboseLog('applyFilters - first tag sample:', tagsToFilter[0]);
        
        const filteredTags = tagsToFilter.filter(tag => {
            // Check vendor filter - only apply if not empty and not "All"
            if (vendorFilter && vendorFilter.trim() !== '' && vendorFilter.toLowerCase() !== 'all') {
                const tagVendor = (tag.Vendor || tag.vendor || '').toString().trim();
                if (tagVendor.toLowerCase() !== vendorFilter.toLowerCase()) {
                    return false;
                }
            }
            
            // Check brand filter - only apply if not empty and not "All"
            if (brandFilter && brandFilter.trim() !== '' && brandFilter.toLowerCase() !== 'all') {
                const tagBrand = (tag['Product Brand'] || tag.productBrand || '').toString().trim();
                if (tagBrand.toLowerCase() !== brandFilter.toLowerCase()) {
                    return false;
                }
            }
            
            // Check product type filter - only apply if not empty and not "All"
            if (productTypeFilter && productTypeFilter.trim() !== '' && productTypeFilter.toLowerCase() !== 'all') {
                const tagProductType = (tag['Product Type*'] || tag.productType || '').toString().trim();
                const normalizedTagProductType = normalizeProductType(tagProductType);
                
                // DEBUG: Log product type filtering details
                verboseLog('🔍 Product Type Filtering Debug:', {
                    tagProductType: tagProductType,
                    normalizedTagProductType: normalizedTagProductType,
                    productTypeFilter: productTypeFilter,
                    match: normalizedTagProductType.toLowerCase() === productTypeFilter.toLowerCase()
                });
                
                if (normalizedTagProductType.toLowerCase() !== productTypeFilter.toLowerCase()) {
                    return false;
                }
            }
            
            // Check lineage filter - only apply if not empty and not "All"
            if (lineageFilter && lineageFilter.trim() !== '' && lineageFilter.toLowerCase() !== 'all') {
                const tagLineage = (tag.currentLineage || tag.canonical_lineage || tag.Lineage || tag.lineage || '').toString().trim();
                if (tagLineage.toLowerCase() !== lineageFilter.toLowerCase()) {
                    return false;
                }
            }
            
            // Check weight filter - only apply if not empty and not "All"
            if (weightFilter && weightFilter.trim() !== '' && weightFilter.toLowerCase() !== 'all') {
                // Get the tag's weight in multiple possible formats
                const tagWeight = (tag['Weight*'] || tag.weight || '').toString().trim();
                // CRITICAL FIX: Check all possible weight field variations for filtering
                const tagWeightWithUnits = (tag.weightWithUnits || tag.WeightWithUnits || tag.WeightUnits || 
                                          tag.CombinedWeight || tag.weightWithUnits || '').toString().trim();
                const tagUnits = (tag.Units || '').toString().trim();
                
                // Create a normalized weight string for comparison
                let normalizedTagWeight = '';
                if (tagWeight && tagUnits) {
                    normalizedTagWeight = `${tagWeight}${tagUnits}`.toLowerCase();
                } else if (tagWeightWithUnits) {
                    normalizedTagWeight = tagWeightWithUnits.toLowerCase();
                } else if (tagWeight) {
                    normalizedTagWeight = tagWeight.toLowerCase();
                }
                
                const filterWeight = weightFilter.toString().trim().toLowerCase();
                
                // Check if any of the weight representations match the filter
                const weightMatches = [
                    normalizedTagWeight,
                    tagWeight.toLowerCase(),
                    tagWeightWithUnits.toLowerCase(),
                    tagUnits.toLowerCase()
                ].some(weight => weight === filterWeight);
                
                if (!weightMatches) {
                    return false;
                }
            }
            
            // Check DOH filter - only apply if not empty and not "All"
            if (dohFilter && dohFilter.trim() !== '' && dohFilter.toLowerCase() !== 'all') {
                const tagDoh = (tag.DOH || tag.doh || '').toString().trim().toUpperCase();
                const filterDoh = dohFilter.toString().trim().toUpperCase();
                if (tagDoh !== filterDoh) {
                    return false;
                }
            }
            
            // Check High CBD filter - only apply if not empty and not "All"
            if (highCbdFilter && highCbdFilter.trim() !== '' && highCbdFilter.toLowerCase() !== 'all') {
                const tagProductType = (tag.productType || tag['Product Type*'] || '').toString().trim().toLowerCase();
                const isHighCbd = tagProductType.startsWith('high cbd');
                
                if (highCbdFilter === 'High CBD Products' && !isHighCbd) {
                    return false;
                } else if (highCbdFilter === 'Non-High CBD Products' && isHighCbd) {
                    return false;
                }
            }
            
            return true;
        });
        
        // DEBUG: Log filtering results
        verboseLog('🔍 Filtering Results:', {
            originalTagsCount: tagsToFilter.length,
            filteredTagsCount: filteredTags.length,
            productTypeFilter: productTypeFilter,
            prerollTags: filteredTags.filter(tag => {
                const tagProductType = (tag['Product Type*'] || tag.productType || '').toString().trim();
                const normalizedType = normalizeProductType(tagProductType);
                return normalizedType.toLowerCase() === 'pre-roll';
            }).length
        });
        
        // Cache the results
        this.state.filterCache = {
            key: filterKey,
            result: filteredTags
        };
        
        // Always pass original tags to preserve persistent selections, with filtered tags for display
        // Use immediate update if requested (for filter changes), otherwise debounced (for search)
        if (immediate) {
            // Immediate update for instant filter response
            this._updateAvailableTags(this.state.originalTags, filteredTags);
        } else {
            // Debounced update for search and other operations
            this.debouncedUpdateAvailableTags(this.state.originalTags, filteredTags);
        }
        
        // Update selected tags to also respect the current filters
        const selectedTagObjects = this.state.persistentSelectedTags.map(name => {
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
        // USER PREFERENCE: Scroll to top after filter update
        requestAnimationFrame(() => {
            this._scrollAvailableTagsToTop();
        });
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
            this.state.isSearching = false;
            return true;
        }

        // Filter tags: only match product name
        const filteredTags = tags.filter(tag => {
            const tagName = tag['Product Name*'] || '';
            return tagName.toLowerCase().includes(searchTerm);
        });

        // Update the list with only matching tags
        if (listId === 'availableTags') {
            this.debouncedUpdateAvailableTags(this.state.originalTags, filteredTags);
            // Scroll to top of available tags list after search
            setTimeout(() => {
                const availableTagsContainer = document.getElementById('availableTags');
                if (availableTagsContainer) {
                    availableTagsContainer.scrollTop = 0;
                }
            }, 50);
            // Ensure groups are expanded while searching
            setTimeout(() => {
                this.expandAllTagGroups();
            }, 120);
        } else if (listId === 'selectedTags') {
            this.updateSelectedTags(filteredTags);
            // Scroll to top of selected tags list after search
            setTimeout(() => {
                const selectedTagsContainer = document.getElementById('selectedTags');
                if (selectedTagsContainer) {
                    selectedTagsContainer.scrollTop = 0;
                }
            }, 50);
        }
        searchInput.classList.add('search-active');
        this.state.isSearching = true;

        // Return boolean indicating whether any tags match the search
        return filteredTags.length > 0;
    },

    handleAvailableTagsSearch(event) {
        return this.handleSearch('availableTags', 'availableTagsSearch');
    },

    handleSelectedTagsSearch(event) {
        return this.handleSearch('selectedTags', 'selectedTagsSearch');
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
        
        // CRITICAL FIX: For JSON matched tags, skip deduplication entirely
        // The backend already handles deduplication correctly, so we preserve all products
        const seenProductKeys = new Set();
        const uniqueTags = tags.filter(tag => {
            // Check if this is a JSON matched product
            const isJsonMatched = tag.Source && tag.Source.includes('JSON Match');
            
            if (isJsonMatched) {
                // For JSON matched products, skip deduplication entirely
                // The backend already ensures we have unique original JSON items
                verboseLog(`✅ JSON MATCH: Preserving hierarchical organization for: ${tag['Product Name*'] || tag.ProductName || 'Unknown'}`);
                verboseLog(`   Vendor: ${tag.vendor || tag['Vendor'] || tag['Vendor/Supplier*'] || 'Not Set'}`);
                verboseLog(`   Brand: ${tag.productBrand || tag['Product Brand'] || tag.ProductBrand || 'Not Set'}`);
                verboseLog(`   Type: ${tag.productType || tag['Product Type*'] || 'Not Set'}`);
                verboseLog(`   Weight: ${tag.weightWithUnits || tag.weight || 'Not Set'}`);
                return true;
            } else {
                // For regular products, use the existing deduplication logic
                const productName = tag['Product Name*'] || tag.ProductName || tag.Description || '';
                const vendor = tag.vendor || tag['Vendor'] || tag['Vendor/Supplier*'] || '';
                const brand = tag.productBrand || tag['Product Brand'] || tag['ProductBrand'] || '';
                const weight = (tag.weight || tag['Weight*'] || tag['Weight'] || tag['WeightUnits'] || '').toString().trim();
                
                // Create a unique key that includes vendor/brand/weight to allow same product names with different weights
                const productKey = `${productName}|${vendor}|${brand}|${weight}`;
                
                if (seenProductKeys.has(productKey)) {
                    console.debug(`Skipping exact duplicate product in organizeBrandCategories: ${productKey}`);
                    return false;
                }
                seenProductKeys.add(productKey);
                return true;
            }
        });
        
        // Debug: Log the first few tags to see their structure
        if (uniqueTags.length > 0) {
            verboseLog('First tag structure:', uniqueTags[0]);
        }
        
        uniqueTags.forEach(tag => {
            // Use the correct field names from the tag object - check multiple possible field names
            let vendor = tag.vendor || tag['Vendor'] || tag['Vendor/Supplier*'] || tag['Vendor/Supplier'] || '';
            let brand = tag.productBrand || tag['Product Brand'] || tag['ProductBrand'] || this.extractBrand(tag) || '';
            const rawProductType = tag.productType || tag['Product Type*'] || tag['Product Type'] || '';
            const normalizedProductType = normalizeProductType(rawProductType.trim());
            const productType = VALID_PRODUCT_TYPES.includes(normalizedProductType.toLowerCase())
              ? normalizedProductType.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(' ')
              : 'Unknown Type';
            const lineage = tag.currentLineage || tag.canonical_lineage || tag.Lineage || tag.lineage || 'MIXED';
            const weight = (tag.weight || tag['Weight*'] || tag['Weight'] || tag['WeightUnits'] || '').toString().trim();
            // CRITICAL FIX: Ensure weightWithUnits is properly populated from multiple possible sources
            const weightWithUnits = (tag.weightWithUnits || tag.WeightWithUnits || tag.WeightUnits || 
                                   tag.CombinedWeight || tag.weightWithUnits || weight || '').toString().trim();

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

            // Determine subcategory for vape products
            const productName = (tag['Product Name*'] || tag.ProductName || tag.Description || '').toString().toLowerCase();
            let subcategory = null;
            
            // Check if this is a vape product that should be categorized
            const isVapeProduct = productType.toLowerCase().includes('vape') || productType.toLowerCase().includes('cartridge');
            
            if (isVapeProduct) {
                if (productName.includes('cartridge')) {
                    subcategory = '510';
                } else if (productName.includes('disposable')) {
                    subcategory = 'Disposable';
                }
            }

            // Normalize the tag data
            const normalizedTag = {
                ...tag,
                vendor: this.capitalizeVendorName((vendor || '').toString().trim()),
                brand: this.capitalizeBrandName((brand || '').toString().trim()),
                productType: productType,
                subcategory: subcategory,
                lineage: (lineage || '').toString().trim().toUpperCase(), // always uppercase for color
                weight: weight,
                weightWithUnits: weightWithUnits,
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
            
            // For vape products with subcategory, add an intermediate subcategory level
            let targetGroups;
            if (normalizedTag.subcategory) {
                let subcategoryGroups = productTypeGroups.get(normalizedTag.productType);
                // Check if this is actually a Map (subcategory structure) or needs to be converted
                if (!(subcategoryGroups instanceof Map) || (subcategoryGroups.size > 0 && Array.from(subcategoryGroups.values())[0] instanceof Array)) {
                    // Need to restructure: convert existing weight groups to subcategory structure
                    const existingWeightGroups = subcategoryGroups;
                    subcategoryGroups = new Map();
                    // Migrate existing items to a default subcategory
                    if (existingWeightGroups instanceof Map && existingWeightGroups.size > 0) {
                        existingWeightGroups.forEach((tags, weight) => {
                            if (!subcategoryGroups.has('Other')) {
                                subcategoryGroups.set('Other', new Map());
                            }
                            subcategoryGroups.get('Other').set(weight, tags);
                        });
                    }
                    productTypeGroups.set(normalizedTag.productType, subcategoryGroups);
                }
                
                // Create subcategory group if it doesn't exist
                if (!subcategoryGroups.has(normalizedTag.subcategory)) {
                    subcategoryGroups.set(normalizedTag.subcategory, new Map());
                }
                targetGroups = subcategoryGroups.get(normalizedTag.subcategory);
            } else {
                // For non-subcategory products, check if we need to handle mixed structure
                let weightGroups = productTypeGroups.get(normalizedTag.productType);
                if (weightGroups instanceof Map && weightGroups.size > 0) {
                    // Check if first entry is a Map (subcategory structure) or Array (weight structure)
                    const firstValue = Array.from(weightGroups.values())[0];
                    if (firstValue instanceof Map) {
                        // This product type already has subcategory structure, add to 'Other'
                        if (!weightGroups.has('Other')) {
                            weightGroups.set('Other', new Map());
                        }
                        targetGroups = weightGroups.get('Other');
                    } else {
                        // This is still weight structure
                        targetGroups = weightGroups;
                    }
                } else {
                    targetGroups = weightGroups;
                }
            }

            // Create weight group if it doesn't exist - use weightWithUnits as the key
            if (!targetGroups.has(normalizedTag.weightWithUnits)) {
                targetGroups.set(normalizedTag.weightWithUnits, []);
            }
            targetGroups.get(normalizedTag.weightWithUnits).push(normalizedTag);
        });

        if (skippedTags > 0) {
            console.info(`Skipped ${skippedTags} tags due to missing vendor information`);
        }

        return vendorGroups;
    },

    // Compute likeness-based ordering helpers
    _getReferenceProductName() {
        try {
            const el = document.getElementById('searchProductName');
            const value = (el && typeof el.value === 'string') ? el.value.trim() : '';
            return value;
        } catch (e) {
            return '';
        }
    },

    _tokenizeName(name) {
        if (!name || typeof name !== 'string') return [];
        return name
            .toLowerCase()
            .replace(/\s+by\s+[^-()]+/g, ' ') // remove trailing "by Vendor"
            .replace(/\([^)]*\)/g, ' ')       // remove parenthetical vendor
            .split(/[^a-z0-9]+/g)
            .filter(Boolean);
    },

    _computeLikenessScore(tagName, refName) {
        if (!refName) return 0;
        const ref = (refName || '').toLowerCase();
        const name = (tagName || '').toLowerCase();
        if (!name) return 0;

        const refTokens = new Set(this._tokenizeName(refName));
        const nameTokens = new Set(this._tokenizeName(tagName));

        let overlap = 0;
        for (const t of refTokens) {
            if (nameTokens.has(t)) overlap += 1;
        }
        const denom = Math.min(refTokens.size || 1, nameTokens.size || 1);
        let score = denom > 0 ? overlap / denom : 0;

        // Substring and prefix bonuses
        if (name.includes(ref)) score += 0.25;
        if (name.startsWith(ref)) score += 0.15;

        return score;
    },

    _sortByLikenessIfRef(tagsArray) {
        const ref = this._getReferenceProductName();
        if (!ref) return tagsArray;
        try {
            const withScores = tagsArray.map(t => ({
                tag: t,
                s: this._computeLikenessScore((t && t['Product Name*']) || t?.ProductName || '', ref)
            }));
            withScores.sort((a, b) => {
                if (b.s !== a.s) return b.s - a.s;
                const an = (a.tag && (a.tag['Product Name*'] || a.tag.ProductName) || '').toString();
                const bn = (b.tag && (b.tag['Product Name*'] || b.tag.ProductName) || '').toString();
                return an.localeCompare(bn);
            });
            return withScores.map(x => x.tag);
        } catch (e) {
            return tagsArray;
        }
    },

    // Debounced version of updateAvailableTags to prevent multiple rapid calls
    debouncedUpdateAvailableTags: debounce(function(originalTags, filteredTags = null) {
        // CRITICAL FIX: Don't update available tags during deselection
        if (this.state.isProcessingDeselection) {
            verboseLog('🚫 SKIPPING debouncedUpdateAvailableTags - currently processing deselection');
            return;
        }
        
        // CRITICAL FIX: Don't clear the list if we're actively refreshing after lineage updates
        // Only skip if there's a pending refresh timeout (active lineage update operation)
        if (this._pendingLineageRefresh) {
            verboseLog('🚫 SKIPPING debouncedUpdateAvailableTags - lineage refresh in progress');
            return;
        }
        
        // Reduced logging to prevent console spam
        // verboseLog('debouncedUpdateAvailableTags called with:', {
        //     originalTagsLength: originalTags ? originalTags.length : 0,
        //     filteredTagsLength: filteredTags ? filteredTags.length : 0,
        //     originalTags: originalTags ? originalTags.slice(0, 2) : null,
        //     filteredTags: filteredTags ? filteredTags.slice(0, 2) : null
        // });
        
        // Show loading splash for tag population
        const tagsToShow = filteredTags || originalTags;
        if (tagsToShow && tagsToShow.length > 0) {
            this.showActionSplash('Loading tags...');
            
            // Show loading indicator in container IMMEDIATELY to prevent blank screen
            const availableTagsContainer = document.getElementById('availableTags');
            if (availableTagsContainer) {
                availableTagsContainer.innerHTML = `
                    <div class="text-center py-4">
                        <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-2 text-white">Loading tags...</p>
                    </div>
                `;
            }
        }
        
        // Use requestAnimationFrame to ensure smooth DOM updates
        requestAnimationFrame(() => {
            this._updateAvailableTags(originalTags, filteredTags);
        });
    }, 300),

    // Helpers to preserve scroll position of the available list across re-renders
    // USER PREFERENCE: Scroll CURRENT INVENTORY to top when filter is applied
    _scrollAvailableTagsToTop() {
        try {
            const availableTagsContainer = document.getElementById('availableTags');
            if (availableTagsContainer) {
                availableTagsContainer.scrollTop = 0;
                verboseLog('✅ Scrolled CURRENT INVENTORY to top after filter change');
            }
        } catch (error) {
            console.warn('Could not scroll to top:', error);
        }
    },

    _saveAvailableScrollPosition() {
        const container = document.getElementById('availableTags');
        if (!container) return null;
        const scrollTop = container.scrollTop;
        let anchorName = null;
        const items = container.querySelectorAll('.tag-item');
        for (const item of items) {
            if (item.offsetTop >= scrollTop) {
                anchorName = item.getAttribute('data-tag-name');
                break;
            }
        }
        return { scrollTop, anchorName };
    },
    _restoreAvailableScrollPosition(saved) {
        if (!saved) return;
        const container = document.getElementById('availableTags');
        if (!container) return;
        
        // Try immediate restoration first
        container.scrollTop = saved.scrollTop;
        
        // Then try after first paint with anchor fallback
        requestAnimationFrame(() => {
            container.scrollTop = saved.scrollTop;
            // Try anchor-based restoration if direct scroll didn't work well
            if (saved.anchorName) {
                const el = container.querySelector(`.tag-item[data-tag-name="${CSS.escape(saved.anchorName)}"]`);
                if (el) {
                    const currentScroll = container.scrollTop;
                    const targetScroll = el.offsetTop;
                    // If we're significantly off, use anchor
                    if (Math.abs(currentScroll - saved.scrollTop) > 50 || Math.abs(currentScroll - targetScroll) < Math.abs(currentScroll - saved.scrollTop)) {
                        container.scrollTop = targetScroll;
                    }
                }
            }
        });
        
        // Final attempt after a delay for slower DOM updates
        setTimeout(() => {
            const currentScroll = container.scrollTop;
            if (Math.abs(currentScroll - saved.scrollTop) > 100) {
                // Still far off, try again
                container.scrollTop = saved.scrollTop;
                // Final anchor attempt
                if (saved.anchorName) {
                    const el = container.querySelector(`.tag-item[data-tag-name="${CSS.escape(saved.anchorName)}"]`);
                    if (el) {
                        container.scrollTop = el.offsetTop;
                    }
                }
            }
        }, 150);
    },

    // CRITICAL FIX: Render JSON matched tags with SAME HIERARCHY as Selected Tags
    // Uses Vendor > Brand > Product Type > Weight organization
    renderJsonMatchedTags(tags) {
        verboseLog('✅ RENDERING JSON MATCHED TAGS WITH HIERARCHY, count:', tags.length);
        
        const availableTagsContainer = document.getElementById('availableTags');
        if (!availableTagsContainer) {
            console.error('Available tags container not found');
            return;
        }
        // Preserve scroll position during re-render
        const savedScroll = this._saveAvailableScrollPosition();

        // Clear existing content
        availableTagsContainer.innerHTML = '';

        // FIXED: Use hierarchical organization (SAME AS SELECTED TAGS)
        verboseLog('Organizing JSON matched tags hierarchically...');
        const groupedTags = this.organizeBrandCategories(tags);
        verboseLog('✅ JSON matched tags organized into hierarchy, vendor count:', groupedTags.size);

        // Create hierarchical structure (same as regular available tags)
        const tagList = document.createElement('div');
        tagList.className = 'tag-list';

        const sortedVendors = Array.from(groupedTags.entries())
            .sort(([a], [b]) => (a || '').localeCompare(b || ''));

        sortedVendors.forEach(([vendor, brandGroups]) => {
            const vendorSection = document.createElement('div');
            vendorSection.className = 'vendor-section mb-3';
            
            // Create vendor header with checkbox
            const vendorHeader = document.createElement('h5');
            vendorHeader.className = 'vendor-header mb-2 d-flex align-items-center cursor-pointer';
            vendorHeader.addEventListener('click', (e) => {
                if (e.target.type === 'checkbox') return;
                const vendorContent = vendorSection.querySelector('.vendor-content');
                const isCollapsed = vendorContent.classList.contains('collapsed');
                vendorContent.classList.toggle('collapsed', !isCollapsed);
                vendorHeader.querySelector('.collapse-icon').textContent = isCollapsed ? '▼' : '▶';
            });
            
            const vendorCheckbox = document.createElement('input');
            vendorCheckbox.type = 'checkbox';
            vendorCheckbox.className = 'select-all-checkbox me-2';
            vendorCheckbox.addEventListener('change', (e) => {
                // PERFORMANCE: Skip during bulk clear operations
                if (this.state.isClearing) {
                    return;
                }
                const savedScroll = this._saveAvailableScrollPosition();
                const isChecked = e.target.checked;
                const checkboxes = vendorSection.querySelectorAll('input[type="checkbox"]');
                checkboxes.forEach(checkbox => {
                    if (!checkbox.classList.contains('tag-checkbox')) {
                        checkbox.checked = isChecked;
                        return;
                    }
                    const tagName = checkbox.value;
                    const tag = this.state.tags.find(t => t['Product Name*'] === tagName);
                    if (tag) {
                        checkbox.checked = isChecked;
                        if (isChecked) {
                            if (!this.state.persistentSelectedTags.includes(tagName)) {
                                this.state.persistentSelectedTags.push(tagName);
                            }
                        } else {
                            const index = this.state.persistentSelectedTags.indexOf(tagName);
                            if (index > -1) {
                                this.state.persistentSelectedTags.splice(index, 1);
                            }
                        }
                    }
                });
                this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                const selectedTagObjects = this.state.persistentSelectedTags.map(name =>
                    this.state.tags.find(t => t['Product Name*'] === name)
                ).filter(Boolean);
                this.updateSelectedTags(selectedTagObjects);
                this.efficientlyUpdateAvailableTagsDisplay();
                requestAnimationFrame(() => {
                    this._restoreAvailableScrollPosition(savedScroll);
                });
            });
            
            vendorHeader.appendChild(vendorCheckbox);
            vendorHeader.appendChild(document.createTextNode(vendor));
            const vendorCollapseIcon = document.createElement('span');
            vendorCollapseIcon.className = 'collapse-icon ms-auto';
            vendorCollapseIcon.textContent = '▼';
            vendorHeader.appendChild(vendorCollapseIcon);
            vendorSection.appendChild(vendorHeader);

            const vendorContent = document.createElement('div');
            vendorContent.className = 'vendor-content';
            vendorSection.appendChild(vendorContent);
            
            const sortedBrands = Array.from(brandGroups.entries())
                .sort(([a], [b]) => (a || '').localeCompare(b || ''));

            sortedBrands.forEach(([brand, productTypeGroups]) => {
                const brandSection = document.createElement('div');
                brandSection.className = 'brand-section ms-3 mb-2';
                
                // Create brand header with checkbox
                const brandHeader = document.createElement('h6');
                brandHeader.className = 'brand-header mb-2 d-flex align-items-center cursor-pointer';
                brandHeader.addEventListener('click', (e) => {
                    if (e.target.type === 'checkbox') return;
                    const brandContent = brandSection.querySelector('.brand-content');
                    const isCollapsed = brandContent.classList.contains('collapsed');
                    brandContent.classList.toggle('collapsed', !isCollapsed);
                    brandHeader.querySelector('.collapse-icon').textContent = isCollapsed ? '▼' : '▶';
                });
                
                const brandCheckbox = document.createElement('input');
                brandCheckbox.type = 'checkbox';
                brandCheckbox.className = 'select-all-checkbox me-2';
                brandCheckbox.addEventListener('change', (e) => {
                    // PERFORMANCE: Skip during bulk clear operations
                    if (this.state.isClearing) {
                        return;
                    }
                    const savedScroll = this._saveAvailableScrollPosition();
                    const isChecked = e.target.checked;
                    const checkboxes = brandSection.querySelectorAll('input[type="checkbox"]');
                    checkboxes.forEach(checkbox => {
                        if (!checkbox.classList.contains('tag-checkbox')) {
                            checkbox.checked = isChecked;
                            return;
                        }
                        const tagName = checkbox.value;
                        const tag = this.state.tags.find(t => t['Product Name*'] === tagName);
                        if (tag) {
                            checkbox.checked = isChecked;
                            if (isChecked) {
                                if (!this.state.persistentSelectedTags.includes(tagName)) {
                                    this.state.persistentSelectedTags.push(tagName);
                                }
                            } else {
                                const index = this.state.persistentSelectedTags.indexOf(tagName);
                                if (index > -1) {
                                    this.state.persistentSelectedTags.splice(index, 1);
                                }
                            }
                        }
                    });
                    this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                    const selectedTagObjects = this.state.persistentSelectedTags.map(name =>
                        this.state.tags.find(t => t['Product Name*'] === name)
                    ).filter(Boolean);
                    this.updateSelectedTags(selectedTagObjects);
                    this.efficientlyUpdateAvailableTagsDisplay();
                    requestAnimationFrame(() => {
                        this._restoreAvailableScrollPosition(savedScroll);
                    });
                });
                
                brandHeader.appendChild(brandCheckbox);
                brandHeader.appendChild(document.createTextNode(brand));
                const brandCollapseIcon = document.createElement('span');
                brandCollapseIcon.className = 'collapse-icon ms-auto';
                brandCollapseIcon.textContent = '▼';
                brandHeader.appendChild(brandCollapseIcon);
                brandSection.appendChild(brandHeader);
                
                const brandContent = document.createElement('div');
                brandContent.className = 'brand-content';
                brandSection.appendChild(brandContent);

                const sortedProductTypes = Array.from(productTypeGroups.entries())
                    .sort(([a], [b]) => (a || '').localeCompare(b || ''));

                sortedProductTypes.forEach(([productType, weightGroupsOrSubcategories]) => {
                    const productTypeSection = document.createElement('div');
                    productTypeSection.className = 'product-type-section ms-3 mb-2';
                    
                    // Create product type header with checkbox
                    const productTypeHeader = document.createElement('div');
                    productTypeHeader.className = 'product-type-header mb-2 d-flex align-items-center cursor-pointer';
                    productTypeHeader.addEventListener('click', (e) => {
                        if (e.target.type === 'checkbox') return;
                        const productTypeContent = productTypeSection.querySelector('.product-type-content');
                        const isCollapsed = productTypeContent.classList.contains('collapsed');
                        productTypeContent.classList.toggle('collapsed', !isCollapsed);
                        productTypeHeader.querySelector('.collapse-icon').textContent = isCollapsed ? '▼' : '▶';
                    });
                    
                    const productTypeCheckbox = document.createElement('input');
                    productTypeCheckbox.type = 'checkbox';
                    productTypeCheckbox.className = 'select-all-checkbox me-2';
                    productTypeCheckbox.addEventListener('change', (e) => {
                        // PERFORMANCE: Skip during bulk clear operations
                        if (this.state.isClearing) {
                            return;
                        }
                        const savedScroll = this._saveAvailableScrollPosition();
                        const isChecked = e.target.checked;
                        const checkboxes = productTypeSection.querySelectorAll('input[type="checkbox"]');
                        checkboxes.forEach(checkbox => {
                            if (!checkbox.classList.contains('tag-checkbox')) {
                                checkbox.checked = isChecked;
                                return;
                            }
                            const tagName = checkbox.value;
                            const tag = this.state.tags.find(t => t['Product Name*'] === tagName);
                            if (tag) {
                                checkbox.checked = isChecked;
                                if (isChecked) {
                                    if (!this.state.persistentSelectedTags.includes(tagName)) {
                                        this.state.persistentSelectedTags.push(tagName);
                                    }
                                } else {
                                    const index = this.state.persistentSelectedTags.indexOf(tagName);
                                    if (index > -1) {
                                        this.state.persistentSelectedTags.splice(index, 1);
                                    }
                                }
                            }
                        });
                        this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                        const selectedTagObjects = this.state.persistentSelectedTags.map(name =>
                            this.state.tags.find(t => t['Product Name*'] === name)
                        ).filter(Boolean);
                        this.updateSelectedTags(selectedTagObjects);
                        this.efficientlyUpdateAvailableTagsDisplay();
                        requestAnimationFrame(() => {
                            this._restoreAvailableScrollPosition(savedScroll);
                        });
                    });
                    
                    productTypeHeader.appendChild(productTypeCheckbox);
                    productTypeHeader.appendChild(document.createTextNode(productType));
                    const typeCollapseIcon = document.createElement('span');
                    typeCollapseIcon.className = 'collapse-icon ms-auto';
                    typeCollapseIcon.textContent = '▼';
                    productTypeHeader.appendChild(typeCollapseIcon);
                    productTypeSection.appendChild(productTypeHeader);
                    
                    const productTypeContent = document.createElement('div');
                    productTypeContent.className = 'product-type-content';
                    productTypeSection.appendChild(productTypeContent);

                    // Check if this product type has subcategories (vape products with 510/Disposable)
                    const hasSubcategories = weightGroupsOrSubcategories instanceof Map && 
                                           weightGroupsOrSubcategories.size > 0 &&
                                           Array.from(weightGroupsOrSubcategories.values())[0] instanceof Map;

                    if (hasSubcategories) {
                        // Render subcategories (510, Disposable, etc.)
                        const sortedSubcategories = Array.from(weightGroupsOrSubcategories.entries())
                            .sort(([a], [b]) => (a || '').localeCompare(b || ''));

                        sortedSubcategories.forEach(([subcategory, weightGroups]) => {
                            const subcategorySection = document.createElement('div');
                            subcategorySection.className = 'subcategory-section ms-3 mb-2';
                            
                            // Create subcategory header with checkbox
                            const subcategoryHeader = document.createElement('div');
                            subcategoryHeader.className = 'subcategory-header mb-2 d-flex align-items-center cursor-pointer';
                            
                            const subcategoryCheckbox = document.createElement('input');
                            subcategoryCheckbox.type = 'checkbox';
                            subcategoryCheckbox.className = 'select-all-checkbox me-2';
                            subcategoryCheckbox.addEventListener('change', (e) => {
                                const savedScroll = this._saveAvailableScrollPosition();
                                const isChecked = e.target.checked;
                                const checkboxes = subcategorySection.querySelectorAll('input.tag-checkbox');
                                checkboxes.forEach(checkbox => {
                                    checkbox.checked = isChecked;
                                    const tagName = checkbox.value;
                                    const tag = this.state.tags.find(t => t['Product Name*'] === tagName);
                                    if (tag) {
                                        if (isChecked) {
                                            if (!this.state.persistentSelectedTags.includes(tagName)) {
                                                this.state.persistentSelectedTags.push(tagName);
                                            }
                                        } else {
                                            const index = this.state.persistentSelectedTags.indexOf(tagName);
                                            if (index > -1) {
                                                this.state.persistentSelectedTags.splice(index, 1);
                                            }
                                        }
                                    }
                                });
                                this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                                const selectedTagObjects = this.state.persistentSelectedTags.map(name =>
                                    this.state.tags.find(t => t['Product Name*'] === name)
                                ).filter(Boolean);
                                this.updateSelectedTags(selectedTagObjects);
                                this.efficientlyUpdateAvailableTagsDisplay();
                                requestAnimationFrame(() => {
                                    this._restoreAvailableScrollPosition(savedScroll);
                                });
                            });
                            
                            subcategoryHeader.appendChild(subcategoryCheckbox);
                            const subcategoryNameSpan = document.createElement('span');
                            subcategoryNameSpan.textContent = subcategory;
                            subcategoryHeader.appendChild(subcategoryNameSpan);
                            subcategorySection.appendChild(subcategoryHeader);

                            // Render weight groups under subcategory
                            const sortedWeights = Array.from(weightGroups.entries())
                                .sort(([a], [b]) => (a || '').localeCompare(b || ''));

                            sortedWeights.forEach(([weight, tagArray]) => {
                                const weightSection = document.createElement('div');
                                weightSection.className = 'weight-section ms-3 mb-2';
                                
                                // Create weight header with checkbox
                                const weightHeader = document.createElement('div');
                                weightHeader.className = 'weight-header mb-1 d-flex align-items-center cursor-pointer';
                                weightHeader.addEventListener('click', (e) => {
                                    if (e.target.type === 'checkbox') return;
                                    const weightContent = weightSection.querySelector('.weight-content');
                                    const isCollapsed = weightContent.classList.contains('collapsed');
                                    weightContent.classList.toggle('collapsed', !isCollapsed);
                                    weightHeader.querySelector('.collapse-icon').textContent = isCollapsed ? '▼' : '▶';
                                });
                                
                                const weightCheckbox = document.createElement('input');
                                weightCheckbox.type = 'checkbox';
                                weightCheckbox.className = 'select-all-checkbox me-2';
                                weightCheckbox.addEventListener('change', (e) => {
                                    // PERFORMANCE: Skip during bulk clear operations
                                    if (this.state.isClearing) {
                                        return;
                                    }
                                    const savedScroll = this._saveAvailableScrollPosition();
                                    const isChecked = e.target.checked;
                                    const checkboxes = weightSection.querySelectorAll('input.tag-checkbox');
                                    checkboxes.forEach(checkbox => {
                                        checkbox.checked = isChecked;
                                        const tagName = checkbox.value;
                                        const tag = this.state.tags.find(t => t['Product Name*'] === tagName);
                                        if (tag) {
                                            if (isChecked) {
                                                if (!this.state.persistentSelectedTags.includes(tagName)) {
                                                    this.state.persistentSelectedTags.push(tagName);
                                                }
                                            } else {
                                                const index = this.state.persistentSelectedTags.indexOf(tagName);
                                                if (index > -1) {
                                                    this.state.persistentSelectedTags.splice(index, 1);
                                                }
                                            }
                                        }
                                    });
                                    this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                                    const selectedTagObjects = this.state.persistentSelectedTags.map(name =>
                                        this.state.tags.find(t => t['Product Name*'] === name)
                                    ).filter(Boolean);
                                    this.updateSelectedTags(selectedTagObjects);
                                    this.efficientlyUpdateAvailableTagsDisplay();
                                    requestAnimationFrame(() => {
                                        this._restoreAvailableScrollPosition(savedScroll);
                                    });
                                });
                                
                                weightHeader.appendChild(weightCheckbox);
                                weightHeader.appendChild(document.createTextNode(weight));
                                const weightCollapseIcon = document.createElement('span');
                                weightCollapseIcon.className = 'collapse-icon ms-auto';
                                weightCollapseIcon.textContent = '▼';
                                weightHeader.appendChild(weightCollapseIcon);
                                weightSection.appendChild(weightHeader);
                                
                                const weightContent = document.createElement('div');
                                weightContent.className = 'weight-content';
                                weightSection.appendChild(weightContent);

                                // Sort tags alphabetically by product name
                                const sortedTags = [...tagArray].sort((a, b) => {
                                    const aName = (a && (a['Product Name*'] || a.ProductName || a.displayName) || '').toString();
                                    const bName = (b && (b['Product Name*'] || b.ProductName || b.displayName) || '').toString();
                                    return aName.localeCompare(bName);
                                });
                                // PERFORMANCE FIX: Render tags progressively to prevent UI freeze
                                this._renderTagsInBatches(sortedTags, weightContent);

                                subcategorySection.appendChild(weightSection);
                            });

                            productTypeSection.appendChild(subcategorySection);
                        });
                    } else {
                        // No subcategories - render weights directly
                        const sortedWeights = Array.from(weightGroupsOrSubcategories.entries())
                            .sort(([a], [b]) => (a || '').localeCompare(b || ''));

                        sortedWeights.forEach(([weight, tagArray]) => {
                            const weightSection = document.createElement('div');
                            weightSection.className = 'weight-section ms-3 mb-2';
                            
                            // Create weight header with checkbox
                            const weightHeader = document.createElement('div');
                            weightHeader.className = 'weight-header mb-1 d-flex align-items-center cursor-pointer';
                            weightHeader.addEventListener('click', (e) => {
                                if (e.target.type === 'checkbox') return;
                                const weightContent = weightSection.querySelector('.weight-content');
                                const isCollapsed = weightContent.classList.contains('collapsed');
                                weightContent.classList.toggle('collapsed', !isCollapsed);
                                weightHeader.querySelector('.collapse-icon').textContent = isCollapsed ? '▼' : '▶';
                            });
                            
                            const weightCheckbox = document.createElement('input');
                            weightCheckbox.type = 'checkbox';
                            weightCheckbox.className = 'select-all-checkbox me-2';
                            weightCheckbox.addEventListener('change', (e) => {
                                const savedScroll = this._saveAvailableScrollPosition();
                                const isChecked = e.target.checked;
                                const checkboxes = weightSection.querySelectorAll('input.tag-checkbox');
                                checkboxes.forEach(checkbox => {
                                    checkbox.checked = isChecked;
                                    const tagName = checkbox.value;
                                    const tag = this.state.tags.find(t => t['Product Name*'] === tagName);
                                    if (tag) {
                                        if (isChecked) {
                                            if (!this.state.persistentSelectedTags.includes(tagName)) {
                                                this.state.persistentSelectedTags.push(tagName);
                                            }
                                        } else {
                                            const index = this.state.persistentSelectedTags.indexOf(tagName);
                                            if (index > -1) {
                                                this.state.persistentSelectedTags.splice(index, 1);
                                            }
                                        }
                                    }
                                });
                                this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                                const selectedTagObjects = this.state.persistentSelectedTags.map(name =>
                                    this.state.tags.find(t => t['Product Name*'] === name)
                                ).filter(Boolean);
                                this.updateSelectedTags(selectedTagObjects);
                                this.efficientlyUpdateAvailableTagsDisplay();
                                requestAnimationFrame(() => {
                                    this._restoreAvailableScrollPosition(savedScroll);
                                });
                            });
                            
                            weightHeader.appendChild(weightCheckbox);
                            weightHeader.appendChild(document.createTextNode(weight));
                            const weightCollapseIcon = document.createElement('span');
                            weightCollapseIcon.className = 'collapse-icon ms-auto';
                            weightCollapseIcon.textContent = '▼';
                            weightHeader.appendChild(weightCollapseIcon);
                            weightSection.appendChild(weightHeader);
                            
                            const weightContent = document.createElement('div');
                            weightContent.className = 'weight-content';
                            weightSection.appendChild(weightContent);

                            // Sort tags alphabetically by product name
                            const sortedTags = [...tagArray].sort((a, b) => {
                                const aName = (a && (a['Product Name*'] || a.ProductName || a.displayName) || '').toString();
                                const bName = (b && (b['Product Name*'] || b.ProductName || b.displayName) || '').toString();
                                return aName.localeCompare(bName);
                            });
                            // PERFORMANCE FIX: Render tags progressively to prevent UI freeze
                            this._renderTagsInBatches(sortedTags, weightContent);

                            productTypeContent.appendChild(weightSection);
                        });
                    }

                    brandContent.appendChild(productTypeSection);
                });

                vendorContent.appendChild(brandSection);
            });

            vendorSection.appendChild(vendorContent);
            tagList.appendChild(vendorSection);
        });

        // PERFORMANCE FIX: Use document fragment for faster DOM updates
        // Atomically replace container content with built tags (this replaces any loading indicator)
        // Use requestAnimationFrame to ensure smooth transition
        requestAnimationFrame(() => {
            // Use document fragment for faster DOM manipulation
            const fragment = document.createDocumentFragment();
            fragment.appendChild(tagList);
            
            availableTagsContainer.innerHTML = '';
            availableTagsContainer.appendChild(fragment);
            
            // After tags are in DOM, restore scroll and initialize
            this._restoreAvailableScrollPosition(savedScroll);
            this.updateSelectAllCheckboxes();
            this.initializeSelectAllCheckbox();
            
            // Update all group-level select all checkboxes
            const container = availableTagsContainer;
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
            container.querySelectorAll('.vendor-section, .brand-section, .product-type-section, .subcategory-section, .weight-section').forEach(section => {
                updateSelectAllCheckboxState(section);
            });
            
            // Hide loading splash only after tags actually appear in DOM
            this._waitForTagsToAppear();
        });
        
        verboseLog('✅ Rendered', tags.length, 'JSON matched tags with HIERARCHY (same as Selected Tags)');
    },

    // Internal function that actually updates the available tags
    _updateAvailableTags(originalTags, filteredTags = null) {
        // Windows optimization: Use requestAnimationFrame for smoother rendering
        if (isWindows) {
            requestAnimationFrame(() => {
                this._performUpdateAvailableTags(originalTags, filteredTags);
            });
            return;
        }
        
        this._performUpdateAvailableTags(originalTags, filteredTags);
    },
    
    _performUpdateAvailableTags(originalTags, filteredTags = null) {
        verboseLog('_updateAvailableTags called with:', {
            originalTagsLength: originalTags ? originalTags.length : 0,
            filteredTagsLength: filteredTags ? filteredTags.length : 0,
            tags: filteredTags || originalTags,
            hydratedFromCache: this.state.hydratedFromCache
        });
        
        const availableTagsContainer = document.getElementById('availableTags');
        if (!availableTagsContainer) {
            console.error('Available tags container not found');
            return;
        }
        // Preserve scroll position during re-render
        const savedScroll = this._saveAvailableScrollPosition();

        const tags = filteredTags || originalTags;
        
        if (!tags || tags.length === 0) {
            verboseLog('No tags provided, showing empty state');
            availableTagsContainer.innerHTML = '<div class="tag-entry">No tags available</div>';
            // Hide splash if showing
            if (this.hideActionSplash) {
                this.hideActionSplash();
            }
            return;
        }
        
        // PERFORMANCE: Skip loading spinner for instant cache loads
        // Only show spinner if not hydrated from cache (i.e., fetching from server)
        const currentContent = availableTagsContainer.innerHTML.trim();
        const hasLoadingIndicator = currentContent.includes('spinner-border') || currentContent.includes('Loading');
        const isEmpty = !currentContent || currentContent === '' || currentContent === '<div class="tag-entry">No tags available</div>';
        
        // Only show loading indicator if NOT loaded from cache and container is empty
        if (!this.state.hydratedFromCache && (isEmpty || hasLoadingIndicator)) {
            // Show loading indicator for server fetch
            availableTagsContainer.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2 text-white">Loading tags...</p>
                </div>
            `;
        }
        
        verboseLog('Tags received, showing simple test first');
        verboseLog('=== TAGS BEING RENDERED ===');
        verboseLog('Tags array:', tags);
        verboseLog('Tags length:', tags.length);
        if (tags.length > 0) {
            verboseLog('First tag structure:', tags[0]);
            verboseLog('First tag keys:', Object.keys(tags[0]));
        }
        
        // Update the state with the tags
        verboseLog('=== UPDATING STATE ===');
        verboseLog('Before update - this.state.tags length:', this.state.tags.length);
        verboseLog('Before update - this.state.originalTags length:', this.state.originalTags.length);
        
        // Only update originalTags if we're not filtering (i.e., if filteredTags is null)
        // This preserves the original data for when filters are reset to "All"
        if (filteredTags === null) {
            this.state.originalTags = [...tags];
        }
        
        // Always update the current tags for display
        this.state.tags = [...tags];
        
        const shouldUseSimplified = !this.state.forceFullAvailableTagRender &&
            !this.state.isSearching &&
            !this.hasActiveFilters() &&
            tags.length > this.SIMPLIFIED_RENDER_THRESHOLD;
        this.state.simplifiedAvailableTagsActive = shouldUseSimplified;
        if (shouldUseSimplified) {
            verboseLog(`⚡ Simplified available-tag rendering enabled for ${tags.length} tags`);
            this.renderSimplifiedAvailableTags(tags, savedScroll);
            return;
        } else if (this.state.forceFullAvailableTagRender && tags.length > this.SIMPLIFIED_RENDER_THRESHOLD) {
            verboseLog('Detailed view forced despite large dataset.');
        }
        
        verboseLog('After update - this.state.tags length:', this.state.tags.length);
        verboseLog('After update - this.state.originalTags length:', this.state.originalTags.length);
        
        // PERFORMANCE: Skip redundant loading indicator for cache loads
        // Only show if not from cache and not already showing
        if (!this.state.hydratedFromCache && !hasLoadingIndicator) {
            // Show loading indicator for slow server fetch
            availableTagsContainer.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2 text-white">Loading tags...</p>
                </div>
            `;
        }
        
        // Schedule scroll restoration after rebuild
        const restoreScrollAfterBuild = () => this._restoreAvailableScrollPosition(savedScroll);
        setTimeout(restoreScrollAfterBuild, 0);

        // Create organized structure with filter headers but no collapsible functionality
        const tagList = document.createElement('div');
        tagList.className = 'tag-list';

        // Add "Select All" checkbox
        const selectAllContainer = document.createElement('div');
        selectAllContainer.className = 'd-flex align-items-center gap-3 mb-2 px-3';
        selectAllContainer.innerHTML = `
            <label class="d-flex align-items-center gap-2 cursor-pointer mb-0 select-all-container">
                <input type="checkbox" id="selectAllAvailable" class="custom-checkbox">
                <span class="text-secondary fw-semibold">SELECT ALL</span>
            </label>
        `;
        tagList.appendChild(selectAllContainer);

        // Add event listener for available tags select all checkbox
        const selectAllAvailable = document.getElementById('selectAllAvailable');
        if (selectAllAvailable && !selectAllAvailable.hasAttribute('data-listener-added')) {
            selectAllAvailable.setAttribute('data-listener-added', 'true');
            selectAllAvailable.addEventListener('change', (e) => {
                // Save current state for undo before making changes (non-blocking)
                this.saveSelectionState('select_all_checkbox');

                verboseLog('Select All Available checkbox changed:', e.target.checked);
                const isChecked = e.target.checked;
                
                // Get all visible tag checkboxes in available tags
                const availableCheckboxes = document.querySelectorAll('#availableTags .tag-checkbox');
                verboseLog('Found available tag checkboxes:', availableCheckboxes.length);
                
                availableCheckboxes.forEach(checkbox => {
                    checkbox.checked = isChecked;
                    // CRITICAL FIX: Look in originalTags first to find tags regardless of filters
                    let tag = this.state.originalTags.find(t => t['Product Name*'] === checkbox.value);
                    // If not found in originalTags, try current tags (filtered view)
                    if (!tag) {
                        tag = this.state.tags.find(t => t['Product Name*'] === checkbox.value);
                    }
                    if (tag) {
                        if (isChecked) {
                            if (!this.state.persistentSelectedTags.includes(tag['Product Name*'])) {
                                this.state.persistentSelectedTags.push(tag['Product Name*']);
                            }
                        } else {
                            const index = this.state.persistentSelectedTags.indexOf(tag['Product Name*']);
                            if (index > -1) {
                                this.state.persistentSelectedTags.splice(index, 1);
                            }
                        }
                    }
                });
                
                // Update the regular selectedTags set to match persistent ones
                this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                
                // Update selected tags display
                // CRITICAL FIX: Use helper function to find ALL selected tags, preserving tags from multiple filters
                const selectedTagObjects = this.getSelectedTagObjects();
                this.updateSelectedTags(selectedTagObjects);
                
                // Update available tags display to reflect selection changes
                this.efficientlyUpdateAvailableTagsDisplay();
                
                // Update select all checkbox state
                this.updateSelectAllCheckboxes();
            });
        } else if (selectAllAvailable) {
            verboseLog('Select All Available checkbox already has listener');
        } else {
            verboseLog('Select All Available checkbox not found');
        }

        // CRITICAL FIX: For JSON matched tags, skip organization entirely and render directly
        const isJsonMatchedSession = tags.some(tag => tag.Source && tag.Source.includes('JSON Match'));
        
        let organizedTags;
        if (isJsonMatchedSession) {
            verboseLog('CRITICAL FIX: JSON matched session detected, skipping organization and rendering directly');
            // For JSON matched tags, render them directly without organization
            this.renderJsonMatchedTags(tags);
            return;
        } else {
            // Organize tags by vendor, brand, product type, weight (SAME HIERARCHY AS SELECTED TAGS)
            // This ensures JSON matched tags and all tags use: Vendor > Brand > Product Type > Weight
            verboseLog('About to organize tags, tags length:', tags.length);
            try {
                organizedTags = this.organizeBrandCategories(tags);
                verboseLog('✅ CURRENT INVENTORY: Using same hierarchical organization as Selected Tags');
                verboseLog('Tags organized successfully, vendor count:', organizedTags.size);
            } catch (error) {
                console.error('Error organizing tags:', error);
                // Fallback to simple list if organization fails
                availableTagsContainer.innerHTML = '<div class="tag-entry">Error organizing tags: ' + error.message + '</div>';
                return;
            }
        }
        
        // Create vendor sections
        if (!organizedTags || organizedTags.size === 0) {
            verboseLog('No organized tags, showing simple list');
            // Fallback to simple list (sorted alphabetically by product name)
            const sortedSimple = [...tags].sort((a, b) => {
                const aName = (a && (a['Product Name*'] || a.ProductName || a.displayName) || '').toString();
                const bName = (b && (b['Product Name*'] || b.ProductName || b.displayName) || '').toString();
                return aName.localeCompare(bName);
            });
            // PERFORMANCE FIX: Render tags progressively to prevent UI freeze
            this._renderTagsInBatches(sortedSimple, tagList);
                    // Atomically replace container content with built tags
                    requestAnimationFrame(() => {
                        availableTagsContainer.innerHTML = '';
                        availableTagsContainer.appendChild(tagList);
                        
                        // After tags are in DOM, restore scroll and initialize
                        this._restoreAvailableScrollPosition(savedScroll);
                        this.updateSelectAllCheckboxes();
                        this.initializeSelectAllCheckbox();
                        
                        // Hide loading splash only after tags actually appear in DOM
                        this._waitForTagsToAppear();
                    });
            return;
        }
        
        const sortedVendors = Array.from(organizedTags.entries())
            .sort(([a], [b]) => (a || '').localeCompare(b || ''));

        sortedVendors.forEach(([vendor, brandGroups]) => {
            const vendorSection = document.createElement('div');
            vendorSection.className = 'vendor-section mb-3';
            
            // Create vendor header with checkbox and collapse functionality
            const vendorHeader = document.createElement('h5');
            vendorHeader.className = 'vendor-header mb-2 d-flex align-items-center cursor-pointer';
            vendorHeader.addEventListener('click', (e) => {
                if (e.target.type === 'checkbox') return; // Don't collapse if clicking checkbox
                if (this.state.isSearching) return; // Don't collapse while searching
                const vendorContent = vendorSection.querySelector('.vendor-content');
                const isCollapsed = vendorContent.classList.contains('collapsed');
                vendorContent.classList.toggle('collapsed', !isCollapsed);
                vendorHeader.querySelector('.collapse-icon').textContent = isCollapsed ? '▼' : '▶';
                
                // Remove the instructional blurb when any chevron is clicked
                this.removeDropdownInstructionBlurb();
            });
            
            const vendorCheckbox = document.createElement('input');
            vendorCheckbox.type = 'checkbox';
            vendorCheckbox.className = 'select-all-checkbox me-2';
            vendorCheckbox.addEventListener('change', (e) => {
                const savedScroll = this._saveAvailableScrollPosition();
                const isChecked = e.target.checked;
                // Select ALL checkboxes (both select-all checkboxes and tag checkboxes) within this section
                const checkboxes = vendorSection.querySelectorAll('input[type="checkbox"]');
                checkboxes.forEach(checkbox => {
                    if (!checkbox.classList.contains('tag-checkbox')) {
                    checkbox.checked = isChecked;
                        return;
                    }
                    
                    const tagName = checkbox.value;
                    const tag = this.state.tags.find(t => t['Product Name*'] === tagName);
                    if (!tag) {
                        checkbox.checked = isChecked;
                        return;
                    }

                    checkbox.checked = isChecked;

                            if (isChecked) {
                        if (!this.state.persistentSelectedTags.includes(tagName)) {
                            this.state.persistentSelectedTags.push(tagName);
                                }
                            } else {
                        // Only remove if the originating event is actually unchecking
                        if (!e.target.checked) {
                            const index = this.state.persistentSelectedTags.indexOf(tagName);
                                if (index > -1) {
                                    this.state.persistentSelectedTags.splice(index, 1);
                            }
                        }
                    }
                });
                this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                const selectedTagObjects = this.state.persistentSelectedTags.map(name =>
                    this.state.tags.find(t => t['Product Name*'] === name)
                ).filter(Boolean);
                this.updateSelectedTags(selectedTagObjects);
                this.efficientlyUpdateAvailableTagsDisplay();
                // Use double requestAnimationFrame to ensure it happens after all updates, including updateSelectAllCheckboxes
                requestAnimationFrame(() => {
                    requestAnimationFrame(() => {
                        this._restoreAvailableScrollPosition(savedScroll);
                    });
                });
            });
            
            vendorHeader.appendChild(vendorCheckbox);
            vendorHeader.appendChild(document.createTextNode(vendor));
            vendorHeader.appendChild(document.createElement('span')).className = 'collapse-icon ms-auto';
            
            // Check if any filters are active to determine initial collapse state
            const hasActiveFilters = this.hasActiveFilters();
            const shouldStartCollapsed = this.state.isSearching ? false : !hasActiveFilters;
            
            vendorHeader.querySelector('.collapse-icon').textContent = shouldStartCollapsed ? '▶' : '▼';
            vendorSection.appendChild(vendorHeader);
            tagList.appendChild(vendorSection);

            // Create vendor content container
            const vendorContent = document.createElement('div');
            vendorContent.className = 'vendor-content';
            if (shouldStartCollapsed) {
                vendorContent.classList.add('collapsed');
            }
            vendorSection.appendChild(vendorContent);

            // Create brand sections
            const sortedBrands = Array.from(brandGroups.entries())
                .sort(([a], [b]) => (a || '').localeCompare(b || ''));

            sortedBrands.forEach(([brand, productTypeGroups]) => {
                const brandSection = document.createElement('div');
                brandSection.className = 'brand-section ms-3 mb-2';
                
                            // Create brand header with checkbox and collapse functionality
            const brandHeader = document.createElement('h6');
            brandHeader.className = 'brand-header mb-2 d-flex align-items-center cursor-pointer';
            brandHeader.addEventListener('click', (e) => {
                if (e.target.type === 'checkbox') return; // Don't collapse if clicking checkbox
                if (this.state.isSearching) return; // Don't collapse while searching
                const brandContent = brandSection.querySelector('.brand-content');
                const isCollapsed = brandContent.classList.contains('collapsed');
                brandContent.classList.toggle('collapsed', !isCollapsed);
                brandHeader.querySelector('.collapse-icon').textContent = isCollapsed ? '▼' : '▶';
                
                // Remove the instructional blurb when any chevron is clicked
                this.removeDropdownInstructionBlurb();
            });
                
                const brandCheckbox = document.createElement('input');
                brandCheckbox.type = 'checkbox';
                brandCheckbox.className = 'select-all-checkbox me-2';
            brandCheckbox.addEventListener('change', (e) => {
                const savedScroll = this._saveAvailableScrollPosition();
                const isChecked = e.target.checked;
                // Select ALL checkboxes (both select-all checkboxes and tag checkboxes) within this section
                const checkboxes = brandSection.querySelectorAll('input[type="checkbox"]');
                checkboxes.forEach(checkbox => {
                    if (!checkbox.classList.contains('tag-checkbox')) {
                    checkbox.checked = isChecked;
                        return;
                    }

                    const tagName = checkbox.value;
                    const tag = this.state.tags.find(t => t['Product Name*'] === tagName);
                    if (!tag) {
                        checkbox.checked = isChecked;
                        return;
                    }

                    checkbox.checked = isChecked;

                            if (isChecked) {
                        if (!this.state.persistentSelectedTags.includes(tagName)) {
                            this.state.persistentSelectedTags.push(tagName);
                                }
                            } else {
                        if (!e.target.checked) {
                            const index = this.state.persistentSelectedTags.indexOf(tagName);
                                if (index > -1) {
                                    this.state.persistentSelectedTags.splice(index, 1);
                            }
                        }
                    }
                });
                this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                // CRITICAL FIX: Use helper function to find ALL selected tags, preserving tags from multiple filters
                const selectedTagObjects = this.getSelectedTagObjects();
                this.updateSelectedTags(selectedTagObjects);
                this.efficientlyUpdateAvailableTagsDisplay();
                // Restore scroll after all DOM updates complete
                requestAnimationFrame(() => {
                    this._restoreAvailableScrollPosition(savedScroll);
                });
            });
            
            brandHeader.appendChild(brandCheckbox);
                brandHeader.appendChild(document.createTextNode(brand));
                brandHeader.appendChild(document.createElement('span')).className = 'collapse-icon ms-auto';
                
                // Check if any filters are active to determine initial collapse state
                const hasActiveFilters = this.hasActiveFilters();
                const shouldStartCollapsed = this.state.isSearching ? false : !hasActiveFilters;
                
                brandHeader.querySelector('.collapse-icon').textContent = shouldStartCollapsed ? '▶' : '▼';
                vendorContent.appendChild(brandSection);
                brandSection.appendChild(brandHeader);

                // Create brand content container
                const brandContent = document.createElement('div');
                brandContent.className = 'brand-content';
                if (shouldStartCollapsed) {
                    brandContent.classList.add('collapsed');
                }
                brandSection.appendChild(brandContent);

                // Create product type sections
                const sortedProductTypes = Array.from(productTypeGroups.entries())
                    .sort(([a], [b]) => (a || '').localeCompare(b || ''));

                sortedProductTypes.forEach(([productType, weightGroupsOrSubcategories]) => {
                    const productTypeSection = document.createElement('div');
                    productTypeSection.className = 'product-type-section ms-3 mb-2';
                    
                    // Check if this product type has subcategories (vape products with 510/Disposable)
                    const hasSubcategories = weightGroupsOrSubcategories instanceof Map && 
                                           weightGroupsOrSubcategories.size > 0 &&
                                           Array.from(weightGroupsOrSubcategories.values())[0] instanceof Map;
                    
                    // Create product type header with checkbox and collapse functionality
                    const typeHeader = document.createElement('div');
                    typeHeader.className = 'product-type-header mb-2 d-flex align-items-center cursor-pointer';
                    typeHeader.addEventListener('click', (e) => {
                        if (e.target.type === 'checkbox') return; // Don't collapse if clicking checkbox
                        if (this.state.isSearching) return; // Don't collapse while searching
                        const productTypeContent = productTypeSection.querySelector('.product-type-content');
                        const isCollapsed = productTypeContent.classList.contains('collapsed');
                        productTypeContent.classList.toggle('collapsed', !isCollapsed);
                        typeHeader.querySelector('.collapse-icon').textContent = isCollapsed ? '▼' : '▶';
                        
                        // Remove the instructional blurb when any chevron is clicked
                        this.removeDropdownInstructionBlurb();
                    });
                    
                    const productTypeCheckbox = document.createElement('input');
                    productTypeCheckbox.type = 'checkbox';
                    productTypeCheckbox.className = 'select-all-checkbox me-2';
                    productTypeCheckbox.addEventListener('change', (e) => {
                        const savedScroll = this._saveAvailableScrollPosition();
                        const isChecked = e.target.checked;
                        // Select ALL checkboxes (both select-all checkboxes and tag checkboxes) within this section
                        const checkboxes = productTypeSection.querySelectorAll('input[type="checkbox"]');
                        checkboxes.forEach(checkbox => {
                            if (!checkbox.classList.contains('tag-checkbox')) {
                            checkbox.checked = isChecked;
                                return;
                            }

                            const tagName = checkbox.value;
                            const tag = this.state.tags.find(t => t['Product Name*'] === tagName);
                            if (!tag) {
                                checkbox.checked = isChecked;
                                return;
                            }

                            checkbox.checked = isChecked;

                                    if (isChecked) {
                                if (!this.state.persistentSelectedTags.includes(tagName)) {
                                    this.state.persistentSelectedTags.push(tagName);
                                        }
                                    } else {
                                if (!e.target.checked) {
                                    const index = this.state.persistentSelectedTags.indexOf(tagName);
                                        if (index > -1) {
                                            this.state.persistentSelectedTags.splice(index, 1);
                                    }
                                }
                            }
                        });
                        this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                        const selectedTagObjects = this.state.persistentSelectedTags.map(name =>
                            this.state.tags.find(t => t['Product Name*'] === name)
                        ).filter(Boolean);
                        this.updateSelectedTags(selectedTagObjects);
                        this.efficientlyUpdateAvailableTagsDisplay();
                        // Restore scroll after all DOM updates complete
                        requestAnimationFrame(() => {
                            this._restoreAvailableScrollPosition(savedScroll);
                        });
                    });
                    
                    typeHeader.appendChild(productTypeCheckbox);
                    typeHeader.appendChild(document.createTextNode(productType));
                    typeHeader.appendChild(document.createElement('span')).className = 'collapse-icon ms-auto';
                    
                    // Check if any filters are active to determine initial collapse state
                    const hasActiveFilters = this.hasActiveFilters();
                    const shouldStartCollapsed = this.state.isSearching ? false : !hasActiveFilters;
                    
                    typeHeader.querySelector('.collapse-icon').textContent = shouldStartCollapsed ? '▶' : '▼';
                    brandContent.appendChild(productTypeSection);
                    productTypeSection.appendChild(typeHeader);

                    // Create product type content container
                    const productTypeContent = document.createElement('div');
                    productTypeContent.className = 'product-type-content';
                    if (shouldStartCollapsed) {
                        productTypeContent.classList.add('collapsed');
                    }
                    productTypeSection.appendChild(productTypeContent);

                    if (hasSubcategories) {
                        // Render subcategories (510, Disposable, etc.)
                        const sortedSubcategories = Array.from(weightGroupsOrSubcategories.entries())
                            .sort(([a], [b]) => (a || '').localeCompare(b || ''));

                        sortedSubcategories.forEach(([subcategory, weightGroups]) => {
                            const subcategorySection = document.createElement('div');
                            subcategorySection.className = 'subcategory-section ms-3 mb-2';
                            
                            // Create subcategory header with checkbox
                            const subcategoryHeader = document.createElement('div');
                            subcategoryHeader.className = 'subcategory-header mb-2 d-flex align-items-center cursor-pointer';
                            
                            const subcategoryCheckbox = document.createElement('input');
                            subcategoryCheckbox.type = 'checkbox';
                            subcategoryCheckbox.className = 'select-all-checkbox me-2';
                            subcategoryCheckbox.addEventListener('change', (e) => {
                                const savedScroll = this._saveAvailableScrollPosition();
                                const isChecked = e.target.checked;
                                const checkboxes = subcategorySection.querySelectorAll('input.tag-checkbox');
                                checkboxes.forEach(checkbox => {
                                    checkbox.checked = isChecked;
                                    const tagName = checkbox.value;
                                    const tag = this.state.tags.find(t => t['Product Name*'] === tagName);
                                    if (tag) {
                                        if (isChecked) {
                                            if (!this.state.persistentSelectedTags.includes(tagName)) {
                                                this.state.persistentSelectedTags.push(tagName);
                                            }
                                        } else {
                                            if (!e.target.checked) {
                                                const index = this.state.persistentSelectedTags.indexOf(tagName);
                                                if (index > -1) {
                                                    this.state.persistentSelectedTags.splice(index, 1);
                                                }
                                            }
                                        }
                                    }
                                });
                                this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                                const selectedTagObjects = this.state.persistentSelectedTags.map(name =>
                                    this.state.tags.find(t => t['Product Name*'] === name)
                                ).filter(Boolean);
                                this.updateSelectedTags(selectedTagObjects);
                                this.efficientlyUpdateAvailableTagsDisplay();
                                requestAnimationFrame(() => {
                                    this._restoreAvailableScrollPosition(savedScroll);
                                });
                            });
                            
                            subcategoryHeader.appendChild(subcategoryCheckbox);
                            const subcategoryNameSpan = document.createElement('span');
                            subcategoryNameSpan.textContent = subcategory;
                            subcategoryHeader.appendChild(subcategoryNameSpan);
                            subcategorySection.appendChild(subcategoryHeader);

                            // Create weight sections
                            const sortedWeights = Array.from(weightGroups.entries())
                                .sort(([a], [b]) => (a || '').localeCompare(b || ''));

                            sortedWeights.forEach(([weight, tagArray]) => {
                                const weightSection = document.createElement('div');
                                weightSection.className = 'weight-section ms-3 mb-1';
                                
                                // Create weight header with checkbox and collapse functionality
                                const weightHeader = document.createElement('div');
                                weightHeader.className = 'weight-header mb-1 d-flex align-items-center cursor-pointer';
                                weightHeader.addEventListener('click', (e) => {
                                    if (e.target.type === 'checkbox') return; // Don't collapse if clicking checkbox
                                    if (this.state.isSearching) return; // Don't collapse while searching
                                    const weightContent = weightSection.querySelector('.weight-content');
                                    const isCollapsed = weightContent.classList.contains('collapsed');
                                    weightContent.classList.toggle('collapsed', !isCollapsed);
                                    weightHeader.querySelector('.collapse-icon').textContent = isCollapsed ? '▼' : '▶';
                                    
                                    // Remove the instructional blurb when any chevron is clicked
                                    this.removeDropdownInstructionBlurb();
                                });
                                
                                const weightCheckbox = document.createElement('input');
                                weightCheckbox.type = 'checkbox';
                                weightCheckbox.className = 'select-all-checkbox me-2';
                                weightCheckbox.addEventListener('change', (e) => {
                                    const savedScroll = this._saveAvailableScrollPosition();
                                    const isChecked = e.target.checked;
                                    // Select ALL checkboxes (both select-all checkboxes and tag checkboxes) within this section
                                    const checkboxes = weightSection.querySelectorAll('input[type="checkbox"]');
                                    checkboxes.forEach(checkbox => {
                                        if (!checkbox.classList.contains('tag-checkbox')) {
                                        checkbox.checked = isChecked;
                                            return;
                                        }

                                        const tagName = checkbox.value;
                                        const tag = this.state.tags.find(t => t['Product Name*'] === tagName);
                                        if (!tag) {
                                            checkbox.checked = isChecked;
                                            return;
                                        }

                                        checkbox.checked = isChecked;

                                                if (isChecked) {
                                            if (!this.state.persistentSelectedTags.includes(tagName)) {
                                                this.state.persistentSelectedTags.push(tagName);
                                                    }
                                                } else {
                                            if (!e.target.checked) {
                                                const index = this.state.persistentSelectedTags.indexOf(tagName);
                                                    if (index > -1) {
                                                        this.state.persistentSelectedTags.splice(index, 1);
                                                }
                                            }
                                        }
                                    });
                                    this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                                    const selectedTagObjects = this.state.persistentSelectedTags.map(name =>
                                        this.state.tags.find(t => t['Product Name*'] === name)
                                    ).filter(Boolean);
                                    this.updateSelectedTags(selectedTagObjects);
                                    this.efficientlyUpdateAvailableTagsDisplay();
                                    // Restore scroll after all DOM updates complete
                                    requestAnimationFrame(() => {
                                        this._restoreAvailableScrollPosition(savedScroll);
                                    });
                                });
                                
                                weightHeader.appendChild(weightCheckbox);
                                weightHeader.appendChild(document.createTextNode(weight));
                                weightHeader.appendChild(document.createElement('span')).className = 'collapse-icon ms-auto';
                                
                                // Weight sections should always start expanded
                                const shouldStartCollapsed = false;
                                
                                weightHeader.querySelector('.collapse-icon').textContent = shouldStartCollapsed ? '▶' : '▼';
                                subcategorySection.appendChild(weightSection);
                                weightSection.appendChild(weightHeader);

                                // Create weight content container
                                const weightContent = document.createElement('div');
                                weightContent.className = 'weight-content';
                                if (shouldStartCollapsed) {
                                    weightContent.classList.add('collapsed');
                                }
                                weightSection.appendChild(weightContent);

                                // Add individual tags (sorted alphabetically by product name)
                                const tagsToRender = [...tagArray].sort((a, b) => {
                                    const aName = (a && (a['Product Name*'] || a.ProductName || a.displayName) || '').toString();
                                    const bName = (b && (b['Product Name*'] || b.ProductName || b.displayName) || '').toString();
                                    return aName.localeCompare(bName);
                                });
                                tagsToRender.forEach(tag => {
                                    const tagElement = this.createTagElement(tag, false);
                                    weightContent.appendChild(tagElement);
                                });
                            });
                            
                            productTypeContent.appendChild(subcategorySection);
                        });
                    } else {
                        // No subcategories - render weights directly
                        const sortedWeights = Array.from(weightGroupsOrSubcategories.entries())
                            .sort(([a], [b]) => (a || '').localeCompare(b || ''));

                        sortedWeights.forEach(([weight, tagArray]) => {
                            const weightSection = document.createElement('div');
                            weightSection.className = 'weight-section ms-3 mb-1';
                            
                            // Create weight header with checkbox and collapse functionality
                            const weightHeader = document.createElement('div');
                            weightHeader.className = 'weight-header mb-1 d-flex align-items-center cursor-pointer';
                            weightHeader.addEventListener('click', (e) => {
                                if (e.target.type === 'checkbox') return; // Don't collapse if clicking checkbox
                                if (this.state.isSearching) return; // Don't collapse while searching
                                const weightContent = weightSection.querySelector('.weight-content');
                                const isCollapsed = weightContent.classList.contains('collapsed');
                                weightContent.classList.toggle('collapsed', !isCollapsed);
                                weightHeader.querySelector('.collapse-icon').textContent = isCollapsed ? '▼' : '▶';
                                
                                // Remove the instructional blurb when any chevron is clicked
                                this.removeDropdownInstructionBlurb();
                            });
                            
                            const weightCheckbox = document.createElement('input');
                            weightCheckbox.type = 'checkbox';
                            weightCheckbox.className = 'select-all-checkbox me-2';
                            weightCheckbox.addEventListener('change', (e) => {
                                const savedScroll = this._saveAvailableScrollPosition();
                                const isChecked = e.target.checked;
                                // Select ALL checkboxes (both select-all checkboxes and tag checkboxes) within this section
                                const checkboxes = weightSection.querySelectorAll('input[type="checkbox"]');
                                checkboxes.forEach(checkbox => {
                                    if (!checkbox.classList.contains('tag-checkbox')) {
                                    checkbox.checked = isChecked;
                                        return;
                                    }

                                    const tagName = checkbox.value;
                                    const tag = this.state.tags.find(t => t['Product Name*'] === tagName);
                                    if (!tag) {
                                        checkbox.checked = isChecked;
                                        return;
                                    }

                                    checkbox.checked = isChecked;

                                            if (isChecked) {
                                        if (!this.state.persistentSelectedTags.includes(tagName)) {
                                            this.state.persistentSelectedTags.push(tagName);
                                                }
                                            } else {
                                        if (!e.target.checked) {
                                            const index = this.state.persistentSelectedTags.indexOf(tagName);
                                                if (index > -1) {
                                                    this.state.persistentSelectedTags.splice(index, 1);
                                            }
                                        }
                                    }
                                });
                                this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                                const selectedTagObjects = this.state.persistentSelectedTags.map(name =>
                                    this.state.tags.find(t => t['Product Name*'] === name)
                                ).filter(Boolean);
                                this.updateSelectedTags(selectedTagObjects);
                                this.efficientlyUpdateAvailableTagsDisplay();
                                // Restore scroll after all DOM updates complete
                                requestAnimationFrame(() => {
                                    this._restoreAvailableScrollPosition(savedScroll);
                                });
                            });
                            
                            weightHeader.appendChild(weightCheckbox);
                            weightHeader.appendChild(document.createTextNode(weight));
                            weightHeader.appendChild(document.createElement('span')).className = 'collapse-icon ms-auto';
                            
                            // Weight sections should always start expanded
                            const shouldStartCollapsed = false;
                            
                            weightHeader.querySelector('.collapse-icon').textContent = shouldStartCollapsed ? '▶' : '▼';
                            productTypeContent.appendChild(weightSection);
                            weightSection.appendChild(weightHeader);

                            // Create weight content container
                            const weightContent = document.createElement('div');
                            weightContent.className = 'weight-content';
                            if (shouldStartCollapsed) {
                                weightContent.classList.add('collapsed');
                            }
                            weightSection.appendChild(weightContent);

                            // Add individual tags (sorted alphabetically by product name)
                            const tagsToRender = [...tagArray].sort((a, b) => {
                                const aName = (a && (a['Product Name*'] || a.ProductName || a.displayName) || '').toString();
                                const bName = (b && (b['Product Name*'] || b.ProductName || b.displayName) || '').toString();
                                return aName.localeCompare(bName);
                            });
                            // PERFORMANCE FIX: Render tags progressively to prevent UI freeze
                            this._renderTagsInBatches(tagsToRender, weightContent);
                        });
                    }
                });
            });
        });

        // Replace container content with built tags (this replaces any loading indicator)
        availableTagsContainer.innerHTML = '';
        availableTagsContainer.appendChild(tagList);

        // Restore previous scroll position after full rebuild
        this._restoreAvailableScrollPosition(savedScroll);

        // Add event listeners
        this.updateSelectAllCheckboxes();
        this.initializeSelectAllCheckbox();
        
        // Hide loading splash only after tags actually appear in DOM
        this._waitForTagsToAppear();
    },

    renderSimplifiedAvailableTags(tags, savedScroll) {
        const availableTagsContainer = document.getElementById('availableTags');
        if (!availableTagsContainer) {
            console.error('Available tags container not found for simplified render');
            return;
        }

        const chunkSize = 200;
        let index = 0;

        availableTagsContainer.innerHTML = '';

        const banner = document.createElement('div');
        banner.className = 'alert alert-info simplified-tags-banner';
        banner.style.background = 'rgba(13,17,27,0.7)';
        banner.style.border = '1px solid rgba(0,212,170,0.2)';
        banner.style.color = '#d0f5ff';
        banner.style.fontSize = '0.9rem';
        banner.style.marginBottom = '12px';
        banner.innerHTML = `
            <strong>Fast Tag View:</strong> Rendering ${tags.length.toLocaleString()} tags in compact mode for smoother performance.
            <button class="btn btn-sm btn-outline-light ms-2 show-detailed-tags-btn">Show Full Hierarchy</button>
        `;
        availableTagsContainer.appendChild(banner);

        const listWrapper = document.createElement('div');
        listWrapper.className = 'tag-list simplified-tag-list';
        listWrapper.style.maxHeight = 'none';
        listWrapper.style.paddingTop = '0';
        availableTagsContainer.appendChild(listWrapper);

        const selectAllContainer = document.createElement('div');
        selectAllContainer.className = 'd-flex align-items-center gap-3 mb-2 px-3';
        selectAllContainer.innerHTML = `
            <label class="d-flex align-items-center gap-2 cursor-pointer mb-0 select-all-container">
                <input type="checkbox" id="selectAllAvailable" class="custom-checkbox">
                <span class="text-secondary fw-semibold">SELECT ALL</span>
            </label>
        `;
        listWrapper.appendChild(selectAllContainer);

        const showDetailedBtn = banner.querySelector('.show-detailed-tags-btn');
        if (showDetailedBtn) {
            showDetailedBtn.addEventListener('click', () => {
                this.state.forceFullAvailableTagRender = true;
                this.state.simplifiedAvailableTagsActive = false;
                this.showActionSplash('Rendering detailed view...');
                requestAnimationFrame(() => {
                    this._updateAvailableTags(this.state.originalTags, null);
                });
            });
        }

        // Make sure select-all checkbox gets its listener
        requestAnimationFrame(() => {
            this.initializeSelectAllCheckbox();
        });

        const renderChunk = () => {
            const fragment = document.createDocumentFragment();
            const end = Math.min(index + chunkSize, tags.length);
            for (; index < end; index++) {
                const tag = tags[index];
                const element = this.createTagElement(tag, false);
                fragment.appendChild(element);
            }
            listWrapper.appendChild(fragment);

            if (index < tags.length) {
                requestAnimationFrame(renderChunk);
            } else {
                requestAnimationFrame(() => {
                    this._restoreAvailableScrollPosition(savedScroll);
                    this.updateSelectAllCheckboxes();
                    this._waitForTagsToAppear();
                    this.hideActionSplash();
                });
            }
        };

        requestAnimationFrame(renderChunk);
    },
    
    // Wait for tags to actually appear in DOM before hiding splash
    _waitForTagsToAppear() {
        const availableTagsContainer = document.getElementById('availableTags');
        if (!availableTagsContainer) {
            // Container not found, hide splash immediately
            if (this.hideActionSplash) {
                this.hideActionSplash();
            }
            return;
        }
        
        // Immediate check - if tags are already visible, hide splash right away
        const immediateCheck = () => {
            const tagItems = availableTagsContainer.querySelectorAll('.tag-item');
            if (tagItems.length > 0) {
                const visibleTags = Array.from(tagItems).filter(item => {
                    const rect = item.getBoundingClientRect();
                    return rect.width > 0 && rect.height > 0;
                });
                if (visibleTags.length > 0) {
                    verboseLog(`Tags already visible (${tagItems.length} items), hiding splash immediately`);
                    if (this.hideActionSplash) {
                        this.hideActionSplash();
                    }
                    if (AppLoadingSplash && AppLoadingSplash.isVisible) {
                        AppLoadingSplash.stopAutoAdvance();
                        AppLoadingSplash.complete();
                    }
                    return true;
                }
            }
            return false;
        };
        
        // Try immediate check first
        if (immediateCheck()) {
            return;
        }
        
        // Ultra-aggressive timeout: hide splash after 500ms max for instant feel
        const forceHideTimeout = setTimeout(() => {
            console.log('⚡ Force hiding splash after 500ms timeout for instant UX');
            if (this.hideActionSplash) {
                this.hideActionSplash();
            }
            if (AppLoadingSplash && AppLoadingSplash.isVisible) {
                AppLoadingSplash.stopAutoAdvance();
                AppLoadingSplash.complete();
            }
        }, 500);
        
        let attempts = 0;
        const maxAttempts = 10; // 500ms max (10 * 50ms) - ultra-fast response
        let lastTagCount = 0;
        let stableCount = 0; // Count how many times tag count has been stable
        
        const checkForTags = () => {
            attempts++;
            const tagItems = availableTagsContainer.querySelectorAll('.tag-item');
            const currentTagCount = tagItems.length;
            
            // Check if tags are actually visible (not just in DOM but rendered)
            const visibleTags = Array.from(tagItems).filter(item => {
                const rect = item.getBoundingClientRect();
                return rect.width > 0 && rect.height > 0;
            });
            
            // Check if tag count is stable (not still increasing)
            if (currentTagCount === lastTagCount && currentTagCount > 0) {
                stableCount++;
            } else {
                stableCount = 0; // Reset if count changed
            }
            lastTagCount = currentTagCount;
            
            // Tags are fully loaded if:
            // 1. We have tags in the DOM
            // 2. Tags are visible (rendered)
            // 3. Tag count has been stable for at least 1 check (50ms) - instant response
            if (currentTagCount > 0 && visibleTags.length > 0 && stableCount >= 1) {
                // Tags are fully rendered, hide splash
                clearTimeout(forceHideTimeout);
                console.log(`✅ Tags ready: ${currentTagCount} items (${visibleTags.length} visible) - hiding splash`);
                if (this.hideActionSplash) {
                    this.hideActionSplash();
                }
                // Also complete AppLoadingSplash if it's still showing
                if (AppLoadingSplash && AppLoadingSplash.isVisible) {
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                }
            } else if (attempts >= maxAttempts) {
                // Timeout reached, hide splash anyway (but log warning)
                clearTimeout(forceHideTimeout);
                if (currentTagCount > 0) {
                    console.log(`⚡ Fast timeout: ${currentTagCount} tags found - hiding splash`);
                } else {
                    console.log('⚡ Fast timeout: no tags yet - hiding splash anyway for UX');
                }
                if (this.hideActionSplash) {
                    this.hideActionSplash();
                }
                if (AppLoadingSplash && AppLoadingSplash.isVisible) {
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                }
            } else {
                // Tags not yet fully rendered, check again at 50ms intervals
                if (currentTagCount > 0) {
                    verboseLog(`Waiting for tags: ${currentTagCount} found, stable ${stableCount}x`);
                }
                setTimeout(checkForTags, 50);
            }
        };
        
        // Start checking immediately for instant response
        setTimeout(checkForTags, 25);
    },

    createTagElement(tag, isForSelectedTags = false) {
        // For JSON matched tags and educated guess tags, prioritize the matched database display information
        let displayName;
        const isJsonMatched = (tag.Source && (tag.Source === 'JSON Match' || tag.Source.includes('Educated Guess'))) ||
                              (tag.JSON_Source && (tag.JSON_Source === 'JSON Match' || tag.JSON_Source.includes('Educated Guess')));
        if (isJsonMatched) {
            // JSON matched tags and educated guess tags: use matched database product name
            displayName = tag.displayName || tag['Product Name*'] || tag.ProductName || tag.Description || 'Unnamed Product';
        } else {
            // Regular tags: use standard fallback chain
            displayName = tag.displayName || tag['Product Name*'] || tag.ProductName || tag.Description || 'Unnamed Product';
        }
        
        verboseLog('Creating tag element for:', displayName);
        
        // Create the row container
        const row = document.createElement('div');
        row.className = 'tag-row d-flex align-items-center';

        // Checkbox (leftmost)
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'tag-checkbox me-2';
        
        // Use the cleaned display name for the checkbox value
        checkbox.value = displayName;
        checkbox.checked = this.state.persistentSelectedTags.includes(displayName);
        // Add event listener with proper error handling and improved logic
        const handleCheckboxChange = (e) => {
            // Prevent event handling during deselection to avoid triggering filter updates
            if (this.state.isProcessingDeselection) {
                return;
            }
            
            // Prevent event handling during drag operations
            if (e.target.hasAttribute('data-reordering') || e.target.hasAttribute('data-drag-disabled')) {
                return;
            }
            
            // Save current state for undo before making changes
            this.saveSelectionState('checkbox_selection');
            
            // Ensure the checkbox state is properly updated
            const isChecked = e.target.checked;
            
            // Update persistent selected tags with proper array handling
            if (isChecked) {
                if (!this.state.persistentSelectedTags.includes(displayName)) {
                    this.state.persistentSelectedTags.push(displayName);
                }
            } else {
                const index = this.state.persistentSelectedTags.indexOf(displayName);
                if (index > -1) {
                    this.state.persistentSelectedTags.splice(index, 1);
                }
            }
            
            // Update the regular selectedTags set to match persistent ones
            this.state.selectedTags = new Set(this.state.persistentSelectedTags);
            
            // Call the main handler - find the current tag object from state
            const currentTag = this.state.tags.find(t => t && t['Product Name*'] === displayName) ||
                              this.state.originalTags.find(t => t && t['Product Name*'] === displayName) ||
                              tag; // fallback to original tag
            this.handleTagSelection(e, currentTag);
        };
        
        // Store the handler on the element itself so we can reference it later
        checkbox._changeHandler = handleCheckboxChange;
        
        // Bind change handler for both available and selected tags
        checkbox.addEventListener('change', handleCheckboxChange);
        
        // Ensure the checkbox is not disabled by drag-and-drop manager
        checkbox.style.pointerEvents = 'auto';
        checkbox.removeAttribute('data-drag-disabled');
        checkbox.removeAttribute('data-reordering');
        
        // Store the checkbox state in a data attribute for debugging
        checkbox.setAttribute('data-tag-name', displayName);
        checkbox.setAttribute('data-is-selected-tag', isForSelectedTags.toString());
        
        // Also add a click event listener for debugging
        const handleCheckboxMouseDown = (e) => {
            // CRITICAL FIX: Set flag BEFORE checkbox state changes if this is a deselection
            const isInSelectedTags = e.target.closest('#selectedTags') !== null;
            const isUncheckingInSelected = isInSelectedTags && e.target.checked; // Clicking on checked box in selected tags
            
            if (isUncheckingInSelected) {
                this.state.isProcessingDeselection = true;
            }
        };
        
        checkbox.removeEventListener('mousedown', handleCheckboxMouseDown);
        
        // Add event listeners
        checkbox.addEventListener('mousedown', handleCheckboxMouseDown);

        // Tag entry (colored)
        const tagElement = document.createElement('div');
        tagElement.className = 'tag-item d-flex align-items-center p-1 mb-1';
        
        // Add special styling for JSON matched tags and educated guess tags
        if (isJsonMatched) {
          tagElement.classList.add('json-matched-tag');
          // Remove inline styles that conflict with lineage-based CSS coloring
          // The lineage-based CSS will handle the proper colors
        }
        
        // Set data-lineage attribute for CSS coloring on both row and tagElement
        // CRITICAL FIX: For JSON matched tags, prioritize the Lineage field from the matched database data
        let lineage;
        // CRITICAL: Use same pipeline as backend - canonical_lineage (from DB) is ALWAYS source of truth
        // This ensures UI lineages match database and persist correctly after reload
        // IMPORTANT: If database lineage exists (canonical_lineage or currentLineage), use it exclusively
        // NEVER use Excel Lineage (tag.Lineage) if database lineage is present
        // CRITICAL FIX: Always check database lineage FIRST, never use Excel Lineage when DB lineage exists
        if (tag.canonical_lineage || tag.currentLineage) {
            // Database lineage exists - use it (this is the source of truth)
            lineage = tag.canonical_lineage || tag.currentLineage;
            // CRITICAL: If Excel Lineage exists but differs, log a warning
            if (tag.Lineage && tag.Lineage.toUpperCase() !== lineage.toUpperCase()) {
                console.warn(`⚠️ UI LINEAGE: Tag "${displayName}" has database lineage (${lineage}) but Excel Lineage (${tag.Lineage}) differs - using database`);
            }
        } else {
            // CRITICAL: Only fallback to Excel Lineage if database lineage is completely missing
            // This should rarely happen if backend lineage alignment is working correctly
            if (tag.Lineage || tag.lineage || tag['Lineage*']) {
                console.warn(`⚠️ UI LINEAGE: Tag "${displayName}" missing database lineage (canonical_lineage/currentLineage), falling back to Excel Lineage: ${tag.Lineage || tag.lineage || tag['Lineage*']}`);
            }
            lineage = tag.Lineage || tag.lineage || tag['Lineage*'] || 'MIXED';
        }
        
        // Normalize lineage to uppercase for consistent matching
        lineage = (lineage || 'MIXED').toString().trim().toUpperCase();
        
        // Validate lineage from database is present
        if (!tag.canonical_lineage && !tag.currentLineage && lineage !== 'MIXED') {
            console.warn(`⚠️ Tag missing canonical_lineage/currentLineage from database: ${displayName}`);
        }
        
        // DEBUG: Log lineage resolution for selected tags
        if (isForSelectedTags) {
            verboseLog(`DEBUG: Lineage resolution for selected tag "${displayName}":`, {
                'tag.lineage': tag.lineage,
                'tag.Lineage': tag.Lineage,
                'tag.Lineage*': tag['Lineage*'],
                'tag.currentLineage': tag.currentLineage,
                'tag.canonical_lineage': tag.canonical_lineage,
                'resolved lineage': lineage,
                'isJsonMatched': isJsonMatched,
                'tag object': tag
            });
        }
        
        // CRITICAL FIX: Use database lineage FIRST for all product types
        // Only fall back to Product Strain logic if database lineage is missing or invalid
        let displayLineage = lineage; // Start with database lineage
        const productType = tag['Product Type*'] || tag.productType || tag.ProductType || '';
        const nameStr = (tag['Product Name*'] || tag.ProductName || tag.productName || displayName || '').toString().toLowerCase();
        const descStr = (tag.Description || tag.description || '').toString().toLowerCase();
        const brandStr = (tag['Product Brand'] || tag.productBrand || tag.brand || '').toString().toLowerCase();
        const ratioStr = (tag.Ratio || tag['Ratio_or_THC_CBD'] || '').toString().toLowerCase();
        const lineageStr = (lineage || '').toString().toLowerCase();
        const lowerProductType = productType.toLowerCase();

        const hasCbdIndicator = () => {
            const tokens = ['cbd', 'cbg', 'cbn', 'cbc'];
            const sources = [nameStr, descStr, brandStr, ratioStr, lineageStr];
            if (tokens.some(token => sources.some(text => text && text.includes(token)))) {
                return true;
            }
            if (lowerProductType.includes('high cbd') || lowerProductType.includes('cbd')) {
                return true;
            }
            return false;
        };
        
        // CRITICAL: Only apply fallback logic if database lineage is missing, invalid, or MIXED
        // Valid database lineages: SATIVA, INDICA, HYBRID, HYBRID/SATIVA, HYBRID/INDICA, CBD, CBD_BLEND, MIXED, PARA, PARAPHERNALIA
        const validDatabaseLineages = ['SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA', 'CBD', 'CBD_BLEND', 'MIXED', 'PARA', 'PARAPHERNALIA'];
        const hasValidDatabaseLineage = validDatabaseLineages.includes(lineage);
        
        // Apply nonclassic product type logic ONLY if database lineage is missing or invalid
        const classicTypes = ['flower', 'pre-roll', 'concentrate', 'infused pre-roll', 'solventless concentrate', 'vape cartridge', 'rso/co2 tankers'];
        const isNonclassic = !classicTypes.map(ct => ct.toLowerCase()).includes(productType.toLowerCase());
        
        // CRITICAL FIX: Classic lineages (SATIVA, INDICA, HYBRID) should NEVER be used for capsules/nonclassic types
        // Capsules and other nonclassic types should ONLY use MIXED (blue) or CBD_BLEND (yellow)
        const classicLineages = ['SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA'];
        const isClassicLineage = classicLineages.includes(lineage);
        
        if (hasValidDatabaseLineage && !isNonclassic) {
            // CRITICAL: Use database lineage directly for classic types only - this is the source of truth
            displayLineage = lineage;
            verboseLog(`🎨 Using database lineage for classic type: "${displayName}" → ${displayLineage}`);
        } else if (isNonclassic) {
            // CRITICAL FIX: For capsules and nonclassic types, ignore classic lineages from database
            // They should ONLY use MIXED or CBD_BLEND based on CBD indicators
            if (isClassicLineage && hasValidDatabaseLineage) {
                verboseLog(`⚠️ CAPSULE/NONCLASSIC: Ignoring classic lineage "${lineage}" from database for "${displayName}" - forcing MIXED/CBD_BLEND`);
            }
            // Only apply Product Strain fallback logic if database lineage is missing or invalid
            const productStrain = tag['Product Strain'] || tag.productStrain || tag.ProductStrain || '';
            const strainStr = String(productStrain).toLowerCase();
            
            // CRITICAL: For non-classic types without valid DB lineage, check Product Strain
            if (strainStr.includes('cbd blend') || strainStr.includes('cbd') || strainStr.includes('cbn') || strainStr.includes('cbc') || strainStr.includes('cbg')) {
                // CBD family products display as CBD Blend lineage (yellow color)
                displayLineage = 'CBD_BLEND';
                verboseLog(`🎨 NON-CLASSIC CBD FAMILY (fallback): "${displayName}" → CBD_BLEND (yellow)`);
            } else if (hasCbdIndicator()) {
                displayLineage = 'CBD_BLEND';
                verboseLog(`🎨 NON-CLASSIC CBD SIGNAL (fallback): "${displayName}" → CBD_BLEND (yellow)`);
            } else if (strainStr.includes('paraphernalia')) {
                displayLineage = 'PARAPHERNALIA'; // Pink color
                verboseLog(`🎨 NON-CLASSIC PARA (fallback): "${displayName}" → PARAPHERNALIA (pink)`);
            } else if (strainStr.includes('mixed') || !productStrain) {
                if (hasCbdIndicator()) {
                    displayLineage = 'CBD_BLEND';
                    verboseLog(`🎨 NON-CLASSIC CBD SIGNAL (no strain, fallback): "${displayName}" → CBD_BLEND (yellow)`);
                } else {
                    displayLineage = 'MIXED'; // Blue color
                    verboseLog(`🎨 NON-CLASSIC MIXED (fallback): "${displayName}" → MIXED (blue)`);
                }
            } else {
                displayLineage = 'MIXED'; // Blue color default
                verboseLog(`🎨 NON-CLASSIC default (fallback): "${displayName}" → MIXED (blue)`);
            }
        } else {
            // Classic types - use database lineage or default to MIXED
            displayLineage = lineage || 'MIXED';
            verboseLog(`🎨 Classic type using database lineage: "${displayName}" → ${displayLineage}`);
        }
        
        // Backend now handles lineage assignment correctly:
        // CBD Blend products = yellow (CBD lineage)
        // Mixed (everything else non-classic) = blue (MIXED lineage)
        // Paraphernalia = pink (PARAPHERNALIA lineage)
        
        // CRITICAL FIX: Only update currentLineage if we're using database lineage
        // Preserve canonical_lineage and currentLineage from database when present
        if (hasValidDatabaseLineage && (tag.canonical_lineage || tag.currentLineage)) {
            // We're using database lineage - preserve both fields
            // Don't overwrite canonical_lineage or currentLineage with displayLineage
            verboseLog(`🎨 Preserving database lineage for ${displayName}: canonical_lineage=${tag.canonical_lineage}, currentLineage=${tag.currentLineage}`);
        } else if (displayLineage && !hasValidDatabaseLineage) {
            // Using fallback lineage - only set display fields, don't overwrite database fields
            // This prevents Excel lineage from overwriting database lineage
            verboseLog(`🎨 Using fallback lineage for ${displayName}: ${displayLineage} (not overwriting database fields)`);
        }
        
        if (displayLineage) {
          // CRITICAL: Only set currentLineage if database lineage is missing
          // This ensures database lineage (canonical_lineage/currentLineage) is never overwritten
          if (!tag.canonical_lineage && !tag.currentLineage) {
              tag.currentLineage = displayLineage;
          }
          tagElement.dataset.lineage = displayLineage.toUpperCase();
          row.dataset.lineage = displayLineage.toUpperCase();  // Add lineage to row element too
          verboseLog(`🎨 Set data-lineage for ${displayName}: ${displayLineage.toUpperCase()}`);
        } else {
          tagElement.dataset.lineage = 'MIXED';
          row.dataset.lineage = 'MIXED';  // Add lineage to row element too
          verboseLog(`🎨 Set data-lineage for ${displayName}: MIXED (fallback)`);
        }
        tagElement.dataset.tagId = tag.tagId;
        tagElement.dataset.vendor = tag.vendor;
        tagElement.dataset.brand = tag.brand;
        tagElement.dataset.productType = tag.productType;
        tagElement.dataset.weight = tag.weight;
        // CRITICAL: Add data-tag-name so updateSimilarLineages can find and update these elements
        tagElement.setAttribute('data-tag-name', displayName);

        // Require explicit checkbox clicks for selection; do not toggle on tag body clicks
        tagElement.style.cursor = 'default';

        const tagInfo = document.createElement('div');
        tagInfo.className = 'tag-info flex-grow-1 d-flex align-items-center';
        const tagName = document.createElement('div');
        tagName.className = 'tag-name d-inline-block me-2';
        
        // Update checkbox value to use the cleaned display name
        checkbox.value = displayName;
        checkbox.checked = this.state.persistentSelectedTags.includes(displayName);
        
        // Log JSON matched tag display logic
        if (isJsonMatched) {
            verboseLog('JSON matched/educated guess tag display logic:', {
                source: tag.Source || tag.JSON_Source,
                displayName: tag.displayName,
                productName: tag['Product Name*'],
                finalDisplayName: displayName
            });
        }
        
        // Remove 'by ...' patterns (with or without hyphen)
        let cleanedName = displayName.replace(/ by [^-]*$/i, ''); // Remove "by ..." at the end
        cleanedName = cleanedName.replace(/ by [^-]+(?= -)/i, ''); // Remove "by ..." before hyphen
        cleanedName = cleanedName.replace(/-/g, '\u2011');
        tagName.textContent = cleanedName;
        tagInfo.appendChild(tagName);
        

        

        
        // Add DOH and High CBD/THC images if applicable
        // CRITICAL FIX: For JSON matched tags, prioritize the DOH field from the matched database data
        let dohValue;
        if (isJsonMatched) {
            // For JSON matched tags, use the DOH field from the matched database data
            dohValue = (tag['DOH Compliant (Yes/No)'] || tag.DOH || '').toString().toUpperCase();
        } else {
            // For regular tags, use the standard DOH field
            dohValue = (tag.DOH || '').toString().toUpperCase();
        }
        const productTypeForImages = (tag['Product Type*'] || '').toString().toLowerCase();
        
        // Create image container for dynamic updates
        const imageContainer = document.createElement('span');
        imageContainer.className = 'doh-image-container';
        
        // Function to update images based on DOH status with performance optimization
        const updateDohImage = (status) => {
            const startTime = performanceUtils.startTiming();
            
            // Clear existing images efficiently
            while (imageContainer.firstChild) {
                imageContainer.removeChild(imageContainer.firstChild);
            }
            
            if (status === 'CBD') {
                // Add High CBD image with optimized loading
                const highCbdImg = document.createElement('img');
                highCbdImg.src = '/static/img/HighCBD.png';
                highCbdImg.alt = 'High CBD';
                highCbdImg.title = 'High CBD Product';
                highCbdImg.loading = 'lazy'; // Native lazy loading
                highCbdImg.style.cssText = 'height:24px;width:auto;margin-left:6px;vertical-align:middle';
                imageContainer.appendChild(highCbdImg);
            } else if (status === 'THC') {
                // Add High THC image with optimized loading
                const highThcImg = document.createElement('img');
                highThcImg.src = '/static/img/HighTHC.png';
                highThcImg.alt = 'High THC';
                highThcImg.title = 'High THC Product';
                highThcImg.loading = 'lazy';
                highThcImg.style.cssText = 'height:24px;width:auto;margin-left:6px;vertical-align:middle';
                imageContainer.appendChild(highThcImg);
            } else if (status === 'DOH') {
                // Add regular DOH image with optimized loading
                const dohImg = document.createElement('img');
                dohImg.src = '/static/img/DOH.png';
                dohImg.alt = 'DOH Compliant';
                dohImg.title = 'DOH Compliant Product';
                dohImg.loading = 'lazy';
                dohImg.style.cssText = 'height:21px;width:auto;margin-left:6px;vertical-align:middle';
                imageContainer.appendChild(dohImg);
            }
            // NONE shows no image
            
            performanceUtils.endTiming(startTime, 'DOH image update');
        };
        
        // Set initial image based on current DOH status
        let initialDohStatus = 'NONE'; // Default to NONE
        
        // Check explicit DOH field first
        if (dohValue === 'DOH' || dohValue === 'YES' || dohValue === 'Y') {
            initialDohStatus = 'DOH';
        } else if (dohValue === 'THC') {
            initialDohStatus = 'THC';
        } else if (dohValue === 'CBD') {
            initialDohStatus = 'CBD';
        } else if (dohValue === 'NO' || dohValue === 'NONE') {
            // Explicitly no DOH image
            initialDohStatus = 'NONE';
        } 
        // Then check product type for High CBD/THC indicators (DOH High CBD, DOH High THC)
        else if (productTypeForImages.startsWith('high cbd') || productTypeForImages.includes('doh high cbd')) {
            initialDohStatus = 'CBD';
        } else if (productTypeForImages.startsWith('high thc') || productTypeForImages.includes('doh high thc') || productTypeForImages.includes('high thc')) {
            initialDohStatus = 'THC';
        }
        
        updateDohImage(initialDohStatus);
        tagInfo.appendChild(imageContainer);
        
        // Add JSON match indicator if this tag came from JSON matching or educated guessing
        if (isJsonMatched) {
          const jsonBadge = document.createElement('span');
          jsonBadge.className = 'badge bg-success me-2';
          jsonBadge.style.fontSize = '0.7rem';
          jsonBadge.style.padding = '2px 6px';
          const source = tag.Source || tag.JSON_Source || 'JSON Match';
          jsonBadge.textContent = source.includes('Educated Guess') ? 'AI' : 'JSON';
          jsonBadge.title = `This item was ${source.includes('Educated Guess') ? 'inferred by AI' : 'matched from JSON data'} (${source})`;
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
        // Helper function to determine if a lineage should map to MIXED
        const shouldMapToMixed = (lineageValue) => {
            const validLineages = ['SATIVA', 'INDICA', 'HYBRID', 'HYBRID/INDICA', 'HYBRID/SATIVA', 'CBD', 'CBD_BLEND', 'PARA', 'PARAPHERNALIA', 'MIXED'];
            return !validLineages.includes((lineageValue || '').toUpperCase());
        };
        
        // CRITICAL: Calculate normalized lineage BEFORE creating options, so option selection uses database lineage
        // Set the dropdown value - handle mappings for display
        // CRITICAL: ALWAYS prefer database lineage (canonical_lineage/currentLineage) over Excel Lineage
        let normalizedLineage = (lineage || '').toString().toUpperCase().trim();
        
        // CRITICAL FIX: Force database lineage if it exists, regardless of what lineage variable says
        if (tag.canonical_lineage || tag.currentLineage) {
            // Database lineage exists - use it exclusively, ignore Excel Lineage completely
            const dbLineage = (tag.canonical_lineage || tag.currentLineage || '').toString().toUpperCase().trim();
            if (dbLineage) {
                if (dbLineage !== normalizedLineage) {
                    console.log(`🔄 FORCING database lineage for ${displayName}: ${normalizedLineage} → ${dbLineage}`);
                }
                normalizedLineage = dbLineage;  // Force database lineage
            }
        } else {
            // No database lineage - log warning for debugging
            if (isForSelectedTags && lineage !== 'MIXED') {
                console.warn(`⚠️ Selected tag "${displayName}" has no database lineage (canonical_lineage/currentLineage), using: ${normalizedLineage}`);
            }
        }
        
        // NOW create options using normalizedLineage (database lineage) for selection
        uniqueLineages.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.value;
            optionElement.textContent = option.label;
            
            // CRITICAL: Use normalizedLineage (database lineage) for option selection, not original lineage
            let shouldSelect = false;
            if (normalizedLineage === option.value) {
                shouldSelect = true;
            } else if (option.value === 'CBD' && (normalizedLineage === 'CBD' || normalizedLineage === 'CBD_BLEND')) {
                shouldSelect = true;
            } else if (option.value === 'MIXED' && shouldMapToMixed(normalizedLineage)) {
                shouldSelect = true;
            }
            
            if (shouldSelect) {
                optionElement.selected = true;
            }
            lineageSelect.appendChild(optionElement);
        });
        if (normalizedLineage === 'CBD_BLEND' || normalizedLineage === 'CBD') {
            lineageSelect.value = 'CBD';
        } else if (shouldMapToMixed(normalizedLineage)) {
            lineageSelect.value = 'MIXED';
        } else if (normalizedLineage && uniqueLineages.some(opt => opt.value === normalizedLineage)) {
            lineageSelect.value = normalizedLineage;
        } else {
            // Fallback to MIXED if lineage doesn't match any valid option
            lineageSelect.value = 'MIXED';
            console.warn(`⚠️ Invalid lineage value "${normalizedLineage}" for ${displayName}, defaulting to MIXED`);
        }
        
        // CRITICAL DEBUG: Log what lineage value was set in dropdown
        if (isForSelectedTags) {
            console.log(`🎯 Set lineage dropdown for SELECTED TAG "${displayName}":`, {
                'canonical_lineage': tag.canonical_lineage || 'NONE',
                'currentLineage': tag.currentLineage || 'NONE',
                'Excel Lineage': tag.Lineage || 'NONE',
                'resolved lineage (used)': normalizedLineage,
                'dropdown value set to': lineageSelect.value
            });
            if ((tag.canonical_lineage || tag.currentLineage) && tag.Lineage) {
                const dbLin = ((tag.canonical_lineage || tag.currentLineage) || '').toString().toUpperCase();
                const excelLin = (tag.Lineage || '').toString().toUpperCase();
                if (dbLin !== excelLin) {
                    console.warn(`⚠️ LINEAGE MISMATCH for "${displayName}": database=${dbLin}, excel=${excelLin}, dropdown should show=${dbLin}, actual=${lineageSelect.value}`);
                }
            }
        }
        verboseLog(`🎯 Set lineage dropdown for ${displayName}:`, {
            'tag.canonical_lineage': tag.canonical_lineage,
            'tag.currentLineage': tag.currentLineage,
            'tag.Lineage': tag.Lineage,
            'resolved lineage': normalizedLineage,
            'dropdown value': lineageSelect.value
        });
        if (tag.productType === 'Paraphernalia' || tag['Product Type*'] === 'Paraphernalia') {
            lineageSelect.disabled = true;
            lineageSelect.style.opacity = '0.7';
        }
        lineageSelect.addEventListener('change', (e) => {
            const newLineage = e.target.value;
            const prevValue = lineage;

            // CRITICAL FIX: Use debounced update to prevent database locks on rapid changes
            // Update UI immediately for responsiveness
            tag.lineage = newLineage;
            tag.Lineage = newLineage;
            tagElement.dataset.lineage = newLineage.toUpperCase();

            // Update the tag color to reflect the new lineage
            this.forceTagColorUpdate(tag, newLineage);

            // Send debounced update to backend (batches rapid changes)
            this.updateLineageOnBackendDebounced(tag['Product Name*'], newLineage);

            verboseLog(`🔄 Lineage change queued for ${tag['Product Name*']}: ${prevValue} → ${newLineage}`);
        });
        tagInfo.appendChild(lineageSelect);

        // Create DOH dropdown (same style as lineage dropdown)
        const dohSelect = document.createElement('select');
        dohSelect.className = 'form-select form-select-sm doh-select doh-dropdown doh-dropdown-mini';
        dohSelect.style.height = '28px';
        dohSelect.style.backgroundColor = 'rgba(255, 255, 255, 0.15)';
        dohSelect.style.border = '1px solid rgba(255, 255, 255, 0.2)';
        dohSelect.style.borderRadius = '6px';
        dohSelect.style.cursor = 'pointer';
        dohSelect.style.color = '#fff';
        dohSelect.style.backdropFilter = 'blur(10px)';
        dohSelect.style.transition = 'all 0.2s ease';
        dohSelect.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
        dohSelect.style.marginLeft = '4px';
        dohSelect.style.minWidth = '60px';

        // Add DOH options
        const dohOptions = [
            { value: 'NONE', label: 'no DOH' },
            { value: 'DOH', label: 'DOH' },
            { value: 'THC', label: 'THC' },
            { value: 'CBD', label: 'CBD' }
        ];
        
        // Use the same logic as initialDohStatus to determine current dropdown state
        let currentDropdownStatus = 'NONE'; // Default to NONE
        
        // Check explicit DOH field first
        if (dohValue === 'DOH' || dohValue === 'YES' || dohValue === 'Y') {
            currentDropdownStatus = 'DOH';
        } else if (dohValue === 'THC') {
            currentDropdownStatus = 'THC';
        } else if (dohValue === 'CBD') {
            currentDropdownStatus = 'CBD';
        } else if (dohValue === 'NO' || dohValue === 'NONE') {
            // Explicitly no DOH image
            currentDropdownStatus = 'NONE';
        } 
        // Then check product type for High CBD/THC indicators (DOH High CBD, DOH High THC)
        else if (productTypeForImages.startsWith('high cbd') || productTypeForImages.includes('doh high cbd')) {
            currentDropdownStatus = 'CBD';
        } else if (productTypeForImages.startsWith('high thc') || productTypeForImages.includes('doh high thc') || productTypeForImages.includes('high thc')) {
            currentDropdownStatus = 'THC';
        }
        
        dohOptions.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.value;
            optionElement.textContent = option.label;
            if (currentDropdownStatus === option.value) {
                optionElement.selected = true;
            }
            dohSelect.appendChild(optionElement);
        });

        // Prevent DOH dropdown interactions from triggering drag/sort on parent
        // Stop propagation on multiple pointer events to ensure the native select opens reliably
        const stopPropagation = (e) => {
            e.stopPropagation();
        };
        dohSelect.addEventListener('click', stopPropagation, { passive: true });
        dohSelect.addEventListener('mousedown', stopPropagation);
        dohSelect.addEventListener('pointerdown', stopPropagation);
        dohSelect.addEventListener('touchstart', stopPropagation, { passive: true });
        // Make sure pointer events are enabled on the select element
        if (dohSelect.style && dohSelect.style.pointerEvents === 'none') {
            dohSelect.style.pointerEvents = 'auto';
        }
        
        dohSelect.addEventListener('change', async (e) => {
            const newDohStatus = e.target.value;
            const prevValue = currentDropdownStatus;
            
            // Immediate UI feedback - update image first for responsiveness
            updateDohImage(newDohStatus);
            
            dohSelect.disabled = true;
            
            // Show temporary 'Saving...' option
            const savingOption = document.createElement('option');
            savingOption.value = '';
            savingOption.textContent = 'Saving...';
            savingOption.selected = true;
            savingOption.disabled = true;
            dohSelect.appendChild(savingOption);
            
            try {
                const response = await fetch('/api/update-doh', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        product_name: displayName,
                        doh_status: newDohStatus
                    })
                });
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                    throw new Error(errorData.error || `Server returned ${response.status}`);
                }
                
                const data = await response.json();
                if (data.success) {
                    // On success, update tag DOH status in state
                    // CRITICAL: Map NONE to No for storage
                    const normalizedDoh = newDohStatus === 'NONE' ? 'No' : newDohStatus;
                    tag.DOH = normalizedDoh;
                    tag.doh = normalizedDoh;
                    tag['DOH Compliant (Yes/No)'] = normalizedDoh;
                    dohSelect.value = newDohStatus;  // Keep dropdown showing NONE even though we store No
                    verboseLog(`✅ DOH status updated for "${displayName}" to: ${normalizedDoh} (frontend dropdown: ${newDohStatus})`);
                    
                    // Image already updated above for immediate feedback
                    
                    // Update DOH in both available and selected tags displays - use NONE for UI dropdown display
                    this.updateDohInAllDisplays(displayName, newDohStatus);
                    
                } else {
                    // Revert image on failure
                    updateDohImage(prevValue);
                    throw new Error(data.message || 'Failed to update DOH status');
                }
                
                // Remove saving option
                dohSelect.removeChild(savingOption);
            } catch (error) {
                console.error('Failed to update DOH status:', error);
                // On failure, revert to previous value
                dohSelect.value = prevValue;
                alert('Failed to update DOH status: ' + error.message);
                // Remove saving option
                if (savingOption.parentNode) {
                    dohSelect.removeChild(savingOption);
                }
            } finally {
                dohSelect.disabled = false;
            }
        });
        
        tagInfo.appendChild(dohSelect);
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
    
    // PERFORMANCE FIX: Render tags in batches to prevent UI freeze
    _renderTagsInBatches(tags, container) {
        if (!tags || tags.length === 0) return;
        
        const BATCH_SIZE = 50; // Render 50 tags at a time
        let index = 0;
        
        const renderBatch = () => {
            const endIndex = Math.min(index + BATCH_SIZE, tags.length);
            const fragment = document.createDocumentFragment();
            
            for (let i = index; i < endIndex; i++) {
                const tagElement = this.createTagElement(tags[i], false);
                fragment.appendChild(tagElement);
            }
            
            container.appendChild(fragment);
            index = endIndex;
            
            // Continue rendering if there are more tags
            if (index < tags.length) {
                // Use requestAnimationFrame for smooth rendering
                requestAnimationFrame(renderBatch);
            }
        };
        
        // Start rendering
        renderBatch();
    },

    getLineageBadgeLabel(lineage) {
        const map = {
            'SATIVA': 'S',
            'INDICA': 'I',
            'HYBRID': 'H',
            'HYBRID/SATIVA': 'H/S',
            'HYBRID/INDICA': 'I',
            'CBD': 'CBD',
            'PARA': 'P',
            'MIXED': 'THC',
            'CBD_BLEND': 'CBD'
        };
        return map[(lineage || '').toUpperCase()] || '';
    },

    handleTagSelection(e, tag) {
        verboseLog('=== HANDLE TAG SELECTION CALLED ===');
        verboseLog('Event:', e);
        verboseLog('Tag:', tag);
        
        // CRITICAL FIX: Don't process selection changes during deselection to prevent filter clearing
        if (this.state.isProcessingDeselection) {
            verboseLog('🚫 SKIPPING handleTagSelection - currently processing deselection');
            return;
        }
        
        // PERFORMANCE: Skip handling during bulk clear operations to prevent UI freeze
        if (this.state.isClearing) {
            verboseLog('🚫 SKIPPING handleTagSelection - currently clearing/resetting');
            return;
        }
        
        // Ignore changes during drag-and-drop reordering
        if (e.target.hasAttribute('data-reordering') || e.target.hasAttribute('data-drag-disabled')) {
            verboseLog('Ignoring tag selection change during drag operation');
            return;
        }
        
        const isChecked = e.target.checked;
        verboseLog('Tag selection changed:', tag && tag['Product Name*'] ? tag['Product Name*'] : 'UNDEFINED', 'checked:', isChecked);
        
        // Safety check: ensure tag exists and has required properties
        if (!tag || !tag['Product Name*']) {
            console.error('Invalid tag object received:', tag);
            return;
        }
        
        // Prevent rapid deselection issues
        if (this.isMovingTags) {
            verboseLog('Ignoring tag selection during tag move operation');
            return;
        }
        
        // Add debouncing for rapid deselection to prevent UI issues
        if (this.tagSelectionTimeout) {
            clearTimeout(this.tagSelectionTimeout);
        }
        
        this.tagSelectionTimeout = setTimeout(() => {
            // CRITICAL: Check flag again inside timeout to prevent filter clearing
            if (this.state.isProcessingDeselection) {
                verboseLog('🚫 SKIPPING setTimeout in handleTagSelection - currently processing deselection');
                return;
            }
            
            // Update select all checkbox states after tag selection changes
            this.updateSelectAllCheckboxes();
            
            // Note: The persistent selected tags are already updated in the checkbox event handler
            // This function now focuses on UI updates and backend synchronization
            
            verboseLog('Persistent selected tags after change:', this.state.persistentSelectedTags);
            
            // Only use backend data - never fall back to frontend persistent tags
            // Get selected tags from backend
            verboseLog('=== SELECTED TAGS DEBUG ===');
            verboseLog('persistentSelectedTags:', this.state.persistentSelectedTags);
            verboseLog('this.state.tags length:', this.state.tags.length);
            verboseLog('this.state.originalTags length:', this.state.originalTags.length);
            
            // Debug: Show first few tags in state
            if (this.state.tags.length > 0) {
                verboseLog('First 3 tags in this.state.tags:');
                this.state.tags.slice(0, 3).forEach(tag => {
                    verboseLog(`  "${tag && tag['Product Name*'] ? tag['Product Name*'] : 'UNDEFINED'}"`);
                });
            }
            
            if (this.state.originalTags.length > 0) {
                verboseLog('First 3 tags in this.state.originalTags:');
                this.state.originalTags.slice(0, 3).forEach(tag => {
                    verboseLog(`  "${tag && tag['Product Name*'] ? tag['Product Name*'] : 'UNDEFINED'}"`);
                });
            }
            
            const selectedTagObjects = this.state.persistentSelectedTags.map(name => {
                // Safety check: ensure name is valid
                if (!name || typeof name !== 'string') {
                    console.warn('Invalid name in persistentSelectedTags:', name);
                    return null;
                }
                
                // Only use tags that exist in the current backend data
                let foundTag = this.state.tags.find(t => t && t['Product Name*'] && t['Product Name*'] === name) || 
                              this.state.originalTags.find(t => t && t['Product Name*'] && t['Product Name*'] === name);
                
                // If not found, try case-insensitive search
                if (!foundTag) {
                    foundTag = this.state.tags.find(t => t && t['Product Name*'] && t['Product Name*'].toLowerCase() === name.toLowerCase()) || 
                              this.state.originalTags.find(t => t && t['Product Name*'] && t['Product Name*'].toLowerCase() === name.toLowerCase());
                }
                
                // If still not found, create a minimal tag object for the selected tag
                if (!foundTag) {
                    verboseLog(`Tag "${name}" not found in state, creating minimal tag object`);
                    foundTag = {
                        'Product Name*': name,
                        'Product Brand': 'Unknown',
                        'Vendor': 'Unknown',
                        'Product Type*': 'Unknown',
                        'Lineage': 'MIXED',
                        'Source': 'Frontend Selection'
                    };
                }
                
                verboseLog(`Looking for tag "${name}":`, foundTag ? 'FOUND' : 'NOT FOUND');
                if (!foundTag) {
                    verboseLog(`  Tag name length: ${name.length}`);
                    verboseLog(`  Tag name characters: ${Array.from(name).map(c => c.charCodeAt(0)).join(', ')}`);
                }
                return foundTag;
            }).filter(Boolean); // Filter out null values from invalid names
            
            verboseLog('selectedTagObjects:', selectedTagObjects);
            verboseLog('selectedTagObjects length:', selectedTagObjects.length);
            
            this.updateSelectedTags(selectedTagObjects);
            
            // FIXED: Don't hide selected tags from available display - keep all items visible
            // This allows users to see all available options even after making selections
            if (isChecked && e.target.closest('#availableTags')) {
                verboseLog('FIXED: Not hiding selected tag from available display - keeping all items visible');
                // Tag remains visible in available list even after selection
            }
            
            // If tag was unchecked in selected list, show it in available display and uncheck it
            if (!isChecked && e.target.closest('#selectedTags') && tag && tag['Product Name*']) {
                // Flag should already be set by mousedown handler, but set it here as backup
                if (!this.state.isProcessingDeselection) {
                    verboseLog('🚫 Backup: Setting isProcessingDeselection flag in handleTagSelection');
                    this.state.isProcessingDeselection = true;
                }
                
                // Robust lookup for the corresponding available tag checkbox
                const originalName = tag['Product Name*'];
                const nonBreakingHyphenName = originalName.replace(/-/g, '\u2011');
                const withoutBySuffix = originalName.replace(/ by [^-]*$/i, '').replace(/ by [^-]+(?= -)/i, '');
                const candidates = [
                    originalName,
                    nonBreakingHyphenName,
                    withoutBySuffix,
                    withoutBySuffix.replace(/-/g, '\u2011')
                ].filter(Boolean);

                let availableTagElement = null;
                for (const candidate of candidates) {
                    availableTagElement = document.querySelector(`#availableTags .tag-checkbox[value="${candidate}"]`);
                    if (availableTagElement) break;
                }
                if (!availableTagElement) {
                    // Fallback: try data-tag-name selector which mirrors the display name
                    for (const candidate of candidates) {
                        const el = document.querySelector(`#availableTags [data-tag-name="${candidate}"] input.tag-checkbox`);
                        if (el) { availableTagElement = el; break; }
                    }
                }
                if (availableTagElement) {
                    const tagElement = availableTagElement.closest('.tag-item');
                    if (tagElement) tagElement.style.display = 'block';
                    // Also uncheck the available tags checkbox
                    // Ensure the tag is removed from persistentSelectedTags (should already be done, but double-check)
                    const idx = this.state.persistentSelectedTags.indexOf(originalName);
                    if (idx > -1) {
                        this.state.persistentSelectedTags.splice(idx, 1);
                    }
                    // Update selectedTags set to match
                    this.state.selectedTags.delete(originalName);
                    // Uncheck the checkbox
                    availableTagElement.checked = false;
                    verboseLog(`✅ Unchecked available tags checkbox for ${originalName}`);
                    
                    // Immediately update hierarchical checkboxes after unchecking
                    // Use requestAnimationFrame to ensure DOM is updated first
                    requestAnimationFrame(() => {
                        this.updateSelectAllCheckboxes();
                    });
                } else {
                    console.warn('⚠️ Could not locate matching available tag checkbox for deselection:', originalName);
                }
                
                // Clear corresponding filters when tag is deselected
                this.clearFiltersForDeselectedTag(tag);
                
                // For JSON matched items and educated guess items, also ensure they appear in available tags
                // This is important for items that might not exist in the original Excel data
                if (tag.Source && (tag.Source === 'JSON Match' || tag.Source.includes('Educated Guess'))) {
                    verboseLog(`${tag.Source.includes('Educated Guess') ? 'Educated guess' : 'JSON matched'} item deselected: ${tag['Product Name*']}`);
                    // Sync with backend to ensure deselection is persisted
                    this.syncDeselectionWithBackend(tag['Product Name*']);
                }
            }
            
            // Update hierarchical checkboxes (vendor, brand, product type, weight) to reflect deselection
            this.updateSelectAllCheckboxes();
            
            // Clear flag after a longer delay to allow any debounced updates to complete
            if (!isChecked && tag && tag['Product Name*']) {
                setTimeout(() => {
                    this.state.isProcessingDeselection = false;
                    verboseLog('✅ Clearing isProcessingDeselection flag after delay');
                }, 3000);
            }
        }, 100); // 100ms debounce delay for individual tag selection
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
            
            // CRITICAL FIX: Debounce backend updates to prevent database lock conflicts when doing many rapid changes
            // This batches rapid changes so they don't all hit the database at once
            this.updateLineageOnBackendDebounced(tagName, newLineage);
        }
    },
    
    // CRITICAL FIX: Debounced wrapper for lineage updates to prevent rapid-fire requests
    _lineageUpdateQueue: {},
    _lineageUpdateTimeouts: {},
    _pendingLineageUpdates: new Set(),
    
    updateLineageOnBackendDebounced(tagName, newLineage) {
        // Cancel any pending update for this tag (only send the latest value)
        if (this._lineageUpdateTimeouts[tagName]) {
            clearTimeout(this._lineageUpdateTimeouts[tagName]);
        }
        
        // Store the latest lineage value for this tag
        this._lineageUpdateQueue[tagName] = newLineage;
        this._pendingLineageUpdates.add(tagName);
        
        // Debounce: wait 500ms before sending request (allows batching rapid changes)
        // This prevents database locks when user changes multiple lineages quickly
        this._lineageUpdateTimeouts[tagName] = setTimeout(() => {
            const finalLineage = this._lineageUpdateQueue[tagName];
            if (finalLineage !== undefined) {
                delete this._lineageUpdateQueue[tagName];
                delete this._lineageUpdateTimeouts[tagName];
                this._pendingLineageUpdates.delete(tagName);
                
                // Send the update
                this.updateLineageOnBackend(tagName, finalLineage);
            }
        }, 500); // 500ms debounce - batches rapid changes
    },

    async updateLineageOnBackend(tagName, newLineage) {
        const requestStartTime = Date.now();
        let timeoutId = null;
        let abortController = null;
        const LINEAGE_UPDATE_TIMEOUT_MS = 45000;
        
        try {
            verboseLog(`🔄 Updating lineage for ${tagName} to ${newLineage}...`);
            
            const payload = {
                tag_name: tagName,
                "Product Name*": tagName,
                lineage: newLineage
            };
            
            // CRITICAL FIX: Add timeout to prevent hanging (increased to 45s to account for database operations)
            abortController = new AbortController();
            timeoutId = setTimeout(() => {
                abortController.abort();
                console.error(`❌ LINEAGE UPDATE TIMEOUT: Request took longer than ${LINEAGE_UPDATE_TIMEOUT_MS / 1000} seconds`);
            }, LINEAGE_UPDATE_TIMEOUT_MS);
            
            const response = await fetch('/api/update-lineage', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
                signal: abortController.signal
            });

            // Clear timeout if request succeeded
            if (timeoutId) {
                clearTimeout(timeoutId);
                timeoutId = null;
            }
            
            const requestDuration = Date.now() - requestStartTime;
            verboseLog(`📡 Response received in ${requestDuration}ms`);
            
            const responseData = await response.json();
            
            if (!response.ok || !responseData.success) {
                const errorMsg = responseData.error || responseData.message || 'Failed to update lineage';
                console.error(`❌ API Error: ${errorMsg}`);
                throw new Error(errorMsg);
            }
            
            // CRITICAL FIX: Only fail if database update actually failed (db_updated === 0)
            // Don't fail just because verification_passed is false - verification might fail even if update succeeded
            if (responseData.db_updated === 0 && responseData.excel_updated === 0) {
                console.error(`❌ LINEAGE UPDATE FAILED: No products updated for '${tagName}'`);
                throw new Error(`Failed to update lineage: ${responseData.message || responseData.error || 'No products were updated'}`);
            }
            
            // Log warning if verification failed but update succeeded
            if (!responseData.verification_passed && responseData.db_updated > 0) {
                console.warn(`⚠️  Lineage update succeeded but verification failed: ${responseData.message || 'Verification check failed'}`);
            }
            
            verboseLog(`✅ Backend confirmed lineage update: ${responseData.message || 'Success'}`);
            verboseLog(`   - DB updated: ${responseData.db_updated || 0} products`);
            verboseLog(`   - Excel updated: ${responseData.excel_updated || 0} products`);
            verboseLog(`   - Verification: ${responseData.verification_passed ? 'PASSED' : 'FAILED'}`);

            // CRITICAL FIX: Use verified lineage from response (may be normalized differently)
            const verifiedLineage = responseData.new_lineage || newLineage;
            
            // Update the tag in original tags as well - update ALL lineage-related fields
            const originalTag = this.state.originalTags.find(t => t['Product Name*'] === tagName);
            if (originalTag) {
                originalTag.lineage = verifiedLineage;
                originalTag.Lineage = verifiedLineage;
                originalTag.currentLineage = verifiedLineage;
                originalTag.canonical_lineage = verifiedLineage;
                verboseLog(`📝 Updated tag in originalTags with verified lineage: ${verifiedLineage}`);
            }

            // Update the tag in current tags list - update ALL lineage-related fields
            const currentTag = this.state.tags.find(t => t['Product Name*'] === tagName);
            if (currentTag) {
                currentTag.lineage = verifiedLineage;
                currentTag.Lineage = verifiedLineage;
                currentTag.currentLineage = verifiedLineage;
                currentTag.canonical_lineage = verifiedLineage;
                verboseLog(`📝 Updated tag in current tags with verified lineage: ${verifiedLineage}`);
            }

            // Optimized: Only update the specific tag elements instead of rebuilding everything
            // Use verified lineage from backend response
            this.updateTagLineageInUI(tagName, verifiedLineage);
            verboseLog(`🎨 Updated UI elements for ${tagName} with verified lineage: ${verifiedLineage}`);
            
            // CRITICAL FIX: Immediately update the tag in originalTags so future renders show correct lineage
            // This ensures that when the tag list is filtered or re-rendered, it shows the updated lineage
            const originalTagIndex = this.state.originalTags.findIndex(t => t['Product Name*'] === tagName);
            if (originalTagIndex >= 0) {
                this.state.originalTags[originalTagIndex].lineage = verifiedLineage;
                this.state.originalTags[originalTagIndex].Lineage = verifiedLineage;
                this.state.originalTags[originalTagIndex].currentLineage = verifiedLineage;
                this.state.originalTags[originalTagIndex].canonical_lineage = verifiedLineage;
                verboseLog(`📝 Updated tag in originalTags with verified lineage: ${verifiedLineage}`);
            }

            // NEW: Instantly update all similar (same vendor + strain) across lists
            // Use verified lineage from backend response
            try {
                this.updateSimilarLineages(tagName, verifiedLineage);
                verboseLog(`✅ Propagated verified lineage '${verifiedLineage}' to similar items (vendor + strain)`);
            } catch (e) {
                console.warn('Failed to update similar lineages locally:', e);
            }
            
            // CRITICAL FIX: Debounce backend refresh to prevent race conditions when multiple updates happen
            // Update originalTags and refresh the UI to show the new lineage
            if (!this._pendingLineageRefresh) {
                this._pendingLineageRefresh = setTimeout(async () => {
                    try {
                        // Only refresh if we haven't had another update in the last 500ms
                        verboseLog('🔄 Debounced backend refresh after lineage update(s)...');
                        const freshTagsResponse = await fetch('/api/available-tags?nocache=1&prefer_db=1&t=' + Date.now());
                        if (freshTagsResponse.ok) {
                            const freshData = await freshTagsResponse.json();
                            verboseLog(`✅ Refreshed ${freshData.tags?.length || 0} tags from backend after lineage update(s)`);
                            
                            // CRITICAL FIX: Update tags in originalTags and current tags to reflect new lineage
                            // This ensures the UI shows the updated lineage values
                            if (freshData.tags && freshData.tags.length > 0) {
                                // Update only the changed tags in originalTags, preserve the rest
                                const updatedTagNames = new Set(this._recentlyUpdatedLineages || []);
                                let updatedCount = 0;
                                
                                freshData.tags.forEach(freshTag => {
                                    const updatedTagName = freshTag['Product Name*'];
                                    if (updatedTagNames.has(updatedTagName)) {
                                        // Update in originalTags
                                        const existingIndex = this.state.originalTags.findIndex(t => t['Product Name*'] === updatedTagName);
                                        if (existingIndex >= 0) {
                                            // Update the existing tag with fresh lineage data
                                            const dbLineage = freshTag.Lineage || freshTag.currentLineage || freshTag.canonical_lineage || freshTag.lineage;
                                            if (dbLineage) {
                                                this.state.originalTags[existingIndex].Lineage = dbLineage;
                                                this.state.originalTags[existingIndex].lineage = dbLineage;
                                                this.state.originalTags[existingIndex].currentLineage = dbLineage;
                                                this.state.originalTags[existingIndex].canonical_lineage = dbLineage;
                                                updatedCount++;
                                            }
                                        }
                                        
                                        // Also update in current tags if visible
                                        const currentIndex = this.state.tags.findIndex(t => t['Product Name*'] === updatedTagName);
                                        if (currentIndex >= 0) {
                                            const dbLineage = freshTag.Lineage || freshTag.currentLineage || freshTag.canonical_lineage || freshTag.lineage;
                                            if (dbLineage) {
                                                this.state.tags[currentIndex].Lineage = dbLineage;
                                                this.state.tags[currentIndex].lineage = dbLineage;
                                                this.state.tags[currentIndex].currentLineage = dbLineage;
                                                this.state.tags[currentIndex].canonical_lineage = dbLineage;
                                            }
                                        }
                                        
                                        // Update UI element for this tag
                                        this.updateTagLineageInUI(updatedTagName, dbLineage || verifiedLineage);
                                    }
                                });
                                
                                verboseLog(`✅ Updated ${updatedCount} tags in originalTags with fresh lineage data (preserved ${this.state.originalTags.length - updatedCount} unchanged tags)`);
                                
                                // CRITICAL FIX: Force UI refresh by re-applying filters to show updated lineage
                                // This ensures the available tags list reflects the new lineage values
                                if (updatedCount > 0 && typeof this.applyFilters === 'function') {
                                    // Re-apply current filters to refresh the UI with updated lineage
                                    try {
                                        this.applyFilters();
                                        verboseLog('✅ Re-applied filters to refresh UI with updated lineage');
                                    } catch (filterError) {
                                        console.warn('Could not re-apply filters:', filterError);
                                    }
                                }
                                
                                // Clear the recently updated list
                                this._recentlyUpdatedLineages = [];
                            }
                        }
                    } catch (refreshError) {
                        console.warn('Could not refresh backend cache:', refreshError);
                    } finally {
                        this._pendingLineageRefresh = null;
                    }
                }, 500); // Debounce for 500ms to batch multiple updates
            }
            
            // Track which tags were recently updated
            if (!this._recentlyUpdatedLineages) {
                this._recentlyUpdatedLineages = [];
            }
            if (!this._recentlyUpdatedLineages.includes(tagName)) {
                this._recentlyUpdatedLineages.push(tagName);
            }

            // CRITICAL FIX: Update selected tags locally without backend fetch
            // This ensures the selected tags dropdowns reflect the current lineage values
            // Use verified lineage from backend response
            if (this.state.selectedTags.has(tagName)) {
                // Find the tag in the selected tags list and update its lineage
                const selectedTagsList = document.querySelectorAll('#selectedTags .tag-item');
                selectedTagsList.forEach(tagElement => {
                    const tagData = tagElement.dataset;
                    if (tagData.productName === tagName) {
                        // Update the lineage in the tag element
                        const lineageSelect = tagElement.querySelector('.lineage-dropdown');
                        if (lineageSelect) {
                            lineageSelect.value = verifiedLineage;
                        }
                        // Also update the tag data object if it exists
                        const tagObj = this.state.tags.find(t => t['Product Name*'] === tagName);
                        if (tagObj) {
                            tagObj.lineage = verifiedLineage;
                            tagObj.Lineage = verifiedLineage;
                            tagObj.currentLineage = verifiedLineage;
                            tagObj.canonical_lineage = verifiedLineage;
                        }
                        verboseLog(`✅ Updated lineage in selected tag UI for ${tagName} to verified lineage: ${verifiedLineage}`);
                    }
                });
            }

            // CRITICAL FIX: Don't refresh available tags - just update the UI directly
            // This prevents the available tags list from being wiped when lineage changes
            verboseLog('✅ Lineage updated successfully - skipping full refresh to preserve available tags');

        } catch (error) {
            // Clear timeout if it's still set
            if (timeoutId) {
                clearTimeout(timeoutId);
                timeoutId = null;
            }
            
            const requestDuration = Date.now() - requestStartTime;
            const isTimeout = error.name === 'AbortError' || error.message.includes('timeout') || requestDuration > 10000;
            
            if (isTimeout) {
                console.error(`❌ LINEAGE UPDATE TIMEOUT after ${requestDuration}ms: ${error.message}`);
                // Show timeout-specific error
                if (window.Toast) {
                    window.Toast.error(`Update timed out after ${(requestDuration/1000).toFixed(1)}s. The update may still be processing. Please refresh the page.`, {
                        duration: 8000,
                        position: 'top-right'
                    });
                } else {
                    alert(`Update timed out. The update may still be processing. Please check the server logs.`);
                }
            } else {
                console.error(`❌ Error updating lineage after ${requestDuration}ms:`, error);
                
                // CRITICAL FIX: Revert local state if update failed (but not for timeout)
                // This prevents showing incorrect lineage in the UI
                try {
                    const originalTag = this.state.originalTags.find(t => t['Product Name*'] === tagName);
                    const currentTag = this.state.tags.find(t => t['Product Name*'] === tagName);
                    
                    // Restore original lineage from backend
                    verboseLog('🔄 Reverting local lineage change after failed update...');
                    
                    // Use a timeout for the revert request too
                    const revertAbortController = new AbortController();
                    const revertTimeout = setTimeout(() => revertAbortController.abort(), 5000);
                    
                    try {
                        const freshTagsResponse = await fetch('/api/available-tags?nocache=1&prefer_db=1&t=' + Date.now(), {
                            signal: revertAbortController.signal
                        });
                        clearTimeout(revertTimeout);
                        
                        if (freshTagsResponse.ok) {
                            const freshData = await freshTagsResponse.json();
                            const freshTag = freshData.tags?.find(t => t['Product Name*'] === tagName);
                            if (freshTag) {
                                const actualLineage = freshTag.Lineage || freshTag.lineage || freshTag.currentLineage || freshTag.canonical_lineage;
                                if (originalTag) {
                                    originalTag.lineage = actualLineage;
                                    originalTag.Lineage = actualLineage;
                                    originalTag.currentLineage = actualLineage;
                                    originalTag.canonical_lineage = actualLineage;
                                }
                                if (currentTag) {
                                    currentTag.lineage = actualLineage;
                                    currentTag.Lineage = actualLineage;
                                    currentTag.currentLineage = actualLineage;
                                    currentTag.canonical_lineage = actualLineage;
                                }
                                // Update UI to show actual lineage
                                this.updateTagLineageInUI(tagName, actualLineage);
                                verboseLog(`✅ Reverted to actual lineage from database: ${actualLineage}`);
                            }
                        }
                    } catch (revertError) {
                        clearTimeout(revertTimeout);
                        if (revertError.name !== 'AbortError') {
                            console.warn('Could not revert lineage after failed update:', revertError);
                        }
                    }
                } catch (revertError) {
                    console.warn('Could not revert lineage after failed update:', revertError);
                }
                
                // Show user-friendly error message
                if (window.Toast) {
                    window.Toast.error(`Failed to update lineage: ${error.message}`, {
                        duration: 5000,
                        position: 'top-right'
                    });
                } else {
                    alert(`Failed to update lineage: ${error.message}`);
                }
            }
        } finally {
            // Ensure timeout is cleared
            if (timeoutId) {
                clearTimeout(timeoutId);
            }
        }
    },

    updateDohInAllDisplays(tagName, newDohStatus) {
        // CRITICAL: Normalize NONE to No for state storage
        const normalizedDoh = newDohStatus === 'NONE' ? 'No' : newDohStatus;
        
        // Update state for both tags and originalTags
        this.state.tags.forEach(tag => {
            if (tag['Product Name*'] === tagName) {
                tag.DOH = normalizedDoh;
                tag.doh = normalizedDoh;
                tag['DOH Compliant (Yes/No)'] = normalizedDoh;
            }
        });
        
        this.state.originalTags.forEach(tag => {
            if (tag['Product Name*'] === tagName) {
                tag.DOH = normalizedDoh;
                tag.doh = normalizedDoh;
                tag['DOH Compliant (Yes/No)'] = normalizedDoh;
            }
        });
        
        // Update available tags display - find by tag name
        const availableItems = document.querySelectorAll('#availableTags .tag-item');
        availableItems.forEach(el => {
            const checkbox = el.querySelector('.tag-checkbox');
            const name = el.getAttribute('data-tag-name') || (checkbox ? checkbox.value : null);
            if (name === tagName) {
                // Update the DOH dropdown
                const dohSelect = el.querySelector('.doh-dropdown');
                if (dohSelect) {
                    dohSelect.value = newDohStatus;
                }
                
                // Update the DOH image
                const imageContainer = el.querySelector('.doh-image-container');
                if (imageContainer) {
                    // Clear existing images
                    while (imageContainer.firstChild) {
                        imageContainer.removeChild(imageContainer.firstChild);
                    }
                    
                    // Add appropriate image based on DOH status
                    if (newDohStatus === 'CBD') {
                        const img = document.createElement('img');
                        img.src = '/static/img/HighCBD.png';
                        img.alt = 'High CBD';
                        img.title = 'High CBD Product';
                        img.style.cssText = 'height:24px;width:auto;margin-left:6px;vertical-align:middle';
                        imageContainer.appendChild(img);
                    } else if (newDohStatus === 'THC') {
                        const img = document.createElement('img');
                        img.src = '/static/img/HighTHC.png';
                        img.alt = 'High THC';
                        img.title = 'High THC Product';
                        img.style.cssText = 'height:24px;width:auto;margin-left:6px;vertical-align:middle';
                        imageContainer.appendChild(img);
                    } else if (newDohStatus === 'DOH') {
                        const img = document.createElement('img');
                        img.src = '/static/img/DOH.png';
                        img.alt = 'DOH Compliant';
                        img.title = 'DOH Compliant Product';
                        img.style.cssText = 'height:21px;width:auto;margin-left:6px;vertical-align:middle';
                        imageContainer.appendChild(img);
                    }
                    // NONE shows no image
                }
            }
        });
        
        // Update selected tags display
        const selectedItems = document.querySelectorAll('#selectedTags .tag-item');
        selectedItems.forEach(el => {
            const checkbox = el.querySelector('.tag-checkbox');
            const name = checkbox ? checkbox.value : el.getAttribute('data-tag-name');
            if (name === tagName) {
                // Update the DOH dropdown
                const dohSelect = el.querySelector('.doh-dropdown');
                if (dohSelect) {
                    dohSelect.value = newDohStatus;
                }
                
                // Update the DOH image
                const imageContainer = el.querySelector('.doh-image-container');
                if (imageContainer) {
                    // Clear existing images
                    while (imageContainer.firstChild) {
                        imageContainer.removeChild(imageContainer.firstChild);
                    }
                    
                    // Add appropriate image based on DOH status
                    if (newDohStatus === 'CBD') {
                        const img = document.createElement('img');
                        img.src = '/static/img/HighCBD.png';
                        img.alt = 'High CBD';
                        img.title = 'High CBD Product';
                        img.style.cssText = 'height:24px;width:auto;margin-left:6px;vertical-align:middle';
                        imageContainer.appendChild(img);
                    } else if (newDohStatus === 'THC') {
                        const img = document.createElement('img');
                        img.src = '/static/img/HighTHC.png';
                        img.alt = 'High THC';
                        img.title = 'High THC Product';
                        img.style.cssText = 'height:24px;width:auto;margin-left:6px;vertical-align:middle';
                        imageContainer.appendChild(img);
                    } else if (newDohStatus === 'DOH') {
                        const img = document.createElement('img');
                        img.src = '/static/img/DOH.png';
                        img.alt = 'DOH Compliant';
                        img.title = 'DOH Compliant Product';
                        img.style.cssText = 'height:21px;width:auto;margin-left:6px;vertical-align:middle';
                        imageContainer.appendChild(img);
                    }
                    // NONE shows no image
                }
            }
        });
        
        verboseLog(`✅ Updated DOH display in all panels for "${tagName}" to "${newDohStatus}"`);
    },

    // Optimized function to update only the specific tag's lineage in the UI
    updateTagLineageInUI(tagName, newLineage) {
        // Helper to safely select an element by data-tag-name, handling quotes and special chars
        const findTagElement = (containerSelector, name) => {
            const safe = (window.CSS && CSS.escape) ? CSS.escape(name) : null;
            if (safe) {
                try {
                    const el = document.querySelector(`${containerSelector} [data-tag-name="${safe}"]`);
                    if (el) return el;
                } catch (e) {
                    // Fall through to manual search
                }
            }
            // Fallback: manual search when name contains quotes or CSS.escape not available
            const candidates = document.querySelectorAll(`${containerSelector} .tag-item`);
            for (const el of candidates) {
                const dataName = el.getAttribute('data-tag-name');
                const checkbox = el.querySelector('.tag-checkbox');
                const cbValue = checkbox ? checkbox.value : null;
                if (dataName === name || cbValue === name) return el;
            }
            return null;
        };

        // Update lineage dropdown in available tags
        const availableTagElement = findTagElement('#availableTags', tagName);
        if (availableTagElement) {
            const lineageSelect = availableTagElement.querySelector('.lineage-dropdown');
            if (lineageSelect) {
                const oldValue = lineageSelect.value;
                lineageSelect.value = newLineage;
                
                // CRITICAL FIX: Trigger change event to ensure any listeners are notified
                if (oldValue !== newLineage) {
                    lineageSelect.dispatchEvent(new Event('change', { bubbles: true }));
                }
                
                // CRITICAL FIX: Also update any lineage display text/span elements
                const lineageDisplay = availableTagElement.querySelector('.lineage-display, .lineage-text, [data-lineage]');
                if (lineageDisplay) {
                    lineageDisplay.textContent = newLineage;
                    if (lineageDisplay.hasAttribute('data-lineage')) {
                        lineageDisplay.setAttribute('data-lineage', newLineage);
                    }
                }
                
                verboseLog(`✅ Updated available tag lineage dropdown for ${tagName} to ${newLineage}`);
            }
        }

        // Update lineage dropdown in selected tags
        const selectedTagElement = findTagElement('#selectedTags', tagName);
        if (selectedTagElement) {
            const lineageSelect = selectedTagElement.querySelector('.lineage-dropdown');
            if (lineageSelect) {
                const oldValue = lineageSelect.value;
                lineageSelect.value = newLineage;
                
                // CRITICAL FIX: Trigger change event to ensure any listeners are notified
                if (oldValue !== newLineage) {
                    lineageSelect.dispatchEvent(new Event('change', { bubbles: true }));
                }
                
                // CRITICAL FIX: Also update any lineage display text/span elements
                const lineageDisplay = selectedTagElement.querySelector('.lineage-display, .lineage-text, [data-lineage]');
                if (lineageDisplay) {
                    lineageDisplay.textContent = newLineage;
                    if (lineageDisplay.hasAttribute('data-lineage')) {
                        lineageDisplay.setAttribute('data-lineage', newLineage);
                    }
                }
                
                verboseLog(`✅ Updated selected tag lineage dropdown for ${tagName} to ${newLineage}`);
            }
        }
    },

    // NEW: Update lineage for all items with the same vendor + strain immediately in UI/state
    updateSimilarLineages(tagName, newLineage) {
        // Find source tag info
        const source = this.state.tags.find(t => (t['Product Name*'] || t.ProductName) === tagName);
        if (!source) {
            console.warn('updateSimilarLineages: Source tag not found for', tagName);
            return;
        }
        const srcVendor = (source['Vendor/Supplier*'] || source['Vendor'] || source.vendor || '').toString().trim().toLowerCase();
        // Prefer explicit strain columns
        // Support multiple possible keys for strain across datasets
        const srcStrain = (
            source['Product Strain'] ||
            source['Strain Names'] ||
            source['ProductStrain'] ||
            source.productStrain ||
            source['Strain'] ||
            source.strain ||
            ''
        ).toString().trim().toLowerCase();
        verboseLog('updateSimilarLineages:', {tagName, vendor: srcVendor, strain: srcStrain});
        if (!srcVendor) {
            console.warn('updateSimilarLineages: No vendor found for', tagName);
            return;
        }

        // Helper to normalize
        const norm = v => (v || '').toString().trim().toLowerCase();
        const isSimilar = (t) => {
            const tagProductName = t['Product Name*'] || t.ProductName || 'UNKNOWN';
            const v = norm(t['Vendor/Supplier*'] || t['Vendor'] || t.vendor);
            
            if (v !== srcVendor) {
                verboseLog(`  ❌ ${tagProductName}: Vendor mismatch (${v} !== ${srcVendor})`);
                return false;
            }
            
            // Strategy: Match by strain if available, otherwise match by product base name
            if (srcStrain) {
                // We have a strain - match by strain
                // Support multiple possible keys for strain across datasets
                const s = norm(
                    t['Product Strain'] ||
                    t['Strain Names'] ||
                    t['ProductStrain'] ||
                    t.productStrain ||
                    t['Strain'] ||
                    t.strain ||
                    ''
                );
                const matches = s === srcStrain;
                
                if (matches) {
                    verboseLog(`  ✅ ${tagProductName}: MATCH by strain (vendor: ${v}, strain: ${s})`);
                } else {
                    verboseLog(`  ❌ ${tagProductName}: Strain mismatch (${s} !== ${srcStrain})`);
                }
                return matches;
            } else {
                // No strain - match by product base name (everything before "by Vendor" or "- Weight")
                const getProductBaseName = (fullName) => {
                    return fullName.split(' by ')[0].split(' - ')[0].trim().toLowerCase();
                };
                const srcBaseName = getProductBaseName(tagName);
                const tagBaseName = getProductBaseName(tagProductName);
                const matches = srcBaseName === tagBaseName;
                
                if (matches) {
                    verboseLog(`  ✅ ${tagProductName}: MATCH by product name (base: ${tagBaseName})`);
                } else {
                    verboseLog(`  ❌ ${tagProductName}: Product name mismatch (${tagBaseName} !== ${srcBaseName})`);
                }
                return matches;
            }
        };

        // Update state.tags and state.originalTags
        let tagsUpdated = 0;
        this.state.tags.forEach(t => {
            if (isSimilar(t)) {
                t.lineage = newLineage;
                t.Lineage = newLineage;
                tagsUpdated++;
            }
        });
        this.state.originalTags.forEach(t => {
            if (isSimilar(t)) {
                t.lineage = newLineage;
                t.Lineage = newLineage;
            }
        });
        verboseLog(`✅ Updated ${tagsUpdated} similar items in state`);

        // Update Available list UI dropdowns
        let availableUpdated = 0;
        const availableItems = document.querySelectorAll('#availableTags .tag-item');
        verboseLog(`🔍 Found ${availableItems.length} available tag items in DOM`);
        availableItems.forEach((el, idx) => {
            // Use same fallback logic as selected tags
            const name = el.getAttribute('data-tag-name') || (el.querySelector('.tag-checkbox')?.value);
            verboseLog(`🔍 Available item ${idx}: data-tag-name="${name}"`);
            const tag = this.state.tags.find(t => (t['Product Name*'] || t.ProductName) === name);
            if (tag && isSimilar(tag)) {
                const select = el.querySelector('.lineage-dropdown');
                if (select) {
                    select.value = newLineage;
                    
                    // Update the data-lineage attribute to change the color
                    el.setAttribute('data-lineage', newLineage.toUpperCase());
                    
                    // Force a style recalculation to apply the new lineage color
                    const originalDisplay = el.style.display;
                    el.style.display = 'none';
                    el.offsetHeight; // Trigger reflow
                    el.style.display = originalDisplay;
                    
                    availableUpdated++;
                    verboseLog(`  ✅ Updated dropdown and color for ${name}`);
                } else {
                    verboseLog(`  ⚠️ No dropdown found for ${name}`);
                }
            } else {
                verboseLog(`  ⚠️ Tag not similar: ${name} (tag found: ${!!tag})`);
            }
        });
        verboseLog(`✅ Updated ${availableUpdated} dropdowns in available tags`);

        // Update Selected list UI dropdowns
        let selectedUpdated = 0;
        const selectedItems = document.querySelectorAll('#selectedTags .tag-item');
        verboseLog(`🔍 Found ${selectedItems.length} selected tag items in DOM`);
        selectedItems.forEach((el, idx) => {
            const name = el.getAttribute('data-tag-name') || (el.querySelector('.tag-checkbox')?.value);
            verboseLog(`🔍 Selected item ${idx}: data-tag-name="${name}"`);
            const tag = this.state.tags.find(t => (t['Product Name*'] || t.ProductName) === name);
            
            if (tag) {
                verboseLog(`  📋 Tag object found for "${name}":`, {
                    vendor: tag['Vendor/Supplier*'] || tag['Vendor'] || tag.vendor,
                    strain: tag['Product Strain'] || tag['Strain Names']
                });
            } else {
                verboseLog(`  ⚠️ Tag object NOT found for "${name}"`);
            }
            
            if (tag && isSimilar(tag)) {
                const select = el.querySelector('.lineage-dropdown');
                if (select) {
                    select.value = newLineage;
                    
                    // Update the data-lineage attribute to change the color
                    el.setAttribute('data-lineage', newLineage.toUpperCase());
                    
                    // Force a style recalculation to apply the new lineage color
                    const originalDisplay = el.style.display;
                    el.style.display = 'none';
                    el.offsetHeight; // Trigger reflow
                    el.style.display = originalDisplay;
                    
                    selectedUpdated++;
                    verboseLog(`  ✅ Updated dropdown and color for ${name}`);
                } else {
                    verboseLog(`  ⚠️ No dropdown found for ${name}`);
                }
            } else {
                verboseLog(`  ⚠️ Tag not similar: ${name} (tag found: ${!!tag})`);
            }
        });
        verboseLog(`✅ Updated ${selectedUpdated} dropdowns in selected tags`);
    },

    updateSelectedTags(tags) {
        // CRITICAL FIX: Always end any existing timer first to prevent "Timer already exists" warning
        // This handles cases where the function is called multiple times rapidly
        try {
            console.timeEnd('updateSelectedTags');
        } catch (e) {
            // Timer doesn't exist, that's fine - continue
        }
        // Now safely start a new timer
        console.time('updateSelectedTags');
        
        if (!tags || !Array.isArray(tags)) {
            console.warn('updateSelectedTags called with invalid tags:', tags);
            tags = [];
        }
        
        // Prevent updates during tag move operations to avoid race conditions
        if (this.isMovingTags) {
            verboseLog('Ignoring updateSelectedTags during tag move operation');
            console.timeEnd('updateSelectedTags');
            return;
        }
        
        // Performance optimization: Check if the update is actually needed
        const container = document.getElementById('selectedTags');
        if (!container) {
            console.error('Selected tags container not found');
            console.timeEnd('updateSelectedTags');
            return;
        }
        
        // CRITICAL: Don't skip update - we need to update dropdowns to show database lineage
        // Even if tag count/names match, lineage values might have changed from database alignment
        // Always re-render to ensure dropdowns show correct database lineage
        const forceUpdate = this._forceSelectedTagsUpdate || false;
        this._forceSelectedTagsUpdate = false; // Reset flag
        
        // Check if the current content matches what we're about to render
        const currentTagCount = container.querySelectorAll('.tag-item').length;
        if (!forceUpdate && currentTagCount === tags.length && tags.length > 0) {
            // Quick check: if we have the same number of tags and they're not empty, 
            // we might not need to update (this is a heuristic to avoid unnecessary updates)
            // BUT: Skip this check if we're forcing update for database lineage
            const currentTagNames = new Set(Array.from(container.querySelectorAll('.tag-item')).map(el => 
                el.querySelector('.tag-checkbox')?.value || el.getAttribute('data-tag-name')
            ).filter(Boolean));
            
            const newTagNames = new Set(tags.map(tag => tag['Product Name*']).filter(Boolean));
            
            // Use Set comparison to handle order differences
            if (currentTagNames.size === newTagNames.size && 
                [...currentTagNames].every(name => newTagNames.has(name))) {
                verboseLog('updateSelectedTags: No changes detected, skipping update');
                console.timeEnd('updateSelectedTags');
                return;
            }
        }
        
        // Dispatch event to notify drag and drop manager that tag updates are starting
        document.dispatchEvent(new CustomEvent('updateSelectedTags'));
        verboseLog('updateSelectedTags called with tags:', tags);

        // Clear existing content
        container.innerHTML = '';

        // For JSON matched items, we want to keep them even if they don't exist in Excel data
        // So we'll be more permissive with validation
        const validTags = [];
        
        // Create a Set for O(1) lookup performance instead of O(n) .some() calls
        const originalTagNames = new Set(this.state.originalTags.map(tag => tag['Product Name*']));
        
        for (const tag of tags) {
            if (tag && tag['Product Name*']) {
                // Check if this tag exists in the original tags (Excel data) - O(1) lookup
                const existsInExcel = originalTagNames.has(tag['Product Name*']);
                
                if (existsInExcel) {
                    validTags.push(tag);
                } else {
                    // For JSON matched items, we'll keep them but mark them as "external"
                    verboseLog(`Tag not found in Excel data (likely JSON matched): ${tag['Product Name*']}`);
                    // Don't add to invalidTags - we'll keep these
                    validTags.push(tag);
                }
            }
        }

        // Update the regular selectedTags set to match persistent ones
        this.state.selectedTags = new Set(this.state.persistentSelectedTags);

        // Use all tags for display (including JSON matched ones)
        // IMPORTANT: For selected tags, we want to preserve the exact order from the backend
        // This is crucial for drag-and-drop reordering to work properly
        tags = validTags;
        
        // NOTE: We do NOT apply filtering to selected tags here
        // Display the selected tags in the same order as the available list for consistency
        // Filtering is only applied to available tags, not selected tags
        verboseLog('Displaying selected tags in available list order (no filtering applied):', tags);
        
        if (tags.length === 0) {
            // Check if we have persistent selected tags that should be displayed
            if (this.state.persistentSelectedTags && this.state.persistentSelectedTags.length > 0) {
                verboseLog('No backend tags but persistent tags exist, rebuilding from persistent state');
                // Rebuild from persistent state - optimized with Maps for O(1) lookup
                const tagsMap = new Map(this.state.tags.map(tag => [tag['Product Name*'], tag]));
                const originalTagsMap = new Map(this.state.originalTags.map(tag => [tag['Product Name*'], tag]));
                
                const persistentTagObjects = this.state.persistentSelectedTags.map(name => {
                    return tagsMap.get(name) || originalTagsMap.get(name);
                }).filter(Boolean);
                
                if (persistentTagObjects.length > 0) {
                    verboseLog('Rebuilding selected tags from persistent state:', persistentTagObjects.length);
                    // Continue with the persistent tags instead of showing empty
                    tags = persistentTagObjects;
                } else {
                    verboseLog('No persistent tags found, showing empty selected tags list');
                    container.innerHTML = `
                    <div class="d-flex align-items-center justify-content-center" style="min-height: 100%;">
                        <div class="text-center p-4" style="max-width: 500px;">
                            <h5 class="text-secondary fw-bold mb-4">Quick Start Guide</h5>
                            
                            <div class="text-start">
                                <div class="mb-4">
                                    <h6 class="text-secondary mb-3">1. Upload Product Data</h6>
                                    <div style="color: #b8b8b8;">
                                        <p class="mb-2 fw-bold fst-italic">📥 Download LOTs Data:</p>
                                        <ol class="ms-3 fst-italic">
                                            <li class="mb-2">Log in to app.posabit.com</li>
                                            <li class="mb-2">Navigate to Inventory → LOTs</li>
                                            <li class="mb-2">Set "Select State" to Active</li>
                                            <li class="mb-2">Click the green Search button</li>
                                            <li class="mb-2">Click the blue Download CSV button</li>
                                            <li class="mb-2">Upload the downloaded file here using the "Upload Data" button</li>
                                        </ol>
                                    </div>
                                </div>

                                <div>
                                    <h6 class="text-secondary mb-3">2. Create Labels</h6>
                                    <ol class="fst-italic ms-3" style="color: #b8b8b8;">
                                        <li class="mb-2">Browse products in the left panel</li>
                                        <li class="mb-2">Check boxes next to products to label</li>
                                        <li class="mb-2">Use filters above to find specific items</li>
                                        <li class="mb-2">Drag and drop to reorder if needed</li>
                                        <li>Click "Generate Labels" when ready</li>
                                    </ol>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                    this.updateTagCount('selected', 0);
                    return;
                }
            } else {
                verboseLog('No backend tags and no persistent tags, showing empty selected tags list');
                container.innerHTML = `
                    <div class="d-flex align-items-center justify-content-center" style="min-height: 100%;">
                        <div class="text-center p-4" style="max-width: 500px;">
                            <h5 class="text-secondary fw-bold mb-3">Quick Start Guide</h5>
                            
                            <div class="text-start">
                                <div class="mb-4">
                                    <h6 class="text-secondary mb-3">1. Upload Product Data</h6>
                                    <div style="color: #b8b8b8;">
                                        <p class="mb-2 fw-bold fst-italic">📥 Download LOTs Data:</p>
                                        <ol class="ms-3 fst-italic">
                                            <li class="mb-2">Log in to app.posabit.com</li>
                                            <li class="mb-2">Navigate to Inventory → LOTs</li>
                                            <li class="mb-2">Set "Select State" to Active</li>
                                            <li class="mb-2">Click the green Search button</li>
                                            <li class="mb-2">Click the blue Download CSV button</li>
                                            <li class="mb-2">Upload the downloaded file here using the "Upload Data" button</li>
                                        </ol>
                                    </div>
                                </div>

                                <div>
                                    <h6 class="text-secondary mb-3">2. Create Labels</h6>
                                    <ol class="fst-italic ms-3" style="color: #b8b8b8;">
                                        <li class="mb-2">Browse products in the left panel</li>
                                        <li class="mb-2">Check boxes next to products to label</li>
                                        <li class="mb-2">Use filters above to find specific items</li>
                                        <li class="mb-2">Drag and drop to reorder if needed</li>
                                        <li>Click "Generate Labels" when ready</li>
                                    </ol>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                this.updateTagCount('selected', 0);
                return;
            }
        }
        
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
            selectAllContainer.className = 'd-flex align-items-center gap-3 mb-2 px-3';
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
                
                // Prevent operation if tags are being moved
                if (this.isMovingTags) {
                    return;
                }
                
                const tagCheckboxes = document.querySelectorAll('#selectedTags .tag-checkbox');
                
                tagCheckboxes.forEach(checkbox => {
                    checkbox.checked = isChecked;
                    const tag = this.state.tags.find(t => t['Product Name*'] === checkbox.value);
                    if (tag) {
                        if (isChecked) {
                            if (!this.state.persistentSelectedTags.includes(tag['Product Name*'])) {
                                this.state.persistentSelectedTags.push(tag['Product Name*']);
                            }
                        } else {
                            const index = this.state.persistentSelectedTags.indexOf(tag['Product Name*']);
                            if (index > -1) {
                                this.state.persistentSelectedTags.splice(index, 1);
                            }
                        }
                    }
                });
                
                // Update the regular selectedTags set to match persistent ones
                this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                
                // Update selected tags display
                // CRITICAL FIX: Use helper function to find ALL selected tags, preserving tags from multiple filters
                const selectedTagObjects = this.getSelectedTagObjects();
                this.updateSelectedTags(selectedTagObjects);
                
                // Efficiently update available tags visibility without full rebuild
                this.efficientlyUpdateAvailableTagsDisplay();
            });
        }

        // Handle new tags being passed in (e.g., from JSON matching)
        // Add new tags to persistentSelectedTags without clearing existing ones
        if (tags.length > 0) {
            verboseLog('Adding new tags to persistentSelectedTags:', tags);
            tags.forEach(tag => {
                if (tag && tag['Product Name*']) {
                    if (!this.state.persistentSelectedTags.includes(tag['Product Name*'])) {
                        this.state.persistentSelectedTags.push(tag['Product Name*']);
                    }
                }
            });
            // Update the regular selectedTags set to match persistent ones
            this.state.selectedTags = new Set(this.state.persistentSelectedTags);
        }

        // Use the tags and display in the same order as the available list for consistency
        let fullTags = tags;
        if (tags && tags.length > 0) {
            verboseLog('Using tags for display (available list order):', tags);
            // Keep selected tags in the same order as the available list for consistency
            fullTags = [...tags];
            // Keep selectedTags set in sync with persistent without reordering
            this.state.selectedTags = new Set(this.state.persistentSelectedTags);
        } else {
            // If no backend tags, show empty selected tags list
            verboseLog('No backend tags, showing empty selected tags list');
            fullTags = [];
            this.state.persistentSelectedTags = [];
            this.state.selectedTags = new Set();
        }
        
        // CRITICAL: Before rendering, normalize all tags to ensure they have database lineage
        // This is essential because selected tags dropdowns must show database lineage, not Excel lineage
        fullTags = fullTags.map(tag => {
            // Normalize lineage fields to ensure database lineage is prioritized
            const normalizedTag = this._normalizeLineageFields({...tag});
            
            // CRITICAL: If tag doesn't have database lineage, try to get it from available tags
            if (!normalizedTag.canonical_lineage && !normalizedTag.currentLineage) {
                const tagName = normalizedTag['Product Name*'];
                const availableTag = this.state.originalTags.find(t => t['Product Name*'] === tagName);
                if (availableTag) {
                    const dbLineage = availableTag.canonical_lineage || availableTag.currentLineage;
                    if (dbLineage) {
                        console.log(`🔄 Getting database lineage for selected tag "${tagName}" from available tags: ${dbLineage}`);
                        normalizedTag.canonical_lineage = dbLineage;
                        normalizedTag.currentLineage = dbLineage;
                        normalizedTag.Lineage = dbLineage;  // Overwrite Excel Lineage with database value
                        normalizedTag.lineage = dbLineage;
                    }
                }
            }
            
            // Debug logging for selected tags with database lineage
            if (normalizedTag.canonical_lineage || normalizedTag.currentLineage) {
                const dbLineage = normalizedTag.canonical_lineage || normalizedTag.currentLineage;
                const excelLineage = normalizedTag.Lineage;
                if (excelLineage && excelLineage.toUpperCase() !== dbLineage.toUpperCase()) {
                    console.log(`✅ Selected tag "${normalizedTag['Product Name*']}": database=${dbLineage}, excel=${excelLineage} → using database`);
                }
            }
            
            return normalizedTag;
        });
        
        // If no tags, just return
        if (!fullTags || fullTags.length === 0) {
            verboseLog('No tags to display in selected tags');
            this.updateTagCount('selected', 0);
            console.timeEnd('updateSelectedTags');
            return;
        }

        // Organize tags into hierarchical groups (SAME HIERARCHY AS AVAILABLE TAGS)
        // This ensures JSON matched tags and all tags use: Vendor > Brand > Product Type > Weight
        const groupedTags = this.organizeBrandCategories(fullTags);
        verboseLog('✅ SELECTED TAGS: Using same hierarchical organization as Current Inventory');
        verboseLog('Grouped selected tags:', groupedTags);

        // Sort vendors alphabetically
        const sortedVendors = Array.from(groupedTags.entries())
            .sort(([a], [b]) => (a || '').localeCompare(b || ''));

        // Create vendor sections
        sortedVendors.forEach(([vendor, brandGroups]) => {
            verboseLog('Processing vendor:', vendor, 'with brand groups:', brandGroups);
            
            const vendorSection = document.createElement('div');
            vendorSection.className = 'vendor-section mb-3';
            
            // Create vendor header with integrated checkbox and collapse functionality
            const vendorHeader = document.createElement('h5');
            vendorHeader.className = 'vendor-header mb-2 d-flex align-items-center collapsible-header';
            vendorHeader.setAttribute('data-collapse-target', 'vendor-' + vendor.replace(/[^a-zA-Z0-9]/g, '_'));
            
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
                                if (!this.state.persistentSelectedTags.includes(tag['Product Name*'])) {
                                    this.state.persistentSelectedTags.push(tag['Product Name*']);
                                }
                            } else {
                                const index = this.state.persistentSelectedTags.indexOf(tag['Product Name*']);
                                if (index > -1) {
                                    this.state.persistentSelectedTags.splice(index, 1);
                                }
                            }
                        }
                    }
                });
                
                // Update the regular selectedTags set to match persistent ones
                this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                
                // Update selected tags display
                // CRITICAL FIX: Use helper function to find ALL selected tags, preserving tags from multiple filters
                const selectedTagObjects = this.getSelectedTagObjects();
                this.updateSelectedTags(selectedTagObjects);
                
                // FIXED: Use efficient update instead of full rebuild to preserve filters and scroll
                // This allows users to see all available options even after making selections
                verboseLog('FIXED: Not filtering out selected tags - keeping all items visible in available list');
                this.efficientlyUpdateAvailableTagsDisplay();
                // Scroll is already preserved since we're not rebuilding the list
            });
            
            // Add collapse/expand icon (will be placed to the right of the vendor name)
            const vendorCollapseIcon = document.createElement('span');
            vendorCollapseIcon.className = 'collapse-icon ms-auto';
            vendorCollapseIcon.textContent = '▼';
            vendorCollapseIcon.style.transition = 'opacity 0.2s ease';

            // Build header: [checkbox] [vendor name (flex-grow)] [collapse icon aligned right]
            vendorHeader.appendChild(vendorCheckbox);
            const vendorNameSpan = document.createElement('span');
            vendorNameSpan.className = 'vendor-title flex-grow-1 text-truncate';
            vendorNameSpan.textContent = vendor;
            vendorHeader.appendChild(vendorNameSpan);
            vendorHeader.appendChild(vendorCollapseIcon);
            
            // Add click handler for collapse/expand
            vendorHeader.addEventListener('click', (e) => {
                if (e.target.classList.contains('select-all-checkbox') || e.target.closest('.select-all-checkbox')) {
                    return; // Don't collapse if clicking checkbox
                }
                const targetSection = vendorSection.querySelector('.collapsible-content');
                const isCollapsed = targetSection.classList.contains('collapsed');
                
                if (isCollapsed) {
                    targetSection.classList.remove('collapsed');
                    vendorCollapseIcon.textContent = '▼';
                } else {
                    targetSection.classList.add('collapsed');
                    vendorCollapseIcon.textContent = '▶';
                }
                
                // Remove the instructional blurb when any chevron is clicked
                this.removeDropdownInstructionBlurb();
            });
            
            vendorSection.appendChild(vendorHeader);

            // Create collapsible content container for vendor
            const vendorContent = document.createElement('div');
            vendorContent.className = 'collapsible-content expanded';
            vendorSection.appendChild(vendorContent);

            // Create brand sections
            const sortedBrands = Array.from(brandGroups.entries())
                .sort(([a], [b]) => (a || '').localeCompare(b || ''));

            sortedBrands.forEach(([brand, productTypeGroups]) => {
                const brandSection = document.createElement('div');
                brandSection.className = 'brand-section ms-3 mb-2';
                
                // Create brand header with integrated checkbox and collapse functionality
                const brandHeader = document.createElement('h6');
                brandHeader.className = 'brand-header mb-2 d-flex align-items-center collapsible-header';
                brandHeader.setAttribute('data-collapse-target', 'brand-' + brand.replace(/[^a-zA-Z0-9]/g, '_'));
                
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
                                    if (!this.state.persistentSelectedTags.includes(tag['Product Name*'])) {
                                        this.state.persistentSelectedTags.push(tag['Product Name*']);
                                    }
                                } else {
                                    const index = this.state.persistentSelectedTags.indexOf(tag['Product Name*']);
                                    if (index > -1) {
                                        this.state.persistentSelectedTags.splice(index, 1);
                                    }
                                }
                            }
                        }
                    });
                    
                    // Update the regular selectedTags set to match persistent ones
                    this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                    
                    // Update selected tags display
                    const selectedTagObjects = Array.from(this.state.persistentSelectedTags).map(name =>
                        this.state.tags.find(t => t['Product Name*'] === name)
                    ).filter(Boolean);
                    
                    this.updateSelectedTags(selectedTagObjects);
                    
                    // Efficiently update available tags visibility without full rebuild
                    this.efficientlyUpdateAvailableTagsDisplay();
                });
                
                // Add collapse/expand icon (to the right of the brand name)
                const brandCollapseIcon = document.createElement('span');
                brandCollapseIcon.className = 'collapse-icon ms-auto';
                brandCollapseIcon.textContent = '▼';
                brandCollapseIcon.style.transition = 'opacity 0.2s ease';

                brandHeader.appendChild(brandCheckbox);
                const brandNameSpan = document.createElement('span');
                brandNameSpan.className = 'brand-title flex-grow-1 text-truncate';
                brandNameSpan.textContent = brand;
                brandHeader.appendChild(brandNameSpan);
                brandHeader.appendChild(brandCollapseIcon);
                
                // Add click handler for collapse/expand
                brandHeader.addEventListener('click', (e) => {
                    if (e.target.classList.contains('select-all-checkbox') || e.target.closest('.select-all-checkbox')) {
                        return; // Don't collapse if clicking checkbox
                    }
                    const targetSection = brandSection.querySelector('.collapsible-content');
                    const isExpanded = targetSection.classList.contains('expanded');
                    
                    if (!isExpanded) {
                        targetSection.classList.add('expanded');
                        targetSection.classList.remove('collapsed');
                        brandCollapseIcon.textContent = '▼';
                    } else {
                        targetSection.classList.remove('expanded');
                        targetSection.classList.add('collapsed');
                        brandCollapseIcon.textContent = '▶';
                    }
                    
                    // Remove the instructional blurb when any chevron is clicked
                    this.removeDropdownInstructionBlurb();
                });
                
                brandSection.appendChild(brandHeader);

                // Create collapsible content container for brand
                const brandContent = document.createElement('div');
                brandContent.className = 'collapsible-content expanded';
                brandSection.appendChild(brandContent);

                // Create product type sections
                const sortedProductTypes = Array.from(productTypeGroups.entries())
                    .sort(([a], [b]) => (a || '').localeCompare(b || ''));

                sortedProductTypes.forEach(([productType, weightGroupsOrSubcategories]) => {
                    const productTypeSection = document.createElement('div');
                    productTypeSection.className = 'product-type-section ms-3 mb-2';
                    
                    // Check if this product type has subcategories (vape products with 510/Disposable)
                    const hasSubcategories = weightGroupsOrSubcategories instanceof Map && 
                                           weightGroupsOrSubcategories.size > 0 &&
                                           Array.from(weightGroupsOrSubcategories.values())[0] instanceof Map;
                    
                    // Create product type header with integrated checkbox and collapse functionality
                    const typeHeader = document.createElement('div');
                    typeHeader.className = 'product-type-header mb-2 d-flex align-items-center collapsible-header';
                    typeHeader.setAttribute('data-collapse-target', 'type-' + productType.replace(/[^a-zA-Z0-9]/g, '_'));
                    
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
                                        if (!this.state.persistentSelectedTags.includes(tag['Product Name*'])) {
                                            this.state.persistentSelectedTags.push(tag['Product Name*']);
                                        }
                                    } else {
                                        const index = this.state.persistentSelectedTags.indexOf(tag['Product Name*']);
                                        if (index > -1) {
                                            this.state.persistentSelectedTags.splice(index, 1);
                                        }
                                    }
                                }
                            }
                        });
                        
                        // Update the regular selectedTags set to match persistent ones
                        this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                        
                        // Update selected tags display
                        const selectedTagObjects = Array.from(this.state.persistentSelectedTags).map(name =>
                            this.state.tags.find(t => t['Product Name*'] === name)
                        ).filter(Boolean);
                        
                        this.updateSelectedTags(selectedTagObjects);
                        
                        // Efficiently update available tags visibility without full rebuild
                        this.efficientlyUpdateAvailableTagsDisplay();
                    });
                    
                    // Add collapse/expand icon (to the right of the product type)
                    const typeCollapseIcon = document.createElement('span');
                    typeCollapseIcon.className = 'collapse-icon ms-auto';
                    typeCollapseIcon.textContent = '▼';
                    typeCollapseIcon.style.transition = 'opacity 0.2s ease';

                    typeHeader.appendChild(productTypeCheckbox);
                    const typeNameSpan = document.createElement('span');
                    typeNameSpan.className = 'type-title flex-grow-1 text-truncate';
                    typeNameSpan.textContent = productType;
                    typeHeader.appendChild(typeNameSpan);
                    typeHeader.appendChild(typeCollapseIcon);
                    
                    // Add click handler for collapse/expand
                    typeHeader.addEventListener('click', (e) => {
                        if (e.target.classList.contains('select-all-checkbox') || e.target.closest('.select-all-checkbox')) {
                            return; // Don't collapse if clicking checkbox
                        }
                        const targetSection = productTypeSection.querySelector('.collapsible-content');
                        const isCollapsed = targetSection.classList.contains('collapsed');
                        
                        if (isCollapsed) {
                            targetSection.classList.remove('collapsed');
                            typeCollapseIcon.textContent = '▼';
                        } else {
                            targetSection.classList.add('collapsed');
                            typeCollapseIcon.textContent = '▶';
                        }
                        
                        // Remove the instructional blurb when any chevron is clicked
                        this.removeDropdownInstructionBlurb();
                    });
                    
                    productTypeSection.appendChild(typeHeader);

                    // Create collapsible content container for product type
                    const productTypeContent = document.createElement('div');
                    productTypeContent.className = 'collapsible-content';
                    productTypeSection.appendChild(productTypeContent);

                    if (hasSubcategories) {
                        // Render subcategories (510, Disposable, etc.)
                        const sortedSubcategories = Array.from(weightGroupsOrSubcategories.entries())
                            .sort(([a], [b]) => (a || '').localeCompare(b || ''));

                        sortedSubcategories.forEach(([subcategory, weightGroups]) => {
                            const subcategorySection = document.createElement('div');
                            subcategorySection.className = 'subcategory-section ms-3 mb-2';
                            
                            // Create subcategory header with checkbox
                            const subcategoryHeader = document.createElement('div');
                            subcategoryHeader.className = 'subcategory-header mb-2 d-flex align-items-center collapsible-header';
                            
                            const subcategoryCheckbox = document.createElement('input');
                            subcategoryCheckbox.type = 'checkbox';
                            subcategoryCheckbox.className = 'select-all-checkbox me-2';
                            subcategoryCheckbox.addEventListener('change', (e) => {
                                const isChecked = e.target.checked;
                                const checkboxes = subcategorySection.querySelectorAll('input.tag-checkbox');
                                checkboxes.forEach(checkbox => {
                                    checkbox.checked = isChecked;
                                    const tagName = checkbox.value;
                                    const tag = this.state.tags.find(t => t['Product Name*'] === tagName);
                                    if (tag) {
                                        if (isChecked) {
                                            if (!this.state.persistentSelectedTags.includes(tagName)) {
                                                this.state.persistentSelectedTags.push(tagName);
                                            }
                                        } else {
                                            const index = this.state.persistentSelectedTags.indexOf(tagName);
                                            if (index > -1) {
                                                this.state.persistentSelectedTags.splice(index, 1);
                                            }
                                        }
                                    }
                                });
                                this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                                const selectedTagObjects = Array.from(this.state.persistentSelectedTags).map(name =>
                                    this.state.tags.find(t => t['Product Name*'] === name)
                                ).filter(Boolean);
                                this.updateSelectedTags(selectedTagObjects);
                                this.efficientlyUpdateAvailableTagsDisplay();
                            });
                            
                            subcategoryHeader.appendChild(subcategoryCheckbox);
                            const subcategoryNameSpan = document.createElement('span');
                            subcategoryNameSpan.className = 'subcategory-title flex-grow-1 text-truncate';
                            subcategoryNameSpan.textContent = subcategory;
                            subcategoryHeader.appendChild(subcategoryNameSpan);
                            subcategorySection.appendChild(subcategoryHeader);

                            // Create weight sections
                            const sortedWeights = Array.from(weightGroups.entries())
                                .sort(([a], [b]) => (a || '').toString().localeCompare((b || '').toString()));

                    sortedWeights.forEach(([weight, tags]) => {
                        const weightSection = document.createElement('div');
                        weightSection.className = 'weight-section ms-3 mb-1';
                        
                        // Create weight header with integrated checkbox and collapse functionality
                        const weightHeader = document.createElement('div');
                        weightHeader.className = 'weight-header mb-1 d-flex align-items-center collapsible-header';
                        weightHeader.setAttribute('data-collapse-target', 'weight-' + weight.replace(/[^a-zA-Z0-9]/g, '_'));
                        
                        const weightCheckbox = document.createElement('input');
                        weightCheckbox.type = 'checkbox';
                        weightCheckbox.className = 'select-all-checkbox me-2';
                        weightCheckbox.addEventListener('change', (e) => {
                            const savedScroll = this._saveAvailableScrollPosition();
                            const isChecked = e.target.checked;
                            // Only iterate tag checkboxes for performance
                            const checkboxes = weightSection.querySelectorAll('input.tag-checkbox');
                            
                            checkboxes.forEach(checkbox => {
                                checkbox.checked = isChecked;
                                // Only update persistentSelectedTags for tag-checkboxes
                                if (checkbox.classList.contains('tag-checkbox')) {
                                    const tag = this.state.tags.find(t => t['Product Name*'] === checkbox.value);
                                    if (tag) {
                                        if (isChecked) {
                                            if (!this.state.persistentSelectedTags.includes(tag['Product Name*'])) {
                                                this.state.persistentSelectedTags.push(tag['Product Name*']);
                                            }
                                        } else {
                                            const index = this.state.persistentSelectedTags.indexOf(tag['Product Name*']);
                                            if (index > -1) {
                                                this.state.persistentSelectedTags.splice(index, 1);
                                            }
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
                            // Restore scroll after all DOM updates complete
                            requestAnimationFrame(() => {
                                this._restoreAvailableScrollPosition(savedScroll);
                            });
                        });
                        
                        // Add collapse/expand icon (to the right of the weight)
                        const weightCollapseIcon = document.createElement('span');
                        weightCollapseIcon.className = 'collapse-icon ms-auto';
                        weightCollapseIcon.textContent = '▼';
                        weightCollapseIcon.style.transition = 'opacity 0.2s ease';

                        weightHeader.appendChild(weightCheckbox);
                        const weightNameSpan = document.createElement('span');
                        weightNameSpan.className = 'weight-title flex-grow-1 text-truncate';
                        weightNameSpan.textContent = weight;
                        weightHeader.appendChild(weightNameSpan);
                        weightHeader.appendChild(weightCollapseIcon);
                        
                        // Add click handler for collapse/expand
                        weightHeader.addEventListener('click', (e) => {
                            if (e.target.classList.contains('select-all-checkbox') || e.target.closest('.select-all-checkbox')) {
                                return; // Don't collapse if clicking checkbox
                            }
                            const targetSection = weightSection.querySelector('.collapsible-content');
                            const isCollapsed = targetSection.classList.contains('collapsed');
                            
                            if (isCollapsed) {
                                targetSection.classList.remove('collapsed');
                                weightCollapseIcon.textContent = '▼';
                            } else {
                                weightSection.classList.add('collapsed');
                                weightCollapseIcon.textContent = '▶';
                            }
                            
                            // Remove the instructional blurb when any chevron is clicked
                            this.removeDropdownInstructionBlurb();
                        });
                        
                        weightSection.appendChild(weightHeader);
                        
                        // Create collapsible content container for weight
                        const weightContent = document.createElement('div');
                        weightContent.className = 'collapsible-content';
                        weightSection.appendChild(weightContent);
                        
                        // Always render tags as leaf nodes - sort alphabetically by product name
                        if (tags && tags.length > 0) {
                            // Sort tags alphabetically by product name
                            const orderedTags = [...tags].sort((a, b) => {
                                const nameA = (a['Product Name*'] || '').toLowerCase();
                                const nameB = (b['Product Name*'] || '').toLowerCase();
                                return nameA.localeCompare(nameB);
                            });
                            
                            orderedTags.forEach(tag => {
                                // CRITICAL: Before creating tag element, ensure tag has database lineage
                                // If database lineage is missing, try to get it from available tags
                                if (!tag.canonical_lineage && !tag.currentLineage) {
                                    const tagName = tag['Product Name*'];
                                    const availableTag = this.state.originalTags.find(t => t['Product Name*'] === tagName);
                                    if (availableTag) {
                                        const dbLineage = availableTag.canonical_lineage || availableTag.currentLineage;
                                        if (dbLineage) {
                                            console.log(`🔄 Selected tag "${tagName}" missing database lineage, using from available tags: ${dbLineage}`);
                                            tag.canonical_lineage = dbLineage;
                                            tag.currentLineage = dbLineage;
                                            tag.Lineage = dbLineage;
                                            tag.lineage = dbLineage;
                                        }
                                    }
                                }
                                
                                // Debug: Log lineage values before rendering
                                const dbLineage = tag.canonical_lineage || tag.currentLineage;
                                const excelLineage = tag.Lineage;
                                if (dbLineage && excelLineage && dbLineage.toUpperCase() !== excelLineage.toUpperCase()) {
                                    console.log(`🎯 Rendering selected tag "${tag['Product Name*']}": db=${dbLineage}, excel=${excelLineage} → dropdown should show ${dbLineage}`);
                                }
                                
                                const tagElement = this.createTagElement(tag, true); // true = isForSelectedTags
                                const checkbox = tagElement.querySelector('.tag-checkbox');
                                const shouldBeChecked = this.state.persistentSelectedTags.includes(tag['Product Name*']);
                                checkbox.checked = shouldBeChecked;
                                verboseLog(`Setting checkbox for "${tag['Product Name*']}" to checked: ${shouldBeChecked}`);
                                
                                // Ensure the checkbox is properly initialized
                                if (shouldBeChecked) {
                                    checkbox.setAttribute('data-checked', 'true');
                                } else {
                                    checkbox.removeAttribute('data-checked');
                                }
                                
                                // Add a small delay to ensure the checkbox is properly rendered
                                setTimeout(() => {
                                    // Double-check the checkbox state
                                    if (shouldBeChecked && !checkbox.checked) {
                                        verboseLog(`Fixing checkbox state for "${tag['Product Name*']}" - should be checked but isn't`);
                                        checkbox.checked = true;
                                    } else if (!shouldBeChecked && checkbox.checked) {
                                        verboseLog(`Fixing checkbox state for "${tag['Product Name*']}" - should not be checked but is`);
                                        checkbox.checked = false;
                                    }
                                }, 10);
                                
                                weightContent.appendChild(tagElement);
                            });
                        }
                        
                        subcategorySection.appendChild(weightSection);
                    });
                    
                            productTypeContent.appendChild(subcategorySection);
                        });
                    } else {
                        // No subcategories - render weights directly
                        const sortedWeights = Array.from(weightGroupsOrSubcategories.entries())
                            .sort(([a], [b]) => (a || '').toString().localeCompare((b || '').toString()));

                        sortedWeights.forEach(([weight, tags]) => {
                            const weightSection = document.createElement('div');
                            weightSection.className = 'weight-section ms-3 mb-1';
                            
                            // Create weight header with integrated checkbox and collapse functionality
                            const weightHeader = document.createElement('div');
                            weightHeader.className = 'weight-header mb-1 d-flex align-items-center collapsible-header';
                            weightHeader.setAttribute('data-collapse-target', 'weight-' + weight.replace(/[^a-zA-Z0-9]/g, '_'));
                            
                            const weightCheckbox = document.createElement('input');
                            weightCheckbox.type = 'checkbox';
                            weightCheckbox.className = 'select-all-checkbox me-2';
                            weightCheckbox.addEventListener('change', (e) => {
                                const savedScroll = this._saveAvailableScrollPosition();
                                const isChecked = e.target.checked;
                                // Only iterate tag checkboxes for performance
                                const checkboxes = weightSection.querySelectorAll('input.tag-checkbox');
                                
                                checkboxes.forEach(checkbox => {
                                    checkbox.checked = isChecked;
                                    // Only update persistentSelectedTags for tag-checkboxes
                                    if (checkbox.classList.contains('tag-checkbox')) {
                                        const tag = this.state.tags.find(t => t['Product Name*'] === checkbox.value);
                                        if (tag) {
                                            if (isChecked) {
                                                if (!this.state.persistentSelectedTags.includes(tag['Product Name*'])) {
                                                    this.state.persistentSelectedTags.push(tag['Product Name*']);
                                                }
                                            } else {
                                                const index = this.state.persistentSelectedTags.indexOf(tag['Product Name*']);
                                                if (index > -1) {
                                                    this.state.persistentSelectedTags.splice(index, 1);
                                                }
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
                                // Restore scroll after all DOM updates complete
                                requestAnimationFrame(() => {
                                    this._restoreAvailableScrollPosition(savedScroll);
                                });
                            });
                            
                            // Add collapse/expand icon (to the right of the weight)
                            const weightCollapseIcon = document.createElement('span');
                            weightCollapseIcon.className = 'collapse-icon ms-auto';
                            weightCollapseIcon.textContent = '▼';
                            weightCollapseIcon.style.transition = 'opacity 0.2s ease';

                            weightHeader.appendChild(weightCheckbox);
                            const weightNameSpan = document.createElement('span');
                            weightNameSpan.className = 'weight-title flex-grow-1 text-truncate';
                            weightNameSpan.textContent = weight;
                            weightHeader.appendChild(weightNameSpan);
                            weightHeader.appendChild(weightCollapseIcon);
                            
                            // Add click handler for collapse/expand
                            weightHeader.addEventListener('click', (e) => {
                                if (e.target.classList.contains('select-all-checkbox') || e.target.closest('.select-all-checkbox')) {
                                    return; // Don't collapse if clicking checkbox
                                }
                                const targetSection = weightSection.querySelector('.collapsible-content');
                                const isCollapsed = targetSection.classList.contains('collapsed');
                                
                                if (isCollapsed) {
                                    targetSection.classList.remove('collapsed');
                                    weightCollapseIcon.textContent = '▼';
                                } else {
                                    weightSection.classList.add('collapsed');
                                    weightCollapseIcon.textContent = '▶';
                                }
                                
                                // Remove the instructional blurb when any chevron is clicked
                                this.removeDropdownInstructionBlurb();
                            });
                            
                            weightSection.appendChild(weightHeader);
                            
                            // Create collapsible content container for weight
                            const weightContent = document.createElement('div');
                            weightContent.className = 'collapsible-content';
                            weightSection.appendChild(weightContent);
                            
                            // Always render tags as leaf nodes - sort alphabetically by product name
                            if (tags && tags.length > 0) {
                                // Sort tags alphabetically by product name
                                const orderedTags = [...tags].sort((a, b) => {
                                    const nameA = (a['Product Name*'] || '').toLowerCase();
                                    const nameB = (b['Product Name*'] || '').toLowerCase();
                                    return nameA.localeCompare(nameB);
                                });
                                
                                orderedTags.forEach(tag => {
                                    const tagElement = this.createTagElement(tag, true); // true = isForSelectedTags
                                    const checkbox = tagElement.querySelector('.tag-checkbox');
                                    const shouldBeChecked = this.state.persistentSelectedTags.includes(tag['Product Name*']);
                                    checkbox.checked = shouldBeChecked;
                                    verboseLog(`Setting checkbox for "${tag['Product Name*']}" to checked: ${shouldBeChecked}`);
                                    
                                    // Ensure the checkbox is properly initialized
                                    if (shouldBeChecked) {
                                        checkbox.setAttribute('data-checked', 'true');
                                    } else {
                                        checkbox.removeAttribute('data-checked');
                                    }
                                    
                                    // Add a small delay to ensure the checkbox is properly rendered
                                    setTimeout(() => {
                                        // Double-check the checkbox state
                                        if (shouldBeChecked && !checkbox.checked) {
                                            verboseLog(`Fixing checkbox state for "${tag['Product Name*']}" - should be checked but isn't`);
                                            checkbox.checked = true;
                                        } else if (!shouldBeChecked && checkbox.checked) {
                                            verboseLog(`Fixing checkbox state for "${tag['Product Name*']}" - should not be checked but is`);
                                            checkbox.checked = false;
                                        }
                                    }, 10);
                                    
                                    weightContent.appendChild(tagElement);
                                });
                            }
                            
                            productTypeContent.appendChild(weightSection);
                        });
                    }
                    
                    brandContent.appendChild(productTypeSection);
                });
                
                vendorContent.appendChild(brandSection);
            });
            
            
            container.appendChild(vendorSection);
        });

        this.updateTagCount('selected', fullTags.length);
        console.timeEnd('updateSelectedTags');

        // Attach delegated change handler once (idempotent)
        if (!container._hasDeselectionHandler) {
            // Only respond to actual checkbox changes; do not toggle on row clicks
            container.addEventListener('change', (e) => {
                const target = e.target;
                if (!target || !target.matches('input[type="checkbox"].tag-checkbox')) return;
                const tagName = target.value;
                if (target.checked) {
                    // For checks, update state immediately to improve responsiveness
                    const idx = this.state.persistentSelectedTags.indexOf(tagName);
                    if (idx === -1) {
                        this.state.persistentSelectedTags.push(tagName);
                        this.state.selectedTags.add(tagName);
                    }
                    return;
                }
                // For unchecks, don't remove the row - let individual handlers handle it
                // This ensures the individual handlers can run properly
            }, { capture: true });
            Object.defineProperty(container, '_hasDeselectionHandler', { value: true, enumerable: false });
        }

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
        container.querySelectorAll('.vendor-section, .brand-section, .product-type-section, .subcategory-section, .weight-section').forEach(section => {
            updateSelectAllCheckboxState(section);
        });
        // Update the top-level select all
        updateSelectAllCheckboxState(container);
        // Update select all checkbox states
        this.updateSelectAllCheckboxes();
        
        // Dispatch event to notify drag and drop manager that tag updates are complete
        document.dispatchEvent(new CustomEvent('updateSelectedTagsComplete'));
        
        // Also directly reinitialize drag and drop to ensure it's working
        if (window.dragAndDropManager) {
            setTimeout(() => {
                verboseLog('Reinitializing drag and drop after updateSelectedTags');
                window.dragAndDropManager.reinitializeTagDragAndDrop();
            }, 100);
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
                    if (!TagManager.state.persistentSelectedTags.includes(this.value)) {
                    TagManager.state.persistentSelectedTags.push(this.value);
                };
                } else {
                    const index = TagManager.state.persistentSelectedTags.indexOf(this.value);
                if (index > -1) {
                    TagManager.state.persistentSelectedTags.splice(index, 1);
                };
                }
                // Update the regular selectedTags set to match persistent ones
                TagManager.state.selectedTags = new Set(TagManager.state.persistentSelectedTags);
                TagManager.updateTagCheckboxes();
            });
        });

        // No full list refresh to preserve scroll/selection
    },

    // Bulk update DOH for selected (or currently visible if none selected)
    async bulkUpdateDohForSelected(newDohStatus) {
        const normalizedDoh = newDohStatus === 'NONE' ? 'No' : newDohStatus;
        // Prefer persistent selected tags; if none, operate on currently visible available tags
        let targets = [...(this.state.persistentSelectedTags || [])];
        if (targets.length === 0) {
            const visible = Array.from(document.querySelectorAll('#availableTags .tag-item'))
                .map(el => el.getAttribute('data-tag-name') || (el.querySelector('.tag-checkbox')?.value))
                .filter(Boolean);
            targets = visible;
        }
        if (!targets || targets.length === 0) return;
        verboseLog(`🔧 Bulk DOH update for ${targets.length} item(s) -> ${normalizedDoh}`);

        // Process with small concurrency to avoid overloading the backend
        const concurrency = 4;
        let index = 0;
        const worker = async () => {
            while (index < targets.length) {
                const name = targets[index++];
                try {
                    const resp = await fetch('/api/update-doh', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ product_name: name, doh_status: newDohStatus })
                    });
                    if (!resp.ok) {
                        const err = await resp.json().catch(() => ({}));
                        throw new Error(err.error || `HTTP ${resp.status}`);
                    }
                    // Reflect in local state/UI
                    this.updateDohInAllDisplays(name, newDohStatus);
                    // Update in-memory objects directly
                    this.state.tags.forEach(t => {
                        if (t['Product Name*'] === name) {
                            t.DOH = normalizedDoh; t.doh = normalizedDoh; t['DOH Compliant (Yes/No)'] = normalizedDoh;
                        }
                    });
                    this.state.originalTags.forEach(t => {
                        if (t['Product Name*'] === name) {
                            t.DOH = normalizedDoh; t.doh = normalizedDoh; t['DOH Compliant (Yes/No)'] = normalizedDoh;
                        }
                    });
                } catch (e) {
                    console.warn(`DOH bulk update failed for ${name}:`, e.message);
                }
            }
        };
        const workers = Array.from({ length: Math.min(concurrency, targets.length) }, () => worker());
        await Promise.all(workers);
        verboseLog('✅ Bulk DOH update complete');
    },

    updateTagCheckboxes() {
        verboseLog('updateTagCheckboxes called');
        // Update available tags checkboxes
        document.querySelectorAll('#availableTags input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = TagManager.state.persistentSelectedTags.includes(checkbox.value);
            
            // Ensure checkbox is properly enabled
            checkbox.style.pointerEvents = 'auto';
            checkbox.removeAttribute('data-drag-disabled');
            checkbox.removeAttribute('data-reordering');
        });
        
        // Update selected tags checkboxes
        document.querySelectorAll('#selectedTags input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = TagManager.state.persistentSelectedTags.includes(checkbox.value);
            
            // Ensure checkbox is properly enabled
            checkbox.style.pointerEvents = 'auto';
            checkbox.removeAttribute('data-drag-disabled');
            checkbox.removeAttribute('data-reordering');
        });
        
        // Also ensure tag items are properly enabled
        document.querySelectorAll('.tag-item').forEach(tagItem => {
            tagItem.style.pointerEvents = 'auto';
            tagItem.removeAttribute('data-drag-disabled');
            tagItem.removeAttribute('data-reordering');
        });
        
        verboseLog('All checkboxes and tag items updated and enabled');
    },

    async fetchAndUpdateAvailableTags() {
        try {
            console.log('=== fetchAndUpdateAvailableTags START ===');
            const hydratedFromCache = this.hydrateAvailableTagsFromCache();
            if (hydratedFromCache) {
                console.log('✅ Tags rendered instantly from cache - skipping loader');
                // Cache hydration already handled rendering, skip loader
                return true;
            }
            
            // Only show loading if we don't have cached tags
            console.log('⏳ No cache available - showing loader');
            this.showActionSplash('Loading tags...');
            
            // Show loading indicator in container IMMEDIATELY to prevent blank screen
            const availableTagsContainer = document.getElementById('availableTags');
            if (availableTagsContainer) {
                availableTagsContainer.innerHTML = `
                    <div class="text-center py-4">
                        <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-2 text-white">Loading tags...</p>
                    </div>
                `;
            }
            
            // Preserve current scroll/anchor so refreshes don't jump the list
            const savedScroll = this._saveAvailableScrollPosition();
            
            // Rate limiting: prevent rapid successive calls
            // Reduced from 2000ms to 500ms to allow faster retries while still preventing abuse
            const now = Date.now();
            if (this._lastFetchTime && (now - this._lastFetchTime) < 500) {
                verboseLog('Rate limiting: skipping fetch (too soon after last fetch)');
                // Hide splash if we're skipping
                if (this.hideActionSplash) {
                    this.hideActionSplash();
                }
                return false;
            }
            this._lastFetchTime = now;
            
            // Check if we're in JSON matching mode and have JSON matched tags
            const hasJsonMatchedTags = this.state.persistentSelectedTags && this.state.persistentSelectedTags.length > 0;
            const hasJsonMatchedData = this.state.tags && this.state.tags.length > 0 && 
                this.state.tags.some(tag => tag.Source === 'JSON Match' || (tag.Source && tag.Source.includes('Educated Guess')));
            
            // Additional checks for JSON matched data
            const hasJsonMatchedInOriginal = this.state.originalTags && this.state.originalTags.length > 0 && 
                this.state.originalTags.some(tag => tag.Source === 'JSON Match' || (tag.Source && tag.Source.includes('Educated Guess')));
            
            // Check if we have any tags with JSON Match source
                    const jsonMatchedCount = this.state.tags ? this.state.tags.filter(tag => tag.Source === 'JSON Match' || (tag.Source && tag.Source.includes('Educated Guess'))).length : 0;
        const originalJsonMatchedCount = this.state.originalTags ? this.state.originalTags.filter(tag => tag.Source === 'JSON Match' || (tag.Source && tag.Source.includes('Educated Guess'))).length : 0;
            
            verboseLog('JSON matching detection:', {
                hasJsonMatchedTags,
                hasJsonMatchedData,
                hasJsonMatchedInOriginal,
                jsonMatchedCount,
                originalJsonMatchedCount,
                tagsLength: this.state.tags ? this.state.tags.length : 0,
                originalTagsLength: this.state.originalTags ? this.state.originalTags.length : 0
            });
            
            // Only skip if we have actual JSON matched data, not just persistent tags
            if (hasJsonMatchedData || hasJsonMatchedInOriginal || jsonMatchedCount > 0) {
                verboseLog('JSON matched data detected: preserving selections but still fetching fresh tags to align lineage');
                // Realign any currently-rendered items before fetch
                if (Array.isArray(this.state.tags) && this.state.tags.length > 0) {
                    try { this.alignDisplayedLineagesWithTags(); } catch (e) { /* noop */ }
                }
                // DO NOT return; continue to fetch to pull DB-aligned lineage for regular tags
            }
            
            verboseLog('Fetching available tags...');
            const timestamp = Date.now();
            
            // OPTIMIZATION: Use fast_load parameter for initial load OR post-upload to skip slow lineage alignment
            // This dramatically speeds up tag loading when cached data is available
            const isInitialLoad = !this.state.tags || this.state.tags.length === 0;
            // Also use fast_load after uploads (when called from refreshTagLists with force=true)
            const isPostUpload = this._isPostUploadLoad || false;
            const fastLoadParam = (isInitialLoad || isPostUpload) ? '&fast_load=1' : '';
            
            // Add retry logic for failed requests
            let response;
            let responseData;
            const maxRetries = 3;
            let retryCount = 0;
            let lastError;
            
            while (retryCount < maxRetries) {
                try {
                    const controller = new AbortController();
                    // PERFORMANCE FIX: Reduced timeout to 8s - fast_load should make this fast enough
                    const timeoutId = setTimeout(() => controller.abort(), 8000);

                    // CRITICAL FIX: Use prefer_db to ensure lineage values come from database
                    // Always use prefer_db=1 to force database lineage alignment, even on cached tags
                    // This ensures UI shows current database lineage values, including previously updated ones
                    // CRITICAL: After Excel upload, always use nocache to force database lineage
                    // This ensures UI shows database lineage, not Excel lineage from cache
                    const forceDbLineage = this._forceDatabaseLineage || false;
                    const useCache = retryCount === 0 && !forceDbLineage; // Don't use cache after upload
                    const cacheParam = useCache ? '' : '&nocache=1';
                    const preferDbParam = '&prefer_db=1';  // CRITICAL: Always use database for lineage accuracy
                    // Note: prefer_db=1 forces lineage alignment even on cached tags, so lineage will be fresh
                    // Use fast_load on first attempt for initial loads (lineage alignment still happens with prefer_db)
                    const fastLoadParam = '&fast_load=1';
                    const fastParam = (retryCount === 0 && (isInitialLoad || isPostUpload)) ? fastLoadParam : fastLoadParam;
                    response = await fetch(`/api/available-tags?t=${timestamp}${cacheParam}${fastParam}${preferDbParam}`, {
                        signal: controller.signal
                    });
                    clearTimeout(timeoutId);

                    verboseLog(`Available tags response status (attempt ${retryCount + 1}/${maxRetries}):`, response.status);

                    if (!response.ok) {
                        if (response.status >= 500 && retryCount < maxRetries - 1) {
                            // Server error - retry
                            retryCount++;
                            const delay = Math.min(1000 * retryCount, 3000); // Exponential backoff, max 3s
                            verboseLog(`Server error ${response.status}, retrying in ${delay}ms...`);
                            await new Promise(resolve => setTimeout(resolve, delay));
                            continue;
                        }
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const responseText = await response.text();
                    try {
                        responseData = responseText ? JSON.parse(responseText) : null;
                    } catch (parseError) {
                        console.error('Failed to parse available tags JSON response:', {
                            parseError,
                            snippet: responseText ? responseText.slice(0, 500) : ''
                        });
                        throw parseError;
                    }
                    break; // Success - exit retry loop
                    
                } catch (error) {
                    lastError = error;
                    if (error.name === 'AbortError') {
                        verboseLog(`Request timeout (attempt ${retryCount + 1}/${maxRetries})`);
                    } else {
                        verboseLog(`Request error (attempt ${retryCount + 1}/${maxRetries}):`, error);
                    }
                    
                    if (retryCount < maxRetries - 1) {
                        retryCount++;
                        const delay = Math.min(1000 * retryCount, 3000);
                        verboseLog(`Retrying in ${delay}ms...`);
                        await new Promise(resolve => setTimeout(resolve, delay));
                    } else {
                        throw error;
                    }
                }
            }
            
            if (!responseData) {
                throw lastError || new Error('Failed to fetch tags after retries');
            }
            verboseLog('Available tags response data:', responseData ? { source: responseData.source, totalCount: responseData.total_count } : null);
            
            // Handle both old array format and new object format
            let tags;
            if (Array.isArray(responseData)) {
                // Old format: direct array
                tags = responseData;
            } else if (responseData && responseData.tags && Array.isArray(responseData.tags)) {
                // New format: {tags: [...], total_count: N, source: '...'}
                tags = responseData.tags;
                verboseLog(`Backend returned ${tags.length} tags from ${responseData.source || 'unknown source'}`);
            } else {
                console.error('No tags loaded from backend or invalid response format:', responseData);
                // Clear existing tags if no new data
                this.state.tags = [];
                this.state.originalTags = [];
                this._updateAvailableTags([]);
                this._restoreAvailableScrollPosition(savedScroll);
                // Hide splash on error
                if (this.hideActionSplash) {
                    this.hideActionSplash();
                }
                return false;
            }
            
            if (tags.length === 0) {
                console.warn('Backend returned empty tags array');
                this.state.tags = [];
                this.state.originalTags = [];
                this._updateAvailableTags([]);
                this._restoreAvailableScrollPosition(savedScroll);
                // Hide splash when no tags
                if (this.hideActionSplash) {
                    this.hideActionSplash();
                }
                return false;
            }
            
            verboseLog(`Fetched ${tags.length} available tags`);

            // Normalize lineage fields so UI consistently prefers database lineage (same pipeline as backend)
            // CRITICAL: Prefer canonical_lineage/currentLineage (from DB) over Lineage to ensure UI matches database
            tags = tags.map(tag => this._normalizeLineageFields(tag));
            
            // CRITICAL FIX: Auto-refresh filters after tags are successfully loaded
            // This ensures filters are populated when data becomes available
            if (tags.length > 0) {
                verboseLog('Tags loaded successfully, refreshing filters...');
                // Use a small delay to ensure Excel processor is ready
                setTimeout(() => {
                    this.fetchAndPopulateFilters(0).catch(error => {
                        console.warn('Auto-refresh filters after tag load failed (non-critical):', error);
                    });
                }, 500);
            }
            
            // Debug: Verify database lineage is being used
            console.log('🔄 Normalized lineage data (database is source of truth):');
            const lineageStats = { withCanonical: 0, withCurrent: 0, withLineage: 0, none: 0 };
            tags.slice(0, 10).forEach(tag => {
                const name = tag['Product Name*'] || tag.ProductName || 'Unknown';
                const canonical = tag.canonical_lineage || 'NONE';
                const current = tag.currentLineage || 'NONE';
                const lineage = tag.Lineage || 'NONE';
                if (tag.canonical_lineage) lineageStats.withCanonical++;
                else if (tag.currentLineage) lineageStats.withCurrent++;
                else if (tag.Lineage) lineageStats.withLineage++;
                else lineageStats.none++;
                console.log(`  ✓ ${name}: canonical=${canonical}, current=${current}, Lineage=${lineage}`);
            });
            console.log(`📊 Lineage source stats (first 10): canonical=${lineageStats.withCanonical}, current=${lineageStats.withCurrent}, Lineage=${lineageStats.withLineage}, none=${lineageStats.none}`);
            
            // Clear existing state and set new data
            this.state.tags = [...tags];
            this.state.originalTags = [...tags]; // Store original tags for validation
            this.state.hydratedFromCache = false;
            this.saveAvailableTagsToCache(tags);
            
            // CRITICAL FIX: Always update UI after loading tags to ensure lineage dropdowns reflect database values
            // This is especially important when lineage alignment happened on the backend
            console.log(`🔄 Updating UI with ${tags.length} tags (source: ${responseData?.source || 'unknown'})`);
            
            // CRITICAL: If lineage was aligned from database, ensure tags are fully re-rendered to show database lineage
            const lineageWasAligned = responseData && responseData.source && 
                (responseData.source.includes('lineage') || responseData.source.includes('db-lineage'));
            
            if (lineageWasAligned) {
                console.log(`✅ Lineage alignment detected (source: ${responseData.source}), re-rendering UI with database lineage`);
            }
            
            // Always update available tags - _updateAvailableTags clears container and re-renders everything
            // This ensures lineage dropdowns reflect the database values from the normalized tags
            this._updateAvailableTags(tags);
            
            // CRITICAL: ALWAYS update selected tags after loading tags to ensure they have database lineage
            // This is essential because selected tags dropdowns need to show database lineage, not Excel lineage
            if (this.state.persistentSelectedTags.length > 0) {
                // Map selected tag names to updated tag objects with database lineage
                const selectedTagObjects = this.state.persistentSelectedTags.map(name => {
                    const updatedTag = tags.find(t => t['Product Name*'] === name);
                    if (updatedTag) {
                        // CRITICAL: Ensure this tag has database lineage - prioritize canonical_lineage/currentLineage
                        const dbLineage = updatedTag.canonical_lineage || updatedTag.currentLineage;
                        if (dbLineage) {
                            // Force all lineage fields to database value (this overwrites Excel Lineage)
                            updatedTag.canonical_lineage = dbLineage;
                            updatedTag.currentLineage = dbLineage;
                            updatedTag.Lineage = dbLineage;  // Overwrite Excel Lineage with database value
                            updatedTag.lineage = dbLineage;
                            updatedTag['Lineage*'] = dbLineage;
                            console.log(`🔄 Selected tag "${name}" updated with database lineage: ${dbLineage} (was: ${updatedTag.Lineage})`);
                        } else {
                            console.warn(`⚠️ Selected tag "${name}" has no database lineage (canonical_lineage or currentLineage)`);
                        }
                        return updatedTag;
                    }
                    console.warn(`⚠️ Selected tag "${name}" not found in updated available tags`);
                    return null;
                }).filter(Boolean);
                
                if (selectedTagObjects.length > 0) {
                    console.log(`✅ Updating ${selectedTagObjects.length} selected tags with database lineage from available tags`);
                    // Force update to ensure dropdowns are re-rendered with database lineage
                    this._forceSelectedTagsUpdate = true;
                    this.updateSelectedTags(selectedTagObjects);
                } else {
                    console.warn(`⚠️ No matching selected tags found in updated available tags`);
                }
            }
            
            // PERFORMANCE: Clear filter cache when tags change
            this._cachedFilterOptions = null;
            this._cachedFilterOptionsHash = null;
            this._cachedFilterOptionsTagsLength = null;
            
            // Preserve selected tags if they exist and are valid (optimized)
            const currentSelectedTags = [...this.state.persistentSelectedTags];
            this.state.persistentSelectedTags = [];
            this.state.selectedTags = new Set();

            if (currentSelectedTags.length > 0) {
                // Build a fast lookup map of product name -> true
                const tagNameSet = new Set(tags.map(t => t['Product Name*']));
                for (const tagName of currentSelectedTags) {
                    if (tagNameSet.has(tagName)) {
                        this.state.persistentSelectedTags.push(tagName);
                        this.state.selectedTags.add(tagName);
                    }
                }
            }
            
            this.validateSelectedTags();
            
            // OPTIMIZATION: If this was a fast load, optionally refresh with lineage alignment in background
            // This allows tags to appear immediately while lineage is updated asynchronously
            if (responseData && responseData.source === 'cache-fast' && tags.length > 0) {
                verboseLog('Fast load completed - tags displayed immediately');
                // Update UI immediately with fast-loaded tags
                this._updateAvailableTags(tags);
                this._restoreAvailableScrollPosition(savedScroll);
                
                // Update tag counts
                this.updateTagCount('available', tags.length);
                this.updateTagCount('selected', this.state.persistentSelectedTags.length);
                
                // Optionally refresh with lineage alignment in background (non-blocking)
                // This ensures lineage is eventually aligned without blocking initial display
                setTimeout(async () => {
                    try {
                        verboseLog('Background: Refreshing tags with lineage alignment...');
                        const lineageResponse = await fetch(`/api/available-tags?t=${Date.now()}&fast_load=0`);
                        if (lineageResponse.ok) {
                            const lineageData = await lineageResponse.json();
                            if (lineageData.tags && lineageData.tags.length > 0) {
                                // Update tags with lineage-aligned data (source will be 'cache+db-lineage' or 'excel+db-lineage')
                                if (lineageData.source && (lineageData.source.includes('lineage') || lineageData.source.includes('db-lineage'))) {
                                    verboseLog(`Background: Updated ${lineageData.tags.length} tags with lineage alignment`);
                                    this.state.tags = [...lineageData.tags];
                                    this.state.originalTags = [...lineageData.tags];
                                    // Only re-render if lineage data actually changed (to avoid flicker)
                                    // Compare lineage values, not just tag names
                                    let lineageChanged = false;
                                    if (tags.length === lineageData.tags.length) {
                                        for (let i = 0; i < tags.length; i++) {
                                            const oldLin = (tags[i].Lineage || tags[i].canonical_lineage || '').toString().trim();
                                            const newLin = (lineageData.tags[i].Lineage || lineageData.tags[i].canonical_lineage || '').toString().trim();
                                            if (oldLin !== newLin) {
                                                lineageChanged = true;
                                                break;
                                            }
                                        }
                                    } else {
                                        lineageChanged = true;
                                    }
                                    
                                    if (lineageChanged) {
                                        // Update only the lineage fields in existing DOM without full re-render
                                        // This is faster and avoids flicker
                                        this._updateAvailableTags(lineageData.tags);
                                    }
                                }
                            }
                        }
                    } catch (bgError) {
                        verboseLog('Background lineage alignment failed (non-critical):', bgError);
                    }
                }, 500); // Small delay to let UI settle
                
                verboseLog(`Successfully updated available tags (fast): ${tags.length} tags`);
                verboseLog('=== fetchAndUpdateAvailableTags END ===');
                return true;
            }
            
            // Update the UI with new tags
            this._updateAvailableTags(tags);
            this._restoreAvailableScrollPosition(savedScroll);
            
            // Update tag counts
            this.updateTagCount('available', tags.length);
            this.updateTagCount('selected', this.state.persistentSelectedTags.length);
            
            verboseLog(`Successfully updated available tags: ${tags.length} tags`);
            verboseLog('=== fetchAndUpdateAvailableTags END ===');
            // Note: Splash will be hidden by _waitForTagsToAppear() when tags appear
            return true;
        } catch (error) {
            console.error('Error fetching available tags:', error);
            verboseLog('=== fetchAndUpdateAvailableTags ERROR ===');
            const fallbackLoaded = await this._fallbackToLiteAvailableTags(error, savedScroll);
            if (fallbackLoaded) {
                verboseLog('✅ Fallback lite tags loaded successfully');
                return true;
            }
            // Hide splash on error
            if (this.hideActionSplash) {
                this.hideActionSplash();
            }

            // CRITICAL FIX: Show user-friendly error message with retry button
            const availableTagsContainer = document.getElementById('availableTags');
            if (availableTagsContainer) {
                availableTagsContainer.innerHTML = `
                    <div class="text-center py-4">
                        <div class="alert alert-warning mx-3">
                            <h5 class="alert-heading">Unable to Load Tags</h5>
                            <p class="mb-3">There was a problem loading the product tags. This can happen if the database is temporarily unavailable or the connection timed out.</p>
                            <button class="btn btn-primary" onclick="TagManager.retryLoadTags()">
                                <i class="fas fa-redo"></i> Retry Loading Tags
                            </button>
                        </div>
                        <small class="text-muted d-block mt-2">Error: ${error.message || 'Unknown error'}</small>
                    </div>
                `;
            }

            return false;
        }
    },

    async retryLoadTags() {
        verboseLog('User requested retry of tag loading');
        // Reset rate limiting to allow immediate retry
        this._lastFetchTime = 0;
        // Show loading indicator
        this.showActionSplash('Retrying tag loading...');
        // Attempt to load tags again
        try {
            await this.fetchAndUpdateAvailableTags();
        } catch (error) {
            console.error('Retry failed:', error);
        }
    },
    
    _normalizeLineageFields(tag) {
        try {
            // CRITICAL: Always prioritize canonical_lineage/currentLineage (from database) as source of truth
            // If database lineage exists, use it exclusively - don't fall back to Excel Lineage
            let lin;
            let fromDatabase = false;
            
            if (tag.canonical_lineage || tag.currentLineage) {
                // Database lineage exists - use it (this is the source of truth)
                lin = (tag.canonical_lineage || tag.currentLineage || '').toString().trim();
                fromDatabase = true;
            } else {
                // No database lineage - fall back to other fields only if database lineage is missing
                lin = (tag.Lineage || tag.lineage || '').toString().trim();
            }
            
            if (lin) {
                const normalized = lin.toUpperCase();
                // CRITICAL: If database lineage exists, set ALL fields to the database value for consistency
                // This ensures UI always shows database lineage, not Excel lineage
                if (fromDatabase) {
                    // Database lineage is source of truth - set ALL fields to database value
                    tag.canonical_lineage = normalized;
                    tag.currentLineage = normalized;
                    tag.Lineage = normalized;
                    tag.lineage = normalized;
                    tag['Lineage*'] = normalized;
                } else {
                    // No database lineage - normalize all fields to the same value
                    // But don't set canonical_lineage/currentLineage (they should come from database)
                    tag.Lineage = normalized;
                    tag.lineage = normalized;
                    tag['Lineage*'] = normalized;
                }
            }
        } catch (e) {
            console.warn('Failed to normalize lineage for tag:', tag, e);
        }
        return tag;
    },
    
    async _fallbackToLiteAvailableTags(originalError, savedScrollPosition) {
        try {
            verboseLog('Attempting fallback to /api/available-tags-lite due to error:', originalError?.message || originalError);
            const response = await fetch(`/api/available-tags-lite?t=${Date.now()}`);
            if (!response.ok) {
                throw new Error(`Lite endpoint HTTP ${response.status}: ${response.statusText}`);
            }
            
            const responseText = await response.text();
            let fallbackData = null;
            if (responseText) {
                try {
                    fallbackData = JSON.parse(responseText);
                } catch (parseError) {
                    console.error('Failed to parse /api/available-tags-lite response:', {
                        parseError,
                        snippet: responseText.slice(0, 500)
                    });
                    throw parseError;
                }
            }
            
            if (!fallbackData || !Array.isArray(fallbackData.tags) || fallbackData.tags.length === 0) {
                verboseLog('Fallback lite endpoint returned no tags');
                return false;
            }
            
            const tags = fallbackData.tags.map(tag => this._normalizeLineageFields(tag));
            this.state.tags = [...tags];
            this.state.originalTags = [...tags];
            this._cachedFilterOptions = null;
            this._cachedFilterOptionsHash = null;
            this._cachedFilterOptionsTagsLength = null;
            
            const currentSelectedTags = [...this.state.persistentSelectedTags];
            this.state.persistentSelectedTags = [];
            this.state.selectedTags = new Set();
            
            if (currentSelectedTags.length > 0) {
                const tagNameSet = new Set(tags.map(t => t['Product Name*']));
                for (const tagName of currentSelectedTags) {
                    if (tagNameSet.has(tagName)) {
                        this.state.persistentSelectedTags.push(tagName);
                        this.state.selectedTags.add(tagName);
                    }
                }
            }
            
            this.validateSelectedTags();
            this._updateAvailableTags(tags);
            this._restoreAvailableScrollPosition(savedScrollPosition);
            this.updateTagCount('available', tags.length);
            this.updateTagCount('selected', this.state.persistentSelectedTags.length);
            
            if (window.Toast && typeof window.Toast.show === 'function') {
                window.Toast.show('warning', 'Loaded limited tag list due to a server error. Some filters may be unavailable.', { duration: 6000 });
            }
            return true;
        } catch (fallbackError) {
            console.error('Fallback to /api/available-tags-lite failed:', fallbackError);
            return false;
        } finally {
            if (this.hideActionSplash) {
                this.hideActionSplash();
            }
        }
    },

    async fetchAndUpdateSelectedTags() {
        try {
            verboseLog('Fetching selected tags...');
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
            
            verboseLog(`Fetched ${selectedTags.length} selected tags:`, selectedTags.map(tag => tag['Product Name*']));
            
            // Update persistentSelectedTags with the fetched tags from backend
            verboseLog('Updating persistentSelectedTags with fetched tags:', selectedTags.map(tag => tag['Product Name*']));
            this.state.persistentSelectedTags = selectedTags.map(tag => tag['Product Name*']);
            // Save to localStorage for persistence
            this.saveSelectedTagsToStorage();
            this.state.selectedTags = new Set(this.state.persistentSelectedTags);
            verboseLog('persistentSelectedTags after update:', this.state.persistentSelectedTags);
            verboseLog('selectedTags after update:', this.state.selectedTags);
            
            this.updateSelectedTags(selectedTags);
            
            // Ensure drag and drop is working after fetching tags
            if (window.dragAndDropManager && selectedTags.length > 0) {
                setTimeout(() => {
                    verboseLog('Reinitializing drag and drop after fetchAndUpdateSelectedTags');
                    window.dragAndDropManager.reinitializeTagDragAndDrop();
                }, 300);
            }
            
            return true;
        } catch (error) {
            console.error('Error fetching selected tags:', error);
            this.updateSelectedTags([]);
            return false;
        }
    },

    async fetchAndPopulateFilters(retryCount = 0, skipIfEmpty = false) {
        const maxRetries = 5; // Increased retries
        const retryDelay = 2000; // Increased to 2 seconds for better chance of data being ready
        
        try {
            // Use the filter options API with cache refresh and timestamp to ensure updated weight formatting
            const timestamp = Date.now();
            const response = await fetch(`/api/filter-options?refresh=true&t=${timestamp}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Failed to fetch filter options: ${response.status} ${errorText}`);
            }
            
            const filterOptions = await response.json();
            verboseLog('Fetched filter options:', filterOptions);
            
            // CRITICAL FIX: Check for error field in response, but don't treat "No default file available" as an error
            // Database-only mode is valid and shouldn't trigger warnings
            if (filterOptions.error && filterOptions.error !== 'No default file available') {
                console.warn(`Filter options error: ${filterOptions.error}`, filterOptions.debug || '');
                
                // If there's an error but we haven't exceeded retries, retry
                if (retryCount < maxRetries) {
                    verboseLog(`⚠️ Filter options error (attempt ${retryCount + 1}/${maxRetries}), retrying in ${retryDelay}ms...`);
                    setTimeout(() => {
                        this.fetchAndPopulateFilters(retryCount + 1, skipIfEmpty);
                    }, retryDelay);
                    return;
                } else {
                    console.error('Filter options error after all retries:', filterOptions.error);
                    // CRITICAL FIX: Don't clear filters if skipIfEmpty is true and user has selections
                    if (!skipIfEmpty) {
                        this.updateFilters({
                            vendor: [],
                            brand: [],
                            productType: [],
                            lineage: [],
                            weight: [],
                            strain: [],
                            doh: [],
                            highCbd: []
                        }, true);
                    } else {
                        verboseLog('⏭️ Skipping filter update - preserving user selections');
                    }
                    return;
                }
            }
            
            // CRITICAL FIX: If database-only mode, don't log as error - this is normal
            if (filterOptions.error === 'No default file available' || filterOptions.debug?.database_only_mode) {
                verboseLog('Database-only mode: No Excel file loaded, using database for filters');
                // Continue to update filters with empty arrays (will be populated from database when available)
            }
            
            // CRITICAL FIX: Check if filters are empty and retry if needed
            const hasData = (filterOptions.vendor && filterOptions.vendor.length > 0) ||
                           (filterOptions.brand && filterOptions.brand.length > 0) ||
                           (filterOptions.productType && filterOptions.productType.length > 0) ||
                           (filterOptions.lineage && filterOptions.lineage.length > 0) ||
                           (filterOptions.weight && filterOptions.weight.length > 0);
            
            if (!hasData && retryCount < maxRetries) {
                verboseLog(`⚠️ Filters are empty (attempt ${retryCount + 1}/${maxRetries}), retrying in ${retryDelay}ms...`);
                setTimeout(() => {
                    this.fetchAndPopulateFilters(retryCount + 1, skipIfEmpty);
                }, retryDelay);
                return;
            }
            
            // CRITICAL FIX: If skipIfEmpty is true and no data, don't update filters to preserve user selections
            if (!hasData && skipIfEmpty && retryCount >= maxRetries) {
                verboseLog('⏭️ Skipping filter update - no data and skipIfEmpty=true, preserving user selections');
                return;
            }
            
            // Update filters even if empty (to clear previous values) - but only if not skipping
            this.updateFilters(filterOptions, true); // Preserve existing filter values
            
            // If filters were empty after retries, log a warning but don't block
            if (!hasData && retryCount >= maxRetries) {
                console.warn('⚠️ Filters remain empty after all retries - data may not be loaded yet. Filters will refresh when data becomes available.');
            } else if (hasData) {
                verboseLog(`✅ Filters loaded successfully: vendor=${filterOptions.vendor?.length || 0}, brand=${filterOptions.brand?.length || 0}, productType=${filterOptions.productType?.length || 0}`);
            }
        } catch (error) {
            console.error('Error fetching filter options:', error);
            
            // Retry on error if we haven't exceeded max retries
            if (retryCount < maxRetries) {
                verboseLog(`⚠️ Filter fetch error (attempt ${retryCount + 1}/${maxRetries}), retrying in ${retryDelay}ms...`);
                setTimeout(() => {
                    this.fetchAndPopulateFilters(retryCount + 1, skipIfEmpty);
                }, retryDelay);
            } else {
                console.error('Failed to load filter options after all retries');
                // CRITICAL FIX: Don't clear filters if skipIfEmpty is true
                if (!skipIfEmpty) {
                    this.updateFilters({
                        vendor: [],
                        brand: [],
                        productType: [],
                        lineage: [],
                        weight: [],
                        strain: [],
                        doh: [],
                        highCbd: []
                    }, true);
                } else {
                    verboseLog('⏭️ Skipping filter update on error - preserving user selections');
                }
            }
        }
    },

    /**
     * Refresh the available tags, selected tags, and filters after an upload completes.
     * Options:
     *   - preserveFilters (default true): keep current filter selections
     *   - force (default true): temporarily bypass fetch rate limiting
     */
    async refreshTagLists(options = {}) {
        const { preserveFilters = true, force = true } = options;
        verboseLog('=== refreshTagLists START ===', { preserveFilters, force });

        // Optionally preserve filters by skipping reset
        if (!preserveFilters) {
            this.clearUIStateForNewFile(false);
        }

        // Temporarily bypass fetch rate limiting if requested
        const previousFetchTime = this._lastFetchTime;
        if (force) {
            this._lastFetchTime = 0;
        }

        // Set flag to enable fast_load for post-upload tag loading
        this._isPostUploadLoad = true;

        try {
            // PERFORMANCE FIX: For post-upload, use fast-load mode to skip database enrichment initially
            // This allows tags to display immediately, then enrich in background
            const isPostUpload = force || this._isPostUploadLoad;
            if (isPostUpload) {
                console.log('⚡ Post-upload detected - using fast tag loading');
                // Set flag to skip enrichment in initial load
                this._skipEnrichment = true;
            }
            
            // CRITICAL FIX: Fetch filters AFTER tags are loaded to ensure data is ready
            await this.fetchAndUpdateAvailableTags();
            await this.fetchAndUpdateSelectedTags();
            
            // Small delay to ensure Excel processor is ready
            await new Promise(resolve => setTimeout(resolve, 200));
            
            // Now fetch filters with retry mechanism
            await this.fetchAndPopulateFilters();
            
            // PERFORMANCE: After tags are displayed, enrich them in background
            if (isPostUpload && this._skipEnrichment) {
                console.log('⚡ Enriching tags in background...');
                this._skipEnrichment = false;
                // Enrich tags in background without blocking UI
                setTimeout(async () => {
                    try {
                        await this.fetchAndUpdateAvailableTags();
                        console.log('✅ Background tag enrichment complete');
                    } catch (err) {
                        console.warn('Background enrichment failed:', err);
                    }
                }, 100);
            }
            
            const results = [true, true, true]; // All succeeded

            // Ensure UI reflects latest state
            this.updateSelectAllCheckboxes();
            this.updateGenerateButtonState();
            this.alignDisplayedLineagesWithTags();

            verboseLog('=== refreshTagLists END ===', results);
            return results;
        } catch (error) {
            console.error('refreshTagLists error:', error);
            throw error;
        } finally {
            // Clear post-upload flag
            this._isPostUploadLoad = false;
            if (force) {
                this._lastFetchTime = previousFetchTime;
            }
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
        console.log('🚀 === TAGMANAGER INIT FUNCTION CALLED ===');
        console.log('⚡ TagManager initializing...');
        const availableTagsContainer = document.getElementById('availableTags');
        console.log('📦 Available tags container found:', !!availableTagsContainer);
        if (availableTagsContainer) {
            console.log('📝 Container ready for tags');
        }
        
        // Skip platform detection for Mac-like speed
        // this.detectPlatform();
        
        // Show application splash screen
        AppLoadingSplash.show();
        AppLoadingSplash.startAutoAdvance();
        
        // Initialize empty state first
        this.clearInitialDataRetry();
        this.initializeEmptyState();
        AppLoadingSplash.nextStep(); // Templates loaded
        
        // Check if there's already data loaded (e.g., from a previous session or default file)
        this.checkForExistingData();
        
        // GUARANTEED FIX: Restore filters from localStorage on page load
        const savedFilters = this.loadFiltersFromStorage();
        this.state.filters = savedFilters || {
            vendor: 'All',
            brand: 'All',
            productType: 'All',
            lineage: 'All',
            weight: 'All'
        };
        
        // Set each filter dropdown to saved value or 'All' (or '')
        const filterIds = ['vendorFilter', 'brandFilter', 'productTypeFilter', 'lineageFilter', 'weightFilter', 'dohFilter', 'highCbdFilter'];
        const filterMap = {
            'vendorFilter': 'vendor',
            'brandFilter': 'brand',
            'productTypeFilter': 'productType',
            'lineageFilter': 'lineage',
            'weightFilter': 'weight',
            'dohFilter': 'doh',
            'highCbdFilter': 'highCbd'
        };
        filterIds.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                const filterKey = filterMap[id];
                const savedValue = this.state.filters[filterKey];
                if (savedValue && savedValue !== 'All') {
                    el.value = savedValue;
                } else {
                    el.value = '';
                }
            }
        });
        // Don't apply filters immediately - let checkForExistingData handle it
        // this.applyFilters();
        
        // Add filter change event listeners immediately (no delay for better UX)
        verboseLog('=== SETTING UP FILTER EVENT LISTENERS ===');
        this.setupFilterEventListeners();
        verboseLog('=== FILTER EVENT LISTENERS SETUP COMPLETE ===');
        
        // Also set up listeners after a short delay as backup (in case filters aren't ready yet)
        setTimeout(() => {
            verboseLog('=== BACKUP: RE-CHECKING FILTER EVENT LISTENERS ===');
            this.setupFilterEventListeners();
        }, 100);
        
        // Add search event listeners
        this.setupSearchEventListeners();
        
        // Skip PC compatibility for Mac-like speed
        // this.initializePCCompatibility();
        
        // Start memory optimization
        this.startMemoryOptimization();
        
        // Start periodic filter refresh to ensure filters stay in sync with data
        this.startPeriodicFilterRefresh();
        
        // Update table header if TagsTable is available
        setTimeout(() => {
            // Also update table header if TagsTable is available
            if (typeof TagsTable !== 'undefined' && TagsTable.updateTableHeader) {
                TagsTable.updateTableHeader();
            }
        }, 100);

        // Initialize drag and drop manager
        // NOTE: Removed early initialization - drag-and-drop will be initialized after tags are loaded
        // by fetchAndUpdateSelectedTags() to avoid "Found 0 total tag rows" warnings
        // setTimeout(() => {
        //     if (window.dragAndDropManager) {
        //         window.dragAndDropManager.setupTagDragAndDrop();
        //     }
        // }, 200);

        // JSON matching is now handled by the modal - removed old above-tags-list logic
        
        // Emergency initialization fix - force complete after 15 seconds
        setTimeout(() => {
            if (AppLoadingSplash && AppLoadingSplash.isVisible) {
                verboseLog('Emergency initialization fix: forcing splash completion');
                AppLoadingSplash.stopAutoAdvance();
                AppLoadingSplash.complete();
            }
        }, 15000);
        
        // Additional emergency fix for stuck initialization
        window.addEventListener('load', () => {
            setTimeout(() => {
                const splash = document.getElementById('appLoadingSplash');
                if (splash && splash.style.display !== 'none') {
                    verboseLog('Emergency fix: hiding stuck splash screen');
                    splash.style.display = 'none';
                    const mainContent = document.getElementById('mainContent');
                    if (mainContent) {
                        mainContent.style.display = 'block';
                    }
                }
            }, 20000); // 20 second emergency timeout
        });
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

    // Set loading state (used by enhanced-ui.js)
    setLoading(isLoading) {
        if (isLoading) {
            this.showLoadingIndicator();
        } else {
            this.hideLoadingIndicator();
        }
    },

    // Initialize with empty state to prevent undefined errors
    initializeEmptyState() {
        verboseLog('Initializing empty state...');
        
        // Initialize with empty arrays to prevent undefined errors
        this.state.tags = [];
        this.state.originalTags = [];
        this.state.selectedTags = new Set();
        this.state.persistentSelectedTags = []; // Changed from Set to Array to preserve order
        
        // Clear any persistent storage
        if (window.localStorage) {
            localStorage.removeItem('selectedTags');
            localStorage.removeItem('selected_tags');
        }
        if (window.sessionStorage) {
            sessionStorage.removeItem('selectedTags');
            sessionStorage.removeItem('selected_tags');
        }
        
        // Don't update UI immediately - let checkForExistingData handle it
        // this.debouncedUpdateAvailableTags([], null);
        // this.updateSelectedTags([]);
        
        // Initialize filters with empty options
        const emptyFilters = {
            vendor: [],
            brand: [],
            productType: [],
            lineage: [],
            weight: []
        };
        this.updateFilters(emptyFilters, false); // Don't preserve values when initializing empty state
        
        verboseLog('Empty state initialized');
    },

    // Check if there's existing data and load it
    async checkForExistingData() {
        // Prevent multiple simultaneous calls
        if (this._checkingExistingData) {
            verboseLog('checkForExistingData already in progress, skipping...');
            return;
        }
        this._checkingExistingData = true;

        verboseLog('=== CHECK FOR EXISTING DATA FUNCTION CALLED ===');
        verboseLog('Checking for existing data...');

        // Check for current uploaded file FIRST to determine if we should show loading or upload prompt
        let hasFile = false;
        try {
            const fileResponse = await fetch('/api/current-file');
            if (fileResponse.ok) {
                const fileData = await fileResponse.json();
                if (fileData && fileData.success && fileData.has_file && fileData.filename) {
                    hasFile = true;
                    verboseLog(`Found uploaded file in session: ${fileData.filename}`);
                    // Update file info
                    const fileInfoText = document.getElementById('fileInfoText');
                    if (fileInfoText) {
                        fileInfoText.textContent = fileData.filename;
                    }
                    const currentFileInfo = document.getElementById('currentFileInfo');
                    if (currentFileInfo) {
                        currentFileInfo.textContent = fileData.filename;
                    }
                    verboseLog(`File info updated: ${fileData.filename} (${fileData.row_count || 0} rows)`);
                }
            }
        } catch (error) {
            verboseLog('Error checking for current file:', error);
        }

        // Show loading splash only if file exists, otherwise show upload prompt
        const availableTagsContainer = document.getElementById('availableTags');
        if (availableTagsContainer) {
            if (hasFile) {
                // File exists - show loading indicator
                this.showActionSplash('Loading tags...');
                availableTagsContainer.innerHTML = `
                    <div class="text-center py-4">
                        <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-2 text-white">Loading tags...</p>
                    </div>
                `;
            } else {
                // No file - show upload prompt instead of loading splash
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
                // No file, so exit early
                this._checkingExistingData = false;
                return;
            }
        }

        const retryDelays = Array.isArray(this.initialDataRetryDelays) && this.initialDataRetryDelays.length > 0
            ? this.initialDataRetryDelays
            : [2000];
        this.state.initialDataAttempts = (this.state.initialDataAttempts || 0) + 1;
        const attemptNumber = this.state.initialDataAttempts;
        const maxAttempts = retryDelays.length + 1;
        verboseLog(`[InitialData] Attempt ${attemptNumber}/${maxAttempts}`);
        if (attemptNumber > maxAttempts) {
            console.warn(`[InitialData] Attempt limit exceeded (${maxAttempts}); falling back to direct tag load.`);
            // CRITICAL FIX: Fall back to direct tag loading instead of giving up
            verboseLog('Attempting direct tag load as fallback...');
            try {
                await this.fetchAndUpdateAvailableTags();
                await this.fetchAndUpdateSelectedTags();
                await this.fetchAndPopulateFilters();
                this._checkingExistingData = false;
                return;
            } catch (fallbackError) {
                console.error('Fallback tag loading failed:', fallbackError);
                if (this.hideActionSplash) {
                    this.hideActionSplash();
                }
                this._checkingExistingData = false;
                return;
            }
        }

        // PERFORMANCE FIX: Try cache first for instant load
        const cachedTags = this.loadAvailableTagsFromCache();
        if (cachedTags && cachedTags.length > 0) {
            console.log(`⚡ INSTANT CACHE LOAD: ${cachedTags.length} tags available`);
            // Render cached tags IMMEDIATELY for instant display
            this.state.tags = [...cachedTags];
            this.state.originalTags = [...cachedTags];
            
            // CRITICAL: Render immediately using requestAnimationFrame for instant UI update
            requestAnimationFrame(() => {
                this._updateAvailableTags(cachedTags);
                console.log(`✅ INSTANT RENDER: ${cachedTags.length} tags displayed from cache`);
                
                // Hide splash IMMEDIATELY since we have cached tags
                if (this.hideActionSplash) {
                    this.hideActionSplash();
                }
                if (typeof AppLoadingSplash !== 'undefined' && AppLoadingSplash.isVisible) {
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                }
            });

            // Continue loading fresh data in background (non-blocking)
            console.log('📡 Background: Fetching selected tags and filters');
            // CRITICAL FIX: Fetch filters AFTER selected tags to ensure data is ready
            Promise.allSettled([
                this.fetchAndUpdateSelectedTags()
            ]).then(() => {
                // Small delay to ensure Excel processor is ready
                return new Promise(resolve => setTimeout(resolve, 200));
            }).then(() => {
                // Now fetch filters with retry mechanism
                return this.fetchAndPopulateFilters();
            }).then(() => {
                console.log('✅ Background: Selected tags and filters loaded');
            }).catch(err => {
                console.warn('Background load error (non-critical):', err);
            });
            
            clearTimeout(splashSafetyTimeout);
            this._checkingExistingData = false;
            return; // Exit early - we have cached data
        }

        // PERFORMANCE FIX: Reduced timeout to 8 seconds - if it takes longer, use cache/fallback
        const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('Initialization timeout')), 8000);
        });

        // Safety net: ensure loading overlay never blocks interaction for long
        // Reduced to 10 seconds since we're using faster timeouts and cache
        const splashSafetyTimeout = setTimeout(() => {
            // Check if tags have loaded before hiding splash
            const availableTagsContainer = document.getElementById('availableTags');
            const tagItems = availableTagsContainer ? availableTagsContainer.querySelectorAll('.tag-item') : [];
            const hasTags = tagItems.length > 0 || (this.state.tags && this.state.tags.length > 0);
            
            if (!hasTags) {
                console.warn('⏳ Safety timeout triggered - no tags found, attempting fallback load (non-blocking)');
                // Fire-and-forget fallback fetch so UI stays responsive
                try {
                    this.fetchAndUpdateAvailableTags().then(() => {
                        verboseLog('Fallback tag loading succeeded');
                        // Hide splash after tags load
                        if (typeof this.hideActionSplash === 'function') {
                            this.hideActionSplash();
                        }
                    }).catch(fallbackError => {
                        console.error('Fallback tag loading failed:', fallbackError);
                        // Only hide splash if we're sure there are no tags
                        if (typeof this.hideActionSplash === 'function') {
                            this.hideActionSplash();
                        }
                    });
                } catch (fallbackError) {
                    console.error('Fallback tag loading threw synchronously:', fallbackError);
                    if (typeof this.hideActionSplash === 'function') {
                        this.hideActionSplash();
                    }
                }
            } else {
                verboseLog(`⏳ Safety timeout triggered but ${tagItems.length} tags found - hiding splash`);
                // Tags are loaded, safe to hide splash
                if (typeof this.hideActionSplash === 'function') {
                    this.hideActionSplash();
                }
            }
            
            AppLoadingSplash.stopAutoAdvance();
            AppLoadingSplash.complete();
        }, 10000); // 10 second safety net - should be enough with optimizations

        try {
            // PERFORMANCE FIX: Use fast_load=1 for initial loads to skip expensive lineage alignment
            // This dramatically speeds up initial tag loading
            const response = await Promise.race([
                fetch('/api/initial-data?fast_load=1'),
                timeoutPromise
            ]);

            if (response.ok) {
                const data = await response.json();
                verboseLog('Initial data response:', data);
                // CRITICAL: Check data_loaded flag first - if false, show upload prompt even if success
                if (data.success && data.data_loaded === false) {
                    verboseLog('No data loaded (data_loaded=false), showing upload prompt');
                    // Complete splash loading when no data
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                    clearTimeout(splashSafetyTimeout);
                    
                    // Hide action splash when no data
                    if (this.hideActionSplash) {
                        this.hideActionSplash();
                    }
                    
                    // Show upload prompt in Current Inventory when no file/data
                    const availableTagsContainer = document.getElementById('availableTags');
                    if (availableTagsContainer) {
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
                    
                    this.initializeEmptyState();
                    this._checkingExistingData = false;
                    return;
                } else if (data.success && data.available_tags && Array.isArray(data.available_tags) && data.available_tags.length > 0) {
                    verboseLog(`Found ${data.available_tags.length} existing tags, loading data...`);

                    // Update splash progress for data loading
                    AppLoadingSplash.updateProgress(60, 'Loading product data...');

                    // Splash already shown at start of function, just update message
                    const splashMessage = document.querySelector('#actionSplash .action-splash-message');
                    if (splashMessage) {
                        splashMessage.textContent = 'Loading product tags...';
                    }

                    // PERFORMANCE FIX: Update tags immediately without debounce delay for initial load
                    AppLoadingSplash.updateProgress(75, 'Processing tags...');
                    // Use direct _updateAvailableTags for instant display (no debounce delay)
                    this._updateAvailableTags(data.available_tags, null);
                    
                    // Run selected tags and filters in parallel for faster loading
                    AppLoadingSplash.updateProgress(85, 'Restoring selections...');
                    verboseLog('About to fetch and update selected tags and filters in parallel...');
                    
                    // CRITICAL FIX: Fetch filters AFTER tags are confirmed loaded
                    // This ensures Excel processor has data before filters are populated
                    await this.fetchAndUpdateSelectedTags();
                    
                    // Small delay to ensure Excel processor is ready
                    await new Promise(resolve => setTimeout(resolve, 100));
                    
                    // Now fetch filters with retry mechanism
                    await this.fetchAndPopulateFilters();
                    
                    verboseLog('fetchAndUpdateSelectedTags result:', selectedTagsResult);
                    verboseLog('persistentSelectedTags after restore:', this.state.persistentSelectedTags);

                    // Update filters from data (already populated in parallel above, but update UI)
                    AppLoadingSplash.updateProgress(90, 'Setting up filters...');
                    this.updateFilters(data.filters || {
                        vendor: [],
                        brand: [],
                        productType: [],
                        lineage: [],
                        weight: []
                    }, true); // Preserve existing values when loading initial data
                    
                    // Wait for tags to appear before hiding splash
                    if (this._waitForTagsToAppear) {
                        this._waitForTagsToAppear();
                    }

                    // Update file info text to show the loaded filename
                    if (data.filename) {
                        const fileInfoText = document.getElementById('fileInfoText');
                        if (fileInfoText) {
                            fileInfoText.textContent = data.filename;
                        }
                    }
                    
                    // CRITICAL FIX: Don't hide splash here - wait for tags to be fully rendered
                    // The _waitForTagsToAppear() function will hide the splash when tags are actually loaded
                    // This ensures the splash stays visible until tags are fully rendered
                    AppLoadingSplash.updateProgress(95, 'Finalizing...');
                    clearTimeout(splashSafetyTimeout);
                    
                    this.clearInitialDataRetry();
                    this._checkingExistingData = false;
                    verboseLog('Initial data loaded successfully');
                    return;
                } else {
                    verboseLog('No initial data available:', data.message || 'No data found');
                    // Complete splash loading even if no data
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                    clearTimeout(splashSafetyTimeout);
                    
                    // Hide action splash when no data
                    if (this.hideActionSplash) {
                        this.hideActionSplash();
                    }
                    
                    // Show upload prompt in Current Inventory when no file/data
                    const availableTagsContainer = document.getElementById('availableTags');
                    if (availableTagsContainer) {
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
                    
                    // FIXED: Initialize empty state instead of loading test data
                    this.initializeEmptyState();
                    this._checkingExistingData = false;
                    this.scheduleInitialDataRetry('Empty initial data response');
                    return;
                }
            } else {
                verboseLog('Initial data endpoint returned error:', response.status);
                // Complete splash loading on error
                AppLoadingSplash.stopAutoAdvance();
                AppLoadingSplash.complete();
                clearTimeout(splashSafetyTimeout);
                
                // Hide action splash on error
                if (this.hideActionSplash) {
                    this.hideActionSplash();
                }
                
                // Show upload prompt in Current Inventory on error (likely no file)
                const availableTagsContainer = document.getElementById('availableTags');
                if (availableTagsContainer) {
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
                
                // FIXED: Initialize empty state instead of loading test data
                this.initializeEmptyState();
                this._checkingExistingData = false;
                this.scheduleInitialDataRetry(`HTTP ${response.status}`);
                return;
            }
        } catch (error) {
            verboseLog('Error loading initial data:', error.message);
            
            // Handle timeout specifically
            if (error.message === 'Initialization timeout') {
                verboseLog('Initialization timed out, proceeding with empty state');
                AppLoadingSplash.updateProgress(100, 'Ready to upload files');
            }
            
            // Complete splash loading on error
            AppLoadingSplash.stopAutoAdvance();
            AppLoadingSplash.complete();
            clearTimeout(splashSafetyTimeout);
            
            // Hide action splash on error
            if (this.hideActionSplash) {
                this.hideActionSplash();
            }
            
            // Show upload prompt in Current Inventory on error/timeout
            const availableTagsContainer = document.getElementById('availableTags');
            if (availableTagsContainer) {
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
            
            // FIXED: Initialize empty state instead of loading test data
            this.initializeEmptyState();
            this._checkingExistingData = false;
            this.scheduleInitialDataRetry(error.message || 'initial data fetch error');
            return;
        }
    },

    loadTestData() {
        verboseLog('=== LOAD TEST DATA FUNCTION CALLED ===');
        verboseLog('Loading test data automatically...');
        
        // Automatically load test data for demonstration
        try {
            const testData = [
                {
                    'Product Name*': 'Blue Dream Flower',
                    'Product Brand': 'Green Valley',
                    'Vendor': 'ABC Dispensary',
                    'Product Type*': 'flower',
                    'Lineage': 'SATIVA',
                    'Weight*': '3.5g',
                    'DOH': 'YES'
                },
                {
                    'Product Name*': 'Purple Kush Concentrate',
                    'Product Brand': 'Purple Labs',
                    'Vendor': 'XYZ Cannabis',
                    'Product Type*': 'concentrate',
                    'Lineage': 'INDICA',
                    'Weight*': '1g',
                    'DOH': 'NO'
                },
                {
                    'Product Name*': 'CBD Gummies',
                    'Product Brand': 'Wellness Co',
                    'Vendor': 'Health Store',
                    'Product Type*': 'edible',
                    'Lineage': 'CBD',
                    'Weight*': '10mg',
                    'DOH': 'YES'
                },
                {
                    'Product Name*': 'Sour Diesel Pre-Roll',
                    'Product Brand': 'Fire Brand',
                    'Vendor': 'Local Dispensary',
                    'Product Type*': 'pre-roll',
                    'Lineage': 'SATIVA',
                    'Weight*': '1g',
                    'DOH': 'YES'
                },
                {
                    'Product Name*': 'OG Kush Flower',
                    'Product Brand': 'OG Farms',
                    'Vendor': 'Premium Cannabis',
                    'Product Type*': 'flower',
                    'Lineage': 'HYBRID',
                    'Weight*': '7g',
                    'DOH': 'NO'
                },
                {
                    'Product Name*': 'Mint Chocolate Chip Edible',
                    'Product Brand': 'Sweet Treats',
                    'Vendor': 'Edibles Plus',
                    'Product Type*': 'edible',
                    'Lineage': 'HYBRID',
                    'Weight*': '50mg',
                    'DOH': 'YES'
                },
                {
                    'Product Name*': 'Lemon Haze Vape Cartridge',
                    'Product Brand': 'Vape Pro',
                    'Vendor': 'Vape Shop',
                    'Product Type*': 'vape cartridge',
                    'Lineage': 'SATIVA',
                    'Weight*': '0.5g',
                    'DOH': 'YES'
                },
                {
                    'Product Name*': 'Granddaddy Purple Concentrate',
                    'Product Brand': 'Purple Labs',
                    'Vendor': 'Premium Cannabis',
                    'Product Type*': 'concentrate',
                    'Lineage': 'INDICA',
                    'Weight*': '2g',
                    'DOH': 'NO'
                }
            ];
            
            verboseLog('Loading test data automatically...');
            verboseLog('Test data:', testData);
            if (testData.length > 0) {
                verboseLog('First test data item fields:', Object.keys(testData[0]));
            }
            
            // Set the test data
            this.state.tags = [...testData];
            this.state.originalTags = [...testData];
            
            verboseLog('State after loading test data:', {
                tagsLength: this.state.tags.length,
                originalTagsLength: this.state.originalTags.length
            });
            
            // Clear selected tags for fresh start
            this.state.persistentSelectedTags = [];
            this.state.selectedTags = new Set();
            
            // Update the UI with test data
            verboseLog('Calling _updateAvailableTags with test data...');
            this._updateAvailableTags(testData);
            
            // Update tag counts
            this.updateTagCount('available', testData.length);
            this.updateTagCount('selected', 0);
            
            // Update filters with test data options
            const filters = {
                vendor: [...new Set(testData.map(tag => tag.Vendor || tag.vendor || ''))],
                brand: [...new Set(testData.map(tag => tag['Product Brand'] || tag.brand || ''))],
                productType: [...new Set(testData.map(tag => tag['Product Type*'] || tag.productType || ''))],
                lineage: [...new Set(testData.map(tag => tag.Lineage || tag.lineage || ''))],
                weight: [...new Set(testData.map(tag => tag['Weight*'] || tag.weight || ''))],
                doh: [...new Set(testData.map(tag => tag.DOH || tag.doh || ''))],
                highCbd: ['Non-High CBD Products']
            };
            
            verboseLog('Test data filters:', filters);
            this.updateFilters(filters, false); // Don't preserve values when loading test data
            
            verboseLog('Test data loaded successfully:', testData.length, 'tags');
            verboseLog('Test data sample:', testData[0]);
            
        } catch (error) {
            console.error('Error loading test data:', error);
        }
        
        // Complete splash loading
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

        // Force refresh persistentSelectedTags from UI checkboxes before generation
        const checkedFromUI = Array.from(document.querySelectorAll('#selectedTags input[type="checkbox"].tag-checkbox:checked')).map(cb => cb.value);
        if (checkedFromUI.length > 0) {
            this.state.persistentSelectedTags = checkedFromUI;
        }

        console.time('debouncedGenerate');
        const generateBtn = document.getElementById('generateBtn');
        const splashModal = document.getElementById('generationSplashModal');
        const splashCanvas = document.getElementById('generation-splash-canvas');

        // Add generation lock to prevent multiple simultaneous requests
        if (this.isGenerating) {
            verboseLog('Generation already in progress, ignoring duplicate request');
            return;
        }
        this.isGenerating = true;

        try {
            // Always use the latest persistentSelectedTags for generation
            let checkedTags = [...this.state.persistentSelectedTags];

            verboseLog('Generation request - persistentSelectedTags:', checkedTags);
            verboseLog('Generation request - persistentSelectedTags count:', checkedTags.length);

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
            
            // Extract filename from Content-Disposition header
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'labels.docx'; // Default filename
            
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="([^"]+)"/);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1];
                }
            }
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename; // Set the filename for download
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
            this.isGenerating = false; // Release generation lock
            console.timeEnd('debouncedGenerate');
        }
    }, 2000), // 2-second debounce delay

    updateTagColor(tag, color) {
        // Find the tag element by product name since that's how they're identified
        const productName = tag['Product Name*'] || tag.ProductName || tag.displayName;
        if (!productName) return;
        
        // Find all tag elements robustly without using an attribute selector that may break on quotes
        const candidates = document.querySelectorAll('.tag-item');
        const tagElements = Array.from(candidates).filter(el => {
            const dataName = el.getAttribute('data-tag-name');
            const checkbox = el.querySelector('.tag-checkbox');
            const cbValue = checkbox ? checkbox.value : null;
            if (dataName === productName || cbValue === productName) return true;
            // Fallback to comparing visible name text
            const tagNameElement = el.querySelector('.tag-name, .product-name');
            return tagNameElement && tagNameElement.textContent.trim() === productName;
        });
        
        tagElements.forEach(tagElement => {
            // Check if this is the right tag element by comparing the product name
            const tagNameElement = tagElement.querySelector('.tag-name, .product-name');
            if (tagNameElement && tagNameElement.textContent.trim() === productName) {
                // Update the data-lineage attribute which triggers CSS color changes
                const lineage = tag.Lineage || tag.lineage;
                if (lineage) {
                    tagElement.dataset.lineage = lineage.toUpperCase();
                }
                
                // Also update the color in the tag object
                tag.color = color;
            }
        });
    },

    // Ensure visible tag elements reflect the lineage stored in state.tags
    alignDisplayedLineagesWithTags() {
        const tagMap = new Map();
        (this.state.tags || []).forEach(t => {
            const name = t['Product Name*'] || t.ProductName || t.displayName;
            if (!name) return;
            const lineage = (t.Lineage || t.lineage || '').toString().trim().toUpperCase();
            if (lineage) tagMap.set(name, lineage);
        });

        if (tagMap.size === 0) return;

        const elements = document.querySelectorAll('.tag-item');
        elements.forEach(el => {
            const tagNameEl = el.querySelector('.tag-name, .product-name');
            const checkbox = el.querySelector('.tag-checkbox');
            const name = (tagNameEl && tagNameEl.textContent.trim()) || (checkbox && checkbox.value) || el.getAttribute('data-tag-name');
            if (!name) return;
            const lineage = tagMap.get(name);
            if (!lineage) return;
            // Update dataset lineage to drive CSS
            el.dataset.lineage = lineage;
        });
    },

    forceTagColorUpdate(tag, newLineage) {
        // Find the tag element by product name
        const productName = tag['Product Name*'] || tag.ProductName || tag.displayName;
        if (!productName) return;
        
        // Find all tag elements that might contain this product
        const allTagElements = document.querySelectorAll('.tag-item');
        
        allTagElements.forEach(tagElement => {
            // Check if this tag element contains the product name
            const tagText = tagElement.textContent || '';
            if (tagText.includes(productName)) {
                // Update the data-lineage attribute to trigger CSS color changes
                tagElement.dataset.lineage = newLineage.toUpperCase();
                
                // Force a style recalculation by temporarily modifying and restoring a style
                const originalDisplay = tagElement.style.display;
                tagElement.style.display = 'none';
                tagElement.offsetHeight; // Trigger reflow
                tagElement.style.display = originalDisplay;
                
                verboseLog(`🎨 Updated color for ${productName}: lineage=${newLineage}, data-lineage=${tagElement.dataset.lineage}`);
                
                // Debug: Check if the element actually has the correct data-lineage attribute
                verboseLog(`🔍 Debug: Element found for ${productName}:`, {
                    element: tagElement,
                    dataLineage: tagElement.dataset.lineage,
                    className: tagElement.className,
                    computedStyle: window.getComputedStyle(tagElement).backgroundColor,
                    allAttributes: Array.from(tagElement.attributes).map(attr => `${attr.name}="${attr.value}"`)
                });
            }
        });
    },

    getLineageColor(lineage) {
        // Use the new backend-matching lineage determination logic
        return this.getLineageColorFromOptimizedRules(lineage);
    },

    getLineageColorFromOptimizedRules(inputLineage) {
        // Prefer explicit lineage provided by backend (DB/UI) when valid
        const normalizedInput = (inputLineage || '').toString().trim().toUpperCase();
        
        // Handle sativa hybrid variations - should be sativa-colored
        if (normalizedInput.includes('SATIVA') && normalizedInput.includes('HYBRID')) {
            return 'var(--lineage-sativa)';  // Sativa hybrids use sativa color
        }
        
        const explicitValues = new Set(['SATIVA','INDICA','HYBRID','HYBRID/SATIVA','HYBRID/INDICA','CBD','MIXED']);
        if (explicitValues.has(normalizedInput)) {
            const lineageColors = {
                'SATIVA': 'var(--lineage-sativa)',
                'INDICA': 'var(--lineage-indica)',
                'HYBRID': 'var(--lineage-hybrid)',
                'HYBRID/SATIVA': 'var(--lineage-sativa)',  // Changed to sativa color
                'HYBRID/INDICA': 'var(--lineage-indica)',
                'CBD': 'var(--lineage-cbd)',
                'MIXED': 'var(--lineage-mixed)'
            };
            return lineageColors[normalizedInput] || 'var(--lineage-mixed)';
        }

        // BACKEND RULES IMPLEMENTATION: Match optimized_lineage_assignment() from excel_processor.py when no explicit lineage
        // Get tag data if available for Product Type and Product Strain analysis
        const tagData = this.getCurrentTagData();
        let finalLineage = normalizedInput;
        
        if (tagData) {
            // Use the comprehensive backend rules function
            finalLineage = this.determineLineageFromBackendRules(tagData);
        }
        
        // Apply color mapping based on final determined lineage
        // Handle sativa hybrid variations - should be sativa-colored
        if (finalLineage.includes('SATIVA') && finalLineage.includes('HYBRID')) {
            return 'var(--lineage-sativa)';  // Sativa hybrids use sativa color
        }
        
        const lineageColors = {
            'SATIVA': 'var(--lineage-sativa)',
            'INDICA': 'var(--lineage-indica)',
            'HYBRID': 'var(--lineage-hybrid)',
            'HYBRID/SATIVA': 'var(--lineage-sativa)',  // Changed to sativa color
            'HYBRID/INDICA': 'var(--lineage-indica)',
            'CBD': 'var(--lineage-cbd)',
            'CBD_BLEND': 'var(--lineage-cbd)',
            'MIXED': 'var(--lineage-mixed)',
            'PARAPHERNALIA': 'var(--lineage-para)',
            'PARA': 'var(--lineage-para)'
        };
        
        return lineageColors[finalLineage] || 'var(--lineage-mixed)';
    },

    // Helper function to get current tag data for lineage rules
    getCurrentTagData() {
        // Try to get tag data from various sources
        if (this.currentTag) {
            return this.currentTag;
        }
        
        // Fallback: return null if no tag data available
        return null;
    },

    // Main function to determine lineage using backend rules (optimized_lineage_assignment equivalent)
    determineLineageFromBackendRules(productData) {
        if (!productData) {
            return 'MIXED'; // Default fallback
        }
        
        const productType = (productData['Product Type*'] || productData.Type || '').toString().trim().toLowerCase();
        const productStrain = (productData['Product Strain'] || '').toString().trim();
        const currentLineage = productData.Lineage || productData.lineage || '';
        
        // Define classic types (matching backend CLASSIC_TYPES)
        const classicTypes = [
            'flower', 'pre-roll', 'joint', 'blunt', 'cone', 'preroll',
            'flower - outdoor', 'flower - indoor', 'flower - greenhouse'
        ];
        
        // Check if lineage is empty/invalid (matching backend empty_lineage_mask)
        const isEmptyLineage = !currentLineage || 
                             currentLineage.toString().trim() === '' || 
                             currentLineage.toString().toLowerCase().trim() === 'nan' ||
                             currentLineage === null || 
                             currentLineage === undefined;
        
        const isClassicType = classicTypes.includes(productType);
        const isNonClassicType = !isClassicType;
        
        // BACKEND RULE 1: Set default lineage for classic types with empty lineage (HYBRID)
        if (isClassicType && isEmptyLineage) {
            return 'HYBRID';
        }
        
        // BACKEND RULE 2: Use Product Strain to determine lineage for ALL non-classic types (override existing lineage)
        // UPDATED: Be more conservative with edible CBD lineage assignment
        if (isNonClassicType && productStrain) {
            const strainLower = productStrain.toLowerCase();
            
            if (strainLower.includes('cbd blend') || strainLower.includes('cbd') || strainLower.includes('cbn') || strainLower.includes('cbc') || strainLower.includes('cbg')) {
                return 'CBD_BLEND';
            }
            // Paraphernalia products -> PARAPHERNALIA lineage (pink) - override existing lineage
            else if (strainLower.includes('paraphernalia')) {
                return 'PARAPHERNALIA';
            }
            // Mixed products -> MIXED lineage (blue) - override existing lineage
            else if (strainLower.includes('mixed')) {
                return 'MIXED';
            }
            // Default fallback for non-classic types with empty lineage -> MIXED
            else if (isEmptyLineage) {
                return 'MIXED';
            }
        }
        // BACKEND RULE 3: Fallback if Product Strain doesn't exist - only for empty lineages in non-classic types
        else if (isNonClassicType && isEmptyLineage) {
            return 'MIXED';
        }
        
        // BACKEND RULE 4: Check for CBD content in product name/description (matching backend logic)
        if (isNonClassicType) {
            const productName = (productData['Product Name*'] || productData.ProductName || '').toString().toUpperCase();
            const description = (productData.Description || '').toString().toUpperCase();
            const hasCbdContent = productName.includes('CBD') || productName.includes('CBG') || productName.includes('CBN') || productName.includes('CBC') ||
                                description.includes('CBD') || description.includes('CBG') || description.includes('CBN') || description.includes('CBC');
            
            if (hasCbdContent) {
                return 'CBD_BLEND';
            }
        }
        
        // If we get here, return the current lineage (no changes needed)
        return currentLineage || 'MIXED';
    },

    async moveToSelected() {
        verboseLog('[DEBUG] moveToSelected function called');
        
        // Get checked tags in availableTags
        const checked = Array.from(document.querySelectorAll('#availableTags input[type="checkbox"].tag-checkbox:checked')).map(cb => cb.value);
        verboseLog('[DEBUG] Found checked tags:', checked);
        
        if (checked.length === 0) {
            console.error('No tags selected to move');
            return;
        }
        
        try {
            // Show action splash for better UX
            this.showActionSplash('Moving tags to selected...');
            
            // Add tags to persistent selected tags (independent of filters)
            checked.forEach(tagName => {
                // Ensure persistentSelectedTags is an array
                if (!Array.isArray(this.state.persistentSelectedTags)) {
                    this.state.persistentSelectedTags = [];
                }
                if (!this.state.persistentSelectedTags.includes(tagName)) {
                    this.state.persistentSelectedTags.push(tagName);
                }
            });
            
            // Update the regular selectedTags set to match persistent ones
            this.state.selectedTags = new Set(this.state.persistentSelectedTags);
            
            // Get the full tag objects for the selected tags - optimized with Map for O(1) lookup
            const tagsMap = new Map(this.state.tags.map(t => [t['Product Name*'], t]));
            const originalTagsMap = new Map(this.state.originalTags.map(t => [t['Product Name*'], t]));
            
            const selectedTagObjects = Array.from(this.state.persistentSelectedTags).map(name => {
                // Safety check: ensure name is valid
                if (!name || typeof name !== 'string') {
                    console.warn('Invalid name in persistentSelectedTags:', name);
                    return null;
                }
                
                // O(1) lookup instead of O(n) find operation
                return tagsMap.get(name) || originalTagsMap.get(name);
            }).filter(Boolean);
            
            // Update the selected tags display
            this.updateSelectedTags(selectedTagObjects);
            
            // Hide selected tags from available tags display for better performance - batched DOM operations
            const availableTagsContainer = document.getElementById('availableTags');
            if (availableTagsContainer) {
                // FIXED: Don't hide selected tags from available display - keep all items visible
                // This allows users to see all available options even after making selections
                verboseLog('FIXED: Not hiding selected tags from available display - keeping all items visible');
                // All tags remain visible in available list even after selection
            }
            
            // Make API call to backend to persist the changes - non-blocking for better performance
            verboseLog('[DEBUG] Making API call to /api/move-tags with direction: to_selected');
            verboseLog('[DEBUG] Tags being moved:', checked);
            verboseLog('[DEBUG] Current persistent selected tags before move:', this.state.persistentSelectedTags);
            
            // Fire and forget API call for better performance
            fetch('/api/move-tags', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tags: checked,
                    direction: 'to_selected'
                })
            }).then(response => {
                verboseLog('[DEBUG] API response status:', response.status);
                if (!response.ok) {
                    console.error('Failed to sync with backend:', response.statusText);
                } else {
                    verboseLog('Successfully synced with backend');
                }
            }).catch(error => {
                console.error('Failed to sync with backend:', error);
            });
            
            // Successfully moved tags to selected
            verboseLog(`Moved ${checked.length} tags to selected list. Total selected: ${this.state.persistentSelectedTags.length}`);
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
        verboseLog('[DEBUG] moveToAvailable function called');
        
        // Get checked tags in selectedTags
        const checked = Array.from(document.querySelectorAll('#selectedTags input[type="checkbox"].tag-checkbox:checked')).map(cb => cb.value);
        verboseLog('[DEBUG] Found checked tags:', checked);
        
        if (checked.length === 0) {
            console.error('No tags selected to move');
            return;
        }
        
        // Prevent multiple simultaneous operations
        if (this.isMovingTags) {
            verboseLog('[DEBUG] Already moving tags, ignoring request');
            return;
        }
        
        this.isMovingTags = true;
        
        try {
            // Show action splash for better UX
            this.showActionSplash('Moving tags to available...');
            
            // Store original state for rollback if needed
            const originalPersistentTags = [...this.state.persistentSelectedTags];
            
            // Remove tags from persistent selected tags
            checked.forEach(tagName => {
                // Ensure persistentSelectedTags is an array
                if (!Array.isArray(this.state.persistentSelectedTags)) {
                    this.state.persistentSelectedTags = [];
                }
                const index = this.state.persistentSelectedTags.indexOf(tagName);
                if (index > -1) {
                    this.state.persistentSelectedTags.splice(index, 1);
                }
            });
            
            // Update the regular selectedTags set to match persistent ones
            this.state.selectedTags = new Set(this.state.persistentSelectedTags);
            
            // Get the full tag objects for the remaining selected tags - optimized with Map for O(1) lookup
            const tagsMap = new Map(this.state.tags.map(t => [t['Product Name*'], t]));
            const originalTagsMap = new Map(this.state.originalTags.map(t => [t['Product Name*'], t]));
            
            const selectedTagObjects = Array.from(this.state.persistentSelectedTags).map(name => {
                // Safety check: ensure name is valid
                if (!name || typeof name !== 'string') {
                    console.warn('Invalid name in persistentSelectedTags:', name);
                    return null;
                }
                
                // O(1) lookup instead of O(n) find operation
                return tagsMap.get(name) || originalTagsMap.get(name);
            }).filter(Boolean);
            
            // Update the selected tags display
            this.updateSelectedTags(selectedTagObjects);
            
            // Get the tag objects for the moved back tags and add them to available tags - optimized with Map
            const movedBackTags = checked.map(tagName => originalTagsMap.get(tagName)).filter(Boolean);
            
            // Show moved back tags in available tags display for better performance - batched DOM operations
            const availableTagsContainer = document.getElementById('availableTags');
            if (availableTagsContainer) {
                const tagElementsToShow = checked.map(tagName => 
                    availableTagsContainer.querySelector(`.tag-checkbox[value="${tagName}"]`)?.closest('.tag-item')
                ).filter(Boolean);
                
                // Batch DOM updates
                tagElementsToShow.forEach(tagItem => {
                    tagItem.style.display = 'block';
                });
            }
            
            // Make API call to backend to persist the changes - non-blocking for better performance
            verboseLog('[DEBUG] Making API call to /api/move-tags with direction: to_available');
            verboseLog('[DEBUG] Tags being moved:', checked);
            verboseLog('[DEBUG] Current persistent selected tags before move:', this.state.persistentSelectedTags);
            
            // Fire and forget API call for better performance
            fetch('/api/move-tags', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tags: checked,
                    direction: 'to_available'
                })
            }).then(response => {
                verboseLog('[DEBUG] API response status:', response.status);
                if (!response.ok) {
                    console.error('Failed to sync with backend:', response.statusText);
                    // Rollback to original state if backend call failed
                    this.state.persistentSelectedTags = originalPersistentTags;
                    this.state.selectedTags = new Set(originalPersistentTags);
                    
                    // Revert the UI to show the original selected tags
                    const originalSelectedTagObjects = originalPersistentTags.map(name => originalTagsMap.get(name)).filter(Boolean);
                    this.updateSelectedTags(originalSelectedTagObjects);
                    
                    // Show error message to user
                    Toast.show('error', 'Failed to deselect tags. Please try again.');
                } else {
                    verboseLog('Successfully synced with backend');
                }
                        }).catch(error => {
                console.error('Failed to sync with backend:', error);
                // Rollback to original state if backend call failed
                this.state.persistentSelectedTags = originalPersistentTags;
                this.state.selectedTags = new Set(originalPersistentTags);
                
                // Revert the UI to show the original selected tags
                const originalSelectedTagObjects = originalPersistentTags.map(name => originalTagsMap.get(name)).filter(Boolean);
                this.updateSelectedTags(originalSelectedTagObjects);
                
                // Show error message to user
                Toast.show('error', 'Failed to deselect tags. Please try again.');
            });
            
            // Successfully moved tags to available
            verboseLog(`Moved ${checked.length} tags to available list. Total selected: ${this.state.persistentSelectedTags.length}`);
        } catch (error) {
            console.error('Failed to move tags:', error.message);
            // Rollback to original state if there was an error
            if (originalPersistentTags) {
                this.state.persistentSelectedTags = originalPersistentTags;
                this.state.selectedTags = new Set(originalPersistentTags);
                
                const originalSelectedTagObjects = originalPersistentTags.map(name => originalTagsMap.get(name)).filter(Boolean);
                this.updateSelectedTags(originalSelectedTagObjects);
            }
            
            Toast.show('error', 'Failed to deselect tags. Please try again.');
        } finally {
            // Reset the moving flag
            this.isMovingTags = false;
            
            // Hide action splash
            setTimeout(() => {
                this.hideActionSplash();
            }, 300);
        }
    },

    async undoMove() {
        try {
            verboseLog('Starting undo operation...');
            // Show loading splash
            this.showActionSplash('Undoing last action...');
            
            // Call the backend API to undo the last move
            const response = await fetch('/api/undo-move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            verboseLog('Undo API response status:', response.status);
            
            if (response.ok) {
                const data = await response.json();
                verboseLog('Undo API response data:', data);
                
                if (data.success) {
                    // Update the persistent selected tags with the restored state
                    this.state.persistentSelectedTags = data.selected_tags;
                    this.state.selectedTags = new Set(data.selected_tags);
                    
                    // Update the selected tags display immediately
                    this.updateSelectedTags(data.selected_tags.map(tagName => 
                        this.state.tags.find(t => t['Product Name*'] === tagName)
                    ).filter(Boolean));
                    
                    // Update available tags with optimized approach
                    this.updateAvailableTagsOptimized(data.available_tags);
                    
                    verboseLog('Undo completed - restored previous state');
                    
                    // Show success message
                    if (window.Toast) {
                        Toast.show('success', 'Undo completed successfully');
                    }
                } else {
                    console.error('Failed to undo move:', data.error);
                    if (window.Toast) {
                        Toast.show('error', `Undo failed: ${data.error}`);
                    }
                }
            } else {
                const errorData = await response.json();
                verboseLog('Undo API error response:', errorData);
                
                if (response.status === 400 && errorData.error === 'No undo history available') {
                    verboseLog('Nothing to undo');
                    if (window.Toast) {
                        Toast.show('info', 'No actions to undo. Try moving some tags first, then use the undo button.');
                    } else {
                        // Fallback if Toast is not available
                        alert('No actions to undo. Try moving some tags first, then use the undo button.');
                    }
                } else {
                    console.error('Failed to undo move on server:', errorData.error);
                    if (window.Toast) {
                        Toast.show('error', `Undo failed: ${errorData.error}`);
                    } else {
                        // Fallback if Toast is not available
                        alert(`Undo failed: ${errorData.error}`);
                    }
                }
            }
        } catch (error) {
            console.error('Failed to undo move:', error.message);
            if (window.Toast) {
                Toast.show('error', `Undo failed: ${error.message}`);
            } else {
                // Fallback if Toast is not available
                alert(`Undo failed: ${error.message}`);
            }
        } finally {
            // Hide loading splash
            this.hideActionSplash();
        }
    },

    async clearSelected() {
        // Prevent multiple simultaneous calls
        if (this.state.isClearing) {
            verboseLog('⚠️ Clear operation already in progress, ignoring duplicate call');
            return;
        }
        
        this.state.isClearing = true;
        this.clearAvailableTagsCache();
        
        try {
            verboseLog('🔄 Clearing selected tags and performing full app reset...');
            
            // Show loading feedback
            this.showActionSplash('Clearing and resetting...');

            // Clear search inputs without nuking the entire DOM
            this.resetSearchInputs();
            
            // Call the backend API to clear selected tags
            let response;
            try {
                response = await fetch('/api/clear-filters', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
            } catch (fetchError) {
                console.error('Network error clearing filters:', fetchError);
                // Continue with local clearing even if API fails
                response = null;
            }
            
            if (response && response.ok) {
                try {
                    const data = await response.json();
                    verboseLog('Backend clear-filters response:', data);
                } catch (jsonError) {
                    console.error('Error parsing response:', jsonError);
                }
            } else if (response) {
                console.error('Failed to clear selected tags on server:', response.status, response.statusText);
            }
            
            // Clear persistent selected tags
            if (this.state) {
                if (Array.isArray(this.state.persistentSelectedTags)) {
                    this.state.persistentSelectedTags = [];
                }
                if (this.state.selectedTags && typeof this.state.selectedTags.clear === 'function') {
                    this.state.selectedTags.clear();
                }
            }
            
            // Update the selected tags display immediately
            if (this.updateSelectedTags) {
                try {
                    this.updateSelectedTags([]);
                } catch (updateError) {
                    console.error('Error updating selected tags display:', updateError);
                }
            }
            
            // PERFORMANCE: Clear checkboxes in batches without dispatching events to prevent UI freeze
            // Event handlers check isClearing flag, so no need to dispatch events
            try {
                const availableCheckboxes = document.querySelectorAll('#availableTags input[type="checkbox"]');
                const batchSize = 100; // Process 100 checkboxes at a time
                
                // Clear checkboxes in batches to prevent blocking UI
                const clearBatch = (index) => {
                    const end = Math.min(index + batchSize, availableCheckboxes.length);
                    for (let i = index; i < end; i++) {
                        availableCheckboxes[i].checked = false;
                    }
                    
                    if (end < availableCheckboxes.length) {
                        // Process next batch in next frame to avoid blocking
                        requestAnimationFrame(() => clearBatch(end));
                    } else {
                        // All checkboxes cleared, now clear selected tags
                        requestAnimationFrame(() => {
                            const selectedCheckboxes = document.querySelectorAll('#selectedTags input[type="checkbox"]');
                            selectedCheckboxes.forEach(checkbox => {
                                checkbox.checked = false;
                            });
                            
                            // Show all available tags in next frame
                            requestAnimationFrame(() => {
                                try {
                                    const availableTagItems = document.querySelectorAll('#availableTags .tag-item');
                                    // Use display style in batch
                                    const tagBatchSize = 200;
                                    const showBatch = (tagIndex) => {
                                        const tagEnd = Math.min(tagIndex + tagBatchSize, availableTagItems.length);
                                        for (let i = tagIndex; i < tagEnd; i++) {
                                            availableTagItems[i].style.display = 'block';
                                        }
                                        if (tagEnd < availableTagItems.length) {
                                            requestAnimationFrame(() => showBatch(tagEnd));
                                        }
                                    };
                                    showBatch(0);
                                } catch (displayError) {
                                    console.error('Error showing available tags:', displayError);
                                }
                            });
                        });
                    }
                };
                
                if (availableCheckboxes.length > 0) {
                    clearBatch(0);
                } else {
                    // No checkboxes to clear, proceed directly
                    const selectedCheckboxes = document.querySelectorAll('#selectedTags input[type="checkbox"]');
                    selectedCheckboxes.forEach(checkbox => {
                        checkbox.checked = false;
                    });
                }
            } catch (checkboxError) {
                console.error('Error clearing checkboxes:', checkboxError);
            }
            
            // Clear filter cache to ensure fresh data
            if (this.state) {
                this.state.filterCache = null;
            }
            
            // PERFORMANCE: Defer expensive operations to avoid blocking UI during clear
            // Use requestAnimationFrame to batch these operations after checkbox clearing completes
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    // Update available tags display to reflect cleared state
                    if (this.efficientlyUpdateAvailableTagsDisplay) {
                        try {
                            this.efficientlyUpdateAvailableTagsDisplay();
                        } catch (updateError) {
                            console.error('Error updating available tags display:', updateError);
                        }
                    }
                    
                    // Update select all checkboxes to unchecked state
                    if (this.updateSelectAllCheckboxes) {
                        try {
                            this.updateSelectAllCheckboxes();
                        } catch (updateError) {
                            console.error('Error updating select all checkboxes:', updateError);
                        }
                    }
                    
                    // Also clear filters (non-blocking)
                    if (this.clearAllFilters) {
                        this.clearAllFilters().catch(filterError => {
                            console.error('Error clearing filters:', filterError);
                        });
                    }
                });
            });
            
            verboseLog('✅ Selected tags cleared and app reset completed successfully');
            
            // Show success message
            if (window.Toast && window.Toast.show) {
                window.Toast.show('success', 'Cleared and reset successfully', { duration: 2000 });
            }
            
        } catch (error) {
            console.error('Failed to clear selected tags:', error);
            // Show error message
            if (window.Toast && window.Toast.show) {
                window.Toast.show('error', `Failed to clear: ${error.message}`, { duration: 5000 });
            } else {
                alert(`Failed to clear and reset: ${error.message}`);
            }
        } finally {
            // Hide loading splash
            this.hideActionSplash();
            // Reset the clearing flag
            this.state.isClearing = false;
        }
    },

    showExcelLoadingSplash(filename) {
        verboseLog('🎬 SHOWING EXCEL SPLASH for:', filename);
        const splash = document.getElementById('excelLoadingSplash');
        const filenameElement = document.getElementById('excelLoadingFilename');
        const statusElement = document.getElementById('excelLoadingStatus');
        
        if (splash && filenameElement && statusElement) {
            verboseLog('✅ Splash elements found, displaying...');
            filenameElement.textContent = filename;
            statusElement.textContent = 'Processing...';
            splash.style.display = 'flex';
            splash.style.zIndex = '99999';
            splash.style.position = 'fixed';
            splash.style.top = '0';
            splash.style.left = '0';
            splash.style.width = '100%';
            splash.style.height = '100%';
            verboseLog('✅ Splash display set to:', splash.style.display);
        } else {
            console.error('❌ Could not find splash elements:', {
                splash: !!splash,
                filenameElement: !!filenameElement,
                statusElement: !!statusElement
            });
        }
    },

    hideExcelLoadingSplash() {
        verboseLog('🎬 HIDING EXCEL SPLASH');
        const splash = document.getElementById('excelLoadingSplash');
        
        if (splash) {
            // Hide splash immediately
            splash.style.display = 'none';
            verboseLog('✅ Splash hidden');
        } else {
            console.error('❌ Could not find splash element to hide');
        }
    },

    updateExcelLoadingStatus(status) {
        const statusElement = document.getElementById('excelLoadingStatus');
        if (statusElement) {
            statusElement.textContent = status;
        }
    },

    showUploadSuccessSplash(rows) {
        // Hide the excel loading splash first
        const oldSplash = document.getElementById('excelLoadingSplash');
        if (oldSplash) {
            oldSplash.style.display = 'none';
        }

        // Create or get the success splash modal
        let successSplash = document.getElementById('uploadSuccessSplash');
        
        if (!successSplash) {
            successSplash = document.createElement('div');
            successSplash.id = 'uploadSuccessSplash';
            successSplash.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                display: none;
                justify-content: center;
                align-items: center;
                z-index: 9999;
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
            `;
            document.body.appendChild(successSplash);
        }
        
        // Set content with cool success design
        successSplash.innerHTML = `
            <div style="position: relative; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center;">
                <div class="success-background-pattern"></div>
                
                <div id="success-splash-container" style="position: relative; width: 500px; height: 400px; border-radius: 24px; overflow: hidden; background: linear-gradient(135deg, rgba(40, 167, 69, 0.95), rgba(76, 175, 80, 0.95)); border: 1px solid rgba(255, 255, 255, 0.3); box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.1), 0 0 40px rgba(76, 175, 80, 0.4); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); z-index: 2;">
                    <div class="success-content" style="position: relative; width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 40px; color: white; text-align: center;">
                        <div class="success-icon-container" style="position: relative; margin-bottom: 20px;">
                            <div class="success-checkmark" style="width: 80px; height: 80px; background: rgba(255, 255, 255, 0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 40px; box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.2); animation: success-bounce 0.6s ease-in-out;">
                                ✓
                            </div>
                        </div>
                        
                        <h1 style="color: #fff; font-weight: 900; letter-spacing: 2px; font-size: 2rem; margin-bottom: 12px; text-shadow: 0 4px 12px rgba(0,0,0,0.3), 0 2px 4px rgba(255,255,255,0.2);">UPLOAD SUCCESSFUL!</h1>
                        <p style="color: rgba(255, 255, 255, 0.95); font-size: 1.1rem; font-weight: 600; letter-spacing: 1px; margin-bottom: 15px; text-shadow: 0 2px 8px rgba(0,0,0,0.3);">${rows || 0} rows processed</p>
                        
                        <div class="success-info" style="width: 100%; max-width: 300px; margin: 20px 0;">
                            <div style="font-size: 0.9rem; font-weight: 500; opacity: 0.9; margin-bottom: 12px; text-shadow: 0 2px 6px rgba(0,0,0,0.2);">Reloading page to display new data...</div>
                            <div class="success-progress-bar" style="width: 100%; height: 6px; background: rgba(255, 255, 255, 0.2); border-radius: 3px; overflow: hidden;">
                                <div class="success-progress-fill" style="height: 100%; background: rgba(255, 255, 255, 0.9); border-radius: 3px; animation: success-progress 2s ease-in-out;"></div>
                            </div>
                        </div>
                        
                        <div class="success-dots" style="display: flex; gap: 6px; justify-content: center; margin-top: 20px;">
                            <div class="dot" style="width: 6px; height: 6px; border-radius: 50%; background: rgba(255, 255, 255, 0.8); animation: dot-pulse 1.4s ease-in-out infinite both;"></div>
                            <div class="dot" style="width: 6px; height: 6px; border-radius: 50%; background: rgba(255, 255, 255, 0.8); animation: dot-pulse 1.4s ease-in-out infinite both; animation-delay: -0.18s;"></div>
                            <div class="dot" style="width: 6px; height: 6px; border-radius: 50%; background: rgba(255, 255, 255, 0.8); animation: dot-pulse 1.4s ease-in-out infinite both; animation-delay: -0.36s;"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <style>
                .success-background-pattern {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: radial-gradient(circle at 20% 50%, rgba(76, 175, 80, 0.1), transparent 50%),
                                radial-gradient(circle at 80% 80%, rgba(40, 167, 69, 0.1), transparent 50%),
                                radial-gradient(circle at 40% 20%, rgba(76, 175, 80, 0.05), transparent 50%);
                    animation: success-pattern-shift 8s ease-in-out infinite;
                }
                
                @keyframes success-pattern-shift {
                    0%, 100% { transform: translate(0, 0); }
                    50% { transform: translate(20px, 20px); }
                }
                
                @keyframes success-bounce {
                    0% { transform: scale(0) rotate(-180deg); opacity: 0; }
                    50% { transform: scale(1.2) rotate(10deg); }
                    70% { transform: scale(0.95) rotate(-5deg); }
                    100% { transform: scale(1) rotate(0deg); opacity: 1; }
                }
                
                @keyframes success-progress {
                    0% { width: 0%; }
                    100% { width: 100%; }
                }
                
                @keyframes dot-pulse {
                    0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
                    40% { transform: scale(1.2); opacity: 1; }
                }
                
                @keyframes status-pulse {
                    0%, 100% { opacity: 1; transform: scale(1); }
                    50% { opacity: 0.5; transform: scale(0.8); }
                }
            </style>
        `;
        
        // Show the splash
        successSplash.style.display = 'flex';
        
        // Auto-hide and reload after animation
        setTimeout(() => {
            if (successSplash) {
                successSplash.style.display = 'none';
            }
        }, 2200);
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

    showEnhancedGenerationSplash(labelCount, templateType, retryCount = 0) {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.showEnhancedGenerationSplash(labelCount, templateType, retryCount);
            });
            return;
        }
        
        const splashModal = document.getElementById('generationSplashModal');
        
        if (!splashModal) {
            console.error('Generation splash modal not found');
            return;
        }
        
        // Show centered, noticeable but clean notification
        splashModal.style.display = 'flex';
        splashModal.style.alignItems = 'center';
        splashModal.style.justifyContent = 'center';
        splashModal.style.padding = '0';
        splashModal.style.pointerEvents = 'auto';
        
        splashModal.innerHTML = `
            <div style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.6);
                backdrop-filter: blur(8px);
                -webkit-backdrop-filter: blur(8px);
                animation: fadeIn 0.2s ease-out;
            " onclick="event.target === this && TagManager.hideEnhancedGenerationSplash()">
                <div style="
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background: rgba(45, 34, 58, 0.95);
                    -webkit-backdrop-filter: blur(20px);
                    backdrop-filter: blur(20px);
                    border: 1px solid rgba(160, 132, 232, 0.3);
                    border-radius: 15px;
                    padding: 36px 42px;
                    min-width: 420px;
                    max-width: 480px;
                    box-shadow: 
                        0 20px 60px rgba(0, 0, 0, 0.5),
                        0 0 0 1px rgba(160, 132, 232, 0.1);
                    animation: scaleIn 0.3s ease-out;
                    color: #ffffff;
                " onclick="event.stopPropagation()">
                    
                    <div style="display: flex; align-items: center; gap: 18px; margin-bottom: 28px;">
                        <div class="spinner" style="
                            width: 36px;
                            height: 36px;
                            border: 3px solid rgba(160, 132, 232, 0.2);
                            border-top-color: #00d4aa;
                            border-radius: 50%;
                            animation: spin 0.8s linear infinite;
                            flex-shrink: 0;
                        "></div>
                        <div style="flex: 1;">
                            <h2 style="
                                font-size: 22px;
                                font-weight: 600;
                                color: #ffffff;
                                margin: 0 0 8px 0;
                                letter-spacing: 0.3px;
                            ">Generating Labels</h2>
                            <div id="status-text" style="
                                font-size: 14px;
                                color: rgba(255, 255, 255, 0.7);
                                transition: opacity 0.2s ease;
                                font-weight: 400;
                            ">Preparing templates...</div>
                        </div>
                    </div>
                    
                    <div style="
                        background: linear-gradient(135deg, rgba(160, 132, 232, 0.15), rgba(0, 212, 170, 0.1));
                        border: 1px solid rgba(160, 132, 232, 0.2);
                        border-radius: 12px;
                        padding: 20px 24px;
                        margin-bottom: 24px;
                    ">
                        <div style="
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            gap: 24px;
                        ">
                            <div>
                                <div style="font-size: 11px; color: rgba(255, 255, 255, 0.6); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 500;">Labels</div>
                                <div style="font-size: 20px; font-weight: 600; color: #00d4aa;">${labelCount}</div>
                            </div>
                            <div style="width: 1px; height: 36px; background: rgba(160, 132, 232, 0.3);"></div>
                            <div>
                                <div style="font-size: 11px; color: rgba(255, 255, 255, 0.6); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 500;">Template</div>
                                <div style="font-size: 20px; font-weight: 600; color: #00d4aa; text-transform: capitalize;">${templateType}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="
                        width: 100%;
                        height: 5px;
                        background: rgba(160, 132, 232, 0.2);
                        border-radius: 3px;
                        overflow: hidden;
                        margin-bottom: 24px;
                    ">
                        <div style="
                            height: 100%;
                            background: linear-gradient(90deg, #00d4aa, #a084e8, #00d4aa);
                            border-radius: 3px;
                            animation: progress 2s ease-in-out infinite;
                            box-shadow: 0 0 10px rgba(0, 212, 170, 0.5);
                        "></div>
                    </div>
                    
                    <button onclick="TagManager.hideEnhancedGenerationSplash()" style="
                        width: 100%;
                        background: rgba(160, 132, 232, 0.15);
                        border: 1px solid rgba(160, 132, 232, 0.3);
                        color: rgba(255, 255, 255, 0.9);
                        padding: 11px;
                        border-radius: 8px;
                        font-size: 13px;
                        font-weight: 500;
                        cursor: pointer;
                        transition: all 0.2s ease;
                    " onmouseover="this.style.background='rgba(160, 132, 232, 0.25)'; this.style.borderColor='rgba(160, 132, 232, 0.5)'; this.style.color='#ffffff'" onmouseout="this.style.background='rgba(160, 132, 232, 0.15)'; this.style.borderColor='rgba(160, 132, 232, 0.3)'; this.style.color='rgba(255, 255, 255, 0.9)'">
                        Cancel
                    </button>
                </div>
            </div>
            
            <style>
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                
                @keyframes scaleIn {
                    from {
                        transform: translate(-50%, -50%) scale(0.9);
                        opacity: 0;
                    }
                    to {
                        transform: translate(-50%, -50%) scale(1);
                        opacity: 1;
                    }
                }
                
                @keyframes progress {
                    0% { width: 0%; }
                    50% { width: 100%; }
                    100% { width: 0%; }
                }
            </style>
        `;
        
        // Start animated status text
        const statusTexts = [
            'Preparing templates...',
            'Processing data...',
            'Generating labels...',
            'Applying formatting...',
            'Finalizing output...'
        ];
        
        let textIndex = 0;
        const statusTextElement = splashModal.querySelector('#status-text');
        
        const updateStatusText = () => {
            if (statusTextElement) {
                statusTextElement.style.opacity = '0';
                setTimeout(() => {
                    statusTextElement.textContent = statusTexts[textIndex];
                    statusTextElement.style.opacity = '1';
                    textIndex = (textIndex + 1) % statusTexts.length;
                }, 200);
            }
        };
        
        // Update text every 2 seconds
        this._loadingTextInterval = setInterval(updateStatusText, 2000);
        updateStatusText(); // Start immediately
    },

    hideEnhancedGenerationSplash() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.hideEnhancedGenerationSplash();
            });
            return;
        }
        
        // Clear the loading text interval
        if (this._loadingTextInterval) {
            clearInterval(this._loadingTextInterval);
            this._loadingTextInterval = null;
        }
        
        const splashModal = document.getElementById('generationSplashModal');
        if (splashModal) {
            splashModal.style.display = 'none';
            verboseLog('Generation splash hidden successfully');
        } else {
            console.warn('Generation splash modal not found when trying to hide');
        }
    },

    showSimpleGenerationSplash(labelCount, templateType) {
        const splashModal = document.getElementById('generationSplashModal');
        if (!splashModal) {
            console.error('Cannot show simple splash - modal not found');
            return;
        }
        
        // Show a simple text-based splash
        splashModal.style.display = 'flex';
        splashModal.innerHTML = `
            <div style="display: flex; justify-content: center; align-items: center; width: 100%; height: 100%;">
            <div class="generation-splash-popup" style="background: rgba(22, 33, 62, 0.95); border-radius: 24px; padding: 40px; text-align: center; color: white; border: 1px solid rgba(0, 212, 170, 0.2); box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(0, 212, 170, 0.1);">
                <h1 style="color: #fff; font-weight: 900; letter-spacing: 3px; font-size: 2.5rem; margin-bottom: 12px; text-shadow: 0 4px 12px rgba(0,0,0,0.5), 0 6px 20px rgba(0,0,0,0.4), 0 2px 4px rgba(160,132,232,0.4), 0 0 30px rgba(160,132,232,0.3); filter: drop-shadow(0 6px 12px rgba(0,0,0,0.4));">AGT DESIGNER</h1>
                <p style="color: #fff; font-size: 1.2rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 20px; text-shadow: 0 3px 8px rgba(0,0,0,0.5), 0 4px 16px rgba(0,0,0,0.4), 0 2px 4px rgba(139,92,246,0.4), 0 0 20px rgba(139,92,246,0.3); filter: drop-shadow(0 3px 6px rgba(0,0,0,0.4));">AUTO-GENERATING TAG DESIGNER</p>
                <p style="margin-bottom: 15px;">Generating Labels...</p>
                <p style="margin-bottom: 15px;">Template: ${templateType.toUpperCase()}</p>
                <p style="margin-bottom: 20px;">Labels: ${labelCount}</p>
                <p style="font-size: 1rem; color: rgba(255, 255, 255, 0.8); margin-top: 0.5rem; font-weight: 500; letter-spacing: 1px; text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5), 0 1px 2px rgba(160,132,232,0.3); opacity: 0.9; margin-bottom: 20px;">©2025 Created by Adam Cordova for A Greener Today</p>
                <div style="margin: 20px 0;">
                    <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                        <div style="width: 100%; height: 100%; background: linear-gradient(90deg, #00d4aa, #0099cc); border-radius: 3px; animation: progress 2s ease-in-out infinite;"></div>
                    </div>
                </div>
                <button onclick="TagManager.hideEnhancedGenerationSplash()" style="background: rgba(220, 53, 69, 0.8); border: 1px solid rgba(220, 53, 69, 0.8); color: white; padding: 8px 16px; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.3s ease; margin-top: 15px;" onmouseover="this.style.background='rgba(220, 53, 69, 1)'; this.style.transform='scale(1.05)'" onmouseout="this.style.background='rgba(220, 53, 69, 0.8)'; this.style.transform='scale(1)'">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 6px; vertical-align: middle;">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
                Exit Generation
                </button>
                <style>
                    @keyframes progress { 0% { width: 0%; } 50% { width: 100%; } 100% { width: 0%; } }
                </style>
                </div>
            </div>
        `;
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
            // CRITICAL FIX: Don't filter out JSON matched tags from available tags
            // FIXED: Don't filter out selected tags - keep all items visible in available list
            // This allows users to see all available options even after making selections
            verboseLog('FIXED: Not filtering out selected tags - keeping all items visible in available list');
            
            // Update state with all available tags (no filtering)
            this.state.tags = [...availableTags];
            
            // Rebuild the available tags display with all tags visible
            this._updateAvailableTags(this.state.originalTags, availableTags);
            
            console.timeEnd('updateAvailableTagsOptimized');
            
            // Hide splash after a short delay
            setTimeout(() => {
                this.hideActionSplash();
            }, 50);
        });
    },

    // Efficient helper to update available tags display without DOM rebuilding
    efficientlyUpdateAvailableTagsDisplay() {
        // FIXED: Don't hide selected tags from available display - keep all items visible
        // This allows users to see all available options even after making selections
        verboseLog('FIXED: Not hiding selected tags from available display - keeping all items visible');
        
        const availableTagElements = document.querySelectorAll('#availableTags .tag-item');
        
        // Show all tags regardless of selection status
        availableTagElements.forEach(tagElement => {
            tagElement.style.display = 'block';
        });
        
        // Update select all checkboxes state
        this.updateSelectAllCheckboxes();
    },

    // Update select all checkboxes state
    updateSelectAllCheckboxes() {
        // CRITICAL: First sync all available tag checkboxes with persistentSelectedTags state
        const availableCheckboxes = document.querySelectorAll('#availableTags .tag-checkbox');
        availableCheckboxes.forEach(checkbox => {
            const tagName = checkbox.value;
            const shouldBeChecked = this.state.persistentSelectedTags.includes(tagName);
            if (checkbox.checked !== shouldBeChecked) {
                checkbox.checked = shouldBeChecked;
            }
        });
        
        // FIXED: Don't filter out hidden elements since we're not hiding any elements anymore
        const checkedCheckboxes = document.querySelectorAll('#availableTags .tag-checkbox:checked');
        
        // Update global select all for available tags
        const selectAllAvailable = document.getElementById('selectAllAvailable');
        if (selectAllAvailable && availableCheckboxes.length > 0) {
            selectAllAvailable.checked = checkedCheckboxes.length === availableCheckboxes.length;
            selectAllAvailable.indeterminate = checkedCheckboxes.length > 0 && checkedCheckboxes.length < availableCheckboxes.length;
        }
        
        // Update selected tags select all checkbox
        const selectedCheckboxes = document.querySelectorAll('#selectedTags .tag-checkbox');
        const selectedChecked = document.querySelectorAll('#selectedTags .tag-checkbox:checked');
        const selectAllSelected = document.getElementById('selectAllSelected');
        
        if (selectAllSelected && selectedCheckboxes.length > 0) {
            selectAllSelected.checked = selectedChecked.length === selectedCheckboxes.length;
            selectAllSelected.indeterminate = selectedChecked.length > 0 && selectedChecked.length < selectedCheckboxes.length;
        }
        
        // Update vendor and brand select all checkboxes for available tags
        const vendorSections = document.querySelectorAll('#availableTags .vendor-section');
        vendorSections.forEach(vendorSection => {
            const vendorCheckboxes = vendorSection.querySelectorAll('.tag-checkbox');
            const vendorChecked = vendorSection.querySelectorAll('.tag-checkbox:checked');
            const vendorSelectAll = vendorSection.querySelector('.select-all-checkbox');
            
            if (vendorSelectAll && vendorCheckboxes.length > 0) {
                vendorSelectAll.checked = vendorChecked.length === vendorCheckboxes.length;
                vendorSelectAll.indeterminate = vendorChecked.length > 0 && vendorChecked.length < vendorCheckboxes.length;
            }
        });
        
        const brandSections = document.querySelectorAll('#availableTags .brand-section');
        brandSections.forEach(brandSection => {
            const brandCheckboxes = brandSection.querySelectorAll('.tag-checkbox');
            const brandChecked = brandSection.querySelectorAll('.tag-checkbox:checked');
            const brandSelectAll = brandSection.querySelector('.select-all-checkbox');
            
            if (brandSelectAll && brandCheckboxes.length > 0) {
                brandSelectAll.checked = brandChecked.length === brandCheckboxes.length;
                brandSelectAll.indeterminate = brandChecked.length > 0 && brandChecked.length < brandCheckboxes.length;
            }
        });
        
        // Update product type checkboxes
        const productTypeSections = document.querySelectorAll('#availableTags .product-type-section');
        productTypeSections.forEach(productTypeSection => {
            const productTypeTagCheckboxes = productTypeSection.querySelectorAll('.tag-checkbox');
            const productTypeChecked = productTypeSection.querySelectorAll('.tag-checkbox:checked');
            const productTypeSelectAll = productTypeSection.querySelector('.select-all-checkbox');
            
            if (productTypeSelectAll && productTypeTagCheckboxes.length > 0) {
                productTypeSelectAll.checked = productTypeChecked.length === productTypeTagCheckboxes.length;
                productTypeSelectAll.indeterminate = productTypeChecked.length > 0 && productTypeChecked.length < productTypeTagCheckboxes.length;
            }
        });
        
        // Update subcategory checkboxes
        const subcategorySections = document.querySelectorAll('#availableTags .subcategory-section');
        subcategorySections.forEach(subcategorySection => {
            const subcategoryTagCheckboxes = subcategorySection.querySelectorAll('.tag-checkbox');
            const subcategoryChecked = subcategorySection.querySelectorAll('.tag-checkbox:checked');
            const subcategorySelectAll = subcategorySection.querySelector('.select-all-checkbox');
            
            if (subcategorySelectAll && subcategoryTagCheckboxes.length > 0) {
                subcategorySelectAll.checked = subcategoryChecked.length === subcategoryTagCheckboxes.length;
                subcategorySelectAll.indeterminate = subcategoryChecked.length > 0 && subcategoryChecked.length < subcategoryTagCheckboxes.length;
            }
        });
        
        // Update weight checkboxes
        const weightSections = document.querySelectorAll('#availableTags .weight-section');
        weightSections.forEach(weightSection => {
            const weightTagCheckboxes = weightSection.querySelectorAll('.tag-checkbox');
            const weightChecked = weightSection.querySelectorAll('.tag-checkbox:checked');
            const weightSelectAll = weightSection.querySelector('.select-all-checkbox');
            
            if (weightSelectAll && weightTagCheckboxes.length > 0) {
                weightSelectAll.checked = weightChecked.length === weightTagCheckboxes.length;
                weightSelectAll.indeterminate = weightChecked.length > 0 && weightChecked.length < weightTagCheckboxes.length;
            }
        });
    },

    // Initialize Select All checkbox with proper event listener
    initializeSelectAllCheckbox() {
        const selectAllAvailable = document.getElementById('selectAllAvailable');
        if (selectAllAvailable && !selectAllAvailable.hasAttribute('data-listener-added')) {
        verboseLog('Initializing Select All Available checkbox');
            selectAllAvailable.setAttribute('data-listener-added', 'true');
            selectAllAvailable.addEventListener('change', (e) => {
                verboseLog('Select All Available checkbox changed:', e.target.checked);
                const isChecked = e.target.checked;
                
                // Get all visible tag checkboxes in available tags
                const availableCheckboxes = document.querySelectorAll('#availableTags .tag-checkbox');
                verboseLog('Found available tag checkboxes:', availableCheckboxes.length);
                
                availableCheckboxes.forEach(checkbox => {
                    checkbox.checked = isChecked;
                    // CRITICAL FIX: Look in originalTags first to find tags regardless of filters
                    let tag = this.state.originalTags.find(t => t['Product Name*'] === checkbox.value);
                    // If not found in originalTags, try current tags (filtered view)
                    if (!tag) {
                        tag = this.state.tags.find(t => t['Product Name*'] === checkbox.value);
                    }
                    if (tag) {
                        if (isChecked) {
                            if (!this.state.persistentSelectedTags.includes(tag['Product Name*'])) {
                                this.state.persistentSelectedTags.push(tag['Product Name*']);
                            }
                        } else {
                            const index = this.state.persistentSelectedTags.indexOf(tag['Product Name*']);
                            if (index > -1) {
                                this.state.persistentSelectedTags.splice(index, 1);
                            }
                        }
                    }
                });
                
                // Update the regular selectedTags set to match persistent ones
                this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                
                // Update selected tags display
                // CRITICAL FIX: Use helper function to find ALL selected tags, preserving tags from multiple filters
                const selectedTagObjects = this.getSelectedTagObjects();
                this.updateSelectedTags(selectedTagObjects);
                
                // Update available tags display to reflect selection changes
                this.efficientlyUpdateAvailableTagsDisplay();
                
                // Update select all checkbox state
                this.updateSelectAllCheckboxes();
            });
        } else if (selectAllAvailable) {
            verboseLog('Select All Available checkbox already has listener');
        } else {
            verboseLog('Select All Available checkbox not found, will retry later');
            // Retry after a short delay in case the DOM hasn't loaded yet
            setTimeout(() => this.initializeSelectAllCheckbox(), 100);
        }
    },

    async uploadFile(file) {
        try {
            verboseLog(`🚀 Starting LIGHTNING upload:`, file.name, 'Size:', file.size, 'bytes');
            
            // Show Excel loading splash screen
            this.showExcelLoadingSplash(file.name);
            
            // Phase 1: Lightning-fast upload (save file only)
            this.updateUploadUI(`⚡ Lightning upload: ${file.name}...`);
            
            const formData = new FormData();
            formData.append('file', file);
            
            verboseLog('🚀 Sending lightning upload request...');
            
            const uploadResponse = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const uploadData = await uploadResponse.json();
            verboseLog('⚡ Lightning upload response:', uploadData);
            
            if (!uploadResponse.ok) {
                throw new Error(uploadData.error || 'Lightning upload failed');
            }
            
            // Upload complete, no need for separate processing step
            const processData = uploadData;
            
            verboseLog(`✅ Lightning upload completed! Upload: ${uploadData.upload_time?.toFixed(3)}s, Process: ${processData.process_time?.toFixed(3)}s`);
            
            // Show success toast
            if (typeof showToast === 'function') {
                showToast('success', `File uploaded successfully! ${uploadData.rows || 0} rows processed.`);
            }
            
            // PERFORMANCE FIX: Load tags instantly instead of reloading page
            // Show loading splash for tag loading
            this.showActionSplash('Loading tags from uploaded file...');
            
            // Show loading indicator in Current Inventory
            const availableTagsContainer = document.getElementById('availableTags');
            if (availableTagsContainer) {
                availableTagsContainer.innerHTML = `
                    <div class="text-center py-4">
                        <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-2 text-white">Loading tags from uploaded file...</p>
                    </div>
                `;
            }
            
            // Update file info immediately
            const fileInfoText = document.getElementById('fileInfoText');
            if (fileInfoText) {
                fileInfoText.textContent = file.name;
            }
            
            // CRITICAL FIX: Save filename to sessionStorage for cache key generation
            if (window.sessionStorage) {
                sessionStorage.setItem('uploaded_filename', file.name);
                console.log('✅ Saved uploaded filename to sessionStorage:', file.name);
            }
            
            // Clear old cache entries for previous files
            this.clearAvailableTagsCache();
            
            // Hide Excel loading splash and show success
            this.hideExcelLoadingSplash();
            this.updateUploadUI(`✅ ${file.name} ready!`, 'File processed successfully', 'success');
            
            // Load tags instantly using fast_load=1 and bypass cache to get fresh data
            // Try multiple times with increasing delays to handle backend processing
            let tagsLoaded = false;
            const maxRetries = 3;
            
            for (let attempt = 0; attempt < maxRetries; attempt++) {
                try {
                    // Increasing delays: 100ms (for session save), 500ms, 1000ms
                    const delay = attempt === 0 ? 100 : attempt === 1 ? 500 : 1000;
                    if (attempt > 0) {
                        await new Promise(resolve => setTimeout(resolve, delay));
                        verboseLog(`🔄 Retry ${attempt + 1}/${maxRetries} loading tags after upload...`);
                    } else {
                        await new Promise(resolve => setTimeout(resolve, delay));
                        verboseLog('🔄 Loading tags instantly after upload...');
                    }
                    
                    const tagsController = new AbortController();
                    const tagsTimeout = setTimeout(() => tagsController.abort(), 8000); // 8s timeout
                    
                    // Use fast_load=1 for instant response, nocache=1 to ensure fresh data from new upload
                    const tagsResponse = await fetch(`/api/available-tags?t=${Date.now()}&nocache=1&fast_load=1`, {
                        signal: tagsController.signal
                    });
                    clearTimeout(tagsTimeout);
                    
                    if (tagsResponse.ok) {
                        const tagsData = await tagsResponse.json();
                        if (tagsData.tags && tagsData.tags.length > 0) {
                            verboseLog(`✅ Loaded ${tagsData.tags.length} tags instantly after upload (attempt ${attempt + 1})`);
                            
                            // Update tags immediately
                            this.state.tags = [...tagsData.tags];
                            this.state.originalTags = [...tagsData.tags];
                            this._updateAvailableTags(tagsData.tags);
                            
                            // Load filters and selected tags in parallel (non-blocking)
                            Promise.allSettled([
                                this.fetchAndPopulateFilters(),
                                this.fetchAndUpdateSelectedTags()
                            ]).then(() => {
                                verboseLog('✅ Filters and selected tags loaded');
                            }).catch(err => {
                                console.warn('Filter/selected tag loading failed:', err);
                            });
                            
                            // Wait for tags to appear, then hide splash
                            if (this._waitForTagsToAppear) {
                                this._waitForTagsToAppear();
                            } else if (this.hideActionSplash) {
                                // Fallback: hide splash after short delay
                                setTimeout(() => {
                                    this.hideActionSplash();
                                }, 500);
                            }
                            
                            tagsLoaded = true;
                            return; // Success - tags loaded instantly!
                        }
                    }
                } catch (tagsError) {
                    if (attempt === maxRetries - 1) {
                        // Last attempt failed
                        console.warn('⚠️ Failed to load tags after all retries, will reload page:', tagsError);
                        // Fallback: reload page if all attempts fail
                        setTimeout(() => {
                            verboseLog('🔄 Reloading page as fallback...');
                            window.location.reload();
                        }, 500);
                        return;
                    }
                    // Continue to next retry
                    verboseLog(`⚠️ Attempt ${attempt + 1} failed, retrying...`);
                }
            }
            
            // If we get here, tags didn't load after all retries - reload page as fallback
            if (!tagsLoaded) {
                setTimeout(() => {
                    verboseLog('🔄 Reloading page to show new data...');
                    window.location.reload();
                }, 500);
            }
            
            return; // Success!
        } catch (error) {
            console.error('⚡ Lightning upload error:', error);
            this.hideExcelLoadingSplash();
            this.updateUploadUI('Upload failed: ' + error.message, 'error');
            return;
        }
    },
    // Fallback upload method for PythonAnywhere
    async uploadFileFallback(file) {
        try {
            verboseLog('Using fallback upload method for:', file.name);
            
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.status === 'ready') {
                verboseLog('Fallback upload successful');
                this.updateUploadUI(file.name, 'File uploaded successfully', 'success');
                // Refresh the page to load the new file
                window.location.reload();
                return true;
            } else {
                console.error('Fallback upload failed:', data.error);
                this.updateUploadUI('Upload failed: ' + (data.error || 'Unknown error'), 'error');
                return false;
            }
        } catch (error) {
            console.error('Fallback upload error:', error);
            this.updateUploadUI('Upload failed: ' + error.message, 'error');
            return false;
        }
    },

    async pollUploadStatusAndUpdateUI(filename, displayName) {
        verboseLog(`Polling upload status for: ${filename}`);
        
        const maxAttempts = 60; // 3 minutes max (3 seconds * 60 = 3 minutes)
        let attempts = 0;
        let consecutiveErrors = 0;
        const maxConsecutiveErrors = 5;
        
        // Add debug logging for upload processing
        verboseLog(`[UPLOAD DEBUG] Starting status polling for: ${filename}`);
        
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
                
                verboseLog(`Upload status: ${status} (age: ${age}s, total files: ${totalFiles})`);
                consecutiveErrors = 0; // Reset error counter on successful response
                
                if (status === 'ready' || status === 'done') {
                    // File is ready for basic operations
                    verboseLog(`[UPLOAD DEBUG] File marked as ready: ${filename}`);
                    this.hideExcelLoadingSplash();
                    this.updateUploadUI(displayName, 'File ready!', 'success');

                    // PERFORMANCE FIX: Removed artificial 1-second delay
                    // Show action splash for upload completion
                    verboseLog(`[UPLOAD DEBUG] Starting finalization process...`);
                    this.showActionSplash('Loading tags...');

                    // CRITICAL: After Excel upload, clear cache FIRST to ensure database lineage is used
                    // Excel upload may create cached tags with Excel lineage, we need database lineage
                    verboseLog('[UPLOAD DEBUG] Clearing cache to ensure database lineage is used...');
                    await fetch('/api/clear-cache', { method: 'POST' })
                        .then(() => verboseLog('✅ Cleared backend cache after upload'))
                        .catch(err => console.warn('Failed to clear cache:', err));
                    
                    // Also clear frontend cache to force fresh load from database
                    if (window.sessionStorage) {
                        const cacheKey = this.getAvailableTagsCacheKey();
                        sessionStorage.removeItem(cacheKey);
                        verboseLog('✅ Cleared frontend cache after upload');
                    }

                    // CRITICAL: After Excel upload, force refresh from database (not cache) to get correct lineage
                    // Set flag to force database lineage (nocache + prefer_db)
                    verboseLog(`[UPLOAD DEBUG] Loading tags from database with lineage alignment...`);
                    this._forceDatabaseLineage = true;
                    
                    // PERFORMANCE FIX: Load tags, filters, and selected tags in parallel
                    const [availableTagsLoaded, selectedTagsLoaded] = await Promise.all([
                        this.fetchAndUpdateAvailableTags(),
                        this.fetchAndUpdateSelectedTags()
                    ]);
                    
                    this._forceDatabaseLineage = false;

                    verboseLog(`[UPLOAD DEBUG] Available tags loaded: ${availableTagsLoaded}, Selected tags loaded: ${selectedTagsLoaded}`);

                    // Load filters after tags are loaded (filters depend on tag data)
                    verboseLog(`[UPLOAD DEBUG] Loading filter options...`);
                    await this.fetchAndPopulateFilters();
                    verboseLog(`[UPLOAD DEBUG] Filter options loaded`);

                    // CRITICAL: After loading tags with database lineage, ensure UI reflects database values
                    // Check if lineage was aligned and force UI update
                    if (availableTagsLoaded && this.state.tags && this.state.tags.length > 0) {
                        verboseLog('[UPLOAD DEBUG] Verifying tags have database lineage...');
                        // Tags should already be updated by fetchAndUpdateAvailableTags, but ensure lineage is correct
                        // Re-render to ensure dropdowns show database lineage (not Excel lineage)
                        const tagsWithDbLineage = this.state.tags.map(tag => {
                            const normalized = this._normalizeLineageFields(tag);
                            // CRITICAL: Ensure database lineage is set on all tags
                            const dbLineage = normalized.canonical_lineage || normalized.currentLineage;
                            if (dbLineage) {
                                // Force all lineage fields to database value
                                normalized.canonical_lineage = dbLineage;
                                normalized.currentLineage = dbLineage;
                                normalized.Lineage = dbLineage;
                                normalized.lineage = dbLineage;
                            }
                            return normalized;
                        });
                        this.state.tags = tagsWithDbLineage;
                        this.state.originalTags = tagsWithDbLineage;
                        verboseLog('[UPLOAD DEBUG] Re-rendering tags with database lineage...');
                        this._updateAvailableTags(tagsWithDbLineage);
                        
                        // CRITICAL: Also update selected tags if any are selected - force update with database lineage
                        if (this.state.persistentSelectedTags.length > 0) {
                            const selectedTagObjects = this.state.persistentSelectedTags.map(name => {
                                const tag = tagsWithDbLineage.find(t => t['Product Name*'] === name);
                                if (tag) {
                                    // Ensure database lineage is set
                                    const dbLineage = tag.canonical_lineage || tag.currentLineage;
                                    if (dbLineage) {
                                        tag.canonical_lineage = dbLineage;
                                        tag.currentLineage = dbLineage;
                                        tag.Lineage = dbLineage;
                                        tag.lineage = dbLineage;
                                        verboseLog(`[UPLOAD DEBUG] Selected tag "${name}" has database lineage: ${dbLineage}`);
                                    }
                                }
                                return tag;
                            }).filter(Boolean);
                            if (selectedTagObjects.length > 0) {
                                verboseLog(`[UPLOAD DEBUG] Updating ${selectedTagObjects.length} selected tags with database lineage`);
                                // Force update to ensure dropdowns are re-rendered
                                this._forceSelectedTagsUpdate = true;
                                this.updateSelectedTags(selectedTagObjects);
                            }
                        }
                    }

                    if (!availableTagsLoaded) {
                        console.error('[UPLOAD DEBUG] Failed to load available tags after upload');
                        console.error('Failed to load product data. Please try refreshing the page.');
                        return;
                    }

                    verboseLog('[UPLOAD DEBUG] Upload processing complete');
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
                        verboseLog('Attempting to load data despite not_found status...');
                        try {
                            const availableTagsLoaded = await this.fetchAndUpdateAvailableTags();
                            if (availableTagsLoaded && this.state.tags && this.state.tags.length > 0) {
                                verboseLog('Data loaded successfully despite not_found status');
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
            // PERFORMANCE FIX: Reduced polling interval from 3s to 1s for faster tag availability
            // Use adaptive polling: faster initially, slower if taking longer
            const pollInterval = attempts < 10 ? 1000 : 2000; // 1s for first 10 attempts, then 2s
            await new Promise(resolve => setTimeout(resolve, pollInterval));
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
        // Auto check all available tags call removed
    },

    setupFilterEventListeners() {
        const filterIds = ['vendorFilter', 'brandFilter', 'productTypeFilter', 'lineageFilter', 'weightFilter', 'dohFilter', 'highCbdFilter'];
        
        verboseLog('Setting up Mac-like fast filter event listeners...');
        
        // Detect Windows platform for optimized performance
        const isWindows = navigator.platform.toLowerCase().includes('win') || 
                         navigator.userAgent.toLowerCase().includes('windows');
        
        // Ultra-fast debounced filter update (Mac-like speed)
        // Immediate filter update function (no debounce for instant response)
        const immediateFilterUpdate = async (filterType, value) => {
            verboseLog(`🔥 immediateFilterUpdate called for ${filterType}: ${value}`);
            
            // CRITICAL FIX: Don't update filters during deselection
            if (this.state.isProcessingDeselection) {
                verboseLog('🚫 SKIPPING immediateFilterUpdate - currently processing deselection');
                return;
            }
            
            // Update filter state immediately
            const filterTypeMap = {
                'vendor': 'vendor',
                'brand': 'brand',
                'productType': 'productType',
                'lineage': 'lineage',
                'weight': 'weight',
                'doh': 'doh',
                'highCbd': 'highCbd'
            };
            
            const stateKey = filterTypeMap[filterType];
            if (stateKey) {
                this.state.filters[stateKey] = value || 'All';
            }
            
            // GUARANTEED FIX: Save filters to localStorage when they change
            this.saveFiltersToStorage();
            
            // Apply filters immediately with immediate UI update (bypass debounce)
            // Cancel any pending debounced updates to prevent delays
            if (this.debouncedUpdateAvailableTags.cancel) {
                this.debouncedUpdateAvailableTags.cancel();
            }
            
            // Call applyFilters with immediate flag to skip debounce
            this.applyFilters(true); // Pass true to indicate immediate update
            
            // Update filter options asynchronously (non-blocking) after UI update
            Promise.resolve().then(async () => {
                if (!isWindows) {
                    // Mac: Update filter options and render active filters
                    await this.updateFilterOptions();
                    this.renderActiveFilters();
                } else {
                    // Windows: Just update filter options (skip renderActiveFilters for speed)
                    await this.updateFilterOptions();
                }
            }).catch(err => {
                console.warn('Filter options update failed (non-critical):', err);
            });
            
            // Special case: DOH filter used as a bulk setter to persist "No" (async, non-blocking)
            if (filterType === 'doh') {
                Promise.resolve().then(async () => {
                    try {
                        const dohValueUpper = (value || '').toString().trim().toUpperCase();
                        // Treat "No"/empty/NONE as removing the DOH image and persisting 'No'
                        if (dohValueUpper === 'NONE' || dohValueUpper === 'NO' || dohValueUpper === '') {
                            await this.bulkUpdateDohForSelected('NONE');
                        } else if (dohValueUpper === 'DOH' || dohValueUpper === 'THC' || dohValueUpper === 'CBD') {
                            await this.bulkUpdateDohForSelected(dohValueUpper);
                        }
                    } catch (bulkErr) {
                        console.warn('Bulk DOH update from filter failed:', bulkErr);
                    }
                });
            }

            verboseLog(`🔥 immediateFilterUpdate completed for ${filterType}`);
        };
        
        filterIds.forEach(filterId => {
            const filterElement = document.getElementById(filterId);
            
            if (filterElement) {
                // Remove all existing listeners for clean slate
                filterElement.removeEventListener('change', filterElement._filterChangeHandler);
                filterElement.removeEventListener('input', filterElement._filterInputHandler);
                filterElement.removeEventListener('click', filterElement._filterClickHandler);
                
                // Single, fast event handler (Mac-like simplicity)
                const self = this;
                filterElement._filterChangeHandler = (event) => {
                    verboseLog(`🔥 FILTER CHANGED: ${filterId} = "${event.target.value}"`);
                    const filterType = self.getFilterTypeFromId(filterId);
                    const value = event.target.value;
                    
                    // Special handling for vendor filter
                    if (filterId === 'vendorFilter' && value && value.trim() !== '' && value.toLowerCase() !== 'all') {
                        self.resetAllOtherFilters();
                    }
                    
                    // Immediate filter update (no debounce for instant response)
                    verboseLog(`🔥 Calling immediateFilterUpdate for ${filterType}: ${value}`);
                    immediateFilterUpdate(filterType, value);
                };
                
                // Only use change event for Mac-like behavior
                filterElement.addEventListener('change', filterElement._filterChangeHandler);
                
                verboseLog(`Fast event listener attached to ${filterId}`);
            }
        });
    },

    setupSearchEventListeners() {
        verboseLog('Setting up search event listeners...');
        
        // Add search event listeners for available tags
        const availableTagsSearch = document.getElementById('availableTagsSearch');
        if (availableTagsSearch) {
            availableTagsSearch.removeEventListener('input', this.handleAvailableTagsSearch.bind(this));
            availableTagsSearch.addEventListener('input', this.handleAvailableTagsSearch.bind(this));
            verboseLog('Added event listener to availableTagsSearch');
        } else {
            console.warn('Available tags search element not found');
        }
        
        // Add search event listeners for selected tags
        const selectedTagsSearch = document.getElementById('selectedTagsSearch');
        if (selectedTagsSearch) {
            selectedTagsSearch.removeEventListener('input', this.handleSelectedTagsSearch.bind(this));
            selectedTagsSearch.addEventListener('input', this.handleSelectedTagsSearch.bind(this));
            verboseLog('Added event listener to selectedTagsSearch');
        } else {
            console.warn('Selected tags search element not found');
        }
    },

    getFilterTypeFromId(filterId) {
        const idToType = {
            'vendorFilter': 'vendor',
            'brandFilter': 'brand',
            'productTypeFilter': 'productType',
            'lineageFilter': 'lineage',
            'weightFilter': 'weight',
            'dohFilter': 'doh',
            'highCbdFilter': 'highCbd'
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
            { id: 'weightFilter', label: 'Weight' },
            { id: 'dohFilter', label: 'DOH' },
            { id: 'highCbdFilter', label: 'High CBD' }
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
                // DEBUG: Log active filter detection
                verboseLog('🔍 Active Filter Detected:', {
                    id: id,
                    label: label,
                    value: select.value,
                    isActive: true
                });
                
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
            } else {
                // DEBUG: Log inactive filter
                verboseLog('🔍 Inactive Filter:', {
                    id: id,
                    label: label,
                    value: select?.value || 'undefined',
                    isActive: false
                });
            }
        });
    },

    // Enhanced function to clear all filters and perform full app reset
    async clearAllFilters() {
        verboseLog('🔄 Clearing all filters...');
        
        try {
            // CRITICAL FIX: Prevent infinite recursion - don't call performFullAppReset which calls this again
            // Instead, do the filter clearing directly
            
            // Clear all filter dropdowns (don't trigger events yet to avoid multiple applyFilters calls)
            const filterIds = ['vendorFilter', 'brandFilter', 'productTypeFilter', 'lineageFilter', 'weightFilter', 'dohFilter', 'highCbdFilter'];
            
            filterIds.forEach(filterId => {
                const filterElement = document.getElementById(filterId);
                if (filterElement) {
                    filterElement.value = '';
                    verboseLog(`Cleared ${filterId}`);
                }
            });
            
            // Clear all search fields
            const searchInputs = document.querySelectorAll('#availableTagsSearch, #selectedTagsSearch');
            searchInputs.forEach(input => {
                if (input) {
                    input.value = '';
                }
            });
            
            // Clear filter cache
            this.state.filterCache = null;
            
            // Apply the cleared filters to show all tags (single call after all filters are cleared)
            if (this.applyFilters) {
                this.applyFilters();
            }
            
            // Update filter dropdowns to show all options
            if (this.state.originalFilterOptions && this.state.originalFilterOptions.vendor) {
                if (this.updateFilters) {
                    this.updateFilters(this.state.originalFilterOptions, false); // Don't preserve values when clearing
                }
            }
            
            // Render active filters (should be empty now)
            if (this.renderActiveFilters) {
                this.renderActiveFilters();
            }
            
            // Add visual feedback to the button
            const clearBtn = document.getElementById('clearFiltersBtn');
            if (clearBtn) {
                clearBtn.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    clearBtn.style.transform = 'scale(1)';
                }, 150);
            }
            
            verboseLog('✅ All filters cleared successfully');
            
        } catch (error) {
            console.error('❌ Error during clear all filters:', error);
            // Show error notification
            if (window.Toast && window.Toast.error) {
                window.Toast.error('Failed to clear filters: ' + error.message, {
                    duration: 5000,
                    position: 'top-right'
                });
            }
        }
    },

    // Function to reset all other filters when vendor changes (but keep vendor filter)
    resetAllOtherFilters() {
        verboseLog('Resetting all other filters while keeping vendor filter...');
        
        // Get the current vendor filter value to preserve it
        const vendorFilter = document.getElementById('vendorFilter');
        const currentVendorValue = vendorFilter ? vendorFilter.value : '';
        
        // List of all filters except vendor
        const otherFilterIds = ['brandFilter', 'productTypeFilter', 'lineageFilter', 'weightFilter', 'dohFilter', 'highCbdFilter'];
        
        // Clear all other filter dropdowns
        otherFilterIds.forEach(filterId => {
            const filterElement = document.getElementById(filterId);
            if (filterElement) {
                filterElement.value = '';
                verboseLog(`Cleared ${filterId}`);
            }
        });
        
        // Update filter options to reflect the new vendor selection
        this.updateFilterOptions();
        
        // Apply the updated filters (vendor only)
        this.applyFilters();
        this.renderActiveFilters();
        
        verboseLog('All other filters reset successfully, vendor filter preserved:', currentVendorValue);
    },

    // Emergency function to clear stuck upload UI
    forceClearUploadUI() {
        verboseLog('Force clearing upload UI state...');
        
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
        
        verboseLog('Upload UI state cleared');
    },

    // Clear all UI state when a new file is uploaded
    clearUIStateForNewFile(preserveFilters = false) {
        verboseLog('Clearing UI state for new file upload, preserveFilters:', preserveFilters);
        
        // Clear persistent selected tags
        this.state.persistentSelectedTags = [];
        this.state.selectedTags.clear();
        
        // Clear tag displays
        const availableContainer = document.getElementById('availableTags');
        const selectedContainer = document.getElementById('selectedTags');
        
        if (availableContainer) {
            // Clear available tags but keep the select all container
            const selectAllContainer = availableContainer.querySelector('.select-all-container');
            availableContainer.innerHTML = '';
            if (selectAllContainer) {
                availableContainer.appendChild(selectAllContainer);
            }
        }
        
        if (selectedContainer) {
            selectedContainer.innerHTML = '';
        }
        
        // Clear search inputs
        const searchInputs = document.querySelectorAll('input[type="text"]');
        searchInputs.forEach(input => {
            if (input.placeholder && input.placeholder.includes('Search')) {
                input.value = '';
            }
        });
        
        // Only clear filters if explicitly requested (for actual new file uploads)
        if (!preserveFilters) {
            verboseLog('Clearing filter settings for new file upload');
            const filterSelects = document.querySelectorAll('select[id*="Filter"]');
            filterSelects.forEach(select => {
                select.value = '';
            });
            
            // Reset filter state to defaults
            this.state.filters = {
                vendor: 'All',
                brand: 'All',
                productType: 'All',
                lineage: 'All',
                weight: 'All',
                doh: 'All',
                highCbd: 'All'
            };
        } else {
            verboseLog('Preserving filter settings during UI refresh');
        }
        
        // Update tag counts
        this.updateTagCount('available', 0);
        this.updateTagCount('selected', 0);
        
        verboseLog('UI state cleared for new file');
    },

    // Validate and clean up selected tags against current Excel data
    validateSelectedTags() {
        // CRITICAL FIX: Don't validate if we're in the middle of processing or if tags are being actively used
        if (this.state.isProcessingDeselection || this.state.isClearing) {
            verboseLog('⏭️ Skipping validateSelectedTags - operation in progress');
            return;
        }
        
        // Add safeguard to prevent clearing tags that were just added via JSON matching
        const hasJsonMatchedTags = this.state.persistentSelectedTags.length > 0;
        
        if (!this.state.originalTags || this.state.originalTags.length === 0) {
            // No Excel data loaded, but don't clear if we have selected tags
            if (!hasJsonMatchedTags) {
                // CRITICAL FIX: Only clear if we're sure there's no data, not just temporarily
                // Check if tags array exists (might be loading)
                if (this.state.tags && this.state.tags.length === 0) {
                    verboseLog('No tags available, clearing selected tags');
                    this.state.persistentSelectedTags = [];
                    this.state.selectedTags.clear();
                } else {
                    verboseLog('Preserving selected tags - data may be loading');
                }
            } else {
                verboseLog('Preserving JSON matched tags even though no Excel data is loaded yet');
            }
            return;
        }

        // CRITICAL FIX: Only validate if we have a significant number of originalTags
        // This prevents clearing during partial data loads
        if (this.state.originalTags.length < 10 && this.state.persistentSelectedTags.length > 0) {
            verboseLog('⏭️ Skipping validation - originalTags count is low, may be partial load');
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

        // CRITICAL FIX: Only clear and update if we actually found invalid tags AND they represent a significant portion
        // This prevents clearing when data is still loading
        if (invalidTags.length > 0 && invalidTags.length > this.state.persistentSelectedTags.length * 0.5) {
            // More than 50% invalid - likely a data mismatch, clean up
            verboseLog(`Cleaning up ${invalidTags.length} invalid tags (${(invalidTags.length / this.state.persistentSelectedTags.length * 100).toFixed(1)}% of selections)`);
            
            // Remove invalid tags and update with corrected case
            this.state.persistentSelectedTags = [];
            correctedTags.forEach(tagName => {
                if (!this.state.persistentSelectedTags.includes(tagName)) {
                    this.state.persistentSelectedTags.push(tagName);
                }
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

    async syncDeselectionWithBackend(tagName) {
        // Synchronize deselection of JSON matched items with the backend
        try {
            verboseLog(`Syncing deselection of JSON matched item: ${tagName}`);
            
            // Call the move tags API to ensure backend state is updated
            const response = await fetch('/api/move-tags', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tags: [tagName],
                    direction: 'to_available'
                })
            });
            
            if (!response.ok) {
                console.warn(`Failed to sync deselection with backend for ${tagName}`);
            } else {
                verboseLog(`Successfully synced deselection of ${tagName} with backend`);
            }
        } catch (error) {
            console.error(`Error syncing deselection with backend: ${error}`);
        }
    },

    updateTagLineage(tag, lineage) {
        // Update the lineage in the tag object
        tag.lineage = lineage;
        
        // Update the color based on the new lineage
        const newColor = this.getLineageColor(lineage);
        this.updateTagColor(tag, newColor);
    },

    // Ensure proper scrolling behavior for tag containers
    hasActiveFilters() {
        // Check if any filters are currently active (not set to "All")
        const vendorFilter = document.getElementById('vendorFilter')?.value || '';
        const brandFilter = document.getElementById('brandFilter')?.value || '';
        const productTypeFilter = document.getElementById('productTypeFilter')?.value || '';
        const lineageFilter = document.getElementById('lineageFilter')?.value || '';
        const weightFilter = document.getElementById('weightFilter')?.value || '';
        const dohFilter = document.getElementById('dohFilter')?.value || '';
        const highCbdFilter = document.getElementById('highCbdFilter')?.value || '';
        
        const filters = [vendorFilter, brandFilter, productTypeFilter, lineageFilter, weightFilter, dohFilter, highCbdFilter];
        
        // Return true if any filter is not empty and not "All"
        return filters.some(filter => filter && filter.trim() !== '' && filter.toLowerCase() !== 'all');
    },

    clearFiltersForDeselectedTag(tag) {
        /**
         * This function is intentionally disabled to prevent filters from being
         * cleared when deselecting tags, which was causing users to lose their
         * filter state and have to start over.
         */
        verboseLog('🚫 SKIPPING filter clearing for deselected tag:', tag['Product Name*']);
        verboseLog('🚫 Filter clearing is DISABLED - should not affect filters');
        verboseLog('🚫 If filters are being cleared, the issue is coming from elsewhere');
        // Functionality removed to preserve user's filter state when deselecting tags
        return; // Explicit return
    },

    ensureProperScrolling() {
        const containers = document.querySelectorAll('.tag-list-container');
        containers.forEach(container => {
            // Remove any height restrictions
            container.style.maxHeight = 'none';
            container.style.height = 'auto';
            
            // Ensure overflow is set to visible to prevent scrollbars
            container.style.overflowY = 'visible';
            container.style.overflowX = 'hidden';
            
            // Force a reflow to ensure changes take effect
            container.offsetHeight;
            
            // Also ensure all child elements can expand
            const children = container.querySelectorAll('*');
            children.forEach(child => {
                child.style.maxHeight = 'none';
                child.style.height = 'auto';
            });
        });
        
        // Also ensure parent containers can expand
        const parentContainers = document.querySelectorAll('.glass-card, .card-body, .col-lg-5');
        parentContainers.forEach(container => {
            container.style.height = 'auto';
            container.style.maxHeight = 'none';
        });
    },

    removeDropdownInstructionBlurb() {
        // Remove the instructional blurb when any chevron is clicked
        const blurb = document.getElementById('dropdownInstructionBlurb');
        if (blurb && !blurb.classList.contains('hidden')) {
            blurb.classList.add('hidden');
            
            // Remove the element from DOM after animation completes
            setTimeout(() => {
                if (blurb && blurb.parentNode) {
                    blurb.parentNode.removeChild(blurb);
                }
            }, 300); // Match the CSS transition duration
        }
    },
    // Start memory optimization
    startMemoryOptimization() {
        // Run memory optimization every 30 seconds
        setInterval(() => {
            this.optimizeMemory();
        }, 30000);
        
        // Clear unused data when page becomes hidden
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.clearUnusedData();
            }
        });
        
        verboseLog('Memory optimization started');
    },

    // Start periodic filter refresh to ensure filters stay in sync with data
    startPeriodicFilterRefresh() {
        // Clear any existing interval
        if (this._filterRefreshInterval) {
            clearInterval(this._filterRefreshInterval);
            this._filterRefreshInterval = null;
        }
        
        // Refresh filters every 60 seconds to ensure they stay in sync with data
        this._filterRefreshInterval = setInterval(() => {
            // Only refresh if we have tags loaded and page is visible
            if (this.state.tags && this.state.tags.length > 0 && !document.hidden) {
                // CRITICAL FIX: Skip refresh if filters already have data and user has selections
                // This prevents clearing user's filter selections
                const hasFilterSelections = Array.from(document.querySelectorAll('select[id*="Filter"]')).some(select => select.value && select.value.trim() !== '');
                const hasSelectedTags = this.state.persistentSelectedTags && this.state.persistentSelectedTags.length > 0;
                
                // Only refresh if filters are empty or if we need to update options (but preserve values)
                if (!hasFilterSelections && !hasSelectedTags) {
                    verboseLog('🔄 Periodic filter refresh triggered (no user selections)');
                    this.fetchAndPopulateFilters(true).catch(error => {
                        console.warn('Periodic filter refresh failed (non-critical):', error);
                    });
                } else {
                    verboseLog('⏭️ Skipping periodic filter refresh - user has active selections');
                }
            }
        }, 60000); // Every 60 seconds
        
        verboseLog('Periodic filter refresh started (every 60 seconds)');
    },

    // Stop periodic filter refresh
    stopPeriodicFilterRefresh() {
        if (this._filterRefreshInterval) {
            clearInterval(this._filterRefreshInterval);
            this._filterRefreshInterval = null;
            verboseLog('Periodic filter refresh stopped');
        }
    },

    // Memory optimization functions
    optimizeMemory() {
        const now = Date.now();
        
        // Only cleanup every 30 seconds to avoid overhead
        if (now - this.state._lastCleanup < 30000) {
            return;
        }
        
        this.state._lastCleanup = now;
        
        // Clear large arrays when not needed
        // REMOVED: 100 tag limit - no longer limiting to allow all tags to generate
        // if (this.state.tags && this.state.tags.length > 1000) {
        //     // Keep only essential data
        //     this.state.tags = this.state.tags.slice(0, 100);
        // }
        
        // Clear filter cache if it's large
        if (this.state.filterCache && JSON.stringify(this.state.filterCache).length > 100000) {
            this.state.filterCache = null;
        }
        
        // Clear old timers
        if (this.state.updateAvailableTagsTimer) {
            clearTimeout(this.state.updateAvailableTagsTimer);
            this.state.updateAvailableTagsTimer = null;
        }
        
        // Force garbage collection if available
        performanceUtils.cleanup.forceGC();
        
        verboseLog('Memory optimization completed');
    },
    
    // Clear unused data
    clearUnusedData() {
        // DON'T clear originalTags - filters need it!
        // if (this.state.originalTags && this.state.originalTags.length > 0) {
        //     this.state.originalTags = [];
        // }
        
        // Clear filter cache
        this.state.filterCache = null;
        
        // Clear brand categories if not needed
        if (this.state.brandCategories.size > 100) {
            this.state.brandCategories.clear();
        }
        
        // Force garbage collection
        performanceUtils.cleanup.forceGC();
    },
    
    // Memory-efficient tag processing
    processTagsMemoryEfficient(tags) {
        if (!tags || !Array.isArray(tags)) {
            return [];
        }
        
        // Process in chunks to avoid memory spikes
        const chunkSize = 100;
        const processedTags = [];
        
        for (let i = 0; i < tags.length; i += chunkSize) {
            const chunk = tags.slice(i, i + chunkSize);
            processedTags.push(...chunk);
            
            // Allow other operations to run
            if (i % (chunkSize * 5) === 0) {
                setTimeout(() => {}, 0);
            }
        }
        
        return processedTags;
    }
};

// Expose TagManager to global scope
window.TagManager = TagManager;
window.updateAvailableTags = TagManager.debouncedUpdateAvailableTags.bind(TagManager);
window.updateFilters = TagManager.updateFilters.bind(TagManager);
window.fetchAndUpdateSelectedTags = TagManager.fetchAndUpdateSelectedTags.bind(TagManager);

function attachSelectedTagsCheckboxListeners() {
    const container = document.getElementById('selectedTags');
    if (!container) return;

    // Parent checkboxes
    container.querySelectorAll('.select-all-checkbox').forEach(parentCheckbox => {
        parentCheckbox.disabled = false;
        const newCheckbox = parentCheckbox.cloneNode(true);
        parentCheckbox.parentNode.replaceChild(newCheckbox, parentCheckbox);

        newCheckbox.addEventListener('change', function(e) {
            verboseLog('Parent checkbox clicked in selected tags', this);
            const isChecked = e.target.checked;
            // Find the closest section (vendor, brand, product type, or weight)
            const parentSection = newCheckbox.closest('.vendor-section, .brand-section, .product-type-section, .subcategory-section, .weight-section');
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
        verboseLog('Attached parent checkbox listener in selected tags', newCheckbox);
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

verboseLog('Original tags:', TagManager.state.originalTags);

// Lineage abbreviation mapping (matching Python version)
const ABBREVIATED_LINEAGE = {
    "SATIVA": "S",
    "INDICA": "I", 
    "HYBRID": "H",
    "HYBRID/SATIVA": "H/S",
    "HYBRID/INDICA": "I",
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

// Auto check all available tags functionality removed

// Only update if filteredTags is defined
if (typeof filteredTags !== 'undefined' && filteredTags) {
    TagsTable.updateTagsList('availableTags', filteredTags);
}
// Auto check all available tags call removed

// Test function for Select All functionality
window.testSelectAll = function() {
  verboseLog('Testing Select All functionality...');
  
  // Test Available Select All
  const selectAllAvailable = document.getElementById('selectAllAvailable');
  verboseLog('Select All Available checkbox:', selectAllAvailable);
  if (selectAllAvailable) {
    verboseLog('Available checkbox checked state:', selectAllAvailable.checked);
    verboseLog('Available checkbox visible:', selectAllAvailable.offsetParent !== null);
    verboseLog('Available checkbox style:', window.getComputedStyle(selectAllAvailable));
    
    // Manually trigger the change event
    selectAllAvailable.checked = !selectAllAvailable.checked;
    selectAllAvailable.dispatchEvent(new Event('change', { bubbles: true }));
    verboseLog('Manually triggered Available change event');
  } else {
    console.error('Select All Available checkbox not found!');
  }
  
  // Test Selected Select All
  const selectAllSelected = document.getElementById('selectAllSelected');
  verboseLog('Select All Selected checkbox:', selectAllSelected);
  if (selectAllSelected) {
    verboseLog('Selected checkbox checked state:', selectAllSelected.checked);
    verboseLog('Selected checkbox visible:', selectAllSelected.offsetParent !== null);
    verboseLog('Selected checkbox style:', window.getComputedStyle(selectAllSelected));
    
    // Manually trigger the change event
    selectAllSelected.checked = !selectAllSelected.checked;
    selectAllSelected.dispatchEvent(new Event('change', { bubbles: true }));
    verboseLog('Manually triggered Selected change event');
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
    
    // Show loading state
    const loadingModal = document.createElement('div');
    loadingModal.className = 'modal fade';
    loadingModal.id = 'jsonLoadingModal';
    loadingModal.innerHTML = `
        <div class="modal-dialog modal-sm">
            <div class="modal-content">
                <div class="modal-body text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Processing JSON data...</p>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(loadingModal);
    
    const loadingInstance = new bootstrap.Modal(loadingModal);
    loadingInstance.show();
    
    try {
        // Send JSON data to backend for matching
        const response = await fetch('/api/json-match', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: jsonText.startsWith('http') ? jsonText : null, json_data: json })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const matchResult = await response.json();
        
        if (matchResult.success) {
            verboseLog('JSON matching successful:', {
                matchedCount: matchResult.matched_count,
                availableTagsCount: matchResult.available_tags ? matchResult.available_tags.length : 0,
                selectedTagsCount: matchResult.selected_tags ? matchResult.selected_tags.length : 0,
                jsonMatchedTagsCount: matchResult.json_matched_tags ? matchResult.json_matched_tags.length : 0
            });
            
            // CRITICAL FIX: Always update available tags first to populate state.tags and state.originalTags
            // This ensures JSON matched products are available for lookup when converting selected tag names to objects
            if (matchResult.available_tags && matchResult.available_tags.length > 0) {
                verboseLog('Updating available tags with new data:', matchResult.available_tags.length);
                TagManager._updateAvailableTags(matchResult.available_tags, null);
                TagManager.saveAvailableTagsToCache(matchResult.available_tags || []);
                TagManager.state.hydratedFromCache = false;
            } else {
                verboseLog('No available tags in response');
            }
            
            // Use the selected tags from the JSON match response
            if (matchResult.selected_tags && matchResult.selected_tags.length > 0) {
                verboseLog('Using selected tags from JSON match response:', matchResult.selected_tags);
                
                // CRITICAL FIX: Convert selected tag names (strings) to tag objects
                // Look up each tag name in available_tags to get the full tag object
                const availableTagsMap = new Map();
                if (matchResult.available_tags && matchResult.available_tags.length > 0) {
                    matchResult.available_tags.forEach(tag => {
                        const tagName = tag['Product Name*'] || tag.ProductName || tag.displayName || '';
                        if (tagName) {
                            availableTagsMap.set(tagName, tag);
                        }
                    });
                }
                
                // Also check in state.tags if available_tags doesn't have it
                if (TagManager.state.tags && TagManager.state.tags.length > 0) {
                    TagManager.state.tags.forEach(tag => {
                        const tagName = tag['Product Name*'] || tag.ProductName || tag.displayName || '';
                        if (tagName && !availableTagsMap.has(tagName)) {
                            availableTagsMap.set(tagName, tag);
                        }
                    });
                }
                
                // Convert selected tag names to tag objects
                const selectedTagObjects = matchResult.selected_tags
                    .map(tagName => {
                        // Try to find the tag object in available_tags map
                        const tagObj = availableTagsMap.get(tagName);
                        if (tagObj) {
                            return tagObj;
                        }
                        // If not found, try to find in state.tags
                        const foundInState = TagManager.state.tags?.find(t => 
                            (t['Product Name*'] || t.ProductName || t.displayName) === tagName
                        );
                        if (foundInState) {
                            return foundInState;
                        }
                        verboseLog(`Warning: Could not find tag object for name: ${tagName}`);
                        return null;
                    })
                    .filter(Boolean); // Remove null entries
                
                verboseLog(`Converted ${matchResult.selected_tags.length} selected tag names to ${selectedTagObjects.length} tag objects`);
                
                if (selectedTagObjects.length > 0) {
                    // Update persistent selected tags with the tag names
                    TagManager.state.persistentSelectedTags = matchResult.selected_tags;
                    TagManager.state.selectedTags = new Set(matchResult.selected_tags);
                    
                    // Now call updateSelectedTags with tag objects
                    TagManager.updateSelectedTags(selectedTagObjects);
                } else {
                    verboseLog('No valid tag objects found for selected tags');
                    TagManager.state.persistentSelectedTags = [];
                    TagManager.state.selectedTags = new Set();
                    
                    // Clear the selected tags display
                    const selectedTagsContainer = document.getElementById('selectedTags');
                    if (selectedTagsContainer) {
                        selectedTagsContainer.innerHTML = '';
                    }
                }
            } else {
                verboseLog('No selected tags in response, clearing selected tags');
                TagManager.state.persistentSelectedTags = [];
                TagManager.state.selectedTags = new Set();
                
                // Clear the selected tags display
                const selectedTagsContainer = document.getElementById('selectedTags');
                if (selectedTagsContainer) {
                    selectedTagsContainer.innerHTML = '';
                }
            }
            
            // Show a notification to the user
            const notificationDiv = document.createElement('div');
            notificationDiv.className = 'alert alert-success alert-dismissible fade show';
            notificationDiv.innerHTML = `
                <strong>JSON Matching Complete!</strong> 
                ${matchResult.matched_count} products were matched and automatically selected for label generation. 
                You can review and modify the selected items as needed.
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            // Insert notification at the top of the main content area
            const mainContent = document.querySelector('.container-fluid') || document.querySelector('.container');
            if (mainContent) {
                mainContent.insertBefore(notificationDiv, mainContent.firstChild);
            }
            
            // Auto-dismiss notification after 10 seconds
            setTimeout(() => {
                if (notificationDiv.parentNode) {
                    notificationDiv.remove();
                }
            }, 10000);
            
            // Show the JSON filter toggle button
            if (typeof updateJsonFilterToggleVisibility === 'function') {
                updateJsonFilterToggleVisibility();
            }
            
            // Force update the toggle button visibility after a short delay to ensure backend state is updated
            setTimeout(() => {
                if (typeof updateJsonFilterToggleVisibility === 'function') {
                    updateJsonFilterToggleVisibility();
                }
            }, 1000);
            
            verboseLog('JSON match response received successfully');
            
        } else {
            throw new Error(matchResult.error || 'JSON matching failed');
        }
        
    } catch (error) {
        console.error('JSON matching error:', error);
        
        // Show error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.innerHTML = `
            <strong>JSON Matching Failed!</strong> 
            ${error.message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert error notification at the top of the main content area
        const mainContent = document.querySelector('.container-fluid') || document.querySelector('.container');
        if (mainContent) {
            mainContent.insertBefore(errorDiv, mainContent.firstChild);
        }
        
    } finally {
        // Hide loading modal
        if (loadingInstance) {
            loadingInstance.hide();
        }
        if (loadingModal && loadingModal.parentNode) {
            loadingModal.parentNode.removeChild(loadingModal);
        }
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Show splash screen immediately (but don't load tags yet - wait for store selection)
    AppLoadingSplash.show();
    AppLoadingSplash.updateProgress(10, 'Initializing application...');
    
    // DO NOT call TagManager.init() here - it will be called after store selection
    // in templates/index.html via checkStoreRequired() callback
    
    // Ensure proper scrolling behavior (safe to call even if TagManager not fully initialized)
    if (window.TagManager && typeof TagManager.ensureProperScrolling === 'function') {
        TagManager.ensureProperScrolling();
    }
    
    // Initialize sticky filter bar behavior
    initializeStickyFilterBar();

    // Add event listener for the clear button with retry mechanism
    function attachClearButtonListener() {
        const clearButton = document.getElementById('clear-filters-btn');
        if (clearButton) {
            // Remove any existing listeners to prevent duplicates
            const newButton = clearButton.cloneNode(true);
            clearButton.parentNode.replaceChild(newButton, clearButton);
            
            newButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                verboseLog('Clear & Reset button clicked');
                if (window.TagManager && TagManager.clearSelected) {
                    verboseLog('Calling TagManager.clearSelected()');
                    TagManager.clearSelected();
                } else {
                    console.error('TagManager or clearSelected method not available');
                    // Fallback: try clearAllFilters
                    if (window.TagManager && TagManager.clearAllFilters) {
                        verboseLog('Fallback: Calling TagManager.clearAllFilters()');
                        TagManager.clearAllFilters();
                    } else {
                        alert('Clear functionality is not available. Please try refreshing the page.');
                    }
                }
            });
            verboseLog('Clear & Reset button event listener attached successfully');
            return true;
        } else {
            console.error('Clear & Reset button not found in DOM');
            return false;
        }
    }
    
    // Try to attach the listener immediately
    if (!attachClearButtonListener()) {
        // If not found, retry after a short delay
        setTimeout(() => {
            if (!attachClearButtonListener()) {
                // Final retry after a longer delay
                setTimeout(() => {
                    attachClearButtonListener();
                }, 500);
            }
        }, 100);
    }

    // Add Esc key event listener for clear filters shortcut
    document.addEventListener('keydown', function(event) {
        // Check if Esc key is pressed and no modal is open
        if (event.key === 'Escape' || event.keyCode === 27) {
            // Check if any modal is currently open
            const openModals = document.querySelectorAll('.modal.show, .modal[style*="display: flex"], .modal[style*="display: block"]');
            const isModalOpen = openModals.length > 0;
            
            // Only clear filters if no modal is open
            if (!isModalOpen) {
                verboseLog('Esc key pressed - clearing filters');
                if (window.TagManager && TagManager.clearAllFilters) {
                    TagManager.clearAllFilters();
                } else if (window.TagManager && TagManager.clearSelected) {
                    TagManager.clearSelected();
                }
                event.preventDefault(); // Prevent default Esc behavior
            }
        }
    });
    verboseLog('Esc key shortcut for clear filters attached');

    // Add event listener for the undo button with retry mechanism
    function attachUndoButtonListener() {
        const undoButton = document.getElementById('undo-move-btn');
        if (undoButton) {
            // Remove any existing listeners to prevent duplicates
            const newButton = undoButton.cloneNode(true);
            undoButton.parentNode.replaceChild(newButton, undoButton);
            
            newButton.addEventListener('click', function() {
                verboseLog('Undo button clicked');
                if (window.TagManager && TagManager.undoMove) {
                    verboseLog('Calling TagManager.undoMove()');
                    TagManager.undoMove();
                } else {
                    console.error('TagManager or undoMove method not available');
                    // Fallback: try to call the undo function directly
                    if (typeof undoMove === 'function') {
                        verboseLog('Calling undoMove() directly');
                        undoMove();
                    } else {
                        console.error('No undo function available');
                        alert('Undo functionality is not available. Please try refreshing the page.');
                    }
                }
            });
            verboseLog('Undo button event listener attached successfully');
            return true;
        } else {
            console.error('Undo button not found in DOM');
            return false;
        }
    }
    
    // Try to attach the listener immediately
    if (!attachUndoButtonListener()) {
        // If not found, retry after a short delay
        setTimeout(() => {
            if (!attachUndoButtonListener()) {
                console.warn('Undo button still not found after retry');
            }
        }, 1000);
    }

    // Note: Select All event listeners are now handled in the TagManager._updateAvailableTags and updateSelectedTags methods
    // to ensure proper state management and prevent duplicate listeners
    
    // Fallback: ensure splash screen completes even if there are issues
    setTimeout(() => {
        if (AppLoadingSplash.isVisible) {
            verboseLog('Fallback: completing splash screen after timeout');
            AppLoadingSplash.stopAutoAdvance();
            AppLoadingSplash.complete();
        }
    }, 10000); // 10 second fallback
});

// Global functions for debugging
window.AppLoadingSplash = AppLoadingSplash;
window.emergencyHideSplash = () => AppLoadingSplash.emergencyHide();

// Global undo function as fallback
window.undoMove = async function() {
    verboseLog('Global undoMove function called');
    if (window.TagManager && TagManager.undoMove) {
        return TagManager.undoMove();
    } else {
        console.error('TagManager not available for undo');
        alert('Undo functionality is not available. Please try refreshing the page.');
    }
};

// Debug function to check undo stack status
window.checkUndoStack = async function() {
    try {
        const response = await fetch('/api/undo-move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.status === 400) {
            const errorData = await response.json();
            verboseLog('Undo stack status:', errorData.error);
            return errorData.error;
        } else {
            verboseLog('Undo stack has items available');
            return 'Has undo items';
        }
    } catch (error) {
        console.error('Error checking undo stack:', error);
        return 'Error checking undo stack';
    }
};

// Test function to manually trigger a move and then check undo
window.testUndoFunctionality = async function() {
    verboseLog('Testing undo functionality...');
    
    // First, check if there are any tags to move
    const availableCheckboxes = document.querySelectorAll('#availableTags input[type="checkbox"].tag-checkbox');
    if (availableCheckboxes.length === 0) {
        verboseLog('No available tags to test with');
        return;
    }
    
    // Check current undo stack
    verboseLog('Initial undo stack status:', await window.checkUndoStack());
    
    // Move one tag to selected
    const firstCheckbox = availableCheckboxes[0];
    firstCheckbox.checked = true;
    
    verboseLog('Moving tag:', firstCheckbox.value);
    
    // Trigger move to selected
    if (window.TagManager && TagManager.moveToSelected) {
        verboseLog('Calling TagManager.moveToSelected()...');
        await TagManager.moveToSelected();
        
        // Wait a moment, then check undo stack
        setTimeout(async () => {
            verboseLog('After move - undo stack status:', await window.checkUndoStack());
        }, 1000);
    } else {
        console.error('TagManager.moveToSelected not available');
    }
};

// Test function to check if move buttons are working
window.testMoveButtons = function() {
    verboseLog('Testing move buttons...');
    
    // Check if move buttons exist
    const moveToSelectedBtn = document.querySelector('button[onclick*="moveToSelected"]') || 
                              document.querySelector('button[title*="Move to Selected"]') ||
                              document.querySelector('button:contains(">")');
    
    const moveToAvailableBtn = document.querySelector('button[onclick*="moveToAvailable"]') || 
                               document.querySelector('button[title*="Move to Available"]') ||
                               document.querySelector('button:contains("<")');
    
    verboseLog('Move to Selected button found:', !!moveToSelectedBtn);
    verboseLog('Move to Available button found:', !!moveToAvailableBtn);
    
    // Check if TagManager is available
    verboseLog('TagManager available:', !!window.TagManager);
    verboseLog('TagManager.moveToSelected available:', !!(window.TagManager && window.TagManager.moveToSelected));
    verboseLog('TagManager.moveToAvailable available:', !!(window.TagManager && window.TagManager.moveToAvailable));
    
    // Check for available tags
    const availableCheckboxes = document.querySelectorAll('#availableTags input[type="checkbox"].tag-checkbox');
    verboseLog('Available checkboxes found:', availableCheckboxes.length);
    
    return {
        moveToSelectedBtn: !!moveToSelectedBtn,
        moveToAvailableBtn: !!moveToAvailableBtn,
        tagManager: !!window.TagManager,
        availableTags: availableCheckboxes.length
    };
};

// Function to clear stuck uploads
async function clearStuckUploads() {
    try {
        verboseLog('Clearing stuck uploads...');
        const response = await fetch('/api/clear-upload-status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        
        if (response.ok) {
            const result = await response.json();
            verboseLog('Upload status cleared:', result.message);
            
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
        // Cache DOM queries
        const cardHeader = document.querySelector('.card-header');
        if (!cardHeader) return;
        
        // Single optimized handler with requestAnimationFrame
        let rafId = null;
        const updateStickyState = () => {
            const headerRect = cardHeader.getBoundingClientRect();
            
            if (headerRect.bottom <= 0) {
                stickyFilterBar.classList.add('is-sticky');
            } else {
                stickyFilterBar.classList.remove('is-sticky');
            }
            
            rafId = null;
        };
        
        // Throttled scroll handler
        const handleScroll = () => {
            if (!rafId) {
                rafId = requestAnimationFrame(updateStickyState);
            }
        };
        
        // Use single scroll listener with passive flag for better performance
        window.addEventListener('scroll', handleScroll, { passive: true });
        tagList.addEventListener('scroll', handleScroll, { passive: true });
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
// Comprehensive app reset function
async function performFullAppReset() {
    verboseLog('🔄 Performing full app reset...');
    
    try {
        // 1. Clear all filters directly (don't call clearAllFilters to avoid recursion)
        const filterIds = ['vendorFilter', 'brandFilter', 'productTypeFilter', 'lineageFilter', 'weightFilter', 'dohFilter', 'highCbdFilter'];
        filterIds.forEach(filterId => {
            const filterElement = document.getElementById(filterId);
            if (filterElement) {
                filterElement.value = '';
                filterElement.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
        
        // 2. Clear all selected tags (handled locally to avoid recursion)
        if (window.TagManager) {
            if (TagManager.state && TagManager.state.selectedTags) {
                TagManager.state.selectedTags.clear();
            }
            if (TagManager.state) {
                TagManager.state.persistentSelectedTags = [];
            }
            if (TagManager.updateSelectedTags) {
                TagManager.updateSelectedTags([]);
            }
        }
        
        // 3. Clear all search fields
        document.querySelectorAll('input[type="text"]').forEach(el => {
            el.value = '';
            // Trigger input events to update any listeners
            el.dispatchEvent(new Event('input', { bubbles: true }));
        });
        
        // 4. Reset all filter dropdowns
        document.querySelectorAll('select').forEach(el => {
            el.selectedIndex = 0;
            // Trigger change events to update any listeners
            el.dispatchEvent(new Event('change', { bubbles: true }));
        });
        
        // 5. Clear all checkboxes
        document.querySelectorAll('input[type="checkbox"]').forEach(el => {
            el.checked = false;
            // Trigger change events to update any listeners
            el.dispatchEvent(new Event('change', { bubbles: true }));
        });
        
        // 6. Clear all textareas
        document.querySelectorAll('textarea').forEach(el => {
            el.value = '';
            el.dispatchEvent(new Event('input', { bubbles: true }));
        });
        
        // 7. Reset TagManager state completely
        if (window.TagManager) {
            // Clear all internal state
            TagManager.state.selectedTags.clear();
            TagManager.state.persistentSelectedTags = [];
            TagManager.state.filterCache = null;
            TagManager.state.originalFilterOptions = {};
            TagManager.state.lastFilterState = {};
            
            // Reset available tags display
            if (TagManager.efficientlyUpdateAvailableTagsDisplay) {
                TagManager.efficientlyUpdateAvailableTagsDisplay();
            }
            
            // Reset selected tags display
            if (TagManager.updateSelectedTags) {
                TagManager.updateSelectedTags([]);
            }
            
            // Update select all checkboxes
            if (TagManager.updateSelectAllCheckboxes) {
                TagManager.updateSelectAllCheckboxes();
            }
        }
        
        // 8. Clear browser storage
        if (window.localStorage) {
            localStorage.clear();
        }
        if (window.sessionStorage) {
            sessionStorage.clear();
        }
        
        // 9. Clear any cached data
        if (window.cache) {
            cache.clear();
        }
        
        // 10. Reset any global variables
        if (window.currentFile) {
            window.currentFile = null;
        }
        if (window.jsonMatchedTags) {
            window.jsonMatchedTags = [];
        }
        
        // 11. Clear any pending requests
        if (window.abortController) {
            window.abortController.abort();
        }
        window.abortController = new AbortController();
        
        // 12. Reset UI elements to initial state
        const availableTagsContainer = document.getElementById('availableTags');
        if (availableTagsContainer) {
            availableTagsContainer.innerHTML = '';
        }
        
        const selectedTagsContainer = document.getElementById('selectedTags');
        if (selectedTagsContainer) {
            selectedTagsContainer.innerHTML = '';
        }
        
        // 13. Clear any file info displays
        const fileInfoElements = document.querySelectorAll('.file-info, .upload-info, .data-info');
        fileInfoElements.forEach(el => {
            el.textContent = '';
            el.style.display = 'none';
        });
        
        // 14. Reset any progress indicators
        const progressBars = document.querySelectorAll('.progress-bar, .loading-bar');
        progressBars.forEach(el => {
            el.style.width = '0%';
            el.style.display = 'none';
        });
        
        // 15. Clear any error messages
        const errorElements = document.querySelectorAll('.alert-danger, .error-message, .warning-message');
        errorElements.forEach(el => {
            el.style.display = 'none';
            el.textContent = '';
        });
        
        // 16. Reset any success messages
        const successElements = document.querySelectorAll('.alert-success, .success-message');
        successElements.forEach(el => {
            el.style.display = 'none';
            el.textContent = '';
        });
        
        // 17. Clear any modal states
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.classList.remove('show');
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
        });
        
        // 18. Reset any tooltip states
        const tooltips = document.querySelectorAll('.tooltip');
        tooltips.forEach(tooltip => {
            tooltip.style.display = 'none';
        });
        
        // 19. Reset any dropdown states
        const dropdowns = document.querySelectorAll('.dropdown-menu');
        dropdowns.forEach(dropdown => {
            dropdown.classList.remove('show');
            dropdown.style.display = 'none';
        });
        
        // 20. Clear any JSON match data
        if (window.jsonMatchData) {
            window.jsonMatchData = null;
        }
        
        verboseLog('✅ Full app reset completed successfully');
        
        // Show success feedback
        if (window.showToast) {
            showToast('App reset completed', 'success');
        }
        
    } catch (error) {
        console.error('❌ Error during full app reset:', error);
        if (window.showToast) {
            showToast('Error during app reset', 'error');
        }
    }
}

// Call clearUIState after export or upload success
// Example: after successful AJAX response for export/upload
// clearUIState();

// Removed conflicting file info text initialization - now handled by checkForExistingData()

// Global function to clear stuck upload UI (can be called from browser console)
window.clearStuckUploadUI = function() {
    if (typeof TagManager !== 'undefined' && TagManager.forceClearUploadUI) {
        TagManager.forceClearUploadUI();
        verboseLog('Stuck upload UI cleared via global function');
    } else {
        console.error('TagManager not available');
    }
};

// Global function to check upload status
window.checkUploadStatus = function(filename) {
    fetch(`/api/upload-status?filename=${encodeURIComponent(filename)}`)
        .then(response => response.json())
        .then(data => {
            verboseLog('Upload status:', data);
        })
        .catch(error => {
            console.error('Error checking upload status:', error);
        });
};

// Event listeners for drag-and-drop reordering
document.addEventListener('selectedTagsReordered', function(event) {
    verboseLog('selectedTagsReordered event received:', event.detail);
    // This event is triggered when tags are reordered via drag-and-drop
    // The UI refresh is handled by the drag-and-drop manager
});

document.addEventListener('forceRefreshSelectedTags', function(event) {
    verboseLog('forceRefreshSelectedTags event received');
    // Force refresh the selected tags display
    if (window.TagManager && window.TagManager.fetchAndUpdateSelectedTags) {
        verboseLog('Forcing refresh of selected tags...');
        window.TagManager.fetchAndUpdateSelectedTags();
    }
});

// JSON Matching Function - Global function for JSON product matching
window.performJsonMatch = function() {
    const jsonUrlInput = document.getElementById('jsonUrlInput');
    const matchBtn = document.querySelector('#jsonMatchModal .btn-modern2');
    const resultsDiv = document.getElementById('jsonMatchResults');
    const matchCount = document.getElementById('matchCount');
    const matchedProductsList = document.getElementById('matchedProductsList');
    
    if (!jsonUrlInput || !matchBtn) {
        console.error('JSON match modal elements not found');
        return;
    }
    
    let jsonUrl = jsonUrlInput.value.trim();
    if (!jsonUrl) {
        console.error('Please enter a JSON URL first.');
        return;
    }

    // Validate URL format - support both HTTP URLs and data URLs
    // Also auto-prepend https:// if no protocol is specified
    if (!jsonUrl.startsWith('http://') && !jsonUrl.startsWith('https://') && !jsonUrl.startsWith('data:')) {
        // Auto-prepend https:// for URLs without protocol
        jsonUrl = 'https://' + jsonUrl;
        verboseLog('Auto-prepending https:// to URL:', jsonUrl);
    }
    
    // Final validation
    if (!/^(https?:\/\/|data:)/i.test(jsonUrl)) {
        console.error('Please enter a valid URL starting with http://, https://, or data:');
        return;
    }

    // Clear previous selected tags list before processing new match
    if (typeof TagManager !== 'undefined') {
        verboseLog('Clearing previous selected tags before JSON match');
        TagManager.state.persistentSelectedTags = [];
        TagManager.state.selectedTags = new Set();
        
        // Clear the selected tags display
        const selectedTagsContainer = document.getElementById('selectedTags');
        if (selectedTagsContainer) {
            selectedTagsContainer.innerHTML = '';
        }
        
        // Update tag counts
        TagManager.updateTagCount('selected', 0);
    }

    // Show loading state
    matchBtn.disabled = true;
    matchBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
    
    // Show progress message
    resultsDiv.classList.remove('d-none');
    matchCount.textContent = 'Processing...';
    matchedProductsList.innerHTML = '<div class="text-info">Matching products from JSON URL. This may take up to 2 minutes for large datasets. Progress will be logged in the browser console.</div>';

    // Add timeout to prevent hanging
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 600000); // 10 minutes timeout
    
    // Use the json-match endpoint
    fetch('/api/json-match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: String(jsonUrl) }),
        signal: controller.signal
    })
    .then(response => {
        if (!response.ok) {
            // Clone the response so we can read it multiple times if needed
            const responseClone = response.clone();
            return response.json().then(error => {
                // Handle both string and object error responses
                const errorMessage = typeof error === 'string' ? error : (error.error || 'JSON matching failed');
                throw new Error(errorMessage);
            }).catch(jsonError => {
                // If JSON parsing fails, try to get text response from the cloned response
                return responseClone.text().then(text => {
                    throw new Error(`Server error: ${text || 'Unknown error'}`);
                });
            });
        }
        return response.json().catch(jsonError => {
            console.error('JSON parsing error:', jsonError);
            console.error('Response status:', response.status);
            console.error('Response headers:', response.headers);
            
            // Clone the response before reading it to avoid "body stream already read" error
            const responseClone = response.clone();
            return responseClone.text().then(text => {
                console.error('Response text:', text);
                throw new Error(`Invalid JSON response from server: ${jsonError.message}. Response: ${text.substring(0, 200)}...`);
            }).catch(textError => {
                console.error('Error reading response text:', textError);
                throw new Error(`Invalid JSON response from server: ${jsonError.message}. Unable to read response text.`);
            });
        });
    })
    .then(matchResult => {
        // Safety check: ensure matchResult is an object
        if (typeof matchResult !== 'object' || matchResult === null) {
            console.error('Invalid matchResult:', matchResult);
            throw new Error('Invalid response format from server');
        }
        
        // Show results
        matchCount.textContent = matchResult.matched_count || 0;
        
        // Populate matched products list with note about where they were added
        if (matchResult.matched_names && matchResult.matched_names.length > 0) {
            matchedProductsList.innerHTML = `
                <div class="alert alert-success mb-3">
                    <strong>Success!</strong> ${matchResult.matched_count} products were matched and added to the <strong>Available Tags</strong> list.
                    <br>Please review the available tags and select the items you need.
                </div>
                <div class="mb-2"><strong>Matched Products:</strong></div>
                ${matchResult.matched_names
                    .map(product => `<div class="mb-1">• ${product}</div>`)
                    .join('')}
            `;
        } else {
            matchedProductsList.innerHTML = '<div class="text-muted">No specific product details available</div>';
        }
        
        resultsDiv.classList.remove('d-none');
        
        // Successfully matched products from JSON URL
        
        // Clear the input
        jsonUrlInput.value = '';
        
        // Refresh the UI with new data
        if (typeof TagManager !== 'undefined') {
            verboseLog('JSON matched products added to available tags for manual selection');
            verboseLog('Matched names:', matchResult.matched_names);
            verboseLog('JSON matched tags:', matchResult.json_matched_tags);
            
            // Update available tags with the new JSON matched items
            verboseLog('Updating available tags with JSON matched data:', {
                availableTagsCount: matchResult.available_tags ? matchResult.available_tags.length : 0,
                matchedCount: matchResult.matched_count,
                sampleTags: matchResult.available_tags ? matchResult.available_tags.slice(0, 3).map(t => t['Product Name*']) : []
            });
            
            // For JSON matching, we want to show JSON matched items by default
            // The backend sends all JSON matched items in available_tags
            verboseLog('JSON match response analysis:');
            verboseLog('- matched_count:', matchResult.matched_count);
            verboseLog('- available_tags length:', matchResult.available_tags ? matchResult.available_tags.length : 0);
            verboseLog('- json_matched_tags length:', matchResult.json_matched_tags ? matchResult.json_matched_tags.length : 0);
            
            // Use available_tags as the primary source (backend sets this to JSON matched items)
            let tagsToShow = matchResult.available_tags || [];
            
            // Fallback to json_matched_tags if available_tags is empty
            if (!tagsToShow || tagsToShow.length === 0) {
                verboseLog('available_tags is empty, falling back to json_matched_tags');
                tagsToShow = matchResult.json_matched_tags || [];
            }
            
            // Fallback to existing tags if both are empty
            if (!tagsToShow || tagsToShow.length === 0) {
                verboseLog('No JSON matched items found, showing existing tags');
                tagsToShow = TagManager.state.originalTags || [];
            }
            
            verboseLog(`Showing ${tagsToShow.length} items in available tags`);
            TagManager._updateAvailableTags(tagsToShow, null);
            
            // For JSON matching, we want to show all matched tags in available tags
            // Clear current selected tags first to ensure all JSON matched tags are visible
            TagManager.state.persistentSelectedTags = [];
            TagManager.state.selectedTags = new Set();
            
            // Clear the selected tags display
            const selectedTagsContainer = document.getElementById('selectedTags');
            if (selectedTagsContainer) {
                selectedTagsContainer.innerHTML = '';
            }
            
            // CRITICAL FIX: For JSON matched sessions, don't filter out selected tags
            // This ensures all 14 tags remain visible in the available list
            TagManager.state.isJsonMatchedSession = true;
            
            // CRITICAL FIX: Automatically select ALL JSON matched tags
            // This ensures all 14 tags are selected for generation
            if (tagsToShow && tagsToShow.length > 0) {
                // Select all available tags
                TagManager.state.persistentSelectedTags = tagsToShow.map(tag => tag['Product Name*'] || tag.ProductName || tag.Description || '');
                TagManager.state.selectedTags = new Set(TagManager.state.persistentSelectedTags);
                
                // Update the UI to reflect the selection
                TagManager.updateSelectedTags(tagsToShow);
                
                verboseLog(`✅ Auto-selected all ${TagManager.state.persistentSelectedTags.length} JSON matched tags`);
            }
            
            // Show a notification to the user
            const notificationDiv = document.createElement('div');
            notificationDiv.className = 'alert alert-success alert-dismissible fade show';
            notificationDiv.innerHTML = `
                <strong>JSON Matching Complete!</strong> 
                ${matchResult.matched_count} products were matched and are now available in the Available Tags list. 
                <strong>All ${matchResult.matched_count} tags have been automatically selected for you!</strong>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            // Insert the notification at the top of the page
            const container = document.querySelector('.container-fluid') || document.querySelector('.container');
            if (container) {
                container.insertBefore(notificationDiv, container.firstChild);
                
                // Auto-dismiss after 10 seconds
                setTimeout(() => {
                    if (notificationDiv.parentNode) {
                        notificationDiv.remove();
                    }
                }, 10000);
            }
            
            // Show the JSON filter toggle button
            if (typeof updateJsonFilterToggleVisibility === 'function') {
                updateJsonFilterToggleVisibility();
            }
            
            // Force update the toggle button visibility after a short delay to ensure backend state is updated
            setTimeout(() => {
                if (typeof updateJsonFilterToggleVisibility === 'function') {
                    updateJsonFilterToggleVisibility();
                }
            }, 1000);
            
            // CRITICAL FIX: Refresh filters after JSON match to ensure new products appear in filter dropdowns
            TagManager.fetchAndPopulateFilters().catch(error => {
                console.warn('Filter refresh after JSON match failed (non-critical):', error);
            });
        }
        
        verboseLog('Available tags updated with JSON matched items');
    })
    .catch(error => {
        console.error('JSON matching error:', error);
        
        // Show error message to user
        matchCount.textContent = 'Error';
        matchedProductsList.innerHTML = `
            <div class="alert alert-danger">
                <strong>Error:</strong> ${error.message}
            </div>
        `;
        resultsDiv.classList.remove('d-none');
    })
    .finally(() => {
        // Reset button state
        matchBtn.disabled = false;
        matchBtn.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="me-2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Match Products
        `;
        
        // Clear timeout
        clearTimeout(timeoutId);
    });
};

// Accessibility fix for JSON Match Modal
document.addEventListener('DOMContentLoaded', function() {
    const jsonMatchModal = document.getElementById('jsonMatchModal');
    if (jsonMatchModal) {
        // Store the element that had focus before the modal opened
        let previouslyFocusedElement = null;
        
        // Handle modal show event
        jsonMatchModal.addEventListener('show.bs.modal', function() {
            // Store the currently focused element
            previouslyFocusedElement = document.activeElement;
            
            // Ensure modal is properly accessible
            jsonMatchModal.removeAttribute('aria-hidden');
            jsonMatchModal.removeAttribute('inert');
            jsonMatchModal.setAttribute('aria-modal', 'true');
        });
        
        // Handle modal shown event
        jsonMatchModal.addEventListener('shown.bs.modal', function() {
            // Focus the first focusable element in the modal
            const firstFocusable = jsonMatchModal.querySelector('input, button, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (firstFocusable) {
                firstFocusable.focus();
            }
        });
        
        // Handle modal hide event
        jsonMatchModal.addEventListener('hide.bs.modal', function() {
            // Move focus away from any focused element inside the modal
            const focusedElement = jsonMatchModal.querySelector(':focus');
            if (focusedElement) {
                focusedElement.blur();
            }
        });
        
        // Handle modal hidden event
        jsonMatchModal.addEventListener('hidden.bs.modal', function() {
            // Set aria-hidden and inert after modal is fully hidden
            jsonMatchModal.setAttribute('aria-hidden', 'true');
            jsonMatchModal.setAttribute('inert', '');
            jsonMatchModal.removeAttribute('aria-modal');
            
            // Restore focus to the previously focused element
            if (previouslyFocusedElement && previouslyFocusedElement.focus) {
                // Use setTimeout to ensure the modal is fully hidden before restoring focus
                setTimeout(() => {
                    try {
                        previouslyFocusedElement.focus();
                    } catch (e) {
                        // If the previously focused element is no longer available, focus the body
                        document.body.focus();
                    }
                }, 100);
            }
        });
        
        // Handle close button clicks to ensure proper focus management
        const closeButtons = jsonMatchModal.querySelectorAll('[data-bs-dismiss="modal"]');
        closeButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Move focus away from the button before the modal starts hiding
                setTimeout(() => {
                    this.blur();
                }, 0);
            });
        });
    }
    
    // Also fix the JSON Inventory Modal
    const jsonInventoryModal = document.getElementById('jsonInventoryModal');
    if (jsonInventoryModal) {
        // Store the element that had focus before the modal opened
        let previouslyFocusedElement = null;
        
        // Handle modal show event
        jsonInventoryModal.addEventListener('show.bs.modal', function() {
            // Store the currently focused element
            previouslyFocusedElement = document.activeElement;
            
            // Ensure modal is properly accessible
            jsonInventoryModal.removeAttribute('aria-hidden');
            jsonInventoryModal.removeAttribute('inert');
            jsonInventoryModal.setAttribute('aria-modal', 'true');
        });
        
        // Handle modal shown event
        jsonInventoryModal.addEventListener('shown.bs.modal', function() {
            // Focus the first focusable element in the modal
            const firstFocusable = jsonInventoryModal.querySelector('input, button, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (firstFocusable) {
                firstFocusable.focus();
            }
        });
        
        // Handle modal hide event
        jsonInventoryModal.addEventListener('hide.bs.modal', function() {
            // Move focus away from any focused element inside the modal
            const focusedElement = jsonInventoryModal.querySelector(':focus');
            if (focusedElement) {
                focusedElement.blur();
            }
        });
        
        // Handle modal hidden event
        jsonInventoryModal.addEventListener('hidden.bs.modal', function() {
            // Set aria-hidden and inert after modal is fully hidden
            jsonInventoryModal.setAttribute('aria-hidden', 'true');
            jsonInventoryModal.setAttribute('inert', '');
            jsonInventoryModal.removeAttribute('aria-modal');
            
            // Restore focus to the previously focused element
            if (previouslyFocusedElement && previouslyFocusedElement.focus) {
                // Use setTimeout to ensure the modal is fully hidden before restoring focus
                setTimeout(() => {
                    try {
                        previouslyFocusedElement.focus();
                    } catch (e) {
                        // If the previously focused element is no longer available, focus the body
                        document.body.focus();
                    }
                }, 100);
            }
        });
        
        // Handle close button clicks to ensure proper focus management
        const closeButtons = jsonInventoryModal.querySelectorAll('[data-bs-dismiss="modal"]');
        closeButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Move focus away from the button before the modal starts hiding
                setTimeout(() => {
                    this.blur();
                }, 0);
            });
        });
    }
});

// JSON Filter Toggle Function
window.toggleJsonFilter = function() {
    const toggleBtn = document.getElementById('jsonFilterToggleBtn');
    const toggleText = document.getElementById('jsonFilterToggleText');
    
    if (!toggleBtn) {
        console.error('JSON filter toggle button not found');
        return;
    }
    
    // Show loading state
    toggleBtn.disabled = true;
    const originalText = toggleText.textContent;
    toggleText.textContent = 'Toggling...';
    
    // Call the toggle API
    fetch('/api/toggle-json-filter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filter_mode: 'toggle' })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            verboseLog('JSON filter toggled successfully:', data);
            verboseLog('Available tags count:', data.available_tags ? data.available_tags.length : 0);
            
            // Update the available tags with the new filtered data
            if (typeof TagManager !== 'undefined' && data.available_tags) {
                verboseLog('Updating TagManager with new tags...');
                
                // Update the TagManager state with the new tags
                TagManager.state.originalTags = [...data.available_tags];
                TagManager.state.tags = [...data.available_tags];
                
                verboseLog('TagManager state updated. Original tags:', TagManager.state.originalTags.length);
                verboseLog('TagManager state updated. Current tags:', TagManager.state.tags.length);
                
                // Use requestAnimationFrame to ensure DOM is ready before updating
                requestAnimationFrame(() => {
                    // Call the update function to refresh the display
                    TagManager._updateAvailableTags(data.available_tags, null);
                    TagManager.saveAvailableTagsToCache(data.available_tags || []);
                    TagManager.state.hydratedFromCache = false;
                    
                    // Update tag counts
                    TagManager.updateTagCount('available', data.available_tags.length);
                    
                    verboseLog('TagManager display updated successfully');
                });
            } else {
                console.warn('TagManager not available or no available_tags in response');
            }
            
            // Update the toggle button text
            toggleText.textContent = data.mode_name || 'Toggle Filter';
            
            // Update the filter button visibility
            if (typeof updateJsonFilterToggleVisibility === 'function') {
                updateJsonFilterToggleVisibility();
            }
            
            // Show notification
            const notificationDiv = document.createElement('div');
            notificationDiv.className = 'alert alert-info alert-dismissible fade show';
            notificationDiv.innerHTML = `
                <strong>Filter Updated!</strong> 
                Now showing ${data.available_count} items in ${data.mode_name}.
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            // Insert notification at the top of the main content area
            const mainContent = document.querySelector('.container-fluid') || document.querySelector('.container');
            if (mainContent) {
                mainContent.insertBefore(notificationDiv, mainContent.firstChild);
            }
            
            // Auto-dismiss notification after 5 seconds
            setTimeout(() => {
                if (notificationDiv.parentNode) {
                    notificationDiv.remove();
                }
            }, 5000);
            
        } else {
            throw new Error(data.error || 'Toggle failed');
        }
    })
    .catch(error => {
        console.error('JSON filter toggle error:', error);
        console.error('Error details:', {
            message: error.message,
            stack: error.stack,
            name: error.name
        });
        
        // Show error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.innerHTML = `
            <strong>Filter Toggle Error!</strong> 
            ${error.message || 'An unknown error occurred while toggling the filter.'}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert error notification at the top of the main content area
        const mainContent = document.querySelector('.container-fluid') || document.querySelector('.container');
        if (mainContent) {
            mainContent.insertBefore(errorDiv, mainContent.firstChild);
        }
        
        // Reset button text
        toggleText.textContent = originalText;
        
        // Auto-dismiss error notification after 8 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 8000);
    })
    .finally(() => {
        // Reset button state
        toggleBtn.disabled = false;
    });
};

// Function to show/hide JSON filter toggle button based on filter status
window.updateJsonFilterToggleVisibility = function() {
    fetch('/api/get-filter-status')
        .then(response => response.json())
        .then(data => {
            const toggleBtn = document.getElementById('jsonFilterToggleBtn');
            const toggleText = document.getElementById('jsonFilterToggleText');
            
            if (toggleBtn && toggleText) {
                if (data.can_toggle) {
                    toggleBtn.style.display = 'block';
                    toggleText.textContent = data.current_mode === 'json_matched' ? 'Show Full List' : 'Show JSON Matched';
                } else {
                    toggleBtn.style.display = 'none';
                }
            }
        })
        .catch(error => {
            console.error('Error checking filter status:', error);
        });
};

// Duplicate error handlers removed - using the ones at the top of the file

// TagManager is already initialized in the main DOMContentLoaded event listener above
// This duplicate initialization has been removed to prevent conflicts

// Add click event listener to title header for page reload
document.addEventListener('DOMContentLoaded', function() {
    const titleElement = document.querySelector('.vibrant-title');
    if (titleElement) {
        titleElement.style.cursor = 'pointer';
        titleElement.title = 'Click to reload the application';
        
        titleElement.addEventListener('click', function() {
            // Add a subtle visual feedback
            titleElement.style.opacity = '0.7';
            titleElement.style.transform = 'scale(0.98)';
            
            // Reset visual state after a brief moment
            setTimeout(() => {
                titleElement.style.opacity = '1';
                titleElement.style.transform = 'scale(1)';
            }, 150);
            
            // Reload the page after a brief delay for visual feedback
            setTimeout(() => {
                window.location.reload();
            }, 200);
        });
    }
});