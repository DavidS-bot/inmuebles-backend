# app/services/smart_notifications.py
from typing import List, Dict, Optional, Tuple
from datetime import date, datetime, timedelta
from sqlmodel import Session, select
from ..models import (
    User, Property, RentalContract, FinancialMovement, MortgageDetails, 
    ClassificationRule, SmartNotification, NotificationRule, NotificationTemplate,
    NotificationChannel, NotificationAnalytics, PaymentRule
)
import json
import statistics
import re

class SmartNotificationEngine:
    def __init__(self, session: Session):
        self.session = session
        self.today = date.today()
        
    def generate_notifications_for_user(self, user_id: int) -> List[Dict]:
        """Generate all contextual notifications for a user"""
        notifications = []
        
        # Check if user hasn't exceeded daily limit
        if not self._can_send_more_notifications(user_id):
            return []
        
        user = self.session.get(User, user_id)
        if not user:
            return []
            
        properties = self.session.exec(
            select(Property).where(Property.owner_id == user_id)
        ).all()
        
        for property in properties:
            notifications.extend(self._generate_contract_notifications(property))
            notifications.extend(self._generate_payment_notifications(property))
            notifications.extend(self._generate_tax_notifications(property))
            notifications.extend(self._generate_optimization_notifications(property))
        
        # Calculate priority scores and sort
        notifications = self._calculate_priority_scores(notifications)
        notifications.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Apply daily limits and timing rules
        filtered_notifications = self._apply_timing_rules(user_id, notifications)
        
        # Save to database
        for notif in filtered_notifications:
            self._save_notification(user_id, notif)
        
        return filtered_notifications
    
    def _generate_contract_notifications(self, property: Property) -> List[Dict]:
        """Generate contract-related notifications"""
        notifications = []
        
        # Get active contracts
        contracts = self.session.exec(
            select(RentalContract)
            .where(RentalContract.property_id == property.id)
            .where(RentalContract.is_active == True)
        ).all()
        
        for contract in contracts:
            if contract.end_date:
                days_until_expiry = (contract.end_date - self.today).days
                
                # Contract expiring in 60 days - with renewal template
                if 50 <= days_until_expiry <= 70:
                    notifications.append({
                        'type': 'contract_expiring_60d',
                        'title': f'Contrato {self._get_property_short_name(property)} vence en {days_until_expiry} días',
                        'message': f'Contrato de {contract.tenant_name} vence el {contract.end_date.strftime("%d/%m/%Y")}. Template de renovación disponible.',
                        'property_id': property.id,
                        'contextual_data': {
                            'tenant_name': contract.tenant_name,
                            'property_address': property.address,
                            'expiry_date': contract.end_date.isoformat(),
                            'current_rent': contract.monthly_rent,
                            'days_remaining': days_until_expiry,
                            'contract_id': contract.id
                        },
                        'action_url': f'/financial-agent/contracts/renew/{contract.id}',
                        'base_priority': 85
                    })
                
                # Contract expiring in 30 days - urgent
                elif 25 <= days_until_expiry <= 35:
                    notifications.append({
                        'type': 'contract_expiring_30d',
                        'title': f'¡Contrato {self._get_property_short_name(property)} vence en {days_until_expiry} días!',
                        'message': f'Acción requerida: Renovar o finalizar contrato de {contract.tenant_name}',
                        'property_id': property.id,
                        'contextual_data': {
                            'tenant_name': contract.tenant_name,
                            'property_address': property.address,
                            'expiry_date': contract.end_date.isoformat(),
                            'days_remaining': days_until_expiry,
                            'contract_id': contract.id
                        },
                        'action_url': f'/financial-agent/contracts/{contract.id}',
                        'base_priority': 95
                    })
        
        return notifications
    
    def _generate_payment_notifications(self, property: Property) -> List[Dict]:
        """Generate payment and rent optimization notifications using configurable payment rules"""
        notifications = []
        
        # Get active contracts for this property
        active_contracts = self.session.exec(
            select(RentalContract)
            .where(RentalContract.property_id == property.id)
            .where(RentalContract.is_active == True)
        ).all()
        
        if not active_contracts:
            return notifications
        
        # Get user's payment rules
        user_id = property.owner_id
        payment_rules = self.session.exec(
            select(PaymentRule)
            .where(PaymentRule.user_id == user_id)
            .where(PaymentRule.is_active == True)
        ).all()
        
        # If no custom rules, create a default one
        if not payment_rules:
            default_rule = PaymentRule(
                user_id=user_id,
                property_id=None,
                tenant_name=None,
                payment_start_day=1,
                payment_end_day=5,
                overdue_grace_days=15,
                warning_days=30,
                critical_days=60,
                rule_name="Regla por defecto",
                is_active=True
            )
            payment_rules = [default_rule]
        
        for contract in active_contracts:
            # Find the most specific rule for this contract
            applicable_rule = self._find_applicable_payment_rule(
                payment_rules, property.id, contract.tenant_name
            )
            
            if not applicable_rule:
                continue
            
            # Check payment status using the rule
            payment_status = self._check_payment_status(contract, applicable_rule)
            
            if payment_status['is_overdue']:
                notifications.append({
                    'type': 'payment_overdue',
                    'title': f'⚠️ {contract.tenant_name} lleva {payment_status["days_overdue"]} días sin pagar - {self._get_property_short_name(property)}',
                    'message': f'Último pago: {payment_status["last_payment_date"] or "No registrado"}. Renta esperada: €{contract.monthly_rent}',
                    'property_id': property.id,
                    'contextual_data': {
                        'tenant_name': contract.tenant_name,
                        'property_address': property.address,
                        'expected_amount': contract.monthly_rent,
                        'days_overdue': payment_status['days_overdue'],
                        'last_payment_date': payment_status['last_payment_date'],
                        'payment_window': f"Días {applicable_rule.payment_start_day}-{applicable_rule.payment_end_day} del mes",
                        'overdue_threshold': applicable_rule.overdue_grace_days,
                        'contract_id': contract.id,
                        'rule_id': applicable_rule.id if hasattr(applicable_rule, 'id') else None
                    },
                    'action_url': f'/financial-agent/property/{property.id}/contact-tenant',
                    'base_priority': self._calculate_payment_priority(payment_status['days_overdue'], applicable_rule)
                })
        
        # Rent optimization analysis
        market_analysis = self._analyze_rent_vs_market(property)
        if market_analysis:
            notifications.append(market_analysis)
        
        return notifications
    
    def _find_applicable_payment_rule(self, rules: List[PaymentRule], property_id: int, tenant_name: str) -> Optional[PaymentRule]:
        """Find the most specific payment rule that applies to this property/tenant"""
        # Priority order: specific property + specific tenant > specific property > global
        
        # 1. Look for property + tenant specific rule
        for rule in rules:
            if (rule.property_id == property_id and 
                rule.tenant_name and rule.tenant_name.lower() in tenant_name.lower()):
                return rule
        
        # 2. Look for property specific rule
        for rule in rules:
            if rule.property_id == property_id and not rule.tenant_name:
                return rule
        
        # 3. Look for tenant specific global rule
        for rule in rules:
            if (not rule.property_id and 
                rule.tenant_name and rule.tenant_name.lower() in tenant_name.lower()):
                return rule
        
        # 4. Look for global rule
        for rule in rules:
            if not rule.property_id and not rule.tenant_name:
                return rule
        
        return None
    
    def _check_payment_status(self, contract: RentalContract, rule: PaymentRule) -> Dict:
        """Check if payments are overdue according to the payment rule"""
        # Get the last payment for this contract
        last_payment = self.session.exec(
            select(FinancialMovement)
            .where(FinancialMovement.property_id == contract.property_id)
            .where(FinancialMovement.category == "Renta")
            .where(FinancialMovement.amount > 0)
            .where(FinancialMovement.concept.contains(contract.tenant_name))  # Try to match by tenant name
            .order_by(FinancialMovement.date.desc())
        ).first()
        
        # If no payment found by tenant name, get the last rent payment for this property
        if not last_payment:
            last_payment = self.session.exec(
                select(FinancialMovement)
                .where(FinancialMovement.property_id == contract.property_id)
                .where(FinancialMovement.category == "Renta")
                .where(FinancialMovement.amount > 0)
                .order_by(FinancialMovement.date.desc())
            ).first()
        
        if last_payment:
            days_since_payment = (self.today - last_payment.date).days
            last_payment_date = last_payment.date.strftime("%d/%m/%Y")
        else:
            # No payments found, use contract start date
            days_since_payment = (self.today - (contract.start_date or self.today - timedelta(days=60))).days
            last_payment_date = None
        
        # Calculate if payment is overdue based on the rule
        # Payment window + grace days = total allowed days before considering overdue
        expected_payment_interval = 30  # Assume monthly rent
        max_allowed_days = expected_payment_interval + rule.overdue_grace_days
        
        is_overdue = days_since_payment > max_allowed_days
        
        return {
            'is_overdue': is_overdue,
            'days_overdue': days_since_payment,
            'last_payment_date': last_payment_date,
            'rule_applied': rule.rule_name
        }
    
    def _calculate_payment_priority(self, days_overdue: int, rule: PaymentRule) -> int:
        """Calculate notification priority based on days overdue and rule thresholds"""
        if days_overdue >= rule.critical_days:
            return 95  # Critical
        elif days_overdue >= rule.warning_days:
            return 85  # High
        elif days_overdue >= rule.overdue_grace_days:
            return 75  # Medium
        else:
            return 60  # Low
    
    def _generate_tax_notifications(self, property: Property) -> List[Dict]:
        """Generate tax and fiscal optimization notifications"""
        notifications = []
        
        # Q4 tax optimization
        current_month = self.today.month
        if current_month >= 10:  # Q4
            tax_savings = self._calculate_q4_tax_savings(property)
            if tax_savings and tax_savings > 100:
                notifications.append({
                    'type': 'tax_optimization_q4',
                    'title': f'Puedes ahorrar €{tax_savings:.0f} optimizando gastos Q4',
                    'message': f'Oportunidades fiscales detectadas para {self._get_property_short_name(property)}',
                    'property_id': property.id,
                    'contextual_data': {
                        'property_address': property.address,
                        'potential_savings': tax_savings,
                        'quarter': 'Q4',
                        'year': self.today.year,
                        'optimization_areas': ['gastos deducibles', 'amortizaciones']
                    },
                    'action_url': f'/financial-agent/tax-assistant?property_id={property.id}',
                    'base_priority': 75
                })
        
        # Modelo 115 ready notification (quarterly)
        if current_month in [3, 6, 9, 12] and self.today.day >= 15:
            if self._should_file_modelo_115(property):
                notifications.append({
                    'type': 'modelo_115_ready',
                    'title': 'Modelo 115 listo para presentar (1-click)',
                    'message': f'Declaración trimestral preparada para {self._get_property_short_name(property)}',
                    'property_id': property.id,
                    'contextual_data': {
                        'property_address': property.address,
                        'quarter': f'Q{(current_month-1)//3 + 1}',
                        'year': self.today.year,
                        'estimated_payment': self._calculate_modelo_115_payment(property)
                    },
                    'action_url': f'/financial-agent/tax-assistant/modelo-115?property_id={property.id}',
                    'base_priority': 80
                })
        
        return notifications
    
    def _generate_optimization_notifications(self, property: Property) -> List[Dict]:
        """Generate financial optimization notifications"""
        notifications = []
        
        # Market rent analysis
        rent_analysis = self._analyze_rent_vs_market(property)
        if rent_analysis:
            notifications.append(rent_analysis)
        
        # Expense optimization
        expense_analysis = self._analyze_expense_optimization(property)
        if expense_analysis:
            notifications.extend(expense_analysis)
        
        return notifications
    
    def _analyze_rent_vs_market(self, property: Property) -> Optional[Dict]:
        """Analyze if rent is below market value"""
        active_contract = self.session.exec(
            select(RentalContract)
            .where(RentalContract.property_id == property.id)
            .where(RentalContract.is_active == True)
        ).first()
        
        if not active_contract:
            return None
        
        # Simplified market analysis (in real implementation, use actual market data)
        current_rent = active_contract.monthly_rent
        estimated_market_rent = self._estimate_market_rent(property)
        
        if estimated_market_rent > current_rent * 1.12:  # 12% below market
            percentage_below = ((estimated_market_rent - current_rent) / current_rent) * 100
            potential_increase = estimated_market_rent - current_rent
            
            return {
                'type': 'rent_below_market',
                'title': f'{self._get_property_short_name(property)} {percentage_below:.0f}% por debajo mercado - ¿subir renta?',
                'message': f'Potencial incremento: +€{potential_increase:.0f}/mes (€{potential_increase*12:.0f}/año)',
                'property_id': property.id,
                'contextual_data': {
                    'property_address': property.address,
                    'current_rent': current_rent,
                    'market_rent': estimated_market_rent,
                    'percentage_below': percentage_below,
                    'annual_potential': potential_increase * 12,
                    'contract_id': active_contract.id
                },
                'action_url': f'/financial-agent/property/{property.id}/rent-analysis',
                'base_priority': 70
            }
        
        return None
    
    def _analyze_expense_optimization(self, property: Property) -> List[Dict]:
        """Analyze expense optimization opportunities"""
        notifications = []
        
        # Get last year's expenses
        last_year = self.today - timedelta(days=365)
        expenses = self.session.exec(
            select(FinancialMovement)
            .where(FinancialMovement.property_id == property.id)
            .where(FinancialMovement.amount < 0)
            .where(FinancialMovement.date >= last_year)
        ).all()
        
        if not expenses:
            return notifications
        
        # Group by subcategory
        category_totals = {}
        for expense in expenses:
            category = expense.subcategory or expense.category
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += abs(expense.amount)
        
        # Find optimization opportunities
        for category, total in category_totals.items():
            if total > 500:  # Only for significant amounts
                savings_potential = self._calculate_savings_potential(category, total)
                if savings_potential > 50:
                    notifications.append({
                        'type': 'expense_optimization',
                        'title': f'Optimizar {category.lower()} - €{savings_potential:.0f} ahorro anual',
                        'message': f'Has gastado €{total:.0f} en {category} - buscar alternativas más económicas',
                        'property_id': property.id,
                        'contextual_data': {
                            'property_address': property.address,
                            'category': category,
                            'annual_spent': total,
                            'potential_savings': savings_potential,
                            'savings_percentage': (savings_potential / total) * 100
                        },
                        'action_url': f'/financial-agent/property/{property.id}/expenses?category={category}',
                        'base_priority': 60
                    })
        
        return notifications
    
    def _calculate_priority_scores(self, notifications: List[Dict]) -> List[Dict]:
        """Calculate intelligent priority scores (1-100)"""
        for notif in notifications:
            base_priority = notif.get('base_priority', 50)
            
            # Adjust based on type
            type_multipliers = {
                'contract_expiring_30d': 1.2,
                'payment_missing': 1.15,
                'tax_optimization_q4': 1.1,
                'modelo_115_ready': 1.1,
                'contract_expiring_60d': 1.05,
                'rent_below_market': 0.95,
                'expense_optimization': 0.85
            }
            
            multiplier = type_multipliers.get(notif['type'], 1.0)
            
            # Adjust based on amounts
            contextual_data = notif.get('contextual_data', {})
            if 'potential_savings' in contextual_data:
                amount = contextual_data['potential_savings']
                if amount > 1000:
                    multiplier += 0.1
                elif amount > 500:
                    multiplier += 0.05
            
            # Calculate final score
            priority_score = min(100, int(base_priority * multiplier))
            notif['priority_score'] = priority_score
            
            # Set priority level
            if priority_score >= 90:
                notif['priority'] = 'critical'
            elif priority_score >= 75:
                notif['priority'] = 'high'
            elif priority_score >= 60:
                notif['priority'] = 'medium'
            else:
                notif['priority'] = 'low'
        
        return notifications
    
    def _apply_timing_rules(self, user_id: int, notifications: List[Dict]) -> List[Dict]:
        """Apply timing rules and daily limits"""
        # Check user's notification rules
        user_rules = self.session.exec(
            select(NotificationRule).where(NotificationRule.user_id == user_id)
        ).first()
        
        max_daily = user_rules.max_daily_notifications if user_rules else 2
        
        # Check how many sent today
        today_count = self.session.exec(
            select(SmartNotification)
            .where(SmartNotification.user_id == user_id)
            .where(SmartNotification.created_at == self.today)
            .where(SmartNotification.status == 'sent')
        ).all()
        
        remaining_slots = max_daily - len(today_count)
        
        if remaining_slots <= 0:
            return []
        
        # Return top priority notifications within limit
        return notifications[:remaining_slots]
    
    def _can_send_more_notifications(self, user_id: int) -> bool:
        """Check if user can receive more notifications today"""
        # Check business hours if enabled
        user_rules = self.session.exec(
            select(NotificationRule).where(NotificationRule.user_id == user_id)
        ).first()
        
        if user_rules and user_rules.business_hours_only:
            current_hour = datetime.now().hour
            if current_hour < 9 or current_hour > 18:
                return False
        
        # Check daily limit
        today_count = len(self.session.exec(
            select(SmartNotification)
            .where(SmartNotification.user_id == user_id)
            .where(SmartNotification.created_at == self.today)
            .where(SmartNotification.status == 'sent')
        ).all())
        
        max_daily = user_rules.max_daily_notifications if user_rules else 2
        return today_count < max_daily
    
    def _save_notification(self, user_id: int, notification_data: Dict) -> SmartNotification:
        """Save notification to database"""
        notif = SmartNotification(
            user_id=user_id,
            property_id=notification_data.get('property_id'),
            notification_type=notification_data['type'],
            title=notification_data['title'],
            message=notification_data['message'],
            contextual_data=json.dumps(notification_data.get('contextual_data', {})),
            priority_score=notification_data['priority_score'],
            action_url=notification_data.get('action_url'),
            status='pending'
        )
        
        self.session.add(notif)
        self.session.commit()
        self.session.refresh(notif)
        
        return notif
    
    # Helper methods
    def _get_property_short_name(self, property: Property) -> str:
        """Get short name for property"""
        address = property.address
        # Extract street name or first part
        parts = address.split(',')
        street = parts[0].strip()
        
        # If it's a number + street, take street name
        street_parts = street.split()
        if len(street_parts) >= 2 and street_parts[-1].replace(',', '').isdigit():
            return ' '.join(street_parts[:-1])
        elif len(street_parts) >= 2:
            return ' '.join(street_parts[:2])
        
        return street[:15] + '...' if len(street) > 15 else street
    
    def _estimate_market_rent(self, property: Property) -> float:
        """Estimate market rent (simplified)"""
        # In real implementation, integrate with real estate APIs
        base_rent_per_m2 = {
            'madrid': 15,
            'barcelona': 13,
            'valencia': 10,
            'sevilla': 8,
            'default': 9
        }
        
        city = 'default'
        address_lower = property.address.lower()
        for city_name in base_rent_per_m2.keys():
            if city_name in address_lower:
                city = city_name
                break
        
        if property.m2:
            return property.m2 * base_rent_per_m2[city]
        else:
            # Estimate based on rooms
            estimated_m2 = (property.rooms or 2) * 15
            return estimated_m2 * base_rent_per_m2[city]
    
    def _calculate_q4_tax_savings(self, property: Property) -> Optional[float]:
        """Calculate potential Q4 tax savings"""
        # Simplified calculation - in real implementation, use tax rules
        last_3_months = self.today - timedelta(days=90)
        expenses = self.session.exec(
            select(FinancialMovement)
            .where(FinancialMovement.property_id == property.id)
            .where(FinancialMovement.amount < 0)
            .where(FinancialMovement.date >= last_3_months)
        ).all()
        
        deductible_expenses = sum(abs(e.amount) for e in expenses)
        return deductible_expenses * 0.21  # 21% tax rate
    
    def _should_file_modelo_115(self, property: Property) -> bool:
        """Check if property should file Modelo 115"""
        # Check if there were rental incomes this quarter
        quarter_start = date(self.today.year, ((self.today.month-1)//3)*3 + 1, 1)
        
        rental_income = self.session.exec(
            select(FinancialMovement)
            .where(FinancialMovement.property_id == property.id)
            .where(FinancialMovement.category == "Renta")
            .where(FinancialMovement.amount > 0)
            .where(FinancialMovement.date >= quarter_start)
        ).all()
        
        return len(rental_income) > 0
    
    def _calculate_modelo_115_payment(self, property: Property) -> float:
        """Calculate estimated Modelo 115 payment"""
        quarter_start = date(self.today.year, ((self.today.month-1)//3)*3 + 1, 1)
        
        rental_income = sum(m.amount for m in self.session.exec(
            select(FinancialMovement)
            .where(FinancialMovement.property_id == property.id)
            .where(FinancialMovement.category == "Renta")
            .where(FinancialMovement.amount > 0)
            .where(FinancialMovement.date >= quarter_start)
        ).all())
        
        return rental_income * 0.19  # 19% retention rate
    
    def _calculate_savings_potential(self, category: str, annual_amount: float) -> float:
        """Calculate potential savings for expense category"""
        savings_rates = {
            'Comunidad': 0.05,  # 5% savings possible
            'Seguros': 0.20,    # 20% savings possible
            'Suministros': 0.15, # 15% savings possible
            'Mantenimiento': 0.10, # 10% savings possible
            'Gestoria': 0.25,    # 25% savings possible
            'default': 0.10
        }
        
        rate = savings_rates.get(category, savings_rates['default'])
        return annual_amount * rate