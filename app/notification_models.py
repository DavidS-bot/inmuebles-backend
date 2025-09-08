# app/notification_models.py - Temporary file to isolate notification models
from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field

# Smart Notification System Models - Simplified for now
class NotificationChannel(SQLModel, table=True):
    __tablename__ = "notification_channels"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    channel_type: str  # "in_app", "email", "push", "whatsapp"
    is_enabled: bool = True
    settings: Optional[str] = None  # JSON string for channel-specific settings

class NotificationRule(SQLModel, table=True):
    __tablename__ = "notification_rules"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    rule_type: str  # "contract_expiring", "payment_due", "tax_opportunity", "rent_optimization", etc.
    is_enabled: bool = True
    threshold_value: Optional[float] = None  # For rules that need thresholds
    days_ahead: Optional[int] = None  # For time-based alerts (e.g., contract expiring in X days)
    priority: str = "medium"  # "critical", "high", "medium", "low"
    
    # Timing rules
    max_daily_notifications: int = 2
    business_hours_only: bool = True
    min_hours_between: int = 4  # Minimum hours between notifications of same type

class SmartNotification(SQLModel, table=True):
    __tablename__ = "smart_notifications"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    property_id: Optional[int] = Field(default=None, foreign_key="property.id")
    
    # Notification content
    notification_type: str  # "contract_expiring", "payment_optimization", "tax_due", etc.
    title: str
    message: str
    contextual_data: Optional[str] = None  # JSON string with additional context
    
    # Priority and scheduling
    priority_score: int  # Calculated priority (1-100)
    scheduled_for: Optional[date] = None  # When to send (for delayed notifications)
    
    # Status and delivery
    status: str = "pending"  # "pending", "sent", "read", "dismissed", "expired"
    created_at: date = Field(default_factory=lambda: date.today())
    sent_at: Optional[date] = None
    read_at: Optional[date] = None
    expires_at: Optional[date] = None
    
    # Channels and delivery
    channels_sent: Optional[str] = None  # JSON array of channels where it was sent
    delivery_attempts: int = 0
    
    # Action data
    action_url: Optional[str] = None
    action_data: Optional[str] = None  # JSON string with action-specific data

class NotificationTemplate(SQLModel, table=True):
    __tablename__ = "notification_templates"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    template_key: str  # "contract_renewal_60d", "tax_savings_q4", etc.
    title_template: str
    message_template: str
    
    # Context variables expected (JSON array)
    variables: Optional[str] = None
    
    # Template metadata
    category: str  # "contract", "tax", "financial", "maintenance"
    default_priority: str = "medium"
    suggested_channels: Optional[str] = None  # JSON array of recommended channels
    
    is_active: bool = True
    created_at: date = Field(default_factory=lambda: date.today())

class NotificationDigest(SQLModel, table=True):
    __tablename__ = "notification_digests"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    digest_type: str  # "daily", "weekly", "monthly"
    
    # Content
    subject: str
    content: str  # HTML content
    notifications_included: Optional[str] = None  # JSON array of notification IDs
    
    # Status
    status: str = "pending"  # "pending", "sent", "failed"
    created_at: date = Field(default_factory=lambda: date.today())
    sent_at: Optional[date] = None

class NotificationAnalytics(SQLModel, table=True):
    __tablename__ = "notification_analytics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    analytics_date: date = Field(default_factory=lambda: date.today())
    
    # Daily metrics
    notifications_sent: int = 0
    notifications_read: int = 0
    notifications_dismissed: int = 0
    notifications_acted: int = 0  # Notifications where user clicked action
    
    # Channel breakdown (JSON)
    channel_stats: Optional[str] = None
    
    # Timing stats
    avg_read_time_minutes: Optional[float] = None
    business_hours_sent: int = 0
    after_hours_sent: int = 0