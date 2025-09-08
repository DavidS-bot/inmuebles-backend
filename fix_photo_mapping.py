#!/usr/bin/env python3
"""Fix the photo-property mapping based on logical address matching"""

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
    
    # Create logical photo assignments based on the expected photo order:
    # Photo 1 = Aranguren 68, Photo 2 = Aranguren 66, Photo 3 = Aranguren 22, Photo 4 = Platón 30, etc.
    print("\nMapping properties to logical photo IDs:")
    
    photo_assignments = []
    
    for prop in properties:
        prop_id = prop.get('id')
        address = prop.get('address', '').lower()
        
        # Determine the correct photo ID based on address
        correct_photo_id = None
        
        if 'aranguren 68' in address:
            correct_photo_id = 1  # Photo 1 should be Aranguren 68
            print(f"Property {prop_id} (Aranguren 68) -> Photo 1")
        elif 'aranguren 66' in address:
            correct_photo_id = 2  # Photo 2 should be Aranguren 66
            print(f"Property {prop_id} (Aranguren 66) -> Photo 2")
        elif 'aranguren 22' in address:
            correct_photo_id = 3  # Photo 3 should be Aranguren 22
            print(f"Property {prop_id} (Aranguren 22) -> Photo 3")
        elif 'platon' in address:
            correct_photo_id = 4  # Photo 4 should be Platon 30
            print(f"Property {prop_id} (Platon 30) -> Photo 4")
        elif 'seneca' in address:
            correct_photo_id = 5  # Photo 5 should be Pozoalbero/Seneca
            print(f"Property {prop_id} (Pozoalbero/Seneca) -> Photo 5")
        elif 'lago de enol' in address and 'puerta f' in address:
            correct_photo_id = 6  # Photo 6 should be Lago de Enol 1F
            print(f"Property {prop_id} (Lago de Enol 1F) -> Photo 6")
        elif 'lago de enol' in address and 'puerta a' in address:
            correct_photo_id = 7  # Photo 7 should be Lago de Enol 2A
            print(f"Property {prop_id} (Lago de Enol 2A) -> Photo 7")
        elif 'lago de enol' in address and 'puerta b' in address:
            correct_photo_id = 8  # Photo 8 should be Lago de Enol 2B
            print(f"Property {prop_id} (Lago de Enol 2B) -> Photo 8")
        elif 'lago de bañolas' in address and 'puerta 4' in address:
            correct_photo_id = 9  # Photo 9 should be Lago de Bañolas 4
            print(f"Property {prop_id} (Lago de Bañolas 4) -> Photo 9")
        elif 'lago de bañolas' in address and 'puerta 9' in address:
            correct_photo_id = 10  # Photo 10 should be Lago de Bañolas 9
            print(f"Property {prop_id} (Lago de Bañolas 9) -> Photo 10")
        elif 'lago de enol' in address and 'puerta g' in address:
            correct_photo_id = 11  # Photo 11 should be Lago de Enol G
            print(f"Property {prop_id} (Lago de Enol G) -> Photo 11")
        
        if correct_photo_id:
            photo_assignments.append((prop_id, f"{BACKEND_URL}/files/photo/{correct_photo_id}"))
    
    print(f"\nUpdating {len(photo_assignments)} photo assignments...")
    
    # Update each property with the correct photo
    updated = 0
    for prop_id, photo_url in photo_assignments:
        try:
            # Find the property data
            property_to_update = None
            for prop in properties:
                if prop.get('id') == prop_id:
                    property_to_update = prop
                    break
            
            if property_to_update:
                # Update property with correct photo URL
                update_data = {
                    "address": property_to_update.get('address'),
                    "type": property_to_update.get('type'),
                    "total_investment": property_to_update.get('total_investment'),
                    "current_value": property_to_update.get('current_value'),
                    "rental_income": property_to_update.get('rental_income'),
                    "expenses": property_to_update.get('expenses'),
                    "photo": photo_url  # Use correct photo URL
                }
                
                update_resp = requests.put(
                    f"{BACKEND_URL}/properties/{prop_id}",
                    json=update_data,
                    headers=headers,
                    timeout=10
                )
                
                if update_resp.status_code in [200, 201]:
                    updated += 1
                    print(f"OK Property {prop_id}: Photo updated")
                else:
                    print(f"FAILED Property {prop_id}: Failed - {update_resp.status_code}")
            else:
                print(f"FAILED Property {prop_id}: Not found")
                
        except Exception as e:
            print(f"ERROR Property {prop_id}: Error - {e}")
    
    print(f"\nOK Successfully updated {updated} properties with correct photos")
    print("Photos should now match the correct properties!")

if __name__ == "__main__":
    main()