#!/usr/bin/env python3
"""
Debug simple - verificar movimientos
"""

import asyncio
import aiohttp

async def simple_debug():
    """Debug simple"""
    
    print("DEBUG - VERIFICANDO MOVIMIENTOS")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # Login
        login_data = aiohttp.FormData()
        login_data.add_field('username', 'admin')
        login_data.add_field('password', 'admin123')
        
        async with session.post(f"{base_url}/auth/login", data=login_data) as response:
            if response.status == 200:
                login_result = await response.json()
                access_token = login_result.get("access_token")
                print("Login exitoso")
            else:
                print("Login fallido")
                return
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Verificar movimientos
        print("\nVerificando movimientos...")
        
        async with session.get(f"{base_url}/financial-movements/", headers=headers) as response:
            if response.status == 200:
                movements = await response.json()
                print(f"Movimientos encontrados: {len(movements)}")
                
                if movements:
                    print("\nPrimeros movimientos:")
                    for i, mov in enumerate(movements[:5]):
                        print(f"  {i+1}. Fecha: {mov['date']}")
                        print(f"     Concepto: {mov['concept'][:40]}")
                        print(f"     Importe: {mov['amount']} euros")
                        print(f"     Property ID: {mov.get('property_id', 'NULL')}")
                        print(f"     User ID: {mov.get('user_id', 'NULL')}")
                        print(f"     Clasificado: {mov.get('is_classified', False)}")
                        print("")
                else:
                    print("No hay movimientos")
            else:
                error = await response.text()
                print(f"Error: {response.status} - {error[:200]}")
        
        # Verificar propiedades
        print("\nVerificando propiedades...")
        
        try:
            async with session.get(f"{base_url}/properties/", headers=headers) as response:
                if response.status == 200:
                    properties = await response.json()
                    print(f"Propiedades encontradas: {len(properties)}")
                    
                    for prop in properties:
                        print(f"  - ID: {prop['id']}, Nombre: {prop.get('name', 'Sin nombre')}")
                        print(f"    Direccion: {prop.get('address', 'Sin direccion')}")
                else:
                    print(f"Error obteniendo propiedades: {response.status}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(simple_debug())