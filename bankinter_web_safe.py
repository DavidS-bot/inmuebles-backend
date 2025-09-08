#!/usr/bin/env python3
"""
Bankinter scraper web-safe - evita problemas de Unicode
"""

import asyncio
import requests
import logging
from datetime import datetime

# Configurar logging sin Unicode problemático
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def execute_web_safe_bankinter():
    """Ejecutar scraping de Bankinter evitando problemas de Unicode"""
    
    try:
        import sys
        import os
        
        # Agregar app al path
        app_path = os.path.join(os.path.dirname(__file__), 'app')
        sys.path.insert(0, app_path)
        
        from services.bankinter_scraper_v7 import BankinterScraperV7
        
        logger.info("Iniciando scraping web-safe de Bankinter")
        
        # Configurar scraper
        scraper = BankinterScraperV7(
            username="75867185",
            password="Motoreta123$",
            agent_username="davsanchez21277@gmail.com",
            agent_password="123456",
            auto_upload=False
        )
        
        # Setup driver
        scraper.setup_driver()
        
        try:
            # Ejecutar el login y navegación
            if not await scraper.login_to_bankinter():
                logger.error("Login falló")
                return create_error_result("Login failed")
            
            if not await scraper.navigate_to_movements():
                logger.error("Navegación falló")
                return create_error_result("Navigation failed")
            
            # Extraer transacciones (sin procesar todavía para evitar Unicode)
            raw_transactions = await scraper.extract_all_movements()
            
            if not raw_transactions:
                logger.error("No se extrajeron transacciones")
                return create_error_result("No transactions extracted")
            
            logger.info(f"Transacciones extraídas: {len(raw_transactions)}")
            
            # Procesar de forma segura evitando Unicode
            safe_transactions = []
            for t in raw_transactions:
                try:
                    # Limpiar concepto de caracteres problemáticos
                    safe_concept = t.description.encode('ascii', 'ignore').decode('ascii')
                    if len(safe_concept) < 5:  # Si se perdió demasiado texto
                        safe_concept = "MOVIMIENTO BANCARIO"
                    
                    safe_transactions.append(t)  # Usar transacción original
                    
                except Exception as e:
                    logger.warning(f"Error procesando transacción, omitida: {e}")
                    continue
            
            logger.info(f"Transacciones procesadas de forma segura: {len(safe_transactions)}")
            
            # Subir directamente sin generar Excel (para evitar Unicode)
            backend_url = "https://inmuebles-backend-api.onrender.com"
            
            # Login al backend
            login_data = {'username': 'davsanchez21277@gmail.com', 'password': '123456'}
            response = requests.post(
                f'{backend_url}/auth/login',
                data=login_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code != 200:
                return create_error_result(f"Backend login failed: {response.status_code}")
            
            token = response.json()['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            
            # Crear movimientos uno por uno (método más directo)
            new_count = 0
            duplicate_count = 0
            
            for transaction in safe_transactions:
                try:
                    # Crear movimiento directamente via API
                    movement_data = {
                        "date": transaction.date.isoformat(),
                        "concept": transaction.description.encode('ascii', 'ignore').decode('ascii'),
                        "amount": float(transaction.amount),
                        "category": "Sin clasificar"
                    }
                    
                    # Intentar crear movimiento
                    response = requests.post(
                        f'{backend_url}/financial-movements/',
                        json=movement_data,
                        headers=headers,
                        timeout=30
                    )
                    
                    if response.status_code == 201:
                        new_count += 1
                    elif response.status_code == 409:  # Conflict - duplicate
                        duplicate_count += 1
                    else:
                        logger.warning(f"Error creando movimiento: {response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"Error procesando movimiento individual: {e}")
                    continue
            
            logger.info(f"Resultado: {new_count} nuevos, {duplicate_count} duplicados")
            
            return {
                "success": True,
                "message": "Scraping web-safe completado exitosamente",
                "new_movements": new_count,
                "duplicates_skipped": duplicate_count,
                "total_movements": len(safe_transactions)
            }
            
        except Exception as e:
            logger.error(f"Error en proceso de scraping: {e}")
            return create_error_result(f"Scraping error: {str(e)}")
            
        finally:
            try:
                scraper.close()
            except:
                pass
                
    except Exception as e:
        logger.error(f"Error general: {e}")
        return create_error_result(f"General error: {str(e)}")

def create_error_result(message):
    """Crear resultado de error estándar"""
    return {
        "success": False,
        "message": message,
        "new_movements": 0,
        "duplicates_skipped": 0,
        "total_movements": 0
    }

async def main():
    """Función principal para testing"""
    result = await execute_web_safe_bankinter()
    print("RESULT_JSON:", result)
    return result

if __name__ == "__main__":
    asyncio.run(main())