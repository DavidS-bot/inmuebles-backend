#!/usr/bin/env python3
"""Fix analytics discrepancies and update property valuations"""

import requests

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

def fix_analytics():
    print("FIXING ANALYTICS AND VALUATIONS")
    print("=" * 40)
    
    # Login
    response = requests.post(f"{PROD_API}/auth/login", 
                           data={"username": EMAIL, "password": PASSWORD}, timeout=10)
    if response.status_code != 200:
        print("Login failed")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 1: Get market valuations
    print("1. GETTING MARKET VALUATIONS:")
    response = requests.get(f"{PROD_API}/integrations/market-prices", headers=headers, timeout=15)
    
    if response.status_code == 200:
        market_response = response.json()
        market_data = market_response.get('market_data', [])
        print(f"   Found {len(market_data)} property valuations")
        
        # Step 2: Update properties with market valuations
        print("\n2. UPDATING PROPERTY VALUATIONS:")
        response = requests.get(f"{PROD_API}/properties", headers=headers, timeout=10)
        properties = response.json()
        
        updated_properties = 0
        
        for prop in properties:
            # Find matching market data
            market_value = None
            for market_prop in market_data:
                if market_prop['property_id'] == prop['id']:
                    market_value = market_prop['estimated_value']
                    break
            
            if market_value and not prop.get('appraisal_value'):
                # Update property with market value
                update_data = {
                    "address": prop['address'],
                    "property_type": prop.get('property_type'),
                    "rooms": prop.get('rooms'),
                    "m2": prop.get('m2'),
                    "purchase_price": prop.get('purchase_price'),
                    "purchase_date": prop.get('purchase_date'),
                    "appraisal_value": market_value,
                    "photo": prop.get('photo')
                }
                
                try:
                    response = requests.put(
                        f"{PROD_API}/properties/{prop['id']}",
                        json=update_data,
                        headers={**headers, "Content-Type": "application/json"},
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        updated_properties += 1
                        print(f"   Updated {prop['address'][:40]:40}: {market_value:>8.0f} EUR")
                    else:
                        print(f"   Failed {prop['address'][:40]}: {response.status_code}")
                        
                except Exception as e:
                    print(f"   Error {prop['address'][:40]}: {str(e)[:30]}")
        
        print(f"\n   Updated {updated_properties} properties with market valuations")
    
    else:
        print(f"   Market prices error: {response.status_code}")
    
    # Step 3: Get corrected analytics summary
    print("\n3. ANALYTICS SUMMARY WITH DEBT:")
    
    # Get mortgage debt total
    response = requests.get(f"{PROD_API}/mortgage-details/", headers=headers, timeout=10)
    total_debt = 0
    if response.status_code == 200:
        mortgages = response.json()
        total_debt = sum(m.get('outstanding_balance', 0) for m in mortgages)
        print(f"   Total mortgage debt: {total_debt:,.2f} EUR")
    
    # Get portfolio analytics
    response = requests.get(f"{PROD_API}/analytics/portfolio-summary", headers=headers, timeout=15)
    if response.status_code == 200:
        analytics = response.json()
        
        # Calculate additional metrics
        total_investment = analytics.get('total_investment', 0)
        total_property_value = 0
        
        # Get updated property values
        response = requests.get(f"{PROD_API}/properties", headers=headers, timeout=10)
        if response.status_code == 200:
            properties = response.json()
            for prop in properties:
                appraisal = prop.get('appraisal_value', 0) or 0
                purchase = prop.get('purchase_price', 0) or 0
                # Use appraisal if available, otherwise purchase price
                total_property_value += appraisal if appraisal > 0 else purchase
        
        print(f"\n   CORRECTED ANALYTICS:")
        print(f"   Total properties: {analytics.get('total_properties', 0)}")
        print(f"   Total investment: {total_investment:,.2f} EUR")
        print(f"   Total property value: {total_property_value:,.2f} EUR") 
        print(f"   Total mortgage debt: {total_debt:,.2f} EUR")
        print(f"   Net equity: {total_property_value - total_debt:,.2f} EUR")
        print(f"   Total net income: {analytics.get('total_net_income', 0):,.2f} EUR")
        print(f"   Average ROI: {analytics.get('average_roi', 0):.2f}%")
        
        # Debt coverage ratio
        debt_coverage = (total_property_value / total_debt * 100) if total_debt > 0 else 0
        print(f"   Debt coverage ratio: {debt_coverage:.1f}%")
        
    else:
        print(f"   Analytics error: {response.status_code}")
    
    # Step 4: Verify active contracts
    print("\n4. VERIFYING ACTIVE CONTRACTS:")
    response = requests.get(f"{PROD_API}/rental-contracts/", headers=headers, timeout=10)
    if response.status_code == 200:
        contracts = response.json()
        
        # Group by property
        active_by_property = {}
        for contract in contracts:
            prop_id = contract['property_id']
            if prop_id not in active_by_property:
                active_by_property[prop_id] = []
            
            # Check if really active (not expired)
            is_active = contract.get('is_active', False)
            is_expired = False
            
            if contract.get('end_date'):
                from datetime import datetime
                try:
                    end_date = datetime.strptime(contract['end_date'], '%Y-%m-%d')
                    if end_date < datetime.now():
                        is_expired = True
                        is_active = False
                except:
                    pass
            
            if is_active and not is_expired:
                active_by_property[prop_id].append(contract)
        
        # Show active contracts by property
        total_active = 0
        for prop_id, active_contracts in active_by_property.items():
            if active_contracts:
                total_active += len(active_contracts)
                # Get property address
                prop_address = "Unknown Property"
                for prop in properties:
                    if prop['id'] == prop_id:
                        prop_address = prop['address'][:40]
                        break
                
                print(f"   {prop_address:40}: {len(active_contracts)} active")
                for contract in active_contracts:
                    print(f"     - {contract['tenant_name'][:35]:35} | {contract['monthly_rent']:4.0f} EUR/month")
        
        print(f"\n   Total active contracts: {total_active}")
        
    print("\n" + "=" * 40)
    print("Analytics fixes completed")

if __name__ == "__main__":
    fix_analytics()