#!/usr/bin/env python3

from flask import Flask, jsonify
import json

app = Flask(__name__)

# Simple test data
test_data = [
    {"name": "test1", "value": 1},
    {"name": "test2", "value": "string"},
    {"name": "test3", "value": 3.5}
]

@app.route('/test')
def test():
    try:
        return jsonify({
            'success': True,
            'data': test_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting simple Flask test...")
    app.run(debug=True, host='0.0.0.0', port=5005)
