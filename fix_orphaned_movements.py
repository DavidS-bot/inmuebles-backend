#!/usr/bin/env python3
"""
Arreglar movimientos huérfanos (sin user_id asignado)
"""

import asyncio
import aiohttp

async def fix_orphaned_movements():
    """Arreglar movimientos sin user_id"""
    
    print("ARREGLANDO MOVIMIENTOS HUERFANOS")
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
        
        print("\n1. CREANDO PROPIEDAD PRINCIPAL...")
        
        # Crear una propiedad principal para asignar los movimientos
        property_data = {
            "name": "Cuenta Principal Bankinter", 
            "address": "Movimientos bancarios importados",
            "property_type": "Cuenta Bancaria",
            "purchase_price": 0,
            "current_value": 0
        }
        
        property_id = None
        async with session.post(f"{base_url}/properties/", json=property_data, headers=headers) as response:
            if response.status == 200:
                new_property = await response.json()
                property_id = new_property['id']
                print(f"Propiedad creada: ID {property_id} - {new_property['name']}")
            else:
                # Tal vez ya existe, obtener propiedades existentes
                async with session.get(f"{base_url}/properties/", headers=headers) as prop_response:
                    if prop_response.status == 200:
                        properties = await prop_response.json()
                        if properties:
                            property_id = properties[0]['id']
                            print(f"Usando propiedad existente: ID {property_id}")
                        else:
                            print("No se pudo crear ni encontrar propiedades")
                            return
                    else:
                        print("No se pudo crear propiedad")
                        return
        
        print(f"\n2. REASIGNANDO MOVIMIENTOS HUERFANOS...")
        
        # Obtener todos los movimientos
        async with session.get(f"{base_url}/financial-movements/", headers=headers) as response:
            if response.status == 200:
                movements = await response.json()
                print(f"Movimientos encontrados: {len(movements)}")
                
                # Filtrar movimientos sin property_id
                orphaned = [m for m in movements if not m.get('property_id')]
                print(f"Movimientos huerfanos: {len(orphaned)}")
                
                if not orphaned:
                    print("No hay movimientos huerfanos")
                    return
                
                # Asignar movimientos a la propiedad
                assigned = 0
                for mov in orphaned:
                    try:
                        # Usar el endpoint de asignación
                        async with session.put(
                            f"{base_url}/financial-movements/{mov['id']}/assign-property",
                            params={"property_id": property_id},
                            headers=headers
                        ) as assign_response:
                            if assign_response.status == 200:
                                assigned += 1
                                if assigned <= 5:  # Solo mostrar los primeros 5
                                    print(f"  Asignado: {mov['concept'][:30]} - {mov['amount']} euros")
                            else:
                                error = await assign_response.text()
                                print(f"  Error asignando {mov['id']}: {error}")
                    except Exception as e:
                        print(f"  Error: {e}")
                
                print(f"\n3. RESULTADO:")
                print(f"Movimientos reasignados exitosamente: {assigned}")
                print(f"Movimientos que quedaron huerfanos: {len(orphaned) - assigned}")
                
                # Verificar resultado final
                print(f"\n4. VERIFICACION FINAL...")
                async with session.get(f"{base_url}/financial-movements/", headers=headers) as final_response:
                    if final_response.status == 200:
                        final_movements = await final_response.json()
                        assigned_movements = [m for m in final_movements if m.get('property_id')]
                        print(f"Total movimientos asignados: {len(assigned_movements)}")
                        print(f"Total movimientos sin asignar: {len(final_movements) - len(assigned_movements)}")
                        
                        if assigned_movements:
                            print("\nAhora los movimientos deberian aparecer en la interfaz web!")
                            print("Ve a: https://inmuebles-david.vercel.app/financial-agent/movements")
            else:
                print("Error obteniendo movimientos")

if __name__ == "__main__":
    asyncio.run(fix_orphaned_movements())