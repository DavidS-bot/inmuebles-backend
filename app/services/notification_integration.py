# app/services/notification_integration.py
from typing import List, Dict, Optional
from datetime import date, datetime, timedelta
from sqlmodel import Session, select
from ..models import (
    User, Property, FinancialMovement, ClassificationRule, 
    SmartNotification, RentalContract
)
from .smart_notifications import SmartNotificationEngine
import json

class NotificationRuleIntegration:
    """
    Service to integrate smart notifications with the existing 
    classification rules and financial movement system
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.notification_engine = SmartNotificationEngine(session)
    
    def trigger_notifications_for_new_movement(self, movement: FinancialMovement) -> List[Dict]:
        """
        Analyze new financial movement and trigger relevant notifications
        """
        notifications = []
        
        if not movement.property_id:
            return notifications
            
        property = self.session.get(Property, movement.property_id)
        if not property:
            return notifications
        
        # Check for payment patterns that should trigger notifications
        notifications.extend(self._check_payment_anomalies(movement, property))
        notifications.extend(self._check_classification_opportunities(movement, property))
        
        return notifications
    
    def _check_payment_anomalies(self, movement: FinancialMovement, property: Property) -> List[Dict]:
        """Check for payment anomalies that should trigger notifications"""
        notifications = []
        
        # Large unexpected expenses
        if movement.amount < -1000 and movement.category == "Gasto":
            notifications.append({
                'type': 'large_expense_alert',
                'title': f'Gasto inusual detectado - {property.address}',
                'message': f'Gasto de €{abs(movement.amount):.0f} registrado: {movement.concept}',
                'property_id': property.id,
                'contextual_data': {
                    'amount': abs(movement.amount),
                    'concept': movement.concept,
                    'date': movement.date.isoformat(),
                    'property_address': property.address
                },
                'action_url': f'/financial-agent/property/{property.id}/movements',
                'base_priority': 80
            })
        
        # Missing rent payment pattern
        if movement.category == "Renta" and movement.amount > 0:
            # Check if this breaks a pattern of missing payments
            last_rent_before = self.session.exec(
                select(FinancialMovement)
                .where(FinancialMovement.property_id == property.id)
                .where(FinancialMovement.category == "Renta")
                .where(FinancialMovement.amount > 0)
                .where(FinancialMovement.date < movement.date)
                .order_by(FinancialMovement.date.desc())
            ).first()
            
            if last_rent_before:
                days_between = (movement.date - last_rent_before.date).days
                if days_between > 40:  # More than typical monthly interval
                    notifications.append({
                        'type': 'rent_payment_restored',
                        'title': f'Pago de renta recibido tras {days_between} días',
                        'message': f'Inquilino ha pagado después de {days_between} días de retraso',
                        'property_id': property.id,
                        'contextual_data': {
                            'days_delayed': days_between,
                            'amount': movement.amount,
                            'tenant_name': movement.tenant_name,
                            'property_address': property.address
                        },
                        'action_url': f'/financial-agent/property/{property.id}',
                        'base_priority': 70
                    })
        
        return notifications
    
    def _check_classification_opportunities(self, movement: FinancialMovement, property: Property) -> List[Dict]:
        """Check if movement reveals opportunities to improve classification rules"""
        notifications = []
        
        if not movement.is_classified:
            # Movement wasn't automatically classified - suggest creating a rule
            notifications.append({
                'type': 'classification_opportunity',
                'title': f'Crear regla de clasificación para "{movement.concept}"',
                'message': f'Movimiento no clasificado automáticamente. ¿Crear regla para casos similares?',
                'property_id': property.id,
                'contextual_data': {
                    'concept': movement.concept,
                    'amount': movement.amount,
                    'suggested_category': self._suggest_category(movement.concept),
                    'property_address': property.address
                },
                'action_url': f'/financial-agent/property/{property.id}/rules',
                'base_priority': 60
            })
        
        return notifications
    
    def _suggest_category(self, concept: str) -> str:
        """Suggest a category based on the movement concept"""
        concept_lower = concept.lower()
        
        # Simple keyword-based suggestions
        if any(word in concept_lower for word in ['hipoteca', 'banco', 'prestamo']):
            return 'Hipoteca'
        elif any(word in concept_lower for word in ['comunidad', 'administrador']):
            return 'Gasto - Comunidad'
        elif any(word in concept_lower for word in ['seguro', 'aseguradora']):
            return 'Gasto - Seguros'
        elif any(word in concept_lower for word in ['ibi', 'impuesto']):
            return 'Gasto - IBI'
        elif any(word in concept_lower for word in ['luz', 'electricidad', 'gas', 'agua']):
            return 'Gasto - Suministros'
        elif any(word in concept_lower for word in ['reparacion', 'fontanero', 'electricista']):
            return 'Gasto - Mantenimiento'
        else:
            return 'Gasto'
    
    def bulk_generate_notifications_for_user(self, user_id: int) -> Dict:
        """
        Generate all types of notifications for a user, integrating 
        with classification rules and movement patterns
        """
        # Use the smart notification engine
        notifications = self.notification_engine.generate_notifications_for_user(user_id)
        
        # Add rule-based notifications
        rule_notifications = self._generate_rule_based_notifications(user_id)
        notifications.extend(rule_notifications)
        
        return {
            'notifications': notifications,
            'total_generated': len(notifications),
            'breakdown': self._analyze_notification_breakdown(notifications)
        }
    
    def _generate_rule_based_notifications(self, user_id: int) -> List[Dict]:
        """Generate notifications based on classification rule patterns"""
        notifications = []
        
        # Get user's properties
        properties = self.session.exec(
            select(Property).where(Property.owner_id == user_id)
        ).all()
        
        for property in properties:
            # Check for properties without classification rules
            rules_count = len(self.session.exec(
                select(ClassificationRule)
                .where(ClassificationRule.property_id == property.id)
                .where(ClassificationRule.is_active == True)
            ).all())
            
            if rules_count == 0:
                notifications.append({
                    'type': 'missing_classification_rules',
                    'title': f'Configurar reglas de clasificación - {property.address}',
                    'message': 'Esta propiedad no tiene reglas de clasificación automática configuradas',
                    'property_id': property.id,
                    'contextual_data': {
                        'property_address': property.address,
                        'suggested_rules': self._get_suggested_rules_for_property(property)
                    },
                    'action_url': f'/financial-agent/property/{property.id}/rules',
                    'base_priority': 65
                })
            
            # Check for unclassified movements in the last month
            last_month = date.today() - timedelta(days=30)
            unclassified_movements = self.session.exec(
                select(FinancialMovement)
                .where(FinancialMovement.property_id == property.id)
                .where(FinancialMovement.is_classified == False)
                .where(FinancialMovement.date >= last_month)
            ).all()
            
            if len(unclassified_movements) >= 3:
                notifications.append({
                    'type': 'multiple_unclassified',
                    'title': f'{len(unclassified_movements)} movimientos sin clasificar - {property.address}',
                    'message': f'Hay {len(unclassified_movements)} movimientos sin clasificar en el último mes',
                    'property_id': property.id,
                    'contextual_data': {
                        'property_address': property.address,
                        'unclassified_count': len(unclassified_movements),
                        'sample_concepts': [m.concept for m in unclassified_movements[:3]]
                    },
                    'action_url': f'/financial-agent/property/{property.id}/movements',
                    'base_priority': 70
                })
        
        return notifications
    
    def _get_suggested_rules_for_property(self, property: Property) -> List[Dict]:
        """Get suggested classification rules for a property"""
        suggestions = []
        
        # Check if property has rental contracts
        contracts = self.session.exec(
            select(RentalContract).where(RentalContract.property_id == property.id)
        ).all()
        
        for contract in contracts:
            if contract.tenant_name:
                suggestions.append({
                    'keyword': contract.tenant_name.lower(),
                    'category': 'Renta',
                    'subcategory': 'Alquiler',
                    'tenant_name': contract.tenant_name
                })
        
        # Standard expense rules
        standard_rules = [
            {'keyword': 'comunidad', 'category': 'Gasto', 'subcategory': 'Comunidad'},
            {'keyword': 'seguro hogar', 'category': 'Gasto', 'subcategory': 'Seguros'},
            {'keyword': 'ibi', 'category': 'Gasto', 'subcategory': 'IBI'},
            {'keyword': 'hipoteca', 'category': 'Hipoteca', 'subcategory': 'Cuota hipoteca'}
        ]
        
        suggestions.extend(standard_rules)
        return suggestions
    
    def _analyze_notification_breakdown(self, notifications: List[Dict]) -> Dict:
        """Analyze the breakdown of generated notifications"""
        breakdown = {
            'by_type': {},
            'by_priority': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
            'properties_affected': set(),
            'total_potential_savings': 0
        }
        
        for notif in notifications:
            # Count by type
            notif_type = notif.get('type', 'unknown')
            breakdown['by_type'][notif_type] = breakdown['by_type'].get(notif_type, 0) + 1
            
            # Count by priority
            priority = notif.get('priority', 'low')
            breakdown['by_priority'][priority] += 1
            
            # Track affected properties
            if notif.get('property_id'):
                breakdown['properties_affected'].add(notif['property_id'])
            
            # Sum potential savings
            contextual_data = notif.get('contextual_data', {})
            if 'potential_savings' in contextual_data:
                breakdown['total_potential_savings'] += contextual_data['potential_savings']
        
        breakdown['properties_affected'] = len(breakdown['properties_affected'])
        return breakdown

def setup_notification_triggers(session: Session):
    """
    Set up database triggers or background tasks for automatic 
    notification generation when financial movements are created
    """
    # This would typically be implemented as database triggers
    # or background task queues (Celery, etc.)
    # For now, we'll provide the integration service
    pass