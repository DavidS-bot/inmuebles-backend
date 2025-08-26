'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';

interface Integration {
  id: string;
  name: string;
  type: 'bank' | 'insurance' | 'market' | 'utility' | 'tax';
  status: 'connected' | 'disconnected' | 'error' | 'pending';
  last_sync: string;
  description: string;
  features: string[];
}

interface MarketData {
  property_id: number;
  address: string;
  estimated_value: number;
  market_trend: 'up' | 'down' | 'stable';
  price_change: number;
  comparable_sales: number;
}

interface BankTransaction {
  id: string;
  date: string;
  description: string;
  amount: number;
  type: 'income' | 'expense';
  category: string;
  property_related: boolean;
}

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [bankTransactions, setBankTransactions] = useState<BankTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'market' | 'banking' | 'setup'>('overview');
  const [connecting, setConnecting] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetchIntegrationsData();
  }, []);

  const fetchIntegrationsData = async () => {
    setLoading(true);
    try {
      const [integrationsRes, marketRes, bankingRes] = await Promise.all([
        fetch('http://localhost:8000/integrations/status'),
        fetch('http://localhost:8000/integrations/market-prices'),
        fetch('http://localhost:8000/integrations/bank-sync')
      ]);

      const integrationsData = await integrationsRes.json();
      const marketDataRes = await marketRes.json();
      const bankingData = await bankingRes.json();

      setIntegrations(integrationsData.integrations || []);
      setMarketData(marketDataRes.market_data || []);
      setBankTransactions(bankingData.transactions || []);
    } catch (error) {
      console.error('Error fetching integrations data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (serviceId: string) => {
    // Redirector especial para Bankinter
    if (serviceId === 'bankinter') {
      router.push('/financial-agent/integrations/bankinter');
      return;
    }

    setConnecting(serviceId);
    try {
      const response = await fetch(`http://localhost:8000/integrations/connect/${serviceId}`, {
        method: 'POST',
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`✅ ${result.message}\n\nCaracterísticas activadas:\n${result.features_enabled.join('\n')}`);
        
        // Actualizar el estado de las integraciones
        setIntegrations(prev => prev.map(integration => 
          integration.id === serviceId 
            ? { ...integration, status: 'connected' as const, last_sync: new Date().toISOString() }
            : integration
        ));
      } else {
        alert('Error al conectar con el servicio');
      }
    } catch (error) {
      console.error('Error connecting:', error);
      alert('Error de conexión');
    } finally {
      setConnecting(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'bg-green-100 text-green-800 border-green-300';
      case 'disconnected': return 'bg-gray-100 text-gray-800 border-gray-300';
      case 'error': return 'bg-red-100 text-red-800 border-red-300';
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'bank': return '🏦';
      case 'insurance': return '🛡️';
      case 'market': return '📈';
      case 'utility': return '⚡';
      case 'tax': return '📊';
      default: return '🔗';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return '📈';
      case 'down': return '📉';
      case 'stable': return '➡️';
      default: return '❓';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen p-8 flex items-center justify-center">
        <div className="glass-card p-8 rounded-xl">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="text-center mt-4 text-gray-600">Cargando integraciones...</p>
        </div>
      </div>
    );
  }

  return (
    <Layout
      title="Integraciones Externas"
      subtitle="Conecta con bancos, mercados y servicios externos"
    >
      <div className="space-y-8">

      <div className="flex justify-center space-x-2 mb-8">
        {[
          { key: 'overview', label: 'Resumen', icon: '🔗' },
          { key: 'market', label: 'Mercado', icon: '📈' },
          { key: 'banking', label: 'Banca', icon: '🏦' },
          { key: 'setup', label: 'Configuración', icon: '⚙️' }
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`px-6 py-3 rounded-lg transition-all flex items-center space-x-2 ${
              activeTab === tab.key
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="glass-card p-6 rounded-xl text-center">
              <div className="text-3xl font-bold text-green-600">
                {integrations.filter(i => i.status === 'connected').length}
              </div>
              <div className="text-gray-600">Conectadas</div>
            </div>
            <div className="glass-card p-6 rounded-xl text-center">
              <div className="text-3xl font-bold text-yellow-600">
                {integrations.filter(i => i.status === 'pending').length}
              </div>
              <div className="text-gray-600">Pendientes</div>
            </div>
            <div className="glass-card p-6 rounded-xl text-center">
              <div className="text-3xl font-bold text-red-600">
                {integrations.filter(i => i.status === 'error').length}
              </div>
              <div className="text-gray-600">Con Errores</div>
            </div>
          </div>

          <div className="glass-card p-6 rounded-xl">
            <h2 className="text-2xl font-bold mb-6">Estado de Integraciones</h2>
            <div className="space-y-4">
              {integrations.map((integration) => (
                <div key={integration.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl">{getTypeIcon(integration.type)}</div>
                      <div>
                        <h3 className="font-semibold text-gray-800">{integration.name}</h3>
                        <p className="text-gray-600 text-sm">{integration.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className={`px-3 py-1 rounded-full text-sm border ${getStatusColor(integration.status)}`}>
                        {integration.status}
                      </span>
                      <button 
                        onClick={() => integration.status === 'connected' ? null : handleConnect(integration.id)}
                        disabled={connecting === integration.id || integration.status === 'connected'}
                        className={`px-4 py-2 text-white rounded transition-colors ${
                          integration.status === 'connected' 
                            ? 'bg-gray-400 cursor-not-allowed'
                            : connecting === integration.id
                            ? 'bg-yellow-500'
                            : 'bg-indigo-600 hover:bg-indigo-700'
                        }`}
                      >
                        {connecting === integration.id ? 'Conectando...' : 
                         integration.status === 'connected' ? 'Conectado' : 'Configurar'}
                      </button>
                    </div>
                  </div>
                  <div className="mt-3 text-sm text-gray-500">
                    Última sincronización: {new Date(integration.last_sync).toLocaleString('es-ES')}
                  </div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {integration.features.map((feature, index) => (
                      <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'market' && (
        <div className="space-y-6">
          <div className="glass-card p-6 rounded-xl">
            <h2 className="text-2xl font-bold mb-6">Valoración de Mercado</h2>
            <div className="space-y-4">
              {marketData.map((property) => (
                <div key={property.property_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-800">{property.address}</h3>
                      <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Valor estimado:</span>
                          <div className="font-semibold text-indigo-600">€{property.estimated_value.toLocaleString()}</div>
                        </div>
                        <div>
                          <span className="text-gray-600">Tendencia:</span>
                          <div className="flex items-center space-x-1">
                            <span>{getTrendIcon(property.market_trend)}</span>
                            <span className="font-semibold">{property.market_trend}</span>
                          </div>
                        </div>
                        <div>
                          <span className="text-gray-600">€/m²:</span>
                          <div className="font-semibold text-indigo-600">€{property.price_per_sqm.toLocaleString()}</div>
                        </div>
                        <div>
                          <span className="text-gray-600">Confianza:</span>
                          <div className="font-semibold">{property.confidence_level}</div>
                        </div>
                      </div>
                    </div>
                    <button className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition-colors ml-4">
                      Ver Detalles
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'banking' && (
        <div className="space-y-6">
          <div className="glass-card p-6 rounded-xl">
            <h2 className="text-2xl font-bold mb-6">Transacciones Bancarias</h2>
            <div className="space-y-3">
              {bankTransactions.map((transaction) => (
                <div key={transaction.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-center">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className={`w-3 h-3 rounded-full ${transaction.type === 'income' ? 'bg-green-500' : 'bg-red-500'}`}></span>
                        <h3 className="font-semibold text-gray-800">{transaction.description}</h3>
                        {transaction.property_related && (
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">Propiedad</span>
                        )}
                      </div>
                      <div className="mt-1 text-sm text-gray-600">
                        {new Date(transaction.date).toLocaleDateString('es-ES')} • {transaction.category}
                      </div>
                    </div>
                    <div className={`text-lg font-bold ${transaction.type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                      {transaction.type === 'income' ? '+' : '-'}€{Math.abs(transaction.amount).toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'setup' && (
        <div className="space-y-6">
          <div className="glass-card p-6 rounded-xl">
            <h2 className="text-2xl font-bold mb-6">Configuración de Integraciones</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-indigo-600">🏦 Integraciones Bancarias</h3>
                <div className="space-y-3">
                  {[
                    { id: 'bankinter', name: 'Bankinter', featured: true },
                    { id: 'santander', name: 'Santander' },
                    { id: 'bbva', name: 'BBVA' },
                    { id: 'caixabank', name: 'CaixaBank' },
                    { id: 'sabadell', name: 'Sabadell' }
                  ].map((bank: {id: string, name: string, featured?: boolean}) => (
                    <div key={bank.id} className={`flex justify-between items-center p-3 border rounded-lg ${
                      bank.featured ? 'border-blue-300 bg-blue-50' : ''
                    }`}>
                      <div className="flex items-center space-x-2">
                        <span className="font-medium">{bank.name}</span>
                        {bank.featured && <span className="text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded">Disponible</span>}
                      </div>
                      <button 
                        onClick={() => handleConnect(bank.id)}
                        disabled={connecting === bank.id}
                        className={`px-4 py-2 text-white rounded transition-colors ${
                          connecting === bank.id ? 'bg-yellow-500' : 
                          bank.featured ? 'bg-blue-600 hover:bg-blue-700' :
                          'bg-gray-400 cursor-not-allowed'
                        }`}
                      >
                        {connecting === bank.id ? 'Conectando...' : 
                         bank.featured ? 'Configurar' : 'Próximamente'}
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-green-600">📈 Servicios de Mercado</h3>
                <div className="space-y-3">
                  {[
                    { id: 'idealista', name: 'Idealista' },
                    { id: 'fotocasa', name: 'Fotocasa' },
                    { id: 'habitaclia', name: 'Habitaclia' },
                    { id: 'pisos', name: 'Pisos.com' }
                  ].map((service) => (
                    <div key={service.id} className="flex justify-between items-center p-3 border rounded-lg">
                      <span className="font-medium">{service.name}</span>
                      <button 
                        onClick={() => handleConnect(service.id)}
                        disabled={connecting === service.id}
                        className={`px-4 py-2 text-white rounded transition-colors ${
                          connecting === service.id ? 'bg-yellow-500' : 'bg-green-600 hover:bg-green-700'
                        }`}
                      >
                        {connecting === service.id ? 'Conectando...' : 'Conectar'}
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-purple-600">🛡️ Seguros</h3>
                <div className="space-y-3">
                  {[
                    { id: 'mapfre', name: 'Mapfre' },
                    { id: 'mutua', name: 'Mutua Madrileña' },
                    { id: 'allianz', name: 'Allianz' },
                    { id: 'axa', name: 'AXA' }
                  ].map((insurance) => (
                    <div key={insurance.id} className="flex justify-between items-center p-3 border rounded-lg">
                      <span className="font-medium">{insurance.name}</span>
                      <button 
                        onClick={() => handleConnect(insurance.id)}
                        disabled={connecting === insurance.id}
                        className={`px-4 py-2 text-white rounded transition-colors ${
                          connecting === insurance.id ? 'bg-yellow-500' : 'bg-purple-600 hover:bg-purple-700'
                        }`}
                      >
                        {connecting === insurance.id ? 'Conectando...' : 'Conectar'}
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-orange-600">📊 Servicios Fiscales</h3>
                <div className="space-y-3">
                  {[
                    { id: 'aeat', name: 'AEAT' },
                    { id: 'gestoria', name: 'Gestoría Digital' },
                    { id: 'taxdown', name: 'TaxDown' },
                    { id: 'declarando', name: 'Declarando' }
                  ].map((service) => (
                    <div key={service.id} className="flex justify-between items-center p-3 border rounded-lg">
                      <span className="font-medium">{service.name}</span>
                      <button 
                        onClick={() => handleConnect(service.id)}
                        disabled={connecting === service.id}
                        className={`px-4 py-2 text-white rounded transition-colors ${
                          connecting === service.id ? 'bg-yellow-500' : 'bg-orange-600 hover:bg-orange-700'
                        }`}
                      >
                        {connecting === service.id ? 'Conectando...' : 'Conectar'}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="glass-card p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-4">🔒 Configuración de Seguridad</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <span className="font-medium">Autenticación de dos factores</span>
                  <p className="text-sm text-gray-600">Protege tus integraciones con 2FA</p>
                </div>
                <button className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition-colors">
                  Activar
                </button>
              </div>
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <span className="font-medium">Cifrado de extremo a extremo</span>
                  <p className="text-sm text-gray-600">Datos protegidos en tránsito y reposo</p>
                </div>
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded text-sm">Activo</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-center space-x-4">
        <button
          onClick={() => router.push('/financial-agent')}
          className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
        >
          ← Volver al Dashboard
        </button>
        <button
          onClick={fetchIntegrationsData}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          🔄 Sincronizar
        </button>
        <button
          className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          ➕ Nueva Integración
        </button>
      </div>
      </div>
    </Layout>
  );
}