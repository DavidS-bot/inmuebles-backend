#!/usr/bin/env python3
"""
Probar con las credenciales reales del usuario
"""
import requests

def test_real_login():
    """Probar login con credenciales reales"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    # Credenciales reales del usuario
    login_data = {
        "username": "davsanchez21277@gmail.com",
        "password": "123456"
    }
    
    print("PROBANDO CREDENCIALES REALES")
    print("=" * 40)
    print(f"Email: {login_data['username']}")
    print(f"Backend: {backend_url}")
    
    try:
        response = requests.post(
            f"{backend_url}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data["access_token"]
            print("LOGIN EXITOSO!")
            print(f"Token: {token[:50]}...")
            
            # Probar endpoints protegidos
            headers = {"Authorization": f"Bearer {token}"}
            
            # Verificar movimientos
            movements_response = requests.get(f"{backend_url}/financial-movements/", headers=headers)
            print(f"GET /financial-movements: {movements_response.status_code}")
            
            if movements_response.status_code == 200:
                movements = movements_response.json()
                print(f"Movimientos encontrados: {len(movements)}")
                
                if movements:
                    total_ingresos = sum(m["amount"] for m in movements if m["amount"] > 0)
                    total_gastos = sum(abs(m["amount"]) for m in movements if m["amount"] < 0)
                    print(f"Total ingresos: {total_ingresos:.2f} EUR")
                    print(f"Total gastos: {total_gastos:.2f} EUR")
                    print(f"Neto: {total_ingresos - total_gastos:.2f} EUR")
                    
                    print("\nUltimos 5 movimientos:")
                    for mov in movements[-5:]:
                        amount_str = f"{mov['amount']:.2f}" if mov['amount'] >= 0 else f"({abs(mov['amount']):.2f})"
                        print(f"  {mov['date']} - {mov['concept'][:40]} - {amount_str} EUR")
            
            # Verificar propiedades
            try:
                properties_response = requests.get(f"{backend_url}/properties/", headers=headers)
                print(f"GET /properties: {properties_response.status_code}")
                
                if properties_response.status_code == 200:
                    properties = properties_response.json()
                    print(f"Propiedades encontradas: {len(properties)}")
                    
                    for prop in properties:
                        print(f"  - {prop.get('name', 'Sin nombre')} (ID: {prop.get('id')})")
                else:
                    print(f"Error properties: {properties_response.text}")
            except:
                print("Endpoint /properties no disponible")
            
            return True
            
        elif response.status_code == 401:
            print("CREDENCIALES INCORRECTAS")
            print(f"Respuesta: {response.text}")
            
            # Intentar registrar el usuario
            print("\nIntentando registrar usuario...")
            register_data = {
                "email": "davsanchez21277@gmail.com",
                "password": "123456"
            }
            
            register_response = requests.post(
                f"{backend_url}/auth/register",
                json=register_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Registro: {register_response.status_code}")
            
            if register_response.status_code in [200, 201]:
                print("Usuario registrado exitosamente!")
                
                # Probar login nuevamente
                login_response = requests.post(
                    f"{backend_url}/auth/login",
                    data=login_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if login_response.status_code == 200:
                    print("Login exitoso despues del registro!")
                    return True
            else:
                print(f"Error en registro: {register_response.text}")
        else:
            print(f"Error inesperado: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except Exception as e:
        print(f"Error de conexion: {e}")
    
    return False

def main():
    success = test_real_login()
    
    print("\n" + "=" * 40)
    if success:
        print("ACCESO CONFIRMADO!")
        print("Ya puedes hacer login en:")
        print("URL: https://inmuebles-david.vercel.app")
        print("Email: davsanchez21277@gmail.com")
        print("Password: 123456")
    else:
        print("PROBLEMA CON EL ACCESO")
        print("Revisa las credenciales o la conexion")
    print("=" * 40)

if __name__ == "__main__":
    main()