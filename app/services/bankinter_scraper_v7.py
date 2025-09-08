#!/usr/bin/env python3
"""
Bankinter Scraper v7 - Con extracción correcta de importes
Corrige la lógica de parsing basada en posiciones de tabla específicas
"""

import asyncio
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import re
import time
import csv
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Importar el formateador
from .bankinter_excel_formatter import BankinterExcelFormatter, BankinterMovement
from .financial_agent_uploader import upload_bankinter_excel

logger = logging.getLogger(__name__)

@dataclass
class TransactionV7:
    date: date
    description: str
    amount: float
    balance: Optional[float] = None
    reference: Optional[str] = None

class BankinterScraperV7:
    """Scraper con extracción correcta de importes basada en estructura de tabla"""
    
    def __init__(self, username: str = None, password: str = None, 
                 agent_username: str = None, agent_password: str = None,
                 auto_upload: bool = False):
        self.username = username
        self.password = password
        self.agent_username = agent_username
        self.agent_password = agent_password
        self.auto_upload = auto_upload
        self.driver = None
        self.wait = None
        # URLs exactas del flujo correcto
        self.login_url = "https://bancaonline.bankinter.com/gestion/login.xhtml"
        self.post_login_url = "https://bancaonline.bankinter.com/extracto/secure/extracto_integral.xhtml"
        self.movements_url = "https://bancaonline.bankinter.com/extracto/secure/movimientos_cuenta.xhtml?INDEX_CTA=1&IND=C&TIPO=N"
        self.account_number = "ES0201280730910160000605"
        
        # Inicializar formateador
        self.formatter = BankinterExcelFormatter()
        
    def setup_driver(self) -> webdriver.Chrome:
        """Configuración robusta del WebDriver"""
        options = Options()
        
        # Anti-detección
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # User agent realista
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.139 Safari/537.36")
        
        # Configurar ventana
        options.add_argument("--window-size=1366,768")
        options.add_argument("--start-maximized")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Script anti-detección
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 15)
        return self.driver

    async def login(self) -> bool:
        """Login con flujo específico"""
        try:
            logger.info("=== LOGIN FLUJO EXACTO V7 ===")
            
            # 1. Navegar a login
            logger.info(f"Navegando a {self.login_url}")
            self.driver.get(self.login_url)
            await asyncio.sleep(3)
            
            # 2. Manejar cookies
            await self._handle_cookies()
            
            # 3. Completar login
            if not await self._complete_login():
                return False
            
            # 4. Verificar llegada a extracto_integral
            await asyncio.sleep(5)
            current_url = self.driver.current_url
            logger.info(f"URL post-login: {current_url}")
            
            if "extracto/secure/extracto_integral" in current_url:
                logger.info("Login exitoso - En extracto_integral")
                return True
            else:
                logger.warning(f"URL inesperada: {current_url}")
                self.driver.get(self.post_login_url)
                await asyncio.sleep(3)
                
                final_url = self.driver.current_url
                if "extracto/secure" in final_url:
                    logger.info("Navegación manual exitosa")
                    return True
                else:
                    logger.error("No se pudo llegar a extracto_integral")
                    return False
            
        except Exception as e:
            logger.error(f"Error en login: {e}")
            return False

    async def _handle_cookies(self):
        """Manejo de cookies"""
        try:
            await asyncio.sleep(2)
            
            cookie_selectors = [
                "//button[contains(text(), 'ACEPTAR')]",
                "//button[contains(text(), 'Aceptar')]",
                "#onetrust-accept-btn-handler"
            ]
            
            for selector in cookie_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if elements:
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                logger.info("Aceptando cookies")
                                element.click()
                                await asyncio.sleep(1)
                                return
                                
                except Exception:
                    continue
            
        except Exception as e:
            logger.warning(f"Error manejando cookies: {e}")

    async def _complete_login(self) -> bool:
        """Completar formulario de login"""
        try:
            # Buscar campos
            username_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='text']")
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            
            if not username_field or not password_field:
                logger.error("Campos de login no encontrados")
                return False
            
            # Completar credenciales
            logger.info("Completando credenciales...")
            username_field.clear()
            username_field.send_keys(self.username)
            await asyncio.sleep(0.5)
            
            password_field.clear()
            password_field.send_keys(self.password)
            await asyncio.sleep(0.5)
            
            # Buscar botón de login
            login_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Entrar')] | //button[@type='submit'] | //input[@type='submit']")
            
            if not login_buttons:
                logger.error("Botón de login no encontrado")
                return False
            
            logger.info("Haciendo clic en botón de login")
            login_buttons[0].click()
            
            return True
            
        except Exception as e:
            logger.error(f"Error completando login: {e}")
            return False

    async def navigate_to_movements(self) -> bool:
        """Navegación específica a movimientos_cuenta.xhtml"""
        try:
            logger.info("=== NAVEGANDO A MOVIMIENTOS V7 ===")
            
            current_url = self.driver.current_url
            logger.info(f"URL actual: {current_url}")
            
            # Navegar directamente a movimientos_cuenta.xhtml con refresh para datos actuales
            logger.info(f"Navegando a {self.movements_url}")
            self.driver.get(self.movements_url)
            await asyncio.sleep(8)
            
            # Forzar refresh para asegurar datos actualizados
            logger.info("Refrescando página para datos más recientes")
            self.driver.refresh()
            await asyncio.sleep(5)
            
            current_url = self.driver.current_url
            logger.info(f"URL después de navegación: {current_url}")
            
            # Verificar si llegamos a movimientos
            if "movimientos_cuenta" in current_url:
                logger.info("Navegación exitosa a movimientos_cuenta")
                self.driver.save_screenshot("movements_page_v7.png")
                return True
            
            logger.error("No se pudo navegar a movimientos")
            return False
            
        except Exception as e:
            logger.error(f"Error navegando a movimientos: {e}")
            return False

    async def extract_movements_correct_amounts(self) -> List[TransactionV7]:
        """Extraer movimientos con importes correctos basados en estructura específica"""
        try:
            logger.info("=== EXTRAYENDO MOVIMIENTOS CON IMPORTES CORRECTOS V7 ===")
            
            current_url = self.driver.current_url
            logger.info(f"Extrayendo de: {current_url}")
            
            # Tomar screenshot
            self.driver.save_screenshot("extraction_v7.png")
            
            transactions = []
            
            # Buscar la tabla principal de movimientos
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            logger.info(f"Tablas encontradas: {len(tables)}")
            
            for i, table in enumerate(tables):
                try:
                    # Verificar si la tabla contiene datos bancarios
                    table_text = table.text.lower()
                    if not any(keyword in table_text for keyword in ['fecha', 'importe', 'concepto', 'saldo']):
                        continue
                    
                    logger.info(f"Analizando tabla {i+1} con contenido bancario...")
                    
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    logger.info(f"Filas en tabla {i+1}: {len(rows)}")
                    
                    # Verificar header para confirmar estructura
                    if len(rows) > 0:
                        header_cells = rows[0].find_elements(By.TAG_NAME, "td")
                        if not header_cells:
                            header_cells = rows[0].find_elements(By.TAG_NAME, "th")
                        
                        if header_cells:
                            header_texts = [cell.text.strip() for cell in header_cells]
                            logger.info(f"Headers detectados: {header_texts}")
                    
                    for j, row in enumerate(rows[1:], 1):  # Saltar header
                        try:
                            # Buscar celdas
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if len(cells) < 4:  # Necesita al menos 4 celdas para la estructura esperada
                                continue
                            
                            # Extraer textos de celdas
                            cell_texts = [cell.text.strip() for cell in cells]
                            
                            # Verificar estructura esperada basada en debug:
                            # [0] = Vacía
                            # [1] = Fecha (27/08/2025)
                            # [2] = Concepto (Trans Inm/ Garcia Baena Jesus...)
                            # [3] = IMPORTE (+750,00 €)
                            # [4] = SALDO (2.092,81 €)
                            
                            # Extraer fecha (celda 1, índice 1)
                            if len(cell_texts) < 2:
                                continue
                                
                            date_text = cell_texts[1] if len(cell_texts) > 1 else ""
                            transaction_date = self._parse_bankinter_date(date_text)
                            
                            if not transaction_date:
                                continue
                            
                            # Filtrar solo transacciones recientes (últimos 3 meses para incluir septiembre)
                            from datetime import datetime
                            current_date = datetime.now()
                            months_diff = (current_date.year - transaction_date.year) * 12 + (current_date.month - transaction_date.month)
                            
                            # Debug: Log all dates being processed
                            # Debug: Log dates (removed for performance)
                            # logger.info(f"Procesando fecha: {transaction_date.strftime('%d/%m/%Y')}, diff_meses: {months_diff}")
                            
                            if months_diff > 3:  # Expandido a 3 meses para asegurar septiembre
                                logger.debug(f"Filtrando fecha antigua: {transaction_date.strftime('%d/%m/%Y')}")
                                continue
                            
                            # Extraer concepto (celda 2, índice 2)
                            concept = cell_texts[2] if len(cell_texts) > 2 else "MOVIMIENTO BANCARIO"
                            
                            # Extraer IMPORTE (celda 3, índice 3) - ESTE ES EL CAMBIO CLAVE
                            amount_text = cell_texts[3] if len(cell_texts) > 3 else ""
                            amount = self._parse_bankinter_amount_correct(amount_text)
                            
                            if amount is None:
                                logger.debug(f"No se pudo parsear importe de: '{amount_text}'")
                                continue
                            
                            # Extraer SALDO (celda 4, índice 4)
                            balance_text = cell_texts[4] if len(cell_texts) > 4 else ""
                            balance = self._parse_bankinter_amount_correct(balance_text)
                            
                            # Crear transacción
                            transaction = TransactionV7(
                                date=transaction_date,
                                description=concept,
                                amount=amount,
                                balance=balance
                            )
                            
                            transactions.append(transaction)
                            # Simplified logging to avoid Unicode issues
                            logger.info(f"Movimiento V7: {transaction_date.strftime('%d/%m/%Y')} - {amount:.2f}€")
                            
                        except Exception as e:
                            logger.debug(f"Error procesando fila {j}: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error procesando tabla {i}: {e}")
                    continue
            
            logger.info(f"Total movimientos extraídos V7: {len(transactions)}")
            
            # Debug: Analyze date distribution
            if transactions:
                from collections import defaultdict
                date_counts = defaultdict(int)
                for mov in transactions:
                    month_key = f"{mov.date.year}-{mov.date.month:02d}"
                    date_counts[month_key] += 1
                
                logger.info("Distribución por meses:")
                for month, count in sorted(date_counts.items()):
                    logger.info(f"  {month}: {count} movimientos")
                
                # Check for September specifically
                sept_count = sum(1 for mov in transactions if mov.date.year == 2025 and mov.date.month == 9)
                aug_count = sum(1 for mov in transactions if mov.date.year == 2025 and mov.date.month == 8)
                logger.info(f"SEPTIEMBRE 2025: {sept_count} movimientos")
                logger.info(f"AGOSTO 2025: {aug_count} movimientos")
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error extrayendo movimientos V7: {e}")
            return []

    def _parse_bankinter_date(self, date_text: str) -> Optional[date]:
        """Parsear fecha específica de Bankinter"""
        if not date_text:
            return None
        
        # Buscar patrón dd/mm/yyyy en el texto
        date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_text)
        if date_match:
            try:
                day, month, year = map(int, date_match.groups())
                return date(year, month, day)
            except ValueError:
                pass
        
        return None

    def _parse_bankinter_amount_correct(self, amount_text: str) -> Optional[float]:
        """Parsear importe específico de Bankinter con formato correcto"""
        if not amount_text:
            return None
        
        # Remover espacios extra y €
        clean_text = amount_text.replace(' ', '').replace('€', '').strip()
        
        # Patrones específicos observados en debug:
        # +750,00 → +750.00
        # -770,67 → -770.67
        # 2.092,81 → 2092.81 (saldo con separador de miles)
        
        # Patrón 1: +/-XXX,XX (importe simple)
        simple_pattern = r'^([+-]?\d+),(\d{2})$'
        match = re.match(simple_pattern, clean_text)
        if match:
            try:
                integer_part = match.group(1)
                decimal_part = match.group(2)
                amount_str = f"{integer_part}.{decimal_part}"
                return float(amount_str)
            except ValueError:
                pass
        
        # Patrón 2: +/-X.XXX,XX (con separador de miles)
        thousands_pattern = r'^([+-]?)(\d{1,3})\.(\d{3}),(\d{2})$'
        match = re.match(thousands_pattern, clean_text)
        if match:
            try:
                sign = match.group(1)
                thousands = match.group(2)
                hundreds = match.group(3)
                decimals = match.group(4)
                
                # Construir número sin separador de miles
                integer_part = f"{thousands}{hundreds}"
                amount_str = f"{sign}{integer_part}.{decimals}"
                return float(amount_str)
            except ValueError:
                pass
        
        # Patrón 3: XXX,XX (sin signo)
        unsigned_pattern = r'^(\d+),(\d{2})$'
        match = re.match(unsigned_pattern, clean_text)
        if match:
            try:
                integer_part = match.group(1)
                decimal_part = match.group(2)
                amount_str = f"{integer_part}.{decimal_part}"
                return float(amount_str)
            except ValueError:
                pass
        
        # Patrón 4: X.XXX,XX (saldo con separador de miles sin signo)
        balance_pattern = r'^(\d{1,3})\.(\d{3}),(\d{2})$'
        match = re.match(balance_pattern, clean_text)
        if match:
            try:
                thousands = match.group(1)
                hundreds = match.group(2)
                decimals = match.group(3)
                
                integer_part = f"{thousands}{hundreds}"
                amount_str = f"{integer_part}.{decimals}"
                return float(amount_str)
            except ValueError:
                pass
        
        logger.debug(f"No se pudo parsear importe: '{clean_text}' de texto original: '{amount_text}'")
        return None

    async def get_august_movements_corrected(self) -> tuple[List[TransactionV7], str, str]:
        """Obtener movimientos de agosto 2025 con importes correctos"""
        try:
            logger.info("=== OBTENIENDO MOVIMIENTOS CORREGIDOS V7 ===")
            
            # 1. Login
            if not await self.login():
                logger.error("Login fallido")
                return [], "", ""
            
            # 2. Navegar a movimientos
            if not await self.navigate_to_movements():
                logger.error("Navegación fallida")
                return [], "", ""
            
            # 3. Extraer movimientos con importes correctos
            transactions = await self.extract_movements_correct_amounts()
            
            if not transactions:
                logger.warning("No se encontraron movimientos")
                return [], "", ""
            
            # 4. Convertir a formato BankinterMovement para el formateador
            bankinter_movements = []
            for t in transactions:
                bm = BankinterMovement(
                    fecha=t.date,
                    concepto=t.description,
                    importe=t.amount,
                    saldo=t.balance or 0.0
                )
                bankinter_movements.append(bm)
            
            # 5. Transformar al formato del agente financiero
            financial_movements = self.formatter.transform_movements(bankinter_movements)
            
            # 6. Mostrar preview
            print("\nPREVIEW DE DATOS CORREGIDOS:")
            print("-" * 60)
            print(f"{'Fecha':<12} {'Concepto':<30} {'Importe Real':<15} {'Saldo':<15}")
            print("-" * 60)
            
            for i, t in enumerate(transactions[:10], 1):
                fecha = t.date.strftime('%d/%m/%Y')
                # Clean concept for safe printing
                try:
                    concepto_clean = t.description.encode('ascii', 'ignore').decode('ascii')
                    concepto = concepto_clean[:27] + "..." if len(concepto_clean) > 30 else concepto_clean
                except:
                    concepto = "CONCEPTO_UNICODE"
                importe = f"{t.amount:+,.2f}€"
                saldo = f"{t.balance:,.2f}€" if t.balance else "N/A"
                
                print(f"{fecha:<12} {concepto:<30} {importe:<15} {saldo:<15}")
            
            # 7. Exportar en ambos formatos
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Formato Excel para visualización (formato español con comas)
            excel_file = self.formatter.export_to_excel(financial_movements, f"bankinter_corregido_{timestamp}.xlsx")
            
            # Formato Excel para API (formato americano con puntos) - PARA SUBIDA AUTOMÁTICA
            api_excel_file = self.formatter.export_to_excel_for_api(bankinter_movements, f"bankinter_api_{timestamp}.xlsx")
            
            # Formato CSV tabulado para agente financiero
            csv_file = self.formatter.export_to_csv_formatted(financial_movements, f"bankinter_corregido_{timestamp}.csv")
            
            logger.info(f"Exportado Excel visualización: {excel_file}")
            logger.info(f"Exportado Excel API: {api_excel_file}")
            logger.info(f"Exportado CSV: {csv_file}")
            
            # 8. Subida automática al agente financiero si está habilitada
            upload_result = None
            if self.auto_upload and self.agent_username and self.agent_password:
                try:
                    print(f"\n=== SUBIDA AUTOMÁTICA AL AGENTE FINANCIERO ===")
                    print(f"Usuario: {self.agent_username}")
                    print(f"Archivo para subida: {api_excel_file} (formato americano)")
                    print(f"Archivo para visualización: {excel_file} (formato español)")
                    
                    upload_result = await upload_bankinter_excel(
                        excel_file_path=api_excel_file,  # ¡USAR ARCHIVO API!
                        username=self.agent_username,
                        password=self.agent_password
                    )
                    
                    print(f"\n✓ SUBIDA EXITOSA:")
                    print(f"  - Movimientos nuevos: {upload_result['new_movements_created']}")
                    print(f"  - Duplicados omitidos: {upload_result['duplicates_skipped']}")
                    print(f"  - Total procesados: {upload_result['total_rows_processed']}")
                    print(f"  - Movimientos existentes: {upload_result['existing_movements_found']}")
                    
                except Exception as e:
                    logger.error(f"Error en subida automática: {e}")
                    print(f"\n❌ ERROR EN SUBIDA AUTOMÁTICA: {e}")
                    print("Los archivos se han generado correctamente, pero la subida falló.")
            
            return transactions, excel_file, api_excel_file, csv_file, upload_result
            
        except Exception as e:
            logger.error(f"Error obteniendo movimientos corregidos: {e}")
            return [], "", "", "", None

    def close(self):
        """Cerrar navegador"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass