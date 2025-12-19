// Detect Windows platform for optimizations
const isWindows = navigator.platform.toLowerCase().includes('win') ||
                 navigator.userAgent.toLowerCase().includes('windows');

// Fast reload mode: set localStorage.setItem('fastReload', 'true') to suppress
// heavy logging and some re-inits during refresh.
const FAST_RELOAD_MODE = window.localStorage?.getItem('fastReload') === 'true';
window.FAST_RELOAD_MODE = FAST_RELOAD_MODE;

// Centralized debug logging toggle (disabled when fast reload is on)
const TAG_MANAGER_DEBUG_ENABLED = !FAST_RELOAD_MODE && Boolean(
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
    // CRITICAL FIX: Remove continuous repaint loop - it causes flashing/glitching
    // Instead, only enable hardware acceleration for smoother rendering
    if (typeof document.documentElement.style.transition !== 'undefined') {
        // Enable hardware acceleration to reduce repaints without continuous loop
        document.body.style.transform = 'translateZ(0)';
        document.body.style.willChange = 'auto'; // Changed from 'contents' to 'auto' to reduce repaints
    }
    
    verboseLog('Windows performance optimizations enabled (hardware acceleration only)');
}

// CRITICAL: Prevent multiple simultaneous page reloads
let _reloadInProgress = false;

// CRITICAL FIX: Emergency kill switch to stop all operations if browser freezes
window.EMERGENCY_KILL_SWITCH = false;
window.enableEmergencyKillSwitch = function() {
    console.error('🚨 EMERGENCY KILL SWITCH ACTIVATED - Stopping all operations');
    window.EMERGENCY_KILL_SWITCH = true;
    
    // Clear all timers
    const highestTimeoutId = setTimeout(() => {}, 0);
    for (let i = 0; i < highestTimeoutId; i++) {
        clearTimeout(i);
    }
    
    // Clear all intervals
    const highestIntervalId = setInterval(() => {}, 99999);
    for (let i = 0; i < highestIntervalId; i++) {
        clearInterval(i);
    }
    
    // Stop all TagManager operations
    if (window.TagManager) {
        window.TagManager._checkingExistingData = false;
        window.TagManager._initializing = false;
        window.TagManager.state.loading = false;
        if (window.TagManager.state.initialDataRetryTimer) {
            clearTimeout(window.TagManager.state.initialDataRetryTimer);
            window.TagManager.state.initialDataRetryTimer = null;
        }
    }
    
    console.log('✅ Emergency kill switch activated - all operations stopped');
};

// Make kill switch accessible via console: enableEmergencyKillSwitch()
let _reloadTimeout = null;

const safeReload = (delay = 0) => {
    // Prevent multiple reloads
    if (_reloadInProgress) {
        console.log('⏭️ Reload already in progress, skipping duplicate reload request');
        return;
    }
    
    _reloadInProgress = true;
    
    // Clear any existing reload timeout
    if (_reloadTimeout) {
        clearTimeout(_reloadTimeout);
        _reloadTimeout = null;
    }
    
    const doReload = () => {
        console.log('🔄 Executing safe page reload...');
        _reloadInProgress = false;
        // Use original reload method to bypass any interceptors
        const originalReload = window.location.reload.bind(window.location);
        originalReload();
    };
    
    if (delay > 0) {
        _reloadTimeout = setTimeout(doReload, delay);
    } else {
        doReload();
    }
};

// Make safeReload available globally
window.safeReload = safeReload;
window._reloadInProgress = false; // Make flag accessible

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
  "pre-roll": "Pre-Roll",  // Normalize to title case for display
  "Pre-Roll": "Pre-Roll",  // Keep title case
  "preroll": "Pre-Roll",  // Map variations to title case
  "Infused Pre-Roll": "Infused Pre-Roll",  // Keep title case
  "infused pre-roll": "Infused Pre-Roll",  // Map lowercase to title case
  "infused preroll": "Infused Pre-Roll",  // Map variations to title case
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
        // Check if we're on PythonAnywhere (including custom domains like agtpricetags.com)
        return window.location.hostname.includes('pythonanywhere.com') ||
               window.location.hostname.includes('agtpricetags.com');
    }
    
    // Choose upload endpoint based on environment
    function getUploadEndpoint() {
        // ALWAYS use instant upload for maximum speed
        return '/upload-instant';
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
            console.log('⚡ Emergency hide splash - 5 second timeout');
            this.emergencyHide();
        }, 5000); // Reduced from 7000 to 5000 for faster recovery
        
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
            splash.classList.add('fade-out');
        }
        
        if (mainContent) {
            mainContent.style.opacity = '1';
            // CRITICAL FIX: Prevent visual glitches by ensuring smooth transition
            if (mainContent) {
                mainContent.style.display = 'block';
                mainContent.style.visibility = 'visible';
                mainContent.style.opacity = '1';
                mainContent.classList.add('loaded');
            }
            mainContent.classList.add('loaded');
        }
        
        // Try to initialize TagManager if it hasn't been initialized yet
        if (window.TagManager && typeof window.TagManager.init === 'function') {
            if (!window.TagManager.state || !window.TagManager.state.initialized) {
                verboseLog('Emergency: Attempting to initialize TagManager from emergencyHide');
                try {
                    window.TagManager.init();
                } catch (e) {
                    console.error('Emergency TagManager.init() from emergencyHide failed:', e);
                }
            }
        }
    }
};

