#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.bankinter_client import download_bankinter_data

async def test_bankinter():
    print("Testing Bankinter client with fixed date imports...")
    
    try:
        result = await download_bankinter_data("75867185", "test123", 30)
        print(f"SUCCESS: {result}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bankinter())