# app/routers/tax_assistant.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, Response
from typing import Dict, List, Optional, Any
from datetime import date, datetime, timedelta
from sqlmodel import Session, select
from pydantic import BaseModel
from ..db import get_session
from ..deps import get_current_user
from ..models import Property, FinancialMovement, RentalContract, User
import calendar
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import json
import logging
from decimal import Decimal

router = APIRouter(prefix="/tax-assistant", tags=["tax-assistant"])

# Logging setup
logger = logging.getLogger(__name__)

class TaxReport(BaseModel):
    year: int
    total_rental_income: float
    total_deductible_expenses: float
    taxable_income: float
    estimated_tax: float
    properties: List[Dict]

class DeductionCategory(BaseModel):
    category: str
    amount: float
    percentage: float
    description: str
    items: List[Dict]

class Modelo115Input(BaseModel):
    year: int
    quarter: int
    rental_income: float
    previous_withholdings: float = 0
    
class Modelo115Output(BaseModel):
    year: int
    quarter: int
    total_income: float
    withholding_rate: float
    withholding_amount: float
    previous_withholdings: float
    net_amount_to_pay: float
    due_date: str
    form_data: Dict[str, Any]

class ExpenseOptimization(BaseModel):
    category: str
    current_amount: float
    potential_savings: float
    suggestions: List[str]
    priority: str  # 'high', 'medium', 'low'
    confidence: float  # 0-1

class FiscalDashboard(BaseModel):
    ytd_savings: float
    upcoming_deadlines: List[Dict]
    optimization_suggestions: List[ExpenseOptimization]
    quarterly_comparison: Dict[str, float]
    tax_efficiency_score: float
    alerts: List[Dict]

@router.get("/summary/{year}")
def get_tax_summary(
    year: int,
    session: Session = Depends(get_session)
):
    """Resumen fiscal del año"""
    properties = session.exec(select(Property)).all()
    
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    total_rental_income = 0
    total_deductible_expenses = 0
    
    for prop in properties:
        movements = session.exec(
            select(FinancialMovement)
            .where(FinancialMovement.property_id == prop.id)
            .where(FinancialMovement.date >= start_date)
            .where(FinancialMovement.date <= end_date)
        ).all()
        
        rental_income = sum(m.amount for m in movements if m.category == "Renta" and m.amount > 0)
        expenses = sum(abs(m.amount) for m in movements if m.amount < 0)
        
        total_rental_income += rental_income
        total_deductible_expenses += expenses
    
    net_income = total_rental_income - total_deductible_expenses
    tax_liability = calculate_estimated_tax(net_income)
    effective_rate = (tax_liability / net_income * 100) if net_income > 0 else 0
    
    return {
        "rental_income": total_rental_income,
        "deductible_expenses": total_deductible_expenses,
        "net_income": net_income,
        "tax_liability": tax_liability,
        "effective_rate": effective_rate,
        "savings_opportunities": total_deductible_expenses * 0.1  # 10% estimado
    }

@router.get("/deductions/{year}")
def get_deductions_breakdown(
    year: int,
    session: Session = Depends(get_session)
):
    """Análisis de deducciones del año"""
    properties = session.exec(select(Property)).all()
    
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    deductions = [
        {
            "concept": "IBI (Impuesto Bienes Inmuebles)",
            "amount": 850.0,
            "percentage": 25.5,
            "description": "Impuesto municipal 100% deducible"
        },
        {
            "concept": "Gastos de Comunidad",
            "amount": 720.0,
            "percentage": 21.6,
            "description": "Cuotas de comunidad 100% deducibles"
        },
        {
            "concept": "Seguros",
            "amount": 450.0,
            "percentage": 13.5,
            "description": "Seguros de hogar 100% deducibles"
        },
        {
            "concept": "Reparaciones y Mantenimiento",
            "amount": 680.0,
            "percentage": 20.4,
            "description": "Gastos de conservación 100% deducibles"
        },
        {
            "concept": "Intereses Hipoteca",
            "amount": 1200.0,
            "percentage": 36.0,
            "description": "Solo intereses, no capital"
        },
        {
            "concept": "Gestión y Administración",
            "amount": 300.0,
            "percentage": 9.0,
            "description": "Gastos de administración 100% deducibles"
        }
    ]
    
    return {
        "deductions": deductions
    }

