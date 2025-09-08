#!/usr/bin/env python3
"""
Verificar endpoints disponibles para contratos de alquiler
"""
import requests

def test_contracts_endpoints():
    """Probar diferentes endpoints para contratos"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    # Login
    login_data = {
        "username": "davsanchez21277@gmail.com",
        "password": "123456"
    }
    
    response = requests.post(
        f"{backend_url}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code != 200:
        print(f"Error en login: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("VERIFICANDO ENDPOINTS DE CONTRATOS")
    print("=" * 40)
    
    # Endpoints a probar
    endpoints = [
        "/rental-contracts",
        "/rental-contracts/",
        "/contracts",
        "/contracts/",
        "/properties/1/contracts",
        "/properties/1/contracts/",
        "/properties/1/rental-contracts",
        "/properties/1/rental-contracts/",
        "/rental-contracts?property_id=1",
        "/rental-contracts/?property_id=1"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{backend_url}{endpoint}", headers=headers)
            print(f"GET {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"  -> {len(data)} contratos encontrados")
                    if len(data) > 0:
                        print(f"  -> Primer contrato: {data[0]}")
                else:
                    print(f"  -> Respuesta: {data}")
                    
        except Exception as e:
            print(f"GET {endpoint}: ERROR - {e}")
    
    # Verificar propiedades disponibles
    print(f"\nVERIFICANDO PROPIEDADES DISPONIBLES:")
    try:
        props_response = requests.get(f"{backend_url}/properties/", headers=headers)
        if props_response.status_code == 200:
            props = props_response.json()
            print(f"Propiedades disponibles: {len(props)}")
            for prop in props[:3]:
                print(f"  - ID {prop['id']}: {prop.get('address', 'Sin direccion')}")
        else:
            print(f"Error obteniendo propiedades: {props_response.status_code}")
    except Exception as e:
        print(f"Error con propiedades: {e}")

if __name__ == "__main__":
    test_contracts_endpoints()