// CRITICAL FIX: Expose TagManager to window immediately when defined
// This allows other scripts to check for TagManager even before it's fully initialized
const TagManager = {
    CACHE_TTL_MS: 10 * 60 * 1000, // 10 minutes
    state: {
        selectedTags: new Set(),
        isClearing: false, // Flag to prevent multiple simultaneous clear operations
        persistentSelectedTags: [], // Array to maintain order
        _selectedTagsSet: new Set(), // PERFORMANCE: Set for O(1) lookups instead of array.includes()
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
        activeFilteredTags: null, // Currently applied filter result (for search)
        updateAvailableTagsTimer: null,
        isSearching: false,
        initialDataAttempts: 0,
        initialDataRetryTimer: null,
        hydratedFromCache: false,
        forceFullAvailableTagRender: true,
        simplifiedAvailableTagsActive: false,
        // Memory optimization flags
        _memoryOptimized: true,
        _lastCleanup: Date.now(),
        // Local undo stack for immediate undo
        localUndoStack: [],
        // Redo stack for snapshot-based redo
        redoSnapshotStack: []
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
            
            // CRITICAL FIX: Don't load from cache if no Excel file is uploaded
            // Only load cache when there's an actual Excel file loaded
            const file = (window.sessionStorage && (sessionStorage.getItem('uploaded_filename') || sessionStorage.getItem('file_path'))) || null;
            if (!file || file === 'nofile' || file === '' || file === 'database') {
                console.log('❌ No Excel file uploaded, skipping cache load');
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
        
        // CRITICAL FIX: Don't load from cache if no Excel file is uploaded
        // Only hydrate cache when there's an actual Excel file loaded
        const file = (window.sessionStorage && (sessionStorage.getItem('uploaded_filename') || sessionStorage.getItem('file_path'))) || null;
        if (!file || file === 'nofile' || file === '' || file === 'database') {
            console.log('❌ No Excel file uploaded, skipping cache hydration');
            return false;
        }
        
        // CRITICAL FIX: On page reload, check if we recently updated lineage
        // If so, skip cache to ensure we get fresh lineage data from database
        const recentLineageUpdate = sessionStorage.getItem('lastLineageUpdateTime');
        if (recentLineageUpdate) {
            const timeSinceUpdate = Date.now() - parseInt(recentLineageUpdate, 10);
            // If lineage was updated within last 2 minutes, skip cache to get fresh data
            if (timeSinceUpdate < 120000) {
                console.log('🔄 Recent lineage update detected, skipping cache to fetch fresh data...');
                sessionStorage.removeItem('lastLineageUpdateTime'); // Clear after use
                return false; // Force fresh fetch
            }
        }
        
        const cachedTags = this.loadAvailableTagsFromCache();
        if (cachedTags && cachedTags.length) {
            console.log(`⚡ INSTANT LOAD: Hydrating ${cachedTags.length} tags from cache`);
            this.state.hydratedFromCache = true;
            this.state.forceFullAvailableTagRender = true;
            this.state.simplifiedAvailableTagsActive = false;
            this.state.tags = [...cachedTags];
            this.state.originalTags = [...cachedTags];
            
            // CRITICAL FIX: Hide splash BEFORE rendering to prevent visual glitches
            if (this.hideActionSplash) {
                this.hideActionSplash();
            }
            if (typeof AppLoadingSplash !== 'undefined' && AppLoadingSplash.isVisible) {
                AppLoadingSplash.stopAutoAdvance();
                AppLoadingSplash.complete();
            }
            
            // CRITICAL FIX: Use requestAnimationFrame to ensure immediate render
            requestAnimationFrame(() => {
                this._updateAvailableTags(cachedTags, null);
                console.log(`✅ INSTANT LOAD: ${cachedTags.length} tags rendered from cache`);

                // PERFORMANCE FIX: Use fast_load for background refresh (non-blocking)
                // This makes page reloads instant while still updating in background
                this._refreshLineageFromDatabase(cachedTags).then(() => {
                    console.log('✅ Background lineage check complete (fast mode)');
                }).catch(err => {
                    console.warn('⚠️ Background lineage check failed (non-critical):', err);
                });
            });
            return true;
        }
        return false;
    },

    // Helper method to refresh lineage from database
    async _refreshLineageFromDatabase(tags) {
        const timestamp = Date.now();
        try {
            // PERFORMANCE FIX: Use fast_load=1 to avoid expensive database queries on page reload
            // The cached lineage is already fresh enough for display purposes
            // Only use fast_load=0 if user explicitly requested lineage update
            const lineageResponse = await fetch(`/api/available-tags?t=${timestamp}&fast_load=1`, {
                signal: AbortSignal.timeout(5000) // 5 second timeout (reduced from 30s)
            });
            if (lineageResponse.ok) {
                const lineageData = await lineageResponse.json();
                const freshTags = lineageData.tags || lineageData;
                if (Array.isArray(freshTags) && freshTags.length > 0) {
                    // Build lineage map from fresh database data
                    const lineageMap = new Map();
                    freshTags.forEach(tag => {
                        const name = tag['Product Name*'] || tag.ProductName;
                        if (name) {
                            const dbLineage = tag.canonical_lineage || tag.currentLineage || tag.Lineage;
                            if (dbLineage) {
                                // CRITICAL: Normalize lineage value using consistent helper function
                                const normalizedLineage = (typeof window.normalizeLineageValue !== 'undefined') 
                                    ? window.normalizeLineageValue(dbLineage)
                                    : dbLineage.toString().trim().toUpperCase();
                                lineageMap.set(name, normalizedLineage);
                            }
                        }
                    });
                    
                    // Update tags with fresh lineage
                    let updatedCount = 0;
                    const tagsToUpdate = tags || this.state.tags;
                    tagsToUpdate.forEach(tag => {
                        const name = tag['Product Name*'] || tag.ProductName;
                        if (name && lineageMap.has(name)) {
                            const dbLineage = lineageMap.get(name);
                            // CRITICAL: Normalize old lineage for comparison
                            const oldLineageRaw = tag.canonical_lineage || tag.currentLineage || tag.Lineage || '';
                            const oldLineage = (typeof window.normalizeLineageValue !== 'undefined')
                                ? window.normalizeLineageValue(oldLineageRaw)
                                : oldLineageRaw.toString().trim().toUpperCase();
                            if (oldLineage !== dbLineage) {
                                tag.canonical_lineage = dbLineage;
                                tag.currentLineage = dbLineage;
                                tag.Lineage = dbLineage;
                                tag.lineage = dbLineage.toLowerCase();
                                updatedCount++;
                                console.log(`🔄 Updated lineage for "${name}": "${oldLineage}" → "${dbLineage}"`);
                            } else {
                                // Ensure fields are set even if values match
                                tag.canonical_lineage = dbLineage;
                                tag.currentLineage = dbLineage;
                                tag.Lineage = dbLineage;
                                tag.lineage = dbLineage.toLowerCase();
                            }
                        }
                    });
                    
                    // Also update originalTags
                    if (this.state.originalTags) {
                        this.state.originalTags.forEach(tag => {
                            const name = tag['Product Name*'] || tag.ProductName;
                            if (name && lineageMap.has(name)) {
                                const dbLineage = lineageMap.get(name);
                                tag.canonical_lineage = dbLineage;
                                tag.currentLineage = dbLineage;
                                tag.Lineage = dbLineage;
                                tag.lineage = dbLineage.toLowerCase();
                            }
                        });
                    }
                    
                    // Update state
                    this.state.tags = [...tagsToUpdate];
                    
                    if (updatedCount > 0) {
                        console.log(`✅ Refreshed lineage for ${updatedCount} tags from database`);
                        // Re-render with updated lineage
                        this._updateAvailableTags(this.state.tags, null);
                    } else {
                        console.log(`✅ Lineage already up-to-date (verified ${freshTags.length} tags)`);
                    }
                }
            }
        } catch (error) {
            console.warn('⚠️ Failed to refresh lineage from database:', error);
            throw error;
        }
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
        // PERFORMANCE: Use Map lookup for O(1) instead of array.find() which is O(n)
        // This function is called frequently, so O(1) lookups provide massive performance boost
        return this.state.persistentSelectedTags
            .map(name => {
                // Try Map lookup first (fastest - O(1))
                let tag = this._tagLookupMap?.get(name);
                
                // If not in Map, fallback to originalTags (only if Map wasn't built yet)
                if (!tag && this.state.originalTags) {
                    tag = this.state.originalTags.find(t => t['Product Name*'] === name);
                }
                
                // Last resort: current tags (filtered view)
                if (!tag && this.state.tags) {
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
            })
            .filter(Boolean);
    },

    clearInitialDataRetry() {
        if (this.state.initialDataRetryTimer) {
            clearTimeout(this.state.initialDataRetryTimer);
            this.state.initialDataRetryTimer = null;
        }
        this.state.initialDataAttempts = 0;
    },

    scheduleInitialDataRetry(reason = 'unknown') {
        // CRITICAL FIX: Check emergency kill switch first
        if (window.EMERGENCY_KILL_SWITCH) {
            console.error('🚨 EMERGENCY KILL SWITCH ACTIVE - Stopping retry scheduling');
            return;
        }
        
        // CRITICAL FIX: Prevent infinite retry loops that freeze the browser
        const delays = Array.isArray(this.initialDataRetryDelays) && this.initialDataRetryDelays.length > 0
            ? this.initialDataRetryDelays
            : [2000];
        const maxAttempts = delays.length + 1;
        const attemptsSoFar = this.state.initialDataAttempts || 0;

        // CRITICAL FIX: Hard limit to prevent infinite loops - never retry more than 5 times total
        const ABSOLUTE_MAX_ATTEMPTS = 5;
        if (attemptsSoFar >= ABSOLUTE_MAX_ATTEMPTS) {
            console.error(`[InitialData] ABSOLUTE MAX ATTEMPTS (${ABSOLUTE_MAX_ATTEMPTS}) reached - STOPPING ALL RETRIES to prevent browser freeze. Last reason: ${reason}`);
            // Clear any pending timers
            if (this.state.initialDataRetryTimer) {
                clearTimeout(this.state.initialDataRetryTimer);
                this.state.initialDataRetryTimer = null;
            }
            // Reset attempts counter to prevent further retries
            this.state.initialDataAttempts = ABSOLUTE_MAX_ATTEMPTS;
            return;
        }

        if (attemptsSoFar >= maxAttempts) {
            console.warn(`[InitialData] Max attempts (${maxAttempts}) reached; not scheduling retry. Last reason: ${reason}`);
            return;
        }

        // CRITICAL FIX: Prevent multiple retry timers from running simultaneously
        if (this.state.initialDataRetryTimer) {
            console.warn(`[InitialData] Retry timer already exists - clearing previous timer to prevent duplicate retries`);
            clearTimeout(this.state.initialDataRetryTimer);
            this.state.initialDataRetryTimer = null;
        }

        // CRITICAL FIX: Prevent retry if checkForExistingData is already running
        if (this._checkingExistingData) {
            console.warn(`[InitialData] checkForExistingData already in progress - skipping retry to prevent concurrent calls`);
            return;
        }

        const delayIndex = Math.max(0, Math.min(attemptsSoFar - 1, delays.length - 1));
        const delay = delays[Math.max(0, delayIndex)] || 2000;
        const nextAttempt = attemptsSoFar + 1;

        verboseLog(`[InitialData] Scheduling retry ${nextAttempt}/${maxAttempts} in ${delay}ms (reason: ${reason})`);

        const self = this;
        this.state.initialDataRetryTimer = setTimeout(function() {
            // CRITICAL FIX: Check if still needed before retrying
            if (self.state.initialized || self._checkingExistingData) {
                console.log(`[InitialData] Skipping retry - already initialized or check in progress`);
                self.state.initialDataRetryTimer = null;
                return;
            }
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
            this.state._selectedTagsSet = new Set(); // PERFORMANCE: Reset Set when clearing tags
            this.state.tags = [];
            this.state.originalTags = [];
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
            // Clear redo stack when making a new selection (can't redo after new action)
            if (this.state.redoStack) {
                this.state.redoStack = [];
            }
            if (this.state.redoSnapshotStack) {
                this.state.redoSnapshotStack = [];
            }

            // IMMEDIATE: Save to local undo stack for instant undo
            if (!this.state.localUndoStack) {
                this.state.localUndoStack = [];
            }
            
            // PERFORMANCE: Use Set for O(1) lookup instead of O(n) .includes()
            const selectedSet = new Set(this.state.persistentSelectedTags);
            
            // Save current state locally
            const currentState = {
                selected_tag_names: [...this.state.persistentSelectedTags],
                available_tag_names: this.state.tags
                    .filter(tag => !selectedSet.has(tag['Product Name*']))
                    .map(tag => tag['Product Name*']),
                action_type: actionType,
                timestamp: new Date().toISOString()
            };
            
            this.state.localUndoStack.push(currentState);
            // Limit local undo stack size
            if (this.state.localUndoStack.length > 5) {
                this.state.localUndoStack = this.state.localUndoStack.slice(-5);
            }
            
            verboseLog(`💾 Saved selection state for undo - Action: ${actionType}, Stack size: ${this.state.localUndoStack.length}, Selected tags: ${currentState.selected_tag_names.length}`);
            
            // Background: Also save to backend (non-blocking)
            // Use fetch instead of sendBeacon for better reliability and error handling
            const payload = JSON.stringify({
                action_type: actionType,
                ...extraPayload
            });
            
            // Always use fetch with keepalive for better reliability
            // sendBeacon doesn't support proper error handling
            fetch('/api/save-selection-state', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: payload,
                keepalive: true  // Ensures request completes even if page is unloading
            }).then(response => {
                if (!response.ok) {
                    verboseLog(`⚠️ Failed to save selection state for undo: ${response.status} ${response.statusText}`);
                } else {
                    verboseLog('✅ Selection state saved successfully to backend for undo');
                }
            }).catch(error => {
                verboseLog('⚠️ Failed to save selection state for undo:', error);
            });
        } catch (error) {
            console.error('❌ Error saving selection state for undo:', error);
        }
    },

    _extractFiltersFromTags(tags) {
        // Extract unique filter values from tags array
        const vendors = new Set();
        const brands = new Set();
        const productTypes = new Set();
        const lineages = new Set();
        const weights = new Set();
        const strains = new Set();
        const doh = new Set();
        const highCbd = new Set();

        tags.forEach(tag => {
            if (tag.Vendor) vendors.add(tag.Vendor);
            if (tag.ProductBrand || tag['Product Brand']) brands.add(tag.ProductBrand || tag['Product Brand']);
            if (tag.ProductType || tag['Product Type*']) productTypes.add(tag.ProductType || tag['Product Type*']);
            if (tag.Lineage) lineages.add(tag.Lineage);
            if (tag.WeightUnits || tag.CombinedWeight) weights.add(tag.WeightUnits || tag.CombinedWeight);
            if (tag.ProductStrain || tag['Product Strain']) strains.add(tag.ProductStrain || tag['Product Strain']);
            if (tag.DOH || tag['DOH Compliant (Yes/No)']) doh.add(tag.DOH || tag['DOH Compliant (Yes/No)']);
            if (tag.Ratio) highCbd.add(tag.Ratio);
        });

        return {
            vendor: Array.from(vendors).filter(Boolean).sort(),
            brand: Array.from(brands).filter(Boolean).sort(),
            productType: Array.from(productTypes).filter(Boolean).sort(),
            lineage: Array.from(lineages).filter(Boolean).sort(),
            weight: Array.from(weights).filter(Boolean).sort(),
            strain: Array.from(strains).filter(Boolean).sort(),
            doh: Array.from(doh).filter(Boolean).sort(),
            highCbd: Array.from(highCbd).filter(Boolean).sort()
        };
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
                // Special handling for High CBD filter - High CBD Products should come first
                if (filterType === 'highCbd') {
                    if (a === 'High CBD Products') return -1;
                    if (b === 'High CBD Products') return 1;
                    if (a === 'Non-High CBD Products') return 1;
                    if (b === 'Non-High CBD Products') return -1;
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
            this.state.activeFilteredTags = null;
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
            this.state.activeFilteredTags = this.state.filterCache.result || null;
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
        
        // If we don't have any tags to filter, log warning but don't fail silently
        if (tagsToFilter.length === 0) {
            console.warn('No tags available for filtering - originalTags:', this.state.originalTags.length, 'tags:', this.state.tags.length);
            // Don't return early - allow filter to run with empty array so UI updates correctly
            // This prevents filters from appearing broken when tags are still loading
        }
        
        verboseLog('applyFilters - tagsToFilter length:', tagsToFilter.length);
        verboseLog('applyFilters - first tag sample:', tagsToFilter[0]);
        
        const filteredTags = tagsToFilter.filter(tag => {
            // Check vendor filter - only apply if not empty and not "All"
            if (vendorFilter && vendorFilter.trim() !== '' && vendorFilter.toLowerCase() !== 'all') {
                // Check multiple possible vendor field names
                const tagVendor = (tag['Vendor/Supplier*'] || tag['Vendor/Supplier'] || tag.Vendor || tag.vendor || '').toString().trim();
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
                
                // Normalize DOH values for comparison
                // Map common variations: "Yes" -> "DOH", "No" -> "NONE"
                let normalizedTagDoh = tagDoh;
                if (tagDoh === 'YES') {
                    normalizedTagDoh = 'DOH';
                } else if (tagDoh === 'NO') {
                    normalizedTagDoh = 'NONE';
                }
                
                // Check if filter matches (exact match or normalized match)
                if (normalizedTagDoh !== filterDoh && tagDoh !== filterDoh) {
                    return false;
                }
            }
            
            // Check High CBD filter - only apply if not empty and not "All"
            if (highCbdFilter && highCbdFilter.trim() !== '' && highCbdFilter.toLowerCase() !== 'all') {
                const tagProductType = (tag.productType || tag['Product Type*'] || '').toString().trim().toLowerCase();
                // Check for all high CBD variations: "high cbd", "doh high cbd", etc.
                const isHighCbd = tagProductType.startsWith('high cbd') || tagProductType.includes('doh high cbd');
                
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
            vendorFilter: vendorFilter,
            brandFilter: brandFilter,
            lineageFilter: lineageFilter,
            weightFilter: weightFilter,
            dohFilter: dohFilter,
            highCbdFilter: highCbdFilter,
            prerollTags: filteredTags.filter(tag => {
                const tagProductType = (tag['Product Type*'] || tag.productType || '').toString().trim();
                const normalizedType = normalizeProductType(tagProductType);
                return normalizedType.toLowerCase() === 'pre-roll';
            }).length
        });
        
        // If filtering resulted in empty array but we had tags to filter, log warning
        if (filteredTags.length === 0 && tagsToFilter.length > 0) {
            console.warn('🔍 Filter resulted in 0 tags but had', tagsToFilter.length, 'tags to filter. Active filters:', {
                vendorFilter, brandFilter, productTypeFilter, lineageFilter, weightFilter, dohFilter, highCbdFilter
            });
        }
        
        // Cache the results
        this.state.filterCache = {
            key: filterKey,
            result: filteredTags
        };
        // Track the currently active filtered set so searches respect filters
        this.state.activeFilteredTags = filteredTags;
        
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
        // CRITICAL FIX: Use getSelectedTagObjects() which properly checks all sources (Map, originalTags, tags)
        // This prevents tags from disappearing when filters are active
        const selectedTagObjects = this.getSelectedTagObjects();
        this.updateSelectedTags(selectedTagObjects);
        this.renderActiveFilters();
        // USER PREFERENCE: Scroll to top after filter update
        requestAnimationFrame(() => {
            this._scrollAvailableTagsToTop();
        });
    },

    handleSearch(listId, searchInputId) {
        // PERFORMANCE FIX: Use requestAnimationFrame for smoother updates
        return requestAnimationFrame(() => {
            const searchInput = document.getElementById(searchInputId);
            if (!searchInput) return false;
            
            const searchTerm = searchInput.value.toLowerCase().trim();

            // Choose which tags to filter
            let tags = [];
            if (listId === 'availableTags') {
                // Respect current filters: fall back to original if no active filters
                const filtered = (this.state.activeFilteredTags && this.state.activeFilteredTags.length > 0)
                    ? this.state.activeFilteredTags
                    : (this.state.filterCache && this.state.filterCache.result ? this.state.filterCache.result : null);
                tags = filtered || this.state.originalTags || [];
            } else if (listId === 'selectedTags') {
                tags = Array.from(this.state.selectedTags).map(name =>
                    this.state.originalTags.find(t => t['Product Name*'] === name)
                ).filter(Boolean);
            }

            if (!searchTerm) {
                // Restore full list
                if (listId === 'availableTags') {
                    // If filters are active, restore the filtered list; otherwise show all
                    const base = (this.state.activeFilteredTags && this.state.activeFilteredTags.length > 0)
                        ? this.state.activeFilteredTags
                        : (this.state.filterCache && this.state.filterCache.result ? this.state.filterCache.result : null);
                    this.debouncedUpdateAvailableTags(this.state.originalTags, base || null);
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
                requestAnimationFrame(() => {
                    const availableTagsContainer = document.getElementById('availableTags');
                    if (availableTagsContainer) {
                        availableTagsContainer.scrollTop = 0;
                    }
                });
                // Ensure groups are expanded while searching
                setTimeout(() => {
                    this.expandAllTagGroups();
                }, 120);
            } else if (listId === 'selectedTags') {
                this.updateSelectedTags(filteredTags);
                // Scroll to top of selected tags list after search
                requestAnimationFrame(() => {
                    const selectedTagsContainer = document.getElementById('selectedTags');
                    if (selectedTagsContainer) {
                        selectedTagsContainer.scrollTop = 0;
                    }
                });
            }
            searchInput.classList.add('search-active');
            this.state.isSearching = true;

            // Return boolean indicating whether any tags match the search
            return filteredTags.length > 0;
        });
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
        // CRITICAL FIX: Don't return empty string - preserve vendor or return 'Unknown Vendor'
        if (!vendor || (typeof vendor === 'string' && vendor.trim() === '')) {
            return 'Unknown Vendor';
        }
        
        // Handle common vendor name patterns
        const vendorTrimmed = String(vendor).trim();
        const vendorLower = vendorTrimmed.toLowerCase();
        
        // Known vendor name mappings (only for capitalization, not merging)
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
        
        // CRITICAL FIX: Preserve original vendor name structure - only capitalize words
        // Don't merge or normalize - each unique vendor should remain separate
        const capitalized = vendorTrimmed.split(' ')
            .map(word => {
                // Preserve special characters and abbreviations
                if (word.includes('.') || word.includes(',') || word.includes('-')) {
                    // Handle abbreviations like "LLC", "Inc.", etc.
                    const upperCaseAbbrevs = ['llc', 'inc', 'ltd', 'corp', 'co'];
                    const wordClean = word.toLowerCase().replace(/[.,]/g, '');
                    if (upperCaseAbbrevs.includes(wordClean)) {
                        return word.toUpperCase();
                    }
                    // Handle hyphenated names
                    if (word.includes('-')) {
                        return word.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join('-');
                    }
                }
                return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
            })
            .join(' ');
        
        // CRITICAL FIX: Never return empty string - if capitalization fails, return original
        return capitalized || vendorTrimmed || 'Unknown Vendor';
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
        
        // CRITICAL FIX: Never drop products here – the backend is the source of truth
        // Previously, we attempted to deduplicate "duplicate" products based on
        // productName|vendor|brand|weight. That caused legitimate products (for example,
        // different DOH statuses or other attributes sharing those fields) to disappear
        // from the UI. To guarantee that **all** products are visible in the selector,
        // we now trust the backend and work with the full tag list.
        const uniqueTags = tags;
        
        // Debug: Log the first few tags to see their structure
        if (uniqueTags.length > 0) {
            verboseLog('First tag structure:', uniqueTags[0]);
        }
        
        // CRITICAL DEBUG: Track all unique vendors to see what's being extracted
        const vendorSet = new Set();
        const vendorCounts = new Map();
        
        uniqueTags.forEach(tag => {
            // Use the correct field names from the tag object - check multiple possible field names
            // CRITICAL FIX: Always extract vendor from vendor fields only, never from brand
            let vendor = tag.vendor || tag['Vendor'] || tag['Vendor/Supplier*'] || tag['Vendor/Supplier'] || '';
            // Normalize empty strings and 'Unknown' to ensure consistent handling
            if (!vendor || vendor.trim() === '' || vendor.trim().toLowerCase() === 'unknown') {
                vendor = '';
            } else {
                vendor = vendor.trim();
            }
            let brand = tag.productBrand || tag['Product Brand'] || tag['ProductBrand'] || this.extractBrand(tag) || '';
            const rawProductType = tag.productType || tag['Product Type*'] || tag['Product Type'] || '';
            const normalizedProductType = normalizeProductType(rawProductType.trim());
            const normalizedLower = normalizedProductType.toLowerCase();
            
            // CRITICAL FIX: Accept High CBD and High THC product types (any product type starting with "high cbd" or "high thc")
            // Also accept any product type that's in VALID_PRODUCT_TYPES
            const isHighCbdType = normalizedLower.startsWith('high cbd');
            const isHighThcType = normalizedLower.startsWith('high thc');
            const isValidType = VALID_PRODUCT_TYPES.includes(normalizedLower) || isHighCbdType || isHighThcType;
            
            const productType = isValidType
              ? normalizedProductType.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(' ')
              : 'Unknown Type';
            // CRITICAL FIX: Always prioritize database lineage fields (currentLineage/canonical_lineage) over Excel Lineage
            const lineage = (tag.currentLineage || tag.canonical_lineage || tag.Lineage || tag.lineage || 'MIXED').toString().trim().toUpperCase();
            const weight = (tag.weight || tag['Weight*'] || tag['Weight'] || tag['WeightUnits'] || '').toString().trim();
            // CRITICAL FIX: Ensure weightWithUnits is properly populated from multiple possible sources
            let weightWithUnits = (tag.weightWithUnits || tag.WeightWithUnits || tag.WeightUnits || 
                                   tag.CombinedWeight || tag.weightWithUnits || weight || '').toString().trim();
            
            // CRITICAL FIX: If weightWithUnits doesn't have units, append default unit "g"
            if (weightWithUnits && !weightWithUnits.match(/[a-zA-Z]+/)) {
                // Weight is just a number, add "g" unit
                weightWithUnits = `${weightWithUnits}g`;
            } else if (!weightWithUnits && weight) {
                // Fallback: if weightWithUnits is empty but weight exists, add "g" unit
                weightWithUnits = `${weight}g`;
            }
            
            // CRITICAL FIX: Normalize weight to remove .0 decimals (e.g., "1.0g" -> "1g", "1.0G" -> "1g")
            // This ensures "1.0g" and "1g" are treated as the same weight group
            if (weightWithUnits) {
                const weightMatch = weightWithUnits.match(/^([\d.]+)([a-zA-Z]+.*)$/i);
                if (weightMatch) {
                    const weightValue = weightMatch[1];
                    let unit = weightMatch[2].toLowerCase(); // Normalize unit to lowercase
                    // Standardize "grams" to "g"
                    if (unit === 'grams' || unit === 'gram') {
                        unit = 'g';
                    }
                    const weightFloat = parseFloat(weightValue);
                    if (!isNaN(weightFloat)) {
                        if (weightFloat % 1 === 0) {
                            // It's a whole number, remove decimal point (e.g., "1.0" -> "1")
                            weightWithUnits = `${Math.round(weightFloat)}${unit}`;
                        } else {
                            // It's a decimal number, remove trailing zeros (e.g., "1.50" -> "1.5")
                            let formatted = weightFloat.toString();
                            formatted = formatted.replace(/\.0+$/, ''); // Remove .0, .00, etc.
                            formatted = formatted.replace(/(\.\d*?)0+$/, '$1'); // Remove trailing zeros after decimal
                            formatted = formatted.replace(/\.$/, ''); // Remove trailing decimal point
                            weightWithUnits = `${formatted}${unit}`;
                        }
                    }
                }
            }
            
            // Extract price for grouping - try multiple possible price fields
            const rawPrice = tag['Price*'] || tag['Price* (Tier Name for Bulk)'] || tag.Price || tag['Product Price'] || tag.price || '';
            // Format price for grouping - use actual price values, not ranges
            let priceGroup = 'No Price';
            if (rawPrice) {
                const priceStr = rawPrice.toString().trim();
                if (priceStr && priceStr !== '' && priceStr !== 'nan' && priceStr.toLowerCase() !== 'none') {
                    // Try to extract numeric price value
                    const priceMatch = priceStr.match(/[\d.]+/);
                    if (priceMatch) {
                        const priceNum = parseFloat(priceMatch[0]);
                        if (!isNaN(priceNum)) {
                            // Format price: omit .00 for whole numbers, show 2 decimals for non-whole numbers
                            if (priceNum % 1 === 0) {
                                priceGroup = `$${Math.round(priceNum)}`;
                            } else {
                                priceGroup = `$${priceNum.toFixed(2)}`;
                            }
                        }
                    }
                }
            }

            // CRITICAL FIX: Never extract vendor from product name - "by Vendor" in product names is actually the brand
            // Vendor should always be in the tag data from Excel - if missing, it's a data quality issue
            // Never use brand as vendor - this causes brands to appear in vendor list
            if (!vendor || vendor.trim() === '' || vendor.trim().toLowerCase() === 'unknown') {
                // Vendor should always be present in Excel data - if missing, log it but use fallback
                // Only log first 10 missing vendors to avoid console spam
                if (!this._missingVendorLogCount) this._missingVendorLogCount = 0;
                if (this._missingVendorLogCount < 10) {
                    console.warn(`⚠️ Missing vendor for product '${tag['Product Name*'] || tag.ProductName || 'Unknown'}'. Vendor should always be in Excel data.`);
                    this._missingVendorLogCount++;
                } else if (this._missingVendorLogCount === 10) {
                    console.warn(`⚠️ ... (suppressing further missing vendor warnings)`);
                    this._missingVendorLogCount++;
                }
                vendor = 'Unknown Vendor';
            } else {
                vendor = vendor.trim();
                // CRITICAL FIX: Don't normalize vendor to empty string - preserve original value
                if (vendor === '') {
                    vendor = 'Unknown Vendor';
                }
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

            // Normalize the tag data (priceGroup is left on the object for analytics,
            // but we no longer group or categorize by price in the UI)
            // CRITICAL: Preserve all lineage fields (database lineage fields must be preserved exactly)
            // CRITICAL FIX: Ensure lineage fields are always set for UI consistency
            // Use database lineage fields first, then fall back to Excel Lineage, then calculated lineage
            const dbLineage = tag.canonical_lineage || tag.currentLineage || '';
            const excelLineage = tag.Lineage || tag.lineage || '';
            const calculatedLineage = lineage ? lineage.toString().trim().toUpperCase() : '';
            let finalLineage = dbLineage || excelLineage || calculatedLineage || 'MIXED';
            let finalLineageUpper = String(finalLineage).trim().toUpperCase();
            
            // CRITICAL FIX: Classic types should NEVER have MIXED/THC lineage - convert to HYBRID
            // This ensures UI displays correct lineage even if database/Excel has wrong value
            const isClassicType = productType && (typeof window.getUniqueLineages === 'function' ? window.getUniqueLineages(productType).length === 6 : false);
            if (isClassicType && (finalLineageUpper === 'MIXED' || finalLineageUpper === 'THC')) {
                finalLineageUpper = 'HYBRID';
                finalLineage = 'HYBRID';
            }
            
            const normalizedVendor = this.capitalizeVendorName((vendor || '').toString().trim());
            
            // CRITICAL DEBUG: Track vendor extraction
            vendorSet.add(normalizedVendor);
            vendorCounts.set(normalizedVendor, (vendorCounts.get(normalizedVendor) || 0) + 1);
            
            const normalizedTag = {
                ...tag,  // Spread all original fields first (preserves canonical_lineage, currentLineage, etc.)
                vendor: normalizedVendor,
                brand: this.capitalizeBrandName((brand || '').toString().trim()),
                productType: productType,
                subcategory: subcategory,
                lineage: finalLineageUpper, // always uppercase for color
                // CRITICAL FIX: Always preserve database lineage fields - they are the source of truth
                // Only override if database lineage doesn't exist
                canonical_lineage: tag.canonical_lineage || dbLineage || finalLineageUpper,
                currentLineage: tag.currentLineage || dbLineage || finalLineageUpper,
                // Set Lineage field for backward compatibility (use database lineage if available)
                Lineage: tag.canonical_lineage || tag.currentLineage || finalLineageUpper,
                weight: weight,
                weightWithUnits: weightWithUnits,
                priceGroup: priceGroup,
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
            
            // COMBINE subcategory with weight to save space (e.g., "1g - 510" instead of separate levels)
            // For vape products with subcategory, combine subcategory with weight
            let combinedWeightKey = normalizedTag.weightWithUnits;
            if (normalizedTag.subcategory) {
                // Format: "weight - subcategory" (e.g., "1g - 510", "1g - Disposable")
                combinedWeightKey = `${normalizedTag.weightWithUnits} - ${normalizedTag.subcategory}`;
            }
            
            // Always treat the product type as a flat weight → products mapping
            // (combining subcategory into weight key for vape products)
            let weightGroups = productTypeGroups.get(normalizedTag.productType);
            if (!(weightGroups instanceof Map)) {
                weightGroups = new Map();
                productTypeGroups.set(normalizedTag.productType, weightGroups);
            }

            // Create weight group (with combined subcategory if applicable) if it doesn't exist
            // and store products grouped by price (price-based subgroups)
            if (!weightGroups.has(combinedWeightKey)) {
                weightGroups.set(combinedWeightKey, new Map());
            }
            const priceGroups = weightGroups.get(combinedWeightKey);
            
            // Create price group if it doesn't exist
            if (!priceGroups.has(normalizedTag.priceGroup)) {
                priceGroups.set(normalizedTag.priceGroup, []);
            }
            const productsAtPrice = priceGroups.get(normalizedTag.priceGroup);
            productsAtPrice.push(normalizedTag);
        });

        if (skippedTags > 0) {
            console.info(`Skipped ${skippedTags} tags due to missing vendor information`);
        }
        
        // CRITICAL DEBUG: Log vendor statistics
        console.log(`📊 Vendor extraction stats: ${vendorSet.size} unique vendors found from ${uniqueTags.length} tags`);
        if (vendorSet.size < 10) {
            console.log('📋 All vendors:', Array.from(vendorSet).sort());
            console.log('📊 Vendor counts:', Array.from(vendorCounts.entries()).sort((a, b) => b[1] - a[1]).slice(0, 20));
        } else {
            console.log('📋 First 20 vendors:', Array.from(vendorSet).sort().slice(0, 20));
            console.log('📊 Top 20 vendor counts:', Array.from(vendorCounts.entries()).sort((a, b) => b[1] - a[1]).slice(0, 20));
        }
        
        // CRITICAL DEBUG: Check if most products are going to Unknown Vendor
        const unknownVendorCount = vendorCounts.get('Unknown Vendor') || 0;
        if (unknownVendorCount > uniqueTags.length * 0.5) {
            console.warn(`⚠️ WARNING: ${unknownVendorCount} out of ${uniqueTags.length} products (${Math.round(unknownVendorCount/uniqueTags.length*100)}%) have no vendor data!`);
            console.warn('⚠️ This suggests the Excel file is missing vendor information for most products.');
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
    // PERFORMANCE: Reduced debounce delay from 300ms to 150ms for faster response
    debouncedUpdateAvailableTags: debounce(function(originalTags, filteredTags = null) {
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
        // Avoid showing splash when user is actively typing/searching to reduce flicker
        if (tagsToShow && tagsToShow.length > 0 && !this.state.isSearching) {
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
        
        // PERFORMANCE: Use setTimeout(0) instead of requestAnimationFrame for faster initial render
        // requestAnimationFrame can add unnecessary delay
        setTimeout(() => {
            this._updateAvailableTags(originalTags, filteredTags);
        }, 0);
    }, 150), // Reduced debounce from 300ms to 150ms for faster response

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

    // CRITICAL FIX: Ensure all checkboxes are enabled and clickable
    _ensureCheckboxesEnabled() {
        const allCheckboxes = document.querySelectorAll('.tag-checkbox');
        allCheckboxes.forEach(checkbox => {
            checkbox.style.pointerEvents = 'auto';
            checkbox.removeAttribute('data-drag-disabled');
            checkbox.removeAttribute('data-reordering');
            // Ensure checkbox is not disabled
            if (checkbox.disabled) {
                checkbox.disabled = false;
            }
        });
        verboseLog(`✅ Ensured ${allCheckboxes.length} checkboxes are enabled`);
    },

    // CRITICAL FIX: Restore checkbox states after re-render to preserve selections made during initial load
    _restoreCheckboxStates() {
        // CRITICAL FIX: Always ensure checkboxes are enabled before restoring states
        this._ensureCheckboxesEnabled();
        
        if (!this.state.persistentSelectedTags || this.state.persistentSelectedTags.length === 0) {
            return;
        }

        const availableTagsContainer = document.getElementById('availableTags');
        if (!availableTagsContainer) {
            return;
        }
        
        // CRITICAL FIX: Ensure _selectedTagsSet is synced before restoring checkboxes
        if (!this.state._selectedTagsSet) {
            this.state._selectedTagsSet = new Set();
        }
        // Sync Set with persistentSelectedTags to ensure consistency
        const currentSet = new Set(this.state.persistentSelectedTags);
        const setNeedsUpdate = this.state.persistentSelectedTags.length !== this.state._selectedTagsSet.size ||
                               !this.state.persistentSelectedTags.every(name => this.state._selectedTagsSet.has(name));
        if (setNeedsUpdate) {
            this.state._selectedTagsSet = currentSet;
        }
        
        // CRITICAL FIX: Use case-insensitive matching to handle any case differences
        const persistentSet = new Set(this.state.persistentSelectedTags.map(name => name.toLowerCase()));
        
        // CRITICAL FIX: Don't restore if we just generated (within last 5 seconds)
        // This prevents clearing checkboxes immediately after generation
        const now = Date.now();
        const recentlyGenerated = this._lastGenerationTime && (now - this._lastGenerationTime) < 5000;
        
        // Restore checkbox states based on persistentSelectedTags
        const checkboxes = availableTagsContainer.querySelectorAll('.tag-checkbox');
        let restoredCount = 0;
        let uncheckedCount = 0;
        
        checkboxes.forEach(checkbox => {
            const tagName = checkbox.value;
            if (tagName) {
                // CRITICAL FIX: Don't modify checkbox if it was recently checked by user
                // This prevents race conditions on initial load and after generation
                if (checkbox.hasAttribute('data-recently-checked')) {
                    return; // Skip this checkbox - user just checked it
                }
                
                // CRITICAL FIX: After generation, only restore checked state, never uncheck
                // This prevents the first checkbox from disappearing after generation
                if (recentlyGenerated && checkbox.checked) {
                    // If checkbox is already checked after generation, ensure it stays checked
                    const isSelected = this.state.persistentSelectedTags.includes(tagName) || 
                                      persistentSet.has(tagName.toLowerCase());
                    if (isSelected && !checkbox.checked) {
                        checkbox.checked = true;
                        restoredCount++;
                    }
                    return; // Don't uncheck anything after generation
                }
                
                // Check both exact match and case-insensitive match
                const isSelected = this.state.persistentSelectedTags.includes(tagName) || 
                                  persistentSet.has(tagName.toLowerCase());
                if (isSelected && !checkbox.checked) {
                    checkbox.checked = true;
                    restoredCount++;
                } else if (!isSelected && checkbox.checked) {
                    // CRITICAL FIX: Only uncheck if it's not in persistentSelectedTags
                    // Don't uncheck if it might be a timing issue
                    const shouldUncheck = !this.state.persistentSelectedTags.includes(tagName) && 
                                         !persistentSet.has(tagName.toLowerCase());
                    if (shouldUncheck) {
                        checkbox.checked = false;
                        uncheckedCount++;
                    }
                }
            }
        });
        
        if (restoredCount > 0) {
            verboseLog(`✅ Restored ${restoredCount} checkbox states after re-render`);
        }
        if (uncheckedCount > 0) {
            verboseLog(`⚠️ Unchecked ${uncheckedCount} checkboxes that shouldn't be selected`);
        }
        
        // CRITICAL FIX: Also ensure selected tags display is updated
        if (this.state.persistentSelectedTags.length > 0) {
            // Update selectedTags set to match persistentSelectedTags
            this.state.selectedTags = new Set(this.state.persistentSelectedTags);
            
            // CRITICAL FIX: Immediately update selected tags display to prevent selections from disappearing
            // Use requestAnimationFrame to ensure DOM is ready, but don't delay too long
            requestAnimationFrame(() => {
                const selectedTagObjects = this.getSelectedTagObjects();
                if (selectedTagObjects.length > 0) {
                    this.updateSelectedTags(selectedTagObjects);
                } else if (this.state.persistentSelectedTags.length > 0) {
                    // CRITICAL FIX: If no tag objects found but we have persistent selections,
                    // try again after a short delay - tags might still be loading
                    setTimeout(() => {
                        const retrySelectedTagObjects = this.getSelectedTagObjects();
                        if (retrySelectedTagObjects.length > 0) {
                            this.updateSelectedTags(retrySelectedTagObjects);
                        } else {
                            console.warn(`⚠️ Could not find tag objects for ${this.state.persistentSelectedTags.length} selected tags - they may be filtered out`);
                        }
                    }, 200);
                }
            });
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
                // CRITICAL FIX: Use getSelectedTagObjects() which checks all sources (Map, originalTags, tags)
                // This prevents tags from disappearing when filters are active
                const selectedTagObjects = this.getSelectedTagObjects();
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
                // CRITICAL FIX: JSON matched tags should always start expanded (not collapsed)
                // Do NOT add 'collapsed' class - keep expanded by default
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
                        // PERFORMANCE: Use Map lookup instead of array.find() inside map - O(1) vs O(n²)
                        const selectedTagObjects = this.state.persistentSelectedTags
                            .map(name => this._tagLookupMap?.get(name))
                            .filter(Boolean);
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
                    // CRITICAL FIX: JSON matched tags should always start expanded (not collapsed)
                    // Do NOT add 'collapsed' class - keep expanded by default
                    productTypeSection.appendChild(productTypeContent);

                    // Subcategories are now combined with weight (e.g., "1g - 510")
                    // Always render weights directly - no separate subcategory level
                    const sortedWeights = Array.from(weightGroupsOrSubcategories.entries())
                        .sort(([a], [b]) => (a || '').localeCompare(b || ''));

                    sortedWeights.forEach(([weight, priceGroups]) => {
                        const weightSection = document.createElement('div');
                        weightSection.className = 'weight-section ms-3 mb-2';
                        
                        // Check if there's only one price group for inline display
                        const isSinglePriceGroup = priceGroups instanceof Map && priceGroups.size === 1;
                        
                        // Create weight header with checkbox
                        const weightHeader = document.createElement('div');
                        weightHeader.className = 'weight-header mb-1 d-flex align-items-center cursor-pointer';
                        if (isSinglePriceGroup) {
                            weightHeader.style.display = 'inline-flex';
                            weightHeader.style.marginRight = '12px';
                        }
                        weightHeader.addEventListener('click', (e) => {
                            if (e.target.type === 'checkbox') return;
                            const weightContent = weightSection.querySelector('.weight-content');
                            if (!weightContent) return; // Safety check
                            const isCollapsed = weightContent.classList.contains('collapsed');
                            weightContent.classList.toggle('collapsed', !isCollapsed);
                            const collapseIcon = weightHeader.querySelector('.collapse-icon');
                            if (collapseIcon) {
                                collapseIcon.textContent = isCollapsed ? '▼' : '▶';
                            }
                        });
                        
                        const weightCheckbox = document.createElement('input');
                        weightCheckbox.type = 'checkbox';
                        weightCheckbox.className = 'select-all-checkbox me-2';
                        weightCheckbox.addEventListener('change', (e) => {
                            const savedScroll = this._saveAvailableScrollPosition();
                            const isChecked = e.target.checked;
                            const checkboxes = weightSection.querySelectorAll('input[type="checkbox"]');
                            checkboxes.forEach(checkbox => {
                                if (!checkbox.classList.contains('tag-checkbox')) {
                                    checkbox.checked = isChecked;
                                    return;
                                }
                                
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
                            // CRITICAL FIX: Use getSelectedTagObjects() which checks all sources
                            const selectedTagObjects = this.getSelectedTagObjects();
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
                        // CRITICAL FIX: JSON matched tags should always start expanded (not collapsed)
                        // Do NOT add 'collapsed' class - keep expanded by default
                        if (isSinglePriceGroup) {
                            weightContent.style.display = 'inline-block';
                        }
                        weightSection.appendChild(weightContent);

                        // Render price subgroups (price groups are now always organized as Map)
                        if (priceGroups instanceof Map) {
                            const sortedPriceGroups = Array.from(priceGroups.entries())
                                .sort(([a], [b]) => {
                                    // Sort price groups: No Price first, then by actual price value (numeric)
                                    if (a === 'No Price') return -1;
                                    if (b === 'No Price') return 1;
                                    // Extract numeric value from price strings (e.g., "$10" -> 10, "$15.50" -> 15.50)
                                    const priceA = parseFloat(a.replace(/[^0-9.]/g, '')) || 0;
                                    const priceB = parseFloat(b.replace(/[^0-9.]/g, '')) || 0;
                                    return priceA - priceB;
                                });
                            
                            const isSinglePriceGroup = sortedPriceGroups.length === 1;
                            
                            sortedPriceGroups.forEach(([priceGroup, tagArray], priceIndex) => {
                                const priceSection = document.createElement('div');
                                priceSection.className = 'price-section ms-3 mb-1';
                                
                                // If single price group, display inline with weight header
                                if (isSinglePriceGroup && priceIndex === 0) {
                                    priceSection.style.display = 'inline-block';
                                    priceSection.style.marginLeft = '12px';
                                    priceSection.style.verticalAlign = 'middle';
                                }
                                
                                // Create price header with checkbox and collapse functionality
                                const priceHeader = document.createElement('div');
                                priceHeader.className = 'price-header mb-1 d-flex align-items-center cursor-pointer';
                                priceHeader.addEventListener('click', (e) => {
                                    if (e.target.type === 'checkbox') return;
                                    const priceContent = priceSection.querySelector('.price-content');
                                    if (!priceContent) return; // Safety check
                                    const isCollapsed = priceContent.classList.contains('collapsed');
                                    priceContent.classList.toggle('collapsed', !isCollapsed);
                                    const collapseIcon = priceHeader.querySelector('.collapse-icon');
                                    if (collapseIcon) {
                                        collapseIcon.textContent = isCollapsed ? '▼' : '▶';
                                    }
                                });
                                
                                const priceCheckbox = document.createElement('input');
                                priceCheckbox.type = 'checkbox';
                                priceCheckbox.className = 'select-all-checkbox me-2';
                                priceCheckbox.addEventListener('change', (e) => {
                                    const savedScroll = this._saveAvailableScrollPosition();
                                    const isChecked = e.target.checked;
                                    const checkboxes = priceSection.querySelectorAll('input[type="checkbox"]');
                                    checkboxes.forEach(checkbox => {
                                        if (!checkbox.classList.contains('tag-checkbox')) {
                                            checkbox.checked = isChecked;
                                            return;
                                        }
                                        
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
                                    // CRITICAL FIX: Use getSelectedTagObjects() which checks all sources
                                    const selectedTagObjects = this.getSelectedTagObjects();
                                    this.updateSelectedTags(selectedTagObjects);
                                    this.efficientlyUpdateAvailableTagsDisplay();
                                    requestAnimationFrame(() => {
                                        this._restoreAvailableScrollPosition(savedScroll);
                                    });
                                });
                                
                                priceHeader.appendChild(priceCheckbox);
                                priceHeader.appendChild(document.createTextNode(priceGroup));
                                const priceCollapseIcon = document.createElement('span');
                                priceCollapseIcon.className = 'collapse-icon ms-auto';
                                priceCollapseIcon.textContent = '▼';
                                priceHeader.appendChild(priceCollapseIcon);
                                
                                // CRITICAL FIX: Append priceHeader to priceSection BEFORE appending priceSection to weightContent
                                priceSection.appendChild(priceHeader);
                                
                                const priceContent = document.createElement('div');
                                priceContent.className = 'price-content';
                                priceSection.appendChild(priceContent);
                                
                                // Now append priceSection to weightContent
                                weightContent.appendChild(priceSection);
                                
                                const sortedTags = [...tagArray].sort((a, b) => {
                                    const aName = (a && (a['Product Name*'] || a.ProductName || a.displayName) || '').toString();
                                    const bName = (b && (b['Product Name*'] || b.ProductName || b.displayName) || '').toString();
                                    return aName.localeCompare(bName);
                                });
                                this._renderTagsInBatches(sortedTags, priceContent);
                            });
                        } else if (Array.isArray(priceGroups)) {
                            // Backward compatibility: if priceGroups is an array, render directly
                            const sortedTags = [...priceGroups].sort((a, b) => {
                                const aName = (a && (a['Product Name*'] || a.ProductName || a.displayName) || '').toString();
                                const bName = (b && (b['Product Name*'] || b.ProductName || b.displayName) || '').toString();
                                return aName.localeCompare(bName);
                            });
                            this._renderTagsInBatches(sortedTags, weightContent);
                        }

                        productTypeContent.appendChild(weightSection);
                    });

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
            
            // PERFORMANCE FIX: Batch DOM operations
            availableTagsContainer.innerHTML = '';
            availableTagsContainer.appendChild(fragment);
            
            // PERFORMANCE FIX: Remove updating class after DOM update to re-enable transitions
            const removeUpdatingClass = () => {
                if (availableTagsContainer) availableTagsContainer.classList.remove('updating');
                const availableTagsList = document.getElementById('availableTagsList');
                if (availableTagsList) availableTagsList.classList.remove('updating');
                const tagListContainer = document.querySelector('.tag-list-container');
                if (tagListContainer) tagListContainer.classList.remove('updating');
            };
            
            // PERFORMANCE FIX: Defer non-critical operations to next frame
            requestAnimationFrame(() => {
                // Remove updating class after render
                removeUpdatingClass();
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
                container.querySelectorAll('.vendor-section, .brand-section, .product-type-section, .subcategory-section, .weight-section, .price-section').forEach(section => {
                    updateSelectAllCheckboxState(section);
                });
                
                        // Hide loading splash only after tags actually appear in DOM
                        this._waitForTagsToAppear();
            });
        });
        
        verboseLog('✅ Rendered', tags.length, 'JSON matched tags with HIERARCHY (same as Selected Tags)');
        } catch (error) {
            console.error('Error in _performUpdateAvailableTags:', error);
            // Ensure updating class is removed even on error
            const availableTagsContainer = document.getElementById('availableTags');
            const availableTagsList = document.getElementById('availableTagsList');
            const tagListContainer = document.querySelector('.tag-list-container');
            if (availableTagsContainer) availableTagsContainer.classList.remove('updating');
            if (availableTagsList) availableTagsList.classList.remove('updating');
            if (tagListContainer) tagListContainer.classList.remove('updating');
            throw error; // Re-throw to allow caller to handle
        }
    },

    // Internal function that actually updates the available tags
    _updateAvailableTags(originalTags, filteredTags = null) {
        // CRITICAL FIX: Render immediately instead of using requestAnimationFrame to prevent delays
        // Tags need to appear immediately after upload, not on next frame
        this._performUpdateAvailableTags(originalTags, filteredTags);
    },
    
    _performUpdateAvailableTags(originalTags, filteredTags = null) {
        // PERFORMANCE FIX: Add updating class to prevent flashing during rapid updates
        const availableTagsContainer = document.getElementById('availableTags');
        const availableTagsList = document.getElementById('availableTagsList');
        const tagListContainer = document.querySelector('.tag-list-container');
        const removeUpdatingClass = () => {
            if (availableTagsContainer) availableTagsContainer.classList.remove('updating');
            if (availableTagsList) availableTagsList.classList.remove('updating');
            if (tagListContainer) tagListContainer.classList.remove('updating');
        };
        
        if (availableTagsContainer) availableTagsContainer.classList.add('updating');
        if (availableTagsList) availableTagsList.classList.add('updating');
        if (tagListContainer) tagListContainer.classList.add('updating');
        
        verboseLog('_updateAvailableTags called with:', {
            originalTagsLength: originalTags ? originalTags.length : 0,
            filteredTagsLength: filteredTags ? filteredTags.length : 0,
            tags: filteredTags || originalTags,
            hydratedFromCache: this.state.hydratedFromCache
        });
        
        if (!availableTagsContainer) {
            console.error('Available tags container not found');
            removeUpdatingClass(); // Ensure class is removed even on error
            return;
        }
        
        // PERFORMANCE FIX: Ensure updating class is removed even if errors occur
        const removeUpdatingClass = () => {
            if (availableTagsContainer) availableTagsContainer.classList.remove('updating');
            if (availableTagsList) availableTagsList.classList.remove('updating');
            if (tagListContainer) tagListContainer.classList.remove('updating');
        };
        
        try {
        
        // CRITICAL FIX: Preserve checkbox selections from DOM before re-rendering
        // This prevents selections made during initial load from being lost
        const currentlyCheckedCheckboxes = availableTagsContainer.querySelectorAll('.tag-checkbox:checked');
        const currentlySelectedTagNames = Array.from(currentlyCheckedCheckboxes).map(cb => cb.value).filter(Boolean);
        
        // CRITICAL FIX: Always preserve persistentSelectedTags, even if DOM doesn't show them
        // This prevents selections from being lost when tags are re-rendered
        if (this.state.persistentSelectedTags && this.state.persistentSelectedTags.length > 0) {
            verboseLog(`🔒 Preserving ${this.state.persistentSelectedTags.length} persistent selected tags before re-render`);
        }
        
        // Merge DOM selections with persistentSelectedTags to ensure nothing is lost
        if (currentlySelectedTagNames.length > 0) {
            const currentSet = new Set(this.state.persistentSelectedTags || []);
            currentlySelectedTagNames.forEach(tagName => {
                if (!currentSet.has(tagName)) {
                    console.log(`🔍 Preserving selection from DOM: ${tagName}`);
                    this.state.persistentSelectedTags.push(tagName);
                }
            });
            // Update selectedTags set to match
            this.state.selectedTags = new Set(this.state.persistentSelectedTags);
            verboseLog(`✅ Preserved ${currentlySelectedTagNames.length} selections from DOM before re-render`);
        }
        
        // CRITICAL FIX: Ensure persistentSelectedTags is never cleared during re-render
        // Save a copy to restore if something goes wrong
        const savedPersistentTags = [...(this.state.persistentSelectedTags || [])];
        
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
            // CRITICAL FIX: Clear filename display when no tags are available
            // This prevents confusion when file path shows but tags don't load
            const fileInfoText = document.getElementById('fileInfoText');
            if (fileInfoText) {
                fileInfoText.textContent = 'No file uploaded';
                verboseLog('✅ Cleared filename display - no tags available');
            }
            return;
        }
        
        // PERFORMANCE: Skip loading spinner entirely to prevent flickering
        // Instead, show tags immediately without intermediate loading state
        const currentContent = availableTagsContainer.innerHTML.trim();
        const hasActualTags = currentContent && !currentContent.includes('spinner-border') && !currentContent.includes('No tags available');
        
        // Don't clear existing tags - just update them smoothly
        if (!hasActualTags) {
            // Only show minimal placeholder if truly empty
            availableTagsContainer.innerHTML = '<div class="text-center py-2 text-muted">Loading...</div>';
        }
        // Otherwise keep existing content to prevent flicker
        
        // PERFORMANCE: Reduced verbose logging for faster rendering
        // Only log essential information
        if (tags.length > 0 && verboseLog.enabled) {
            verboseLog(`Rendering ${tags.length} tags`);
        }
        
        // CRITICAL FIX: Ensure all tags in state have database lineage fields prioritized
        // This ensures TagManager always uses database lineage, not Excel lineage
        const tagsWithDbLineage = tags.map(tag => {
            // If tag has database lineage fields, ensure they're used and Excel Lineage is updated to match
            if (tag.canonical_lineage || tag.currentLineage) {
                const dbLineage = tag.canonical_lineage || tag.currentLineage;
                // Update Excel Lineage field to match database lineage for consistency
                tag.Lineage = dbLineage;
                tag.lineage = dbLineage.toLowerCase();
                // CRITICAL: Ensure database lineage fields are preserved (don't let them get lost)
                if (!tag.canonical_lineage && tag.currentLineage) {
                    tag.canonical_lineage = tag.currentLineage;
                }
                if (!tag.currentLineage && tag.canonical_lineage) {
                    tag.currentLineage = tag.canonical_lineage;
                }
            } else {
                // CRITICAL FIX: If database lineage fields are missing but Lineage exists, check if it's actually from database
                // Sometimes backend sets Lineage but not canonical_lineage/currentLineage
                // In that case, we should treat Lineage as database lineage if it was set by backend
                // But we can't distinguish, so we'll log a warning for debugging
                const tagName = tag['Product Name*'] || tag.ProductName || 'Unknown';
                if (tag.Lineage && tag.Lineage !== 'MIXED' && tag.Lineage !== 'HYBRID') {
                    // Log warning for tags that might have database lineage but missing fields
                    console.warn(`⚠️ Tag "${tagName}" has Lineage="${tag.Lineage}" but missing canonical_lineage/currentLineage fields`);
                }
            }
            return tag;
        });
        
        // Only update originalTags if we're not filtering (i.e., if filteredTags is null)
        // This preserves the original data for when filters are reset to "All"
        if (filteredTags === null) {
            this.state.originalTags = [...tagsWithDbLineage];
        }
        
        // Always update the current tags for display
        this.state.tags = [...tagsWithDbLineage];
        
        // PERFORMANCE: Build tag lookup Map once when tags load for instant checkbox operations
        // Also build Set for selected tags for O(1) lookups instead of array.includes()
        this._tagLookupMap = new Map();
        this.state.tags.forEach(t => {
            if (t && t['Product Name*']) {
                this._tagLookupMap.set(t['Product Name*'], t);
            }
        });
        this.state.originalTags.forEach(t => {
            if (t && t['Product Name*'] && !this._tagLookupMap.has(t['Product Name*'])) {
                this._tagLookupMap.set(t['Product Name*'], t);
            }
        });
        
        // PERFORMANCE: Convert persistentSelectedTags to Set for O(1) lookups
        if (!this.state._selectedTagsSet || this.state._selectedTagsSet.size !== this.state.persistentSelectedTags.length) {
            this.state._selectedTagsSet = new Set(this.state.persistentSelectedTags);
        }
        
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
        
        // PERFORMANCE: Removed redundant logging
        
        // PERFORMANCE: Skip redundant loading indicator for cache loads
        // Only show if not from cache and not already showing
        const hasLoadingIndicator = availableTagsContainer.innerHTML.includes('spinner-border');
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
            
            // CRITICAL FIX: For large datasets, organize asynchronously to prevent UI freeze
            const LARGE_DATASET_THRESHOLD = 500;
            if (tags.length > LARGE_DATASET_THRESHOLD) {
                verboseLog(`⚡ Large dataset (${tags.length} tags) - organizing asynchronously to prevent freeze`);
                // Show loading indicator while organizing
                availableTagsContainer.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Organizing tags...</span></div><p class="mt-2 text-white">Organizing tags...</p></div>';
                
                // Organize in next event loop tick to prevent blocking
                setTimeout(() => {
                    try {
                        organizedTags = this.organizeBrandCategories(tags);
                        verboseLog('✅ CURRENT INVENTORY: Using same hierarchical organization as Selected Tags');
                        verboseLog('Tags organized successfully, vendor count:', organizedTags.size);
                        // Continue with normal rendering flow
                        this._renderOrganizedTags(organizedTags, tagList, availableTagsContainer, savedScroll, savedPersistentTags);
                    } catch (error) {
                        console.error('Error organizing tags:', error);
                        // CRITICAL FIX: Fallback to simple list rendering if organization fails
                        console.log('🔄 Falling back to simple list rendering due to organization error');
                        const sortedSimple = [...tags].sort((a, b) => {
                            const aName = (a && (a['Product Name*'] || a.ProductName || a.displayName) || '').toString();
                            const bName = (b && (b['Product Name*'] || b.ProductName || b.displayName) || '').toString();
                            return aName.localeCompare(bName);
                        });
                        this._renderTagsInBatches(sortedSimple, tagList);
                        availableTagsContainer.innerHTML = '';
                        availableTagsContainer.appendChild(tagList);
                        // PERFORMANCE FIX: Remove updating class after render
                        if (availableTagsContainer) availableTagsContainer.classList.remove('updating');
                        const availableTagsList = document.getElementById('availableTagsList');
                        if (availableTagsList) availableTagsList.classList.remove('updating');
                        const tagListContainer = document.querySelector('.tag-list-container');
                        if (tagListContainer) tagListContainer.classList.remove('updating');
                        this._restoreCheckboxStates();
                        this._restoreAvailableScrollPosition(savedScroll);
                    }
                }, 0);
                return; // Exit early, rendering will continue in callback
            }
            
            // Small dataset - organize synchronously (fast enough)
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
                    // CRITICAL FIX: Replace container content immediately - don't wait for next frame
                    availableTagsContainer.innerHTML = '';
                    availableTagsContainer.appendChild(tagList);
                    // PERFORMANCE FIX: Remove updating class after render
                    if (availableTagsContainer) availableTagsContainer.classList.remove('updating');
                    const availableTagsList = document.getElementById('availableTagsList');
                    if (availableTagsList) availableTagsList.classList.remove('updating');
                    const tagListContainer = document.querySelector('.tag-list-container');
                    if (tagListContainer) tagListContainer.classList.remove('updating');
                        
                        // CRITICAL FIX: Restore checkbox states after re-render to preserve selections
                        // Also restore persistentSelectedTags if it was accidentally cleared
                        if (savedPersistentTags.length > 0 && (!this.state.persistentSelectedTags || this.state.persistentSelectedTags.length === 0)) {
                            console.log(`🔄 Restoring ${savedPersistentTags.length} persistent selected tags that were cleared`);
                            this.state.persistentSelectedTags = [...savedPersistentTags];
                            this.state.selectedTags = new Set(savedPersistentTags);
                        }
                        this._restoreCheckboxStates();
                        
                        // CRITICAL FIX: Also update selected tags display to ensure they're shown
                        if (this.state.persistentSelectedTags && this.state.persistentSelectedTags.length > 0) {
                            setTimeout(() => {
                                const selectedTagObjects = this.getSelectedTagObjects();
                                if (selectedTagObjects.length > 0) {
                                    this.updateSelectedTags(selectedTagObjects);
                                }
                            }, 100);
                        }
                        
                        // After tags are in DOM, restore scroll and initialize
                        this._restoreAvailableScrollPosition(savedScroll);
                        this.updateSelectAllCheckboxes();
                        this.initializeSelectAllCheckbox();
                        
                        // Hide loading splash only after tags actually appear in DOM
                        this._waitForTagsToAppear();
        }
        
        // CRITICAL FIX: Render organized tags in chunks to prevent UI freeze
        this._renderOrganizedTags(organizedTags, tagList, availableTagsContainer, savedScroll, savedPersistentTags);
    },
    
    _renderOrganizedTags(organizedTags, tagList, availableTagsContainer, savedScroll, savedPersistentTags) {
        const sortedVendors = Array.from(organizedTags.entries())
            .sort(([a], [b]) => (a || '').localeCompare(b || ''));

        // CRITICAL FIX: Render vendors in chunks to prevent UI freeze for large datasets
        const VENDOR_BATCH_SIZE = 5; // Process 5 vendors at a time
        let vendorIndex = 0;
        
        const renderVendorBatch = () => {
            const endIndex = Math.min(vendorIndex + VENDOR_BATCH_SIZE, sortedVendors.length);
            
            for (let i = vendorIndex; i < endIndex; i++) {
                const [vendor, brandGroups] = sortedVendors[i];
                this._renderVendorSection(vendor, brandGroups, tagList);
            }
            
            vendorIndex = endIndex;
            
            // Continue rendering if there are more vendors
            if (vendorIndex < sortedVendors.length) {
                // Use requestIdleCallback if available for better performance, otherwise setTimeout
                if (window.requestIdleCallback) {
                    requestIdleCallback(renderVendorBatch, { timeout: 50 });
                } else {
                    setTimeout(renderVendorBatch, 0);
                }
            } else {
                // All vendors rendered - finalize
                // CRITICAL FIX: Append immediately instead of waiting for next frame
                availableTagsContainer.innerHTML = '';
                availableTagsContainer.appendChild(tagList);
                
                // PERFORMANCE FIX: Remove updating class after render
                if (availableTagsContainer) availableTagsContainer.classList.remove('updating');
                const availableTagsList = document.getElementById('availableTagsList');
                if (availableTagsList) availableTagsList.classList.remove('updating');
                const tagListContainer = document.querySelector('.tag-list-container');
                if (tagListContainer) tagListContainer.classList.remove('updating');
                    
                    // CRITICAL FIX: Restore checkbox states after re-render
                    if (savedPersistentTags.length > 0 && (!this.state.persistentSelectedTags || this.state.persistentSelectedTags.length === 0)) {
                        console.log(`🔄 Restoring ${savedPersistentTags.length} persistent selected tags`);
                        this.state.persistentSelectedTags = [...savedPersistentTags];
                        this.state.selectedTags = new Set(savedPersistentTags);
                    }
                    this._restoreCheckboxStates();
                    
                    // Update selected tags display
                    if (this.state.persistentSelectedTags && this.state.persistentSelectedTags.length > 0) {
                        setTimeout(() => {
                            const selectedTagObjects = this.getSelectedTagObjects();
                            if (selectedTagObjects.length > 0) {
                                this.updateSelectedTags(selectedTagObjects);
                            }
                        }, 100);
                    }
                    
                    // Restore scroll and initialize
                    this._restoreAvailableScrollPosition(savedScroll);
                    this.updateSelectAllCheckboxes();
                    this.initializeSelectAllCheckbox();
                    
                    // Hide loading splash
                    this._waitForTagsToAppear();
            }
        };
        
        // Start rendering vendors
        renderVendorBatch();
    },
    
    _renderVendorSection(vendor, brandGroups, tagList) {
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
                    // PERFORMANCE: Use Map lookup instead of array.find() - O(1) vs O(n)
                    const tag = this._tagLookupMap?.get(tagName);
                    if (!tag) {
                        checkbox.checked = isChecked;
                        return;
                    }

                    checkbox.checked = isChecked;

                    // PERFORMANCE: Use Set for O(1) lookups instead of array.includes()
                    if (isChecked) {
                        if (!this.state._selectedTagsSet.has(tagName)) {
                            this.state.persistentSelectedTags.push(tagName);
                            this.state._selectedTagsSet.add(tagName);
                        }
                    } else {
                        // Only remove if the originating event is actually unchecking
                        if (!e.target.checked) {
                            const index = this.state.persistentSelectedTags.indexOf(tagName);
                            if (index > -1) {
                                this.state.persistentSelectedTags.splice(index, 1);
                                this.state._selectedTagsSet.delete(tagName);
                            }
                        }
                    }
                });
                this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                // CRITICAL FIX: Use getSelectedTagObjects() which checks all sources (Map, originalTags, tags)
                // This prevents tags from disappearing when filters are active
                const selectedTagObjects = this.getSelectedTagObjects();
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
                    // PERFORMANCE: Use Map lookup instead of array.find() - O(1) vs O(n)
                    const tag = this._tagLookupMap?.get(tagName);
                    if (!tag) {
                        checkbox.checked = isChecked;
                        return;
                    }

                    checkbox.checked = isChecked;

                    // PERFORMANCE: Use Set for O(1) lookups instead of array.includes()
                    if (isChecked) {
                        if (!this.state._selectedTagsSet.has(tagName)) {
                            this.state.persistentSelectedTags.push(tagName);
                            this.state._selectedTagsSet.add(tagName);
                        }
                    } else {
                        if (!e.target.checked) {
                            const index = this.state.persistentSelectedTags.indexOf(tagName);
                            if (index > -1) {
                                this.state.persistentSelectedTags.splice(index, 1);
                                this.state._selectedTagsSet.delete(tagName);
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
                    // Check by looking at keys - subcategories have keys like "510" or "Disposable"
                    // Price groups have keys like "$10-$19.99", weights have keys like "3.5g"
                    // Subcategories are now combined with weight (e.g., "1g - 510")
                    // Always render weights directly - no separate subcategory level
                    
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
                            // PERFORMANCE: Use Map lookup instead of array.find() - O(1) vs O(n)
                            const tag = this._tagLookupMap?.get(tagName);
                            if (!tag) {
                                checkbox.checked = isChecked;
                                return;
                            }

                            checkbox.checked = isChecked;

                            // PERFORMANCE: Use Set for O(1) lookups instead of array.includes()
                            if (isChecked) {
                                if (!this.state._selectedTagsSet.has(tagName)) {
                                    this.state.persistentSelectedTags.push(tagName);
                                    this.state._selectedTagsSet.add(tagName);
                                }
                            } else {
                                if (!e.target.checked) {
                                    const index = this.state.persistentSelectedTags.indexOf(tagName);
                                    if (index > -1) {
                                        this.state.persistentSelectedTags.splice(index, 1);
                                        this.state._selectedTagsSet.delete(tagName);
                                    }
                                }
                            }
                        });
                        this.state.selectedTags = new Set(this.state.persistentSelectedTags);
                        // PERFORMANCE: Use Map lookup instead of array.find() inside map - O(1) vs O(n²)
                        const selectedTagObjects = this.state.persistentSelectedTags
                            .map(name => this._tagLookupMap?.get(name))
                            .filter(Boolean);
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

                    // Subcategories are now combined with weight - render weights directly
                    const sortedWeights = Array.from(weightGroupsOrSubcategories.entries())
                        .sort(([a], [b]) => (a || '').localeCompare(b || ''));

                    sortedWeights.forEach(([weight, priceGroups]) => {
                        const weightSection = document.createElement('div');
                        weightSection.className = 'weight-section ms-3 mb-1';
                        
                        // Check if there's only one price group for inline display
                        const isSinglePriceGroup = priceGroups instanceof Map && priceGroups.size === 1;
                        
                        // Create weight header with checkbox and collapse functionality
                        const weightHeader = document.createElement('div');
                        weightHeader.className = 'weight-header mb-1 d-flex align-items-center cursor-pointer';
                        if (isSinglePriceGroup) {
                            weightHeader.style.display = 'inline-flex';
                            weightHeader.style.marginRight = '12px';
                        }
                        weightHeader.addEventListener('click', (e) => {
                            if (e.target.type === 'checkbox') return; // Don't collapse if clicking checkbox
                            if (this.state.isSearching) return; // Don't collapse while searching
                            const weightContent = weightSection.querySelector('.weight-content');
                            if (!weightContent) return; // Safety check
                            const isCollapsed = weightContent.classList.contains('collapsed');
                            weightContent.classList.toggle('collapsed', !isCollapsed);
                            const collapseIcon = weightHeader.querySelector('.collapse-icon');
                            if (collapseIcon) {
                                collapseIcon.textContent = isCollapsed ? '▼' : '▶';
                            }
                            
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
                            // CRITICAL FIX: Use getSelectedTagObjects() which checks all sources
                            const selectedTagObjects = this.getSelectedTagObjects();
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
                        if (isSinglePriceGroup) {
                            weightContent.style.display = 'inline-block';
                        }
                        weightSection.appendChild(weightContent);

                        // Handle price groups - check if priceGroups is a Map (new structure) or Array (old structure)
                        if (priceGroups instanceof Map) {
                            // New structure: priceGroups is a Map of price groups to tag arrays
                            const sortedPriceGroups = Array.from(priceGroups.entries())
                                .sort(([a], [b]) => {
                                    // Sort price groups: No Price first, then by actual price value (numeric)
                                    if (a === 'No Price') return -1;
                                    if (b === 'No Price') return 1;
                                    // Extract numeric value from price strings (e.g., "$10" -> 10, "$15.50" -> 15.50)
                                    const priceA = parseFloat(a.replace(/[^0-9.]/g, '')) || 0;
                                    const priceB = parseFloat(b.replace(/[^0-9.]/g, '')) || 0;
                                    return priceA - priceB;
                                });
                            
                            const isSinglePriceGroup = sortedPriceGroups.length === 1;
                            
                            sortedPriceGroups.forEach(([priceGroup, tagArray], priceIndex) => {
                                const priceSection = document.createElement('div');
                                priceSection.className = 'price-section ms-3 mb-1';
                                
                                // If single price group, display inline with weight header
                                if (isSinglePriceGroup && priceIndex === 0) {
                                    priceSection.style.display = 'inline-block';
                                    priceSection.style.marginLeft = '12px';
                                    priceSection.style.verticalAlign = 'middle';
                                }
                                
                                // Create price header with checkbox and collapse functionality
                                const priceHeader = document.createElement('div');
                                priceHeader.className = 'price-header mb-1 d-flex align-items-center cursor-pointer';
                                priceHeader.addEventListener('click', (e) => {
                                    if (e.target.type === 'checkbox') return;
                                    if (this.state.isSearching) return;
                                    const priceContent = priceSection.querySelector('.price-content');
                                    if (!priceContent) return; // Safety check
                                    const isCollapsed = priceContent.classList.contains('collapsed');
                                    priceContent.classList.toggle('collapsed', !isCollapsed);
                                    const collapseIcon = priceHeader.querySelector('.collapse-icon');
                                    if (collapseIcon) {
                                        collapseIcon.textContent = isCollapsed ? '▼' : '▶';
                                    }
                                    this.removeDropdownInstructionBlurb();
                                });
                                
                                const priceCheckbox = document.createElement('input');
                                priceCheckbox.type = 'checkbox';
                                priceCheckbox.className = 'select-all-checkbox me-2';
                                priceCheckbox.addEventListener('change', (e) => {
                                    const savedScroll = this._saveAvailableScrollPosition();
                                    const isChecked = e.target.checked;
                                    const checkboxes = priceSection.querySelectorAll('input[type="checkbox"]');
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
                                    // CRITICAL FIX: Use getSelectedTagObjects() which checks all sources
                                    const selectedTagObjects = this.getSelectedTagObjects();
                                    this.updateSelectedTags(selectedTagObjects);
                                    this.efficientlyUpdateAvailableTagsDisplay();
                                    requestAnimationFrame(() => {
                                        this._restoreAvailableScrollPosition(savedScroll);
                                    });
                                });
                                
                                priceHeader.appendChild(priceCheckbox);
                                priceHeader.appendChild(document.createTextNode(priceGroup));
                                // Only show price collapse icon if there are multiple price groups
                                if (!isSinglePriceGroup) {
                                    const priceCollapseIcon = document.createElement('span');
                                    priceCollapseIcon.className = 'collapse-icon ms-auto';
                                    priceCollapseIcon.textContent = '▼';
                                    priceHeader.appendChild(priceCollapseIcon);
                                }
                                
                                // CRITICAL FIX: Append priceHeader to priceSection BEFORE appending priceSection to weightContent
                                priceSection.appendChild(priceHeader);
                                
                                // Create price content container
                                const priceContent = document.createElement('div');
                                priceContent.className = 'price-content';
                                priceSection.appendChild(priceContent);
                                
                                // Now append priceSection to weightContent
                                weightContent.appendChild(priceSection);
                                
                                // Add individual tags (sorted alphabetically by product name)
                                const tagsToRender = [...tagArray].sort((a, b) => {
                                    const aName = (a && (a['Product Name*'] || a.ProductName || a.displayName) || '').toString();
                                    const bName = (b && (b['Product Name*'] || b.ProductName || b.displayName) || '').toString();
                                    return aName.localeCompare(bName);
                                });
                                // PERFORMANCE: Use DocumentFragment for batch DOM insertion
                                const fragment = document.createDocumentFragment();
                                tagsToRender.forEach(tag => {
                                    const tagElement = this.createTagElement(tag, false);
                                    fragment.appendChild(tagElement);
                                });
                                priceContent.appendChild(fragment);
                            });
                        } else {
                            // Old structure: priceGroups is actually a tag array (backward compatibility)
                            const tagsToRender = [...(Array.isArray(priceGroups) ? priceGroups : [])].sort((a, b) => {
                                const aName = (a && (a['Product Name*'] || a.ProductName || a.displayName) || '').toString();
                                const bName = (b && (b['Product Name*'] || b.ProductName || b.displayName) || '').toString();
                                return aName.localeCompare(bName);
                            });
                            // PERFORMANCE: Use DocumentFragment for batch DOM insertion
                            const fragment = document.createDocumentFragment();
                            tagsToRender.forEach(tag => {
                                const tagElement = this.createTagElement(tag, false);
                                fragment.appendChild(tagElement);
                            });
                            weightContent.appendChild(fragment);
                        }
                    });
                });
            });
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
                
                // CRITICAL FIX: Mark tags as ready and enable dropdowns after a short delay
                // This prevents dropdowns from freezing if used immediately after page load
                this._fetchingAvailableTags = false;
                setTimeout(() => {
                    // Ensure TagManager is fully initialized before enabling dropdowns
                    if (!this.state.initialized) {
                        this.state.initialized = true;
                    }
                    console.log('✅ Dropdowns enabled - tags fully loaded and TagManager initialized');
                }, 100); // Small delay to ensure all event listeners are attached
                
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
        
        // CRITICAL FIX: Ensure _selectedTagsSet is initialized before checking checkbox state
        if (!this.state._selectedTagsSet) {
            this.state._selectedTagsSet = new Set(this.state.persistentSelectedTags || []);
        }
        
        // PERFORMANCE: Use Set for O(1) lookup instead of array.includes() - O(n)
        checkbox.checked = this.state._selectedTagsSet.has(displayName);
        
        // Add event listener with proper error handling and improved logic
        const handleCheckboxChange = (e) => {
            // CRITICAL FIX: Always allow checkbox clicks - clear drag attributes if they exist
            // This prevents checkboxes from being permanently disabled after drag operations
            if (e.target.hasAttribute('data-reordering')) {
                e.target.removeAttribute('data-reordering');
                console.log('🔧 Cleared data-reordering attribute from checkbox:', displayName);
            }
            if (e.target.hasAttribute('data-drag-disabled')) {
                e.target.removeAttribute('data-drag-disabled');
                e.target.style.pointerEvents = 'auto';
                console.log('🔧 Cleared data-drag-disabled attribute from checkbox:', displayName);
            }
            
            // CRITICAL FIX: Ensure checkbox is enabled even if drag state was set
            e.target.style.pointerEvents = 'auto';
            e.target.removeAttribute('data-reordering');
            e.target.removeAttribute('data-drag-disabled');
            
            // Ensure the checkbox state is properly updated
            const isChecked = e.target.checked;
            
            // CRITICAL FIX: Ensure _selectedTagsSet exists before using it
            if (!this.state._selectedTagsSet) {
                this.state._selectedTagsSet = new Set(this.state.persistentSelectedTags || []);
            }
            
            // PERFORMANCE: Use Set for O(1) lookups and updates instead of array operations
            if (isChecked) {
                if (!this.state._selectedTagsSet.has(displayName)) {
                    this.state.persistentSelectedTags.push(displayName);
                    this.state._selectedTagsSet.add(displayName);
                    // CRITICAL FIX: Mark checkbox as recently checked to prevent race conditions
                    checkbox.setAttribute('data-recently-checked', 'true');
                    setTimeout(() => checkbox.removeAttribute('data-recently-checked'), 1000);
                }
            } else {
                const index = this.state.persistentSelectedTags.indexOf(displayName);
                if (index > -1) {
                    this.state.persistentSelectedTags.splice(index, 1);
                    this.state._selectedTagsSet.delete(displayName);
                }
            }
            
            // Update the regular selectedTags set to match persistent ones
            this.state.selectedTags = new Set(this.state.persistentSelectedTags);
            
            // PERFORMANCE: For deselection, use immediate DOM manipulation instead of full rebuild
            if (!isChecked && isForSelectedTags) {
                // Find and remove the tag element from selected tags immediately for instant feedback
                const tagItem = e.target.closest('.tag-item');
                if (tagItem) {
                    // Immediate removal - no animation delay
                    tagItem.remove();
                    this.updateTagCount('selected', this.state.persistentSelectedTags.length);
                }
                
                // Update the corresponding checkbox in available tags - use cached reference if possible
                requestAnimationFrame(() => {
                    // Try to get checkbox using the optimized approach - search only within available tags
                    const availableContainer = document.getElementById('availableTags');
                    if (availableContainer) {
                        const availableCheckbox = availableContainer.querySelector(`input[data-tag-name="${displayName}"]`);
                        if (availableCheckbox && availableCheckbox.checked) {
                            availableCheckbox.checked = false;
                        }
                    }
                });
                
                // Defer expensive operations to background with longer delay
                setTimeout(() => this.saveSelectionState('checkbox_selection'), 500);
                
                // CRITICAL: Do NOT trigger any filter updates or available tags re-render
                return; // Exit immediately to prevent any further processing
            } else {
                // For selection, defer full rebuild
                setTimeout(() => {
                    // CRITICAL FIX: Use fallback lookup if tag not in _tagLookupMap
                    // This prevents tags from disappearing on first selection
                    const selectedTagObjects = this.state.persistentSelectedTags
                        .map(name => {
                            // Try lookup map first
                            let tag = this._tagLookupMap?.get(name);
                            if (tag) return tag;
                            
                            // Fallback to state.tags
                            tag = this.state.tags.find(t => t && (t['Product Name*'] === name || t.ProductName === name));
                            if (tag) return tag;
                            
                            // Fallback to originalTags
                            tag = this.state.originalTags.find(t => t && (t['Product Name*'] === name || t.ProductName === name));
                            if (tag) return tag;
                            
                            // If still not found, log warning but don't filter out - preserve selection
                            console.warn(`Tag '${name}' not found in lookup maps, but preserving selection`);
                            return null;
                        })
                        .filter(Boolean);
                    
                    // Only update if we have valid tag objects
                    if (selectedTagObjects.length > 0) {
                        this.updateSelectedTags(selectedTagObjects);
                    } else {
                        // If no valid objects but we have persistent selections, rebuild lookup map
                        console.warn('No valid tag objects found, rebuilding lookup map');
                        // Rebuild the lookup map
                        this._tagLookupMap = new Map();
                        this.state.tags.forEach(t => {
                            if (t && t['Product Name*']) {
                                this._tagLookupMap.set(t['Product Name*'], t);
                            }
                        });
                        this.state.originalTags.forEach(t => {
                            if (t && t['Product Name*'] && !this._tagLookupMap.has(t['Product Name*'])) {
                                this._tagLookupMap.set(t['Product Name*'], t);
                            }
                        });
                        // Retry with rebuilt map
                        const retryTagObjects = this.state.persistentSelectedTags
                            .map(name => this._tagLookupMap?.get(name))
                            .filter(Boolean);
                        if (retryTagObjects.length > 0) {
                            this.updateSelectedTags(retryTagObjects);
                        }
                    }
                }, 0);
                
                // Defer state saving to avoid blocking UI
                setTimeout(() => this.saveSelectionState('checkbox_selection'), 50);
            }
        };
        
        // Store the handler on the element itself so we can reference it later
        checkbox._changeHandler = handleCheckboxChange;
        
        // Bind change handler for both available and selected tags
        checkbox.addEventListener('change', handleCheckboxChange);
        
        // CRITICAL FIX: Add click handler as fallback to ensure checkboxes always respond
        // This prevents checkboxes from being unresponsive after drag operations or tag updates
        checkbox.addEventListener('click', (e) => {
            // Clear any drag attributes that might block the checkbox
            if (e.target.hasAttribute('data-reordering') || e.target.hasAttribute('data-drag-disabled')) {
                e.target.removeAttribute('data-reordering');
                e.target.removeAttribute('data-drag-disabled');
                e.target.style.pointerEvents = 'auto';
                console.log('🔧 Click handler cleared drag attributes from checkbox:', displayName);
            }
            // Ensure checkbox is enabled
            e.target.disabled = false;
            e.target.style.pointerEvents = 'auto';
        });
        
        // Ensure the checkbox is not disabled by drag-and-drop manager
        checkbox.style.pointerEvents = 'auto';
        checkbox.removeAttribute('data-drag-disabled');
        checkbox.removeAttribute('data-reordering');
        checkbox.disabled = false;
        
        // Store the checkbox state in a data attribute for debugging
        checkbox.setAttribute('data-tag-name', displayName);
        checkbox.setAttribute('data-is-selected-tag', isForSelectedTags.toString());
        
        // No longer need mousedown handler - deselection is now optimized with immediate DOM manipulation

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
        // CRITICAL FIX: ALWAYS check database fields FIRST - database is the source of truth
        // NEVER use Excel Lineage if database lineage exists
        if (tag.canonical_lineage || tag.currentLineage) {
            // Database lineage exists - use it EXCLUSIVELY (this is the source of truth)
            lineage = tag.canonical_lineage || tag.currentLineage;
            // CRITICAL: Log when we're overriding Excel lineage with database lineage
            if (tag.Lineage && tag.Lineage.toUpperCase() !== lineage.toUpperCase()) {
                console.log(`🔄 TagManager: Using database lineage for "${displayName}": Excel="${tag.Lineage}" → DB="${lineage}"`);
            }
            // CRITICAL: Overwrite Excel Lineage in tag object to ensure consistency
            if (tag.Lineage !== lineage) {
                tag.Lineage = lineage;
                tag.lineage = lineage.toLowerCase();
                console.log(`✅ TagManager: Updated tag object for "${displayName}" - set Lineage to database value: "${lineage}"`);
            }
        } else {
            // CRITICAL: Only fallback to Excel Lineage if database lineage is completely missing
            // This should rarely happen if backend lineage alignment is working correctly
            lineage = tag.Lineage || tag.lineage || tag['Lineage*'] || 'MIXED';
            if (lineage && lineage !== 'MIXED') {
                console.warn(`⚠️ TagManager: Tag "${displayName}" missing database lineage (canonical_lineage/currentLineage), using Excel Lineage: "${lineage}"`);
                console.warn(`⚠️ TagManager: Tag object fields:`, {
                    canonical_lineage: tag.canonical_lineage,
                    currentLineage: tag.currentLineage,
                    Lineage: tag.Lineage,
                    lineage: tag.lineage
                });
            }
        }
        
        // Normalize lineage to uppercase for consistent matching - respect database value
        lineage = (lineage || '').toString().trim().toUpperCase();
        
        // CRITICAL FIX: Classic types should NEVER have MIXED/THC lineage - convert to HYBRID
        // This ensures UI displays correct lineage even if database/Excel has wrong value
        const productTypeCheck = tag['Product Type*'] || tag.productType || tag.ProductType || '';
        const classicTypes = ['flower', 'pre-roll', 'concentrate', 'infused pre-roll', 'solventless concentrate', 'vape cartridge', 'rso/co2 tankers'];
        const isClassicType = classicTypes.map(ct => ct.toLowerCase()).includes((productTypeCheck || '').toString().toLowerCase());
        if (isClassicType && (lineage === 'MIXED' || lineage === 'THC')) {
            lineage = 'HYBRID';
        }
        
        // Only set default if lineage is completely missing
        if (!lineage) {
            lineage = isClassicType ? 'HYBRID' : 'MIXED';
        }
        
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
        let displayLineage = lineage; // Start with database lineage (already converted if classic type)
        const nameStr = (tag['Product Name*'] || tag.ProductName || tag.productName || displayName || '').toString().toLowerCase();
        const descStr = (tag.Description || tag.description || '').toString().toLowerCase();
        const brandStr = (tag['Product Brand'] || tag.productBrand || tag.brand || '').toString().toLowerCase();
        const ratioStr = (tag.Ratio || tag['Ratio_or_THC_CBD'] || '').toString().toLowerCase();
        const lineageStr = (lineage || '').toString().toLowerCase();
        const lowerProductType = (productTypeCheck || '').toString().toLowerCase();

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
        
        // CRITICAL: Define validDatabaseLineages and hasValidDatabaseLineage BEFORE the if/else block
        // so it's always available regardless of which path is taken
        // Valid database lineages: SATIVA, INDICA, HYBRID, HYBRID/SATIVA, HYBRID/INDICA, CBD, CBD_BLEND, MIXED, PARA, PARAPHERNALIA
        const validDatabaseLineages = ['SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA', 'CBD', 'CBD_BLEND', 'MIXED', 'PARA', 'PARAPHERNALIA'];
        const hasValidDatabaseLineage = validDatabaseLineages.includes(lineage);
        
        // CRITICAL FIX: Paraphernalia products should ALWAYS get PARAPHERNALIA lineage (pink color)
        // Check if product type is "paraphernalia" - this overrides everything else
        if (lowerProductType === 'paraphernalia') {
            displayLineage = 'PARAPHERNALIA';
            verboseLog(`🎯 Paraphernalia product detected: "${displayName}" (${lowerProductType}) → PARAPHERNALIA (pink)`);
            // Set the lineage data attributes
            tagElement.dataset.lineage = 'PARAPHERNALIA';
            row.dataset.lineage = 'PARAPHERNALIA';
            // Update tag object
            if (!tag.canonical_lineage && !tag.currentLineage) {
                tag.currentLineage = 'PARAPHERNALIA';
            }
            // Skip the rest of the lineage logic for Paraphernalia products
        } else if (lowerProductType.startsWith('high cbd')) {
            // CRITICAL FIX: High CBD products should ALWAYS get CBD_BLEND lineage (takes priority over database lineage)
            // Check if product type starts with "high cbd" - this overrides everything else
            displayLineage = 'CBD_BLEND';
            verboseLog(`🎯 High CBD product detected: "${displayName}" (${lowerProductType}) → CBD_BLEND (yellow)`);
            // Set the lineage data attributes
            tagElement.dataset.lineage = 'CBD_BLEND';
            row.dataset.lineage = 'CBD_BLEND';
            // Update tag object
            if (!tag.canonical_lineage && !tag.currentLineage) {
                tag.currentLineage = 'CBD_BLEND';
            }
            // Skip the rest of the lineage logic for High CBD products
        } else {
        
        // CRITICAL: Only apply fallback logic if database lineage is missing, invalid, or MIXED
        
        // Apply nonclassic product type logic ONLY if database lineage is missing or invalid
        // Reuse classicTypes already declared above (line 4325)
        const isNonclassic = !classicTypes.map(ct => ct.toLowerCase()).includes(lowerProductType);
        
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
            // Even if database has SATIVA/INDICA/HYBRID, we ignore it for nonclassic types
            if (isClassicLineage && hasValidDatabaseLineage) {
                verboseLog(`⚠️ CAPSULE/NONCLASSIC: Ignoring classic lineage "${lineage}" from database for "${displayName}" - forcing MIXED/CBD_BLEND`);
            }
            
            // Only apply Product Strain fallback logic if database lineage is missing, invalid, or is a classic lineage
            const productStrain = tag['Product Strain'] || tag.productStrain || tag.ProductStrain || '';
            const strainStr = String(productStrain).toLowerCase();
            
            // CRITICAL: For non-classic types, always check for CBD indicators first
            // If database has a valid non-classic lineage (like CBD_BLEND or MIXED), use it
            // But if database has classic lineage, ignore it and use CBD detection
            if (!isClassicLineage && hasValidDatabaseLineage && (lineage === 'CBD_BLEND' || lineage === 'MIXED' || lineage === 'PARAPHERNALIA')) {
                // Use valid non-classic lineage from database
                displayLineage = lineage;
                verboseLog(`🎨 NON-CLASSIC using valid DB lineage: "${displayName}" → ${displayLineage}`);
            } else if (strainStr.includes('cbd blend') || strainStr.includes('cbd') || strainStr.includes('cbn') || strainStr.includes('cbc') || strainStr.includes('cbg')) {
                // CBD family products display as CBD Blend lineage (yellow color)
                displayLineage = 'CBD_BLEND';
                verboseLog(`🎨 NON-CLASSIC CBD FAMILY: "${displayName}" → CBD_BLEND (yellow)`);
            } else if (hasCbdIndicator()) {
                displayLineage = 'CBD_BLEND';
                verboseLog(`🎨 NON-CLASSIC CBD SIGNAL: "${displayName}" → CBD_BLEND (yellow)`);
            } else if (lowerProductType === 'paraphernalia' || strainStr.includes('paraphernalia')) {
                // CRITICAL FIX: Paraphernalia products should be pink - check both product type and strain
                displayLineage = 'PARAPHERNALIA'; // Pink color
                verboseLog(`🎨 NON-CLASSIC PARA: "${displayName}" (${lowerProductType}) → PARAPHERNALIA (pink)`);
            } else {
                // Default to MIXED for all other nonclassic types (including capsules without CBD indicators)
                displayLineage = 'MIXED'; // Blue color
                verboseLog(`🎨 NON-CLASSIC default (capsule/nonclassic): "${displayName}" → MIXED (blue)`);
            }
        } else {
            // Classic types - use database lineage or default to HYBRID (never MIXED for classic types)
            // CRITICAL FIX: Always use the resolved lineage (which already has database value and MIXED->HYBRID conversion)
            displayLineage = lineage || 'HYBRID';
            verboseLog(`🎨 Classic type using database lineage: "${displayName}" → ${displayLineage}`);
        }
        } // End of else block for High CBD check
        
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
                highThcImg.style.cssText = 'height:28px;width:28px;object-fit:contain;margin-left:6px;vertical-align:middle';
                imageContainer.appendChild(highThcImg);
            } else if (status === 'DOH') {
                // Add regular DOH image with optimized loading
                const dohImg = document.createElement('img');
                dohImg.src = '/static/img/DOH.png';
                dohImg.alt = 'DOH Compliant';
                dohImg.title = 'DOH Compliant Product';
                dohImg.loading = 'lazy';
                dohImg.style.cssText = 'height:36px;width:36px;object-fit:contain;margin-left:6px;vertical-align:middle';
                imageContainer.appendChild(dohImg);
            }
            // NONE shows no image
            
            performanceUtils.endTiming(startTime, 'DOH image update');
        };
        
        // Check if product type indicates High CBD (more robust check)
        // Check both the original product type and normalized version
        const productTypeOriginal = (tag['Product Type*'] || tag.productType || tag.Type || '').toString().toLowerCase().trim();
        const isHighCbdProduct = productTypeForImages.startsWith('high cbd') || 
                                 productTypeForImages.includes('doh high cbd') ||
                                 productTypeOriginal.startsWith('high cbd') ||
                                 productTypeOriginal.includes('doh high cbd') ||
                                 productTypeForImages.includes('high cbd edible') ||
                                 productTypeOriginal.includes('high cbd edible');
        
        // Set initial image based on current DOH status
        let initialDohStatus = 'NONE'; // Default to NONE
        
        // For High CBD products, only show High CBD badge (not DOH badge)
        // CRITICAL: This check must happen BEFORE any DOH status checks
        if (isHighCbdProduct) {
            // High CBD products should only show High CBD badge, not DOH badge
            // Clear any existing images first
            while (imageContainer.firstChild) {
                imageContainer.removeChild(imageContainer.firstChild);
            }
            const highCbdImg = document.createElement('img');
            highCbdImg.src = '/static/img/HighCBD.png';
            highCbdImg.alt = 'High CBD';
            highCbdImg.title = 'High CBD Product';
            highCbdImg.loading = 'lazy';
            highCbdImg.style.cssText = 'height:24px;width:auto;margin-left:6px;vertical-align:middle';
            imageContainer.appendChild(highCbdImg);
            // Don't call updateDohImage for High CBD products - skip DOH logic entirely
        } else {
            // For non-High CBD products, use normal DOH logic
            // Check explicit DOH field first
            if (dohValue === 'DOH' || dohValue === 'YES' || dohValue === 'Y') {
                initialDohStatus = 'DOH';
            } else if (dohValue === 'THC') {
                initialDohStatus = 'THC';
            } else if (dohValue === 'CBD') {
                initialDohStatus = 'CBD';
            } else if (dohValue === 'NO' || dohValue === 'NONE') {
                initialDohStatus = 'NONE';
            } 
            // Then check product type for High THC indicators
            else if (productTypeForImages.startsWith('high thc') || productTypeForImages.includes('doh high thc') || productTypeForImages.includes('high thc')) {
                initialDohStatus = 'THC';
            }
            
            updateDohImage(initialDohStatus);
        }
        
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
        lineageSelect.style.height = '14px'; /* Compact */
        lineageSelect.style.backgroundColor = 'rgba(255, 255, 255, 0.15)';
        lineageSelect.style.border = '0.5px solid rgba(255, 255, 255, 0.2)';
        lineageSelect.style.borderRadius = '2px'; /* Very small radius */
        lineageSelect.style.cursor = 'pointer';
        lineageSelect.style.color = '#fff';
        lineageSelect.style.backdropFilter = 'blur(10px)';
        lineageSelect.style.transition = 'all 0.2s ease';
        lineageSelect.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.1)';
        lineageSelect.style.fontSize = '8px'; /* Compact font */
        lineageSelect.style.transform = 'none'; /* No transform - CSS handles size */
        lineageSelect.style.transformOrigin = 'left center';
        lineageSelect.style.lineHeight = '1.0';
        lineageSelect.style.fontWeight = 'bold';
        lineageSelect.style.letterSpacing = '-0.1px';
        lineageSelect.style.marginLeft = '-4px';
        lineageSelect.style.marginRight = '2px';
        lineageSelect.style.width = '35px'; /* Compact */
        lineageSelect.style.minWidth = '30px';
        lineageSelect.style.maxWidth = '40px';
        lineageSelect.style.flexShrink = '0';
        lineageSelect.style.overflow = 'visible';
        lineageSelect.style.textOverflow = 'clip';
        lineageSelect.style.whiteSpace = 'nowrap';
        lineageSelect.style.padding = '2px 6px 2px 3px'; /* Minimal padding for compact dropdown */
        lineageSelect.style.boxSizing = 'border-box';
        /* Style dropdown arrow - larger and more visible */
        lineageSelect.style.backgroundImage = "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='8' height='8' viewBox='0 0 12 12'%3E%3Cpath fill='%23ffffff' d='M6 9L1 4h10z'/%3E%3C/svg%3E\")";
        lineageSelect.style.backgroundRepeat = 'no-repeat';
        lineageSelect.style.backgroundPosition = 'right 3px center';
        lineageSelect.style.backgroundSize = '8px 8px'; /* Larger arrow */
        lineageSelect.style.webkitAppearance = 'none';
        lineageSelect.style.mozAppearance = 'none';
        lineageSelect.style.appearance = 'none';
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
        // Add lineage options (no product-type filtering)
        const allLineageOptions = [
            { value: 'SATIVA', label: 'S' },
            { value: 'INDICA', label: 'I' },
            { value: 'HYBRID', label: 'H' },
            { value: 'HYBRID/INDICA', label: 'H/I' },
            { value: 'HYBRID/SATIVA', label: 'H/S' },
            { value: 'CBD', label: 'CBD' },
            { value: 'PARA', label: 'P' },
            { value: 'MIXED', label: 'THC' }
        ];
        
        // CRITICAL: Calculate normalized lineage BEFORE creating options, so option selection uses database lineage
        // Set the dropdown value - handle mappings for display
        // CRITICAL: ALWAYS prefer database lineage (canonical_lineage/currentLineage) over Excel Lineage
        let normalizedLineage = (lineage || '').toString().toUpperCase().trim();
        
        // CRITICAL FIX: Force database lineage if it exists, regardless of what lineage variable says
        // IMPORTANT: Check tag object DIRECTLY, not the lineage variable, to ensure we get the latest database values
        const tagDbLineage = (tag.canonical_lineage || tag.currentLineage || '').toString().toUpperCase().trim();
        if (tagDbLineage) {
            // Database lineage exists - use it exclusively, ignore Excel Lineage completely
            if (tagDbLineage !== normalizedLineage) {
                console.log(`🔄 FORCING database lineage for ${displayName}: ${normalizedLineage} → ${tagDbLineage} (from tag.canonical_lineage=${tag.canonical_lineage} or tag.currentLineage=${tag.currentLineage})`);
            }
            normalizedLineage = tagDbLineage;  // Force database lineage
        } else {
            // No database lineage - log warning for debugging
            if (isForSelectedTags && normalizedLineage && normalizedLineage !== 'MIXED') {
                console.warn(`⚠️ Selected tag "${displayName}" has no database lineage (canonical_lineage/currentLineage), using: ${normalizedLineage}`);
                console.warn(`⚠️ Tag object lineage fields:`, {
                    canonical_lineage: tag.canonical_lineage || 'MISSING',
                    currentLineage: tag.currentLineage || 'MISSING',
                    Lineage: tag.Lineage || 'MISSING',
                    lineage: tag.lineage || 'MISSING'
                });
            }
        }
        
        // Show all lineage options for every product type (no restrictions)
        let uniqueLineages = allLineageOptions;
        
        // Helper function to determine if a lineage should map to MIXED
        const shouldMapToMixed = (lineageValue) => {
            const validLineages = ['SATIVA', 'INDICA', 'HYBRID', 'HYBRID/INDICA', 'HYBRID/SATIVA', 'CBD', 'CBD_BLEND', 'PARA', 'PARAPHERNALIA', 'MIXED'];
            return !validLineages.includes((lineageValue || '').toUpperCase());
        };
        
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
            // CRITICAL FIX: Classic types should never get MIXED - use HYBRID instead
            if (isClassicTypeForDropdown) {
                lineageSelect.value = 'HYBRID';
                console.log(`🔄 DROPDOWN FIX: Mapped invalid lineage "${normalizedLineage}" to HYBRID for classic type "${displayName}"`);
            } else {
                lineageSelect.value = 'MIXED';
            }
        } else if (normalizedLineage && uniqueLineages.some(opt => opt.value === normalizedLineage)) {
            lineageSelect.value = normalizedLineage;
        } else {
            // CRITICAL FIX: Smart fallback based on product type and lineage
            if (isClassicTypeForDropdown) {
                // Classic types default to HYBRID
                lineageSelect.value = 'HYBRID';
                console.warn(`⚠️ Invalid lineage value "${normalizedLineage}" for classic type "${displayName}", defaulting to HYBRID`);
            } else if (isParaphernaliaType || normalizedLineage === 'PARA' || normalizedLineage === 'PARAPHERNALIA') {
                // Paraphernalia items should always use PARA
                lineageSelect.value = 'PARA';
            } else if (normalizedLineage === 'HYBRID' && !isClassicTypeForDropdown) {
                // Non-classic items with HYBRID lineage (likely accessories/paraphernalia misclassified)
                // Silently default to MIXED (THC) without warning since HYBRID isn't valid for non-classic
                lineageSelect.value = 'MIXED';
            } else {
                // All other non-classic types default to MIXED
                lineageSelect.value = 'MIXED';
                console.warn(`⚠️ Invalid lineage value "${normalizedLineage}" for "${displayName}", defaulting to MIXED`);
            }
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
            // CRITICAL FIX: Skip if this is a programmatic update (not user-initiated)
            if (e.target._isProgrammaticUpdate) {
                e.target._isProgrammaticUpdate = false;
                return; // Don't process programmatic updates
            }
            
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

        // Create DOH dropdown (same style as lineage dropdown) - all products use regular DOH dropdown
        const dohSelect = document.createElement('select');
        dohSelect.className = 'form-select form-select-sm doh-select doh-dropdown doh-dropdown-mini';
        dohSelect.style.height = '14px'; /* Compact */
        dohSelect.style.backgroundColor = 'rgba(255, 255, 255, 0.15)';
        dohSelect.style.border = '0.5px solid rgba(255, 255, 255, 0.2)';
        dohSelect.style.borderRadius = '2px'; /* Very small radius */
        dohSelect.style.cursor = 'pointer';
        dohSelect.style.color = '#fff';
        dohSelect.style.backdropFilter = 'blur(10px)';
        dohSelect.style.transition = 'all 0.2s ease';
        dohSelect.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.1)';
        dohSelect.style.marginLeft = '1px';
        dohSelect.style.marginRight = '-2px';
        dohSelect.style.minWidth = '70px'; /* Even wider for full text visibility */
        dohSelect.style.maxWidth = '70px';
        dohSelect.style.width = '70px';
        dohSelect.style.fontSize = '9px'; /* Slightly larger font */
        dohSelect.style.transform = 'none'; /* No transform - CSS handles size */
        dohSelect.style.transformOrigin = 'left center';
        dohSelect.style.lineHeight = '1.0';
        dohSelect.style.fontWeight = '300';
        dohSelect.style.letterSpacing = '-0.1px';
        dohSelect.style.padding = '2px 12px 2px 6px'; /* More padding for full text visibility */
        dohSelect.style.textAlign = 'left'; /* Left align text */
        dohSelect.style.overflow = 'visible'; /* Don't clip text */
        dohSelect.style.textOverflow = 'clip'; /* Don't use ellipsis */
        dohSelect.style.whiteSpace = 'nowrap'; /* Keep text on one line */
        dohSelect.style.webkitAppearance = 'none'; /* Remove default arrow */
        dohSelect.style.mozAppearance = 'none';
        dohSelect.style.appearance = 'none';
        dohSelect.style.boxSizing = 'border-box';
        /* Add custom dropdown arrow - larger and more visible */
        dohSelect.style.backgroundImage = "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='8' height='8' viewBox='0 0 12 12'%3E%3Cpath fill='%23000000' d='M6 9L1 4h10z'/%3E%3C/svg%3E\")";
        dohSelect.style.backgroundRepeat = 'no-repeat';
        dohSelect.style.backgroundPosition = 'right 6px center';
        dohSelect.style.backgroundSize = '8px 8px'; /* Larger arrow */

        let currentDropdownStatus = 'NONE'; // Default to NONE
        
        // All products get normal DOH dropdown
        const dohOptions = [
            { value: 'NONE', label: '' }, // Empty label for "No DOH"
            { value: 'DOH', label: 'DOH' },
            { value: 'THC', label: 'THC' },
            { value: 'CBD', label: 'CBD' }
        ];
        
        // Use the same logic as initialDohStatus to determine current dropdown state
        // For high CBD products, CBD trumps DOH (High CBD implies DOH compliance)
        if (isHighCbdProduct) {
            // If DOH/Yes status exists, CBD trumps it for High CBD products
            if (dohValue === 'DOH' || dohValue === 'YES' || dohValue === 'Y') {
                currentDropdownStatus = 'CBD';
            } else if (dohValue === 'THC') {
                // Keep THC if explicitly set
                currentDropdownStatus = 'THC';
            } else if (dohValue === 'CBD') {
                currentDropdownStatus = 'CBD';
            } else {
                // Default to CBD for High CBD products (no status, No, or NONE)
                currentDropdownStatus = 'CBD';
            }
        } else {
            // Non-High CBD products: Check explicit DOH field first
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
            // Then check product type for High THC indicators (DOH High THC)
            else if (productTypeForImages.startsWith('high thc') || productTypeForImages.includes('doh high thc') || productTypeForImages.includes('high thc')) {
                currentDropdownStatus = 'THC';
            }
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
            // CRITICAL FIX: Prevent interactions during initial tag load to avoid freezes
            if (this._fetchingAvailableTags || !this.state.initialized) {
                console.warn('⚠️ DOH dropdown change blocked - tags still loading or TagManager not initialized');
                // Revert to previous value
                e.target.value = currentDropdownStatus;
                return;
            }
            
            let newDohStatus = e.target.value;
            const prevValue = currentDropdownStatus;
            
            // For regular DOH dropdown, map NONE to No for backend
            let backendDohStatus = (newDohStatus === 'NONE') ? 'No' : newDohStatus;
            
            // Immediate UI feedback - update image first for responsiveness
            if (typeof updateDohImage === 'function') {
                updateDohImage(newDohStatus);
            }
            
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
                        doh_status: backendDohStatus
                    })
                });
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                    throw new Error(errorData.error || `Server returned ${response.status}`);
                }
                
                const data = await response.json();
                if (data.success) {
                    // On success, update tag DOH status in state
                    tag.DOH = backendDohStatus;
                    tag.doh = backendDohStatus;
                    tag['DOH Compliant (Yes/No)'] = backendDohStatus;
                    dohSelect.value = newDohStatus;  // Keep dropdown showing UI value
                    verboseLog(`✅ DOH status updated for "${displayName}" to: ${backendDohStatus} (frontend dropdown: ${newDohStatus})`);
                    
                    // Image already updated above for immediate feedback
                    
                    // Update DOH in both available and selected tags displays
                    if (typeof this.updateDohInAllDisplays === 'function') {
                        this.updateDohInAllDisplays(displayName, newDohStatus);
                    }
                    
                } else {
                    // Revert image on failure
                    updateDohImage(prevValue);
                    throw new Error(data.message || 'Failed to update DOH status');
                }
                
                // Remove saving option
                dohSelect.removeChild(savingOption);
            } catch (error) {
                console.error(`Failed to update DOH status:`, error);
                // On failure, revert to previous value
                dohSelect.value = prevValue;
                // Revert image
                updateDohImage(prevValue);
                alert(`Failed to update DOH status: ` + error.message);
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
        
        // PERFORMANCE: Increase batch size for faster rendering (100 tags per batch)
        // Use larger batches for better performance on modern browsers
        const BATCH_SIZE = 100;
        let index = 0;
        
        const renderBatch = () => {
            const endIndex = Math.min(index + BATCH_SIZE, tags.length);
            const fragment = document.createDocumentFragment();
            
            // PERFORMANCE: Build HTML string first, then set innerHTML once per batch
            // This is faster than multiple appendChild calls for large batches
            const batchHtml = [];
            for (let i = index; i < endIndex; i++) {
                const tagElement = this.createTagElement(tags[i], false);
                if (tagElement) {
                    fragment.appendChild(tagElement);
                }
            }
            
            container.appendChild(fragment);
            index = endIndex;
            
            // Continue rendering if there are more tags
            if (index < tags.length) {
                // CRITICAL FIX: Use requestAnimationFrame for smoother rendering without flickering
                // This ensures rendering happens at the optimal time for the browser
                requestAnimationFrame(renderBatch);
            }
        };
        
        // Start rendering immediately
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
        // PERFORMANCE: Instant checkbox response - defer ALL processing
        // Guards only
        if (this.state.isProcessingDeselection || this.state.isClearing || this.isMovingTags) return;
        if (e.target.hasAttribute('data-reordering') || e.target.hasAttribute('data-drag-disabled')) return;
        if (!tag || !tag['Product Name*']) return;
        
        // PERFORMANCE: Defer everything to avoid blocking checkbox UI
        const isChecked = e.target.checked;
        const originalName = tag['Product Name*'];
        
        // Only handle deselection from selected tags
        if (!isChecked && e.target.closest('#selectedTags')) {
            setTimeout(() => {
                const availableCheckbox = document.querySelector(`#availableTags .tag-checkbox[value="${originalName}"]`);
                if (availableCheckbox) availableCheckbox.checked = false;
                
                this.clearFiltersForDeselectedTag(tag);
                
                if (tag.Source && (tag.Source === 'JSON Match' || tag.Source.includes('Educated Guess'))) {
                    this.syncDeselectionWithBackend(originalName);
                }
            }, 0);
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
            
            // CRITICAL FIX: Debounce backend updates to prevent database lock conflicts when doing many rapid changes
            // This batches rapid changes so they don't all hit the database at once
            this.updateLineageOnBackendDebounced(tagName, newLineage);
        }
    },
    
    // CRITICAL FIX: Global queue system to serialize ALL lineage updates and prevent database locks
    // This ensures only one update hits the database at a time, even for different tags
    _lineageUpdateQueue: {},  // Per-tag latest values (deduplicates rapid changes to same tag)
    _lineageUpdateTimeout: null,  // Single global timeout for all updates
    _lineageUpdateProcessing: false,  // Flag to prevent concurrent processing
    _lineageUpdatePending: new Set(),  // Track which tags have pending updates
    _lineageUpdateInProgress: false,  // Flag to prevent clearing selected tags during lineage updates
    
    updateLineageOnBackendDebounced(tagName, newLineage) {
        // CRITICAL FIX: Track pending lineage updates for reload protection
        if (!this._lineageUpdatePending) {
            this._lineageUpdatePending = new Set();
        }
        this._lineageUpdatePending.add(tagName);
        // Store the latest lineage value for this tag (overwrites previous if same tag)
        this._lineageUpdateQueue[tagName] = newLineage;
        this._lineageUpdatePending.add(tagName);
        
        // Cancel any pending global timeout
        if (this._lineageUpdateTimeout) {
            clearTimeout(this._lineageUpdateTimeout);
            this._lineageUpdateTimeout = null;
        }
        
        // Debounce: wait 500ms before starting to process updates
        // This batches rapid changes across ALL tags, not just per-tag
        this._lineageUpdateTimeout = setTimeout(() => {
            this._processLineageUpdateQueue();
        }, 500); // 500ms debounce - batches rapid changes across all tags
    },
    
    async _processLineageUpdateQueue() {
        // Prevent concurrent processing
        if (this._lineageUpdateProcessing) {
            // If already processing, reschedule this batch
            this._lineageUpdateTimeout = setTimeout(() => {
                this._processLineageUpdateQueue();
            }, 200);
            return;
        }
        
        // Copy the queue before clearing (prevents race conditions with new updates)
        const updatesToProcess = Object.entries({...this._lineageUpdateQueue});
        if (updatesToProcess.length === 0) {
            return;
        }
        
        // Clear the queue and pending set (new updates will create a new batch)
        this._lineageUpdateQueue = {};
        this._lineageUpdatePending.clear();
        this._lineageUpdateTimeout = null;
        this._lineageUpdateProcessing = true;
        
        verboseLog(`🔄 Processing ${updatesToProcess.length} lineage update(s) sequentially...`);
        
        // Process updates one at a time with increasing delays between each
        // This ensures database operations don't compete for locks, especially during Excel uploads
        for (let i = 0; i < updatesToProcess.length; i++) {
            const [tagName, newLineage] = updatesToProcess[i];
            
            // Retry logic with exponential backoff for database lock errors
            let retryCount = 0;
            const maxRetries = 3;
            let lastError = null;
            
            while (retryCount <= maxRetries) {
                try {
                    // Wait between updates (longer delay if retrying)
                    if (i > 0 || retryCount > 0) {
                        const delay = retryCount > 0 
                            ? Math.min(500 * Math.pow(2, retryCount - 1), 2000) // Exponential backoff: 500ms, 1000ms, 2000ms
                            : 300; // 300ms delay between different tags (increased from 100ms)
                        await new Promise(resolve => setTimeout(resolve, delay));
                    }
                    
                    await this.updateLineageOnBackend(tagName, newLineage);
                    verboseLog(`✅ Processed lineage update ${i + 1}/${updatesToProcess.length}: ${tagName}${retryCount > 0 ? ` (retry ${retryCount})` : ''}`);
                    lastError = null;
                    break; // Success, exit retry loop
                } catch (error) {
                    lastError = error;
                    const errorMsg = error.message || String(error);
                    
                    // CRITICAL FIX: On timeout, don't retry - UI is already updated
                    // Just log and continue - the backend may still process it
                    if (errorMsg.includes('timeout') || errorMsg.includes('aborted')) {
                        console.warn(`⚠️ Lineage update timeout for ${tagName} - UI already updated, skipping retry`);
                        break; // Exit retry loop - UI is correct, backend may catch up later
                    }
                    
                    // Only retry on database lock errors (not timeouts)
                    if (retryCount < maxRetries && (
                        errorMsg.includes('database is locked') || 
                        errorMsg.includes('LockTimeoutError') ||
                        errorMsg.includes('Service Unavailable') ||
                        errorMsg.includes('connection timeout')
                    )) {
                        retryCount++;
                        console.warn(`⚠️ Database locked for ${tagName}, retrying in ${Math.min(500 * Math.pow(2, retryCount - 1), 2000)}ms (attempt ${retryCount}/${maxRetries})...`);
                        continue; // Retry
                    } else {
                        // Not a retryable error or max retries reached
                        console.error(`❌ Failed to update lineage for ${tagName}:`, error);
                        break; // Exit retry loop
                    }
                }
            }
            
            // If we exhausted retries, log the final error
            if (lastError && retryCount > maxRetries) {
                console.error(`❌ Failed to update lineage for ${tagName} after ${maxRetries} retries:`, lastError);
            }
        }
        
        this._lineageUpdateProcessing = false;
        verboseLog(`✅ Completed processing ${updatesToProcess.length} lineage update(s)`);
    },

    async updateLineageOnBackend(tagName, newLineage) {
        const requestStartTime = Date.now();
        let timeoutId = null;
        let abortController = null;
        // CRITICAL FIX: Reduced to 10s - UI updates immediately, backend can catch up
        const LINEAGE_UPDATE_TIMEOUT_MS = 10000;
        
        // CRITICAL FIX: Update UI IMMEDIATELY before backend call
        // This ensures the user sees the change right away, even if backend is slow
        this.updateTagLineageInUI(tagName, newLineage);
        const originalTag = this.state.originalTags.find(t => t['Product Name*'] === tagName);
        if (originalTag) {
            originalTag.lineage = newLineage;
            originalTag.Lineage = newLineage;
            originalTag.currentLineage = newLineage;
            originalTag.canonical_lineage = newLineage;
        }
        const currentTag = this.state.tags.find(t => t['Product Name*'] === tagName);
        if (currentTag) {
            currentTag.lineage = newLineage;
            currentTag.Lineage = newLineage;
            currentTag.currentLineage = newLineage;
            currentTag.canonical_lineage = newLineage;
        }
        
        try {
            verboseLog(`🔄 Updating lineage for ${tagName} to ${newLineage}...`);
            
            const payload = {
                tag_name: tagName,
                "Product Name*": tagName,
                lineage: newLineage
            };
            
            // CRITICAL FIX: Shorter timeout - if backend is slow, we'll retry in background
            abortController = new AbortController();
            timeoutId = setTimeout(() => {
                abortController.abort();
                const elapsed = Date.now() - requestStartTime;
                console.warn(`⚠️ LINEAGE UPDATE TIMEOUT after ${(elapsed/1000).toFixed(1)}s - UI already updated, will retry in background`);
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

            // CRITICAL FIX: Clear frontend cache after successful lineage update
            // This ensures that on page reload, fresh lineage data is fetched from database
            if (responseData.db_updated > 0 || responseData.excel_updated > 0) {
                this.clearAvailableTagsCache();
                // Store timestamp of lineage update to skip cache on next page load
                sessionStorage.setItem('lastLineageUpdateTime', Date.now().toString());
                console.log('🗑️ Cleared frontend cache after lineage update to ensure fresh data on reload');
            }

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
            
            // CRITICAL FIX: Skip debounced backend refresh to prevent clearing selected tags
            // We already update the UI directly with updateTagLineageInUI, so no refresh needed
            // The state is already updated above, and the UI is updated immediately
            // A full refresh would risk clearing selected tags, so we skip it entirely
            verboseLog('✅ Lineage updated in state and UI - skipping backend refresh to preserve selected tags');
            
            // OLD CODE REMOVED: The debounced refresh was causing selected tags to be cleared
            // We now rely on direct state/UI updates which are faster and safer
            
            // Track which tags were recently updated
            if (!this._recentlyUpdatedLineages) {
                this._recentlyUpdatedLineages = [];
            }
            if (!this._recentlyUpdatedLineages.includes(tagName)) {
                this._recentlyUpdatedLineages.push(tagName);
            }
            
            // CRITICAL FIX: Mark this lineage update as completed for reload protection
            if (this._lineageUpdatePending) {
                this._lineageUpdatePending.delete(tagName);
            }
            
            // CRITICAL FIX: Store completion timestamp to ensure database has time to flush
            if (!this._lineageUpdateCompletions) {
                this._lineageUpdateCompletions = new Map();
            }
            this._lineageUpdateCompletions.set(tagName, Date.now());

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

            // CRITICAL FIX: Update all instances of this tag to show new lineage
            // This ensures lineage changes are visible immediately and persist through re-renders
            setTimeout(() => {
                // Update the tag lookup map with new lineage
                if (this._tagLookupMap) {
                    const tagInMap = this._tagLookupMap.get(tagName);
                    if (tagInMap) {
                        tagInMap.lineage = verifiedLineage;
                        tagInMap.Lineage = verifiedLineage;
                        tagInMap.currentLineage = verifiedLineage;
                        tagInMap.canonical_lineage = verifiedLineage;
                    }
                }
                
                // CRITICAL FIX: Update all tag elements in the DOM to show new lineage
                // Find all instances using multiple selectors to catch all cases
                const selectors = [
                    `[data-tag-name="${CSS.escape(tagName)}"]`,
                    `.tag-checkbox[value="${CSS.escape(tagName)}"]`,
                    `.tag-row[data-product-name="${CSS.escape(tagName)}"]`
                ];
                
                selectors.forEach(selector => {
                    try {
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(element => {
                            const tagItem = element.closest('.tag-item') || element.closest('.tag-row') || element;
                            if (tagItem) {
                                // Update data-lineage attribute
                                tagItem.dataset.lineage = verifiedLineage.toUpperCase();
                                
                                // Update lineage dropdown if it exists
                                const lineageSelect = tagItem.querySelector('.lineage-dropdown');
                                if (lineageSelect) {
                                    if (lineageSelect.value !== verifiedLineage) {
                                        lineageSelect._isProgrammaticUpdate = true;
                                        lineageSelect.value = verifiedLineage;
                                        lineageSelect._isProgrammaticUpdate = false;
                                    }
                                }
                                
                                // Update tag color
                                const tag = this.state.tags.find(t => (t['Product Name*'] || t.ProductName) === tagName) ||
                                           this.state.originalTags.find(t => (t['Product Name*'] || t.ProductName) === tagName);
                                if (tag) {
                                    this.forceTagColorUpdate(tag, verifiedLineage);
                                }
                            }
                        });
                    } catch (e) {
                        // Ignore selector errors
                    }
                });
                
                // CRITICAL FIX: Force refresh available tags display to ensure lineage is visible
                // This re-renders tags with updated lineage from state
                if (typeof this.efficientlyUpdateAvailableTagsDisplay === 'function') {
                    this.efficientlyUpdateAvailableTagsDisplay();
                    verboseLog('✅ Refreshed available tags display to show updated lineage');
                } else if (typeof this._updateAvailableTags === 'function' && this.state.tags.length > 0) {
                    // Fallback: re-render available tags with current state
                    this._updateAvailableTags(this.state.tags, null);
                    verboseLog('✅ Re-rendered available tags to show updated lineage');
                }
            }, 100);
            
            verboseLog('✅ Lineage updated successfully - refreshed display to show changes');

        } catch (error) {
            // Clear timeout if it's still set
            if (timeoutId) {
                clearTimeout(timeoutId);
                timeoutId = null;
            }
            
            const requestDuration = Date.now() - requestStartTime;
            const isTimeout = error.name === 'AbortError' || error.message.includes('timeout') || requestDuration > 10000;
            
            if (isTimeout) {
                // CRITICAL FIX: Don't throw error on timeout - UI is already updated
                // The backend may still process it, and we'll verify on next refresh
                console.warn(`⚠️ LINEAGE UPDATE TIMEOUT after ${requestDuration}ms - UI already updated, backend may still be processing`);
                // Don't show error to user - UI is already correct
                // The update will be verified on next page load or tag refresh
                return; // Exit gracefully - don't throw
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
                        img.style.cssText = 'height:28px;width:28px;object-fit:contain;margin-left:6px;vertical-align:middle';
                        imageContainer.appendChild(img);
                    } else if (newDohStatus === 'DOH') {
                        const img = document.createElement('img');
                        img.src = '/static/img/DOH.png';
                        img.alt = 'DOH Compliant';
                        img.title = 'DOH Compliant Product';
                        img.style.cssText = 'height:36px;width:36px;object-fit:contain;margin-left:6px;vertical-align:middle';
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
                        img.style.cssText = 'height:28px;width:28px;object-fit:contain;margin-left:6px;vertical-align:middle';
                        imageContainer.appendChild(img);
                    } else if (newDohStatus === 'DOH') {
                        const img = document.createElement('img');
                        img.src = '/static/img/DOH.png';
                        img.alt = 'DOH Compliant';
                        img.title = 'DOH Compliant Product';
                        img.style.cssText = 'height:36px;width:36px;object-fit:contain;margin-left:6px;vertical-align:middle';
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

        // CRITICAL FIX: Update tag data in state first to prevent change handler from reverting
        const updateTagInState = (tagElement) => {
            if (!tagElement) return;
            const tagDataName = tagElement.getAttribute('data-tag-name');
            if (!tagDataName) return;
            
            // Find and update the tag in state
            const stateTag = this.state.tags.find(t => (t['Product Name*'] || t.ProductName) === tagDataName);
            const originalTag = this.state.originalTags.find(t => (t['Product Name*'] || t.ProductName) === tagDataName);
            
            if (stateTag) {
                stateTag.lineage = newLineage;
                stateTag.Lineage = newLineage;
                stateTag.currentLineage = newLineage;
                stateTag.canonical_lineage = newLineage;
            }
            if (originalTag) {
                originalTag.lineage = newLineage;
                originalTag.Lineage = newLineage;
                originalTag.currentLineage = newLineage;
                originalTag.canonical_lineage = newLineage;
            }
            
            // Update data attributes
            tagElement.dataset.lineage = newLineage.toUpperCase();
        };

        // Update lineage dropdown in available tags
        const availableTagElement = findTagElement('#availableTags', tagName);
        if (availableTagElement) {
            // CRITICAL FIX: Update state first to prevent change handler from reverting
            updateTagInState(availableTagElement);
            
            const lineageSelect = availableTagElement.querySelector('.lineage-dropdown');
            if (lineageSelect) {
                const oldValue = lineageSelect.value;
                if (oldValue !== newLineage) {
                    // CRITICAL FIX: Mark as programmatic update to prevent change handler from processing
                    lineageSelect._isProgrammaticUpdate = true;
                    lineageSelect.value = newLineage;
                    
                    // Update tag color
                    const tag = this.state.tags.find(t => (t['Product Name*'] || t.ProductName) === tagName);
                    if (tag) {
                        this.forceTagColorUpdate(tag, newLineage);
                    }
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
            // CRITICAL FIX: Update state first to prevent change handler from reverting
            updateTagInState(selectedTagElement);
            
            const lineageSelect = selectedTagElement.querySelector('.lineage-dropdown');
            if (lineageSelect) {
                const oldValue = lineageSelect.value;
                if (oldValue !== newLineage) {
                    // CRITICAL FIX: Mark as programmatic update to prevent change handler from processing
                    lineageSelect._isProgrammaticUpdate = true;
                    lineageSelect.value = newLineage;
                    
                    // Update tag color
                    const tag = this.state.tags.find(t => (t['Product Name*'] || t.ProductName) === tagName);
                    if (tag) {
                        this.forceTagColorUpdate(tag, newLineage);
                    }
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

        // CRITICAL FIX: If there's an active lineage filter and the updated tag's new lineage doesn't match,
        // clear the lineage filter so the tag remains visible
        const lineageFilterElement = document.getElementById('lineageFilter');
        if (lineageFilterElement) {
            const activeLineageFilter = lineageFilterElement.value || '';
            if (activeLineageFilter.trim() !== '' && activeLineageFilter.toLowerCase() !== 'all') {
                const normalizedNewLineage = (typeof window.normalizeLineageValue !== 'undefined')
                    ? window.normalizeLineageValue(newLineage)
                    : newLineage.toString().trim().toUpperCase();
                const normalizedFilter = (typeof window.normalizeLineageValue !== 'undefined')
                    ? window.normalizeLineageValue(activeLineageFilter)
                    : activeLineageFilter.toString().trim().toUpperCase();
                
                // If the new lineage doesn't match the active filter, clear the filter
                if (normalizedNewLineage !== normalizedFilter) {
                    verboseLog(`🔄 Clearing lineage filter (${normalizedFilter}) because updated tag lineage (${normalizedNewLineage}) doesn't match`);
                    lineageFilterElement.value = 'All';
                    // Trigger filter update to refresh display
                    if (typeof this.applyFilters === 'function') {
                        this.applyFilters(true); // Use immediate update
                    }
                }
            }
        }
    },

    // NEW: Update lineage for all items with the same vendor + strain immediately in UI/state
    // CRITICAL FIX: For nonclassic types, only update the specific product, don't propagate
    updateSimilarLineages(tagName, newLineage) {
        // Helper to normalize values
        const norm = v => (v || '').toString().trim().toLowerCase();

        // Robust helper to pull vendor from a tag record
        const getVendor = (t) => {
            if (!t) return '';
            const vendorKeys = [
                'Vendor/Supplier*',
                'Vendor/Supplier',
                'Vendor*',
                'Vendor',
                'Supplier*',
                'Supplier',
                'vendor'
            ];
            for (const key of vendorKeys) {
                if (t[key]) return t[key];
            }
            // Fallback: treat Product Brand as pseudo‑vendor when no explicit vendor is present
            return t['Product Brand'] || t.Brand || t.brand || '';
        };

        // Find source tag info
        const source = this.state.tags.find(t => (t['Product Name*'] || t.ProductName) === tagName) ||
                       this.state.originalTags.find(t => (t['Product Name*'] || t.ProductName) === tagName);
        if (!source) {
            console.warn('updateSimilarLineages: Source tag not found for', tagName);
            return;
        }
        
        // CRITICAL FIX: Check if this is a nonclassic product type
        // For nonclassic types, don't propagate lineage changes to other products
        const productType = (source['Product Type*'] || source.ProductType || source.Type || '').toString().trim().toLowerCase();
        const classicTypes = ['flower', 'pre-roll', 'concentrate', 'infused pre-roll', 'solventless concentrate', 'vape cartridge', 'rso/co2 tankers'];
        const isNonclassic = !classicTypes.includes(productType);
        
        if (isNonclassic) {
            verboseLog(`🔄 Nonclassic product '${tagName}' (type: ${productType}) - skipping lineage propagation to other products`);
            return; // Don't propagate for nonclassic types
        }
        
        const srcVendor = norm(getVendor(source));
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
            console.warn('updateSimilarLineages: No vendor/brand context found for', tagName);
            return;
        }

        const isSimilar = (t) => {
            const tagProductName = t['Product Name*'] || t.ProductName || 'UNKNOWN';
            const v = norm(getVendor(t));
            
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
        const affectedNames = new Set();
        this.state.tags.forEach(t => {
            if (isSimilar(t)) {
                t.lineage = newLineage;
                t.Lineage = newLineage;
                tagsUpdated++;
                const name = t['Product Name*'] || t.ProductName;
                if (name && name !== tagName) {
                    affectedNames.add(name);
                }
            }
        });
        this.state.originalTags.forEach(t => {
            if (isSimilar(t)) {
                t.lineage = newLineage;
                t.Lineage = newLineage;
                const name = t['Product Name*'] || t.ProductName;
                if (name && name !== tagName) {
                    affectedNames.add(name);
                }
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
            // PERFORMANCE: Use Map lookup for O(1) instead of array.find() - O(n)
            const tag = this._tagLookupMap?.get(name);
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

        // CRITICAL FIX: If there's an active lineage filter and the updated tag's new lineage doesn't match,
        // clear the lineage filter so the tag remains visible
        const lineageFilterElement = document.getElementById('lineageFilter');
        if (lineageFilterElement) {
            const activeLineageFilter = lineageFilterElement.value || '';
            if (activeLineageFilter.trim() !== '' && activeLineageFilter.toLowerCase() !== 'all') {
                const normalizedNewLineage = (typeof window.normalizeLineageValue !== 'undefined')
                    ? window.normalizeLineageValue(newLineage)
                    : newLineage.toString().trim().toUpperCase();
                const normalizedFilter = (typeof window.normalizeLineageValue !== 'undefined')
                    ? window.normalizeLineageValue(activeLineageFilter)
                    : activeLineageFilter.toString().trim().toUpperCase();
                
                // If the new lineage doesn't match the active filter, clear the filter
                if (normalizedNewLineage !== normalizedFilter) {
                    verboseLog(`🔄 Clearing lineage filter (${normalizedFilter}) because updated tag lineage (${normalizedNewLineage}) doesn't match`);
                    lineageFilterElement.value = 'All';
                    // Trigger filter update to refresh display
                    if (typeof this.applyFilters === 'function') {
                        this.applyFilters(true); // Use immediate update
                    }
                }
            }
        }

        // Propagate lineage change to backend for all affected similar items
        if (typeof this.updateLineageOnBackendDebounced === 'function') {
            affectedNames.forEach(name => {
                this.updateLineageOnBackendDebounced(name, newLineage);
            });
        }
    },

    updateSelectedTags(tags) {
        // PERFORMANCE: Skip batching - update immediately for responsive UI
        this._performUpdateSelectedTags(tags);
    },
    
    _performUpdateSelectedTags(tags) {
        // CRITICAL FIX: Removed console.time/timeEnd to prevent "Timer does not exist" errors
        // These were only for debugging and causing issues when called from lineage updates

        // CRITICAL FIX: Block any clearing of tags if generation is in progress or just completed
        const now = Date.now();
        const isGenerating = this.isGenerating === true;
        const recentlyGenerated = this._lastGenerationTime && (now - this._lastGenerationTime) < 30000; // 30 seconds
        
        if ((isGenerating || recentlyGenerated) && (!tags || tags.length === 0) && this.state.persistentSelectedTags.length > 0) {
            verboseLog('🚫 BLOCKED: Prevented clearing selected tags during/after generation');
            // Force re-render with current selections instead
            const currentTags = this.state.persistentSelectedTags
                .map(tagName => this._tagLookupMap?.get(tagName) ||
                               this.state.tags.find(t => t['Product Name*'] === tagName) ||
                               this.state.originalTags.find(t => t['Product Name*'] === tagName) ||
                               { 'Product Name*': tagName, displayName: tagName, lineage: 'MIXED' })
                .filter(Boolean);
            if (currentTags.length > 0) {
                tags = currentTags;
                this._forceSelectedTagsUpdate = true;
            } else {
                tags = this.state.persistentSelectedTags.map(name => ({
                    'Product Name*': name,
                    displayName: name,
                    lineage: 'MIXED'
                }));
                this._forceSelectedTagsUpdate = true;
            }
        }

        if (!tags || !Array.isArray(tags)) {
            console.warn('updateSelectedTags called with invalid tags:', tags);
            tags = [];
        }
        
        // CRITICAL FIX: If called with empty array but we have persistentSelectedTags, preserve them
        // This prevents selections from being cleared when updateSelectedTags([]) is called
        if (tags.length === 0 && this.state.persistentSelectedTags.length > 0) {
            // CRITICAL FIX: If we just generated tags, NEVER clear them (extended protection)
            const now = Date.now();
            const recentlyGenerated = this._lastGenerationTime && (now - this._lastGenerationTime) < 30000; // 30 seconds
            
            if (recentlyGenerated) {
                verboseLog('🚫 BLOCKED: Attempted to clear selected tags right after generation - preserving selections');
                // Force re-render with current selections
                const currentTags = this.state.persistentSelectedTags
                    .map(tagName => this._tagLookupMap?.get(tagName) ||
                                   this.state.tags.find(t => t['Product Name*'] === tagName) ||
                                   this.state.originalTags.find(t => t['Product Name*'] === tagName) ||
                                   { 'Product Name*': tagName, displayName: tagName, lineage: 'MIXED' })
                    .filter(Boolean);
                if (currentTags.length > 0) {
                    tags = currentTags;
                    this._forceSelectedTagsUpdate = true;
                } else {
                    // Fallback to placeholders
                    tags = this.state.persistentSelectedTags.map(name => ({
                        'Product Name*': name,
                        displayName: name,
                        lineage: 'MIXED'
                    }));
                    this._forceSelectedTagsUpdate = true;
                }
            } else {
                verboseLog('updateSelectedTags called with empty array, but preserving persistentSelectedTags:', this.state.persistentSelectedTags);
                // PERFORMANCE: Use existing _tagLookupMap instead of creating new Maps
                // This avoids O(n) Map creation and uses already-built lookup Map
                tags = this.state.persistentSelectedTags
                    .map(tagName => this._tagLookupMap?.get(tagName))
                    .filter(Boolean);
                
                if (tags.length === 0) {
                    verboseLog('No tag objects found for persistentSelectedTags, but keeping selections in state - rendering lightweight placeholders');
                    // Render lightweight placeholders so the user still sees and can reselect their tags
                    tags = this.state.persistentSelectedTags.map(name => ({
                        'Product Name*': name,
                        displayName: name,
                        lineage: 'MIXED'
                    }));
                    // Force an update so the placeholders appear
                    this._forceSelectedTagsUpdate = true;
                }
            }
        }
        
        // Prevent updates during tag move operations to avoid race conditions
        if (this.isMovingTags) {
            verboseLog('Ignoring updateSelectedTags during tag move operation');
            return;
        }
        
        // Performance optimization: Check if the update is actually needed
        const container = document.getElementById('selectedTags');
        if (!container) {
            console.error('Selected tags container not found');
            return;
        }
        
        // CRITICAL: Don't skip update - we need to update dropdowns to show database lineage
        // Even if tag count/names match, lineage values might have changed from database alignment
        // Always re-render to ensure dropdowns show correct database lineage
        const forceUpdate = this._forceSelectedTagsUpdate || false;
        this._forceSelectedTagsUpdate = false; // Reset flag
        
        // PERFORMANCE: Quick comparison using cached state instead of slow DOM queries
        // SAFETY: Only skip if the DOM already has matching tag items. If the DOM was cleared
        // elsewhere (e.g., splash or filter refresh), we must re-render even when names match
        if (!forceUpdate && this._lastRenderedSelectedTags) {
            const lastNames = this._lastRenderedSelectedTags;
            const newNames = tags.map(tag => tag['Product Name*']).filter(Boolean);
            const renderedItems = container.querySelectorAll('.tag-item').length;
            const hasRenderedItems = renderedItems > 0;
            
            if (hasRenderedItems &&
                lastNames.length === newNames.length &&
                lastNames.every((name, idx) => name === newNames[idx])) {
                verboseLog('updateSelectedTags: No changes detected, skipping update (DOM already rendered)');
                return;
            }
        }
        
        // Cache for next comparison
        this._lastRenderedSelectedTags = tags.map(tag => tag['Product Name*']).filter(Boolean);
        
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

        // CRITICAL FIX: Use persistentSelectedTags as the source of truth, not the tags array passed in
        // This prevents selection glitches where tags array might not match the actual selected state
        // Build the tags array from persistentSelectedTags to ensure consistency
        const persistentTagNames = [...this.state.persistentSelectedTags];
        
        // Handle new tags being passed in (e.g., from JSON matching) - add them to persistentSelectedTags
        if (tags.length > 0) {
            verboseLog('Processing tags for updateSelectedTags:', tags.length);
            tags.forEach(tag => {
                if (tag && tag['Product Name*']) {
                    const tagName = tag['Product Name*'];
                    if (!this.state.persistentSelectedTags.includes(tagName)) {
                        this.state.persistentSelectedTags.push(tagName);
                        if (!persistentTagNames.includes(tagName)) {
                            persistentTagNames.push(tagName);
                        }
                    }
                }
            });
        }
        
        // CRITICAL FIX: Build fullTags from persistentSelectedTags to ensure checkbox state matches
        // Find tag objects for all persistentSelectedTags, preserving order
        const tagsMap = new Map(tags.map(t => [t['Product Name*'], t]));
        const originalTagsMap = new Map(this.state.originalTags.map(t => [t['Product Name*'], t]));
        const stateTagsMap = new Map(this.state.tags.map(t => [t['Product Name*'], t]));
        
        // Build fullTags from persistentSelectedTags in order, using tags passed in or finding from state
        let fullTags = persistentTagNames.map(tagName => {
            // Try to find tag in the passed tags array first, then in state
            return tagsMap.get(tagName) || 
                   stateTagsMap.get(tagName) || 
                   originalTagsMap.get(tagName) ||
                   null;
        }).filter(Boolean); // Remove any null entries
        
        // If we have fewer tags than persistentSelectedTags, log a warning
        if (fullTags.length < this.state.persistentSelectedTags.length) {
            const missing = this.state.persistentSelectedTags.filter(name => 
                !tagsMap.has(name) && !stateTagsMap.has(name) && !originalTagsMap.has(name)
            );
            if (missing.length > 0) {
                console.warn(`⚠️ Some selected tags not found in available tags:`, missing);
            }
        }
        
        // Update selectedTags set to match persistentSelectedTags
        this.state.selectedTags = new Set(this.state.persistentSelectedTags);
        
        // CRITICAL FIX: If no tag objects found but we have persistentSelectedTags, create minimal tag objects
        // This ensures selected tags are displayed even if they're not yet in the tag maps
        if (fullTags.length === 0 && this.state.persistentSelectedTags.length > 0) {
            verboseLog(`No tag objects found for ${this.state.persistentSelectedTags.length} selected tags, creating minimal tag objects`);
            // Create minimal tag objects for selected tags that aren't found
            fullTags = this.state.persistentSelectedTags.map(tagName => {
                // Try one more time to find the tag with case-insensitive search
                let foundTag = null;
                for (const tag of [...this.state.tags, ...this.state.originalTags]) {
                    if (tag && tag['Product Name*'] && tag['Product Name*'].toLowerCase() === tagName.toLowerCase()) {
                        foundTag = tag;
                        break;
                    }
                }
                
                if (!foundTag) {
                    // Create minimal tag object so it can be displayed
                    verboseLog(`Creating minimal tag object for "${tagName}"`);
                    return {
                        'Product Name*': tagName,
                        'Product Brand': 'Unknown',
                        'Vendor': 'Unknown',
                        'Product Type*': 'Unknown',
                        'Lineage': 'MIXED',
                        'Source': 'Frontend Selection'
                    };
                }
                return foundTag;
            }).filter(Boolean);
            
            if (fullTags.length === 0) {
                verboseLog('Still no tags after creating minimal objects, keeping selections in state');
                // Don't return - keep selections in state even if we can't display them yet
                this.updateTagCount('selected', this.state.persistentSelectedTags.length);
                return;
            }
        } else if (fullTags.length === 0) {
            // Only clear if we truly have no selections
            verboseLog('No tags to display in selected tags');
            this.updateTagCount('selected', 0);
            return;
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
                                // CRITICAL FIX: Use getSelectedTagObjects() which checks all sources
                                const selectedTagObjects = this.getSelectedTagObjects();
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
                            // CRITICAL FIX: Use getSelectedTagObjects() which checks all sources
                            const selectedTagObjects = this.getSelectedTagObjects();
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
                                // CRITICAL FIX: Use getSelectedTagObjects() which checks both state.tags AND originalTags
                                // This prevents tags from disappearing when filters are active
                                const selectedTagObjects = this.getSelectedTagObjects();
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

        // CRITICAL FIX: After rebuilding selected tags, ensure all checkboxes are properly checked
        // This fixes the issue where drag-and-drop causes tags to deselect themselves
        setTimeout(() => {
            const allCheckboxes = container.querySelectorAll('.tag-checkbox');
            allCheckboxes.forEach(checkbox => {
                const tagName = checkbox.value;
                const shouldBeChecked = this.state.persistentSelectedTags.includes(tagName);
                if (shouldBeChecked && !checkbox.checked) {
                    console.log(`🔧 Fixing unchecked checkbox for "${tagName}" after drag operation`);
                    checkbox.checked = true;
                } else if (!shouldBeChecked && checkbox.checked) {
                    console.log(`🔧 Fixing incorrectly checked checkbox for "${tagName}" after drag operation`);
                    checkbox.checked = false;
                }
            });
        }, 50); // Small delay to ensure DOM is fully rendered

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
        if (!FAST_RELOAD_MODE && window.dragAndDropManager) {
            setTimeout(() => {
                verboseLog('Reinitializing drag and drop after updateSelectedTags');
                window.dragAndDropManager.reinitializeTagDragAndDrop();
            }, 100);
        }

        // Safety net: if the selected list ended up empty but we still have persistent selections,
        // immediately rebuild from persistentSelectedTags (prevents disappearing selections).
        if (!this._isRestoringSelectedTags) {
            this._isRestoringSelectedTags = true;
            setTimeout(() => {
                try {
                    const selectedContainer = document.getElementById('selectedTags');
                    const renderedRows = selectedContainer ? selectedContainer.querySelectorAll('.tag-row').length : 0;
                    if (renderedRows === 0 && this.state.persistentSelectedTags && this.state.persistentSelectedTags.length > 0) {
                        verboseLog('⚠️ Selected list empty but persistent selections exist, restoring from persistentSelectedTags');
                        const fallbackTags = this.state.persistentSelectedTags.map(name =>
                            this._tagLookupMap?.get(name) ||
                            this.state.tags.find(t => t['Product Name*'] === name) ||
                            this.state.originalTags.find(t => t['Product Name*'] === name) || 
                            { 'Product Name*': name, displayName: name, lineage: 'MIXED' }
                        ).filter(Boolean);
                        this.updateSelectedTags(fallbackTags);
                    }
                } finally {
                    this._isRestoringSelectedTags = false;
                }
            }, 0);
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

    // Ultra-fast, non-blocking prefetch using the lite tags endpoint.
    // This is used to get *something* on screen immediately on cold loads,
    // while the full /api/available-tags endpoint continues to load in the background.
    async _prefetchLiteAvailableTags(savedScrollPosition) {
        try {
            // If we already rendered lite or full tags, don't overwrite them
            if (this._liteTagsRendered || (Array.isArray(this.state.tags) && this.state.tags.length > 0)) {
                return;
            }

            verboseLog('Prefetching lite available tags for instant first render...');
            const controller = new AbortController();
            // Keep this timeout short – we only want it if it is truly fast
            const timeoutId = setTimeout(() => controller.abort(), 3000);

            const response = await fetch(`/api/available-tags-lite?t=${Date.now()}`, {
                signal: controller.signal
            });
            clearTimeout(timeoutId);

            if (!response.ok) {
                // Check for store mismatch error
                if (response.status === 400) {
                    try {
                        const errorData = await response.json();
                        if (errorData.source === 'store-mismatch-error') {
                            console.error('❌ STORE MISMATCH:', errorData.error);
                            alert(`⚠️ STORE MISMATCH DETECTED\n\n${errorData.error}\n\nThe wrong file was loaded. Please upload the correct Excel file for ${errorData.current_store}.`);
                            return;
                        }
                    } catch (e) {
                        // Not JSON or parsing failed, continue
                    }
                }
                verboseLog('Lite tags prefetch skipped – non-OK response:', response.status);
                return;
            }

            const responseText = await response.text();
            if (!responseText) {
                verboseLog('Lite tags prefetch returned empty body');
                return;
            }

            let liteData;
            try {
                liteData = JSON.parse(responseText);
            } catch (parseError) {
                console.warn('Failed to parse /api/available-tags-lite prefetch response:', {
                    parseError,
                    snippet: responseText.slice(0, 500)
                });
                return;
            }

            if (!liteData || !Array.isArray(liteData.tags) || liteData.tags.length === 0) {
                verboseLog('Lite tags prefetch returned no tags – skipping UI update');
                return;
            }

            // Normalize lineage fields to keep behavior consistent with full endpoint
            const liteTags = liteData.tags.map(tag => this._normalizeLineageFields ? this._normalizeLineageFields(tag) : tag);

            // If full tags arrived while we were fetching lite tags, don't overwrite them
            if (Array.isArray(this.state.tags) && this.state.tags.length > 0) {
                verboseLog('Skipping lite prefetch render – full tags already loaded');
                return;
            }

            this._liteTagsRendered = true;
            this.state.tags = [...liteTags];
            this.state.originalTags = [...liteTags];
            this.state.hydratedFromCache = false;
            this.saveAvailableTagsToCache(liteTags);

            this._updateAvailableTags(liteTags);
            if (savedScrollPosition) {
                this._restoreAvailableScrollPosition(savedScrollPosition);
            }

            this.updateTagCount('available', liteTags.length);
            this.updateTagCount('selected', this.state.persistentSelectedTags.length);

            // Once something is on screen, remove the splash so it feels instant
            if (this.hideActionSplash) {
                this.hideActionSplash();
            }

            verboseLog(`✅ Lite tags prefetch rendered ${liteTags.length} tags for instant load`);
        } catch (e) {
            if (e && e.name === 'AbortError') {
                verboseLog('Lite tags prefetch aborted (timeout) – continuing with full available-tags flow');
            } else {
                verboseLog('Lite tags prefetch failed (non-critical):', e);
            }
        }
    },

    async fetchAndUpdateAvailableTags() {
        // CRITICAL FIX: Reset stuck flag if it's been set for too long
        if (this._fetchingAvailableTags) {
            const fetchStartTime = this._fetchingAvailableTagsStartTime || Date.now();
            const stuckDuration = Date.now() - fetchStartTime;
            if (stuckDuration > 30000) {
                console.warn('⚠️ _fetchingAvailableTags stuck for 30+ seconds, resetting flag');
                this._fetchingAvailableTags = false;
            } else {
                console.log('⏸️ Tag fetch already in progress, waiting for completion...');
                // Wait up to 2 seconds for in-progress fetch to complete
                let waitCount = 0;
                while (this._fetchingAvailableTags && waitCount < 20) {
                    await new Promise(resolve => setTimeout(resolve, 100));
                    waitCount++;
                }
                // If still in progress after waiting, skip to prevent hang
                if (this._fetchingAvailableTags) {
                    console.log('⏸️ Tag fetch still in progress after wait, skipping duplicate call');
                    // CRITICAL FIX: Force hide splash if we're stuck waiting
                    if (AppLoadingSplash && AppLoadingSplash.isVisible) {
                        console.log('⚡ Force hiding splash - tag fetch stuck');
                        AppLoadingSplash.stopAutoAdvance();
                        AppLoadingSplash.complete();
                    }
                    return false;
                }
            }
        }
        
        // Set flag to prevent concurrent calls
        this._fetchingAvailableTags = true;
        this._fetchingAvailableTagsStartTime = Date.now();
        // Track background-processing retries (reset on success)
        this._backgroundProcessingRetries = this._backgroundProcessingRetries || 0;
        
        // CRITICAL FIX: Add timeout to force hide splash if fetch takes too long
        const splashTimeout = setTimeout(() => {
            if (AppLoadingSplash && AppLoadingSplash.isVisible) {
                console.log('⚡ Force hiding splash - tag fetch timeout (30s)');
                AppLoadingSplash.stopAutoAdvance();
                AppLoadingSplash.complete();
            }
        }, 30000); // 30 second timeout
        
        // CRITICAL FIX: Use try-finally to ensure flag is always reset
        try {
            console.log('=== fetchAndUpdateAvailableTags START ===');
            // Ensure flag is initialized
            if (typeof this._liteTagsRendered === 'undefined') {
                this._liteTagsRendered = false;
            }

            // CRITICAL: Declare safetyTimeout at the very start of function so it's always available in catch block
            // This prevents "safetyTimeout is not defined" errors if an exception occurs early
            let safetyTimeout = null;
            
            const hydratedFromCache = this.hydrateAvailableTagsFromCache();
            if (hydratedFromCache) {
                console.log('✅ Tags rendered instantly from cache');
                // PERFORMANCE FIX: Background refresh uses fast_load now (set in _refreshLineageFromDatabase)
                console.log('⚡ PERFORMANCE: Cache loaded, background refresh will use fast mode');
                return true;
            }
            
            // Only show loading if we don't have cached tags
            console.log('⏳ No cache available - preparing loader');
            // Only replace the list with a loader on true cold start; during mid-use refreshes,
            // keep the existing inventory visible so it does not disappear while new tags load.
            const availableTagsContainer = document.getElementById('availableTags');
            const hasExistingTags = Array.isArray(this.state.tags) && this.state.tags.length > 0;
            
            // CRITICAL: Add safety timeout to hide spinner after longer delay
            // This prevents indefinite hanging even if error handling fails
            if (!hasExistingTags) {
                safetyTimeout = setTimeout(() => {
                    console.warn('⚠️ Safety timeout: Hiding loading spinner');
                    // Just hide the splash, don't show error message
                    if (this.hideActionSplash) {
                        this.hideActionSplash();
                    }
                    // Don't show error message - let the app continue working
                }, 60000); // 60 seconds - very generous timeout
            }
            
            if (!hasExistingTags) {
                this.showActionSplash('Loading tags...');
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
            } else {
                // For warm refreshes, just show the splash without clearing the current list.
                this.showActionSplash('Refreshing tags...');
            }
            
            // Preserve current scroll/anchor so refreshes don't jump the list
            const savedScroll = this._saveAvailableScrollPosition();

            // Fire off a non-blocking lite prefetch to get instant tags while the
            // full /api/available-tags endpoint is still loading.
            // This should never throw or block the main flow.
            this._prefetchLiteAvailableTags(savedScroll).catch(err => {
                verboseLog('Lite prefetch error (non-critical):', err);
            });
            
            // Rate limiting: prevent rapid successive calls
            // Increased to 1000ms to prevent restarts from multiple rapid calls
            const now = Date.now();
            if (this._lastFetchTime && (now - this._lastFetchTime) < 1000) {
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
            
            // PERFORMANCE FIX: Always use fast_load=1 for instant tag loading
            // This skips expensive lineage alignment on cached tags for faster response
            // Lineage will still be aligned when needed, but cached tags return instantly
            const fastLoadParam = '&fast_load=1';
            
            // Add retry logic for failed requests
            // CRITICAL FIX: Handle 202 (processing) separately with more retries
            let response;
            let responseData;
            const maxRetries = 3; // Allow retries for errors
            const maxProcessingRetries = 30; // Allow 30 retries for 202 (file processing) - enough for 60+ seconds of loading
            let retryCount = 0;
            let processingRetryCount = 0;
            let lastError;
            
            // CRITICAL: Continue retrying as long as EITHER condition is met (not both)
            // This allows 202 retries to continue even after error retries are exhausted
            while (retryCount < maxRetries || processingRetryCount < maxProcessingRetries) {
                try {
                    const controller = new AbortController();
                    // CRITICAL: Set timeout to 180 seconds for PythonAnywhere large file loading
                    // Background thread needs time to load 2000+ rows and cache tags
                    const timeoutId = setTimeout(() => {
                        controller.abort();
                        console.warn('⚠️ Tag loading timeout after 180 seconds - will try cache or show error');
                    }, 180000); // 3 minutes for large files on PythonAnywhere

                    // CRITICAL FIX: Use prefer_db to ensure lineage values come from database
                    // PERFORMANCE: Only force prefer_db after uploads to avoid slow queries on cached loads
                    const forceDbLineage = this._forceDatabaseLineage || false;
                    const useCache = retryCount === 0 && !forceDbLineage; // Don't use cache after upload
                    const cacheParam = useCache ? '' : '&nocache=1';
                    // Only use prefer_db when forcing database lineage (after upload), otherwise let fast_load optimize
                    const preferDbParam = forceDbLineage ? '&prefer_db=1' : '';
                    response = await fetch(`/api/available-tags?t=${timestamp}${cacheParam}${fastLoadParam}${preferDbParam}`, {
                        signal: controller.signal
                    });
                    clearTimeout(timeoutId);

                    verboseLog(`Available tags response status (attempt ${retryCount + 1}/${maxRetries}, processing retries: ${processingRetryCount + 1}/${maxProcessingRetries}):`, response.status);

                    // Handle 202 Accepted (file still processing) - allow more retries for this
                    if (response.status === 202) {
                        processingRetryCount++;
                        if (processingRetryCount >= maxProcessingRetries) {
                            // Too many processing retries - try to use cache or show helpful error
                            verboseLog('⏳ File processing taking too long, trying cache fallback...');
                            const cachedTags = this.hydrateAvailableTagsFromCache();
                            if (cachedTags) {
                                verboseLog('✅ Using cached tags as fallback for slow processing');
                                return true;
                            }
                            throw new Error('File is still processing. Please wait a moment and refresh the page, or try uploading again.');
                        }
                        
                        // Show user-friendly loading message
                        
                        verboseLog(`⏳ File still processing (202), retrying immediately... (${processingRetryCount}/${maxProcessingRetries})`);
                        // PERFORMANCE: No delay - retry immediately for faster response
                        continue; // Retry without incrementing error retry count
                    }

                    if (!response.ok) {
                        // CRITICAL FIX: Handle 503 errors gracefully - try to use cache
                        if (response.status === 503) {
                            verboseLog('⚠️ Server returned 503 (Service Unavailable), attempting to use cached data...');
                            // Try to use cached tags if available
                            const cachedTags = this.hydrateAvailableTagsFromCache();
                            if (cachedTags) {
                                verboseLog('✅ Using cached tags as fallback for 503 error');
                                return true;
                            }
                            // If no cache, throw error but don't retry 503 (server is overloaded)
                            throw new Error(`HTTP 503: Service Unavailable - Server is temporarily overloaded. Please try again in a moment.`);
                        }
                        if (response.status >= 500 && retryCount < maxRetries - 1) {
                            // Server error - retry immediately
                            retryCount++;
                            verboseLog(`Server error ${response.status}, retrying immediately...`);
                            // PERFORMANCE: No delay - retry immediately
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
                        verboseLog(`Retrying immediately...`);
                        // PERFORMANCE: No delay - retry immediately for faster response
                    } else {
                        throw error;
                    }
                }
            }
            
            if (!responseData) {
                // Try cache as final fallback before throwing error
                const cachedTags = this.hydrateAvailableTagsFromCache();
                if (cachedTags) {
                    verboseLog('✅ Using cached tags as final fallback after failed fetch');
                    return true;
                }
                throw lastError || new Error('Failed to fetch tags after retries. Please try refreshing the page or uploading the file again.');
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
                // Try cache before giving up
                const cachedTags = this.hydrateAvailableTagsFromCache();
                if (cachedTags) {
                    verboseLog('✅ Using cached tags as fallback for invalid response format');
                    return true;
                }
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
                // Check if this is an error response with a message
                if (responseData.error || responseData.message) {
                    const errorMsg = responseData.error || responseData.message;
                    console.warn('Backend returned empty tags with message:', errorMsg);

                    // Auto-retry when backend is still loading the file in background
                    const lowerMsg = (errorMsg || '').toLowerCase();
                    const isBackgroundLoading = lowerMsg.includes('loading in background') || lowerMsg.includes('processing') || lowerMsg.includes('will appear shortly');
                    if (isBackgroundLoading) {
                        this._backgroundProcessingRetries += 1;
                        const maxBgRetries = 12; // ~24s if 2s delay
                        if (this._backgroundProcessingRetries <= maxBgRetries) {
                            const delayMs = 2000;
                            verboseLog(`⏳ Background load in progress (retry ${this._backgroundProcessingRetries}/${maxBgRetries}) – retrying in ${delayMs}ms`);
                            setTimeout(() => {
                                // Fire-and-forget; flag will prevent duplicate overlaps
                                this.fetchAndUpdateAvailableTags().catch(e => console.warn('Background retry failed:', e));
                            }, delayMs);
                            // Keep splash visible; don't overwrite UI with message
                            return false;
                        }
                        console.warn('⚠️ Background loading retries exhausted; showing message to user');
                    }

                    // Try cache as fallback
                    const cachedTags = this.hydrateAvailableTagsFromCache();
                    if (cachedTags) {
                        verboseLog('✅ Using cached tags as fallback for error response');
                        return true;
                    }
                    // Show message to user if no cache available
                    const availableTagsContainer = document.getElementById('availableTags');
                    if (availableTagsContainer && errorMsg) {
                        availableTagsContainer.innerHTML = `
                            <div class="text-center py-4">
                                <div class="alert alert-info mx-3">
                                    <p class="mb-2">${errorMsg}</p>
                                    <button class="btn btn-primary btn-sm" onclick="TagManager.fetchAndUpdateAvailableTags()">
                                        <i class="fas fa-redo"></i> Retry
                                    </button>
                                </div>
                            </div>
                        `;
                    }
                } else {
                    console.warn('Backend returned empty tags array - no Excel file loaded');
                }
                this.state.tags = [];
                this.state.originalTags = [];
                this._updateAvailableTags([]);
                this._restoreAvailableScrollPosition(savedScroll);
                // Hide splash when no tags
                if (this.hideActionSplash) {
                    this.hideActionSplash();
                }
                // CRITICAL FIX: Still complete initialization even with no tags
                // This allows the app to load and show the upload UI
                if (AppLoadingSplash && AppLoadingSplash.isVisible) {
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                }
                // Return true to indicate initialization completed (even with no tags)
                return true;
            }
            
            // PERFORMANCE OPTIMIZATION: Single-pass normalization to reduce processing overhead
            // Normalize tags to ensure database lineage is ALWAYS used (single pass instead of multiple)
            verboseLog(`Normalizing ${tags.length} tags to prioritize database lineage...`);
            const normalizedTags = tags.map(tag => {
                // CRITICAL: ALWAYS prioritize database lineage fields over Excel Lineage
                if (tag.canonical_lineage || tag.currentLineage) {
                    const dbLineage = (tag.canonical_lineage || tag.currentLineage).toString().trim().toUpperCase();
                    // Update all lineage fields to match database lineage for consistency
                    tag.Lineage = dbLineage;
                    tag.lineage = dbLineage.toLowerCase();
                    tag.currentLineage = dbLineage;
                    tag.canonical_lineage = dbLineage;
                    }
                // Apply normalization function if available (for additional processing)
                return this._normalizeLineageFields ? this._normalizeLineageFields(tag) : tag;
            });
            
            tags = normalizedTags;
            verboseLog(`Fetched and normalized ${tags.length} available tags`);

            // PERFORMANCE: Reduced debug logging - only log summary, not every tag
            if (verboseLog.enabled) {
            const tagsWithDbLineage = tags.filter(t => t.canonical_lineage || t.currentLineage).length;
                verboseLog(`📊 ${tagsWithDbLineage}/${tags.length} tags have database lineage fields`);
            }
            
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
            
            // CRITICAL: Clear safety timeout since we successfully loaded tags
            if (safetyTimeout) {
                clearTimeout(safetyTimeout);
                safetyTimeout = null;
            }
            
            // CRITICAL FIX: Ensure ALL tags in state have database lineage fields set
            // This ensures TagManager state ALWAYS reflects database lineage, not Excel lineage
            const stateTagsWithDbLineage = tags; // Already normalized above, no need for another pass
            
            // Clear existing state and set new data
            this.state.tags = [...stateTagsWithDbLineage];
            this.state.originalTags = [...stateTagsWithDbLineage]; // Store original tags for validation
            this.state.hydratedFromCache = false;
            // CRITICAL FIX: Ensure _selectedTagsSet is initialized when tags are loaded
            if (!this.state._selectedTagsSet) {
                this.state._selectedTagsSet = new Set(this.state.persistentSelectedTags || []);
            }
            this.saveAvailableTagsToCache(tags);
            
            // CRITICAL FIX: Always update UI after loading tags to ensure lineage dropdowns reflect database values
            // This is especially important when lineage alignment happened on the backend
            console.log(`🔄 Updating UI with ${tags.length} tags (source: ${responseData?.source || 'unknown'})`);
            this._backgroundProcessingRetries = 0; // reset after successful load
            
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
            // CRITICAL FIX: Preserve persistentSelectedTags even if tag objects aren't immediately found
            // Save a copy before any operations to prevent accidental loss
            const savedSelectedTagsBeforeUpdate = [...(this.state.persistentSelectedTags || [])];
            
            if (this.state.persistentSelectedTags.length > 0) {
                console.log(`🔄 Preserving ${this.state.persistentSelectedTags.length} selected tags during tag update`);
                
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
                    // CRITICAL FIX: Don't log warning if tag isn't found - it might be temporarily unavailable
                    // The tag might be in a different filter or still loading
                    return null;
                }).filter(Boolean);
                
                // CRITICAL FIX: Even if some tag objects aren't found, preserve the selections
                // They might be in a different filter or temporarily unavailable
                if (selectedTagObjects.length > 0) {
                    console.log(`✅ Updating ${selectedTagObjects.length} selected tags with database lineage from available tags`);
                    // Force update to ensure dropdowns are re-rendered with database lineage
                    this._forceSelectedTagsUpdate = true;
                    this.updateSelectedTags(selectedTagObjects);
                } else if (this.state.persistentSelectedTags.length > 0) {
                    // CRITICAL FIX: If no tag objects found but we have persistent selections,
                    // don't clear them - they might be in a different filter or still loading
                    console.log(`⚠️ Selected tag objects not found in current tags, but preserving ${this.state.persistentSelectedTags.length} selections`);
                    // Try to restore from originalTags as fallback
                    const fallbackTagObjects = this.state.persistentSelectedTags.map(name => {
                        return this.state.originalTags.find(t => t['Product Name*'] === name);
                    }).filter(Boolean);
                    
                    if (fallbackTagObjects.length > 0) {
                        console.log(`✅ Found ${fallbackTagObjects.length} selected tags in originalTags, restoring...`);
                        this._forceSelectedTagsUpdate = true;
                        this.updateSelectedTags(fallbackTagObjects);
                    }
                }
            }
            
            // CRITICAL FIX: Safety check - if persistentSelectedTags were accidentally cleared, restore them
            if (savedSelectedTagsBeforeUpdate.length > 0 && this.state.persistentSelectedTags.length === 0) {
                console.warn('⚠️ persistentSelectedTags were cleared during tag update, restoring from saved copy');
                this.state.persistentSelectedTags = [...savedSelectedTagsBeforeUpdate];
                this.state.selectedTags = new Set(savedSelectedTagsBeforeUpdate);
                // Restore checkboxes after a short delay to ensure DOM is ready
                setTimeout(() => {
                    this._restoreCheckboxStates();
                }, 100);
            }
            
            // PERFORMANCE: Clear filter cache when tags change
            this._cachedFilterOptions = null;
            this._cachedFilterOptionsHash = null;
            this._cachedFilterOptionsTagsLength = null;
            
            // CRITICAL FIX: Don't clear selected tags here - they've already been preserved and updated above
            // The code above (lines 7845-7877) already handles updating selected tags with database lineage
            // Clearing and restoring here was causing selections to disappear after first selection
            // CRITICAL FIX: Don't filter out selected tags - preserve them even if temporarily not in available tags
            // This prevents tags from disappearing during loading, updates, or when tags are temporarily unavailable
            // The validateSelectedTags function will handle cleanup of truly invalid tags later
            if (this.state.persistentSelectedTags.length > 0) {
                // Don't filter here - preserve all selections
                // Tags might be temporarily unavailable during updates but will come back
                verboseLog(`Preserving ${this.state.persistentSelectedTags.length} selected tags during tag update`);
                // Just update selectedTags set to match persistentSelectedTags
                this.state.selectedTags = new Set(this.state.persistentSelectedTags);
            }
            
            this.validateSelectedTags();
            
            // OPTIMIZATION: If this was a fast load, optionally refresh with lineage alignment in background
            // CRITICAL FIX: Disabled background refresh to prevent restarts - lineage is already aligned in main fetch
            // This allows tags to appear immediately without triggering another load
            if (responseData && responseData.source === 'cache-fast' && tags.length > 0) {
                verboseLog('Fast load completed - tags displayed immediately');
                // Update UI immediately with fast-loaded tags
                this._updateAvailableTags(tags);
                this._restoreAvailableScrollPosition(savedScroll);
                
                // Update tag counts
                this.updateTagCount('available', tags.length);
                this.updateTagCount('selected', this.state.persistentSelectedTags.length);
                
                // REMOVED: Background refresh was causing multiple restarts
                // Lineage is already aligned in the main fetch, no need for background refresh
                
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
            
            // CRITICAL FIX: Ensure filter row container is visible after tags are loaded
            const filterRow = document.querySelector('.filter-row');
            if (filterRow) {
                filterRow.style.display = 'flex';
                filterRow.style.visibility = 'visible';
                verboseLog('✅ Filter row container made visible after tag update');
            }
            
            // CRITICAL FIX: Ensure filters are rendered after tags are updated
            if (this.renderActiveFilters) {
                this.renderActiveFilters();
                verboseLog('✅ Filters rendered after tag update');
            }
            
            verboseLog(`Successfully updated available tags: ${tags.length} tags`);
            verboseLog('=== fetchAndUpdateAvailableTags END ===');
            // Note: Splash will be hidden by _waitForTagsToAppear() when tags appear
            return true;
        } catch (error) {
            // CRITICAL: Clear safety timeout on error
            // Use try-catch to handle case where safetyTimeout might not be in scope
            try {
                if (typeof safetyTimeout !== 'undefined' && safetyTimeout) {
                    clearTimeout(safetyTimeout);
                }
            } catch (e) {
                // Ignore - variable might not be in scope
            }
            
            console.error('Error fetching available tags:', error);
            verboseLog('=== fetchAndUpdateAvailableTags ERROR ===');
            // Note: Flag will be reset in finally block
            // CRITICAL FIX: savedScroll may not be defined if error occurs early - save it now if needed
            const savedScrollForFallback = typeof savedScroll !== 'undefined' ? savedScroll : this._saveAvailableScrollPosition();
            // If this is just a timeout/AbortError and we already have tags on screen,
            // keep the existing inventory visible and avoid nuking the UI.
            const hasExistingTags = Array.isArray(this.state.tags) && this.state.tags.length > 0;
            if (error && error.name === 'AbortError' && hasExistingTags) {
                verboseLog('Available tags request aborted, preserving existing inventory');
                if (this.hideActionSplash) {
                    this.hideActionSplash();
                }
                return true;
            }

            // Try cache as fallback before showing error
            const cachedTags = this.hydrateAvailableTagsFromCache();
            if (cachedTags) {
                verboseLog('✅ Using cached tags as fallback after error');
                return true;
            }

            // If lite tags already rendered successfully, don't invoke fallback again
            const fallbackLoaded = this._liteTagsRendered
                ? false
                : await this._fallbackToLiteAvailableTags(error, savedScrollForFallback);
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
                const errorMessage = error.message || 'Unknown error';
                const isProcessingError = errorMessage.includes('still processing') || errorMessage.includes('processing');
                availableTagsContainer.innerHTML = `
                    <div class="text-center py-4">
                        <div class="alert alert-warning mx-3">
                            <h5 class="alert-heading">Unable to Load Tags</h5>
                            <p class="mb-3">${isProcessingError 
                                ? 'The file is still being processed. Please wait a moment and try again, or refresh the page.' 
                                : 'There was a problem loading the product tags. This can happen if the database is temporarily unavailable or the connection timed out.'}</p>
                            <button class="btn btn-primary" onclick="TagManager.retryLoadTags()">
                                <i class="fas fa-redo"></i> Retry Loading Tags
                            </button>
                        </div>
                        <small class="text-muted d-block mt-2">Error: ${errorMessage}</small>
                    </div>
                `;
            }

            return false;
        } finally {
            // CRITICAL FIX: Always reset flag in finally block to ensure it's cleared even if error occurs
            // This prevents the hangup issue where the flag gets stuck in true state
            this._fetchingAvailableTags = false;
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
            this.state._selectedTagsSet = new Set(); // PERFORMANCE: Reset Set when clearing tags
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
            
            // CRITICAL FIX: Prevent fetching if we just had a recent selection (within last 2 seconds)
            // This prevents tags from disappearing right after selection on initial load
            const now = Date.now();
            if (this._lastTagSelectionTime && (now - this._lastTagSelectionTime) < 2000) {
                verboseLog('⏸️ Skipping fetchAndUpdateSelectedTags - recent tag selection detected (within 2s)');
                return true; // Return success to avoid error handling
            }
            
            // CRITICAL FIX: Prevent clearing tags right after generation (within last 30 seconds)
            // Generation doesn't clear backend selected tags, so don't fetch and overwrite local selections
            if (this._lastGenerationTime && (now - this._lastGenerationTime) < 30000) {
                verboseLog('⏸️ Skipping fetchAndUpdateSelectedTags - recent generation detected (within 30s), preserving current selections');
                return true; // Return success to preserve current selections
            }
            
            // CRITICAL FIX: Preserve local selections before fetching from backend
            // This prevents selections from disappearing if backend hasn't saved them yet
            const localSelections = [...this.state.persistentSelectedTags];
            verboseLog('Local selections before fetch:', localSelections);
            
            const timestamp = Date.now();
            const response = await fetch(`/api/selected-tags?t=${timestamp}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const selectedTags = await response.json();
            
            if (!selectedTags || !Array.isArray(selectedTags)) {
                console.warn('No selected tags found in backend - preserving local selections');
                // CRITICAL FIX: Don't clear if we have local selections
                if (localSelections.length > 0) {
                    verboseLog('Preserving local selections:', localSelections);
                    // Keep local selections and update display
                    const localTagObjects = localSelections.map(name => {
                        return this.state.tags.find(t => t['Product Name*'] === name) ||
                               this.state.originalTags.find(t => t['Product Name*'] === name) ||
                               null;
                    }).filter(Boolean);
                    
                    if (localTagObjects.length > 0) {
                        this.updateSelectedTags(localTagObjects);
                    }
                } else {
                    // Only clear if we truly have no selections locally or in backend
                    this.updateSelectedTags([]);
                }
                return true;
            }
            
            verboseLog(`Fetched ${selectedTags.length} selected tags from backend:`, selectedTags.map(tag => tag['Product Name*']));

            // CRITICAL FIX: Trust backend as source of truth on page load
            // Only merge if we have recent local changes (within last 2 seconds)
            const hasRecentLocalChanges = this._lastTagSelectionTime && (now - this._lastTagSelectionTime) < 2000;
            const hasRecentGeneration = this._lastGenerationTime && (now - this._lastGenerationTime) < 10000;

            let finalSelections;
            let finalTagObjects;

            if ((hasRecentLocalChanges || hasRecentGeneration) && localSelections.length > 0) {
                // Merge recent local changes/generation with backend to prevent losing selections
                const backendTagNames = selectedTags.map(tag => tag['Product Name*']);
                finalSelections = [...new Set([...localSelections, ...backendTagNames])];
                verboseLog('Merged selections (recent local/generation + backend):', finalSelections);
            } else if (localSelections.length > 0 && selectedTags.length === 0) {
                // CRITICAL FIX: If backend is empty but we have local selections, preserve local selections
                // This prevents clearing tags after generation when backend hasn't saved them yet
                finalSelections = localSelections;
                verboseLog('Backend empty but local selections exist - preserving local selections:', finalSelections);
            } else {
                // Trust backend completely on page reload (only if backend has data)
                finalSelections = selectedTags.map(tag => tag['Product Name*']);
                verboseLog('Using backend selections as source of truth:', finalSelections);
            }

            // Update persistentSelectedTags with final selections
            this.state.persistentSelectedTags = finalSelections;
            // Save to localStorage for persistence
            this.saveSelectedTagsToStorage();
            this.state.selectedTags = new Set(this.state.persistentSelectedTags);
            verboseLog('persistentSelectedTags updated:', this.state.persistentSelectedTags);

            // Build tag objects for final selections
            const tagsMap = new Map(selectedTags.map(t => [t['Product Name*'], t]));
            const stateTagsMap = new Map(this.state.tags.map(t => [t['Product Name*'], t]));
            const originalTagsMap = new Map(this.state.originalTags.map(t => [t['Product Name*'], t]));

            finalTagObjects = finalSelections.map(tagName => {
                return tagsMap.get(tagName) ||
                       stateTagsMap.get(tagName) ||
                       originalTagsMap.get(tagName) ||
                       null;
            }).filter(Boolean);

            verboseLog('Final tag objects:', finalTagObjects.length);
            this.updateSelectedTags(finalTagObjects);
            
            // Ensure drag and drop is working after fetching tags
            if (window.dragAndDropManager && finalTagObjects.length > 0) {
                setTimeout(() => {
                    verboseLog('Reinitializing drag and drop after fetchAndUpdateSelectedTags');
                    window.dragAndDropManager.reinitializeTagDragAndDrop();
                }, 300);
            }
            
            return true;
        } catch (error) {
            console.error('Error fetching selected tags:', error);
            // CRITICAL FIX: Don't clear selections on error - preserve local selections
            const localSelections = [...this.state.persistentSelectedTags];
            if (localSelections.length > 0) {
                verboseLog('Error fetching selected tags, preserving local selections:', localSelections);
                const localTagObjects = localSelections.map(name => {
                    return this.state.tags.find(t => t['Product Name*'] === name) ||
                           this.state.originalTags.find(t => t['Product Name*'] === name) ||
                           null;
                }).filter(Boolean);
                
                if (localTagObjects.length > 0) {
                    this.updateSelectedTags(localTagObjects);
                }
            } else {
                // Only clear if we have no local selections
                this.updateSelectedTags([]);
            }
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

        // PERFORMANCE FIX: Debounce rapid refresh calls to prevent flashing
        const now = Date.now();
        if (!this._lastRefreshTime) {
            this._lastRefreshTime = 0;
        }
        const timeSinceLastRefresh = now - this._lastRefreshTime;
        const minRefreshInterval = 1000; // Minimum 1 second between refreshes
        
        if (timeSinceLastRefresh < minRefreshInterval && !force) {
            verboseLog(`Skipping refresh - only ${timeSinceLastRefresh}ms since last refresh`);
            return [true, true, true]; // Return success without refreshing
        }
        this._lastRefreshTime = now;

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

            // PERFORMANCE: No delay needed - fetch filters immediately
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
        // Show splash screen before starting export
        if (this.showActionSplash) {
            this.showActionSplash('Exporting data to Excel...');
        } else if (typeof showExportSplash === 'function') {
            showExportSplash();
        } else {
            // Fallback: show a simple loading message
            console.log('Exporting data to Excel...');
        }
        
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
            
            // Hide splash screen after successful download
            if (this.hideActionSplash) {
                this.hideActionSplash();
            } else if (typeof hideExportSplash === 'function') {
                hideExportSplash();
            }
        } catch (error) {
            console.error('Error downloading Excel:', error);
            // Hide splash screen on error
            if (this.hideActionSplash) {
                this.hideActionSplash();
            } else if (typeof hideExportSplash === 'function') {
                hideExportSplash();
            }
            alert(error.message || 'Failed to download Excel');
        }
    },

    // Initialize the tag manager
    init() {
        // CRITICAL FIX: Prevent multiple initialization calls
        if (this.state.initialized || this._initializing) {
            console.log('⚠️ TagManager already initialized or initializing, skipping duplicate init call');
            return;
        }
        this._initializing = true;
        
        console.log('🚀 === TAGMANAGER INIT FUNCTION CALLED ===');
        console.log('⚡ TagManager initializing...');
        const availableTagsContainer = document.getElementById('availableTags');
        console.log('📦 Available tags container found:', !!availableTagsContainer);
        if (availableTagsContainer) {
            console.log('📝 Container ready for tags');
        }
        
        // CRITICAL FIX: Initialize lineage update tracking
        this._lineageUpdatePending = new Set();
        this._lineageUpdateCompletions = new Map();
        this._lineageUpdateProcessing = false;
        
        // CRITICAL FIX: Prevent page reload until lineage updates complete
        this._setupLineageUpdateReloadProtection();
        
        // Skip platform detection for Mac-like speed
        // this.detectPlatform();
        
        // CRITICAL FIX: Hydrate from cache FIRST synchronously for instant display
        // This ensures tags appear immediately on page reload before any API calls
        const hydrated = this.hydrateAvailableTagsFromCache();
        if (hydrated) {
            console.log(`⚡ INSTANT CACHE: Tags hydrated from cache, displayed immediately`);
            this.state.initialized = true;
            this._initializing = false;
            
            // Load selected tags and filters in background (non-blocking)
            this.fetchAndUpdateSelectedTags().catch(err => console.warn('Error loading selected tags:', err));
            if (this.fetchAndPopulateFilters) {
                this.fetchAndPopulateFilters().catch(err => console.warn('Error loading filters:', err));
            }
            
            // CRITICAL FIX: Still fetch fresh data in background to ensure tags are up-to-date
            // This prevents stale cache from preventing tag loading
            setTimeout(() => {
                if (!this._checkingExistingData) {
                    this.checkForExistingData().catch(err => {
                        console.warn('Background refresh after cache load failed (non-critical):', err);
                    });
                }
            }, 1000);
            
            // Continue with rest of initialization (filters, etc.) but skip splash
            this._continueInitWithoutSplash();
            return;
        }
        
        // No cache - show splash screen and load from server
        // Show application splash screen
        AppLoadingSplash.show();
        AppLoadingSplash.startAutoAdvance();
        
        // Initialize empty state first (but don't clear if we have tags)
        this.clearInitialDataRetry();
        // CRITICAL FIX: Only initialize empty state if we don't have tags already
        if (!this.state.tags || this.state.tags.length === 0) {
            this.initializeEmptyState();
        }
        AppLoadingSplash.nextStep(); // Templates loaded
        
        // Check if there's already data loaded (e.g., from a previous session or default file)
        this.checkForExistingData().then(() => {
            this.state.initialized = true;
            this._initializing = false;
            
            // CRITICAL FIX: Verify tags actually loaded, retry if not
            setTimeout(() => {
                const hasTags = this.state.tags && this.state.tags.length > 0;
                const hasRenderedTags = document.getElementById('availableTags')?.querySelectorAll('.tag-item').length > 0;
                if (!hasTags && !hasRenderedTags) {
                    console.warn('⚠️ Tags not loaded after checkForExistingData, attempting direct fetch...');
                    this.fetchAndUpdateAvailableTags().catch(e => {
                        console.error('Direct fetch after checkForExistingData failed:', e);
                    });
                }
            }, 2000);
        }).catch(err => {
            console.error('Error during initialization:', err);
            // CRITICAL FIX: Still try to fetch tags even if checkForExistingData fails
            console.log('🔄 Initialization failed, attempting direct tag fetch as fallback...');
            this.fetchAndUpdateAvailableTags().then(() => {
                this.state.initialized = true;
                this._initializing = false;
            }).catch(fetchErr => {
                console.error('Fallback fetch also failed:', fetchErr);
                this.state.initialized = true;
                this._initializing = false;
            });
        });
        
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
        
        // Emergency initialization fix - force complete after 8 seconds
        setTimeout(() => {
            if (AppLoadingSplash && AppLoadingSplash.isVisible) {
                verboseLog('Emergency initialization fix: forcing splash completion');
                AppLoadingSplash.stopAutoAdvance();
                AppLoadingSplash.complete();
                
                // Also try to initialize TagManager if it hasn't been initialized yet
                if (window.TagManager && typeof window.TagManager.init === 'function' && !window.TagManager.state.initialized) {
                    verboseLog('Emergency: Attempting to initialize TagManager');
                    try {
                        window.TagManager.init();
                    } catch (e) {
                        console.error('Emergency TagManager.init() failed:', e);
                    }
                }
            }
        }, 8000); // Reduced from 15000 to 8000
        
        // Additional emergency fix for stuck initialization
        window.addEventListener('load', () => {
            setTimeout(() => {
                const splash = document.getElementById('appLoadingSplash');
                if (splash && splash.style.display !== 'none') {
                    verboseLog('Emergency fix: hiding stuck splash screen');
                    splash.style.display = 'none';
                    const mainContent = document.getElementById('mainContent');
                    if (mainContent) {
                        // CRITICAL FIX: Prevent visual glitches by ensuring smooth transition
                        mainContent.style.display = 'block';
                        mainContent.style.visibility = 'visible';
                        mainContent.style.opacity = '1';
                        mainContent.classList.add('loaded');
                    }
                    
                    // Force initialize TagManager if still not initialized
                    if (window.TagManager && typeof window.TagManager.init === 'function' && !window.TagManager.state.initialized) {
                        verboseLog('Emergency: Force initializing TagManager after load');
                        try {
                            window.TagManager.init();
                        } catch (e) {
                            console.error('Emergency TagManager.init() after load failed:', e);
                        }
                    }
                }
            }, 10000); // Reduced from 20000 to 10000
        });
    },

    // Continue initialization without showing splash (for cache hits)
    _continueInitWithoutSplash() {
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
        
        // Add filter change event listeners immediately
        verboseLog('=== SETTING UP FILTER EVENT LISTENERS ===');
        this.setupFilterEventListeners();
        verboseLog('=== FILTER EVENT LISTENERS SETUP COMPLETE ===');
        
        // Add search event listeners
        this.setupSearchEventListeners();
        
        // Start memory optimization
        this.startMemoryOptimization();
        
        // Start periodic filter refresh
        this.startPeriodicFilterRefresh();
        
        // Update table header if TagsTable is available
        setTimeout(() => {
            if (typeof TagsTable !== 'undefined' && TagsTable.updateTableHeader) {
                TagsTable.updateTableHeader();
            }
        }, 100);
    },

    // CRITICAL FIX: Setup reload protection to wait for pending lineage updates
    _setupLineageUpdateReloadProtection() {
        // Intercept page reload attempts - but use safeReload to prevent multiple reloads
        const originalReload = window.location.reload.bind(window.location);
        window.location.reload = (force) => {
            // Use safeReload if available to prevent multiple reloads
            if (window.safeReload && !_reloadInProgress) {
                this._waitForPendingLineageUpdates().then(() => {
                    console.log('✅ All lineage updates completed, proceeding with reload...');
                    safeReload(0);
                }).catch((error) => {
                    console.warn('⚠️ Error waiting for lineage updates, reloading anyway:', error);
                    safeReload(0);
                });
            } else {
                // Fallback to original behavior if safeReload not available
                this._waitForPendingLineageUpdates().then(() => {
                    console.log('✅ All lineage updates completed, proceeding with reload...');
                    originalReload(force);
                }).catch((error) => {
                    console.warn('⚠️ Error waiting for lineage updates, reloading anyway:', error);
                    originalReload(force);
                });
            }
        };
        
        // Add beforeunload handler to warn if updates are pending
        window.addEventListener('beforeunload', (event) => {
            if (this._hasPendingLineageUpdates()) {
                const message = 'Lineage updates are in progress. Reloading now may cause changes to be lost.';
                event.preventDefault();
                event.returnValue = message;
                return message;
            }
        });
        
        console.log('🛡️ Lineage update reload protection enabled');
    },

    // Check if there are pending lineage updates
    _hasPendingLineageUpdates() {
        return (this._lineageUpdatePending && this._lineageUpdatePending.size > 0) ||
               (this._lineageUpdateProcessing === true);
    },

    // Wait for all pending lineage updates to complete
    async _waitForPendingLineageUpdates(maxWaitMs = 5000) {
        const startTime = Date.now();
        
        while (this._hasPendingLineageUpdates() && (Date.now() - startTime) < maxWaitMs) {
            console.log(`⏳ Waiting for lineage updates to complete... (pending: ${this._lineageUpdatePending?.size || 0}, processing: ${this._lineageUpdateProcessing})`);
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        // Additional wait to ensure database commits are flushed (backend waits 0.1s + verification time)
        if (this._lineageUpdateCompletions && this._lineageUpdateCompletions.size > 0) {
            const lastCompletion = Math.max(...Array.from(this._lineageUpdateCompletions.values()));
            const timeSinceLastCompletion = Date.now() - lastCompletion;
            const additionalWait = Math.max(0, 500 - timeSinceLastCompletion); // Wait at least 500ms after last completion
            if (additionalWait > 0) {
                console.log(`⏳ Waiting ${additionalWait}ms for database commits to flush...`);
                await new Promise(resolve => setTimeout(resolve, additionalWait));
            }
        }
        
        if (this._hasPendingLineageUpdates()) {
            console.warn('⚠️ Still have pending lineage updates after waiting, proceeding anyway');
        } else {
            console.log('✅ All lineage updates completed');
        }
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
        this.state._selectedTagsSet = new Set(); // CRITICAL: Initialize Set for checkbox state management

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
        // CRITICAL FIX: Check emergency kill switch first
        if (window.EMERGENCY_KILL_SWITCH) {
            console.error('🚨 EMERGENCY KILL SWITCH ACTIVE - Stopping checkForExistingData');
            this._checkingExistingData = false;
            return;
        }
        
        // CRITICAL FIX: Reset stuck flag after 30 seconds to prevent permanent blocking
        if (this._checkingExistingData) {
            const checkStartTime = this._checkingExistingDataStartTime || Date.now();
            const stuckDuration = Date.now() - checkStartTime;
            if (stuckDuration > 30000) {
                console.warn('⚠️ checkForExistingData stuck for 30+ seconds, resetting flag');
                this._checkingExistingData = false;
            } else {
                console.warn('⚠️ checkForExistingData already in progress, skipping to prevent browser freeze...');
                return;
            }
        }
        
        // CRITICAL FIX: Reset attempt counter on page refresh to allow fresh retries
        // Only enforce max attempts within the same session, not across page refreshes
        const pageLoadTime = performance.timing?.navigationStart || Date.now();
        const timeSincePageLoad = Date.now() - pageLoadTime;
        if (timeSincePageLoad < 5000) {
            // Fresh page load - reset attempt counter
            this.state.initialDataAttempts = 0;
        }
        
        const ABSOLUTE_MAX_ATTEMPTS = 10; // Increased from 5 to allow more retries
        if ((this.state.initialDataAttempts || 0) >= ABSOLUTE_MAX_ATTEMPTS) {
            console.error(`❌ STOPPING checkForExistingData - max attempts (${ABSOLUTE_MAX_ATTEMPTS}) exceeded`);
            // CRITICAL FIX: Still try direct fetch as last resort instead of giving up completely
            console.log('🔄 Last resort: Attempting direct tag fetch...');
            try {
                await this.fetchAndUpdateAvailableTags();
                this._checkingExistingData = false;
                return;
            } catch (err) {
                console.error('Last resort fetch failed:', err);
                this._checkingExistingData = false;
                return;
            }
        }
        
        // CRITICAL FIX: Always try to fetch fresh data, even if cache exists
        // Cache is just for instant display, but we should still refresh in background
        const recentUpload = this._lastUploadTime && (Date.now() - this._lastUploadTime) < 5000;
        const hasCachedTags = this.state.hydratedFromCache && this.state.tags && this.state.tags.length > 0;
        
        // If we have cached tags but no recent upload, still fetch fresh data in background
        // but don't clear existing tags
        if (!recentUpload && hasCachedTags) {
            verboseLog('✅ Tags loaded from cache, fetching fresh data in background...');
            // Still fetch fresh data but don't block UI
            this.fetchAndUpdateAvailableTags().catch(err => {
                console.warn('Background refresh failed (non-critical):', err);
            });
            return;
        }
        
        this._checkingExistingData = true;
        this._checkingExistingDataStartTime = Date.now();

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

        // CRITICAL FIX: Don't clear container if tags are already displayed from cache
        const hasDisplayedTags = this.state.hydratedFromCache && this.state.tags && this.state.tags.length > 0;
        
        // Show loading splash only if file exists AND tags aren't already displayed
        const availableTagsContainer = document.getElementById('availableTags');
        if (availableTagsContainer && !hasDisplayedTags) {
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
                // No file - but still try to load tags from database (store-based)
                // Show loading indicator while attempting to load from database
                this.showActionSplash('Loading tags from database...');
                availableTagsContainer.innerHTML = `
                    <div class="text-center py-4">
                        <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-2 text-white">Loading tags from database...</p>
                    </div>
                `;
                // Continue to load tags from database even without uploaded file
                // Don't exit early - let the function continue to fetch from database
            }
        } else if (hasDisplayedTags) {
            // Tags already displayed from cache - skip showing loading spinner
            verboseLog('Tags already displayed from cache, skipping loading indicator');
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

        // Safety net: ensure loading overlay never blocks interaction for long
        // Reduced to 10 seconds since we're using faster timeouts and cache
        // Declare splashSafetyTimeout early so it can be cleared in early return paths
        let splashSafetyTimeout = null;

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
            
            if (splashSafetyTimeout) {
                clearTimeout(splashSafetyTimeout);
            }
            this._checkingExistingData = false;
            return; // Exit early - we have cached data
        }

        // PERFORMANCE FIX: Increased timeout to 60 seconds for large files
        // Large Excel files can take time to process, especially on first load
        const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('Initialization timeout')), 60000);
        });

        // Set the safety timeout - increased for large files
        splashSafetyTimeout = setTimeout(() => {
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
        }, 60000); // 60 second safety net - increased for large files

        try {
            // PERFORMANCE FIX: Use fast_load=1 for initial loads to skip expensive lineage alignment
            // This dramatically speeds up initial tag loading
            // CRITICAL FIX: Add timeout to prevent hanging - if API takes too long, complete initialization anyway
            const response = await Promise.race([
                fetch('/api/initial-data?fast_load=1'),
                timeoutPromise
            ]).catch(err => {
                // If fetch fails or times out, complete initialization anyway
                console.warn('Initial data fetch failed or timed out:', err);
                // Complete splash screen
                if (AppLoadingSplash && AppLoadingSplash.isVisible) {
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                }
                if (this.hideActionSplash) {
                    this.hideActionSplash();
                }
                // Show upload prompt
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
                clearTimeout(splashSafetyTimeout);
                throw err; // Re-throw to be caught by outer catch
            });

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
                    
                    // CRITICAL FIX: Store tags in state immediately
                    this.state.tags = [...data.available_tags];
                    this.state.originalTags = [...data.available_tags];
                    
                    // CRITICAL FIX: Save to cache immediately for instant reload
                    this.saveAvailableTagsToCache(data.available_tags);
                    console.log(`💾 Cached ${data.available_tags.length} tags for instant reload`);
                    
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
                    
                    // CRITICAL FIX: If file exists but tags are empty, retry loading tags
                    // This handles the case where file is still processing
                    if (hasFile && (!data.available_tags || data.available_tags.length === 0)) {
                        verboseLog('⚠️ File exists but tags are empty - file may still be processing, retrying...');
                        const availableTagsContainer = document.getElementById('availableTags');
                        if (availableTagsContainer) {
                            availableTagsContainer.innerHTML = `
                                <div class="text-center py-4">
                                    <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                    <p class="mt-2 text-white">File processing, loading tags...</p>
                                </div>
                            `;
                        }
                        
                        // Retry loading tags after a delay (silently)
                        this._checkingExistingData = false;
                        setTimeout(() => {
                            this.checkForExistingData();
                        }, 2000); // Wait 2 seconds before retry
                        return;
                    }
                    
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
            
            // CRITICAL FIX: Try fallback fetch before giving up completely
            console.log('🔄 Error occurred, attempting fallback tag fetch...');
            let fallbackSucceeded = false;
            try {
                const fallbackResult = await this.fetchAndUpdateAvailableTags();
                if (fallbackResult) {
                    console.log('✅ Fallback fetch succeeded');
                    fallbackSucceeded = true;
                    this._checkingExistingData = false;
                    clearTimeout(splashSafetyTimeout);
                    return;
                }
            } catch (fallbackError) {
                console.error('Fallback fetch also failed:', fallbackError);
            }
            
            // Complete splash loading on error
            AppLoadingSplash.stopAutoAdvance();
            AppLoadingSplash.complete();
            clearTimeout(splashSafetyTimeout);
            
            // Hide action splash on error
            if (this.hideActionSplash) {
                this.hideActionSplash();
            }
            
            // Show upload prompt in Current Inventory on error/timeout (only if fallback failed)
            if (!fallbackSucceeded) {
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
            }
            
            this._checkingExistingData = false;
            this.scheduleInitialDataRetry(error.message || 'initial data fetch error');
            return;
        } finally {
            // CRITICAL FIX: Always reset checking flag in finally block to prevent stuck state
            // This ensures the flag is reset even if an unexpected error occurs
            setTimeout(() => {
                if (this._checkingExistingData) {
                    const checkDuration = Date.now() - (this._checkingExistingDataStartTime || Date.now());
                    if (checkDuration > 60000) {
                        console.warn('⚠️ checkForExistingData took longer than 60 seconds, forcing reset');
                        this._checkingExistingData = false;
                    }
                }
            }, 100);
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
            
            // CRITICAL FIX: Mark that we just generated tags to prevent them from being cleared
            // This prevents fetchAndUpdateSelectedTags from clearing selections after generation
            this._lastTagSelectionTime = Date.now();
            this._lastGenerationTime = Date.now();
            verboseLog('✅ Generation complete - preserving selected tags');
            
            // CRITICAL FIX: Sync _selectedTagsSet with persistentSelectedTags before any updates
            // This ensures checkbox states are properly maintained after generation
            if (!this.state._selectedTagsSet) {
                this.state._selectedTagsSet = new Set();
            }
            this.state._selectedTagsSet.clear();
            this.state.persistentSelectedTags.forEach(name => {
                this.state._selectedTagsSet.add(name);
            });
            
            // CRITICAL FIX: Explicitly refresh selected tags display to ensure they remain visible
            // This prevents any race conditions where other code might clear them
            if (this.state.persistentSelectedTags && this.state.persistentSelectedTags.length > 0) {
                const selectedTagObjects = this.getSelectedTagObjects();
                if (selectedTagObjects.length > 0) {
                    // Use setTimeout to ensure this happens after any other pending updates
                    setTimeout(() => {
                        this.updateSelectedTags(selectedTagObjects);
                        // CRITICAL FIX: Ensure all checkboxes are enabled after generation
                        this._ensureCheckboxesEnabled();
                        // CRITICAL FIX: Restore checkbox states after updating selected tags
                        // This ensures available tag checkboxes match persistentSelectedTags
                        setTimeout(() => {
                            this._restoreCheckboxStates();
                            // Double-check that checkboxes are still enabled after restore
                            this._ensureCheckboxesEnabled();
                        }, 50);
                        verboseLog('✅ Refreshed selected tags display after generation');
                    }, 100);
                }
            }
        } catch (error) {
            console.error('Error generating labels:', error);
            // CRITICAL FIX: Even on error, mark generation time to preserve selections
            // This prevents tags from disappearing if generation partially succeeded
            this._lastTagSelectionTime = Date.now();
            this._lastGenerationTime = Date.now();
        } finally {
            // CRITICAL FIX: Ensure generation timestamp is always set, even if something goes wrong
            if (!this._lastGenerationTime) {
                this._lastGenerationTime = Date.now();
                this._lastTagSelectionTime = Date.now();
            }
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
        
        // CRITICAL FIX: Paraphernalia products should ALWAYS get PARAPHERNALIA lineage (pink color)
        // Check if product type is "paraphernalia" - this takes priority over everything else
        if (productType === 'paraphernalia') {
            console.log(`🎯 Paraphernalia product detected: "${productType}" → PARAPHERNALIA (pink)`);
            return 'PARAPHERNALIA';
        }
        
        // CRITICAL FIX: High CBD products should ALWAYS get CBD_BLEND lineage
        // Check if product type starts with "high cbd" - this takes priority over everything else
        if (productType.startsWith('high cbd')) {
            console.log(`🎯 High CBD product detected: "${productType}" → CBD_BLEND`);
            return 'CBD_BLEND';
        }
        
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
            // Also check product type as fallback
            else if (strainLower.includes('paraphernalia') || productType === 'paraphernalia') {
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
        
        // Save state for undo BEFORE making changes
        this.saveSelectionState('move_to_selected');
        
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
        
        // Save state for undo BEFORE making changes
        this.saveSelectionState('move_to_available');
        
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
            console.log('🔙 Undoing most recent checkbox selection...');

            // Check if there's anything to undo
            if (!this.state.localUndoStack || this.state.localUndoStack.length === 0) {
                if (window.Toast) {
                    Toast.show('info', 'Nothing to undo');
                }
                return;
            }

            // Show user feedback immediately
            if (window.Toast) {
                Toast.show('info', 'Undoing last selection batch...');
            }

            // Capture current state for redo
            const captureCurrentState = () => ({
                selected_tag_names: [...(this.state.persistentSelectedTags || [])],
                available_tag_names: (this.state.tags || [])
                    .filter(tag => tag && !this.state.persistentSelectedTags.includes(tag['Product Name*']))
                    .map(tag => tag['Product Name*']),
                action_type: 'undo_capture',
                timestamp: new Date().toISOString()
            });

            if (!this.state.redoSnapshotStack) {
                this.state.redoSnapshotStack = [];
            }
            this.state.redoSnapshotStack.push(captureCurrentState());
            if (this.state.redoSnapshotStack.length > 5) {
                this.state.redoSnapshotStack = this.state.redoSnapshotStack.slice(-5);
            }

            // Restore the last saved snapshot
            const lastSnapshot = this.state.localUndoStack.pop();
            const selectedNames = lastSnapshot.selected_tag_names || [];

            this.state.persistentSelectedTags = [...selectedNames];
            this.state.selectedTags = new Set(selectedNames);

            const selectedTagObjects = selectedNames.map(tagName =>
                this.state.tags.find(t => t['Product Name*'] === tagName)
            ).filter(Boolean);
            this.updateSelectedTags(selectedTagObjects);
            this._restoreCheckboxStates();
            this.updateSelectAllCheckboxes();

            if (window.Toast) {
                Toast.show('success', `Undo: restored ${selectedNames.length} selection(s)`);
            }

            verboseLog(`✅ Undo applied - restored ${selectedNames.length} selections`);

        } catch (error) {
            console.error('Failed to undo:', error.message);
            if (window.Toast) {
                Toast.show('error', `Undo failed: ${error.message}`);
            } else {
                alert(`Undo failed: ${error.message}`);
            }
        }
    },

    async redoMove() {
        try {
            console.log('🔁 Redoing most recent undo...');

            // Check if there's anything to redo
            if (!this.state.redoSnapshotStack || this.state.redoSnapshotStack.length === 0) {
                if (window.Toast) {
                    Toast.show('info', 'Nothing to redo');
                }
                return;
            }

            // Show user feedback immediately
            if (window.Toast) {
                Toast.show('info', 'Redoing last batch...');
            }

            // Capture current state for future undo
            const captureCurrentState = () => ({
                selected_tag_names: [...(this.state.persistentSelectedTags || [])],
                available_tag_names: (this.state.tags || [])
                    .filter(tag => tag && !this.state.persistentSelectedTags.includes(tag['Product Name*']))
                    .map(tag => tag['Product Name*']),
                action_type: 'redo_capture',
                timestamp: new Date().toISOString()
            });

            const snapshotToRestore = this.state.redoSnapshotStack.pop();
            if (!this.state.localUndoStack) {
                this.state.localUndoStack = [];
            }
            this.state.localUndoStack.push(captureCurrentState());
            if (this.state.localUndoStack.length > 5) {
                this.state.localUndoStack = this.state.localUndoStack.slice(-5);
            }

            const selectedNames = snapshotToRestore.selected_tag_names || [];
            this.state.persistentSelectedTags = [...selectedNames];
            this.state.selectedTags = new Set(selectedNames);

            const selectedTagObjects = selectedNames.map(tagName =>
                this.state.tags.find(t => t['Product Name*'] === tagName)
            ).filter(Boolean);
            this.updateSelectedTags(selectedTagObjects);
            this._restoreCheckboxStates();
            this.updateSelectAllCheckboxes();

            if (window.Toast) {
                Toast.show('success', `Redo: restored ${selectedNames.length} selection(s)`);
            }

            verboseLog(`✅ Redo applied - restored ${selectedNames.length} selections`);

        } catch (error) {
            console.error('Failed to redo:', error.message);
            if (window.Toast) {
                Toast.show('error', `Redo failed: ${error.message}`);
            } else {
                alert(`Redo failed: ${error.message}`);
            }
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
        
        // CRITICAL FIX: Get button references before try block so they're accessible in catch
        const clearBtn = document.getElementById('clearFiltersBtn');
        const clearResetBtn = document.querySelector('button[onclick*="clearSelected"]');
        
        // CRITICAL FIX: Disable clear button immediately to prevent multiple clicks
        if (clearBtn) {
            clearBtn.disabled = true;
            clearBtn.style.opacity = '0.6';
            clearBtn.style.cursor = 'wait';
        }
        if (clearResetBtn) {
            clearResetBtn.disabled = true;
            clearResetBtn.style.opacity = '0.6';
            clearResetBtn.style.cursor = 'wait';
        }
        
        // CRITICAL FIX: Set timeout to ensure flag is always reset (prevent freeze)
        const clearingTimeout = setTimeout(() => {
            if (this.state.isClearing) {
                console.warn('⚠️ Clear operation took too long, forcing reset of isClearing flag');
                this.state.isClearing = false;
                // Re-enable buttons
                if (clearBtn) {
                    clearBtn.disabled = false;
                    clearBtn.style.opacity = '1';
                    clearBtn.style.cursor = 'pointer';
                }
                if (clearResetBtn) {
                    clearResetBtn.disabled = false;
                    clearResetBtn.style.opacity = '1';
                    clearResetBtn.style.cursor = 'pointer';
                }
            }
        }, 10000); // 10 second timeout
        
        try {
            verboseLog('🔄 Clearing selected tags and performing full app reset...');
            
            // INSTANTANEOUS: Update UI state immediately (synchronously)
            // Clear persistent selected tags
            if (this.state) {
                if (Array.isArray(this.state.persistentSelectedTags)) {
                    this.state.persistentSelectedTags = [];
                }
                if (this.state.selectedTags && typeof this.state.selectedTags.clear === 'function') {
                    this.state.selectedTags.clear();
                }
                this.state.filterCache = null;
            }
            
            // INSTANTANEOUS: Clear all checkboxes immediately (no batching)
            try {
                const availableCheckboxes = document.querySelectorAll('#availableTags input[type="checkbox"]');
                for (let i = 0; i < availableCheckboxes.length; i++) {
                    availableCheckboxes[i].checked = false;
                }
                
                const selectedCheckboxes = document.querySelectorAll('#selectedTags input[type="checkbox"]');
                for (let i = 0; i < selectedCheckboxes.length; i++) {
                    selectedCheckboxes[i].checked = false;
                }
            } catch (checkboxError) {
                console.error('Error clearing checkboxes:', checkboxError);
            }
            
            // INSTANTANEOUS: Clear search inputs
            this.resetSearchInputs();
            
            // INSTANTANEOUS: Clear all filter dropdowns
            const filterIds = ['vendorFilter', 'brandFilter', 'productTypeFilter', 'lineageFilter', 'weightFilter', 'dohFilter', 'highCbdFilter'];
            filterIds.forEach(filterId => {
                const filterElement = document.getElementById(filterId);
                if (filterElement) {
                    filterElement.value = '';
                }
            });
            
            // INSTANTANEOUS: Reset template to horizontal
            const templateSelect = document.getElementById('templateSelect');
            if (templateSelect) {
                templateSelect.value = 'horizontal';
            }
            
            // INSTANTANEOUS: Update selected tags display immediately
            if (this.updateSelectedTags) {
                try {
                    this.updateSelectedTags([]);
                } catch (updateError) {
                    console.error('Error updating selected tags display:', updateError);
                }
            }
            
            // INSTANTANEOUS: Show all available tags immediately
            try {
                const availableTagItems = document.querySelectorAll('#availableTags .tag-item');
                for (let i = 0; i < availableTagItems.length; i++) {
                    availableTagItems[i].style.display = 'block';
                }
            } catch (displayError) {
                console.error('Error showing available tags:', displayError);
            }
            
            // INSTANTANEOUS: Update select all checkboxes
            if (this.updateSelectAllCheckboxes) {
                try {
                    this.updateSelectAllCheckboxes();
                } catch (updateError) {
                    console.error('Error updating select all checkboxes:', updateError);
                }
            }
            
            // INSTANTANEOUS: Apply filters to show all tags
            if (this.applyFilters) {
                this.applyFilters();
            }
            
            // INSTANTANEOUS: Render active filters (should be empty now)
            if (this.renderActiveFilters) {
                this.renderActiveFilters();
            }
            
            // INSTANTANEOUS: Update available tags display
            if (this.efficientlyUpdateAvailableTagsDisplay) {
                try {
                    this.efficientlyUpdateAvailableTagsDisplay();
                } catch (updateError) {
                    console.error('Error updating available tags display:', updateError);
                }
            }
            
            // Reset the clearing flag immediately
            clearTimeout(clearingTimeout);
            this.state.isClearing = false;
            
            // CRITICAL FIX: Re-enable clear button
            if (clearBtn) {
                clearBtn.disabled = false;
                clearBtn.style.opacity = '1';
                clearBtn.style.cursor = 'pointer';
            }
            if (clearResetBtn) {
                clearResetBtn.disabled = false;
                clearResetBtn.style.opacity = '1';
                clearResetBtn.style.cursor = 'pointer';
            }
            
            verboseLog('✅ Selected tags cleared and app reset completed successfully');
            
            // Show success message (non-blocking)
            if (window.Toast && window.Toast.show) {
                window.Toast.show('success', 'Cleared and reset successfully', { duration: 2000 });
            }
            
            // CRITICAL FIX: Add timeout to fetch operations to prevent hanging
            const fetchWithTimeout = (url, options, timeout = 5000) => {
                return Promise.race([
                    fetch(url, options),
                    new Promise((_, reject) => 
                        setTimeout(() => reject(new Error('Request timeout')), timeout)
                    )
                ]);
            };
            
            // NON-BLOCKING: Clear JSON matches and switch to full Excel view with timeout
            // CRITICAL FIX: Wait for any in-progress fetch to complete before starting new one
            const refreshTagsAfterClear = async () => {
                // Wait for any in-progress fetch to complete (max 3 seconds)
                let waitCount = 0;
                while (this._fetchingAvailableTags && waitCount < 30) {
                    await new Promise(resolve => setTimeout(resolve, 100));
                    waitCount++;
                }
                
                // Now refresh tags
                verboseLog('Refreshing available tags with full Excel data...');
                if (this.fetchAndUpdateAvailableTags) {
                    try {
                        await this.fetchAndUpdateAvailableTags();
                    } catch (fetchError) {
                        console.error('Error refreshing available tags:', fetchError);
                        this.state.isClearing = false; // Ensure flag is reset
                    }
                }
            };
            
            fetchWithTimeout('/api/json-clear', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            }, 5000).then(() => {
                // Then switch to full Excel view
                return fetchWithTimeout('/api/toggle-json-filter', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filter_mode: 'full_excel' })
                }, 5000);
            }).then(response => {
                if (response && response.ok) {
                    return response.json();
                }
                return null;
            }).then(data => {
                // Always refresh available tags after clearing JSON matches and switching to full Excel
                refreshTagsAfterClear();
            }).catch(fetchError => {
                // Silently handle errors - UI is already updated, but still try to refresh tags
                verboseLog('Backend JSON clear/toggle call failed (non-critical):', fetchError);
                // Still refresh tags to ensure we show full Excel data
                refreshTagsAfterClear();
            });
            
            // NON-BLOCKING: Fire-and-forget backend API call for clearing filters (don't wait for it)
            fetchWithTimeout('/api/clear-filters', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            }, 5000).catch(fetchError => {
                // Silently handle errors - UI is already updated
                verboseLog('Backend clear-filters call failed (non-critical):', fetchError);
            });
            
        } catch (error) {
            console.error('Failed to clear selected tags:', error);
            // CRITICAL FIX: Always reset the clearing flag and clear timeout
            clearTimeout(clearingTimeout);
            this.state.isClearing = false;
            
            // CRITICAL FIX: Re-enable clear button even on error (buttons already declared above)
            if (clearBtn) {
                clearBtn.disabled = false;
                clearBtn.style.opacity = '1';
                clearBtn.style.cursor = 'pointer';
            }
            if (clearResetBtn) {
                clearResetBtn.disabled = false;
                clearResetBtn.style.opacity = '1';
                clearResetBtn.style.cursor = 'pointer';
            }
            
            // Show error message (non-blocking)
            if (window.Toast && window.Toast.show) {
                window.Toast.show('error', `Failed to clear: ${error.message}`, { duration: 5000 });
            } else {
                alert(`Failed to clear and reset: ${error.message}`);
            }
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
            
            // CRITICAL FIX: Add safety timeout to auto-hide splash after 30 seconds
            // This prevents the modal from getting stuck if something goes wrong
            if (this._splashTimeout) {
                clearTimeout(this._splashTimeout);
            }
            this._splashTimeout = setTimeout(() => {
                console.warn('⚠️ Safety timeout: Auto-hiding splash after 30 seconds');
                this.hideExcelLoadingSplash();
            }, 30000); // 30 second safety timeout
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
        
        // Clear safety timeout if it exists
        if (this._splashTimeout) {
            clearTimeout(this._splashTimeout);
            this._splashTimeout = null;
        }
        
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
                    from { transform: rotate(0deg); }
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
        // PERFORMANCE: Batch operation only - not called on single checkbox changes
        // CRITICAL: First sync all available tag checkboxes with persistentSelectedTags state
        const availableCheckboxes = document.querySelectorAll('#availableTags .tag-checkbox');
        availableCheckboxes.forEach(checkbox => {
            const tagName = checkbox.value;
            const shouldBeChecked = this.state.persistentSelectedTags.includes(tagName);
            if (checkbox.checked !== shouldBeChecked) {
                checkbox.checked = shouldBeChecked;
            }
        });
        
        // CRITICAL FIX: Also sync selected tag checkboxes with persistentSelectedTags state
        // This prevents selected tags from being unchecked when available tags are re-rendered
        const selectedCheckboxes = document.querySelectorAll('#selectedTags .tag-checkbox');
        selectedCheckboxes.forEach(checkbox => {
            const tagName = checkbox.value;
            const shouldBeChecked = this.state.persistentSelectedTags.includes(tagName);
            if (checkbox.checked !== shouldBeChecked) {
                checkbox.checked = shouldBeChecked;
                verboseLog(`Synced selected tag checkbox for "${tagName}": ${shouldBeChecked}`);
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
        
        // Update selected tags select all checkbox (reuse selectedCheckboxes from above)
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
        // CRITICAL FIX: Prevent concurrent uploads
        if (this._uploadInProgress) {
            console.warn('⚠️ Upload already in progress, ignoring duplicate request');
            return;
        }

        this._uploadInProgress = true;
        
        // CRITICAL FIX: Create upload-specific abort controller to prevent global one from interfering
        const uploadAbortController = new AbortController();
        this._uploadAbortController = uploadAbortController;

        // CRITICAL FIX: Disable upload button and file input during upload
        const uploadBtn = document.getElementById('uploadTriggerBtn');
        const fileInput = document.getElementById('fileInput');
        if (uploadBtn) uploadBtn.disabled = true;
        if (fileInput) fileInput.disabled = true;

        try {
            verboseLog(`🚀 Starting LIGHTNING upload:`, file.name, 'Size:', file.size, 'bytes');

            // CRITICAL: Check store selection before attempting upload
            try {
                const storeCheckResponse = await fetch('/api/check-store-required');
                const storeCheckData = await storeCheckResponse.json();
                if (storeCheckData.required && !storeCheckData.has_store) {
                    const errorMsg = 'Please select a store before uploading files. Click on the store name in the header to select a store.';
                    console.error('Upload blocked:', errorMsg);
                    this.updateUploadUI(errorMsg, 'error');
                    if (typeof showToast === 'function') {
                        showToast('error', errorMsg);
                    } else {
                        alert(errorMsg);
                    }
                    this.hideExcelLoadingSplash();
                    return;
                }
            } catch (storeCheckError) {
                console.warn('Could not verify store selection, proceeding with upload:', storeCheckError);
                // Continue with upload - backend will handle validation
            }
            
            // CRITICAL: Clear cache but PRESERVE selected tags during upload
            this._lastUploadTime = Date.now();
            this.state.hydratedFromCache = false; // Force fresh data load
            
            // CRITICAL: Save selected tags before clearing cache
            const savedSelectedTags = [...(this.state.persistentSelectedTags || [])];
            verboseLog('💾 Preserving selected tags before upload:', savedSelectedTags);
            
            this.state.tags = []; // Clear in-memory tags
            this.state.originalTags = []; // Clear original tags
            
            // Clear localStorage cache but preserve selected tags
            try {
                // Save selected tags to temp variable
                const selectedTagsBackup = localStorage.getItem('selectedTags');
                
                localStorage.removeItem('tagManagerState');
                localStorage.removeItem('availableTagsCache');
                
                // Restore selected tags
                if (selectedTagsBackup) {
                    localStorage.setItem('selectedTags', selectedTagsBackup);
                }
                
                verboseLog('🔄 Cleared localStorage cache (preserved selected tags)');
            } catch (e) {
                verboseLog('⚠️ Could not clear localStorage:', e);
            }
            
            // Restore selected tags to state
            this.state.persistentSelectedTags = savedSelectedTags;
            this.state.selectedTags = new Set(savedSelectedTags);
            
            verboseLog('🔄 Cache cleared for upload - selected tags preserved');
            
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
            
            // Parse response - handle both success and error responses
            let uploadData;
            try {
                uploadData = await uploadResponse.json();
            } catch (parseError) {
                console.error('Failed to parse upload response:', parseError);
                throw new Error(`Upload failed: Server returned invalid response (${uploadResponse.status})`);
            }
            
            verboseLog('⚡ Lightning upload response:', uploadData);
            
            if (!uploadResponse.ok) {
                const errorMsg = uploadData.error || uploadData.message || `Upload failed (${uploadResponse.status})`;
                console.error('Upload failed:', errorMsg);
                throw new Error(errorMsg);
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

            // Safety timeout: Auto-hide splash after 30s in case something goes wrong
            const splashTimeout = setTimeout(() => {
                verboseLog('⚠️ Safety timeout: Force hiding action splash after 30s');
                if (this.hideActionSplash) {
                    this.hideActionSplash();
                }
            }, 30000);

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

            // NEW: Immediately kick off lite tag prefetch so something appears quickly,
            // even if the full /api/available-tags call is still processing the upload.
            if (typeof this._prefetchLiteAvailableTags === 'function') {
                try {
                    const savedScroll = this._saveAvailableScrollPosition
                        ? this._saveAvailableScrollPosition()
                        : null;
                    this._prefetchLiteAvailableTags(savedScroll).catch(err => {
                        verboseLog('Lite prefetch after upload failed (non-critical):', err);
                    });
                } catch (e) {
                    verboseLog('Lite prefetch after upload threw (non-critical):', e);
                }
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
            // Try a fast path, then fall back to the standard loader quickly if it lags
            let tagsLoaded = false;
            const maxRetries = 2;  // Keep one retry for transient failures
            const fastLoadTimeoutMs = 90000; // Allow slower backend without multiple timeouts
            let standardFetchStarted = false;

            const startStandardTagFetch = async () => {
                if (tagsLoaded || standardFetchStarted) return;
                standardFetchStarted = true;
                verboseLog('🔄 Switching to standard tag fetch fallback...');
                try {
                    await this.fetchAndUpdateAvailableTags();
                    tagsLoaded = true;
                    verboseLog('✅ Tags loaded via standard fallback');
                } catch (fallbackError) {
                    console.error('⚠️ Standard tag loading via fallback failed:', fallbackError);
                }
            };

            for (let attempt = 0; attempt < maxRetries; attempt++) {
                let tagsTimeout = null;
                let tagsController = null;
                try {
                    // PERFORMANCE: No delays - try immediately for maximum speed
                    // Retries happen instantly without waiting
                    
                    // CRITICAL FIX: Clean up any previous controller before creating new one
                    if (tagsController) {
                        try {
                            tagsController.abort();
                        } catch (e) {
                            // Ignore errors from aborting already-aborted controller
                        }
                    }
                    
                    tagsController = new AbortController();
                    // PERFORMANCE: Longer timeout for PythonAnywhere (network latency + processing time)
                    tagsTimeout = setTimeout(() => {
                        if (tagsController && !tagsController.signal.aborted) {
                            tagsController.abort(new DOMException('Request timeout after 90s', 'TimeoutError'));
                        }
                    }, fastLoadTimeoutMs);

                    // Use fast_load=1 for instant response, nocache=1 to ensure fresh data from new upload
                    let tagsResponse;
                    try {
                        tagsResponse = await fetch(`/api/available-tags?t=${Date.now()}&nocache=1&fast_load=1`, {
                            signal: tagsController.signal
                        });
                    } catch (fetchError) {
                        // CRITICAL FIX: Only log if it's not an expected abort
                        if (fetchError.name !== 'AbortError' || attempt === maxRetries - 1) {
                            console.error(`⚠️ Tag fetch failed (attempt ${attempt + 1}/${maxRetries}):`, fetchError);
                        }
                        if (tagsTimeout) {
                            clearTimeout(tagsTimeout);
                            tagsTimeout = null;
                        }
                        if (tagsController) {
                            tagsController = null;
                        }
                        if (attempt < maxRetries - 1) {
                            continue; // Retry
                        }
                        throw fetchError; // Last attempt failed
                    }
                    if (tagsTimeout) {
                        clearTimeout(tagsTimeout);
                        tagsTimeout = null;
                    }
                    
                    if (tagsResponse.ok) {
                        const tagsData = await tagsResponse.json();
                        if (tagsData.tags && tagsData.tags.length > 0) {
                            verboseLog(`✅ Loaded ${tagsData.tags.length} tags instantly after upload (attempt ${attempt + 1})`);

                            // Update tags immediately
                            this.state.tags = [...tagsData.tags];
                            this.state.originalTags = [...tagsData.tags];
                            this._updateAvailableTags(tagsData.tags);

                            // CRITICAL: Extract and populate filters from tags data immediately
                            // This ensures filters appear instantly without waiting for separate API call
                            if (tagsData.tags && tagsData.tags.length > 0) {
                                const extractedFilters = this._extractFiltersFromTags(tagsData.tags);
                                this.updateFilters(extractedFilters);
                                verboseLog('✅ Filters extracted from tags immediately:', extractedFilters);
                                
                                // CRITICAL FIX: Ensure filter row container is visible
                                const filterRow = document.querySelector('.filter-row');
                                if (filterRow) {
                                    filterRow.style.display = 'flex';
                                    filterRow.style.visibility = 'visible';
                                    verboseLog('✅ Filter row container made visible');
                                }
                                
                                // CRITICAL FIX: Ensure filters are rendered after upload
                                if (this.renderActiveFilters) {
                                    this.renderActiveFilters();
                                    verboseLog('✅ Filters rendered after upload');
                                }
                            }

                            // Load filters and selected tags in parallel (non-blocking) to refresh with full options
                            Promise.allSettled([
                                this.fetchAndPopulateFilters(),
                                this.fetchAndUpdateSelectedTags()
                            ]).then(() => {
                                verboseLog('✅ Filters and selected tags refreshed');
                                
                                // CRITICAL FIX: Ensure filters are rendered after they're populated
                                if (this.renderActiveFilters) {
                                    this.renderActiveFilters();
                                    verboseLog('✅ Filters rendered after population');
                                }
                            }).catch(err => {
                                console.warn('Filter/selected tag loading failed (non-critical):', err);
                                
                                // CRITICAL FIX: Ensure filter row container is visible even on error
                                const filterRow = document.querySelector('.filter-row');
                                if (filterRow) {
                                    filterRow.style.display = 'flex';
                                    filterRow.style.visibility = 'visible';
                                    verboseLog('✅ Filter row container made visible after error');
                                }
                                
                                // CRITICAL FIX: Still render filters even if population failed
                                if (this.renderActiveFilters) {
                                    this.renderActiveFilters();
                                    verboseLog('✅ Filters rendered after population error');
                                }
                            });
                            
                            // Clear safety timeout since we're about to hide splash
                            if (splashTimeout) {
                                clearTimeout(splashTimeout);
                            }

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
                            // Update upload UI to show completion
                            // Update file info text to show completion
                            const fileInfoElement = document.getElementById('fileInfoText');
                            if (fileInfoElement) {
                                const fileName = sessionStorage.getItem('uploaded_filename') || 'File';
                                fileInfoElement.textContent = `✅ ${fileName} ready!`;
                            }
                            return; // Success - tags loaded instantly!
                        } else {
                            verboseLog('ℹ️ Fast load returned no tags yet - falling back to standard fetch');
                            if (tagsTimeout) {
                                clearTimeout(tagsTimeout);
                                tagsTimeout = null;
                            }
                            await startStandardTagFetch();
                            return;
                        }
                    }
                } catch (tagsError) {
                    // CRITICAL FIX: Always clear timeout and abort controller on error
                    if (tagsTimeout) {
                        clearTimeout(tagsTimeout);
                        tagsTimeout = null;
                    }
                    if (tagsController) {
                        try {
                            if (!tagsController.signal.aborted) {
                                tagsController.abort();
                            }
                        } catch (e) {
                            // Ignore errors from aborting
                        }
                        tagsController = null;
                    }

                    // Silently handle errors - retry without showing notifications (splash is still visible)
                    const isTimeout = tagsError.name === 'AbortError' || tagsError.message?.includes('aborted');
                    
                    // If timeout/abort or we're on the last attempt, jump to the robust standard fetch
                    if (isTimeout || attempt === maxRetries - 1) {
                        console.warn(`⚠️ Fast tag load failed (attempt ${attempt + 1}) - starting standard fetch`, tagsError);
                        if (splashTimeout) {
                            clearTimeout(splashTimeout);
                        }
                        await startStandardTagFetch();
                        return;
                    }

                    // Otherwise retry the fast path once more
                    verboseLog(`⚠️ Attempt ${attempt + 1} failed, retrying fast path...`);
                }
            }
            
            // If we get here, tags didn't load after all retries - try standard method instead of reloading
            if (!tagsLoaded) {
                console.warn('⚠️ Tags not loaded after retries, trying standard method...');

                // Clear safety timeout
                if (splashTimeout) {
                    clearTimeout(splashTimeout);
                }

                // CRITICAL: Hide splash before trying fallback
                if (this.hideActionSplash) {
                    this.hideActionSplash();
                }

                // CRITICAL FIX: Reset fetching flag to allow fallback to proceed
                this._fetchingAvailableTags = false;
                try {
                    await this.fetchAndUpdateAvailableTags();
                    tagsLoaded = true;
                    verboseLog('✅ Tags loaded using standard method');
                } catch (fallbackError) {
                    console.error('⚠️ Standard tag loading failed:', fallbackError);
                    // Show error without reloading - let user decide to manually refresh
                    this.updateUploadUI('Could not load tags. Please refresh the page to try again.', 'error');
                    if (typeof showToast === 'function') {
                        showToast('error', 'Tag loading failed. Please refresh the page manually.');
                    }
                }
            }
            
            return; // Success!
        } catch (error) {
            console.error('⚡ Lightning upload error:', error);
            // CRITICAL: Always hide splash on error
            this.hideExcelLoadingSplash();
            // Also hide action splash if it's showing
            if (this.hideActionSplash) {
                this.hideActionSplash();
            }

            // CRITICAL: Also hide action splash if it's showing
            if (this.hideActionSplash) {
                this.hideActionSplash();
            }

            // Check for SSL/TLS errors
            let errorMessage = error.message;
            if (error.message && (
                error.message.includes('SSL') || 
                error.message.includes('TLS') || 
                error.message.includes('ERR_SSL') ||
                error.message.includes('BAD_RECORD_MAC')
            )) {
                errorMessage = 'SSL connection error. Please check your internet connection and try again. If the problem persists, contact support.';
            }
            
            const fullErrorMessage = 'Upload failed: ' + errorMessage;
            console.error('Upload error:', fullErrorMessage);
            this.updateUploadUI(fullErrorMessage, 'error');
            
            // Also show toast notification for better visibility
            if (typeof showToast === 'function') {
                showToast('error', fullErrorMessage);
            } else {
                // Fallback to alert if toast is not available
                alert(fullErrorMessage);
            }
            return;
        } finally {
            // CRITICAL FIX: Always clear upload flag and re-enable controls
            this._uploadInProgress = false;
            // Clean up upload-specific abort controller
            if (this._uploadAbortController) {
                this._uploadAbortController = null;
            }
            const uploadBtn = document.getElementById('uploadTriggerBtn');
            const fileInput = document.getElementById('fileInput');
            if (uploadBtn) uploadBtn.disabled = false;
            if (fileInput) fileInput.disabled = false;
        }
    },
    // Fallback upload method for PythonAnywhere
    async uploadFileFallback(file) {
        try {
            verboseLog('Using fallback upload method for:', file.name);
            
            // CRITICAL: Clear cache but PRESERVE selected tags during upload
            this._lastUploadTime = Date.now();
            this.state.hydratedFromCache = false; // Force fresh data load
            
            // CRITICAL: Save selected tags before clearing cache
            const savedSelectedTags = [...(this.state.persistentSelectedTags || [])];
            verboseLog('💾 Preserving selected tags before fallback upload:', savedSelectedTags);
            
            this.state.tags = []; // Clear in-memory tags
            this.state.originalTags = []; // Clear original tags
            
            // Clear localStorage cache but preserve selected tags
            try {
                // Save selected tags to temp variable
                const selectedTagsBackup = localStorage.getItem('selectedTags');
                
                localStorage.removeItem('tagManagerState');
                localStorage.removeItem('availableTagsCache');
                
                // Restore selected tags
                if (selectedTagsBackup) {
                    localStorage.setItem('selectedTags', selectedTagsBackup);
                }
                
                verboseLog('🔄 Cleared localStorage cache (preserved selected tags)');
            } catch (e) {
                verboseLog('⚠️ Could not clear localStorage:', e);
            }
            
            // Restore selected tags to state
            this.state.persistentSelectedTags = savedSelectedTags;
            this.state.selectedTags = new Set(savedSelectedTags);
            
            verboseLog('🔄 Cache cleared for fallback upload - selected tags preserved');
            
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
                safeReload(500); // Small delay to ensure UI updates
                return true;
            } else {
                console.error('Fallback upload failed:', data.error);
                this.updateUploadUI('Upload failed: ' + (data.error || 'Unknown error'), 'error');
                return false;
            }
        } catch (error) {
            console.error('Fallback upload error:', error);
            
            // Check for SSL/TLS errors
            let errorMessage = error.message;
            if (error.message && (
                error.message.includes('SSL') || 
                error.message.includes('TLS') || 
                error.message.includes('ERR_SSL') ||
                error.message.includes('BAD_RECORD_MAC')
            )) {
                errorMessage = 'SSL connection error. Please check your internet connection and try again. If the problem persists, contact support.';
            }
            
            this.updateUploadUI('Upload failed: ' + errorMessage, 'error');
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

                    // CRITICAL FIX: Clear splash timeout on success
                    if (window._splashTimeoutId) {
                        clearTimeout(window._splashTimeoutId);
                        window._splashTimeoutId = null;
                        verboseLog('[UPLOAD DEBUG] Cleared splash timeout');
                    }

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

                    // CRITICAL FIX: Clear splash timeout on error
                    if (window._splashTimeoutId) {
                        clearTimeout(window._splashTimeoutId);
                        window._splashTimeoutId = null;
                    }

                    if (confirm('Upload failed due to network error. Would you like to reload and try again?')) {
                        window.location.reload();
                    }
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
        
        // Timeout - try one last recovery attempt
        console.error('⚠️ Upload polling timed out - attempting final recovery');
        this.updateExcelLoadingStatus('Timeout - attempting recovery...');

        try {
            // Final attempt to load data directly
            verboseLog('[UPLOAD DEBUG] Final recovery attempt - loading data directly');
            await fetch('/api/clear-cache', { method: 'POST' }).catch(() => {});
            this._forceDatabaseLineage = true;
            const loaded = await this.fetchAndUpdateAvailableTags();
            this._forceDatabaseLineage = false;

            if (loaded && this.state.tags && this.state.tags.length > 0) {
                verboseLog('[UPLOAD DEBUG] Recovery successful - data found');
                this.hideExcelLoadingSplash();
                this.updateUploadUI(filename, 'Upload recovered successfully', 'success');

                // CRITICAL FIX: Load filters and selected tags in parallel for faster recovery
                try {
                    await Promise.all([
                        this.fetchAndPopulateFilters(),
                        this.fetchAndUpdateSelectedTags()
                    ]);
                    verboseLog('[UPLOAD DEBUG] Filters and selected tags loaded after recovery');
                } catch (loadErr) {
                    console.warn('⚠️ Could not load filters/selected tags after recovery:', loadErr);
                }

                alert('Upload completed successfully after recovery.');
                return;
            }
        } catch (recoveryError) {
            console.error('[UPLOAD DEBUG] Final recovery failed:', recoveryError);
        }

        // If recovery failed, show error and offer reload
        this.hideExcelLoadingSplash();
        this.updateUploadUI('Upload timed out', 'Processing took too long', 'error');
        console.error('Upload timed out. Please try again.');

        // CRITICAL FIX: Clear splash timeout on final timeout
        if (window._splashTimeoutId) {
            clearTimeout(window._splashTimeoutId);
            window._splashTimeoutId = null;
        }

        if (confirm('Upload timed out. Would you like to reload the page and try again?')) {
            window.location.reload();
        }
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
        
        // Store reference to this for use in closures
        const self = this;
        
        // Ultra-fast debounced filter update (Mac-like speed)
        // Immediate filter update function (no debounce for instant response)
        const immediateFilterUpdate = async (filterType, value) => {
            verboseLog(`🔥 immediateFilterUpdate called for ${filterType}: ${value}`);
            
            // CRITICAL FIX: Don't update filters during deselection
            if (self.state.isProcessingDeselection) {
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
                self.state.filters[stateKey] = value || 'All';
            }
            
            // GUARANTEED FIX: Save filters to localStorage when they change
            self.saveFiltersToStorage();
            
            // Apply filters immediately with immediate UI update (bypass debounce)
            // Cancel any pending debounced updates to prevent delays
            if (self.debouncedUpdateAvailableTags && self.debouncedUpdateAvailableTags.cancel) {
                self.debouncedUpdateAvailableTags.cancel();
            }
            
            // Call applyFilters with immediate flag to skip debounce
            if (self.applyFilters) {
                try {
                    self.applyFilters(true); // Pass true to indicate immediate update
                } catch (filterError) {
                    console.error('Error applying filters:', filterError);
                    // Retry after a short delay if filters fail (might be timing issue)
                    setTimeout(() => {
                        if (self.applyFilters && (self.state.originalTags.length > 0 || self.state.tags.length > 0)) {
                            console.log('Retrying filter application after error...');
                            self.applyFilters(true);
                        }
                    }, 100);
                }
            } else {
                console.error('applyFilters method not found on TagManager');
            }
            
            // Update filter options asynchronously (non-blocking) after UI update
            Promise.resolve().then(async () => {
                if (!isWindows) {
                    // Mac: Update filter options and render active filters
                    if (self.updateFilterOptions) {
                        await self.updateFilterOptions();
                    }
                    if (self.renderActiveFilters) {
                        self.renderActiveFilters();
                    }
                } else {
                    // Windows: Just update filter options (skip renderActiveFilters for speed)
                    if (self.updateFilterOptions) {
                        await self.updateFilterOptions();
                    }
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
                            if (self.bulkUpdateDohForSelected) {
                                await self.bulkUpdateDohForSelected('NONE');
                            }
                        } else if (dohValueUpper === 'DOH' || dohValueUpper === 'THC' || dohValueUpper === 'CBD') {
                            if (self.bulkUpdateDohForSelected) {
                                await self.bulkUpdateDohForSelected(dohValueUpper);
                            }
                        }
                    } catch (bulkErr) {
                        console.warn('Bulk DOH update from filter failed:', bulkErr);
                    }
                });
            }

            verboseLog(`🔥 immediateFilterUpdate completed for ${filterType}`);
        };
        
        let foundCount = 0;
        let missingFilters = [];
        
        filterIds.forEach(filterId => {
            const filterElement = document.getElementById(filterId);
            
            if (filterElement) {
                foundCount++;
                // Remove all existing listeners for clean slate
                if (filterElement._filterChangeHandler) {
                    filterElement.removeEventListener('change', filterElement._filterChangeHandler);
                }
                if (filterElement._filterInputHandler) {
                    filterElement.removeEventListener('input', filterElement._filterInputHandler);
                }
                if (filterElement._filterClickHandler) {
                    filterElement.removeEventListener('click', filterElement._filterClickHandler);
                }
                
                // PERFORMANCE FIX: Add throttling to filter handlers to prevent excessive updates
                if (!self._filterThrottleTimers) {
                    self._filterThrottleTimers = {};
                }
                
                // Single, fast event handler with throttling for better performance
                filterElement._filterChangeHandler = (event) => {
                    try {
                        verboseLog(`🔥 FILTER CHANGED: ${filterId} = "${event.target.value}"`);
                        const filterType = self.getFilterTypeFromId(filterId);
                        const value = event.target.value;
                        
                        // Clear existing throttle timer for this filter
                        if (self._filterThrottleTimers[filterId]) {
                            clearTimeout(self._filterThrottleTimers[filterId]);
                        }
                        
                        // Throttle filter updates (150ms delay for smoother performance)
                        self._filterThrottleTimers[filterId] = setTimeout(() => {
                            // Special handling for vendor filter
                            if (filterId === 'vendorFilter' && value && value.trim() !== '' && value.toLowerCase() !== 'all') {
                                if (self.resetAllOtherFilters) {
                                    self.resetAllOtherFilters();
                                }
                            }
                            
                            // Filter update with requestAnimationFrame for smoother rendering
                            requestAnimationFrame(() => {
                                verboseLog(`🔥 Calling immediateFilterUpdate for ${filterType}: ${value}`);
                                immediateFilterUpdate(filterType, value);
                            });
                        }, 150); // 150ms throttle delay
                    } catch (error) {
                        console.error(`Error in filter change handler for ${filterId}:`, error);
                    }
                };
                
                // Only use change event for Mac-like behavior
                filterElement.addEventListener('change', filterElement._filterChangeHandler);
                
                verboseLog(`✅ Fast event listener attached to ${filterId}`);
            } else {
                missingFilters.push(filterId);
                console.warn(`⚠️ Filter element not found: ${filterId}`);
            }
        });
        
        if (foundCount === 0) {
            console.error('❌ No filter elements found! Filters will not work. Retrying in 500ms...');
            setTimeout(() => {
                console.log('🔄 Retrying filter event listener setup...');
                this.setupFilterEventListeners();
            }, 500);
        } else if (missingFilters.length > 0) {
            console.warn(`⚠️ Some filter elements missing: ${missingFilters.join(', ')}. Found ${foundCount}/${filterIds.length} filters.`);
        } else {
            verboseLog(`✅ All ${foundCount} filter event listeners attached successfully`);
        }
    },

    setupSearchEventListeners() {
        verboseLog('Setting up search event listeners...');
        
        // CRITICAL FIX: Add debouncing to search handlers for better performance
        // Debounce timers for search inputs
        if (!this._searchDebounceTimers) {
            this._searchDebounceTimers = {
                available: null,
                selected: null
            };
        }
        
        // Debounced search handler for available tags
        const debouncedAvailableSearch = (event) => {
            if (this._searchDebounceTimers.available) {
                clearTimeout(this._searchDebounceTimers.available);
            }
            this._searchDebounceTimers.available = setTimeout(() => {
                this.handleAvailableTagsSearch(event);
            }, 300); // 300ms debounce delay
        };
        
        // Debounced search handler for selected tags
        const debouncedSelectedSearch = (event) => {
            if (this._searchDebounceTimers.selected) {
                clearTimeout(this._searchDebounceTimers.selected);
            }
            this._searchDebounceTimers.selected = setTimeout(() => {
                this.handleSelectedTagsSearch(event);
            }, 300); // 300ms debounce delay
        };
        
        // Add search event listeners for available tags
        const availableTagsSearch = document.getElementById('availableTagsSearch');
        if (availableTagsSearch) {
            availableTagsSearch.removeEventListener('input', this._boundAvailableSearch);
            availableTagsSearch.removeEventListener('input', debouncedAvailableSearch);
            this._boundAvailableSearch = debouncedAvailableSearch;
            availableTagsSearch.addEventListener('input', debouncedAvailableSearch);
            verboseLog('Added debounced event listener to availableTagsSearch');
        } else {
            console.warn('Available tags search element not found');
        }
        
        // Add search event listeners for selected tags
        const selectedTagsSearch = document.getElementById('selectedTagsSearch');
        if (selectedTagsSearch) {
            selectedTagsSearch.removeEventListener('input', this._boundSelectedSearch);
            selectedTagsSearch.removeEventListener('input', debouncedSelectedSearch);
            this._boundSelectedSearch = debouncedSelectedSearch;
            selectedTagsSearch.addEventListener('input', debouncedSelectedSearch);
            verboseLog('Added debounced event listener to selectedTagsSearch');
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

// CRITICAL FIX: Expose TagManager to global scope IMMEDIATELY
// This must happen as soon as the TagManager object is created, not at the end
// This allows initializeFileUpload and other scripts to detect TagManager early
try {
    if (typeof window !== 'undefined') {
        window.TagManager = TagManager;
        // Also set a flag to indicate TagManager is loaded
        window.tagManagerLoaded = true;
        console.log('✅ TagManager assigned to window.TagManager');
        
        // CRITICAL FIX: Hydrate from cache immediately for instant tag display on reload
        // This runs synchronously before any API calls or async operations
        try {
            if (typeof TagManager.hydrateAvailableTagsFromCache === 'function') {
                const hydrated = TagManager.hydrateAvailableTagsFromCache();
                if (hydrated) {
                    console.log('⚡ INSTANT: Tags hydrated from cache immediately on script load');
                }
            }
        } catch (cacheError) {
            console.warn('Cache hydration error (non-critical):', cacheError);
        }
        
        // Also expose helper functions immediately
        if (TagManager.debouncedUpdateAvailableTags) {
            window.updateAvailableTags = TagManager.debouncedUpdateAvailableTags.bind(TagManager);
        }
        if (TagManager.updateFilters) {
            window.updateFilters = TagManager.updateFilters.bind(TagManager);
        }
        if (TagManager.fetchAndUpdateSelectedTags) {
            window.fetchAndUpdateSelectedTags = TagManager.fetchAndUpdateSelectedTags.bind(TagManager);
        }
    }
} catch (error) {
    console.error('❌ Error assigning TagManager to window:', error);
    // Try to assign anyway - this is critical
    try {
        if (typeof window !== 'undefined' && typeof TagManager !== 'undefined') {
            window.TagManager = TagManager;
            window.tagManagerLoaded = true;
            console.log('✅ TagManager assigned to window.TagManager (fallback)');
            
            // CRITICAL FIX: Hydrate from cache immediately for instant tag display on reload
            // This runs synchronously before any API calls or async operations
            try {
                if (typeof TagManager.hydrateAvailableTagsFromCache === 'function') {
                    const hydrated = TagManager.hydrateAvailableTagsFromCache();
                    if (hydrated) {
                        console.log('⚡ INSTANT: Tags hydrated from cache immediately on script load');
                    }
                }
            } catch (cacheError) {
                console.warn('Cache hydration error (non-critical):', cacheError);
            }
        }
    } catch (fallbackError) {
        console.error('❌ CRITICAL: Failed to assign TagManager even in fallback:', fallbackError);
    }
}

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
    
    // CRITICAL FIX: Add safeguard to ensure tags always load after page refresh
    // Check after 5 seconds if tags are loaded, and retry if not
    setTimeout(() => {
        if (window.TagManager && window.TagManager.state) {
            const hasTags = window.TagManager.state.tags && window.TagManager.state.tags.length > 0;
            const isInitialized = window.TagManager.state.initialized;
            const isChecking = window.TagManager._checkingExistingData;
            
            if (!hasTags && isInitialized && !isChecking) {
                console.warn('⚠️ SAFEGUARD: Tags not loaded after 5 seconds, attempting retry...');
                // Reset flags to allow retry
                window.TagManager._checkingExistingData = false;
                window.TagManager.state.initialDataAttempts = 0;
                // Try to load tags
                if (typeof window.TagManager.checkForExistingData === 'function') {
                    window.TagManager.checkForExistingData().catch(err => {
                        console.error('Safeguard retry failed:', err);
                        // Last resort: try direct fetch
                        if (typeof window.TagManager.fetchAndUpdateAvailableTags === 'function') {
                            window.TagManager.fetchAndUpdateAvailableTags().catch(e => {
                                console.error('Safeguard direct fetch also failed:', e);
                            });
                        }
                    });
                }
            }
        }
    }, 5000);
    
    // Additional safeguard after 10 seconds
    setTimeout(() => {
        if (window.TagManager && window.TagManager.state) {
            const hasTags = window.TagManager.state.tags && window.TagManager.state.tags.length > 0;
            const availableContainer = document.getElementById('availableTags');
            const hasRenderedTags = availableContainer && availableContainer.querySelectorAll('.tag-item').length > 0;
            
            if (!hasTags && !hasRenderedTags) {
                console.error('❌ CRITICAL: Tags still not loaded after 10 seconds - forcing direct fetch');
                // Force reset all flags
                window.TagManager._checkingExistingData = false;
                window.TagManager._fetchingAvailableTags = false;
                window.TagManager.state.initialDataAttempts = 0;
                // Force direct fetch
                if (typeof window.TagManager.fetchAndUpdateAvailableTags === 'function') {
                    window.TagManager.fetchAndUpdateAvailableTags().catch(e => {
                        console.error('Critical safeguard fetch failed:', e);
                    });
                }
            }
        }
    }, 10000);
    
    // CRITICAL FIX: Reset stuck flags when page becomes visible (user switches tabs)
    // This prevents flags from being stuck if user switches tabs during loading
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible' && window.TagManager) {
            // Check if flags are stuck
            const checkingStuck = window.TagManager._checkingExistingData;
            const checkingStartTime = window.TagManager._checkingExistingDataStartTime || Date.now();
            const checkingDuration = Date.now() - checkingStartTime;
            
            const fetchingStuck = window.TagManager._fetchingAvailableTags;
            const fetchingStartTime = window.TagManager._fetchingAvailableTagsStartTime || Date.now();
            const fetchingDuration = Date.now() - fetchingStartTime;
            
            if (checkingStuck && checkingDuration > 30000) {
                console.warn('⚠️ Resetting stuck _checkingExistingData flag on visibility change');
                window.TagManager._checkingExistingData = false;
            }
            
            if (fetchingStuck && fetchingDuration > 30000) {
                console.warn('⚠️ Resetting stuck _fetchingAvailableTags flag on visibility change');
                window.TagManager._fetchingAvailableTags = false;
            }
            
            // If tags aren't loaded and flags are reset, try loading again
            const hasTags = window.TagManager.state?.tags && window.TagManager.state.tags.length > 0;
            if (!hasTags && !checkingStuck && !fetchingStuck) {
                console.log('🔄 Page visible and no tags loaded, attempting to load tags...');
                if (typeof window.TagManager.checkForExistingData === 'function') {
                    window.TagManager.checkForExistingData().catch(e => {
                        console.error('Visibility change retry failed:', e);
                    });
                }
            }
        }
    });
    
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
            
            newButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('🔙 Undo button clicked');
                verboseLog('Undo button clicked');
                
                if (window.TagManager && typeof window.TagManager.undoMove === 'function') {
                    console.log('✅ Calling TagManager.undoMove()');
                    verboseLog('Calling TagManager.undoMove()');
                    window.TagManager.undoMove().catch(error => {
                        console.error('❌ Error in undoMove:', error);
                        alert(`Undo failed: ${error.message || error}`);
                    });
                } else {
                    console.error('❌ TagManager or undoMove method not available', {
                        hasTagManager: !!window.TagManager,
                        hasUndoMove: !!(window.TagManager && TagManager.undoMove),
                        typeofUndoMove: typeof (window.TagManager && TagManager.undoMove)
                    });
                    // Fallback: try to call the undo function directly
                    if (typeof window.undoMove === 'function') {
                        console.log('🔄 Calling window.undoMove() directly');
                        verboseLog('Calling undoMove() directly');
                        window.undoMove().catch(error => {
                            console.error('❌ Error in window.undoMove:', error);
                            alert(`Undo failed: ${error.message || error}`);
                        });
                    } else {
                        console.error('❌ No undo function available');
                        alert('Undo functionality is not available. Please try refreshing the page.');
                    }
                }
            });
            console.log('✅ Undo button event listener attached successfully');
            verboseLog('Undo button event listener attached successfully');
            return true;
        } else {
            console.error('❌ Undo button not found in DOM');
            return false;
        }
    }
    
    // Add event listener for the redo button with retry mechanism
    function attachRedoButtonListener() {
        const redoButton = document.getElementById('redo-move-btn');
        if (redoButton) {
            // Remove any existing listeners to prevent duplicates
            const newButton = redoButton.cloneNode(true);
            redoButton.parentNode.replaceChild(newButton, redoButton);

            newButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('🔁 Redo button clicked');
                verboseLog('Redo button clicked');

                if (window.TagManager && typeof window.TagManager.redoMove === 'function') {
                    console.log('✅ Calling TagManager.redoMove()');
                    verboseLog('Calling TagManager.redoMove()');
                    window.TagManager.redoMove().catch(error => {
                        console.error('❌ Error in redoMove:', error);
                        alert(`Redo failed: ${error.message || error}`);
                    });
                } else {
                    console.error('❌ TagManager or redoMove method not available');
                    alert('Redo functionality is not available. Please try refreshing the page.');
                }
            });
            console.log('✅ Redo button event listener attached successfully');
            verboseLog('Redo button event listener attached successfully');
            return true;
        } else {
            console.error('❌ Redo button not found in DOM');
            return false;
        }
    }

    // Try to attach the listeners immediately (we're already inside DOMContentLoaded)
    if (!attachUndoButtonListener()) {
        // If not found, retry after a short delay
        setTimeout(() => {
            if (!attachUndoButtonListener()) {
                console.warn('⚠️ Undo button still not found after retry');
                // Final retry after longer delay
                setTimeout(() => {
                    attachUndoButtonListener();
                }, 2000);
            }
        }, 1000);
    }

    // Attach redo button listener
    if (!attachRedoButtonListener()) {
        // If not found, retry after a short delay
        setTimeout(() => {
            if (!attachRedoButtonListener()) {
                console.warn('⚠️ Redo button still not found after retry');
                // Final retry after longer delay
                setTimeout(() => {
                    attachRedoButtonListener();
                }, 2000);
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
            safeReload(1000);
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
        
        // 11. Clear any pending requests (but don't abort upload-specific requests)
        if (window.abortController && !TagManager._uploadInProgress) {
            try {
                window.abortController.abort();
            } catch (e) {
                // Ignore errors from aborting
            }
        }
        if (!TagManager._uploadInProgress) {
            window.abortController = new AbortController();
        }
        
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
            safeReload(200);
        });
    }
});