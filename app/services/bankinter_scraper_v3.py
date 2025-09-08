#!/usr/bin/env python3
"""
Bankinter Scraper v3 - Versión final para movimientos reales
Navega a través de la interfaz real de usuario
"""

import asyncio
import logging
import time
from datetime import datetime, date, timedelta
from typing import List, Optional
from dataclasses import dataclass

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

class BankinterScraperV3:
    """Scraper final para movimientos bancarios reales"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.driver = None
        self.wait = None
        self.login_url = "https://bancaonline.bankinter.com/gestion/login.xhtml"
        
    def setup_driver(self):
        """Configuración optimizada del WebDriver"""
        options = Options()
        
        # Configuración anti-detección
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Configuración de privacidad y rendimiento
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.cookies": 1,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        })
        
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.driver = driver
            self.wait = WebDriverWait(driver, 15)
            return driver
            
        except Exception as e:
            logger.error(f"Error configurando WebDriver: {e}")
            raise

    async def login(self) -> bool:
        """Login mejorado con verificación"""
        try:
            logger.info("=== INICIANDO LOGIN ===")
            
            if not self.driver:
                self.setup_driver()
                
            # Ir a la página de login
            logger.info(f"Navegando a: {self.login_url}")
            self.driver.get(self.login_url)
            await asyncio.sleep(3)
            
            # Manejar cookies
            logger.info("Manejando popup de cookies...")
            await self._handle_cookies()
            
            # Completar formulario de login
            logger.info("Completando formulario de login...")
            if not await self._fill_login_form():
                return False
            
            # Verificar login exitoso
            logger.info("Verificando login...")
            if await self._verify_login():
                logger.info("✅ LOGIN EXITOSO")
                return True
            else:
                logger.error("❌ LOGIN FALLIDO")
                return False
                
        except Exception as e:
            logger.error(f"Error durante login: {e}")
            return False

    async def _handle_cookies(self):
        """Manejo mejorado de cookies"""
        try:
            await asyncio.sleep(2)
            
            # Buscar y hacer clic en ACEPTAR
            cookie_selectors = [
                "//button[text()='ACEPTAR']",
                "//button[contains(text(), 'ACEPTAR')]",
                "//button[contains(text(), 'Aceptar')]"
            ]
            
            for selector in cookie_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            logger.info(f"Haciendo clic en cookies: {element.text}")
                            element.click()
                            await asyncio.sleep(1)
                            return True
                except:
                    continue
                    
            # Fallback con JavaScript
            js_click = """
            document.querySelectorAll('button').forEach(btn => {
                if(btn.textContent.includes('ACEPTAR')) btn.click()
            })
            """
            self.driver.execute_script(js_click)
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.debug(f"Error manejando cookies: {e}")

    async def _fill_login_form(self) -> bool:
        """Completar formulario de login"""
        try:
            # Selectores múltiples para campos
            username_selectors = [
                (By.ID, "loginForm:usuario"),
                (By.XPATH, "//input[@placeholder='Usuario']"),
                (By.CSS_SELECTOR, "input[type='text']")
            ]
            
            password_selectors = [
                (By.ID, "loginForm:password"),
                (By.XPATH, "//input[@placeholder='Contraseña']"),
                (By.CSS_SELECTOR, "input[type='password']")
            ]
            
            button_selectors = [
                (By.ID, "loginForm:entrar"),
                (By.XPATH, "//button[contains(text(), 'INICIAR')]"),
                (By.CSS_SELECTOR, "button")
            ]
            
            # Buscar campo usuario
            username_field = None
            for by_type, selector in username_selectors:
                try:
                    username_field = self.wait.until(EC.presence_of_element_located((by_type, selector)))
                    logger.info(f"Campo usuario encontrado: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not username_field:
                raise Exception("Campo usuario no encontrado")
            
            # Buscar campo contraseña
            password_field = None
            for by_type, selector in password_selectors:
                try:
                    password_field = self.driver.find_element(by_type, selector)
                    logger.info(f"Campo contraseña encontrado: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not password_field:
                raise Exception("Campo contraseña no encontrado")
            
            # Completar credenciales
            logger.info("Introduciendo credenciales...")
            username_field.clear()
            username_field.send_keys(self.username)
            await asyncio.sleep(0.5)
            
            password_field.clear()
            password_field.send_keys(self.password)
            await asyncio.sleep(0.5)
            
            # Buscar y hacer clic en botón
            login_button = None
            for by_type, selector in button_selectors:
                try:
                    if by_type == By.CSS_SELECTOR and selector == "button":
                        buttons = self.driver.find_elements(by_type, selector)
                        for btn in buttons:
                            if btn.is_displayed() and btn.is_enabled():
                                btn_text = btn.text.upper()
                                if any(word in btn_text for word in ["INICIAR", "ENTRAR", "LOGIN"]):
                                    login_button = btn
                                    logger.info(f"Botón encontrado: {btn.text}")
                                    break
                        if login_button:
                            break
                    else:
                        login_button = self.driver.find_element(by_type, selector)
                        if login_button.is_displayed():
                            logger.info(f"Botón encontrado: {selector}")
                            break
                except:
                    continue
            
            if login_button:
                login_button.click()
                logger.info("Click en botón de login realizado")
                await asyncio.sleep(3)
                return True
            else:
                raise Exception("Botón de login no encontrado")
            
        except Exception as e:
            logger.error(f"Error completando formulario: {e}")
            return False

    async def _verify_login(self) -> bool:
        """Verificar que el login fue exitoso"""
        try:
            await asyncio.sleep(3)
            
            # Indicadores de login exitoso
            success_indicators = [
                "bienvenido", "welcome", "posición", "cuentas", 
                "saldo", "logout", "cerrar sesión"
            ]
            
            current_url = self.driver.current_url.lower()
            page_source = self.driver.page_source.lower()
            
            # Verificar URL (no debe contener 'login' o 'error')
            if "login" not in current_url and "error" not in current_url and "notfound" not in current_url:
                # Verificar contenido de la página
                for indicator in success_indicators:
                    if indicator in page_source:
                        logger.info(f"Login verificado por indicador: {indicator}")
                        return True
            
            # Screenshot para debug
            self.driver.save_screenshot("login_verification.png")
            logger.info(f"URL actual: {current_url}")
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando login: {e}")
            return False

    async def get_real_movements(self, start_date: date = None, end_date: date = None) -> List[Transaction]:
        """Obtener movimientos bancarios reales navegando por la interfaz"""
        try:
            if not start_date:
                start_date = date.today().replace(day=1)  # Primer día del mes actual
            if not end_date:
                end_date = date.today()
                
            logger.info(f"=== BUSCANDO MOVIMIENTOS REALES ===")
            logger.info(f"Período: {start_date} a {end_date}")
            
            # Tomar screenshot inicial
            self.driver.save_screenshot("post_login_page.png")
            logger.info("Screenshot post-login: post_login_page.png")
            
            # Estrategia 1: Buscar enlaces a cuentas o movimientos
            if await self._navigate_to_accounts():
                transactions = await self._extract_movements()
                if transactions:
                    return self._filter_by_date(transactions, start_date, end_date)
            
            # Estrategia 2: Buscar menús de navegación
            if await self._navigate_through_menu():
                transactions = await self._extract_movements()
                if transactions:
                    return self._filter_by_date(transactions, start_date, end_date)
            
            # Estrategia 3: Buscar en toda la página actual
            logger.info("Buscando datos en página actual...")
            transactions = await self._extract_from_current_page()
            
            return self._filter_by_date(transactions, start_date, end_date)
            
        except Exception as e:
            logger.error(f"Error obteniendo movimientos: {e}")
            return []

    async def _navigate_to_accounts(self) -> bool:
        """Navegar a la sección de cuentas"""
        try:
            logger.info("Estrategia 1: Navegando a cuentas...")
            
            # Enlaces típicos para cuentas
            account_selectors = [
                "//a[contains(text(), 'Cuentas')]",
                "//a[contains(text(), 'Mis cuentas')]",
                "//a[contains(text(), 'Posición')]",
                "//a[contains(text(), 'Balance')]",
                "//button[contains(text(), 'Cuentas')]",
                "//span[contains(text(), 'Cuentas')]",
                "a[href*='cuenta']",
                "a[href*='position']",
                "a[href*='balance']"
            ]
            
            for selector in account_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            logger.info(f"Haciendo clic en: {element.text}")
                            element.click()
                            await asyncio.sleep(3)
                            
                            # Verificar si cambió la página
                            current_url = self.driver.current_url
                            if 'cuenta' in current_url.lower() or 'position' in current_url.lower():
                                logger.info(f"Navegación exitosa a cuentas: {current_url}")
                                return True
                                
                except Exception as e:
                    logger.debug(f"Error con selector {selector}: {e}")
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error navegando a cuentas: {e}")
            return False

    async def _navigate_through_menu(self) -> bool:
        """Navegar a través del menú principal"""
        try:
            logger.info("Estrategia 2: Navegando por menús...")
            
            # Buscar menús típicos
            menu_selectors = [
                "//nav//a",  # Enlaces en navegación
                "//ul//a",   # Enlaces en listas
                "//div[contains(@class, 'menu')]//a",
                ".navigation a",
                ".sidebar a",
                ".menu a"
            ]
            
            for selector in menu_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.text:
                            text = element.text.lower()
                            if any(word in text for word in ['cuenta', 'movimiento', 'posición', 'balance']):
                                logger.info(f"Encontrado enlace de menú: {element.text}")
                                element.click()
                                await asyncio.sleep(3)
                                return True
                                
                except Exception as e:
                    logger.debug(f"Error con menú {selector}: {e}")
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error navegando por menús: {e}")
            return False

    async def _extract_movements(self) -> List[Transaction]:
        """Extraer movimientos de la página actual"""
        try:
            logger.info("Extrayendo movimientos de página actual...")
            
            # Tomar screenshot
            screenshot_name = f"movements_page_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_name)
            logger.info(f"Screenshot: {screenshot_name}")
            
            transactions = []
            
            # Buscar tablas con transacciones
            table_selectors = [
                "table tbody tr",
                "table tr",
                ".transactions tr",
                ".movimientos tr",
                ".movements tr",
                "tr[class*='transaction']",
                "tr[class*='movimiento']"
            ]
            
            for selector in table_selectors:
                try:
                    rows = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    logger.info(f"Encontradas {len(rows)} filas con selector: {selector}")
                    
                    for row in rows:
                        if row.is_displayed():
                            text = row.text.strip()
                            if self._looks_like_transaction(text):
                                transaction = self._parse_transaction(text)
                                if transaction:
                                    transactions.append(transaction)
                                    logger.info(f"Transacción extraída: {transaction.date} - {transaction.amount}€")
                                    
                except Exception as e:
                    logger.debug(f"Error con selector {selector}: {e}")
                    continue
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error extrayendo movimientos: {e}")
            return []

    async def _extract_from_current_page(self) -> List[Transaction]:
        """Extraer cualquier dato financiero de la página actual"""
        try:
            logger.info("Extrayendo todos los datos de la página...")
            
            transactions = []
            page_source = self.driver.page_source
            
            # Buscar patrones de transacciones en el HTML
            import re
            
            # Patrón para encontrar fechas + importes
            pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{4}).*?([-+]?\s*\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€?'
            matches = re.findall(pattern, page_source)
            
            for i, (date_str, amount_str) in enumerate(matches):
                try:
                    # Parsear fecha
                    transaction_date = self._parse_date(date_str)
                    
                    # Parsear importe
                    amount = float(amount_str.replace(' ', '').replace(',', '.'))
                    
                    transaction = Transaction(
                        date=transaction_date,
                        description=f"Movimiento {i+1}",
                        amount=amount
                    )
                    
                    transactions.append(transaction)
                    logger.info(f"Transacción de página: {transaction_date} - {amount}€")
                    
                except Exception as e:
                    logger.debug(f"Error parseando: {e}")
                    continue
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error extrayendo de página: {e}")
            return []

    def _looks_like_transaction(self, text: str) -> bool:
        """Verificar si el texto parece una transacción"""
        if len(text) < 10:
            return False
        
        # Debe tener fecha y dinero
        has_date = any(char in text for char in ['/', '-']) and any(char.isdigit() for char in text)
        has_money = '€' in text or 'EUR' in text or (',' in text and any(char.isdigit() for char in text))
        
        return has_date and has_money

    def _parse_transaction(self, text: str) -> Optional[Transaction]:
        """Parsear texto de transacción"""
        try:
            import re
            
            # Buscar fecha
            date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})'
            date_match = re.search(date_pattern, text)
            
            # Buscar importe
            amount_pattern = r'([-+]?\s*\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€?'
            amount_matches = re.findall(amount_pattern, text)
            
            if not date_match or not amount_matches:
                return None
            
            # Parsear datos
            transaction_date = self._parse_date(date_match.group(1))
            amount = float(amount_matches[0].replace(' ', '').replace(',', '.'))
            
            # Extraer descripción
            description_start = date_match.end()
            amount_start = text.find(amount_matches[0])
            description = text[description_start:amount_start].strip()
            
            if not description:
                description = text[:50].strip()
            
            return Transaction(
                date=transaction_date,
                description=description,
                amount=amount,
                balance=float(amount_matches[1]) if len(amount_matches) > 1 else None
            )
            
        except Exception as e:
            logger.debug(f"Error parseando transacción: {e}")
            return None

    def _parse_date(self, date_str: str) -> date:
        """Parsear fecha en varios formatos"""
        date_str = date_str.strip()
        
        formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
                
        # Fallback a fecha actual
        return date.today()

    def _filter_by_date(self, transactions: List[Transaction], start_date: date, end_date: date) -> List[Transaction]:
        """Filtrar transacciones por rango de fechas"""
        filtered = [
            t for t in transactions 
            if start_date <= t.date <= end_date
        ]
        
        logger.info(f"Filtradas {len(filtered)} de {len(transactions)} transacciones por fecha")
        return filtered

    async def export_to_csv(self, transactions: List[Transaction], filename: str = None) -> str:
        """Exportar a CSV"""
        import csv
        
        if not filename:
            filename = f"movimientos_bankinter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Fecha', 'Descripción', 'Importe', 'Saldo'])
                
                for t in transactions:
                    writer.writerow([
                        t.date.strftime('%d/%m/%Y'),
                        t.description,
                        f"{t.amount:.2f}",
                        f"{t.balance:.2f}" if t.balance else ""
                    ])
                    
            logger.info(f"Exportado a: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exportando: {e}")
            raise

    def close(self):
        """Cerrar WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()