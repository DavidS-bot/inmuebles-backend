#!/usr/bin/env python3
"""
Debug - verificar por qué no se muestran los movimientos
"""

import asyncio
import aiohttp
import json

async def debug_movements_display():
    """Debug del problema de visualización de movimientos"""
    
    print("DEBUG - MOVIMIENTOS NO SE MUESTRAN")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # 1. Verificar login
    print("1. VERIFICANDO LOGIN...")
    
    async with aiohttp.ClientSession() as session:
        # Login
        login_data = aiohttp.FormData()
        login_data.add_field('username', 'admin')
        login_data.add_field('password', 'admin123')
        
        async with session.post(f"{base_url}/auth/login", data=login_data) as response:
            if response.status == 200:
                login_result = await response.json()
                access_token = login_result.get("access_token")
                print("✓ Login exitoso")
            else:
                print("❌ Login fallido")
                return
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 2. Verificar usuario actual
        print("\n2. VERIFICANDO USUARIO ACTUAL...")
        try:
            async with session.get(f"{base_url}/auth/me", headers=headers) as response:
                if response.status == 200:
                    user_info = await response.json()
                    print(f"Usuario: {user_info}")
                    user_id = user_info.get('id')
                else:
                    print("No hay endpoint /auth/me")
                    user_id = 2  # Asumiendo que es el admin con ID 2
        except:
            user_id = 2
            print(f"Asumiendo user_id: {user_id}")
        
        # 3. Verificar movimientos financieros directos
        print(f"\n3. VERIFICANDO MOVIMIENTOS FINANCIEROS...")
        
        async with session.get(f"{base_url}/financial-movements/", headers=headers) as response:
            if response.status == 200:
                movements = await response.json()
                print(f"Movimientos encontrados: {len(movements)}")
                
                if movements:
                    print("Primeros 3 movimientos:")
                    for i, mov in enumerate(movements[:3]):
                        print(f"  {i+1}. {mov['date']} - {mov['concept'][:30]} - {mov['amount']}€")
                        print(f"     property_id: {mov.get('property_id')}")
                        print(f"     user_id: {mov.get('user_id')}")
                        print(f"     is_classified: {mov.get('is_classified')}")
                else:
                    print("No se encontraron movimientos")
            else:
                error = await response.text()
                print(f"Error obteniendo movimientos: {response.status} - {error}")
        
        # 4. Verificar propiedades del usuario
        print(f"\n4. VERIFICANDO PROPIEDADES DEL USUARIO...")
        
        try:
            async with session.get(f"{base_url}/properties/", headers=headers) as response:
                if response.status == 200:
                    properties = await response.json()
                    print(f"Propiedades encontradas: {len(properties)}")
                    
                    if properties:
                        print("Propiedades:")
                        for prop in properties:
                            print(f"  - ID: {prop['id']}, Nombre: {prop.get('name', 'Sin nombre')}")
                    else:
                        print("El usuario no tiene propiedades")
                        
                        # Crear una propiedad de ejemplo
                        print("\n5. CREANDO PROPIEDAD DE EJEMPLO...")
                        property_data = {
                            "name": "Propiedad Principal",
                            "address": "Calle Ejemplo 123",
                            "property_type": "Apartamento",
                            "purchase_price": 100000,
                            "current_value": 120000
                        }
                        
                        async with session.post(f"{base_url}/properties/", 
                                               json=property_data, 
                                               headers=headers) as create_response:
                            if create_response.status == 200:
                                new_property = await create_response.json()
                                print(f"✓ Propiedad creada: ID {new_property['id']}")
                                
                                # Reasignar movimientos a la nueva propiedad
                                print(f"\n6. REASIGNANDO MOVIMIENTOS A LA NUEVA PROPIEDAD...")
                                
                                # Obtener movimientos otra vez
                                async with session.get(f"{base_url}/financial-movements/", headers=headers) as mov_response:
                                    if mov_response.status == 200:
                                        movements = await mov_response.json()
                                        
                                        for mov in movements[:5]:  # Solo los primeros 5
                                            try:
                                                async with session.put(
                                                    f"{base_url}/financial-movements/{mov['id']}/assign-property",
                                                    params={"property_id": new_property['id']},
                                                    headers=headers
                                                ) as assign_response:
                                                    if assign_response.status == 200:
                                                        print(f"  ✓ Movimiento {mov['id']} asignado")
                                                    else:
                                                        print(f"  ❌ Error asignando movimiento {mov['id']}")
                                            except Exception as e:
                                                print(f"  Error: {e}")
                            else:
                                error = await create_response.text()
                                print(f"❌ Error creando propiedad: {error}")
                else:
                    error = await response.text()
                    print(f"Error obteniendo propiedades: {response.status} - {error}")
        except Exception as e:
            print(f"Error verificando propiedades: {e}")
        
        # 7. Verificar movimientos después de asignación
        print(f"\n7. VERIFICANDO MOVIMIENTOS DESPUÉS DE ASIGNACIÓN...")
        
        async with session.get(f"{base_url}/financial-movements/", headers=headers) as response:
            if response.status == 200:
                movements = await response.json()
                print(f"Movimientos totales: {len(movements)}")
                
                assigned_movements = [m for m in movements if m.get('property_id')]
                print(f"Movimientos asignados a propiedades: {len(assigned_movements)}")
                
                if assigned_movements:
                    print("Movimientos asignados:")
                    for mov in assigned_movements[:3]:
                        print(f"  - {mov['date']} - {mov['concept'][:30]} - {mov['amount']}€ - Prop: {mov.get('property_id')}")

if __name__ == "__main__":
    asyncio.run(debug_movements_display())