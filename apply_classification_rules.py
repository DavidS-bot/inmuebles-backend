#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para aplicar reglas de clasificación automáticamente a movimientos sin asignar
"""

import sqlite3
import re

def apply_classification_rules():
    """Aplicar reglas de clasificación a movimientos sin asignar"""
    
    conn = sqlite3.connect('./data/dev.db')
    cursor = conn.cursor()
    
    print("=== APLICACIÓN AUTOMÁTICA DE REGLAS DE CLASIFICACIÓN ===\n")
    
    # Obtener todas las reglas activas
    print("1. Cargando reglas de clasificación activas...")
    cursor.execute("""
        SELECT id, property_id, keyword, category, tenant_name 
        FROM classificationrule 
        WHERE is_active = 1
        ORDER BY property_id
    """)
    
    rules = cursor.fetchall()
    print(f"   Encontradas {len(rules)} reglas activas")
    
    # Mostrar las reglas
    for rule in rules:
        rule_id, property_id, keyword, category, tenant_name = rule
        tenant_info = f" - {tenant_name}" if tenant_name else ""
        print(f"   Regla {rule_id}: '{keyword}' -> Propiedad {property_id} ({category}){tenant_info}")
    
    # Obtener movimientos sin asignar
    print("\n2. Buscando movimientos sin asignar...")
    cursor.execute("""
        SELECT id, date, concept, amount 
        FROM financialmovement 
        WHERE property_id IS NULL 
        AND date >= '2025-08-01'
        ORDER BY date DESC
    """)
    
    unassigned_movements = cursor.fetchall()
    print(f"   Encontrados {len(unassigned_movements)} movimientos sin asignar")
    
    # Aplicar reglas
    print("\n3. Aplicando reglas de clasificación...")
    
    assignments = []
    
    for movement in unassigned_movements:
        mov_id, mov_date, concept, amount = movement
        
        # Normalizar concepto para comparación
        concept_normalized = concept.upper().strip()
        
        # Buscar coincidencias con las reglas
        best_match = None
        best_score = 0
        
        for rule in rules:
            rule_id, property_id, keyword, category, tenant_name = rule
            keyword_normalized = keyword.upper().strip()
            
            # Verificar coincidencia exacta o parcial
            if keyword_normalized in concept_normalized:
                # Calcular score basado en la longitud de la coincidencia
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
        
        # Si encontramos una coincidencia válida, guardar la asignación
        if best_match and best_score > 0.2:  # Umbral mínimo de coincidencia
            assignments.append({
                'movement_id': mov_id,
                'movement_date': mov_date,
                'concept': concept,
                'amount': amount,
                'match': best_match
            })
    
    print(f"   Identificadas {len(assignments)} asignaciones automáticas")
    
    # Mostrar asignaciones propuestas
    print("\n4. Asignaciones propuestas:")
    for i, assignment in enumerate(assignments[:10]):  # Mostrar primeras 10
        mov_id = assignment['movement_id']
        concept = assignment['concept'][:40] + '...' if len(assignment['concept']) > 40 else assignment['concept']
        match = assignment['match']
        
        print(f"   {i+1}. Movimiento {mov_id}: {concept}")
        print(f"      -> Propiedad {match['property_id']} ({match['category']})")
        print(f"      -> Inquilino: {match['tenant_name'] or 'N/A'}")
        print(f"      -> Coincidencia: {match['score']:.2f}")
        print()
    
    if len(assignments) > 10:
        print(f"   ... y {len(assignments) - 10} asignaciones más")
    
    # Aplicar las asignaciones
    print(f"\n5. Aplicando {len(assignments)} asignaciones...")
    
    applied = 0
    errors = 0
    
    for assignment in assignments:
        try:
            mov_id = assignment['movement_id']
            property_id = assignment['match']['property_id']
            tenant_name = assignment['match']['tenant_name']
            
            # Actualizar el movimiento
            cursor.execute("""
                UPDATE financialmovement 
                SET property_id = ?, tenant_name = ?
                WHERE id = ?
            """, (property_id, tenant_name, mov_id))
            
            if cursor.rowcount > 0:
                applied += 1
            
        except Exception as e:
            print(f"   Error aplicando asignación para movimiento {mov_id}: {e}")
            errors += 1
    
    # Confirmar cambios
    conn.commit()
    
    # Verificar resultados
    print("\n6. Verificando resultados...")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM financialmovement 
        WHERE property_id IS NULL 
        AND date >= '2025-08-01'
    """)
    remaining_unassigned = cursor.fetchone()[0]
    
    print(f"   Asignaciones aplicadas: {applied}")
    print(f"   Errores: {errors}")
    print(f"   Movimientos sin asignar restantes: {remaining_unassigned}")
    
    # Mostrar algunos ejemplos de movimientos asignados
    print("\n7. Ejemplos de movimientos recién asignados:")
    cursor.execute("""
        SELECT fm.id, fm.date, fm.concept, fm.amount, fm.property_id, fm.tenant_name
        FROM financialmovement fm
        WHERE fm.property_id IS NOT NULL 
        AND fm.date >= '2025-09-01'
        ORDER BY fm.id DESC
        LIMIT 5
    """)
    
    assigned_examples = cursor.fetchall()
    for mov in assigned_examples:
        mov_id, date, concept, amount, property_id, tenant_name = mov
        concept_short = concept[:35] + '...' if len(concept) > 35 else concept
        tenant_short = tenant_name[:20] + '...' if tenant_name and len(tenant_name) > 20 else tenant_name
        print(f"   ID {mov_id}: €{amount} -> Prop {property_id} - {tenant_short}")
        print(f"     {concept_short}")
    
    conn.close()
    print("\n[COMPLETADO] Aplicación de reglas finalizada!")

if __name__ == "__main__":
    apply_classification_rules()