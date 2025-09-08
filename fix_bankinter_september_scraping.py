#!/usr/bin/env python3
"""
Fix Bankinter scraping to capture September and August 2025 data
Enhanced navigation to ensure current month data is captured
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
class TransactionV7:
    date: date
    description: str
    amount: float
    balance: Optional[float] = None
    reference: Optional[str] = None

class BankinterScraperSeptember:
    """Enhanced scraper to capture September 2025 data"""
    
    def __init__(self, username: str = "75867185", password: str = "Motoreta123$"):
        self.username = username
        self.password = password
        self.driver = None
        self.wait = None
        
        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
    def setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome driver with anti-detection"""
        options = Options()
        
        # Anti-detection options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Optional: run in background
        # options.add_argument("--headless")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        
        return driver
    
    async def login_to_bankinter(self) -> bool:
        """Login to Bankinter with exact flow"""
        try:
            logger.info("=== LOGIN FLOW EXACT V7 ===")
            logger.info("Navegando a https://bancaonline.bankinter.com/gestion/login.xhtml")
            
            self.driver.get("https://bancaonline.bankinter.com/gestion/login.xhtml")
            await asyncio.sleep(5)
            
            # Accept cookies if present
            try:
                logger.info("Aceptando cookies")
                cookies_button = self.wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
                cookies_button.click()
                await asyncio.sleep(2)
            except:
                pass
            
            # Fill credentials
            logger.info("Completando credenciales...")
            username_field = self.wait.until(EC.presence_of_element_located((By.ID, "form-login-userId")))
            username_field.clear()
            username_field.send_keys(self.username)
            
            password_field = self.driver.find_element(By.ID, "form-login-password")
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Click login button
            logger.info("Haciendo clic en botón de login")
            login_button = self.driver.find_element(By.ID, "form-login-btnLogin")
            login_button.click()
            
            await asyncio.sleep(10)
            
            current_url = self.driver.current_url
            logger.info(f"URL post-login: {current_url}")
            
            if "extracto_integral" in current_url:
                logger.info("Login exitoso - En extracto_integral")
                return True
            else:
                logger.warning(f"URL inesperada: {current_url}")
                return False
                
        except Exception as e:
            logger.error(f"Error en login: {e}")
            return False
    
    async def navigate_to_current_movements(self) -> bool:
        """Navigate to movements page with current month focus"""
        try:
            logger.info("=== NAVEGANDO A MOVIMIENTOS ACTUALES ===")
            
            # First, try to navigate to movements page
            movements_url = "https://bancaonline.bankinter.com/extracto/secure/movimientos_cuenta.xhtml?INDEX_CTA=1&IND=C&TIPO=N"
            logger.info(f"Navegando a {movements_url}")
            self.driver.get(movements_url)
            await asyncio.sleep(10)
            
            current_url = self.driver.current_url
            logger.info(f"URL después de navegación: {current_url}")
            
            if "movimientos_cuenta" not in current_url:
                logger.error("No se pudo navegar a movimientos")
                return False
                
            # Take screenshot to see the current state
            self.driver.save_screenshot("movements_page_september.png")
            
            # Try to click on current month or navigate to September if not already there
            try:
                await self.ensure_current_month_data()
            except Exception as e:
                logger.warning(f"No se pudo navegar a mes actual: {e}")
                # Continue anyway, maybe the data is already visible
            
            logger.info("Navegación exitosa a movimientos actuales")
            return True
            
        except Exception as e:
            logger.error(f"Error navegando a movimientos: {e}")
            return False
    
    async def ensure_current_month_data(self):
        """Try to navigate to current month data (September 2025)"""
        try:
            logger.info("Intentando asegurar datos del mes actual (Septiembre 2025)")
            
            # Look for month navigation elements
            # Different possible selectors for month navigation
            month_selectors = [
                "select[name*='mes']",
                "select[name*='month']", 
                ".month-selector",
                ".date-selector",
                "select.form-control",
                "#mesDesde",
                "#mesHasta",
                ".calendario"
            ]
            
            for selector in month_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"Encontrado selector de mes: {selector}")
                        # Try to interact with it
                        element = elements[0]
                        if element.tag_name == "select":
                            from selenium.webdriver.support.ui import Select
                            select = Select(element)
                            # Try to select September (09) or current month
                            for option in ["09", "9", "September", "Septiembre", str(datetime.now().month)]:
                                try:
                                    select.select_by_value(option)
                                    logger.info(f"Seleccionado mes: {option}")
                                    await asyncio.sleep(3)
                                    break
                                except:
                                    try:
                                        select.select_by_visible_text(option)
                                        logger.info(f"Seleccionado mes por texto: {option}")
                                        await asyncio.sleep(3)
                                        break
                                    except:
                                        continue
                        break
                except Exception as e:
                    continue
            
            # Look for "actualizar" or "consultar" button
            update_buttons = [
                "input[value*='Consultar']",
                "input[value*='Actualizar']", 
                "button[type='submit']",
                ".btn-primary",
                ".consultar"
            ]
            
            for btn_selector in update_buttons:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, btn_selector)
                    if button.is_displayed():
                        logger.info(f"Haciendo clic en botón actualizar: {btn_selector}")
                        button.click()
                        await asyncio.sleep(5)
                        break
                except:
                    continue
            
        except Exception as e:
            logger.warning(f"Error asegurando datos del mes actual: {e}")
    
    def _parse_bankinter_date(self, date_text: str) -> Optional[date]:
        """Parse Bankinter date format"""
        if not date_text:
            return None
        
        # Look for dd/mm/yyyy pattern
        date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_text)
        if date_match:
            try:
                day, month, year = map(int, date_match.groups())
                return date(year, month, day)
            except ValueError:
                pass
        
        return None
    
    def _parse_amount(self, amount_text: str) -> float:
        """Parse amount from Spanish format"""
        if not amount_text:
            return 0.0
        
        # Remove whitespace and currency symbols
        clean_text = amount_text.strip().replace('€', '').replace('EUR', '')
        
        # Handle negative amounts with parentheses or minus sign
        is_negative = '-' in clean_text or '(' in clean_text
        
        # Remove negative indicators and parentheses
        clean_text = clean_text.replace('-', '').replace('(', '').replace(')', '').strip()
        
        # Replace comma with dot for decimal separator
        clean_text = clean_text.replace('.', '').replace(',', '.')
        
        try:
            amount = float(clean_text)
            return -amount if is_negative else amount
        except ValueError:
            logger.warning(f"No se pudo parsear importe: {amount_text}")
            return 0.0
    
    async def extract_all_movements(self) -> List[TransactionV7]:
        """Extract all visible movements from the page"""
        try:
            logger.info("=== EXTRAYENDO TODOS LOS MOVIMIENTOS VISIBLES ===")
            
            # Take screenshot
            self.driver.save_screenshot("extraction_september.png")
            
            movements = []
            
            # Find tables with movement data
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            logger.info(f"Tablas encontradas: {len(tables)}")
            
            for i, table in enumerate(tables):
                try:
                    table_text = table.text.lower()
                    
                    # Skip tables that don't contain banking data
                    if not any(keyword in table_text for keyword in ['fecha', 'importe', 'concepto', 'saldo']):
                        continue
                    
                    logger.info(f"Analizando tabla {i+1} con datos bancarios...")
                    
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    logger.info(f"Filas en tabla {i+1}: {len(rows)}")
                    
                    # Find headers
                    headers = []
                    if rows:
                        first_row = rows[0]
                        header_cells = first_row.find_elements(By.TAG_NAME, "th") or first_row.find_elements(By.TAG_NAME, "td")
                        headers = [cell.text.strip().upper() for cell in header_cells]
                        logger.info(f"Headers detectados: {headers}")
                    
                    # Process data rows
                    for j, row in enumerate(rows[1:], 1):
                        try:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if len(cells) < 4:  # Need at least date, concept, amount, balance
                                continue
                            
                            cell_texts = [cell.text.strip() for cell in cells]
                            
                            # Extract date (usually first or second column)
                            date_text = ""
                            for idx in [0, 1]:
                                if idx < len(cell_texts) and cell_texts[idx]:
                                    if re.search(r'\d{1,2}/\d{1,2}/\d{4}', cell_texts[idx]):
                                        date_text = cell_texts[idx]
                                        break
                            
                            transaction_date = self._parse_bankinter_date(date_text)
                            if not transaction_date:
                                continue
                            
                            # NO FILTER BY DATE - Accept all recent movements
                            # We want both August and September 2025
                            current_date = datetime.now()
                            months_diff = (current_date.year - transaction_date.year) * 12 + (current_date.month - transaction_date.month)
                            
                            if months_diff > 6:  # Only skip movements older than 6 months
                                continue
                            
                            # Extract concept (usually in middle columns)
                            concept = ""
                            for idx in [2, 3, 1]:  # Try different positions
                                if idx < len(cell_texts) and cell_texts[idx]:
                                    concept = cell_texts[idx]
                                    if len(concept) > 10:  # Prefer longer descriptions
                                        break
                            
                            if not concept:
                                continue
                            
                            # Extract amount (usually last or second-to-last column)
                            amount = 0.0
                            for idx in [-2, -1, 4]:  # Try from end backwards
                                if abs(idx) <= len(cell_texts):
                                    amount_text = cell_texts[idx] if idx >= 0 else cell_texts[len(cell_texts) + idx]
                                    if re.search(r'[\d,.-]+', amount_text):
                                        amount = self._parse_amount(amount_text)
                                        if amount != 0.0:
                                            break
                            
                            # Extract balance (usually last column)
                            balance = None
                            if len(cell_texts) > 0:
                                balance_text = cell_texts[-1]
                                if re.search(r'[\d,.-]+', balance_text):
                                    try:
                                        balance = self._parse_amount(balance_text)
                                    except:
                                        balance = None
                            
                            # Create transaction
                            transaction = TransactionV7(
                                date=transaction_date,
                                description=concept,
                                amount=amount,
                                balance=balance
                            )
                            
                            movements.append(transaction)
                            logger.info(f"Movimiento: {transaction_date.strftime('%d/%m/%Y')} - {concept[:30]}... - {amount:.2f}€ (Saldo: {balance:.2f}€ if balance else 'N/A')")
                            
                        except Exception as e:
                            logger.debug(f"Error procesando fila {j}: {e}")
                            continue
                    
                except Exception as e:
                    logger.debug(f"Error procesando tabla {i+1}: {e}")
                    continue
            
            logger.info(f"Total movimientos extraídos: {len(movements)}")
            
            # Sort by date descending
            movements.sort(key=lambda x: x.date, reverse=True)
            
            return movements
            
        except Exception as e:
            logger.error(f"Error extrayendo movimientos: {e}")
            return []
    
    async def scrape_september_data(self) -> List[TransactionV7]:
        """Main function to scrape September and August data"""
        try:
            logger.info("=== INICIANDO SCRAPING SEPTIEMBRE/AGOSTO 2025 ===")
            
            # Setup driver
            self.setup_driver()
            
            try:
                # Login
                if not await self.login_to_bankinter():
                    logger.error("Login falló")
                    return []
                
                # Navigate to movements
                if not await self.navigate_to_current_movements():
                    logger.error("Navegación falló")
                    return []
                
                # Extract movements
                movements = await self.extract_all_movements()
                
                if movements:
                    logger.info("=== RESUMEN DE MOVIMIENTOS ENCONTRADOS ===")
                    september_count = sum(1 for m in movements if m.date.month == 9 and m.date.year == 2025)
                    august_count = sum(1 for m in movements if m.date.month == 8 and m.date.year == 2025)
                    
                    logger.info(f"Movimientos Septiembre 2025: {september_count}")
                    logger.info(f"Movimientos Agosto 2025: {august_count}")
                    logger.info(f"Total movimientos: {len(movements)}")
                    
                    # Show recent movements
                    logger.info("\n=== MOVIMIENTOS MÁS RECIENTES ===")
                    for movement in movements[:10]:
                        logger.info(f"{movement.date.strftime('%d/%m/%Y')} - {movement.description[:40]}... - {movement.amount:+.2f}€")
                
                return movements
                
            finally:
                if self.driver:
                    self.driver.quit()
            
        except Exception as e:
            logger.error(f"Error en scraping: {e}")
            return []

