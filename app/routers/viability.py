from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from datetime import datetime
from pydantic import BaseModel

from ..models import ViabilityStudy, ViabilityProjection, User
from ..deps import get_session, get_current_user
from ..services.viability_calculator import (
    calculate_viability_metrics,
    generate_temporal_projection,
    perform_sensitivity_analysis,
    compare_studies
)

router = APIRouter(prefix="/viability", tags=["Estudios de Viabilidad"])

class ViabilityStudyCreate(BaseModel):
    study_name: str
    
    # DATOS DE COMPRA
    purchase_price: float
    property_valuation: Optional[float] = None
    purchase_taxes_percentage: float = 0.11
    renovation_costs: Optional[float] = 0
    real_estate_commission: Optional[float] = 0
    
    # FINANCIACIÓN
    loan_amount: float
    interest_rate: float
    loan_term_years: int = 25
    
    # INGRESOS
    monthly_rent: float
    annual_rent_increase: float = 0.02
    
    # GASTOS FIJOS ANUALES
    community_fees: Optional[float] = 0
    property_tax_ibi: float
    life_insurance: Optional[float] = 0
    home_insurance: float
    maintenance_percentage: float = 0.01
    property_management_fee: Optional[float] = 0
    
    # RIESGO
    vacancy_risk_percentage: float = 0.05
    stress_test_rent_decrease: float = 0.10

@router.post("/", response_model=ViabilityStudy)
async def create_viability_study(
    study_data: ViabilityStudyCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Crear nuevo estudio de viabilidad con cálculos automáticos"""
    try:
        # Crear diccionario de datos desde el modelo Pydantic
        data_dict = study_data.dict()
        data_dict['user_id'] = current_user.id
        
        # Crear instancia del modelo SQLModel
        study = ViabilityStudy(**data_dict)
        
        # Calcular todas las métricas automáticamente
        study = calculate_viability_metrics(study)
        
        # Guardar en base de datos
        db.add(study)
        db.commit()
        db.refresh(study)
        
        # Generar y guardar proyección temporal (10 años por defecto)
        projection_data = generate_temporal_projection(study, years=10)
        for proj_dict in projection_data:
            projection = ViabilityProjection(**proj_dict)
            db.add(projection)
        
        db.commit()
        
        return study
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creando estudio: {str(e)}")

@router.get("/", response_model=List[ViabilityStudy])
async def get_user_viability_studies(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Listar estudios de viabilidad del usuario"""
    statement = select(ViabilityStudy).where(ViabilityStudy.user_id == current_user.id)
    studies = db.exec(statement).all()
    return studies

@router.get("/{study_id}", response_model=ViabilityStudy)
async def get_viability_study(
    study_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Obtener estudio específico con detalles completos"""
    statement = select(ViabilityStudy).where(
        ViabilityStudy.id == study_id,
        ViabilityStudy.user_id == current_user.id
    )
    study = db.exec(statement).first()
    
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    
    return study

@router.get("/{study_id}/projection", response_model=List[ViabilityProjection])
async def get_viability_projection(
    study_id: int,
    years: int = Query(default=10, ge=1, le=30),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Obtener proyección temporal del estudio (hasta 30 años)"""
    # Verificar que el estudio pertenece al usuario
    study_statement = select(ViabilityStudy).where(
        ViabilityStudy.id == study_id,
        ViabilityStudy.user_id == current_user.id
    )
    study = db.exec(study_statement).first()
    
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    
    # Obtener proyecciones existentes
    projection_statement = select(ViabilityProjection).where(
        ViabilityProjection.viability_study_id == study_id,
        ViabilityProjection.year <= years
    ).order_by(ViabilityProjection.year, ViabilityProjection.month)
    
    projections = db.exec(projection_statement).all()
    
    # Si no hay proyecciones o se solicitan más años, generar nuevas
    max_year_in_db = max([p.year for p in projections]) if projections else 0
    
    if max_year_in_db < years:
        # Eliminar proyecciones existentes para recalcular
        for projection in projections:
            db.delete(projection)
        
        # Generar nuevas proyecciones
        new_projections = generate_temporal_projection(study, years=years)
        for projection in new_projections:
            projection.viability_study_id = study_id
            db.add(projection)
        
        db.commit()
        
        # Obtener proyecciones recién creadas
        projections = db.exec(projection_statement).all()
    
    return projections

@router.put("/{study_id}", response_model=ViabilityStudy)
async def update_viability_study(
    study_id: int,
    updates: dict,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Actualizar estudio y recalcular métricas automáticamente"""
    # Obtener estudio existente
    statement = select(ViabilityStudy).where(
        ViabilityStudy.id == study_id,
        ViabilityStudy.user_id == current_user.id
    )
    study = db.exec(statement).first()
    
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    
    try:
        # Actualizar campos
        for key, value in updates.items():
            if hasattr(study, key) and key not in ['id', 'user_id', 'created_at']:
                setattr(study, key, value)
        
        # Recalcular métricas
        study = calculate_viability_metrics(study)
        study.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(study)
        
        # Eliminar y regenerar proyecciones
        projection_statement = select(ViabilityProjection).where(
            ViabilityProjection.viability_study_id == study_id
        )
        projections = db.exec(projection_statement).all()
        for projection in projections:
            db.delete(projection)
        
        # Generar nuevas proyecciones
        new_projections = generate_temporal_projection(study, years=10)
        for projection in new_projections:
            projection.viability_study_id = study_id
            db.add(projection)
        
        db.commit()
        
        return study
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error actualizando estudio: {str(e)}")

@router.delete("/{study_id}")
async def delete_viability_study(
    study_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Eliminar estudio de viabilidad"""
    statement = select(ViabilityStudy).where(
        ViabilityStudy.id == study_id,
        ViabilityStudy.user_id == current_user.id
    )
    study = db.exec(statement).first()
    
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    
    # Eliminar proyecciones relacionadas
    projection_statement = select(ViabilityProjection).where(
        ViabilityProjection.viability_study_id == study_id
    )
    projections = db.exec(projection_statement).all()
    for projection in projections:
        db.delete(projection)
    
    # Eliminar estudio
    db.delete(study)
    db.commit()
    
    return {"message": "Estudio eliminado correctamente"}

@router.post("/compare")
async def compare_viability_studies(
    study_ids: List[int],
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Comparar múltiples estudios de viabilidad"""
    if len(study_ids) < 2:
        raise HTTPException(status_code=400, detail="Se necesitan al menos 2 estudios para comparar")
    
    if len(study_ids) > 10:
        raise HTTPException(status_code=400, detail="Máximo 10 estudios para comparar")
    
    # Obtener estudios del usuario
    statement = select(ViabilityStudy).where(
        ViabilityStudy.id.in_(study_ids),
        ViabilityStudy.user_id == current_user.id
    )
    studies = db.exec(statement).all()
    
    if len(studies) != len(study_ids):
        raise HTTPException(status_code=404, detail="Algunos estudios no fueron encontrados")
    
    try:
        comparison = compare_studies(studies)
        return comparison
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error comparando estudios: {str(e)}")

@router.post("/{study_id}/sensitivity-analysis")
async def sensitivity_analysis(
    study_id: int,
    parameters: Optional[dict] = None,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Análisis de sensibilidad cambiando variables clave"""
    statement = select(ViabilityStudy).where(
        ViabilityStudy.id == study_id,
        ViabilityStudy.user_id == current_user.id
    )
    study = db.exec(statement).first()
    
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    
    try:
        sensitivity_results = perform_sensitivity_analysis(study, parameters or {})
        return sensitivity_results
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en análisis de sensibilidad: {str(e)}")

@router.get("/{study_id}/summary")
async def get_study_summary(
    study_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Obtener resumen ejecutivo del estudio"""
    statement = select(ViabilityStudy).where(
        ViabilityStudy.id == study_id,
        ViabilityStudy.user_id == current_user.id
    )
    study = db.exec(statement).first()
    
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    
    # Calcular métricas adicionales para el resumen
    months_to_positive = 0
    if study.monthly_net_cashflow > 0:
        months_to_positive = 0
    else:
        # Estimar cuántos meses hasta cashflow positivo (simplificado)
        monthly_deficit = abs(study.monthly_net_cashflow)
        if monthly_deficit > 0:
            months_to_positive = int(study.down_payment / monthly_deficit)
    
    payback_period_years = None
    if study.annual_net_cashflow > 0:
        payback_period_years = study.down_payment / study.annual_net_cashflow
    
    summary = {
        "study_name": study.study_name,
        "investment_summary": {
            "total_investment": study.total_purchase_price,
            "down_payment": study.down_payment,
            "loan_amount": study.loan_amount,
            "loan_to_value": study.loan_to_value
        },
        "return_metrics": {
            "net_annual_return": study.net_annual_return,
            "total_annual_return": study.total_annual_return,
            "monthly_cashflow": study.monthly_net_cashflow,
            "annual_cashflow": study.annual_net_cashflow,
            "payback_period_years": payback_period_years
        },
        "risk_assessment": {
            "risk_level": study.risk_level,
            "is_favorable": study.is_favorable,
            "break_even_rent": study.break_even_rent,
            "rent_buffer_percent": ((study.monthly_rent - study.break_even_rent) / study.monthly_rent * 100) if study.monthly_rent > 0 else 0,
            "months_to_positive_cashflow": months_to_positive
        },
        "key_assumptions": {
            "purchase_price": study.purchase_price,
            "monthly_rent": study.monthly_rent,
            "interest_rate": study.interest_rate,
            "loan_term": study.loan_term_years,
            "annual_rent_increase": study.annual_rent_increase
        }
    }
    
    return summary

@router.post("/{study_id}/recalculate")
async def recalculate_study(
    study_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Forzar recálculo completo del estudio"""
    statement = select(ViabilityStudy).where(
        ViabilityStudy.id == study_id,
        ViabilityStudy.user_id == current_user.id
    )
    study = db.exec(statement).first()
    
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    
    try:
        # Recalcular métricas
        study = calculate_viability_metrics(study)
        db.commit()
        db.refresh(study)
        
        return {"message": "Estudio recalculado correctamente", "study": study}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error recalculando estudio: {str(e)}")