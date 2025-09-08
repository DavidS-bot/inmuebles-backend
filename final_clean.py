#!/usr/bin/env python3
import sqlite3
import re

conn = sqlite3.connect('./data/dev.db')
cursor = conn.cursor()

print("Limpiando coletillas...")

# Encontrar movimientos con coletillas
cursor.execute("SELECT id, concept FROM financialmovement WHERE concept LIKE '%Pulsa para ver%'")
movements = cursor.fetchall()

print(f"Encontrados {len(movements)} movimientos con coletillas")

cleaned_count = 0
for mov_id, concept in movements:
    # Limpiar concepto
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

print(f"Limpiados {cleaned_count} movimientos")

# Aplicar clasificación
cursor.execute("SELECT id, concept FROM financialmovement WHERE property_id IS NULL LIMIT 50")
unassigned = cursor.fetchall()

cursor.execute("SELECT property_id, keyword, tenant_name FROM classificationrule WHERE is_active = 1")
rules = cursor.fetchall()

assigned_count = 0
for mov_id, concept in unassigned:
    concept_upper = concept.upper().strip()
    best_match = None
    best_score = 0
    
    for property_id, keyword, tenant_name in rules:
        if keyword.upper().strip() in concept_upper:
            score = len(keyword) / len(concept)
            if score > best_score:
                best_score = score
                best_match = (property_id, tenant_name)
    
    if best_match and best_score > 0.2:
        cursor.execute("UPDATE financialmovement SET property_id = ?, tenant_name = ? WHERE id = ?", 
                      (best_match[0], best_match[1], mov_id))
        if cursor.rowcount > 0:
            assigned_count += 1

conn.commit()

# Verificación final
cursor.execute("SELECT COUNT(*) FROM financialmovement WHERE concept LIKE '%Pulsa para ver%'")
remaining = cursor.fetchone()[0]

print(f"Asignados {assigned_count} movimientos")
print(f"Coletillas restantes: {remaining}")

conn.close()
print("Completado!")