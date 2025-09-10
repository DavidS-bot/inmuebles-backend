#!/usr/bin/env python3

import requests
import json

def simple_api_test():
    """Simple test of the API without unicode issues"""
    
    print("SIMPLE API TEST")
    print("=" * 50)
    
    # Login
    login_data = {
        "username": "davsanchez21277@gmail.com", 
        "password": "123456"
    }
    
    try:
        response = requests.post(
            "https://inmuebles-backend-api.onrender.com/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            print(f"[ERROR] Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        token_data = response.json()
        token = token_data.get("access_token")
        
        print(f"[OK] Login successful")
        print(f"Token: {token[:20]}...")
        
        # Test viability endpoint
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            "https://inmuebles-backend-api.onrender.com/viability/",
            headers=headers
        )
        
        print(f"\n[TEST] Viability endpoint:")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            studies = response.json()
            print(f"Studies found: {len(studies)}")
            
            if len(studies) > 0:
                print(f"\n[SUCCESS] API IS WORKING!")
                
                # Calculate stats
                total = len(studies)
                favorable = len([s for s in studies if s.get('net_annual_return', 0) > 0])
                avg_return = sum([s.get('net_annual_return', 0) for s in studies]) / len(studies)
                
                print(f"\nFRONTEND SHOULD SHOW:")
                print(f"Total Estudios: {total}")
                print(f"Favorables: {favorable}")
                print(f"Rentabilidad Media: {avg_return:.1%}")
                
                print(f"\nSTUDY LIST:")
                for i, study in enumerate(studies, 1):
                    name = study.get('study_name', 'N/A')
                    price = study.get('purchase_price', 0)
                    rent = study.get('monthly_rent', 0)
                    return_rate = study.get('net_annual_return', 0)
                    risk = study.get('risk_level', 'N/A')
                    
                    print(f"{i}. {name}")
                    print(f"   Price: EUR{price:,.0f} | Rent: EUR{rent:,.0f}")
                    print(f"   Return: {return_rate:.2%} | Risk: {risk}")
                
                return True
            else:
                print(f"[ERROR] No studies found")
                return False
        else:
            print(f"[ERROR] API failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        return False

if __name__ == "__main__":
    print("TESTING VIABILITY API DIRECTLY")
    print("="*50)
    
    success = simple_api_test()
    
    print("\n" + "="*50)
    if success:
        print("[SUCCESS] THE API IS WORKING CORRECTLY!")
        print("")
        print("FRONTEND PROBLEM DIAGNOSIS:")
        print("1. The backend API is working perfectly")
        print("2. The frontend is not calling the API correctly")
        print("3. Possible causes:")
        print("   - Token not saved in localStorage")
        print("   - Frontend caching old data")
        print("   - JavaScript errors preventing API calls")
        print("   - Authentication not working in frontend")
        print("")
        print("IMMEDIATE SOLUTIONS:")
        print("1. Open browser Developer Tools (F12)")
        print("2. Go to Console tab")
        print("3. Look for errors when loading the page")
        print("4. Go to Application/Storage tab")
        print("5. Check localStorage for 'auth_token'")
        print("6. If no token, go to /login and login again")
        print("7. Clear all browser data and try again")
        
    else:
        print("[FAILED] API NOT WORKING")
        print("Need to fix backend first")