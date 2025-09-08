import sqlite3

db_path = './data/dev.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("="*80)
print("CLASSIFICATION RULES DATA CHECK:")
print("="*80)

# Check all classification rules
cursor.execute("""
    SELECT 
        cr.id,
        cr.property_id,
        cr.keyword,
        cr.category,
        cr.subcategory,
        cr.tenant_name,
        cr.is_active,
        p.address as property_address
    FROM classificationrule cr
    LEFT JOIN property p ON cr.property_id = p.id
    ORDER BY cr.property_id, cr.id
""")

print("\nAll Classification Rules:")
print("-" * 80)
current_property_id = None

for row in cursor.fetchall():
    rule_id, property_id, keyword, category, subcategory, tenant_name, is_active, property_address = row
    
    if current_property_id != property_id:
        current_property_id = property_id
        print(f"\n>> Property {property_id}: {property_address}")
        print("-" * 40)
    
    status = "Active" if is_active else "Inactive"
    subcategory_text = f" -> {subcategory}" if subcategory else ""
    tenant_text = f" (Tenant: {tenant_name})" if tenant_name else ""
    
    print(f"  Rule {rule_id}: '{keyword}' -> {category}{subcategory_text}{tenant_text} [{status}]")

# Summary
cursor.execute("SELECT COUNT(*) FROM classificationrule")
total_rules = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM classificationrule WHERE is_active = 1")
active_rules = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT property_id) FROM classificationrule")
properties_with_rules = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM property")
total_properties = cursor.fetchone()[0]

print("\n" + "="*80)
print("SUMMARY:")
print(f"Total rules: {total_rules}")
print(f"Active rules: {active_rules}")
print(f"Inactive rules: {total_rules - active_rules}")
print(f"Properties with rules: {properties_with_rules} out of {total_properties}")
print(f"Properties WITHOUT rules: {total_properties - properties_with_rules}")
print("="*80)

conn.close()