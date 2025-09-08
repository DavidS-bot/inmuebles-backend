#!/usr/bin/env python3
"""
Generate final comprehensive report of classification rules
"""
import json
from collections import defaultdict, Counter

def generate_final_report():
    """Generate comprehensive report"""
    
    with open('production_classification_rules.json', 'r', encoding='utf-8') as f:
        rules = json.load(f)
    
    print("COMPREHENSIVE CLASSIFICATION RULES REPORT")
    print("=" * 60)
    print(f"Source: https://inmuebles-david.vercel.app/financial-agent/rules")
    print(f"Extraction Date: 2025-09-04")
    print(f"Total Rules Extracted: {len(rules)}")
    
    # Category analysis
    categories = Counter(rule['category'] for rule in rules)
    print(f"\nRULES BY CATEGORY:")
    print("-" * 30)
    for category, count in categories.items():
        print(f"{category}: {count} rules")
    
    # Property analysis
    properties = Counter(rule['property_id'] for rule in rules)
    print(f"\nRULES BY PROPERTY:")
    print("-" * 30)
    for prop_id, count in sorted(properties.items()):
        print(f"Property {prop_id}: {count} rules")
    
    # Detailed breakdown by category
    print(f"\nDETAILED RULES BY CATEGORY:")
    print("=" * 60)
    
    # Group by category
    by_category = defaultdict(list)
    for rule in rules:
        by_category[rule['category']].append(rule)
    
    for category in sorted(by_category.keys()):
        category_rules = by_category[category]
        print(f"\n{category.upper()} RULES ({len(category_rules)} total):")
        print("-" * (len(category) + 20))
        
        for i, rule in enumerate(category_rules, 1):
            tenant_info = f" [{rule['tenant_name']}]" if rule.get('tenant_name') else ""
            subcat_info = f" ({rule['subcategory']})" if rule.get('subcategory') else ""
            prop_info = f"[Property {rule['property_id']}]"
            
            print(f"{i:2d}. {rule['keyword'][:45]:<45} {prop_info:<12} {subcat_info}{tenant_info}")
    
    # Tenant analysis
    print(f"\nTENANT ANALYSIS:")
    print("-" * 30)
    tenants = [rule for rule in rules if rule.get('tenant_name')]
    tenant_names = Counter(rule['tenant_name'] for rule in tenants)
    
    print(f"Total rules with tenant names: {len(tenants)}")
    print(f"Unique tenants: {len(tenant_names)}")
    print("\nTenants with multiple rules:")
    for tenant, count in tenant_names.items():
        if count > 1:
            print(f"  {tenant}: {count} rules")
    
    # Keyword pattern analysis
    print(f"\nKEYWORD PATTERN ANALYSIS:")
    print("-" * 30)
    
    # Common patterns
    patterns = defaultdict(int)
    for rule in rules:
        keyword = rule['keyword'].upper()
        if 'TRANS' in keyword:
            patterns['TRANSFERENCIA'] += 1
        elif 'LIQUID' in keyword:
            patterns['LIQUIDACION'] += 1
        elif 'CUOTA' in keyword:
            patterns['CUOTA'] += 1
        elif 'ABONO' in keyword:
            patterns['ABONO'] += 1
        elif keyword.startswith('0049'):
            patterns['CODIGO_NUMERICO'] += 1
    
    print("Common keyword patterns:")
    for pattern, count in patterns.items():
        print(f"  {pattern}: {count} rules")
    
    # Summary for import
    import_summary = {
        "total_rules": len(rules),
        "categories": dict(categories),
        "properties": len(properties),
        "rules_for_import": [
            {
                "keyword": rule["keyword"],
                "category": rule["category"],
                "subcategory": rule.get("subcategory"),
                "tenant_name": rule.get("tenant_name"),
                "property_id": rule["property_id"],
                "is_active": rule["is_active"]
            }
            for rule in rules
        ]
    }
    
    with open('rules_for_local_import.json', 'w', encoding='utf-8') as f:
        json.dump(import_summary, f, indent=2, ensure_ascii=False)
    
    print(f"\nFILES GENERATED:")
    print("-" * 30)
    print(f"1. production_classification_rules.json - Raw extracted data")
    print(f"2. classification_rules_clean.json - Cleaned structured data")  
    print(f"3. rules_for_local_import.json - Ready for local database import")
    print(f"4. rules_analysis.json - Statistical analysis")
    
    print(f"\nREADY FOR LOCAL IMPORT:")
    print("-" * 30)
    print(f"The file 'rules_for_local_import.json' contains all {len(rules)} rules")
    print(f"in the correct format for importing to your local database.")
    print(f"This will help ensure no duplicates when importing to local system.")

if __name__ == "__main__":
    generate_final_report()