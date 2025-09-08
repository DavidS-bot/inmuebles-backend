#!/usr/bin/env python3
"""
Setup final de producción con property_id
"""
import requests

def main():
    print("SETUP FINAL DE PRODUCCION")
    print("=" * 30)
    
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
    
    # 2. Crear movimiento directo (sin property_id primero)
    print("2. Creando movimiento de prueba...")
    
    movement_data = {
        "date": "2025-08-28",
        "concept": "PRUEBA PRODUCCION",
        "amount": 500.0,
        "category": "Ingresos"
    }
    
    create_response = requests.post(
        f"{backend_url}/financial-movements/",
        json=movement_data,
        headers={**headers, "Content-Type": "application/json"}
    )
    
    print(f"POST /financial-movements: {create_response.status_code}")
    
    if create_response.status_code in [200, 201]:
        movement = create_response.json()
        print(f"Movimiento creado: ID {movement.get('id')}")
    else:
        print(f"Error: {create_response.text}")
    
    # 3. Intentar upload con property_id=1 (asumiendo que existe)
    print("\n3. Upload con property_id=1...")
    
    excel_file = "test_minimo.xlsx"
    
    try:
        with open(excel_file, 'rb') as f:
            files = {'file': (excel_file, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            upload_response = requests.post(
                f"{backend_url}/financial-movements/upload-excel?property_id=1",
                files=files,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            print(f"Upload con property_id=1: {upload_response.status_code}")
            
            if upload_response.status_code in [200, 201]:
                result = upload_response.json()
                print(f"Upload exitoso: {result}")
            else:
                print(f"Error: {upload_response.text}")
                
                # Intentar sin property_id
                print("Intentando sin property_id...")
                upload_response2 = requests.post(
                    f"{backend_url}/financial-movements/upload-excel",
                    files=files,
                    headers={"Authorization": f"Bearer {token}"}
                )
                print(f"Sin property_id: {upload_response2.status_code}")
                
    except FileNotFoundError:
        print(f"Archivo {excel_file} no encontrado, creando movimientos manuales...")
        
        # Crear movimientos manuales
        manual_movements = [
            {
                "date": "2025-01-01",
                "concept": "PRUEBA INGRESO",
                "amount": 1000.0,
                "category": "Ingresos"
            },
            {
                "date": "2025-01-02", 
                "concept": "PRUEBA GASTO",
                "amount": -500.0,
                "category": "Gastos"
            },
            {
                "date": "2025-01-03",
                "concept": "OTRA PRUEBA",
                "amount": 250.0,
                "category": "Ingresos"
            }
        ]
        
        for movement in manual_movements:
            create_response = requests.post(
                f"{backend_url}/financial-movements/",
                json=movement,
                headers={**headers, "Content-Type": "application/json"}
            )
            
            if create_response.status_code in [200, 201]:
                print(f"Creado: {movement['concept']}")
    
    # 4. Verificar estado final
    print("\n4. Estado final:")
    
    movements_response = requests.get(f"{backend_url}/financial-movements/", headers=headers)
    if movements_response.status_code == 200:
        movements = movements_response.json()
        print(f"Total movimientos: {len(movements)}")
        
        if movements:
            total_ingresos = sum(m["amount"] for m in movements if m["amount"] > 0)
            total_gastos = sum(abs(m["amount"]) for m in movements if m["amount"] < 0)
            print(f"Ingresos: {total_ingresos:.2f} EUR")
            print(f"Gastos: {total_gastos:.2f} EUR")
            print(f"Neto: {total_ingresos - total_gastos:.2f} EUR")
            
            print("\nPrimeros movimientos:")
            for i, mov in enumerate(movements[:5]):
                amount_str = f"{mov['amount']:.2f}" if mov['amount'] >= 0 else f"({abs(mov['amount']):.2f})"
                print(f"  {mov['date']} - {mov['concept']} - {amount_str} EUR")
        else:
            print("No hay movimientos")
    
    print("\n" + "=" * 30)
    print("ACCESO A LA APLICACION:")
    print("URL: https://inmuebles-david.vercel.app")
    print("Email: admin@inmuebles.com")
    print("Password: admin123")
    print("=" * 30)

if __name__ == "__main__":
    main()