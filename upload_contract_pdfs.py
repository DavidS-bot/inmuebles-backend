#!/usr/bin/env python3
"""Upload PDF files for contracts"""

import requests
import os
from pathlib import Path

PROD_API = "https://inmuebles-backend-api.onrender.com"
EMAIL = "davsanchez21277@gmail.com"
PASSWORD = "123456"

# PDF to tenant mapping based on filenames
PDF_MAPPING = {
    "contract_1_": "Rocio Soto",
    "contract_2_": "Jorge Rodriguez Moreno / Susana",
    "contract_3_": "Alvaro",
    "contract_4_": "Maria Hidalgo Llorca / Jose Antonio",
    "contract_5_": "Alvaro",  # duplicate
    "contract_6_": "Antonio Rashad Hanson / Olga",
    "contract_7_": "Diego Ribera",
    "contract_8_": "Leandro Emanuel",
    "contract_9_": "Sergio Bravo",
    "contract_10_": "Judit Torres Castillo y Jesus",
    "contract_11_": "Antonio Jose Lopez",
    "contract_14_": "Roberto",
    "contract_15_": "Manuela",
    "contract_16_": "Judit Torres Castillo",  # solo
    "contract_17_": "Jesus Javier",
    "contract_18_": "Lucia Marin",
    "contract_19_": "Manuel Orellana",
    "contract_20_": "Manuel Avalos"
}

def upload_pdfs():
    print("UPLOADING CONTRACT PDFs")
    print("=" * 40)
    
    # Login
    response = requests.post(f"{PROD_API}/auth/login", 
                           data={"username": EMAIL, "password": PASSWORD}, timeout=10)
    if response.status_code != 200:
        print("Login failed")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login OK")
    
    # Get contracts
    response = requests.get(f"{PROD_API}/rental-contracts/", headers=headers, timeout=10)
    if response.status_code != 200:
        print("Failed to get contracts")
        return
    
    contracts = response.json()
    print(f"Found {len(contracts)} contracts\n")
    
    # Get PDF files
    pdf_dir = Path("data/assets/contracts")
    if not pdf_dir.exists():
        print(f"PDF directory not found: {pdf_dir}")
        return
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files\n")
    
    uploaded = 0
    skipped = 0
    failed = 0
    
    # Process each PDF
    for pdf_file in sorted(pdf_files):
        filename = pdf_file.name
        
        # Find matching tenant
        matched_tenant = None
        for key, tenant_pattern in PDF_MAPPING.items():
            if filename.startswith(key):
                matched_tenant = tenant_pattern
                break
        
        if not matched_tenant:
            print(f"SKIP: No mapping for {filename[:50]}")
            skipped += 1
            continue
        
        # Find matching contract
        matched_contract = None
        for contract in contracts:
            tenant_name = contract['tenant_name'].lower()
            if matched_tenant.lower() in tenant_name or tenant_name in matched_tenant.lower():
                matched_contract = contract
                break
        
        if not matched_contract:
            print(f"NO CONTRACT: {filename[:50]} -> {matched_tenant}")
            failed += 1
            continue
        
        # Upload PDF
        try:
            with open(pdf_file, 'rb') as f:
                files = {'file': (filename, f, 'application/pdf')}
                response = requests.post(
                    f"{PROD_API}/rental-contracts/{matched_contract['id']}/upload-pdf",
                    files=files,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    uploaded += 1
                    print(f"OK: {filename[:40]:40} -> {matched_contract['tenant_name'][:30]}")
                else:
                    failed += 1
                    print(f"FAIL ({response.status_code}): {filename[:40]}")
                    
        except Exception as e:
            failed += 1
            print(f"ERROR: {filename[:40]} - {str(e)[:30]}")
    
    print(f"\nSUMMARY:")
    print(f"  Uploaded: {uploaded}")
    print(f"  Skipped: {skipped}")
    print(f"  Failed: {failed}")
    
    # Final check
    print(f"\nVERIFYING PDFs:")
    response = requests.get(f"{PROD_API}/rental-contracts/", headers=headers, timeout=10)
    if response.status_code == 200:
        contracts = response.json()
        with_pdf = sum(1 for c in contracts if c.get('contract_pdf_path'))
        print(f"  Contracts with PDFs: {with_pdf}/{len(contracts)}")

if __name__ == "__main__":
    upload_pdfs()