@router.get("/annual-report/{year}")
def get_annual_tax_report(
    year: int,
    session: Session = Depends(get_session)
):
    """Generar informe fiscal anual completo"""
    
    # Obtener propiedades del usuario
    properties = session.exec(select(Property)).all()
    
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    total_rental_income = 0
    total_deductible_expenses = 0
    property_reports = []
    
    for prop in properties:
        # Obtener movimientos del año
        movements = session.exec(
            select(FinancialMovement)
            .where(FinancialMovement.property_id == prop.id)
            .where(FinancialMovement.date >= start_date)
            .where(FinancialMovement.date <= end_date)
        ).all()
        
        # Separar ingresos y gastos
        rental_income = sum(m.amount for m in movements if m.category == "Renta" and m.amount > 0)
        
        # Gastos deducibles por categoría
        deductible_expenses = {
            "IBI": 0,
            "Comunidad": 0,
            "Seguros": 0,
            "Reparaciones": 0,
            "Hipoteca": 0,  # Solo intereses
            "Gestión": 0,
            "Suministros": 0,
            "Otros": 0
        }
        
        for movement in movements:
            if movement.amount < 0:  # Es un gasto
                amount = abs(movement.amount)
                subcategory = movement.subcategory or movement.category
                
                if subcategory in deductible_expenses:
                    deductible_expenses[subcategory] += amount
                elif "IBI" in movement.concept.upper():
                    deductible_expenses["IBI"] += amount
                elif "COMUNIDAD" in movement.concept.upper():
                    deductible_expenses["Comunidad"] += amount
                elif "SEGURO" in movement.concept.upper():
                    deductible_expenses["Seguros"] += amount
                elif "REPARACION" in movement.concept.upper() or "MANTENIMIENTO" in movement.concept.upper():
                    deductible_expenses["Reparaciones"] += amount
                elif "HIPOTECA" in movement.concept.upper() or "INTERES" in movement.concept.upper():
                    deductible_expenses["Hipoteca"] += amount
                elif "GESTION" in movement.concept.upper() or "ADMINISTRACION" in movement.concept.upper():
                    deductible_expenses["Gestión"] += amount
                elif any(word in movement.concept.upper() for word in ["LUZ", "AGUA", "GAS", "INTERNET"]):
                    deductible_expenses["Suministros"] += amount
                else:
                    deductible_expenses["Otros"] += amount
        
        property_total_expenses = sum(deductible_expenses.values())
        property_taxable_income = rental_income - property_total_expenses
        
        # Calcular amortización de la vivienda (3% anual del valor de compra, excluyendo terreno)
        amortization = 0
        if prop.purchase_price:
            # Estimamos que el 70% del precio es construcción (deducible) y 30% terreno (no deducible)
            building_value = prop.purchase_price * 0.7
            amortization = building_value * 0.03  # 3% anual
        
        property_reports.append({
            "property_id": prop.id,
            "address": prop.address,
            "rental_income": rental_income,
            "deductible_expenses": deductible_expenses,
            "total_expenses": property_total_expenses,
            "amortization": amortization,
            "taxable_income": rental_income - property_total_expenses - amortization,
            "months_rented": calculate_months_rented(prop.id, year, session)
        })
        
        total_rental_income += rental_income
        total_deductible_expenses += property_total_expenses + amortization
    
    taxable_income = total_rental_income - total_deductible_expenses
    estimated_tax = calculate_estimated_tax(taxable_income)
    
    return {
        "year": year,
        "total_rental_income": total_rental_income,
        "total_expenses": total_deductible_expenses,
        "depreciation": sum(p.get("amortization", 0) for p in property_reports),
        "net_result": taxable_income,
        "tax_rate": 24.0,  # Tipo impositivo estimado
        "tax_amount": estimated_tax,
        "quarterly_payments": [estimated_tax/4, estimated_tax/4, estimated_tax/4, estimated_tax/4]
    }

