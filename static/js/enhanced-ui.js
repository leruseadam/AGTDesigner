// Enhanced UI JavaScript
// This file contains all the enhanced UI functionality

// CRITICAL FIX: Global flag to prevent duplicate uploads on PC
let uploadInProgress = false;

// Immediately attach handlers - page should already be loaded
console.log('🔧 Enhanced UI: Loading...');
const fileDropZone = document.getElementById('fileDropZone');
const fileInput = document.getElementById('fileInput');
const currentFileInfo = document.getElementById('currentFileInfo');
const currentFile = document.getElementById('currentFile');

console.log('📝 File elements found:', {
  fileDropZone: !!fileDropZone,
  fileInput: !!fileInput,
  currentFileInfo: !!currentFileInfo,
  currentFile: !!currentFile
});

  // Drag and drop handlers
  if (fileDropZone) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      fileDropZone.addEventListener(eventName, preventDefaults, false);
    });
  }

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  if (fileDropZone) {
    ['dragenter', 'dragover'].forEach(eventName => {
      fileDropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      fileDropZone.addEventListener(eventName, unhighlight, false);
    });
  }

  function highlight(e) {
    fileDropZone.classList.add('dragover');
  }

  function unhighlight(e) {
    fileDropZone.classList.remove('dragover');
  }

  if (fileDropZone) {
    fileDropZone.addEventListener('drop', handleDrop, false);
  }

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
  }

if (fileInput) {
  console.log('✅ Attaching change listener to fileInput');
  fileInput.addEventListener('change', function(e) {
    console.log('🔄 File input change event fired');
    if (e.target.files && e.target.files.length > 0) {
      console.log('🎬 UPLOAD START: Showing splash immediately');
      handleFiles(e.target.files);
      // Prevent any other handlers from running
      e.stopPropagation();
    }
  });
} else {
  console.error('❌ fileInput element not found!');
}

// Note: Removed duplicate TagManager upload handler to prevent conflicts
// The handleFiles() function above handles uploads and shows the splash correctly

// Helper function to hide splash with minimum display time
function hideSplashWithDelay(splashStartTime, minDisplayTime = 800) {
  const elapsedTime = Date.now() - splashStartTime;
  const remainingTime = Math.max(0, minDisplayTime - elapsedTime);
  
  console.log(`⏱️ Splash timing: elapsed=${elapsedTime}ms, minimum=${minDisplayTime}ms, waiting=${remainingTime}ms`);
  
  setTimeout(() => {
    console.log('⏱️ Minimum display time reached, hiding splash now');
    // Hide directly without waiting for TagManager
    const splash = document.getElementById('excelLoadingSplash');
    if (splash) {
      splash.style.display = 'none';
      console.log('✅ Splash hidden directly');
    } else {
      console.error('❌ Could not find splash element to hide');
    }
  }, remainingTime);
}

