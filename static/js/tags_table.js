// Classic types that should show "Lineage" instead of "Brand"
const CLASSIC_TYPES = [
    "flower", "pre-roll", "concentrate", "infused pre-roll", 
    "solventless concentrate", "vape cartridge"
];

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

// Use full lineage names for all dropdowns
const getUniqueLineages = () => {
  return ['SATIVA','INDICA','HYBRID','HYBRID/SATIVA','HYBRID/INDICA','CBD','MIXED','PARA'];
};

function createTagRow(tag) {
    const lineage = tag.Lineage || tag.lineage || 'MIXED';
    const tagName = tag['Product Name*'] || tag.ProductName || '';
    const brand = tag['Product Brand'] || tag.Brand || '';
    const type = tag['Product Type*'] || tag.Type || '';

    return `
        <tr class="tag-row" data-tag-name="${tagName}" data-lineage="${lineage}">
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
                        <option value="MIXED" ${lineage === 'MIXED' ? 'selected' : ''}>THC</option>
                        <option value="PARA" ${lineage === 'PARA' ? 'selected' : ''}>P</option>
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
    const brandHeader = document.querySelector('th:contains("Brand")');
    
    if (!productTypeFilter || !brandHeader) {
      return;
    }
    
    const selectedProductType = productTypeFilter.value.toLowerCase().trim();
    const isClassicType = CLASSIC_TYPES.includes(selectedProductType);
    
    if (isClassicType) {
      brandHeader.textContent = 'Lineage';
    } else {
      brandHeader.textContent = 'Brand';
    }
  }

  // Render a tag row as a div with an inline dropdown for lineage
  static createTagRow(tag, isSelected = false) {
    const lineage = tag.Lineage || tag.lineage || 'MIXED';
    const tagName = tag['Product Name*'] || tag.ProductName || '';
    const brand = tag['Product Brand'] || tag.Brand || '';
    const vendor = tag['Vendor'] || tag['Vendor/Supplier*'] || tag['Vendor/Supplier'] || tag['Supplier'] || tag['Vendor*'] || tag['Supplier*'] || '';
    const type = tag['Product Type*'] || tag.Type || '';
    const safeTagName = tagName.replace(/"/g, '&quot;');
    const safeId = `tag_${safeTagName.replace(/[^a-zA-Z0-9]/g, '_')}`;
    const lineageColors = (window.TagManager && window.TagManager.state && window.TagManager.state.lineageColors) || {};
    const color = lineageColors[lineage.toUpperCase()] || 'var(--lineage-mixed)';

    // Use abbreviated lineage names for compact dropdown
    const uniqueLineages = getUniqueLineages();
    const dropdownOptions = uniqueLineages.map(lin => {
      const selected = (lineage === lin || (lin === 'CBD' && lineage === 'CBD_BLEND')) ? 'selected' : '';
      const displayName = ABBREVIATED_LINEAGE[lin] || lin;
      return `<option value="${lin}" ${selected}>${displayName}</option>`;
    }).join('');

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
        dohImageHtml = '<img src="/static/img/DOH.png" alt="DOH Compliant" title="DOH Compliant Product" style="height: 24px; width: auto; margin-left: 6px; vertical-align: middle;">';
      }
    }

    return `
      <div class="tag-item d-flex align-items-center p-2 mb-2" 
           data-tag-name="${safeTagName}" 
           data-lineage="${lineage}"
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
          </div>
          <small class="text-muted d-block mt-1">${brand}${vendor ? ` (${vendor})` : ''} | ${type}</small>
        </div>
      </div>
    `;
  }

  static createLineageSelect(currentLineage, tagName) {
    const uniqueLineages = getUniqueLineages();
    const options = uniqueLineages.map(lin => {
      const selected = (currentLineage === lin || (lin === 'CBD' && currentLineage === 'CBD_BLEND')) ? 'selected' : '';
      const displayName = ABBREVIATED_LINEAGE[lin] || lin;
      return `<option value="${lin}" ${selected}>${displayName}</option>`;
    }).join('');
    return `
      <select class="form-select form-select-sm lineage-dropdown lineage-dropdown-mini" 
              onchange="TagsTable.handleLineageChange(this, '${tagName}')">
        ${options}
      </select>
    `;
  }

  static async handleLineageChange(selectElement, tagName) {
    const newLineage = selectElement.value;
    const tagItem = selectElement.closest(".tag-item");
    const oldLineage = tagItem.dataset.lineage;

    try {
      const response = await fetch("/api/update-lineage", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tag_name: tagName, lineage: newLineage })
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Failed to update lineage");
      }

      // Update the local UI
      tagItem.dataset.lineage = newLineage;
      
      // Show success message
                  console.log(`Updated lineage for ${tagName} (${oldLineage} → ${newLineage})`);

      // Update the tag in TagManager state without refreshing the entire list
      const tag = TagManager.state.tags.find(t => t['Product Name*'] === tagName);
      if (tag) {
        tag.lineage = newLineage;
      }
      
      // Update the tag in original tags as well
      const originalTag = TagManager.state.originalTags.find(t => t['Product Name*'] === tagName);
      if (originalTag) {
        originalTag.lineage = newLineage;
      }
      
      // Only update selected tags if the changed tag is in the selected list
      if (TagManager.state.selectedTags.has(tagName)) {
        await TagManager.fetchAndUpdateSelectedTags();
      }

      // Refresh available tags from backend to ensure UI shows updated lineage
      if (TagManager.fetchAndUpdateAvailableTags) {
        try {
          console.log('Refreshing available tags to show updated lineage...');
          await TagManager.fetchAndUpdateAvailableTags();
          console.log('Available tags refreshed successfully');
        } catch (refreshError) {
          console.warn('Failed to refresh available tags:', refreshError);
          // Don't fail the lineage update if refresh fails
        }
      }

    } catch (error) {
      console.error('Error updating lineage:', error);
              console.error("Failed to update lineage:", error.message);
      // Revert the select element to the old value
      selectElement.value = oldLineage;
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
      const displayName = ABBREVIATED_LINEAGE[lin] || lin;
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
      const isClassicType = CLASSIC_TYPES.includes(selectedProductType);
      const brandHeaderText = isClassicType ? 'Lineage' : 'Brand';

      const tableHtml = `
          <table class="table table-hover">
              <thead>
                  <tr>
                      <th>Name</th>
                      <th>Lineage</th>
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
    
    // Add new tags
    tags.forEach(tag => {
      const tagHtml = this.createTagRow(tag, isSelected);
      container.insertAdjacentHTML('beforeend', tagHtml);
    });

    // Add event listeners to new elements
    this.addEventListeners(container);
  }

  static addEventListeners(container) {
    // Add checkbox change listeners
    container.querySelectorAll('.tag-checkbox').forEach(checkbox => {
      checkbox.addEventListener('change', function() {
        try {
          if (this.checked) {
            TagManager.state.selectedTags.add(this.value);
          } else {
            TagManager.state.selectedTags.delete(this.value);
          }
          TagManager.updateTagCheckboxes();
        } catch (error) {
          console.error('Error in checkbox change handler:', error);
          // Prevent the error from causing the page to exit
        }
      });
    });

    // Add click listeners to tag items to toggle checkboxes
    container.querySelectorAll('.tag-item').forEach(tagItem => {
      tagItem.addEventListener('click', function(e) {
        try {
          // Don't trigger if clicking on the checkbox itself or lineage dropdown
          if (e.target.classList.contains('tag-checkbox') || 
              e.target.classList.contains('lineage-dropdown') || 
              e.target.closest('.lineage-dropdown')) {
            return;
          }
          
          // Find the checkbox within this tag item
          const checkbox = this.querySelector('.tag-checkbox');
          if (checkbox) {
            // Toggle the checkbox
            checkbox.checked = !checkbox.checked;
            // Trigger the change event
            checkbox.dispatchEvent(new Event('change', { bubbles: true }));
          }
        } catch (error) {
          console.error('Error in tag item click handler:', error);
          // Prevent the error from causing the page to exit
          e.preventDefault();
          e.stopPropagation();
        }
      });
      
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

  document.getElementById('addSelectedTagsBtn').addEventListener('click', function() {
    const checked = document.querySelectorAll('#availableTags .tag-checkbox:checked');
    const tagsToMove = Array.from(checked).map(cb => cb.value);
    TagManager.moveToSelected(tagsToMove);
  });

  document.querySelectorAll('select').forEach(sel => {
    // REMOVE all JS that sets style.width, style.minWidth, style.maxWidth, style.fontSize, style.paddingLeft, style.paddingRight for lineage dropdowns
  });
});