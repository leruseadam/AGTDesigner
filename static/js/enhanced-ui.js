// Enhanced UI JavaScript
// This file contains all the enhanced UI functionality

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
      handleFiles(e.target.files);
    }
  });
} else {
  console.error('❌ fileInput element not found!');
}

// Also try to attach via main.js handler as backup
if (fileInput && window.TagManager) {
  console.log('✅ Attaching TagManager upload handler as backup');
  fileInput.addEventListener('change', function(e) {
    if (e.target.files && e.target.files.length > 0 && window.TagManager.uploadFile) {
      console.log('🔄 Calling TagManager.uploadFile as backup');
      window.TagManager.uploadFile(e.target.files[0]);
    }
  });
}

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

    // Show Excel loading splash screen - DIRECT METHOD (doesn't wait for TagManager)
    const splashStartTime = Date.now();
    console.log('🎬 UPLOAD: Attempting to show splash for:', file.name);
    const splash = document.getElementById('excelLoadingSplash');
    const filenameElement = document.getElementById('excelLoadingFilename');
    const statusElement = document.getElementById('excelLoadingStatus');
    
    if (splash && filenameElement && statusElement) {
      console.log('🎬 UPLOAD: Showing splash directly');
      filenameElement.textContent = file.name;
      statusElement.textContent = 'Processing...';
      splash.style.display = 'flex';
      splash.style.zIndex = '99999';
    } else {
      console.error('🎬 UPLOAD: Could not find splash elements:', {
        splash: !!splash,
        filenameElement: !!filenameElement,
        statusElement: !!statusElement
      });
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
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData
      });
      console.log('📡 Upload response status:', response.status);
      const data = await response.json();
      console.log('📦 Upload response data:', data);
      
      if (response.ok && data.success) {
        // File uploaded successfully - data is already processed synchronously
        console.log(`File uploaded successfully: ${data.filename}, rows: ${data.rows}`);
        console.log('Upload response data:', data);
        
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
        
        // Hide splash screen with minimum display time (800ms) so user can see it
        hideSplashWithDelay(splashStartTime, 800);
        
        // Clear UI state for fresh data
        if (typeof TagManager !== 'undefined') {
          TagManager.clearUIStateForNewFile(true); // Preserve filters
        }
        
        // Show success message with splash screen
        console.log('✅ Upload successful! Reloading page to show new data...');
        
        // Show success splash instead of alert
        // if (typeof TagManager !== 'undefined' && TagManager.showUploadSuccessSplash) {
        //   TagManager.showUploadSuccessSplash(data.rows);
        // }
        
        // Reload page after a short delay
        setTimeout(() => {
          window.location.reload();
        }, 2000);
        
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
        await Promise.all([
          // Available tags
          (async () => {
            console.log('Fetching available tags...');
            const res = await TagManager.fetchAndUpdateAvailableTags();
            console.log('Available tags result:', res);
          })(),
          // Selected tags
          (async () => {
            console.log('Fetching selected tags...');
            const res = await TagManager.fetchAndUpdateSelectedTags();
            console.log('Selected tags result:', res);
          })(),
          // Filter options
          (async () => {
            console.log('Fetching filter options...');
            await TagManager.fetchAndPopulateFilters();
            console.log('Filter options updated');
          })()
        ]);
        console.timeEnd('post-ready-data-fetch');
        
        // Hide splash screen on success
        if (typeof TagManager !== 'undefined' && TagManager.hideExcelLoadingSplash) {
          TagManager.hideExcelLoadingSplash();
        }
        
        // Show success message
        showToast('success', `File "${filename}" loaded successfully!`);
        
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
        
        // Continue polling in 1 second for faster response
        setTimeout(poll, 1000);
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
        
        // Continue polling in 1 second for faster response
        setTimeout(poll, 1000);
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
      
      // Continue polling in 1 second for faster response
      setTimeout(poll, 1000);
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

    // Hide scrollbars for a cleaner fit
    document.documentElement.style.overflow = 'hidden';
    document.body.style.overflow = 'hidden';

    // Expose current scale for quick verification in DevTools
    document.documentElement.setAttribute('data-app-scale', String(appliedScale));

    // If still no visible change and scale ~1, force a visible 0.9 once
    if (appliedScale >= 0.995) {
      applyGlobalZoom(0.9);
    }
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
    // Ensure visible change regardless
    setTimeout(() => {
      if ((document.documentElement.getAttribute('data-app-scale') || '1') === '1') {
        applyGlobalZoom(0.9);
      }
    }, 400);
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

