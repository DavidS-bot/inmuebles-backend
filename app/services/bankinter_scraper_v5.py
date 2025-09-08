#!/usr/bin/env python3
"""
Bankinter Scraper v5 - Flujo exacto de navegación
Sigue el flujo específico: login -> extracto_integral -> movimientos_cuenta
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

logger = logging.getLogger(__name__)

@dataclass
class Transaction:
    date: date
    description: str
    amount: float
    balance: Optional[float] = None
    reference: Optional[str] = None

class BankinterScraperV5:
    """Scraper con flujo exacto de navegación"""
    
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
            logger.info("=== LOGIN FLUJO EXACTO ===")
            
            # 1. Navegar a login
            logger.info(f"Paso 1: Navegando a {self.login_url}")
            self.driver.get(self.login_url)
            await asyncio.sleep(3)
            
            # 2. Manejar cookies
            logger.info("Paso 2: Manejando cookies...")
            await self._handle_cookies()
            
            # 3. Completar login
            logger.info("Paso 3: Completando login...")
            if not await self._complete_login():
                return False
            
            # 4. Verificar llegada a extracto_integral
            await asyncio.sleep(5)
            current_url = self.driver.current_url
            logger.info(f"Paso 4: URL post-login: {current_url}")
            
            # Verificar que llegamos a la página correcta
            if "extracto/secure/extracto_integral" in current_url:
                logger.info("✓ Login exitoso - En extracto_integral como esperado")
                self.driver.save_screenshot("login_success_v5.png")
                return True
            else:
                logger.warning(f"URL inesperada post-login: {current_url}")
                # Intentar navegar manualmente a extracto_integral
                logger.info("Intentando navegar a extracto_integral...")
                self.driver.get(self.post_login_url)
                await asyncio.sleep(3)
                
                final_url = self.driver.current_url
                if "extracto/secure" in final_url:
                    logger.info("✓ Navegación manual exitosa")
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
                "#onetrust-accept-btn-handler",
                ".ot-sdk-show-settings"
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
                                logger.info(f"Aceptando cookies: {element.text}")
                                element.click()
                                await asyncio.sleep(1)
                                return
                                
                except Exception:
                    continue
            
            logger.info("No se encontró popup de cookies")
            
        except Exception as e:
            logger.warning(f"Error manejando cookies: {e}")

    async def _complete_login(self) -> bool:
        """Completar formulario de login"""
        try:
            # Buscar campo de usuario
            username_selectors = [
                "input[type='text']",
                "input[name*='usuario']",
                "#usuario"
            ]
            
            username_field = None
            for selector in username_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        username_field = element
                        break
                if username_field:
                    break
            
            if not username_field:
                logger.error("Campo de usuario no encontrado")
                return False
            
            # Buscar campo de contraseña
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            
            if not password_field:
                logger.error("Campo de contraseña no encontrado")
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
            button_selectors = [
                "//button[contains(text(), 'Entrar')]",
                "//button[@type='submit']",
                "//input[@type='submit']",
                "//button"
            ]
            
            login_button = None
            for selector in button_selectors:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        text = element.text.strip().lower()
                        if 'entrar' in text or element.get_attribute('type') == 'submit':
                            login_button = element
                            break
                if login_button:
                    break
            
            if not login_button:
                logger.error("Botón de login no encontrado")
                return False
            
            logger.info("Haciendo clic en botón de login")
            login_button.click()
            
            return True
            
        except Exception as e:
            logger.error(f"Error completando login: {e}")
            return False

    async def navigate_to_movements(self) -> bool:
        """Navegación específica a movimientos_cuenta.xhtml"""
        try:
            logger.info("=== NAVEGANDO A MOVIMIENTOS EXACTO ===")
            
            current_url = self.driver.current_url
            logger.info(f"URL actual: {current_url}")
            
            # Verificar que estamos en extracto_integral
            if "extracto_integral" not in current_url:
                logger.warning("No estamos en extracto_integral, navegando...")
                self.driver.get(self.post_login_url)
                await asyncio.sleep(4)
                current_url = self.driver.current_url
                logger.info(f"Nueva URL: {current_url}")
            
            # Método 1: Navegar directamente a movimientos_cuenta.xhtml
            logger.info(f"Método 1: Navegación directa a {self.movements_url}")
            self.driver.get(self.movements_url)
            await asyncio.sleep(5)
            
            current_url = self.driver.current_url
            logger.info(f"URL después de navegación directa: {current_url}")
            
            # Verificar si llegamos a movimientos
            if "movimientos_cuenta" in current_url:
                logger.info("✓ Navegación directa exitosa a movimientos_cuenta")
                self.driver.save_screenshot("movements_page_v5.png")
                return True
            
            # Verificar si nos redirigieron al login (sesión expiró)
            if "login" in current_url:
                logger.warning("Redirigido a login - sesión expirada")
                return False
            
            # Método 2: Buscar y hacer clic en el número de cuenta
            logger.info(f"Método 2: Buscando número de cuenta {self.account_number}")
            
            # Navegar de vuelta a extracto_integral
            self.driver.get(self.post_login_url)
            await asyncio.sleep(4)
            
            # Buscar el número de cuenta
            account_selectors = [
                f"//a[contains(text(), '{self.account_number}')]",
                f"//span[contains(text(), '{self.account_number}')]//ancestor::a",
                f"//td[contains(text(), '{self.account_number}')]//ancestor::a",
                f"//*[contains(text(), '{self.account_number}')]"
            ]
            
            account_found = False
            for selector in account_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    
                    if elements:
                        logger.info(f"Encontrado número de cuenta con selector: {selector}")
                        
                        for element in elements:
                            if element.is_displayed():
                                text = element.text.strip()
                                logger.info(f"Elemento encontrado: '{text}'")
                                
                                # Si es un enlace, hacer clic
                                if element.tag_name.lower() == 'a' or element.find_elements(By.XPATH, ".//ancestor::a"):
                                    logger.info("Haciendo clic en número de cuenta...")
                                    element.click()
                                    await asyncio.sleep(5)
                                    
                                    new_url = self.driver.current_url
                                    logger.info(f"URL después del clic: {new_url}")
                                    
                                    if "movimientos" in new_url or "extracto" in new_url:
                                        logger.info("✓ Navegación por número de cuenta exitosa")
                                        self.driver.save_screenshot("movements_via_account_v5.png")
                                        account_found = True
                                        break
                        
                        if account_found:
                            break
                            
                except Exception as e:
                    logger.debug(f"Error con selector {selector}: {e}")
                    continue
            
            if account_found:
                return True
            
            # Método 3: Buscar enlaces de movimientos en la página
            logger.info("Método 3: Buscando enlaces de movimientos...")
            
            movement_selectors = [
                "//a[contains(@href, 'movimientos')]",
                "//a[contains(text(), 'Movimientos')]",
                "//a[contains(text(), 'Ver movimientos')]",
                "//a[contains(@href, 'extracto')]"
            ]
            
            for selector in movement_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    
                    for element in elements:
                        if element.is_displayed():
                            text = element.text.strip()
                            href = element.get_attribute('href') or ""
                            
                            logger.info(f"Probando enlace: '{text}' -> {href}")
                            element.click()
                            await asyncio.sleep(4)
                            
                            new_url = self.driver.current_url
                            if "movimientos" in new_url:
                                logger.info("✓ Navegación por enlace exitosa")
                                return True
                            
                except Exception as e:
                    logger.debug(f"Error con enlace: {e}")
                    continue
            
            logger.error("No se pudo navegar a movimientos con ningún método")
            return False
            
        except Exception as e:
            logger.error(f"Error navegando a movimientos: {e}")
            return False

    async def extract_real_movements(self) -> List[Transaction]:
        """Extraer movimientos reales de la página específica de movimientos"""
        try:
            logger.info("=== EXTRAYENDO MOVIMIENTOS REALES ===")
            
            current_url = self.driver.current_url
            page_source = self.driver.page_source
            
            logger.info(f"Extrayendo de: {current_url}")
            logger.info(f"Tamaño página: {len(page_source):,} caracteres")
            
            # Tomar screenshot para análisis
            self.driver.save_screenshot("extraction_page_v5.png")
            
            transactions = []
            
            # Método 1: Buscar tablas estructuradas de movimientos
            logger.info("Buscando tablas de movimientos...")
            table_transactions = await self._extract_from_movement_tables()
            if table_transactions:
                transactions.extend(table_transactions)
                logger.info(f"Extraídos {len(table_transactions)} de tablas")
            
            # Método 2: Buscar estructura específica de Bankinter
            logger.info("Buscando estructura específica de Bankinter...")
            bankinter_transactions = await self._extract_bankinter_structure()
            if bankinter_transactions:
                transactions.extend(bankinter_transactions)
                logger.info(f"Extraídos {len(bankinter_transactions)} de estructura Bankinter")
            
            # Método 3: Análisis con regex específico para agosto
            logger.info("Análisis con regex para agosto 2025...")
            regex_transactions = await self._extract_august_regex()
            if regex_transactions:
                transactions.extend(regex_transactions)
                logger.info(f"Extraídos {len(regex_transactions)} con regex agosto")
            
            # Eliminar duplicados
            unique_transactions = self._remove_duplicates(transactions)
            
            logger.info(f"Total movimientos únicos extraídos: {len(unique_transactions)}")
            return unique_transactions
            
        except Exception as e:
            logger.error(f"Error extrayendo movimientos: {e}")
            return []

    async def _extract_from_movement_tables(self) -> List[Transaction]:
        """Extraer de tablas específicas de movimientos"""
        transactions = []
        
        try:
            # Buscar tablas que contengan movimientos
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
                    
                    for j, row in enumerate(rows):
                        try:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if len(cells) < 3:
                                continue
                            
                            cell_texts = [cell.text.strip() for cell in cells]
                            
                            # Buscar fecha de agosto 2025
                            transaction_date = None
                            for cell_text in cell_texts:
                                if self._is_august_2025_date(cell_text):
                                    transaction_date = self._parse_date(cell_text)
                                    break
                            
                            if not transaction_date:
                                continue
                            
                            # Buscar importe
                            amount = None
                            for cell_text in cell_texts:
                                parsed_amount = self._parse_amount(cell_text)
                                if parsed_amount is not None:
                                    amount = parsed_amount
                                    break
                            
                            if amount is None:
                                continue
                            
                            # Descripción
                            description = self._extract_description(cell_texts, transaction_date, amount)
                            
                            transaction = Transaction(
                                date=transaction_date,
                                description=description,
                                amount=amount
                            )
                            
                            transactions.append(transaction)
                            logger.info(f"Movimiento tabla: {transaction_date.strftime('%d/%m/%Y')} - {description[:30]} - {amount:.2f}€")
                            
                        except Exception as e:
                            logger.debug(f"Error procesando fila {j}: {e}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Error procesando tabla {i}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error extrayendo de tablas: {e}")
        
        return transactions

    async def _extract_bankinter_structure(self) -> List[Transaction]:
        """Extraer usando estructura específica de Bankinter"""
        transactions = []
        
        try:
            # Buscar elementos con clases específicas de Bankinter
            bankinter_selectors = [
                ".movimiento", ".transaction", ".movimento",
                ".row-movimiento", ".lista-movimientos tr",
                "tbody tr", ".table-movimientos tr"
            ]
            
            for selector in bankinter_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        text = element.text.strip()
                        
                        # Verificar si contiene fecha de agosto 2025
                        if not self._contains_august_2025(text):
                            continue
                        
                        # Extraer datos del texto
                        transaction_date = self._extract_date_from_text(text)
                        if not transaction_date:
                            continue
                        
                        amount = self._extract_amount_from_text(text)
                        if amount is None:
                            continue
                        
                        description = self._clean_description_text(text)
                        
                        transaction = Transaction(
                            date=transaction_date,
                            description=description,
                            amount=amount
                        )
                        
                        transactions.append(transaction)
                        
                except Exception as e:
                    logger.debug(f"Error con selector {selector}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error extrayendo estructura Bankinter: {e}")
        
        return transactions

    async def _extract_august_regex(self) -> List[Transaction]:
        """Extraer usando regex específico para agosto 2025"""
        transactions = []
        
        try:
            page_source = self.driver.page_source
            
            # Patrones específicos para agosto 2025
            august_patterns = [
                # Formato español: dd/08/2025
                r'(\d{1,2})/08/2025[^0-9]*([^0-9]+?)[^0-9]*([+-]?\d+[,\.]\d{2})',
                # Formato ISO: 2025-08-dd
                r'2025-08-(\d{1,2})[^0-9]*([^0-9]+?)[^0-9]*([+-]?\d+[,\.]\d{2})',
                # Formato con mes escrito
                r'(\d{1,2})[^0-9]*agosto[^0-9]*2025[^0-9]*([^0-9]+?)[^0-9]*([+-]?\d+[,\.]\d{2})'
            ]
            
            for pattern in august_patterns:
                matches = re.finditer(pattern, page_source, re.IGNORECASE | re.DOTALL)
                
                for match in matches:
                    try:
                        groups = match.groups()
                        
                        if len(groups) == 3:
                            day_str, description, amount_str = groups
                            day = int(day_str)
                            transaction_date = date(2025, 8, day)
                        else:
                            continue
                        
                        # Parsear importe
                        amount = self._parse_amount(amount_str)
                        if amount is None:
                            continue
                        
                        # Limpiar descripción
                        clean_desc = self._clean_description_text(description)
                        
                        transaction = Transaction(
                            date=transaction_date,
                            description=clean_desc,
                            amount=amount
                        )
                        
                        transactions.append(transaction)
                        
                    except Exception as e:
                        logger.debug(f"Error procesando match regex: {e}")
                        continue
            
        except Exception as e:
            logger.error(f"Error con regex agosto: {e}")
        
        return transactions

    def _is_august_2025_date(self, text: str) -> bool:
        """Verificar si el texto contiene una fecha de agosto 2025"""
        if not text:
            return False
        
        august_patterns = [
            r'\d{1,2}/08/2025',
            r'2025-08-\d{1,2}',
            r'\d{1,2}\s+ago\w*\s+2025'
        ]
        
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in august_patterns)

    def _contains_august_2025(self, text: str) -> bool:
        """Verificar si el texto contiene referencias a agosto 2025"""
        return ('08' in text or 'agosto' in text.lower()) and '2025' in text

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parsear fecha específicamente para agosto 2025"""
        if not date_str:
            return None
        
        # Patrones para agosto 2025
        patterns = [
            (r'(\d{1,2})/08/2025', lambda m: date(2025, 8, int(m.group(1)))),
            (r'2025-08-(\d{1,2})', lambda m: date(2025, 8, int(m.group(1)))),
            (r'(\d{1,2})\s+ago\w*\s+2025', lambda m: date(2025, 8, int(m.group(1))))
        ]
        
        for pattern, parser in patterns:
            match = re.search(pattern, date_str, re.IGNORECASE)
            if match:
                try:
                    return parser(match)
                except (ValueError, IndexError):
                    continue
        
        return None

    def _extract_date_from_text(self, text: str) -> Optional[date]:
        """Extraer fecha de texto libre"""
        august_patterns = [
            r'(\d{1,2})/08/2025',
            r'2025-08-(\d{1,2})',
            r'(\d{1,2})\s+ago\w*\s+2025'
        ]
        
        for pattern in august_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    day = int(match.group(1))
                    if 1 <= day <= 31:
                        return date(2025, 8, day)
                except (ValueError, IndexError):
                    continue
        
        return None

    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """Parsear importe"""
        if not amount_str:
            return None
        
        # Limpiar y buscar patrón de dinero
        clean_str = str(amount_str).strip()
        
        # Patrones de dinero
        money_patterns = [
            r'([+-]?\d{1,3}(?:[.,]\d{3})*[,\.]\d{2})',  # 1.234,56 o 1,234.56
            r'([+-]?\d+[,\.]\d{2})',  # 123,45 o 123.45
            r'([+-]?\d+)',  # Solo números enteros
        ]
        
        for pattern in money_patterns:
            match = re.search(pattern, clean_str)
            if match:
                try:
                    amount_text = match.group(1)
                    # Normalizar formato decimal
                    if ',' in amount_text and '.' in amount_text:
                        # Formato 1.234,56
                        amount_text = amount_text.replace('.', '').replace(',', '.')
                    elif amount_text.count(',') == 1 and len(amount_text.split(',')[1]) == 2:
                        # Formato 123,45
                        amount_text = amount_text.replace(',', '.')
                    
                    return float(amount_text)
                except ValueError:
                    continue
        
        return None

    def _extract_amount_from_text(self, text: str) -> Optional[float]:
        """Extraer importe de texto"""
        return self._parse_amount(text)

    def _extract_description(self, cell_texts: List[str], transaction_date: date, amount: float) -> str:
        """Extraer descripción de las celdas"""
        description_parts = []
        
        for cell_text in cell_texts:
            # Omitir celdas que contienen fecha o importe
            if (self._parse_date(cell_text) or 
                self._parse_amount(cell_text) is not None):
                continue
            
            if cell_text and len(cell_text.strip()) > 0:
                description_parts.append(cell_text.strip())
        
        return " | ".join(description_parts) if description_parts else "Movimiento bancario"

    def _clean_description_text(self, text: str) -> str:
        """Limpiar texto de descripción"""
        if not text:
            return "Movimiento bancario"
        
        # Remover fechas
        text = re.sub(r'\d{1,2}/08/2025', '', text)
        text = re.sub(r'2025-08-\d{1,2}', '', text)
        
        # Remover importes
        text = re.sub(r'[+-]?\d+[,\.]\d{2}', '', text)
        
        # Remover caracteres especiales y limpiar espacios
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text[:100] if text else "Movimiento bancario"

    def _remove_duplicates(self, transactions: List[Transaction]) -> List[Transaction]:
        """Eliminar transacciones duplicadas"""
        unique_transactions = []
        seen = set()
        
        for t in transactions:
            # Crear clave única
            key = f"{t.date}_{t.description[:20]}_{t.amount}"
            if key not in seen:
                seen.add(key)
                unique_transactions.append(t)
        
        return unique_transactions

    async def get_august_movements(self) -> List[Transaction]:
        """Obtener movimientos específicos de agosto 2025"""
        try:
            logger.info("=== OBTENIENDO MOVIMIENTOS DE AGOSTO 2025 ===")
            
            # 1. Login
            if not await self.login():
                logger.error("Login fallido")
                return []
            
            # 2. Navegar a movimientos
            if not await self.navigate_to_movements():
                logger.error("Navegación a movimientos fallida")
                return []
            
            # 3. Extraer movimientos
            transactions = await self.extract_real_movements()
            
            # 4. Filtrar solo agosto 2025
            august_transactions = [
                t for t in transactions 
                if t.date.year == 2025 and t.date.month == 8
            ]
            
            logger.info(f"Movimientos de agosto 2025: {len(august_transactions)}")
            return august_transactions
            
        except Exception as e:
            logger.error(f"Error obteniendo movimientos de agosto: {e}")
            return []

    async def export_to_csv(self, transactions: List[Transaction], filename: str = None) -> str:
        """Exportar a CSV"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"bankinter_agosto_2025_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Header
                writer.writerow(['Fecha', 'Descripción', 'Importe', 'Saldo', 'Referencia'])
                
                # Datos
                for t in transactions:
                    writer.writerow([
                        t.date.strftime('%d/%m/%Y'),
                        t.description,
                        f"{t.amount:.2f}",
                        f"{t.balance:.2f}" if t.balance else "",
                        t.reference or ""
                    ])
            
            logger.info(f"Datos exportados a: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exportando: {e}")
            raise

    def close(self):
        """Cerrar navegador"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass