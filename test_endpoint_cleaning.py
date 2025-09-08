#!/usr/bin/env python3
import requests
import json

# Test the endpoint cleaning
url = "http://localhost:8001/bankinter/update-movements"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkYXZzYW5jaGV6MjEyNzdAZ21haWwuY29tIiwiZXhwIjoxNzI1OTA3MjAwfQ.L8x9FrE4jyRaKP-_3tD7c1v6_0mWONkF0dP7YjPZg9Q",
    "Content-Type": "application/json"
}

print("Calling endpoint...")
try:
    response = requests.post(url, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("Response:", json.dumps(result, indent=2))
    else:
        print("Error:", response.text)
except Exception as e:
    print("Exception:", e)