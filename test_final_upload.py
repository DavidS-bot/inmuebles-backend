#!/usr/bin/env python3
"""
Test final de subida con archivo API generado
"""

import asyncio
from app.services.financial_agent_uploader import upload_bankinter_excel

async def test_final_upload():
    """Test de subida con archivo API más reciente"""
    
    print("TEST FINAL - SUBIDA CON ARCHIVO API")
    print("=" * 50)
    
    # Usar el archivo API más reciente generado
    api_file = "bankinter_api_20250828_112544.xlsx"
    
    try:
        print(f"Archivo para subida: {api_file}")
        print("Backend: http://localhost:8000")
        print("Usuario: admin")
        
        result = await upload_bankinter_excel(
            excel_file_path=api_file,
            username="admin", 
            password="admin123",
            base_url="http://localhost:8000"
        )
        
        print("\nSUBIDA EXITOSA:")
        print(f"  - Movimientos nuevos: {result['new_movements_created']}")
        print(f"  - Duplicados omitidos: {result['duplicates_skipped']}")
        print(f"  - Total procesados: {result['total_rows_processed']}")
        print(f"  - Existentes encontrados: {result['existing_movements_found']}")
        
        if result['new_movements_created'] > 0:
            print("\n*** EXITO TOTAL ***")
            print("Los movimientos de Bankinter se subieron correctamente al agente financiero!")
            print("La integracion automatica esta funcionando!")
            return True
        else:
            print("\nNo se crearon movimientos nuevos (posibles duplicados o errores de formato)")
            return False
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    resultado = asyncio.run(test_final_upload())
    
    if resultado:
        print(f"\nFLUJO COMPLETO FUNCIONANDO")
    else:
        print(f"\nRevisar configuracion")