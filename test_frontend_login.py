import requests
import json

# Test the exact same request that the frontend would make
def test_login():
    url = "http://localhost:8000/auth/login"
    
    # Test with form data (like frontend does)
    form_data = {
        'username': 'davsanchez21277@gmail.com',
        'password': '123456'
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(url, data=form_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"Token received: {token[:20]}...")
            
            # Test if token works for properties endpoint
            auth_headers = {'Authorization': f'Bearer {token}'}
            props_response = requests.get('http://localhost:8000/properties', headers=auth_headers)
            print(f"Properties endpoint status: {props_response.status_code}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_login()
    print(f"Login test {'PASSED' if success else 'FAILED'}")