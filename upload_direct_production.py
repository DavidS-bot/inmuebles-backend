#!/usr/bin/env python3
"""
Upload directo a producción usando endpoints confirmados
"""
import requests

def main():
    print("UPLOAD DIRECTO A PRODUCCION")
    print("=" * 40)
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    # 1. Login
    login_data = {
        "username": "admin@inmuebles.com",
        "password": "admin123"
    }
    
    response = requests.post(
        f"{backend_url}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code != 200:
        print(f"Error login: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Login exitoso!")
    
    # 2. Verificar propiedades existentes
    properties_response = requests.get(f"{backend_url}/properties/", headers=headers)
    print(f"GET /properties: {properties_response.status_code}")
    
    if properties_response.status_code == 200:
        properties = properties_response.json()
        print(f"Propiedades existentes: {len(properties)}")
        
        if properties:
            property_id = properties[0]["id"]
            print(f"Usando propiedad ID: {property_id}")
        else:
            # Crear propiedad
            property_data = {
                "name": "Mi Casa Principal",
                "address": "Calle Principal 123",
                "property_type": "Apartamento",
                "price": 150000
            }
            
            create_response = requests.post(
                f"{backend_url}/properties/",
                json=property_data,
                headers={**headers, "Content-Type": "application/json"}
            )
            
            print(f"POST /properties: {create_response.status_code}")
            
            if create_response.status_code in [200, 201]:
                property_id = create_response.json()["id"]
                print(f"Propiedad creada ID: {property_id}")
            else:
                print(f"Error creando propiedad: {create_response.text}")
                property_id = None
    else:
        print(f"Error obteniendo propiedades: {properties_response.text}")
        property_id = None
    
    # 3. Verificar movimientos existentes
    movements_response = requests.get(f"{backend_url}/financial-movements/", headers=headers)
    print(f"GET /financial-movements: {movements_response.status_code}")
    
    if movements_response.status_code == 200:
        movements = movements_response.json()
        print(f"Movimientos existentes: {len(movements)}")
        
        if len(movements) == 0 and property_id:
            # Crear movimientos de prueba
            test_movements = [
                {
                    "date": "2025-08-27",
                    "concept": "ALQUILER AGOSTO",
                    "amount": 800.0,
                    "property_id": property_id
                },
                {
                    "date": "2025-08-26",
                    "concept": "GASTOS COMUNIDAD",
                    "amount": -120.0,
                    "property_id": property_id
                }
            ]
            
            for movement in test_movements:
                create_response = requests.post(
                    f"{backend_url}/financial-movements/",
                    json=movement,
                    headers={**headers, "Content-Type": "application/json"}
                )
                
                print(f"POST /financial-movements: {create_response.status_code}")
                
                if create_response.status_code in [200, 201]:
                    print(f"Movimiento creado: {movement['concept']}")
                else:
                    print(f"Error: {create_response.text}")
    
    # 4. Intentar upload de Excel
    excel_file = "test_minimo.xlsx"
    print(f"\n4. Intentando upload {excel_file}...")
    
    try:
        with open(excel_file, 'rb') as f:
            files = {'file': (excel_file, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            upload_response = requests.post(
                f"{backend_url}/financial-movements/upload-excel",
                files=files,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            print(f"POST /financial-movements/upload-excel: {upload_response.status_code}")
            
            if upload_response.status_code in [200, 201]:
                result = upload_response.json()
                print(f"Upload exitoso: {result}")
            else:
                print(f"Error upload: {upload_response.text}")
                
    except FileNotFoundError:
        print(f"Archivo {excel_file} no encontrado")
    
    # 5. Verificación final
    print("\n5. Estado final:")
    
    # Contar movimientos
    final_movements = requests.get(f"{backend_url}/financial-movements/", headers=headers)
    if final_movements.status_code == 200:
        movements = final_movements.json()
        print(f"Total movimientos: {len(movements)}")
        
        if movements:
            total_ingresos = sum(m["amount"] for m in movements if m["amount"] > 0)
            total_gastos = sum(abs(m["amount"]) for m in movements if m["amount"] < 0)
            print(f"Ingresos: {total_ingresos:.2f} EUR")
            print(f"Gastos: {total_gastos:.2f} EUR")
            print(f"Neto: {total_ingresos - total_gastos:.2f} EUR")
    
    print("\n" + "=" * 40)
    print("ACCEDE A TU APLICACION:")
    print("URL: https://inmuebles-david.vercel.app")
    print("Email: admin@inmuebles.com")
    print("Password: admin123")
    print("=" * 40)

if __name__ == "__main__":
    main()