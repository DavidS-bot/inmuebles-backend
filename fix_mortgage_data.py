#!/usr/bin/env python3
"""Script para corregir datos de hipoteca"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from app.db import engine
from app.models import MortgageDetails

def fix_mortgage_data():
    """Corregir saldos pendientes de hipotecas"""
    
    with Session(engine) as session:
        mortgages = session.exec(select(MortgageDetails)).all()
        
        print(f"Encontradas {len(mortgages)} hipotecas")
        
        for mortgage in mortgages:
            if mortgage.outstanding_balance == 0.0:
                # Establecer saldo pendiente como 70% del importe inicial
                mortgage.outstanding_balance = mortgage.initial_amount * 0.7
                print(f"Propiedad {mortgage.property_id}: Updated outstanding_balance to {mortgage.outstanding_balance:.2f}")
        
        session.commit()
        print("Datos de hipoteca corregidos")

if __name__ == "__main__":
    fix_mortgage_data()