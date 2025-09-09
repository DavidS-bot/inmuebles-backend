#!/usr/bin/env python3

import requests
import json
import time

def test_frontend_api_connection():
    """Test if frontend can connect to API properly"""
    
    print("TESTING FRONTEND-API CONNECTION")
    print("=" * 50)
    
    # Test the latest deployment
    frontend_urls = [
        "https://inmuebles-web.vercel.app",
        "https://inmuebles-david.vercel.app",
        "https://inmuebles-ct13w6oju-davsanchez21277-9843s-projects.vercel.app"
    ]
    
    for url in frontend_urls:
        print(f"\n=== Testing {url} ===")
        
        try:
            # Test if frontend loads
            response = requests.get(f"{url}/api/health", timeout=10)
            print(f"Health check: {response.status_code}")
        except Exception as e:
            print(f"Frontend health check failed: {e}")
        
        try:
            # Test a public endpoint
            response = requests.get(url, timeout=10)
            print(f"Homepage status: {response.status_code}")
            if response.status_code == 200:
                if "Inmuebles" in response.text:
                    print("Frontend loaded correctly")
                else:
                    print("Frontend loaded but content unexpected")
        except Exception as e:
            print(f"Homepage test failed: {e}")
    
    # Test backend connectivity from different origins
    print(f"\n=== Testing Backend CORS ===")
    
    for frontend_url in frontend_urls:
        try:
            response = requests.get(
                "https://inmuebles-backend-api.onrender.com/health",
                headers={
                    "Origin": frontend_url,
                    "Referer": frontend_url
                },
                timeout=10
            )
            print(f"Backend accessible from {frontend_url}: {response.status_code}")
        except Exception as e:
            print(f"Backend test from {frontend_url} failed: {e}")

if __name__ == "__main__":
    test_frontend_api_connection()