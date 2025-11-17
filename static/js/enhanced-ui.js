// Enhanced UI JavaScript
// This file contains all the enhanced UI functionality

// Immediately attach handlers - page should already be loaded
console.log('🔧 Enhanced UI: Loading...');

// Helper function to show Excel splash - callable from anywhere
window.showExcelUploadSplash = function(fileName) {
  console.log('🎬 showExcelUploadSplash called for:', fileName);
  const splash = document.getElementById('excelLoadingSplash');
  if (!splash) {
    console.error('❌ excelLoadingSplash element not found!');
    // Try again after a short delay
    setTimeout(() => {
      const retrySplash = document.getElementById('excelLoadingSplash');
      if (retrySplash) {
        window.showExcelUploadSplash(fileName);
      } else {
        console.error('❌ excelLoadingSplash still not found after retry');
      }
    }, 100);
    return;
  }
  
  console.log('✅ Splash element found, showing...');
  splash.classList.remove('fade-out', 'd-none', 'hidden');
  splash.style.setProperty('display', 'flex', 'important');
  splash.style.setProperty('z-index', '999999', 'important');
  splash.style.setProperty('position', 'fixed', 'important');
  splash.style.setProperty('top', '0', 'important');
  splash.style.setProperty('left', '0', 'important');
  splash.style.setProperty('width', '100%', 'important');
  splash.style.setProperty('height', '100%', 'important');
  splash.style.setProperty('visibility', 'visible', 'important');
  splash.style.setProperty('opacity', '1', 'important');
  splash.style.setProperty('background', 'rgba(0, 0, 0, 0.8)', 'important');
  
  // Remove inline style="display: none" if present
  if (splash.hasAttribute('style')) {
    const currentStyle = splash.getAttribute('style');
    if (currentStyle.includes('display: none')) {
      splash.setAttribute('style', currentStyle.replace(/display:\s*none[;]?/gi, ''));
    }
  }
  
  const filenameElement = document.getElementById('excelLoadingFilename');
  const statusElement = document.getElementById('excelLoadingStatus');
  if (filenameElement) filenameElement.textContent = fileName || 'Processing...';
  if (statusElement) statusElement.textContent = 'Uploading file...';
  
  // Force reflow
  splash.offsetHeight;
  void splash.offsetWidth;
  
  console.log('✅ Excel splash shown with display:', window.getComputedStyle(splash).display);
};

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
      
      // Show splash IMMEDIATELY before calling handleFiles
      if (typeof window.showExcelUploadSplash === 'function') {
        window.showExcelUploadSplash(e.target.files[0].name);
      } else {
        console.error('❌ showExcelUploadSplash function not available');
      }
      
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
  if (files.length > 0) {
    const file = files[0];
    console.log('📄 File selected:', file.name, 'size:', file.size);
    
    // CRITICAL: Show Excel loading splash screen FIRST before anything else
    const splashStartTime = Date.now();
    console.log('🎬 UPLOAD: Showing splash IMMEDIATELY for:', file.name);
    
    // Use global function to show splash
    if (typeof window.showExcelUploadSplash === 'function') {
      window.showExcelUploadSplash(file.name);
    }
    
    function showExcelSplash(splash, filenameElement, statusElement, fileName) {
      if (!splash) {
        console.error('❌ Splash element is null!');
        return;
      }
      
      console.log('🎬 UPLOAD: Splash elements found - displaying NOW');
      if (filenameElement) filenameElement.textContent = fileName;
      if (statusElement) statusElement.textContent = 'Uploading file...';
      
      // Remove any classes that might hide it
      splash.classList.remove('fade-out', 'd-none', 'hidden');
      
      // CRITICAL: Set all visibility properties aggressively with !important
      splash.style.setProperty('display', 'flex', 'important');
      splash.style.setProperty('z-index', '999999', 'important');
      splash.style.setProperty('position', 'fixed', 'important');
      splash.style.setProperty('top', '0', 'important');
      splash.style.setProperty('left', '0', 'important');
      splash.style.setProperty('width', '100%', 'important');
      splash.style.setProperty('height', '100%', 'important');
      splash.style.setProperty('visibility', 'visible', 'important');
      splash.style.setProperty('opacity', '1', 'important');
      splash.style.setProperty('pointer-events', 'auto', 'important');
      splash.style.setProperty('background', 'rgba(0, 0, 0, 0.8)', 'important');
      
      // Remove inline style="display: none" if present
      if (splash.hasAttribute('style')) {
        const currentStyle = splash.getAttribute('style');
        if (currentStyle.includes('display: none')) {
          splash.setAttribute('style', currentStyle.replace(/display:\s*none[;]?/gi, ''));
        }
      }
      
      // Force multiple reflows to ensure visibility
      splash.offsetHeight;
      void splash.offsetWidth;
      
      // Force browser to repaint in next frame
      requestAnimationFrame(() => {
        splash.style.setProperty('display', 'flex', 'important');
        const computed = window.getComputedStyle(splash);
        console.log('✅ Excel splash forced repaint:', {
          display: splash.style.display,
          computedDisplay: computed.display,
          zIndex: splash.style.zIndex,
          computedZIndex: computed.zIndex,
          visibility: computed.visibility,
          opacity: computed.opacity
        });
        
        // Double-check after a short delay
        setTimeout(() => {
          const finalCheck = window.getComputedStyle(splash);
          if (finalCheck.display === 'none' || finalCheck.visibility === 'hidden') {
            console.error('❌ Splash still hidden after all attempts!', {
              display: finalCheck.display,
              visibility: finalCheck.visibility,
              opacity: finalCheck.opacity,
              zIndex: finalCheck.zIndex
            });
            // Last resort: try to force it again
            splash.style.setProperty('display', 'flex', 'important');
            splash.style.setProperty('visibility', 'visible', 'important');
          } else {
            console.log('✅ Splash confirmed visible');
          }
        }, 50);
      });
      
      console.log('✅ SPLASH SHOWN - display:', splash.style.display);
    }
    
    // Try to show splash immediately
    let splash = document.getElementById('excelLoadingSplash');
    let filenameElement = document.getElementById('excelLoadingFilename');
    let statusElement = document.getElementById('excelLoadingStatus');
    
    if (splash) {
      // Show splash even if filename/status elements aren't found
      showExcelSplash(splash, filenameElement, statusElement, file.name);
    } else {
      // If not found, wait a bit and try again (for cases where DOM isn't ready)
      console.warn('⚠️ Excel splash element not found immediately, retrying...');
      const retryInterval = setInterval(() => {
        splash = document.getElementById('excelLoadingSplash');
        filenameElement = document.getElementById('excelLoadingFilename');
        statusElement = document.getElementById('excelLoadingStatus');
        if (splash) {
          clearInterval(retryInterval);
          showExcelSplash(splash, filenameElement, statusElement, file.name);
        }
      }, 50);
      
      // Stop retrying after 1 second
      setTimeout(() => {
        clearInterval(retryInterval);
        if (!splash) {
          console.error('❌ Could not find Excel splash element after retry');
        }
      }, 1000);
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
      
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData
      });
      console.log('📡 Upload response status:', response.status);
      
      // Update splash status
      if (statusElement) statusElement.textContent = 'Processing data...';
      
      const data = await response.json();
      console.log('📦 Upload response data:', data);
      
      if (response.ok && data.success) {
        // For PythonAnywhere/web deployment the file continues processing in background.
        if (data.processing) {
          console.log(`Background processing required for ${data.filename || file.name}`);
          
          // Keep splash visible and update messaging while we wait for processing to finish.
          if (statusElement) statusElement.textContent = 'Processing file...';
          if (typeof TagManager !== 'undefined' && TagManager.updateExcelLoadingStatus) {
            TagManager.updateExcelLoadingStatus('Processing file...');
          }
          
          // Start polling backend until the upload is ready, then stop normal success flow.
          if (typeof pollUploadStatus === 'function') {
            pollUploadStatus(data.filename || file.name);
          } else {
            console.warn('pollUploadStatus function not available; using manual refresh');

            // Hide Excel splash FIRST
            const excelSplash = document.getElementById('excelLoadingSplash');
            if (excelSplash) excelSplash.style.display = 'none';

            // CRITICAL: Show tag loading splash immediately
            console.log('🎬 Background processing mode, showing tag loading splash...');
            if (typeof TagManager !== 'undefined' && TagManager.showTagLoadingSplash) {
              TagManager.showTagLoadingSplash('Loading tags from uploaded file...');
            } else {
              // Fallback if TagManager not available
              const tagSplash = document.getElementById('tagLoadingSplash');
              const statusElement = document.getElementById('tagLoadingStatus');
              if (tagSplash) {
                if (statusElement) statusElement.textContent = 'Loading tags from uploaded file...';
                tagSplash.classList.remove('fade-out', 'd-none', 'hidden');
                tagSplash.style.setProperty('display', 'flex', 'important');
                tagSplash.style.setProperty('z-index', '999999', 'important');
                tagSplash.style.setProperty('opacity', '1', 'important');
                tagSplash.style.setProperty('visibility', 'visible', 'important');
                console.log('✅ Tag loading splash shown (fallback method)');
              }
            }

            setTimeout(() => {
              console.log('🔄 Starting manual tag refresh...');
              if (typeof TagManager !== 'undefined' && TagManager.refreshTagLists) {
                TagManager.refreshTagLists({ preserveFilters: true, force: true })
                  .then(() => {
                    console.log('✅ Manual tag refresh complete');
                  })
                  .catch(err => {
                    console.error('Manual refreshTagLists failed', err);
                    if (TagManager.hideTagLoadingSplash) {
                      TagManager.hideTagLoadingSplash();
                    }
                  });
              } else if (typeof TagManager !== 'undefined') {
                console.log('⚠️ Using fallback individual tag fetch methods');
                Promise.all([
                  TagManager.fetchAndUpdateAvailableTags?.(),
                  TagManager.fetchAndUpdateSelectedTags?.(),
                  TagManager.fetchAndPopulateFilters?.()
                ]).then(() => {
                  console.log('✅ Fallback tag refresh complete');
                  if (TagManager.hideTagLoadingSplash) {
                    TagManager.hideTagLoadingSplash();
                  }
                }).catch(err => {
                  console.error('Fallback tag refresh failed', err);
                  if (TagManager.hideTagLoadingSplash) {
                    TagManager.hideTagLoadingSplash();
                  }
                });
              }
            }, 2000);
          }
          return;
        }

        // File uploaded successfully - data is already processed synchronously
        console.log(`File uploaded successfully: ${data.filename}, rows: ${data.rows}`);
        console.log('Upload response data:', data);
        
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
            return;
          }
        }
        
        // Hide Excel splash and show tag loading splash before refreshing
        const splashEl = document.getElementById('excelLoadingSplash');
        if (splashEl) splashEl.style.display = 'none';

        // CRITICAL: Show tag loading splash immediately and keep it visible
        console.log('🎬 Excel upload complete, showing tag loading splash...');
        if (typeof TagManager !== 'undefined' && TagManager.showTagLoadingSplash) {
          TagManager.showTagLoadingSplash('Loading tags from uploaded file...');
        } else {
          // Fallback if TagManager not available
          const tagSplash = document.getElementById('tagLoadingSplash');
          const statusElement = document.getElementById('tagLoadingStatus');
          if (tagSplash) {
            if (statusElement) statusElement.textContent = 'Loading tags from uploaded file...';
            tagSplash.classList.remove('fade-out', 'd-none', 'hidden');
            tagSplash.style.setProperty('display', 'flex', 'important');
            tagSplash.style.setProperty('z-index', '999999', 'important');
            tagSplash.style.setProperty('opacity', '1', 'important');
            tagSplash.style.setProperty('visibility', 'visible', 'important');
            console.log('✅ Tag loading splash shown (fallback method)');
          }
        }

        if (typeof TagManager !== 'undefined') {
          try {
            TagManager.clearUIStateForNewFile(true); // keep filters
            // Kick off refresh without awaiting to prevent UI stall
            setTimeout(() => {
              if (TagManager.refreshTagLists) {
                console.time('post-upload-refresh-async');
                console.log('🔄 Starting tag refresh after Excel upload...');
                TagManager.refreshTagLists({ preserveFilters: true, force: true })
                  .then(() => {
                    console.log('✅ Tag refresh complete after Excel upload');
                  })
                  .finally(() => console.timeEnd('post-upload-refresh-async'))
                  .catch(err => {
                    console.error('Async refreshTagLists failed', err);
                    // Hide splash on error
                    if (TagManager.hideTagLoadingSplash) {
                      TagManager.hideTagLoadingSplash();
                    }
                    // Don't reload - just show error and let user retry
                    showToast('error', 'Failed to refresh tags. Please try refreshing manually.');
                  });
              } else {
                // Fallback individual fetches without await
                console.log('⚠️ refreshTagLists not available, using fallback methods');
                Promise.all([
                  TagManager.fetchAndUpdateAvailableTags?.(),
                  TagManager.fetchAndUpdateSelectedTags?.(),
                  TagManager.fetchAndPopulateFilters?.()
                ]).then(() => {
                  console.log('✅ Fallback tag refresh complete');
                  if (TagManager.hideTagLoadingSplash) {
                    TagManager.hideTagLoadingSplash();
                  }
                }).catch(err => {
                  console.error('Fallback tag refresh failed', err);
                  if (TagManager.hideTagLoadingSplash) {
                    TagManager.hideTagLoadingSplash();
                  }
                });
              }
            }, 0);
          } catch (e) {
            console.error('Post-upload async refresh setup failed', e);
            // Don't reload on error - just log it and let the user continue
            // The tag loading splash will handle showing loading state
            if (TagManager && TagManager.hideTagLoadingSplash) {
              TagManager.hideTagLoadingSplash();
            }
          }
        } else {
          // TagManager not available - try to show splash manually and fetch tags
          console.warn('TagManager not available, attempting manual tag refresh');
          const tagSplash = document.getElementById('tagLoadingSplash');
          const statusElement = document.getElementById('tagLoadingStatus');
          if (tagSplash) {
            if (statusElement) statusElement.textContent = 'Loading tags from uploaded file...';
            tagSplash.style.display = 'flex';
          }
          // Try to fetch tags manually
          setTimeout(() => {
            fetch('/api/available-tags')
              .then(response => response.json())
              .then(data => {
                if (data.tags) {
                  console.log('Tags fetched manually:', data.tags.length);
                }
                if (tagSplash) {
                  tagSplash.style.display = 'none';
                }
              })
              .catch(err => {
                console.error('Manual tag fetch failed:', err);
                if (tagSplash) {
                  tagSplash.style.display = 'none';
                }
              });
          }, 100);
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
      // Hide splash screen on error with minimum display time
      hideSplashWithDelay(splashStartTime, 800);
      showToast("error", 'Upload failed');
    } finally {
      TagManager.setLoading(false);
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
function pollUploadStatus(filename) {
  let pollCount = 0;
  const maxPolls = 120; // Poll for up to 2 minutes (120 * 1 second)
  
  // Show tag loading splash immediately when polling starts
  // This ensures user sees feedback during the entire waiting period
  console.log('🎬 Polling started, showing tag loading splash...');
  if (typeof TagManager !== 'undefined' && TagManager.showTagLoadingSplash) {
    TagManager.showTagLoadingSplash('Processing file and loading tags...');
  } else {
    // Fallback: show tag loading splash directly
    const tagSplash = document.getElementById('tagLoadingSplash');
    if (tagSplash) {
      tagSplash.classList.remove('fade-out', 'd-none', 'hidden');
      tagSplash.style.setProperty('display', 'flex', 'important');
      tagSplash.style.setProperty('z-index', '999999', 'important');
      tagSplash.style.setProperty('visibility', 'visible', 'important');
      tagSplash.style.setProperty('opacity', '1', 'important');
      const statusEl = document.getElementById('tagLoadingStatus');
      if (statusEl) statusEl.textContent = 'Processing file and loading tags...';
    }
  }
  
  const poll = async () => {
    try {
      const response = await fetch(`/api/upload-status?filename=${encodeURIComponent(filename)}`);
      const data = await response.json();
      
      console.log(`Upload status for ${filename}: ${data.status}`);
      console.log('Upload status response:', data);
      
      // Update splash status during polling
      if (data.status === 'processing') {
        if (typeof TagManager !== 'undefined' && TagManager.showTagLoadingSplash) {
          TagManager.showTagLoadingSplash('Processing file...');
        } else {
          const tagSplash = document.getElementById('tagLoadingSplash');
          const statusEl = document.getElementById('tagLoadingStatus');
          if (tagSplash && statusEl) {
            statusEl.textContent = 'Processing file...';
          }
        }
      }
      
      if (data.status === 'ready') {
        // File processing is complete, fetch updated data
        console.log(`File processing complete for ${filename}, fetching updated data...`);
        
        // Clear any existing UI state to ensure fresh start
        if (typeof TagManager !== 'undefined') {
          // Use the new comprehensive UI clearing function
          TagManager.clearUIStateForNewFile(true); // Preserve filters during UI refresh
        }
        
        console.log('File processing complete, updating UI...');

        // Hide Excel splash FIRST
        if (typeof TagManager !== 'undefined' && TagManager.hideExcelLoadingSplash) {
          TagManager.hideExcelLoadingSplash();
        } else {
          const s = document.getElementById('excelLoadingSplash');
          if (s) s.style.display = 'none';
        }

        // CRITICAL: Show tag loading splash immediately and keep it visible
        console.log('🎬 File processing complete, showing tag loading splash...');
        if (typeof TagManager !== 'undefined' && TagManager.showTagLoadingSplash) {
          TagManager.showTagLoadingSplash('Loading tags from uploaded file...');
        } else {
          // Fallback if TagManager not available
          const tagSplash = document.getElementById('tagLoadingSplash');
          const statusElement = document.getElementById('tagLoadingStatus');
          if (tagSplash) {
            if (statusElement) statusElement.textContent = 'Loading tags from uploaded file...';
            tagSplash.classList.remove('fade-out', 'd-none', 'hidden');
            tagSplash.style.setProperty('display', 'flex', 'important');
            tagSplash.style.setProperty('z-index', '999999', 'important');
            tagSplash.style.setProperty('opacity', '1', 'important');
            tagSplash.style.setProperty('visibility', 'visible', 'important');
            console.log('✅ Tag loading splash shown (fallback method)');
          }
        }

        // Show success toast
        showToast('success', `File "${filename}" loaded successfully!`);

        // CRITICAL: Update file info display immediately
        const fileInfoText = document.getElementById('fileInfoText');
        if (fileInfoText && filename) {
          fileInfoText.textContent = filename;
          console.log(`✅ Updated fileInfoText with: ${filename}`);
        }
        
        // Fetch all updated data in parallel to avoid serial bottlenecks
        console.time('post-ready-data-fetch');
        console.log('🔄 Starting tag refresh after file processing complete...');
        if (typeof TagManager !== 'undefined' && TagManager.refreshTagLists) {
          await TagManager.refreshTagLists({ preserveFilters: true, force: true });
          console.log('✅ Tag refresh complete after file processing');
        } else if (typeof TagManager !== 'undefined') {
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
          console.log('✅ Fallback tag refresh complete');
          // Hide splash after fallback completes
          if (TagManager.hideTagLoadingSplash) {
            TagManager.hideTagLoadingSplash();
          }
        } else {
          // TagManager not available - try manual fetch
          console.warn('TagManager not available, attempting manual tag refresh');
          const tagSplash = document.getElementById('tagLoadingSplash');
          await fetch('/api/available-tags')
            .then(response => response.json())
            .then(data => {
              if (data.tags) {
                console.log('Tags fetched manually:', data.tags.length);
              }
              if (tagSplash) {
                tagSplash.style.display = 'none';
              }
            })
            .catch(err => {
              console.error('Manual tag fetch failed:', err);
              if (tagSplash) {
                tagSplash.style.display = 'none';
              }
            });
        }
        console.timeEnd('post-ready-data-fetch');
        
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

  function scaleAppToFit() {
    const main = document.getElementById('mainContent');
    const page = document.body;
    if (!main || !page) return;

    // Temporarily reset transform to measure full, natural page size
    const prevTransformMain = main.style.transform;
    const prevTransformBody = page.style.transform;
    const prevWidthBody = page.style.width;
    const prevHeightBody = page.style.height;
    main.style.transform = 'none';
    page.style.transform = 'none';
    page.style.width = '';
    page.style.height = '';

    // Compute a visual bounding box of visible, non-fixed children within main content
    const container = main;
    const visibleChildren = Array.from(container.querySelectorAll(':scope > *'))
      .filter(el => el.offsetParent !== null && getComputedStyle(el).position !== 'fixed');

    let left = Infinity, top = Infinity, right = -Infinity, bottom = -Infinity;
    visibleChildren.forEach(el => {
      const r = el.getBoundingClientRect();
      const docLeft = r.left + window.scrollX;
      const docTop = r.top + window.scrollY;
      const docRight = r.right + window.scrollX;
      const docBottom = r.bottom + window.scrollY;
      left = Math.min(left, docLeft);
      top = Math.min(top, docTop);
      right = Math.max(right, docRight);
      bottom = Math.max(bottom, docBottom);
    });

    // Fallback if nothing matched
    if (!isFinite(left) || !isFinite(top) || !isFinite(right) || !isFinite(bottom)) {
      const r = container.getBoundingClientRect();
      left = r.left + window.scrollX;
      top = r.top + window.scrollY;
      right = r.right + window.scrollX;
      bottom = r.bottom + window.scrollY;
    }

    const contentWidth = Math.max(1, right - left);
    const contentHeight = Math.max(1, bottom - top);

    const vw = window.innerWidth;
    const vh = window.innerHeight;

    if (!contentWidth || !contentHeight || !vw || !vh) {
      main.style.transform = prevTransformMain;
      page.style.transform = prevTransformBody;
      page.style.width = prevWidthBody;
      page.style.height = prevHeightBody;
      return;
    }

    let scale = Math.min(vw / contentWidth, vh / contentHeight);
    if (!isFinite(scale) || scale <= 0) scale = 1;
    scale = Math.min(scale, 1);

    // Apply to body with width/height compensation so layout reflows to fit
    const applyScaleToBody = (s) => {
      page.style.transform = `scale(${s})`;
      page.style.transformOrigin = 'top left';
      page.style.width = `${(100 / s).toFixed(4)}%`;
      page.style.height = `${(100 / s).toFixed(4)}%`;
    };

    let appliedScale = scale;
    const minScale = 0.6;
    const step = 0.05;
    while (appliedScale >= minScale) {
      applyScaleToBody(appliedScale);
      const r = main.getBoundingClientRect();
      if (r.width <= vw && r.height <= vh) break;
      appliedScale = Math.max(minScale, +(appliedScale - step).toFixed(3));
      if (appliedScale === minScale) {
        applyScaleToBody(appliedScale);
        break;
      }
    }

    const normalizedScale = normalizeLargeViewportScale(appliedScale, vw, vh, minScale);
    if (normalizedScale !== appliedScale) {
      appliedScale = normalizedScale;
      applyScaleToBody(appliedScale);
    }

    // Hide scrollbars for a cleaner fit
    document.documentElement.style.overflow = 'hidden';
    document.body.style.overflow = 'hidden';

    // Expose current scale for quick verification in DevTools
    document.documentElement.setAttribute('data-app-scale', String(appliedScale));
  }

  // Expose for other scripts
  window.scaleAppToFit = scaleAppToFit;

  // Apply on ready (after content becomes visible), and on resize/orientation
  document.addEventListener('DOMContentLoaded', function() {
    const main = document.getElementById('mainContent');
    if (!main) return;

    const tryApply = () => {
      const visible = main.offsetParent !== null || getComputedStyle(main).opacity !== '0';
      if (visible) {
        requestAnimationFrame(scaleAppToFit);
      } else {
        setTimeout(tryApply, 200);
      }
    };
    tryApply();
  });

  // Ensure after full load (fonts/images) we re-calc
  window.addEventListener('load', () => {
    requestAnimationFrame(scaleAppToFit);
    setTimeout(scaleAppToFit, 0);
    setTimeout(scaleAppToFit, 250);
  });

  let resizeTimer;
  window.addEventListener('resize', () => {
    cancelAnimationFrame(resizeTimer);
    resizeTimer = requestAnimationFrame(scaleAppToFit);
  });
  window.addEventListener('orientationchange', () => setTimeout(scaleAppToFit, 0));
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

