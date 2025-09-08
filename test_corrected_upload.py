#!/usr/bin/env python3
"""
Test de subida con archivo corregido
"""

import asyncio
from app.services.financial_agent_uploader import upload_bankinter_excel

async def test_corrected_upload():
    """Test con archivo de números puros"""
    
    print("TEST - ARCHIVO CON NUMEROS PUROS")
    print("=" * 50)
    
    # Usar el archivo corregido
    corrected_file = "bankinter_api_corregido_numeros.xlsx"
    
    try:
        print(f"Archivo: {corrected_file}")
        print("Backend: http://localhost:8000")
        
        result = await upload_bankinter_excel(
            excel_file_path=corrected_file,
            username="admin",
            password="admin123", 
            base_url="http://localhost:8000"
        )
        
        print(f"RESULTADO:")
        print(f"  - Movimientos creados: {result['new_movements_created']}")
        print(f"  - Duplicados omitidos: {result['duplicates_skipped']}")
        print(f"  - Total procesados: {result['total_rows_processed']}")
        print(f"  - Errores: {result['upload_result'].get('errors', [])[:3]}")
        
        if result['new_movements_created'] > 0:
            print(f"\nEXITO - El archivo con numeros puros funciona!")
            print(f"Ahora puedes subirlo manualmente a Vercel")
        else:
            print(f"\nTodavia hay un problema con el formato")
            
        return result['new_movements_created'] > 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    resultado = asyncio.run(test_corrected_upload())
    
    if resultado:
        print(f"\nEL ARCHIVO CORREGIDO FUNCIONA")
        print("bankinter_api_corregido_numeros.xlsx")
        print("Subelo a https://inmuebles-david.vercel.app/financial-agent/movements")
    else:
        print(f"\nTodavia hay problemas con el formato")