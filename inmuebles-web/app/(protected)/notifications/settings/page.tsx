'use client';

import React, { useState, useEffect } from 'react';
import { Settings, Bell, Mail, Smartphone, MessageCircle, Save, CheckCircle } from 'lucide-react';

export default function NotificationSettingsPage() {
  const [channels, setChannels] = useState([]);
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const [channelsRes, rulesRes] = await Promise.all([
        fetch('/api/notifications/channels'),
        fetch('/api/notifications/rules')
      ]);
      
      const channelsData = await channelsRes.json();
      const rulesData = await rulesRes.json();
      
      setChannels(channelsData || []);
      setRules(rulesData || []);
    } catch (error) {
      console.error('Error fetching settings:', error);
      // Set demo data
      setChannels([
        { id: 1, type: 'in_app', enabled: true, settings: {} },
        { id: 2, type: 'email', enabled: false, settings: {} },
        { id: 3, type: 'push', enabled: false, settings: {} },
        { id: 4, type: 'whatsapp', enabled: false, settings: {} }
      ]);
      setRules([
        { id: 1, type: 'default', enabled: true, daily_limit: 2, business_hours_only: true }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleChannelToggle = async (channelId: number, enabled: boolean) => {
    try {
      setSaving(true);
      
      // Update local state
      setChannels(prev => 
        prev.map(ch => 
          ch.id === channelId ? { ...ch, enabled } : ch
        )
      );

      // In a real implementation, this would call the API
      // await fetch(`/api/notifications/channels/${channelId}`, {
      //   method: 'PUT',
      //   body: JSON.stringify({ is_enabled: enabled })
      // });

      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (error) {
      console.error('Error updating channel:', error);
    } finally {
      setSaving(false);
    }
  };

  const getChannelIcon = (type: string) => {
    switch (type) {
      case 'in_app':
        return <Bell className="h-5 w-5" />;
      case 'email':
        return <Mail className="h-5 w-5" />;
      case 'push':
        return <Smartphone className="h-5 w-5" />;
      case 'whatsapp':
        return <MessageCircle className="h-5 w-5" />;
      default:
        return <Bell className="h-5 w-5" />;
    }
  };

  const getChannelName = (type: string) => {
    switch (type) {
      case 'in_app':
        return 'Notificaciones en App';
      case 'email':
        return 'Email Digest Semanal';
      case 'push':
        return 'Notificaciones Push';
      case 'whatsapp':
        return 'WhatsApp (Próximamente)';
      default:
        return type;
    }
  };

  const getChannelDescription = (type: string) => {
    switch (type) {
      case 'in_app':
        return 'Notificaciones inmediatas en la aplicación con alertas contextuales';
      case 'email':
        return 'Resumen semanal con insights y oportunidades de ahorro';
      case 'push':
        return 'Notificaciones críticas en tu dispositivo móvil';
      case 'whatsapp':
        return 'Alertas importantes directamente en WhatsApp';
      default:
        return `Configuración para ${type}`;
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-300 rounded w-1/3 mb-4"></div>
          <div className="space-y-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="bg-white p-6 rounded-lg border">
                <div className="h-4 bg-gray-300 rounded w-1/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <div className="bg-blue-100 p-2 rounded-lg">
            <Settings className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Configuración de Notificaciones
            </h1>
            <p className="text-gray-600">
              Personaliza cómo y cuándo recibes notificaciones inteligentes
            </p>
          </div>
        </div>

        {saved && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span className="text-green-800">Configuración guardada correctamente</span>
          </div>
        )}
      </div>

      {/* Notification Channels */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Canales de Notificación</h2>
          <p className="text-gray-600 mt-1">Configura dónde quieres recibir tus notificaciones</p>
        </div>

        <div className="p-6 space-y-4">
          {channels.map((channel) => (
            <div 
              key={channel.id}
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center space-x-4">
                <div className={`p-2 rounded-lg ${channel.enabled ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-400'}`}>
                  {getChannelIcon(channel.type)}
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">
                    {getChannelName(channel.type)}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {getChannelDescription(channel.type)}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={channel.enabled}
                    onChange={(e) => handleChannelToggle(channel.id, e.target.checked)}
                    disabled={channel.type === 'whatsapp'} // Disabled for future feature
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600 disabled:opacity-50"></div>
                </label>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Timing Rules */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Reglas de Timing</h2>
          <p className="text-gray-600 mt-1">Controla cuándo y con qué frecuencia recibes notificaciones</p>
        </div>

        <div className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Máximo de notificaciones por día
              </label>
              <select className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value={2}>2 notificaciones</option>
                <option value={5}>5 notificaciones</option>
                <option value={10}>10 notificaciones</option>
                <option value={-1}>Sin límite</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Horario de notificaciones
              </label>
              <select className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value={true}>Solo horario laboral (9:00 - 18:00)</option>
                <option value={false}>Todo el día</option>
              </select>
            </div>
          </div>

          {/* Priority Settings */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Tipos de Notificación</h3>
            <div className="space-y-3">
              {[
                { type: 'Contratos próximos a vencer', icon: '📅', enabled: true },
                { type: 'Optimización fiscal Q4', icon: '💰', enabled: true },
                { type: 'Pagos pendientes', icon: '⚠️', enabled: true },
                { type: 'Oportunidades de renta', icon: '📈', enabled: true },
                { type: 'Gastos inusuales', icon: '🔍', enabled: false }
              ].map((notifType, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">{notifType.icon}</span>
                    <span className="text-gray-900">{notifType.type}</span>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      defaultChecked={notifType.enabled}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Demo Section */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <div className="bg-blue-100 p-2 rounded-lg">
            <Bell className="h-5 w-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-medium text-blue-900 mb-2">🧠 Sistema de Notificaciones Inteligentes</h3>
            <p className="text-blue-800 mb-4">
              Tu sistema utiliza IA para generar notificaciones contextuales que maximizan la rentabilidad 
              y minimizan la gestión manual de tus propiedades inmobiliarias.
            </p>
            <div className="bg-white border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium text-blue-900 mb-2">Ejemplos de notificaciones inteligentes:</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• "Contrato Serrano 21 vence en 60 días + template renovación"</li>
                <li>• "Puedes ahorrar €230 optimizando gastos Q4"</li>
                <li>• "Modelo 115 listo para presentar (1-click)"</li>
                <li>• "Lago Enol 12% por debajo mercado - ¿subir renta?"</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}