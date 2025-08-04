// Test script for modal accessibility fix
// Run this in the browser console to test the fix

console.log('Testing modal accessibility fix...');

// Test 1: Check if modals have proper event listeners
function testModalEventListeners() {
  const modals = document.querySelectorAll('.modal');
  console.log(`Found ${modals.length} modals`);
  
  modals.forEach(modal => {
    const hasShowHandler = modal._accessibilityShowHandler !== undefined;
    const hasHideHandler = modal._accessibilityHideHandler !== undefined;
    console.log(`Modal ${modal.id}: Show handler: ${hasShowHandler}, Hide handler: ${hasHideHandler}`);
  });
}

// Test 2: Simulate modal opening and check aria-hidden
function testModalAriaHidden() {
  const jsonMatchModal = document.getElementById('jsonMatchModal');
  if (!jsonMatchModal) {
    console.log('JSON Match Modal not found');
    return;
  }
  
  console.log('Testing JSON Match Modal accessibility...');
  console.log('Initial aria-hidden:', jsonMatchModal.getAttribute('aria-hidden'));
  
  // Simulate opening the modal
  const modal = new bootstrap.Modal(jsonMatchModal);
  
  // Check if aria-hidden is removed when modal is shown
  jsonMatchModal.addEventListener('show.bs.modal', function() {
    console.log('Modal show event fired');
    console.log('aria-hidden after show:', this.getAttribute('aria-hidden'));
  });
  
  jsonMatchModal.addEventListener('shown.bs.modal', function() {
    console.log('Modal shown event fired');
    console.log('aria-hidden after shown:', this.getAttribute('aria-hidden'));
    
    // Close the modal after a short delay
    setTimeout(() => {
      modal.hide();
    }, 1000);
  });
  
  // Check if aria-hidden is restored when modal is hidden
  jsonMatchModal.addEventListener('hidden.bs.modal', function() {
    console.log('Modal hide event fired');
    console.log('aria-hidden after hide:', this.getAttribute('aria-hidden'));
  });
  
  // Open the modal
  modal.show();
}

// Test 3: Check focus management
function testFocusManagement() {
  console.log('Testing focus management...');
  
  // Create a test button to focus
  const testButton = document.createElement('button');
  testButton.textContent = 'Test Focus Button';
  testButton.id = 'testFocusButton';
  testButton.style.position = 'fixed';
  testButton.style.top = '10px';
  testButton.style.left = '10px';
  testButton.style.zIndex = '9999';
  document.body.appendChild(testButton);
  
  // Focus the test button
  testButton.focus();
  console.log('Focused test button:', document.activeElement);
  
  // Open JSON Match Modal
  const jsonMatchModal = document.getElementById('jsonMatchModal');
  if (jsonMatchModal) {
    const modal = new bootstrap.Modal(jsonMatchModal);
    
    jsonMatchModal.addEventListener('show.bs.modal', function() {
      console.log('Modal opened, checking focus...');
      console.log('Active element:', document.activeElement);
      console.log('Test button has data-bs-focus-prev:', testButton.hasAttribute('data-bs-focus-prev'));
      
      // Close modal after 2 seconds
      setTimeout(() => {
        modal.hide();
      }, 2000);
    });
    
    jsonMatchModal.addEventListener('hidden.bs.modal', function() {
      console.log('Modal closed, checking focus restoration...');
      setTimeout(() => {
        console.log('Active element after modal close:', document.activeElement);
        console.log('Test button has data-bs-focus-prev:', testButton.hasAttribute('data-bs-focus-prev'));
        
        // Clean up test button
        testButton.remove();
      }, 100);
    });
    
    modal.show();
  }
}

// Test 4: Check for accessibility violations
function checkAccessibilityViolations() {
  console.log('Checking for accessibility violations...');
  
  const openModals = document.querySelectorAll('.modal.show');
  const violations = [];
  
  openModals.forEach(modal => {
    const hasAriaHidden = modal.hasAttribute('aria-hidden');
    const hasFocusableElements = modal.querySelectorAll('button, input, select, textarea, [tabindex]').length > 0;
    
    if (hasAriaHidden && hasFocusableElements) {
      violations.push(`Modal ${modal.id} has aria-hidden with focusable elements`);
    }
  });
  
  if (violations.length > 0) {
    console.error('Accessibility violations found:', violations);
  } else {
    console.log('No accessibility violations detected');
  }
}

// Test 5: Test MutationObserver functionality
function testMutationObserver() {
  console.log('Testing MutationObserver functionality...');
  
  const jsonMatchModal = document.getElementById('jsonMatchModal');
  if (!jsonMatchModal) {
    console.log('JSON Match Modal not found');
    return;
  }
  
  // Manually set aria-hidden to test the observer
  console.log('Manually setting aria-hidden to true...');
  jsonMatchModal.setAttribute('aria-hidden', 'true');
  console.log('aria-hidden after manual set:', jsonMatchModal.getAttribute('aria-hidden'));
  
  // Add show class to simulate visible modal
  jsonMatchModal.classList.add('show');
  console.log('Added show class to modal');
  
  // Wait a moment for the observer to react
  setTimeout(() => {
    console.log('aria-hidden after observer should have reacted:', jsonMatchModal.getAttribute('aria-hidden'));
    jsonMatchModal.classList.remove('show');
  }, 100);
}

// Run all tests
console.log('=== Running Modal Accessibility Tests ===');
testModalEventListeners();
checkAccessibilityViolations();
testMutationObserver();

// Uncomment the following lines to run interactive tests
// testModalAriaHidden();
// testFocusManagement();

console.log('=== Tests Complete ===');
console.log('To run interactive tests, uncomment the testModalAriaHidden() and testFocusManagement() calls in the console.'); 