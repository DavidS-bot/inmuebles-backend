import sqlite3
import json

db_path = './data/dev.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("="*80)
print("MORTGAGE DATA CHECK:")
print("="*80)

# Query with correct column names
cursor.execute("""
    SELECT 
        p.id,
        p.address,
        p.purchase_price,
        p.down_payment,
        md.id as mortgage_id,
        md.initial_amount,
        md.outstanding_balance,
        md.margin_percentage,
        md.bank_entity
    FROM property p
    LEFT JOIN mortgagedetails md ON p.id = md.property_id
    ORDER BY p.id
""")

print("\nProperty Mortgage Information:")
print("-" * 80)
for row in cursor.fetchall():
    print(f"Property {row[0]}: {row[1]}")
    print(f"  Purchase Price: €{row[2]:,.2f}" if row[2] else "  Purchase Price: None")
    print(f"  Down Payment: €{row[3]:,.2f}" if row[3] else "  Down Payment: None")
    
    # Calculate initial debt
    initial_debt = (row[2] - row[3]) if (row[2] and row[3]) else row[2] if row[2] else 0
    print(f"  Calculated Initial Debt: €{initial_debt:,.2f}")
    
    if row[4]:  # Has mortgage record
        print(f"  Mortgage ID: {row[4]}")
        print(f"  Bank: {row[8]}")
        print(f"  Initial Mortgage Amount: €{row[5]:,.2f}" if row[5] else "  Initial Amount: None")
        print(f"  Outstanding Balance: €{row[6]:,.2f}" if row[6] else "  Outstanding Balance: 0.00")
        print(f"  Margin: {row[7]:.2f}%" if row[7] else "  Margin: None")
        print(f"  >>> EQUITY: €{(row[2] - (row[6] or 0)):,.2f}" if row[2] else "  >>> EQUITY: N/A")
    else:
        print("  ❌ NO MORTGAGE DATA FOUND - THIS IS THE PROBLEM!")
        print(f"  >>> EQUITY (no debt): €{row[2]:,.2f}" if row[2] else "  >>> EQUITY: N/A")
    print()

# Count properties with and without mortgage data
cursor.execute("SELECT COUNT(*) FROM property")
total_properties = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT property_id) FROM mortgagedetails")
properties_with_mortgage = cursor.fetchone()[0]

print("="*80)
print(f"SUMMARY: {properties_with_mortgage} out of {total_properties} properties have mortgage data")
print(f"MISSING MORTGAGE DATA FOR {total_properties - properties_with_mortgage} PROPERTIES!")
print("="*80)

conn.close()