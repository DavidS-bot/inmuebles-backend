from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
import asyncio
import subprocess
import sys
import os
from ..deps import get_current_user
from ..models import User

router = APIRouter(prefix="/bankinter", tags=["Bankinter"])


@router.post("/update-movements")
def update_bankinter_movements(current_user: User = Depends(get_current_user)):
    """Test endpoint - simplified version"""
    try:
        print(f"BANKINTER ENDPOINT CALLED for user: {current_user.id}")
        return {
            "success": True, 
            "message": "Modo de prueba activado", 
            "new_movements": 0,
            "duplicates_skipped": 0,
            "total_movements": 0
        }
    except Exception as e:
        print(f"ERROR in bankinter endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))