async def main():
    """Test the enhanced scraper"""
    scraper = BankinterScraperSeptember()
    movements = await scraper.scrape_september_data()
    
    if movements:
        print(f"\n✅ Scraping exitoso: {len(movements)} movimientos extraídos")
        
        # Check for September movements
        september_movements = [m for m in movements if m.date.month == 9 and m.date.year == 2025]
        august_movements = [m for m in movements if m.date.month == 8 and m.date.year == 2025]
        
        print(f"📅 Septiembre 2025: {len(september_movements)} movimientos")
        print(f"📅 Agosto 2025: {len(august_movements)} movimientos")
        
        if september_movements:
            print("\n🎯 MOVIMIENTOS DE SEPTIEMBRE ENCONTRADOS:")
            for movement in september_movements:
                print(f"  {movement.date.strftime('%d/%m/%Y')} - {movement.description[:50]}... - {movement.amount:+.2f}€")
        else:
            print("\n⚠️ No se encontraron movimientos de Septiembre 2025")
            print("Los movimientos más recientes son:")
            for movement in movements[:5]:
                print(f"  {movement.date.strftime('%d/%m/%Y')} - {movement.description[:50]}... - {movement.amount:+.2f}€")
    else:
        print("❌ No se pudieron extraer movimientos")

if __name__ == "__main__":
    asyncio.run(main())