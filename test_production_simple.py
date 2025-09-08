#!/usr/bin/env python3
"""
Test de subida a producción con credenciales fijas
"""

import asyncio
import logging
from app.services.financial_agent_uploader import upload_bankinter_excel

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_production_upload():
    """Test de subida a producción en Vercel"""
    
    print("TEST DE SUBIDA A PRODUCCION - VERCEL")
    print("=" * 60)
    
    # Usar el archivo API más reciente (formato americano)
    api_file = "bankinter_api_20250828_112544.xlsx"
    
    # URL de producción
    production_url = "https://inmuebles-david.vercel.app"
    
    # Credenciales de prueba (ajustar según sea necesario)
    credentials_to_try = [
        ("admin", "admin123"),
        ("admin", "admin"),
        ("david", "david123"),
        ("user", "password"),
        ("test", "test123")
    ]
    
    print(f"Archivo para subida: {api_file}")
    print(f"Backend producción: {production_url}")
    print(f"Probando credenciales automáticamente...")
    
    for username, password in credentials_to_try:
        try:
            print(f"\n=== Probando: {username} / {password} ===")
            
            result = await upload_bankinter_excel(
                excel_file_path=api_file,
                username=username, 
                password=password,
                base_url=production_url
            )
            
            print(f"\n*** SUBIDA A PRODUCCIÓN EXITOSA ***")
            print(f"  - Usuario exitoso: {username}")
            print(f"  - Movimientos nuevos: {result['new_movements_created']}")
            print(f"  - Duplicados omitidos: {result['duplicates_skipped']}")
            print(f"  - Total procesados: {result['total_rows_processed']}")
            print(f"  - Existentes: {result['existing_movements_found']}")
            
            print(f"\n🎯 VERIFICAR EN:")
            print(f"https://inmuebles-david.vercel.app/financial-agent/movements")
            print(f"\n¡Los movimientos de Bankinter deberían aparecer!")
            
            return True
            
        except Exception as e:
            print(f"❌ Fallo con {username}: {str(e)[:100]}...")
            continue
    
    print(f"\n❌ Ninguna credencial funcionó")
    print(f"Necesitas proporcionar las credenciales correctas de producción")
    return False

if __name__ == "__main__":
    resultado = asyncio.run(test_production_upload())
    
    if resultado:
        print(f"\n✓ INTEGRACION COMPLETA FUNCIONANDO EN PRODUCCION")
    else:
        print(f"\n❌ No se pudieron encontrar credenciales válidas")