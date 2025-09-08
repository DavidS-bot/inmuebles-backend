#!/usr/bin/env python3
"""
Local server to run Bankinter scraper from web interface
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import sys
import uvicorn
from typing import Dict
import asyncio

app = FastAPI(title="Local Bankinter Scraper", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.post("/run-scraper")
async def run_scraper() -> Dict:
    """Execute the Bankinter scraper"""
    
    try:
        print("Starting local Bankinter scraper...")
        
        # Execute the FRESH scraper script (always scrapes)
        result = subprocess.run(
            [sys.executable, 'run_fresh_scraper.py'], 
            capture_output=True, 
            text=True, 
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print("Scraper completed successfully!")
            
            # Parse output
            output_lines = result.stdout.strip().split('\n')
            created_movements = 0
            total_rows = 0
            
            for line in output_lines:
                if 'Created movements:' in line:
                    created_movements = int(line.split(':')[1].strip())
                elif 'Total rows:' in line:
                    total_rows = int(line.split(':')[1].strip())
            
            return {
                "success": True,
                "message": "Scraper executed successfully",
                "new_movements": created_movements,
                "total_rows": total_rows,
                "output": result.stdout
            }
        else:
            print(f"Scraper failed: {result.stderr}")
            return {
                "success": False,
                "message": f"Scraper failed: {result.stderr}",
                "output": result.stdout
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": "Scraper timed out (took longer than 5 minutes)"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error running scraper: {str(e)}"
        }

@app.get("/health")
def health():
    return {"status": "ok", "service": "Local Bankinter Scraper"}

if __name__ == "__main__":
    print("Starting local Bankinter scraper server...")
    print("Server will be available at http://localhost:8000")
    print("Use this to run real Bankinter scraping from the web interface")
    
    uvicorn.run(app, host="127.0.0.1", port=8003)