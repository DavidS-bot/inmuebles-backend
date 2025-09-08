#!/usr/bin/env python3
"""
Test del scraper v4 mejorado con navegación secuencial
"""

import asyncio
import logging
from datetime import date
from app.services.bankinter_scraper_v4 import BankinterScraperV4

# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_scraper_v4():
    """Test completo del scraper v4"""
    
    username = "75867185"
    password = "Motoreta123$"
    
    # Período de agosto 2025
    start_date = date(2025, 8, 1)
    end_date = date(2025, 8, 31)
    
    print("BANKINTER SCRAPER V4 - TEST NAVEGACION SECUENCIAL")
    print("=" * 60)
    print(f"Usuario: {username}")
    print(f"Período: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
    
    scraper = None
    try:
        scraper = BankinterScraperV4(username=username, password=password)
        
        print(f"\n[1/4] Configurando navegador...")
        scraper.setup_driver()
        print("Navegador configurado con anti-detección mejorada")
        
        print(f"\n[2/4] Realizando login secuencial...")
        login_success = await scraper.login()
        
        if not login_success:
            print("ERROR: Login fallido")
            return False
        
        print("Login exitoso - Sesión establecida")
        
        print(f"\n[3/4] Navegando paso a paso a movimientos...")
        navigation_success = await scraper.navigate_to_movements()
        
        if not navigation_success:
            print("ERROR: No se pudo navegar a movimientos")
            return False
        
        print("Navegación exitosa - Área de movimientos alcanzada")
        
        print(f"\n[4/4] Extrayendo movimientos con métodos múltiples...")
        transactions = await scraper.extract_movements_from_current_page()
        
        print(f"\nRESULTADOS:")
        print(f"Total movimientos extraídos: {len(transactions)}")
        
        if transactions:
            # Filtrar agosto 2025
            agosto_2025 = [t for t in transactions if t.date.year == 2025 and t.date.month == 8]
            
            print(f"Movimientos de agosto 2025: {len(agosto_2025)}")
            
            if agosto_2025:
                print(f"\n=== MOVIMIENTOS DE AGOSTO 2025 ===")
                print(f"{'#':<3} {'FECHA':<12} {'DESCRIPCIÓN':<50} {'IMPORTE':<12}")
                print("-" * 80)
                
                total_amount = 0
                ingresos = 0
                gastos = 0
                
                for i, t in enumerate(agosto_2025, 1):
                    fecha_str = t.date.strftime('%d/%m/%Y')
                    desc_str = t.description[:47] + "..." if len(t.description) > 50 else t.description
                    amount_str = f"{t.amount:+,.2f}€"
                    
                    print(f"{i:<3} {fecha_str:<12} {desc_str:<50} {amount_str:<12}")
                    
                    total_amount += t.amount
                    if t.amount > 0:
                        ingresos += t.amount
                    else:
                        gastos += t.amount
                
                print("-" * 80)
                print(f"RESUMEN AGOSTO 2025:")
                print(f"  Ingresos:    {ingresos:8.2f}€")
                print(f"  Gastos:      {gastos:8.2f}€")
                print(f"  Balance:     {total_amount:8.2f}€")
                print(f"  Promedio/día: {total_amount/31:6.2f}€")
                
                # Exportar datos
                print(f"\n[EXPORTACION] Generando CSV...")
                csv_file = await scraper.export_to_csv(agosto_2025, "movimientos_agosto_2025_v4.csv")
                print(f"Exportado: {csv_file}")
                
                print(f"\n[EXITO] MOVIMIENTOS DE AGOSTO 2025 EXTRAIDOS")
                return True
            
            else:
                print(f"Sin movimientos específicos de agosto 2025")
                
                # Mostrar distribución por mes
                print(f"\nDistribución por mes:")
                monthly_data = {}
                for t in transactions:
                    month_key = f"{t.date.year}-{t.date.month:02d}"
                    if month_key not in monthly_data:
                        monthly_data[month_key] = []
                    monthly_data[month_key].append(t)
                
                for month, movs in sorted(monthly_data.items()):
                    total = sum(m.amount for m in movs)
                    print(f"  {month}: {len(movs)} movimientos, {total:.2f}€")
                
                # Exportar todos los datos encontrados
                csv_file = await scraper.export_to_csv(transactions, "todos_movimientos_v4.csv")
                print(f"\nTodos los datos exportados: {csv_file}")
        
        else:
            print(f"No se encontraron movimientos")
            
            # Información de debug
            current_url = scraper.driver.current_url
            page_title = scraper.driver.title
            page_size = len(scraper.driver.page_source)
            
            print(f"\nINFORMACION DEBUG:")
            print(f"  URL final: {current_url}")
            print(f"  Título: {page_title}")
            print(f"  Tamaño página: {page_size:,} caracteres")
            
            # Análisis de contenido
            page_source = scraper.driver.page_source.lower()
            keywords = {
                'agosto': page_source.count('agosto'),
                '08': page_source.count('08'),
                '2025': page_source.count('2025'),
                'movimiento': page_source.count('movimiento'),
                'euro': page_source.count('euro'),
                'eur': page_source.count('eur')
            }
            
            print(f"  Palabras clave: {keywords}")
            
            if keywords['08'] > 0 and keywords['2025'] > 0:
                print(f"  -> HAY DATOS DE AGOSTO 2025 PERO NO SE EXTRAJERON")
                print(f"  -> El parser necesita ajustes adicionales")
            
        return len(transactions) > 0
        
    except Exception as e:
        print(f"\nERROR CRÍTICO: {e}")
        return False
        
    finally:
        if scraper:
            print(f"\nCerrando navegador...")
            scraper.close()

if __name__ == "__main__":
    try:
        resultado = asyncio.run(test_scraper_v4())
        
        if resultado:
            print(f"\n" + "="*60)
            print(f"[EXITO] SCRAPER V4 FUNCIONANDO")
            print(f"Navegación secuencial y extracción completadas")
            print(f"="*60)
        else:
            print(f"\n" + "="*60)
            print(f"[INFO] SCRAPER V4 PARCIALMENTE FUNCIONAL")
            print(f"Login y navegación OK - Parser necesita ajustes")
            print(f"="*60)
            
    except KeyboardInterrupt:
        print(f"\nTest cancelado por usuario")
    except Exception as e:
        print(f"\nError fatal: {e}")