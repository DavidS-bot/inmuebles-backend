#!/usr/bin/env python3
"""Assign uploaded photos to properties"""

import requests

BACKEND_URL = "https://inmuebles-backend-api.onrender.com"
USER_EMAIL = "davsanchez21277@gmail.com"
USER_PASSWORD = "123456"

def main():
    # Login
    login_data = {"username": USER_EMAIL, "password": USER_PASSWORD}
    login_resp = requests.post(
        f"{BACKEND_URL}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10
    )
    
    if login_resp.status_code != 200:
        print("Login failed")
        return
    
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Get properties
    props_resp = requests.get(f"{BACKEND_URL}/properties", headers=headers)
    if props_resp.status_code != 200:
        print("Failed to get properties")
        return
    
    properties = props_resp.json()
    print(f"Found {len(properties)} properties")
    
    # Assign photo URLs to properties
    # We have 11 photos uploaded, assign them to the 11 properties
    photo_assignments = [
        (1, f"{BACKEND_URL}/files/photo/1"),   # Property 1
        (2, f"{BACKEND_URL}/files/photo/2"),   # Property 2
        (3, f"{BACKEND_URL}/files/photo/3"),   # Property 3
        (4, f"{BACKEND_URL}/files/photo/4"),   # Property 4
        (5, f"{BACKEND_URL}/files/photo/5"),   # Property 5
        (6, f"{BACKEND_URL}/files/photo/6"),   # Property 6
        (7, f"{BACKEND_URL}/files/photo/7"),   # Property 7
        (8, f"{BACKEND_URL}/files/photo/8"),   # Property 8
        (9, f"{BACKEND_URL}/files/photo/9"),   # Property 9
        (10, f"{BACKEND_URL}/files/photo/10"), # Property 10
        (11, f"{BACKEND_URL}/files/photo/11"), # Property 11
    ]
    
    updated = 0
    for prop_id, photo_url in photo_assignments:
        try:
            # Find property by ID
            property_to_update = None
            for prop in properties:
                if prop.get('id') == prop_id:
                    property_to_update = prop
                    break
            
            if property_to_update:
                # Update property with photo URL
                update_data = {
                    "address": property_to_update.get('address'),
                    "type": property_to_update.get('type'),
                    "total_investment": property_to_update.get('total_investment'),
                    "current_value": property_to_update.get('current_value'),
                    "rental_income": property_to_update.get('rental_income'),
                    "expenses": property_to_update.get('expenses'),
                    "photo": photo_url  # FIXED: Use 'photo' field instead of 'photo_url'
                }
                
                update_resp = requests.put(
                    f"{BACKEND_URL}/properties/{prop_id}",
                    json=update_data,
                    headers=headers,
                    timeout=10
                )
                
                if update_resp.status_code in [200, 201]:
                    updated += 1
                    print(f"Property {prop_id}: Photo assigned")
                else:
                    print(f"Property {prop_id}: Failed - {update_resp.status_code}")
            else:
                print(f"Property {prop_id}: Not found")
                
        except Exception as e:
            print(f"Property {prop_id}: Error - {e}")
    
    print(f"\nUpdated {updated} properties with photos")
    
    # Verify photos are accessible
    print("\nTesting photo URLs...")
    for i in range(1, 4):
        test_url = f"{BACKEND_URL}/files/photo/{i}"
        try:
            test_resp = requests.get(test_url, timeout=5)
            print(f"Photo {i}: {test_resp.status_code} - {'OK' if test_resp.status_code == 200 else 'FAILED'}")
        except:
            print(f"Photo {i}: Connection error")
    
    print("\nDone! Properties now have photo URLs assigned.")
    print("The photos should now be visible in the web application!")

if __name__ == "__main__":
    main()