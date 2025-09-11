#!/usr/bin/env python3
"""
Simple test script para verificar la implementación de Open Banking
"""

import asyncio
import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

async def test_nordigen_client():
    """Test básico del cliente Nordigen"""
    try:
        from app.openbanking.clients.nordigen_client import nordigen_client
        
        print("Testing Nordigen Client...")
        
        # Test: Obtener instituciones (requiere credenciales válidas)
        try:
            institutions = await nordigen_client.get_institutions("ES")
            print(f"[OK] Institutions fetched: {len(institutions)} banks available")
            
            # Mostrar algunos bancos principales
            main_banks = [inst for inst in institutions if any(
                keyword in inst['name'].upper() 
                for keyword in ['BBVA', 'SANTANDER', 'CAIXABANK', 'BANKINTER']
            )]
            
            if main_banks:
                print("Main Spanish banks found:")
                for bank in main_banks[:5]:
                    print(f"   - {bank['name']} ({bank['id']})")
            
        except Exception as e:
            print(f"[ERROR] Institution fetch failed: {e}")
            print("This is expected if Nordigen credentials are not configured")
            
    except ImportError as e:
        print(f"[ERROR] Failed to import Nordigen client: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

def test_database_models():
    """Test de modelos de base de datos"""
    try:
        from app.models import BankConnection, BankAccount, FinancialMovement
        
        print("\nTesting Database Models...")
        
        # Verificar que los modelos tienen los campos esperados
        connection_fields = BankConnection.__fields__.keys()
        expected_connection_fields = [
            'institution_id', 'institution_name', 'requisition_id',
            'consent_status', 'auto_sync_enabled', 'sync_frequency_hours'
        ]
        
        missing_fields = [field for field in expected_connection_fields if field not in connection_fields]
        if missing_fields:
            print(f"[ERROR] BankConnection missing fields: {missing_fields}")
        else:
            print("[OK] BankConnection model has all required fields")
        
        # Verificar campos de FinancialMovement
        movement_fields = FinancialMovement.__fields__.keys()
        expected_movement_fields = ['external_id', 'bank_account_id', 'source']
        
        missing_movement_fields = [field for field in expected_movement_fields if field not in movement_fields]
        if missing_movement_fields:
            print(f"[ERROR] FinancialMovement missing fields: {missing_movement_fields}")
        else:
            print("[OK] FinancialMovement model has all required fields")
            
    except Exception as e:
        print(f"[ERROR] Database model test failed: {e}")

def test_api_router():
    """Test de router de API"""
    try:
        from app.routers.openbanking import router
        
        print("\nTesting API Router...")
        
        # Verificar que el router tiene las rutas esperadas
        routes = [route.path for route in router.routes]
        expected_routes = [
            '/institutions', '/connections', '/connections/{connection_id}/callback',
            '/connections/{connection_id}/sync', '/connections/{connection_id}',
            '/connections/{connection_id}/toggle-auto-sync'
        ]
        
        missing_routes = [route for route in expected_routes if route not in routes]
        if missing_routes:
            print(f"[ERROR] Missing API routes: {missing_routes}")
        else:
            print(f"[OK] All API routes present: {len(routes)} total routes")
            
    except Exception as e:
        print(f"[ERROR] API router test failed: {e}")

def test_scheduler():
    """Test del scheduler"""
    try:
        from app.scheduler import OpenBankingScheduler
        
        print("\nTesting Scheduler...")
        
        scheduler = OpenBankingScheduler()
        print("[OK] Scheduler instance created successfully")
        
        # Test start/stop (sin ejecutar jobs reales)
        print("[INFO] Scheduler start/stop test skipped (would run background jobs)")
        
    except Exception as e:
        print(f"[ERROR] Scheduler test failed: {e}")

def test_environment_variables():
    """Test de variables de entorno"""
    print("\nTesting Environment Variables...")
    
    # Variables requeridas para Open Banking
    required_vars = ['NORDIGEN_SECRET_ID', 'NORDIGEN_SECRET_KEY']
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"[WARNING] Missing environment variables: {missing_vars}")
        print("[INFO] Add them to .env file for full functionality")
    else:
        print("[OK] All required environment variables present")
    
    # Variables opcionales
    optional_vars = ['DATABASE_URL', 'SECRET_KEY']
    present_optional = [var for var in optional_vars if os.getenv(var)]
    print(f"[INFO] Optional variables present: {present_optional}")

async def main():
    """Función principal de test"""
    print("Open Banking Implementation Test")
    print("=" * 50)
    
    # Tests síncronos
    test_database_models()
    test_api_router()
    test_scheduler()
    test_environment_variables()
    
    # Tests asíncronos
    await test_nordigen_client()
    
    print("\n" + "=" * 50)
    print("[OK] Test completed!")
    print("\nNext steps:")
    print("1. Set up Nordigen credentials in .env")
    print("2. Test frontend at /bank-connections")
    print("3. Connect a sandbox bank for testing")
    print("4. Monitor logs for sync operations")

if __name__ == "__main__":
    asyncio.run(main())