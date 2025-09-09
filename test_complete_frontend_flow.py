#!/usr/bin/env python3

import requests
import json

def test_complete_frontend_flow():
    """Test the complete frontend authentication and data flow"""
    
    print("TESTING COMPLETE FRONTEND FLOW")
    print("=" * 50)
    
    # Simulate the exact frontend flow
    session = requests.Session()
    
    # 1. Test NextAuth login endpoint
    print("1. Testing NextAuth login...")
    
    try:
        # Test NextAuth callback endpoint
        auth_response = session.post(
            "https://inmuebles-web.vercel.app/api/auth/callback/credentials",
            json={
                "email": "davsanchez21277@gmail.com",
                "password": "123456"
            },
            headers={
                "Content-Type": "application/json",
                "Origin": "https://inmuebles-web.vercel.app"
            }
        )
        
        print(f"NextAuth login status: {auth_response.status_code}")
        print(f"NextAuth response: {auth_response.text[:200]}...")
        
    except Exception as e:
        print(f"NextAuth login error: {e}")
    
    # 2. Test direct API calls (what frontend should do)
    print(f"\n2. Testing direct API calls...")
    
    # Login directly to backend
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
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"Backend login successful")
            
            # Test viability endpoint
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                "https://inmuebles-backend-api.onrender.com/viability/",
                headers=headers
            )
            
            if response.status_code == 200:
                studies = response.json()
                print(f"Viability studies: {len(studies)} found")
                
                # Show summary stats that frontend should display
                total_studies = len(studies)
                favorable_studies = len([s for s in studies if s.get('net_annual_return', 0) > 0])
                avg_return = sum([s.get('net_annual_return', 0) for s in studies]) / len(studies) if studies else 0
                
                print(f"\nFRONTEND SHOULD SHOW:")
                print(f"Total Estudios: {total_studies}")
                print(f"Favorables: {favorable_studies}")
                print(f"Rentabilidad Media: {avg_return:.1%}")
                
                for i, study in enumerate(studies, 1):
                    name = study.get('study_name', 'N/A')
                    price = study.get('purchase_price', 0)
                    rent = study.get('monthly_rent', 0)
                    return_rate = study.get('net_annual_return', 0)
                    risk = study.get('risk_level', 'N/A')
                    
                    print(f"  Study {i}: {name}")
                    print(f"    Price: €{price:,.0f} | Rent: €{rent:,.0f}/mes")
                    print(f"    Return: {return_rate:.2%} | Risk: {risk}")
                
            else:
                print(f"Viability API failed: {response.status_code}")
                
        else:
            print(f"Backend login failed: {response.status_code}")
            
    except Exception as e:
        print(f"Direct API test error: {e}")
    
    # 3. Test if the issue is caching
    print(f"\n3. Cache busting suggestions...")
    print("The frontend might be caching old data.")
    print("Try these steps:")
    print("1. Hard refresh the page (Ctrl+F5)")
    print("2. Clear browser cache and cookies")
    print("3. Logout and login again")
    print("4. Try incognito/private browsing")

if __name__ == "__main__":
    test_complete_frontend_flow()