#!/usr/bin/env python3

import requests
import json

# Configuration
API_BASE = "https://inmuebles-backend-api.onrender.com"
TEST_USER_EMAIL = "test@test.com"  # Change this to your test user
TEST_USER_PASSWORD = "test123"     # Change this to your test password

def test_viability_creation():
    """Test creating a viability study in production"""
    
    print("[TEST] Testing Viability Study Creation in Production")
    print("=" * 50)
    
    # Step 1: Login to get token
    print("1. Logging in...")
    login_data = {
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        token_data = response.json()
        token = token_data.get("access_token")
        
        if not token:
            print(f"❌ No token received: {token_data}")
            return False
            
        print(f"[OK] Login successful, got token: {token[:20]}...")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 2: Test viability endpoint
    print("\n2. Testing viability endpoint...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    study_data = {
        "study_name": "Test Study API",
        "purchase_price": 200000,
        "property_valuation": 200000,
        "purchase_taxes_percentage": 0.11,
        "renovation_costs": 5000,
        "real_estate_commission": 6000,
        "loan_amount": 160000,
        "interest_rate": 0.035,
        "loan_term_years": 25,
        "monthly_rent": 1200,
        "annual_rent_increase": 0.02,
        "community_fees": 1200,
        "property_tax_ibi": 800,
        "life_insurance": 300,
        "home_insurance": 200,
        "maintenance_percentage": 0.01,
        "property_management_fee": 0,
        "vacancy_risk_percentage": 0.05,
        "stress_test_rent_decrease": 0.10
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/viability/",
            headers=headers,
            json=study_data
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Study created successfully!")
            print(f"Study ID: {result.get('id')}")
            print(f"Study Name: {result.get('study_name')}")
            print(f"Net Annual Return: {result.get('net_annual_return', 0):.2%}")
            print(f"Monthly Cashflow: €{result.get('monthly_net_cashflow', 0):.2f}")
            print(f"Risk Level: {result.get('risk_level')}")
            return True
        else:
            print(f"❌ Study creation failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def test_endpoints():
    """Test various endpoints"""
    print("\n🔍 Testing Endpoints")
    print("=" * 30)
    
    endpoints_to_test = [
        "/health",
        "/test-auth",
        "/viability/"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{API_BASE}{endpoint}")
            print(f"{endpoint}: {response.status_code}")
        except Exception as e:
            print(f"{endpoint}: ERROR - {e}")

if __name__ == "__main__":
    print("🧪 PRODUCTION VIABILITY TEST")
    print("=" * 40)
    
    # Test basic endpoints
    test_endpoints()
    
    # Test viability creation
    success = test_viability_creation()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ TESTS FAILED - Check errors above")
        print("\n🔧 Possible issues:")
        print("- Wrong login credentials")
        print("- Database tables not created") 
        print("- Authentication problems")
        print("- Missing dependencies")