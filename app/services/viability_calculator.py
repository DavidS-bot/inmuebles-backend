import math
import json
from typing import Dict, List, Tuple
from datetime import datetime, date

def calculate_monthly_payment(loan_amount: float, annual_rate: float, years: int) -> float:
    """Calcular pago mensual de hipoteca usando fórmula estándar"""
    if annual_rate == 0:
        return loan_amount / (years * 12)
    
    monthly_rate = annual_rate / 12
    num_payments = years * 12
    
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                     ((1 + monthly_rate) ** num_payments - 1)
    
    return round(monthly_payment, 2)

def calculate_variable_rate_payment(study) -> float:
    """Calcular pago mensual inicial para préstamo variable"""
    if study.loan_type == "variable" and study.euribor_reset_vector:
        try:
            # Obtener vector de Euribor
            euribor_vector = json.loads(study.euribor_reset_vector) if isinstance(study.euribor_reset_vector, str) else study.euribor_reset_vector
            
            # Tipo inicial: Euribor actual + diferencial
            initial_rate = (euribor_vector[0] / 100) + (study.euribor_spread or 0.015)
            
            return calculate_monthly_payment(study.loan_amount, initial_rate, study.loan_term_years)
        except:
            # Fallback al tipo fijo si hay error
            return calculate_monthly_payment(study.loan_amount, study.interest_rate, study.loan_term_years)
    else:
        return calculate_monthly_payment(study.loan_amount, study.interest_rate, study.loan_term_years)

def calculate_monthly_expenses(study) -> float:
    """Calcular gastos mensuales totales"""
    annual_expenses = (
        (study.community_fees or 0) +
        study.property_tax_ibi +
        (study.life_insurance or 0) +
        study.home_insurance +
        (study.purchase_price * study.maintenance_percentage) +  # Mantenimiento anual
        (study.property_management_fee or 0)
    )
    
    return round(annual_expenses / 12, 2)

def calculate_risk_level(study) -> str:
    """Determinar nivel de riesgo basado en métricas clave"""
    risk_factors = 0
    
    # Factor 1: Rentabilidad neta baja
    if study.net_annual_return < 0.04:  # Menos del 4%
        risk_factors += 2
    elif study.net_annual_return < 0.06:  # Menos del 6%
        risk_factors += 1
    
    # Factor 2: Cashflow negativo
    if study.monthly_net_cashflow < 0:
        risk_factors += 2
    elif study.monthly_net_cashflow < 100:  # Menos de 100€/mes
        risk_factors += 1
    
    # Factor 3: LTV alto
    if study.loan_to_value > 0.85:  # Más del 85%
        risk_factors += 2
    elif study.loan_to_value > 0.75:  # Más del 75%
        risk_factors += 1
    
    # Factor 4: Renta cercana al break-even
    rent_buffer = (study.monthly_rent - study.break_even_rent) / study.monthly_rent
    if rent_buffer < 0.10:  # Menos del 10% de buffer
        risk_factors += 2
    elif rent_buffer < 0.20:  # Menos del 20% de buffer
        risk_factors += 1
    
    # Determinar nivel de riesgo
    if risk_factors >= 5:
        return "HIGH"
    elif risk_factors >= 3:
        return "MEDIUM"
    else:
        return "LOW"

