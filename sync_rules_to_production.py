import sqlite3
import requests
import json

# Local database
local_db = './data/dev.db'

# Production API
PROD_API = "https://inmuebles-backend-api.onrender.com"

def get_auth_token():
    """Get authentication token from production"""
    try:
        # Try form data format
        response = requests.post(f"{PROD_API}/auth/login", 
                               data={"username": "admin", "password": "admin123"}, 
                               timeout=10)
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Login failed (form): {response.status_code} - {response.text}")
            
            # Try JSON format
            response = requests.post(f"{PROD_API}/auth/login", 
                                   json={"username": "admin", "password": "admin123"},
                                   headers={"Content-Type": "application/json"}, 
                                   timeout=10)
            if response.status_code == 200:
                return response.json()["access_token"]
            else:
                print(f"Login failed (json): {response.status_code} - {response.text}")
            
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def get_local_rules():
    """Get all rules from local database"""
    conn = sqlite3.connect(local_db)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            cr.id,
            cr.property_id,
            cr.keyword,
            cr.category,
            cr.subcategory,
            cr.tenant_name,
            cr.is_active
        FROM classificationrule cr
        WHERE cr.is_active = 1
        ORDER BY cr.property_id, cr.id
    """)
    
    rules = []
    for row in cursor.fetchall():
        rule_id, property_id, keyword, category, subcategory, tenant_name, is_active = row
        rules.append({
            'property_id': property_id,
            'keyword': keyword,
            'category': category,
            'subcategory': subcategory,
            'tenant_name': tenant_name,
            'is_active': bool(is_active)
        })
    
    conn.close()
    return rules

def get_production_rules(token):
    """Get all rules from production"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{PROD_API}/classification-rules/", 
                              headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get production rules: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error getting production rules: {e}")
        return []

def sync_rules_to_production(token):
    """Sync all local rules to production"""
    print("="*80)
    print("SYNCING CLASSIFICATION RULES TO PRODUCTION")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    local_rules = get_local_rules()
    production_rules = get_production_rules(token)
    
    print(f"\nLocal rules: {len(local_rules)}")
    print(f"Production rules: {len(production_rules)}")
    
    # Create a set of production rule signatures for comparison
    prod_rule_sigs = set()
    for rule in production_rules:
        sig = f"{rule['property_id']}-{rule['keyword']}-{rule['category']}"
        prod_rule_sigs.add(sig)
    
    created_count = 0
    skipped_count = 0
    
    for rule in local_rules:
        rule_sig = f"{rule['property_id']}-{rule['keyword']}-{rule['category']}"
        
        if rule_sig in prod_rule_sigs:
            print(f"  SKIP: Property {rule['property_id']} - '{rule['keyword']}' ({rule['category']}) - already exists")
            skipped_count += 1
            continue
        
        try:
            response = requests.post(f"{PROD_API}/classification-rules/", 
                                   json=rule, 
                                   headers=headers, 
                                   timeout=10)
            if response.status_code in [200, 201]:
                print(f"  ✓ CREATED: Property {rule['property_id']} - '{rule['keyword']}' ({rule['category']})")
                created_count += 1
            else:
                print(f"  ✗ FAILED: Property {rule['property_id']} - '{rule['keyword']}' - {response.status_code}: {response.text}")
        except Exception as e:
            print(f"  ✗ ERROR: Property {rule['property_id']} - '{rule['keyword']}' - {e}")
    
    print(f"\n" + "="*80)
    print("SYNC SUMMARY:")
    print(f"Created: {created_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Total local: {len(local_rules)}")
    print("="*80)

if __name__ == "__main__":
    print("Getting authentication token...")
    token = get_auth_token()
    
    if token:
        print("Token obtained successfully!")
        sync_rules_to_production(token)
    else:
        print("Failed to get authentication token!")