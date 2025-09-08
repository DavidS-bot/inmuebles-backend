from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict
import asyncio
import os
import sys
import logging
from ..deps import get_current_user
from ..models import User

router = APIRouter(prefix="/bankinter-real", tags=["Bankinter Real"])

logger = logging.getLogger(__name__)

@router.post("/update-movements-real")
async def update_bankinter_movements_real(
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Execute real Bankinter scraper v7 and upload movements"""
    
    try:
        logger.info("🏦 Iniciando ejecución real del scraper Bankinter v7")
        
        # Add backend path to import the working script
        backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        app_path = os.path.join(backend_path, 'app')
        
        # Add paths to sys.path
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        if app_path not in sys.path:
            sys.path.insert(0, app_path)
        
        # Import and execute the working script
        try:
            from services.bankinter_scraper_v7 import BankinterScraperV7
            import pandas as pd
            import requests
            
            # Execute the same process that we tested successfully
            scraper = BankinterScraperV7(
                username="75867185",
                password="Motoreta123$",
                agent_username="davsanchez21277@gmail.com",
                agent_password="123456",
                auto_upload=False
            )
            
            # Setup and run scraper
            scraper.setup_driver()
            transactions, excel_file, api_excel_file, csv_file, _ = await scraper.get_august_movements_corrected()
            
            if not transactions:
                scraper.close()
                return {
                    "success": True,
                    "message": "No se encontraron movimientos nuevos",
                    "new_movements": 0,
                    "duplicates_skipped": 0,
                    "total_movements": 0
                }
            
            # Upload using local backend
            backend_url = "http://localhost:8001"
            
            # Login to backend
            login_data = {'username': 'davsanchez21277@gmail.com', 'password': '123456'}
            response = requests.post(
                f'{backend_url}/auth/login',
                data=login_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code != 200:
                scraper.close()
                raise HTTPException(status_code=401, detail="Backend authentication failed")
            
            token = response.json()['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            
            # Upload Excel file
            with open(api_excel_file, 'rb') as file:
                files = {'file': (api_excel_file, file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                
                response = requests.post(
                    f'{backend_url}/financial-movements/upload-excel-global',
                    files=files,
                    headers=headers,
                    timeout=60
                )
            
            scraper.close()
            
            if response.status_code == 200:
                result = response.json()
                
                return {
                    "success": True,
                    "message": "Bankinter update completed successfully",
                    "new_movements": result.get("created_movements", 0),
                    "duplicates_skipped": result.get("duplicates_skipped", 0),
                    "total_movements": result.get("total_rows", len(transactions))
                }
            else:
                raise HTTPException(status_code=500, detail=f"Upload failed: {response.status_code}")
                
        except ImportError as e:
            logger.error(f"Import error: {e}")
            raise HTTPException(status_code=500, detail=f"Scraper import failed: {str(e)}")
        except Exception as e:
            logger.error(f"Scraper execution error: {e}")
            raise HTTPException(status_code=500, detail=f"Scraper execution failed: {str(e)}")
            
    except Exception as e:
        logger.error(f"General error in Bankinter update: {e}")
        raise HTTPException(status_code=500, detail=f"Bankinter update failed: {str(e)}")

# Background task version for long-running process
@router.post("/update-movements-background") 
async def update_bankinter_movements_background(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Start Bankinter update as background task"""
    
    background_tasks.add_task(_execute_bankinter_background, current_user.id)
    
    return {
        "success": True,
        "message": "Bankinter update started in background",
        "status": "processing"
    }

async def _execute_bankinter_background(user_id: int):
    """Background task to execute Bankinter scraper"""
    
    try:
        logger.info(f"🏦 Background Bankinter update started for user {user_id}")
        
        # Execute the same working script
        backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        app_path = os.path.join(backend_path, 'app')
        
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        if app_path not in sys.path:
            sys.path.insert(0, app_path)
        
        from bankinter_update_endpoint import execute_bankinter_update
        
        result = await execute_bankinter_update()
        
        logger.info(f"✅ Background Bankinter update completed for user {user_id}: {result}")
        
    except Exception as e:
        logger.error(f"❌ Background Bankinter update failed for user {user_id}: {e}")