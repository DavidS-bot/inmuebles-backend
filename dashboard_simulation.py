#!/usr/bin/env python3
"""Simulate exactly what the dashboard does"""

import requests

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def simulate_dashboard():
    print("DASHBOARD SIMULATION TEST")
    print("=" * 30)
    
    # Login (same as dashboard)
    try:
        response = requests.post(f"{PROD_API}/auth/login", 
                               data={"username": EMAIL, "password": PASSWORD}, timeout=10)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return
        token = response.json()["access_token"]
        print("✅ Login successful")
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 1: Load properties (like dashboard does)
    try:
        response = requests.get(f"{PROD_API}/properties", headers=headers, timeout=10)
        if response.status_code == 200:
            properties = response.json()
            print(f"✅ Properties loaded: {len(properties)}")
        else:
            print(f"❌ Properties failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Properties error: {e}")
        return
    
    # Step 2: Try analytics endpoint (dashboard's first choice)
    total_gross_income = 0
    total_expenses = 0
    current_year = 2025
    
    try:
        response = requests.get(f"{PROD_API}/analytics/portfolio-summary?year={current_year}", 
                               headers=headers, timeout=15)
        if response.status_code == 200:
            portfolio_data = response.json()
            total_gross_income = portfolio_data.get('total_income', 0)
            total_expenses = portfolio_data.get('total_expenses', 0)
            print(f"✅ Analytics data loaded:")
            print(f"   Total Income: {total_gross_income:,.2f} EUR")
            print(f"   Total Expenses: {total_expenses:,.2f} EUR")
        else:
            print(f"⚠️  Analytics failed: {response.status_code}, will use fallback")
    except Exception as e:
        print(f"⚠️  Analytics error: {e}, will use fallback")
    
    # Step 3: Load mortgages (CRITICAL - this was the bug)
    total_debt = 0
    try:
        response = requests.get(f"{PROD_API}/mortgage-details/", headers=headers, timeout=15)
        if response.status_code == 200:
            mortgages = response.json()
            total_debt = sum(m.get('outstanding_balance', 0) for m in mortgages)
            print(f"✅ MORTGAGES LOADED: {len(mortgages)} items")
            print(f"✅ TOTAL DEBT: {total_debt:,.2f} EUR")
        else:
            print(f"❌ Mortgages failed: {response.status_code}")
            print(f"   This would cause debt to show as 0,00 EUR!")
    except Exception as e:
        print(f"❌ Mortgages error: {e}")
        print(f"   This would cause debt to show as 0,00 EUR!")
    
    # Step 4: Calculate totals (like dashboard does)
    total_investment = sum(p.get('purchase_price', 0) for p in properties)
    total_market_value = sum(p.get('current_value', p.get('purchase_price', 0) * 1.1) for p in properties)
    total_equity = total_market_value - total_debt
    total_net_income = total_gross_income - total_expenses
    
    print(f"\n📊 DASHBOARD CALCULATIONS:")
    print(f"   Total Investment: {total_investment:,.2f} EUR")
    print(f"   Total Market Value: {total_market_value:,.2f} EUR")
    print(f"   Total Equity: {total_equity:,.2f} EUR")
    print(f"   Total Debt: {total_debt:,.2f} EUR")
    print(f"   Total Net Income: {total_net_income:,.2f} EUR")
    
    # Step 5: Check if classification rules and contracts are available
    try:
        response = requests.get(f"{PROD_API}/classification-rules/", headers=headers, timeout=10)
        if response.status_code == 200:
            rules = response.json()
            print(f"✅ Classification Rules: {len(rules)} available")
        else:
            print(f"❌ Classification Rules: {response.status_code}")
    except Exception as e:
        print(f"❌ Classification Rules error: {e}")
    
    try:
        response = requests.get(f"{PROD_API}/rental-contracts/", headers=headers, timeout=10)
        if response.status_code == 200:
            contracts = response.json()
            print(f"✅ Rental Contracts: {len(contracts)} available")
        else:
            print(f"❌ Rental Contracts: {response.status_code}")
    except Exception as e:
        print(f"❌ Rental Contracts error: {e}")
    
    print(f"\n🎯 EXPECTED DASHBOARD VALUES:")
    print(f"   Valor Total Mercado: {total_market_value:,.2f} €")
    print(f"   Equity Total: {total_equity:,.2f} €")
    print(f"   Deuda Total: {total_debt:,.2f} €")  # This should NOT be 0!
    
    if total_debt > 0:
        print(f"✅ SUCCESS: Dashboard should show correct debt!")
    else:
        print(f"❌ PROBLEM: Dashboard will still show 0,00 € debt!")

if __name__ == "__main__":
    simulate_dashboard()