#!/usr/bin/env python3
import sqlite3
import re
import os

print("=== TESTING DIRECT CLEANING LOGIC ===")

# Get the path to the backend directory
backend_path = os.getcwd()
db_path = os.path.join(backend_path, 'data/dev.db')

print(f"Backend path: {backend_path}")
print(f"Database path: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Check current coletillas
    cursor.execute("SELECT COUNT(*) FROM financialmovement WHERE concept LIKE '%Pulsa para ver%'")
    before_count = cursor.fetchone()[0]
    print(f"Before cleaning: {before_count} movements with coletillas")
    
    # 2. Apply the EXACT same logic as in bankinter_simple.py
    cursor.execute("SELECT id, concept FROM financialmovement WHERE concept LIKE '%Pulsa para ver%' ORDER BY id DESC LIMIT 50")
    movements = cursor.fetchall()
    
    cleaned_count = 0
    for mov_id, concept in movements:
        cleaned = re.sub(r'Pulsa para ver detalle.*$', '', concept, flags=re.IGNORECASE | re.MULTILINE)
        cleaned = re.sub(r'\n.*Pulsa para ver.*$', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        cleaned = re.sub(r'.*Pulsa para ver.*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\n+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        if cleaned != concept and cleaned:
            cursor.execute("UPDATE financialmovement SET concept = ? WHERE id = ?", (cleaned, mov_id))
            if cursor.rowcount > 0:
                cleaned_count += 1
                print(f"Cleaned movement {mov_id}: '{concept}' -> '{cleaned}'")
    
    # 3. Apply classification
    cursor.execute("SELECT id, concept FROM financialmovement WHERE property_id IS NULL ORDER BY id DESC LIMIT 20")
    unassigned = cursor.fetchall()
    
    cursor.execute("SELECT property_id, keyword, tenant_name FROM classificationrule WHERE is_active = 1")
    rules = cursor.fetchall()
    
    assigned_count = 0
    for mov_id, concept in unassigned:
        concept_upper = concept.upper().strip()
        for property_id, keyword, tenant_name in rules:
            if keyword.upper().strip() in concept_upper and len(keyword) > 5:
                cursor.execute("UPDATE financialmovement SET property_id = ?, tenant_name = ? WHERE id = ?", 
                              (property_id, tenant_name, mov_id))
                if cursor.rowcount > 0:
                    assigned_count += 1
                    print(f"Assigned movement {mov_id} to property {property_id}")
                    break
    
    conn.commit()
    
    # 4. Check after cleaning
    cursor.execute("SELECT COUNT(*) FROM financialmovement WHERE concept LIKE '%Pulsa para ver%'")
    after_count = cursor.fetchone()[0]
    
    print(f"RESULT: {cleaned_count} coletillas cleaned, {assigned_count} movements assigned")
    print(f"After cleaning: {after_count} movements with coletillas remaining")
    
    conn.close()
    
    # 5. Simulate the exact print statement that should appear in logs
    print(f"Auto-clean: {cleaned_count} coletillas limpiadas, {assigned_count} movimientos asignados")
    
except Exception as e:
    print(f"ERROR: {e}")