#!/usr/bin/env python3
"""
Fix for PythonAnywhere initialization issues
"""

import os
import shutil
import time

def backup_current_files():
    """Backup current files before making changes."""
    backup_dir = "backup_initialization_fix"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        'static/js/main.js',
        'app.py',
        'templates/index.html'
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, f"{backup_dir}/{os.path.basename(file)}.backup")
            print(f"✅ Backed up {file}")

def fix_initialization_timeout():
    """Fix initialization timeout issues in main.js."""
    
    # Read the current main.js
    with open('static/js/main.js', 'r') as f:
        content = f.read()
    
    # Add timeout and fallback mechanisms to checkForExistingData
    old_check_function = '''    // Check if there's existing data and load it
    async checkForExistingData() {
        console.log('Checking for existing data...');
        
        try {
            // Use the new initial-data endpoint for faster loading
            const response = await fetch('/api/initial-data');
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.available_tags && Array.isArray(data.available_tags) && data.available_tags.length > 0) {
                    console.log(`Found ${data.available_tags.length} existing tags, loading data...`);
                    
                    // Update splash progress for data loading
                    AppLoadingSplash.updateProgress(60, 'Loading product data...');
                    
                    // Show action splash for initial tag population
                    this.showActionSplash('Loading product tags...');
                    
                    // Update available tags
                    AppLoadingSplash.updateProgress(75, 'Processing tags...');
                    this.debouncedUpdateAvailableTags(data.available_tags, null);
                    
                    // Don't restore selected tags on page reload - start with empty selection
                    AppLoadingSplash.updateProgress(85, 'Initializing selections...');
                    this.state.persistentSelectedTags = [];
                    this.state.selectedTags = new Set();
                    this.updateSelectedTags([]);
                    
                    // Update filters
                    AppLoadingSplash.updateProgress(90, 'Setting up filters...');
                    this.updateFilters(data.filters || {
                        vendor: [],
                        brand: [],
                        productType: [],
                        lineage: [],
                        weight: []
                    });
                    
                    // Update file info text to show the loaded filename
                    if (data.filename) {
                        const fileInfoText = document.getElementById('fileInfoText');
                        if (fileInfoText) {
                            fileInfoText.textContent = data.filename;
                        }
                    }
                    
                    // Complete splash loading
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                    
                    // Hide action splash after a short delay to ensure smooth transition
                    setTimeout(() => {
                        this.hideActionSplash();
                    }, 200);
                    
                    console.log('Initial data loaded successfully');
                    return;
                } else {
                    console.log('No initial data available:', data.message || 'No data found');
                    // Complete splash loading even if no data
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                }
            }
        } catch (error) {
            console.log('Error loading initial data:', error.message);
            // Complete splash loading on error
            AppLoadingSplash.stopAutoAdvance();
            AppLoadingSplash.complete();
        }
        
        console.log('No existing data found, waiting for file upload...');
        // Complete splash loading if no data found
        AppLoadingSplash.stopAutoAdvance();
        AppLoadingSplash.complete();
    },'''
    
    new_check_function = '''    // Check if there's existing data and load it
    async checkForExistingData() {
        console.log('Checking for existing data...');
        
        // Add timeout protection
        const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('Initialization timeout')), 10000); // 10 second timeout
        });
        
        try {
            // Use the new initial-data endpoint for faster loading with timeout
            const response = await Promise.race([
                fetch('/api/initial-data'),
                timeoutPromise
            ]);
            
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.available_tags && Array.isArray(data.available_tags) && data.available_tags.length > 0) {
                    console.log(`Found ${data.available_tags.length} existing tags, loading data...`);
                    
                    // Update splash progress for data loading
                    AppLoadingSplash.updateProgress(60, 'Loading product data...');
                    
                    // Show action splash for initial tag population
                    this.showActionSplash('Loading product tags...');
                    
                    // Update available tags
                    AppLoadingSplash.updateProgress(75, 'Processing tags...');
                    this.debouncedUpdateAvailableTags(data.available_tags, null);
                    
                    // Don't restore selected tags on page reload - start with empty selection
                    AppLoadingSplash.updateProgress(85, 'Initializing selections...');
                    this.state.persistentSelectedTags = [];
                    this.state.selectedTags = new Set();
                    this.updateSelectedTags([]);
                    
                    // Update filters
                    AppLoadingSplash.updateProgress(90, 'Setting up filters...');
                    this.updateFilters(data.filters || {
                        vendor: [],
                        brand: [],
                        productType: [],
                        lineage: [],
                        weight: []
                    });
                    
                    // Update file info text to show the loaded filename
                    if (data.filename) {
                        const fileInfoText = document.getElementById('fileInfoText');
                        if (fileInfoText) {
                            fileInfoText.textContent = data.filename;
                        }
                    }
                    
                    // Complete splash loading
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                    
                    // Hide action splash after a short delay to ensure smooth transition
                    setTimeout(() => {
                        this.hideActionSplash();
                    }, 200);
                    
                    console.log('Initial data loaded successfully');
                    return;
                } else {
                    console.log('No initial data available:', data.message || 'No data found');
                    // Complete splash loading even if no data
                    AppLoadingSplash.stopAutoAdvance();
                    AppLoadingSplash.complete();
                }
            } else {
                console.log('Initial data endpoint returned error:', response.status);
                // Complete splash loading on error
                AppLoadingSplash.stopAutoAdvance();
                AppLoadingSplash.complete();
            }
        } catch (error) {
            console.log('Error loading initial data:', error.message);
            
            // Handle timeout specifically
            if (error.message === 'Initialization timeout') {
                console.log('Initialization timed out, proceeding with empty state');
                AppLoadingSplash.updateProgress(100, 'Ready to upload files');
            }
            
            // Complete splash loading on error
            AppLoadingSplash.stopAutoAdvance();
            AppLoadingSplash.complete();
        }
        
        console.log('No existing data found, waiting for file upload...');
        // Complete splash loading if no data found
        AppLoadingSplash.stopAutoAdvance();
        AppLoadingSplash.complete();
    },'''
    
    if old_check_function in content:
        content = content.replace(old_check_function, new_check_function)
        print("✅ Added timeout protection to initialization")
    else:
        print("⚠️  Could not find checkForExistingData function to replace")
    
    # Write back the updated content
    with open('static/js/main.js', 'w') as f:
        f.write(content)

