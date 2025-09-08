#!/usr/bin/env python3
import requests
import json

# Test without authentication first - just to trigger the endpoint
url = "http://localhost:8001/bankinter/update-movements"

print("Calling endpoint without auth (should fail with 401 but logs should show attempt)...")
try:
    response = requests.post(url, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print("Exception:", e)

print("\nCheck the backend logs for the '🏦 Iniciando actualización Bankinter...' message")