#!/usr/bin/env python3
"""
Test script for European format parsing functions
"""

import sys
import os
sys.path.append('.')

from app.routers.financial_movements import parse_european_date, parse_european_amount
from datetime import date

def test_date_parsing():
    """Test European date parsing"""
    print("Testing European Date Parsing:")
    
    test_dates = [
        "20/02/2024",
        "21/02/2024", 
        "01/12/2023",
        "2024-02-20",  # Also support ISO
        "28/02/2024"
    ]
    
    for test_date in test_dates:
        result = parse_european_date(test_date)
        print(f"  '{test_date}' -> {result}")
        
    print()

def test_amount_parsing():
    """Test European amount parsing"""
    print("Testing European Amount Parsing:")
    
    test_amounts = [
        "-70,00 €",
        "-98,47 €", 
        "1.234,56 €",
        "-64,00 €",
        "12,31 €",
        "-319,23 €",
        "70.00",  # Already correct format
        -50.25,   # Already number
    ]
    
    for test_amount in test_amounts:
        result = parse_european_amount(test_amount)
        print(f"  '{test_amount}' -> {result}")
        
    print()

if __name__ == "__main__":
    print("Testing European Format Parsers")
    print("=" * 40)
    test_date_parsing()
    test_amount_parsing()
    print("Tests completed!")