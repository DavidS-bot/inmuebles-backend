#!/usr/bin/env python3
"""
Generar archivo API corregido con números puros
"""

import asyncio
from app.services.bankinter_scraper_v7 import BankinterScraperV7

async def generate_corrected_api_file():
    """Generar archivo API con formato correcto"""
    
    print("GENERANDO ARCHIVO API CORREGIDO")
    print("=" * 50)
    
    # Usar los datos que ya extrajimos para evitar hacer scraping de nuevo
    # Vamos a crear el archivo directamente desde los datos conocidos
    
    # Crear scraper solo para usar el formateador
    scraper = BankinterScraperV7(username="dummy", password="dummy", auto_upload=False)
    
    # Usar datos de ejemplo conocidos (los del último scraping exitoso)
    from app.services.bankinter_excel_formatter import BankinterMovement
    from datetime import date
    
    # Crear algunos movimientos de ejemplo con datos reales
    movements = [
        BankinterMovement(fecha=date(2025, 8, 27), concepto="TRANS INM GARCIA BAENA JESUS", importe=750.00, saldo=2092.81),
        BankinterMovement(fecha=date(2025, 8, 26), concepto="RECIB BANKINTER SEGUROS DE VI", importe=-770.67, saldo=1342.81),
        BankinterMovement(fecha=date(2025, 8, 25), concepto="BIZUM CARMEN RAMOS LOP", importe=-10.50, saldo=2113.48),
        BankinterMovement(fecha=date(2025, 8, 20), concepto="IKEA JEREZ HFB", importe=-36.47, saldo=2123.98),
        BankinterMovement(fecha=date(2025, 8, 21), concepto="LEROY MERLIN JEREZ", importe=-68.73, saldo=2160.45),
        BankinterMovement(fecha=date(2025, 8, 19), concepto="TRANS INM FABIOLA IMAGIN", importe=-1000.00, saldo=2749.05),
        BankinterMovement(fecha=date(2025, 8, 11), concepto="TRANS DAVID SANCHEZ SANTANDER", importe=-2000.00, saldo=5322.93),
        BankinterMovement(fecha=date(2025, 8, 6), concepto="TRANS MARIA ROCIO SOTO ZUNIGA", importe=800.00, saldo=8117.91),
        BankinterMovement(fecha=date(2025, 8, 5), concepto="TRANS INM ANTONIO JOSE LOPEZ", importe=650.00, saldo=8426.53),
        BankinterMovement(fecha=date(2025, 8, 5), concepto="TRANSF ANTONIO RASHAD HANSON", importe=1300.00, saldo=8859.67),
    ]
    
    print(f"Generando archivo con {len(movements)} movimientos de ejemplo...")
    
    # Generar archivo API corregido
    api_file = scraper.formatter.export_to_excel_for_api(movements, "bankinter_api_corregido_numeros.xlsx")
    
    print(f"Archivo generado: {api_file}")
    
    # Verificar el contenido
    import pandas as pd
    df = pd.read_excel(api_file)
    
    print(f"\nContenido del archivo:")
    print(f"Filas: {len(df)}")
    print(df.head())
    print(f"\nTipos de datos:")
    print(df.dtypes)
    
    # Verificar que los importes son números
    print(f"\nEjemplos de importes:")
    for i, row in df.head().iterrows():
        print(f"  Fila {i+1}: {row['Importe']} (tipo: {type(row['Importe'])}) - {'✓' if isinstance(row['Importe'], (int, float)) else '❌'}")
    
    return api_file

if __name__ == "__main__":
    resultado = asyncio.run(generate_corrected_api_file())
    print(f"\nArchivo listo para subir: {resultado}")
    print("Sube este archivo a https://inmuebles-david.vercel.app/financial-agent/movements")