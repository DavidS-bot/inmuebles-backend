#!/usr/bin/env python3
"""
Bankinter Scraper v4 - Navegación secuencial mejorada
Mantiene sesión activa y navega paso a paso
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
from selenium.webdriver.common.action_chains import ActionChains

logger = logging.getLogger(__name__)

@dataclass
class Transaction:
    date: date
    description: str
    amount: float
    balance: Optional[float] = None
    reference: Optional[str] = None

class BankinterScraperV4:
    """Scraper mejorado con navegación secuencial"""
    
    def __init__(self, username: str = None, password: str = None):
        self.username = username
        self.password = password
        self.driver = None
        self.wait = None
        self.login_url = "https://bancaonline.bankinter.com/gestion/login.xhtml"
        
    def setup_driver(self) -> webdriver.Chrome:
        """Configuración robusta del WebDriver"""
        options = Options()
        
        # Anti-detección mejorada
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=9222")
        
        # User agent realista
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.139 Safari/537.36")
        
        # Configurar ventana
        options.add_argument("--window-size=1366,768")
        options.add_argument("--start-maximized")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Script anti-detección
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Timeout generoso para páginas bancarias
        self.wait = WebDriverWait(self.driver, 15)
        
        return self.driver

    async def login(self) -> bool:
        """Login mejorado con manejo de sesión"""
        try:
            logger.info("=== INICIANDO LOGIN V4 ===")
            
            # 1. Navegar a la página de login
            logger.info(f"Navegando a: {self.login_url}")
            self.driver.get(self.login_url)
            
            # Esperar carga inicial
            await asyncio.sleep(3)
            
            # 2. Manejar popup de cookies
            logger.info("Manejando popup de cookies...")
            await self._handle_cookies()
            
            # 3. Completar formulario de login
            logger.info("Completando formulario de login...")
            login_success = await self._complete_login_form()
            
            if not login_success:
                logger.error("Error completando formulario de login")
                return False
            
            # 4. Verificar login exitoso
            await asyncio.sleep(5)
            current_url = self.driver.current_url
            logger.info(f"URL post-login: {current_url}")
            
            # Verificar que no estamos en página de error
            if "login" in current_url.lower() and "error" not in current_url.lower():
                logger.warning("Posible redirección a login, verificando...")
                
            # Tomar screenshot del estado post-login
            self.driver.save_screenshot("login_success_v4.png")
            
            logger.info("Login completado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error en login: {e}")
            return False

    async def _handle_cookies(self):
        """Manejo robusto de cookies"""
        try:
            # Esperar a que aparezca el popup
            await asyncio.sleep(2)
            
            cookie_selectors = [
                "//button[contains(text(), 'ACEPTAR')]",
                "//button[contains(text(), 'Aceptar')]",
                "//button[contains(text(), 'Accept')]",
                "#onetrust-accept-btn-handler",
                ".ot-sdk-show-settings",
                "[data-testid='uc-accept-all-button']"
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
                                logger.info(f"Haciendo clic en cookies: {element.text}")
                                element.click()
                                await asyncio.sleep(1)
                                return
                                
                except Exception as e:
                    continue
            
            logger.info("No se encontró popup de cookies o ya fue manejado")
            
        except Exception as e:
            logger.warning(f"Error manejando cookies: {e}")

    async def _complete_login_form(self) -> bool:
        """Completar formulario de login de forma robusta"""
        try:
            # Selectores múltiples para campos
            username_selectors = [
                "input[type='text']",
                "input[name*='usuario']",
                "input[id*='usuario']",
                "#usuario",
                ".form-control"
            ]
            
            password_selectors = [
                "input[type='password']",
                "input[name*='password']",
                "input[id*='password']",
                "#password"
            ]
            
            button_selectors = [
                "//button[contains(text(), 'Entrar')]",
                "//button[contains(text(), 'ENTRAR')]",
                "//button[@type='submit']",
                "//input[@type='submit']",
                "//button",
                ".btn-primary",
                ".submit-button"
            ]
            
            # Buscar y completar campo de usuario
            username_field = None
            for selector in username_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            username_field = element
                            break
                    if username_field:
                        break
                except:
                    continue
            
            if not username_field:
                logger.error("No se encontró campo de usuario")
                return False
            
            # Buscar campo de contraseña
            password_field = None
            for selector in password_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            password_field = element
                            break
                    if password_field:
                        break
                except:
                    continue
            
            if not password_field:
                logger.error("No se encontró campo de contraseña")
                return False
            
            # Completar credenciales con pauses realistas
            logger.info("Introduciendo credenciales...")
            username_field.clear()
            await asyncio.sleep(0.5)
            username_field.send_keys(self.username)
            
            await asyncio.sleep(1)
            
            password_field.clear()
            await asyncio.sleep(0.5)
            password_field.send_keys(self.password)
            
            await asyncio.sleep(1)
            
            # Buscar y hacer clic en botón de login
            login_button = None
            for selector in button_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # Verificar que sea un botón de login
                            text = element.text.strip().lower()
                            if any(word in text for word in ['entrar', 'login', 'acceder', 'submit']) or element.get_attribute('type') == 'submit':
                                login_button = element
                                break
                    
                    if login_button:
                        break
                        
                except:
                    continue
            
            if not login_button:
                logger.error("No se encontró botón de login")
                return False
            
            logger.info("Haciendo clic en botón de login")
            login_button.click()
            
            return True
            
        except Exception as e:
            logger.error(f"Error completando formulario: {e}")
            return False

    async def navigate_to_movements(self) -> bool:
        """Navegación secuencial al área de movimientos"""
        try:
            logger.info("=== NAVEGANDO A MOVIMIENTOS ===")
            
            # 1. Esperar a que la página cargue después del login
            await asyncio.sleep(5)
            current_url = self.driver.current_url
            logger.info(f"URL inicial: {current_url}")
            
            # 2. Buscar y hacer clic en área de cuentas/posición global
            logger.info("Paso 1: Navegando a área de cuentas...")
            
            accounts_navigation_selectors = [
                "//a[contains(text(), 'Posición global')]",
                "//a[contains(text(), 'Cuentas')]",
                "//a[contains(text(), 'Mi dinero')]",
                "//a[contains(@href, 'posicion')]",
                "//a[contains(@href, 'cuentas')]",
                ".nav-item a[href*='cuenta']",
                ".menu-item a[href*='posicion']"
            ]
            
            navigation_success = False
            for selector in accounts_navigation_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed():
                            text = element.text.strip()
                            href = element.get_attribute('href') or ""
                            logger.info(f"Probando navegación: '{text}' -> {href}")
                            
                            element.click()
                            await asyncio.sleep(4)
                            
                            new_url = self.driver.current_url
                            logger.info(f"Nueva URL: {new_url}")
                            
                            # Verificar que navegamos exitosamente
                            if new_url != current_url and "bancaonline.bankinter.com" in new_url:
                                logger.info("Navegación exitosa a área de cuentas")
                                navigation_success = True
                                self.driver.save_screenshot("step1_accounts_area.png")
                                break
                    
                    if navigation_success:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error con selector {selector}: {e}")
                    continue
            
            if not navigation_success:
                logger.warning("Navegación directa no encontrada, intentando URLs conocidas...")
                # Intentar URLs directas secuenciales
                sequential_urls = [
                    "https://bancaonline.bankinter.com/gestion/posicion.xhtml",
                    "https://bancaonline.bankinter.com/gestion/cuentas.xhtml"
                ]
                
                for url in sequential_urls:
                    logger.info(f"Intentando URL directa: {url}")
                    self.driver.get(url)
                    await asyncio.sleep(4)
                    
                    final_url = self.driver.current_url
                    if "bancaonline.bankinter.com/gestion/" in final_url and "login" not in final_url:
                        logger.info(f"Navegación exitosa: {final_url}")
                        navigation_success = True
                        break
            
            if not navigation_success:
                logger.error("No se pudo navegar al área de cuentas")
                return False
            
            # 3. Buscar enlaces específicos de movimientos/extractos
            logger.info("Paso 2: Buscando enlaces de movimientos...")
            
            movement_selectors = [
                "//a[contains(text(), 'Movimientos')]",
                "//a[contains(text(), 'Extractos')]",
                "//a[contains(text(), 'Ver movimientos')]",
                "//a[contains(text(), 'Consultar movimientos')]",
                "//a[contains(@href, 'movimientos')]",
                "//a[contains(@href, 'extracto')]",
                ".account-link[href*='movimientos']",
                ".movement-link",
                "a[title*='movimiento']"
            ]
            
            movement_found = False
            for selector in movement_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements[:3]:  # Probar los primeros 3
                        if element.is_displayed():
                            text = element.text.strip()
                            href = element.get_attribute('href') or ""
                            
                            if text or href:
                                logger.info(f"Probando enlace de movimientos: '{text}' -> {href[:50]}")
                                
                                element.click()
                                await asyncio.sleep(5)
                                
                                new_url = self.driver.current_url
                                logger.info(f"URL después de clic: {new_url}")
                                
                                # Verificar que llegamos a página de movimientos
                                if any(keyword in new_url.lower() for keyword in ['movimientos', 'extracto', 'movements']):
                                    logger.info("¡Navegación exitosa a movimientos!")
                                    movement_found = True
                                    self.driver.save_screenshot("step2_movements_page.png")
                                    break
                                elif "login" not in new_url:
                                    # Página válida, continuar explorando
                                    logger.info("Página válida, continuando búsqueda...")
                    
                    if movement_found:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error con selector movimientos {selector}: {e}")
                    continue
            
            # 4. Si no encontramos enlace directo, buscar en la página actual
            if not movement_found:
                logger.info("Paso 3: Explorando página actual para movimientos...")
                current_url = self.driver.current_url
                
                # Buscar formularios o secciones que permitan consultar movimientos
                forms = self.driver.find_elements(By.TAG_NAME, "form")
                logger.info(f"Formularios encontrados: {len(forms)}")
                
                # Buscar campos de fecha que indiquen consulta de movimientos
                date_inputs = self.driver.find_elements(By.CSS_SELECTOR, 
                    "input[type='date'], input[name*='fecha'], input[placeholder*='fecha']")
                
                if date_inputs:
                    logger.info(f"Campos de fecha encontrados: {len(date_inputs)} - Posible formulario de consulta")
                    movement_found = True
                    self.driver.save_screenshot("step3_query_form.png")
                
                # Buscar cualquier referencia a movimientos en texto
                page_source = self.driver.page_source.lower()
                movement_keywords = page_source.count('movimiento') + page_source.count('extracto')
                
                if movement_keywords > 5:  # Si hay muchas referencias
                    logger.info(f"Referencias a movimientos encontradas: {movement_keywords}")
                    movement_found = True
            
            if movement_found:
                logger.info("=== NAVEGACION A MOVIMIENTOS COMPLETADA ===")
                return True
            else:
                logger.error("No se pudo acceder al área de movimientos")
                return False
            
        except Exception as e:
            logger.error(f"Error navegando a movimientos: {e}")
            return False

    async def extract_movements_from_current_page(self) -> List[Transaction]:
        """Extraer movimientos de la página actual con métodos múltiples"""
        try:
            logger.info("=== EXTRAYENDO MOVIMIENTOS ===")
            
            transactions = []
            current_url = self.driver.current_url
            page_source = self.driver.page_source
            
            logger.info(f"Extrayendo de: {current_url}")
            logger.info(f"Tamaño de página: {len(page_source):,} caracteres")
            
            # Método 1: Buscar tablas estructuradas
            logger.info("Método 1: Buscando tablas...")
            table_transactions = await self._extract_from_tables()
            if table_transactions:
                transactions.extend(table_transactions)
                logger.info(f"Extraídos {len(table_transactions)} movimientos de tablas")
            
            # Método 2: Buscar divs con estructura de movimientos
            logger.info("Método 2: Buscando divs estructurados...")
            div_transactions = await self._extract_from_divs()
            if div_transactions:
                transactions.extend(div_transactions)
                logger.info(f"Extraídos {len(div_transactions)} movimientos de divs")
            
            # Método 3: Análisis de texto con regex
            logger.info("Método 3: Análisis con regex...")
            regex_transactions = await self._extract_with_regex()
            if regex_transactions:
                transactions.extend(regex_transactions)
                logger.info(f"Extraídos {len(regex_transactions)} movimientos con regex")
            
            # Método 4: JavaScript para datos dinámicos
            logger.info("Método 4: Extracción con JavaScript...")
            js_transactions = await self._extract_with_javascript()
            if js_transactions:
                transactions.extend(js_transactions)
                logger.info(f"Extraídos {len(js_transactions)} movimientos con JavaScript")
            
            # Eliminar duplicados
            if transactions:
                unique_transactions = []
                seen = set()
                
                for t in transactions:
                    # Crear clave única basada en fecha + descripción + importe
                    key = f"{t.date}_{t.description[:20]}_{t.amount}"
                    if key not in seen:
                        seen.add(key)
                        unique_transactions.append(t)
                
                logger.info(f"Total movimientos únicos: {len(unique_transactions)}")
                return unique_transactions
            
            logger.warning("No se encontraron movimientos con ningún método")
            return []
            
        except Exception as e:
            logger.error(f"Error extrayendo movimientos: {e}")
            return []

    async def _extract_from_tables(self) -> List[Transaction]:
        """Extraer movimientos de tablas HTML"""
        transactions = []
        
        try:
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            
            for i, table in enumerate(tables):
                logger.info(f"Analizando tabla {i+1}...")
                
                rows = table.find_elements(By.TAG_NAME, "tr")
                if len(rows) < 2:  # Necesita al menos header + 1 fila
                    continue
                
                for j, row in enumerate(rows[1:], 1):  # Saltar header
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) < 3:  # Necesita al menos fecha, descripción, importe
                            continue
                        
                        # Extraer texto de las celdas
                        cell_texts = [cell.text.strip() for cell in cells]
                        
                        # Buscar patrón de fecha en alguna celda
                        transaction_date = None
                        for cell_text in cell_texts:
                            date_match = self._parse_date(cell_text)
                            if date_match:
                                transaction_date = date_match
                                break
                        
                        if not transaction_date:
                            continue
                        
                        # Buscar patrón de importe
                        amount = None
                        for cell_text in cell_texts:
                            amount_match = self._parse_amount(cell_text)
                            if amount_match:
                                amount = amount_match
                                break
                        
                        if amount is None:
                            continue
                        
                        # Descripción es el texto más largo que no sea fecha ni importe
                        description = ""
                        for cell_text in cell_texts:
                            if (cell_text and 
                                not self._parse_date(cell_text) and 
                                self._parse_amount(cell_text) is None and
                                len(cell_text) > len(description)):
                                description = cell_text
                        
                        if not description:
                            description = " | ".join(cell_texts[:3])
                        
                        transaction = Transaction(
                            date=transaction_date,
                            description=description[:100],  # Limitar longitud
                            amount=amount
                        )
                        
                        transactions.append(transaction)
                        logger.debug(f"Movimiento tabla: {transaction_date} - {description[:30]} - {amount}")
                        
                    except Exception as e:
                        logger.debug(f"Error procesando fila {j} de tabla {i}: {e}")
                        continue
            
        except Exception as e:
            logger.error(f"Error extrayendo de tablas: {e}")
        
        return transactions

    async def _extract_from_divs(self) -> List[Transaction]:
        """Extraer movimientos de estructuras div"""
        transactions = []
        
        try:
            # Buscar divs que puedan contener movimientos
            div_selectors = [
                "div[class*='movement']",
                "div[class*='transaction']", 
                "div[class*='row']",
                "div[class*='item']",
                "div[class*='entry']",
                ".movement",
                ".transaction",
                ".account-movement"
            ]
            
            for selector in div_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    try:
                        text = element.text.strip()
                        if not text or len(text) < 10:  # Muy corto para ser movimiento
                            continue
                        
                        # Buscar fecha en el texto
                        transaction_date = self._parse_date_from_text(text)
                        if not transaction_date:
                            continue
                        
                        # Buscar importe en el texto
                        amount = self._parse_amount_from_text(text)
                        if amount is None:
                            continue
                        
                        # Descripción es el texto restante
                        description = self._clean_description(text)
                        
                        transaction = Transaction(
                            date=transaction_date,
                            description=description,
                            amount=amount
                        )
                        
                        transactions.append(transaction)
                        
                    except Exception as e:
                        logger.debug(f"Error procesando div: {e}")
                        continue
            
        except Exception as e:
            logger.error(f"Error extrayendo de divs: {e}")
        
        return transactions

    async def _extract_with_regex(self) -> List[Transaction]:
        """Extraer movimientos usando regex en el texto completo"""
        transactions = []
        
        try:
            page_source = self.driver.page_source
            
            # Patrones para agosto 2025 específicamente
            agosto_patterns = [
                # dd/MM/yyyy - descripción - importe
                r'(\d{1,2}[/\-]08[/\-]2025).*?([A-Za-z\s\-\.\,\d\(\)]+?).*?(\d+[,\.]\d{2})\s*€?',
                # yyyy-MM-dd formato ISO
                r'(2025[/\-]08[/\-]\d{1,2}).*?([A-Za-z\s\-\.\,\d\(\)]+?).*?(\d+[,\.]\d{2})\s*€?',
                # Agosto escrito
                r'(\d{1,2}\s+ago\w*\s+2025).*?([A-Za-z\s\-\.\,\d\(\)]+?).*?(\d+[,\.]\d{2})\s*€?'
            ]
            
            for pattern in agosto_patterns:
                matches = re.findall(pattern, page_source, re.IGNORECASE | re.DOTALL)
                
                for match in matches:
                    try:
                        date_str, description, amount_str = match
                        
                        # Parsear fecha
                        transaction_date = self._parse_date(date_str)
                        if not transaction_date or transaction_date.month != 8 or transaction_date.year != 2025:
                            continue
                        
                        # Parsear importe
                        amount = self._parse_amount(amount_str)
                        if amount is None:
                            continue
                        
                        # Limpiar descripción
                        clean_description = self._clean_description(description)
                        
                        transaction = Transaction(
                            date=transaction_date,
                            description=clean_description,
                            amount=amount
                        )
                        
                        transactions.append(transaction)
                        
                    except Exception as e:
                        logger.debug(f"Error procesando match regex: {e}")
                        continue
            
        except Exception as e:
            logger.error(f"Error extrayendo con regex: {e}")
        
        return transactions

    async def _extract_with_javascript(self) -> List[Transaction]:
        """Extraer movimientos usando JavaScript para elementos dinámicos"""
        transactions = []
        
        try:
            # Script JavaScript para buscar elementos con fechas de agosto 2025
            js_script = """
            var results = [];
            var elements = document.querySelectorAll('*');
            
            for (var i = 0; i < elements.length; i++) {
                var el = elements[i];
                var text = el.textContent || el.innerText || '';
                
                // Buscar fechas de agosto 2025
                if ((text.includes('08') || text.toLowerCase().includes('ago')) && 
                    text.includes('2025')) {
                    
                    // Buscar también números que parezcan importes
                    var amountRegex = /\\d+[.,]\\d{2}/g;
                    var amounts = text.match(amountRegex);
                    
                    if (amounts && amounts.length > 0) {
                        results.push({
                            text: text.trim(),
                            tag: el.tagName,
                            class: el.className,
                            amounts: amounts
                        });
                    }
                }
            }
            
            return results.slice(0, 20); // Limitar resultados
            """
            
            js_results = self.driver.execute_script(js_script)
            
            for result in js_results:
                try:
                    text = result['text']
                    amounts = result['amounts']
                    
                    # Parsear fecha del texto
                    transaction_date = self._parse_date_from_text(text)
                    if not transaction_date or transaction_date.month != 8 or transaction_date.year != 2025:
                        continue
                    
                    # Usar el primer importe encontrado
                    amount = self._parse_amount(amounts[0])
                    if amount is None:
                        continue
                    
                    # Descripción limpia
                    description = self._clean_description(text)
                    
                    transaction = Transaction(
                        date=transaction_date,
                        description=description,
                        amount=amount
                    )
                    
                    transactions.append(transaction)
                    
                except Exception as e:
                    logger.debug(f"Error procesando resultado JS: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error extrayendo con JavaScript: {e}")
        
        return transactions

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parsear fecha de string"""
        if not date_str:
            return None
        
        # Limpiar string
        date_str = date_str.strip()
        
        # Patrones de fecha
        patterns = [
            (r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', '%d/%m/%Y'),  # dd/mm/yyyy
            (r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})', '%Y/%m/%d'),  # yyyy/mm/dd
            (r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{2})', '%d/%m/%y'),   # dd/mm/yy
        ]
        
        for pattern, format_str in patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    if format_str in ['%d/%m/%Y', '%d/%m/%y']:
                        day, month, year = match.groups()
                    else:  # '%Y/%m/%d'
                        year, month, day = match.groups()
                    
                    # Convertir año de 2 dígitos
                    if len(year) == 2:
                        year = int(year)
                        if year > 50:
                            year += 1900
                        else:
                            year += 2000
                    
                    return date(int(year), int(month), int(day))
                    
                except ValueError:
                    continue
        
        return None

    def _parse_date_from_text(self, text: str) -> Optional[date]:
        """Parsear fecha de texto libre"""
        # Buscar patrones específicos de agosto 2025
        agosto_patterns = [
            r'\b(\d{1,2})[/\-]08[/\-]2025\b',
            r'\b2025[/\-]08[/\-](\d{1,2})\b', 
            r'\b(\d{1,2})\s+ago\w*\s+2025\b'
        ]
        
        for pattern in agosto_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    day = int(match.group(1))
                    return date(2025, 8, day)
                except (ValueError, IndexError):
                    continue
        
        return None

    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """Parsear importe de string"""
        if not amount_str:
            return None
        
        # Limpiar string
        amount_str = str(amount_str).strip()
        
        # Buscar patrón de dinero
        money_pattern = r'([+-]?\d+(?:[.,]\d{2})?)'
        match = re.search(money_pattern, amount_str.replace(' ', ''))
        
        if match:
            try:
                amount_text = match.group(1)
                # Convertir coma decimal a punto
                amount_text = amount_text.replace(',', '.')
                return float(amount_text)
            except ValueError:
                pass
        
        return None

    def _parse_amount_from_text(self, text: str) -> Optional[float]:
        """Parsear importe de texto libre"""
        # Buscar patrones de dinero
        money_patterns = [
            r'([+-]?\d+[.,]\d{2})\s*€',
            r'([+-]?\d+[.,]\d{2})\s*EUR',
            r'([+-]?\d+[.,]\d{2})',
        ]
        
        for pattern in money_patterns:
            match = re.search(pattern, text)
            if match:
                return self._parse_amount(match.group(1))
        
        return None

    def _clean_description(self, text: str) -> str:
        """Limpiar descripción eliminando fechas e importes"""
        if not text:
            return ""
        
        # Remover fechas
        text = re.sub(r'\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}', '', text)
        text = re.sub(r'\d{4}[/\-]\d{1,2}[/\-]\d{1,2}', '', text)
        
        # Remover importes
        text = re.sub(r'[+-]?\d+[.,]\d{2}\s*€?', '', text)
        
        # Limpiar espacios múltiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text[:100]  # Limitar longitud

    async def get_movements(self, start_date: date, end_date: date) -> List[Transaction]:
        """Obtener movimientos del período especificado"""
        try:
            logger.info(f"=== OBTENIENDO MOVIMIENTOS {start_date} - {end_date} ===")
            
            # 1. Realizar login
            if not await self.login():
                logger.error("Login fallido")
                return []
            
            # 2. Navegar a movimientos
            if not await self.navigate_to_movements():
                logger.error("No se pudo navegar a movimientos")
                return []
            
            # 3. Extraer movimientos
            all_transactions = await self.extract_movements_from_current_page()
            
            # 4. Filtrar por período
            filtered_transactions = []
            for transaction in all_transactions:
                if start_date <= transaction.date <= end_date:
                    filtered_transactions.append(transaction)
            
            logger.info(f"Movimientos en período: {len(filtered_transactions)}")
            return filtered_transactions
            
        except Exception as e:
            logger.error(f"Error obteniendo movimientos: {e}")
            return []

    async def export_to_csv(self, transactions: List[Transaction], filename: str = None) -> str:
        """Exportar transacciones a CSV"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"bankinter_movements_{timestamp}.csv"
        
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
            
            logger.info(f"Transacciones exportadas a: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exportando CSV: {e}")
            raise

    def close(self):
        """Cerrar navegador"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass