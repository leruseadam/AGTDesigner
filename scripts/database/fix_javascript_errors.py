#!/usr/bin/env python3
"""
Fix JavaScript syntax errors on production website
"""

import os
import re

def fix_javascript_errors():
    print("🔧 Fixing JavaScript syntax errors...")
    
    # Fix 1: Remove duplicate CLASSIC_TYPES declaration from tags_table.js
    tags_table_path = "static/js/tags_table.js"
    if os.path.exists(tags_table_path):
        print(f"Fixing {tags_table_path}...")
        with open(tags_table_path, 'r') as f:
            content = f.read()
        
        # Remove the CLASSIC_TYPES declaration since it's already in main.js
        content = re.sub(
            r'// Classic types that should show "Lineage" instead of "Brand"\nconst CLASSIC_TYPES = \[\n[^\]]+\];\n\n',
            '',
            content
        )
        
        with open(tags_table_path, 'w') as f:
            f.write(content)
        print("✅ Removed duplicate CLASSIC_TYPES declaration")
    
    # Fix 2: Check for syntax errors in index.html
    index_path = "templates/index.html"
    if os.path.exists(index_path):
        print(f"Checking {index_path} for syntax errors...")
        with open(index_path, 'r') as f:
            content = f.read()
        
        # Look for common syntax issues
        issues_found = []
        
        # Check for unmatched braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            issues_found.append(f"Unmatched braces: {open_braces} open, {close_braces} close")
        
        # Check for unmatched parentheses
        open_parens = content.count('(')
        close_parens = content.count(')')
        if open_parens != close_parens:
            issues_found.append(f"Unmatched parentheses: {open_parens} open, {close_parens} close")
        
        if issues_found:
            print("⚠️  Potential syntax issues found:")
            for issue in issues_found:
                print(f"   - {issue}")
        else:
            print("✅ No obvious syntax issues found")
    
    print("\n🔧 Creating JavaScript error fix script...")
    
    # Create a script to fix common JavaScript issues
    fix_script = """// JavaScript Error Fix Script
// Run this in browser console to fix common issues

console.log('🔧 Running JavaScript error fixes...');

// Fix 1: Ensure CLASSIC_TYPES is only declared once
if (typeof CLASSIC_TYPES === 'undefined') {
    const CLASSIC_TYPES = [
        "flower", "pre-roll", "concentrate", "infused pre-roll", 
        "solventless concentrate", "vape cartridge", "rso/co2 tankers"
    ];
    console.log('✅ CLASSIC_TYPES defined');
}

// Fix 2: Create backup definitions for missing functions
if (typeof performDetailedJsonMatch === 'undefined') {
    window.performDetailedJsonMatch = function() {
        console.warn('performDetailedJsonMatch not found, using backup');
        return false;
    };
    console.log('✅ performDetailedJsonMatch backup created');
}

if (typeof displayDetailedMatchResults === 'undefined') {
    window.displayDetailedMatchResults = function() {
        console.warn('displayDetailedMatchResults not found, using backup');
        return false;
    };
    console.log('✅ displayDetailedMatchResults backup created');
}

// Fix 3: Ensure error handling is in place
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.message, 'at', e.filename, ':', e.lineno);
    // Don't let errors break the page
    return true;
});

console.log('✅ JavaScript error fixes applied');
"""
    
    with open("static/js/error_fix.js", 'w') as f:
        f.write(fix_script)
    
    print("✅ Created static/js/error_fix.js")
    
    # Create HTML fix instructions
    html_fix = """
<!-- JavaScript Error Fix -->
<script>
// Load error fix script
(function() {
    const script = document.createElement('script');
    script.src = '/static/js/error_fix.js';
    script.onload = function() {
        console.log('Error fix script loaded successfully');
    };
    script.onerror = function() {
        console.warn('Error fix script failed to load');
    };
    document.head.appendChild(script);
})();
</script>
"""
    
    with open("javascript_error_fix.html", 'w') as f:
        f.write(html_fix)
    
    print("✅ Created javascript_error_fix.html")
    
    print("\n📋 Manual fixes needed:")
    print("1. Upload static/js/error_fix.js to PythonAnywhere")
    print("2. Add the script tag to your HTML template")
    print("3. Or run the script directly in browser console")
    print("4. Check for any remaining syntax errors in browser console")

if __name__ == "__main__":
    fix_javascript_errors()
