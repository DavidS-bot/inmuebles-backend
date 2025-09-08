#!/usr/bin/env python3
"""
Servicio para subir movimientos al agente financiero con deduplicación automática
"""

import asyncio
import aiohttp
import aiofiles
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

class FinancialAgentUploader:
    def __init__(self, base_url: str = "http://localhost:8000", 
                 username: str = None, password: str = None):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session: Optional[aiohttp.ClientSession] = None
        self.access_token: Optional[str] = None
        self.logger = logging.getLogger(__name__)
        
    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession()
        await self.login()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    async def login(self) -> bool:
        """Autenticarse en el agente financiero"""
        if not self.username or not self.password:
            raise ValueError("Username and password required for authentication")
            
        login_url = f"{self.base_url}/auth/login"
        
        # Usar form data en lugar de JSON (OAuth2PasswordRequestForm)
        login_data = aiohttp.FormData()
        login_data.add_field('username', self.username)
        login_data.add_field('password', self.password)
        
        try:
            self.logger.info(f"Attempting login to {login_url}")
            async with self.session.post(login_url, data=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.access_token = result.get("access_token")
                    if self.access_token:
                        self.logger.info("✓ Login successful")
                        return True
                    else:
                        self.logger.error("Login response missing access_token")
                        return False
                else:
                    error_text = await response.text()
                    self.logger.error(f"Login failed with status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Obtener headers de autenticación"""
        if not self.access_token:
            raise ValueError("Not authenticated - call login() first")
        return {"Authorization": f"Bearer {self.access_token}"}
    
    async def upload_excel_file(self, excel_file_path: str) -> Dict[str, Any]:
        """
        Subir archivo Excel al agente financiero con deduplicación automática
        
        Args:
            excel_file_path: Ruta al archivo Excel con formato Fecha|Concepto|Importe
            
        Returns:
            Dict con resultado de la subida
        """
        if not Path(excel_file_path).exists():
            raise FileNotFoundError(f"Excel file not found: {excel_file_path}")
        
        upload_url = f"{self.base_url}/financial-movements/upload-excel-global"
        
        try:
            self.logger.info(f"Uploading Excel file: {excel_file_path}")
            
            # Leer archivo
            async with aiofiles.open(excel_file_path, 'rb') as file:
                file_content = await file.read()
            
            # Preparar multipart form data
            data = aiohttp.FormData()
            data.add_field('file', file_content, 
                          filename=Path(excel_file_path).name,
                          content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            
            # Enviar request
            async with self.session.post(upload_url, 
                                       data=data, 
                                       headers=self.get_auth_headers()) as response:
                
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"✓ Upload successful: {result}")
                    return result
                else:
                    error_text = await response.text()
                    self.logger.error(f"Upload failed with status {response.status}: {error_text}")
                    raise Exception(f"Upload failed: {response.status} - {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Upload error: {e}")
            raise
    
    async def get_existing_movements(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        Obtener movimientos existentes para verificar duplicados
        
        Args:
            start_date: Fecha inicio en formato YYYY-MM-DD
            end_date: Fecha fin en formato YYYY-MM-DD
            
        Returns:
            Lista de movimientos existentes
        """
        url = f"{self.base_url}/financial-movements/"
        params = {}
        
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        try:
            self.logger.info(f"Fetching existing movements from {start_date} to {end_date}")
            
            async with self.session.get(url, 
                                      params=params,
                                      headers=self.get_auth_headers()) as response:
                
                if response.status == 200:
                    movements = await response.json()
                    self.logger.info(f"✓ Retrieved {len(movements)} existing movements")
                    return movements
                else:
                    error_text = await response.text()
                    self.logger.error(f"Failed to get movements: {response.status} - {error_text}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error getting movements: {e}")
            return []
    
    async def upload_with_deduplication_check(self, excel_file_path: str) -> Dict[str, Any]:
        """
        Subir con verificación manual adicional de duplicados
        
        Args:
            excel_file_path: Ruta al archivo Excel
            
        Returns:
            Dict con estadísticas de subida y deduplicación
        """
        self.logger.info("=== STARTING UPLOAD WITH DEDUPLICATION ===")
        
        # 1. Obtener movimientos existentes del mes actual
        from datetime import date, timedelta
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        end_of_month = date(today.year, today.month + 1, 1) - timedelta(days=1)
        
        existing_movements = await self.get_existing_movements(
            start_date=start_of_month.isoformat(),
            end_date=end_of_month.isoformat()
        )
        
        # 2. Crear firmas de movimientos existentes
        existing_signatures = set()
        for movement in existing_movements:
            signature = f"{movement['date']}|{movement['concept']}|{movement['amount']}"
            existing_signatures.add(signature)
        
        self.logger.info(f"Found {len(existing_signatures)} existing movement signatures")
        
        # 3. Subir archivo (el endpoint ya maneja deduplicación)
        upload_result = await self.upload_excel_file(excel_file_path)
        
        # 4. Compilar estadísticas
        result = {
            "upload_result": upload_result,
            "existing_movements_found": len(existing_movements),
            "duplicates_skipped": upload_result.get("duplicates_skipped", 0),
            "new_movements_created": upload_result.get("created_movements", 0),
            "total_rows_processed": upload_result.get("total_rows", 0),
            "upload_timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"✓ Upload completed: {result}")
        return result

# Función de conveniencia para uso directo
async def upload_bankinter_excel(excel_file_path: str, 
                               username: str, password: str,
                               base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """
    Función de conveniencia para subir archivo Excel de Bankinter al agente financiero
    
    Args:
        excel_file_path: Ruta al archivo Excel generado por el scraper
        username: Usuario del agente financiero
        password: Contraseña del agente financiero
        base_url: URL base del agente financiero
        
    Returns:
        Dict con resultado de la subida
    """
    async with FinancialAgentUploader(base_url, username, password) as uploader:
        return await uploader.upload_with_deduplication_check(excel_file_path)

# Ejemplo de uso
if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    if len(sys.argv) < 4:
        print("Usage: python financial_agent_uploader.py <excel_file> <username> <password>")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    
    async def main():
        result = await upload_bankinter_excel(excel_file, username, password)
        print(json.dumps(result, indent=2))
    
    asyncio.run(main())