async function handleFiles(files) {
  console.log('📁 handleFiles called with:', files.length, 'files');

  // CRITICAL FIX: Prevent duplicate uploads on PC
  if (uploadInProgress) {
    console.warn('⚠️ Upload already in progress, ignoring duplicate call');
    return;
  }

  if (files.length > 0) {
    const file = files[0];
    console.log('📄 File selected:', file.name, 'size:', file.size);

    // Set upload flag IMMEDIATELY to prevent duplicates
    uploadInProgress = true;

    // CRITICAL: Show Excel loading splash screen FIRST before anything else
    const splashStartTime = Date.now();
    console.log('🎬 UPLOAD: Showing splash IMMEDIATELY for:', file.name);
    const splash = document.getElementById('excelLoadingSplash');
    const filenameElement = document.getElementById('excelLoadingFilename');
    const statusElement = document.getElementById('excelLoadingStatus');
    
    if (splash && filenameElement && statusElement) {
      console.log('🎬 UPLOAD: Splash elements found - displaying NOW');
      filenameElement.textContent = file.name;
      statusElement.textContent = 'Uploading file...';
      splash.style.display = 'flex';
      splash.style.zIndex = '99999';
      splash.style.position = 'fixed';
      splash.style.top = '0';
      splash.style.left = '0';
      splash.style.width = '100%';
      splash.style.height = '100%';
      console.log('✅ SPLASH SHOWN - display:', splash.style.display);

      // CRITICAL FIX: Add automatic timeout recovery to prevent infinite hanging
      // If splash is still visible after 4 minutes, force recovery
      const maxSplashTime = 240000; // 4 minutes
      const splashTimeoutId = setTimeout(() => {
        if (splash.style.display !== 'none') {
          console.error('⚠️ CRITICAL: Splash screen timeout - forcing recovery');
          statusElement.textContent = 'Upload took too long. Attempting recovery...';

          // Try to recover by loading data directly
          setTimeout(async () => {
            try {
              console.log('🔄 Attempting recovery by loading data directly...');
              if (typeof TagManager !== 'undefined' && TagManager.fetchAndUpdateAvailableTags) {
                await fetch('/api/clear-cache', { method: 'POST' }).catch(() => {});
                TagManager._forceDatabaseLineage = true;
                const loaded = await TagManager.fetchAndUpdateAvailableTags();
                TagManager._forceDatabaseLineage = false;

                if (loaded && TagManager.state && TagManager.state.tags && TagManager.state.tags.length > 0) {
                  console.log('✅ Recovery successful - data loaded');

                  // CRITICAL FIX: Also load filters after recovery
                  try {
                    if (TagManager.fetchAndPopulateFilters) {
                      await TagManager.fetchAndPopulateFilters();
                      console.log('✅ Filters loaded after recovery');
                    }
                  } catch (filterErr) {
                    console.warn('⚠️ Could not load filters after recovery:', filterErr);
                  }

                  splash.style.display = 'none';
                  uploadInProgress = false;
                  alert('Upload completed successfully after recovery.');
                } else {
                  throw new Error('Recovery failed - no data');
                }
              } else {
                throw new Error('TagManager not available');
              }
            } catch (error) {
              console.error('❌ Recovery failed:', error);
              splash.style.display = 'none';
              uploadInProgress = false;
              if (confirm('Upload recovery failed. Would you like to reload the page?')) {
                window.location.reload();
              }
            }
          }, 1000);
        }
      }, maxSplashTime);

      // Store timeout ID so it can be cleared if upload completes normally
      window._splashTimeoutId = splashTimeoutId;
    } else {
      console.error('❌ UPLOAD: Could not find splash elements:', {
        splash: !!splash,
        filenameElement: !!filenameElement,
        statusElement: !!statusElement
      });
      // Reset upload flag on error
      uploadInProgress = false;
      alert('Error: Upload splash screen not found. Please refresh the page.');
      return;
    }
    
    // Now update file info UI
    if (currentFile) currentFile.textContent = file.name;
    if (currentFileInfo) currentFileInfo.style.display = 'block';
    
    // Update the file path container with the new file name
    const filePathContainer = document.querySelector('.file-path-container');
    const currentFileInfoElement = document.getElementById('currentFileInfo');
    if (currentFileInfoElement) {
      currentFileInfoElement.textContent = file.name;
    }
    
    // Animate the file info appearance
    if (currentFileInfo) {
      currentFileInfo.style.opacity = '0';
      setTimeout(() => {
        currentFileInfo.style.transition = 'opacity 0.3s ease';
        currentFileInfo.style.opacity = '1';
      }, 10);
    }

    // Handle file upload
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      TagManager.setLoading(true);
      
      // Clear UI state immediately when upload starts
      if (typeof TagManager !== 'undefined' && TagManager.clearUIStateForNewFile) {
        TagManager.clearUIStateForNewFile(true); // Preserve filters during upload
      }
      
      console.log('🚀 Sending upload request to /upload...');
      // Update splash status
      if (statusElement) statusElement.textContent = 'Uploading file...';
      
      // CRITICAL FIX: Increase timeout for large files - 504 errors mean server timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
        console.warn('⚠️ Upload timeout after 180 seconds');
      }, 180000); // 180 second timeout (3 minutes) for large files
      
      let response;
      let retryCount = 0;
      const maxRetries = 2;
      
      // CRITICAL FIX: Retry logic for 504 Gateway Timeout errors
      while (retryCount <= maxRetries) {
        try {
          response = await fetch('/upload', {
            method: 'POST',
            body: formData,
            headers: {
              'X-Post-Upload': '1'  // Flag for fast tag loading
            },
            signal: controller.signal
          });
          
          // Clear timeout if request succeeded
          clearTimeout(timeoutId);
          
          // If we got a 504, retry
          if (response.status === 504 && retryCount < maxRetries) {
            retryCount++;
            console.warn(`⚠️ Got 504 Gateway Timeout, retrying (${retryCount}/${maxRetries})...`);
            if (statusElement) statusElement.textContent = `Retrying upload (${retryCount}/${maxRetries})...`;
            // Wait 2 seconds before retry
            await new Promise(resolve => setTimeout(resolve, 2000));
            continue;
          }
          
          // Break out of retry loop if successful or non-retryable error
          break;
        } catch (error) {
          // If abort error and we haven't exceeded retries, retry
          if (error.name === 'AbortError' && retryCount < maxRetries) {
            retryCount++;
            console.warn(`⚠️ Upload aborted, retrying (${retryCount}/${maxRetries})...`);
            if (statusElement) statusElement.textContent = `Retrying upload (${retryCount}/${maxRetries})...`;
            // Wait 2 seconds before retry
            await new Promise(resolve => setTimeout(resolve, 2000));
            continue;
          }
          // Re-throw if we've exhausted retries or it's a different error
          throw error;
        }
      }
      
      console.log('📡 Upload response status:', response.status);
      
      // Update splash status
      if (statusElement) statusElement.textContent = 'Processing data...';
      
      // Check if response is ok before parsing JSON
      if (!response.ok) {
        let errorMessage = `Upload failed with status ${response.status}`;
        if (response.status === 504) {
          errorMessage = 'Upload timed out on server. The file may be too large or the server is busy. Please try again or use a smaller file.';
        }
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || errorData.message || errorMessage;
        } catch (e) {
          const errorText = await response.text();
          if (errorText) {
            errorMessage = errorText;
          }
        }
        console.error('❌ Upload failed:', errorMessage);
        if (statusElement) statusElement.textContent = `❌ Error: ${errorMessage}`;
        if (splash) splash.style.display = 'none';
        // Reset upload flag on error
        uploadInProgress = false;
        alert(`Upload failed: ${errorMessage}`);
        return;
      }
      
      const data = await response.json();
      console.log('📦 Upload response data:', data);
      
      if (response.ok && data.success) {
        // CRITICAL FIX: Check if processing is explicitly true (not just truthy)
        // Backend now returns processing: False, so we should proceed with normal flow
        if (data.processing === true) {
          console.log(`Background processing required for ${data.filename || file.name}`);
          
          // Keep splash visible and update messaging while we wait for processing to finish.
          if (statusElement) statusElement.textContent = 'Processing file...';
          if (typeof TagManager !== 'undefined' && TagManager.updateExcelLoadingStatus) {
            TagManager.updateExcelLoadingStatus('Processing file...');
          }
          
          // Start polling backend until the upload is ready, then stop normal success flow.
          // CRITICAL FIX: Use TagManager's poll method which is guaranteed to exist
          if (typeof TagManager !== 'undefined' && typeof TagManager.pollUploadStatusAndUpdateUI === 'function') {
            console.log('✅ Using TagManager.pollUploadStatusAndUpdateUI');
            TagManager.pollUploadStatusAndUpdateUI(data.filename || file.name, file.name);
            // Reset upload flag after polling starts
            uploadInProgress = false;
          } else if (typeof window.pollUploadStatus === 'function') {
            console.log('✅ Using window.pollUploadStatus');
            window.pollUploadStatus(data.filename || file.name);
            uploadInProgress = false;
          } else {
            console.warn('⚠️ pollUploadStatus function not available; loading data directly');
            // CRITICAL FIX: Instead of reloading, try to load data directly
            if (statusElement) statusElement.textContent = 'Loading data...';

            setTimeout(async () => {
              try {
                if (typeof TagManager !== 'undefined' && TagManager.fetchAndUpdateAvailableTags) {
                  console.log('Attempting direct data load after upload...');
                  // Clear cache first
                  await fetch('/api/clear-cache', { method: 'POST' }).catch(() => {});

                  // Load tags directly
                  TagManager._forceDatabaseLineage = true;
                  const loaded = await TagManager.fetchAndUpdateAvailableTags();
                  TagManager._forceDatabaseLineage = false;

                  if (loaded && TagManager.state && TagManager.state.tags && TagManager.state.tags.length > 0) {
                    console.log('✅ Data loaded successfully');

                    // CRITICAL FIX: Load filters after tags
                    try {
                      if (TagManager.fetchAndPopulateFilters) {
                        await TagManager.fetchAndPopulateFilters();
                        console.log('✅ Filters loaded successfully');
                      }
                    } catch (filterErr) {
                      console.warn('⚠️ Could not load filters:', filterErr);
                    }

                    if (splash) splash.style.display = 'none';
                    uploadInProgress = false;
                  } else {
                    throw new Error('No data loaded');
                  }
                } else {
                  throw new Error('TagManager not available');
                }
              } catch (error) {
                console.error('Failed to load data directly, reloading page...', error);
                if (window.safeReload) {
                  window.safeReload(2000);
                } else {
                  if (window._reloadTimeout) clearTimeout(window._reloadTimeout);
                  window._reloadTimeout = setTimeout(() => {
                    if (!window._reloadInProgress) {
                      window._reloadInProgress = true;
                      window.location.reload();
                    }
                  }, 2000);
                }
              }
            }, 2000);
          }
          return;
        }
        
        // CRITICAL FIX: If processing is false or undefined, proceed with normal success flow
        console.log('✅ Upload complete - processing synchronously, loading tags...');

        // File uploaded successfully - data is already processed synchronously
        console.log(`File uploaded successfully: ${data.filename}, rows: ${data.rows}`);
        console.log('Upload response data:', data);
        
        // CRITICAL FIX: Reset retry counter after successful upload to allow fresh tag loading
        if (typeof TagManager !== 'undefined') {
          if (TagManager.clearInitialDataRetry) {
            TagManager.clearInitialDataRetry();
            TagManager.state.initialDataAttempts = 0;
            console.log('✅ Reset retry counter after upload');
          }
        }
        
        // Update splash to show success
        if (statusElement) statusElement.textContent = `✅ Success! ${data.rows || 'File'} rows loaded`;
        
        // Check for store mismatch warning
        if (data.warning) {
          console.warn('⚠️ Store mismatch warning:', data.warning);
          // Show warning alert to user
          const warningMsg = `${data.warning}\n\nSelected Store: ${data.selected_store}\nDetected in Filename: ${data.detected_store}`;
          if (confirm(warningMsg + '\n\nDo you want to continue anyway?')) {
            // User confirmed, continue with upload
          } else {
            // User cancelled, don't reload - hide splash directly
            const splash = document.getElementById('excelLoadingSplash');
            if (splash) splash.style.display = 'none';
            // Reset upload flag when user cancels
            uploadInProgress = false;
            return;
          }
        }
        
        // Hide splash immediately and refresh data asynchronously (non-blocking)
        const splashEl = document.getElementById('excelLoadingSplash');
        if (splashEl) splashEl.style.display = 'none';
        if (typeof TagManager !== 'undefined') {
          try {
            TagManager.clearUIStateForNewFile(true); // keep filters
            
            // CRITICAL FIX: Load tags IMMEDIATELY - backend now loads file synchronously
            // Tags should be available instantly after upload completes
            console.log('🚀 Loading tags immediately after upload...');
            
            // CRITICAL FIX: Force database lineage after upload to ensure fresh data
            TagManager._forceDatabaseLineage = true;
            
            // Try refreshTagLists first (most reliable)
            if (TagManager.refreshTagLists) {
              console.time('post-upload-refresh-async');
              TagManager.refreshTagLists({ preserveFilters: true, force: true })
                .then(async () => {
                  console.timeEnd('post-upload-refresh-async');
                  console.log('✅ Tags loaded successfully via refreshTagLists');
                  // Clear force flag after successful load
                  TagManager._forceDatabaseLineage = false;

                  // CRITICAL FIX: Populate filters after tags are loaded
                  console.log('🔄 Loading filters after successful tag refresh...');
                  try {
                    if (TagManager.fetchAndPopulateFilters) {
                      await TagManager.fetchAndPopulateFilters();
                      console.log('✅ Filters populated successfully');
                    }
                  } catch (filterErr) {
                    console.error('⚠️ Filter population failed (non-critical):', filterErr);
                  }
                })
                .catch(err => {
                  console.error('❌ refreshTagLists failed:', err);
                  // Clear force flag on error
                  TagManager._forceDatabaseLineage = false;
                  
                  // Fallback: Try fetchAndUpdateAvailableTags with retry logic
                  console.warn('🔄 Trying fetchAndUpdateAvailableTags with retry...');
                  let retryAttempt = 0;
                  const maxRetries = 5;
                  
                  const tryFetchTags = () => {
                    if (retryAttempt >= maxRetries) {
                      console.error('❌ All tag loading attempts failed');
                      // Last resort: reload page
                      if (window.safeReload) {
                        window.safeReload(2000);
                      } else {
                        if (window._reloadTimeout) {
                          clearTimeout(window._reloadTimeout);
                        }
                        window._reloadTimeout = setTimeout(() => {
                          if (!window._reloadInProgress) {
                            window._reloadInProgress = true;
                            window.location.reload();
                          }
                        }, 2000);
                      }
                      return;
                    }
                    
                    retryAttempt++;
                    console.log(`🔄 Attempt ${retryAttempt}/${maxRetries} to load tags...`);
                    
                    TagManager.fetchAndUpdateAvailableTags?.()
                      .then(async () => {
                        console.log('✅ Tags loaded successfully via fetchAndUpdateAvailableTags');

                        // CRITICAL FIX: Load filters after tags succeed
                        try {
                          if (TagManager.fetchAndPopulateFilters) {
                            await TagManager.fetchAndPopulateFilters();
                            console.log('✅ Filters populated after retry');
                          }
                        } catch (filterErr) {
                          console.error('⚠️ Filter population failed (non-critical):', filterErr);
                        }
                      })
                      .catch(fetchErr => {
                        console.error(`❌ Attempt ${retryAttempt} failed:`, fetchErr);
                        // Retry after delay
                        setTimeout(tryFetchTags, 2000 * retryAttempt); // Progressive delay
                      });
                  };
                  
                  tryFetchTags();
                });
            } else {
              // Fallback: individual fetches without await
              console.warn('⚠️ refreshTagLists not available, using individual fetches');
              TagManager._forceDatabaseLineage = true;
              TagManager.fetchAndUpdateAvailableTags?.()
                .then(() => {
                  TagManager._forceDatabaseLineage = false;
                })
                .catch(() => {
                  TagManager._forceDatabaseLineage = false;
                });
              TagManager.fetchAndUpdateSelectedTags?.();
              TagManager.fetchAndPopulateFilters?.();
            }
          } catch (e) {
            console.error('Post-upload async refresh setup failed', e);
            // Try to load tags individually instead of reloading immediately
            console.warn('Trying individual tag fetches as fallback...');
            Promise.allSettled([
              TagManager?.fetchAndUpdateAvailableTags?.() || Promise.resolve(),
              TagManager?.fetchAndUpdateSelectedTags?.() || Promise.resolve(),
              TagManager?.fetchAndPopulateFilters?.() || Promise.resolve()
            ]).then(() => {
              console.log('✅ Fallback tag loading completed');
            }).catch(fallbackErr => {
              console.error('All tag loading methods failed, reloading as last resort', fallbackErr);
              if (window.safeReload) {
                window.safeReload(2000);
              } else {
                // CRITICAL FIX: Debounce reloads to prevent flashing
                if (window._reloadTimeout) {
                  clearTimeout(window._reloadTimeout);
                }
                window._reloadTimeout = setTimeout(() => {
                  if (!window._reloadInProgress) {
                    window._reloadInProgress = true;
                    window.location.reload();
                  }
                }, 2000);
              }
            });
          }
        } else {
          // TagManager not available - try to wait a bit and retry before reloading
          console.warn('TagManager not available, waiting before reload...');
          setTimeout(() => {
            if (typeof TagManager !== 'undefined') {
              console.log('TagManager now available, loading tags...');
              TagManager.fetchAndUpdateAvailableTags?.();
              TagManager.fetchAndUpdateSelectedTags?.();
              TagManager.fetchAndPopulateFilters?.();
            } else {
              console.warn('TagManager still not available, reloading as last resort');
              if (window.safeReload) {
                window.safeReload(1000);
              } else {
                // CRITICAL FIX: Debounce reloads to prevent flashing
                if (window._reloadTimeout) {
                  clearTimeout(window._reloadTimeout);
                }
                window._reloadTimeout = setTimeout(() => {
                  if (!window._reloadInProgress) {
                    window._reloadInProgress = true;
                    window.location.reload();
                  }
                }, 2000);
              }
            }
          }, 2000);
        }
        
        // Add animation class to file path container
        if (filePathContainer) {
          filePathContainer.classList.add('file-loaded');
          setTimeout(() => {
            filePathContainer.classList.remove('file-loaded');
          }, 600);
        }
        
        // Show success feedback
        if (fileDropZone) {
          fileDropZone.style.borderColor = '#4facfe';
          setTimeout(() => {
            fileDropZone.style.borderColor = '';
          }, 1000);
        }
      } else {
        // Hide splash screen on error with minimum display time
        hideSplashWithDelay(splashStartTime, 800);
        // Show detailed error message if available
        const errorMsg = data.error || 'Upload failed';
        if (data.filename && data.selected_store) {
          showToast("error", `${errorMsg}\nFilename: ${data.filename}\nSelected Store: ${data.selected_store}`);
        } else {
          showToast("error", errorMsg);
        }
      }
    } catch (error) {
      console.error('Upload error:', error);
      
      // Clear timeout if it exists
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      
      // Hide splash screen on error with minimum display time
      hideSplashWithDelay(splashStartTime, 800);
      
      // Show specific error message
      const errorMsg = error.name === 'AbortError' 
        ? 'Upload timed out. Please try again with a smaller file or check your connection.'
        : error.message || 'Upload failed. Please try again.';
      
      showToast("error", errorMsg);
      
      // Also hide splash directly in case hideSplashWithDelay doesn't work
      const splash = document.getElementById('excelLoadingSplash');
      if (splash) splash.style.display = 'none';
    } finally {
      TagManager.setLoading(false);
      // CRITICAL FIX: Reset upload flag to allow future uploads
      uploadInProgress = false;
      console.log('✅ Upload flag reset - ready for next upload');

      // CRITICAL FIX: Clear splash timeout if it exists
      if (window._splashTimeoutId) {
        clearTimeout(window._splashTimeoutId);
        window._splashTimeoutId = null;
        console.log('✅ Cleared splash timeout');
      }
    }
  }
}

