#!/usr/bin/env python3

import os
import sys
import json
import pandas as pd
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import threading
import time
import numpy as np

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
    if isinstance(obj, dict):
        return {k: clean_nan_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan_values(item) for item in obj]
    elif isinstance(obj, float) and np.isnan(obj):
        return None  # Convert NaN to None for JSON
    else:
        return obj

def process_file_chunked(filepath, filename):
    """Process Excel file in chunks for better performance - EXACT COPY from main app"""
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
        print(f"Stored in processed_data: {filename in processed_data}")
        print(f"Processed data keys: {list(processed_data.keys())}")
        print(f"Data sample: {all_data[0] if all_data else 'No data'}")
        
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        import traceback
        traceback.print_exc()
        processing_status[filename] = {
            'status': 'error',
            'progress': 0,
            'error': str(e)
        }

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and start background processing - EXACT COPY from main app"""
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
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/initial-data', methods=['GET'])
def initial_data():
    """Initial data endpoint - EXACT COPY from main app"""
    try:
        print(f"Initial data called. Processed data keys: {list(processed_data.keys())}")
        
        all_data = []
        for filename, data in processed_data.items():
            if data['status'] == 'completed':
                print(f"Processing data from {filename}: {len(data['data'])} items")
                # Clean the data before adding
                cleaned_data = clean_nan_values(data['data'])
                all_data.extend(cleaned_data)
        
        print(f"Total items to return: {len(all_data)}")
        
        # Test JSON serialization step by step
        try:
            print("Testing JSON serialization...")
            json.dumps(all_data[:5])  # Test first 5
            print("First 5 items JSON serialization successful")
            
            json.dumps(all_data)  # Test all data
            print("Full data JSON serialization successful")
            
        except Exception as json_error:
            print(f"JSON serialization error: {json_error}")
            # Find the problematic item
            for i, item in enumerate(all_data):
                try:
                    json.dumps(item)
                except Exception as item_error:
                    print(f"Problematic item {i}: {item}")
                    print(f"Item error: {item_error}")
                    break
        
        return jsonify({
            'success': True,
            'data': all_data,
            'total_count': len(all_data),
            'message': f'Retrieved {len(all_data)} items'
        })
    except Exception as e:
        print(f"Error in initial_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to get initial data: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting test app with exact main app flow...")
    app.run(debug=True, host='0.0.0.0', port=5004)