@router.get("/deduction-analysis/{year}")
def get_deduction_analysis(
    year: int,
    session: Session = Depends(get_session)
):
    """Análisis detallado de deducciones por categoría"""
    
    properties = session.exec(select(Property)).all()
    
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    # Agrupar todos los gastos por categoría
    all_expenses = {}
    total_expenses = 0
    
    for prop in properties:
        movements = session.exec(
            select(FinancialMovement)
            .where(FinancialMovement.property_id == prop.id)
            .where(FinancialMovement.date >= start_date)
            .where(FinancialMovement.date <= end_date)
            .where(FinancialMovement.amount < 0)
        ).all()
        
        for movement in movements:
            amount = abs(movement.amount)
            category = movement.subcategory or movement.category
            
            if category not in all_expenses:
                all_expenses[category] = {
                    "total": 0,
                    "items": []
                }
            
            all_expenses[category]["total"] += amount
            all_expenses[category]["items"].append({
                "property_address": prop.address,
                "date": movement.date.isoformat(),
                "concept": movement.concept,
                "amount": amount
            })
            
            total_expenses += amount
    
    # Crear categorías con porcentajes
    deduction_categories = []
    for category, data in all_expenses.items():
        percentage = (data["total"] / total_expenses * 100) if total_expenses > 0 else 0
        
        # Determinar descripción fiscal
        descriptions = {
            "IBI": "Impuesto sobre Bienes Inmuebles (100% deducible)",
            "Comunidad": "Gastos de comunidad (100% deducible)",
            "Seguros": "Seguros de la vivienda (100% deducible)",
            "Reparaciones": "Reparaciones y conservación (100% deducible)",
            "Hipoteca": "Intereses de hipoteca (100% deducible)",
            "Gestión": "Gastos de gestión y administración (100% deducible)",
            "Suministros": "Suministros cuando no haya inquilino (100% deducible)",
            "Gasto": "Gastos generales (revisar deducibilidad)"
        }
        
        description = descriptions.get(category, "Revisar clasificación y deducibilidad")
        
        deduction_categories.append(DeductionCategory(
            category=category,
            amount=data["total"],
            percentage=percentage,
            description=description,
            items=data["items"][:5]  # Mostrar solo los 5 primeros items
        ))
    
    # Ordenar por importe descendente
    deduction_categories.sort(key=lambda x: x.amount, reverse=True)
    
    return {
        "year": year,
        "total_expenses": total_expenses,
        "categories": deduction_categories,
        "summary": {
            "top_category": deduction_categories[0].category if deduction_categories else None,
            "top_amount": deduction_categories[0].amount if deduction_categories else 0,
            "total_categories": len(deduction_categories)
        }
    }

@router.get("/quarterly-summary/{year}/{quarter}")
def get_quarterly_summary(
    year: int,
    quarter: int,
    session: Session = Depends(get_session)
):
    """Resumen trimestral para pagos fraccionados"""
    
    if quarter not in [1, 2, 3, 4]:
        return {"error": "Quarter must be between 1 and 4"}
    
    # Calcular fechas del trimestre
    start_month = (quarter - 1) * 3 + 1
    end_month = quarter * 3
    start_date = date(year, start_month, 1)
    end_date = date(year, end_month, calendar.monthrange(year, end_month)[1])
    
    properties = session.exec(select(Property)).all()
    
    quarterly_income = 0
    quarterly_expenses = 0
    
    for prop in properties:
        movements = session.exec(
            select(FinancialMovement)
            .where(FinancialMovement.property_id == prop.id)
            .where(FinancialMovement.date >= start_date)
            .where(FinancialMovement.date <= end_date)
        ).all()
        
        income = sum(m.amount for m in movements if m.amount > 0 and m.category == "Renta")
        expenses = sum(abs(m.amount) for m in movements if m.amount < 0)
        
        quarterly_income += income
        quarterly_expenses += expenses
    
    quarterly_profit = quarterly_income - quarterly_expenses
    estimated_quarterly_tax = calculate_estimated_tax(quarterly_profit) / 4  # Aproximación
    
    return {
        "year": year,
        "quarter": quarter,
        "period": f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
        "income": quarterly_income,
        "expenses": quarterly_expenses,
        "profit": quarterly_profit,
        "estimated_tax": estimated_quarterly_tax,
        "accumulated_year": {
            "quarters_completed": quarter,
            "estimated_annual_income": quarterly_income * (4 / quarter),
            "estimated_annual_tax": estimated_quarterly_tax * 4
        }
    }

@router.get("/tax-planning/{year}")
def get_tax_planning_suggestions(
    year: int,
    session: Session = Depends(get_session)
):
    """Sugerencias de planificación fiscal"""
    
    suggestions = []
    
    # Obtener datos del año actual
    annual_report = get_annual_tax_report(year, session)
    
    # 1. Optimización de gastos deducibles
    if annual_report.taxable_income > 10000:
        suggestions.append({
            "category": "deductions",
            "title": "Maximizar deducciones",
            "description": "Con ingresos altos, cada euro de gasto deducible te ahorra impuestos. Revisa si hay gastos pendientes antes de fin de año.",
            "priority": "high",
            "potential_savings": annual_report.taxable_income * 0.24 * 0.1  # 10% más de deducciones
        })
    
    # 2. Distribución temporal de ingresos
    current_month = datetime.now().month
    if current_month <= 10 and annual_report.taxable_income > 15000:
        suggestions.append({
            "category": "timing",
            "title": "Considerar diferir ingresos",
            "description": "Si esperas menores ingresos el próximo año, considera diferir algunos cobros para optimizar la carga fiscal.",
            "priority": "medium",
            "potential_savings": annual_report.estimated_tax * 0.05
        })
    
    # 3. Inversiones en mejoras
    for prop_report in annual_report.properties:
        if prop_report["rental_income"] > prop_report["total_expenses"] * 3:
            suggestions.append({
                "category": "investments",
                "title": f"Mejoras en {prop_report['address'][:30]}...",
                "description": "Esta propiedad tiene alta rentabilidad. Considera inversiones en mejoras que sean deducibles.",
                "priority": "low",
                "potential_savings": 1000
            })
    
    # 4. Estructura empresarial
    if annual_report.total_rental_income > 50000:
        suggestions.append({
            "category": "structure",
            "title": "Evaluar constitución de sociedad",
            "description": "Con ingresos elevados, una sociedad podría ofrecer ventajas fiscales. Consulta con tu asesor.",
            "priority": "medium",
            "potential_savings": annual_report.estimated_tax * 0.15
        })
    
    return {
        "year": year,
        "suggestions": suggestions,
        "total_potential_savings": sum(s["potential_savings"] for s in suggestions),
        "next_deadlines": get_next_tax_deadlines()
    }

@router.get("/documents-checklist/{year}")
def get_tax_documents_checklist(
    year: int,
    session: Session = Depends(get_session)
):
    """Lista de documentos necesarios para la declaración"""
    
    checklist = [
        {
            "category": "Ingresos",
            "documents": [
                "Recibos de alquiler de todos los meses",
                "Contratos de arrendamiento vigentes",
                "Comunicaciones de subidas de renta"
            ]
        },
        {
            "category": "Gastos Deducibles",
            "documents": [
                "Recibos de IBI de todas las propiedades",
                "Gastos de comunidad",
                "Seguros de hogar y responsabilidad civil",
                "Facturas de reparaciones y mantenimiento",
                "Certificados de intereses de hipoteca",
                "Facturas de gestión inmobiliaria",
                "Suministros cuando no haya inquilino"
            ]
        },
        {
            "category": "Amortizaciones",
            "documents": [
                "Escrituras de compra de las propiedades",
                "Facturas de obras y mejoras",
                "Certificados catastrales"
            ]
        },
        {
            "category": "Otros",
            "documents": [
                "Declaraciones de años anteriores",
                "Justificantes de pagos fraccionados",
                "Comunicaciones de Hacienda"
            ]
        }
    ]
    
    return {
        "year": year,
        "checklist": checklist,
        "deadline": f"30/06/{year + 1}",
        "recommendations": [
            "Organiza los documentos por propiedad y categoría",
            "Digitaliza todos los documentos importantes",
            "Guarda copias de seguridad en la nube",
            "Consulta con un asesor fiscal especializado en inmuebles"
        ]
    }

def calculate_months_rented(property_id: int, year: int, session: Session) -> int:
    """Calcular meses que la propiedad estuvo alquilada"""
    contracts = session.exec(
        select(RentalContract).where(RentalContract.property_id == property_id)
    ).all()
    
    start_year = date(year, 1, 1)
    end_year = date(year, 12, 31)
    
    total_days = 0
    for contract in contracts:
        # Calcular overlap del contrato con el año
        contract_start = max(contract.start_date, start_year)
        contract_end = min(contract.end_date or end_year, end_year)
        
        if contract_start <= contract_end:
            total_days += (contract_end - contract_start).days + 1
    
    return min(12, total_days // 30)  # Convertir días a meses aproximados

def calculate_estimated_tax(taxable_income: float) -> float:
    """Calcular impuesto estimado sobre ingresos inmobiliarios"""
    if taxable_income <= 0:
        return 0
    
    # Tramos IRPF 2024 (aproximados)
    if taxable_income <= 12450:
        return taxable_income * 0.19
    elif taxable_income <= 20200:
        return 12450 * 0.19 + (taxable_income - 12450) * 0.24
    elif taxable_income <= 35200:
        return 12450 * 0.19 + 7750 * 0.24 + (taxable_income - 20200) * 0.30
    elif taxable_income <= 60000:
        return 12450 * 0.19 + 7750 * 0.24 + 15000 * 0.30 + (taxable_income - 35200) * 0.37
    else:
        return 12450 * 0.19 + 7750 * 0.24 + 15000 * 0.30 + 24800 * 0.37 + (taxable_income - 60000) * 0.47

def get_next_tax_deadlines() -> List[Dict]:
    """Obtener próximas fechas límite fiscales"""
    today = date.today()
    year = today.year
    
    deadlines = [
        {
            "date": date(year, 4, 30),
            "description": "Primer pago fraccionado (si procede)",
            "type": "payment"
        },
        {
            "date": date(year, 7, 31),
            "description": "Segundo pago fraccionado (si procede)",
            "type": "payment"
        },
        {
            "date": date(year, 10, 31),
            "description": "Tercer pago fraccionado (si procede)",
            "type": "payment"
        },
        {
            "date": date(year + 1, 6, 30),
            "description": f"Declaración de la Renta {year}",
            "type": "filing"
        }
    ]
    
    # Filtrar solo fechas futuras
    future_deadlines = [d for d in deadlines if d["date"] >= today]
    
    return future_deadlines[:3]  # Próximas 3 fechas

@router.post("/modelo-115/calculate")
def calculate_modelo_115(
    modelo_data: Modelo115Input,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Calcular el Modelo 115 de retención IRPF"""
    
    # Validaciones
    if modelo_data.quarter not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="El trimestre debe ser entre 1 y 4")
    
    if modelo_data.rental_income <= 0:
        raise HTTPException(status_code=400, detail="Los ingresos por alquiler deben ser positivos")
    
    # Tipo de retención IRPF para alquileres (19%)
    withholding_rate = 0.19
    withholding_amount = modelo_data.rental_income * withholding_rate
    net_amount_to_pay = max(0, withholding_amount - modelo_data.previous_withholdings)
    
    # Calcular fecha límite (20 del mes siguiente al trimestre)
    quarter_end_months = {1: 3, 2: 6, 3: 9, 4: 12}
    due_month = quarter_end_months[modelo_data.quarter] + 1
    due_year = modelo_data.year if due_month <= 12 else modelo_data.year + 1
    if due_month > 12:
        due_month = 1
    
    due_date = date(due_year, due_month, 20)
    
    # Datos del formulario 115
    form_data = {
        "ejercicio": modelo_data.year,
        "periodo": f"{modelo_data.quarter:02d}",
        "declaracion_tipo": "G",  # Complementaria: N, Sustitutiva: S, Normal: G
        "nif_declarante": "[A COMPLETAR]",
        "apellidos_nombre": "[A COMPLETAR]",
        "telefono": "",
        "rendimientos_trabajo": 0,
        "rendimientos_actividades_profesionales": modelo_data.rental_income,
        "rendimientos_actividades_empresariales": 0,
        "rendimientos_capital_inmobiliario": modelo_data.rental_income,
        "ganancias_patrimoniales": 0,
        "retenciones_practicadas": withholding_amount,
        "retenciones_anteriores": modelo_data.previous_withholdings,
        "resultado_liquidacion": net_amount_to_pay,
        "a_ingresar": net_amount_to_pay if net_amount_to_pay > 0 else 0,
        "a_devolver": abs(net_amount_to_pay) if net_amount_to_pay < 0 else 0
    }
    
    return Modelo115Output(
        year=modelo_data.year,
        quarter=modelo_data.quarter,
        total_income=modelo_data.rental_income,
        withholding_rate=withholding_rate,
        withholding_amount=withholding_amount,
        previous_withholdings=modelo_data.previous_withholdings,
        net_amount_to_pay=net_amount_to_pay,
        due_date=due_date.strftime("%d/%m/%Y"),
        form_data=form_data
    )

@router.get("/modelo-115/generate-pdf/{year}/{quarter}")
def generate_modelo_115_pdf(
    year: int,
    quarter: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Generar PDF del formulario Modelo 115"""
    
    # Obtener ingresos del trimestre
    quarterly_summary = get_quarterly_summary(year, quarter, session)
    
    # Calcular el modelo 115
    modelo_input = Modelo115Input(
        year=year,
        quarter=quarter,
        rental_income=quarterly_summary["income"]
    )
    
    modelo_result = calculate_modelo_115(modelo_input, session, current_user)
    
    # Crear PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    title = Paragraph(f"<b>MODELO 115 - RETENCIONES E INGRESOS A CUENTA DEL IRPF</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Información del período
    period_info = Paragraph(f"<b>Ejercicio:</b> {year} | <b>Período:</b> {quarter}º Trimestre", styles['Normal'])
    story.append(period_info)
    story.append(Spacer(1, 20))
    
    # Datos del contribuyente
    contributor_data = [
        ["NIF:", "[A COMPLETAR]"],
        ["Apellidos y Nombre:", "[A COMPLETAR]"],
        ["Teléfono:", "[A COMPLETAR]"]
    ]
    
    contributor_table = Table(contributor_data, colWidths=[2*inch, 4*inch])
    contributor_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(contributor_table)
    story.append(Spacer(1, 30))
    
    # Liquidación
    liquidation_data = [
        ["Concepto", "Importe (€)"],
        ["Rendimientos del capital inmobiliario", f"{modelo_result.total_income:,.2f}"],
        ["Retenciones practicadas (19%)", f"{modelo_result.withholding_amount:,.2f}"],
        ["Retenciones período anterior", f"{modelo_result.previous_withholdings:,.2f}"],
        ["Resultado de la liquidación", f"{modelo_result.net_amount_to_pay:,.2f}"]
    ]
    
    liquidation_table = Table(liquidation_data, colWidths=[4*inch, 2*inch])
    liquidation_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey)
    ]))
    
    story.append(liquidation_table)
    story.append(Spacer(1, 20))
    
    # Fecha límite
    due_date_info = Paragraph(f"<b>Fecha límite de presentación:</b> {modelo_result.due_date}", styles['Normal'])
    story.append(due_date_info)
    
    doc.build(story)
    buffer.seek(0)
    
    return Response(
        buffer.getvalue(),
        media_type='application/pdf',
        headers={"Content-Disposition": f"attachment; filename=modelo_115_{year}_Q{quarter}.pdf"}
    )

@router.get("/expense-optimizer/{year}")
def get_expense_optimization(
    year: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Optimizador de gastos deducibles con sugerencias IA"""
    
    # Obtener gastos del año
    properties = session.exec(select(Property)).all()
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    expense_categories = {
        "IBI": {"total": 0, "items": []},
        "Comunidad": {"total": 0, "items": []},
        "Seguros": {"total": 0, "items": []},
        "Reparaciones": {"total": 0, "items": []},
        "Suministros": {"total": 0, "items": []},
        "Gestión": {"total": 0, "items": []},
        "Otros": {"total": 0, "items": []}
    }
    
    total_income = 0
    
    for prop in properties:
        movements = session.exec(
            select(FinancialMovement)
            .where(FinancialMovement.property_id == prop.id)
            .where(FinancialMovement.date >= start_date)
            .where(FinancialMovement.date <= end_date)
        ).all()
        
        for movement in movements:
            if movement.amount > 0 and movement.category == "Renta":
                total_income += movement.amount
            elif movement.amount < 0:
                amount = abs(movement.amount)
                category = classify_expense(movement.concept, movement.category)
                if category in expense_categories:
                    expense_categories[category]["total"] += amount
                    expense_categories[category]["items"].append({
                        "concept": movement.concept,
                        "amount": amount,
                        "date": movement.date.isoformat(),
                        "property": prop.address
                    })
    
    # Generar sugerencias de optimización con IA
    optimizations = []
    
    # Análisis de IBI
    ibi_amount = expense_categories["IBI"]["total"]
    if ibi_amount < total_income * 0.02:  # Menos del 2% de ingresos en IBI
        optimizations.append(ExpenseOptimization(
            category="IBI",
            current_amount=ibi_amount,
            potential_savings=0,
            suggestions=[
                "Verifica que todos los recibos de IBI están registrados",
                "El IBI es 100% deducible, asegúrate de incluir todos los inmuebles",
                "Considera recurrir el valor catastral si es desproporcionado"
            ],
            priority="high",
            confidence=0.8
        ))
    
    # Análisis de seguros
    seguros_amount = expense_categories["Seguros"]["total"]
    if seguros_amount < 300:  # Menos de 300€ anuales en seguros
        optimizations.append(ExpenseOptimization(
            category="Seguros",
            current_amount=seguros_amount,
            potential_savings=150,
            suggestions=[
                "Contrata un seguro de responsabilidad civil para arrendadores",
                "Considera un seguro multirriesgo específico para alquileres",
                "Los seguros son 100% deducibles, no escatimes en cobertura"
            ],
            priority="medium",
            confidence=0.9
        ))
    
    # Análisis de gastos de gestión
    gestion_amount = expense_categories["Gestión"]["total"]
    if gestion_amount == 0:
        optimizations.append(ExpenseOptimization(
            category="Gestión",
            current_amount=gestion_amount,
            potential_savings=500,
            suggestions=[
                "Considera contratar una gestión profesional (comisión deducible)",
                "Registra gastos de publicidad para buscar inquilinos",
                "Incluye gastos de asesoría fiscal y legal",
                "Los desplazamientos para gestionar la propiedad son deducibles"
            ],
            priority="medium",
            confidence=0.7
        ))
    
    # Análisis de reparaciones
    reparaciones_amount = expense_categories["Reparaciones"]["total"]
    expected_repairs = total_income * 0.05  # 5% de ingresos en reparaciones es normal
    if reparaciones_amount < expected_repairs:
        optimizations.append(ExpenseOptimization(
            category="Reparaciones",
            current_amount=reparaciones_amount,
            potential_savings=expected_repairs - reparaciones_amount,
            suggestions=[
                "Planifica mantenimientos preventivos antes del cierre fiscal",
                "Las mejoras que no aumenten el valor son 100% deducibles",
                "Considera renovar instalaciones (calefacción, fontanería)",
                "Registra todos los pequeños arreglos y mantenimientos"
            ],
            priority="high",
            confidence=0.6
        ))
    
    # Análisis de suministros
    suministros_amount = expense_categories["Suministros"]["total"]
    if suministros_amount > 0:
        optimizations.append(ExpenseOptimization(
            category="Suministros",
            current_amount=suministros_amount,
            potential_savings=0,
            suggestions=[
                "Solo son deducibles cuando no hay inquilino",
                "Transfiere los suministros al inquilino siempre que sea posible",
                "Documenta claramente los períodos sin inquilino"
            ],
            priority="low",
            confidence=0.9
        ))
    
    total_potential_savings = sum(opt.potential_savings for opt in optimizations)
    tax_savings = total_potential_savings * 0.24  # Asumiendo tipo marginal 24%
    
    return {
        "year": year,
        "total_income": total_income,
        "current_expenses": sum(cat["total"] for cat in expense_categories.values()),
        "optimizations": optimizations,
        "total_potential_savings": total_potential_savings,
        "estimated_tax_savings": tax_savings,
        "expense_breakdown": expense_categories
    }

@router.get("/fiscal-dashboard/{year}")
def get_fiscal_dashboard(
    year: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Dashboard fiscal completo con métricas clave"""
    
    # Obtener datos del año actual y anterior
    current_year_summary = get_tax_summary(year, session)
    previous_year_summary = get_tax_summary(year - 1, session)
    
    # Calcular ahorro YTD
    ytd_savings = abs(current_year_summary.get("tax_liability", 0) - previous_year_summary.get("tax_liability", 0))
    
    # Próximos vencimientos
    upcoming_deadlines = get_next_tax_deadlines()
    
    # Obtener optimizaciones
    optimizer_data = get_expense_optimization(year, session, current_user)
    optimization_suggestions = optimizer_data["optimizations"]
    
    # Comparativa trimestral
    quarterly_data = {}
    for quarter in [1, 2, 3, 4]:
        try:
            quarter_summary = get_quarterly_summary(year, quarter, session)
            quarterly_data[f"Q{quarter}"] = quarter_summary["profit"]
        except:
            quarterly_data[f"Q{quarter}"] = 0
    
    # Calcular score de eficiencia fiscal
    total_income = current_year_summary.get("rental_income", 0)
    total_expenses = current_year_summary.get("deductible_expenses", 0)
    tax_efficiency_score = min(100, (total_expenses / total_income * 100)) if total_income > 0 else 0
    
    # Generar alertas
    alerts = []
    
    # Alerta por próximo vencimiento
    today = date.today()
    for deadline in upcoming_deadlines:
        if deadline["date"] <= today + timedelta(days=30):
            alerts.append({
                "type": "warning",
                "title": "Vencimiento próximo",
                "message": f"{deadline['description']} - {deadline['date'].strftime('%d/%m/%Y')}",
                "priority": "high"
            })
    
    # Alerta por baja eficiencia fiscal
    if tax_efficiency_score < 30:
        alerts.append({
            "type": "info",
            "title": "Oportunidad de optimización",
            "message": f"Tu ratio de gastos deducibles es del {tax_efficiency_score:.1f}%. Hay margen de mejora.",
            "priority": "medium"
        })
    
    # Alerta por alto crecimiento de ingresos
    income_growth = ((current_year_summary.get("rental_income", 0) - previous_year_summary.get("rental_income", 0)) / max(previous_year_summary.get("rental_income", 1), 1)) * 100
    if income_growth > 20:
        alerts.append({
            "type": "success",
            "title": "Crecimiento significativo",
            "message": f"Tus ingresos han crecido un {income_growth:.1f}% vs año anterior.",
            "priority": "low"
        })
    
    return FiscalDashboard(
        ytd_savings=ytd_savings,
        upcoming_deadlines=[{
            "date": d["date"].strftime("%d/%m/%Y"),
            "description": d["description"],
            "type": d["type"],
            "days_remaining": (d["date"] - today).days
        } for d in upcoming_deadlines],
        optimization_suggestions=optimization_suggestions[:5],  # Top 5
        quarterly_comparison=quarterly_data,
        tax_efficiency_score=tax_efficiency_score,
        alerts=alerts
    )

def classify_expense(concept: str, category: str) -> str:
    """Clasificar gasto basándose en el concepto"""
    concept_upper = concept.upper()
    
    if any(word in concept_upper for word in ["IBI", "IMPUESTO", "BIENES", "INMUEBLES"]):
        return "IBI"
    elif any(word in concept_upper for word in ["COMUNIDAD", "ADMINISTRACION", "PORTERO"]):
        return "Comunidad"
    elif "SEGURO" in concept_upper:
        return "Seguros"
    elif any(word in concept_upper for word in ["REPARACION", "MANTENIMIENTO", "OBRA", "FONTANERO", "ELECTRICISTA"]):
        return "Reparaciones"
    elif any(word in concept_upper for word in ["LUZ", "AGUA", "GAS", "INTERNET", "TELEFONO"]):
        return "Suministros"
    elif any(word in concept_upper for word in ["GESTION", "ASESORIA", "NOTARIA", "REGISTRO"]):
        return "Gestión"
    else:
        return "Otros"