// Add smooth scrolling (but ONLY on Mac - Windows handles native scrolling better)
if (typeof window.isWindows === 'undefined') {
  window.isWindows = /Windows|Win32|Win64/.test(navigator.userAgent);
}
if (!window.isWindows) {
  document.querySelectorAll('.tag-list-container').forEach(container => {
    container.addEventListener('wheel', (e) => {
      e.preventDefault();
      container.scrollTop += e.deltaY * 0.5;
    });
  });
  console.log('🍎 Mac detected - using custom smooth scrolling');
} else {
  console.log('🪟 Windows detected - using native scrolling for better performance');
}

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
  if (e.ctrlKey || e.metaKey) {
    switch(e.key) {
      case 'g':
        e.preventDefault();
        document.getElementById('generateBtn').click();
        break;
      case 'z':
        e.preventDefault();
        document.getElementById('undo-move-btn').click();
        break;
      case 'h':
        e.preventDefault();
        document.getElementById('help-btn').click();
        break;
    }
  }
});

// Initialize tooltips
const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl);
});

// Page load animations
window.addEventListener('DOMContentLoaded', function() {
  window.scrollTo(0, 0);
  
  // Add staggered fade-in animation
  document.querySelectorAll('.fade-in').forEach((el, index) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    setTimeout(() => {
      el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    }, index * 100);
  });
});

