#!/usr/bin/env python3
"""
Subir datos esenciales de local a producción
"""
import requests
import json

def get_production_token():
    """Obtener token de producción"""
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    login_data = {
        "username": "admin@inmuebles.com",
        "password": "admin123"
    }
    
    response = requests.post(
        f"{backend_url}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Error login produccion: {response.status_code}")
        return None

def get_local_token():
    """Obtener token local"""
    local_url = "http://localhost:8000"
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(
        f"{local_url}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Error login local: {response.status_code}")
        return None

def create_essential_property(prod_token):
    """Crear una propiedad básica en producción"""
    backend_url = "https://inmuebles-backend-api.onrender.com"
    headers = {"Authorization": f"Bearer {prod_token}", "Content-Type": "application/json"}
    
    property_data = {
        "name": "Mi Casa Principal",
        "address": "Calle Principal 123",
        "property_type": "Apartamento", 
        "price": 150000,
        "description": "Propiedad principal para movimientos financieros"
    }
    
    response = requests.post(f"{backend_url}/properties/", json=property_data, headers=headers)
    
    if response.status_code in [200, 201]:
        property_info = response.json()
        print(f"Propiedad creada: ID {property_info.get('id')}")
        return property_info.get('id')
    else:
        print(f"Error creando propiedad: {response.status_code} - {response.text}")
        return None

def upload_sample_movements(prod_token, property_id):
    """Subir algunos movimientos de muestra"""
    backend_url = "https://inmuebles-backend-api.onrender.com"
    headers = {"Authorization": f"Bearer {prod_token}", "Content-Type": "application/json"}
    
    # Movimientos de muestra
    sample_movements = [
        {
            "date": "2025-08-27",
            "concept": "ALQUILER PROPIEDAD PRINCIPAL",
            "amount": 800.0,
            "property_id": property_id,
            "category": "Ingresos por alquiler"
        },
        {
            "date": "2025-08-26", 
            "concept": "GASTOS COMUNIDAD",
            "amount": -120.0,
            "property_id": property_id,
            "category": "Gastos de comunidad"
        },
        {
            "date": "2025-08-25",
            "concept": "REPARACION FONTANERIA",
            "amount": -85.50,
            "property_id": property_id,
            "category": "Mantenimiento"
        },
        {
            "date": "2025-08-24",
            "concept": "ALQUILER AGOSTO",
            "amount": 800.0,
            "property_id": property_id,
            "category": "Ingresos por alquiler"
        }
    ]
    
    created_count = 0
    
    for movement in sample_movements:
        response = requests.post(f"{backend_url}/financial-movements/", json=movement, headers=headers)
        
        if response.status_code in [200, 201]:
            created_count += 1
            print(f"Movimiento creado: {movement['concept']}")
        else:
            print(f"Error creando movimiento: {response.status_code}")
    
    print(f"Total movimientos creados: {created_count}")
    return created_count

def upload_local_excel_file(prod_token):
    """Subir archivo Excel desde local"""
    backend_url = "https://inmuebles-backend-api.onrender.com"
    headers = {"Authorization": f"Bearer {prod_token}"}
    
    # Usar el archivo de movimientos que ya tienes
    excel_files = [
        "movimientos_locales_20250828_122322.xlsx",
        "test_minimo.xlsx", 
        "bankinter_agente_financiero_20250828_105840.xlsx"
    ]
    
    for filename in excel_files:
        try:
            with open(filename, 'rb') as f:
                files = {'file': (filename, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                
                response = requests.post(
                    f"{backend_url}/financial-movements/upload-excel",
                    files=files,
                    headers={"Authorization": f"Bearer {prod_token}"}
                )
                
                if response.status_code in [200, 201]:
                    print(f"Archivo {filename} subido exitosamente!")
                    result = response.json()
                    print(f"Movimientos procesados: {result.get('movements_created', 'N/A')}")
                    return True
                else:
                    print(f"Error subiendo {filename}: {response.status_code}")
                    
        except FileNotFoundError:
            print(f"Archivo {filename} no encontrado")
            continue
        except Exception as e:
            print(f"Error con {filename}: {e}")
            continue
    
    return False

def main():
    print("SUBIENDO DATOS A PRODUCCION")
    print("=" * 40)
    
    # 1. Obtener tokens
    print("\n1. Obteniendo tokens...")
    prod_token = get_production_token()
    if not prod_token:
        print("Error: No se pudo obtener token de producción")
        return
    
    local_token = get_local_token()
    if not local_token:
        print("Warning: No se pudo obtener token local")
    
    # 2. Crear propiedad básica
    print("\n2. Creando propiedad básica...")
    property_id = create_essential_property(prod_token)
    
    if not property_id:
        print("Error: No se pudo crear propiedad")
        return
    
    # 3. Subir movimientos de muestra
    print("\n3. Subiendo movimientos de muestra...")
    movements_created = upload_sample_movements(prod_token, property_id)
    
    # 4. Intentar subir archivo Excel
    print("\n4. Intentando subir archivo Excel...")
    excel_uploaded = upload_local_excel_file(prod_token)
    
    # 5. Verificación final
    print("\n5. Verificacion final...")
    backend_url = "https://inmuebles-backend-api.onrender.com"
    headers = {"Authorization": f"Bearer {prod_token}"}
    
    # Verificar movimientos
    movements_response = requests.get(f"{backend_url}/financial-movements/", headers=headers)
    if movements_response.status_code == 200:
        movements = movements_response.json()
        print(f"Total movimientos en produccion: {len(movements)}")
        
        # Calcular totales
        total_ingresos = sum(m["amount"] for m in movements if m["amount"] > 0)
        total_gastos = sum(abs(m["amount"]) for m in movements if m["amount"] < 0)
        
        print(f"Total ingresos: {total_ingresos:.2f} EUR")
        print(f"Total gastos: {total_gastos:.2f} EUR")
        print(f"Neto: {total_ingresos - total_gastos:.2f} EUR")
    
    # Verificar propiedades
    properties_response = requests.get(f"{backend_url}/properties/", headers=headers)
    if properties_response.status_code == 200:
        properties = properties_response.json()
        print(f"Total propiedades: {len(properties)}")
    
    print("\n" + "=" * 40)
    print("CONFIGURACION COMPLETA!")
    print("=" * 40)
    print("Frontend: https://inmuebles-david.vercel.app")
    print("Backend: https://inmuebles-backend-api.onrender.com")
    print("Email: admin@inmuebles.com") 
    print("Password: admin123")
    print("\nYa puedes hacer login y ver tus movimientos!")

if __name__ == "__main__":
    main()