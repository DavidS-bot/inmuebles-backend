#!/usr/bin/env python3
"""Script para exportar todos los datos de la base de datos local"""

import sys
import os
import json
from datetime import datetime, date
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select
from app.db import engine
from app.models import Property, MortgageDetails, FinancialMovement, ClassificationRule

def date_serializer(obj):
    """Serializar dates y datetimes para JSON"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def export_all_data():
    """Exportar todos los datos a JSON"""
    data = {
        "properties": [],
        "mortgages": [],
        "financial_movements": [],
        "classification_rules": []
    }
    
    with Session(engine) as session:
        # Exportar propiedades
        properties = session.exec(select(Property)).all()
        for prop in properties:
            prop_dict = prop.model_dump()
            data["properties"].append(prop_dict)
        
        print(f"Exported {len(data['properties'])} properties")
        
        # Exportar hipotecas
        mortgages = session.exec(select(MortgageDetails)).all()
        for mortgage in mortgages:
            mortgage_dict = mortgage.model_dump()
            data["mortgages"].append(mortgage_dict)
        
        print(f"Exported {len(data['mortgages'])} mortgages")
        
        # Exportar movimientos financieros
        movements = session.exec(select(FinancialMovement)).all()
        for movement in movements:
            movement_dict = movement.model_dump()
            data["financial_movements"].append(movement_dict)
        
        print(f"Exported {len(data['financial_movements'])} financial movements")
        
        # Exportar reglas de clasificación
        rules = session.exec(select(ClassificationRule)).all()
        for rule in rules:
            rule_dict = rule.model_dump()
            data["classification_rules"].append(rule_dict)
        
        print(f"Exported {len(data['classification_rules'])} classification rules")
    
    # Guardar a archivo JSON
    with open("exported_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=date_serializer)
    
    print("All data exported to exported_data.json")
    return data

if __name__ == "__main__":
    export_all_data()