'use client';

import React, { useState, useEffect } from 'react';
import { 
  Bell, Filter, Calendar, TrendingUp, AlertTriangle, Info, 
  CheckCircle, Clock, Settings, BarChart3, Archive, Trash2,
  ArrowRight, Target, DollarSign
} from 'lucide-react';

interface SmartNotification {
  id: number;
  type: string;
  title: string;
  message: string;
  priority: string;
  priority_score: number;
  property_id?: number;
  contextual_data?: any;
  action_url?: string;
  created_at: string;
  status: string;
}

interface NotificationCenterProps {
  apiUrl?: string;
}

export default function NotificationCenter({ apiUrl = 'http://localhost:8000' }: NotificationCenterProps) {
  const [notifications, setNotifications] = useState<SmartNotification[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('priority');
  const [showSettings, setShowSettings] = useState(false);
  const [analytics, setAnalytics] = useState<any>({
    today: { sent: 0, read: 0, dismissed: 0, acted: 0 },
    week: { sent: 0, read: 0, dismissed: 0, acted: 0 },
    month: { sent: 0, read: 0, dismissed: 0, acted: 0 },
    engagement_rate: 0
  });

  useEffect(() => {
    fetchSmartNotifications();
    fetchAnalytics();
  }, []);

  const fetchSmartNotifications = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/notifications/alerts`);
      const data = await response.json();
      // The alerts endpoint returns data.notifications array
      const notificationsList = data?.notifications || [];
      
      // Transform alerts format to expected notification format
      const transformedNotifications = notificationsList.map((alert: any, index: number) => ({
        id: typeof alert.id === 'string' ? index + 1 : alert.id,
        type: alert.type || 'info',
        title: alert.title,
        message: alert.description,
        priority: alert.type === 'critical' ? 'critical' : alert.type === 'warning' ? 'high' : alert.type === 'success' ? 'medium' : 'low',
        priority_score: alert.type === 'critical' ? 95 : alert.type === 'warning' ? 80 : alert.type === 'success' ? 70 : 60,
        property_id: alert.property_id,
        contextual_data: {
          amount: alert.amount,
          due_date: alert.due_date,
          actions: alert.actions,
          property_id: alert.property_id,
          alert_type: alert.type,
          raw_id: alert.id
        },
        action_url: Array.isArray(alert.actions) && alert.actions.length > 0 ? '/financial-agent' : null,
        created_at: alert.created_at,
        status: 'pending'
      }));
      
      setNotifications(transformedNotifications);
    } catch (error) {
      console.error('Error fetching smart notifications:', error);
      // Fallback to demo data
      setNotifications([
        {
          id: 1,
          type: 'contract_expiring_60d',
          title: 'Contrato Serrano 21 vence en 60 días + template renovación',
          message: 'María García - Contrato vence 15/11/2025. Template de renovación preparado.',
          priority: 'critical',
          priority_score: 95,
          property_id: 1,
          contextual_data: {
            tenant_name: 'María García',
            property_address: 'Calle Serrano 21',
            expiry_date: '2025-11-15',
            days_remaining: 60
          },
          action_url: '/financial-agent/contracts/renew/1',
          created_at: '2025-09-03T09:15:00',
          status: 'pending'
        },
        {
          id: 2,
          type: 'tax_optimization_q4',
          title: 'Puedes ahorrar €230 optimizando gastos Q4',
          message: 'Oportunidades detectadas: seguros (€120), suministros (€110)',
          priority: 'high',
          priority_score: 80,
          property_id: 2,
          contextual_data: {
            potential_savings: 230,
            optimization_areas: ['seguros', 'suministros']
          },
          action_url: '/financial-agent/tax-assistant',
          created_at: '2025-09-03T08:30:00',
          status: 'pending'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`${apiUrl}/notifications/analytics`);
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      } else {
        throw new Error('Analytics API not available');
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
      // Always set fallback analytics to prevent undefined errors
      setAnalytics({
        today: { sent: 3, read: 2, dismissed: 0, acted: 1 },
        week: { sent: 12, read: 8, dismissed: 2, acted: 6 },
        month: { sent: 45, read: 32, dismissed: 8, acted: 24 },
        engagement_rate: 71.1
      });
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'contract_expiring_60d':
      case 'contract_expiring_30d':
        return <Calendar className="h-5 w-5 text-blue-500" />;
      case 'payment_missing':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'tax_optimization_q4':
      case 'modelo_115_ready':
        return <Target className="h-5 w-5 text-green-500" />;
      case 'rent_below_market':
      case 'expense_optimization':
        return <TrendingUp className="h-5 w-5 text-purple-500" />;
      default:
        return <Bell className="h-5 w-5 text-gray-500" />;
    }
  };

  const getPriorityColor = (priority?: string) => {
    if (!priority) return 'bg-gray-100 text-gray-800 border-gray-200';
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getContextualInfo = (notification: SmartNotification) => {
    const data = notification.contextual_data || {};
    const info = [];

    // Original contextual data
    if (data.tenant_name) {
      info.push(`Inquilino: ${data.tenant_name}`);
    }
    if (data.potential_savings) {
      info.push(`Ahorro: €${data.potential_savings}`);
    }
    if (data.days_remaining) {
      info.push(`${data.days_remaining} días restantes`);
    }
    if (data.property_address) {
      info.push(`Dirección: ${data.property_address}`);
    }

    // New transformed data from alerts endpoint
    if (data.amount) {
      info.push(`Importe: €${data.amount}`);
    }
    if (data.due_date) {
      info.push(`Fecha límite: ${new Date(data.due_date).toLocaleDateString('es-ES')}`);
    }
    if (data.actions && Array.isArray(data.actions)) {
      info.push(`Acciones disponibles: ${data.actions.length}`);
    }
    if (data.property_id) {
      info.push(`Propiedad ID: #${data.property_id}`);
    }

    return info;
  };

  const filteredNotifications = (Array.isArray(notifications) ? notifications : []).filter(notification => {
    if (filter === 'all') return true;
    if (filter === 'unread') return notification.status === 'pending';
    if (filter === 'critical') return notification.priority === 'critical';
    if (filter === 'contracts') return notification.type.includes('contract');
    if (filter === 'financial') return notification.type.includes('tax') || notification.type.includes('optimization');
    return true;
  });

  const sortedNotifications = [...filteredNotifications].sort((a, b) => {
    if (sortBy === 'priority') return b.priority_score - a.priority_score;
    if (sortBy === 'date') return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    return 0;
  });

  const handleAction = async (notification: SmartNotification) => {
    try {
      await fetch(`${apiUrl}/notifications/${notification.id}/action`, { method: 'POST' });
      if (notification.action_url) {
        window.location.href = notification.action_url;
      }
    } catch (error) {
      console.error('Error handling action:', error);
    }
  };

  const handleDismiss = async (notificationId: number) => {
    try {
      await fetch(`${apiUrl}/notifications/${notificationId}/dismiss`, { method: 'POST' });
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
    } catch (error) {
      console.error('Error dismissing notification:', error);
    }
  };

  const handleMarkRead = async (notificationId: number) => {
    try {
      await fetch(`${apiUrl}/notifications/${notificationId}/read`, { method: 'POST' });
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, status: 'read' } : n)
      );
    } catch (error) {
      console.error('Error marking as read:', error);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Centro de Notificaciones Inteligentes
            </h1>
            <p className="text-gray-600">
              Notificaciones contextuales y oportunidades optimizadas por IA
            </p>
          </div>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
          >
            <Settings className="h-6 w-6" />
          </button>
        </div>

        {/* Analytics Summary */}
        {analytics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Hoy</p>
                  <p className="text-2xl font-semibold text-gray-900">{analytics.today?.sent || 0}</p>
                </div>
                <Bell className="h-8 w-8 text-blue-500" />
              </div>
            </div>
            
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Esta Semana</p>
                  <p className="text-2xl font-semibold text-gray-900">{analytics.week?.sent || 0}</p>
                </div>
                <BarChart3 className="h-8 w-8 text-green-500" />
              </div>
            </div>
            
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Engagement</p>
                  <p className="text-2xl font-semibold text-gray-900">{analytics.engagement_rate?.toFixed(1) || '0.0'}%</p>
                </div>
                <Target className="h-8 w-8 text-purple-500" />
              </div>
            </div>
            
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Acciones</p>
                  <p className="text-2xl font-semibold text-gray-900">{analytics.week?.acted || 0}</p>
                </div>
                <CheckCircle className="h-8 w-8 text-orange-500" />
              </div>
            </div>
          </div>
        )}

        {/* Filters and Controls */}
        <div className="flex flex-wrap items-center gap-4 bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center space-x-2">
            <Filter className="h-5 w-5 text-gray-400" />
            <span className="text-sm font-medium text-gray-700">Filtrar:</span>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">Todas</option>
              <option value="unread">No leídas</option>
              <option value="critical">Críticas</option>
              <option value="contracts">Contratos</option>
              <option value="financial">Financieras</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700">Ordenar:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="priority">Por Prioridad</option>
              <option value="date">Por Fecha</option>
            </select>
          </div>

          <div className="flex items-center space-x-2 ml-auto">
            <span className="text-sm text-gray-600">
              {sortedNotifications.length} notificación{sortedNotifications.length !== 1 ? 'es' : ''}
            </span>
          </div>
        </div>
      </div>

      {/* Notifications List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Generando notificaciones inteligentes...</p>
        </div>
      ) : sortedNotifications.length === 0 ? (
        <div className="text-center py-12">
          <Bell className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <p className="text-lg text-gray-600 mb-2">No hay notificaciones</p>
          <p className="text-gray-500">¡Perfecto! No tienes asuntos pendientes importantes.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {sortedNotifications.map((notification) => (
            <div
              key={notification.id}
              className={`bg-white rounded-lg border-l-4 shadow-sm hover:shadow-md transition-shadow ${
                notification.priority === 'critical' ? 'border-l-red-500' :
                notification.priority === 'high' ? 'border-l-orange-500' :
                notification.priority === 'medium' ? 'border-l-yellow-500' :
                'border-l-green-500'
              } ${notification.status === 'pending' ? 'bg-gray-50' : ''}`}
            >
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4 flex-1">
                    {getNotificationIcon(notification.type)}
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {notification.title}
                        </h3>
                        <div className="flex items-center space-x-2">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getPriorityColor(notification.priority)}`}>
                            {notification.priority?.toUpperCase() || 'NORMAL'} ({notification.priority_score || 0})
                          </span>
                          {notification.status === 'pending' && (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              NUEVA
                            </span>
                          )}
                        </div>
                      </div>

                      <p className="text-gray-700 mb-3">
                        {notification.message}
                      </p>

                      {/* Contextual Information */}
                      {notification.contextual_data && (
                        <div className="bg-gray-50 rounded-lg p-3 mb-3">
                          <h4 className="text-sm font-medium text-gray-700 mb-2">Información contextual:</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-600">
                            {getContextualInfo(notification).map((info, index) => (
                              <div key={index} className="flex items-center space-x-1">
                                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                                <span>{info}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span className="flex items-center">
                            <Clock className="h-4 w-4 mr-1" />
                            {new Date(notification.created_at).toLocaleString('es-ES')}
                          </span>
                          {notification.property_id && (
                            <span>Propiedad #{notification.property_id}</span>
                          )}
                        </div>

                        <div className="flex items-center space-x-2">
                          {notification.status === 'pending' && (
                            <button
                              onClick={() => handleMarkRead(notification.id)}
                              className="text-sm text-gray-600 hover:text-gray-800 px-3 py-1 rounded-md hover:bg-gray-100"
                            >
                              Marcar leída
                            </button>
                          )}
                          
                          {notification.contextual_data?.actions && Array.isArray(notification.contextual_data.actions) && notification.contextual_data.actions.length > 0 && (
                            <div className="flex flex-wrap gap-2">
                              {notification.contextual_data.actions.slice(0, 2).map((action: string, actionIndex: number) => (
                                <button
                                  key={actionIndex}
                                  onClick={() => handleAction(notification)}
                                  className="inline-flex items-center px-3 py-1 bg-blue-500 text-white text-xs font-medium rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                  {action}
                                  <ArrowRight className="h-3 w-3 ml-1" />
                                </button>
                              ))}
                              {notification.contextual_data.actions.length > 2 && (
                                <span className="text-xs text-gray-500 px-2 py-1">
                                  +{notification.contextual_data.actions.length - 2} más
                                </span>
                              )}
                            </div>
                          )}
                          
                          <button
                            onClick={() => handleDismiss(notification.id)}
                            className="text-gray-400 hover:text-gray-600 p-2 rounded-md hover:bg-gray-100"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}