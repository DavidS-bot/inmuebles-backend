#!/usr/bin/env python3
"""
Script para verificar los resultados finales de la limpieza y clasificación
"""

import sqlite3
from datetime import date

def verify_results():
    print("=== VERIFICACION FINAL DE RESULTADOS ===\n")
    
    conn = sqlite3.connect('./data/dev.db')
    cursor = conn.cursor()
    
    # Estadísticas generales
    print("1. Estadísticas generales de movimientos (desde Agosto 2025):")
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN property_id IS NOT NULL THEN 1 END) as assigned,
            COUNT(CASE WHEN property_id IS NULL THEN 1 END) as unassigned,
            COUNT(CASE WHEN concept LIKE '%Pulsa para ver%' THEN 1 END) as coletillas
        FROM financialmovement 
        WHERE date >= '2025-08-01'
    """)
    
    stats = cursor.fetchone()
    total, assigned, unassigned, coletillas = stats
    
    print(f"   Total movimientos: {total}")
    print(f"   Asignados a propiedades: {assigned}")
    print(f"   Sin asignar: {unassigned}")
    print(f"   Con coletillas restantes: {coletillas}")
    print(f"   Porcentaje asignado: {(assigned/total*100):.1f}%")
    
    # Verificar movimientos recientes asignados
    print("\n2. Movimientos recién asignados (últimos 10):")
    cursor.execute("""
        SELECT id, date, concept, amount, property_id, tenant_name
        FROM financialmovement 
        WHERE property_id IS NOT NULL 
        AND date >= '2025-09-01'
        ORDER BY id DESC
        LIMIT 10
    """)
    
    recent_assigned = cursor.fetchall()
    for mov in recent_assigned:
        mov_id, date, concept, amount, property_id, tenant_name = mov
        concept_short = concept[:40] + '...' if len(concept) > 40 else concept
        tenant_short = tenant_name[:25] + '...' if tenant_name and len(tenant_name) > 25 else tenant_name or 'N/A'
        print(f"   ID {mov_id}: €{amount} -> Prop {property_id}")
        print(f"     Concepto: {concept_short}")
        print(f"     Inquilino: {tenant_short}")
        print()
    
    # Verificar que no hay coletillas
    print("3. Verificación de limpieza de coletillas:")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM financialmovement 
        WHERE concept LIKE '%Pulsa para ver%'
    """)
    
    remaining_coletillas = cursor.fetchone()[0]
    if remaining_coletillas == 0:
        print("   [OK] No se encontraron coletillas restantes")
    else:
        print(f"   [ADVERTENCIA] Quedan {remaining_coletillas} coletillas")
    
    # Distribución por propiedades
    print("\n4. Distribución de movimientos por propiedad:")
    cursor.execute("""
        SELECT 
            property_id,
            COUNT(*) as count,
            SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as ingresos,
            SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as gastos
        FROM financialmovement 
        WHERE property_id IS NOT NULL 
        AND date >= '2025-08-01'
        GROUP BY property_id
        ORDER BY property_id
    """)
    
    property_stats = cursor.fetchall()
    for prop_id, count, ingresos, gastos in property_stats:
        balance = ingresos + gastos
        print(f"   Propiedad {prop_id}: {count} movimientos")
        print(f"     Ingresos: €{ingresos:.2f} | Gastos: €{gastos:.2f} | Balance: €{balance:.2f}")
    
    conn.close()
    print("\n[COMPLETADO] Verificación finalizada!")

if __name__ == "__main__":
    verify_results()