def calculate_viability_metrics(study):
    """Calcular todas las métricas derivadas del estudio"""
    
    # 1. CÁLCULOS DE COMPRA
    study.purchase_costs = study.purchase_price * study.purchase_taxes_percentage
    study.total_purchase_price = (
        study.purchase_price + 
        study.purchase_costs + 
        (study.renovation_costs or 0) + 
        (study.real_estate_commission or 0)
    )
    
    # 2. CÁLCULOS DE FINANCIACIÓN
    study.down_payment = study.total_purchase_price - study.loan_amount
    study.loan_to_value = study.loan_amount / study.total_purchase_price if study.total_purchase_price > 0 else 0
    
    # Calcular pago mensual según tipo de préstamo
    if hasattr(study, 'loan_type') and study.loan_type == "variable":
        study.monthly_mortgage_payment = calculate_variable_rate_payment(study)
    else:
        study.monthly_mortgage_payment = calculate_monthly_payment(
            study.loan_amount, 
            study.interest_rate, 
            study.loan_term_years
        )
    
    # 3. CÁLCULOS DE GASTOS
    monthly_expenses = calculate_monthly_expenses(study)
    
    # 4. CÁLCULOS DE RENTABILIDAD
    study.monthly_net_cashflow = study.monthly_rent - study.monthly_mortgage_payment - monthly_expenses
    study.annual_net_cashflow = study.monthly_net_cashflow * 12
    
    # Rentabilidad neta anual (sobre equity invertido)
    if study.down_payment > 0:
        study.net_annual_return = study.annual_net_cashflow / study.down_payment
    else:
        study.net_annual_return = 0
    
    # 5. CÁLCULOS DE EQUITY
    # Interés mensual aproximado (primera cuota)
    if study.loan_amount > 0:
        monthly_interest = (study.loan_amount * study.interest_rate) / 12
        study.monthly_equity_increase = study.monthly_mortgage_payment - monthly_interest
    else:
        study.monthly_equity_increase = 0
    
    study.annual_equity_increase = study.monthly_equity_increase * 12
    
    # Rentabilidad total (cashflow + equity)
    total_annual_benefit = study.annual_net_cashflow + study.annual_equity_increase
    if study.down_payment > 0:
        study.total_annual_return = total_annual_benefit / study.down_payment
    else:
        study.total_annual_return = 0
    
    # 6. ANÁLISIS DE RIESGO
    study.break_even_rent = study.monthly_mortgage_payment + monthly_expenses
    
    # Determinar si es favorable (mínimo 5% rentabilidad neta)
    study.is_favorable = study.net_annual_return > 0.05 and study.monthly_net_cashflow > 0
    
    # Calcular nivel de riesgo
    study.risk_level = calculate_risk_level(study)
    
    # 7. ACTUALIZAR TIMESTAMP
    study.updated_at = datetime.utcnow()
    
    return study

def generate_temporal_projection(study, years: int = 10) -> List:
    """Generar proyección mes a mes durante X años"""
    if years > 30:
        years = 30  # Máximo 30 años
    
    projections = []
    
    # Variables iniciales
    current_loan_balance = study.loan_amount
    accumulated_cashflow = 0
    current_property_value = study.purchase_price
    accumulated_equity = study.down_payment
    
    # Tasas mensuales
    monthly_interest_rate = study.interest_rate / 12
    monthly_rent_increase = study.annual_rent_increase / 12
    property_appreciation_rate = 0.03 / 12  # 3% anual de revalorización
    
    # Gastos mensuales (constantes)
    monthly_expenses = calculate_monthly_expenses(study)
    
    for year in range(1, years + 1):
        for month in range(1, 13):
            # Renta con incremento anual
            months_elapsed = (year - 1) * 12 + month - 1
            current_monthly_rent = study.monthly_rent * ((1 + study.annual_rent_increase) ** ((year - 1)))
            
            # Cálculos de hipoteca
            if current_loan_balance > 0:
                monthly_interest = current_loan_balance * monthly_interest_rate
                monthly_principal = study.monthly_mortgage_payment - monthly_interest
                
                # No puede pagar más principal del que queda
                if monthly_principal > current_loan_balance:
                    monthly_principal = current_loan_balance
                    monthly_interest = study.monthly_mortgage_payment - monthly_principal
                
                current_loan_balance -= monthly_principal
                current_loan_balance = max(0, current_loan_balance)  # No puede ser negativo
            else:
                monthly_interest = 0
                monthly_principal = 0
            
            # Valor de propiedad con revalorización
            current_property_value *= (1 + property_appreciation_rate)
            
            # Cashflow del mes
            monthly_net_cashflow = current_monthly_rent - study.monthly_mortgage_payment - monthly_expenses
            accumulated_cashflow += monthly_net_cashflow
            
            # Equity acumulado
            accumulated_equity += monthly_principal
            
            # Métricas
            if study.down_payment > 0:
                annual_return = (monthly_net_cashflow * 12) / study.down_payment
                total_return_with_equity = ((monthly_net_cashflow + monthly_principal) * 12) / study.down_payment
            else:
                annual_return = 0
                total_return_with_equity = 0
            
            current_ltv = current_loan_balance / current_property_value if current_property_value > 0 else 0
            
            # Crear projection como diccionario primero, se convertirá en el router
            projection = {
                'viability_study_id': study.id,
                'year': year,
                'month': month,
                'outstanding_loan_balance': round(current_loan_balance, 2),
                'accumulated_equity': round(accumulated_equity, 2),
                'property_value': round(current_property_value, 2),
                'monthly_rent': round(current_monthly_rent, 2),
                'monthly_mortgage_payment': study.monthly_mortgage_payment,
                'monthly_interest': round(monthly_interest, 2),
                'monthly_principal': round(monthly_principal, 2),
                'monthly_expenses': monthly_expenses,
                'monthly_net_cashflow': round(monthly_net_cashflow, 2),
                'accumulated_cashflow': round(accumulated_cashflow, 2),
                'annual_return': round(annual_return, 4),
                'total_return_with_equity': round(total_return_with_equity, 4),
                'current_ltv': round(current_ltv, 4)
            }
            
            projections.append(projection)
    
    return projections

def perform_sensitivity_analysis(study, parameters: Dict) -> Dict:
    """Análisis de sensibilidad variando parámetros clave"""
    base_metrics = {
        'net_annual_return': study.net_annual_return,
        'monthly_cashflow': study.monthly_net_cashflow,
        'total_annual_return': study.total_annual_return
    }
    
    sensitivity_results = {
        'base_scenario': base_metrics,
        'scenarios': {}
    }
    
    # Escenarios a probar
    scenarios = {
        'rent_decrease_5': {'monthly_rent': study.monthly_rent * 0.95},
        'rent_decrease_10': {'monthly_rent': study.monthly_rent * 0.90},
        'rent_increase_10': {'monthly_rent': study.monthly_rent * 1.10},
        'interest_increase_1': {'interest_rate': study.interest_rate + 0.01},
        'interest_increase_2': {'interest_rate': study.interest_rate + 0.02},
        'maintenance_double': {'maintenance_percentage': study.maintenance_percentage * 2},
        'vacancy_1month': {'monthly_rent': study.monthly_rent * (11/12)},  # 1 mes vacío
        'vacancy_2months': {'monthly_rent': study.monthly_rent * (10/12)},  # 2 meses vacíos
    }
    
    for scenario_name, changes in scenarios.items():
        # Crear copia simple de las propiedades del estudio
        test_data = {
            'monthly_rent': getattr(study, 'monthly_rent', 0),
            'purchase_price': getattr(study, 'purchase_price', 0),
            'interest_rate': getattr(study, 'interest_rate', 0),
            'maintenance_percentage': getattr(study, 'maintenance_percentage', 0.01)
        }
        
        # Aplicar cambios
        for param, value in changes.items():
            test_data[param] = value
        
        # Calcular métricas simplificadas para el escenario
        # Esta es una versión simplificada que no requiere crear objetos completos
        rent_change = changes.get('monthly_rent', study.monthly_rent) / study.monthly_rent
        adjusted_annual_return = study.net_annual_return * rent_change
        adjusted_monthly_cashflow = study.monthly_net_cashflow * rent_change
        
        sensitivity_results['scenarios'][scenario_name] = {
            'net_annual_return': adjusted_annual_return,
            'monthly_cashflow': adjusted_monthly_cashflow,
            'total_annual_return': study.total_annual_return * rent_change,
            'changes': changes
        }
    
    return sensitivity_results

def compare_studies(studies: List) -> Dict:
    """Comparar múltiples estudios de viabilidad"""
    if len(studies) < 2:
        raise ValueError("Se necesitan al menos 2 estudios para comparar")
    
    comparison = {
        'summary': [],
        'best_cash_flow': None,
        'best_net_return': None,
        'best_total_return': None,
        'lowest_risk': None
    }
    
    best_cashflow_study = max(studies, key=lambda s: s.monthly_net_cashflow)
    best_net_return_study = max(studies, key=lambda s: s.net_annual_return)
    best_total_return_study = max(studies, key=lambda s: s.total_annual_return)
    
    # Encontrar el de menor riesgo
    risk_order = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2}
    lowest_risk_study = min(studies, key=lambda s: risk_order.get(s.risk_level, 1))
    
    for study in studies:
        comparison['summary'].append({
            'id': study.id,
            'name': study.study_name,
            'purchase_price': study.purchase_price,
            'monthly_rent': study.monthly_rent,
            'down_payment': study.down_payment,
            'monthly_cashflow': study.monthly_net_cashflow,
            'net_annual_return': study.net_annual_return,
            'total_annual_return': study.total_annual_return,
            'risk_level': study.risk_level,
            'is_favorable': study.is_favorable,
            'loan_to_value': study.loan_to_value
        })
    
    comparison['best_cash_flow'] = {
        'study_id': best_cashflow_study.id,
        'study_name': best_cashflow_study.study_name,
        'value': best_cashflow_study.monthly_net_cashflow
    }
    
    comparison['best_net_return'] = {
        'study_id': best_net_return_study.id,
        'study_name': best_net_return_study.study_name,
        'value': best_net_return_study.net_annual_return
    }
    
    comparison['best_total_return'] = {
        'study_id': best_total_return_study.id,
        'study_name': best_total_return_study.study_name,
        'value': best_total_return_study.total_annual_return
    }
    
    comparison['lowest_risk'] = {
        'study_id': lowest_risk_study.id,
        'study_name': lowest_risk_study.study_name,
        'risk_level': lowest_risk_study.risk_level
    }
    
    return comparison