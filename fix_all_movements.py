#!/usr/bin/env python3
"""
Script corregido para limpiar TODOS los movimientos con coletillas
"""

import sqlite3
import re

def clean_all_movements():
    print("=== LIMPIEZA MASIVA DE MOVIMIENTOS ===\n")
    
    conn = sqlite3.connect('./data/dev.db')
    cursor = conn.cursor()
    
    # 1. Encontrar todos los movimientos con coletillas
    print("1. Buscando movimientos con coletillas...")
    cursor.execute("""
        SELECT id, concept
        FROM financialmovement 
        WHERE concept LIKE '%Pulsa para ver%'
    """)
    
    movements_with_coletillas = cursor.fetchall()
    print(f"   Encontrados {len(movements_with_coletillas)} movimientos con coletillas")
    
    if not movements_with_coletillas:
        print("   No hay movimientos con coletillas!")
        return
    
    cleaned_count = 0
    
    # 2. Limpiar cada movimiento
    print("\n2. Limpiando movimientos...")
    for mov_id, concept in movements_with_coletillas:
        # Aplicar limpieza CORRECTA (sin escapes dobles)
        cleaned_concept = re.sub(r'Pulsa para ver detalle.*$', '', concept, flags=re.IGNORECASE | re.MULTILINE)
        cleaned_concept = re.sub(r'\n.*Pulsa para ver.*$', '', cleaned_concept, flags=re.IGNORECASE | re.MULTILINE)
        cleaned_concept = re.sub(r'.*Pulsa para ver.*', '', cleaned_concept, flags=re.IGNORECASE)
        cleaned_concept = re.sub(r'\n+', ' ', cleaned_concept)
        cleaned_concept = re.sub(r'\s+', ' ', cleaned_concept)
        cleaned_concept = cleaned_concept.strip()
        
        if cleaned_concept != concept and cleaned_concept:
            cursor.execute("UPDATE financialmovement SET concept = ? WHERE id = ?", (cleaned_concept, mov_id))
            if cursor.rowcount > 0:
                cleaned_count += 1
                original_short = concept[:30] + '...' if len(concept) > 30 else concept
                cleaned_short = cleaned_concept[:30] + '...' if len(cleaned_concept) > 30 else cleaned_concept
                print(f"   [OK] Mov {mov_id}: '{original_short}' -> '{cleaned_short}'")
    
    # 3. Aplicar clasificación automática
    print(f"\n3. Aplicando clasificación automática...")
    cursor.execute("""
        SELECT id, concept FROM financialmovement 
        WHERE property_id IS NULL
        ORDER BY date DESC
        LIMIT 100
    """)
    
    unassigned_movements = cursor.fetchall()
    
    # Obtener reglas activas
    cursor.execute("""
        SELECT id, property_id, keyword, category, tenant_name 
        FROM classificationrule 
        WHERE is_active = 1
    """)
    
    rules = cursor.fetchall()
    assigned_count = 0
    
    # Aplicar clasificación
    for mov_id, concept in unassigned_movements:
        concept_normalized = concept.upper().strip()
        best_match = None
        best_score = 0
        
        for rule in rules:
            rule_id, property_id, keyword, category, tenant_name = rule
            keyword_normalized = keyword.upper().strip()
            
            if keyword_normalized in concept_normalized:
                score = len(keyword_normalized) / len(concept_normalized)
                if score > best_score:
                    best_score = score
                    best_match = {'property_id': property_id, 'tenant_name': tenant_name}
        
        # Aplicar si tenemos buena coincidencia
        if best_match and best_score > 0.2:
            cursor.execute("""
                UPDATE financialmovement 
                SET property_id = ?, tenant_name = ?
                WHERE id = ?
            """, (best_match['property_id'], best_match['tenant_name'], mov_id))
            
            if cursor.rowcount > 0:
                assigned_count += 1
                concept_short = concept[:35] + '...' if len(concept) > 35 else concept
                print(f"   [OK] Mov {mov_id}: '{concept_short}' -> Prop {best_match['property_id']}")
    
    conn.commit()
    
    # 4. Verificación final
    print(f"\n4. Verificación final...")
    cursor.execute("SELECT COUNT(*) FROM financialmovement WHERE concept LIKE '%Pulsa para ver%'")
    remaining_coletillas = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM financialmovement WHERE property_id IS NULL")
    remaining_unassigned = cursor.fetchone()[0]
    
    print(f"   [RESULTADO] {cleaned_count} coletillas limpiadas")
    print(f"   [RESULTADO] {assigned_count} movimientos asignados")
    print(f"   [RESULTADO] {remaining_coletillas} coletillas restantes")
    print(f"   [RESULTADO] {remaining_unassigned} movimientos sin asignar")
    
    conn.close()
    print(f"\n[COMPLETADO] Limpieza masiva finalizada!")

if __name__ == "__main__":
    clean_all_movements()