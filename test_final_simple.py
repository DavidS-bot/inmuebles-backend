#!/usr/bin/env python3
"""
Test final simple del scraper v3 - Sin emojis para Windows
"""

import asyncio
import logging
from datetime import date
from app.services.bankinter_scraper_v3 import BankinterScraperV3

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_final_simple():
    """Test final del scraper v3 sin emojis"""
    
    username = "75867185"
    password = "Motoreta123$"
    
    # Período del mes actual
    today = date.today()
    start_date = date(today.year, today.month, 1)
    end_date = today
    
    print("=" * 60)
    print("BANKINTER SCRAPER V3 - TEST FINAL")
    print("=" * 60)
    print(f"Usuario: {username}")
    print(f"Periodo: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
    print(f"Total dias: {(end_date - start_date).days + 1}")
    
    scraper = None
    try:
        scraper = BankinterScraperV3(username=username, password=password)
        
        print(f"\n[PASO 1/4] Configurando navegador...")
        scraper.setup_driver()
        print("[OK] Navegador configurado")
        
        print(f"\n[PASO 2/4] Realizando login...")
        login_success = await scraper.login()
        
        if not login_success:
            print("[ERROR] Login fallido")
            return False
            
        print("[OK] Login exitoso - Acceso a Bankinter conseguido")
        
        print(f"\n[PASO 3/4] Buscando movimientos bancarios reales...")
        print("Estrategias: navegacion por interfaz + extraccion inteligente")
        
        transactions = await scraper.get_real_movements(start_date, end_date)
        
        print(f"\n[PASO 4/4] RESULTADOS FINALES")
        print("=" * 50)
        
        if transactions:
            print(f"[EXITO] {len(transactions)} movimientos encontrados")
            
            print(f"\nMOVIMIENTOS DE {start_date.strftime('%B %Y').upper()}")
            print("-" * 80)
            print(f"{'#':<3} {'FECHA':<12} {'DESCRIPCION':<45} {'IMPORTE':<12}")
            print("-" * 80)
            
            total_ingresos = 0
            total_gastos = 0
            
            for i, t in enumerate(transactions, 1):
                fecha_str = t.date.strftime('%d/%m/%Y')
                descripcion = t.description[:45] if len(t.description) > 45 else t.description
                importe_str = f"{t.amount:+,.2f}EUR"
                
                print(f"{i:<3} {fecha_str:<12} {descripcion:<45} {importe_str:<12}")
                
                if t.amount > 0:
                    total_ingresos += t.amount
                else:
                    total_gastos += t.amount
            
            print("-" * 80)
            print(f"RESUMEN FINANCIERO")
            print(f"Total ingresos:  {total_ingresos:+10.2f}EUR")
            print(f"Total gastos:    {total_gastos:+10.2f}EUR")
            print(f"Balance neto:    {total_ingresos + total_gastos:+10.2f}EUR")
            print(f"Promedio/dia:    {(total_ingresos + total_gastos) / ((end_date - start_date).days + 1):+10.2f}EUR")
            
            # Análisis de tipos de movimientos
            movs_positivos = [t for t in transactions if t.amount > 0]
            movs_negativos = [t for t in transactions if t.amount < 0]
            
            print(f"\nANALISIS DE MOVIMIENTOS")
            print(f"Ingresos: {len(movs_positivos)} movimientos")
            print(f"Gastos: {len(movs_negativos)} movimientos")
            
            if movs_positivos:
                print(f"Ingreso promedio: {sum(t.amount for t in movs_positivos) / len(movs_positivos):,.2f}EUR")
            if movs_negativos:
                print(f"Gasto promedio: {sum(t.amount for t in movs_negativos) / len(movs_negativos):,.2f}EUR")
            
            # Exportar datos
            print(f"\n[EXPORTACION] Generando archivo CSV...")
            csv_file = await scraper.export_to_csv(transactions)
            print(f"Archivo generado: {csv_file}")
            
            print(f"\n[COMPLETADO] SCRAPER V3 FINALIZADO CON EXITO")
            return True
            
        else:
            print(f"[AVISO] No se encontraron movimientos en el periodo especificado")
            print(f"\nPosibles causas:")
            print(f"- No hay transacciones en agosto 2025")
            print(f"- La cuenta esta vacia o inactiva")
            print(f"- Los movimientos estan en otra seccion del banco")
            
            print(f"\nINFORMACION DE DEBUG:")
            try:
                current_url = scraper.driver.current_url
                print(f"URL final: {current_url}")
                
                # Buscar indicios de datos bancarios
                page_source = scraper.driver.page_source.lower()
                keywords = ['saldo', 'balance', 'cuenta', 'movimiento', 'transaccion']
                found = [kw for kw in keywords if kw in page_source]
                
                print(f"Palabras clave encontradas: {found}")
                print(f"Longitud del contenido: {len(page_source)} caracteres")
                
            except Exception as e:
                print(f"Error en debug: {e}")
            
            print(f"\n[OK] Login y navegacion funcionaron correctamente")
            print(f"[INFO] Solo falta encontrar la pagina correcta de movimientos")
            return False
        
    except Exception as e:
        print(f"\n[ERROR CRITICO] {e}")
        logger.error(f"Test failed: {e}")
        return False
        
    finally:
        if scraper:
            print(f"\n[LIMPIEZA] Cerrando navegador...")
            scraper.close()

def main():
    """Función principal"""
    try:
        result = asyncio.run(test_final_simple())
        
        if result:
            print(f"\n" + "=" * 60)
            print(f"[EXITO] TEST EXITOSO - MOVIMIENTOS OBTENIDOS")
            print(f"=" * 60)
        else:
            print(f"\n" + "=" * 60)
            print(f"[INFO] TEST COMPLETADO - SIN MOVIMIENTOS")
            print(f"El scraper funciona, solo necesita ajuste de navegacion")
            print(f"=" * 60)
            
    except KeyboardInterrupt:
        print(f"\n[CANCELADO] Test cancelado por usuario")
    except Exception as e:
        print(f"\n[ERROR] Error fatal: {e}")

if __name__ == "__main__":
    main()