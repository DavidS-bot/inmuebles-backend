#!/usr/bin/env python3
"""
Prueba diferentes credenciales en producción
"""
import requests

def test_credentials(username, password):
    """Probar credenciales específicas"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(
            f"{backend_url}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"EXITO! Usuario: {username}, Password: {password}")
            print(f"Token: {token_data.get('access_token', 'No token')[:30]}...")
            return token_data.get('access_token')
        else:
            print(f"Fallo {username}/{password}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error con {username}: {e}")
        return None

def main():
    print("PROBANDO CREDENCIALES EN PRODUCCION")
    print("=" * 50)
    
    # Lista de credenciales posibles
    credentials = [
        ("davsanchez21277@gmail.com", "admin123"),
        ("davsanchez21277@gmail.com", "inmuebles123"),
        ("davsanchez21277@gmail.com", "password"),
        ("davsanchez21277@gmail.com", "admin"),
        ("admin", "admin123"),
        ("admin", "admin"),
        ("user", "user123"),
        ("test", "test123"),
        ("david", "admin123"),
        ("david", "inmuebles123"),
        ("admin", "inmuebles123"),
        ("admin", "password"),
        ("demo", "demo123"),
        ("root", "admin123")
    ]
    
    for username, password in credentials:
        token = test_credentials(username, password)
        if token:
            print(f"\nCREDENCIALES ENCONTRADAS:")
            print(f"Usuario: {username}")
            print(f"Password: {password}")
            print(f"Backend: https://inmuebles-backend-api.onrender.com")
            print(f"Frontend: https://inmuebles-david.vercel.app")
            break
    else:
        print("\nNo se encontraron credenciales validas.")
        print("Es posible que necesites resetear la base de datos de produccion.")

if __name__ == "__main__":
    main()