#!/usr/bin/env python3
"""
PythonAnywhere File Upload Fix
Comprehensive solution for file upload issues on PythonAnywhere.
"""

import re

def print_fix_plan():
    """Print the comprehensive fix plan."""
    
    print("🔧 PythonAnywhere File Upload Fix")
    print("=" * 40)
    print()
    
    print("📋 ISSUES IDENTIFIED:")
    print("-" * 25)
    print("• Server returning HTML instead of JSON")
    print("• TagManager.showError is not a function")
    print("• File upload failing on PythonAnywhere")
    print("• JavaScript errors preventing upload")
    print()
    
    print("🛠️ COMPREHENSIVE FIX PLAN:")
    print("-" * 30)
    print("1. Fix JavaScript error handling")
    print("2. Add proper error methods to TagManager")
    print("3. Improve server-side error handling")
    print("4. Add PythonAnywhere-specific upload optimizations")
    print("5. Test the complete fix")
    print()

def fix_javascript_errors():
    """Fix JavaScript errors in enhanced-ui.js."""
    
    print("🔧 Fixing JavaScript errors...")
    
    # Fix the TagManager.showError calls
    enhanced_ui_path = "static/js/enhanced-ui.js"
    
    with open(enhanced_ui_path, 'r') as f:
        content = f.read()
    
    # Replace TagManager.showError with showToast
    content = re.sub(
        r'TagManager\.showError\(([^)]+)\)',
        r'showToast("error", \1)',
        content
    )
    
    with open(enhanced_ui_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed TagManager.showError calls")

def add_tagmanager_error_methods():
    """Add error handling methods to TagManager."""
    
    print("🔧 Adding error methods to TagManager...")
    
    main_js_path = "static/js/main.js"
    
    with open(main_js_path, 'r') as f:
        content = f.read()
    
    # Find the TagManager object and add error methods
    tagmanager_pattern = r'(const TagManager = \{[\s\S]*?)(\}; // TagManager)'
    
    error_methods = '''
    // Error handling methods
    showError(message) {
        console.error('TagManager Error:', message);
        if (typeof showToast === 'function') {
            showToast('error', message);
        } else {
            alert('Error: ' + message);
        }
    },
    
    showSuccess(message) {
        console.log('TagManager Success:', message);
        if (typeof showToast === 'function') {
            showToast('success', message);
        }
    },
    
    showWarning(message) {
        console.warn('TagManager Warning:', message);
        if (typeof showToast === 'function') {
            showToast('warning', message);
        }
    },
    
    showInfo(message) {
        console.info('TagManager Info:', message);
        if (typeof showToast === 'function') {
            showToast('info', message);
        }
    },
'''
    
    # Insert error methods before the closing brace
    content = re.sub(
        tagmanager_pattern,
        r'\1' + error_methods + r'\2',
        content
    )
    
    with open(main_js_path, 'w') as f:
        f.write(content)
    
    print("✅ Added error methods to TagManager")

def improve_server_error_handling():
    """Improve server-side error handling for PythonAnywhere."""
    
    print("🔧 Improving server error handling...")
    
    app_py_path = "app.py"
    
    with open(app_py_path, 'r') as f:
        content = f.read()
    
    # Add better error handling to the upload route
    upload_route_pattern = r'(@app\.route\(\'/upload\', methods=\[\'POST\'\]\)\s*def upload_file\(\):[\s\S]*?)(return jsonify\(\{.*?\}\), \d+\))'
    
    improved_error_handling = '''
        # PythonAnywhere-specific error handling
        except Exception as e:
            logging.error(f"PythonAnywhere upload error: {e}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            
            # Return proper JSON error response
            error_response = {
                'error': f'Upload failed: {str(e)}',
                'details': 'Please try again or contact support if the problem persists.'
            }
            
            # Ensure we return JSON, not HTML
            response = jsonify(error_response)
            response.headers['Content-Type'] = 'application/json'
            return response, 500
'''
    
    # Add the error handling before the final return
    content = re.sub(
        upload_route_pattern,
        r'\1' + improved_error_handling + r'\2',
        content
    )
    
    with open(app_py_path, 'w') as f:
        f.write(content)
    
    print("✅ Improved server error handling")

def add_pythonanywhere_upload_optimizations():
    """Add PythonAnywhere-specific upload optimizations."""
    
    print("🔧 Adding PythonAnywhere upload optimizations...")
    
    app_py_path = "app.py"
    
    with open(app_py_path, 'r') as f:
        content = f.read()
    
    # Add PythonAnywhere-specific configurations
    config_pattern = r'(app\.config\[.*?\] = .*?\n)'
    
    pythonanywhere_config = '''
# PythonAnywhere-specific upload configurations
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit for PythonAnywhere
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['PYTHONANYWHERE_MODE'] = True

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

'''
    
    # Insert the configuration
    content = re.sub(
        config_pattern,
        r'\1' + pythonanywhere_config,
        content,
        count=1
    )
    
    with open(app_py_path, 'w') as f:
        f.write(content)
    
    print("✅ Added PythonAnywhere upload optimizations")

def create_test_script():
    """Create a test script to verify the fix."""
    
    print("🔧 Creating test script...")
    
    test_script = '''#!/usr/bin/env python3
"""
Test script for PythonAnywhere upload fix
"""

import requests
import os

def test_upload():
    """Test the upload functionality."""
    
    print("🧪 Testing PythonAnywhere Upload Fix")
    print("=" * 40)
    
    # Create a test file
    test_file_path = "test_upload.xlsx"
    with open(test_file_path, 'w') as f:
        f.write("test content")
    
    try:
        # Test upload
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post('http://localhost:5000/upload', files=files)
        
        print(f"Upload response status: {response.status_code}")
        print(f"Upload response content: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Upload test successful!")
        else:
            print("❌ Upload test failed!")
            
    except Exception as e:
        print(f"❌ Upload test error: {e}")
    
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    test_upload()
'''
    
    with open("test_pythonanywhere_upload.py", 'w') as f:
        f.write(test_script)
    
    print("✅ Created test script")

def main():
    """Run the complete fix."""
    
    print_fix_plan()
    
    try:
        fix_javascript_errors()
        add_tagmanager_error_methods()
        improve_server_error_handling()
        add_pythonanywhere_upload_optimizations()
        create_test_script()
        
        print()
        print("🎉 PythonAnywhere Upload Fix Complete!")
        print("=" * 40)
        print()
        print("📋 NEXT STEPS:")
        print("1. Commit and push the changes")
        print("2. Test the upload functionality")
        print("3. Check PythonAnywhere logs for any remaining issues")
        print()
        print("🔧 FIXES APPLIED:")
        print("• Fixed TagManager.showError JavaScript errors")
        print("• Added proper error handling methods to TagManager")
        print("• Improved server-side error handling for PythonAnywhere")
        print("• Added PythonAnywhere-specific upload optimizations")
        print("• Created test script for verification")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main() 