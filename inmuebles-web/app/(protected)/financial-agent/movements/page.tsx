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

export default function FinancialMovementsPage() {
  const [movements, setMovements] = useState<MovementWithProperty[]>([]);
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showNewMovementModal, setShowNewMovementModal] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [showDeleteAllModal, setShowDeleteAllModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedProperty, setSelectedProperty] = useState<number>(0);
  const [selectedMovement, setSelectedMovement] = useState<number | null>(null);
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  
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
      const propertiesRes = await api.get("/properties");
      setProperties(propertiesRes.data);

      // Build query params for movements
      const queryParams = new URLSearchParams();
      if (filters.property_id) queryParams.append("property_id", filters.property_id);
      if (filters.category) queryParams.append("category", filters.category);
      if (filters.start_date) queryParams.append("start_date", filters.start_date);
      if (filters.end_date) queryParams.append("end_date", filters.end_date);

      // Load movements
      const movementsRes = await api.get(`/financial-movements?${queryParams.toString()}`);
      
      // Enrich movements with property info
      const enrichedMovements = movementsRes.data.map((movement: FinancialMovement) => {
        const property = propertiesRes.data.find((p: Property) => p.id === movement.property_id);
        return {
          ...movement,
          property_address: property?.address || "Propiedad desconocida"
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

      setMovements(filteredMovements);
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
        property_id: Number(newMovement.property_id),
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

      const response = await api.post('/financial-movements/upload-excel-global', formData);
      const result = response.data;
      
      // Show success message
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
      
      // Close modal and refresh data
      setShowUploadModal(false);
      setSelectedFile(null);
      await loadData();
      
    } catch (error: any) {
      console.error('Error uploading file:', error);
      const errorMessage = error?.response?.data?.detail || 'Error al procesar el archivo Excel';
      alert(`❌ Error: ${errorMessage}`);
    } finally {
      setUploading(false);
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
      let errorMessage = 'Error al eliminar movimientos';
      
      if (error?.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else {
          errorMessage = JSON.stringify(error.response.data.detail);
        }
      }
      
      alert(`❌ Error: ${errorMessage}`);
    } finally {
      setDeleting(false);
    }
  };

  const handleAssignProperty = async () => {
    if (!selectedMovement || !selectedProperty) return;

    try {
      await api.put(`/financial-movements/${selectedMovement}/assign-property`, null, {
        params: { property_id: selectedProperty }
      });
      
      alert('✅ Propiedad asignada exitosamente!');
      setShowAssignModal(false);
      setSelectedMovement(null);
      setSelectedProperty(0);
      await loadData();
      
    } catch (error: any) {
      console.error('Error assigning property:', error);
      const errorMessage = error?.response?.data?.detail || 'Error al asignar propiedad';
      alert(`❌ Error: ${errorMessage}`);
    }
  };

  const handleDeleteMovement = async (movementId: number) => {
    if (!confirm("¿Estás seguro de que quieres eliminar este movimiento?")) {
      return;
    }

    try {
      await api.delete(`/financial-movements/${movementId}`);
      await loadData();
    } catch (error) {
      console.error("Error deleting movement:", error);
      alert("Error al eliminar el movimiento");
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        return dateString; // Return original string if invalid date
      }
      return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      });
    } catch (error) {
      console.error('Error formatting date:', dateString, error);
      return dateString; // Return original string on error
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
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <nav className="text-sm text-gray-500 mb-2">
            <a href="/financial-agent" className="hover:text-blue-600">Agente Financiero</a>
            <span className="mx-2">&gt;</span>
            <span>Movimientos Financieros</span>
          </nav>
          <h1 className="text-3xl font-bold text-gray-900">💰 Movimientos Financieros</h1>
          <p className="text-gray-600 mt-1">Gestión de extractos bancarios y transacciones</p>
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={() => setShowNewMovementModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            + Nuevo Movimiento
          </button>
          <button
            onClick={() => setShowUploadModal(true)}
            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
          >
            📁 Subir Extracto
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
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
          <p className="text-sm text-gray-600">Total Ingresos</p>
          <p className="text-2xl font-bold text-green-600">{formatCurrency(totalIncome)}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-red-500">
          <p className="text-sm text-gray-600">Total Gastos</p>
          <p className="text-2xl font-bold text-red-600">{formatCurrency(totalExpenses)}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
          <p className="text-sm text-gray-600">Neto</p>
          <p className={`text-2xl font-bold ${netAmount >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
            {formatCurrency(netAmount)}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-gray-500">
          <p className="text-sm text-gray-600">Total Movimientos</p>
          <p className="text-2xl font-bold text-gray-600">{movements.length}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Propiedad</label>
            <select
              value={filters.property_id}
              onChange={(e) => setFilters({...filters, property_id: e.target.value})}
              className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm"
            >
              <option value="">Todas</option>
              {properties.map((property) => (
                <option key={property.id} value={property.id}>
                  {property.address}
                </option>
              ))}
            </select>
          </div>

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
      <div className="bg-white rounded-lg shadow">
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
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Fecha
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Propiedad
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Concepto
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Categoría
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Importe
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
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {movement.property_address}
                      </td>
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
                      <td className="px-4 py-3 text-center">
                        <div className="flex justify-center space-x-2">
                          {!movement.property_address || movement.property_address === "Propiedad desconocida" ? (
                            <button
                              onClick={() => {
                                setSelectedMovement(movement.id);
                                setShowAssignModal(true);
                              }}
                              className="text-blue-600 hover:text-blue-800 text-sm"
                              title="Asignar propiedad"
                            >
                              🏠
                            </button>
                          ) : null}
                          <button
                            onClick={() => handleDeleteMovement(movement.id)}
                            className="text-red-600 hover:text-red-800 text-sm"
                            title="Eliminar movimiento"
                          >
                            🗑️
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

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
          </>
        )}
      </div>

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

              <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                <p className="text-sm text-blue-800">
                  ℹ️ Los movimientos se subirán sin asignar a propiedades. Después podrás asignar conceptos específicos a propiedades.
                </p>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
                <p className="text-sm text-yellow-800">
                  🔄 Si ya subiste este archivo antes, los duplicados serán omitidos automáticamente.
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

      {/* New Movement Modal */}
      {showNewMovementModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Nuevo Movimiento</h3>
            
            <form onSubmit={handleCreateMovement} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Propiedad</label>
                <select
                  value={newMovement.property_id}
                  onChange={(e) => setNewMovement({...newMovement, property_id: Number(e.target.value)})}
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

              <div className="grid grid-cols-2 gap-4">
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
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Subcategoría</label>
                  <input
                    type="text"
                    value={newMovement.subcategory}
                    onChange={(e) => setNewMovement({...newMovement, subcategory: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    placeholder="Ej: IBI, Comunidad"
                  />
                </div>
              </div>

              {newMovement.category === "Renta" && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nombre del Inquilino</label>
                  <input
                    type="text"
                    value={newMovement.tenant_name}
                    onChange={(e) => setNewMovement({...newMovement, tenant_name: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    placeholder="Nombre del inquilino (opcional)"
                  />
                </div>
              )}

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
                  Esta acción no se puede deshacer. Se eliminarán todos tus movimientos financieros.
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

      {/* Assign Property Modal */}
      {showAssignModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">🏠 Asignar Propiedad</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Seleccionar Propiedad
                </label>
                <select
                  value={selectedProperty}
                  onChange={(e) => setSelectedProperty(Number(e.target.value))}
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

              <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                <p className="text-sm text-blue-800">
                  💡 El movimiento seleccionado se asignará a esta propiedad.
                </p>
              </div>

              <div className="flex justify-end space-x-4 pt-4">
                <button
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
                  onClick={handleAssignProperty}
                  disabled={!selectedProperty}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Asignar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}