#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import threading
import time
import json

app = Flask(__name__)

# Global variables
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

def process_file_simple(filepath, filename):
    """Simple file processing"""
    try:
        print(f"Processing {filename}...")
        
        # Read Excel file
        df = pd.read_excel(filepath)
        print(f"Loaded {len(df)} rows")
        
        # Convert to dict
        data = df.to_dict('records')
        print(f"Converted to {len(data)} records")
        
        # Clean data
        cleaned_data = clean_nan_values(data)
        print(f"Cleaned data: {len(cleaned_data)} records")
        
        # Store in global variable
        processed_data[filename] = {
            'data': cleaned_data,
            'status': 'completed',
            'total_rows': len(cleaned_data)
        }
        
        processing_status[filename] = {
            'status': 'completed',
            'progress': 100,
            'processed_rows': len(cleaned_data),
            'total_rows': len(cleaned_data)
        }
        
        print(f"Stored data for {filename}")
        print(f"Processed data keys: {list(processed_data.keys())}")
        
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        import traceback
        traceback.print_exc()

@app.route('/upload', methods=['POST'])
def upload_file():
    """Simple upload endpoint"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.endswith(('.xlsx', '.xls')):
            filename = file.filename
            filepath = f"uploads/{filename}"
            
            # Create uploads directory
            os.makedirs('uploads', exist_ok=True)
            
            # Save file
            file.save(filepath)
            print(f"File saved to: {filepath}")
            
            # Start background processing
            thread = threading.Thread(target=process_file_simple, args=(filepath, filename))
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'success': True,
                'message': f'File {filename} uploaded successfully. Processing in background...',
                'filename': filename,
                'status': 'processing'
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/initial-data', methods=['GET'])
def initial_data():
    """Initial data endpoint"""
    try:
        print(f"Initial data called. Processed data keys: {list(processed_data.keys())}")
        
        all_data = []
        for filename, data in processed_data.items():
            if data['status'] == 'completed':
                print(f"Processing data from {filename}: {len(data['data'])} items")
                all_data.extend(data['data'])
        
        print(f"Total items to return: {len(all_data)}")
        
        # Test JSON serialization
        try:
            json.dumps(all_data[:5])  # Test first 5
            print("JSON serialization test passed for first 5")
        except Exception as e:
            print(f"JSON serialization test failed: {e}")
            return jsonify({'error': f'JSON serialization failed: {str(e)}'}), 500
        
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
    print("Starting minimal test app...")
    app.run(debug=True, host='0.0.0.0', port=5003)