// Enhanced button click feedback
document.querySelectorAll('.btn').forEach(button => {
  button.addEventListener('click', function(e) {
    // Create ripple effect
    const ripple = document.createElement('span');
    const rect = this.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    this.appendChild(ripple);
    
    setTimeout(() => {
      ripple.remove();
    }, 600);
  });
});

// Enhanced form control interactions
document.querySelectorAll('.form-control-modern, .form-select-modern').forEach(control => {
  control.addEventListener('focus', function() {
    this.style.transform = 'translateY(-1px)';
  });
  
  control.addEventListener('blur', function() {
    this.style.transform = 'translateY(0)';
  });
});

// Enhanced tag item interactions
document.querySelectorAll('.tag-item').forEach(tag => {
  tag.addEventListener('mouseenter', function() {
    this.style.transform = 'translateY(-1px)';
  });
  
  tag.addEventListener('mouseleave', function() {
    this.style.transform = 'translateY(0)';
  });
});

// Auto-upload functionality
// Auto upload check functionality removed

// Auto upload check functionality removed

// Enhanced modal animations
const modals = document.querySelectorAll('.modal');
modals.forEach(modal => {
  modal.addEventListener('show.bs.modal', function() {
    // Store the currently focused element before opening modal
    const activeElement = document.activeElement;
    if (activeElement && !modal.contains(activeElement)) {
      activeElement.setAttribute('data-bs-focus-prev', 'true');
    }
    
    this.style.opacity = '0';
    setTimeout(() => {
      this.style.transition = 'opacity 0.3s ease';
      this.style.opacity = '1';
    }, 10);
  });
  
  modal.addEventListener('shown.bs.modal', function() {
    // Remove aria-hidden when modal is fully shown
    this.removeAttribute('aria-hidden');
  });
  
  modal.addEventListener('hidden.bs.modal', function() {
    // Use inert attribute instead of aria-hidden for better accessibility
    this.setAttribute('inert', '');
    this.removeAttribute('aria-hidden');
    
    // Ensure focus is moved outside the modal
    const previouslyFocusedElement = document.querySelector('[data-bs-focus-prev]');
    if (previouslyFocusedElement) {
      previouslyFocusedElement.focus();
      previouslyFocusedElement.removeAttribute('data-bs-focus-prev');
    }
    
    console.log('Modal hidden with accessibility fix:', this.id);
  });
});

