#!/usr/bin/env python3
"""Script para verificar directamente qué está devolviendo analytics"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime
from sqlmodel import Session, select
from app.db import engine
from app.models import Property, MortgageDetails, FinancialMovement, RentalContract
from app.routers.mortgage_calculator import calculate_monthly_payment_detailed, calculate_remaining_months

def simulate_analytics_endpoint():
    """Simular exactamente lo que hace el endpoint analytics"""
    
    with Session(engine) as session:
        property_id = 1
        year = 2025
        
        # Obtener la propiedad
        property_data = session.get(Property, property_id)
        if not property_data:
            print("ERROR: Propiedad no encontrada")
            return
        
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
        
        # Ingresos por categoría
        rent_income = sum(m.amount for m in movements if m.category == "Renta" and m.amount > 0)
        
        # Gastos por categoría
        expenses_by_category = {}
        for movement in movements:
            if movement.amount < 0:
                category = movement.subcategory or movement.category
                expenses_by_category[category] = expenses_by_category.get(category, 0) + abs(movement.amount)
        
        # Obtener hipoteca de la propiedad
        mortgage = session.exec(
            select(MortgageDetails)
            .where(MortgageDetails.property_id == property_id)
        ).first()
        
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
        
        # ROI sobre cash aportado (más realista)
        roi_on_cash = (net_income / cash_contributed * 100) if cash_contributed > 0 else 0
        
        # ROI sobre inversión total (tradicional)
        roi_on_investment = (net_income / total_investment * 100) if total_investment > 0 else 0
        
        # Rental Yield (Rentabilidad bruta sobre cash)
        gross_yield_cash = (rent_income / cash_contributed * 100) if cash_contributed > 0 else 0
        gross_yield_investment = (rent_income / total_investment * 100) if total_investment > 0 else 0
        
        # Cash flow mensual promedio
        monthly_cash_flow = net_income / 12
        
        # Contrato activo
        active_contract = session.exec(
            select(RentalContract)
            .where(RentalContract.property_id == property_id)
            .where(RentalContract.is_active == True)
        ).first()
        
        # Estructura de respuesta exacta
        response = {
            "property": {
                "id": property_data.id,
                "address": property_data.address,
                "total_investment": total_investment,
                "cash_contributed": cash_contributed,
                "initial_debt": initial_debt,
                "purchase_price": property_data.purchase_price,
                "current_value": property_data.appraisal_value
            },
            "financial_metrics": {
                "total_income": total_income,
                "total_expenses": total_expenses,
                "net_income": net_income,
                "roi_on_cash": round(roi_on_cash, 2),
                "roi_on_investment": round(roi_on_investment, 2),
                "gross_yield_cash": round(gross_yield_cash, 2),
                "gross_yield_investment": round(gross_yield_investment, 2),
                "monthly_cash_flow": round(monthly_cash_flow, 2)
            },
            "income_breakdown": {
                "rent": rent_income,
                "other": total_income - rent_income
            },
            "expenses_by_category": expenses_by_category,
            "rental_info": {
                "active_contract": bool(active_contract),
                "monthly_rent": active_contract.monthly_rent if active_contract else 0,
                "tenant_name": active_contract.tenant_name if active_contract else None,
                "contract_end": active_contract.end_date.isoformat() if active_contract and active_contract.end_date else None
            },
            "mortgage_info": {
                "has_mortgage": bool(mortgage),
                "outstanding_balance": mortgage.outstanding_balance if mortgage else 0,
                "monthly_payment": 0 if not mortgage else calculate_monthly_payment_detailed(
                    mortgage.outstanding_balance, 5.0, mortgage.start_date, mortgage.end_date
                ),
                "current_rate": (1.5 + 3.5) if mortgage else 0,  # margin + euribor estimado
                "remaining_months": calculate_remaining_months(mortgage.end_date) if mortgage else 0,
                "start_date": mortgage.start_date.isoformat() if mortgage else None,
                "end_date": mortgage.end_date.isoformat() if mortgage else None
            },
            "year": year
        }
        
        print("=== RESPONSE STRUCTURE ===")
        print(f"property.cash_contributed: {response['property']['cash_contributed']}")
        print(f"property.total_investment: {response['property']['total_investment']}")
        print(f"property.initial_debt: {response['property']['initial_debt']}")
        print(f"property.purchase_price: {response['property']['purchase_price']}")
        print("")
        print("Full property object:")
        import json
        print(json.dumps(response['property'], indent=2))

if __name__ == "__main__":
    simulate_analytics_endpoint()