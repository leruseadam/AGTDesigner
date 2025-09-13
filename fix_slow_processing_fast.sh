#!/bin/bash
# Fix slow processing with much faster approach
echo "Fixing slow processing with fast approach..."

# Create backup
cp /home/adamcordova/AGTDesigner/app.py /home/adamcordova/AGTDesigner/app.py.backup.$(date +%Y%m%d_%H%M%S)

# Create fast processing app.py
cat > /home/adamcordova/AGTDesigner/app.py << 'EOF'
import os
import sys
import json
import pandas as pd
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import tempfile
import shutil
import traceback
import threading
import time
import pickle

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Set upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Persistent storage files
PROCESSED_DATA_FILE = 'processed_data.pkl'
PROCESSING_STATUS_FILE = 'processing_status.pkl'

def load_persistent_data():
    """Load data from persistent storage"""
    global processed_data, processing_status
    processed_data = {}
    processing_status = {}
    
    try:
        if os.path.exists(PROCESSED_DATA_FILE):
            with open(PROCESSED_DATA_FILE, 'rb') as f:
                processed_data = pickle.load(f)
            print(f"Loaded {len(processed_data)} processed files from storage")
    except Exception as e:
        print(f"Error loading processed data: {e}")
        processed_data = {}
    
    try:
        if os.path.exists(PROCESSING_STATUS_FILE):
            with open(PROCESSING_STATUS_FILE, 'rb') as f:
                processing_status = pickle.load(f)
            print(f"Loaded {len(processing_status)} processing statuses from storage")
    except Exception as e:
        print(f"Error loading processing status: {e}")
        processing_status = {}

def save_processed_data():
    """Save processed data to persistent storage"""
    try:
        with open(PROCESSED_DATA_FILE, 'wb') as f:
            pickle.dump(processed_data, f)
    except Exception as e:
        print(f"Error saving processed data: {e}")

def save_processing_status():
    """Save processing status to persistent storage"""
    try:
        with open(PROCESSING_STATUS_FILE, 'wb') as f:
            pickle.dump(processing_status, f)
    except Exception as e:
        print(f"Error saving processing status: {e}")

# Load persistent data on startup
load_persistent_data()

def clean_nan_values(obj):
    """Clean NaN values for JSON serialization"""
    import numpy as np
    if isinstance(obj, dict):
        return {k: clean_nan_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan_values(item) for item in obj]
    elif isinstance(obj, float) and np.isnan(obj):
        return None  # Convert NaN to None for JSON
    else:
        return obj

