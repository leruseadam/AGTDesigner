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
        "CBD_BLEND": "CBDE",
        "MIXED": "THC",
        "PARA": "P",
        "PARAPHERNALIA": "P"
    };
}
// Use window.ABBREVIATED_LINEAGE directly to avoid const redeclaration
// This will reference the one from main.js if it exists, or our fallback

// Helper function to normalize lineage values consistently - make it globally available
if (typeof window.normalizeLineageValue === 'undefined') {
  window.normalizeLineageValue = function(lineage) {
    if (!lineage) return 'MIXED';
    
    const normalized = String(lineage).trim().toUpperCase();
    
    // CRITICAL: "THC" is an abbreviation for "MIXED"
    // Convert it to MIXED - valid for non-classic types (edibles), invalid for classic types
    if (normalized === 'THC') {
      return 'MIXED'; // Convert THC abbreviation to MIXED
    }
    
    // Handle common variations
    if (normalized === 'CBD_BLEND' || normalized === 'CBD BLEND' || normalized === 'CBDE') {
      return 'CBD_BLEND';
    }
    if (normalized.includes('HYBRID/INDICA') || normalized.includes('HYBRID INDICA')) {
      return 'HYBRID/INDICA';
    }
    if (normalized.includes('HYBRID/SATIVA') || normalized.includes('HYBRID SATIVA')) {
      return 'HYBRID/SATIVA';
    }
    if (normalized.includes('SATIVA') && !normalized.includes('HYBRID')) {
      return 'SATIVA';
    }
    if (normalized.includes('INDICA') && !normalized.includes('HYBRID')) {
      return 'INDICA';
    }
    if (normalized.includes('HYBRID')) {
      return 'HYBRID';
    }
    if (normalized.includes('CBD')) {
      return 'CBD';
    }
    if (normalized.includes('PARAPHERNALIA') || normalized === 'PARA') {
      return 'PARA';  // Match dropdown option value
    }
    if (normalized.includes('MIXED')) {
      return 'MIXED';
    }
    
    // Default fallback
    return normalized || 'MIXED';
  };
}

// Use full lineage names for all dropdowns
const getUniqueLineages = (productType = null) => {
  // Valid lineages for classic types (from VALID_CLASSIC_LINEAGES constant)
  const VALID_CLASSIC_LINEAGES = ['SATIVA','INDICA','HYBRID','HYBRID/SATIVA','HYBRID/INDICA','CBD'];
  const NONCLASSIC_LINEAGES = ['CBD','MIXED']; // Only CBD and MIXED for nonclassic types (edibles, tinctures, topicals, etc.)
  const PARAPHERNALIA_LINEAGES = ['PARA']; // Only PARA for paraphernalia
  
  // If productType is provided, filter lineages based on type
  if (productType) {
    const typeLower = (productType || '').toString().toLowerCase().trim();
    const CLASSIC_TYPES = [
      'flower', 'bud', 'pre-roll', 'infused pre-roll', 'preroll',
      'concentrate', 'solventless concentrate', 'live resin', 'rosin', 
      'wax', 'shatter', 'hash', 'kief', 'butane extract', 'distillate', 
      'rso', 'co2 extract', 'honey crystal', 'liquid diamond', 'caviar',
      'vape cartridge', 'vape pen', 'disposable', 'rso/co2 tankers'
    ];
    
    // Check for paraphernalia first
    if (typeLower === 'paraphernalia') {
      return PARAPHERNALIA_LINEAGES;
    }
    
    const isClassicType = CLASSIC_TYPES.some(ct => typeLower.includes(ct) || typeLower === ct);
    if (isClassicType) {
      // For classic types, only return valid classic lineages (no MIXED, no PARA)
      return VALID_CLASSIC_LINEAGES;
    }
    
    // For non-classic types (edibles, tinctures, topicals, capsules, etc.), only return MIXED and CBD
    return NONCLASSIC_LINEAGES;
  }
  
  // Default: return all lineages if no product type specified (for backwards compatibility)
  return ['SATIVA','INDICA','HYBRID','HYBRID/SATIVA','HYBRID/INDICA','CBD','MIXED','PARA'];
};

