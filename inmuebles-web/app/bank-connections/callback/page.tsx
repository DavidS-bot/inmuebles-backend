"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import api from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle, XCircle, Loader2, AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function BankConnectionCallback() {
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");
  const [details, setDetails] = useState<any>(null);
  const searchParams = useSearchParams();
  const router = useRouter();

  useEffect(() => {
    processCallback();
  }, []);

  const processCallback = async () => {
    try {
      // Obtener parámetros de la URL
      const ref = searchParams.get("ref");
      const error = searchParams.get("error");

      if (error) {
        setStatus("error");
        setMessage(`Error en el consentimiento: ${error}`);
        return;
      }

      if (!ref) {
        setStatus("error");
        setMessage("Referencia de conexión no encontrada en la URL");
        return;
      }

      // Buscar la conexión por referencia (ref contiene el requisition reference)
      const connectionsResponse = await api.get("/openbanking/connections");
      const connections = connectionsResponse.data;
      
      const connection = connections.find((conn: any) => 
        conn.requisition_reference === ref || 
        ref.includes(conn.requisition_reference)
      );

      if (!connection) {
        setStatus("error");
        setMessage("Conexión bancaria no encontrada");
        return;
      }

      // Procesar el callback
      const response = await api.post(`/openbanking/connections/${connection.id}/callback`);
      
      setStatus("success");
      setMessage("Conexión bancaria establecida correctamente");
      setDetails(response.data);

    } catch (error: any) {
      console.error("Error processing callback:", error);
      setStatus("error");
      setMessage(
        error.response?.data?.detail || 
        "Error procesando la respuesta del banco"
      );
    }
  };

  const goToConnections = () => {
    router.push("/bank-connections");
  };

  const StatusIcon = () => {
    switch (status) {
      case "loading":
        return <Loader2 className="h-16 w-16 animate-spin text-blue-500" />;
      case "success":
        return <CheckCircle className="h-16 w-16 text-green-500" />;
      case "error":
        return <XCircle className="h-16 w-16 text-red-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center pb-4">
          <div className="flex justify-center mb-4">
            <StatusIcon />
          </div>
          <CardTitle className="text-xl">
            {status === "loading" && "Procesando Conexión..."}
            {status === "success" && "¡Conexión Exitosa!"}
            {status === "error" && "Error en la Conexión"}
          </CardTitle>
        </CardHeader>
        
        <CardContent className="text-center space-y-4">
          <p className="text-gray-600">{message}</p>

          {status === "success" && details && (
            <div className="bg-green-50 p-4 rounded-lg text-left">
              <h4 className="font-medium text-green-800 mb-2">Detalles de la conexión:</h4>
              <ul className="text-sm text-green-700 space-y-1">
                <li>• Cuentas detectadas: {details.accounts_created}</li>
                <li>• Estado: {details.connection_status}</li>
                <li>• Sincronización: Automática cada 24 horas</li>
              </ul>
            </div>
          )}

          {status === "error" && (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Si el problema persiste, puedes intentar conectar el banco nuevamente 
                desde la página de conexiones bancarias.
              </AlertDescription>
            </Alert>
          )}

          <div className="pt-4">
            <Button onClick={goToConnections} className="w-full">
              Ir a Conexiones Bancarias
            </Button>
          </div>

          {status === "loading" && (
            <p className="text-xs text-gray-500">
              Esto puede tomar unos segundos mientras verificamos 
              el consentimiento con tu banco...
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}