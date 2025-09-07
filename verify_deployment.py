#!/usr/bin/env python3
"""
Verify Database Deployment
Checks if the database was deployed successfully
"""

import requests
import sys

def verify_deployment(web_url):
    """Verify that the database deployment was successful"""
    print(f"🔍 Verifying deployment at {web_url}...")
    print()
    
    try:
        # Test basic connectivity
        print("1. Testing basic connectivity...")
        response = requests.get(f"{web_url}/api/status", timeout=10)
        if response.status_code == 200:
            print("   ✅ Web app is responding")
        else:
            print(f"   ❌ Web app returned status {response.status_code}")
            return False
        
        # Test database stats
        print("2. Checking database stats...")
        response = requests.get(f"{web_url}/api/database-stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            total_products = stats.get('stats', {}).get('total_products', 0)
            unique_brands = stats.get('stats', {}).get('unique_brands', 0)
            unique_vendors = stats.get('stats', {}).get('unique_vendors', 0)
            
            print(f"   📊 Total products: {total_products}")
            print(f"   🏷️  Unique brands: {unique_brands}")
            print(f"   🏪 Unique vendors: {unique_vendors}")
            
            if total_products >= 7000:  # Should have around 7,870
                print("   ✅ Database deployment successful!")
                return True
            else:
                print("   ⚠️  Database seems incomplete")
                return False
        else:
            print(f"   ❌ Database stats failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to web app")
        print("   💡 Make sure the web app is running and accessible")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out")
        print("   💡 Web app might be starting up, try again in a moment")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python verify_deployment.py <web_app_url>")
        print("Example: python verify_deployment.py https://your-username.pythonanywhere.com")
        sys.exit(1)
    
    web_url = sys.argv[1].rstrip('/')
    
    print("🚀 Database Deployment Verification")
    print("=" * 40)
    print()
    
    if verify_deployment(web_url):
        print()
        print("🎉 SUCCESS! Your database has been deployed successfully!")
        print("   - 7,870+ products are now available on the web")
        print("   - You can now upload Excel files and generate labels")
        print("   - The web app should be much faster now")
    else:
        print()
        print("❌ DEPLOYMENT VERIFICATION FAILED")
        print("   - Check that the web app is running")
        print("   - Verify the database file was uploaded correctly")
        print("   - Try the deployment steps again")

if __name__ == "__main__":
    main()
