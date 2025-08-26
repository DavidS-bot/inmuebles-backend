'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import Layout from '@/components/Layout';

interface BankiterConfig {
  username: string;
  password: string;
  api_key?: string;
  auto_sync: boolean;
  sync_frequency: string;
}

interface BankAccount {
  account_number: string;
  account_name: string;
  balance: number;
}

interface ConnectionStatus {
  success: boolean;
  method?: string;
  accounts_found?: number;
  accounts?: BankAccount[];
  error?: string;
}

interface BankiterStatus {
  integration: string;
  status: string;
  connection_method: string;
  last_sync: string;
  accounts_connected: number;
  transactions_imported: number;
  features: {
    statement_download: boolean;
    automatic_sync: boolean;
    transaction_categorization: boolean;
    balance_monitoring: boolean;
    csv_export: boolean;
  };
}

export default function BankinterIntegrationPage() {
  const [config, setConfig] = useState<BankiterConfig>({
    username: '',
    password: '',
    api_key: '',
    auto_sync: true,
    sync_frequency: 'daily'
  });
  
  const [status, setStatus] = useState<BankiterStatus | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [activeTab, setActiveTab] = useState<'setup' | 'status' | 'download' | 'settings'>('setup');
  
  const router = useRouter();

  useEffect(() => {
    fetchBankiterStatus();
  }, []);

  const fetchBankiterStatus = async () => {
    try {
      const response = await api.get('/integrations/bankinter/status');
      setStatus(response.data);
    } catch (error) {
      console.error('Error fetching Bankinter status:', error);
    }
  };

  const handleTestConnection = async () => {
    if (!config.username || !config.password) {
      alert('Por favor, introduce usuario y contraseña');
      return;
    }

    setTesting(true);
    try {
      const response = await api.post('/integrations/bankinter/test-connection', {
        username: config.username,
        password: config.password,
        api_key: config.api_key || null
      });
      
      setConnectionStatus(response.data);
    } catch (error: any) {
      setConnectionStatus({
        success: false,
        error: error.response?.data?.detail || 'Error de conexión'
      });
    } finally {
      setTesting(false);
    }
  };

  const handleConnect = async () => {
    if (!config.username || !config.password) {
      alert('Por favor, introduce usuario y contraseña');
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/integrations/bankinter/connect', config);
      
      if (response.data.success) {
        alert('[OK] Conexión establecida exitosamente');
        await fetchBankiterStatus();
        setActiveTab('status');
      } else {
        alert(`[ERROR] Error: ${response.data.error}`);
      }
    } catch (error: any) {
      alert(`[ERROR] Error: ${error.response?.data?.detail || 'Error de conexión'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!config.username || !config.password) {
      alert('Por favor, introduce usuario y contraseña');
      return;
    }

    setDownloading(true);
    try {
      const response = await api.post('/integrations/bankinter/download', {
        username: config.username,
        password: config.password,
        days_back: 90,
        auto_categorize: true,
        import_to_system: true
      });

      if (response.data.success) {
        alert(`[OK] Descarga completada: ${response.data.summary.transactions_downloaded} transacciones`);
        // Mostrar resumen
        console.log('Download summary:', response.data);
      }
    } catch (error: any) {
      alert(`[ERROR] Error: ${error.response?.data?.detail || 'Error en descarga'}`);
    } finally {
      setDownloading(false);
    }
  };

  const handleSyncNow = async () => {
    try {
      const response = await api.post('/integrations/bankinter/sync-now');
      alert(`[SYNC] ${response.data.message}`);
    } catch (error: any) {
      alert(`[ERROR] Error: ${error.response?.data?.detail || 'Error de sincronización'}`);
    }
  };

  return (
    <Layout
      title="Integración con Bankinter"
      subtitle="Conecta tu cuenta de Bankinter para descargar extractos automáticamente"
      breadcrumbs={[
        { label: 'Agente Financiero', href: '/financial-agent' },
        { label: 'Integraciones', href: '/financial-agent/integrations' },
        { label: 'Bankinter', href: '/financial-agent/integrations/bankinter' }
      ]}
    >
      <div className="space-y-8">

      {/* Navigation Tabs */}
      <div className="flex justify-center space-x-2 mb-8">
        {[
          { key: 'setup', label: 'Configuración', icon: '[CONFIG]' },
          { key: 'status', label: 'Estado', icon: '[STATUS]' },
          { key: 'download', label: 'Descargar', icon: '[DOWN]' },
          { key: 'settings', label: 'Ajustes', icon: '[SET]' }
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`px-6 py-3 rounded-lg transition-all flex items-center space-x-2 ${
              activeTab === tab.key
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Setup Tab */}
      {activeTab === 'setup' && (
        <div className="max-w-2xl mx-auto">
          <div className="glass-card p-8 rounded-xl">
            <h2 className="text-2xl font-bold mb-6">[BANK] Configurar Conexión</h2>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Usuario Bankinter
                </label>
                <input
                  type="text"
                  value={config.username}
                  onChange={(e) => setConfig({...config, username: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Tu nombre de usuario"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contraseña
                </label>
                <input
                  type="password"
                  value={config.password}
                  onChange={(e) => setConfig({...config, password: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Tu contraseña"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Clave API PSD2 (Opcional)
                </label>
                <input
                  type="text"
                  value={config.api_key}
                  onChange={(e) => setConfig({...config, api_key: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Opcional: Para acceso via API"
                />
                <p className="text-sm text-gray-500 mt-1">
                  Si tienes una clave PSD2, se utilizará preferentemente sobre web scraping
                </p>
              </div>

              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  checked={config.auto_sync}
                  onChange={(e) => setConfig({...config, auto_sync: e.target.checked})}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="text-sm text-gray-700">
                  Sincronización automática
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Frecuencia de sincronización
                </label>
                <select
                  value={config.sync_frequency}
                  onChange={(e) => setConfig({...config, sync_frequency: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="daily">Diaria</option>
                  <option value="weekly">Semanal</option>
                  <option value="manual">Manual</option>
                </select>
              </div>

              {/* Connection Test */}
              <div className="border-t pt-6">
                <button
                  onClick={handleTestConnection}
                  disabled={testing}
                  className="w-full mb-4 bg-yellow-600 text-white px-6 py-3 rounded-lg hover:bg-yellow-700 disabled:opacity-50 transition-colors"
                >
                  {testing ? '[LOADING] Probando conexión...' : '[TEST] Probar Conexión'}
                </button>

                {connectionStatus && (
                  <div className={`p-4 rounded-lg ${connectionStatus.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                    {connectionStatus.success ? (
                      <div>
                        <h3 className="font-semibold text-green-800">[OK] Conexión exitosa</h3>
                        <p className="text-green-700">Método: {connectionStatus.method}</p>
                        <p className="text-green-700">Cuentas encontradas: {connectionStatus.accounts_found}</p>
                        {connectionStatus.accounts && (
                          <div className="mt-2">
                            <h4 className="font-medium">Cuentas:</h4>
                            {connectionStatus.accounts.map((acc, idx) => (
                              <div key={idx} className="text-sm text-green-600">
                                {acc.account_name}: {acc.account_number} (€{acc.balance.toFixed(2)})
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ) : (
                      <div>
                        <h3 className="font-semibold text-red-800">[ERROR] Error de conexión</h3>
                        <p className="text-red-700">{connectionStatus.error}</p>
                      </div>
                    )}
                  </div>
                )}

                <button
                  onClick={handleConnect}
                  disabled={loading}
                  className="w-full mt-4 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {loading ? '[LOADING] Configurando...' : '[SAVE] Guardar Configuración'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Status Tab */}
      {activeTab === 'status' && status && (
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="glass-card p-6 rounded-xl">
              <h3 className="text-lg font-semibold mb-4">[CONN] Estado de Conexión</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span>Estado:</span>
                  <span className={`font-semibold ${status.status === 'configured' ? 'text-green-600' : 'text-red-600'}`}>
                    {status.status === 'configured' ? '[OK] Configurado' : '[ERROR] No configurado'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Método:</span>
                  <span>{status.connection_method}</span>
                </div>
                <div className="flex justify-between">
                  <span>Última sincronización:</span>
                  <span>{new Date(status.last_sync).toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Cuentas conectadas:</span>
                  <span>{status.accounts_connected}</span>
                </div>
              </div>
            </div>

            <div className="glass-card p-6 rounded-xl">
              <h3 className="text-lg font-semibold mb-4">[STATS] Estadísticas</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span>Transacciones importadas:</span>
                  <span className="font-semibold">{status.transactions_imported}</span>
                </div>
                <div className="flex justify-between">
                  <span>Frecuencia sync:</span>
                  <span>{status.sync_frequency}</span>
                </div>
                <div className="flex justify-between">
                  <span>Auto-categorización:</span>
                  <span className={status.auto_categorization ? 'text-green-600' : 'text-red-600'}>
                    {status.auto_categorization ? '[ON] Activa' : '[OFF] Inactiva'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Features */}
          <div className="glass-card p-6 rounded-xl mb-6">
            <h3 className="text-lg font-semibold mb-4">[FEATURES] Funcionalidades</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(status.features).map(([key, enabled]) => (
                <div key={key} className="flex items-center space-x-2">
                  <span className={enabled ? 'text-green-600' : 'text-gray-400'}>
                    {enabled ? '[ON]' : '[OFF]'}
                  </span>
                  <span className="text-sm capitalize">{key.replace('_', ' ')}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-center space-x-4">
            <button
              onClick={handleSyncNow}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              [SYNC] Sincronizar Ahora
            </button>
          </div>
        </div>
      )}

      {/* Download Tab */}
      {activeTab === 'download' && (
        <div className="max-w-2xl mx-auto">
          <div className="glass-card p-8 rounded-xl">
            <h2 className="text-2xl font-bold mb-6">[DOWNLOAD] Descargar Extractos</h2>
            
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-800 mb-2">[INFO] Opciones de Descarga</h3>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Descargará los últimos 90 días de movimientos</li>
                  <li>• Las transacciones se categorizarán automáticamente</li>
                  <li>• Se importarán directamente al sistema</li>
                  <li>• Se generará un archivo CSV como respaldo</li>
                </ul>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Usuario Bankinter
                </label>
                <input
                  type="text"
                  value={config.username}
                  onChange={(e) => setConfig({...config, username: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Tu nombre de usuario"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contraseña
                </label>
                <input
                  type="password"
                  value={config.password}
                  onChange={(e) => setConfig({...config, password: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Tu contraseña"
                />
              </div>

              <button
                onClick={handleDownload}
                disabled={downloading || !config.username || !config.password}
                className="w-full bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                {downloading ? '[LOADING] Descargando extractos...' : '[DOWNLOAD] Descargar Extractos'}
              </button>

              {downloading && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-yellow-800">
                    [LOADING] Descargando datos de Bankinter... Esto puede tardar unos minutos.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Settings Tab */}
      {activeTab === 'settings' && (
        <div className="max-w-2xl mx-auto">
          <div className="glass-card p-8 rounded-xl">
            <h2 className="text-2xl font-bold mb-6">[SETTINGS] Configuración Avanzada</h2>
            
            <div className="space-y-6">
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold mb-2">[SECURITY] Seguridad</h3>
                <p className="text-sm text-gray-600 mb-3">
                  Tus credenciales se almacenan de forma encriptada y solo se usan para conectar con Bankinter.
                </p>
                <button className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 text-sm">
                  [DELETE] Eliminar Credenciales Guardadas
                </button>
              </div>

              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold mb-2">[DATA] Datos</h3>
                <p className="text-sm text-gray-600 mb-3">
                  Gestiona los datos importados desde Bankinter.
                </p>
                <div className="flex space-x-2">
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm">
                    [EXPORT] Exportar Datos
                  </button>
                  <button className="bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 text-sm">
                    [REPROCESS] Reprocessar Categorías
                  </button>
                </div>
              </div>

              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold mb-2">[AUTO] Automatización</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Sincronización automática</span>
                    <input type="checkbox" defaultChecked className="h-4 w-4" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Notificaciones por email</span>
                    <input type="checkbox" className="h-4 w-4" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Auto-categorización</span>
                    <input type="checkbox" defaultChecked className="h-4 w-4" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Back Button */}
      <div className="flex justify-center">
        <button
          onClick={() => router.push('/financial-agent/integrations')}
          className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
        >
          ← Volver a Integraciones
        </button>
      </div>
      </div>
    </Layout>
  );
}