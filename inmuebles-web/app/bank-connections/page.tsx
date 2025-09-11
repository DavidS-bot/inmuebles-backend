"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, Building2, CreditCard, Plus, Trash2, RefreshCw, Settings } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface BankAccount {
  id: number;
  account_id: string;
  iban?: string;
  account_name?: string;
  account_type?: string;
  available_balance?: number;
  current_balance?: number;
  currency: string;
  last_transaction_sync?: string;
}

interface BankConnection {
  id: number;
  institution_name: string;
  institution_logo?: string;
  consent_status: string;
  is_active: boolean;
  created_at: string;
  last_sync?: string;
  sync_status: string;
  sync_error?: string;
  auto_sync_enabled: boolean;
  accounts: BankAccount[];
}

interface Institution {
  id: string;
  name: string;
  bic: string;
  transaction_total_days: string;
  countries: string[];
  logo: string;
}

export default function BankConnectionsPage() {
  const [connections, setConnections] = useState<BankConnection[]>([]);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState<number | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedInstitution, setSelectedInstitution] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadConnections();
    loadInstitutions();
  }, []);

  const loadConnections = async () => {
    try {
      const response = await api.get("/openbanking/connections");
      setConnections(response.data);
    } catch (error) {
      console.error("Error loading connections:", error);
      setError("Error cargando conexiones bancarias");
    } finally {
      setLoading(false);
    }
  };

  const loadInstitutions = async () => {
    try {
      const response = await api.get("/openbanking/institutions?country_code=ES");
      setInstitutions(response.data);
    } catch (error) {
      console.error("Error loading institutions:", error);
    }
  };

  const createConnection = async () => {
    if (!selectedInstitution) return;

    try {
      setLoading(true);
      const redirectUrl = `${window.location.origin}/bank-connections/callback`;
      
      const response = await api.post("/openbanking/connections", {
        institution_id: selectedInstitution,
        redirect_url: redirectUrl
      });

      // Redirigir al banco para el consentimiento
      window.location.href = response.data.consent_url;
    } catch (error) {
      console.error("Error creating connection:", error);
      setError("Error creando conexión bancaria");
      setLoading(false);
    }
  };

  const syncConnection = async (connectionId: number) => {
    try {
      setSyncing(connectionId);
      await api.post(`/openbanking/connections/${connectionId}/sync`, {
        days_back: 30
      });
      
      // Recargar conexiones para ver el estado actualizado
      await loadConnections();
    } catch (error) {
      console.error("Error syncing connection:", error);
      setError("Error sincronizando conexión");
    } finally {
      setSyncing(null);
    }
  };

  const deleteConnection = async (connectionId: number) => {
    if (!confirm("¿Estás seguro de que quieres eliminar esta conexión?")) return;

    try {
      await api.delete(`/openbanking/connections/${connectionId}`);
      await loadConnections();
    } catch (error) {
      console.error("Error deleting connection:", error);
      setError("Error eliminando conexión");
    }
  };

  const toggleAutoSync = async (connectionId: number, enabled: boolean) => {
    try {
      await api.post(`/openbanking/connections/${connectionId}/toggle-auto-sync`, {
        enabled
      });
      await loadConnections();
    } catch (error) {
      console.error("Error toggling auto sync:", error);
      setError("Error actualizando configuración");
    }
  };

  const getStatusBadge = (status: string) => {
    const statusMap = {
      "CR": { label: "Creado", variant: "secondary" as const },
      "GC": { label: "Dando Consentimiento", variant: "default" as const },
      "UA": { label: "Sin Autorizar", variant: "destructive" as const },
      "RJ": { label: "Rechazado", variant: "destructive" as const },
      "EX": { label: "Expirado", variant: "destructive" as const },
      "GA": { label: "Acceso Concedido", variant: "default" as const },
      "SA": { label: "Seleccionar Cuentas", variant: "default" as const },
      "LN": { label: "Conectado", variant: "default" as const }
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

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="h-8 w-8 animate-spin" />
          <span className="ml-2">Cargando conexiones bancarias...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Conexiones Bancarias</h1>
        <p className="text-gray-600">
          Conecta tus cuentas bancarias para importar transacciones automáticamente mediante Open Banking (PSD2).
        </p>
      </div>

      {error && (
        <Alert className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="mb-6">
        <Button onClick={() => setShowAddForm(!showAddForm)} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Conectar Nuevo Banco
        </Button>
      </div>

      {showAddForm && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Conectar Nuevo Banco</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Seleccionar Banco
                </label>
                <select
                  value={selectedInstitution}
                  onChange={(e) => setSelectedInstitution(e.target.value)}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="">Seleccionar banco...</option>
                  {institutions.map((institution) => (
                    <option key={institution.id} value={institution.id}>
                      {institution.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex gap-2">
                <Button onClick={createConnection} disabled={!selectedInstitution}>
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
                Conecta tu primer banco para comenzar a importar transacciones automáticamente.
              </p>
              <Button onClick={() => setShowAddForm(true)}>
                Conectar Primer Banco
              </Button>
            </CardContent>
          </Card>
        ) : (
          connections.map((connection) => (
            <Card key={connection.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {connection.institution_logo && (
                      <img
                        src={connection.institution_logo}
                        alt={connection.institution_name}
                        className="h-8 w-8 rounded"
                      />
                    )}
                    <div>
                      <CardTitle className="text-lg">{connection.institution_name}</CardTitle>
                      <div className="flex gap-2 mt-1">
                        {getStatusBadge(connection.consent_status)}
                        {getSyncStatusBadge(connection.sync_status, connection.sync_error)}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => syncConnection(connection.id)}
                      disabled={syncing === connection.id || connection.consent_status !== "LN"}
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
                      onClick={() => toggleAutoSync(connection.id, !connection.auto_sync_enabled)}
                    >
                      <Settings className="h-4 w-4" />
                      Auto-sync: {connection.auto_sync_enabled ? "ON" : "OFF"}
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
                      <span className="font-medium">Estado:</span>
                      <br />
                      {connection.is_active ? "Activo" : "Inactivo"}
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
                        Cuentas Bancarias
                      </h4>
                      <div className="grid gap-3">
                        {connection.accounts.map((account) => (
                          <div key={account.id} className="p-3 border rounded-lg bg-gray-50">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm">
                              <div>
                                <span className="font-medium">
                                  {account.account_name || account.iban || "Cuenta"}
                                </span>
                                {account.iban && (
                                  <div className="text-gray-600">{account.iban}</div>
                                )}
                              </div>
                              <div>
                                <span className="font-medium">Saldo Disponible:</span>
                                <br />
                                {formatBalance(account.available_balance, account.currency)}
                              </div>
                              <div>
                                <span className="font-medium">Saldo Actual:</span>
                                <br />
                                {formatBalance(account.current_balance, account.currency)}
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