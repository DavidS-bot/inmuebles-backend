#!/usr/bin/env python3
"""Fix property photos to match correct properties"""

import requests
import sqlite3
from pathlib import Path
import os

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def fix_photos():
    print("FIXING PROPERTY PHOTOS")
    print("=" * 40)
    
    # Get local database photo mappings
    db_path = Path("data/dev.db")
    if not db_path.exists():
        print("Local database not found")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get properties with photos
    cursor.execute("SELECT id, address, photo FROM property WHERE photo IS NOT NULL")
    local_properties = cursor.fetchall()
    
    print(f"Found {len(local_properties)} properties with photos in local DB")
    
    # Login to production
    response = requests.post(f"{PROD_API}/auth/login", 
                           data={"username": EMAIL, "password": PASSWORD}, timeout=10)
    if response.status_code != 200:
        print("Login failed")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get production properties
    response = requests.get(f"{PROD_API}/properties", headers=headers, timeout=10)
    prod_properties = response.json()
    
    print(f"Found {len(prod_properties)} properties in production")
    
    updated = 0
    
    for local_prop in local_properties:
        # Find matching production property by address
        prod_prop = None
        local_addr = local_prop['address'].lower().strip()
        
        for pp in prod_properties:
            prod_addr = pp['address'].lower().strip()
            # Match by significant parts of address
            if ("aranguren" in local_addr and "aranguren" in prod_addr and 
                ("68" in local_addr and "68" in prod_addr or
                 "66" in local_addr and "66" in prod_addr or
                 "22" in local_addr and "22" in prod_addr)):
                prod_prop = pp
                break
            elif "platon" in local_addr and "platon" in prod_addr:
                prod_prop = pp
                break
            elif "seneca" in local_addr and "seneca" in prod_addr:
                prod_prop = pp
                break
            elif ("lago" in local_addr and "lago" in prod_addr and 
                  ("enol" in local_addr and "enol" in prod_addr or
                   "bañolas" in local_addr and "ba" in prod_addr)):
                # More specific matching for Lago properties
                if ("puerta f" in local_addr and "puerta f" in prod_addr or
                    "primera" in local_addr and "primera" in prod_addr):
                    prod_prop = pp
                    break
                elif ("puerta a" in local_addr and "puerta a" in prod_addr):
                    prod_prop = pp
                    break
                elif ("puerta 4" in local_addr and "puerta 4" in prod_addr):
                    prod_prop = pp
                    break
                elif ("puerta 9" in local_addr and "puerta 9" in prod_addr):
                    prod_prop = pp
                    break
                elif ("puerta g" in local_addr and "puerta g" in prod_addr):
                    prod_prop = pp
                    break
        
        if not prod_prop:
            print(f"No match for: {local_prop['address'][:50]}")
            continue
        
        # Get photo file path
        photo_path = local_prop['photo']
        if photo_path.startswith('/uploads/photo/'):
            # Extract filename
            filename = photo_path.split('/')[-1]
            local_photo_file = Path(f"uploads/{filename}")
            
            if not local_photo_file.exists():
                print(f"Photo not found: {local_photo_file}")
                continue
            
            print(f"Uploading photo for: {prod_prop['address'][:40]}")
            
            try:
                # Upload photo to production
                with open(local_photo_file, 'rb') as f:
                    files = {'file': (filename, f, 'image/jpeg')}
                    response = requests.post(
                        f"{PROD_API}/uploads/photo",
                        files=files,
                        headers=headers,
                        timeout=30
                    )
                    
                    if response.status_code in [200, 201]:
                        photo_data = response.json()
                        photo_url = photo_data.get('url', '')
                        
                        # Update property with new photo URL
                        update_data = {
                            "address": prod_prop['address'],
                            "property_type": prod_prop.get('property_type'),
                            "rooms": prod_prop.get('rooms'),
                            "m2": prod_prop.get('m2'),
                            "purchase_price": prod_prop.get('purchase_price'),
                            "purchase_date": prod_prop.get('purchase_date'),
                            "photo": photo_url
                        }
                        
                        response = requests.put(
                            f"{PROD_API}/properties/{prod_prop['id']}",
                            json=update_data,
                            headers={**headers, "Content-Type": "application/json"},
                            timeout=15
                        )
                        
                        if response.status_code == 200:
                            updated += 1
                            print(f"  SUCCESS: Updated photo for {prod_prop['address'][:40]}")
                        else:
                            print(f"  FAILED to update property: {response.status_code}")
                    else:
                        print(f"  FAILED to upload photo: {response.status_code}")
                        
            except Exception as e:
                print(f"  ERROR: {str(e)[:50]}")
    
    print(f"\nUpdated {updated} property photos")
    conn.close()

if __name__ == "__main__":
    fix_photos()