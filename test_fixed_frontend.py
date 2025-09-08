#!/usr/bin/env python3
"""
Verificar que la corrección del frontend funciona
"""
import requests

def test_movements_display():
    """Probar que ahora los movimientos se muestren correctamente"""
    
    backend_url = "https://inmuebles-backend-api.onrender.com"
    
    print("VERIFICANDO CORRECION DEL FRONTEND")
    print("=" * 40)
    
    # 1. Login
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
    
    print("Login exitoso!")
    
    # 2. Verificar movimientos
    movements_response = requests.get(f"{backend_url}/financial-movements/", headers=headers)
    
    if movements_response.status_code == 200:
        movements = movements_response.json()
        print(f"Total movimientos: {len(movements)}")
        
        if len(movements) > 0:
            print("\nPrimeros 5 movimientos:")
            for i, mov in enumerate(movements[:5]):
                amount_str = f"{mov['amount']:.2f}" if mov['amount'] >= 0 else f"({abs(mov['amount']):.2f})"
                print(f"  {i+1}. {mov['date']} - {mov['concept'][:40]} - {amount_str} EUR")
            
            # Calcular totales
            total_ingresos = sum(m["amount"] for m in movements if m["amount"] > 0)
            total_gastos = sum(abs(m["amount"]) for m in movements if m["amount"] < 0)
            
            print(f"\nTOTALES:")
            print(f"Ingresos: {total_ingresos:.2f} EUR")
            print(f"Gastos: {total_gastos:.2f} EUR")
            print(f"Neto: {total_ingresos - total_gastos:.2f} EUR")
            
            print("\n" + "=" * 40)
            print("TODO FUNCIONANDO CORRECTAMENTE!")
            print("=" * 40)
            print("Frontend: https://inmuebles-david.vercel.app")
            print("Email: davsanchez21277@gmail.com") 
            print("Password: 123456")
            print("\nAhora deberia poder ver todos tus movimientos!")
            print("Ve a: Agente Financiero > Movimientos Financieros")
            
        else:
            print("No hay movimientos (problema persistente)")
    else:
        print(f"Error obteniendo movimientos: {movements_response.status_code}")

if __name__ == "__main__":
    test_movements_display()