from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
import glob
import os
import requests
from datetime import datetime
from ..deps import get_current_user
from ..models import User
import subprocess
import sys

router = APIRouter(prefix="/bankinter-upload", tags=["Bankinter Upload"])

@router.post("/upload-latest")
async def upload_latest_bankinter_file(current_user: User = Depends(get_current_user)) -> Dict:
    """Upload the latest Bankinter Excel file from local directory"""
    
    try:
        # Find all bankinter files
        pattern = "bankinter_api_*.xlsx"
        files = glob.glob(pattern)
        
        if not files:
            raise HTTPException(status_code=404, detail="No Bankinter files found")
        
        # Sort by modification time, get the latest
        latest_file = max(files, key=os.path.getmtime)
        file_size = os.path.getsize(latest_file)
        mod_time = datetime.fromtimestamp(os.path.getmtime(latest_file))
        
        # Execute the upload script
        backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        script_path = os.path.join(backend_path, 'upload_latest_bankinter.py')
        
        # Run the script
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, 
                              text=True, 
                              cwd=backend_path)
        
        if result.returncode == 0:
            # Parse the output to extract statistics
            output_lines = result.stdout.strip().split('\n')
            
            created_movements = 0
            total_rows = 0
            duplicates_skipped = 0
            
            for line in output_lines:
                if 'Movements created:' in line:
                    created_movements = int(line.split(':')[1].strip())
                elif 'Total rows processed:' in line:
                    total_rows = int(line.split(':')[1].strip())
                elif 'Duplicates skipped:' in line:
                    duplicates_skipped = int(line.split(':')[1].strip())
            
            return {
                "success": True,
                "message": f"Latest Bankinter file processed successfully",
                "file": latest_file,
                "file_size": file_size,
                "file_date": mod_time.isoformat(),
                "created_movements": created_movements,
                "total_rows": total_rows,
                "duplicates_skipped": duplicates_skipped,
                "output": result.stdout
            }
        else:
            raise HTTPException(status_code=500, detail=f"Upload script failed: {result.stderr}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload latest Bankinter file: {str(e)}")