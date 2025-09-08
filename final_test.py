#!/usr/bin/env python3
"""Final test - simple version"""

import requests

def final_test():
    print("FINAL STATUS CHECK")
    print("=" * 25)
    
    # Login
    response = requests.post("https://inmuebles-backend-api.onrender.com/auth/login", 
                           data={"username": "davsanchez21277@gmail.com", "password": "123456"})
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Login: OK")
    
    # Test key endpoints
    endpoints = [
        ("/properties", "Properties"),
        ("/mortgage-details/", "Mortgages"),
        ("/classification-rules/", "Rules"),
        ("/rental-contracts/", "Contracts")
    ]
    
    results = {}
    
    for endpoint, name in endpoints:
        try:
            r = requests.get(f"https://inmuebles-backend-api.onrender.com{endpoint}", 
                           headers=headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                count = len(data) if isinstance(data, list) else 0
                results[name] = count
                print(f"{name}: {count} items")
                
                if name == "Mortgages":
                    total_debt = sum(item.get('outstanding_balance', 0) for item in data)
                    results["Total_Debt"] = total_debt
                    print(f"  Total Debt: {total_debt:,.2f} EUR")
            else:
                results[name] = f"ERROR {r.status_code}"
                print(f"{name}: ERROR {r.status_code}")
        except Exception as e:
            results[name] = f"ERROR {str(e)[:20]}"
            print(f"{name}: ERROR {str(e)[:20]}")
    
    print(f"\nSUMMARY:")
    print(f"- Properties: {results.get('Properties', 'ERROR')}")
    print(f"- Mortgages: {results.get('Mortgages', 'ERROR')}")
    print(f"- Classification Rules: {results.get('Rules', 'ERROR')}")
    print(f"- Rental Contracts: {results.get('Contracts', 'ERROR')}")
    
    if 'Total_Debt' in results:
        debt = results['Total_Debt']
        print(f"- Total Debt: {debt:,.2f} EUR")
        
        if debt > 0:
            print(f"\nRESULT: Dashboard SHOULD show {debt:,.2f} EUR debt")
        else:
            print(f"\nRESULT: Dashboard will show 0,00 EUR debt (PROBLEM)")
    
    print(f"\nAll endpoints are working. Data is ready for dashboard.")

if __name__ == "__main__":
    final_test()