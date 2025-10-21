#!/usr/bin/env python3
"""
TAG GENERATION PERFORMANCE TEST
Test the tag generation performance improvements
"""

import os
import time
import logging
import requests
import json
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_test_tags(count: int) -> List[Dict[str, str]]:
    """Create test tags for performance testing"""
    test_tags = []
    for i in range(1, count + 1):
        tag = {
            "Product Name*": f"Test Product {i}",
            "Product Brand": f"Brand {i % 5}",
            "Price": f"${i * 2.50:.2f}",
            "Lineage": f"Lineage {i % 3}",
            "Product Type*": f"Type {i % 4}",
            "Description": f"Test description for product {i}"
        }
        test_tags.append(tag)
    return test_tags

def test_generation_endpoint(endpoint: str, tags: List[Dict], template_type: str = "vertical", 
                           scale_factor: float = 1.0) -> Dict[str, Any]:
    """Test a specific generation endpoint"""
    try:
        logging.info(f"🧪 Testing {endpoint} with {len(tags)} tags...")
        
        start_time = time.time()
        
        # Prepare request data
        request_data = {
            "selected_tags": tags,
            "template_type": template_type,
            "scale_factor": scale_factor
        }
        
        # Make request (assuming local server)
        response = requests.post(
            f"http://localhost:5000{endpoint}",
            json=request_data,
            timeout=60  # 60 second timeout
        )
        
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            # Check if it's a DOCX file
            content_type = response.headers.get('Content-Type', '')
            if 'wordprocessingml' in content_type:
                file_size = len(response.content)
                logging.info(f"✅ {endpoint} SUCCESS:")
                logging.info(f"   Processing time: {processing_time:.3f}s")
                logging.info(f"   File size: {file_size:,} bytes")
                logging.info(f"   Tags processed: {len(tags)}")
                
                return {
                    "success": True,
                    "processing_time": processing_time,
                    "file_size": file_size,
                    "tags_processed": len(tags),
                    "method": endpoint.replace('/api/generate-', '').replace('/', '')
                }
            else:
                logging.error(f"❌ {endpoint} returned non-DOCX content: {content_type}")
                return {"success": False, "error": "Non-DOCX response"}
        else:
            error_text = response.text
            logging.error(f"❌ {endpoint} FAILED: HTTP {response.status_code}")
            logging.error(f"   Error: {error_text}")
            return {"success": False, "error": f"HTTP {response.status_code}: {error_text}"}
            
    except requests.exceptions.Timeout:
        logging.error(f"❌ {endpoint} TIMEOUT after 60 seconds")
        return {"success": False, "error": "Request timeout"}
    except requests.exceptions.ConnectionError:
        logging.error(f"❌ {endpoint} CONNECTION ERROR - is the server running?")
        return {"success": False, "error": "Connection error"}
    except Exception as e:
        logging.error(f"❌ {endpoint} ERROR: {e}")
        return {"success": False, "error": str(e)}

def test_performance_scenarios():
    """Test different performance scenarios"""
    logging.info("🧪 TAG GENERATION PERFORMANCE TEST")
    logging.info("=" * 60)
    
    # Test scenarios
    scenarios = [
        {"name": "Small Set", "count": 5, "description": "Instant processing"},
        {"name": "Medium Set", "count": 25, "description": "Fast processing"},
        {"name": "Large Set", "count": 100, "description": "Chunked processing"},
        {"name": "Very Large Set", "count": 300, "description": "Streaming processing"}
    ]
    
    # Endpoints to test
    endpoints = [
        "/api/generate-fast",
        "/api/generate-parallel", 
        "/api/generate"
    ]
    
    results = {}
    
    for scenario in scenarios:
        logging.info(f"\n📊 Testing {scenario['name']} ({scenario['count']} tags)")
        logging.info(f"   Expected: {scenario['description']}")
        
        # Create test tags
        test_tags = create_test_tags(scenario['count'])
        
        scenario_results = {}
        
        for endpoint in endpoints:
            result = test_generation_endpoint(endpoint, test_tags)
            scenario_results[endpoint] = result
            
            if result['success']:
                # Calculate performance metrics
                tags_per_second = result['tags_processed'] / result['processing_time']
                logging.info(f"   📈 {endpoint}: {tags_per_second:.1f} tags/sec")
        
        results[scenario['name']] = scenario_results
        
        # Small delay between scenarios
        time.sleep(1)
    
    return results

def print_performance_summary(results: Dict[str, Any]):
    """Print a comprehensive performance summary"""
    logging.info("\n📊 PERFORMANCE SUMMARY")
    logging.info("=" * 60)
    
    for scenario_name, scenario_results in results.items():
        logging.info(f"\n{scenario_name}:")
        
        for endpoint, result in scenario_results.items():
            method_name = endpoint.replace('/api/generate-', '').replace('/', '')
            if result['success']:
                tags_per_sec = result['tags_processed'] / result['processing_time']
                logging.info(f"  ✅ {method_name:12}: {result['processing_time']:6.3f}s, {tags_per_sec:6.1f} tags/sec")
            else:
                logging.info(f"  ❌ {method_name:12}: FAILED - {result.get('error', 'Unknown error')}")
    
    # Find fastest method for each scenario
    logging.info("\n🏆 FASTEST METHOD PER SCENARIO:")
    logging.info("-" * 40)
    
    for scenario_name, scenario_results in results.items():
        fastest_method = None
        fastest_time = float('inf')
        
        for endpoint, result in scenario_results.items():
            if result['success'] and result['processing_time'] < fastest_time:
                fastest_time = result['processing_time']
                fastest_method = endpoint.replace('/api/generate-', '').replace('/', '')
        
        if fastest_method:
            logging.info(f"  {scenario_name:15}: {fastest_method} ({fastest_time:.3f}s)")
        else:
            logging.info(f"  {scenario_name:15}: All methods failed")

def test_performance_monitor():
    """Test the performance monitoring system"""
    try:
        logging.info("\n📊 Testing performance monitor...")
        
        # Try to get performance report
        response = requests.get("http://localhost:5000/api/performance-report", timeout=10)
        
        if response.status_code == 200:
            report = response.json()
            logging.info("✅ Performance monitor is working")
            logging.info(f"   Report: {report}")
        else:
            logging.warning(f"⚠️ Performance monitor returned HTTP {response.status_code}")
            
    except Exception as e:
        logging.warning(f"⚠️ Performance monitor test failed: {e}")

def main():
    """Main test function"""
    logging.info("🚀 Starting Tag Generation Performance Test")
    logging.info("Make sure the Flask server is running on localhost:5000")
    
    # Test performance scenarios
    results = test_performance_scenarios()
    
    # Print summary
    print_performance_summary(results)
    
    # Test performance monitor
    test_performance_monitor()
    
    logging.info("\n✅ Performance test completed!")
    logging.info("Check the logs above for detailed results")

if __name__ == "__main__":
    main()
