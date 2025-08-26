"use client";
import { useState, useEffect } from "react";
import api from "@/lib/api";
import Layout from '@/components/Layout';

interface DocumentAlert {
  type: string;
  message: string;
  priority: string;
  due_date?: string;
  property_id?: number;
  contract_id?: number;
}

interface PropertyDocuments {
  property_id: number;
  property_address: string;
  contracts: Record<string, {
    contract_info: {
      id: number;
      tenant_name: string;
      start_date: string;
      end_date?: string;
      is_active: boolean;
      contract_pdf?: string;
    };
    documents: Array<{
      id: number;
      type: string;
      name: string;
      upload_date: string;
      file_size?: number;
      description?: string;
    }>;
  }>;
}

interface DocumentTemplate {
  name: string;
  type: string;
  description: string;
  required_fields: string[];
}

export default function DocumentsPage() {
  const [alerts, setAlerts] = useState<DocumentAlert[]>([]);
  const [properties, setProperties] = useState<any[]>([]);
  const [selectedProperty, setSelectedProperty] = useState<number | null>(null);
  const [propertyDocuments, setPropertyDocuments] = useState<PropertyDocuments | null>(null);
  const [templates, setTemplates] = useState<DocumentTemplate[]>([]);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [selectedContract, setSelectedContract] = useState<number | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);

  useEffect(() => {
    fetchAlerts();
    fetchProperties();
    fetchTemplates();
  }, []);

  useEffect(() => {
    if (selectedProperty) {
      fetchPropertyDocuments();
    }
  }, [selectedProperty]);

  const fetchAlerts = async () => {
    try {
      const response = await api.get("/documents/alerts");
      setAlerts(response.data.alerts);
    } catch (error) {
      console.error("Error fetching alerts:", error);
    }
  };

  const fetchProperties = async () => {
    try {
      const response = await api.get("/properties");
      setProperties(response.data);
      if (response.data.length > 0 && !selectedProperty) {
        setSelectedProperty(response.data[0].id);
      }
    } catch (error) {
      console.error("Error fetching properties:", error);
    }
  };

  const fetchPropertyDocuments = async () => {
    if (!selectedProperty) return;
    
    try {
      const response = await api.get(`/documents/property/${selectedProperty}`);
      setPropertyDocuments(response.data);
    } catch (error) {
      console.error("Error fetching property documents:", error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await api.get("/documents/templates");
      setTemplates(response.data.templates);
    } catch (error) {
      console.error("Error fetching templates:", error);
    }
  };

  const handleFileUpload = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedContract) return;

    const formData = new FormData(event.currentTarget);
    setUploadingFile(true);

    try {
      await api.post(`/documents/upload/${selectedContract}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setShowUploadModal(false);
      await fetchPropertyDocuments();
      await fetchAlerts();
      alert("Documento subido exitosamente");
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Error al subir el archivo");
    } finally {
      setUploadingFile(false);
    }
  };

  const deleteDocument = async (documentId: number) => {
    if (!confirm("¿Está seguro de que desea eliminar este documento?")) return;

    try {
      await api.delete(`/documents/document/${documentId}`);
      await fetchPropertyDocuments();
      await fetchAlerts();
      alert("Documento eliminado exitosamente");
    } catch (error) {
      console.error("Error deleting document:", error);
      alert("Error al eliminar el documento");
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high": return "bg-red-100 text-red-800 border-red-200";
      case "medium": return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "low": return "bg-green-100 text-green-800 border-green-200";
      default: return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getDocumentTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      dni: "DNI/NIE",
      payslip: "Nómina",
      employment_contract: "Contrato Trabajo",
      bank_statement: "Extracto Bancario",
      other: "Otro"
    };
    return labels[type] || type;
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return "";
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(1)} MB`;
  };

  return (
    <Layout
      title="Gestor de Documentos"
      subtitle="Administra y organiza documentos de inquilinos y propiedades"
      breadcrumbs={[
        { label: 'Agente Financiero', href: '/financial-agent' },
        { label: 'Documentos', href: '/financial-agent/documents' }
      ]}
    >
      <div className="space-y-6">

      {/* Alerts Section */}
      {alerts.length > 0 && (
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-4">🚨 Alertas Pendientes</h2>
          <div className="space-y-2">
            {alerts.map((alert, index) => (
              <div
                key={index}
                className={`p-3 rounded border ${getPriorityColor(alert.priority)}`}
              >
                <div className="flex justify-between items-start">
                  <p className="font-medium">{alert.message}</p>
                  <span className="text-xs px-2 py-1 rounded bg-white bg-opacity-50">
                    {alert.priority.toUpperCase()}
                  </span>
                </div>
                {alert.due_date && (
                  <p className="text-sm mt-1">
                    Vence: {new Date(alert.due_date).toLocaleDateString()}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Property Selection */}
      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold mb-3">Seleccionar Propiedad</h2>
        <select
          value={selectedProperty || ""}
          onChange={(e) => setSelectedProperty(Number(e.target.value))}
          className="w-full border rounded px-3 py-2"
        >
          <option value="">Seleccionar propiedad...</option>
          {properties.map((property) => (
            <option key={property.id} value={property.id}>
              {property.address}
            </option>
          ))}
        </select>
      </div>

      {/* Documents by Contract */}
      {propertyDocuments && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b flex justify-between items-center">
            <h2 className="text-lg font-semibold">
              Documentos - {propertyDocuments.property_address}
            </h2>
            <button
              onClick={() => setShowUploadModal(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Subir Documento
            </button>
          </div>
          
          <div className="p-4">
            {Object.entries(propertyDocuments.contracts).map(([contractId, contractData]) => (
              <div key={contractId} className="mb-6 border rounded-lg p-4">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-semibold text-lg">
                      {contractData.contract_info.tenant_name}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {new Date(contractData.contract_info.start_date).toLocaleDateString()} - 
                      {contractData.contract_info.end_date 
                        ? new Date(contractData.contract_info.end_date).toLocaleDateString()
                        : "Indefinido"
                      }
                    </p>
                    <span className={`inline-block px-2 py-1 rounded text-xs ${
                      contractData.contract_info.is_active 
                        ? "bg-green-100 text-green-800" 
                        : "bg-red-100 text-red-800"
                    }`}>
                      {contractData.contract_info.is_active ? "Activo" : "Inactivo"}
                    </span>
                  </div>
                </div>

                {/* Documents List */}
                <div className="space-y-2">
                  <h4 className="font-medium">Documentos del Inquilino:</h4>
                  {contractData.documents.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {contractData.documents.map((doc) => (
                        <div key={doc.id} className="border rounded p-3">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-medium">{doc.name}</p>
                              <p className="text-sm text-gray-600">
                                {getDocumentTypeLabel(doc.type)}
                              </p>
                              <p className="text-xs text-gray-500">
                                {new Date(doc.upload_date).toLocaleDateString()}
                                {doc.file_size && ` • ${formatFileSize(doc.file_size)}`}
                              </p>
                              {doc.description && (
                                <p className="text-xs text-gray-500 mt-1">
                                  {doc.description}
                                </p>
                              )}
                            </div>
                            <button
                              onClick={() => deleteDocument(doc.id)}
                              className="text-red-600 hover:text-red-800 text-sm"
                            >
                              Eliminar
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 italic">No hay documentos subidos</p>
                  )}
                </div>

                {/* Required Documents Checklist */}
                <div className="mt-4">
                  <h4 className="font-medium mb-2">Documentos Requeridos:</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                    {["dni", "payslip", "employment_contract", "bank_statement"].map((reqType) => {
                      const hasDoc = contractData.documents.some(doc => doc.type === reqType);
                      return (
                        <div
                          key={reqType}
                          className={`p-2 rounded ${
                            hasDoc 
                              ? "bg-green-100 text-green-800" 
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          <span className="mr-1">{hasDoc ? "✓" : "✗"}</span>
                          {getDocumentTypeLabel(reqType)}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Subir Documento</h3>
            
            <form onSubmit={handleFileUpload} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Contrato
                </label>
                <select
                  name="contract_id"
                  value={selectedContract || ""}
                  onChange={(e) => setSelectedContract(Number(e.target.value))}
                  className="w-full border rounded px-3 py-2"
                  required
                >
                  <option value="">Seleccionar contrato...</option>
                  {propertyDocuments && Object.entries(propertyDocuments.contracts).map(([contractId, contractData]) => (
                    <option key={contractId} value={contractId}>
                      {contractData.contract_info.tenant_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Tipo de Documento
                </label>
                <select
                  name="document_type"
                  className="w-full border rounded px-3 py-2"
                  required
                >
                  <option value="">Seleccionar tipo...</option>
                  <option value="dni">DNI/NIE</option>
                  <option value="payslip">Nómina</option>
                  <option value="employment_contract">Contrato Trabajo</option>
                  <option value="bank_statement">Extracto Bancario</option>
                  <option value="other">Otro</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Archivo
                </label>
                <input
                  type="file"
                  name="file"
                  accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                  className="w-full border rounded px-3 py-2"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Descripción (opcional)
                </label>
                <textarea
                  name="description"
                  className="w-full border rounded px-3 py-2"
                  rows={3}
                  placeholder="Descripción del documento..."
                />
              </div>

              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 border rounded hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={uploadingFile}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  {uploadingFile ? "Subiendo..." : "Subir"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Templates Section */}
      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold mb-4">📄 Plantillas Disponibles</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {templates.map((template, index) => (
            <div key={index} className="border rounded p-3">
              <h3 className="font-medium">{template.name}</h3>
              <p className="text-sm text-gray-600 mt-1">{template.description}</p>
              <p className="text-xs text-gray-500 mt-2">
                Campos requeridos: {template.required_fields.join(", ")}
              </p>
              <button className="mt-2 text-blue-600 hover:underline text-sm">
                Generar documento
              </button>
            </div>
          ))}
        </div>
      </div>
      </div>
    </Layout>
  );
}