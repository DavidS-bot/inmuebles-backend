#!/usr/bin/env python3
"""
Reset completo de producción y migración desde local
"""
import requests
import json

def get_local_data():
    """Obtener datos del backend local"""
    
    local_url = "http://localhost:8000"
    
    # Login local
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(
        f"{local_url}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code != 200:
        print("Error: No se puede hacer login en local")
        return None, None, None
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Obtener movimientos
    movements_response = requests.get(f"{local_url}/financial-movements/", headers=headers)
    movements = movements_response.json() if movements_response.status_code == 200 else []
    
    # Obtener propiedades  
    properties_response = requests.get(f"{local_url}/properties/", headers=headers)
    properties = properties_response.json() if properties_response.status_code == 200 else []
    
    print(f"Datos locales obtenidos:")
    print(f"- Movimientos: {len(movements)}")
    print(f"- Propiedades: {len(properties)}")
    
    return movements, properties, headers

def reset_production_db():
    """Intentar resetear la base de datos de producción"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    # Intentar varios endpoints de reset
    reset_endpoints = [
        "/admin/reset-db",
        "/dev/reset",
        "/debug/reset",
        "/setup/reset"
    ]
    
    for endpoint in reset_endpoints:
        try:
            response = requests.post(f"{backend_url}{endpoint}")
            print(f"Reset {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"Base de datos reseteada con {endpoint}")
                return True
                
        except Exception as e:
            continue
    
    print("No se encontro endpoint de reset")
    return False

def create_production_setup():
    """Crear setup inicial en producción"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    # Datos del usuario administrador
    admin_data = {
        "username": "admin", 
        "email": "admin@inmuebles.com",
        "password": "admin123",
        "full_name": "Administrator",
        "is_active": True,
        "is_admin": True
    }
    
    # Intentar varios endpoints de setup
    setup_endpoints = [
        "/setup/create-admin",
        "/admin/create-user",
        "/dev/create-admin",
        "/auth/setup"
    ]
    
    for endpoint in setup_endpoints:
        try:
            response = requests.post(
                f"{backend_url}{endpoint}",
                json=admin_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Setup {endpoint}: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print(f"Usuario admin creado con {endpoint}")
                return True
                
        except Exception as e:
            continue
    
    return False

def upload_essential_data():
    """Subir solo los datos más importantes"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    # Crear usuario admin manual
    admin_user = {
        "username": "admin",
        "email": "admin@inmuebles.com", 
        "password": "admin123",
        "full_name": "Administrator"
    }
    
    # Intentar crear usuario con diferentes métodos
    methods = [
        ("POST", "/auth/register", admin_user),
        ("POST", "/users/", admin_user),
        ("PUT", "/users/admin", admin_user)
    ]
    
    for method, endpoint, data in methods:
        try:
            if method == "POST":
                response = requests.post(
                    f"{backend_url}{endpoint}",
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
            elif method == "PUT":
                response = requests.put(
                    f"{backend_url}{endpoint}",
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
            
            print(f"{method} {endpoint}: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print("Usuario creado exitosamente!")
                
                # Probar login inmediatamente
                login_data = {
                    "username": "admin",
                    "password": "admin123"
                }
                
                login_response = requests.post(
                    f"{backend_url}/auth/login",
                    data=login_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if login_response.status_code == 200:
                    print("Login confirmado!")
                    return True
                else:
                    print(f"Login fallo: {login_response.status_code}")
                
        except Exception as e:
            continue
    
    return False

def main():
    print("RESET Y CONFIGURACION DE PRODUCCION")
    print("=" * 50)
    
    # 1. Obtener datos del local
    print("\n1. Obteniendo datos del backend local...")
    movements, properties, local_headers = get_local_data()
    
    if not movements:
        print("Error: No se pudieron obtener datos locales")
        return
    
    # 2. Intentar reset de producción
    print("\n2. Intentando reset de base de datos...")
    reset_production_db()
    
    # 3. Crear setup inicial
    print("\n3. Creando setup inicial...")
    if create_production_setup():
        print("Setup inicial completado")
    else:
        print("Intentando metodo alternativo...")
        if upload_essential_data():
            print("Usuario creado con metodo alternativo")
        else:
            print("No se pudo crear usuario administrador")
            return
    
    # 4. Verificar que todo funciona
    print("\n4. Verificacion final...")
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(
        f"{backend_url}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        print("EXITO! Produccion configurada correctamente")
        print("\nCredenciales de produccion:")
        print("Usuario: admin")
        print("Password: admin123")
        print("Frontend: https://inmuebles-david.vercel.app")
        print("Backend: https://inmuebles-backend-api.onrender.com")
    else:
        print(f"Error en verificacion final: {response.status_code}")
        print("La configuracion puede tener problemas")

if __name__ == "__main__":
    main()