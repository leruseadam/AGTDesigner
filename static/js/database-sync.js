// Database synchronization and analytics functions

async function openDatabaseAnalytics() {
  console.log('Opening database analytics...');
  
  // Show loading state
  const loadingHtml = `
    <div class="text-center">
      <div class="spinner-border text-info" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3">Loading database analytics...</p>
    </div>
  `;
  showDatabaseModal('Database Analytics', loadingHtml);
  
  try {
    // Fetch all required data in parallel
    const [healthResponse, statsResponse, vendorStatsResponse, analyticsResponse] = await Promise.all([
      fetch('/api/database-health'),
      fetch('/api/database-stats'),
      fetch('/api/database-vendor-stats'),
      fetch('/api/database-analytics')
    ]);
    
    const health = await healthResponse.json();
    const stats = await statsResponse.json();
    const vendorStats = await vendorStatsResponse.json();
    const analytics = await analyticsResponse.json();
    
    // Create health status indicator with modern design
    const healthColor = health.status === 'healthy' ? 'success' : 
                       health.status === 'warning' ? 'warning' : 'danger';
    const healthIcon = health.status === 'healthy' ? 'check-circle' : 
                      health.status === 'warning' ? 'exclamation-circle' : 'x-circle';
    const healthGradient = health.status === 'healthy' ? 'var(--success-gradient)' : 
                          health.status === 'warning' ? 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)' : 
                          'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
                      
    const healthHtml = `
      <div class="row mb-4">
        <div class="col-md-4">
          <div class="analytics-card health-card">
            <div class="analytics-card-icon" style="background: ${healthGradient};">
              <i class="bi bi-${healthIcon}"></i>
            </div>
            <div class="analytics-card-content">
              <h2 class="analytics-card-value" style="background: ${healthGradient}; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">${health.health_score}%</h2>
              <p class="analytics-card-label">Database Health</p>
              <div class="analytics-card-details">
                <div class="detail-item">
                  <span class="detail-label">Size</span>
                  <span class="detail-value">${health.metrics ? `${health.metrics.database_size_mb.toFixed(1)} MB` : 'N/A'}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Memory</span>
                  <span class="detail-value">${health.metrics ? `${health.metrics.memory_usage_mb.toFixed(1)} MB` : 'N/A'}</span>
              </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="analytics-card stats-card">
            <div class="analytics-card-icon" style="background: var(--primary-gradient);">
              <i class="bi bi-box-seam"></i>
            </div>
            <div class="analytics-card-content">
              <h2 class="analytics-card-value" style="background: var(--primary-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">${health.metrics ? health.metrics.total_products.toLocaleString() : 'N/A'}</h2>
              <p class="analytics-card-label">Total Products</p>
              <div class="analytics-card-badge">
                <span class="badge-modern">${health.metrics ? health.metrics.products_last_24h : '0'} new (24h)</span>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="analytics-card stats-card">
            <div class="analytics-card-icon" style="background: var(--secondary-gradient);">
              <i class="bi bi-flower1"></i>
              </div>
            <div class="analytics-card-content">
              <h2 class="analytics-card-value" style="background: var(--secondary-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">${health.metrics ? health.metrics.total_strains.toLocaleString() : 'N/A'}</h2>
              <p class="analytics-card-label">Total Strains</p>
              <div class="analytics-card-badge">
                <span class="badge-modern">Active</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    // Create vendor statistics section with modern design
    const vendorStatsHtml = `
      <div class="row mb-4">
        <div class="col-md-6">
          <div class="analytics-section-card">
            <div class="analytics-section-header">
              <div class="section-header-icon" style="background: var(--primary-gradient);">
                <i class="bi bi-building"></i>
              </div>
              <div>
                <h5 class="section-title">Vendors</h5>
                <p class="section-subtitle">${vendorStats.vendors ? vendorStats.vendors.length : 0} total vendors</p>
              </div>
            </div>
            <div class="analytics-section-body">
              ${vendorStats.vendors && vendorStats.vendors.length > 0 ? 
                vendorStats.vendors.map((vendor, index) => 
                  `<div class="analytics-list-item ${index < vendorStats.vendors.length - 1 ? 'has-border' : ''}">
                    <div class="list-item-content">
                      <h6 class="list-item-title">${vendor.vendor || 'Unknown'}</h6>
                      <p class="list-item-meta">
                        <span><i class="bi bi-tag"></i> ${vendor.unique_brands || 0} brands</span>
                        <span><i class="bi bi-grid"></i> ${vendor.unique_product_types || 0} types</span>
                      </p>
                    </div>
                    <div class="list-item-badge">
                      <span class="badge-gradient">${vendor.product_count || 0}</span>
                    </div>
                  </div>`
                ).join('') : 
                '<div class="empty-state"><i class="bi bi-inbox"></i><p>No vendor data available</p></div>'
              }
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="analytics-section-card">
            <div class="analytics-section-header">
              <div class="section-header-icon" style="background: var(--secondary-gradient);">
                <i class="bi bi-grid-3x3-gap"></i>
              </div>
              <div>
                <h5 class="section-title">Product Types</h5>
                <p class="section-subtitle">${vendorStats.product_types ? vendorStats.product_types.length : 0} categories</p>
              </div>
            </div>
            <div class="analytics-section-body">
              ${vendorStats.product_types && vendorStats.product_types.length > 0 ? 
                vendorStats.product_types.map((type, index) => 
                  `<div class="analytics-list-item ${index < vendorStats.product_types.length - 1 ? 'has-border' : ''}">
                    <div class="list-item-content">
                      <h6 class="list-item-title">${type.product_type || 'Unknown'}</h6>
                      <p class="list-item-meta">
                        <span><i class="bi bi-building"></i> ${type.unique_vendors || 0} vendors</span>
                        <span><i class="bi bi-tag"></i> ${type.unique_brands || 0} brands</span>
                      </p>
                    </div>
                    <div class="list-item-badge">
                      <span class="badge-gradient badge-success">${type.product_count || 0}</span>
                    </div>
                  </div>`
                ).join('') : 
                '<div class="empty-state"><i class="bi bi-inbox"></i><p>No product type data available</p></div>'
              }
            </div>
          </div>
        </div>
      </div>
    `;

    // Create daily usage graph section with modern design
    const vendorBrandsHtml = `
      <div class="row mb-4">
        <div class="col-12">
          <div class="analytics-section-card">
            <div class="analytics-section-header">
              <div class="section-header-icon" style="background: var(--third-gradient);">
                <i class="bi bi-graph-up-arrow"></i>
              </div>
              <div>
                <h5 class="section-title">Usage Analytics</h5>
                <p class="section-subtitle">Daily activity trends</p>
              </div>
            </div>
            <div class="analytics-section-body">
              <div class="chart-container">
                <canvas id="usageChart"></canvas>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    // Create summary section with modern design
    const summaryHtml = `
      <div class="row mb-4">
        <div class="col-12">
          <div class="analytics-info-card">
            <div class="info-card-icon">
              <i class="bi bi-info-circle"></i>
            </div>
            <div class="info-card-content">
              <h6 class="info-card-title">Analytics Summary</h6>
              <p class="info-card-text">
              ${health.metrics && health.metrics.total_products > 0 ? 
                  `This comprehensive dashboard shows real-time statistics from your product database with <strong>${health.metrics.total_products.toLocaleString()}</strong> products currently loaded. Data is automatically updated each time you upload new Excel files.` :
                'Upload Excel files to populate the database and unlock detailed vendor analytics, strain statistics, and performance metrics.'
              }
            </p>
            ${stats.error || vendorStats.error || analytics.error ? 
                `<div class="info-card-warning">
                  <i class="bi bi-exclamation-triangle"></i>
                  <span>Some data may be limited due to: ${[stats.error, vendorStats.error, analytics.error].filter(e => e).join(', ')}</span>
                </div>` : 
              ''
            }
            </div>
          </div>
        </div>
      </div>
    `;

    // Add export button with modern design
    const exportButtonHtml = `
      <div class="row">
        <div class="col-12">
          <div class="analytics-actions">
            <button class="btn-analytics-export" onclick="exportDatabase()">
              <i class="bi bi-download"></i>
              <span>Export Database</span>
          </button>
          </div>
        </div>
      </div>
    `;

    // Combine all sections
    const modalContent = `
      ${healthHtml}
      ${vendorStatsHtml}
      ${vendorBrandsHtml}
      ${summaryHtml}
      ${exportButtonHtml}
    `;

    // Update modal content
    showDatabaseModal('Database Analytics', modalContent);
    
    // Initialize the usage chart after the modal is shown
    const modal = document.getElementById('databaseModal');
    modal.addEventListener('shown.bs.modal', function () {
      // Get historical usage data - handle case where upload_stats might not exist
      const usageData = (window.upload_stats && window.upload_stats.historical) ? window.upload_stats.historical : [];
      
      // Only create chart if we have valid data
      if (usageData && usageData.length > 0) {
        const dates = usageData.map(d => new Date(d.date).toLocaleDateString());

        const ctx = document.getElementById('usageChart').getContext('2d');
        new Chart(ctx, {
        type: 'line',
        data: {
          labels: dates,
          datasets: [
            {
              label: 'File Uploads',
              data: usageData.map(d => d.ready_files),
              borderColor: '#a084e8',
              backgroundColor: 'rgba(160, 132, 232, 0.1)',
              tension: 0.4,
              fill: true,
              borderWidth: 2
            },
            {
              label: 'Products Added',
              data: usageData.map(d => d.total_files),
              borderColor: '#ff8fab',
              backgroundColor: 'rgba(255, 143, 171, 0.1)',
              tension: 0.4,
              fill: true,
              borderWidth: 2
            },
            {
              label: 'Memory Usage (MB)',
              data: usageData.map(d => d.memory_usage_mb),
              borderColor: '#43e97b',
              backgroundColor: 'rgba(67, 233, 123, 0.1)',
              tension: 0.4,
              fill: true,
              borderWidth: 2
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
              labels: {
                color: 'rgba(255, 255, 255, 0.8)'
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: {
                color: 'rgba(160, 132, 232, 0.15)'
              },
              ticks: {
                color: 'rgba(255, 255, 255, 0.7)',
                font: {
                  size: 11
                }
              }
            },
            x: {
              grid: {
                color: 'rgba(160, 132, 232, 0.15)'
              },
              ticks: {
                color: 'rgba(255, 255, 255, 0.7)',
                font: {
                  size: 11
                }
              }
            }
          }
        }
      });
        } else {
          // No historical data available
          const chartContainer = document.getElementById('usageChart');
          if (chartContainer) {
            chartContainer.parentElement.innerHTML = '<div class="empty-state"><i class="bi bi-graph-down"></i><p>No historical usage data available</p></div>';
          }
        }
      });

  } catch (error) {
    console.error('Error loading database analytics:', error);
    showDatabaseModal('Database Analytics', `
      <div class="alert alert-danger">
        <h6>Error Loading Analytics</h6>
        <p class="mb-0">Failed to load database analytics: ${error.message}</p>
      </div>
    `);
  }
}

