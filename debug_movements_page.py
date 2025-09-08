#!/usr/bin/env python3
"""
Debug específico de la página de movimientos financieros
"""
import requests

def debug_movements_page():
    """Simular exactamente lo que hace el navegador en /financial-agent/movements"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    print("DEBUGEANDO PAGINA DE MOVIMIENTOS FINANCIEROS")
    print("=" * 55)
    
    # 1. Login como usuario real
    login_data = {
        "username": "davsanchez21277@gmail.com",
        "password": "123456"
    }
    
    print("1. Haciendo login...")
    
    response = requests.post(
        f"{backend_url}/auth/login",
        data=login_data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://inmuebles-david.vercel.app",
            "Referer": "https://inmuebles-david.vercel.app/login"
        }
    )
    
    if response.status_code != 200:
        print(f"Error en login: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    print(f"Login exitoso - Token: {token[:30]}...")
    
    # 2. Simular la secuencia exacta que hace la página
    print("\n2. Simulando carga de la página de movimientos...")
    
    # Headers que usaría el navegador
    browser_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "https://inmuebles-david.vercel.app",
        "Referer": "https://inmuebles-david.vercel.app/financial-agent/movements",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 2.1. Intentar cargar propiedades (esto falla pero debe continuar)
    print("\n2.1. Intentando cargar propiedades...")
    properties_response = requests.get(f"{backend_url}/properties/", headers=browser_headers)
    print(f"GET /properties/: {properties_response.status_code}")
    
    if properties_response.status_code != 200:
        print("Propiedades falla (esperado), continuando...")
    
    # 2.2. Cargar movimientos (esto DEBE funcionar)
    print("\n2.2. Cargando movimientos...")
    movements_response = requests.get(f"{backend_url}/financial-movements/", headers=browser_headers)
    print(f"GET /financial-movements/: {movements_response.status_code}")
    
    if movements_response.status_code == 200:
        movements = movements_response.json()
        print(f"Movimientos cargados: {len(movements)}")
        
        if len(movements) > 0:
            print("\nPRIMEROS 5 MOVIMIENTOS:")
            for i, mov in enumerate(movements[:5]):
                print(f"  {i+1}. {mov['date']} | {mov['concept'][:35]} | {mov['amount']:.2f} EUR")
            
            print(f"\nTOTALES:")
            ingresos = sum(m["amount"] for m in movements if m["amount"] > 0)
            gastos = sum(abs(m["amount"]) for m in movements if m["amount"] < 0)
            print(f"Ingresos: {ingresos:.2f} EUR")
            print(f"Gastos: {gastos:.2f} EUR")
            print(f"Neto: {ingresos - gastos:.2f} EUR")
            
            # Verificar si hay algún problema con el formato
            print(f"\nANALISIS DE ESTRUCTURA:")
            first_mov = movements[0]
            print(f"Primer movimiento completo:")
            for key, value in first_mov.items():
                print(f"  {key}: {value} ({type(value).__name__})")
                
        else:
            print("NO HAY MOVIMIENTOS! (Este es el problema)")
            
    elif movements_response.status_code == 401:
        print("Error 401: Token invalido o problema de autenticacion")
        print("Respuesta:", movements_response.text)
    elif movements_response.status_code == 403:
        print("Error 403: Sin permisos")
        print("Respuesta:", movements_response.text)
    else:
        print(f"Error {movements_response.status_code}")
        print("Respuesta:", movements_response.text)
    
    # 3. Probar diferentes variaciones de la llamada
    print("\n3. Probando variaciones de la llamada...")
    
    test_endpoints = [
        "/financial-movements",
        "/financial-movements/",
        "/financial-movements?limit=50",
        "/financial-movements/?limit=50"
    ]
    
    for endpoint in test_endpoints:
        test_response = requests.get(f"{backend_url}{endpoint}", headers=browser_headers)
        print(f"GET {endpoint}: {test_response.status_code}")
        
        if test_response.status_code == 200:
            data = test_response.json()
            print(f"  -> {len(data)} movimientos encontrados")
    
    # 4. Verificar si el problema es de filtros
    print("\n4. Verificando filtros...")
    
    # Probar sin filtros
    no_filter_response = requests.get(f"{backend_url}/financial-movements/", headers=browser_headers)
    if no_filter_response.status_code == 200:
        no_filter_data = no_filter_response.json()
        print(f"Sin filtros: {len(no_filter_data)} movimientos")
        
        # Probar con filtros comunes que podría estar usando el frontend
        filter_tests = [
            "?property_id=",
            "?category=",
            "?start_date=&end_date=",
            "?property_id=&category=&start_date=&end_date="
        ]
        
        for filter_test in filter_tests:
            filter_response = requests.get(f"{backend_url}/financial-movements/{filter_test}", headers=browser_headers)
            if filter_response.status_code == 200:
                filter_data = filter_response.json()
                print(f"Con filtro '{filter_test}': {len(filter_data)} movimientos")

def main():
    debug_movements_page()
    
    print("\n" + "=" * 55)
    print("INSTRUCCIONES PARA DEBUG EN NAVEGADOR:")
    print("=" * 55)
    print("1. Ve a https://inmuebles-david.vercel.app/financial-agent/movements")
    print("2. Presiona F12 para abrir DevTools")
    print("3. Ve a la pestaña 'Console'")
    print("4. Recarga la página (Ctrl+R)")
    print("5. Busca errores en rojo")
    print("6. Ve a la pestaña 'Network'")
    print("7. Mira las llamadas a /financial-movements/")
    print("8. Verifica el status code y la respuesta")

if __name__ == "__main__":
    main()