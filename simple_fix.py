#!/usr/bin/env python3
"""
Arreglo simple - asignar movimientos a propiedad
"""

import asyncio
import aiohttp

async def simple_fix():
    """Arreglo simple"""
    
    print("ARREGLO SIMPLE - ASIGNAR MOVIMIENTOS")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # Login
        login_data = aiohttp.FormData()
        login_data.add_field('username', 'admin')
        login_data.add_field('password', 'admin123')
        
        async with session.post(f"{base_url}/auth/login", data=login_data) as response:
            login_result = await response.json()
            access_token = login_result.get("access_token")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 1. Crear propiedad
        property_data = {
            "name": "Cuenta Bankinter", 
            "address": "Movimientos bancarios",
            "property_type": "Cuenta",
            "purchase_price": 0,
            "current_value": 0
        }
        
        async with session.post(f"{base_url}/properties/", json=property_data, headers=headers) as response:
            if response.status == 200:
                new_property = await response.json()
                property_id = new_property['id']
                print(f"Propiedad creada: ID {property_id}")
            else:
                print("Error creando propiedad, intentando usar existente...")
                # Buscar propiedades existentes
                async with session.get(f"{base_url}/properties/", headers=headers) as prop_response:
                    properties = await prop_response.json()
                    if properties:
                        property_id = properties[0]['id']
                        print(f"Usando propiedad existente: ID {property_id}")
                    else:
                        print("No hay propiedades disponibles")
                        return
        
        # 2. Obtener movimientos huerfanos
        async with session.get(f"{base_url}/financial-movements/", headers=headers) as response:
            movements = await response.json()
            orphaned = [m for m in movements if not m.get('property_id')]
            print(f"Movimientos huerfanos: {len(orphaned)}")
        
        # 3. Asignar primeros 10 movimientos
        assigned = 0
        for mov in orphaned[:10]:  # Solo los primeros 10
            async with session.put(
                f"{base_url}/financial-movements/{mov['id']}/assign-property",
                params={"property_id": property_id},
                headers=headers
            ) as assign_response:
                if assign_response.status == 200:
                    assigned += 1
                    print(f"Asignado: {mov['concept'][:30]} - {mov['amount']} euros")
        
        print(f"\nMovimientos asignados: {assigned}")
        print("Ve a la interfaz web para verificar que aparecen los movimientos")

if __name__ == "__main__":
    asyncio.run(simple_fix())