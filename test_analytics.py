#!/usr/bin/env python3
"""Script para probar la lógica de analytics directamente"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime
from sqlmodel import Session, select
from app.db import engine
from app.models import Property, MortgageDetails, FinancialMovement

def test_analytics_logic():
    """Probar la lógica de analytics que debería usar el endpoint"""
    
    with Session(engine) as session:
        property_id = 1
        year = 2025
        
        # Obtener la propiedad
        property_data = session.get(Property, property_id)
        if not property_data:
            print("Propiedad no encontrada")
            return
        
        # Obtener hipoteca
        mortgage = session.exec(
            select(MortgageDetails)
            .where(MortgageDetails.property_id == property_id)
        ).first()
        
        # Movimientos del año
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        movements = session.exec(
            select(FinancialMovement)
            .where(FinancialMovement.property_id == property_id)
            .where(FinancialMovement.date >= start_date)
            .where(FinancialMovement.date <= end_date)
        ).all()
        
        # Cálculos básicos
        total_income = sum(m.amount for m in movements if m.amount > 0)
        total_expenses = sum(abs(m.amount) for m in movements if m.amount < 0)
        net_income = total_income - total_expenses
        
        # Cálculo de inversión total: precio de compra + 10% proxy para impuestos y gastos
        purchase_price = property_data.purchase_price or 0
        total_investment = purchase_price * 1.10  # Precio compra + 10% proxy
        
        # Cash aportado: precio de compra - importe inicial hipoteca (de gestión hipotecaria)
        initial_debt = 0
        if mortgage:
            initial_debt = mortgage.initial_amount
        
        cash_contributed = purchase_price - initial_debt
        # Asegurar que cash_contributed sea al menos 20% del precio de compra
        if cash_contributed <= 0:
            cash_contributed = purchase_price * 0.2
        
        print(f"=== Analytics Test for Property {property_id} ===")
        print(f"Purchase Price: €{purchase_price:,.2f}")
        print(f"Total Investment: €{total_investment:,.2f}")
        print(f"Initial Debt: €{initial_debt:,.2f}")
        print(f"Cash Contributed: €{cash_contributed:,.2f}")
        print(f"")
        print(f"Movements in {year}: {len(movements)}")
        print(f"Total Income: €{total_income:,.2f}")
        print(f"Total Expenses: €{total_expenses:,.2f}")
        print(f"Net Income: €{net_income:,.2f}")
        print(f"")
        print(f"Expected return structure:")
        print({
            "property": {
                "id": property_data.id,
                "address": property_data.address,
                "total_investment": total_investment,
                "cash_contributed": cash_contributed,
                "initial_debt": initial_debt,
                "purchase_price": property_data.purchase_price,
                "current_value": property_data.appraisal_value
            }
        })

if __name__ == "__main__":
    test_analytics_logic()