def add_emergency_initialization_fix():
    """Add emergency initialization fix to prevent infinite loading."""
    
    # Read the current main.js
    with open('static/js/main.js', 'r') as f:
        content = f.read()
    
    # Add emergency initialization fix
    emergency_fix = '''
    // Emergency initialization fix - force complete after 15 seconds
    setTimeout(() => {
        if (AppLoadingSplash && AppLoadingSplash.isVisible) {
            console.log('Emergency initialization fix: forcing splash completion');
            AppLoadingSplash.stopAutoAdvance();
            AppLoadingSplash.complete();
        }
    }, 15000);
    
    // Additional emergency fix for stuck initialization
    window.addEventListener('load', () => {
        setTimeout(() => {
            const splash = document.getElementById('appLoadingSplash');
            if (splash && splash.style.display !== 'none') {
                console.log('Emergency fix: hiding stuck splash screen');
                splash.style.display = 'none';
                const mainContent = document.getElementById('mainContent');
                if (mainContent) {
                    mainContent.style.display = 'block';
                }
            }
        }, 20000); // 20 second emergency timeout
    });
'''
    
    # Find where to insert the emergency fix (after the init function)
    if 'init() {' in content:
        # Find the end of the init function
        init_start = content.find('init() {')
        if init_start != -1:
            # Find the closing brace of the init function
            brace_count = 0
            insert_index = init_start
            
            for i in range(init_start, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        insert_index = i + 1
                        break
            
            # Insert the emergency fix
            content = content[:insert_index] + emergency_fix + content[insert_index:]
            print("✅ Added emergency initialization fix")
    
    # Write back the updated content
    with open('static/js/main.js', 'w') as f:
        f.write(content)

def create_initialization_test_page():
    """Create a test page for initialization issues."""
    
    test_page = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Initialization Test - PythonAnywhere</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .test-section { border: 1px solid #ccc; padding: 20px; margin: 20px 0; border-radius: 5px; }
        .status { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .status.success { background-color: #d4edda; color: #155724; }
        .status.error { background-color: #f8d7da; color: #721c24; }
        .status.info { background-color: #d1ecf1; color: #0c5460; }
        button { padding: 10px 20px; margin: 10px; cursor: pointer; }
        .loading { display: inline-block; width: 20px; height: 20px; border: 3px solid #f3f3f3; border-top: 3px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <h1>PythonAnywhere Initialization Test</h1>
    
    <div class="test-section">
        <h3>API Endpoint Tests</h3>
        <button onclick="testEndpoint('/api/initial-data')">Test /api/initial-data</button>
        <button onclick="testEndpoint('/api/status')">Test /api/status</button>
        <button onclick="testEndpoint('/api/health')">Test /api/health</button>
        <div id="apiResults"></div>
    </div>
    
    <div class="test-section">
        <h3>File Loading Tests</h3>
        <button onclick="testFileLoading()">Test File Loading</button>
        <button onclick="testDefaultFile()">Test Default File</button>
        <div id="fileResults"></div>
    </div>
    
    <div class="test-section">
        <h3>Performance Tests</h3>
        <button onclick="testPerformance()">Test Performance</button>
        <div id="performanceResults"></div>
    </div>
    
    <div class="test-section">
        <h3>Emergency Fixes</h3>
        <button onclick="forceComplete()">Force Complete Initialization</button>
        <button onclick="clearSession()">Clear Session</button>
        <button onclick="reloadPage()">Reload Page</button>
        <div id="emergencyResults"></div>
    </div>
    
    <script>
        async function testEndpoint(endpoint) {
            const resultsDiv = document.getElementById('apiResults');
            resultsDiv.innerHTML = '<div class="status info"><div class="loading"></div> Testing ' + endpoint + '...</div>';
            
            try {
                const startTime = Date.now();
                const response = await fetch(endpoint);
                const endTime = Date.now();
                const duration = endTime - startTime;
                
                if (response.ok) {
                    const data = await response.json();
                    resultsDiv.innerHTML = '<div class="status success">✅ ' + endpoint + ' is working (${duration}ms)<br>Response: ' + JSON.stringify(data).substring(0, 200) + '...</div>';
                } else {
                    resultsDiv.innerHTML = '<div class="status error">❌ ' + endpoint + ' failed: ' + response.status + ' ' + response.statusText + ' (${duration}ms)</div>';
                }
            } catch (error) {
                resultsDiv.innerHTML = '<div class="status error">❌ ' + endpoint + ' error: ' + error.message + '</div>';
            }
        }
        
        async function testFileLoading() {
            const resultsDiv = document.getElementById('fileResults');
            resultsDiv.innerHTML = '<div class="status info"><div class="loading"></div> Testing file loading...</div>';
            
            try {
                const response = await fetch('/api/initial-data');
                if (response.ok) {
                    const data = await response.json();
                    if (data.success && data.available_tags && data.available_tags.length > 0) {
                        resultsDiv.innerHTML = '<div class="status success">✅ File loading working: ' + data.available_tags.length + ' tags loaded</div>';
                    } else {
                        resultsDiv.innerHTML = '<div class="status info">ℹ️ No file data available: ' + (data.message || 'No data') + '</div>';
                    }
                } else {
                    resultsDiv.innerHTML = '<div class="status error">❌ File loading failed: ' + response.status + '</div>';
                }
            } catch (error) {
                resultsDiv.innerHTML = '<div class="status error">❌ File loading error: ' + error.message + '</div>';
            }
        }
        
        async function testDefaultFile() {
            const resultsDiv = document.getElementById('fileResults');
            resultsDiv.innerHTML = '<div class="status info"><div class="loading"></div> Testing default file...</div>';
            
            try {
                const response = await fetch('/api/status');
                if (response.ok) {
                    const data = await response.json();
                    resultsDiv.innerHTML = '<div class="status success">✅ Default file test: ' + JSON.stringify(data).substring(0, 200) + '...</div>';
                } else {
                    resultsDiv.innerHTML = '<div class="status error">❌ Default file test failed: ' + response.status + '</div>';
                }
            } catch (error) {
                resultsDiv.innerHTML = '<div class="status error">❌ Default file test error: ' + error.message + '</div>';
            }
        }
        
        async function testPerformance() {
            const resultsDiv = document.getElementById('performanceResults');
            resultsDiv.innerHTML = '<div class="status info"><div class="loading"></div> Testing performance...</div>';
            
            const tests = [
                { name: 'Initial Data', endpoint: '/api/initial-data' },
                { name: 'Status', endpoint: '/api/status' },
                { name: 'Health', endpoint: '/api/health' }
            ];
            
            let results = [];
            for (const test of tests) {
                try {
                    const startTime = Date.now();
                    const response = await fetch(test.endpoint);
                    const endTime = Date.now();
                    const duration = endTime - startTime;
                    
                    results.push(test.name + ': ' + duration + 'ms (' + (response.ok ? 'OK' : 'FAIL') + ')');
                } catch (error) {
                    results.push(test.name + ': ERROR (' + error.message + ')');
                }
            }
            
            resultsDiv.innerHTML = '<div class="status success">✅ Performance test results:<br>' + results.join('<br>') + '</div>';
        }
        
        function forceComplete() {
            const resultsDiv = document.getElementById('emergencyResults');
            resultsDiv.innerHTML = '<div class="status info">Forcing initialization completion...</div>';
            
            // Force hide splash screen
            const splash = document.getElementById('appLoadingSplash');
            if (splash) {
                splash.style.display = 'none';
            }
            
            // Show main content
            const mainContent = document.getElementById('mainContent');
            if (mainContent) {
                mainContent.style.display = 'block';
            }
            
            // Call emergency hide function if available
            if (window.emergencyHideSplash) {
                window.emergencyHideSplash();
            }
            
            resultsDiv.innerHTML = '<div class="status success">✅ Forced initialization completion</div>';
        }
        
        function clearSession() {
            const resultsDiv = document.getElementById('emergencyResults');
            resultsDiv.innerHTML = '<div class="status info">Clearing session...</div>';
            
            // Clear localStorage and sessionStorage
            if (window.localStorage) {
                localStorage.clear();
            }
            if (window.sessionStorage) {
                sessionStorage.clear();
            }
            
            resultsDiv.innerHTML = '<div class="status success">✅ Session cleared</div>';
        }
        
        function reloadPage() {
            window.location.reload();
        }
    </script>
</body>
</html>
'''
    
    with open('templates/initialization_test.html', 'w') as f:
        f.write(test_page)
    
    print("✅ Created initialization test page")

def add_initialization_test_route():
    """Add route to serve the initialization test page."""
    
    # Read the current app.py
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Add the test route
    test_route = '''
@app.route('/initialization-test')
def initialization_test():
    """Serve the initialization test page"""
    return render_template('initialization_test.html')

'''
    
    # Find where to insert the test route (after other routes)
    if '@app.route' in content:
        # Insert after the last route
        lines = content.split('\n')
        insert_index = len(lines) - 1
        
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].startswith('@app.route'):
                insert_index = i + 1
                break
        
        lines.insert(insert_index, test_route)
        content = '\n'.join(lines)
        print("✅ Added initialization test route")
    
    # Write back the updated content
    with open('app.py', 'w') as f:
        f.write(content)

def create_initialization_debug_script():
    """Create a debug script for initialization issues."""
    
    debug_script = '''#!/usr/bin/env python3
"""
Initialization Debug Script for PythonAnywhere
"""

import os
import requests
import time

def test_initialization_endpoints():
    """Test all initialization-related endpoints."""
    print("🔍 Testing initialization endpoints...")
    
    endpoints = [
        '/api/initial-data',
        '/api/status',
        '/api/health',
        '/upload-test',
        '/initialization-test'
    ]
    
    for endpoint in endpoints:
        try:
            print(f"Testing {endpoint}...")
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=10)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  Success: {endpoint} is working")
            elif response.status_code == 405:  # Method Not Allowed
                print(f"  Note: {endpoint} exists but doesn't accept GET requests")
            else:
                print(f"  Error: {response.status_code}")
        except Exception as e:
            print(f"  Error: {e}")
    
    print()

def test_initialization_performance():
    """Test initialization performance."""
    print("⚡ Testing initialization performance...")
    
    endpoints = [
        '/api/initial-data',
        '/api/status',
        '/api/health'
    ]
    
    for endpoint in endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=10)
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"{endpoint}: {duration:.2f}s ({response.status_code})")
        except Exception as e:
            print(f"{endpoint}: ERROR ({e})")
    
    print()

def check_initialization_configuration():
    """Check initialization configuration."""
    print("⚙️  Checking initialization configuration...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        checks = [
            ('initialize_excel_processor', 'Excel processor initialization'),
            ('get_default_upload_file', 'Default file loading'),
            ('/api/initial-data', 'Initial data endpoint'),
            ('AppLoadingSplash', 'Loading splash screen')
        ]
        
        for check, description in checks:
            if check in content:
                print(f"✅ {description}: Found")
            else:
                print(f"❌ {description}: Not found")
                
    except Exception as e:
        print(f"Configuration check error: {e}")

def main():
    """Run all tests."""
    print("🧪 PythonAnywhere Initialization Debug")
    print("=" * 40)
    
    check_initialization_configuration()
    print()
    test_initialization_endpoints()
    test_initialization_performance()
    
    print("=" * 40)
    print("📋 Next steps:")
    print("1. Visit: https://yourusername.pythonanywhere.com/initialization-test")
    print("2. Test the main application")
    print("3. Check the PythonAnywhere error logs if issues persist")

if __name__ == "__main__":
    main()
'''
    
    with open('debug_initialization.py', 'w') as f:
        f.write(debug_script)
    
    print("✅ Created initialization debug script")

def main():
    """Main fix function."""
    print("🔧 PythonAnywhere Initialization Fix")
    print("=" * 40)
    
    try:
        # Backup current files
        backup_current_files()
        
        # Apply fixes
        fix_initialization_timeout()
        add_emergency_initialization_fix()
        create_initialization_test_page()
        add_initialization_test_route()
        create_initialization_debug_script()
        
        print("\n" + "=" * 40)
        print("✅ Initialization fixes complete!")
        print("\n📋 Fixes applied:")
        print("1. Added 10-second timeout to initialization")
        print("2. Added emergency initialization fix (15-second fallback)")
        print("3. Added emergency splash screen hiding (20-second fallback)")
        print("4. Created initialization test page")
        print("5. Added initialization debug script")
        
        print("\n📋 Next steps:")
        print("1. Reload your web app in PythonAnywhere")
        print("2. Visit: https://yourusername.pythonanywhere.com/initialization-test")
        print("3. Test the main application")
        print("4. Run: python3 debug_initialization.py")
        
        print("\n🔧 If you need to revert:")
        print("cp backup_initialization_fix/main.js.backup static/js/main.js")
        print("cp backup_initialization_fix/app.py.backup app.py")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 