async function exportDatabase() {
  // Show splash screen
  showExportSplash();
  
  try {
    const response = await fetch('/api/database-export');
    
    if (!response.ok) {
      // Try to read detailed error message from JSON response
      let errorMessage = `Export failed: ${response.status} ${response.statusText}`;
      let errorDetails = null;
      try {
        const responseText = await response.text();
        try {
          const data = JSON.parse(responseText);
          if (data && data.error) {
            errorMessage = data.error;
            if (data.details) {
              errorDetails = data.details;
            }
            if (data.type) {
              errorMessage += ` (${data.type})`;
            }
          } else if (data && data.message) {
            errorMessage = data.message;
          }
        } catch (parseError) {
          // If response isn't JSON, try to extract error from text
          if (responseText && responseText.length < 500) {
            errorMessage = responseText;
          }
        }
      } catch (readError) {
        console.error('Error reading error response:', readError);
      }
      
      console.error('Database export error:', errorMessage);
      if (errorDetails) {
        console.error('Error details:', errorDetails);
      }
      
      throw new Error(errorMessage);
    }
    
    // Get the filename from the Content-Disposition header
    const contentDisposition = response.headers.get('Content-Disposition');
    const filenameMatch = contentDisposition && contentDisposition.match(/filename="(.+)"/);
    const filename = filenameMatch ? filenameMatch[1] : 'product_database_export.xlsx';
    
    // Create a blob from the response
    const blob = await response.blob();
    
    // Create a download link and trigger it
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
    
    // Hide splash screen and show success message
    hideExportSplash();
    const successToast = new bootstrap.Toast(document.getElementById('successToast'));
    document.getElementById('successToastMessage').textContent = 'Database exported successfully';
    successToast.show();
    
  } catch (error) {
    console.error('Error exporting database:', error);
    hideExportSplash();
    const errorToast = new bootstrap.Toast(document.getElementById('errorToast'));
    document.getElementById('errorToastMessage').textContent = `Failed to export database: ${error.message}`;
    errorToast.show();
  }
}

