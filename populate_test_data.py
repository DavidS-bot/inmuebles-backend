#!/usr/bin/env python3
"""Script para poblar datos de prueba en la base de datos"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from sqlmodel import Session, select
from app.db import engine
from app.models import Property, MortgageDetails

def populate_test_data():
    """Poblar datos de prueba para las propiedades existentes"""
    
    with Session(engine) as session:
        # Obtener todas las propiedades
        properties = session.exec(select(Property)).all()
        
        print(f"Encontradas {len(properties)} propiedades")
        
        for i, prop in enumerate(properties):
            print(f"Propiedad {prop.id}: {prop.address}")
            print(f"  - purchase_price: {prop.purchase_price}")
            print(f"  - acquisition_costs: {prop.acquisition_costs}")
            print(f"  - renovation_costs: {prop.renovation_costs}")
            
            # Actualizar purchase_price si está vacío
            if not prop.purchase_price:
                prop.purchase_price = 200000.0 + (i * 50000.0)  # Precios entre 200k y 450k
                print(f"  - Updated purchase_price to: {prop.purchase_price}")
            
            # Verificar si ya tiene hipoteca
            existing_mortgage = session.exec(
                select(MortgageDetails).where(MortgageDetails.property_id == prop.id)
            ).first()
            
            if not existing_mortgage:
                # Crear datos de hipoteca de prueba
                mortgage_amount = prop.purchase_price * 0.8  # 80% financiado
                mortgage = MortgageDetails(
                    property_id=prop.id,
                    bank_entity="Banco Santander",
                    mortgage_type="Variable",
                    initial_amount=mortgage_amount,
                    outstanding_balance=mortgage_amount * 0.9,  # 90% del inicial pendiente
                    margin_percentage=1.5,  # 1.5% margen
                    start_date=date(2020, 1, 1),
                    end_date=date(2050, 1, 1)
                )
                session.add(mortgage)
                print(f"  - Added mortgage: {mortgage_amount:.2f} initial, {mortgage.outstanding_balance:.2f} outstanding")
            else:
                print(f"  - Existing mortgage: {existing_mortgage.initial_amount} initial, {existing_mortgage.outstanding_balance} outstanding")
        
        session.commit()
        print("Datos de prueba actualizados correctamente")

if __name__ == "__main__":
    populate_test_data()