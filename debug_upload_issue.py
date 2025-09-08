#!/usr/bin/env python3
"""
Debug del problema de upload - revisar el archivo Excel generado
"""

import pandas as pd
import asyncio
from app.services.financial_agent_uploader import upload_bankinter_excel

async def debug_upload_issue():
    """Debug del problema de upload"""
    
    print("DEBUG - PROBLEMA DE UPLOAD")
    print("=" * 50)
    
    # 1. Verificar el contenido del archivo API generado
    api_file = "bankinter_api_20250828_112945.xlsx"
    
    try:
        print(f"\n1. ANALIZANDO ARCHIVO: {api_file}")
        df = pd.read_excel(api_file)
        
        print(f"Filas: {len(df)}")
        print(f"Columnas: {list(df.columns)}")
        print(f"\nPrimeras 5 filas:")
        print(df.head())
        
        print(f"\nTipos de datos:")
        print(df.dtypes)
        
        print(f"\nEjemplos de importes:")
        for i, row in df.head().iterrows():
            print(f"  Fila {i+1}: '{row['Importe']}' (tipo: {type(row['Importe'])})")
        
        # 2. Crear archivo de prueba simple
        print(f"\n2. CREANDO ARCHIVO DE PRUEBA SIMPLE")
        
        test_data = {
            'Fecha': ['27/08/2025', '26/08/2025', '25/08/2025'],
            'Concepto': ['TRANSFERENCIA GARCIA BAENA', 'RECIBO BANKINTER SEGUROS', 'BIZUM CARMEN RAMOS'],
            'Importe': [750.00, -770.67, -10.50]  # Números puros, sin formatear
        }
        
        df_test = pd.DataFrame(test_data)
        test_file = "test_simple_numbers.xlsx"
        df_test.to_excel(test_file, index=False)
        
        print(f"Archivo de prueba creado: {test_file}")
        print(df_test)
        
        # 3. Test de upload con archivo simple
        print(f"\n3. PROBANDO UPLOAD CON ARCHIVO SIMPLE")
        
        result = await upload_bankinter_excel(
            excel_file_path=test_file,
            username="admin",
            password="admin123",
            base_url="http://localhost:8000"
        )
        
        print(f"Resultado:")
        print(f"  - Movimientos creados: {result['new_movements_created']}")
        print(f"  - Duplicados omitidos: {result['duplicates_skipped']}")
        print(f"  - Total procesados: {result['total_rows_processed']}")
        print(f"  - Errores: {result['upload_result'].get('errors', [])[:3]}")
        
        if result['new_movements_created'] > 0:
            print(f"\n✓ ARCHIVO SIMPLE FUNCIONA")
            print("El problema está en el formato del archivo original")
        else:
            print(f"\n❌ PROBLEMA CON EL FORMATO DE NUMEROS")
            print("Revisar el procesamiento de importes")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    resultado = asyncio.run(debug_upload_issue())