def process_file_fast(filepath, filename):
    """Process Excel file quickly with single read"""
    try:
        print(f"Starting fast processing of {filename}")
        
        # Verify file exists before processing
        if not os.path.exists(filepath):
            print(f"ERROR: File {filepath} does not exist!")
            processing_status[filename] = {
                'status': 'error',
                'progress': 0,
                'error': f'File {filename} not found in uploads directory'
            }
            save_processing_status()
            return
        
        # Update status to processing
        processing_status[filename] = {
            'status': 'processing',
            'progress': 10,
            'processed_rows': 0,
            'total_rows': 0
        }
        save_processing_status()
        
        # Read entire Excel file at once (much faster)
        print(f"Reading Excel file: {filepath}")
        df = pd.read_excel(filepath)
        total_rows = len(df)
        print(f"Total rows to process: {total_rows}")
        
        # Update progress
        processing_status[filename] = {
            'status': 'processing',
            'progress': 50,
            'processed_rows': 0,
            'total_rows': total_rows
        }
        save_processing_status()
        
        # Convert to list of dictionaries
        print("Converting to dictionary format...")
        data = df.to_dict('records')
        
        # Update progress
        processing_status[filename] = {
            'status': 'processing',
            'progress': 80,
            'processed_rows': total_rows,
            'total_rows': total_rows
        }
        save_processing_status()
        
        # Clean NaN values
        print("Cleaning NaN values...")
        data = clean_nan_values(data)
        
        # Store final data
        processed_data[filename] = {
            'data': data,
            'status': 'completed',
            'total_rows': len(data),
            'filepath': filepath
        }
        
        processing_status[filename] = {
            'status': 'completed',
            'progress': 100,
            'processed_rows': len(data),
            'total_rows': len(data)
        }
        
        # Save final data to disk
        save_processed_data()
        save_processing_status()
        
        print(f"Completed processing {filename}: {len(data)} rows")
        print(f"File still exists at: {filepath}")
        
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        processing_status[filename] = {
            'status': 'error',
            'progress': 0,
            'error': str(e)
        }
        save_processing_status()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and start background processing"""
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
            
            # Save file
            file.save(filepath)
            print(f"File saved to: {filepath}")
            
            # Verify file was saved
            if not os.path.exists(filepath):
                return jsonify({'error': 'Failed to save file'}), 500
            
            # Get file size for verification
            file_size = os.path.getsize(filepath)
            print(f"File size: {file_size} bytes")
            
            # Initialize processing status BEFORE starting background thread
            processing_status[filename] = {
                'status': 'processing',
                'progress': 0,
                'processed_rows': 0,
                'total_rows': 0
            }
            
            # Save status to disk immediately
            save_processing_status()
            
            # Start background processing
            thread = threading.Thread(target=process_file_fast, args=(filepath, filename))
            thread.daemon = True
            thread.start()
            
            # Return immediate response
            return jsonify({
                'success': True,
                'message': f'File {filename} uploaded successfully. Processing in background...',
                'filename': filename,
                'status': 'processing',
                'file_size': file_size
            })
        else:
            return jsonify({'error': 'Invalid file type. Please upload Excel files only.'}), 400
            
    except Exception as e:
        print(f"Upload error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/upload-status', methods=['GET'])
def upload_status():
    """Upload status endpoint with progress tracking"""
    try:
        filename = request.args.get('filename')
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        print(f"Status check for filename: {filename}")
        print(f"Processing status keys: {list(processing_status.keys())}")
        print(f"Processed data keys: {list(processed_data.keys())}")
        
        if filename in processing_status:
            status_info = processing_status[filename].copy()
            status_info['filename'] = filename
            print(f"Returning processing status: {status_info}")
            return jsonify(status_info)
        elif filename in processed_data:
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
                'status': 'not_found',
                'filename': filename,
                'message': 'File not found',
                'progress': 0,
                'success': False
            })
    except Exception as e:
        print(f"Status check error: {str(e)}")
        return jsonify({'error': f'Status check failed: {str(e)}'}), 500

@app.route('/api/available-tags', methods=['GET'])
def available_tags():
    """Get all available tags from processed data"""
    try:
        all_tags = []
        for filename, data in processed_data.items():
            if data['status'] == 'completed':
                all_tags.extend(data['data'])
        
        return jsonify({
            'success': True,
            'data': all_tags,
            'total_count': len(all_tags),
            'message': f'Retrieved {len(all_tags)} tags'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get tags: {str(e)}'}), 500

@app.route('/api/initial-data', methods=['GET'])
def initial_data():
    """Initial data endpoint - return all processed data"""
    try:
        all_data = []
        for filename, data in processed_data.items():
            if data['status'] == 'completed':
                all_data.extend(data['data'])
        
        return jsonify({
            'success': True,
            'data': all_data,
            'total_count': len(all_data),
            'message': f'Retrieved {len(all_data)} items'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get initial data: {str(e)}'}), 500

@app.route('/api/file-info', methods=['GET'])
def file_info():
    """Get information about uploaded files"""
    try:
        files_info = []
        for filename, data in processed_data.items():
            file_info = {
                'filename': filename,
                'status': data['status'],
                'total_rows': data['total_rows'],
                'filepath': data.get('filepath', 'Unknown')
            }
            files_info.append(file_info)
        
        return jsonify({
            'success': True,
            'files': files_info,
            'total_files': len(files_info)
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get file info: {str(e)}'}), 500

@app.route('/api/performance/status', methods=['GET'])
def performance_status():
    """Performance status endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Performance monitoring active',
        'processed_files': len(processed_data),
        'processing_files': len([f for f in processing_status.values() if f['status'] == 'processing'])
    })

@app.route('/api/performance/clear-cache', methods=['POST'])
def clear_cache():
    """Clear cache endpoint"""
    global processed_data, processing_status
    processed_data = {}
    processing_status = {}
    
    # Also clear persistent storage
    try:
        if os.path.exists(PROCESSED_DATA_FILE):
            os.remove(PROCESSED_DATA_FILE)
        if os.path.exists(PROCESSING_STATUS_FILE):
            os.remove(PROCESSING_STATUS_FILE)
    except Exception as e:
        print(f"Error clearing persistent storage: {e}")
    
    return jsonify({
        'success': True,
        'message': 'Cache cleared'
    })

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True, host='0.0.0.0', port=5000)
EOF

# Verify the file compiles
echo "Verifying Python syntax..."
python3 -m py_compile /home/adamcordova/AGTDesigner/app.py
if [ $? -eq 0 ]; then
    echo "✅ Python syntax is valid!"
    echo "✅ Fast processing implemented!"
    echo "✅ Single Excel read instead of multiple chunked reads!"
    echo "✅ Much faster processing!"
    echo "Reloading web app..."
    touch /var/www/www_agtpricetags_com_wsgi.py
    echo "Web app reloaded! Processing should be much faster now."
else
    echo "❌ Syntax errors found. Restoring backup..."
    cp /home/adamcordova/AGTDesigner/app.py.backup.* /home/adamcordova/AGTDesigner/app.py
    exit 1
fi

echo "Fast processing fix applied successfully!"
