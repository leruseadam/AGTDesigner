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
processing_status = {}

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

def process_file_chunked(filepath, filename):
    """Process Excel file in chunks for better performance"""
    try:
        print(f"Starting chunked processing of {filename}")
        
        # Verify file exists before processing
        if not os.path.exists(filepath):
            print(f"ERROR: File {filepath} does not exist!")
            processing_status[filename] = {
                'status': 'error',
                'progress': 0,
                'error': f'File {filename} not found in uploads directory'
            }
            return
        
        # Read Excel file in chunks
        chunk_size = 1000  # Process 1000 rows at a time
        all_data = []
        
        # First, get total rows for progress tracking
        df_total = pd.read_excel(filepath)
        total_rows = len(df_total)
        print(f"Total rows to process: {total_rows}")
        
        # Process in chunks
        for chunk_start in range(0, total_rows, chunk_size):
            chunk_end = min(chunk_start + chunk_size, total_rows)
            
            # Read chunk
            df_chunk = pd.read_excel(filepath, skiprows=chunk_start, nrows=chunk_size)
            
            # Convert to list of dictionaries
            chunk_data = df_chunk.to_dict('records')
            
            # Clean NaN values
            chunk_data = clean_nan_values(chunk_data)
            
            # Add to all_data
            all_data.extend(chunk_data)
            
            # Update progress
            progress = int((chunk_end / total_rows) * 100)
            processing_status[filename] = {
                'status': 'processing', 
                'progress': progress,
                'processed_rows': chunk_end,
                'total_rows': total_rows
            }
            
            print(f"Processed {chunk_end}/{total_rows} rows ({progress}%)")
            
            # Small delay to prevent overwhelming the system
            time.sleep(0.1)
        
        # Store final data
        processed_data[filename] = {
            'data': all_data,
            'status': 'completed',
            'total_rows': len(all_data),
            'filepath': filepath  # Store filepath for reference
        }
        
        processing_status[filename] = {
            'status': 'completed',
            'progress': 100,
            'processed_rows': len(all_data),
            'total_rows': len(all_data)
        }
        
        print(f"Completed processing {filename}: {len(all_data)} rows")
        print(f"File still exists at: {filepath}")
        
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        processing_status[filename] = {
            'status': 'error',
            'progress': 0,
            'error': str(e)
        }

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
            
            # Start background processing
            thread = threading.Thread(target=process_file_chunked, args=(filepath, filename))
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
    return jsonify({
        'success': True,
        'message': 'Cache cleared'
    })

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True, host='0.0.0.0', port=5001)
