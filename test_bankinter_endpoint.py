#!/usr/bin/env python3
"""
Test script para el endpoint de Bankinter
"""

import os
import sys
sys.path.append('.')

from app.routers.integrations import sync_bankinter_now
from app.database import get_session
from app.models import User
from sqlmodel import Session, create_engine, select

# Mock session and user for testing
class MockUser:
    id = 1

class MockSession:
    def __init__(self):
        pass
    
    def exec(self, query):
        class MockResult:
            def first(self):
                return None  # No existing movements
        return MockResult()
    
    def add(self, movement):
        print(f"✓ Would add movement: {movement.concept} - {movement.amount}€ - {movement.date}")
    
    def commit(self):
        print("✓ Would commit changes to database")
    
    def rollback(self):
        print("✗ Rolling back changes")

async def test_endpoint():
    """Test the bankinter sync endpoint"""
    print("🧪 TESTING BANKINTER SYNC ENDPOINT")
    print("="*50)
    
    mock_session = MockSession()
    mock_user = MockUser()
    
    try:
        result = await sync_bankinter_now(session=mock_session, current_user=mock_user)
        print("✅ ENDPOINT RESPONSE:")
        print(f"   Status: {result.get('sync_status')}")
        print(f"   Message: {result.get('message')}")
        print(f"   New movements: {result.get('new_movements', 0)}")
        print(f"   Duplicates: {result.get('duplicates_skipped', 0)}")
        print(f"   Total processed: {result.get('total_processed', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_endpoint())
    if success:
        print("\n🎉 TEST PASSED!")
    else:
        print("\n💥 TEST FAILED!")