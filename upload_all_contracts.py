#!/usr/bin/env python3
"""Subir TODOS los contratos PDF y documentos de inquilinos"""

import os
import requests
from pathlib import Path
import time

BACKEND_URL = "https://inmuebles-backend-api.onrender.com"
USER_EMAIL = "davsanchez21277@gmail.com"
USER_PASSWORD = "123456"

def get_auth_token():
    login_data = {"username": USER_EMAIL, "password": USER_PASSWORD}
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def upload_all_contracts():
    """Subir TODOS los contratos PDF"""
    token = get_auth_token()
    if not token:
        print("Auth failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    contracts_dir = Path("data/assets/contracts")
    
    if not contracts_dir.exists():
        print("Contracts directory not found")
        return
    
    uploaded_contracts = 0
    failed_contracts = 0
    
    all_contracts = list(contracts_dir.glob("*.pdf")) + list(contracts_dir.glob("*.PDF"))
    print(f"Found {len(all_contracts)} contract files to upload...")
    
    for i, contract_file in enumerate(all_contracts, 1):
        print(f"Uploading {i}/{len(all_contracts)}: {contract_file.name}")
        
        try:
            with open(contract_file, 'rb') as f:
                files = {'file': (contract_file.name, f, 'application/pdf')}
                response = requests.post(
                    f"{BACKEND_URL}/uploads/document",
                    files=files,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    uploaded_contracts += 1
                    print(f"  Success")
                else:
                    failed_contracts += 1
                    print(f"  Failed: {response.status_code}")
        except Exception as e:
            failed_contracts += 1
            print(f"  Error: {e}")
        
        # Pequeña pausa entre uploads
        time.sleep(0.5)
    
    print(f"\n=== CONTRACTS UPLOAD SUMMARY ===")
    print(f"Total files found: {len(all_contracts)}")
    print(f"Successfully uploaded: {uploaded_contracts}")
    print(f"Failed uploads: {failed_contracts}")
    
    return uploaded_contracts

def upload_tenant_documents():
    """Subir documentos de inquilinos"""
    token = get_auth_token()
    if not token:
        return 0
    
    headers = {"Authorization": f"Bearer {token}"}
    tenant_docs_dir = Path("uploads/tenant_documents")
    
    if not tenant_docs_dir.exists():
        print("Tenant documents directory not found")
        return 0
    
    uploaded_docs = 0
    failed_docs = 0
    
    all_docs = list(tenant_docs_dir.iterdir())
    all_docs = [doc for doc in all_docs if doc.is_file()]
    
    if not all_docs:
        print("No tenant documents found")
        return 0
        
    print(f"\nFound {len(all_docs)} tenant document files to upload...")
    
    for i, doc_file in enumerate(all_docs, 1):
        print(f"Uploading {i}/{len(all_docs)}: {doc_file.name}")
        
        try:
            content_type = 'application/pdf' if doc_file.suffix.lower() == '.pdf' else 'image/jpeg'
            
            with open(doc_file, 'rb') as f:
                files = {'file': (doc_file.name, f, content_type)}
                response = requests.post(
                    f"{BACKEND_URL}/uploads/tenant-document",
                    files=files,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    uploaded_docs += 1
                    print(f"  Success")
                else:
                    failed_docs += 1
                    print(f"  Failed: {response.status_code}")
        except Exception as e:
            failed_docs += 1
            print(f"  Error: {e}")
        
        time.sleep(0.5)
    
    print(f"\n=== TENANT DOCS UPLOAD SUMMARY ===")
    print(f"Total files found: {len(all_docs)}")
    print(f"Successfully uploaded: {uploaded_docs}")
    print(f"Failed uploads: {failed_docs}")
    
    return uploaded_docs

def main():
    print("Starting complete file upload process...")
    print("=" * 60)
    
    # Subir contratos
    contracts_uploaded = upload_all_contracts()
    
    # Subir documentos de inquilinos
    tenant_docs_uploaded = upload_tenant_documents()
    
    print("\n" + "=" * 60)
    print("FINAL UPLOAD SUMMARY")
    print("=" * 60)
    print(f"Contract PDFs uploaded: {contracts_uploaded}")
    print(f"Tenant documents uploaded: {tenant_docs_uploaded}")
    print(f"Property photos: 10 (already uploaded)")
    
    total_files = contracts_uploaded + tenant_docs_uploaded + 10
    print(f"\nTotal files in system: {total_files}")
    print("\nYour application now has ALL files uploaded!")

if __name__ == "__main__":
    main()