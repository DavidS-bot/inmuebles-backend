#!/usr/bin/env python3
"""Get correct contract data from local database"""

import sqlite3
import json
from pathlib import Path
import os

def get_local_contracts():
    print("EXTRACTING LOCAL CONTRACT DATA")
    print("=" * 40)
    
    # Connect to local database
    db_path = Path("data/dev.db")
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all rental contracts with property info
    query = """
    SELECT 
        rc.id,
        rc.property_id,
        rc.tenant_name,
        rc.start_date,
        rc.end_date,
        rc.monthly_rent,
        rc.deposit,
        rc.is_active,
        rc.contract_pdf_path,
        rc.contract_file_name,
        p.address as property_address
    FROM rentalcontract rc
    JOIN property p ON rc.property_id = p.id
    ORDER BY p.address, rc.tenant_name
    """
    
    cursor.execute(query)
    contracts = cursor.fetchall()
    
    print(f"Found {len(contracts)} contracts in local database\n")
    
    # Group by property
    by_property = {}
    for contract in contracts:
        prop_addr = contract['property_address']
        if prop_addr not in by_property:
            by_property[prop_addr] = []
        by_property[prop_addr].append(dict(contract))
    
    # Display contracts
    for prop_addr, prop_contracts in by_property.items():
        print(f"\n{prop_addr}:")
        for c in prop_contracts:
            print(f"  - Tenant: {c['tenant_name']}")
            print(f"    Rent: {c['monthly_rent']} EUR/month")
            print(f"    Deposit: {c['deposit']} EUR")
            print(f"    Start: {c['start_date']}")
            print(f"    Active: {c['is_active']}")
            if c['contract_pdf_path']:
                print(f"    PDF: {c['contract_file_name'] or c['contract_pdf_path']}")
    
    # Check PDF files
    print("\n" + "=" * 40)
    print("PDF FILES CHECK:")
    
    contracts_dir = Path("data/assets/contracts")
    if contracts_dir.exists():
        pdfs = list(contracts_dir.glob("*.pdf"))
        print(f"Found {len(pdfs)} PDF files in {contracts_dir}")
        
        # Match PDFs to contracts
        print("\nMatching PDFs to tenants:")
        for pdf_file in sorted(pdfs):
            filename = pdf_file.name
            # Extract tenant name from filename
            if "Rocio" in filename or "Rocío" in filename:
                tenant = "Rocío"
            elif "Susana" in filename:
                tenant = "Susana y Jorge"
            elif "Alvaro" in filename:
                tenant = "Álvaro"
            elif "J. Antonio" in filename or "Antonio y Maria" in filename:
                tenant = "J. Antonio y María"
            elif "Antonio-Olga" in filename or "Antonio y Olga" in filename:
                tenant = "Antonio y Olga"
            elif "Diego y Soledad" in filename:
                tenant = "Diego y Soledad"
            elif "Leandro Emanuel" in filename:
                tenant = "Leandro Emanuel"
            elif "Sergio Bravo" in filename:
                tenant = "Sergio Bravo"
            elif "Judit y Jesús" in filename or "Judit y Jesus" in filename:
                tenant = "Judit y Jesús"
            elif "Antonio. P. 1" in filename:
                tenant = "Antonio"
            elif "Roberto y Kerthyns" in filename:
                tenant = "Roberto y Kerthyns"
            elif "Manuela" in filename:
                tenant = "Manuela"
            elif "Jesús Javier" in filename or "Jesus Javier" in filename:
                tenant = "Jesús Javier y Carolina"
            elif "Lucia" in filename or "Lucía" in filename:
                tenant = "Lucía"
            elif "Manuel Orellana" in filename:
                tenant = "Manuel Orellana"
            elif "Eva y Manuel" in filename:
                tenant = "Eva y Manuel"
            else:
                tenant = "Unknown"
            
            print(f"  {filename[:50]}... -> {tenant}")
    
    # Save to JSON for upload script
    export_data = []
    for contract in contracts:
        export_data.append({
            "tenant_name": contract['tenant_name'],
            "property_address": contract['property_address'],
            "monthly_rent": contract['monthly_rent'],
            "deposit": contract['deposit'],
            "start_date": contract['start_date'],
            "end_date": contract['end_date'],
            "is_active": contract['is_active']
        })
    
    with open("local_contracts_data.json", "w", encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nExported {len(export_data)} contracts to local_contracts_data.json")
    
    conn.close()

if __name__ == "__main__":
    get_local_contracts()