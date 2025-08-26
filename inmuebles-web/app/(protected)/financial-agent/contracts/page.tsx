"use client";
import { useState, useEffect } from "react";
import api from "@/lib/api";

interface Property {
  id: number;
  address: string;
  property_type?: string;
}

interface RentalContract {
  id: number;
  property_id: number;
  tenant_name: string;
  start_date: string;
  end_date?: string;
  monthly_rent: number;
  deposit?: number;
  contract_pdf_path?: string;
  contract_file_name?: string;
  is_active: boolean;
  // Nuevos campos del inquilino
  tenant_email?: string;
  tenant_phone?: string;
  tenant_dni?: string;
  tenant_address?: string;
  monthly_income?: number;
  job_position?: string;
  employer_name?: string;
}

interface TenantDocument {
  id: number;
  rental_contract_id: number;
  document_type: string;
  document_name: string;
  file_path: string;
  file_size?: number;
  upload_date: string;
  description?: string;
}

interface ContractWithProperty extends RentalContract {
  property_address: string;
}

export default function RentalContractsPage() {
  const [contracts, setContracts] = useState<ContractWithProperty[]>([]);
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNewContractModal, setShowNewContractModal] = useState(false);
  const [selectedContract, setSelectedContract] = useState<ContractWithProperty | null>(null);
  const [activeFilter, setActiveFilter] = useState<"all" | "active" | "inactive">("all");
  
  // PDF upload state
  const [uploadingPdf, setUploadingPdf] = useState(false);
  const [selectedPdf, setSelectedPdf] = useState<File | null>(null);
  const [showPdfViewer, setShowPdfViewer] = useState(false);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loadingPdf, setLoadingPdf] = useState(false);
  
  // Tenant documents state
  const [tenantDocuments, setTenantDocuments] = useState<TenantDocument[]>([]);
  const [loadingDocuments, setLoadingDocuments] = useState(false);
  const [showDocumentsModal, setShowDocumentsModal] = useState(false);
  const [uploadingDocument, setUploadingDocument] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState("dni");
  const [documentDescription, setDocumentDescription] = useState("");
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingContract, setEditingContract] = useState<RentalContract | null>(null);

  // New contract form
  const [newContract, setNewContract] = useState({
    property_id: 0,
    tenant_name: "",
    start_date: "",
    end_date: "",
    monthly_rent: 0,
    deposit: 0,
    tenant_email: "",
    tenant_phone: "",
    tenant_dni: "",
    tenant_address: "",
    monthly_income: 0,
    job_position: "",
    employer_name: ""
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load properties
      const propertiesRes = await api.get("/properties");
      setProperties(propertiesRes.data);

      // Load contracts
      const contractsRes = await api.get("/rental-contracts/");
      
      // Enrich contracts with property info
      const enrichedContracts = contractsRes.data.map((contract: RentalContract) => {
        const property = propertiesRes.data.find((p: Property) => p.id === contract.property_id);
        return {
          ...contract,
          property_address: property?.address || "Propiedad desconocida"
        };
      });

      setContracts(enrichedContracts);
    } catch (error) {
      console.error("Error loading contracts:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateContract = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const contractData = {
        ...newContract,
        property_id: Number(newContract.property_id),
        monthly_rent: Number(newContract.monthly_rent),
        deposit: newContract.deposit ? Number(newContract.deposit) : undefined,
        end_date: newContract.end_date || undefined
      };

      await api.post("/rental-contracts/", contractData);
      
      setShowNewContractModal(false);
      setNewContract({
        property_id: 0,
        tenant_name: "",
        start_date: "",
        end_date: "",
        monthly_rent: 0,
        deposit: 0,
        tenant_email: "",
        tenant_phone: "",
        tenant_dni: "",
        tenant_address: "",
        monthly_income: 0,
        job_position: "",
        employer_name: ""
      });
      
      await loadData();
    } catch (error) {
      console.error("Error creating contract:", error);
      alert("Error al crear el contrato");
    }
  };

  const handleUpdateContract = async (contractId: number, updates: Partial<RentalContract>) => {
    try {
      await api.put(`/rental-contracts/${contractId}`, updates);
      await loadData();
      setSelectedContract(null);
    } catch (error) {
      console.error("Error updating contract:", error);
      alert("Error al actualizar el contrato");
    }
  };

  const handleDeleteContract = async (contractId: number) => {
    if (!confirm("¿Estás seguro de que quieres eliminar este contrato?")) {
      return;
    }

    try {
      await api.delete(`/rental-contracts/${contractId}`);
      await loadData();
      setSelectedContract(null);
    } catch (error) {
      console.error("Error deleting contract:", error);
      alert("Error al eliminar el contrato");
    }
  };

  const handlePdfUpload = async () => {
    if (!selectedPdf || !selectedContract) return;
    
    setUploadingPdf(true);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedPdf);
      
      await api.post(`/rental-contracts/${selectedContract.id}/upload-pdf`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      // Reload data to show updated contract
      await loadData();
      
      // Find and update the selected contract
      const updatedContracts = await api.get("/rental-contracts/");
      const updatedContract = updatedContracts.data.find((c: RentalContract) => c.id === selectedContract.id);
      if (updatedContract) {
        const property = properties.find(p => p.id === updatedContract.property_id);
        setSelectedContract({
          ...updatedContract,
          property_address: property?.address || "Propiedad desconocida"
        });
      }
      
      setSelectedPdf(null);
      alert("PDF subido correctamente");
    } catch (error: any) {
      console.error('Error uploading PDF:', error);
      alert(error?.response?.data?.detail || 'Error al subir el PDF');
    } finally {
      setUploadingPdf(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        alert('Solo se permiten archivos PDF');
        return;
      }
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        alert('El archivo es demasiado grande. Máximo 10MB');
        return;
      }
      setSelectedPdf(file);
    }
  };

  const handleDownloadPdf = async (contractId: number, fileName: string) => {
    try {
      setLoadingPdf(true);
      const response = await api.get(`/rental-contracts/${contractId}/download-pdf`, {
        responseType: 'blob'
      });
      
      // Create blob URL and trigger download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = fileName || 'contrato.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      console.error('Error downloading PDF:', error);
      alert(error?.response?.data?.detail || 'Error al descargar el PDF');
    } finally {
      setLoadingPdf(false);
    }
  };

  const handleViewPdf = async (contractId: number) => {
    try {
      setLoadingPdf(true);
      const response = await api.get(`/rental-contracts/${contractId}/download-pdf`, {
        responseType: 'blob'
      });
      
      // Create blob URL for viewing
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      setPdfUrl(url);
      setShowPdfViewer(true);
    } catch (error: any) {
      console.error('Error loading PDF:', error);
      alert(error?.response?.data?.detail || 'Error al cargar el PDF');
    } finally {
      setLoadingPdf(false);
    }
  };

  const handleOpenInNewTab = async (contractId: number) => {
    try {
      setLoadingPdf(true);
      const response = await api.get(`/rental-contracts/${contractId}/download-pdf`, {
        responseType: 'blob'
      });
      
      // Create blob URL and open in new tab
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
      
      // Clean up after a delay
      setTimeout(() => {
        window.URL.revokeObjectURL(url);
      }, 1000);
    } catch (error: any) {
      console.error('Error opening PDF:', error);
      alert(error?.response?.data?.detail || 'Error al abrir el PDF');
    } finally {
      setLoadingPdf(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES');
  };

  // Tenant Documents Functions
  const loadTenantDocuments = async (contractId: number) => {
    try {
      setLoadingDocuments(true);
      const response = await api.get(`/rental-contracts/${contractId}/documents`);
      setTenantDocuments(response.data);
    } catch (error) {
      console.error("Error loading tenant documents:", error);
      alert("Error al cargar los documentos del inquilino");
    } finally {
      setLoadingDocuments(false);
    }
  };

  const handleShowDocuments = (contract: ContractWithProperty) => {
    setSelectedContract(contract);
    setShowDocumentsModal(true);
    loadTenantDocuments(contract.id);
  };

  const handleDocumentUpload = async () => {
    if (!selectedDocument || !selectedContract) return;

    setUploadingDocument(true);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedDocument);
      formData.append('document_type', documentType);
      if (documentDescription) {
        formData.append('description', documentDescription);
      }
      
      await api.post(`/rental-contracts/${selectedContract.id}/documents`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      // Reload documents
      await loadTenantDocuments(selectedContract.id);
      
      setSelectedDocument(null);
      setDocumentDescription("");
      setDocumentType("dni");
      alert("Documento subido correctamente");
    } catch (error: any) {
      console.error('Error uploading document:', error);
      alert(error?.response?.data?.detail || 'Error al subir el documento');
    } finally {
      setUploadingDocument(false);
    }
  };

  const handleDocumentFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const allowedTypes = [
        'application/pdf', 
        'image/png', 
        'image/jpeg', 
        'image/jpg',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      ];
      
      if (!allowedTypes.includes(file.type)) {
        alert('Tipo de archivo no permitido. Formatos válidos: PDF, PNG, JPG, DOC, DOCX');
        return;
      }
      
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        alert('El archivo es demasiado grande. Máximo 10MB');
        return;
      }
      
      setSelectedDocument(file);
    }
  };

  const handleDeleteDocument = async (documentId: number) => {
    if (!confirm("¿Estás seguro de que quieres eliminar este documento?")) {
      return;
    }

    try {
      await api.delete(`/rental-contracts/${selectedContract?.id}/documents/${documentId}`);
      await loadTenantDocuments(selectedContract!.id);
      alert("Documento eliminado correctamente");
    } catch (error) {
      console.error("Error deleting document:", error);
      alert("Error al eliminar el documento");
    }
  };

  const handleDownloadDocument = async (documentId: number, fileName: string) => {
    try {
      const response = await api.get(`/rental-contracts/${selectedContract?.id}/documents/${documentId}/download`, {
        responseType: 'blob'
      });
      
      // Create blob URL and trigger download
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      console.error('Error downloading document:', error);
      alert(error?.response?.data?.detail || 'Error al descargar el documento');
    }
  };

  const getDocumentTypeLabel = (type: string) => {
    const types: Record<string, string> = {
      'dni': 'DNI/NIE',
      'payslip': 'Nómina',
      'employment_contract': 'Contrato Laboral',
      'bank_statement': 'Extracto Bancario',
      'other': 'Otro'
    };
    return types[type] || type;
  };

  const getDocumentTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      'dni': '🆔',
      'payslip': '💰',
      'employment_contract': '📝',
      'bank_statement': '🏦',
      'other': '📄'
    };
    return icons[type] || '📄';
  };

  const handleEditContract = (contract: ContractWithProperty) => {
    setEditingContract(contract);
    setShowEditModal(true);
  };

  const handleSaveContractEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingContract) return;

    try {
      await api.put(`/rental-contracts/${editingContract.id}`, editingContract);
      await loadData();
      setShowEditModal(false);
      setEditingContract(null);
      alert("Contrato actualizado correctamente");
    } catch (error) {
      console.error("Error updating contract:", error);
      alert("Error al actualizar el contrato");
    }
  };

  const filteredContracts = contracts.filter(contract => {
    // Check if contract is expired based on end_date
    const isExpired = contract.end_date && new Date(contract.end_date) < new Date();
    const actualStatus = !contract.end_date || (!isExpired && contract.is_active);
    
    switch (activeFilter) {
      case "active":
        return actualStatus;
      case "inactive":
        return !actualStatus;
      default:
        return true;
    }
  });

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <nav className="text-sm text-gray-500 mb-2">
            <a href="/financial-agent" className="hover:text-blue-600">Agente Financiero</a>
            <span className="mx-2">&gt;</span>
            <span>Contratos de Alquiler</span>
          </nav>
          <h1 className="text-3xl font-bold text-gray-900">📄 Contratos de Alquiler</h1>
          <p className="text-gray-600 mt-1">Gestión de contratos y inquilinos</p>
        </div>
        
        <button
          onClick={() => setShowNewContractModal(true)}
          className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
        >
          + Nuevo Contrato
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
          <p className="text-sm text-gray-600">Contratos Activos</p>
          <p className="text-2xl font-bold text-green-600">
            {contracts.filter(c => {
              const isExpired = c.end_date && new Date(c.end_date) < new Date();
              return !c.end_date || (!isExpired && c.is_active);
            }).length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-gray-500">
          <p className="text-sm text-gray-600">Total Contratos</p>
          <p className="text-2xl font-bold text-gray-600">{contracts.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
          <p className="text-sm text-gray-600">Renta Mensual Total</p>
          <p className="text-2xl font-bold text-blue-600">
            {formatCurrency(contracts.filter(c => {
              const isExpired = c.end_date && new Date(c.end_date) < new Date();
              return !c.end_date || (!isExpired && c.is_active);
            }).reduce((sum, c) => sum + c.monthly_rent, 0))}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500">
          <p className="text-sm text-gray-600">Depósitos Total</p>
          <p className="text-2xl font-bold text-purple-600">
            {formatCurrency(contracts.filter(c => {
              const isExpired = c.end_date && new Date(c.end_date) < new Date();
              return !c.end_date || (!isExpired && c.is_active);
            }).reduce((sum, c) => sum + (c.deposit || 0), 0))}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex space-x-4">
          {[
            { key: "all", label: "Todos", count: contracts.length },
            { key: "active", label: "Activos", count: contracts.filter(c => {
              const isExpired = c.end_date && new Date(c.end_date) < new Date();
              return !c.end_date || (!isExpired && c.is_active);
            }).length },
            { key: "inactive", label: "Inactivos", count: contracts.filter(c => {
              const isExpired = c.end_date && new Date(c.end_date) < new Date();
              return c.end_date && isExpired || !c.is_active;
            }).length }
          ].map((filter) => (
            <button
              key={filter.key}
              onClick={() => setActiveFilter(filter.key as any)}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                activeFilter === filter.key
                  ? "bg-blue-100 text-blue-700"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              {filter.label} ({filter.count})
            </button>
          ))}
        </div>
      </div>

      {/* Contracts List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Lista de Contratos</h2>
        </div>
        
        {filteredContracts.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <p>No hay contratos para mostrar</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Inquilino
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Propiedad
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Período
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Renta/Mes
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Depósito
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Gestión
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredContracts.map((contract) => {
                  // Check if contract is expired based on end_date
                  const isExpired = contract.end_date && new Date(contract.end_date) < new Date();
                  const actualStatus = !contract.end_date || (!isExpired && contract.is_active);
                  
                  return (
                    <tr key={contract.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="font-medium text-gray-900">{contract.tenant_name}</div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {contract.property_address}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        <div>{formatDate(contract.start_date)}</div>
                        <div className={isExpired ? "text-red-600 font-medium" : ""}>
                          {contract.end_date ? `hasta ${formatDate(contract.end_date)}` : "Sin fecha fin"}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm font-medium text-green-600">
                        {formatCurrency(contract.monthly_rent)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {contract.deposit ? formatCurrency(contract.deposit) : "N/A"}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                          actualStatus
                            ? "bg-green-100 text-green-800"
                            : "bg-gray-100 text-gray-800"
                        }`}>
                          {actualStatus ? "Activo" : "Inactivo"}
                        </span>
                      </td>
                    <td className="px-6 py-4 text-sm space-x-2">
                      <button
                        onClick={() => handleEditContract(contract)}
                        className="text-blue-600 hover:text-blue-800 text-xs px-2 py-1 rounded border border-blue-200 hover:bg-blue-50"
                        title="Editar información del inquilino"
                      >
                        ✏️ Editar Info
                      </button>
                      <button
                        onClick={() => handleShowDocuments(contract)}
                        className="text-green-600 hover:text-green-800 text-xs px-2 py-1 rounded border border-green-200 hover:bg-green-50"
                        title="Gestionar documentos del inquilino"
                      >
                        📁 Documentos
                      </button>
                    </td>
                    <td className="px-6 py-4 text-sm space-x-2">
                      <button
                        onClick={() => setSelectedContract(contract)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        Ver Detalles
                      </button>
                      {contract.contract_pdf_path && (
                        <>
                          <span className="text-gray-300">•</span>
                          <a
                            href={`/api/rental-contracts/${contract.id}/download-pdf`}
                            className="text-purple-600 hover:text-purple-800"
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            PDF
                          </a>
                        </>
                      )}
                    </td>
                  </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* New Contract Modal */}
      {showNewContractModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Nuevo Contrato</h3>
            
            <form onSubmit={handleCreateContract} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Propiedad</label>
                <select
                  value={newContract.property_id}
                  onChange={(e) => setNewContract({...newContract, property_id: Number(e.target.value)})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                >
                  <option value={0}>Seleccionar propiedad</option>
                  {properties.map((property) => (
                    <option key={property.id} value={property.id}>
                      {property.address}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nombre del Inquilino</label>
                <input
                  type="text"
                  value={newContract.tenant_name}
                  onChange={(e) => setNewContract({...newContract, tenant_name: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Fecha Inicio</label>
                  <input
                    type="date"
                    value={newContract.start_date}
                    onChange={(e) => setNewContract({...newContract, start_date: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Fecha Fin (opcional)</label>
                  <input
                    type="date"
                    value={newContract.end_date}
                    onChange={(e) => setNewContract({...newContract, end_date: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Renta Mensual (€)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newContract.monthly_rent}
                    onChange={(e) => setNewContract({...newContract, monthly_rent: Number(e.target.value)})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Depósito (€)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newContract.deposit}
                    onChange={(e) => setNewContract({...newContract, deposit: Number(e.target.value)})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowNewContractModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                  Crear Contrato
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Contract Details Modal */}
      {selectedContract && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Detalles del Contrato - {selectedContract.tenant_name}
              </h3>
              <button
                onClick={() => setSelectedContract(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Propiedad:</span>
                  <div className="font-medium">{selectedContract.property_address}</div>
                </div>
                <div>
                  <span className="text-gray-600">Estado:</span>
                  <div>
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                      selectedContract.is_active
                        ? "bg-green-100 text-green-800"
                        : "bg-gray-100 text-gray-800"
                    }`}>
                      {selectedContract.is_active ? "Activo" : "Inactivo"}
                    </span>
                  </div>
                </div>
                <div>
                  <span className="text-gray-600">Fecha Inicio:</span>
                  <div className="font-medium">{formatDate(selectedContract.start_date)}</div>
                </div>
                <div>
                  <span className="text-gray-600">Fecha Fin:</span>
                  <div className="font-medium">
                    {selectedContract.end_date ? formatDate(selectedContract.end_date) : "Sin fecha fin"}
                  </div>
                </div>
                <div>
                  <span className="text-gray-600">Renta Mensual:</span>
                  <div className="font-medium text-green-600">
                    {formatCurrency(selectedContract.monthly_rent)}
                  </div>
                </div>
                <div>
                  <span className="text-gray-600">Depósito:</span>
                  <div className="font-medium">
                    {selectedContract.deposit ? formatCurrency(selectedContract.deposit) : "N/A"}
                  </div>
                </div>
              </div>

              <div className="border-t pt-4">
                <h4 className="font-medium text-gray-900 mb-3">Documento del Contrato</h4>
                
                {selectedContract.contract_pdf_path ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <svg className="w-10 h-10 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                        </svg>
                        <div>
                          <p className="font-medium text-green-800">{selectedContract.contract_file_name}</p>
                          <p className="text-sm text-green-600">Documento del contrato adjunto</p>
                        </div>
                      </div>
                    </div>
                    
                    {/* Action buttons */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      <button
                        onClick={() => handleViewPdf(selectedContract.id)}
                        disabled={loadingPdf}
                        className="flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {loadingPdf ? (
                          <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                        ) : (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                        )}
                        <span>{loadingPdf ? 'Cargando...' : 'Ver PDF'}</span>
                      </button>
                      
                      <button
                        onClick={() => handleDownloadPdf(selectedContract.id, selectedContract.contract_file_name || 'contrato.pdf')}
                        disabled={loadingPdf}
                        className="flex items-center justify-center space-x-2 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {loadingPdf ? (
                          <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                        ) : (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        )}
                        <span>{loadingPdf ? 'Descargando...' : 'Descargar'}</span>
                      </button>
                      
                      <button
                        onClick={() => handleOpenInNewTab(selectedContract.id)}
                        disabled={loadingPdf}
                        className="flex items-center justify-center space-x-2 px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {loadingPdf ? (
                          <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                        ) : (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                        )}
                        <span>{loadingPdf ? 'Abriendo...' : 'Abrir en nueva pestaña'}</span>
                      </button>
                    </div>
                    
                    <div className="text-center pt-2 border-t border-green-200">
                      <button
                        onClick={() => document.getElementById(`pdf-input-${selectedContract.id}`)?.click()}
                        className="text-sm text-blue-600 hover:text-blue-800 underline"
                      >
                        Cambiar documento
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                      <svg className="w-12 h-12 text-gray-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <p className="text-gray-600 mb-3">No hay documento adjunto</p>
                      <button
                        onClick={() => document.getElementById(`pdf-input-${selectedContract.id}`)?.click()}
                        className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        <span>Subir PDF del Contrato</span>
                      </button>
                    </div>
                  </div>
                )}
                
                {/* File input */}
                <input
                  id={`pdf-input-${selectedContract.id}`}
                  type="file"
                  accept="application/pdf"
                  onChange={handleFileChange}
                  className="hidden"
                />
                
                {/* Show selected file and upload button */}
                {selectedPdf && (
                  <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                        </svg>
                        <span className="text-sm font-medium text-blue-800">{selectedPdf.name}</span>
                        <span className="text-xs text-blue-600">({(selectedPdf.size / 1024 / 1024).toFixed(1)} MB)</span>
                      </div>
                      <div className="space-x-2">
                        <button
                          onClick={() => setSelectedPdf(null)}
                          className="text-sm text-gray-600 hover:text-gray-800"
                        >
                          Cancelar
                        </button>
                        <button
                          onClick={handlePdfUpload}
                          disabled={uploadingPdf}
                          className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {uploadingPdf ? 'Subiendo...' : 'Subir'}
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex justify-between pt-4 border-t">
                <div className="space-x-2">
                  <button
                    onClick={() => handleUpdateContract(selectedContract.id, { is_active: !selectedContract.is_active })}
                    className={`px-4 py-2 rounded-md text-sm font-medium ${
                      selectedContract.is_active
                        ? "bg-orange-100 text-orange-700 hover:bg-orange-200"
                        : "bg-green-100 text-green-700 hover:bg-green-200"
                    }`}
                  >
                    {selectedContract.is_active ? "Desactivar" : "Activar"}
                  </button>
                </div>
                <div className="space-x-2">
                  <button
                    onClick={() => handleDeleteContract(selectedContract.id)}
                    className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm"
                  >
                    Eliminar
                  </button>
                  <button
                    onClick={() => setSelectedContract(null)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 text-sm"
                  >
                    Cerrar
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* PDF Viewer Modal */}
      {showPdfViewer && pdfUrl && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-6xl h-[90vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                Visualizador de PDF - {selectedContract?.contract_file_name}
              </h3>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => selectedContract && handleDownloadPdf(selectedContract.id, selectedContract.contract_file_name || 'contrato.pdf')}
                  className="flex items-center space-x-1 px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span>Descargar</span>
                </button>
                <button
                  onClick={() => selectedContract && handleOpenInNewTab(selectedContract.id)}
                  className="flex items-center space-x-1 px-3 py-1 bg-purple-600 text-white rounded text-sm hover:bg-purple-700"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  <span>Nueva pestaña</span>
                </button>
                <button
                  onClick={() => {
                    setShowPdfViewer(false);
                    if (pdfUrl) {
                      window.URL.revokeObjectURL(pdfUrl);
                      setPdfUrl(null);
                    }
                  }}
                  className="text-gray-400 hover:text-gray-600 p-1"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div className="flex-1 bg-gray-100">
              <iframe
                src={`${pdfUrl}#toolbar=1&navpanes=1&scrollbar=1&page=1&view=FitH`}
                className="w-full h-full border-0"
                title="PDF Viewer"
              />
            </div>
            
            {/* Fallback message */}
            <div className="p-4 border-t border-gray-200 bg-gray-50">
              <p className="text-sm text-gray-600 text-center">
                💡 Si el PDF no se muestra correctamente, puedes usar los botones de arriba para descargarlo o abrirlo en una nueva pestaña.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Edit Contract Modal */}
      {showEditModal && editingContract && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Editar Información del Contrato - {editingContract.tenant_name}
              </h3>
              <button
                onClick={() => setShowEditModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <form onSubmit={handleSaveContractEdit} className="space-y-6">
              {/* Información básica del contrato */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-3">Información del Contrato</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nombre del Inquilino</label>
                    <input
                      type="text"
                      value={editingContract.tenant_name}
                      onChange={(e) => setEditingContract({...editingContract, tenant_name: e.target.value})}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Renta Mensual (€)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={editingContract.monthly_rent}
                      onChange={(e) => setEditingContract({...editingContract, monthly_rent: Number(e.target.value)})}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Depósito (€)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={editingContract.deposit || 0}
                      onChange={(e) => setEditingContract({...editingContract, deposit: Number(e.target.value)})}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                </div>
              </div>

              {/* Información personal del inquilino */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-3">Información Personal</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                      type="email"
                      value={editingContract.tenant_email || ""}
                      onChange={(e) => setEditingContract({...editingContract, tenant_email: e.target.value})}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                      placeholder="email@ejemplo.com"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
                    <input
                      type="tel"
                      value={editingContract.tenant_phone || ""}
                      onChange={(e) => setEditingContract({...editingContract, tenant_phone: e.target.value})}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                      placeholder="+34 600 000 000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">DNI/NIE</label>
                    <input
                      type="text"
                      value={editingContract.tenant_dni || ""}
                      onChange={(e) => setEditingContract({...editingContract, tenant_dni: e.target.value})}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                      placeholder="12345678A"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Dirección Personal</label>
                    <input
                      type="text"
                      value={editingContract.tenant_address || ""}
                      onChange={(e) => setEditingContract({...editingContract, tenant_address: e.target.value})}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                      placeholder="Calle, número, ciudad"
                    />
                  </div>
                </div>
              </div>

              {/* Información financiera del inquilino */}
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-3">Información Financiera y Laboral</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Ingresos Mensuales (€)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={editingContract.monthly_income || 0}
                      onChange={(e) => setEditingContract({...editingContract, monthly_income: Number(e.target.value)})}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                      placeholder="2500.00"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Puesto de Trabajo</label>
                    <input
                      type="text"
                      value={editingContract.job_position || ""}
                      onChange={(e) => setEditingContract({...editingContract, job_position: e.target.value})}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                      placeholder="Desarrollador Senior"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nombre del Empleador</label>
                    <input
                      type="text"
                      value={editingContract.employer_name || ""}
                      onChange={(e) => setEditingContract({...editingContract, employer_name: e.target.value})}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                      placeholder="Empresa ABC S.L."
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-4 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Guardar Cambios
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Documents Modal */}
      {showDocumentsModal && selectedContract && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Documentos del Inquilino - {selectedContract.tenant_name}
              </h3>
              <button
                onClick={() => {
                  setShowDocumentsModal(false);
                  setTenantDocuments([]);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            {/* Upload Section */}
            <div className="mb-6 p-4 border-2 border-dashed border-gray-300 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-3">Subir Nuevo Documento</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Documento</label>
                  <select
                    value={documentType}
                    onChange={(e) => setDocumentType(e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="dni">DNI/NIE</option>
                    <option value="payslip">Nómina</option>
                    <option value="employment_contract">Contrato Laboral</option>
                    <option value="bank_statement">Extracto Bancario</option>
                    <option value="other">Otro</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Descripción (opcional)</label>
                  <input
                    type="text"
                    value={documentDescription}
                    onChange={(e) => setDocumentDescription(e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    placeholder="Nómina de enero 2024"
                  />
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <input
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg,.doc,.docx"
                  onChange={handleDocumentFileChange}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
                
                {selectedDocument && (
                  <button
                    onClick={handleDocumentUpload}
                    disabled={uploadingDocument}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {uploadingDocument ? 'Subiendo...' : 'Subir'}
                  </button>
                )}
              </div>
              
              {selectedDocument && (
                <div className="mt-2 text-sm text-gray-600">
                  Archivo seleccionado: {selectedDocument.name} ({(selectedDocument.size / 1024 / 1024).toFixed(2)} MB)
                </div>
              )}
            </div>
            
            {/* Documents List */}
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Documentos Guardados</h4>
              
              {loadingDocuments ? (
                <div className="flex justify-center py-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              ) : tenantDocuments.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>No hay documentos subidos para este inquilino</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {tenantDocuments.map((doc) => (
                    <div key={doc.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center space-x-3">
                          <span className="text-2xl">{getDocumentTypeIcon(doc.document_type)}</span>
                          <div>
                            <h5 className="font-medium text-gray-900">{doc.document_name}</h5>
                            <p className="text-sm text-gray-600">{getDocumentTypeLabel(doc.document_type)}</p>
                            {doc.description && (
                              <p className="text-xs text-gray-500 mt-1">{doc.description}</p>
                            )}
                            <div className="flex items-center space-x-2 text-xs text-gray-400 mt-1">
                              <span>{formatDate(doc.upload_date)}</span>
                              {doc.file_size && (
                                <>
                                  <span>•</span>
                                  <span>{(doc.file_size / 1024 / 1024).toFixed(2)} MB</span>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleDownloadDocument(doc.id, doc.document_name)}
                            className="text-blue-600 hover:text-blue-800 text-sm"
                            title="Descargar"
                          >
                            ⬇️
                          </button>
                          <button
                            onClick={() => handleDeleteDocument(doc.id)}
                            className="text-red-600 hover:text-red-800 text-sm"
                            title="Eliminar"
                          >
                            🗑️
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            <div className="flex justify-end pt-4 border-t mt-6">
              <button
                onClick={() => {
                  setShowDocumentsModal(false);
                  setTenantDocuments([]);
                }}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}