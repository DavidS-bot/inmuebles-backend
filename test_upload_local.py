#!/usr/bin/env python3
"""
Test de subida a backend local
"""

import asyncio
import logging
from app.services.financial_agent_uploader import upload_bankinter_excel

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_upload_local():
    """Test de subida al backend local"""
    
    print("TEST DE SUBIDA AL BACKEND LOCAL")
    print("=" * 50)
    
    # Usar el archivo corregido más reciente
    excel_file = "bankinter_corregido_20250828_110803.xlsx"
    
    # Credenciales por defecto del backend local
    agent_username = "admin"
    agent_password = "admin123"
    
    # URL del backend local
    local_url = "http://localhost:8000"
    
    try:
        print(f"Subiendo archivo: {excel_file}")
        print(f"Usuario: {agent_username}")
        print(f"Backend: {local_url}")
        
        result = await upload_bankinter_excel(
            excel_file_path=excel_file,
            username=agent_username,
            password=agent_password,
            base_url=local_url
        )
        
        print("\n✓ SUBIDA EXITOSA:")
        print(f"  - Movimientos nuevos creados: {result['new_movements_created']}")
        print(f"  - Duplicados omitidos: {result['duplicates_skipped']}")
        print(f"  - Total filas procesadas: {result['total_rows_processed']}")
        print(f"  - Movimientos existentes: {result['existing_movements_found']}")
        print(f"  - Timestamp: {result['upload_timestamp']}")
        
        return True
        
    except Exception as e:
        print(f"\nERROR en subida: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    resultado = asyncio.run(test_upload_local())
    
    if resultado:
        print(f"\nPROCESO COMPLETADO EXITOSAMENTE")
    else:
        print(f"\nPROCESO COMPLETADO CON ERRORES")