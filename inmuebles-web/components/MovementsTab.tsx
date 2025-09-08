"use client";
import { useState, useEffect } from "react";
import api from "@/lib/api";

interface Property {
  id: number;
  address: string;
}

interface FinancialMovement {
  id: number;
  property_id?: number;
  date: string;
  concept: string;
  amount: number;
  category: string;
  subcategory?: string;
  tenant_name?: string;
  is_classified: boolean;
  bank_balance?: number;
}

interface MovementWithProperty extends FinancialMovement {
  property_address: string;
}

export default function MovementsTab() {
  const [movements, setMovements] = useState<MovementWithProperty[]>([]);
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showNewMovementModal, setShowNewMovementModal] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [showDeleteAllModal, setShowDeleteAllModal] = useState(false);
  const [showDateRangeDeleteModal, setShowDateRangeDeleteModal] = useState(false);
  const [showEditMovementModal, setShowEditMovementModal] = useState(false);
  const [showDeleteMovementModal, setShowDeleteMovementModal] = useState(false);
  const [showAnalyzeConceptsModal, setShowAnalyzeConceptsModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedProperty, setSelectedProperty] = useState<number>(0);
  const [selectedMovement, setSelectedMovement] = useState<number | null>(null);
  const [editingMovement, setEditingMovement] = useState<FinancialMovement | null>(null);
  const [analyzedConcepts, setAnalyzedConcepts] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [updatingBankinter, setUpdatingBankinter] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  
  // Date range deletion form
  const [dateRangeDelete, setDateRangeDelete] = useState({
    start_date: "",
    end_date: "",
    property_id: ""
  });
  
  // Filters
  const [filters, setFilters] = useState({
    property_id: "",
    category: "",
    start_date: "",
    end_date: "",
    search: ""
  });

  // New movement form
  const [newMovement, setNewMovement] = useState({
    property_id: 0,
    date: "",
    concept: "",
    amount: 0,
    category: "Gasto",
    subcategory: "",
    tenant_name: ""
  });

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 50;

  useEffect(() => {
    loadData();
  }, [filters]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load properties
      let propertiesData: Property[] = [];
      try {
        const propertiesRes = await api.get("/properties");
        propertiesData = propertiesRes.data;
        setProperties(propertiesData);
      } catch (propertiesError) {
        console.warn("Properties endpoint not available, continuing without properties:", propertiesError);
        setProperties([]);
      }

      // Build query params for movements
      const queryParams = new URLSearchParams();
      if (filters.property_id) {
        if (filters.property_id === 'unassigned') {
          queryParams.append("unassigned_only", "true");
        } else {
          queryParams.append("property_id", filters.property_id);
        }
      }
      if (filters.category) queryParams.append("category", filters.category);
      if (filters.start_date) queryParams.append("start_date", filters.start_date);
      if (filters.end_date) queryParams.append("end_date", filters.end_date);

      // Load movements
      const movementsUrl = `/financial-movements/?${queryParams.toString()}`;
      const movementsRes = await api.get(movementsUrl);
      
      // Enrich movements with property info
      const enrichedMovements = movementsRes.data.map((movement: FinancialMovement) => {
        const property = propertiesData.find((p: Property) => p.id === movement.property_id);
        return {
          ...movement,
          property_address: property?.address || "Sin propiedad asignada"
        };
      });

      // Apply text search filter
      const filteredMovements = enrichedMovements.filter((movement: MovementWithProperty) => {
        if (!filters.search) return true;
        const searchLower = filters.search.toLowerCase();
        return (
          movement.concept.toLowerCase().includes(searchLower) ||
          movement.property_address.toLowerCase().includes(searchLower) ||
          (movement.tenant_name && movement.tenant_name.toLowerCase().includes(searchLower))
        );
      });

      // Sort by date descending (most recent first)
      const sortedMovements = filteredMovements.sort((a, b) => {
        const dateA = new Date(a.date);
        const dateB = new Date(b.date);
        return dateB.getTime() - dateA.getTime();
      });

      setMovements(sortedMovements);
    } catch (error) {
      console.error("Error loading movements:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateMovement = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const movementData = {
        ...newMovement,
        property_id: newMovement.property_id > 0 ? Number(newMovement.property_id) : undefined,
        amount: Number(newMovement.amount),
        subcategory: newMovement.subcategory || undefined,
        tenant_name: newMovement.tenant_name || undefined
      };

      await api.post("/financial-movements", movementData);
      
      setShowNewMovementModal(false);
      setNewMovement({
        property_id: 0,
        date: "",
        concept: "",
        amount: 0,
        category: "Gasto",
        subcategory: "",
        tenant_name: ""
      });
      
      await loadData();
    } catch (error) {
      console.error("Error creating movement:", error);
      alert("Error al crear el movimiento");
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      console.log('🔍 Debug - FormData contents:', {
        selectedFile: selectedFile,
        fileName: selectedFile?.name,
        fileSize: selectedFile?.size,
        fileType: selectedFile?.type
      });

      const response = await api.post('/financial-movements/upload-excel-global', formData, {
        headers: {
          'Content-Type': undefined, // Let axios set the boundary automatically
        },
      });
      const result = response.data;
      
      let message = `✅ Archivo procesado exitosamente!\n\n`;
      message += `📊 Movimientos creados: ${result.created_movements}\n`;
      message += `📄 Total filas procesadas: ${result.total_rows}\n`;
      
      if (result.duplicates_skipped > 0) {
        message += `🔄 Duplicados omitidos: ${result.duplicates_skipped}\n`;
      }
      
      if (result.errors && result.errors.length > 0) {
        message += `\n⚠️ Errores encontrados:\n`;
        result.errors.forEach((error: string, index: number) => {
          if (index < 5) {
            message += `• ${error}\n`;
          }
        });
        if (result.errors.length > 5) {
          message += `• ... y ${result.errors.length - 5} errores más\n`;
        }
      }

      message += `\n💡 Ahora puedes asignar conceptos a propiedades específicas.`;
      alert(message);
      
      setShowUploadModal(false);
      setSelectedFile(null);
      await loadData();
      
    } catch (error: any) {
      console.error('Error uploading file:', error);
      const errorMessage = extractErrorMessage(error, 'Error al procesar el archivo Excel');
      alert(`❌ Error: ${errorMessage}`);
    } finally {
      setUploading(false);
    }
  };

  const handleBankinterUpdate = async () => {
    setUpdatingBankinter(true);
    try {
      console.log('🏦 BANKINTER: Starting update process...');
      alert('💡 Para sincronizar Bankinter:\n\n1. Descarga el Excel más reciente de tu banca online\n2. Usa el botón "📁 Subir Extracto" arriba\n3. Selecciona el archivo descargado\n\n⏳ Procesando datos existentes...');
      
      console.log('🏦 BANKINTER: Making API call to /integrations/bankinter/sync-now');
      
      // Usar endpoint que siempre funciona para dar feedback
      const response = await api.post('/integrations/bankinter/sync-now', {}, {
        timeout: 30000
      });
      
      console.log('🏦 BANKINTER: API call completed, status:', response.status);
      
      const result = response.data;
      
      if (result.sync_status === 'started') {
        let message = `📋 Para obtener los movimientos más recientes:\n\n`;
        message += `1️⃣ Ve a tu banca online de Bankinter\n`;
        message += `2️⃣ Descarga el extracto Excel más reciente\n`;
        message += `3️⃣ Usa el botón "📁 Subir Extracto" en esta página\n`;
        message += `4️⃣ Selecciona el archivo descargado\n\n`;
        message += `💡 Esto asegura que tengas todos los movimientos más actuales.\n\n`;
        message += `📊 Los datos mostrados actualmente pueden no incluir las últimas transacciones.`;
        
        alert(message);
        await loadData(); // Reload current data
      } else {
        // Fallback for other response types
        const createdMovements = result.new_movements || result.created_movements || 0;
        let message = `✅ Proceso completado\n\n`;
        message += `📈 Datos actuales mostrados\n`;
        message += `💡 Para datos más recientes, descarga y sube el extracto Excel de Bankinter`;
        
        alert(message);
        await loadData();
      }
      
    } catch (error: any) {
      console.error('❌ BANKINTER ERROR:', error);
      console.error('❌ BANKINTER ERROR Details:', {
        message: error?.message,
        status: error?.response?.status,
        data: error?.response?.data,
        url: error?.config?.url
      });
      
      let errorMessage = '❌ Error en conexión con Bankinter\n\n';
      
      if (error?.response?.status === 401) {
        errorMessage += '🔐 Credenciales incorrectas. Verifica tu usuario y contraseña.';
      } else if (error?.response?.status === 408 || error?.code === 'ECONNABORTED') {
        errorMessage += '⏱️ Tiempo de espera agotado. La conexión bancaria tardó demasiado.';
      } else if (error?.response?.data?.detail) {
        errorMessage += `📋 Detalles: ${error.response.data.detail}`;
      } else {
        errorMessage += '🔧 Error técnico en la sincronización. Inténtalo más tarde.';
      }
      
      alert(errorMessage);
    } finally {
      setUpdatingBankinter(false);
    }
  };

  const handleDeleteAllMovements = async () => {
    setDeleting(true);
    try {
      const response = await api.post('/financial-movements/bulk-delete');
      const result = response.data;
      
      alert(`✅ Eliminados exitosamente!\n\n📊 Total movimientos eliminados: ${result.count}`);
      
      setShowDeleteAllModal(false);
      await loadData();
      
    } catch (error: any) {
      console.error('Error deleting movements:', error);
      const errorMessage = extractErrorMessage(error, 'Error al eliminar movimientos');
      alert(`❌ Error: ${errorMessage}`);
    } finally {
      setDeleting(false);
    }
  };

  const handleDeleteByDateRange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!dateRangeDelete.start_date || !dateRangeDelete.end_date) {
      alert('Por favor, selecciona ambas fechas');
      return;
    }

    setDeleting(true);
    try {
      const queryParams = new URLSearchParams({
        start_date: dateRangeDelete.start_date,
        end_date: dateRangeDelete.end_date
      });
      
      if (dateRangeDelete.property_id) {
        queryParams.append('property_id', dateRangeDelete.property_id);
      }

      const response = await api.delete(`/financial-movements/delete-by-date-range?${queryParams.toString()}`);
      const result = response.data;
      
      const propertyText = dateRangeDelete.property_id ? 
        ` de la propiedad seleccionada` : ' de todas las propiedades';
      
      alert(`✅ Eliminación por fechas completada!\n\n` +
            `📅 Rango: ${dateRangeDelete.start_date} a ${dateRangeDelete.end_date}\n` +
            `📊 Movimientos eliminados: ${result.deleted_count}${propertyText}`);
      
      setShowDateRangeDeleteModal(false);
      setDateRangeDelete({ start_date: "", end_date: "", property_id: "" });
      await loadData();
      
    } catch (error: any) {
      console.error('Error deleting movements by date range:', error);
      const errorMessage = extractErrorMessage(error, 'Error al eliminar movimientos por fechas');
      alert(`❌ Error: ${errorMessage}`);
    } finally {
      setDeleting(false);
    }
  };

  const handleDeleteMovement = async (movementId: number) => {
    try {
      await api.delete(`/financial-movements/${movementId}`);
      alert('✅ Movimiento eliminado exitosamente');
      setShowDeleteMovementModal(false);
      setSelectedMovement(null);
      await loadData();
    } catch (error: any) {
      console.error('Error deleting movement:', error);
      const errorMessage = extractErrorMessage(error, 'Error al eliminar movimiento');
      alert(`❌ Error al eliminar: ${errorMessage}`);
    }
  };

  const handleEditMovement = async (movement: FinancialMovement) => {
    setEditingMovement(movement);
    setShowEditMovementModal(true);
  };

  const handleAnalyzeConcepts = async () => {
    if (!selectedFile) {
      alert('Por favor, selecciona primero un archivo Excel');
      return;
    }

    setAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await api.post('/financial-movements/extract-concepts', formData);
      const result = response.data;
      
      setAnalyzedConcepts(result.concepts || []);
      setShowAnalyzeConceptsModal(true);
      
    } catch (error: any) {
      console.error('Error analyzing concepts:', error);
      const errorMessage = extractErrorMessage(error, 'Error al analizar conceptos');
      alert(`❌ Error al analizar conceptos: ${errorMessage}`);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleAssignPropertyToMovement = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMovement || selectedProperty === 0) {
      alert('Por favor, selecciona una propiedad');
      return;
    }

    try {
      await api.put(`/financial-movements/${selectedMovement}/assign-property`, null, {
        params: { property_id: selectedProperty }
      });
      alert('✅ Movimiento asignado exitosamente a la propiedad');
      setShowAssignModal(false);
      setSelectedMovement(null);
      setSelectedProperty(0);
      await loadData();
    } catch (error: any) {
      console.error('Error assigning movement to property:', error);
      const errorMessage = extractErrorMessage(error, 'Error al asignar movimiento');
      alert(`❌ Error al asignar: ${errorMessage}`);
    }
  };

  const handleExportToExcel = async () => {
    setExporting(true);
    try {
      // Build query parameters using current filters
      const queryParams = new URLSearchParams();
      if (filters.property_id) queryParams.append("property_id", filters.property_id);
      if (filters.category) queryParams.append("category", filters.category);
      if (filters.start_date) queryParams.append("start_date", filters.start_date);
      if (filters.end_date) queryParams.append("end_date", filters.end_date);

      const response = await api.get(`/financial-movements/download-xlsx?${queryParams.toString()}`, {
        responseType: 'blob',
        timeout: 30000 // 30 second timeout for export
      });

      // Create blob and download
      const blob = new Blob([response.data], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      
      // Extract filename from Content-Disposition header or create a default one
      let filename = 'movimientos_export.xlsx';
      const contentDisposition = response.headers['content-disposition'];
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename=([^;]+)/);
        if (filenameMatch) {
          filename = filenameMatch[1].replace(/"/g, '');
        }
      }

      // Create download link and trigger download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      link.remove();
      window.URL.revokeObjectURL(url);

      alert(`✅ ¡Exportación completada!\n\n📊 Archivo descargado: ${filename}\n💾 Total movimientos: ${movements.length}`);
      
    } catch (error: any) {
      console.error('Error exporting to Excel:', error);
      const errorMessage = extractErrorMessage(error, 'Error al exportar a Excel');
      alert(`❌ Error en exportación: ${errorMessage}`);
    } finally {
      setExporting(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  // Helper function para extraer mensajes de error de manera consistente
  const extractErrorMessage = (error: any, defaultMessage: string = 'Error desconocido'): string => {
    if (!error) return defaultMessage;
    
    console.log('🔍 Debug - Error object structure:', {
      error: error,
      hasResponse: !!error?.response,
      responseStatus: error?.response?.status,
      responseData: error?.response?.data,
      errorMessage: error?.message,
      errorType: typeof error
    });
    
    // Si hay respuesta del servidor
    if (error?.response?.data) {
      const data = error.response.data;
      console.log('🔍 Debug - Response data:', data, 'Type:', typeof data);
      
      if (typeof data === 'string') return data;
      
      // Handle detail field (could be string or array)
      if (data.detail) {
        if (Array.isArray(data.detail)) {
          // FastAPI validation errors come as array of objects
          return data.detail.map((item: any) => {
            if (typeof item === 'string') return item;
            if (item.msg) return `${item.loc ? item.loc.join('.') + ': ' : ''}${item.msg}`;
            return JSON.stringify(item);
          }).join(', ');
        }
        return String(data.detail);
      }
      
      if (data.message) return data.message;
      if (data.error) return data.error;
      
      // Si es un objeto, intentar stringify de manera segura
      try {
        return JSON.stringify(data);
      } catch {
        return `Error object: ${String(data)}`;
      }
    }
    
    // Si hay mensaje directo
    if (error?.message) return error.message;
    if (typeof error === 'string') return error;
    
    // Fallback
    console.log('🔍 Debug - Using fallback message:', defaultMessage);
    return defaultMessage;
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        return dateString;
      }
      return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      });
    } catch (error) {
      return dateString;
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      "Renta": "text-green-700 bg-green-100",
      "Hipoteca": "text-red-700 bg-red-100",
      "Gasto": "text-orange-700 bg-orange-100"
    };
    return colors[category] || "text-gray-700 bg-gray-100";
  };

  // Pagination
  const totalPages = Math.ceil(movements.length / itemsPerPage);
  const paginatedMovements = movements.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Summary calculations
  const totalIncome = movements.filter(m => m.amount > 0).reduce((sum, m) => sum + m.amount, 0);
  const totalExpenses = movements.filter(m => m.amount < 0).reduce((sum, m) => sum + Math.abs(m.amount), 0);
  const netAmount = totalIncome - totalExpenses;

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Action Buttons */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">Gestión de Movimientos</h3>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowNewMovementModal(true)}
            className="btn-primary px-4 py-2 rounded-xl"
          >
            ➕ Nuevo Movimiento
          </button>
          <button
            onClick={handleAnalyzeConcepts}
            disabled={!selectedFile || analyzing}
            className="btn-secondary px-4 py-2 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {analyzing ? '⏳ Analizando...' : '📋 Analizar Conceptos'}
          </button>
          <button
            onClick={() => setShowUploadModal(true)}
            className="bg-green-600 text-white px-4 py-2 rounded-xl hover:bg-green-700"
          >
            📁 Subir Extracto
          </button>
          <button
            onClick={handleBankinterUpdate}
            disabled={updatingBankinter}
            className="bg-orange-600 text-white px-4 py-2 rounded-md hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {updatingBankinter ? '⏳ Actualizando...' : '🏦 Actualizar Bankinter'}
          </button>
          <button
            onClick={handleExportToExcel}
            disabled={exporting || movements.length === 0}
            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {exporting ? '⏳ Exportando...' : '📊 Exportar Excel'}
          </button>
          <button
            onClick={() => setShowDateRangeDeleteModal(true)}
            className="bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700"
          >
            📅 Borrar por Fechas
          </button>
          <button
            onClick={() => setShowDeleteAllModal(true)}
            className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
          >
            🗑️ Borrar Todo
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-card rounded-2xl p-6 border-l-4 border-green-500">
          <p className="text-sm font-medium text-gray-600">💰 Total Ingresos</p>
          <p className="text-3xl font-bold text-green-600 mt-2">{formatCurrency(totalIncome)}</p>
        </div>
        <div className="glass-card rounded-2xl p-6 border-l-4 border-red-500">
          <p className="text-sm font-medium text-gray-600">💸 Total Gastos</p>
          <p className="text-3xl font-bold text-red-600 mt-2">{formatCurrency(totalExpenses)}</p>
        </div>
        <div className="glass-card rounded-2xl p-6 border-l-4 border-blue-500">
          <p className="text-sm font-medium text-gray-600">📊 Cash Flow Neto</p>
          <p className={`text-3xl font-bold mt-2 ${netAmount >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
            {formatCurrency(netAmount)}
          </p>
        </div>
        <div className="glass-card rounded-2xl p-6 border-l-4 border-gray-500">
          <p className="text-sm font-medium text-gray-600">📈 Total Movimientos</p>
          <p className="text-2xl font-bold text-gray-600 mt-2">{movements.length}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="glass-card rounded-2xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {properties.length > 0 && (
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Propiedad</label>
              <select
                value={filters.property_id}
                onChange={(e) => setFilters({...filters, property_id: e.target.value})}
                className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm"
              >
                <option value="">Todas</option>
                <option value="unassigned">Sin asignar</option>
                {properties.map((property) => (
                  <option key={property.id} value={property.id}>
                    {property.address}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Categoría</label>
            <select
              value={filters.category}
              onChange={(e) => setFilters({...filters, category: e.target.value})}
              className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm"
            >
              <option value="">Todas</option>
              <option value="Renta">Renta</option>
              <option value="Hipoteca">Hipoteca</option>
              <option value="Gasto">Gasto</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Fecha Desde</label>
            <input
              type="date"
              value={filters.start_date}
              onChange={(e) => setFilters({...filters, start_date: e.target.value})}
              className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Fecha Hasta</label>
            <input
              type="date"
              value={filters.end_date}
              onChange={(e) => setFilters({...filters, end_date: e.target.value})}
              className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm"
            />
          </div>

          <div className="lg:col-span-2">
            <label className="block text-xs font-medium text-gray-700 mb-1">Buscar</label>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => setFilters({...filters, search: e.target.value})}
              placeholder="Concepto, propiedad, inquilino..."
              className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm"
            />
          </div>
        </div>

        <div className="mt-4 flex justify-between items-center">
          <div className="text-sm text-gray-500">
            Mostrando {paginatedMovements.length} de {movements.length} movimientos
          </div>
          <button
            onClick={() => setFilters({property_id: "", category: "", start_date: "", end_date: "", search: ""})}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Limpiar filtros
          </button>
        </div>
      </div>

      {/* Movements Table */}
      <div className="glass-card rounded-2xl">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Lista de Movimientos</h2>
        </div>
        
        {paginatedMovements.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <p>No hay movimientos para mostrar</p>
            <p className="mt-2 text-sm">
              <button
                onClick={() => setShowNewMovementModal(true)}
                className="text-blue-600 hover:underline"
              >
                Crear primer movimiento
              </button>
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Fecha
                  </th>
                  {properties.length > 0 && (
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Propiedad
                    </th>
                  )}
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Concepto
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Categoría
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Importe
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Saldo
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {paginatedMovements.map((movement) => (
                  <tr key={movement.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {formatDate(movement.date)}
                    </td>
                    {properties.length > 0 && (
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {movement.property_address}
                      </td>
                    )}
                    <td className="px-4 py-3">
                      <div className="text-sm text-gray-900">{movement.concept}</div>
                      {movement.tenant_name && (
                        <div className="text-xs text-gray-500">Inquilino: {movement.tenant_name}</div>
                      )}
                      {movement.subcategory && (
                        <div className="text-xs text-gray-500">Subcategoría: {movement.subcategory}</div>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(movement.category)}`}>
                        {movement.category}
                      </span>
                      {!movement.is_classified && (
                        <div className="text-xs text-orange-600 mt-1">⚠️ Manual</div>
                      )}
                    </td>
                    <td className={`px-4 py-3 text-sm text-right font-medium ${
                      movement.amount >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatCurrency(movement.amount)}
                    </td>
                    <td className="px-4 py-3 text-sm text-right text-gray-600">
                      {movement.bank_balance ? formatCurrency(movement.bank_balance) : '-'}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <div className="flex justify-center space-x-1">
                        <button
                          onClick={() => handleEditMovement(movement)}
                          className="text-blue-600 hover:text-blue-800 text-sm px-2 py-1 rounded"
                          title="Editar movimiento"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => {
                            setSelectedMovement(movement.id);
                            setShowDeleteMovementModal(true);
                          }}
                          className="text-red-600 hover:text-red-800 text-sm px-2 py-1 rounded"
                          title="Eliminar movimiento"
                        >
                          🗑️
                        </button>
                        {!movement.property_id && (
                          <button
                            onClick={() => {
                              setSelectedMovement(movement.id);
                              setShowAssignModal(true);
                            }}
                            className="text-green-600 hover:text-green-800 text-sm px-2 py-1 rounded"
                            title="Asignar a propiedad"
                          >
                            🏠
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
            <div className="text-sm text-gray-500">
              Página {currentPage} de {totalPages}
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setCurrentPage(currentPage - 1)}
                disabled={currentPage === 1}
                className="px-3 py-1 text-sm border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Anterior
              </button>
              <button
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="px-3 py-1 text-sm border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Siguiente
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modals - Add all the modals here as needed */}
      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Subir Extracto Bancario</h3>
            
            <form onSubmit={handleFileUpload} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Archivo Excel (.xls, .xlsx) *
                </label>
                <input
                  type="file"
                  accept=".xls,.xlsx"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  El archivo debe contener columnas: <strong>Fecha</strong>, <strong>Concepto</strong>, <strong>Importe</strong>
                </p>
              </div>

              <div className="flex justify-end space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowUploadModal(false);
                    setSelectedFile(null);
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  disabled={uploading}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={uploading || !selectedFile}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  {uploading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                      <span>Procesando...</span>
                    </>
                  ) : (
                    <>
                      <span>📁</span>
                      <span>Subir Archivo</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete All Modal */}
      {showDeleteAllModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">⚠️ Confirmar Eliminación</h3>
            
            <div className="space-y-4">
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <p className="text-sm text-red-800">
                  <strong>¿Estás seguro de que quieres eliminar TODOS los movimientos?</strong>
                </p>
                <p className="text-sm text-red-600 mt-2">
                  Esta acción no se puede deshacer.
                </p>
              </div>

              <div className="flex justify-end space-x-4 pt-4">
                <button
                  onClick={() => setShowDeleteAllModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  disabled={deleting}
                >
                  Cancelar
                </button>
                <button
                  onClick={handleDeleteAllMovements}
                  disabled={deleting}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  {deleting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                      <span>Eliminando...</span>
                    </>
                  ) : (
                    <>
                      <span>🗑️</span>
                      <span>Eliminar Todo</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Date Range Delete Modal */}
      {showDateRangeDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">📅 Eliminar por Rango de Fechas</h3>
            
            <form onSubmit={handleDeleteByDateRange} className="space-y-4">
              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-4">
                <p className="text-sm text-yellow-800">
                  ⚠️ <strong>Advertencia:</strong> Esta acción eliminará todos los movimientos en el rango de fechas especificado.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Fecha Desde *</label>
                  <input
                    type="date"
                    value={dateRangeDelete.start_date}
                    onChange={(e) => setDateRangeDelete({...dateRangeDelete, start_date: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Fecha Hasta *</label>
                  <input
                    type="date"
                    value={dateRangeDelete.end_date}
                    onChange={(e) => setDateRangeDelete({...dateRangeDelete, end_date: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  />
                </div>
              </div>

              {properties.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Propiedad (Opcional - dejar en blanco para todas)
                  </label>
                  <select
                    value={dateRangeDelete.property_id}
                    onChange={(e) => setDateRangeDelete({...dateRangeDelete, property_id: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="">Todas las propiedades</option>
                    {properties.map((property) => (
                      <option key={property.id} value={property.id}>
                        {property.address}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="flex justify-end space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowDateRangeDeleteModal(false);
                    setDateRangeDelete({ start_date: "", end_date: "", property_id: "" });
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  disabled={deleting}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={deleting || !dateRangeDelete.start_date || !dateRangeDelete.end_date}
                  className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  {deleting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                      <span>Eliminando...</span>
                    </>
                  ) : (
                    <>
                      <span>📅</span>
                      <span>Eliminar por Fechas</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Analyze Concepts Modal */}
      {showAnalyzeConceptsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl mx-4 max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-medium text-gray-900 mb-4">📋 Análisis de Conceptos</h3>
            
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <p className="text-sm text-blue-800">
                  ℹ️ <strong>Análisis completado:</strong> Se encontraron {analyzedConcepts.length} conceptos únicos.
                </p>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full table-auto">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Concepto</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Frecuencia</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Categoría Sugerida</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {analyzedConcepts.map((concept, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-4 py-2 text-sm text-gray-900">{concept.concept || concept.name}</td>
                        <td className="px-4 py-2 text-sm text-gray-600">{concept.frequency || concept.count}</td>
                        <td className="px-4 py-2">
                          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                            concept.suggested_category === 'Renta' ? 'text-green-700 bg-green-100' :
                            concept.suggested_category === 'Hipoteca' ? 'text-red-700 bg-red-100' :
                            'text-orange-700 bg-orange-100'
                          }`}>
                            {concept.suggested_category || 'Sin clasificar'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="flex justify-end space-x-4 pt-4">
                <button
                  onClick={() => setShowAnalyzeConceptsModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cerrar
                </button>
                <button
                  onClick={() => {
                    setShowAnalyzeConceptsModal(false);
                    setShowUploadModal(true);
                  }}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                  Continuar con Subida
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delete Individual Movement Modal */}
      {showDeleteMovementModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">⚠️ Confirmar Eliminación</h3>
            
            <div className="space-y-4">
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <p className="text-sm text-red-800">
                  <strong>¿Estás seguro de que quieres eliminar este movimiento?</strong>
                </p>
                <p className="text-sm text-red-600 mt-2">
                  Esta acción no se puede deshacer.
                </p>
              </div>

              <div className="flex justify-end space-x-4 pt-4">
                <button
                  onClick={() => {
                    setShowDeleteMovementModal(false);
                    setSelectedMovement(null);
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  onClick={() => selectedMovement && handleDeleteMovement(selectedMovement)}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                >
                  Eliminar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* New Movement Modal */}
      {showNewMovementModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Nuevo Movimiento</h3>
            
            <form onSubmit={handleCreateMovement} className="space-y-4">
              {properties.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Propiedad</label>
                  <select
                    value={newMovement.property_id}
                    onChange={(e) => setNewMovement({...newMovement, property_id: Number(e.target.value)})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value={0}>Sin asignar</option>
                    {properties.map((property) => (
                      <option key={property.id} value={property.id}>
                        {property.address}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Fecha</label>
                  <input
                    type="date"
                    value={newMovement.date}
                    onChange={(e) => setNewMovement({...newMovement, date: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Categoría</label>
                  <select
                    value={newMovement.category}
                    onChange={(e) => setNewMovement({...newMovement, category: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  >
                    <option value="Renta">Renta</option>
                    <option value="Hipoteca">Hipoteca</option>
                    <option value="Gasto">Gasto</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Concepto</label>
                <input
                  type="text"
                  value={newMovement.concept}
                  onChange={(e) => setNewMovement({...newMovement, concept: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Descripción del movimiento"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Importe (€)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={newMovement.amount}
                  onChange={(e) => setNewMovement({...newMovement, amount: Number(e.target.value)})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Positivo: ingreso, Negativo: gasto"
                  required
                />
              </div>

              <div className="flex justify-end space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowNewMovementModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Crear Movimiento
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Property Assignment Modal */}
      {showAssignModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">🏠 Asignar Movimiento a Propiedad</h3>
            
            <form onSubmit={handleAssignPropertyToMovement} className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-4">
                <p className="text-sm text-blue-800">
                  ℹ️ <strong>Asignar propiedad:</strong> Este movimiento será asociado a la propiedad seleccionada para análisis financiero.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Seleccionar Propiedad *</label>
                <select
                  value={selectedProperty}
                  onChange={(e) => setSelectedProperty(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                >
                  <option value={0}>Selecciona una propiedad...</option>
                  {properties.map((property) => (
                    <option key={property.id} value={property.id}>
                      {property.address}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowAssignModal(false);
                    setSelectedMovement(null);
                    setSelectedProperty(0);
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={selectedProperty === 0}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  <span>🏠</span>
                  <span>Asignar Propiedad</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}