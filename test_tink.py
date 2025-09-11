#!/usr/bin/env python3
"""
Test simple para verificar Tink Open Banking
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

async def test_tink_client():
    """Test básico del cliente Tink"""
    try:
        from app.openbanking.clients.tink_client import tink_client
        
        print("Testing Tink Client...")
        
        # Test: Obtener proveedores (requiere credenciales válidas)
        try:
            providers = await tink_client.get_providers("ES")
            print(f"[OK] Providers fetched: {len(providers)} banks available")
            
            # Mostrar algunos bancos españoles
            spanish_banks = [p for p in providers if any(
                keyword in p.get('displayName', '').upper() 
                for keyword in ['BBVA', 'SANTANDER', 'CAIXABANK', 'BANKINTER']
            )]
            
            if spanish_banks:
                print("Spanish banks found:")
                for bank in spanish_banks[:5]:
                    print(f"   - {bank.get('displayName')} ({bank.get('name')})")
            
        except Exception as e:
            print(f"[ERROR] Provider fetch failed: {e}")
            print("This is expected if Tink credentials are not configured")
            
    except ImportError as e:
        print(f"[ERROR] Failed to import Tink client: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

def test_environment_variables():
    """Test de variables de entorno para Tink"""
    print("\nTesting Tink Environment Variables...")
    
    # Variables requeridas para Tink
    required_vars = ['TINK_CLIENT_ID', 'TINK_CLIENT_SECRET']
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"[WARNING] Missing environment variables: {missing_vars}")
        print("[INFO] Add them to .env file after registering with Tink")
    else:
        print("[OK] All required Tink environment variables present")

def test_api_router():
    """Test del router de Tink"""
    try:
        from app.routers.openbanking_tink import router
        
        print("\nTesting Tink API Router...")
        
        # Verificar que el router tiene las rutas esperadas
        routes = [route.path for route in router.routes]
        expected_routes = [
            '/providers', '/connections', '/connections/{connection_id}/sync', 
            '/connections/{connection_id}'
        ]
        
        missing_routes = [route for route in expected_routes if route not in routes]
        if missing_routes:
            print(f"[ERROR] Missing API routes: {missing_routes}")
        else:
            print(f"[OK] All Tink API routes present: {len(routes)} total routes")
            
    except Exception as e:
        print(f"[ERROR] Tink API router test failed: {e}")

async def main():
    """Función principal de test"""
    print("Tink Open Banking Test")
    print("=" * 40)
    
    # Tests síncronos
    test_environment_variables()
    test_api_router()
    
    # Tests asíncronos
    await test_tink_client()
    
    print("\n" + "=" * 40)
    print("[OK] Test completed!")
    print("\nNext steps:")
    print("1. Register at https://tink.com/get-started/")
    print("2. Get Client ID and Client Secret")
    print("3. Add credentials to .env file:")
    print("   TINK_CLIENT_ID=your-client-id")
    print("   TINK_CLIENT_SECRET=your-client-secret")
    print("4. Test the connection")

if __name__ == "__main__":
    asyncio.run(main())