"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, Building2, CreditCard, Plus, Trash2, RefreshCw, Settings, CheckCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface BankAccount {
  id: string;
  name: string;
  type: string;
  balance: number;
  currencyCode: string;
  identifiers?: {
    iban?: {
      iban: string;
    };
  };
  availableBalance?: number;
  refreshed?: string;
}

interface BankConnection {
  id: number;
  provider_name: string;
  institution_name: string;
  status: string;
  is_active: boolean;
  created_at: string;
  last_sync?: string;
  sync_status: string;
  sync_error?: string;
  accounts: BankAccount[];
}

interface TinkProvider {
  name: string;
  displayName: string;
  type: string;
  status: string;
  credentialsType: string;
  helpText?: string;
  popular?: boolean;
  transactionDaysRange?: number;
}

export default function OpenBankingPage() {
  const [connections, setConnections] = useState<BankConnection[]>([]);
  const [providers, setProviders] = useState<TinkProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState<number | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadConnections();
    loadProviders();
  }, []);

  const loadConnections = async () => {
    try {
      const response = await api.get("/openbanking-tink/connections");
      setConnections(response.data);
    } catch (error: any) {
      console.error("Error loading connections:", error);
      if (error.response?.status !== 404) {
        setError("Error cargando conexiones bancarias");
      }
    } finally {
      setLoading(false);
    }
  };

  const loadProviders = async () => {
    try {
      const response = await api.get("/openbanking-tink/providers?country_code=ES");
      setProviders(response.data);
    } catch (error: any) {
      console.error("Error loading providers:", error);
      setError("Error cargando bancos disponibles");
    }
  };

  const createConnection = async () => {
    if (!selectedProvider) return;

    try {
      setLoading(true);
      setError(null);
      
      const redirectUrl = `${window.location.origin}/bank-connections/callback`;
      
      const response = await api.post("/openbanking-tink/connections", {
        provider_name: selectedProvider,
        redirect_url: redirectUrl
      });

      if (response.data.link_url) {
        // Redirigir al banco para el consentimiento
        window.location.href = response.data.link_url;
      } else {
        setSuccess("Conexión creada exitosamente para datos demo");
        setShowAddForm(false);
        await loadConnections();
      }
    } catch (error: any) {
      console.error("Error creating connection:", error);
      setError(error.response?.data?.detail || "Error creando conexión bancaria");
      setLoading(false);
    }
  };

  const syncConnection = async (connectionId: number) => {
    try {
      setSyncing(connectionId);
      setError(null);
      
      await api.post(`/openbanking-tink/connections/${connectionId}/sync`);
      
      setSuccess("Sincronización iniciada exitosamente");
      // Recargar conexiones para ver el estado actualizado
      await loadConnections();
    } catch (error: any) {
      console.error("Error syncing connection:", error);
      setError(error.response?.data?.detail || "Error sincronizando conexión");
    } finally {
      setSyncing(null);
    }
  };

  const deleteConnection = async (connectionId: number) => {
    if (!confirm("¿Estás seguro de que quieres eliminar esta conexión?")) return;

    try {
      await api.delete(`/openbanking-tink/connections/${connectionId}`);
      await loadConnections();
      setSuccess("Conexión eliminada exitosamente");
    } catch (error: any) {
      console.error("Error deleting connection:", error);
      setError(error.response?.data?.detail || "Error eliminando conexión");
    }
  };

  const getStatusBadge = (status: string) => {
    const statusMap = {
      "ACTIVE": { label: "Activo", variant: "default" as const },
      "INACTIVE": { label: "Inactivo", variant: "secondary" as const },
      "PENDING": { label: "Pendiente", variant: "default" as const },
      "ERROR": { label: "Error", variant: "destructive" as const },
      "EXPIRED": { label: "Expirado", variant: "destructive" as const }
    };

    const config = statusMap[status as keyof typeof statusMap] || { label: status, variant: "secondary" as const };
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const getSyncStatusBadge = (status: string, error?: string) => {
    if (error) {
      return <Badge variant="destructive" title={error}>Error</Badge>;
    }

    const statusMap = {
      "PENDING": { label: "Pendiente", variant: "secondary" as const },
      "SYNCING": { label: "Sincronizando...", variant: "default" as const },
      "SUCCESS": { label: "Exitoso", variant: "default" as const },
      "COMPLETED": { label: "Completado", variant: "default" as const },
      "ERROR": { label: "Error", variant: "destructive" as const }
    };

    const config = statusMap[status as keyof typeof statusMap] || { label: status, variant: "secondary" as const };
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const formatBalance = (balance?: number, currency: string = "EUR") => {
    if (balance === undefined || balance === null) return "N/A";
    return new Intl.NumberFormat("es-ES", {
      style: "currency",
      currency: currency
    }).format(balance);
  };

  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="h-8 w-8 animate-spin" />
          <span className="ml-2">Cargando Open Banking...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Open Banking - Tink</h1>
        <p className="text-gray-600">
          Conecta tus cuentas bancarias usando Tink Open Banking para importar transacciones automáticamente.
        </p>
        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center gap-2 text-blue-800">
            <AlertCircle className="h-4 w-4" />
            <span className="font-medium">Modo Sandbox/Demo</span>
          </div>
          <p className="text-blue-700 text-sm mt-1">
            Actualmente estás en modo sandbox. Los bancos mostrados contienen datos demo para pruebas.
          </p>
        </div>
      </div>

      {error && (
        <Alert className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="flex justify-between items-center">
            {error}
            <Button variant="ghost" size="sm" onClick={clearMessages}>×</Button>
          </AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="mb-6 border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="flex justify-between items-center text-green-800">
            {success}
            <Button variant="ghost" size="sm" onClick={clearMessages}>×</Button>
          </AlertDescription>
        </Alert>
      )}

      <div className="mb-6">
        <Button onClick={() => setShowAddForm(!showAddForm)} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Conectar Banco Demo
        </Button>
      </div>

      {showAddForm && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Conectar Banco Demo - Tink</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Seleccionar Banco Demo
                </label>
                <select
                  value={selectedProvider}
                  onChange={(e) => setSelectedProvider(e.target.value)}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="">Seleccionar banco demo...</option>
                  {providers.map((provider) => (
                    <option key={provider.name} value={provider.name}>
                      {provider.displayName}
                      {provider.popular && " ⭐"}
                    </option>
                  ))}
                </select>
              </div>
              
              {selectedProvider && (
                <div className="p-3 bg-gray-50 rounded-md">
                  {providers.find(p => p.name === selectedProvider)?.helpText && (
                    <p className="text-sm text-gray-600">
                      {providers.find(p => p.name === selectedProvider)?.helpText}
                    </p>
                  )}
                </div>
              )}

              <div className="flex gap-2">
                <Button onClick={createConnection} disabled={!selectedProvider}>
                  Conectar
                </Button>
                <Button variant="outline" onClick={() => setShowAddForm(false)}>
                  Cancelar
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6">
        {connections.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <Building2 className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-medium mb-2">No hay conexiones bancarias</h3>
              <p className="text-gray-600 mb-4">
                Conecta tu primer banco demo para comenzar a probar la funcionalidad de Open Banking.
              </p>
              <Button onClick={() => setShowAddForm(true)}>
                Conectar Primer Banco Demo
              </Button>
            </CardContent>
          </Card>
        ) : (
          connections.map((connection) => (
            <Card key={connection.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Building2 className="h-8 w-8 text-blue-600" />
                    <div>
                      <CardTitle className="text-lg">{connection.institution_name}</CardTitle>
                      <div className="flex gap-2 mt-1">
                        {getStatusBadge(connection.status)}
                        {getSyncStatusBadge(connection.sync_status, connection.sync_error)}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => syncConnection(connection.id)}
                      disabled={syncing === connection.id}
                    >
                      {syncing === connection.id ? (
                        <RefreshCw className="h-4 w-4 animate-spin" />
                      ) : (
                        <RefreshCw className="h-4 w-4" />
                      )}
                      Sincronizar
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => deleteConnection(connection.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Proveedor:</span>
                      <br />
                      {connection.provider_name}
                    </div>
                    <div>
                      <span className="font-medium">Creado:</span>
                      <br />
                      {new Date(connection.created_at).toLocaleDateString("es-ES")}
                    </div>
                    <div>
                      <span className="font-medium">Última Sync:</span>
                      <br />
                      {connection.last_sync 
                        ? new Date(connection.last_sync).toLocaleDateString("es-ES")
                        : "Nunca"
                      }
                    </div>
                    <div>
                      <span className="font-medium">Cuentas:</span>
                      <br />
                      {connection.accounts.length}
                    </div>
                  </div>

                  {connection.accounts.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-3 flex items-center gap-2">
                        <CreditCard className="h-4 w-4" />
                        Cuentas Bancarias Demo
                      </h4>
                      <div className="grid gap-3">
                        {connection.accounts.map((account) => (
                          <div key={account.id} className="p-3 border rounded-lg bg-gray-50">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm">
                              <div>
                                <span className="font-medium">
                                  {account.name}
                                </span>
                                <div className="text-gray-600">
                                  {account.type} • {account.currencyCode}
                                </div>
                                {account.identifiers?.iban?.iban && (
                                  <div className="text-gray-600 text-xs">
                                    {account.identifiers.iban.iban}
                                  </div>
                                )}
                              </div>
                              <div>
                                <span className="font-medium">Saldo:</span>
                                <br />
                                {formatBalance(account.balance, account.currencyCode)}
                              </div>
                              <div>
                                <span className="font-medium">Disponible:</span>
                                <br />
                                {formatBalance(account.availableBalance, account.currencyCode)}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {connection.sync_error && (
                    <Alert>
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription>
                        <span className="font-medium">Error de sincronización:</span>
                        <br />
                        {connection.sync_error}
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}