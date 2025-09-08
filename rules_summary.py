#!/usr/bin/env python3
"""
Create a structured summary of the extracted classification rules
"""
import json
from collections import defaultdict

def load_and_analyze_rules():
    """Load the rules and create a structured analysis"""
    
    with open('production_classification_rules.json', 'r', encoding='utf-8') as f:
        rules = json.load(f)
    
    # Group rules by property and category
    by_property = defaultdict(lambda: {"Renta": [], "Hipoteca": [], "Gasto": []})
    by_category = {"Renta": [], "Hipoteca": [], "Gasto": []}
    
    for rule in rules:
        prop_id = rule["property_id"]
        category = rule["category"]
        
        rule_summary = {
            "id": rule["id"],
            "keyword": rule["keyword"],
            "subcategory": rule.get("subcategory"),
            "tenant_name": rule.get("tenant_name"),
            "is_active": rule["is_active"]
        }
        
        by_property[prop_id][category].append(rule_summary)
        by_category[category].append({
            **rule_summary,
            "property_id": prop_id
        })
    
    # Create clean summary
    summary = {
        "total_rules": len(rules),
        "total_properties": len(by_property),
        "rules_by_category": {
            "Renta": len(by_category["Renta"]),
            "Hipoteca": len(by_category["Hipoteca"]),
            "Gasto": len(by_category["Gasto"])
        },
        "rules_by_property": {
            str(prop_id): {
                "total_rules": sum(len(by_property[prop_id][cat]) for cat in by_property[prop_id]),
                "renta_rules": len(by_property[prop_id]["Renta"]),
                "hipoteca_rules": len(by_property[prop_id]["Hipoteca"]),
                "gasto_rules": len(by_property[prop_id]["Gasto"]),
                "rules": dict(by_property[prop_id])
            }
            for prop_id in sorted(by_property.keys())
        },
        "all_rules_by_category": by_category
    }
    
    return summary

def main():
    print("ANALYZING EXTRACTED CLASSIFICATION RULES")
    print("=" * 50)
    
    summary = load_and_analyze_rules()
    
    # Save structured summary
    with open('rules_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"Total rules: {summary['total_rules']}")
    print(f"Total properties with rules: {summary['total_properties']}")
    print("\nRules by category:")
    for category, count in summary['rules_by_category'].items():
        print(f"  {category}: {count}")
    
    print(f"\nRules by property:")
    for prop_id, data in summary['rules_by_property'].items():
        print(f"  Property {prop_id}: {data['total_rules']} rules " +
              f"(Renta: {data['renta_rules']}, Hipoteca: {data['hipoteca_rules']}, Gasto: {data['gasto_rules']})")
    
    print(f"\nDetailed analysis saved to: rules_analysis.json")
    
    # Show some sample rules by category
    print(f"\nSAMPLE RULES BY CATEGORY:")
    print("-" * 30)
    
    for category in ["Renta", "Hipoteca", "Gasto"]:
        rules = summary['all_rules_by_category'][category][:3]  # First 3 rules
        print(f"\n{category} ({len(summary['all_rules_by_category'][category])} total):")
        for rule in rules:
            tenant_info = f" [{rule['tenant_name']}]" if rule.get('tenant_name') else ""
            subcat_info = f" ({rule['subcategory']})" if rule.get('subcategory') else ""
            print(f"  - {rule['keyword'][:50]}{'...' if len(rule['keyword']) > 50 else ''}{subcat_info}{tenant_info}")

if __name__ == "__main__":
    main()