// Poll upload status and update UI when processing is complete
// Make pollUploadStatus globally accessible
window.pollUploadStatus = function pollUploadStatus(filename) {
  let pollCount = 0;
  const maxPolls = 120; // Poll for up to 2 minutes (120 * 1 second)
  
  const poll = async () => {
    try {
      const response = await fetch(`/api/upload-status?filename=${encodeURIComponent(filename)}`);
      const data = await response.json();
      
      console.log(`Upload status for ${filename}: ${data.status}`);
      console.log('Upload status response:', data);
      
      if (data.status === 'ready') {
        // File processing is complete, fetch updated data
        console.log(`File processing complete for ${filename}, fetching updated data...`);
        
        // Clear any existing UI state to ensure fresh start
        if (typeof TagManager !== 'undefined') {
          // Use the new comprehensive UI clearing function
          TagManager.clearUIStateForNewFile(true); // Preserve filters during UI refresh
        }
        
        console.log('File processing complete, updating UI...');

        // Fetch all updated data in parallel to avoid serial bottlenecks
        console.time('post-ready-data-fetch');
        if (typeof TagManager !== 'undefined' && TagManager.refreshTagLists) {
          await TagManager.refreshTagLists({ preserveFilters: true, force: true });
        } else {
          await Promise.all([
            // Available tags
            (async () => {
              console.log('Fetching available tags (fallback)...');
              const res = await TagManager.fetchAndUpdateAvailableTags();
              console.log('Available tags result:', res);
            })(),
            // Selected tags
            (async () => {
              console.log('Fetching selected tags (fallback)...');
              const res = await TagManager.fetchAndUpdateSelectedTags();
              console.log('Selected tags result:', res);
            })(),
            // Filter options
            (async () => {
              console.log('Fetching filter options (fallback)...');
              await TagManager.fetchAndPopulateFilters();
              console.log('Filter options updated');
            })()
          ]);
        }
        console.timeEnd('post-ready-data-fetch');
        
        // Hide splash and trigger async, non-blocking refresh
        if (typeof TagManager !== 'undefined' && TagManager.hideExcelLoadingSplash) {
          TagManager.hideExcelLoadingSplash();
        } else {
          const s = document.getElementById('excelLoadingSplash');
          if (s) s.style.display = 'none';
        }
        showToast('success', `File "${filename}" loaded successfully!`);
        if (typeof TagManager !== 'undefined') {
          try {
            TagManager.clearUIStateForNewFile?.(true);
            setTimeout(() => {
              if (TagManager.refreshTagLists) {
                TagManager.refreshTagLists({ preserveFilters: true, force: true })
                  .catch(err => {
                    console.error('refreshTagLists failed after poll-ready', err);
                    if (window.safeReload) {
                      window.safeReload(1000);
                    } else {
                      // CRITICAL FIX: Debounce reloads to prevent flashing
                      if (window._reloadTimeout) {
                        clearTimeout(window._reloadTimeout);
                      }
                      window._reloadTimeout = setTimeout(() => {
                        if (!window._reloadInProgress) {
                          window._reloadInProgress = true;
                          window.location.reload();
                        }
                      }, 2000);
                    }
                  });
              } else {
                TagManager.fetchAndUpdateAvailableTags?.();
                TagManager.fetchAndUpdateSelectedTags?.();
                TagManager.fetchAndPopulateFilters?.();
              }
            }, 0);
          } catch (e) {
            console.error('Async refresh setup failed after poll-ready', e);
            if (window.safeReload) {
              window.safeReload(1000);
            } else {
              // CRITICAL FIX: Debounce reloads to prevent flashing
              if (window._reloadTimeout) {
                clearTimeout(window._reloadTimeout);
              }
              window._reloadTimeout = setTimeout(() => {
                if (!window._reloadInProgress) {
                  window._reloadInProgress = true;
                  window.location.reload();
                }
              }, 2000);
            }
          }
        } else {
          if (window.safeReload) {
            window.safeReload(500);
          } else {
            // CRITICAL FIX: Debounce reloads to prevent flashing
            if (window._reloadTimeout) {
              clearTimeout(window._reloadTimeout);
            }
            window._reloadTimeout = setTimeout(() => {
              if (!window._reloadInProgress) {
                window._reloadInProgress = true;
                window.location.reload();
              }
            }, 2000);
          }
        }
        
        return; // Stop polling
      } else if (data.status === 'error') {
        // Processing failed
        console.error(`File processing failed for ${filename}: ${data.error || 'Unknown error'}`);
        
        // Hide splash screen on error
        if (typeof TagManager !== 'undefined' && TagManager.hideExcelLoadingSplash) {
          TagManager.hideExcelLoadingSplash();
        }
        
        showToast('error', `File processing failed: ${data.error || 'Unknown error'}`);
        return; // Stop polling
      } else if (data.status === 'processing') {
        // Still processing, continue polling
        pollCount++;
        
        // Update splash screen status with progress
        if (typeof TagManager !== 'undefined' && TagManager.updateExcelLoadingStatus) {
          const progressPercent = Math.min((pollCount / maxPolls) * 100, 95);
          // Remove numeric percent from splash per request; keep animated dots
          TagManager.updateExcelLoadingStatus('Processing file...');
        }
        
        if (pollCount >= maxPolls) {
          console.error(`File processing timeout for ${filename} after ${maxPolls} polls`);
          
          // Hide splash screen on timeout
          if (typeof TagManager !== 'undefined' && TagManager.hideExcelLoadingSplash) {
            TagManager.hideExcelLoadingSplash();
          }
          
          showToast('error', `File processing timeout. Please try again.`);
          return; // Stop polling
        }
        
        // Continue polling frequently for faster response
        setTimeout(poll, 500);
      } else if (data.status === 'not_found') {
        // File not found in processing status - check if it exists
        console.warn(`File not found in processing status: ${filename}`);
        console.log('Upload status details:', data);
        
        if (data.file_exists) {
          // File exists but status was cleared - treat as ready
          console.log(`File ${filename} exists but status was cleared - treating as ready`);
          showToast('success', `File "${filename}" loaded successfully!`);
          return; // Stop polling
        } else {
          // File doesn't exist - stop polling
          console.error(`File ${filename} does not exist in uploads directory`);
          
          // Hide splash screen on file not found
          if (typeof TagManager !== 'undefined' && TagManager.hideExcelLoadingSplash) {
            TagManager.hideExcelLoadingSplash();
          }
          
          showToast('error', `File "${filename}" not found. Please upload again.`);
          return; // Stop polling
        }
      } else {
        // Unknown status
        console.warn(`Unknown upload status for ${filename}: ${data.status}`);
        pollCount++;
        if (pollCount >= maxPolls) {
          // Hide splash screen on unknown status timeout
          if (typeof TagManager !== 'undefined' && TagManager.hideExcelLoadingSplash) {
            TagManager.hideExcelLoadingSplash();
          }
          
          showToast('error', `File processing failed: Unknown status`);
          return; // Stop polling
        }
        
        // Continue polling frequently for faster response
        setTimeout(poll, 500);
      }
    } catch (error) {
      console.error(`Error polling upload status for ${filename}:`, error);
      pollCount++;
      if (pollCount >= maxPolls) {
        // Hide splash screen on network error timeout
        if (typeof TagManager !== 'undefined' && TagManager.hideExcelLoadingSplash) {
          TagManager.hideExcelLoadingSplash();
        }
        
        showToast('error', `File processing failed: Network error`);
        return; // Stop polling
      }
      
      // Continue polling frequently for faster response
      setTimeout(poll, 500);
    }
  };
  
  // Start polling
  poll();
}

// Add hover sound effects (optional - requires adding audio files)
function addHoverSound() {
  const hoverSound = new Audio('/static/sounds/hover.mp3');
  hoverSound.volume = 0.1;
  
  document.querySelectorAll('.btn, .tag-item').forEach(element => {
    element.addEventListener('mouseenter', () => {
      hoverSound.currentTime = 0;
      hoverSound.play().catch(() => {});
    });
  });
}

// Particle effect on button clicks (optional)
function createParticles(x, y) {
  const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c'];
  
  for (let i = 0; i < 10; i++) {
    const particle = document.createElement('div');
    particle.style.position = 'fixed';
    particle.style.left = x + 'px';
    particle.style.top = y + 'px';
    particle.style.width = '5px';
    particle.style.height = '5px';
    particle.style.background = colors[Math.floor(Math.random() * colors.length)];
    particle.style.borderRadius = '50%';
    particle.style.pointerEvents = 'none';
    particle.style.zIndex = '9999';
    
    const angle = (Math.PI * 2 * i) / 10;
    const velocity = 2 + Math.random() * 2;
    const vx = Math.cos(angle) * velocity;
    const vy = Math.sin(angle) * velocity;
    
    document.body.appendChild(particle);
    
    let opacity = 1;
    const animate = () => {
      particle.style.left = (parseFloat(particle.style.left) + vx) + 'px';
      particle.style.top = (parseFloat(particle.style.top) + vy) + 'px';
      opacity -= 0.02;
      particle.style.opacity = opacity;
      
      if (opacity > 0) {
        requestAnimationFrame(animate);
      } else {
        particle.remove();
      }
    };
    
    requestAnimationFrame(animate);
  }
}

// Add particle effect to important buttons
document.getElementById('generateBtn')?.addEventListener('click', function(e) {
  createParticles(e.clientX, e.clientY);
});

// Auto-save functionality indicator
let autoSaveTimer;
function showAutoSave() {
  const indicator = document.createElement('div');
  indicator.className = 'auto-save-indicator';
  indicator.textContent = 'Auto-saved';
  indicator.style.cssText = `
    position: fixed;
    bottom: 20px;
    left: 20px;
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    padding: 10px 20px;
    border-radius: 8px;
    color: #4facfe;
    font-weight: 600;
    opacity: 0;
    transition: opacity 0.3s ease;
    z-index: 1000;
  `;
  
  document.body.appendChild(indicator);
  
  setTimeout(() => {
    indicator.style.opacity = '1';
  }, 10);
  
  setTimeout(() => {
    indicator.style.opacity = '0';
    setTimeout(() => {
      indicator.remove();
    }, 300);
  }, 2000);
}

// Dynamic background based on time of day (optional)
function setDynamicBackground() {
  const hour = new Date().getHours();
  const body = document.body;
  
  if (hour >= 6 && hour < 12) {
    // Morning
    body.style.setProperty('--bg-gradient', 'linear-gradient(-45deg, #0a0a0a, #1a0033, #330066, #4d0080)');
  } else if (hour >= 12 && hour < 18) {
    // Afternoon
    body.style.setProperty('--bg-gradient', 'linear-gradient(-45deg, #0a0a0a, #1a0033, #4d0033, #660033)');
  } else {
    // Evening/Night
    body.style.setProperty('--bg-gradient', 'linear-gradient(-45deg, #0a0a0a, #0a0a1a, #1a0a2a, #2a0a3a)');
  }
}

