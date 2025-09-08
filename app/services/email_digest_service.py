# app/services/email_digest_service.py
from typing import List, Dict, Optional
from datetime import date, datetime, timedelta
from sqlmodel import Session, select
from ..models import (
    User, SmartNotification, NotificationDigest, NotificationChannel
)
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os

class EmailDigestService:
    """
    Service to generate and send weekly/monthly email digests
    of smart notifications and insights
    """
    
    def __init__(self, session: Session):
        self.session = session
        
        # Email configuration (from environment variables)
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@inmuebles.com')
    
    def generate_weekly_digest_for_user(self, user_id: int) -> Optional[Dict]:
        """Generate weekly digest for a user"""
        user = self.session.get(User, user_id)
        if not user:
            return None
        
        # Check if user has email notifications enabled
        email_channel = self.session.exec(
            select(NotificationChannel)
            .where(NotificationChannel.user_id == user_id)
            .where(NotificationChannel.channel_type == "email")
            .where(NotificationChannel.is_enabled == True)
        ).first()
        
        if not email_channel:
            return None
        
        # Get notifications from last week
        week_ago = date.today() - timedelta(days=7)
        notifications = self.session.exec(
            select(SmartNotification)
            .where(SmartNotification.user_id == user_id)
            .where(SmartNotification.created_at >= week_ago)
            .order_by(SmartNotification.priority_score.desc())
        ).all()
        
        if not notifications:
            return None  # Don't send digest if no notifications
        
        # Generate digest content
        digest_data = self._generate_digest_content(user, notifications, 'weekly')
        
        # Save digest to database
        digest = NotificationDigest(
            user_id=user_id,
            digest_type='weekly',
            subject=digest_data['subject'],
            content=digest_data['html_content'],
            notifications_included=json.dumps([n.id for n in notifications]),
            status='pending'
        )
        
        self.session.add(digest)
        self.session.commit()
        self.session.refresh(digest)
        
        return {
            'digest_id': digest.id,
            'user_email': user.email,
            'subject': digest_data['subject'],
            'notifications_count': len(notifications),
            'digest_data': digest_data
        }
    
    def send_weekly_digest(self, digest_id: int) -> bool:
        """Send a specific weekly digest"""
        digest = self.session.get(NotificationDigest, digest_id)
        if not digest or digest.status != 'pending':
            return False
        
        user = self.session.get(User, digest.user_id)
        if not user:
            return False
        
        try:
            success = self._send_email(
                to_email=user.email,
                subject=digest.subject,
                html_content=digest.content
            )
            
            if success:
                digest.status = 'sent'
                digest.sent_at = date.today()
            else:
                digest.status = 'failed'
            
            self.session.commit()
            return success
            
        except Exception as e:
            print(f"Error sending digest: {e}")
            digest.status = 'failed'
            self.session.commit()
            return False
    
    def _generate_digest_content(self, user: User, notifications: List[SmartNotification], digest_type: str) -> Dict:
        """Generate HTML content for email digest"""
        
        # Calculate summary stats
        total_notifications = len(notifications)
        critical_count = len([n for n in notifications if n.priority_score >= 90])
        high_count = len([n for n in notifications if n.priority_score >= 75])
        
        # Group notifications by type
        grouped_notifications = {}
        total_potential_savings = 0
        
        for notification in notifications:
            notif_type = notification.notification_type
            if notif_type not in grouped_notifications:
                grouped_notifications[notif_type] = []
            
            grouped_notifications[notif_type].append(notification)
            
            # Calculate potential savings
            if notification.contextual_data:
                try:
                    contextual_data = json.loads(notification.contextual_data)
                    if 'potential_savings' in contextual_data:
                        total_potential_savings += contextual_data['potential_savings']
                except:
                    pass
        
        # Generate subject
        subject = f"Resumen Semanal Inmobiliario - {total_notifications} Notificaciones"
        if critical_count > 0:
            subject += f" ({critical_count} Críticas)"
        
        # Generate HTML content
        html_content = self._build_html_digest(
            user=user,
            notifications=notifications,
            grouped_notifications=grouped_notifications,
            total_potential_savings=total_potential_savings,
            critical_count=critical_count,
            high_count=high_count,
            digest_type=digest_type
        )
        
        return {
            'subject': subject,
            'html_content': html_content,
            'summary': {
                'total_notifications': total_notifications,
                'critical_count': critical_count,
                'high_count': high_count,
                'potential_savings': total_potential_savings,
                'notification_types': list(grouped_notifications.keys())
            }
        }
    
    def _build_html_digest(self, user: User, notifications: List[SmartNotification], 
                          grouped_notifications: Dict, total_potential_savings: float,
                          critical_count: int, high_count: int, digest_type: str) -> str:
        """Build HTML email content"""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ padding: 30px; }}
                .summary {{ background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 30px; }}
                .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; margin-top: 15px; }}
                .summary-item {{ text-align: center; }}
                .summary-number {{ font-size: 24px; font-weight: bold; color: #4a5568; }}
                .summary-label {{ font-size: 12px; color: #718096; text-transform: uppercase; }}
                .notification {{ background-color: #fff; border-left: 4px solid #e2e8f0; margin-bottom: 20px; padding: 15px; border-radius: 0 8px 8px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .notification.critical {{ border-left-color: #e53e3e; }}
                .notification.high {{ border-left-color: #dd6b20; }}
                .notification.medium {{ border-left-color: #d69e2e; }}
                .notification-title {{ font-weight: bold; color: #2d3748; margin-bottom: 8px; }}
                .notification-message {{ color: #4a5568; margin-bottom: 10px; }}
                .notification-meta {{ display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }}
                .priority-badge {{ padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; text-transform: uppercase; }}
                .priority-critical {{ background-color: #feb2b2; color: #c53030; }}
                .priority-high {{ background-color: #fbd38d; color: #c05621; }}
                .priority-medium {{ background-color: #faf089; color: #b7791f; }}
                .priority-low {{ background-color: #c6f6d5; color: #2f855a; }}
                .action-button {{ display: inline-block; background-color: #4299e1; color: white; text-decoration: none; padding: 8px 16px; border-radius: 6px; font-size: 14px; margin-top: 10px; }}
                .section-title {{ font-size: 18px; font-weight: bold; color: #2d3748; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
                .footer {{ background-color: #2d3748; color: white; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; }}
                .savings-highlight {{ background-color: #c6f6d5; border: 1px solid #9ae6b4; border-radius: 8px; padding: 15px; margin-bottom: 20px; text-align: center; }}
                .savings-amount {{ font-size: 28px; font-weight: bold; color: #2f855a; }}
            </style>
        </head>
        <body>
            <div class="container">
                <!-- Header -->
                <div class="header">
                    <h1>🏡 Resumen Semanal Inmobiliario</h1>
                    <p>Notificaciones inteligentes para tus propiedades</p>
                    <p style="margin: 0; opacity: 0.9;">Semana del {(date.today() - timedelta(days=7)).strftime('%d/%m/%Y')} al {date.today().strftime('%d/%m/%Y')}</p>
                </div>
                
                <!-- Content -->
                <div class="content">
                    <!-- Summary Stats -->
                    <div class="summary">
                        <h2 style="margin-top: 0; color: #2d3748;">📊 Resumen de la Semana</h2>
                        <div class="summary-grid">
                            <div class="summary-item">
                                <div class="summary-number">{len(notifications)}</div>
                                <div class="summary-label">Notificaciones</div>
                            </div>
                            <div class="summary-item">
                                <div class="summary-number" style="color: #e53e3e;">{critical_count}</div>
                                <div class="summary-label">Críticas</div>
                            </div>
                            <div class="summary-item">
                                <div class="summary-number" style="color: #dd6b20;">{high_count}</div>
                                <div class="summary-label">Alta Prioridad</div>
                            </div>
                            <div class="summary-item">
                                <div class="summary-number" style="color: #38a169;">€{total_potential_savings:.0f}</div>
                                <div class="summary-label">Ahorro Potencial</div>
                            </div>
                        </div>
                    </div>
                    
                    {self._build_savings_highlight(total_potential_savings) if total_potential_savings > 0 else ''}
                    
                    <!-- Notifications by Priority -->
                    <div class="section-title">🔔 Notificaciones Destacadas</div>
        """
        
        # Add top priority notifications
        priority_notifications = sorted(notifications, key=lambda x: x.priority_score, reverse=True)[:5]
        
        for notification in priority_notifications:
            priority_class = self._get_priority_class(notification.priority_score)
            priority_label = self._get_priority_label(notification.priority_score)
            
            contextual_info = ""
            if notification.contextual_data:
                try:
                    data = json.loads(notification.contextual_data)
                    if data.get('property_address'):
                        contextual_info += f"📍 {data['property_address']}<br>"
                    if data.get('tenant_name'):
                        contextual_info += f"👤 {data['tenant_name']}<br>"
                    if data.get('potential_savings'):
                        contextual_info += f"💰 Ahorro potencial: €{data['potential_savings']:.0f}<br>"
                except:
                    pass
            
            html += f"""
            <div class="notification {priority_class}">
                <div class="notification-title">{notification.title}</div>
                <div class="notification-message">{notification.message}</div>
                {f'<div style="font-size: 12px; color: #718096; margin: 8px 0;">{contextual_info}</div>' if contextual_info else ''}
                <div class="notification-meta">
                    <span class="priority-badge priority-{priority_class}">{priority_label}</span>
                    <small style="color: #718096;">{notification.created_at.strftime('%d/%m/%Y')}</small>
                </div>
                {f'<a href="https://inmuebles-web.vercel.app{notification.action_url}" class="action-button">Ver detalles</a>' if notification.action_url else ''}
            </div>
            """
        
        # Add footer with recommendations
        recommendations = self._generate_weekly_recommendations(notifications)
        
        html += f"""
                    <!-- Recommendations -->
                    <div class="section-title">💡 Recomendaciones de la Semana</div>
                    <div style="background-color: #edf2f7; border-radius: 8px; padding: 20px;">
        """
        
        for i, recommendation in enumerate(recommendations[:3], 1):
            html += f"<p><strong>{i}.</strong> {recommendation}</p>"
        
        if not recommendations:
            html += "<p>¡Excelente! No hay recomendaciones específicas esta semana. Tus propiedades están bien gestionadas.</p>"
        
        html += """
                    </div>
                </div>
                
                <!-- Footer -->
                <div class="footer">
                    <p><strong>🏡 Sistema de Notificaciones Inteligentes</strong></p>
                    <p style="margin: 10px 0;">Optimizando la gestión de tus propiedades inmobiliarias</p>
                    <p style="margin: 0; font-size: 12px; opacity: 0.8;">
                        <a href="https://inmuebles-web.vercel.app/financial-agent" style="color: #90cdf4;">Acceder al dashboard</a> | 
                        <a href="https://inmuebles-web.vercel.app/notifications/settings" style="color: #90cdf4;">Configurar notificaciones</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _build_savings_highlight(self, total_savings: float) -> str:
        """Build savings highlight section"""
        if total_savings <= 0:
            return ""
        
        return f"""
        <div class="savings-highlight">
            <div style="font-size: 16px; color: #2f855a; margin-bottom: 8px;">💰 Oportunidad de Ahorro Semanal</div>
            <div class="savings-amount">€{total_savings:.0f}</div>
            <div style="font-size: 14px; color: #68d391; margin-top: 5px;">
                Ahorro anual estimado: €{total_savings * 52:.0f}
            </div>
        </div>
        """
    
    def _get_priority_class(self, priority_score: int) -> str:
        """Get CSS class for priority level"""
        if priority_score >= 90:
            return "critical"
        elif priority_score >= 75:
            return "high"
        elif priority_score >= 60:
            return "medium"
        else:
            return "low"
    
    def _get_priority_label(self, priority_score: int) -> str:
        """Get label for priority level"""
        if priority_score >= 90:
            return "Crítica"
        elif priority_score >= 75:
            return "Alta"
        elif priority_score >= 60:
            return "Media"
        else:
            return "Baja"
    
    def _generate_weekly_recommendations(self, notifications: List[SmartNotification]) -> List[str]:
        """Generate weekly recommendations based on notifications"""
        recommendations = []
        
        # Analyze notification types
        type_counts = {}
        for notif in notifications:
            type_counts[notif.notification_type] = type_counts.get(notif.notification_type, 0) + 1
        
        # Generate recommendations
        if type_counts.get("contract_expiring_60d", 0) > 0:
            recommendations.append("Revisa los contratos próximos a vencer y prepara las renovaciones con antelación para mantener la ocupación.")
        
        if type_counts.get("payment_missing", 0) > 1:
            recommendations.append("Considera implementar recordatorios automáticos de pago o domiciliaciones para reducir retrasos.")
        
        if type_counts.get("expense_optimization", 0) > 2:
            recommendations.append("Dedica tiempo esta semana a comparar proveedores y negociar mejores tarifas para servicios recurrentes.")
        
        if type_counts.get("rent_below_market", 0) > 0:
            recommendations.append("Evalúa incrementos de renta graduales basados en análisis de mercado para maximizar ROI sin afectar ocupación.")
        
        if type_counts.get("tax_optimization_q4", 0) > 0:
            recommendations.append("Aprovecha las últimas semanas del año para optimizar gastos deducibles y preparar la declaración fiscal.")
        
        return recommendations
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add HTML part
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def send_weekly_digests_batch(self) -> Dict:
        """Send weekly digests to all eligible users"""
        results = {
            'total_users': 0,
            'digests_generated': 0,
            'digests_sent': 0,
            'errors': []
        }
        
        # Get all users with email notifications enabled
        users_with_email = self.session.exec(
            select(User).join(NotificationChannel).where(
                NotificationChannel.channel_type == "email",
                NotificationChannel.is_enabled == True
            )
        ).all()
        
        results['total_users'] = len(users_with_email)
        
        for user in users_with_email:
            try:
                # Generate digest
                digest_data = self.generate_weekly_digest_for_user(user.id)
                
                if digest_data:
                    results['digests_generated'] += 1
                    
                    # Send digest
                    if self.send_weekly_digest(digest_data['digest_id']):
                        results['digests_sent'] += 1
                
            except Exception as e:
                results['errors'].append(f"User {user.id}: {str(e)}")
        
        return results