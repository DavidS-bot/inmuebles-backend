#!/usr/bin/env python3

import requests
import json

def create_studies_for_main_user():
    """Create viability studies for the main user"""
    
    print("CREATING STUDIES FOR MAIN USER")
    print("=" * 50)
    
    # Login as main user
    print("1. Logging in as main user...")
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
            print(f"Login failed: {response.status_code} - {response.text}")
            return False
            
        token = response.json().get("access_token")
        print(f"Login successful")
        
    except Exception as e:
        print(f"Login error: {e}")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Create multiple viability studies
    print("\n2. Creating viability studies...")
    
    studies_to_create = [
        {
            "study_name": "Piso Barcelona - Eixample",
            "purchase_price": 400000,
            "property_valuation": 400000,
            "purchase_taxes_percentage": 0.11,
            "renovation_costs": 20000,
            "real_estate_commission": 12000,
            "loan_amount": 320000,
            "interest_rate": 0.038,
            "loan_term_years": 30,
            "monthly_rent": 2200,
            "annual_rent_increase": 0.03,
            "community_fees": 1800,
            "property_tax_ibi": 1500,
            "life_insurance": 450,
            "home_insurance": 400,
            "maintenance_percentage": 0.015,
            "property_management_fee": 0.08,
            "vacancy_risk_percentage": 0.06,
            "stress_test_rent_decrease": 0.12
        },
        {
            "study_name": "Casa Valencia - Centro",
            "purchase_price": 280000,
            "property_valuation": 280000,
            "purchase_taxes_percentage": 0.10,
            "renovation_costs": 15000,
            "real_estate_commission": 8400,
            "loan_amount": 224000,
            "interest_rate": 0.041,
            "loan_term_years": 25,
            "monthly_rent": 1600,
            "annual_rent_increase": 0.025,
            "community_fees": 1200,
            "property_tax_ibi": 900,
            "life_insurance": 350,
            "home_insurance": 300,
            "maintenance_percentage": 0.012,
            "property_management_fee": 0.06,
            "vacancy_risk_percentage": 0.05,
            "stress_test_rent_decrease": 0.10
        },
        {
            "study_name": "Apartamento Sevilla - Triana",
            "purchase_price": 220000,
            "property_valuation": 220000,
            "purchase_taxes_percentage": 0.09,
            "renovation_costs": 8000,
            "real_estate_commission": 6600,
            "loan_amount": 176000,
            "interest_rate": 0.039,
            "loan_term_years": 30,
            "monthly_rent": 1300,
            "annual_rent_increase": 0.02,
            "community_fees": 800,
            "property_tax_ibi": 600,
            "life_insurance": 280,
            "home_insurance": 250,
            "maintenance_percentage": 0.01,
            "property_management_fee": 0.05,
            "vacancy_risk_percentage": 0.04,
            "stress_test_rent_decrease": 0.08
        }
    ]
    
    created_studies = 0
    for i, study_data in enumerate(studies_to_create, 1):
        try:
            response = requests.post(
                "https://inmuebles-backend-api.onrender.com/viability/",
                headers=headers,
                json=study_data
            )
            
            if response.status_code == 200:
                print(f"[OK] Study {i}: {study_data['study_name']}")
                created_studies += 1
            else:
                print(f"[ERROR] Study {i} failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"[ERROR] Study {i} error: {e}")
    
    # Verify studies were created
    print(f"\n3. Verifying created studies...")
    try:
        response = requests.get(
            "https://inmuebles-backend-api.onrender.com/viability/",
            headers=headers
        )
        
        if response.status_code == 200:
            studies = response.json()
            print(f"Total studies for main user: {len(studies)}")
            
            for study in studies:
                name = study.get('study_name', 'N/A')
                purchase_price = study.get('purchase_price', 0)
                monthly_rent = study.get('monthly_rent', 0)
                net_return = study.get('net_annual_return', 0)
                risk_level = study.get('risk_level', 'N/A')
                
                print(f"  - {name}")
                print(f"    Price: EUR{purchase_price:,.0f} | Rent: EUR{monthly_rent:,.0f}")
                print(f"    Return: {net_return:.2%} | Risk: {risk_level}")
                
        else:
            print(f"Failed to verify studies: {response.status_code}")
            
    except Exception as e:
        print(f"Error verifying studies: {e}")
    
    print(f"\nSUMMARY: Created {created_studies} studies for main user")
    return created_studies > 0

if __name__ == "__main__":
    success = create_studies_for_main_user()
    if success:
        print("\n[SUCCESS] STUDIES CREATED FOR MAIN USER!")
        print("Now the frontend should show the studies")
        print("Go to: https://inmuebles-web.vercel.app/estudios-viabilidad")
    else:
        print("\n[FAILED] FAILED TO CREATE STUDIES")