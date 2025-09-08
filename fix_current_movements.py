#!/usr/bin/env python3
"""
Script para limpiar movimientos actuales y aplicar clasificación correctamente
"""

import sqlite3
import re

def clean_and_classify_current_movements():
    print("=== LIMPIEZA Y CLASIFICACION DE MOVIMIENTOS ACTUALES ===\n")
    
    conn = sqlite3.connect('./data/dev.db')
    cursor = conn.cursor()
    
    # 1. Limpiar todas las coletillas de movimientos recientes
    print("1. Limpiando coletillas de movimientos de septiembre 2025...")
    cursor.execute("""
        SELECT id, concept
        FROM financialmovement 
        WHERE date >= '2025-09-01' 
        AND (concept LIKE '%Pulsa para ver%' OR concept LIKE '%pulsa para ver%')
    """)
    
    movements_with_coletillas = cursor.fetchall()
    print(f"   Encontrados {len(movements_with_coletillas)} movimientos con coletillas")
    
    cleaned_count = 0
    for mov_id, concept in movements_with_coletillas:
        # Limpiar concepto
        cleaned_concept = clean_concept_text(concept)
        
        if cleaned_concept != concept:
            cursor.execute("""
                UPDATE financialmovement 
                SET concept = ? 
                WHERE id = ?
            """, (cleaned_concept, mov_id))
            
            if cursor.rowcount > 0:
                cleaned_count += 1
                print(f"   Limpiado movimiento {mov_id}: '{concept[:40]}...' -> '{cleaned_concept[:40]}...'")
    
    conn.commit()
    print(f"   [OK] {cleaned_count} movimientos limpiados")
    
    # 2. Verificar reglas de clasificación activas
    print("\n2. Verificando reglas de clasificación...")
    cursor.execute("""
        SELECT COUNT(*) FROM classificationrule WHERE is_active = 1
    """)
    active_rules_count = cursor.fetchone()[0]
    print(f"   Reglas activas: {active_rules_count}")
    
    # 3. Aplicar clasificación a movimientos de septiembre sin asignar
    print("\n3. Aplicando clasificación a movimientos de septiembre...")
    cursor.execute("""
        SELECT id, date, concept, amount 
        FROM financialmovement 
        WHERE date >= '2025-09-01' 
        AND property_id IS NULL
        ORDER BY date DESC
    """)
    
    unassigned_movements = cursor.fetchall()
    print(f"   Movimientos sin asignar: {len(unassigned_movements)}")
    
    # Obtener todas las reglas activas
    cursor.execute("""
        SELECT id, property_id, keyword, category, tenant_name 
        FROM classificationrule 
        WHERE is_active = 1
        ORDER BY property_id
    """)
    
    rules = cursor.fetchall()
    
    # Aplicar clasificación con scoring
    assignments = []
    for movement in unassigned_movements:
        mov_id, mov_date, concept, amount = movement
        concept_normalized = concept.upper().strip()
        
        # Buscar mejor coincidencia
        best_match = None
        best_score = 0
        
        for rule in rules:
            rule_id, property_id, keyword, category, tenant_name = rule
            keyword_normalized = keyword.upper().strip()
            
            if keyword_normalized in concept_normalized:
                score = len(keyword_normalized) / len(concept_normalized)
                if score > best_score:
                    best_score = score
                    best_match = {
                        'rule_id': rule_id,
                        'property_id': property_id,
                        'keyword': keyword,
                        'category': category,
                        'tenant_name': tenant_name,
                        'score': score
                    }
        
        # Si encontramos coincidencia válida
        if best_match and best_score > 0.2:
            assignments.append({
                'movement_id': mov_id,
                'match': best_match,
                'concept': concept
            })
    
    print(f"   Asignaciones encontradas: {len(assignments)}")
    
    # Aplicar asignaciones
    applied = 0
    for assignment in assignments:
        mov_id = assignment['movement_id']
        match = assignment['match']
        
        try:
            cursor.execute("""
                UPDATE financialmovement 
                SET property_id = ?, tenant_name = ?
                WHERE id = ?
            """, (match['property_id'], match['tenant_name'], mov_id))
            
            if cursor.rowcount > 0:
                applied += 1
                concept_short = assignment['concept'][:35] + '...' if len(assignment['concept']) > 35 else assignment['concept']
                print(f"   [OK] Mov {mov_id}: '{concept_short}' -> Prop {match['property_id']}")
            
        except Exception as e:
            print(f"   [ERROR] Error asignando mov {mov_id}: {e}")
    
    conn.commit()
    print(f"   [OK] {applied} movimientos asignados")
    
    # 4. Verificación final
    print("\n4. Verificación final...")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM financialmovement 
        WHERE date >= '2025-09-01' 
        AND concept LIKE '%Pulsa para ver%'
    """)
    remaining_coletillas = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM financialmovement 
        WHERE date >= '2025-09-01' 
        AND property_id IS NULL
    """)
    remaining_unassigned = cursor.fetchone()[0]
    
    print(f"   Coletillas restantes (Sept 2025): {remaining_coletillas}")
    print(f"   Movimientos sin asignar (Sept 2025): {remaining_unassigned}")
    
    # Mostrar algunos ejemplos de éxito
    print("\n5. Ejemplos de movimientos asignados en septiembre:")
    cursor.execute("""
        SELECT fm.id, fm.date, fm.concept, fm.amount, fm.property_id, fm.tenant_name
        FROM financialmovement fm
        WHERE fm.date >= '2025-09-01' 
        AND fm.property_id IS NOT NULL 
        ORDER BY fm.date DESC
        LIMIT 5
    """)
    
    assigned_examples = cursor.fetchall()
    for mov in assigned_examples:
        mov_id, date, concept, amount, property_id, tenant_name = mov
        concept_short = concept[:35] + '...' if len(concept) > 35 else concept
        tenant_short = tenant_name[:25] + '...' if tenant_name and len(tenant_name) > 25 else tenant_name or 'N/A'
        print(f"   ID {mov_id}: €{amount} -> Prop {property_id}")
        print(f"     Concepto: {concept_short}")
        print(f"     Inquilino: {tenant_short}")
        print()
    
    conn.close()
    print("[COMPLETADO] Limpieza y clasificación finalizada!")

def clean_concept_text(concept):
    """Limpiar texto del concepto removiendo coletillas de Bankinter"""
    if not concept:
        return concept
    
    # Remover texto "Pulsa para ver detalle del movimiento" y variaciones
    cleaned = re.sub(r'Pulsa para ver detalle.*$', '', concept, flags=re.IGNORECASE | re.MULTILINE)
    cleaned = re.sub(r'\\n.*Pulsa para ver.*$', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
    cleaned = re.sub(r'.*Pulsa para ver.*', '', cleaned, flags=re.IGNORECASE)
    
    # Limpiar saltos de línea y espacios extra
    cleaned = re.sub(r'\\n+', ' ', cleaned)
    cleaned = re.sub(r'\\s+', ' ', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned if cleaned else concept

if __name__ == "__main__":
    clean_and_classify_current_movements()