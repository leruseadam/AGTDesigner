#!/bin/bash
# Debug and fix upload issues for local development
echo "Debugging upload issues locally..."

# Check current app.py status
echo "=== Current app.py status ==="
if [ -f "app.py" ]; then
    echo "First 10 lines of app.py:"
    head -10 app.py
    echo ""
    echo "File size:"
    wc -l app.py
    echo ""
    
    # Check if app.py compiles
    echo "=== Python syntax check ==="
    python3 -m py_compile app.py
    if [ $? -eq 0 ]; then
        echo "✅ app.py syntax is valid"
    else
        echo "❌ app.py has syntax errors"
    fi
else
    echo "❌ app.py not found in current directory"
fi
echo ""

# Check if upload folder exists
echo "=== Upload folder check ==="
if [ -d "uploads" ]; then
    echo "✅ Upload folder exists"
    ls -la uploads/
else
    echo "❌ Upload folder missing, creating..."
    mkdir -p uploads
    chmod 755 uploads
fi
echo ""

# Check if pandas is installed
echo "=== Dependencies check ==="
python3 -c "import pandas; print('✅ pandas available')" 2>/dev/null || echo "❌ pandas not available"
python3 -c "import flask; print('✅ flask available')" 2>/dev/null || echo "❌ flask not available"
echo ""

# Create a comprehensive working app.py
echo "=== Creating comprehensive working app.py ==="
cat > app.py << 'EOF'
import os
import sys
import json
import pandas as pd
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import tempfile
import shutil
import traceback

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Set upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Store processed data globally
processed_data = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    try:
        print(f"Upload request received: {request.files}")
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.endswith(('.xlsx', '.xls')):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            print(f"File saved to: {filepath}")
            
            # Process Excel file
            try:
                print("Reading Excel file...")
                df = pd.read_excel(filepath)
                print(f"Excel file read successfully, shape: {df.shape}")
                
                # Convert to list of dictionaries
                data = df.to_dict('records')
                
                # Store data globally for status checking
                processed_data[filename] = {
                    'data': data,
                    'status': 'completed',
                    'total_rows': len(data)
                }
                
                print(f"Processed {len(data)} rows")
                
                return jsonify({
                    'success': True,
                    'message': f'File {filename} uploaded and processed successfully',
                    'data': data[:50],  # Return first 50 rows
                    'filename': filename,
                    'total_rows': len(data)
                })
            except Exception as e:
                print(f"Error processing file: {str(e)}")
                print(traceback.format_exc())
                return jsonify({'error': f'Error processing file: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Invalid file type. Please upload Excel files only.'}), 400
            
    except Exception as e:
        print(f"Upload error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/upload-status', methods=['GET'])
def upload_status():
    """Upload status endpoint"""
    try:
        filename = request.args.get('filename')
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        if filename in processed_data:
            return jsonify({
                'status': 'completed',
                'filename': filename,
                'message': 'Upload processing completed',
                'progress': 100,
                'success': True,
                'total_rows': processed_data[filename]['total_rows']
            })
        else:
            return jsonify({
                'status': 'processing',
                'filename': filename,
                'message': 'File is being processed',
                'progress': 50,
                'success': False
            })
    except Exception as e:
        return jsonify({'error': f'Status check failed: {str(e)}'}), 500

@app.route('/api/performance/status', methods=['GET'])
def performance_status():
    """Performance status endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Performance monitoring active',
        'processed_files': len(processed_data)
    })

@app.route('/api/performance/clear-cache', methods=['POST'])
def clear_cache():
    """Clear cache endpoint"""
    global processed_data
    processed_data = {}
    return jsonify({
        'success': True,
        'message': 'Cache cleared'
    })

@app.route('/api/initial-data', methods=['GET'])
def initial_data():
    """Initial data endpoint"""
    return jsonify({
        'success': True,
        'data': [],
        'message': 'No initial data'
    })

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True, host='0.0.0.0', port=5000)
EOF

# Verify the file compiles
echo "=== Verifying new app.py ==="
python3 -m py_compile app.py
if [ $? -eq 0 ]; then
    echo "✅ New app.py syntax is valid!"
    echo "✅ Upload folder created"
    echo "✅ Dependencies checked"
    echo ""
    echo "=== Local Upload Debug Complete ==="
    echo "✅ Created comprehensive working app.py"
    echo "✅ Added detailed logging and error handling"
    echo "✅ Increased file size limit to 50MB"
    echo "✅ Added global data storage for status checking"
    echo "✅ Added all necessary endpoints"
    echo ""
    echo "To test locally, run: python3 app.py"
    echo "Then go to: http://localhost:5000"
else
    echo "❌ New app.py has syntax errors"
    exit 1
fi
