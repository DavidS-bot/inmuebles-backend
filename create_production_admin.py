#!/usr/bin/env python3
"""
Crea un usuario administrador directamente en el backend de producción
"""
import requests
import json

def create_production_user():
    """Crear usuario admin en producción"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    # Datos del usuario administrador
    user_data = {
        "username": "admin",
        "email": "admin@inmuebles.com",
        "password": "admin123",
        "full_name": "Administrator"
    }
    
    print("CREANDO USUARIO ADMINISTRADOR EN PRODUCCIÓN")
    print("=" * 50)
    print(f"Backend: {backend_url}")
    
    # Intentar registrar usuario
    try:
        response = requests.post(
            f"{backend_url}/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200 or response.status_code == 201:
            print("Usuario creado exitosamente!")
            print(f"Usuario: {user_data['username']}")
            print(f"Contraseña: {user_data['password']}")
            return True
        else:
            print(f"Error al crear usuario: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
            # Intentar con endpoint alternativo
            print("\nIntentando con endpoint /users/...")
            response = requests.post(
                f"{backend_url}/users/",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200 or response.status_code == 201:
                print("Usuario creado con endpoint alternativo!")
                return True
            else:
                print(f"Tambien fallo: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"Error de conexion: {e}")
        return False

def test_login():
    """Probar login con el usuario creado"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print("\nPROBANDO LOGIN...")
    print("=" * 30)
    
    try:
        # Probar login con form data
        response = requests.post(
            f"{backend_url}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print("Login exitoso!")
            print(f"Token: {token_data.get('access_token', 'No token')[:50]}...")
            return token_data.get('access_token')
        else:
            print(f"Error en login: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
            # Probar con token endpoint
            print("\nIntentando con /token...")
            response = requests.post(
                f"{backend_url}/token",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                print("Login exitoso con /token!")
                return token_data.get('access_token')
            else:
                print(f"Tambien fallo: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"Error de conexion: {e}")
        return None

def test_protected_endpoint(token):
    """Probar endpoint protegido"""
    if not token:
        return
        
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    print("\nPROBANDO ENDPOINT PROTEGIDO...")
    print("=" * 35)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Probar varios endpoints
        endpoints = ["/users/me", "/financial-movements/", "/properties/"]
        
        for endpoint in endpoints:
            response = requests.get(f"{backend_url}{endpoint}", headers=headers)
            print(f"GET {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"{endpoint} funciona!")
                if endpoint == "/financial-movements/":
                    data = response.json()
                    print(f"   Movimientos encontrados: {len(data)}")
                elif endpoint == "/properties/":
                    data = response.json()
                    print(f"   Propiedades encontradas: {len(data)}")
                break
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("CONFIGURANDO BACKEND DE PRODUCCIÓN")
    print("=" * 60)
    
    # 1. Crear usuario
    if create_production_user():
        print("\nUsuario administrador creado")
    else:
        print("\nNo se pudo crear usuario (puede que ya exista)")
    
    # 2. Probar login
    token = test_login()
    
    # 3. Probar endpoint protegido
    if token:
        test_protected_endpoint(token)
    
    print("\n" + "=" * 60)
    print("RESUMEN:")
    print("Frontend: https://inmuebles-david.vercel.app")
    print("Backend: https://inmuebles-backend-api.onrender.com") 
    print("Usuario: admin")
    print("Contraseña: admin123")
    print("\nIntenta hacer login ahora!")

if __name__ == "__main__":
    main()