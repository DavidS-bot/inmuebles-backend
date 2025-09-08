#!/usr/bin/env python3
"""Check local mortgage revision data"""

import sqlite3
import json
from pathlib import Path

def check_local_mortgage_data():
    db_path = "data/dev.db"
    if not Path(db_path).exists():
        print(f"Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Get results as dictionaries
    
    try:
        # Check mortgage details table
        cursor = conn.execute("SELECT * FROM mortgage_details")
        mortgages = cursor.fetchall()
        
        print(f"Found {len(mortgages)} mortgage records:")
        print("=" * 60)
        
        for mortgage in mortgages:
            print(f"Property ID: {mortgage['property_id']}")
            print(f"Initial Amount: {mortgage['initial_amount']}")
            print(f"Outstanding Balance: {mortgage['outstanding_balance']}")
            print(f"Interest Rate: {mortgage['interest_rate']}%")
            print(f"Margin: {mortgage['margin_percentage']}%")
            print(f"Start Date: {mortgage['start_date']}")
            print(f"End Date: {mortgage['end_date']}")
            print(f"Monthly Payment: {mortgage['monthly_payment']}")
            print(f"Bank: {mortgage['bank_name']}")
            print("-" * 40)
        
        # Also check if there are any revision/history tables
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("Available tables:")
        for table in tables:
            if 'mortgage' in table['name'].lower() or 'revision' in table['name'].lower():
                print(f"- {table['name']}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    check_local_mortgage_data()