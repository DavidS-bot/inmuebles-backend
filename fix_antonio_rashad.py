#!/usr/bin/env python3
"""
Script para investigar y corregir el problema específico con Antonio Rashad Hanson
"""

import sqlite3
import re

def fix_antonio_rashad():
    print("=== INVESTIGACION Y CORRECCION ANTONIO RASHAD HANSON ===\n")
    
    conn = sqlite3.connect('./data/dev.db')
    cursor = conn.cursor()
    
    # 1. Buscar movimientos de Antonio Rashad Hanson
    print("1. Buscando movimientos de Antonio Rashad Hanson...")
    cursor.execute("""
        SELECT id, date, concept, amount, property_id, tenant_name 
        FROM financialmovement 
        WHERE concept LIKE '%ANTONIO RASHAD HANSON%' 
        OR concept LIKE '%antonio Rashad Hanson%'
        OR concept LIKE '%RASHAD%'
        ORDER BY date DESC
    """)
    
    antonio_movements = cursor.fetchall()
    print(f"   Encontrados {len(antonio_movements)} movimientos relacionados:")
    
    for mov in antonio_movements:
        mov_id, date, concept, amount, property_id, tenant_name = mov
        status = f"ASIGNADO a Prop {property_id}" if property_id else "SIN ASIGNAR"
        print(f"   ID {mov_id} ({date}): €{amount} - {status}")
        print(f"     Concepto: {concept}")
        print(f"     Inquilino: {tenant_name or 'N/A'}")
        print()
    
    # 2. Verificar reglas existentes para Antonio
    print("2. Verificando reglas de clasificación para Antonio...")
    cursor.execute("""
        SELECT id, property_id, keyword, category, tenant_name, is_active
        FROM classificationrule 
        WHERE keyword LIKE '%ANTONIO%' 
        OR keyword LIKE '%RASHAD%'
        OR tenant_name LIKE '%ANTONIO%'
        ORDER BY id
    """)
    
    antonio_rules = cursor.fetchall()
    print(f"   Encontradas {len(antonio_rules)} reglas para Antonio:")
    
    for rule in antonio_rules:
        rule_id, property_id, keyword, category, tenant_name, is_active = rule
        status = "ACTIVA" if is_active else "INACTIVA"
        print(f"   Regla {rule_id}: '{keyword}' -> Prop {property_id} ({category}) - {status}")
        print(f"     Inquilino: {tenant_name}")
        print()
    
    # 3. Probar coincidencias manualmente
    print("3. Probando coincidencias de reglas...")
    unassigned_antonio = [mov for mov in antonio_movements if not mov[4]]  # property_id is None
    
    if unassigned_antonio:
        print(f"   Movimientos sin asignar: {len(unassigned_antonio)}")
        
        for mov in unassigned_antonio:
            mov_id, date, concept, amount, property_id, tenant_name = mov
            concept_normalized = concept.upper().strip()
            print(f"   \nAnalizando movimiento {mov_id}:")
            print(f"     Concepto normalizado: '{concept_normalized}'")
            
            # Probar cada regla
            best_match = None
            best_score = 0
            
            for rule in antonio_rules:
                if not rule[5]:  # Skip inactive rules
                    continue
                    
                rule_id, prop_id, keyword, category, rule_tenant, is_active = rule
                keyword_normalized = keyword.upper().strip()
                
                if keyword_normalized in concept_normalized:
                    score = len(keyword_normalized) / len(concept_normalized)
                    print(f"     COINCIDENCIA con regla {rule_id}: '{keyword}' (score: {score:.2f})")
                    
                    if score > best_score:
                        best_score = score
                        best_match = {
                            'rule_id': rule_id,
                            'property_id': prop_id,
                            'keyword': keyword,
                            'category': category,
                            'tenant_name': rule_tenant,
                            'score': score
                        }
                else:
                    print(f"     No coincide con regla {rule_id}: '{keyword}'")
            
            if best_match and best_score > 0.2:
                print(f"     MEJOR COINCIDENCIA: Regla {best_match['rule_id']} -> Prop {best_match['property_id']}")
                
                # Aplicar la asignación
                try:
                    cursor.execute("""
                        UPDATE financialmovement 
                        SET property_id = ?, tenant_name = ?
                        WHERE id = ?
                    """, (best_match['property_id'], best_match['tenant_name'], mov_id))
                    
                    if cursor.rowcount > 0:
                        print(f"     [OK] Movimiento {mov_id} asignado a propiedad {best_match['property_id']}")
                    else:
                        print(f"     [ERROR] No se pudo asignar movimiento {mov_id}")
                        
                except Exception as e:
                    print(f"     [ERROR] Error asignando movimiento {mov_id}: {e}")
            else:
                print(f"     [ADVERTENCIA] No se encontró coincidencia válida para movimiento {mov_id}")
    else:
        print("   [OK] Todos los movimientos de Antonio ya están asignados")
    
    # Confirmar cambios
    conn.commit()
    
    # 4. Verificación final
    print("\n4. Verificación final...")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM financialmovement 
        WHERE (concept LIKE '%ANTONIO RASHAD HANSON%' 
        OR concept LIKE '%antonio Rashad Hanson%'
        OR concept LIKE '%RASHAD%')
        AND property_id IS NULL
    """)
    
    remaining_unassigned = cursor.fetchone()[0]
    print(f"   Movimientos de Antonio sin asignar: {remaining_unassigned}")
    
    if remaining_unassigned == 0:
        print("   [OK] Todos los movimientos de Antonio están ahora asignados")
    else:
        print(f"   [ADVERTENCIA] Quedan {remaining_unassigned} movimientos sin asignar")
    
    conn.close()
    print("\n[COMPLETADO] Corrección de Antonio Rashad finalizada!")

if __name__ == "__main__":
    fix_antonio_rashad()