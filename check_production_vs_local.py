#!/usr/bin/env python3
"""
Verificar diferencia entre local y producción
"""

import asyncio
import aiohttp

async def check_both_environments():
    """Verificar local vs producción"""
    
    print("VERIFICANDO ENTORNOS - LOCAL VS PRODUCCION")
    print("=" * 60)
    
    environments = [
        ("LOCAL", "http://localhost:8000"),
        ("PRODUCCION", "https://inmuebles-david.vercel.app")
    ]
    
    for env_name, base_url in environments:
        print(f"\n=== {env_name} ({base_url}) ===")
        
        async with aiohttp.ClientSession() as session:
            try:
                # Intentar login
                login_data = aiohttp.FormData()
                login_data.add_field('username', 'admin')
                login_data.add_field('password', 'admin123')
                
                async with session.post(f"{base_url}/auth/login", data=login_data) as response:
                    if response.status == 200:
                        login_result = await response.json()
                        access_token = login_result.get("access_token")
                        print("Login: EXITOSO")
                        
                        headers = {"Authorization": f"Bearer {access_token}"}
                        
                        # Verificar movimientos
                        async with session.get(f"{base_url}/financial-movements/", headers=headers) as mov_response:
                            if mov_response.status == 200:
                                movements = await mov_response.json()
                                print(f"Movimientos: {len(movements)}")
                                
                                if movements:
                                    assigned_movements = [m for m in movements if m.get('property_id')]
                                    print(f"Movimientos asignados: {len(assigned_movements)}")
                                    
                                    # Mostrar ejemplo
                                    if assigned_movements:
                                        first = assigned_movements[0]
                                        print(f"Ejemplo: {first['concept'][:30]} - {first['amount']}€")
                            else:
                                print(f"Error movimientos: {mov_response.status}")
                        
                        # Verificar propiedades
                        async with session.get(f"{base_url}/properties/", headers=headers) as prop_response:
                            if prop_response.status == 200:
                                properties = await prop_response.json()
                                print(f"Propiedades: {len(properties)}")
                            else:
                                print(f"Error propiedades: {prop_response.status}")
                    
                    elif response.status == 401 and "vercel" in base_url.lower():
                        print("Login: BLOQUEADO POR VERCEL AUTH")
                        print("La aplicacion en produccion requiere bypass token")
                    else:
                        print(f"Login: FALLO ({response.status})")
                        
            except Exception as e:
                print(f"Error: {str(e)[:100]}...")

async def suggest_solution():
    """Sugerir solución basada en el diagnóstico"""
    
    print(f"\n" + "=" * 60)
    print("DIAGNOSTICO Y SOLUCION")
    print("=" * 60)
    
    print("\nPROBLEMA IDENTIFICADO:")
    print("- Los movimientos están en el backend LOCAL (localhost:8000)")
    print("- La interfaz web está en PRODUCCION (vercel.app)")
    print("- Son dos bases de datos completamente diferentes")
    
    print("\nSOLUCIONES POSIBLES:")
    print("\n1. OPCION RAPIDA - Subir archivo directamente en producción:")
    print("   a) Ve a: https://inmuebles-david.vercel.app/financial-agent/movements")
    print("   b) Usa el botón 'Subir Excel' o 'Import' de la interfaz")
    print("   c) Sube el archivo: bankinter_api_corregido_numeros.xlsx")
    print("   d) Asegúrate de que haya una propiedad creada primero")
    
    print("\n2. OPCION TECNICA - Configurar upload automático a producción:")
    print("   a) Necesitarías las credenciales correctas de producción")
    print("   b) O un token de bypass de Vercel")
    print("   c) Modificar el uploader para usar producción")
    
    print("\n3. OPCION ALTERNATIVA - Usar backend local:")
    print("   a) Cambiar la interfaz web para apuntar a localhost:8000")
    print("   b) Solo para desarrollo/testing")
    
    print(f"\nRECOMENDACION:")
    print("Usar la OPCION 1 (subida manual) es lo más rápido y seguro")

if __name__ == "__main__":
    asyncio.run(check_both_environments())
    asyncio.run(suggest_solution())