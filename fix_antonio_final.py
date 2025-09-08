#!/usr/bin/env python3
"""
Script para crear reglas específicas para Antonio Rashad con la estructura correcta
"""

import sqlite3

def fix_antonio_final():
    print("=== SOLUCION FINAL PARA ANTONIO RASHAD HANSON ===\n")
    
    conn = sqlite3.connect('./data/dev.db')
    cursor = conn.cursor()
    
    # 1. Verificar estructura de la tabla classificationrule
    print("1. Verificando estructura de la tabla classificationrule...")
    cursor.execute("PRAGMA table_info(classificationrule)")
    columns = cursor.fetchall()
    
    print("   Columnas disponibles:")
    for col in columns:
        print(f"     {col[1]} ({col[2]})")
    
    column_names = [col[1] for col in columns]
    
    # 2. Verificar movimientos sin asignar de Antonio
    print("\n2. Movimientos de Antonio sin asignar:")
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
    for mov in unassigned_movements:
        mov_id, date, concept, amount = mov
        print(f"   ID {mov_id} ({date}): €{amount}")
        print(f"     Concepto: '{concept.strip()}'")
        print()
    
    # 3. Crear reglas con la estructura correcta (sin user_id si no existe)
    print("3. Creando reglas faltantes...")
    
    rules_to_create = [
        {
            'keyword': 'TRANSF /ANTONIO RASHAD HANSON',
            'property_id': 3,
            'category': 'Renta',
            'tenant_name': 'Antonio Rashad Hanson / Olga Ventrone'
        },
        {
            'keyword': 'TRANS INM/ ANTONIO RASHAD HANS',
            'property_id': 3,
            'category': 'Renta', 
            'tenant_name': 'Antonio Rashad Hanson / Olga Ventrone'
        }
    ]
    
    created_rules = []
    for rule in rules_to_create:
        try:
            # Verificar si la regla ya existe
            cursor.execute("SELECT id FROM classificationrule WHERE keyword = ?", (rule['keyword'],))
            existing = cursor.fetchone()
            
            if existing:
                print(f"   [INFO] Regla '{rule['keyword']}' ya existe (ID: {existing[0]})")
                continue
            
            # Crear la regla con las columnas correctas
            if 'user_id' in column_names:
                cursor.execute("""
                    INSERT INTO classificationrule 
                    (property_id, keyword, category, tenant_name, is_active, user_id)
                    VALUES (?, ?, ?, ?, 1, 1)
                """, (rule['property_id'], rule['keyword'], rule['category'], rule['tenant_name']))
            else:
                cursor.execute("""
                    INSERT INTO classificationrule 
                    (property_id, keyword, category, tenant_name, is_active)
                    VALUES (?, ?, ?, ?, 1)
                """, (rule['property_id'], rule['keyword'], rule['category'], rule['tenant_name']))
            
            rule_id = cursor.lastrowid
            created_rules.append((rule_id, rule))
            
            print(f"   [OK] Creada regla {rule_id}: '{rule['keyword']}' -> Prop {rule['property_id']}")
            
        except Exception as e:
            print(f"   [ERROR] Error creando regla '{rule['keyword']}': {e}")
    
    # Confirmar creación de reglas
    conn.commit()
    
    # 4. Aplicar reglas directamente a los movimientos problemáticos
    print("\n4. Aplicando asignaciones directas a movimientos específicos...")
    
    specific_assignments = [
        {
            'movement_id': 2807,
            'concept_contains': 'Transf /antonio Rashad Hanson',
            'property_id': 3,
            'tenant_name': 'Antonio Rashad Hanson / Olga Ventrone'
        },
        {
            'movement_id': 1667,
            'concept_contains': 'TRANS INM/ Antonio Rashad Hans',
            'property_id': 3,
            'tenant_name': 'Antonio Rashad Hanson / Olga Ventrone'
        }
    ]
    
    for assignment in specific_assignments:
        try:
            # Verificar que el movimiento existe y no está asignado
            cursor.execute("""
                SELECT id, concept, property_id 
                FROM financialmovement 
                WHERE id = ?
            """, (assignment['movement_id'],))
            
            movement = cursor.fetchone()
            if not movement:
                print(f"   [ERROR] Movimiento {assignment['movement_id']} no encontrado")
                continue
            
            mov_id, concept, current_property_id = movement
            
            if current_property_id is not None:
                print(f"   [INFO] Movimiento {mov_id} ya está asignado a propiedad {current_property_id}")
                continue
            
            # Verificar que el concepto coincide
            if assignment['concept_contains'].upper() in concept.upper():
                # Asignar el movimiento
                cursor.execute("""
                    UPDATE financialmovement 
                    SET property_id = ?, tenant_name = ?
                    WHERE id = ?
                """, (assignment['property_id'], assignment['tenant_name'], mov_id))
                
                if cursor.rowcount > 0:
                    print(f"   [OK] Movimiento {mov_id} asignado a propiedad {assignment['property_id']}")
                else:
                    print(f"   [ERROR] No se pudo asignar movimiento {mov_id}")
            else:
                print(f"   [ADVERTENCIA] Concepto del movimiento {mov_id} no coincide exactamente")
                print(f"     Esperado: '{assignment['concept_contains']}'")
                print(f"     Real: '{concept}'")
                
        except Exception as e:
            print(f"   [ERROR] Error asignando movimiento {assignment['movement_id']}: {e}")
    
    # Confirmar asignaciones
    conn.commit()
    
    # 5. Verificación final
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
        print("   [SUCCESS] Todos los movimientos de Antonio están ahora asignados!")
    else:
        print(f"   [ADVERTENCIA] Quedan {remaining_unassigned} movimientos sin asignar")
    
    # Mostrar resumen de todos los movimientos de Antonio
    print("\n6. Resumen de todos los movimientos de Antonio:")
    cursor.execute("""
        SELECT id, date, concept, amount, property_id, tenant_name
        FROM financialmovement 
        WHERE (concept LIKE '%ANTONIO RASHAD HANSON%' 
        OR concept LIKE '%antonio Rashad Hanson%'
        OR concept LIKE '%RASHAD%')
        ORDER BY date DESC
        LIMIT 10
    """)
    
    all_antonio_movements = cursor.fetchall()
    for mov in all_antonio_movements:
        mov_id, date, concept, amount, property_id, tenant_name = mov
        status = f"Prop {property_id}" if property_id else "SIN ASIGNAR"
        print(f"   ID {mov_id} ({date}): €{amount} -> {status}")
        print(f"     {concept.strip()}")
        print()
    
    conn.close()
    print("[COMPLETADO] Solución final para Antonio Rashad finalizada!")

if __name__ == "__main__":
    fix_antonio_final()