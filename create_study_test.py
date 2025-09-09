#!/usr/bin/env python3

import requests
import json

# Configuration
API_BASE = "https://inmuebles-backend-api.onrender.com"
TEST_USER_EMAIL = "admin@admin.com"
TEST_USER_PASSWORD = "admin123"

def create_study_with_admin():
    """Create a viability study using admin credentials"""
    
    print("Creating Viability Study with Admin Credentials")
    print("=" * 50)
    
    # Step 1: Login to get token
    print("1. Logging in as admin...")
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
            print(f"Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        token_data = response.json()
        token = token_data.get("access_token")
        
        if not token:
            print(f"No token received: {token_data}")
            return False
            
        print(f"Login successful, got token: {token[:20]}...")
        
    except Exception as e:
        print(f"Login error: {e}")
        return False
    
    # Step 2: Create viability study
    print("\n2. Creating viability study...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Real Madrid Centro property analysis
    study_data = {
        "study_name": "Madrid Centro - Calle Mayor 45",
        "purchase_price": 350000,
        "property_valuation": 350000,
        "purchase_taxes_percentage": 0.11,
        "renovation_costs": 15000,
        "real_estate_commission": 10500,
        "loan_amount": 280000,
        "interest_rate": 0.042,
        "loan_term_years": 30,
        "monthly_rent": 1800,
        "annual_rent_increase": 0.025,
        "community_fees": 1500,
        "property_tax_ibi": 1200,
        "life_insurance": 400,
        "home_insurance": 350,
        "maintenance_percentage": 0.015,
        "property_management_fee": 0.08,
        "vacancy_risk_percentage": 0.08,
        "stress_test_rent_decrease": 0.15
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/viability/",
            headers=headers,
            json=study_data
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("STUDY CREATED SUCCESSFULLY!")
            print(f"Full response: {json.dumps(result, indent=2)}")
            
            # Safe formatting with default values
            study_id = result.get('id', 'N/A')
            study_name = result.get('study_name', 'N/A')
            purchase_price = result.get('purchase_price', 0)
            total_investment = result.get('total_purchase_price', 0)
            monthly_rent = result.get('monthly_rent', 0)
            monthly_cashflow = result.get('monthly_net_cashflow', 0)
            annual_return = result.get('net_annual_return', 0)
            risk_level = result.get('risk_level', 'N/A')
            ltv_ratio = result.get('ltv_ratio', 0)
            
            print(f"Study ID: {study_id}")
            print(f"Study Name: {study_name}")
            print(f"Purchase Price: EUR{purchase_price:,.2f}")
            print(f"Total Investment: EUR{total_investment:,.2f}")
            print(f"Monthly Rent: EUR{monthly_rent:,.2f}")
            print(f"Monthly Net Cashflow: EUR{monthly_cashflow:,.2f}")
            print(f"Net Annual Return: {annual_return:.2%}")
            print(f"Risk Level: {risk_level}")
            print(f"LTV Ratio: {ltv_ratio:.1%}")
            
            return True
        else:
            print(f"Study creation failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Request error: {e}")
        return False

if __name__ == "__main__":
    print("CREATING VIABILITY STUDY WITH ADMIN CREDENTIALS")
    print("=" * 60)
    
    success = create_study_with_admin()
    
    print("\n" + "=" * 60)
    if success:
        print("STUDY CREATION COMPLETED SUCCESSFULLY!")
        print("Check the results at: https://inmuebles-web.vercel.app/estudios-viabilidad")
    else:
        print("STUDY CREATION FAILED - Check errors above")