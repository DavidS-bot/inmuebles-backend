'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';

interface Notification {
  id: string;
  type: 'warning' | 'info' | 'success' | 'critical';
  title: string;
  description: string;
  created_at: string;
  property_id?: number;
  amount?: number;
  due_date?: string;
  actions?: string[];
}

interface NotificationStats {
  total_alerts: number;
  critical_alerts: number;
  potential_savings: number;
  overdue_payments: number;
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [stats, setStats] = useState<NotificationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'critical' | 'warning' | 'info'>('all');
  const router = useRouter();

  useEffect(() => {
    fetchNotifications();
    fetchStats();
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await fetch('http://localhost:8000/notifications/alerts');
      const data = await response.json();
      setNotifications(data.notifications || []);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/notifications/stats');
      const data = await response.json();
      setStats(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching stats:', error);
      setLoading(false);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'critical': return '🚨';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
      case 'success': return '✅';
      default: return '📢';
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'critical': return 'border-red-500 bg-red-50';
      case 'warning': return 'border-yellow-500 bg-yellow-50';
      case 'info': return 'border-blue-500 bg-blue-50';
      case 'success': return 'border-green-500 bg-green-50';
      default: return 'border-gray-300 bg-gray-50';
    }
  };

  const filteredNotifications = notifications.filter(n => 
    filter === 'all' || n.type === filter
  );

  if (loading) {
    return (
      <div className="min-h-screen p-8 flex items-center justify-center">
        <div className="glass-card p-8 rounded-xl">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="text-center mt-4 text-gray-600">Cargando notificaciones...</p>
        </div>
      </div>
    );
  }

  return (
    <Layout
      title="Sistema de Notificaciones"
      subtitle="Alertas proactivas y monitorización inteligente"
      breadcrumbs={[
        { label: 'Agente Financiero', href: '/financial-agent' },
        { label: 'Notificaciones', href: '/financial-agent/notifications' }
      ]}
    >
      <div className="space-y-8">

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="glass-card p-6 rounded-xl text-center">
            <div className="text-3xl font-bold text-indigo-600">{stats.total_alerts}</div>
            <div className="text-gray-600">Total Alertas</div>
          </div>
          <div className="glass-card p-6 rounded-xl text-center">
            <div className="text-3xl font-bold text-red-600">{stats.critical_alerts}</div>
            <div className="text-gray-600">Críticas</div>
          </div>
          <div className="glass-card p-6 rounded-xl text-center">
            <div className="text-3xl font-bold text-green-600">€{stats.potential_savings?.toLocaleString()}</div>
            <div className="text-gray-600">Ahorro Potencial</div>
          </div>
          <div className="glass-card p-6 rounded-xl text-center">
            <div className="text-3xl font-bold text-orange-600">{stats.overdue_payments}</div>
            <div className="text-gray-600">Pagos Vencidos</div>
          </div>
        </div>
      )}

      <div className="glass-card p-6 rounded-xl">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Notificaciones Activas</h2>
          <div className="flex space-x-2">
            {['all', 'critical', 'warning', 'info'].map((filterType) => (
              <button
                key={filterType}
                onClick={() => setFilter(filterType as any)}
                className={`px-4 py-2 rounded-lg transition-all ${
                  filter === filterType
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {filterType === 'all' ? 'Todas' : filterType}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          {filteredNotifications.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🎉</div>
              <h3 className="text-xl font-semibold text-gray-600">¡No hay notificaciones!</h3>
              <p className="text-gray-500">Todo está funcionando correctamente</p>
            </div>
          ) : (
            filteredNotifications.map((notification) => (
              <div
                key={notification.id}
                className={`border-l-4 p-4 rounded-lg ${getNotificationColor(notification.type)} hover:shadow-lg transition-all cursor-pointer`}
                onClick={() => {
                  if (notification.property_id) {
                    router.push(`/financial-agent/property/${notification.property_id}`);
                  }
                }}
              >
                <div className="flex items-start space-x-3">
                  <div className="text-2xl">{getNotificationIcon(notification.type)}</div>
                  <div className="flex-1">
                    <div className="flex justify-between items-start">
                      <h3 className="font-semibold text-gray-800">{notification.title}</h3>
                      <span className="text-sm text-gray-500">
                        {new Date(notification.created_at).toLocaleDateString('es-ES')}
                      </span>
                    </div>
                    <p className="text-gray-600 mt-1">{notification.description}</p>
                    
                    {notification.amount && (
                      <div className="mt-2 text-sm">
                        <span className="font-medium">Importe: </span>
                        <span className="text-indigo-600">€{notification.amount.toLocaleString()}</span>
                      </div>
                    )}
                    
                    {notification.due_date && (
                      <div className="mt-1 text-sm">
                        <span className="font-medium">Vencimiento: </span>
                        <span className="text-orange-600">
                          {new Date(notification.due_date).toLocaleDateString('es-ES')}
                        </span>
                      </div>
                    )}
                    
                    {notification.actions && notification.actions.length > 0 && (
                      <div className="mt-3 flex space-x-2">
                        {notification.actions.map((action, index) => (
                          <button
                            key={index}
                            className="px-3 py-1 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700 transition-colors"
                          >
                            {action}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="flex justify-center space-x-4">
        <button
          onClick={() => router.push('/financial-agent')}
          className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
        >
          ← Volver al Dashboard
        </button>
        <button
          onClick={() => {
            fetchNotifications();
            fetchStats();
          }}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          🔄 Actualizar
        </button>
      </div>
      </div>
    </Layout>
  );
}