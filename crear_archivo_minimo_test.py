#!/usr/bin/env python3
"""
Crear un archivo mínimo de prueba para verificar que funciona la subida
"""

import pandas as pd

def crear_archivo_test():
    """Crear archivo mínimo de prueba"""
    
    print("CREANDO ARCHIVO DE PRUEBA MINIMO")
    print("=" * 50)
    
    # Crear solo 3 movimientos de prueba muy simples
    test_data = {
        'Fecha': ['01/01/2025', '02/01/2025', '03/01/2025'],
        'Concepto': ['PRUEBA INGRESO', 'PRUEBA GASTO', 'OTRA PRUEBA'],
        'Importe': [1000.00, -500.00, 250.00]
    }
    
    df = pd.DataFrame(test_data)
    
    print("Datos de prueba:")
    print(df)
    
    # Guardar archivos en múltiples formatos
    files_created = []
    
    # Excel
    excel_file = "test_minimo.xlsx"
    df.to_excel(excel_file, index=False)
    files_created.append(excel_file)
    
    # CSV
    csv_file = "test_minimo.csv"
    df.to_csv(csv_file, index=False)
    files_created.append(csv_file)
    
    # CSV con separador tab (más compatible)
    csv_tab_file = "test_minimo_tab.csv"
    df.to_csv(csv_tab_file, index=False, sep='\t')
    files_created.append(csv_tab_file)
    
    print(f"\nArchivos creados:")
    for file in files_created:
        print(f"  - {file}")
    
    print(f"\nINSTRUCCIONES:")
    print("1. Ve a: https://inmuebles-david.vercel.app/financial-agent/movements")
    print("2. ANTES de subir archivo:")
    print("   - Crea UNA propiedad (ej: 'Mi Casa')")
    print("   - Asegurate que estes logueado")
    print("3. Sube el archivo: test_minimo.xlsx")
    print("4. Deberian aparecer 3 movimientos:")
    print("   - PRUEBA INGRESO: 1000.00€")
    print("   - PRUEBA GASTO: -500.00€") 
    print("   - OTRA PRUEBA: 250.00€")
    print("5. Si aparecen, el sistema funciona")
    print("6. Si NO aparecen, hay un problema de configuracion")

if __name__ == "__main__":
    crear_archivo_test()