#!/usr/bin/env python3
"""Debug the registered routes to understand the conflict"""

import requests

def debug_routes():
    """Debug the available routes"""
    base_url = "http://localhost:8000"
    
    print("=== Testing Route Registration ===")
    
    # Check if we can access the OpenAPI spec to see registered routes
    try:
        response = requests.get(f"{base_url}/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            print(f"Found {len(paths)} registered paths:")
            
            # Look for our financial-movements paths
            financial_paths = [path for path in paths.keys() if "financial-movements" in path]
            print(f"\nFinancial movements paths ({len(financial_paths)}):")
            for path in sorted(financial_paths):
                methods = list(paths[path].keys())
                print(f"  {path} - Methods: {methods}")
                
                # Check if our specific endpoint is there
                if "delete-by-date-range" in path:
                    print(f"    *** FOUND OUR ENDPOINT: {path} ***")
                    print(f"    Methods: {methods}")
                    
        else:
            print(f"Failed to get OpenAPI spec: {response.status_code}")
            
    except Exception as e:
        print(f"Error getting OpenAPI spec: {e}")
    
    # Test accessing our endpoint directly to see what error we get
    print(f"\n=== Testing Direct Access ===")
    try:
        test_url = f"{base_url}/financial-movements/delete-by-date-range"
        response = requests.delete(test_url)
        print(f"Direct DELETE to {test_url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error in direct test: {e}")

if __name__ == "__main__":
    debug_routes()