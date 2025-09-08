# app/routers/payment_rules.py
# Updated 2025-09-09 - Force redeploy for production
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import date
from sqlmodel import Session, select
from pydantic import BaseModel
from ..db import get_session
from ..deps import get_current_user
from ..models import User, PaymentRule, Property, RentalContract

# Pydantic models for request/response
class PaymentRuleCreate(BaseModel):
    property_id: Optional[int] = None
    tenant_name: Optional[str] = None
    payment_start_day: int = 1
    payment_end_day: int = 5
    allow_previous_month_end: bool = False
    previous_month_end_days: int = 0
    overdue_grace_days: int = 15
    warning_days: int = 30
    critical_days: int = 60
    rule_name: str
    is_active: bool = True

class PaymentRuleUpdate(BaseModel):
    property_id: Optional[int] = None
    tenant_name: Optional[str] = None
    payment_start_day: Optional[int] = None
    payment_end_day: Optional[int] = None
    allow_previous_month_end: Optional[bool] = None
    previous_month_end_days: Optional[int] = None
    overdue_grace_days: Optional[int] = None
    warning_days: Optional[int] = None
    critical_days: Optional[int] = None
    rule_name: Optional[str] = None
    is_active: Optional[bool] = None

class PropertyTenantInfo(BaseModel):
    property_id: int
    property_address: str
    tenants: List[str]

router = APIRouter(prefix="/payment-rules", tags=["payment-rules"])

# Force reload test

@router.get("/", response_model=List[PaymentRule])
def get_payment_rules(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all payment rules for the current user"""
    rules = session.exec(
        select(PaymentRule).where(PaymentRule.user_id == current_user.id)
    ).all()
    return rules

@router.post("/", response_model=PaymentRule)
def create_payment_rule(
    rule_data: PaymentRuleCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new payment rule"""
    # Validate property ownership if property_id is provided
    if rule_data.property_id:
        property_obj = session.get(Property, rule_data.property_id)
        if not property_obj or property_obj.owner_id != current_user.id:
            raise HTTPException(status_code=404, detail="Property not found")
    
    # Create the rule
    rule = PaymentRule(
        user_id=current_user.id,
        property_id=rule_data.property_id,
        tenant_name=rule_data.tenant_name,
        payment_start_day=rule_data.payment_start_day,
        payment_end_day=rule_data.payment_end_day,
        allow_previous_month_end=rule_data.allow_previous_month_end,
        previous_month_end_days=rule_data.previous_month_end_days,
        overdue_grace_days=rule_data.overdue_grace_days,
        warning_days=rule_data.warning_days,
        critical_days=rule_data.critical_days,
        rule_name=rule_data.rule_name,
        is_active=rule_data.is_active
    )
    
    session.add(rule)
    session.commit()
    session.refresh(rule)
    return rule

@router.put("/{rule_id}", response_model=PaymentRule)
def update_payment_rule(
    rule_id: int,
    rule_data: PaymentRuleUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update an existing payment rule"""
    rule = session.get(PaymentRule, rule_id)
    if not rule or rule.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Payment rule not found")
    
    # Update fields that are provided
    update_data = rule_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(rule, key) and key != "id" and key != "user_id":
            setattr(rule, key, value)
    
    session.add(rule)
    session.commit()
    session.refresh(rule)
    return rule

@router.delete("/{rule_id}")
def delete_payment_rule(
    rule_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a payment rule"""
    rule = session.get(PaymentRule, rule_id)
    if not rule or rule.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Payment rule not found")
    
    session.delete(rule)
    session.commit()
    return {"message": "Payment rule deleted successfully"}

@router.get("/properties-and-tenants", response_model=List[PropertyTenantInfo])
def get_properties_and_tenants(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all properties and their active tenants for rule creation"""
    properties = session.exec(
        select(Property).where(Property.owner_id == current_user.id)
    ).all()
    
    result = []
    for prop in properties:
        # Get active contracts for this property
        active_contracts = session.exec(
            select(RentalContract)
            .where(RentalContract.property_id == prop.id)
            .where(RentalContract.is_active == True)
        ).all()
        
        tenants = [contract.tenant_name for contract in active_contracts]
        
        result.append(PropertyTenantInfo(
            property_id=prop.id,
            property_address=prop.address,
            tenants=tenants
        ))
    
    return result

@router.get("/default-rule")
def create_default_rule(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a default payment rule if user doesn't have any"""
    existing_rules = session.exec(
        select(PaymentRule).where(PaymentRule.user_id == current_user.id)
    ).all()
    
    if not existing_rules:
        default_rule = PaymentRule(
            user_id=current_user.id,
            property_id=None,  # Global rule
            tenant_name=None,  # All tenants
            payment_start_day=1,
            payment_end_day=5,
            allow_previous_month_end=False,
            previous_month_end_days=0,
            overdue_grace_days=15,
            warning_days=30,
            critical_days=60,
            rule_name="Regla por defecto",
            is_active=True
        )
        
        session.add(default_rule)
        session.commit()
        session.refresh(default_rule)
        return default_rule
    
    return existing_rules[0]