function showExportSplash() {
  // Create splash screen HTML
  const splashHtml = `
    <div id="exportSplash" class="export-splash-overlay">
      <div class="export-splash-content">
        <div class="export-splash-icon">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <h4 class="export-splash-title">Exporting Database</h4>
        <p class="export-splash-message">Preparing your database export...</p>
        <div class="export-splash-progress">
          <div class="progress">
            <div class="progress-bar progress-bar-striped progress-bar-animated" 
                 role="progressbar" style="width: 0%"></div>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Add to body
  document.body.insertAdjacentHTML('beforeend', splashHtml);
  
  // Animate progress bar
  const progressBar = document.querySelector('#exportSplash .progress-bar');
  let progress = 0;
  const interval = setInterval(() => {
    progress += Math.random() * 15;
    if (progress > 90) progress = 90;
    progressBar.style.width = progress + '%';
  }, 200);
  
  // Store interval ID for cleanup
  document.getElementById('exportSplash').dataset.intervalId = interval;
}

function hideExportSplash() {
  const splash = document.getElementById('exportSplash');
  if (splash) {
    // Clear progress animation
    const intervalId = splash.dataset.intervalId;
    if (intervalId) {
      clearInterval(parseInt(intervalId));
    }
    
    // Animate out
    splash.style.opacity = '0';
    splash.style.transform = 'scale(0.8)';
    
    setTimeout(() => {
      splash.remove();
    }, 300);
  }
}

// Helper function to show database modal
function showDatabaseModal(title, content) {
  const modal = document.getElementById('databaseModal');
  if (!modal) {
    console.error('Database modal element not found');
    return;
  }
  
  const modalTitle = modal.querySelector('.modal-title');
  const modalBody = modal.querySelector('.modal-body');
  
  if (modalTitle) modalTitle.textContent = title;
  if (modalBody) modalBody.innerHTML = content;
  
  const bsModal = new bootstrap.Modal(modal);
  bsModal.show();
}