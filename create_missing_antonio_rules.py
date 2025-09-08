#!/usr/bin/env python3
"""
Script para crear las reglas faltantes para Antonio Rashad Hanson
"""

import sqlite3

def create_missing_rules():
    print("=== CREACION DE REGLAS FALTANTES PARA ANTONIO ===\n")
    
    conn = sqlite3.connect('./data/dev.db')
    cursor = conn.cursor()
    
    # Verificar movimientos sin asignar de Antonio
    print("1. Verificando movimientos de Antonio sin asignar...")
    cursor.execute("""
        SELECT id, date, concept, amount 
        FROM financialmovement 
        WHERE (concept LIKE '%ANTONIO RASHAD HANSON%' 
        OR concept LIKE '%antonio Rashad Hanson%'
        OR concept LIKE '%RASHAD%')
        AND property_id IS NULL
        ORDER BY date DESC
    """)
    
    unassigned_movements = cursor.fetchall()
    print(f"   Encontrados {len(unassigned_movements)} movimientos sin asignar:")
    
    for mov in unassigned_movements:
        mov_id, date, concept, amount = mov
        print(f"   ID {mov_id} ({date}): €{amount}")
        print(f"     Concepto: '{concept}'")
        print()
    
    # Crear reglas para los patrones faltantes
    print("2. Creando reglas para patrones faltantes...")
    
    # Regla para "Transf /antonio Rashad Hanson" (minúsculas)
    rule1_keyword = "TRANSF /ANTONIO RASHAD HANSON"
    
    # Regla para "TRANS INM/ ANTONIO RASHAD HANS" (nombre truncado)
    rule2_keyword = "TRANS INM/ ANTONIO RASHAD HANS"
    
    # Verificar si ya existen estas reglas
    cursor.execute("""
        SELECT keyword FROM classificationrule 
        WHERE keyword IN (?, ?)
    """, (rule1_keyword, rule2_keyword))
    
    existing_rules = [row[0] for row in cursor.fetchall()]
    
    rules_to_create = []
    
    if rule1_keyword not in existing_rules:
        rules_to_create.append({
            'keyword': rule1_keyword, 
            'pattern': 'Transf /antonio Rashad Hanson',
            'property_id': 3,
            'category': 'Renta',
            'tenant_name': 'Antonio Rashad Hanson / Olga Ventrone'
        })
    
    if rule2_keyword not in existing_rules:
        rules_to_create.append({
            'keyword': rule2_keyword,
            'pattern': 'TRANS INM/ Antonio Rashad Hans',
            'property_id': 3, 
            'category': 'Renta',
            'tenant_name': 'Antonio Rashad Hanson / Olga Ventrone'
        })
    
    print(f"   Reglas a crear: {len(rules_to_create)}")
    
    # Crear las reglas
    created_rules = []
    for rule in rules_to_create:
        try:
            cursor.execute("""
                INSERT INTO classificationrule 
                (property_id, keyword, category, tenant_name, is_active, user_id)
                VALUES (?, ?, ?, ?, 1, 1)
            """, (rule['property_id'], rule['keyword'], rule['category'], rule['tenant_name']))
            
            rule_id = cursor.lastrowid
            created_rules.append(rule_id)
            
            print(f"   [OK] Creada regla {rule_id}: '{rule['keyword']}' -> Prop {rule['property_id']}")
            
        except Exception as e:
            print(f"   [ERROR] Error creando regla '{rule['keyword']}': {e}")
    
    # Confirmar creación de reglas
    conn.commit()
    
    print(f"\n3. Reglas creadas exitosamente: {len(created_rules)}")
    
    # Ahora aplicar las reglas a los movimientos sin asignar
    if created_rules:
        print("\n4. Aplicando nuevas reglas a movimientos sin asignar...")
        
        for mov in unassigned_movements:
            mov_id, date, concept, amount = mov
            concept_normalized = concept.upper().strip()
            
            # Probar coincidencias con las nuevas reglas
            for rule in rules_to_create:
                keyword_normalized = rule['keyword'].upper().strip()
                
                if keyword_normalized in concept_normalized:
                    print(f"   Asignando movimiento {mov_id} usando regla '{rule['keyword']}'")
                    
                    try:
                        cursor.execute("""
                            UPDATE financialmovement 
                            SET property_id = ?, tenant_name = ?
                            WHERE id = ?
                        """, (rule['property_id'], rule['tenant_name'], mov_id))
                        
                        if cursor.rowcount > 0:
                            print(f"   [OK] Movimiento {mov_id} asignado a propiedad {rule['property_id']}")
                        else:
                            print(f"   [ERROR] No se pudo asignar movimiento {mov_id}")
                            
                    except Exception as e:
                        print(f"   [ERROR] Error asignando movimiento {mov_id}: {e}")
                    
                    break  # Solo aplicar una regla por movimiento
    
    # Confirmar asignaciones
    conn.commit()
    
    # Verificación final
    print("\n5. Verificación final...")
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
        
        # Mostrar cuáles quedan
        cursor.execute("""
            SELECT id, concept 
            FROM financialmovement 
            WHERE (concept LIKE '%ANTONIO RASHAD HANSON%' 
            OR concept LIKE '%antonio Rashad Hanson%'
            OR concept LIKE '%RASHAD%')
            AND property_id IS NULL
        """)
        
        still_unassigned = cursor.fetchall()
        for mov_id, concept in still_unassigned:
            print(f"     ID {mov_id}: '{concept}'")
    
    conn.close()
    print("\n[COMPLETADO] Creación de reglas faltantes finalizada!")

if __name__ == "__main__":
    create_missing_rules()