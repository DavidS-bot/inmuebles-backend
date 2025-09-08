#!/usr/bin/env python3
import sqlite3
import re

conn = sqlite3.connect('./data/dev.db')
cursor = conn.cursor()

print('=== LIMPIEZA MANUAL PASO A PASO ===')

# Obtener un movimiento específico para probar
cursor.execute('''
    SELECT id, concept FROM financialmovement 
    WHERE id = 2796 
''')

mov_id, concept = cursor.fetchone()
print(f'ANTES - ID {mov_id}:')
print(f'  Concepto original: "{concept}"')
print(f'  Longitud: {len(concept)}')
print(f'  Contiene "Pulsa": {"Pulsa para ver" in concept}')
print(f'  Repr: {repr(concept)}')

# Aplicar limpieza paso a paso
print('\n=== APLICANDO LIMPIEZA ===')

original = concept

# Paso 1: Regex principal
cleaned = re.sub(r'Pulsa para ver detalle.*$', '', concept, flags=re.IGNORECASE | re.MULTILINE)
print(f'Paso 1 - Después regex principal: "{cleaned}"')

# Paso 2: Regex con salto de línea
cleaned = re.sub(r'\n.*Pulsa para ver.*$', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
print(f'Paso 2 - Después regex salto línea: "{cleaned}"')

# Paso 3: Regex general
cleaned = re.sub(r'.*Pulsa para ver.*', '', cleaned, flags=re.IGNORECASE)
print(f'Paso 3 - Después regex general: "{cleaned}"')

# Paso 4: Limpiar saltos de línea
cleaned = re.sub(r'\n+', ' ', cleaned)
print(f'Paso 4 - Después limpiar saltos: "{cleaned}"')

# Paso 5: Limpiar espacios
cleaned = re.sub(r'\s+', ' ', cleaned)
print(f'Paso 5 - Después limpiar espacios: "{cleaned}"')

# Paso 6: Strip
cleaned = cleaned.strip()
print(f'Paso 6 - Después strip: "{cleaned}"')

print('\n=== RESULTADO ===')
print(f'Original: "{original}"')
print(f'Limpiado: "{cleaned}"')
print(f'Diferente: {cleaned != original}')
print(f'Limpiado válido: {bool(cleaned)}')

if cleaned != original and cleaned:
    print('\n=== APLICANDO UPDATE ===')
    cursor.execute('UPDATE financialmovement SET concept = ? WHERE id = ?', (cleaned, mov_id))
    print(f'Rows affected: {cursor.rowcount}')
    conn.commit()
    
    # Verificar cambio
    cursor.execute('SELECT concept FROM financialmovement WHERE id = ?', (mov_id,))
    new_concept = cursor.fetchone()[0]
    print(f'Nuevo concepto en DB: "{new_concept}"')
else:
    print('No se necesita actualización')

conn.close()