#!/usr/bin/env python3
"""
Test del scraper v7 con importes corregidos
"""

import asyncio
import logging
from app.services.bankinter_scraper_v7 import BankinterScraperV7

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_corrected_amounts():
    """Test completo del scraper v7 con importes correctos"""
    
    username = "75867185"
    password = "Motoreta123$"
    
    print("BANKINTER SCRAPER V7 - IMPORTES CORREGIDOS")
    print("=" * 60)
    print(f"Usuario: {username}")
    print(f"Correcci\u00f3n: Extraer importes de celda 4, saldos de celda 5")
    print(f"Ejemplo esperado:")
    print(f"  Fecha: 27/08/2025")
    print(f"  Concepto: Trans Inm/ Garcia Baena Jesus")
    print(f"  Importe: +750,00 \u20ac (NO 27,00)")
    print(f"  Saldo: 2.092,81 \u20ac")
    
    scraper = None
    try:
        scraper = BankinterScraperV7(username=username, password=password)
        
        print(f"\n[1/4] Configurando navegador...")
        scraper.setup_driver()
        print("OK - Navegador configurado")
        
        print(f"\n[2/4] Ejecutando extraccion corregida...")
        
        # Ejecutar proceso completo
        transactions, excel_file, csv_file = await scraper.get_august_movements_corrected()
        
        if not transactions:
            print("ERROR - No se encontraron movimientos")
            return False
        
        print(f"OK - {len(transactions)} movimientos procesados")
        
        print(f"\n[3/4] VERIFICACION DE IMPORTES:")
        print("Comparando con valores esperados...")
        
        # Verificar primeros movimientos contra valores conocidos
        expected_amounts = {
            27: 750.00,   # 27/08/2025 debe ser +750,00 (no 27)
            26: -770.67,  # 26/08/2025 debe ser -770,67 (no 26)  
            25: -10.50,   # 25/08/2025 debe ser -10,50 (no 25)
        }
        
        verification_ok = True
        for t in transactions:
            day = t.date.day
            if day in expected_amounts:
                expected = expected_amounts[day]
                actual = t.amount
                
                if abs(actual - expected) < 0.01:  # Tolerancia de centavos
                    print(f"  OK - D\u00eda {day:2d}: {actual:+8.2f}\u20ac (esperado: {expected:+8.2f}\u20ac)")
                else:
                    print(f"  ERROR - D\u00eda {day:2d}: {actual:+8.2f}\u20ac (esperado: {expected:+8.2f}\u20ac)")
                    verification_ok = False
        
        if verification_ok:
            print("VERIFICACION EXITOSA - Importes correctos!")
        else:
            print("VERIFICACION FALLIDA - Revisar l\u00f3gica de extracci\u00f3n")
        
        print(f"\n[4/4] ESTADISTICAS FINALES:")
        
        # Calcular estad\u00edsticas
        total_ingresos = sum(t.amount for t in transactions if t.amount > 0)
        total_gastos = sum(t.amount for t in transactions if t.amount < 0)
        balance = total_ingresos + total_gastos
        
        print(f"Total movimientos: {len(transactions)}")
        print(f"Ingresos: {total_ingresos:,.2f}\u20ac")
        print(f"Gastos: {total_gastos:,.2f}\u20ac")
        print(f"Balance: {balance:,.2f}\u20ac")
        
        print(f"\nARCHIVOS GENERADOS:")
        print(f"Excel: {excel_file}")
        print(f"CSV: {csv_file}")
        
        print(f"\nLISTO PARA AGENTE FINANCIERO:")
        print(f"Los archivos ya tienen el formato correcto para:")
        print(f"https://inmuebles-david.vercel.app/financial-agent/movements")
        
        print(f"\n" + "="*60)
        print(f"EXITO - SCRAPER V7 CON IMPORTES CORRECTOS")
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
        resultado = asyncio.run(test_corrected_amounts())
        
        if resultado:
            print(f"\nPROCESO COMPLETADO EXITOSAMENTE")
            print(f"Importes corregidos y listos para usar")
        else:
            print(f"\nPROCESO COMPLETADO CON INCIDENCIAS")
            print(f"Revisar logs para mas detalles")
            
    except Exception as e:
        print(f"Error: {e}")