// Initialize enhanced features
document.addEventListener('DOMContentLoaded', function() {
  // Optional: Enable hover sounds
  // addHoverSound();
  
  // Optional: Set dynamic background
  // setDynamicBackground();
  
  // Welcome animation removed - redundant with splash screen
});

// Scale the entire app to fit within the viewport
(function() {
  // Brute-force global zoom/transform fallback that always shows a change
  function applyGlobalZoom(scale) {
    const s = Math.max(0.6, Math.min(1, Number(scale) || 1));
    const html = document.documentElement;
    const body = document.body;
    // Prefer zoom where available (Chrome/Edge)
    try { html.style.setProperty('zoom', String(s), 'important'); } catch(_) {}
    try { body.style.setProperty('zoom', String(s), 'important'); } catch(_) {}
    // Transform fallback (Safari/Firefox)
    const transformVal = `scale(${s})`;
    const widthVal = `${(100 / s).toFixed(4)}%`;
    const heightVal = `${(100 / s).toFixed(4)}%`;
    body.style.setProperty('transform', transformVal, 'important');
    body.style.setProperty('-webkit-transform', transformVal, 'important');
    body.style.setProperty('transform-origin', 'top left', 'important');
    body.style.setProperty('-webkit-transform-origin', 'top left', 'important');
    body.style.setProperty('width', widthVal, 'important');
    body.style.setProperty('height', heightVal, 'important');
    html.setAttribute('data-app-scale', String(s));
  }

  const BASELINE_WIDTH = 1920;
  const BASELINE_HEIGHT = 1080;
  const LARGE_VIEWPORT_SOFTENING = 0.3;
  const LARGE_VIEWPORT_MIN_SCALE = 0.7;

  function normalizeLargeViewportScale(scale, viewportWidth, viewportHeight, minScale) {
    const softenRatio = (ratio) => {
      const bounded = Math.min(1, Math.max(0, ratio));
      const softened = bounded + (1 - bounded) * LARGE_VIEWPORT_SOFTENING;
      return Math.max(LARGE_VIEWPORT_MIN_SCALE, softened);
    };

    const widthRatio = BASELINE_WIDTH / Math.max(viewportWidth, BASELINE_WIDTH);
    const heightRatio = BASELINE_HEIGHT / Math.max(viewportHeight, BASELINE_HEIGHT);
    const normalized = Math.min(scale, softenRatio(widthRatio), softenRatio(heightRatio));
    return Math.min(scale, Math.max(normalized, minScale));
  }

  // CRITICAL FIX: Prevent rapid re-renders causing flashing
  let isScaling = false;
  let lastAppliedScale = null;
  let scaleTimeout = null;
  let rafPending = false;

  function scaleAppToFit() {
    // Prevent multiple simultaneous calls
    if (isScaling || rafPending) return;
    
    const main = document.getElementById('mainContent');
    const page = document.body;
    if (!main || !page) return;

    // Use requestAnimationFrame to batch DOM reads/writes and prevent flashing
    rafPending = true;
    requestAnimationFrame(() => {
      rafPending = false;
      if (isScaling) return;
      
      isScaling = true;

      // CRITICAL FIX: Calculate natural size WITHOUT resetting transforms to prevent flashing
      // Get current transform scale if it exists
      const currentScale = lastAppliedScale || 1;
      const computedStyle = window.getComputedStyle(page);
      const currentTransform = computedStyle.transform;
      
      // Parse current scale from transform matrix if it exists
      let existingScale = 1;
      if (currentTransform && currentTransform !== 'none') {
        const matrix = currentTransform.match(/matrix\(([^)]+)\)/);
        if (matrix) {
          const values = matrix[1].split(',').map(v => parseFloat(v.trim()));
          if (values.length >= 4) {
            existingScale = Math.sqrt(values[0] * values[0] + values[1] * values[1]);
          }
        }
      }

      // Measure content size accounting for current scale
      const container = main;
      const visibleChildren = Array.from(container.querySelectorAll(':scope > *'))
        .filter(el => el.offsetParent !== null && getComputedStyle(el).position !== 'fixed');

      let left = Infinity, top = Infinity, right = -Infinity, bottom = -Infinity;
      visibleChildren.forEach(el => {
        const r = el.getBoundingClientRect();
        // Adjust for current scale to get natural size
        const docLeft = (r.left + window.scrollX) / existingScale;
        const docTop = (r.top + window.scrollY) / existingScale;
        const docRight = (r.right + window.scrollX) / existingScale;
        const docBottom = (r.bottom + window.scrollY) / existingScale;
        left = Math.min(left, docLeft);
        top = Math.min(top, docTop);
        right = Math.max(right, docRight);
        bottom = Math.max(bottom, docBottom);
      });

      // Fallback if nothing matched
      if (!isFinite(left) || !isFinite(top) || !isFinite(right) || !isFinite(bottom)) {
        const r = container.getBoundingClientRect();
        left = (r.left + window.scrollX) / existingScale;
        top = (r.top + window.scrollY) / existingScale;
        right = (r.right + window.scrollX) / existingScale;
        bottom = (r.bottom + window.scrollY) / existingScale;
      }

      const contentWidth = Math.max(1, right - left);
      const contentHeight = Math.max(1, bottom - top);

      const vw = window.innerWidth;
      const vh = window.innerHeight;

      if (!contentWidth || !contentHeight || !vw || !vh) {
        isScaling = false;
        return;
      }

      let scale = Math.min(vw / contentWidth, vh / contentHeight);
      if (!isFinite(scale) || scale <= 0) scale = 1;
      scale = Math.min(scale, 1);

      // Apply to body with width/height compensation so layout reflows to fit
      // CRITICAL FIX: Use transform3d for better performance and prevent flashing
      const applyScaleToBody = (s) => {
        // Use transform3d to trigger hardware acceleration and prevent flashing
        page.style.setProperty('transform', `scale3d(${s}, ${s}, 1)`, 'important');
        page.style.setProperty('-webkit-transform', `scale3d(${s}, ${s}, 1)`, 'important');
        page.style.setProperty('transform-origin', 'top left', 'important');
        page.style.setProperty('-webkit-transform-origin', 'top left', 'important');
        page.style.setProperty('width', `${(100 / s).toFixed(4)}%`, 'important');
        page.style.setProperty('height', `${(100 / s).toFixed(4)}%`, 'important');
        // Enable will-change for smoother transitions
        page.style.setProperty('will-change', 'transform', 'important');
      };

      let appliedScale = scale;
      const minScale = 0.6;
      const step = 0.05;
      
      // Simplified calculation - apply scale directly without iterative loop
      // This prevents multiple DOM writes that cause flashing
      appliedScale = Math.max(minScale, Math.min(scale, 1));
      const normalizedScale = normalizeLargeViewportScale(appliedScale, vw, vh, minScale);
      appliedScale = normalizedScale;

      // Only update if scale actually changed significantly to prevent unnecessary re-renders
      if (lastAppliedScale !== null && Math.abs(lastAppliedScale - appliedScale) < 0.01) {
        isScaling = false;
        return;
      }

      lastAppliedScale = appliedScale;

      // Apply scale in a single operation to prevent flashing
      applyScaleToBody(appliedScale);

      // Hide scrollbars for a cleaner fit
      document.documentElement.style.overflow = 'hidden';
      document.body.style.overflow = 'hidden';

      // Expose current scale for quick verification in DevTools
      document.documentElement.setAttribute('data-app-scale', String(appliedScale));
      
      // Reset flag after rendering completes
      requestAnimationFrame(() => {
        isScaling = false;
        // Remove will-change after animation completes to free resources
        page.style.setProperty('will-change', 'auto', 'important');
      });
    });
  }

  // Expose for other scripts
  window.scaleAppToFit = scaleAppToFit;

  // Apply on ready (after content becomes visible), and on resize/orientation
  document.addEventListener('DOMContentLoaded', function() {
    const main = document.getElementById('mainContent');
    if (!main) return;

    let tryApplyAttempts = 0;
    const maxAttempts = 10; // Prevent infinite loop
    
    const tryApply = () => {
      if (tryApplyAttempts >= maxAttempts) return; // Stop after max attempts
      tryApplyAttempts++;
      
      const visible = main.offsetParent !== null || getComputedStyle(main).opacity !== '0';
      if (visible) {
        // CRITICAL FIX: Longer delay on initial load to prevent flashing
        if (scaleTimeout) clearTimeout(scaleTimeout);
        scaleTimeout = setTimeout(() => {
          scaleAppToFit();
        }, 300); // Increased from 100ms to 300ms
      } else {
        setTimeout(tryApply, 200);
      }
    };
    tryApply();
  });

  // Ensure after full load (fonts/images) we re-calc - CRITICAL FIX: Only call once
  window.addEventListener('load', () => {
    if (scaleTimeout) clearTimeout(scaleTimeout);
    // CRITICAL FIX: Longer delay after full load to prevent flashing
    scaleTimeout = setTimeout(() => {
      scaleAppToFit();
    }, 400); // Increased from 100ms to 400ms
  });

  // CRITICAL FIX: Aggressive throttling to prevent rapid flashing
  let resizeTimer;
  let lastResizeTime = 0;
  let resizeTimeoutId = null;
  const RESIZE_THROTTLE_MS = 500; // Increased from 300ms to 500ms for better stability
  
  window.addEventListener('resize', () => {
    const now = Date.now();
    // Aggressive throttle to max once per RESIZE_THROTTLE_MS to prevent flashing
    if (now - lastResizeTime < RESIZE_THROTTLE_MS) {
      // Cancel pending calls
      if (resizeTimeoutId) clearTimeout(resizeTimeoutId);
      cancelAnimationFrame(resizeTimer);
      // Schedule a single delayed call
      resizeTimeoutId = setTimeout(() => {
        if (scaleTimeout) clearTimeout(scaleTimeout);
        scaleTimeout = setTimeout(() => {
          scaleAppToFit();
        }, RESIZE_THROTTLE_MS);
        resizeTimeoutId = null;
      }, RESIZE_THROTTLE_MS);
      return;
    }
    lastResizeTime = now;
    // Cancel any pending calls
    if (resizeTimeoutId) clearTimeout(resizeTimeoutId);
    cancelAnimationFrame(resizeTimer);
    if (scaleTimeout) clearTimeout(scaleTimeout);
    // Use longer delay to prevent rapid re-renders
    scaleTimeout = setTimeout(() => {
      scaleAppToFit();
    }, RESIZE_THROTTLE_MS);
  });
  
  window.addEventListener('orientationchange', () => {
    // Cancel all pending calls
    if (resizeTimeoutId) clearTimeout(resizeTimeoutId);
    if (scaleTimeout) clearTimeout(scaleTimeout);
    cancelAnimationFrame(resizeTimer);
    // Longer delay for orientation change to prevent flashing
    scaleTimeout = setTimeout(() => {
      scaleAppToFit();
    }, 800);
  });
})();

