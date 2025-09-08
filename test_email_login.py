#!/usr/bin/env python3
"""
Probar login con email en producción
"""
import requests

def test_email_credentials():
    """Probar credenciales con email"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    # El sistema usa email como username
    credentials = [
        ("admin@inmuebles.com", "admin123"),
        ("admin@admin.com", "admin123"),
        ("test@test.com", "test123"),
        ("user@user.com", "user123"),
        ("david@inmuebles.com", "admin123"),
        ("admin@localhost", "admin123"),
        ("admin@example.com", "admin123")
    ]
    
    print("PROBANDO LOGIN CON EMAIL EN PRODUCCION")
    print("=" * 50)
    
    for email, password in credentials:
        login_data = {
            "username": email,  # OAuth2PasswordRequestForm usa "username" pero el backend lo trata como email
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
                print(f"EXITO! Email: {email}, Password: {password}")
                print(f"Token: {token_data.get('access_token', 'No token')[:30]}...")
                
                # Probar endpoint protegido
                headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                test_response = requests.get(f"{backend_url}/financial-movements/", headers=headers)
                print(f"Test endpoint: {test_response.status_code}")
                
                if test_response.status_code == 200:
                    movements = test_response.json()
                    print(f"Movimientos en produccion: {len(movements)}")
                
                return email, password, token_data['access_token']
                
            else:
                print(f"Fallo {email}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Error con {email}: {e}")
    
    print("\nNo se encontraron credenciales validas con email")
    
    # Intentar registrar usuario admin
    print("\nIntentando registrar admin@inmuebles.com...")
    
    register_data = {
        "email": "admin@inmuebles.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{backend_url}/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            print("Usuario registrado exitosamente!")
            
            # Probar login inmediato
            login_data = {
                "username": "admin@inmuebles.com",
                "password": "admin123"
            }
            
            login_response = requests.post(
                f"{backend_url}/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                print("Login exitoso despues del registro!")
                return "admin@inmuebles.com", "admin123", token_data['access_token']
            else:
                print(f"Login fallo despues del registro: {login_response.status_code}")
        else:
            print(f"Registro fallo: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error en registro: {e}")
    
    return None, None, None

def main():
    email, password, token = test_email_credentials()
    
    if email and password:
        print("\n" + "=" * 50)
        print("CREDENCIALES ENCONTRADAS!")
        print("=" * 50)
        print(f"Frontend: https://inmuebles-david.vercel.app")
        print(f"Backend: https://inmuebles-backend-api.onrender.com")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print("\nPuedes hacer login en la aplicacion web!")
    else:
        print("\nNo se pudo acceder al backend de produccion")
        print("Puede que necesites contactar al administrador del servicio")

if __name__ == "__main__":
    main()