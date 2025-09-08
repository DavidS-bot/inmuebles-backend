#!/usr/bin/env python3
"""
Simple local PDF server to serve contract PDFs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from pathlib import Path

app = FastAPI(title="Local PDF Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Local PDF Server is running"}

@app.get("/contract/{contract_id}")
def serve_contract_pdf(contract_id: int):
    """Serve contract PDF by ID"""
    
    # Map contract IDs to local file paths
    # This is based on the local database contract paths
    contract_files = {
        1: "data/assets/contracts/contract_1_Contrato de Rocío. Aranguren, 68. 18 de Noviembre 2022.pdf",
        2: "data/assets/contracts/contract_2_Contrato de arrendamiento Susana y Jorge. Aranguren, 66. 30 de Junio 2022. Firmado.pdf",
        3: "data/assets/contracts/contract_3_Alvaro. Contrato de arrendamiento de vivienda habitual. Aranguren, nº 22. 14 de Junio 2025. (2).pdf",
        4: "data/assets/contracts/contract_4_Contrato de arrendamiento de vivienda habitual. Aranguren, 22. J. Antonio y Maria. 16-12-2023.pdf",
        5: "data/assets/contracts/contract_5_Alvaro. Contrato de arrendamiento de vivienda habitual. Aranguren, nº 22. 14 de Junio 2025. (2).pdf",
        6: "data/assets/contracts/contract_6_Draft Lease Contract EN_SP Antonio-Olga. Calle Platón, 30. Jerez de la Fra. Cádiz. - Signed DSR.pdf",
        7: "data/assets/contracts/contract_7_Contrato Diego y Soledad. Platón, 30. 1 de Julio del 2022 FIRMADO.pdf",
        8: "data/assets/contracts/contract_8_Contrato de Arrendamiento. D. Leandro Emanuel. Pozoalbero. 24-02-25.pdf",
        9: "data/assets/contracts/contract_9_Contrato de arrendamiento habitual. Piso Pozoalbero. Sergio Bravo Bañasco. 25 de Febrero´24.pdf",
        10: "data/assets/contracts/contract_10_Contrato arrendamiento Judit y Jesús. Lago de Enol, 1. P. 1-1F. (12-01-25).pdf",
        11: "data/assets/contracts/contract_11_Contrato de arrendamiento. Antonio. P. 1. Planta 2. Letra A 11-06-23.pdf",
        12: "data/assets/contracts/contract_12_CONTRA_1.PDF",
        14: "data/assets/contracts/contract_14_Contrato arrendamiento Roberto y Kerthyns. Lago de Enol, 1. Bloque 2. Bajo n.4 (17-01-2025).pdf",
        15: "data/assets/contracts/contract_15_Contrato de arrendamiento de vivienda habitual. Manuela. Bloque 2. Bajo 4 Firmado 15-06-2023.pdf",
        16: "data/assets/contracts/contract_16_Contrato arrendamiento. Judit. Lago de Enol. Bloque 2. Bajo n. 4. 22 de Octubre 2024. (firmado).pdf",
        17: "data/assets/contracts/contract_17_Contrato de arrendamiento FIRMADO. D. Jesús Javier y Carolina Olalla. Lago de Enol. Bloque 2. 1 P. Vivienda nº 9. Jerez.29-07-2023.docx.pdf",
        18: "data/assets/contracts/contract_18_Contrato de arrendamiento Lucia. Lago de Enol, 2. 2ª planta. Número 9. (02-05-25).pdf",
        19: "data/assets/contracts/contract_19_Contrato arrendamiento Manuel Orellana. Lago de Enol, 1. P1. 1ºG. (27-08-24).pdf",
        20: "data/assets/contracts/contract_20_Eva y Manuel. Contrato arrendamiento. Lago de Enol. 1-1G. 01-07-25.pdf"
    }
    
    if contract_id not in contract_files:
        raise HTTPException(status_code=404, detail=f"Contract {contract_id} not found")
    
    file_path = contract_files[contract_id]
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"PDF file not found at {file_path}")
    
    # Extract filename for download
    filename = os.path.basename(file_path)
    
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Cache-Control": "max-age=3600"}  # Cache for 1 hour
    )

@app.get("/health")
def health():
    return {"status": "healthy", "service": "PDF Server"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8002))  # Different port from Bankinter API
    print(f"Starting PDF server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)