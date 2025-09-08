#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
import re
from difflib import SequenceMatcher

def normalize_name(name):
    """Normalizar nombres para comparación"""
    if not name:
        return ""
    # Remover caracteres especiales y normalizar
    name = str(name).upper()
    name = re.sub(r'[^\w\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name)
    return name.strip()

def similarity(a, b):
    """Calcular similaridad entre dos strings"""
    return SequenceMatcher(None, normalize_name(a), normalize_name(b)).ratio()

def extract_tenant_name_from_concept(concept):
    """Extraer nombre del inquilino del concepto del movimiento"""
    if not concept:
        return ""
    
    concept = concept.upper()
    
    # Patrones comunes
    patterns = [
        r'TRANS\s*/?\s*(.+?)(?:PULSA|$)',
        r'TRANSFERENCIA\s*/?\s*(.+?)(?:PULSA|$)',
        r'/(.+?)(?:PULSA|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, concept)
        if match:
            name = match.group(1).strip()
            # Limpiar texto adicional
            name = re.sub(r'PULSA.*', '', name)
            name = re.sub(r'MARIA\s+DEL\s+', 'MARIA ', name)
            return normalize_name(name)
    
    return ""

def main():
    conn = sqlite3.connect('./data/dev.db')
    cursor = conn.cursor()
    
    print("=== REPARANDO MOVIMIENTOS SIN PROPIEDAD ASIGNADA ===\n")
    
    # Obtener contratos activos
    print("1. Obteniendo contratos activos...")
    cursor.execute('SELECT id, property_id, tenant_name, monthly_rent FROM rentalcontract WHERE is_active = 1;')
    active_contracts = cursor.fetchall()
    
    tenant_to_property = {}
    for contract in active_contracts:
        contract_id, property_id, tenant_name, rent = contract
        normalized_name = normalize_name(tenant_name)
        if normalized_name not in tenant_to_property:
            tenant_to_property[normalized_name] = []
        tenant_to_property[normalized_name].append({
            'contract_id': contract_id,
            'property_id': property_id,
            'rent': rent,
            'original_name': tenant_name
        })
    
    print(f"   Encontrados {len(tenant_to_property)} inquilinos únicos")
    
    # Obtener movimientos sin asignar
    print("2. Obteniendo movimientos sin propiedad asignada...")
    cursor.execute("""
        SELECT id, date, concept, amount 
        FROM financialmovement 
        WHERE property_id IS NULL 
        AND date >= '2025-01-01' 
        AND amount > 0 
        ORDER BY date DESC
    """)
    unassigned_movements = cursor.fetchall()
    
    print(f"   Encontrados {len(unassigned_movements)} movimientos sin asignar")
    
    # Procesar asignaciones
    print("3. Procesando asignaciones...")
    assignments = []
    
    for movement in unassigned_movements:
        mov_id, mov_date, concept, amount = movement
        extracted_name = extract_tenant_name_from_concept(concept)
        
        if not extracted_name:
            continue
        
        best_match = None
        best_similarity = 0.6  # Umbral mínimo de similaridad
        
        for tenant_normalized, properties in tenant_to_property.items():
            sim = similarity(extracted_name, tenant_normalized)
            if sim > best_similarity:
                best_similarity = sim
                best_match = properties[0]  # Tomar la primera propiedad si hay múltiples
        
        if best_match:
            # Verificar si el monto coincide aproximadamente
            rent = best_match['rent']
            if abs(amount - rent) <= 100:  # Tolerancia de €100
                assignments.append({
                    'movement_id': mov_id,
                    'property_id': best_match['property_id'],
                    'tenant_name': best_match['original_name'],
                    'concept': concept[:50] + '...' if len(concept) > 50 else concept,
                    'amount': amount,
                    'rent': rent,
                    'similarity': best_similarity
                })
    
    print(f"   Identificadas {len(assignments)} asignaciones posibles")
    
    # Mostrar asignaciones para revisión
    print("\n4. Asignaciones identificadas:")
    for i, assignment in enumerate(assignments[:20]):  # Mostrar solo las primeras 20
        print(f"   {i+1}. Movimiento {assignment['movement_id']} -> Propiedad {assignment['property_id']}")
        print(f"      Inquilino: {assignment['tenant_name']}")
        print(f"      Concepto: {assignment['concept']}")
        print(f"      Monto: €{assignment['amount']} (Renta: €{assignment['rent']}) - Similaridad: {assignment['similarity']:.2f}")
        print()
    
    if len(assignments) > 20:
        print(f"   ... y {len(assignments) - 20} asignaciones más")
    
    # Aplicar asignaciones
    print(f"\n5. Aplicando {len(assignments)} asignaciones...")
    
    updates_applied = 0
    for assignment in assignments:
        try:
            cursor.execute("""
                UPDATE financialmovement 
                SET property_id = ? 
                WHERE id = ?
            """, (assignment['property_id'], assignment['movement_id']))
            
            if cursor.rowcount > 0:
                updates_applied += 1
        
        except Exception as e:
            print(f"   Error aplicando asignación para movimiento {assignment['movement_id']}: {e}")
    
    conn.commit()
    
    # Verificar resultados
    print(f"\n6. Verificando resultados...")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM financialmovement 
        WHERE property_id IS NULL 
        AND date >= '2025-01-01' 
        AND amount > 0
    """)
    remaining_unassigned = cursor.fetchone()[0]
    
    print(f"   Asignaciones aplicadas: {updates_applied}")
    print(f"   Movimientos sin asignar restantes: {remaining_unassigned}")
    print(f"   Movimientos reparados: {len(unassigned_movements) - remaining_unassigned}")
    
    conn.close()
    print("\n[COMPLETADO] Reparación de movimientos finalizada!")

if __name__ == "__main__":
    main()