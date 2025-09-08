#!/usr/bin/env python3
"""
Exporta todos los movimientos desde el backend local funcionando
y los guarda en múltiples formatos para uso inmediato
"""
import requests
import pandas as pd
from datetime import datetime
import json

class LocalMovementsExporter:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.token = None
        
    def login(self):
        """Login al backend local"""
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(
            f"{self.base_url}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            print("Login exitoso al backend local")
            return True
        else:
            print(f"Error en login: {response.status_code}")
            return False
    
    def get_movements(self):
        """Obtiene todos los movimientos del backend local"""
        if not self.token:
            print("No hay token de autenticacion")
            return []
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/financial-movements/", headers=headers)
        
        if response.status_code == 200:
            movements = response.json()
            print(f"Obtenidos {len(movements)} movimientos del backend local")
            return movements
        else:
            print(f"Error obteniendo movimientos: {response.status_code}")
            return []
    
    def calculate_totals(self, movements):
        """Calcula totales de ingresos, gastos y neto"""
        total_ingresos = sum(m["amount"] for m in movements if m["amount"] > 0)
        total_gastos = sum(abs(m["amount"]) for m in movements if m["amount"] < 0)
        neto = total_ingresos - total_gastos
        
        return {
            "total_ingresos": total_ingresos,
            "total_gastos": total_gastos,
            "neto": neto,
            "total_movimientos": len(movements)
        }
    
    def export_to_excel(self, movements, filename=None):
        """Exporta movimientos a Excel con formato para agente financiero"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"movimientos_locales_{timestamp}.xlsx"
        
        # Preparar datos para Excel
        excel_data = []
        for mov in movements:
            # Formato para el agente financiero
            amount_formatted = mov["amount"]
            if amount_formatted < 0:
                amount_str = f"({abs(amount_formatted):.2f})"
            else:
                amount_str = f"{amount_formatted:.2f}"
            
            excel_data.append({
                "Fecha": mov["date"],
                "Concepto": mov["concept"],
                "Importe": amount_str,
                "Categoria": mov.get("category", "Sin clasificar"),
                "Property_ID": mov.get("property_id", "Sin asignar"),
                "ID": mov["id"]
            })
        
        df = pd.DataFrame(excel_data)
        df.to_excel(filename, index=False)
        print(f"Exportado a Excel: {filename}")
        return filename
    
    def export_to_csv(self, movements, filename=None):
        """Exporta movimientos a CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"movimientos_locales_{timestamp}.csv"
        
        csv_data = []
        for mov in movements:
            csv_data.append({
                "Fecha": mov["date"],
                "Concepto": mov["concept"],
                "Importe": mov["amount"],
                "Categoria": mov.get("category", "Sin clasificar"),
                "Property_ID": mov.get("property_id", "Sin asignar"),
                "ID": mov["id"]
            })
        
        df = pd.DataFrame(csv_data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Exportado a CSV: {filename}")
        return filename
    
    def export_to_json(self, movements, filename=None):
        """Exporta movimientos a JSON completo"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"movimientos_locales_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(movements, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Exportado a JSON: {filename}")
        return filename
    
    def create_summary_report(self, movements, totals):
        """Crea un reporte resumen"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resumen_movimientos_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("RESUMEN DE MOVIMIENTOS FINANCIEROS\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Fecha de exportación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Backend local: http://localhost:8000\n\n")
            
            f.write("TOTALES:\n")
            f.write(f"• Total Movimientos: {totals['total_movimientos']}\n")
            f.write(f"• Total Ingresos: {totals['total_ingresos']:.2f} EUR\n")
            f.write(f"• Total Gastos: {totals['total_gastos']:.2f} EUR\n")
            f.write(f"• Neto: {totals['neto']:.2f} EUR\n\n")
            
            # Análisis por categorías
            categories = {}
            for mov in movements:
                cat = mov.get("category", "Sin clasificar")
                if cat not in categories:
                    categories[cat] = {"count": 0, "total": 0}
                categories[cat]["count"] += 1
                categories[cat]["total"] += mov["amount"]
            
            f.write("ANÁLISIS POR CATEGORÍAS:\n")
            for cat, data in categories.items():
                f.write(f"• {cat}: {data['count']} movimientos, Total: {data['total']:.2f} EUR\n")
            
            # Movimientos más recientes
            f.write(f"\nÚLTIMOS 10 MOVIMIENTOS:\n")
            recent = sorted(movements, key=lambda x: x["date"], reverse=True)[:10]
            for mov in recent:
                amount_str = f"{mov['amount']:.2f}" if mov['amount'] >= 0 else f"({abs(mov['amount']):.2f})"
                f.write(f"• {mov['date']} - {mov['concept'][:50]} - {amount_str} EUR\n")
        
        print(f"Reporte creado: {filename}")
        return filename

def main():
    print("EXPORTADOR DE MOVIMIENTOS DEL BACKEND LOCAL")
    print("=" * 50)
    
    exporter = LocalMovementsExporter()
    
    # 1. Login al backend local
    if not exporter.login():
        return
    
    # 2. Obtener todos los movimientos
    movements = exporter.get_movements()
    if not movements:
        print("No se pudieron obtener movimientos")
        return
    
    # 3. Calcular totales
    totals = exporter.calculate_totals(movements)
    
    print(f"\nRESUMEN:")
    print(f"• Total Movimientos: {totals['total_movimientos']}")
    print(f"• Total Ingresos: {totals['total_ingresos']:.2f} EUR")
    print(f"• Total Gastos: {totals['total_gastos']:.2f} EUR")
    print(f"• Neto: {totals['neto']:.2f} EUR")
    
    # 4. Exportar a múltiples formatos
    print(f"\nEXPORTANDO ARCHIVOS:")
    excel_file = exporter.export_to_excel(movements)
    csv_file = exporter.export_to_csv(movements)
    json_file = exporter.export_to_json(movements)
    summary_file = exporter.create_summary_report(movements, totals)
    
    print(f"\nEXPORTACION COMPLETA")
    print(f"Archivos creados:")
    print(f"• Excel: {excel_file}")
    print(f"• CSV: {csv_file}")
    print(f"• JSON: {json_file}")
    print(f"• Resumen: {summary_file}")
    print(f"\nPuedes abrir cualquiera de estos archivos para ver tus movimientos.")
    print(f"El backend local (localhost:8000) sigue funcionando perfectamente.")

if __name__ == "__main__":
    main()