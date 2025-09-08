#!/usr/bin/env python3
"""
Simular las llamadas que hace el frontend al backend
"""
import requests
import json

def test_frontend_backend_flow():
    """Simular el flujo completo frontend -> backend"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    print("SIMULANDO FLUJO FRONTEND -> BACKEND")
    print("=" * 50)
    
    # 1. Login como lo haría el frontend
    print("1. Login desde frontend...")
    
    login_data = {
        "username": "davsanchez21277@gmail.com",
        "password": "123456"
    }
    
    # Simular headers que enviaría el frontend
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://inmuebles-david.vercel.app",
        "Referer": "https://inmuebles-david.vercel.app/"
    }
    
    response = requests.post(
        f"{backend_url}/auth/login",
        data=login_data,
        headers=headers
    )
    
    print(f"Login status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error en login: {response.text}")
        return
    
    token = response.json()["access_token"]
    print(f"Token obtenido: {token[:30]}...")
    
    # 2. Llamada a movimientos como lo haría el frontend
    print("\n2. Obteniendo movimientos...")
    
    api_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "https://inmuebles-david.vercel.app",
        "Referer": "https://inmuebles-david.vercel.app/financial-agent/movements"
    }
    
    # Probar diferentes endpoints que podría usar el frontend
    endpoints_to_test = [
        "/financial-movements/",
        "/financial-movements",
        "/movements/",
        "/movements"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\nProbando {endpoint}...")
        
        response = requests.get(f"{backend_url}{endpoint}", headers=api_headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Movimientos encontrados: {len(data)}")
            
            if data:
                print("Primeros 3 movimientos:")
                for i, mov in enumerate(data[:3]):
                    print(f"  {i+1}. {mov.get('date')} - {mov.get('concept', '')[:40]} - {mov.get('amount', 0)}")
                
                # Verificar estructura de datos
                print(f"\nEstructura del primer movimiento:")
                first_mov = data[0]
                for key, value in first_mov.items():
                    print(f"  {key}: {value}")
                
                return True
        elif response.status_code == 401:
            print("Error 401: Token inválido o expirado")
        elif response.status_code == 404:
            print("Error 404: Endpoint no encontrado")
        elif response.status_code == 405:
            print("Error 405: Método no permitido")
        else:
            print(f"Error {response.status_code}: {response.text}")
    
    # 3. Probar con parámetros que podría usar el frontend
    print("\n3. Probando con filtros...")
    
    filter_params = [
        "",
        "?limit=100",
        "?offset=0&limit=100",
        "?page=1&size=100"
    ]
    
    for params in filter_params:
        response = requests.get(f"{backend_url}/financial-movements/{params}", headers=api_headers)
        print(f"Con parámetros '{params}': {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  -> {len(data)} movimientos")
            if len(data) > 0:
                break
    
    return False

def test_cors_headers():
    """Verificar configuración CORS"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    print("\n4. Verificando CORS...")
    
    # OPTIONS request para verificar CORS
    response = requests.options(
        f"{backend_url}/financial-movements/",
        headers={
            "Origin": "https://inmuebles-david.vercel.app",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization, Content-Type"
        }
    )
    
    print(f"OPTIONS status: {response.status_code}")
    print(f"CORS headers:")
    
    cors_headers = [
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Methods", 
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Credentials"
    ]
    
    for header in cors_headers:
        value = response.headers.get(header, "NO CONFIGURADO")
        print(f"  {header}: {value}")

def main():
    success = test_frontend_backend_flow()
    test_cors_headers()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ BACKEND RESPONDE CORRECTAMENTE")
        print("El problema puede estar en el frontend (JavaScript/React)")
        print("Revisa la consola del navegador (F12) para ver errores")
    else:
        print("❌ PROBLEMA EN LA CONEXIÓN BACKEND")
        print("Revisa la configuración del API o los endpoints")
    
    print("\n💡 SUGERENCIAS:")
    print("1. Abre https://inmuebles-david.vercel.app")
    print("2. Presiona F12 para abrir Developer Tools")
    print("3. Ve a la pestaña 'Console'")
    print("4. Haz login y ve a Movimientos Financieros")
    print("5. Mira si hay errores en rojo en la consola")
    print("6. Ve a la pestaña 'Network' para ver las llamadas HTTP")

if __name__ == "__main__":
    main()