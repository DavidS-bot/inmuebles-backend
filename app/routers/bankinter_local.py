from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
import subprocess
import sys
import os
from ..deps import get_current_user
from ..models import User

router = APIRouter(prefix="/bankinter-local", tags=["Bankinter Local"])

@router.post("/sync-and-upload")
async def sync_and_upload_local(current_user: User = Depends(get_current_user)) -> Dict:
    """Execute local scraper and upload to production"""
    
    try:
        # Get the backend directory
        backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        script_path = os.path.join(backend_path, 'run_local_scraper.py')
        
        if not os.path.exists(script_path):
            raise HTTPException(status_code=500, detail="Local scraper script not found")
        
        # Execute the scraper script
        result = subprocess.run(
            [sys.executable, script_path], 
            capture_output=True, 
            text=True, 
            cwd=backend_path,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            # Parse output to get statistics
            output_lines = result.stdout.strip().split('\n')
            
            created_movements = 0
            total_rows = 0
            duplicates_skipped = 0
            
            for line in output_lines:
                if 'Created movements:' in line:
                    created_movements = int(line.split(':')[1].strip())
                elif 'Total rows:' in line:
                    total_rows = int(line.split(':')[1].strip())
                elif 'Duplicates skipped:' in line:
                    duplicates_skipped = int(line.split(':')[1].strip())
            
            return {
                "success": True,
                "message": "Local Bankinter scraper executed and uploaded successfully",
                "created_movements": created_movements,
                "total_rows": total_rows,
                "duplicates_skipped": duplicates_skipped,
                "output": result.stdout
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Local scraper failed: {result.stderr}"
            )
            
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=408, 
            detail="Local scraper timed out (took longer than 5 minutes)"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to execute local scraper: {str(e)}"
        )