#!/usr/bin/env python3
"""
Script para importar reglas de clasificación de producción sin duplicar
"""

import json
from app.db import get_session
from app.models import ClassificationRule
from sqlmodel import select

def load_production_rules():
    """Cargar reglas de producción desde archivo JSON"""
    with open('rules_for_local_import.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['rules_for_import']

def get_existing_keywords(session):
    """Obtener keywords de reglas existentes"""
    statement = select(ClassificationRule)
    existing_rules = session.exec(statement).all()
    return {rule.keyword.strip() for rule in existing_rules}

def import_new_rules():
    """Importar solo las reglas nuevas"""
    session = next(get_session())
    
    try:
        # Cargar reglas de producción
        production_rules = load_production_rules()
        print(f"Reglas de produccion cargadas: {len(production_rules)}")
        
        # Obtener keywords existentes
        existing_keywords = get_existing_keywords(session)
        print(f"Reglas existentes en local: {len(existing_keywords)}")
        
        # Filtrar reglas nuevas
        new_rules = []
        duplicates = 0
        
        for rule in production_rules:
            keyword = rule['keyword'].strip()
            if keyword not in existing_keywords:
                new_rules.append(rule)
            else:
                duplicates += 1
                print(f"Skipping duplicate: {keyword}")
        
        print(f"Reglas nuevas a importar: {len(new_rules)}")
        print(f"Duplicados omitidos: {duplicates}")
        
        if not new_rules:
            print("No hay nuevas reglas para importar")
            return
        
        # Confirmar importación
        confirm = input(f"\nImportar {len(new_rules)} reglas nuevas? (y/N): ")
        if confirm.lower() != 'y':
            print("Importacion cancelada")
            return
        
        # Importar reglas nuevas
        imported = 0
        for rule_data in new_rules:
            try:
                rule = ClassificationRule(
                    user_id=1,  # Assuming user ID 1
                    property_id=rule_data.get('property_id'),
                    keyword=rule_data['keyword'],
                    category=rule_data['category'],
                    subcategory=rule_data.get('subcategory'),
                    tenant_name=rule_data.get('tenant_name'),
                    is_active=rule_data.get('is_active', True),
                    priority=1
                )
                
                session.add(rule)
                imported += 1
                print(f"Added: {rule_data['keyword']} -> {rule_data['category']}")
                
            except Exception as e:
                print(f"Error importing rule {rule_data['keyword']}: {e}")
        
        # Commit changes
        session.commit()
        print(f"\nSuccessfully imported {imported} new classification rules!")
        
        # Show final stats
        final_statement = select(ClassificationRule)
        final_count = len(session.exec(final_statement).all())
        print(f"Total rules in database: {final_count}")
        
    except Exception as e:
        session.rollback()
        print(f"Error during import: {e}")
        
    finally:
        session.close()

if __name__ == "__main__":
    print("Importando reglas de clasificacion de produccion...")
    print("=" * 50)
    import_new_rules()