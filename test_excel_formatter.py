#!/usr/bin/env python3
"""
Test del scraper v6 con formateo Excel para agente financiero
"""

import asyncio
import logging
from app.services.bankinter_scraper_v6 import BankinterScraperV6

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_excel_formatter():
    """Test completo del scraper v6 con formateo Excel"""
    
    username = "75867185"
    password = "Motoreta123$"
    
    print("BANKINTER SCRAPER V6 - FORMATO AGENTE FINANCIERO")
    print("=" * 60)
    print(f"Usuario: {username}")
    print(f"Objetivo: Extraer datos en formato compatible con:")
    print(f"  https://inmuebles-david.vercel.app/financial-agent/movements")
    print(f"  Formato: Fecha | Concepto | Importe")
    print(f"  Gastos: (70,00) | Ingresos: 70,00")
    
    scraper = None
    try:
        scraper = BankinterScraperV6(username=username, password=password)
        
        print(f"\n[1/4] Configurando navegador...")
        scraper.setup_driver()
        print("OK - Navegador configurado")
        
        print(f"\n[2/4] Ejecutando extraccion completa...")
        print("Esto incluye: login + navegacion + extraccion + formateo + exportacion")
        
        # Ejecutar proceso completo
        transactions, excel_file, csv_file = await scraper.get_august_movements_formatted()
        
        if not transactions:
            print("ERROR - No se encontraron movimientos")
            return False
        
        print(f"OK - {len(transactions)} movimientos procesados")
        
        print(f"\n[3/4] ARCHIVOS GENERADOS:")
        print(f"Excel para agente: {excel_file}")
        print(f"CSV para agente: {csv_file}")
        
        print(f"\n[4/4] RESUMEN DE MOVIMIENTOS AGOSTO 2025:")
        print(f"Total movimientos: {len(transactions)}")
        
        # Estadísticas
        total_ingresos = sum(t.amount for t in transactions if t.amount > 0)
        total_gastos = sum(t.amount for t in transactions if t.amount < 0)
        balance = total_ingresos + total_gastos
        
        print(f"Ingresos: {total_ingresos:.2f}EUR")
        print(f"Gastos: {total_gastos:.2f}EUR") 
        print(f"Balance: {balance:.2f}EUR")
        
        # Mostrar algunos ejemplos en formato final
        print(f"\nEJEMPLOS EN FORMATO AGENTE FINANCIERO:")
        print(f"(Como aparecerán en Excel/CSV)")
        print("-" * 60)
        print(f"{'Fecha':<12} {'Concepto':<35} {'Importe':<15}")
        print("-" * 60)
        
        # Mostrar primeros 10 movimientos
        for i, t in enumerate(transactions[:10], 1):
            fecha = t.date.strftime('%d/%m/%Y')
            concepto = scraper.formatter.clean_concept(t.description)[:32] + "..." if len(t.description) > 35 else scraper.formatter.clean_concept(t.description)
            importe = scraper.formatter.format_amount(t.amount)
            
            print(f"{fecha:<12} {concepto:<35} {importe:<15}")
        
        if len(transactions) > 10:
            print(f"... y {len(transactions) - 10} movimientos más")
        
        print(f"\n" + "="*60)
        print(f"EXITO - DATOS LISTOS PARA AGENTE FINANCIERO")
        print(f"Puedes subir {excel_file} o {csv_file} a:")
        print(f"https://inmuebles-david.vercel.app/financial-agent/movements")
        print(f"="*60)
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    try:
        resultado = asyncio.run(test_excel_formatter())
        
        if resultado:
            print(f"\nPROCESO COMPLETADO EXITOSAMENTE")
            print(f"Los archivos estan listos para usar en el agente financiero")
        else:
            print(f"\nPROCESO COMPLETADO CON INCIDENCIAS")
            print(f"Revisar logs para mas detalles")
            
    except Exception as e:
        print(f"Error: {e}")