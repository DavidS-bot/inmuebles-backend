#!/usr/bin/env python3
"""Upload PDF files in batches"""

import requests
import os
from pathlib import Path
import time

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

# PDF to tenant mapping (simplified)
PDF_MAPPING = {
    "contract_1_": "Rocio",
    "contract_2_": "Jorge",
    "contract_3_": "Alvaro",
    "contract_4_": "Maria Hidalgo",
    "contract_5_": "Alvaro",
    "contract_6_": "Antonio Rashad",
    "contract_7_": "Diego",
    "contract_8_": "Leandro",
    "contract_9_": "Sergio",
    "contract_10_": "Judit Torres Castillo y Jesus",
    "contract_11_": "Antonio Jose",
    "contract_14_": "Roberto",
    "contract_15_": "Manuela",
    "contract_16_": "Judit Torres Castillo",
    "contract_17_": "Jesus Javier",
    "contract_18_": "Lucia",
    "contract_19_": "Manuel Orellana",
    "contract_20_": "Manuel Avalos"
}

def upload_batch():
    print("BATCH PDF UPLOAD")
    print("=" * 30)
    
    # Login
    response = requests.post(f"{PROD_API}/auth/login", 
                           data={"username": EMAIL, "password": PASSWORD}, timeout=15)
    if response.status_code != 200:
        print("Login failed")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login OK")
    
    # Get contracts
    response = requests.get(f"{PROD_API}/rental-contracts/", headers=headers, timeout=15)
    contracts = response.json()
    print(f"Found {len(contracts)} contracts")
    
    # Get PDFs
    pdf_dir = Path("data/assets/contracts")
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files")
    
    uploaded = 0
    skipped = 0
    
    for pdf_file in sorted(pdf_files):
        filename = pdf_file.name
        
        # Find tenant pattern
        matched_tenant = None
        for key, tenant_pattern in PDF_MAPPING.items():
            if filename.startswith(key):
                matched_tenant = tenant_pattern
                break
        
        if not matched_tenant:
            print(f"SKIP: {filename[:40]}")
            skipped += 1
            continue
        
        # Find contract
        matched_contract = None
        for contract in contracts:
            tenant_name = contract['tenant_name'].lower()
            pattern_lower = matched_tenant.lower()
            
            if pattern_lower in tenant_name or any(word in tenant_name for word in pattern_lower.split()):
                matched_contract = contract
                break
        
        if not matched_contract:
            print(f"NO MATCH: {filename[:30]} -> {matched_tenant}")
            continue
        
        # Check if already has PDF
        if matched_contract.get('contract_pdf_path'):
            print(f"HAS PDF: {matched_contract['tenant_name'][:40]}")
            skipped += 1
            continue
        
        # Upload
        try:
            print(f"Uploading: {filename[:40]}...")
            with open(pdf_file, 'rb') as f:
                files = {'file': (filename, f, 'application/pdf')}
                response = requests.post(
                    f"{PROD_API}/rental-contracts/{matched_contract['id']}/upload-pdf",
                    files=files,
                    headers=headers,
                    timeout=45
                )
                
                if response.status_code in [200, 201]:
                    uploaded += 1
                    print(f"OK: {matched_contract['tenant_name'][:40]}")
                else:
                    print(f"FAIL ({response.status_code}): {filename[:30]}")
                    
        except Exception as e:
            print(f"ERROR: {filename[:30]} - {str(e)[:40]}")
        
        # Small delay between uploads
        time.sleep(1)
    
    print(f"\nRESULT: {uploaded} uploaded, {skipped} skipped")

if __name__ == "__main__":
    upload_batch()