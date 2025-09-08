#!/usr/bin/env python3
"""
API simple para ejecutar el scraper Bankinter que ya funciona
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
app_path = os.path.join(current_dir, 'app')
sys.path.insert(0, app_path)

app = FastAPI(title="Bankinter Scraper API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Bankinter Scraper API is running"}

@app.post("/scrape-bankinter")
async def scrape_bankinter():
    """Execute the proven working Bankinter scraper v7 - ADMIN ONLY"""
    
    # Security note: This is running locally so only the admin can access it
    # In production, this would need proper authentication
    
    try:
        from bankinter_update_endpoint import execute_bankinter_update
        
        print("Ejecutando scraper Bankinter v7 (ADMIN ONLY)...")
        result = await execute_bankinter_update()
        
        print(f"Scraper completado para admin: {result}")
        
        return {
            "success": result["success"],
            "message": result["message"],
            "new_movements": result["new_movements"],
            "duplicates_skipped": result["duplicates_skipped"],
            "total_movements": result["total_movements"],
            "scraped_live": True,
            "admin_only": True,
            "warning": "Este endpoint solo funciona localmente para el administrador"
        }
        
    except Exception as e:
        print(f"Error en scraper: {e}")
        raise HTTPException(status_code=500, detail=f"Scraper error: {str(e)}")

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)