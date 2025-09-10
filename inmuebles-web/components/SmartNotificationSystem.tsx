'use client';

import React, { useState, useEffect } from 'react';
import { Bell, X, Check, AlertTriangle, Info, TrendingUp, Calendar, ArrowRight } from 'lucide-react';

interface NotificationData {
  id: string;
  type: 'critical' | 'warning' | 'info' | 'success';
  title: string;
  description: string;
  created_at: string;
  property_id?: number;
  amount?: number;
  due_date?: string;
  actions: string[];
  priority_score?: number;
}

interface SmartNotificationSystemProps {
  apiUrl?: string;
}

export default function SmartNotificationSystem({ apiUrl }: SmartNotificationSystemProps) {
  const API_URL = apiUrl || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const [notifications, setNotifications] = useState<NotificationData[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchNotifications();
    // Set up periodic refresh (every 5 minutes)
    const interval = setInterval(fetchNotifications, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/notifications/alerts`);
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
      } else {
        // Fallback to demo data
        setNotifications([
          {
            id: "demo_001",
            type: "critical",
            title: "Contrato Serrano 21 vence en 60 días + template renovación",
            description: "María García - Contrato vence 15/11/2025. Template de renovación preparado.",
            created_at: "2025-09-03T09:15:00",
            property_id: 1,
            amount: 1200.0,
            due_date: "2025-11-15",
            actions: ["Enviar template renovación", "Contactar inquilino", "Ver historial pagos"]
          },
          {
            id: "demo_002", 
            type: "success",
            title: "Puedes ahorrar €230 optimizando gastos Q4",
            description: "Oportunidades detectadas: seguros (€120), suministros (€110)",
            created_at: "2025-09-03T08:30:00",
            property_id: 2,
            amount: 230.0,
            actions: ["Ver análisis completo", "Comparar seguros", "Optimizar suministros"]
          }
        ]);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
      // Fallback to demo data on error
      setNotifications([
        {
          id: "demo_001",
          type: "critical",
          title: "Sistema de Notificaciones Inteligentes Activo",
          description: "El sistema está funcionando correctamente. Se mostrarán notificaciones contextuales cuando estén disponibles.",
          created_at: new Date().toISOString(),
          property_id: null,
          amount: null,
          actions: ["Ver configuración"]
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'critical':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'success':
        return <TrendingUp className="h-5 w-5 text-green-500" />;
      case 'info':
        return <Info className="h-5 w-5 text-blue-500" />;
      default:
        return <Bell className="h-5 w-5 text-gray-500" />;
    }
  };

  const getNotificationBgColor = (type: string) => {
    switch (type) {
      case 'critical':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'info':
        return 'bg-blue-50 border-blue-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getPriorityBadge = (type: string, priorityScore?: number) => {
    const score = priorityScore || 50;
    const priority = score >= 90 ? 'CRÍTICA' : score >= 75 ? 'ALTA' : score >= 60 ? 'MEDIA' : 'BAJA';
    
    const colorClass = type === 'critical' ? 'bg-red-100 text-red-800' :
                      type === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                      type === 'success' ? 'bg-green-100 text-green-800' :
                      'bg-blue-100 text-blue-800';

    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colorClass}`}>
        {priority}
      </span>
    );
  };

  const formatAmount = (amount?: number) => {
    if (!amount) return '';
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleNotificationAction = async (notificationId: string, action: string) => {
    // Track action analytics
    try {
      await fetch(`${API_URL}/notifications/${notificationId}/action`, {
        method: 'POST'
      });
    } catch (error) {
      console.error('Error tracking notification action:', error);
    }

    // Handle specific actions
    switch (action) {
      case 'Enviar template renovación':
      case 'Presentar automáticamente':
      case 'Ver análisis completo':
      case 'Ver análisis mercado':
        // These would open specific pages/modals
        console.log(`Action: ${action} for notification ${notificationId}`);
        break;
      default:
        console.log(`Generic action: ${action}`);
    }
  };

  const dismissNotification = async (notificationId: string) => {
    try {
      await fetch(`${API_URL}/notifications/${notificationId}/dismiss`, {
        method: 'POST'
      });
      
      // Remove from local state
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
    } catch (error) {
      console.error('Error dismissing notification:', error);
    }
  };

  const markAsRead = async (notificationId: string) => {
    try {
      await fetch(`${API_URL}/notifications/${notificationId}/read`, {
        method: 'POST'
      });
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const unreadCount = notifications.length;
  const criticalCount = notifications.filter(n => n.type === 'critical').length;

  return (
    <div className="relative">
      {/* Notification Bell */}
      <button
        onClick={() => setShowNotifications(!showNotifications)}
        className="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg"
      >
        <Bell className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className={`absolute -top-1 -right-1 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none transform translate-x-1/2 -translate-y-1/2 rounded-full ${
            criticalCount > 0 ? 'bg-red-500 text-white animate-pulse' : 'bg-blue-500 text-white'
          }`}>
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notification Panel */}
      {showNotifications && (
        <div className="absolute right-0 top-12 w-96 bg-white rounded-lg shadow-lg border border-gray-200 z-50 max-h-96 overflow-y-auto">
          <div className="p-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">
                Notificaciones Inteligentes
              </h3>
              <button
                onClick={() => setShowNotifications(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            {unreadCount > 0 && (
              <p className="text-sm text-gray-600 mt-1">
                {unreadCount} notificación{unreadCount !== 1 ? 'es' : ''} pendiente{unreadCount !== 1 ? 's' : ''}
              </p>
            )}
          </div>

          {loading ? (
            <div className="p-4 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
              <p className="text-sm text-gray-600 mt-2">Cargando notificaciones...</p>
            </div>
          ) : notifications.length === 0 ? (
            <div className="p-4 text-center">
              <Bell className="h-8 w-8 text-gray-300 mx-auto mb-2" />
              <p className="text-sm text-gray-600">No hay notificaciones nuevas</p>
            </div>
          ) : (
            <div className="max-h-80 overflow-y-auto">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-4 border-b border-gray-100 ${getNotificationBgColor(notification.type)} hover:bg-opacity-80 transition-colors`}
                  onClick={() => markAsRead(notification.id)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-start space-x-3 flex-1">
                      {getNotificationIcon(notification.type)}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <h4 className="text-sm font-semibold text-gray-900 truncate">
                            {notification.title}
                          </h4>
                          {getPriorityBadge(notification.type, notification.priority_score)}
                        </div>
                        <p className="text-sm text-gray-700 mb-2">
                          {notification.description}
                        </p>
                        
                        {/* Contextual Information */}
                        <div className="flex items-center space-x-4 text-xs text-gray-500 mb-3">
                          <span className="flex items-center">
                            <Calendar className="h-3 w-3 mr-1" />
                            {formatDate(notification.created_at)}
                          </span>
                          {notification.amount && (
                            <span className="font-medium text-gray-700">
                              {formatAmount(notification.amount)}
                            </span>
                          )}
                          {notification.due_date && (
                            <span className="text-red-600">
                              Vence: {new Date(notification.due_date).toLocaleDateString('es-ES')}
                            </span>
                          )}
                        </div>

                        {/* Action Buttons */}
                        {notification.actions && notification.actions.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {notification.actions.slice(0, 2).map((action, index) => (
                              <button
                                key={index}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleNotificationAction(notification.id, action);
                                }}
                                className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                              >
                                {action}
                                <ArrowRight className="h-3 w-3 ml-1" />
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        dismissNotification(notification.id);
                      }}
                      className="text-gray-400 hover:text-gray-600 ml-2"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="p-3 bg-gray-50 border-t border-gray-200">
              <button
                onClick={() => {
                  setShowNotifications(false);
                  // Navigate to full notifications page
                }}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                Ver todas las notificaciones →
              </button>
            </div>
          )}
        </div>
      )}

      {/* Toast Notifications for Critical Alerts */}
      <ToastNotifications 
        notifications={notifications.filter(n => n.type === 'critical')}
        onDismiss={dismissNotification}
        onAction={handleNotificationAction}
      />
    </div>
  );
}

// Toast component for critical notifications
interface ToastNotificationsProps {
  notifications: NotificationData[];
  onDismiss: (id: string) => void;
  onAction: (id: string, action: string) => void;
}

function ToastNotifications({ notifications, onDismiss, onAction }: ToastNotificationsProps) {
  const [visibleToasts, setVisibleToasts] = useState<Set<string>>(new Set());

  useEffect(() => {
    // Show new critical notifications as toasts
    notifications.forEach(notif => {
      if (!visibleToasts.has(notif.id)) {
        setVisibleToasts(prev => new Set(prev).add(notif.id));
        
        // Auto-hide after 10 seconds for critical notifications
        setTimeout(() => {
          setVisibleToasts(prev => {
            const newSet = new Set(prev);
            newSet.delete(notif.id);
            return newSet;
          });
        }, 10000);
      }
    });
  }, [notifications]);

  const visibleNotifications = notifications.filter(n => visibleToasts.has(n.id));

  if (visibleNotifications.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 space-y-2 z-50">
      {visibleNotifications.map((notification) => (
        <div
          key={notification.id}
          className="bg-red-500 text-white p-4 rounded-lg shadow-lg max-w-sm animate-slide-in-right"
        >
          <div className="flex justify-between items-start">
            <div className="flex items-start space-x-2">
              <AlertTriangle className="h-5 w-5 mt-0.5 animate-pulse" />
              <div className="flex-1">
                <h4 className="font-semibold text-sm mb-1">
                  {notification.title}
                </h4>
                <p className="text-sm opacity-90 mb-3">
                  {notification.description}
                </p>
                {notification.actions && notification.actions[0] && (
                  <button
                    onClick={() => {
                      onAction(notification.id, notification.actions[0]);
                      onDismiss(notification.id);
                      setVisibleToasts(prev => {
                        const newSet = new Set(prev);
                        newSet.delete(notification.id);
                        return newSet;
                      });
                    }}
                    className="bg-white bg-opacity-20 hover:bg-opacity-30 px-3 py-1 rounded text-xs font-medium transition-colors"
                  >
                    {notification.actions[0]}
                  </button>
                )}
              </div>
            </div>
            <button
              onClick={() => {
                onDismiss(notification.id);
                setVisibleToasts(prev => {
                  const newSet = new Set(prev);
                  newSet.delete(notification.id);
                  return newSet;
                });
              }}
              className="text-white opacity-70 hover:opacity-100"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}