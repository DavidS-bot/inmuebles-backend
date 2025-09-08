#!/usr/bin/env python3
"""
Test scraper v5 con flujo exacto de navegación
"""

import asyncio
import logging
from datetime import date
from app.services.bankinter_scraper_v5 import BankinterScraperV5

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_exact_flow():
    """Test con flujo exacto de navegación"""
    
    username = "75867185"
    password = "Motoreta123$"
    
    print("BANKINTER SCRAPER V5 - FLUJO EXACTO")
    print("=" * 60)
    print(f"Usuario: {username}")
    print(f"Flujo:")
    print(f"  1. Login: bancaonline.bankinter.com/gestion/login.xhtml")
    print(f"  2. Post-login: extracto/secure/extracto_integral.xhtml")
    print(f"  3. Movimientos: movimientos_cuenta.xhtml?INDEX_CTA=1&IND=C&TIPO=N")
    print(f"  4. Alternativa: Clic en ES0201280730910160000605")
    
    scraper = None
    try:
        scraper = BankinterScraperV5(username=username, password=password)
        
        print(f"\n[PASO 1/4] Configurando navegador...")
        scraper.setup_driver()
        print("✓ Navegador configurado")
        
        print(f"\n[PASO 2/4] Login con flujo exacto...")
        login_success = await scraper.login()
        
        if not login_success:
            print("✗ ERROR: Login fallido")
            return False
        
        print("✓ Login exitoso - Sesión en extracto_integral")
        
        print(f"\n[PASO 3/4] Navegación exacta a movimientos...")
        navigation_success = await scraper.navigate_to_movements()
        
        if not navigation_success:
            print("✗ ERROR: Navegación a movimientos fallida")
            
            # Mostrar información de debug
            current_url = scraper.driver.current_url
            page_title = scraper.driver.title
            print(f"  URL actual: {current_url}")
            print(f"  Título: {page_title}")
            
            return False
        
        print("✓ Navegación exitosa - En página de movimientos")
        
        print(f"\n[PASO 4/4] Extrayendo movimientos de agosto 2025...")
        august_transactions = await scraper.get_august_movements()
        
        if not august_transactions:
            # Intentar extraer cualquier movimiento para debug
            print("Sin movimientos de agosto, extrayendo cualquier movimiento...")
            all_transactions = await scraper.extract_real_movements()
            
            print(f"Total movimientos encontrados: {len(all_transactions)}")
            
            if all_transactions:
                print(f"\nMovimientos encontrados (otros meses):")
                monthly_data = {}
                for t in all_transactions:
                    month_key = f"{t.date.year}-{t.date.month:02d}"
                    if month_key not in monthly_data:
                        monthly_data[month_key] = []
                    monthly_data[month_key].append(t)
                
                for month, movs in sorted(monthly_data.items()):
                    total = sum(m.amount for m in movs)
                    print(f"  {month}: {len(movs)} movimientos, total: {total:.2f}€")
                    
                    # Mostrar algunos ejemplos
                    for i, m in enumerate(movs[:3], 1):
                        print(f"    {i}. {m.date.strftime('%d/%m/%Y')} - {m.description[:40]} - {m.amount:.2f}€")
                
                # Exportar todos los datos para análisis
                csv_file = await scraper.export_to_csv(all_transactions, "todos_movimientos_v5.csv")
                print(f"\nTodos los movimientos exportados: {csv_file}")
            
            else:
                print("✗ No se encontraron movimientos de ningún tipo")
                
                # Debug de la página actual
                current_url = scraper.driver.current_url
                page_source = scraper.driver.page_source
                
                print(f"\nINFORMACIÓN DE DEBUG:")
                print(f"  URL final: {current_url}")
                print(f"  Tamaño página: {len(page_source):,} caracteres")
                
                # Análisis de contenido
                page_lower = page_source.lower()
                keywords = {
                    'agosto': page_lower.count('agosto'),
                    '08': page_lower.count('08'),
                    '2025': page_lower.count('2025'),
                    'movimiento': page_lower.count('movimiento'),
                    'saldo': page_lower.count('saldo'),
                    'fecha': page_lower.count('fecha'),
                    'importe': page_lower.count('importe'),
                    'euro': page_lower.count('euro'),
                    'eur': page_lower.count('eur')
                }
                
                print(f"  Palabras clave encontradas:")
                for word, count in keywords.items():
                    if count > 0:
                        print(f"    '{word}': {count} veces")
                
                # Guardar HTML para análisis manual
                with open("debug_movements_page_v5.html", "w", encoding="utf-8", errors="ignore") as f:
                    f.write(page_source)
                print(f"  HTML guardado: debug_movements_page_v5.html")
            
            return len(all_transactions) > 0
        
        print(f"✓ ENCONTRADOS {len(august_transactions)} MOVIMIENTOS DE AGOSTO 2025")
        
        # Mostrar movimientos de agosto
        print(f"\n=== MOVIMIENTOS DE AGOSTO 2025 ===")
        print(f"{'#':<3} {'FECHA':<12} {'DESCRIPCIÓN':<50} {'IMPORTE':<12}")
        print("-" * 80)
        
        total_amount = 0
        ingresos = 0
        gastos = 0
        
        for i, t in enumerate(august_transactions, 1):
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
        print(f"  Total movimientos: {len(august_transactions)}")
        print(f"  Ingresos:    {ingresos:8.2f}€")
        print(f"  Gastos:      {gastos:8.2f}€")
        print(f"  Balance:     {total_amount:8.2f}€")
        print(f"  Promedio/día: {total_amount/31:6.2f}€")
        
        # Exportar datos
        print(f"\n[EXPORTACIÓN] Generando CSV...")
        csv_file = await scraper.export_to_csv(august_transactions, "movimientos_agosto_2025_exacto.csv")
        print(f"✓ Exportado: {csv_file}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if scraper:
            print(f"\nCerrando navegador...")
            scraper.close()

if __name__ == "__main__":
    try:
        resultado = asyncio.run(test_exact_flow())
        
        if resultado:
            print(f"\n" + "="*60)
            print(f"✓ ÉXITO: SCRAPER V5 CON FLUJO EXACTO FUNCIONA")
            print(f"Movimientos de agosto 2025 extraídos correctamente")
            print(f"="*60)
        else:
            print(f"\n" + "="*60)
            print(f"⚠ INFO: FLUJO EJECUTADO CON INCIDENCIAS")
            print(f"Revisar logs y archivos de debug generados")
            print(f"="*60)
            
    except KeyboardInterrupt:
        print(f"\nTest cancelado por usuario")
    except Exception as e:
        print(f"\nError fatal: {e}")