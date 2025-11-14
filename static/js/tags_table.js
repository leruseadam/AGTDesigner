// Classic types that should show "Lineage" instead of "Brand"
if (typeof window.CLASSIC_TYPES === 'undefined') {
  window.CLASSIC_TYPES = [
    "flower", "pre-roll", "concentrate", "infused pre-roll", 
    "solventless concentrate", "vape cartridge", "rso/co2 tankers"
  ];
}
// Use window.CLASSIC_TYPES directly to avoid duplicate const declaration
// Reference window.CLASSIC_TYPES directly instead of creating a const
// This prevents "Identifier 'CLASSIC_TYPES' has already been declared" errors

// Lineage abbreviation mapping (matching Python version)
// Use global ABBREVIATED_LINEAGE from main.js to avoid duplicate declaration
// If not defined, create it as a fallback
if (typeof window.ABBREVIATED_LINEAGE === 'undefined') {
    window.ABBREVIATED_LINEAGE = {
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
}
// Use window.ABBREVIATED_LINEAGE directly to avoid const redeclaration
// This will reference the one from main.js if it exists, or our fallback

// Use full lineage names for all dropdowns
const getUniqueLineages = () => {
  return ['SATIVA','INDICA','HYBRID','HYBRID/SATIVA','HYBRID/INDICA','CBD','MIXED','PARA'];
};

function createTagRow(tag) {
  // CRITICAL: Use same pipeline as backend - prefer canonical_lineage/currentLineage (from DB) over Lineage
  // This ensures UI lineages match database (strains.canonical_lineage is source of truth)
  const lineage = tag.canonical_lineage || tag.currentLineage || tag.Lineage || tag.lineage || 'MIXED';
    const dohStatus = tag.DOH || tag['DOH Compliant (Yes/No)'] || 'No';
    
    // For JSON matched tags and educated guess tags, prioritize the original display information over derived product names
    let tagName;
    if (tag.Source && (tag.Source.includes('JSON Match') || tag.Source.includes('Educated Guess'))) {
        tagName = tag.displayName || tag['Product Name*'] || tag.ProductName || '';
    } else {
        tagName = tag['Product Name*'] || tag.ProductName || '';
    }
    
    const brand = tag['Product Brand'] || tag.Brand || '';
    const type = tag['Product Type*'] || tag.Type || '';

    return `
        <tr class="tag-row" data-tag-name="${tagName}" data-lineage="${lineage}" data-doh="${dohStatus}">
            <td class="align-middle">${tagName}</td>
            <td class="align-middle">
                <div class="d-flex align-items-center">
                    <select class="form-select form-select-sm lineage-dropdown lineage-dropdown-mini" 
                            onchange="TagsTable.handleLineageChange(this, '${tagName}')">
                        <option value="SATIVA" ${lineage === 'SATIVA' ? 'selected' : ''}>S</option>
                        <option value="INDICA" ${lineage === 'INDICA' ? 'selected' : ''}>I</option>
                        <option value="HYBRID" ${lineage === 'HYBRID' ? 'selected' : ''}>H</option>
                        <option value="HYBRID/SATIVA" ${lineage === 'HYBRID/SATIVA' ? 'selected' : ''}>H/S</option>
                        <option value="HYBRID/INDICA" ${lineage === 'HYBRID/INDICA' ? 'selected' : ''}>H/I</option>
                        <option value="CBD" ${(lineage === 'CBD' || lineage === 'CBD_BLEND') ? 'selected' : ''}>CBD</option>
                        <option value="MIXED" ${(lineage === 'MIXED' || !['SATIVA', 'INDICA', 'HYBRID', 'HYBRID/INDICA', 'HYBRID/SATIVA', 'CBD', 'CBD_BLEND', 'PARA', 'PARAPHERNALIA', 'MIXED'].includes((lineage || '').toUpperCase())) ? 'selected' : ''}>THC</option>
                        <option value="PARA" ${lineage === 'PARA' ? 'selected' : ''}>P</option>
                    </select>
                </div>
            </td>
            <td class="align-middle">
                <div class="d-flex align-items-center">
                    <select class="form-select form-select-sm doh-dropdown doh-dropdown-mini" 
                            onchange="TagsTable.handleDohChange(this, '${tagName}')">
                        <option value="NONE" ${(!dohStatus || dohStatus === 'No' || dohStatus === 'NONE') ? 'selected' : ''}>None</option>
                        <option value="DOH" ${dohStatus === 'DOH' || dohStatus === 'Yes' ? 'selected' : ''}>DOH</option>
                        <option value="THC" ${dohStatus === 'THC' ? 'selected' : ''}>THC</option>
                        <option value="CBD" ${dohStatus === 'CBD' ? 'selected' : ''}>CBD</option>
                    </select>
                </div>
            </td>
            <td class="align-middle">${brand}</td>
            <td class="align-middle">${type}</td>
        </tr>
    `;
}

class TagsTable {
  static LINEAGE_OPTIONS = [
    'SATIVA',
    'INDICA',
    'HYBRID',
    'HYBRID/SATIVA',
    'HYBRID/INDICA',
    'CBD',
    'CBD_BLEND',
    'MIXED',
    'PARA'
  ];

  // Function to update table header based on product type
  static updateTableHeader() {
    const productTypeFilter = document.getElementById('productTypeFilter');
    // Fix: Use native JavaScript instead of jQuery :contains() selector
    const allHeaders = Array.from(document.querySelectorAll('th'));
    const brandHeader = allHeaders.find(th => th.textContent.includes('Brand') || th.textContent.includes('Lineage'));
    
    if (!productTypeFilter || !brandHeader) {
      return;
    }
    
    const selectedProductType = productTypeFilter.value.toLowerCase().trim();
    const isClassicType = window.CLASSIC_TYPES.includes(selectedProductType);
    
    if (isClassicType) {
      brandHeader.textContent = 'Lineage';
    } else {
      brandHeader.textContent = 'Brand';
    }
  }

  // Render a tag row as a div with an inline dropdown for lineage and DOH
  static createTagRow(tag, isSelected = false) {
  // CRITICAL: Use same pipeline as backend - prefer canonical_lineage/currentLineage (from DB) over Lineage
  // This ensures UI lineages match database (strains.canonical_lineage is source of truth)
  const lineage = tag.canonical_lineage || tag.currentLineage || tag.Lineage || tag.lineage || 'MIXED';
    const dohStatus = tag.DOH || tag['DOH Compliant (Yes/No)'] || 'No';
    console.log('DOH Status for tag:', tag['Product Name*'] || tag.ProductName, '=', dohStatus); // Debug log
    
    // For JSON matched tags and educated guess tags, prioritize the original display information over derived product names
    let tagName;
    if (tag.Source && (tag.Source.includes('JSON Match') || tag.Source.includes('Educated Guess'))) {
        tagName = tag.displayName || tag['Product Name*'] || tag.ProductName || '';
    } else {
        tagName = tag['Product Name*'] || tag.ProductName || '';
    }
    
    const brand = tag['Product Brand'] || tag.Brand || '';
    const vendor = tag['Vendor'] || tag['Vendor/Supplier*'] || tag['Vendor/Supplier'] || tag['Supplier'] || tag['Vendor*'] || tag['Supplier*'] || '';
    const type = tag['Product Type*'] || tag.Type || '';
    const safeTagName = tagName.replace(/"/g, '&quot;');
    const safeId = `tag_${safeTagName.replace(/[^a-zA-Z0-9]/g, '_')}`;
    
    // SYNCHRONIZED WITH BACKEND: Apply same lineage coloring logic as backend docx_formatting.py
    function getLineageColorFromBackendRules(lineage) {
        if (!lineage) return 'var(--lineage-mixed)';
        
        const text = lineage.toString().toUpperCase().trim();
        
        // Remove any marker wrappers for robust matching (same as backend)
        const markers = ["LINEAGE_START", "LINEAGE_END", "PRODUCTSTRAIN_START", "PRODUCTSTRAIN_END", "PRODUCTBRAND_CENTER_START", "PRODUCTBRAND_CENTER_END"];
        let cleanText = text;
        markers.forEach(marker => {
            cleanText = cleanText.replace(marker, "");
        });
        cleanText = cleanText.trim();
        
        // Apply EXACT same lineage coloring logic as backend (priority order matters!)
        if (cleanText.includes("PARAPHERNALIA")) {
            return 'var(--lineage-para)';
        } else if (cleanText.includes("HYBRID/INDICA") || cleanText.includes("HYBRID INDICA")) {
            return 'var(--lineage-indica)';
        } else if (cleanText.includes("HYBRID/SATIVA") || cleanText.includes("HYBRID SATIVA")) {
            return 'var(--lineage-sativa)';  // Sativa hybrids use sativa color
        } else if (cleanText.includes("SATIVA")) {
            return 'var(--lineage-sativa)';
        } else if (cleanText.includes("INDICA")) {
            return 'var(--lineage-indica)';
        } else if (cleanText.includes("HYBRID")) {
            return 'var(--lineage-hybrid)';
        } else if (cleanText.includes("CBD") || cleanText.includes("CBD_BLEND") || cleanText.includes("CBD BLEND")) {
            return 'var(--lineage-cbd)';
        } else if (cleanText.includes("MIXED")) {
            // MIXED lineage always gets blue bars (covers non-classic types like edibles)
            return 'var(--lineage-mixed)';
        } else {
            // Check for product brand values that get blue bars for non-classic types
            const brandKeywords = [
                "MOONSHOT", "PLATINUM", "PREMIUM", "GOLD", "SILVER", "ELITE", "SELECT", "RESERVE", 
                "CRAFT", "ARTISAN", "BOUTIQUE", "SIGNATURE", "LIMITED", "EXCLUSIVE", "PRIVATE", 
                "CUSTOM", "SPECIAL", "DELUXE", "ULTRA", "SUPER", "MEGA", "MAX", "PRO", "PLUS", 
                "X", "CONSTELLATION"
            ];
            
            const hasBrandKeyword = brandKeywords.some(brand => cleanText.includes(brand));
            if (hasBrandKeyword) {
                // Product Brand values get blue bars for non-classic types
                return 'var(--lineage-mixed)';
            }
        }
        
        // Default fallback (same as backend)
        return 'var(--lineage-mixed)';
    }
    
    const color = getLineageColorFromBackendRules(lineage);

    // Use abbreviated lineage names for compact dropdown
    const uniqueLineages = getUniqueLineages();
    const dropdownOptions = uniqueLineages.map(lin => {
      const selected = (lineage === lin || (lin === 'CBD' && lineage === 'CBD_BLEND')) ? 'selected' : '';
      const displayName = window.ABBREVIATED_LINEAGE[lin] || lin;
      return `<option value="${lin}" ${selected}>${displayName}</option>`;
    }).join('');

    // DOH dropdown options - map stored values to display values
    const dohDropdownOptions = [
      `<option value="NONE" ${(!dohStatus || dohStatus === 'No' || dohStatus === 'NONE') ? 'selected' : ''}>None</option>`,
      `<option value="DOH" ${dohStatus === 'DOH' || dohStatus === 'Yes' ? 'selected' : ''}>DOH</option>`,
      `<option value="THC" ${dohStatus === 'THC' ? 'selected' : ''}>THC</option>`,
      `<option value="CBD" ${dohStatus === 'CBD' ? 'selected' : ''}>CBD</option>`
    ].join('');
    
    // Debug: Log DOH dropdown creation
    console.log('Creating DOH dropdown for tag:', tagName, 'DOH Status:', dohStatus);

    // Add DOH and High CBD images if applicable
    const dohValue = (tag.DOH || '').toString().toUpperCase();
    const productType = (tag['Product Type*'] || '').toString().toLowerCase();
    let dohImageHtml = '';
    
    if (dohValue === 'YES') {
      if (productType.startsWith('high cbd')) {
        dohImageHtml = '<img src="/static/img/HighCBD.png" alt="High CBD" title="High CBD Product" style="height: 24px; width: auto; margin-left: 6px; vertical-align: middle;">';
      } else if (tagName.toLowerCase().includes('high thc')) {
        dohImageHtml = '<img src="/static/img/HighTHC.png" alt="High THC" title="High THC Product" style="height: 24px; width: auto; margin-left: 6px; vertical-align: middle;">';
      } else {
        dohImageHtml = '<img src="/static/img/DOH.png" alt="DOH Compliant" title="DOH Compliant Product" style="height: 21px; width: auto; margin-left: 6px; vertical-align: middle;">';
      }
    }

    return `
      <div class="tag-item d-flex align-items-center p-2 mb-2" 
           data-tag-name="${safeTagName}" 
           data-lineage="${lineage}"
           data-doh="${dohStatus}"
           style="background: ${color}; cursor: pointer;">
        <div class="checkbox-container me-2">
          <input type="checkbox" 
                 class="tag-checkbox" 
                 id="${safeId}"
                 value="${safeTagName}"
                 ${isSelected ? 'checked' : ''}>
        </div>
        <div class="quantity-badge me-2">${tag.Quantity || tag.quantity || ''}</div>
        <div class="tag-info flex-grow-1">
          <div class="d-flex align-items-center">
            <label class="tag-name me-3" for="${safeId}">${tagName}${dohImageHtml}</label>
            <select class="form-select form-select-sm lineage-dropdown lineage-dropdown-mini" 
                    onchange="TagsTable.handleLineageChange(this, '${safeTagName}')">
              ${dropdownOptions}
            </select>
            <select class="form-select form-select-sm doh-dropdown doh-dropdown-mini ms-2" 
                    onchange="TagsTable.handleDohChange(this, '${safeTagName}')"
                    title="DOH Status">
              ${dohDropdownOptions}
            </select>
          </div>
          <small class="text-muted d-block mt-1">${brand}${vendor ? ` (${vendor})` : ''} | ${type} | DOH: ${dohStatus}</small>
        </div>
      </div>
    `;
  }

  static createLineageSelect(currentLineage, tagName) {
    const uniqueLineages = getUniqueLineages();
    const options = uniqueLineages.map(lin => {
      const selected = (currentLineage === lin || (lin === 'CBD' && currentLineage === 'CBD_BLEND')) ? 'selected' : '';
      const displayName = window.ABBREVIATED_LINEAGE[lin] || lin;
      return `<option value="${lin}" ${selected}>${displayName}</option>`;
    }).join('');
    return `
      <select class="form-select form-select-sm lineage-dropdown lineage-dropdown-mini" 
              onchange="TagsTable.handleLineageChange(this, '${tagName}')">
        ${options}
      </select>
    `;
  }

  static async handleDohChange(selectElement, tagName) {
    const newDohStatus = selectElement.value;
    const tagRow = selectElement.closest(".tag-row");
    const oldDohStatus = tagRow.dataset.doh;

    console.log(`🔄 Updating DOH for ${tagName}: ${oldDohStatus} → ${newDohStatus}`);

    try {
      const response = await fetch("/api/update-doh", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tag_name: tagName, doh: newDohStatus })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        console.error(`❌ API Error: ${data.error || "Failed to update DOH"}`);
        throw new Error(data.error || "Failed to update DOH");
      }
      
      if (!data.success) {
        console.error(`❌ Update failed: ${data.message || data.error || "Unknown error"}`);
        throw new Error(data.message || data.error || "Failed to update DOH status");
      }
      
      // CRITICAL: Normalize DOH value for storage (backend stores 'No' for 'NONE', but UI shows 'NONE')
      // Map UI dropdown value to storage value: NONE -> No, everything else stays the same
      const normalizedDoh = newDohStatus === 'NONE' ? 'No' : newDohStatus;
      
      // Update the local UI dataset
      tagRow.dataset.doh = newDohStatus; // Keep UI showing the dropdown value
      
      // Show success message
      console.log(`✅ Successfully updated DOH for ${tagName} (${oldDohStatus} → ${newDohStatus}), stored as: ${normalizedDoh}`);
      
      // Update the tag in TagManager state if it exists - use normalized value for storage
      if (typeof TagManager !== 'undefined' && TagManager.state) {
        const tag = TagManager.state.tags?.find(t => t['Product Name*'] === tagName);
        if (tag) {
          tag.DOH = normalizedDoh;
          tag.doh = normalizedDoh;
          tag['DOH Compliant (Yes/No)'] = normalizedDoh;
          console.log(`📝 Updated tag DOH in TagManager.state.tags to: ${normalizedDoh}`);
        }
        
        const originalTag = TagManager.state.originalTags?.find(t => t['Product Name*'] === tagName);
        if (originalTag) {
          originalTag.DOH = normalizedDoh;
          originalTag.doh = normalizedDoh;
          originalTag['DOH Compliant (Yes/No)'] = normalizedDoh;
          console.log(`📝 Updated tag DOH in TagManager.state.originalTags to: ${normalizedDoh}`);
        }
        
        // Update DOH in all displays (available and selected tags)
        if (typeof TagManager.updateDohInAllDisplays === 'function') {
          TagManager.updateDohInAllDisplays(tagName, newDohStatus);
          console.log(`📝 Propagated DOH update to all displays`);
        }
      }

      // Show brief visual feedback
      selectElement.style.backgroundColor = '#d4edda';
      setTimeout(() => {
        selectElement.style.backgroundColor = '';
      }, 500);

    } catch (error) {
      console.error(`❌ Error updating DOH for ${tagName}:`, error);
      
      // Revert the dropdown to the old value
      selectElement.value = oldDohStatus;
      
      // Show error feedback
      selectElement.style.backgroundColor = '#f8d7da';
      setTimeout(() => {
        selectElement.style.backgroundColor = '';
      }, 1000);
      
      // Show user-friendly error message
      if (typeof showToast === 'function') {
        showToast(`Failed to update DOH for ${tagName}: ${error.message}`, 'error');
      } else {
        alert(`Failed to update DOH for ${tagName}: ${error.message}`);
      }
    }
  }

  static async handleLineageChange(selectElement, tagName) {
    const newLineage = selectElement.value;
    const tagRow = selectElement.closest(".tag-row");
    const oldLineage = tagRow?.dataset.lineage || selectElement.closest(".tag-item")?.dataset.lineage;

    console.log(`🔄 Updating lineage for ${tagName}: ${oldLineage} → ${newLineage}`);

    try {
      const response = await fetch("/api/update-lineage", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tag_name: tagName, lineage: newLineage })
      });
      
      if (!response.ok) {
        const error = await response.json();
        console.error(`❌ API Error: ${error.error || "Failed to update lineage"}`);
        throw new Error(error.error || "Failed to update lineage");
      }

      // Show success message
      const result = await response.json();
      console.log(`✅ Successfully updated lineage for ${tagName} (${oldLineage} → ${newLineage})`);

      // Update UI elements directly without full refresh (prevents hanging)
      if (typeof TagManager !== 'undefined' && typeof TagManager.updateTagLineageInUI === 'function') {
        TagManager.updateTagLineageInUI(tagName, newLineage);
        console.log(`🎨 Updated lineage UI for ${tagName}`);
      }
      
      // Update similar products in the background (non-blocking)
      if (typeof TagManager !== 'undefined' && typeof TagManager.updateSimilarLineages === 'function') {
        TagManager.updateSimilarLineages(tagName, newLineage);
        console.log(`🎨 Updated similar lineages for ${tagName}`);
      }

      // Refresh backend cache in the background (non-blocking)
      setTimeout(async () => {
        try {
          if (typeof TagManager !== 'undefined' && typeof TagManager.refreshBackendCache === 'function') {
            await TagManager.refreshBackendCache();
            console.log('✅ Backend cache refreshed in background');
          }
        } catch (e) {
          console.warn('Background cache refresh failed:', e);
        }
      }, 100);

      // Show brief visual feedback
      selectElement.style.backgroundColor = '#d4edda';
      setTimeout(() => {
        selectElement.style.backgroundColor = '';
      }, 500);

    } catch (error) {
      console.error('Error updating lineage:', error);
      console.error("Failed to update lineage:", error.message);
      // Revert the select element to the old value
      selectElement.value = oldLineage;
      selectElement.style.backgroundColor = '#f8d7da';
      setTimeout(() => {
        selectElement.style.backgroundColor = '';
      }, 1000);
    }
  }

  static openLineageEditor(tagName, currentLineage) {
    const modal = document.getElementById('lineageEditorModal');
    if (!modal) return;

    // Store the currently focused element before opening modal
    const activeElement = document.activeElement;
    if (activeElement && !modal.contains(activeElement)) {
      activeElement.setAttribute('data-bs-focus-prev', 'true');
    }

    document.getElementById('editTagName').value = tagName;
    const select = document.getElementById('editLineageSelect');
    select.innerHTML = '';
    // Only show unique lineages (CBD and CBD_BLEND as one)
    const uniqueLineages = ['SATIVA','INDICA','HYBRID','HYBRID/SATIVA','HYBRID/INDICA','CBD','MIXED','PARA'];
    uniqueLineages.forEach(lin => {
      const option = document.createElement('option');
      option.value = lin;
      const displayName = window.ABBREVIATED_LINEAGE[lin] || lin;
      option.textContent = displayName;
      if ((currentLineage === lin) || (lin === 'CBD' && currentLineage === 'CBD_BLEND')) {
        option.selected = true;
      }
      select.appendChild(option);
    });
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
    // Let CSS handle the styling instead of inline styles
    setTimeout(() => {
      const select = document.getElementById('editLineageSelect');
      if (select) {
        // Ensure the compact classes are applied
        select.classList.add('lineage-dropdown-mini');
      }
    }, 200);
  }

  static async saveLineageChanges() {
      const tagName = document.getElementById('editTagName').value;
      const newLineage = document.getElementById('editLineageSelect').value;

      try {
          const response = await fetch('/api/update-lineage', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                  tag_name: tagName,
                  lineage: newLineage
              })
          });

          if (!response.ok) throw new Error('Failed to update lineage');

          // Update UI
          document.querySelectorAll(`[data-tag-name="${tagName}"]`).forEach(tagItem => {
              tagItem.dataset.lineage = newLineage;
              const lineageText = tagItem.querySelector('small');
              if (lineageText) {
                  lineageText.textContent = `Lineage: ${newLineage}`;
              }
          });

          // Close modal
          bootstrap.Modal.getInstance(document.getElementById('lineageEditorModal')).hide();
          
          // Re-render using existing data and current filters to preserve selections and filters
          if (typeof TagManager !== 'undefined') {
            try {
              console.log('Re-rendering tags locally after lineage change (preserve filters and selections)');
              if (TagManager.updateFilterOptions) await TagManager.updateFilterOptions();
              if (TagManager.applyFilters) TagManager.applyFilters();
              console.log('Local re-render complete');
            } catch (refreshError) {
              console.warn('Local re-render after lineage change failed:', refreshError);
            }
          }
          
          // Restore focus to previously focused element
          setTimeout(() => {
            const previouslyFocusedElement = document.querySelector('[data-bs-focus-prev]');
            if (previouslyFocusedElement) {
              previouslyFocusedElement.focus();
              previouslyFocusedElement.removeAttribute('data-bs-focus-prev');
            }
          }, 150);
          
          // Successfully updated lineage

      } catch (error) {
          console.error('Error:', error);
          console.error('Failed to update lineage');
      }
  }

  static renderTags(tags, containerId) {
      const container = document.getElementById(containerId);
      if (!container) return;

      // Determine the header text based on current product type
      const productTypeFilter = document.getElementById('productTypeFilter');
      const selectedProductType = productTypeFilter?.value?.toLowerCase().trim() || '';
      const isClassicType = window.CLASSIC_TYPES.includes(selectedProductType);
      const brandHeaderText = isClassicType ? 'Lineage' : 'Brand';

      const tableHtml = `
          <table class="table table-hover">
              <thead>
                  <tr>
                      <th>Name</th>
                      <th>Lineage</th>
                      <th>DOH</th>
                      <th>${brandHeaderText}</th>
                      <th>Type</th>
                      <th></th>
                  </tr>
              </thead>
              <tbody>
                  ${tags.map(tag => this.createTagRow(tag)).join('')}
              </tbody>
          </table>
      `;
      
      container.innerHTML = tableHtml;
  }

  static updateTagsList(containerId, tags, isSelected = false) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Clear existing content
    container.innerHTML = '';
    
    // Performance optimization: Render tags in batches to keep UI responsive
    // OPTIMIZATION: Increased batch sizes and improved progressive rendering for faster initial display
    // For small lists (< 500), render all at once for better performance
    // For larger lists, use progressive rendering with larger initial batch
    const batchSize = tags.length > 500 ? 200 : tags.length;
    const initialBatchSize = tags.length > 500 ? 300 : tags.length; // Show more tags immediately
    
    if (tags.length <= batchSize) {
      // Small list: render all at once using DocumentFragment for efficiency
      const fragment = document.createDocumentFragment();
      const tempDiv = document.createElement('div');
      
      tags.forEach(tag => {
        const tagHtml = this.createTagRow(tag, isSelected);
        tempDiv.insertAdjacentHTML('beforeend', tagHtml);
      });
      
      // Move all nodes from tempDiv to fragment
      while (tempDiv.firstChild) {
        fragment.appendChild(tempDiv.firstChild);
      }
      
      container.appendChild(fragment);
      this.addEventListeners(container);
    } else {
      // Large list: progressive rendering with faster initial batch
      let index = 0;
      let isFirstBatch = true;
      
      const processBatch = () => {
        // Use larger batch size for first batch to show content faster
        const currentBatchSize = isFirstBatch ? initialBatchSize : batchSize;
        const endIndex = Math.min(index + currentBatchSize, tags.length);
        const fragment = document.createDocumentFragment();
        const tempDiv = document.createElement('div');
        
        for (let i = index; i < endIndex; i++) {
          const tagHtml = this.createTagRow(tags[i], isSelected);
          tempDiv.insertAdjacentHTML('beforeend', tagHtml);
        }
        
        // Move nodes to fragment and append to container
        while (tempDiv.firstChild) {
          fragment.appendChild(tempDiv.firstChild);
        }
        container.appendChild(fragment);
        
        // Add event listeners for this batch
        this.addEventListeners(container);
        
        index = endIndex;
        isFirstBatch = false;
        
        // If more tags to process, schedule next batch
        if (index < tags.length) {
          // Use setTimeout with 0ms for faster subsequent batches (after initial display)
          // This is faster than requestAnimationFrame for bulk rendering
          setTimeout(processBatch, 0);
        }
      };
      
      // Start processing immediately
      processBatch();
    }
  }

  static addEventListeners(container) {
    // Add checkbox change listeners
    container.querySelectorAll('.tag-checkbox').forEach(checkbox => {
      checkbox.addEventListener('change', function(e) {
        try {
          // CRITICAL FIX: Don't process during deselection to prevent filter clearing
          if (TagManager.state.isProcessingDeselection) {
            console.log('🚫 TagsTable: Skipping checkbox handler - currently processing deselection');
            return;
          }
          
          if (this.checked) {
            TagManager.state.selectedTags.add(this.value);
          } else {
            const tagName = this.value;
            console.log(`🔄 Deselecting tag: ${tagName}`);
            
            TagManager.state.selectedTags.delete(tagName);
            // Also remove from persistent selections to avoid drift
            const idx = TagManager.state.persistentSelectedTags.indexOf(tagName);
            if (idx > -1) TagManager.state.persistentSelectedTags.splice(idx, 1);
            
            // CRITICAL: Also uncheck the corresponding checkbox in available tags
            // Try multiple selector approaches to be more robust
            let availableCheckbox = document.querySelector(`#availableTags .tag-checkbox[value="${tagName}"]`);
            if (!availableCheckbox) {
              // Try escaping special characters in the value
              const escapedValue = tagName.replace(/"/g, '\\"');
              availableCheckbox = document.querySelector(`#availableTags .tag-checkbox[value="${escapedValue}"]`);
            }
            if (!availableCheckbox) {
              // Try finding by iterating through checkboxes
              const allAvailableCheckboxes = document.querySelectorAll('#availableTags .tag-checkbox');
              for (let cb of allAvailableCheckboxes) {
                if (cb.value === tagName) {
                  availableCheckbox = cb;
                  break;
                }
              }
            }
            
            if (availableCheckbox) {
              availableCheckbox.checked = false;
              console.log(`✅ Unchecked available tags checkbox for ${tagName}`);
              
              // Also update the UI state if the checkbox element has a handler
              if (availableCheckbox._changeHandler) {
                console.log('Found checkbox handler, triggering update');
                // Don't trigger the handler, just ensure UI consistency
              }
              
              // Immediately update hierarchical checkboxes after unchecking
              requestAnimationFrame(() => {
                if (TagManager.updateSelectAllCheckboxes) {
                  TagManager.updateSelectAllCheckboxes();
                }
              });
            } else {
              console.warn(`⚠️ Could not find available tags checkbox for: ${tagName}`);
            }
            
            // Remove DOM row when in selected list without triggering big re-render
            const row = this.closest('.tag-item, .tag-row');
            if (row && row.parentElement && row.parentElement.id === 'selectedTags') {
              row.remove();
              TagManager.updateTagCount('selected', TagManager.state.persistentSelectedTags.length);
            }
          }
          // Halt further propagation to avoid any global listeners that might reload data
          if (typeof e.stopImmediatePropagation === 'function') e.stopImmediatePropagation();
          e.stopPropagation();
          e.preventDefault();
        } catch (error) {
          console.error('Error in checkbox change handler:', error);
          // Prevent the error from causing the page to exit
        }
      });
    });

    // Require explicit checkbox clicks; do not toggle selection on tag body clicks
    container.querySelectorAll('.tag-item').forEach(tagItem => {
      tagItem.style.cursor = 'default';
      
      // Add right-click context menu for strain lineage editing
      tagItem.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        const tagName = this.getAttribute('data-tag-name');
        const tag = TagManager.state.tags.find(t => t['Product Name*'] === tagName);
        
        if (tag && tag['Product Strain']) {
          const strainName = tag['Product Strain'];
          const currentLineage = tag.Lineage || tag.lineage || 'MIXED';
          
          // Remove any existing context menu
          const existingMenu = document.querySelector('.context-menu');
          if (existingMenu) {
            existingMenu.remove();
          }
          
          // Show context menu
          const contextMenu = document.createElement('div');
          contextMenu.className = 'context-menu';
          contextMenu.style.cssText = `
            position: fixed;
            top: ${e.clientY}px;
            left: ${e.clientX}px;
            background: white;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
            min-width: 200px;
          `;
          
          const menuItem = document.createElement('div');
          menuItem.className = 'context-menu-item';
          menuItem.style.cssText = `
            padding: 8px 12px;
            cursor: pointer;
            border-bottom: 1px solid #eee;
          `;
          menuItem.textContent = `Edit Strain Lineage: ${strainName}`;
          menuItem.addEventListener('click', () => {
            try {
              if (window.strainLineageEditor) {
                window.strainLineageEditor.openEditor(strainName, currentLineage);
              }
              contextMenu.remove();
            } catch (error) {
              console.error('Error in context menu click handler:', error);
              contextMenu.remove();
            }
          });
          
          const closeItem = document.createElement('div');
          closeItem.className = 'context-menu-item';
          closeItem.style.cssText = `
            padding: 8px 12px;
            cursor: pointer;
            color: #666;
          `;
          closeItem.textContent = 'Cancel';
          closeItem.addEventListener('click', () => {
            try {
              contextMenu.remove();
            } catch (error) {
              console.error('Error in context menu close handler:', error);
            }
          });
          
          contextMenu.appendChild(menuItem);
          contextMenu.appendChild(closeItem);
          document.body.appendChild(contextMenu);
          
          // Close menu when clicking outside
          const closeMenu = (e) => {
            if (!contextMenu.contains(e.target)) {
              contextMenu.remove();
              document.removeEventListener('click', closeMenu);
            }
          };
          setTimeout(() => document.addEventListener('click', closeMenu), 100);
        }
      });
    });

    // Add move button listeners
    container.querySelectorAll('.move-tag-btn').forEach(button => {
      button.addEventListener('click', function() {
        const direction = this.dataset.direction;
        const tagName = this.dataset.tag;
        
        if (direction === 'to_selected') {
          TagManager.moveToSelected();
        } else {
          TagManager.moveToAvailable();
        }
      });
    });
  }

  static async updateLineage(tagName, newLineage) {
      try {
          const response = await fetch('/api/update-lineage', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                  tag_name: tagName,
                  lineage: newLineage
              })
          });

          if (!response.ok) throw new Error('Failed to update lineage');

          // Update UI
          document.querySelectorAll(`[data-tag-name="${tagName}"]`).forEach(item => {
              item.dataset.lineage = newLineage;
          });

          // Refresh available tags from backend to ensure UI shows updated lineage
          if (typeof TagManager !== 'undefined' && TagManager.fetchAndUpdateAvailableTags) {
            try {
              console.log('Refreshing available tags to show updated lineage...');
              await TagManager.fetchAndUpdateAvailableTags();
              console.log('Available tags refreshed successfully');
            } catch (refreshError) {
              console.warn('Failed to refresh available tags:', refreshError);
              // Don't fail the lineage update if refresh fails
            }
          }

          // Successfully updated lineage

      } catch (error) {
          console.error('Error:', error);
          console.error('Failed to update lineage');
      }
  }
}

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Handle save changes button click
  document.getElementById('saveLineageChanges')?.addEventListener('click', TagsTable.saveLineageChanges);

  // Example usage when data is loaded:
  if (typeof TagManager !== 'undefined') {
    TagManager.onTagsLoaded = (tags) => {
      TagsTable.updateTagsList('availableTags', tags);
    };
  }

  const addSelectedTagsBtn = document.getElementById('addSelectedTagsBtn');
  if (addSelectedTagsBtn) {
    addSelectedTagsBtn.addEventListener('click', function() {
      const checked = document.querySelectorAll('#availableTags .tag-checkbox:checked');
      const tagsToMove = Array.from(checked).map(cb => cb.value);
      TagManager.moveToSelected(tagsToMove);
    });
  }

  document.querySelectorAll('select').forEach(sel => {
    // REMOVE all JS that sets style.width, style.minWidth, style.maxWidth, style.fontSize, style.paddingLeft, style.paddingRight for lineage dropdowns
  });
});