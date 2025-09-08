#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpiar las coletillas "Pulsa para ver detalle del movimiento" 
de los conceptos de movimientos bancarios existentes
"""

import sqlite3
import re

def clean_concept_text(concept):
    """Limpiar texto del concepto removiendo coletillas de Bankinter"""
    if not concept:
        return concept
    
    # Remover texto "Pulsa para ver detalle del movimiento" y variaciones
    cleaned = re.sub(r'Pulsa para ver detalle.*$', '', concept, flags=re.IGNORECASE | re.MULTILINE)
    cleaned = re.sub(r'\n.*Pulsa para ver.*$', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
    cleaned = re.sub(r'.*Pulsa para ver.*', '', cleaned, flags=re.IGNORECASE)
    
    # Limpiar saltos de línea y espacios extra
    cleaned = re.sub(r'\n+', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned if cleaned else concept

def main():
    print("=== LIMPIEZA DE COLETILLAS BANKINTER ===\n")
    
    # Conectar a la base de datos
    conn = sqlite3.connect('./data/dev.db')
    cursor = conn.cursor()
    
    print("1. Identificando movimientos con coletillas...")
    
    # Buscar movimientos que contengan la coletilla
    cursor.execute("""
        SELECT id, concept, date, amount 
        FROM financialmovement 
        WHERE concept LIKE '%Pulsa para ver%' 
        OR concept LIKE '%pulsa para ver%'
        ORDER BY date DESC
    """)
    
    movements_with_coletillas = cursor.fetchall()
    
    print(f"   Encontrados {len(movements_with_coletillas)} movimientos con coletillas")
    
    if len(movements_with_coletillas) == 0:
        print("   ✓ No se encontraron movimientos con coletillas")
        conn.close()
        return
    
    # Mostrar algunos ejemplos
    print("\n2. Ejemplos de movimientos a limpiar:")
    for i, (mov_id, concept, date, amount) in enumerate(movements_with_coletillas[:5]):
        concept_preview = concept[:80] + '...' if len(concept) > 80 else concept
        print(f"   ID {mov_id} ({date}): {concept_preview}")
        
        # Mostrar cómo quedaría limpio
        cleaned = clean_concept_text(concept)
        cleaned_preview = cleaned[:80] + '...' if len(cleaned) > 80 else cleaned
        print(f"   -> LIMPIO: {cleaned_preview}")
        print()
    
    if len(movements_with_coletillas) > 5:
        print(f"   ... y {len(movements_with_coletillas) - 5} movimientos más")
    
    # Proceder con la limpieza
    print(f"\n3. Iniciando limpieza de {len(movements_with_coletillas)} movimientos...")
    
    cleaned_count = 0
    errors = 0
    
    for mov_id, concept, date, amount in movements_with_coletillas:
        try:
            cleaned_concept = clean_concept_text(concept)
            
            # Solo actualizar si hubo cambios
            if cleaned_concept != concept:
                cursor.execute("""
                    UPDATE financialmovement 
                    SET concept = ? 
                    WHERE id = ?
                """, (cleaned_concept, mov_id))
                
                if cursor.rowcount > 0:
                    cleaned_count += 1
                    
        except Exception as e:
            print(f"   Error limpiando movimiento {mov_id}: {e}")
            errors += 1
    
    # Confirmar cambios
    conn.commit()
    
    # Verificar resultados
    print("\n4. Verificando resultados...")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM financialmovement 
        WHERE concept LIKE '%Pulsa para ver%' 
        OR concept LIKE '%pulsa para ver%'
    """)
    remaining_coletillas = cursor.fetchone()[0]
    
    print(f"   [OK] Movimientos limpiados: {cleaned_count}")
    print(f"   [OK] Errores encontrados: {errors}")
    print(f"   [OK] Coletillas restantes: {remaining_coletillas}")
    
    if remaining_coletillas == 0:
        print("   [OK] Todos los movimientos han sido limpiados exitosamente!")
    
    # Mostrar algunos ejemplos de movimientos limpiados
    print("\n5. Ejemplos de movimientos después de la limpieza:")
    cursor.execute("""
        SELECT concept, date, amount 
        FROM financialmovement 
        WHERE date >= '2025-08-01' 
        AND amount > 0
        ORDER BY date DESC 
        LIMIT 5
    """)
    
    clean_examples = cursor.fetchall()
    for concept, date, amount in clean_examples:
        concept_preview = concept[:60] + '...' if len(concept) > 60 else concept
        print(f"   {date}: €{amount} - {concept_preview}")
    
    conn.close()
    print("\n[COMPLETADO] Limpieza de coletillas finalizada!")

if __name__ == "__main__":
    main()