// Expose manual control in console
window.setAppScale = function(s) {
  const n = Number(s);
  if (!isFinite(n)) return;
  (function(){
    const html = document.documentElement;
    const body = document.body;
    try { html.style.setProperty('zoom', String(n), 'important'); } catch(_) {}
    try { body.style.setProperty('zoom', String(n), 'important'); } catch(_) {}
    const t = `scale(${n})`;
    const w = `${(100 / n).toFixed(4)}%`;
    const h = `${(100 / n).toFixed(4)}%`;
    body.style.setProperty('transform', t, 'important');
    body.style.setProperty('-webkit-transform', t, 'important');
    body.style.setProperty('transform-origin', 'top left', 'important');
    body.style.setProperty('-webkit-transform-origin', 'top left', 'important');
    body.style.setProperty('width', w, 'important');
    body.style.setProperty('height', h, 'important');
    html.setAttribute('data-app-scale', String(n));
  })();
};

// Toast notification function
function showToast(type, message) {
    const toastEl = document.createElement('div');
    toastEl.className = `toast toast-modern ${type} show`;
    toastEl.setAttribute('role', 'alert');
    toastEl.innerHTML = `
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    const container = document.getElementById('toast-container') || (() => {
        const cont = document.createElement('div');
        cont.id = 'toast-container';
        cont.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 1050;';
        document.body.appendChild(cont);
        return cont;
    })();
    
    container.appendChild(toastEl);
    
    setTimeout(() => {
        toastEl.remove();
    }, 3000);
}

