"use client";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import api from "@/lib/api";

interface Property {
  id: number;
  address: string;
  property_type?: string;
  rooms?: number;
  m2?: number;
  purchase_price?: number;
  purchase_date?: string;
  appraisal_value?: number;
  down_payment?: number;
  acquisition_costs?: number;
  renovation_costs?: number;
  photo?: string | null;
}

interface MortgageDetails {
  id: number;
  property_id: number;
  loan_id?: string;
  bank_entity?: string;
  mortgage_type: string;
  initial_amount: number;
  outstanding_balance: number;
  margin_percentage: number;
  start_date: string;
  end_date: string;
  review_period_months: number;
}

interface FinancialMovement {
  id: number;
  date: string;
  concept: string;
  amount: number;
  category: string;
  subcategory?: string;
  tenant_name?: string;
}

interface FinancialSummary {
  property_id: number;
  year: number;
  summary_by_category: Record<string, { total: number; count: number }>;
  total_income: number;
  total_expenses: number;
  net_cash_flow: number;
  total_movements: number;
}

interface RentalContract {
  id: number;
  tenant_name: string;
  start_date: string;
  end_date?: string;
  monthly_rent: number;
  deposit?: number;
  is_active: boolean;
}

export default function PropertyFinancialDetailsPage() {
  const params = useParams();
  const propertyId = Number(params.id);
  
  const [property, setProperty] = useState<Property | null>(null);
  const [mortgageDetails, setMortgageDetails] = useState<MortgageDetails | null>(null);
  const [summary, setSummary] = useState<FinancialSummary | null>(null);
  const [movements, setMovements] = useState<FinancialMovement[]>([]);
  const [contracts, setContracts] = useState<RentalContract[]>([]);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [activeTab, setActiveTab] = useState<"summary" | "movements" | "contracts" | "details">("movements");
  const [loading, setLoading] = useState(true);
  
  // Editing state
  const [editingProperty, setEditingProperty] = useState(false);
  const [editingMortgage, setEditingMortgage] = useState(false);
  const [propertyForm, setPropertyForm] = useState<Property | null>(null);
  const [mortgageForm, setMortgageForm] = useState<MortgageDetails | null>(null);
  const [saving, setSaving] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  
  // Photo upload state
  const [showPhotoModal, setShowPhotoModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);

  useEffect(() => {
    if (propertyId) {
      loadData();
    }
  }, [propertyId, selectedYear]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load property details
      const propertyRes = await api.get(`/properties/${propertyId}`);
      setProperty(propertyRes.data);

      // Load financial summary
      try {
        const summaryRes = await api.get(
          `/financial-movements/property/${propertyId}/summary?year=${selectedYear}`
        );
        setSummary(summaryRes.data);
      } catch (error) {
        setSummary({
          property_id: propertyId,
          year: selectedYear,
          summary_by_category: {},
          total_income: 0,
          total_expenses: 0,
          net_cash_flow: 0,
          total_movements: 0
        });
      }

      // Load movements
      try {
        const startDate = `${selectedYear}-01-01`;
        const endDate = `${selectedYear}-12-31`;
        const movementsRes = await api.get(
          `/financial-movements?property_id=${propertyId}&start_date=${startDate}&end_date=${endDate}`
        );
        setMovements(movementsRes.data);
      } catch (error) {
        setMovements([]);
      }

      // Load rental contracts
      try {
        const contractsRes = await api.get(
          `/rental-contracts?property_id=${propertyId}`
        );
        setContracts(contractsRes.data);
      } catch (error) {
        setContracts([]);
      }

      // Load mortgage details
      try {
        const mortgageRes = await api.get(
          `/mortgage-details/property/${propertyId}/details`
        );
        setMortgageDetails(mortgageRes.data);
      } catch (error) {
        setMortgageDetails(null);
      }

    } catch (error) {
      console.error("Error loading property data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPhotoPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handlePhotoUpload = async () => {
    if (!selectedFile || !property) return;
    
    setUploadingPhoto(true);
    
    try {
      // Upload photo
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      const photoResponse = await api.post('/uploads/photo', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      // Update property with new photo URL
      await api.put(`/properties/${property.id}`, {
        ...property,
        photo: photoResponse.data.url
      });
      
      // Refresh property data
      await loadData();
      
      // Close modal and reset state
      setShowPhotoModal(false);
      setSelectedFile(null);
      setPhotoPreview(null);
    } catch (error) {
      console.error('Error uploading photo:', error);
      alert('Error al subir la foto');
    } finally {
      setUploadingPhoto(false);
    }
  };

  const removePhoto = () => {
    setSelectedFile(null);
    setPhotoPreview(null);
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

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      "Renta": "text-green-600 bg-green-100",
      "Hipoteca": "text-red-600 bg-red-100",
      "Gasto": "text-orange-600 bg-orange-100"
    };
    return colors[category] || "text-gray-600 bg-gray-100";
  };

  const startEditingProperty = () => {
    if (property) {
      setPropertyForm({...property});
      setEditingProperty(true);
      setValidationErrors({});
      setHasUnsavedChanges(false);
    }
  };

  const startEditingMortgage = () => {
    if (mortgageDetails) {
      setMortgageForm({...mortgageDetails});
      setEditingMortgage(true);
      setValidationErrors({});
      setHasUnsavedChanges(false);
    }
  };

  const cancelPropertyEdit = () => {
    if (hasUnsavedChanges) {
      if (!confirm('Tienes cambios sin guardar. ¿Estás seguro de que quieres cancelar?')) {
        return;
      }
    }
    setEditingProperty(false);
    setPropertyForm(null);
    setValidationErrors({});
    setHasUnsavedChanges(false);
  };

  const cancelMortgageEdit = () => {
    if (hasUnsavedChanges) {
      if (!confirm('Tienes cambios sin guardar. ¿Estás seguro de que quieres cancelar?')) {
        return;
      }
    }
    setEditingMortgage(false);
    setMortgageForm(null);
    setValidationErrors({});
    setHasUnsavedChanges(false);
  };

  const validatePropertyForm = () => {
    if (!propertyForm) return { isValid: false, errors: {} };
    
    const errors: Record<string, string> = {};
    
    if (!propertyForm.address.trim()) {
      errors.address = 'La dirección es obligatoria';
    }
    
    if (propertyForm.purchase_price && propertyForm.purchase_price < 0) {
      errors.purchase_price = 'El precio de compra no puede ser negativo';
    }
    
    if (propertyForm.appraisal_value && propertyForm.appraisal_value < 0) {
      errors.appraisal_value = 'El valor de tasación no puede ser negativo';
    }
    
    if (propertyForm.down_payment && propertyForm.down_payment < 0) {
      errors.down_payment = 'La entrada pagada no puede ser negativa';
    }
    
    if (propertyForm.acquisition_costs && propertyForm.acquisition_costs < 0) {
      errors.acquisition_costs = 'Los gastos de compra no pueden ser negativos';
    }
    
    if (propertyForm.renovation_costs && propertyForm.renovation_costs < 0) {
      errors.renovation_costs = 'Los gastos de renovación no pueden ser negativos';
    }
    
    if (propertyForm.rooms && propertyForm.rooms < 0) {
      errors.rooms = 'El número de habitaciones no puede ser negativo';
    }
    
    if (propertyForm.m2 && propertyForm.m2 < 0) {
      errors.m2 = 'Los metros cuadrados no pueden ser negativos';
    }
    
    return { isValid: Object.keys(errors).length === 0, errors };
  };
  
  const handlePropertyFormChange = (field: keyof Property, value: any) => {
    if (!propertyForm) return;
    
    const newForm = { ...propertyForm, [field]: value };
    setPropertyForm(newForm);
    setHasUnsavedChanges(true);
    
    // Real-time validation
    const validation = validatePropertyForm();
    setValidationErrors(validation.errors);
  };

  const savePropertyChanges = async () => {
    if (!propertyForm || !property) return;
    
    const validation = validatePropertyForm();
    if (!validation.isValid) {
      setValidationErrors(validation.errors);
      const firstError = Object.values(validation.errors)[0];
      alert(firstError);
      return;
    }
    
    setSaving(true);
    try {
      const response = await api.put(`/properties/${property.id}`, propertyForm);
      setProperty(response.data);
      setEditingProperty(false);
      setPropertyForm(null);
      setValidationErrors({});
      setHasUnsavedChanges(false);
    } catch (error) {
      console.error('Error saving property:', error);
      alert('Error al guardar los cambios de la propiedad');
    } finally {
      setSaving(false);
    }
  };

  const validateMortgageForm = () => {
    if (!mortgageForm) return { isValid: false, errors: {} };
    
    const errors: Record<string, string> = {};
    
    if (mortgageForm.outstanding_balance <= 0) {
      errors.outstanding_balance = 'El saldo pendiente debe ser mayor que 0';
    }
    
    if (mortgageForm.margin_percentage < 0) {
      errors.margin_percentage = 'El margen no puede ser negativo';
    }
    
    if (mortgageForm.margin_percentage > 10) {
      errors.margin_percentage = 'El margen parece muy alto. Verifique que es correcto';
    }
    
    if (mortgageForm.review_period_months <= 0) {
      errors.review_period_months = 'El periodo de revisión debe ser mayor que 0';
    }
    
    if (mortgageForm.end_date) {
      const endDate = new Date(mortgageForm.end_date);
      const today = new Date();
      if (endDate < today) {
        errors.end_date = 'La fecha de vencimiento no puede ser anterior a hoy';
      }
    }
    
    return { isValid: Object.keys(errors).length === 0, errors };
  };
  
  const handleMortgageFormChange = (field: keyof MortgageDetails, value: any) => {
    if (!mortgageForm) return;
    
    const newForm = { ...mortgageForm, [field]: value };
    setMortgageForm(newForm);
    setHasUnsavedChanges(true);
    
    // Real-time validation
    const validation = validateMortgageForm();
    setValidationErrors(validation.errors);
  };

  const saveMortgageChanges = async () => {
    if (!mortgageForm || !mortgageDetails) return;
    
    const validation = validateMortgageForm();
    if (!validation.isValid) {
      setValidationErrors(validation.errors);
      const firstError = Object.values(validation.errors)[0];
      alert(firstError);
      return;
    }
    
    setSaving(true);
    try {
      const response = await api.put(`/mortgage-details/${mortgageDetails.id}`, mortgageForm);
      setMortgageDetails(response.data);
      setEditingMortgage(false);
      setMortgageForm(null);
      setValidationErrors({});
      setHasUnsavedChanges(false);
    } catch (error) {
      console.error('Error saving mortgage:', error);
      alert('Error al guardar los cambios de la hipoteca');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!property) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">Propiedad no encontrada</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-start">
          <div className="flex space-x-6">
            {/* Property Photo */}
            <div className="flex-shrink-0">
              <div className="relative group">
                {property.photo ? (
                  <img 
                    src={property.photo.startsWith('http') ? property.photo : `${process.env.NEXT_PUBLIC_API_URL}${property.photo}`}
                    alt={property.address}
                    className="w-32 h-32 rounded-lg object-cover border border-gray-200"
                  />
                ) : (
                  <div className="w-32 h-32 bg-gray-100 rounded-lg flex items-center justify-center border border-gray-200">
                    <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                )}
                <button
                  onClick={() => setShowPhotoModal(true)}
                  className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all"
                >
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </button>
              </div>
            </div>
            
            {/* Property Info */}
            <div>
              <nav className="text-sm text-gray-500 mb-2">
                <a href="/financial-agent" className="hover:text-blue-600">Agente Financiero</a>
                <span className="mx-2">&gt;</span>
                <span>Detalles de Propiedad</span>
              </nav>
              <h1 className="text-3xl font-bold text-gray-900">{property.address}</h1>
              <p className="text-gray-600 mt-1">
                {property.property_type} • {property.rooms} habitaciones • {property.m2}m²
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <select 
              value={selectedYear} 
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              className="border border-gray-300 rounded-md px-3 py-2"
            >
              {[...Array(5)].map((_, i) => {
                const year = new Date().getFullYear() - i;
                return <option key={year} value={year}>{year}</option>
              })}
            </select>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
            <p className="text-sm text-gray-600">Ingresos</p>
            <p className="text-xl font-bold text-green-600">{formatCurrency(summary.total_income)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-red-500">
            <p className="text-sm text-gray-600">Gastos</p>
            <p className="text-xl font-bold text-red-600">{formatCurrency(summary.total_expenses)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
            <p className="text-sm text-gray-600">Cash Flow</p>
            <p className={`text-xl font-bold ${summary.net_cash_flow >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
              {formatCurrency(summary.net_cash_flow)}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-gray-500">
            <p className="text-sm text-gray-600">Movimientos</p>
            <p className="text-xl font-bold text-gray-600">{summary.total_movements}</p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { key: "movements", label: "Movimientos", icon: "💰" },
              { key: "contracts", label: "Contratos", icon: "📄" },
              { key: "details", label: "Detalles Editables", icon: "✏️" },
              { key: "summary", label: "Resumen", icon: "📊" }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                  activeTab === tab.key
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Summary Tab */}
          {activeTab === "summary" && summary && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium">Resumen por Categoría - {selectedYear}</h3>
              
              {Object.keys(summary.summary_by_category).length > 0 ? (
                <div className="grid gap-4">
                  {Object.entries(summary.summary_by_category).map(([category, data]) => (
                    <div key={category} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                      <div className="flex items-center">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getCategoryColor(category)}`}>
                          {category}
                        </span>
                        <span className="ml-3 text-gray-600">{data.count} movimientos</span>
                      </div>
                      <div className="text-lg font-medium">
                        {formatCurrency(data.total)}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p>No hay datos financieros para {selectedYear}</p>
                  <p className="mt-2 text-sm">
                    <a href={`/financial-agent/property/${propertyId}/movements`} className="text-blue-600 hover:underline">
                      Subir extractos bancarios
                    </a>
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Movements Tab */}
          {activeTab === "movements" && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium">Movimientos Financieros - {selectedYear}</h3>
                <a
                  href={`/financial-agent/property/${propertyId}/movements/upload`}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  Subir extractos
                </a>
              </div>
              
              {movements.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse border border-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="border border-gray-200 px-4 py-3 text-left text-sm font-medium text-gray-700">
                          Fecha
                        </th>
                        <th className="border border-gray-200 px-4 py-3 text-left text-sm font-medium text-gray-700">
                          Concepto
                        </th>
                        <th className="border border-gray-200 px-4 py-3 text-left text-sm font-medium text-gray-700">
                          Categoría
                        </th>
                        <th className="border border-gray-200 px-4 py-3 text-right text-sm font-medium text-gray-700">
                          Importe
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {movements.map((movement) => (
                        <tr key={movement.id} className="hover:bg-gray-50">
                          <td className="border border-gray-200 px-4 py-3 text-sm">
                            {formatDate(movement.date)}
                          </td>
                          <td className="border border-gray-200 px-4 py-3 text-sm">
                            <div>{movement.concept}</div>
                            {movement.tenant_name && (
                              <div className="text-xs text-gray-500">Inquilino: {movement.tenant_name}</div>
                            )}
                          </td>
                          <td className="border border-gray-200 px-4 py-3 text-sm">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${getCategoryColor(movement.category)}`}>
                              {movement.category}
                            </span>
                            {movement.subcategory && (
                              <div className="text-xs text-gray-500 mt-1">{movement.subcategory}</div>
                            )}
                          </td>
                          <td className={`border border-gray-200 px-4 py-3 text-sm text-right font-medium ${
                            movement.amount >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {formatCurrency(movement.amount)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p>No hay movimientos para {selectedYear}</p>
                </div>
              )}
            </div>
          )}

          {/* Contracts Tab */}
          {activeTab === "contracts" && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium">📄 Contratos de Alquiler</h3>
                <a
                  href="/financial-agent/contracts"
                  className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
                >
                  + Nuevo Contrato
                </a>
              </div>
              
              {contracts.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Inquilino</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Período</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Renta/Mes</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Depósito</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {contracts.map((contract) => {
                        // Check if contract is expired based on end_date
                        const isExpired = contract.end_date && new Date(contract.end_date) < new Date();
                        const actualStatus = !contract.end_date || (!isExpired && contract.is_active);
                        
                        return (
                          <tr key={contract.id} className="hover:bg-gray-50">
                            <td className="px-4 py-4">
                              <div className="font-medium text-gray-900">{contract.tenant_name}</div>
                            </td>
                            <td className="px-4 py-4 text-sm text-gray-600">
                              <div>{formatDate(contract.start_date)}</div>
                              <div className={isExpired ? "text-red-600 font-medium" : ""}>
                                {contract.end_date ? `hasta ${formatDate(contract.end_date)}` : "Sin fecha fin"}
                              </div>
                            </td>
                            <td className="px-4 py-4 text-sm font-medium text-green-600">
                              {formatCurrency(contract.monthly_rent)}
                            </td>
                            <td className="px-4 py-4 text-sm text-gray-600">
                              {contract.deposit ? formatCurrency(contract.deposit) : "N/A"}
                            </td>
                            <td className="px-4 py-4">
                              <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                                actualStatus
                                  ? "bg-green-100 text-green-800"
                                  : "bg-gray-100 text-gray-800"
                              }`}>
                                {actualStatus ? "Activo" : "Inactivo"}
                              </span>
                            </td>
                            <td className="px-4 py-4 text-sm">
                              <a
                                href="/financial-agent/contracts"
                                className="text-blue-600 hover:text-blue-800"
                              >
                                Ver Detalles
                              </a>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p>No hay contratos registrados para esta propiedad</p>
                  <a
                    href="/financial-agent/contracts"
                    className="text-blue-600 hover:text-blue-800 underline mt-2 inline-block"
                  >
                    Crear primer contrato
                  </a>
                </div>
              )}
            </div>
          )}

          {/* Editable Details Tab */}
          {activeTab === "details" && (
            <div className="space-y-8">
              {/* Property Details Section */}
              <div className="bg-gray-50 rounded-lg p-6">
                <div className="flex justify-between items-center mb-6">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-lg font-semibold text-gray-900">Datos de la Propiedad</h3>
                    {editingProperty && hasUnsavedChanges && (
                      <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">
                        Cambios sin guardar
                      </span>
                    )}
                  </div>
                  {!editingProperty ? (
                    <button
                      onClick={startEditingProperty}
                      className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center space-x-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                      <span>Editar</span>
                    </button>
                  ) : (
                    <div className="flex space-x-2">
                      <button
                        onClick={cancelPropertyEdit}
                        className="bg-gray-500 text-white px-4 py-2 rounded-md hover:bg-gray-600"
                        disabled={saving}
                      >
                        Cancelar
                      </button>
                      <button
                        onClick={savePropertyChanges}
                        disabled={saving}
                        className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50"
                      >
                        {saving ? 'Guardando...' : 'Guardar'}
                      </button>
                    </div>
                  )}
                </div>
                
                {editingProperty && propertyForm ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Dirección</label>
                      <input
                        type="text"
                        value={propertyForm.address}
                        onChange={(e) => handlePropertyFormChange('address', e.target.value)}
                        className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 ${
                          validationErrors.address 
                            ? 'border-red-300 focus:ring-red-500' 
                            : 'border-gray-300 focus:ring-blue-500'
                        }`}
                      />
                      {validationErrors.address && (
                        <p className="mt-1 text-sm text-red-600">{validationErrors.address}</p>
                      )}
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Propiedad</label>
                      <select
                        value={propertyForm.property_type || ''}
                        onChange={(e) => handlePropertyFormChange('property_type', e.target.value || undefined)}
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Seleccionar tipo</option>
                        <option value="Piso">Piso</option>
                        <option value="Casa">Casa</option>
                        <option value="Unifamiliar">Unifamiliar</option>
                        <option value="Local">Local</option>
                        <option value="Oficina">Oficina</option>
                        <option value="Garaje">Garaje</option>
                        <option value="Trastero">Trastero</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Habitaciones</label>
                      <input
                        type="number"
                        value={propertyForm.rooms || ''}
                        onChange={(e) => handlePropertyFormChange('rooms', e.target.value ? parseInt(e.target.value) : undefined)}
                        className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 ${
                          validationErrors.rooms 
                            ? 'border-red-300 focus:ring-red-500' 
                            : 'border-gray-300 focus:ring-blue-500'
                        }`}
                      />
                      {validationErrors.rooms && (
                        <p className="mt-1 text-sm text-red-600">{validationErrors.rooms}</p>
                      )}
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Metros cuadrados</label>
                      <input
                        type="number"
                        value={propertyForm.m2 || ''}
                        onChange={(e) => setPropertyForm({...propertyForm, m2: e.target.value ? parseInt(e.target.value) : undefined})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Fecha de Compra</label>
                      <input
                        type="date"
                        value={propertyForm.purchase_date || ''}
                        onChange={(e) => setPropertyForm({...propertyForm, purchase_date: e.target.value || undefined})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Precio de Compra (€)</label>
                      <input
                        type="number"
                        step="0.01"
                        value={propertyForm.purchase_price || ''}
                        onChange={(e) => handlePropertyFormChange('purchase_price', e.target.value ? parseFloat(e.target.value) : undefined)}
                        className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 ${
                          validationErrors.purchase_price 
                            ? 'border-red-300 focus:ring-red-500' 
                            : 'border-gray-300 focus:ring-blue-500'
                        }`}
                      />
                      {validationErrors.purchase_price && (
                        <p className="mt-1 text-sm text-red-600">{validationErrors.purchase_price}</p>
                      )}
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Valor Tasación (€)</label>
                      <input
                        type="number"
                        step="0.01"
                        value={propertyForm.appraisal_value || ''}
                        onChange={(e) => setPropertyForm({...propertyForm, appraisal_value: e.target.value ? parseFloat(e.target.value) : undefined})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Entrada Pagada (€)</label>
                      <input
                        type="number"
                        step="0.01"
                        value={propertyForm.down_payment || ''}
                        onChange={(e) => setPropertyForm({...propertyForm, down_payment: e.target.value ? parseFloat(e.target.value) : undefined})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Gastos de Compra (€)</label>
                      <input
                        type="number"
                        step="0.01"
                        value={propertyForm.acquisition_costs || ''}
                        onChange={(e) => setPropertyForm({...propertyForm, acquisition_costs: e.target.value ? parseFloat(e.target.value) : undefined})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Gastos de Renovación (€)</label>
                      <input
                        type="number"
                        step="0.01"
                        value={propertyForm.renovation_costs || ''}
                        onChange={(e) => setPropertyForm({...propertyForm, renovation_costs: e.target.value ? parseFloat(e.target.value) : undefined})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-500">Dirección</label>
                        <p className="text-gray-900">{property?.address}</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-500">Tipo de Propiedad</label>
                        <p className="text-gray-900">{property?.property_type || 'No especificado'}</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-500">Habitaciones</label>
                        <p className="text-gray-900">{property?.rooms || 'No especificado'}</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-500">Metros cuadrados</label>
                        <p className="text-gray-900">{property?.m2 ? `${property.m2}m²` : 'No especificado'}</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-500">Fecha de Compra</label>
                        <p className="text-gray-900">{property?.purchase_date ? formatDate(property.purchase_date) : 'No especificada'}</p>
                      </div>
                    </div>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-500">Precio de Compra</label>
                        <p className="text-gray-900 font-semibold">{property?.purchase_price ? formatCurrency(property.purchase_price) : 'No especificado'}</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-500">Valor Tasación</label>
                        <p className="text-gray-900 font-semibold">{property?.appraisal_value ? formatCurrency(property.appraisal_value) : 'No especificado'}</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-500">Entrada Pagada</label>
                        <p className="text-gray-900 font-semibold">{property?.down_payment ? formatCurrency(property.down_payment) : 'No especificado'}</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-500">Gastos de Compra</label>
                        <p className="text-gray-900 font-semibold">{property?.acquisition_costs ? formatCurrency(property.acquisition_costs) : 'No especificados'}</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-500">Gastos de Renovación</label>
                        <p className="text-gray-900 font-semibold">{property?.renovation_costs ? formatCurrency(property.renovation_costs) : 'No especificados'}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Mortgage Details Section */}
              <div className="bg-gray-50 rounded-lg p-6">
                <div className="flex justify-between items-center mb-6">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-lg font-semibold text-gray-900">Datos de la Hipoteca</h3>
                    {editingMortgage && hasUnsavedChanges && (
                      <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">
                        Cambios sin guardar
                      </span>
                    )}
                  </div>
                  {mortgageDetails ? (
                    !editingMortgage ? (
                      <button
                        onClick={startEditingMortgage}
                        className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center space-x-2"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                        <span>Editar</span>
                      </button>
                    ) : (
                      <div className="flex space-x-2">
                        <button
                          onClick={cancelMortgageEdit}
                          className="bg-gray-500 text-white px-4 py-2 rounded-md hover:bg-gray-600"
                          disabled={saving}
                        >
                          Cancelar
                        </button>
                        <button
                          onClick={saveMortgageChanges}
                          disabled={saving}
                          className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50"
                        >
                          {saving ? 'Guardando...' : 'Guardar'}
                        </button>
                      </div>
                    )
                  ) : (
                    <a
                      href={`/financial-agent/property/${propertyId}/mortgage`}
                      className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
                    >
                      Crear Hipoteca
                    </a>
                  )}
                </div>
                
                {mortgageDetails ? (
                  editingMortgage && mortgageForm ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">ID del Préstamo</label>
                        <input
                          type="text"
                          value={mortgageForm.loan_id || ''}
                          onChange={(e) => setMortgageForm({...mortgageForm, loan_id: e.target.value || undefined})}
                          className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Entidad Bancaria</label>
                        <input
                          type="text"
                          value={mortgageForm.bank_entity || ''}
                          onChange={(e) => setMortgageForm({...mortgageForm, bank_entity: e.target.value || undefined})}
                          className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Hipoteca</label>
                        <select
                          value={mortgageForm.mortgage_type}
                          onChange={(e) => setMortgageForm({...mortgageForm, mortgage_type: e.target.value})}
                          className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="Variable">Variable</option>
                          <option value="Fija">Fija</option>
                          <option value="Mixta">Mixta</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Saldo Pendiente (€)</label>
                        <input
                          type="number"
                          step="0.01"
                          value={mortgageForm.outstanding_balance}
                          onChange={(e) => handleMortgageFormChange('outstanding_balance', parseFloat(e.target.value))}
                          className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 ${
                            validationErrors.outstanding_balance 
                              ? 'border-red-300 focus:ring-red-500' 
                              : 'border-gray-300 focus:ring-blue-500'
                          }`}
                        />
                        {validationErrors.outstanding_balance && (
                          <p className="mt-1 text-sm text-red-600">{validationErrors.outstanding_balance}</p>
                        )}
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Margen (%)</label>
                        <input
                          type="number"
                          step="0.01"
                          value={mortgageForm.margin_percentage}
                          onChange={(e) => handleMortgageFormChange('margin_percentage', parseFloat(e.target.value))}
                          className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 ${
                            validationErrors.margin_percentage 
                              ? 'border-red-300 focus:ring-red-500' 
                              : 'border-gray-300 focus:ring-blue-500'
                          }`}
                        />
                        {validationErrors.margin_percentage && (
                          <p className="mt-1 text-sm text-red-600">{validationErrors.margin_percentage}</p>
                        )}
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Fecha de Vencimiento</label>
                        <input
                          type="date"
                          value={mortgageForm.end_date}
                          onChange={(e) => setMortgageForm({...mortgageForm, end_date: e.target.value})}
                          className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Periodo de Revisión (meses)</label>
                        <select
                          value={mortgageForm.review_period_months}
                          onChange={(e) => setMortgageForm({...mortgageForm, review_period_months: parseInt(e.target.value)})}
                          className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value={3}>3 meses</option>
                          <option value={6}>6 meses</option>
                          <option value={12}>12 meses</option>
                        </select>
                      </div>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-500">ID del Préstamo</label>
                          <p className="text-gray-900">{mortgageDetails.loan_id || 'No especificado'}</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Entidad Bancaria</label>
                          <p className="text-gray-900">{mortgageDetails.bank_entity || 'No especificada'}</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Tipo de Hipoteca</label>
                          <p className="text-gray-900">{mortgageDetails.mortgage_type}</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Periodo de Revisión</label>
                          <p className="text-gray-900">{mortgageDetails.review_period_months} meses</p>
                        </div>
                      </div>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Importe Inicial</label>
                          <p className="text-gray-900 font-semibold">{formatCurrency(mortgageDetails.initial_amount)}</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Saldo Pendiente</label>
                          <p className="text-gray-900 font-semibold">{formatCurrency(mortgageDetails.outstanding_balance)}</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Margen</label>
                          <p className="text-gray-900 font-semibold">{mortgageDetails.margin_percentage}%</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Fecha de Vencimiento</label>
                          <p className="text-gray-900">{formatDate(mortgageDetails.end_date)}</p>
                        </div>
                      </div>
                    </div>
                  )
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <p>No hay datos de hipoteca registrados para esta propiedad</p>
                    <p className="mt-2 text-sm">
                      <a href={`/financial-agent/property/${propertyId}/mortgage`} className="text-blue-600 hover:underline">
                        Crear datos de hipoteca
                      </a>
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Acciones</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href={`/financial-agent/property/${propertyId}/mortgage`}
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-purple-300 hover:shadow-md transition-all"
          >
            <div className="text-purple-500 mr-3">🏦</div>
            <div>
              <div className="font-medium">Gestionar Hipoteca</div>
              <div className="text-sm text-gray-500">Cálculos y simulaciones</div>
            </div>
          </a>
          
          <a
            href={`/financial-agent/property/${propertyId}/rules`}
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all"
          >
            <div className="text-blue-500 mr-3">⚙️</div>
            <div>
              <div className="font-medium">Reglas de Clasificación</div>
              <div className="text-sm text-gray-500">Automatizar categorización</div>
            </div>
          </a>
          
          <a
            href={`/financial-agent/property/${propertyId}/reports`}
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-green-300 hover:shadow-md transition-all"
          >
            <div className="text-green-500 mr-3">📊</div>
            <div>
              <div className="font-medium">Informes</div>
              <div className="text-sm text-gray-500">Exportar y analizar</div>
            </div>
          </a>
        </div>
      </div>

      {/* Photo Upload Modal */}
      {showPhotoModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Cambiar Foto de Propiedad</h2>
                <button
                  onClick={() => {
                    setShowPhotoModal(false);
                    removePhoto();
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-4">
                {photoPreview ? (
                  <div className="space-y-3">
                    <div className="relative">
                      <img 
                        src={photoPreview} 
                        alt="Vista previa" 
                        className="w-full h-48 object-cover rounded-lg border border-gray-300"
                      />
                      <button
                        type="button"
                        onClick={removePhoto}
                        className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                    <button
                      type="button"
                      onClick={() => document.getElementById('property-photo-input')?.click()}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm text-gray-700 hover:bg-gray-50"
                    >
                      Seleccionar Otra Foto
                    </button>
                  </div>
                ) : (
                  <div 
                    onClick={() => document.getElementById('property-photo-input')?.click()}
                    className="w-full h-48 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center cursor-pointer hover:border-gray-400 transition-colors"
                  >
                    <div className="text-center">
                      <svg className="w-12 h-12 text-gray-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <p className="text-gray-600">Haz clic para seleccionar una foto</p>
                      <p className="text-sm text-gray-500 mt-1">PNG, JPG hasta 5MB</p>
                    </div>
                  </div>
                )}
                
                <input
                  id="property-photo-input"
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="hidden"
                />

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowPhotoModal(false);
                      removePhoto();
                    }}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handlePhotoUpload}
                    disabled={!selectedFile || uploadingPhoto}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {uploadingPhoto ? "Subiendo..." : "Guardar Foto"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}