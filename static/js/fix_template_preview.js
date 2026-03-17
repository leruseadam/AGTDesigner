// Template Preview Fix
// This script fixes the template preview functionality in the Edit Template modal

let templatePreviewInitAttempts = 0;
let templatePreviewInitialized = false;
const MAX_INIT_ATTEMPTS = 2; // Reduced from 10 to avoid console spam

document.addEventListener('DOMContentLoaded', function() {
    scheduleTemplatePreviewInit();
});

function scheduleTemplatePreviewInit(delay = 500) {
    setTimeout(function() {
        initializeTemplatePreview();
    }, delay);
}

function initializeTemplatePreview() {
    if (templatePreviewInitialized) {
        return;
    }
    
    // Check if we've exceeded max attempts
    if (templatePreviewInitAttempts >= MAX_INIT_ATTEMPTS) {
        // Already tried enough times, stop trying
        return;
    }
    
    templatePreviewInitAttempts += 1;
    
    // Get all the necessary elements
    const editTemplateModal = document.getElementById('editTemplateModal');
    const templateSelectModal = document.getElementById('templateSelectModal');
    const scaleInputModal = document.getElementById('scaleInputModal');
    const fontSelectModal = document.getElementById('fontSelectModal');
    const fontSizingModeModal = document.getElementById('fontSizingModeModal');
    const fieldFontSizesSection = document.getElementById('fieldFontSizesSection');
    const templateSelect = document.getElementById('templateSelect');
    const scaleInput = document.getElementById('scaleInput');
    const fontSelect = document.getElementById('fontSelect');
    const saveTemplateBtn = document.getElementById('saveTemplateBtn');
    const previewContainer = document.getElementById('templatePreviewModal');
    
    // If the modal doesn't exist, exit gracefully without spamming console
    if (!editTemplateModal || !previewContainer) {
        if (templatePreviewInitAttempts < MAX_INIT_ATTEMPTS) {
            // Only retry once more, silently
            scheduleTemplatePreviewInit(1000);
        }
        // Exit silently if modal doesn't exist - it's not required for the app to function
        return;
    }
    
    templatePreviewInitialized = true;
    
    // Function to update the template preview
    function updateTemplatePreview() {
        if (!previewContainer) {
            return;
        }
        
        // Get current values with fallbacks
        const templateType = templateSelectModal ? templateSelectModal.value : 'vertical';
        const fontFamily = fontSelectModal ? fontSelectModal.value : 'Arial';
        const scale = scaleInputModal ? scaleInputModal.value : '1.0';
        const fontSizeMode = fontSizingModeModal ? fontSizingModeModal.value : 'auto';
        
        // Get font sizes for fixed mode
        let brandSize = 14;
        let descriptionSize = 16;
        let priceSize = 18;
        let lineageSize = 12;
        
        if (fontSizeMode === 'fixed') {
            const brandElement = document.getElementById('brandFontSize');
            const descriptionElement = document.getElementById('descriptionFontSize');
            const priceElement = document.getElementById('priceFontSize');
            const lineageElement = document.getElementById('lineageFontSize');
            
            if (brandElement) brandSize = brandElement.value || 14;
            if (descriptionElement) descriptionSize = descriptionElement.value || 16;
            if (priceElement) priceSize = priceElement.value || 18;
            if (lineageElement) lineageSize = lineageElement.value || 12;
        }
        
        // Create preview HTML
        let previewHtml = `
            <div style="font-family: ${fontFamily}; transform: scale(${scale}); transform-origin: top left;">
                <div style="border: 1px solid #ccc; padding: 8px; margin: 4px; background: white; border-radius: 4px;">
                    <div style="font-weight: bold; font-size: ${brandSize}px; color: #333; margin-bottom: 4px;">Sample Brand</div>
                    <div style="font-size: ${descriptionSize}px; color: #666; margin-bottom: 4px;">Sample Description Text</div>
                    <div style="font-size: ${priceSize}px; font-weight: bold; color: #007bff; margin-bottom: 4px;">$25.00</div>
                    <div style="font-size: ${lineageSize}px; color: #009900; text-transform: uppercase;">HYBRID</div>
                </div>
            </div>
        `;
        
        previewContainer.innerHTML = previewHtml;
    }
    
    // Font sizing mode change handler
    if (fontSizingModeModal && fieldFontSizesSection) {
        fontSizingModeModal.addEventListener('change', function() {
            if (this.value === 'fixed') {
                fieldFontSizesSection.style.display = 'block';
            } else {
                fieldFontSizesSection.style.display = 'none';
            }
            updateTemplatePreview();
        });
    }
    
    // Add event listeners for preview updates
    const previewElements = [
        templateSelectModal, scaleInputModal, fontSelectModal, 
        fontSizingModeModal, document.getElementById('descriptionFontSize'),
        document.getElementById('brandFontSize'), document.getElementById('priceFontSize'),
        document.getElementById('lineageFontSize'), document.getElementById('ratioFontSize'),
        document.getElementById('vendorFontSize')
    ];
    
    previewElements.forEach(element => {
        if (element) {
            element.addEventListener('change', updateTemplatePreview);
            element.addEventListener('input', updateTemplatePreview);
        }
    });
    
    // When modal opens, sync values from main form and update preview
    editTemplateModal.addEventListener('show.bs.modal', function () {
        // Sync values from main form
        if (templateSelectModal && templateSelect) {
            templateSelectModal.value = templateSelect.value;
        }
        if (scaleInputModal && scaleInput) {
            scaleInputModal.value = scaleInput.value;
        }
        if (fontSelectModal && fontSelect) {
            fontSelectModal.value = fontSelect.value;
        }
        
        // Set default values for new fields
        if (fontSizingModeModal) fontSizingModeModal.value = 'auto';
        if (document.getElementById('lineSpacingModal')) document.getElementById('lineSpacingModal').value = '1.0';
        if (document.getElementById('paragraphSpacingModal')) document.getElementById('paragraphSpacingModal').value = '0';
        
        // Update preview with a slight delay to ensure modal is fully rendered
        setTimeout(updateTemplatePreview, 200);
    });
    
    // When save button is clicked, sync values back to main form
    if (saveTemplateBtn) {
        saveTemplateBtn.addEventListener('click', function () {
            if (templateSelect && templateSelectModal) {
                templateSelect.value = templateSelectModal.value;
            }
            if (scaleInput && scaleInputModal) {
                scaleInput.value = scaleInputModal.value;
            }
            if (fontSelect && fontSelectModal) {
                fontSelect.value = fontSelectModal.value;
            }
            
            // Save additional settings to localStorage for persistence
            let templateType = templateSelectModal ? templateSelectModal.value : 'vertical';
            // SAFETY: Clamp templateType to one of the actual options on the main select.
            // If an old or invalid value is present (e.g., from a previous version),
            // force it to a known-safe default so the dropdown never renders blank.
            if (templateSelect) {
                const allowedValues = Array.from(templateSelect.options || []).map(opt => opt.value);
                if (!allowedValues.includes(templateType)) {
                    templateType = allowedValues.includes('horizontal') ? 'horizontal' : (allowedValues[0] || 'horizontal');
                }
            }

            const templateSettings = {
                templateType: templateType,
                scale: scaleInputModal ? scaleInputModal.value : '1.0',
                font: fontSelectModal ? fontSelectModal.value : 'Arial',
                fontSizeMode: fontSizingModeModal ? fontSizingModeModal.value : 'auto',
                lineBreaks: document.getElementById('enableLineBreaksModal')?.checked || true,
                textWrapping: document.getElementById('enableTextWrappingModal')?.checked || true,
                boldHeaders: document.getElementById('enableBoldTextModal')?.checked || false,
                italicDescriptions: document.getElementById('enableItalicTextModal')?.checked || false,
                lineSpacing: document.getElementById('lineSpacingModal')?.value || '1.0',
                paragraphSpacing: document.getElementById('paragraphSpacingModal')?.value || '0',
                textColor: document.getElementById('textColorModal')?.value || '#000000',
                backgroundColor: document.getElementById('backgroundColorModal')?.value || '#ffffff',
                headerColor: document.getElementById('headerColorModal')?.value || '#333333',
                accentColor: document.getElementById('accentColorModal')?.value || '#007bff',
                autoResize: document.getElementById('enableAutoResizeModal')?.checked || true,
                smartTruncation: document.getElementById('enableSmartTruncationModal')?.checked || true,
                optimization: document.getElementById('enableOptimizationModal')?.checked || false,
                fieldFontSizes: {
                    description: document.getElementById('descriptionFontSize')?.value || 16,
                    brand: document.getElementById('brandFontSize')?.value || 14,
                    price: document.getElementById('priceFontSize')?.value || 18,
                    lineage: document.getElementById('lineageFontSize')?.value || 12,
                    ratio: document.getElementById('ratioFontSize')?.value || 10,
                    vendor: document.getElementById('vendorFontSize')?.value || 8
                }
            };
            
            // Save to localStorage for persistence
            localStorage.setItem('templateSettings', JSON.stringify(templateSettings));
            
            // Save to backend for generation
            fetch('/api/template-settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(templateSettings)
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    console.warn('Template Preview Fix: Failed to save template settings to backend:', data.error);
                }
            })
            .catch(error => {
                console.error('Template Preview Fix: Error saving template settings to backend:', error);
            });
            
            // Close the modal
            const modal = bootstrap.Modal.getInstance(editTemplateModal);
            if (modal) {
                modal.hide();
            }
            
            // Show success message
            if (typeof showToast === 'function') {
                showToast('Template settings saved successfully!', 'success');
            }
        });
    }
    
    // Load saved settings when page loads
    const savedSettings = localStorage.getItem('templateSettings');
    if (savedSettings) {
        try {
            const settings = JSON.parse(savedSettings);
            let templateType = settings.templateType || 'vertical';

            if (templateSelect) {
                const allowedValues = Array.from(templateSelect.options || []).map(opt => opt.value);
                if (!allowedValues.includes(templateType)) {
                    // Invalid / legacy value in storage → normalize to a safe default
                    templateType = allowedValues.includes('horizontal') ? 'horizontal' : (allowedValues[0] || 'horizontal');
                    settings.templateType = templateType;
                    // Persist the normalized value so future loads are clean
                    localStorage.setItem('templateSettings', JSON.stringify(settings));
                }
                templateSelect.value = templateType;
            }

            if (scaleInput) scaleInput.value = settings.scale || '1.0';
            if (fontSelect) fontSelect.value = settings.font || 'Arial';
        } catch (e) {
            // Silently fail if settings can't be loaded
        }
    }
}

// Make the function globally available for the manual refresh button
window.updateTemplatePreview = function() {
    const previewContainer = document.getElementById('templatePreviewModal');
    if (previewContainer) {
        // Trigger the preview update
        const event = new Event('change');
        const templateSelectModal = document.getElementById('templateSelectModal');
        if (templateSelectModal) {
            templateSelectModal.dispatchEvent(event);
        }
    }
}; 