function createTagRow(tag) {
  // CRITICAL: Check sovereign_lineage first (user edits), then canonical_lineage, currentLineage, or Lineage
  // CRITICAL FIX: Correct lineage priority - matches DOCX generation and backend
  // Priority: sovereign_lineage (user edits) > canonical_lineage (strains table) > currentLineage > Lineage (Excel)
  // This ensures database lineage (canonical_lineage) takes priority over Excel lineage
  let rawLineage = tag.sovereign_lineage || tag.canonical_lineage || tag.currentLineage || tag.Lineage || tag.lineage || '';
  
  // Normalize to uppercase, but keep the original value
  let lineage = String(rawLineage || '').trim().toUpperCase();
  
  // CRITICAL FIX: Classic types should NEVER have MIXED/THC lineage - convert to HYBRID
  // This ensures UI displays correct lineage even if database/Excel has wrong value
  const productType = tag['Product Type*'] || tag.Type || '';
  const isClassicType = productType && getUniqueLineages(productType).length === 6;
  if (isClassicType && (lineage === 'MIXED' || lineage === 'THC')) {
    lineage = 'HYBRID';
  }

  // CRITICAL FIX: For non-classic types, detect CBD indicators in product name/strain
  // Products with CBD/CBN/CBG/CBC in the name should show CBD lineage, not MIXED
  const productNameForCbd = tag['Product Name*'] || tag.ProductName || '';
  const productStrainForCbd = tag['Product Strain'] || tag.productStrain || '';
  const nameAndStrainLower = (productNameForCbd + ' ' + productStrainForCbd).toLowerCase();
  const hasCbdIndicator = ['cbd', 'cbn', 'cbg', 'cbc'].some(token => nameAndStrainLower.includes(token));

  // CRITICAL FIX: For non-classic types, CBD indicators ALWAYS override other lineages
  // Check CBD indicators FIRST before applying defaults
  if (!isClassicType && hasCbdIndicator) {
    // Non-classic types with CBD indicators should show CBD_BLEND (yellow), regardless of database value
    lineage = 'CBD_BLEND';
  } else if (!lineage) {
    // Only set default if lineage is completely missing
    if (isClassicType) {
      lineage = 'HYBRID';
    } else {
      lineage = 'MIXED';
    }
  }
    // CRITICAL FIX: Extract DOH status and normalize it consistently (same as TagsTable.createTagRow)
    const rawDohStatus = tag.DOH || tag['DOH Compliant (Yes/No)'] || tag.doh || tag['DOH Compliant'] || '';
    const dohStatusNormalized = rawDohStatus.toString().trim().toUpperCase();
    
    // Normalize DOH values: YES/Y -> DOH, NO/N -> NONE, empty -> NONE
    let dohStatus = 'NONE';
    if (dohStatusNormalized === 'YES' || dohStatusNormalized === 'Y') {
      dohStatus = 'DOH';
    } else if (dohStatusNormalized === 'DOH' || dohStatusNormalized.includes('DOH') || dohStatusNormalized === 'COMPLIANT') {
      dohStatus = 'DOH';
    } else if (dohStatusNormalized === 'CBD') {
      dohStatus = 'CBD';
    } else if (dohStatusNormalized === 'THC') {
      dohStatus = 'THC';
    } else if (dohStatusNormalized === 'NO' || dohStatusNormalized === 'N' || dohStatusNormalized === 'NONE' || !dohStatusNormalized) {
      dohStatus = 'NONE';
    } else {
      // Keep original value if it's something else
      dohStatus = dohStatusNormalized;
    }
    
    // For JSON matched tags and educated guess tags, prioritize the original display information over derived product names
    let tagName;
    if (tag.Source && (tag.Source.includes('JSON Match') || tag.Source.includes('Educated Guess'))) {
        tagName = tag.displayName || tag['Product Name*'] || tag.ProductName || '';
    } else {
        tagName = tag['Product Name*'] || tag.ProductName || '';
    }
    
    const brand = tag['Product Brand'] || tag.Brand || '';
    
    // Extract weight units from multiple possible sources
    let weightWithUnits = (tag.weightWithUnits || tag.WeightWithUnits || tag.WeightUnits || 
                           tag.CombinedWeight || tag['Weight*'] || tag.Weight || tag.weight || '').toString().trim();
    
    // Format weight to remove .0 decimals (e.g., "1.0g" -> "1g", but "1.5g" stays "1.5g")
    if (weightWithUnits) {
        // Match pattern: number with optional decimal, followed by unit
        const weightMatch = weightWithUnits.match(/^([\d.]+)([a-zA-Z]+.*)$/);
        if (weightMatch) {
            const weightValue = weightMatch[1];
            const unit = weightMatch[2];
            // Try to parse as float
            const weightFloat = parseFloat(weightValue);
            if (!isNaN(weightFloat)) {
                if (weightFloat % 1 === 0) {
                    // It's a whole number, remove decimal point (e.g., "1.0" -> "1")
                    weightWithUnits = `${Math.round(weightFloat)}${unit}`;
                } else {
                    // It's a decimal number, remove trailing zeros (e.g., "1.50" -> "1.5", "1.0" -> "1")
                    // Convert to string and remove trailing zeros and decimal point if needed
                    let formatted = weightFloat.toString();
                    formatted = formatted.replace(/\.0+$/, ''); // Remove .0, .00, etc.
                    formatted = formatted.replace(/(\.\d*?)0+$/, '$1'); // Remove trailing zeros after decimal
                    formatted = formatted.replace(/\.$/, ''); // Remove trailing decimal point
                    weightWithUnits = `${formatted}${unit}`;
                }
            }
        }
    }

    // Add DOH badge HTML (same logic as TagsTable.createTagRow)
    const productTypeForBadge = (tag['Product Type*'] || tag.Type || '').toLowerCase().trim();
    const isHighCbdProductForBadge = productTypeForBadge.startsWith('high cbd') || 
                                     productTypeForBadge.includes('doh high cbd') ||
                                     productTypeForBadge.includes('high cbd edible') ||
                                     productTypeForBadge.includes('high cbd liquid') ||
                                     productTypeForBadge.includes('high cbd solid') ||
                                     productTypeForBadge.includes('high cbd topical');
    
    let dohImageHtml = '';
    if (isHighCbdProductForBadge) {
      dohImageHtml = '<img src="/static/img/HighCBD.png" alt="High CBD" title="High CBD Product" style="height: 28px; width: 28px; object-fit: contain; margin-left: 6px; vertical-align: middle;">';
    } else if (dohStatus === 'DOH') {
      if (tagName.toLowerCase().includes('high thc')) {
        dohImageHtml = '<img src="/static/img/HighTHC.png" alt="High THC" title="High THC Product" style="height: 28px; width: 28px; object-fit: contain; margin-left: 6px; vertical-align: middle;">';
      } else {
        dohImageHtml = '<img src="/static/img/DOH.png" alt="DOH Compliant" title="DOH Compliant Product" style="height: 36px; width: 36px; object-fit: contain; margin-left: 6px; vertical-align: middle;">';
      }
    } else if (dohStatus === 'CBD') {
      dohImageHtml = '<img src="/static/img/HighCBD.png" alt="High CBD" title="High CBD Product" style="height: 28px; width: 28px; object-fit: contain; margin-left: 6px; vertical-align: middle;">';
    } else if (dohStatus === 'THC') {
      dohImageHtml = '<img src="/static/img/HighTHC.png" alt="High THC" title="High THC Product" style="height: 28px; width: 28px; object-fit: contain; margin-left: 6px; vertical-align: middle;">';
    }

    return `
        <tr class="tag-row" data-tag-name="${tagName}" data-lineage="${lineage}" data-doh="${dohStatus}">
            <td class="align-middle tag-name-cell">${tagName}${dohImageHtml}</td>
            <td class="align-middle">
                <div class="d-flex align-items-center">
                    <select class="form-select form-select-sm lineage-dropdown lineage-dropdown-mini" 
                            onchange="TagsTable.handleLineageChange(this, '${tagName}')">
                        ${(() => {
                          const productType = tag['Product Type*'] || tag.Type || '';
                          const uniqueLineages = getUniqueLineages(productType);
                          
                          // CRITICAL FIX: Convert MIXED/THC to HYBRID for classic types before dropdown creation
                          let dropdownLineage = lineage;
                          const isClassicType = productType && getUniqueLineages(productType).length === 6;
                          if (isClassicType && (dropdownLineage === 'MIXED' || dropdownLineage === 'THC')) {
                            dropdownLineage = 'HYBRID';
                          }
                          
                          return uniqueLineages.map(lin => {
                            const linNormalized = (typeof window.normalizeLineageValue !== 'undefined') 
                              ? window.normalizeLineageValue(lin)
                              : String(lin).trim().toUpperCase();
                            
                            // Compare normalized values directly - use converted lineage for classic types
                            const selected = (dropdownLineage === linNormalized) ? 'selected' : '';
                            // Get abbreviation with fallback - handle both PARA and PARAPHERNALIA
                            let displayName = lin;
                            if (window.ABBREVIATED_LINEAGE) {
                              displayName = window.ABBREVIATED_LINEAGE[lin] || 
                                           window.ABBREVIATED_LINEAGE[lin.toUpperCase()] || 
                                           lin;
                            }
                            return `<option value="${lin}" ${selected}>${displayName}</option>`;
                          }).join('');
                        })()}
                    </select>
                </div>
            </td>
            <td class="align-middle">
                <div class="d-flex align-items-center">
                    ${(() => {
                      const productType = tag['Product Type*'] || tag.Type || '';
                      const productTypeLower = productType.toLowerCase().trim();
                      // More robust High CBD check - handle variations in product type format
                      const isHighCbdProduct = productTypeLower.startsWith('high cbd') ||
                                               productTypeLower.includes('doh high cbd') ||
                                               productTypeLower.includes('high cbd edible') ||
                                               productTypeLower.includes('high cbd liquid') ||
                                               productTypeLower.includes('high cbd solid') ||
                                               productTypeLower.includes('high cbd topical');

                      // Check if non-classic type (edibles, tinctures, topicals, capsules, gummies)
                      // Non-classic types should NOT have THC option - only NONE, DOH, CBD
                      const isNonClassicType = getUniqueLineages(productType).length === 2;

                      // For high CBD products, CBD trumps DOH (High CBD implies DOH compliance)
                      let effectiveDohStatus = dohStatus;
                      if (isHighCbdProduct) {
                        // If no status or DOH/Yes, default to CBD (High CBD trumps DOH)
                        if (!dohStatus || dohStatus === 'No' || dohStatus === 'NONE' || dohStatus === 'DOH' || dohStatus === 'Yes') {
                          effectiveDohStatus = 'CBD';
                        }
                      }

                      // For non-classic types, convert THC to DOH (THC badge not valid for edibles/tinctures)
                      if (isNonClassicType && effectiveDohStatus === 'THC') {
                        effectiveDohStatus = 'DOH';
                      }

                      // Non-classic types get dropdown without THC option
                      if (isNonClassicType) {
                        return `
                          <select class="form-select form-select-sm doh-dropdown doh-dropdown-mini"
                                  onchange="TagsTable.handleDohChange(this, '${tagName}')">
                            <option value="NONE" ${(!effectiveDohStatus || effectiveDohStatus === 'No' || effectiveDohStatus === 'NONE') ? 'selected' : ''}></option>
                            <option value="DOH" ${effectiveDohStatus === 'DOH' || effectiveDohStatus === 'Yes' ? 'selected' : ''}>DOH</option>
                            <option value="CBD" ${effectiveDohStatus === 'CBD' ? 'selected' : ''}>CBD</option>
                          </select>
                        `;
                      }

                      // Classic types get full dropdown with THC option
                      return `
                        <select class="form-select form-select-sm doh-dropdown doh-dropdown-mini"
                                onchange="TagsTable.handleDohChange(this, '${tagName}')">
                          <option value="NONE" ${(!effectiveDohStatus || effectiveDohStatus === 'No' || effectiveDohStatus === 'NONE') ? 'selected' : ''}></option>
                          <option value="DOH" ${effectiveDohStatus === 'DOH' || effectiveDohStatus === 'Yes' ? 'selected' : ''}>DOH</option>
                          <option value="THC" ${effectiveDohStatus === 'THC' ? 'selected' : ''}>THC</option>
                          <option value="CBD" ${effectiveDohStatus === 'CBD' ? 'selected' : ''}>CBD</option>
                        </select>
                      `;
                    })()}
                </div>
            </td>
            <td class="align-middle">${brand}</td>
            <td class="align-middle">${weightWithUnits || ''}</td>
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
  // CRITICAL: Check sovereign_lineage first (user edits), then canonical_lineage, currentLineage, or Lineage
  let rawLineage = tag.sovereign_lineage || tag.currentLineage || tag.canonical_lineage || tag.Lineage || tag.lineage || '';
  
  // Normalize to uppercase, but keep the original database value
  let lineage = String(rawLineage || '').trim().toUpperCase();
  
  const productType = tag['Product Type*'] || tag.Type || '';
  const isClassicType = productType && getUniqueLineages(productType).length === 6;

  // Detect CBD indicators in product name/strain — applies to ALL product types
  const productNameForCbd = tag['Product Name*'] || tag.ProductName || '';
  const productStrainForCbd = tag['Product Strain'] || tag.productStrain || '';
  const nameAndStrainLower = (productNameForCbd + ' ' + productStrainForCbd).toLowerCase();
  const hasCbdIndicator = ['cbd', 'cbn', 'cbg', 'cbc'].some(token => nameAndStrainLower.includes(token));

  if (hasCbdIndicator && (!lineage || lineage === 'MIXED' || lineage === 'HYBRID' || lineage === 'THC')) {
    // Any product with CBD/CBN/CBG/CBC in name that doesn't already have an explicit lineage
    // should show CBD (classic) or CBD_BLEND (non-classic)
    lineage = isClassicType ? 'CBD' : 'CBD_BLEND';
  } else if (isClassicType && (lineage === 'MIXED' || lineage === 'THC')) {
    // Classic types with MIXED/THC stored value → HYBRID
    lineage = 'HYBRID';
  } else if (!isClassicType && lineage === 'HYBRID') {
    // Non-classic types should never be HYBRID — fall back to MIXED
    lineage = 'MIXED';
  } else if (!lineage) {
    lineage = isClassicType ? 'HYBRID' : 'MIXED';
  }
  
    // CRITICAL FIX: Extract DOH status and normalize it consistently
    const rawDohStatus = tag.DOH || tag['DOH Compliant (Yes/No)'] || tag.doh || tag['DOH Compliant'] || '';
    const dohStatusNormalized = rawDohStatus.toString().trim().toUpperCase();
    
    // Normalize DOH values: YES/Y -> DOH, NO/N -> NONE, empty -> NONE
    let dohStatus = 'NONE';
    if (dohStatusNormalized === 'YES' || dohStatusNormalized === 'Y') {
      dohStatus = 'DOH';
    } else if (dohStatusNormalized === 'DOH' || dohStatusNormalized.includes('DOH') || dohStatusNormalized === 'COMPLIANT') {
      dohStatus = 'DOH';
    } else if (dohStatusNormalized === 'CBD') {
      dohStatus = 'CBD';
    } else if (dohStatusNormalized === 'THC') {
      dohStatus = 'THC';
    } else if (dohStatusNormalized === 'NO' || dohStatusNormalized === 'N' || dohStatusNormalized === 'NONE' || !dohStatusNormalized) {
      dohStatus = 'NONE';
    } else {
      // Keep original value if it's something else (like CBD, THC, etc.)
      dohStatus = dohStatusNormalized;
    }
    
    console.log('🏷️ DOH Status for tag:', tag['Product Name*'] || tag.ProductName, 'rawDohStatus=', rawDohStatus, 'normalized=', dohStatus); // Debug log
    
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
    // Extract weight units from multiple possible sources
    let weightWithUnits = (tag.weightWithUnits || tag.WeightWithUnits || tag.WeightUnits || 
                           tag.CombinedWeight || tag['Weight*'] || tag.Weight || tag.weight || '').toString().trim();
    
    // Format weight to remove .0 decimals (e.g., "1.0g" -> "1g", but "1.5g" stays "1.5g")
    if (weightWithUnits) {
        // Match pattern: number with optional decimal, followed by unit
        const weightMatch = weightWithUnits.match(/^([\d.]+)([a-zA-Z]+.*)$/);
        if (weightMatch) {
            const weightValue = weightMatch[1];
            const unit = weightMatch[2];
            // Try to parse as float
            const weightFloat = parseFloat(weightValue);
            if (!isNaN(weightFloat)) {
                if (weightFloat % 1 === 0) {
                    // It's a whole number, remove decimal point (e.g., "1.0" -> "1")
                    weightWithUnits = `${Math.round(weightFloat)}${unit}`;
                } else {
                    // It's a decimal number, remove trailing zeros (e.g., "1.50" -> "1.5", "1.0" -> "1")
                    // Convert to string and remove trailing zeros and decimal point if needed
                    let formatted = weightFloat.toString();
                    formatted = formatted.replace(/\.0+$/, ''); // Remove .0, .00, etc.
                    formatted = formatted.replace(/(\.\d*?)0+$/, '$1'); // Remove trailing zeros after decimal
                    formatted = formatted.replace(/\.$/, ''); // Remove trailing decimal point
                    weightWithUnits = `${formatted}${unit}`;
                }
            }
        }
    }
    
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
    // CRITICAL: Exclude MIXED for classic types - MIXED is only for non-classic types
    // Note: productType already declared above (line 233), reusing it here
    const uniqueLineages = getUniqueLineages(productType);
    
    // lineage is already normalized above; use it directly for the dropdown
    let dropdownLineage = lineage;
    
    const dropdownOptions = uniqueLineages.map(lin => {
      // Both values are already normalized - direct comparison
      const linNormalized = window.normalizeLineageValue(lin);
      const selected = (dropdownLineage === linNormalized) ? 'selected' : '';
      // Get abbreviation with fallback - handle both PARA and PARAPHERNALIA
      let displayName = lin;
      if (window.ABBREVIATED_LINEAGE) {
        displayName = window.ABBREVIATED_LINEAGE[lin] || 
                     window.ABBREVIATED_LINEAGE[lin.toUpperCase()] || 
                     lin;
      }
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
    // CRITICAL FIX: Use the normalized dohStatus that was already extracted above
    const productTypeLower = productType.toLowerCase().trim();
    // More robust High CBD check - handle variations in product type format
    const isHighCbdProduct = productTypeLower.startsWith('high cbd') || 
                             productTypeLower.includes('doh high cbd') ||
                             productTypeLower.includes('high cbd edible') ||
                             productTypeLower.includes('high cbd liquid') ||
                             productTypeLower.includes('high cbd solid') ||
                             productTypeLower.includes('high cbd topical');
    let dohImageHtml = '';
    
    // Debug: Log DOH badge check for troubleshooting
    console.log(`🏷️ DOH Badge Check for "${tagName}": dohStatus="${dohStatus}", rawDohStatus="${rawDohStatus}", isHighCbdProduct=${isHighCbdProduct}`);
    
    // CRITICAL FIX: High CBD products should ONLY show High CBD badge (not DOH badge)
    // This check must happen FIRST, before any DOH status checks
    if (isHighCbdProduct) {
      // High CBD products get only the High CBD badge, regardless of DOH status
      dohImageHtml = '<img src="/static/img/HighCBD.png" alt="High CBD" title="High CBD Product" style="height: 28px; width: 28px; object-fit: contain; margin-left: 6px; vertical-align: middle;">';
    } else if (dohStatus === 'DOH') {
      // DOH compliant products - show DOH badge (unless it's High THC)
      if (tagName.toLowerCase().includes('high thc')) {
        dohImageHtml = '<img src="/static/img/HighTHC.png" alt="High THC" title="High THC Product" style="height: 28px; width: 28px; object-fit: contain; margin-left: 6px; vertical-align: middle;">';
      } else {
        dohImageHtml = '<img src="/static/img/DOH.png" alt="DOH Compliant" title="DOH Compliant Product" style="height: 36px; width: 36px; object-fit: contain; margin-left: 6px; vertical-align: middle;">';
      }
    } else if (dohStatus === 'CBD') {
      // DOH status is CBD - show High CBD badge (only for non-High CBD product types)
      dohImageHtml = '<img src="/static/img/HighCBD.png" alt="High CBD" title="High CBD Product" style="height: 28px; width: 28px; object-fit: contain; margin-left: 6px; vertical-align: middle;">';
    } else if (dohStatus === 'THC') {
      dohImageHtml = '<img src="/static/img/HighTHC.png" alt="High THC" title="High THC Product" style="height: 28px; width: 28px; object-fit: contain; margin-left: 6px; vertical-align: middle;">';
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
                 data-tag-name="${safeTagName}"
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
            ${(() => {
              const productType = tag['Product Type*'] || tag.Type || '';
              const productTypeLower = productType.toLowerCase().trim();
              // More robust High CBD check - handle variations in product type format
              const isHighCbdProduct = productTypeLower.startsWith('high cbd') || 
                                       productTypeLower.includes('doh high cbd') ||
                                       productTypeLower.includes('high cbd edible') ||
                                       productTypeLower.includes('high cbd liquid') ||
                                       productTypeLower.includes('high cbd solid') ||
                                       productTypeLower.includes('high cbd topical');
              
              // For high CBD products, CBD trumps DOH (High CBD implies DOH compliance)
              let effectiveDohStatus = dohStatus;
              if (isHighCbdProduct) {
                // If no status or DOH/Yes, default to CBD (High CBD trumps DOH)
                if (!dohStatus || dohStatus === 'No' || dohStatus === 'NONE' || dohStatus === 'DOH' || dohStatus === 'Yes') {
                  effectiveDohStatus = 'CBD';
                }
                // Otherwise keep existing status (e.g., if explicitly set to THC)
              }
              
              // All products get normal DOH dropdown
              const dohOptions = [
                `<option value="NONE" ${(!effectiveDohStatus || effectiveDohStatus === 'No' || effectiveDohStatus === 'NONE') ? 'selected' : ''}></option>`,
                `<option value="DOH" ${effectiveDohStatus === 'DOH' || effectiveDohStatus === 'Yes' ? 'selected' : ''}>DOH</option>`,
                `<option value="THC" ${effectiveDohStatus === 'THC' ? 'selected' : ''}>THC</option>`,
                `<option value="CBD" ${effectiveDohStatus === 'CBD' ? 'selected' : ''}>CBD</option>`
              ].join('');
              
              return `
                <select class="form-select form-select-sm doh-dropdown doh-dropdown-mini ms-2" 
                        onchange="TagsTable.handleDohChange(this, '${safeTagName}')"
                        title="DOH Status">
                  ${dohOptions}
                </select>
              `;
            })()}
          </div>
        </div>
      </div>
    `;
  }

  static async handleLineageChange(selectElement, tagName) {
    const newLineage = selectElement.value;
    const tagRow = selectElement.closest(".tag-item") || selectElement.closest(".tag-row");
    const oldLineage = tagRow?.dataset.lineage || 'MIXED';

    console.log(`🔄 Updating lineage for ${tagName}: ${oldLineage} → ${newLineage}`);

    try {
      const response = await fetch("/api/update-lineage", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tag_name: tagName, lineage: newLineage })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        console.error(`❌ API Error: ${data.error || "Failed to update lineage"}`);
        throw new Error(data.error || "Failed to update lineage");
      }
      
      if (!data.success) {
        console.error(`❌ Update failed: ${data.message || data.error || "Unknown error"}`);
        throw new Error(data.message || data.error || "Failed to update lineage");
      }
      
      // Update the local UI dataset
      if (tagRow) {
        tagRow.dataset.lineage = newLineage;
      }
      
      // Update the tag in the main state
      if (window.TagManager && window.TagManager.state) {
        const tag = window.TagManager.state.tags.find(t => t['Product Name*'] === tagName);
        if (tag) {
          tag.currentLineage = newLineage;
          tag.canonical_lineage = newLineage;
          tag.Lineage = newLineage;
        }
      }
      
      console.log(`✅ Lineage updated successfully for "${tagName}"`);
    } catch (error) {
      console.error(`❌ Error updating lineage for ${tagName}:`, error);
      // Revert the dropdown selection on error
      selectElement.value = oldLineage;
    }
  }

  static async handleDohChange(selectElement, tagName) {
    const newDohStatus = selectElement.value;
    const tagRow = selectElement.closest(".tag-item") || selectElement.closest(".tag-row");
    const oldDohStatus = tagRow?.dataset.doh || 'No';

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
      
      // Update the local UI dataset
      if (tagRow) {
        tagRow.dataset.doh = newDohStatus;
      }
      
      // Update the tag in the main state
      if (window.TagManager && window.TagManager.state) {
        const tag = window.TagManager.state.tags.find(t => t['Product Name*'] === tagName);
        if (tag) {
          tag.DOH = newDohStatus;
        }
      }
      
      console.log(`✅ DOH updated successfully for "${tagName}"`);
    } catch (error) {
      console.error(`❌ Error updating DOH for ${tagName}:`, error);
      // Revert the dropdown selection on error
      selectElement.value = oldDohStatus;
    }
  }

  static async handleHighCbdChange(selectElement, tagName) {
    const newHighCbdStatus = selectElement.value;
    // Map "High CBD" to "CBD" for backend storage, "None" to "No"
    const newDohStatus = newHighCbdStatus === 'High CBD' ? 'CBD' : (newHighCbdStatus === 'None' ? 'No' : 'No');
    const tagRow = selectElement.closest(".tag-item") || selectElement.closest(".tag-row");
    const oldDohStatus = tagRow?.dataset.doh || 'No';

    console.log(`🔄 Updating High CBD for ${tagName}: ${oldDohStatus} → ${newDohStatus} (display: ${newHighCbdStatus})`);

    try {
      const response = await fetch("/api/update-doh", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tag_name: tagName, doh: newDohStatus })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        console.error(`❌ API Error: ${data.error || "Failed to update High CBD"}`);
        throw new Error(data.error || "Failed to update High CBD");
      }
      
      if (!data.success) {
        console.error(`❌ Update failed: ${data.message || data.error || "Unknown error"}`);
        throw new Error(data.message || data.error || "Failed to update High CBD status");
      }
      
      // Update the local UI dataset - store as CBD for High CBD, No for None
      if (tagRow) {
        tagRow.dataset.doh = newDohStatus;
      }
      
      // Update the tag in the main state
      if (window.TagManager && window.TagManager.state) {
        const tag = window.TagManager.state.tags.find(t => t['Product Name*'] === tagName);
        if (tag) {
          tag.DOH = newDohStatus;
        }
      }
      
      console.log(`✅ High CBD updated successfully for "${tagName}"`);
    } catch (error) {
      console.error(`❌ Error updating High CBD for ${tagName}:`, error);
      // Revert the dropdown selection on error
      const oldHighCbdStatus = oldDohStatus === 'CBD' || oldDohStatus === 'Yes' || oldDohStatus === 'DOH' ? 'High CBD' : 'None';
      selectElement.value = oldHighCbdStatus;
    }
  }

  static createLineageSelect(currentLineage, tagName, productType = null) {
    // CRITICAL: Exclude MIXED for classic types - MIXED is only for non-classic types
    // Normalize current lineage using consistent helper function
    const normalizedLineage = window.normalizeLineageValue(currentLineage);
    
    const uniqueLineages = getUniqueLineages(productType);
    const options = uniqueLineages.map(lin => {
      // Both values are already normalized - direct comparison
      const linNormalized = window.normalizeLineageValue(lin);
      const selected = (normalizedLineage === linNormalized) ? 'selected' : '';
      // Get abbreviation with fallback - handle both PARA and PARAPHERNALIA
      let displayName = lin;
      if (window.ABBREVIATED_LINEAGE) {
        displayName = window.ABBREVIATED_LINEAGE[lin] || 
                     window.ABBREVIATED_LINEAGE[lin.toUpperCase()] || 
                     lin;
      }
      return `<option value="${lin}" ${selected}>${displayName}</option>`;
    }).join('');
    
    // CRITICAL: Escape tagName to prevent breaking inline handlers with quotes/special chars
    const escapedTagName = (tagName || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
    
    return `
      <select class="form-select form-select-sm lineage-dropdown lineage-dropdown-mini" 
              data-tag-name="${escapedTagName}"
              onchange="TagsTable.handleLineageChange(this, '${escapedTagName}')">
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
    }
  }

  static async handleHighCbdChange(selectElement, tagName) {
    const newHighCbdStatus = selectElement.value;
    // Map "High CBD" to "CBD" for backend storage, "None" to "No"
    const newDohStatus = newHighCbdStatus === 'High CBD' ? 'CBD' : (newHighCbdStatus === 'None' ? 'No' : 'No');
    const tagRow = selectElement.closest(".tag-item") || selectElement.closest(".tag-row");
    const oldDohStatus = tagRow?.dataset.doh || 'No';

    console.log(`🔄 Updating High CBD for ${tagName}: ${oldDohStatus} → ${newDohStatus} (display: ${newHighCbdStatus})`);

    try {
      const response = await fetch("/api/update-doh", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tag_name: tagName, doh: newDohStatus })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        console.error(`❌ API Error: ${data.error || "Failed to update High CBD"}`);
        throw new Error(data.error || "Failed to update High CBD");
      }
      
      if (!data.success) {
        console.error(`❌ Update failed: ${data.message || data.error || "Unknown error"}`);
        throw new Error(data.message || data.error || "Failed to update High CBD status");
      }
      
      // Update the local UI dataset - store as CBD for High CBD, No for None
      if (tagRow) {
        tagRow.dataset.doh = newDohStatus;
      }
      
      // Show success message
      console.log(`✅ Successfully updated High CBD for ${tagName} (${oldDohStatus} → ${newDohStatus}), stored as: ${newDohStatus}`);
      
      // Update the tag in TagManager state if it exists
      if (typeof TagManager !== 'undefined' && TagManager.state) {
        const tag = TagManager.state.tags?.find(t => t['Product Name*'] === tagName);
        if (tag) {
          tag.DOH = newDohStatus;
          tag.doh = newDohStatus;
          tag['DOH Compliant (Yes/No)'] = newDohStatus;
          console.log(`📝 Updated tag High CBD in TagManager.state.tags to: ${newDohStatus}`);
        }
        
        const originalTag = TagManager.state.originalTags?.find(t => t['Product Name*'] === tagName);
        if (originalTag) {
          originalTag.DOH = newDohStatus;
          originalTag.doh = newDohStatus;
          originalTag['DOH Compliant (Yes/No)'] = newDohStatus;
          console.log(`📝 Updated tag High CBD in TagManager.state.originalTags to: ${newDohStatus}`);
        }
        
        // Update High CBD in all displays (available and selected tags)
        if (typeof TagManager.updateDohInAllDisplays === 'function') {
          TagManager.updateDohInAllDisplays(tagName, newDohStatus);
          console.log(`📝 Propagated High CBD update to all displays`);
        }
      }

      // Show brief visual feedback
      selectElement.style.backgroundColor = '#d4edda';
      setTimeout(() => {
        selectElement.style.backgroundColor = '';
      }, 500);

    } catch (error) {
      console.error(`❌ Error updating High CBD for ${tagName}:`, error);
      
      // Revert the dropdown to the old value
      const oldHighCbdStatus = oldDohStatus === 'CBD' || oldDohStatus === 'Yes' || oldDohStatus === 'DOH' ? 'High CBD' : 'None';
      selectElement.value = oldHighCbdStatus;
      
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
    // CRITICAL FIX: Set flag to prevent ANY clearing of selected tags
    if (typeof TagManager !== 'undefined') {
      TagManager._lineageUpdateInProgress = true;
    }
    
    // CRITICAL FIX: Preserve selected tags IMMEDIATELY before anything else
    const savedSelectedTags = typeof TagManager !== 'undefined' && TagManager.state ? 
      [...(TagManager.state.persistentSelectedTags || [])] : [];
    
    // CRITICAL: Log immediately at function start
    console.log('═══════════════════════════════════════════════════════════');
    console.log('🔄 [LINEAGE UPDATE] FUNCTION CALLED');
    console.log('═══════════════════════════════════════════════════════════');
    console.log('Tag Name:', tagName);
    console.log('Select Element:', selectElement);
    console.log('Select Value:', selectElement?.value);
    console.log('📌 Preserved selected tags:', savedSelectedTags.length, savedSelectedTags);
    
    // CRITICAL FIX: Restore function that runs VERY aggressively
    let restoreInterval = null;
    const restoreSelectedTags = () => {
      if (savedSelectedTags.length > 0 && typeof TagManager !== 'undefined' && TagManager.state) {
        const current = TagManager.state.persistentSelectedTags || [];
        const currentSet = new Set(current);
        const savedSet = new Set(savedSelectedTags);
        
        // Check if tags are missing
        const missing = savedSelectedTags.filter(t => !currentSet.has(t));
        if (missing.length > 0 || current.length !== savedSelectedTags.length) {
          console.log('🔄 RESTORING selected tags (missing:', missing.length, '):', savedSelectedTags);
          
          // Restore state
          TagManager.state.persistentSelectedTags = [...savedSelectedTags];
          TagManager.state.selectedTags = new Set(savedSelectedTags);
          
          // Restore checkboxes
          savedSelectedTags.forEach(tagName => {
            const checkboxes = document.querySelectorAll(`input[type="checkbox"][value="${CSS.escape(tagName)}"]`);
            checkboxes.forEach(cb => {
              if (!cb.checked) cb.checked = true;
            });
          });
          
          // Restore display if container is empty
          const selectedContainer = document.getElementById('selectedTags');
          if (selectedContainer && selectedContainer.children.length === 0 && savedSelectedTags.length > 0) {
            // Find tag objects and restore display
            const tagObjects = savedSelectedTags.map(name => {
              return TagManager.state.tags.find(t => (t['Product Name*'] || t.ProductName) === name) ||
                     TagManager.state.originalTags.find(t => (t['Product Name*'] || t.ProductName) === name) ||
                     null;
            }).filter(Boolean);
            
            if (tagObjects.length > 0 && typeof TagManager.updateSelectedTags === 'function') {
              // Temporarily allow update to restore display
              const wasBlocked = TagManager._lineageUpdateInProgress;
              TagManager._lineageUpdateInProgress = false;
              TagManager.updateSelectedTags(tagObjects);
              TagManager._lineageUpdateInProgress = wasBlocked;
            }
          }
        }
      }
    };
    
    // Start VERY aggressive restore - every 50ms
    restoreInterval = setInterval(restoreSelectedTags, 50);
    
    try {
      
      if (!selectElement) {
        console.error('❌ [LINEAGE UPDATE] Missing selectElement');
        return;
      }
      
      if (!tagName) {
        console.error('❌ [LINEAGE UPDATE] Missing tagName');
        tagName = selectElement.getAttribute('data-tag-name') || selectElement.closest('.tag-row')?.dataset?.tagName || 'Unknown';
        console.log(`🔧 [LINEAGE UPDATE] Extracted tagName from DOM: ${tagName}`);
      }
      
      // CRITICAL FIX: Read value multiple ways to handle edge cases where last option doesn't register
      let newLineage = selectElement.value;
      if (!newLineage && selectElement.selectedIndex >= 0) {
        // Fallback: get value from selectedIndex if value is empty
        const selectedOption = selectElement.options[selectElement.selectedIndex];
        if (selectedOption) {
          newLineage = selectedOption.value;
          console.log(`🔧 [LINEAGE UPDATE] Using selectedIndex fallback: ${newLineage}`);
        }
      }
      if (!newLineage) {
        console.error('❌ [LINEAGE UPDATE] No lineage value selected', { 
          tagName, 
          selectElementValue: selectElement.value,
          selectedIndex: selectElement.selectedIndex,
          optionsLength: selectElement.options.length,
          lastOptionValue: selectElement.options.length > 0 ? selectElement.options[selectElement.options.length - 1].value : 'N/A'
        });
        return;
      }
      
      const tagRow = selectElement.closest(".tag-row");
      const oldLineage = tagRow?.dataset.lineage || selectElement.closest(".tag-item")?.dataset.lineage || selectElement.getAttribute('data-lineage');

      console.log(`🔄 [LINEAGE UPDATE] Updating lineage for ${tagName}: ${oldLineage || 'undefined'} → ${newLineage}`);

    // CRITICAL FIX: Use debounced update to prevent database locks on rapid changes
    // Update UI immediately for responsiveness
    if (tagRow) {
      tagRow.dataset.lineage = newLineage.toUpperCase();
    }
    const tagItem = selectElement.closest(".tag-item");
    if (tagItem) {
      tagItem.dataset.lineage = newLineage.toUpperCase();
    }

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

    // Send debounced update to backend (batches rapid changes)
    // This prevents database locks when user changes multiple lineages quickly
    if (typeof TagManager !== 'undefined' && typeof TagManager.updateLineageOnBackendDebounced === 'function') {
      TagManager.updateLineageOnBackendDebounced(tagName, newLineage);
      console.log(`🔄 Lineage change queued for ${tagName}: ${oldLineage} → ${newLineage}`);
    } else {
      // Fallback to direct API call if TagManager debounced method not available
      console.warn('⚠️ TagManager.updateLineageOnBackendDebounced not available, using direct API call');
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

        const result = await response.json();
        if (result.success) {
          console.log(`✅ Successfully updated lineage for ${tagName} (${oldLineage || 'undefined'} → ${newLineage})`);
          console.log(`✅ Update result:`, result);
        } else {
          console.error(`❌ Lineage update failed for ${tagName}:`, result.error || 'Unknown error');
          console.error(`❌ Full response:`, result);
        }
      } catch (error) {
        console.error(`❌ Error updating lineage for ${tagName}:`, error);
        console.error(`❌ Error details:`, { message: error.message, stack: error.stack });
        // Revert the select element to the old value
        selectElement.value = oldLineage;
        selectElement.style.backgroundColor = '#f8d7da';
        setTimeout(() => {
          selectElement.style.backgroundColor = '';
        }, 1000);
        return;
      }
    }

    // CRITICAL FIX: Update lineage in state and UI without any refresh that could clear selected tags
    // We update the state directly and then update the dropdowns, avoiding any full re-renders
    const updateLineageUI = async () => {
      try {
        // CRITICAL FIX: Restore selected tags before checking update status
        restoreSelectedTags();
        
        // CRITICAL FIX: Check if lineage update is still pending before updating
        // If update is still processing, wait a bit longer
        if (typeof TagManager !== 'undefined' && TagManager._lineageUpdateProcessing) {
          console.log('Lineage update still processing, waiting longer before updating UI...');
          setTimeout(updateLineageUI, 1000); // Wait another second
          return;
        }
        
        // Also check if this specific tag's update is pending
        if (typeof TagManager !== 'undefined' && TagManager._lineageUpdatePending && TagManager._lineageUpdatePending.has(tagName)) {
          console.log(`Lineage update for "${tagName}" still pending, waiting longer before updating UI...`);
          setTimeout(updateLineageUI, 1000); // Wait another second
          return;
        }
        
        // CRITICAL FIX: Just update the specific tag's lineage in state and UI
        // Don't fetch all tags - that could trigger a refresh that clears selected tags
        // Instead, query just this one tag's lineage from the database
        try {
          const lineageCheckResponse = await fetch('/api/debug-product-lineage', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              product_names: [tagName]
            })
          });
          
          if (lineageCheckResponse.ok) {
            const lineageData = await lineageCheckResponse.json();
            const productData = (lineageData.results || lineageData.products || [])[0];
            if (productData) {
              const dbLineage = productData.effective_lineage || 
                               productData.database_values?.products_table?.Lineage ||
                               productData.database_values?.strains_table?.canonical_lineage || 
                               productData.database_values?.strains_table?.canonical_lineage;
              
              if (dbLineage) {
                const dbLineageClean = String(dbLineage).trim().toUpperCase();
                
                // Update state directly without triggering any re-renders
                if (TagManager && TagManager.state) {
                  // Update in originalTags
                  const originalTagIndex = TagManager.state.originalTags.findIndex(t => 
                    (t['Product Name*'] || t.ProductName) === tagName
                  );
                  if (originalTagIndex >= 0) {
                    TagManager.state.originalTags[originalTagIndex].Lineage = dbLineageClean;
                    TagManager.state.originalTags[originalTagIndex].lineage = dbLineageClean.toLowerCase();
                    TagManager.state.originalTags[originalTagIndex].currentLineage = dbLineageClean;
                    TagManager.state.originalTags[originalTagIndex].canonical_lineage = dbLineageClean;
                  }
                  
                  // Update in current tags
                  const currentTagIndex = TagManager.state.tags.findIndex(t => 
                    (t['Product Name*'] || t.ProductName) === tagName
                  );
                  if (currentTagIndex >= 0) {
                    TagManager.state.tags[currentTagIndex].Lineage = dbLineageClean;
                    TagManager.state.tags[currentTagIndex].lineage = dbLineageClean.toLowerCase();
                    TagManager.state.tags[currentTagIndex].currentLineage = dbLineageClean;
                    TagManager.state.tags[currentTagIndex].canonical_lineage = dbLineageClean;
                  }
                }
                
                // Update dropdowns directly in DOM without any re-rendering
                const updateLineageDropdown = (containerId) => {
                  const container = document.getElementById(containerId);
                  if (!container) return;
                  
                  // Find all tag elements
                  const tagElements = container.querySelectorAll('.tag-entry, [data-tag-name]');
                  tagElements.forEach(tagElement => {
                    const elementTagName = tagElement.getAttribute('data-tag-name') || 
                                          tagElement.querySelector('.tag-name, [data-product-name]')?.textContent?.trim() ||
                                          tagElement.textContent?.match(/^[^-\n]+/)?.[0]?.trim();
                    
                    if (elementTagName && (elementTagName === tagName || elementTagName.includes(tagName) || tagName.includes(elementTagName))) {
                      const lineageSelect = tagElement.querySelector('.lineage-select, .lineage-dropdown, select.lineage-select');
                      if (lineageSelect && lineageSelect.value !== dbLineageClean) {
                        // Mark as programmatic update to prevent change handler
                        lineageSelect._isProgrammaticUpdate = true;
                        lineageSelect.value = dbLineageClean;
                        
                        // Update tag color if function exists
                        if (typeof TagManager !== 'undefined' && typeof TagManager.forceTagColorUpdate === 'function') {
                          const tag = TagManager.state.tags.find(t => (t['Product Name*'] || t.ProductName) === tagName) ||
                                     TagManager.state.originalTags.find(t => (t['Product Name*'] || t.ProductName) === tagName);
                          if (tag) {
                            TagManager.forceTagColorUpdate(tag, dbLineageClean);
                          }
                        }
                        
                        // Clear flag after delay
                        setTimeout(() => {
                          lineageSelect._isProgrammaticUpdate = false;
                        }, 100);
                      }
                    }
                  });
                };
                
                // Update both available and selected tags containers
                updateLineageDropdown('availableTags');
                updateLineageDropdown('selectedTags');
                
                console.log(`✅ Updated lineage for "${tagName}" to ${dbLineageClean} (selected tags preserved)`);
              }
            }
          }
        } catch (lineageCheckErr) {
          console.warn('Could not verify lineage from database:', lineageCheckErr);
        }
        
        // CRITICAL FIX: Final restore and clear interval
        restoreSelectedTags();
        if (restoreInterval) {
          clearInterval(restoreInterval);
        }
      } catch (e) {
        console.warn('Background lineage update failed:', e);
        // CRITICAL FIX: Restore on error too
        restoreSelectedTags();
        if (restoreInterval) {
          clearInterval(restoreInterval);
        }
      }
    };

    // REMOVED: This setTimeout was causing selected tags to randomly disappear 2 seconds after lineage changes
    // The lineage is already updated immediately in the database and state, no need for delayed UI update
    // setTimeout(updateLineageUI, 2000);

    // Show brief visual feedback
    selectElement.style.backgroundColor = '#d4edda';
    setTimeout(() => {
      selectElement.style.backgroundColor = '';
    }, 500);
    
    // CRITICAL FIX: Final restore and clear interval
    if (restoreInterval) {
      clearInterval(restoreInterval);
    }
    restoreSelectedTags();
    
    // CRITICAL FIX: Clear the flag after a delay to allow any pending operations to complete
    setTimeout(() => {
      if (typeof TagManager !== 'undefined') {
        TagManager._lineageUpdateInProgress = false;
        console.log('✅ Cleared lineage update flag');
      }
    }, 3000); // Wait 3 seconds after update completes
    
    console.log(`✅ handleLineageChange completed for ${tagName}`);
  } catch (error) {
    // CRITICAL: Catch any errors in the handler itself
    console.error(`❌ CRITICAL ERROR in handleLineageChange for ${tagName}:`, error);
    console.error(`❌ Error stack:`, error.stack);
    
    // CRITICAL FIX: Clear interval and restore selected tags even on error
    if (restoreInterval) {
      clearInterval(restoreInterval);
    }
    restoreSelectedTags();
    
    // CRITICAL FIX: Clear the flag on error too
    setTimeout(() => {
      if (typeof TagManager !== 'undefined') {
        TagManager._lineageUpdateInProgress = false;
      }
    }, 1000);
    
    // Show error feedback to user
    if (selectElement) {
      selectElement.style.backgroundColor = '#f8d7da';
      setTimeout(() => {
        selectElement.style.backgroundColor = '';
      }, 2000);
    }
    
    // Show user-friendly error
    if (typeof showToast === 'function') {
      showToast(`Failed to update lineage: ${error.message}`, 'error');
    } else {
      alert(`Failed to update lineage: ${error.message}`);
    }
  }
  }

  static openLineageEditor(tagName, currentLineage, productType = null) {
    const modal = document.getElementById('lineageEditorModal');
    if (!modal) return;

    // Try to get product type from tag if not provided
    if (!productType && typeof TagManager !== 'undefined') {
      const tag = TagManager.getTagByName(tagName);
      if (tag) {
        productType = tag['Product Type*'] || tag.productType || tag.ProductType || null;
      }
    }

    // Store the currently focused element before opening modal
    const activeElement = document.activeElement;
    if (activeElement && !modal.contains(activeElement)) {
      activeElement.setAttribute('data-bs-focus-prev', 'true');
    }

    document.getElementById('editTagName').value = tagName;
    const select = document.getElementById('editLineageSelect');
    select.innerHTML = '';
    // CRITICAL FIX: Use getUniqueLineages to filter options based on product type
    // For nonclassic types (edibles, tinctures, etc.), only show MIXED and CBD
    // For paraphernalia, only show PARA
    // For classic types, show all classic lineages
    const uniqueLineages = getUniqueLineages(productType);
    uniqueLineages.forEach(lin => {
      const option = document.createElement('option');
      option.value = lin;
      // Get abbreviation with fallback - handle both PARA and PARAPHERNALIA
      let displayName = lin;
      if (window.ABBREVIATED_LINEAGE) {
        displayName = window.ABBREVIATED_LINEAGE[lin] || 
                     window.ABBREVIATED_LINEAGE[lin.toUpperCase()] || 
                     lin;
      }
      option.textContent = displayName;
      if (currentLineage === lin) {
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
      // Map UI-only option to server value
      const sendLineage = (newLineage === 'THC') ? 'MIXED' : newLineage;

      try {
          const response = await fetch('/api/update-lineage', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
                body: JSON.stringify({
                    tag_name: tagName,
                    lineage: sendLineage
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
          
          // CRITICAL FIX: Don't re-render after lineage change - it clears selected tags
          // Just update the specific tag's lineage in state and UI directly
          if (typeof TagManager !== 'undefined') {
            try {
              // Update the tag's lineage in state directly
              const tagIndex = TagManager.state.originalTags.findIndex(t => (t['Product Name*'] || t.ProductName) === tagName);
              if (tagIndex >= 0) {
                TagManager.state.originalTags[tagIndex].Lineage = newLineage;
                TagManager.state.originalTags[tagIndex].lineage = newLineage.toLowerCase();
                TagManager.state.originalTags[tagIndex].currentLineage = newLineage;
                TagManager.state.originalTags[tagIndex].canonical_lineage = newLineage;
              }
              
              const currentTagIndex = TagManager.state.tags.findIndex(t => (t['Product Name*'] || t.ProductName) === tagName);
              if (currentTagIndex >= 0) {
                TagManager.state.tags[currentTagIndex].Lineage = newLineage;
                TagManager.state.tags[currentTagIndex].lineage = newLineage.toLowerCase();
                TagManager.state.tags[currentTagIndex].currentLineage = newLineage;
                TagManager.state.tags[currentTagIndex].canonical_lineage = newLineage;
              }
              
              // Update UI directly without re-rendering
              if (typeof TagManager.updateTagLineageInUI === 'function') {
                TagManager.updateTagLineageInUI(tagName, newLineage);
              }
              
              console.log('✅ Updated lineage in state and UI (selected tags preserved)');
            } catch (updateError) {
              console.warn('Failed to update lineage in state:', updateError);
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
                      <th class="tag-name-header">Name</th>
                      <th>Lineage</th>
                      <th>DOH</th>
                      <th>${brandHeaderText}</th>
                      <th>Weight</th>
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
    // Add lightweight checkbox change listeners (UI-only; heavy work is centralized in TagManager)
    container.querySelectorAll('.tag-checkbox').forEach(checkbox => {
      checkbox.addEventListener('change', function(e) {
        try {
          // Keep this handler minimal so checkbox toggles feel instant.
          // TagManager's delegated handlers will manage state, counts, and
          // any cross-list synchronization.
          if (typeof e.stopImmediatePropagation === 'function') e.stopImmediatePropagation();
          e.stopPropagation();
        } catch (error) {
          console.error('Error in lightweight checkbox change handler:', error);
        }
      }, { passive: true });
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

// CRITICAL: Expose TagsTable globally so inline event handlers can access it
// This ensures onchange="TagsTable.handleLineageChange(...)" works in HTML
if (typeof window !== 'undefined') {
  window.TagsTable = TagsTable;
  // Also expose handleLineageChange directly for easier debugging
  window.handleLineageChange = TagsTable.handleLineageChange.bind(TagsTable);
  console.log('✅ TagsTable exposed globally on window object');
  console.log('✅ TagsTable.handleLineageChange available:', typeof TagsTable.handleLineageChange);
  
  // CRITICAL: Add event delegation as fallback for lineage dropdowns
  // This catches lineage changes even if inline handlers don't work
  document.addEventListener('change', function(e) {
    if (e.target && e.target.classList && e.target.classList.contains('lineage-dropdown')) {
      const tagName = e.target.getAttribute('data-tag-name') || 
                      e.target.closest('.tag-row')?.dataset?.tagName ||
                      e.target.closest('.tag-item')?.dataset?.tagName;
      
      if (tagName) {
        console.log('🔄 [EVENT DELEGATION] Caught lineage change via event delegation for:', tagName);
        TagsTable.handleLineageChange(e.target, tagName);
      } else {
        console.warn('⚠️ [EVENT DELEGATION] Lineage dropdown changed but no tagName found');
      }
    }
  });
  console.log('✅ Event delegation added for lineage dropdowns');
}
