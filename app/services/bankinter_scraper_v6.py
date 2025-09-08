#!/usr/bin/env python3
"""
Bankinter Scraper v6 - Con extracción de saldo y formateo Excel
Extrae datos en formato compatible con agente financiero
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
from .bankinter_excel_formatter import BankinterExcelFormatter, BankinterMovement, convert_scraper_to_bankinter_movements

logger = logging.getLogger(__name__)

@dataclass
class TransactionV6:
    date: date
    description: str
    amount: float
    balance: Optional[float] = None
    reference: Optional[str] = None

class BankinterScraperV6:
    """Scraper con extracción de saldo y formateo Excel"""
    
    def __init__(self, username: str = None, password: str = None):
        self.username = username
        self.password = password
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
            logger.info("=== LOGIN FLUJO EXACTO V6 ===")
            
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
            logger.info("=== NAVEGANDO A MOVIMIENTOS V6 ===")
            
            current_url = self.driver.current_url
            logger.info(f"URL actual: {current_url}")
            
            # Navegar directamente a movimientos_cuenta.xhtml
            logger.info(f"Navegando a {self.movements_url}")
            self.driver.get(self.movements_url)
            await asyncio.sleep(5)
            
            current_url = self.driver.current_url
            logger.info(f"URL después de navegación: {current_url}")
            
            # Verificar si llegamos a movimientos
            if "movimientos_cuenta" in current_url:
                logger.info("Navegación exitosa a movimientos_cuenta")
                self.driver.save_screenshot("movements_page_v6.png")
                return True
            
            logger.error("No se pudo navegar a movimientos")
            return False
            
        except Exception as e:
            logger.error(f"Error navegando a movimientos: {e}")
            return False

    async def extract_movements_with_balance(self) -> List[TransactionV6]:
        """Extraer movimientos con saldo de la tabla de Bankinter"""
        try:
            logger.info("=== EXTRAYENDO MOVIMIENTOS CON SALDO V6 ===")
            
            current_url = self.driver.current_url
            logger.info(f"Extrayendo de: {current_url}")
            
            # Tomar screenshot
            self.driver.save_screenshot("extraction_v6.png")
            
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
                    
                    for j, row in enumerate(rows):
                        try:
                            # Buscar celdas
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if len(cells) < 3:  # Necesita al menos fecha, concepto, importe
                                continue
                            
                            cell_texts = [cell.text.strip() for cell in cells]
                            
                            # Extraer fecha (buscar en las primeras celdas)
                            transaction_date = None
                            date_text = ""
                            
                            for cell_text in cell_texts[:2]:  # Buscar fecha en las primeras 2 celdas
                                if self._contains_date(cell_text):
                                    transaction_date = self._parse_bankinter_date(cell_text)
                                    date_text = cell_text
                                    break
                            
                            if not transaction_date:
                                continue
                            
                            # Filtrar solo agosto 2025
                            if transaction_date.year != 2025 or transaction_date.month != 8:
                                continue
                            
                            # Extraer concepto (celda con más texto, que no sea fecha ni número)
                            concept = ""
                            for cell_text in cell_texts:
                                if (cell_text and 
                                    not self._contains_date(cell_text) and 
                                    not self._is_amount(cell_text) and
                                    len(cell_text) > len(concept)):
                                    concept = cell_text
                            
                            if not concept:
                                concept = "MOVIMIENTO BANCARIO"
                            
                            # Extraer importe y saldo (buscar números con formato €)
                            amount = None
                            balance = None
                            
                            amounts_found = []
                            for cell_text in cell_texts:
                                parsed_amount = self._parse_bankinter_amount(cell_text)
                                if parsed_amount is not None:
                                    amounts_found.append(parsed_amount)
                            
                            # El primer número suele ser el importe, el segundo el saldo
                            if len(amounts_found) >= 2:
                                amount = amounts_found[0]
                                balance = amounts_found[1]
                            elif len(amounts_found) == 1:
                                amount = amounts_found[0]
                                balance = None
                            else:
                                continue  # Sin importe, saltar
                            
                            # Crear transacción
                            transaction = TransactionV6(
                                date=transaction_date,
                                description=concept,
                                amount=amount,
                                balance=balance
                            )
                            
                            transactions.append(transaction)
                            logger.info(f"Movimiento: {transaction_date.strftime('%d/%m/%Y')} - {concept[:30]} - {amount:.2f}€ (Saldo: {balance:.2f}€ if balance else 'N/A')")
                            
                        except Exception as e:
                            logger.debug(f"Error procesando fila {j}: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error procesando tabla {i}: {e}")
                    continue
            
            logger.info(f"Total movimientos extraídos: {len(transactions)}")
            return transactions
            
        except Exception as e:
            logger.error(f"Error extrayendo movimientos: {e}")
            return []

    def _contains_date(self, text: str) -> bool:
        """Verificar si el texto contiene una fecha"""
        if not text:
            return False
        
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',  # dd/mm/yyyy
            r'\d{4}-\d{1,2}-\d{1,2}',  # yyyy-mm-dd
            r'(lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo)',  # días de semana
        ]
        
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in date_patterns)

    def _parse_bankinter_date(self, date_text: str) -> Optional[date]:
        """Parsear fecha específica de Bankinter (puede incluir día de semana)"""
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
        
        # Buscar patrón yyyy-mm-dd
        date_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_text)
        if date_match:
            try:
                year, month, day = map(int, date_match.groups())
                return date(year, month, day)
            except ValueError:
                pass
        
        return None

    def _is_amount(self, text: str) -> bool:
        """Verificar si el texto es un importe"""
        if not text:
            return False
        
        # Buscar patrones de dinero
        money_patterns = [
            r'[+-]?\d+[\s,\.]\d{2}\s*€',
            r'[+-]?\d+,\d{2}',
            r'[+-]?\d+\.\d{2}'
        ]
        
        return any(re.search(pattern, text) for pattern in money_patterns)

    def _parse_bankinter_amount(self, amount_text: str) -> Optional[float]:
        """Parsear importe específico de Bankinter"""
        if not amount_text:
            return None
        
        # Remover espacios y €
        clean_text = amount_text.replace(' ', '').replace('€', '').strip()
        
        # Buscar patrón de número con formato europeo (coma decimal)
        # +750,00 o -770,67 o 1.234,56
        money_patterns = [
            r'([+-]?\d{1,3}(?:\.\d{3})*),(\d{2})',  # 1.234,56 o +750,00
            r'([+-]?\d+),(\d{2})',  # 123,45
            r'([+-]?\d+)\.(\d{2})',  # 123.45 (formato anglosajon)
            r'([+-]?\d+)',  # Solo enteros
        ]
        
        for pattern in money_patterns:
            match = re.search(pattern, clean_text)
            if match:
                try:
                    if len(match.groups()) == 2:
                        # Formato con decimales
                        integer_part = match.group(1).replace('.', '')  # Remover separador de miles
                        decimal_part = match.group(2)
                        amount_str = f"{integer_part}.{decimal_part}"
                    else:
                        # Solo enteros
                        amount_str = match.group(1).replace('.', '')
                    
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None

    async def get_august_movements_formatted(self) -> tuple[List[TransactionV6], str, str]:
        """Obtener movimientos de agosto 2025 y exportar en ambos formatos"""
        try:
            logger.info("=== OBTENIENDO MOVIMIENTOS FORMATEADOS ===")
            
            # 1. Login
            if not await self.login():
                logger.error("Login fallido")
                return [], "", ""
            
            # 2. Navegar a movimientos
            if not await self.navigate_to_movements():
                logger.error("Navegación fallida")
                return [], "", ""
            
            # 3. Extraer movimientos con saldo
            transactions = await self.extract_movements_with_balance()
            
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
            self.formatter.preview_transformation(bankinter_movements, num_examples=5)
            
            # 7. Exportar en ambos formatos
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Formato Excel para agente financiero
            excel_file = self.formatter.export_to_excel(financial_movements, f"bankinter_agente_financiero_{timestamp}.xlsx")
            
            # Formato CSV tabulado para agente financiero
            csv_file = self.formatter.export_to_csv_formatted(financial_movements, f"bankinter_agente_financiero_{timestamp}.csv")
            
            logger.info(f"Exportado Excel: {excel_file}")
            logger.info(f"Exportado CSV: {csv_file}")
            
            return transactions, excel_file, csv_file
            
        except Exception as e:
            logger.error(f"Error obteniendo movimientos formateados: {e}")
            return [], "", ""

    def close(self):
        """Cerrar navegador"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass