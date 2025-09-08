# app/routers/notifications.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional
from datetime import date, datetime, timedelta
from sqlmodel import Session, select
from pydantic import BaseModel
from ..db import get_session
from ..deps import get_current_user
from ..models import (
    User, Property, RentalContract, FinancialMovement, MortgageDetails, EuriborRate
)
from ..notification_models import (
    SmartNotification, NotificationRule, NotificationChannel, NotificationTemplate,
    NotificationDigest, NotificationAnalytics
)
# Temporarily comment out imports to fix startup
# from ..services.smart_notifications import SmartNotificationEngine
# from ..services.email_digest_service import EmailDigestService
# from ..services.notification_integration import NotificationRuleIntegration
import statistics
import json

router = APIRouter(prefix="/notifications", tags=["notifications"])

# Pydantic models for API
class NotificationRuleCreate(BaseModel):
    rule_type: str
    threshold_value: Optional[float] = None
    days_ahead: Optional[int] = None
    priority: str = "medium"
    max_daily_notifications: int = 2
    business_hours_only: bool = True
    min_hours_between: int = 4

class NotificationChannelCreate(BaseModel):
    channel_type: str  # "in_app", "email", "push", "whatsapp"
    is_enabled: bool = True
    settings: Optional[Dict] = None

class SmartNotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str
    priority: str
    priority_score: int
    property_id: Optional[int] = None
    contextual_data: Optional[Dict] = None
    action_url: Optional[str] = None
    created_at: date
    status: str
    
class NotificationSettingsResponse(BaseModel):
    channels: List[Dict]
    rules: List[Dict]
    daily_limit: int
    business_hours_only: bool

class NotificationStatsResponse(BaseModel):
    today: Dict[str, int]
    week: Dict[str, int]
    month: Dict[str, int]
    engagement_rate: float

# Temporarily commented out to fix startup issues
# @router.get("/smart", response_model=List[SmartNotificationResponse])
# def get_smart_notifications(
#     generate_new: bool = True,
#     session: Session = Depends(get_session),
#     current_user: User = Depends(get_current_user)
# ):
#     """Get intelligent contextual notifications"""
#     return []

@router.get("/alerts")
def get_active_notifications(
    session: Session = Depends(get_session)
):
    """Legacy endpoint - redirect to smart notifications"""
    
    # For demo purposes, return contextual notifications
    demo_notifications = [
        {
            "id": "smart_001",
            "type": "critical",
            "title": "Contrato Serrano 21 vence en 60 días + template renovación",
            "description": "María García - Contrato vence 15/11/2025. Template de renovación preparado.",
            "created_at": "2025-09-03T09:15:00",
            "property_id": 1,
            "amount": 1200.0,
            "due_date": "2025-11-15",
            "actions": ["Enviar template renovación", "Contactar inquilino", "Ver historial pagos"]
        },
        {
            "id": "smart_002", 
            "type": "success",
            "title": "Puedes ahorrar €230 optimizando gastos Q4",
            "description": "Oportunidades detectadas: seguros (€120), suministros (€110)",
            "created_at": "2025-09-03T08:30:00",
            "property_id": 2,
            "amount": 230.0,
            "actions": ["Ver análisis completo", "Comparar seguros", "Optimizar suministros"]
        },
        {
            "id": "smart_003",
            "type": "info",
            "title": "Modelo 115 listo para presentar (1-click)",
            "description": "Q3 2025 - Retención calculada: €456. Presentación automática disponible.",
            "created_at": "2025-09-03T07:45:00",
            "property_id": 1,
            "amount": 456.0,
            "due_date": "2025-10-20",
            "actions": ["Presentar automáticamente", "Revisar cálculos", "Descargar formulario"]
        },
        {
            "id": "smart_004",
            "type": "warning", 
            "title": "Lago Enol 12% por debajo mercado - ¿subir renta?",
            "description": "Renta actual: €850. Mercado: €950 (+€100/mes, €1.200/año)",
            "created_at": "2025-09-02T16:20:00",
            "property_id": 3,
            "amount": 1200.0,
            "actions": ["Ver análisis mercado", "Simular incremento", "Contactar inquilino"]
        }
    ]
    
    return {
        "notifications": demo_notifications,
        "total": len(demo_notifications),
        "by_type": {
            "critical": len([n for n in demo_notifications if n["type"] == "critical"]),
            "warning": len([n for n in demo_notifications if n["type"] == "warning"]),
            "info": len([n for n in demo_notifications if n["type"] == "info"]),
            "success": len([n for n in demo_notifications if n["type"] == "success"])
        },
        "smart_features": {
            "contextual": True,
            "timing_optimized": True,
            "priority_scored": True,
            "action_ready": True
        }
    }

@router.get("/stats")
def get_notification_stats(
    session: Session = Depends(get_session)
):
    """Estadísticas de notificaciones"""
    
    return {
        "total_alerts": 4,
        "critical_alerts": 1,
        "potential_savings": 120,
        "overdue_payments": 2
    }

@router.get("/original-alerts")
def get_original_notifications(
    session: Session = Depends(get_session)
):
    """Obtener propiedades del usuario (implementación original)"""
    notifications = []
    today = date.today()
    
    # Obtener propiedades del usuario
    properties = session.exec(select(Property)).all()
    
    for prop in properties:
        # 1. Contratos próximos a vencer
        contracts = session.exec(
            select(RentalContract)
            .where(RentalContract.property_id == prop.id)
            .where(RentalContract.is_active == True)
        ).all()
        
        for contract in contracts:
            if contract.end_date:
                days_until_expiry = (contract.end_date - today).days
                
                if 0 <= days_until_expiry <= 30:
                    notifications.append(Notification(
                        id=f"contract_expiry_{contract.id}",
                        type="contract_expiring",
                        title="Contrato próximo a vencer",
                        message=f"El contrato de {contract.tenant_name} en {prop.address} vence en {days_until_expiry} días",
                        priority="high" if days_until_expiry <= 7 else "medium",
                        property_id=prop.id,
                        due_date=contract.end_date,
                        action_url=f"/financial-agent/contracts",
                        created_at=datetime.now(),
                        read=False
                    ))
        
        # 2. Pagos de renta pendientes (detectar si no hay ingresos en los últimos 35 días)
        last_month = today - timedelta(days=35)
        recent_rent_payments = session.exec(
            select(FinancialMovement)
            .where(FinancialMovement.property_id == prop.id)
            .where(FinancialMovement.category == "Renta")
            .where(FinancialMovement.amount > 0)
            .where(FinancialMovement.date >= last_month)
        ).all()
        
        active_contract = session.exec(
            select(RentalContract)
            .where(RentalContract.property_id == prop.id)
            .where(RentalContract.is_active == True)
        ).first()
        
        if active_contract and not recent_rent_payments:
            notifications.append(Notification(
                id=f"missing_rent_{prop.id}",
                type="payment_due",
                title="Posible pago de renta pendiente",
                message=f"No se ha registrado pago de renta en {prop.address} en los últimos 35 días",
                priority="high",
                property_id=prop.id,
                amount=active_contract.monthly_rent,
                action_url=f"/financial-agent/property/{prop.id}",
                created_at=datetime.now(),
                read=False
            ))
        
        # 3. Gastos inusuales (gastos 3x superiores al promedio mensual)
        six_months_ago = today - timedelta(days=180)
        expenses = session.exec(
            select(FinancialMovement)
            .where(FinancialMovement.property_id == prop.id)
            .where(FinancialMovement.amount < 0)
            .where(FinancialMovement.date >= six_months_ago)
        ).all()
        
        if expenses:
            monthly_expenses = {}
            for expense in expenses:
                month_key = f"{expense.date.year}-{expense.date.month:02d}"
                if month_key not in monthly_expenses:
                    monthly_expenses[month_key] = 0
                monthly_expenses[month_key] += abs(expense.amount)
            
            if len(monthly_expenses) >= 3:
                avg_monthly_expense = statistics.mean(monthly_expenses.values())
                current_month = f"{today.year}-{today.month:02d}"
                current_month_expense = monthly_expenses.get(current_month, 0)
                
                if current_month_expense > avg_monthly_expense * 2.5:
                    notifications.append(Notification(
                        id=f"unusual_expense_{prop.id}",
                        type="unusual_expense",
                        title="Gastos inusuales detectados",
                        message=f"Los gastos de {prop.address} este mes (€{current_month_expense:.0f}) superan significativamente el promedio (€{avg_monthly_expense:.0f})",
                        priority="medium",
                        property_id=prop.id,
                        amount=current_month_expense - avg_monthly_expense,
                        action_url=f"/financial-agent/property/{prop.id}",
                        created_at=datetime.now(),
                        read=False
                    ))
        
        # 4. Oportunidades de ahorro en hipoteca
        mortgage = session.exec(
            select(MortgageDetails).where(MortgageDetails.property_id == prop.id)
        ).first()
        
        if mortgage:
            # Obtener tasa Euribor actual
            latest_euribor = session.exec(
                select(EuriborRate).order_by(EuriborRate.date.desc())
            ).first()
            
            if latest_euribor:
                current_rate = latest_euribor.rate_12m + mortgage.margin_percentage
                
                # Si la tasa actual es significativamente menor que hace 12 meses
                year_ago_euribor = session.exec(
                    select(EuriborRate)
                    .where(EuriborRate.date <= today - timedelta(days=365))
                    .order_by(EuriborRate.date.desc())
                ).first()
                
                if year_ago_euribor:
                    old_rate = year_ago_euribor.rate_12m + mortgage.margin_percentage
                    rate_diff = old_rate - current_rate
                    
                    if rate_diff > 0.5:  # Si la diferencia es mayor a 0.5%
                        monthly_savings = mortgage.outstanding_balance * (rate_diff / 100) / 12
                        notifications.append(Notification(
                            id=f"refinance_opportunity_{prop.id}",
                            type="savings_opportunity",
                            title="Oportunidad de refinanciación",
                            message=f"Los tipos han bajado {rate_diff:.2f}%. Podrías ahorrar €{monthly_savings:.0f}/mes refinanciando la hipoteca de {prop.address}",
                            priority="low",
                            property_id=prop.id,
                            amount=monthly_savings * 12,
                            action_url=f"/financial-agent/mortgage-calculator",
                            created_at=datetime.now(),
                            read=False
                        ))
        
        # 5. Revisiones de hipoteca próximas
        if mortgage:
            # Calcular próxima revisión (cada 12 meses desde start_date)
            months_since_start = (today.year - mortgage.start_date.year) * 12 + (today.month - mortgage.start_date.month)
            months_to_next_review = mortgage.review_period_months - (months_since_start % mortgage.review_period_months)
            
            if months_to_next_review <= 2:
                next_review_date = today + timedelta(days=months_to_next_review * 30)
                notifications.append(Notification(
                    id=f"mortgage_review_{prop.id}",
                    type="mortgage_review",
                    title="Revisión de hipoteca próxima",
                    message=f"La hipoteca de {prop.address} se revisará aproximadamente el {next_review_date.strftime('%d/%m/%Y')}",
                    priority="medium",
                    property_id=prop.id,
                    due_date=next_review_date,
                    action_url=f"/financial-agent/property/{prop.id}/mortgage",
                    created_at=datetime.now(),
                    read=False
                ))
    
    # Ordenar por prioridad y fecha
    priority_order = {"high": 3, "medium": 2, "low": 1}
    notifications.sort(key=lambda x: (priority_order.get(x.priority, 0), x.created_at), reverse=True)
    
    return {
        "notifications": notifications,
        "summary": {
            "total": len(notifications),
            "high_priority": len([n for n in notifications if n.priority == "high"]),
            "medium_priority": len([n for n in notifications if n.priority == "medium"]),
            "low_priority": len([n for n in notifications if n.priority == "low"])
        }
    }

@router.get("/savings-opportunities")
def get_savings_opportunities(
    session: Session = Depends(get_session)
):
    """Análisis de oportunidades de ahorro"""
    opportunities = []
    
    # Obtener propiedades del usuario
    properties = session.exec(
        select(Property)
    ).all()
    
    for prop in properties:
        # 1. Análisis de gastos recurrentes
        last_year = date.today() - timedelta(days=365)
        expenses = session.exec(
            select(FinancialMovement)
            .where(FinancialMovement.property_id == prop.id)
            .where(FinancialMovement.amount < 0)
            .where(FinancialMovement.date >= last_year)
        ).all()
        
        # Agrupar gastos por categoría
        category_totals = {}
        for expense in expenses:
            category = expense.subcategory or expense.category
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += abs(expense.amount)
        
        # Identificar categorías con mayor gasto
        if category_totals:
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            top_category, top_amount = sorted_categories[0]
            
            if top_amount > 1000:  # Si el gasto anual supera €1000
                opportunities.append({
                    "type": "expense_optimization",
                    "property_id": prop.id,
                    "property_address": prop.address,
                    "title": f"Optimizar gastos de {top_category}",
                    "description": f"Has gastado €{top_amount:.0f} en {top_category} este año. Considera buscar alternativas más económicas.",
                    "potential_savings": top_amount * 0.15,  # Estimación 15% de ahorro
                    "priority": "medium"
                })
        
        # 2. Análisis de rentabilidad
        total_expenses = sum(abs(e.amount) for e in expenses)
        total_income = sum(e.amount for e in session.exec(
            select(FinancialMovement)
            .where(FinancialMovement.property_id == prop.id)
            .where(FinancialMovement.amount > 0)
            .where(FinancialMovement.date >= last_year)
        ).all())
        
        if total_income > 0:
            profit_margin = (total_income - total_expenses) / total_income
            if profit_margin < 0.3:  # Si el margen es menor al 30%
                opportunities.append({
                    "type": "rent_increase",
                    "property_id": prop.id,
                    "property_address": prop.address,
                    "title": "Considerar ajuste de renta",
                    "description": f"El margen de beneficio ({profit_margin*100:.1f}%) está por debajo del objetivo (30%). Evalúa incremento de renta.",
                    "potential_savings": total_income * 0.1,  # Estimación 10% incremento
                    "priority": "low"
                })
    
    return {
        "opportunities": opportunities,
        "total_potential_savings": sum(opp["potential_savings"] for opp in opportunities)
    }

@router.post("/mark-read/{notification_id}")
def mark_notification_read(
    notification_id: str,
    session: Session = Depends(get_session)
):
    """Marcar notificación como leída (en una implementación real se guardaría en BD)"""
    return {"message": "Notification marked as read", "notification_id": notification_id}

@router.get("/settings")
def get_notification_settings(
    session: Session = Depends(get_session)
):
    """Obtener configuración de notificaciones del usuario"""
    # En una implementación real, esto se obtendría de la base de datos
    default_settings = {
        "payment_due": NotificationRule(type="payment_due", enabled=True, email_enabled=False),
        "unusual_expense": NotificationRule(type="unusual_expense", threshold=1000.0, enabled=True, email_enabled=False),
        "contract_expiring": NotificationRule(type="contract_expiring", enabled=True, email_enabled=False),
        "savings_opportunity": NotificationRule(type="savings_opportunity", enabled=True, email_enabled=False),
        "mortgage_review": NotificationRule(type="mortgage_review", enabled=True, email_enabled=False)
    }
    
    return {
        "user_id": 1,
        "email": "demo@example.com",
        "rules": default_settings
    }

@router.post("/settings")
def update_notification_settings(
    settings: Dict[str, NotificationRule],
    session: Session = Depends(get_session)
):
    """Actualizar configuración de notificaciones"""
    # En una implementación real, esto se guardaría en la base de datos
    return {
        "message": "Notification settings updated successfully",
        "settings": settings
    }

# New Smart Notification Endpoints

@router.post("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    session: Session = Depends(get_session)
):
    """Mark notification as read - temporarily simplified"""
    return {"message": "Notification marked as read (demo mode)"}

@router.post("/{notification_id}/dismiss")
def dismiss_notification(
    notification_id: int,
    session: Session = Depends(get_session)
):
    """Dismiss notification - temporarily simplified"""
    return {"message": "Notification dismissed (demo mode)"}

@router.post("/{notification_id}/action")
def notification_action(
    notification_id: int,
    session: Session = Depends(get_session)
):
    """Track that user took action on notification - temporarily simplified"""
    return {
        "message": "Action tracked (demo mode)",
        "action_url": "/financial-agent"
    }

@router.get("/channels", response_model=List[Dict])
def get_notification_channels(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get user's notification channels configuration"""
    channels = session.exec(
        select(NotificationChannel).where(NotificationChannel.user_id == current_user.id)
    ).all()
    
    if not channels:
        # Create default channels
        default_channels = [
            {"channel_type": "in_app", "is_enabled": True},
            {"channel_type": "email", "is_enabled": False},
            {"channel_type": "push", "is_enabled": False},
            {"channel_type": "whatsapp", "is_enabled": False}
        ]
        
        for channel_data in default_channels:
            channel = NotificationChannel(
                user_id=current_user.id,
                **channel_data
            )
            session.add(channel)
        
        session.commit()
        channels = session.exec(
            select(NotificationChannel).where(NotificationChannel.user_id == current_user.id)
        ).all()
    
    return [
        {
            "id": channel.id,
            "type": channel.channel_type,
            "enabled": channel.is_enabled,
            "settings": json.loads(channel.settings) if channel.settings else {}
        }
        for channel in channels
    ]

@router.put("/channels/{channel_id}")
def update_notification_channel(
    channel_id: int,
    channel_data: NotificationChannelCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update notification channel settings"""
    channel = session.get(NotificationChannel, channel_id)
    if not channel or channel.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    channel.is_enabled = channel_data.is_enabled
    if channel_data.settings:
        channel.settings = json.dumps(channel_data.settings)
    
    session.commit()
    
    return {"message": "Channel updated successfully"}

@router.get("/rules", response_model=List[Dict])
def get_notification_rules(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get user's notification rules"""
    rules = session.exec(
        select(NotificationRule).where(NotificationRule.user_id == current_user.id)
    ).all()
    
    if not rules:
        # Create default rule
        default_rule = NotificationRule(
            user_id=current_user.id,
            rule_type="default",
            is_enabled=True,
            max_daily_notifications=2,
            business_hours_only=True,
            min_hours_between=4
        )
        session.add(default_rule)
        session.commit()
        rules = [default_rule]
    
    return [
        {
            "id": rule.id,
            "type": rule.rule_type,
            "enabled": rule.is_enabled,
            "threshold": rule.threshold_value,
            "days_ahead": rule.days_ahead,
            "priority": rule.priority,
            "daily_limit": rule.max_daily_notifications,
            "business_hours_only": rule.business_hours_only,
            "min_hours_between": rule.min_hours_between
        }
        for rule in rules
    ]

@router.post("/rules")
def create_notification_rule(
    rule_data: NotificationRuleCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create new notification rule"""
    rule = NotificationRule(
        user_id=current_user.id,
        **rule_data.dict()
    )
    
    session.add(rule)
    session.commit()
    session.refresh(rule)
    
    return {"message": "Rule created successfully", "rule_id": rule.id}

@router.get("/digest/weekly")
def get_weekly_digest(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Generate weekly notification digest"""
    week_ago = date.today() - timedelta(days=7)
    
    # Get notifications from last week
    notifications = session.exec(
        select(SmartNotification)
        .where(SmartNotification.user_id == current_user.id)
        .where(SmartNotification.created_at >= week_ago)
        .order_by(SmartNotification.priority_score.desc())
    ).all()
    
    # Group by type
    grouped = {}
    for notif in notifications:
        if notif.notification_type not in grouped:
            grouped[notif.notification_type] = []
        grouped[notif.notification_type].append({
            "title": notif.title,
            "message": notif.message,
            "priority_score": notif.priority_score,
            "property_id": notif.property_id,
            "action_url": notif.action_url
        })
    
    # Calculate summary stats
    total_notifications = len(notifications)
    high_priority = len([n for n in notifications if n.priority_score >= 75])
    properties_affected = len(set(n.property_id for n in notifications if n.property_id))
    
    return {
        "period": "weekly",
        "date_range": {
            "from": week_ago.isoformat(),
            "to": date.today().isoformat()
        },
        "summary": {
            "total_notifications": total_notifications,
            "high_priority": high_priority,
            "properties_affected": properties_affected
        },
        "notifications_by_type": grouped,
        "recommendations": _generate_weekly_recommendations(notifications)
    }

@router.get("/analytics", response_model=NotificationStatsResponse)
def get_notification_analytics(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get notification analytics and engagement stats"""
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Get analytics records
    today_analytics = session.exec(
        select(NotificationAnalytics)
        .where(NotificationAnalytics.user_id == current_user.id)
        .where(NotificationAnalytics.date == today)
    ).first()
    
    week_analytics = session.exec(
        select(NotificationAnalytics)
        .where(NotificationAnalytics.user_id == current_user.id)
        .where(NotificationAnalytics.date >= week_ago)
    ).all()
    
    month_analytics = session.exec(
        select(NotificationAnalytics)
        .where(NotificationAnalytics.user_id == current_user.id)
        .where(NotificationAnalytics.date >= month_ago)
    ).all()
    
    # Calculate engagement rate
    total_sent = sum(a.notifications_sent for a in month_analytics)
    total_read = sum(a.notifications_read for a in month_analytics)
    engagement_rate = (total_read / total_sent * 100) if total_sent > 0 else 0
    
    return NotificationStatsResponse(
        today={
            "sent": today_analytics.notifications_sent if today_analytics else 0,
            "read": today_analytics.notifications_read if today_analytics else 0,
            "dismissed": today_analytics.notifications_dismissed if today_analytics else 0,
            "acted": today_analytics.notifications_acted if today_analytics else 0
        },
        week={
            "sent": sum(a.notifications_sent for a in week_analytics),
            "read": sum(a.notifications_read for a in week_analytics),
            "dismissed": sum(a.notifications_dismissed for a in week_analytics),
            "acted": sum(a.notifications_acted for a in week_analytics)
        },
        month={
            "sent": total_sent,
            "read": total_read,
            "dismissed": sum(a.notifications_dismissed for a in month_analytics),
            "acted": sum(a.notifications_acted for a in month_analytics)
        },
        engagement_rate=engagement_rate
    )

# Helper functions
def _get_priority_level(priority_score: int) -> str:
    """Convert priority score to level"""
    if priority_score >= 90:
        return "critical"
    elif priority_score >= 75:
        return "high"
    elif priority_score >= 60:
        return "medium"
    else:
        return "low"

def _update_analytics(session: Session, user_id: int, action: str):
    """Update daily analytics"""
    today = date.today()
    
    # Get or create today's analytics
    analytics = session.exec(
        select(NotificationAnalytics)
        .where(NotificationAnalytics.user_id == user_id)
        .where(NotificationAnalytics.date == today)
    ).first()
    
    if not analytics:
        analytics = NotificationAnalytics(user_id=user_id, date=today)
        session.add(analytics)
    
    # Update counter
    if action == "read":
        analytics.notifications_read += 1
    elif action == "dismissed":
        analytics.notifications_dismissed += 1
    elif action == "acted":
        analytics.notifications_acted += 1
    
    session.commit()

def _generate_weekly_recommendations(notifications: List[SmartNotification]) -> List[str]:
    """Generate personalized recommendations based on notification patterns"""
    recommendations = []
    
    # Analyze notification types
    type_counts = {}
    for notif in notifications:
        type_counts[notif.notification_type] = type_counts.get(notif.notification_type, 0) + 1
    
    # Generate recommendations
    if type_counts.get("contract_expiring_60d", 0) > 0:
        recommendations.append("Revisa los contratos próximos a vencer y prepara las renovaciones con antelación")
    
    if type_counts.get("payment_missing", 0) > 1:
        recommendations.append("Considera implementar pagos automáticos con tus inquilinos para evitar retrasos")
    
    if type_counts.get("expense_optimization", 0) > 2:
        recommendations.append("Dedica tiempo a revisar y optimizar los gastos recurrentes de tus propiedades")
    
    if type_counts.get("rent_below_market", 0) > 0:
        recommendations.append("Evalúa incrementos de renta basados en análisis de mercado para maximizar rentabilidad")
    
    return recommendations

# Temporarily commented out endpoints that use services to fix startup
@router.post("/digest/weekly/send")
def send_weekly_digest_to_user(
    session: Session = Depends(get_session)
):
    """Generate and send weekly digest to current user - temporarily disabled"""
    return {
        "message": "Service temporarily disabled - will be enabled after startup fixes",
        "digest_generated": False
    }

@router.post("/digest/weekly/batch")
def send_weekly_digests_batch(
    session: Session = Depends(get_session)
):
    """Send weekly digests to all eligible users - temporarily disabled"""
    return {
        "message": "Service temporarily disabled",
        "results": {"total_users": 0, "digests_sent": 0}
    }

@router.post("/integration/trigger")
def trigger_notifications_for_user(
    session: Session = Depends(get_session)
):
    """Trigger comprehensive notification generation - temporarily disabled"""
    return {
        "message": "Service temporarily disabled",
        "results": {"notifications": [], "total_generated": 0}
    }