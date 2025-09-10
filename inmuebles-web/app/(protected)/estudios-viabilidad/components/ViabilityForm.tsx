"use client";

import React, { useState } from 'react';
import { X, Calculator, Home, CreditCard, Euro, TrendingUp, AlertCircle } from 'lucide-react';

interface ViabilityFormProps {
  onClose: () => void;
  onStudyCreated: (study: any) => void;
}

export default function ViabilityForm({ onClose, onStudyCreated }: ViabilityFormProps) {
  const [formData, setFormData] = useState({
    study_name: '',
    
    // Datos de compra
    purchase_price: 0,
    property_valuation: 0,
    purchase_taxes_percentage: 0.11,
    renovation_costs: 0,
    real_estate_commission: 0,
    
    // Financiación
    loan_amount: 0,
    interest_rate: 0.035,
    loan_term_years: 25,
    
    // Ingresos
    monthly_rent: 0,
    annual_rent_increase: 0.02,
    
    // Gastos
    community_fees: 0,
    property_tax_ibi: 0,
    life_insurance: 0,
    home_insurance: 0,
    maintenance_percentage: 0.01,
    property_management_fee: 0,
    
    // Riesgo
    vacancy_risk_percentage: 0.05,
    stress_test_rent_decrease: 0.10
  });

  const [activeTab, setActiveTab] = useState('general');
  const [calculating, setCalculating] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [apiError, setApiError] = useState<string>('');

  const tabs = [
    { id: 'general', label: 'General', icon: Home },
    { id: 'compra', label: 'Compra', icon: Home },
    { id: 'financiacion', label: 'Financiación', icon: CreditCard },
    { id: 'ingresos', label: 'Ingresos', icon: Euro },
    { id: 'gastos', label: 'Gastos', icon: TrendingUp }
  ];

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.study_name.trim()) {
      newErrors.study_name = 'El nombre del estudio es obligatorio';
    }
    if (formData.purchase_price <= 0) {
      newErrors.purchase_price = 'El precio de compra debe ser mayor a 0';
    }
    if (formData.loan_amount < 0) {
      newErrors.loan_amount = 'El monto del préstamo no puede ser negativo';
    }
    if (formData.loan_amount >= formData.purchase_price + (formData.renovation_costs || 0) + (formData.real_estate_commission || 0)) {
      newErrors.loan_amount = 'El préstamo no puede ser mayor que el precio total';
    }
    if (formData.interest_rate < 0 || formData.interest_rate > 1) {
      newErrors.interest_rate = 'La tasa de interés debe estar entre 0% y 100%';
    }
    if (formData.monthly_rent <= 0) {
      newErrors.monthly_rent = 'La renta mensual debe ser mayor a 0';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setCalculating(true);
    setApiError('');
    
    try {
      const token = localStorage.getItem('auth_token');
      console.log('API URL:', process.env.NEXT_PUBLIC_API_URL);
      console.log('Token available:', !!token);
      console.log('Form data:', formData);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/viability/`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });
      
      console.log('Response status:', response.status);
      
      if (response.ok) {
        const newStudy = await response.json();
        console.log('Study created successfully:', newStudy);
        onStudyCreated(newStudy);
        onClose();
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Error desconocido' }));
        console.error('Error creating study:', errorData);
        setApiError(`Error ${response.status}: ${errorData.detail || 'No se pudo crear el estudio'}`);
      }
    } catch (error) {
      console.error('Network error:', error);
      setApiError('Error de conexión. Verifica tu conexión a internet.');
    } finally {
      setCalculating(false);
    }
  };

  const updateFormData = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when field is updated
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const calculatePreview = () => {
    const totalPrice = formData.purchase_price + (formData.renovation_costs || 0) + (formData.real_estate_commission || 0);
    const purchaseCosts = formData.purchase_price * formData.purchase_taxes_percentage;
    const totalInvestment = totalPrice + purchaseCosts;
    const downPayment = totalInvestment - formData.loan_amount;
    const ltv = formData.loan_amount / totalInvestment;

    return {
      totalInvestment,
      downPayment,
      ltv,
      grossYield: formData.monthly_rent > 0 ? (formData.monthly_rent * 12) / formData.purchase_price : 0
    };
  };

  const preview = calculatePreview();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b bg-gray-50">
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Calculator className="h-6 w-6 text-blue-600" />
            Nuevo Estudio de Viabilidad
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="flex">
          {/* Sidebar with tabs */}
          <div className="w-64 bg-gray-50 border-r">
            <nav className="p-4">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 mb-2 rounded-lg transition-colors text-left ${
                    activeTab === tab.id
                      ? 'bg-blue-100 text-blue-700 border border-blue-300'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <tab.icon className="h-5 w-5" />
                  {tab.label}
                </button>
              ))}
            </nav>

            {/* Preview Panel */}
            <div className="p-4 border-t">
              <h3 className="font-semibold text-gray-900 mb-3">Vista Previa</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Inversión total:</span>
                  <span className="font-medium">{preview.totalInvestment.toLocaleString()}€</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Entrada:</span>
                  <span className="font-medium">{preview.downPayment.toLocaleString()}€</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">LTV:</span>
                  <span className="font-medium">{(preview.ltv * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Rend. bruto:</span>
                  <span className="font-medium">{(preview.grossYield * 100).toFixed(2)}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Main content */}
          <div className="flex-1">
            <form onSubmit={handleSubmit} className="flex flex-col h-full">
              <div className="flex-1 overflow-y-auto p-6">
                {/* General Tab */}
                {activeTab === 'general' && (
                  <div className="space-y-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Información General</h3>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Nombre del estudio *
                      </label>
                      <input
                        type="text"
                        value={formData.study_name}
                        onChange={(e) => updateFormData('study_name', e.target.value)}
                        className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                          errors.study_name ? 'border-red-300' : 'border-gray-300'
                        }`}
                        placeholder="Ej: Piso Malasaña - Análisis inicial"
                      />
                      {errors.study_name && (
                        <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
                          <AlertCircle className="h-4 w-4" />
                          {errors.study_name}
                        </p>
                      )}
                    </div>

                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h4 className="font-medium text-blue-900 mb-2">¿Qué incluye este análisis?</h4>
                      <ul className="text-sm text-blue-800 space-y-1">
                        <li>• Cálculo automático de cashflow y rentabilidad</li>
                        <li>• Proyección financiera hasta 30 años</li>
                        <li>• Análisis de riesgo y sensibilidad</li>
                        <li>• Comparativa con otros estudios</li>
                        <li>• Métricas de inversión (ROI, LTV, etc.)</li>
                      </ul>
                    </div>
                  </div>
                )}

                {/* Compra Tab */}
                {activeTab === 'compra' && (
                  <div className="space-y-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Datos de Compra</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Precio de compra (€) *
                        </label>
                        <input
                          type="number"
                          value={formData.purchase_price}
                          onChange={(e) => updateFormData('purchase_price', Number(e.target.value))}
                          className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                            errors.purchase_price ? 'border-red-300' : 'border-gray-300'
                          }`}
                          placeholder="200000"
                        />
                        {errors.purchase_price && (
                          <p className="mt-1 text-sm text-red-600">{errors.purchase_price}</p>
                        )}
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Valoración de tasación (€)
                        </label>
                        <input
                          type="number"
                          value={formData.property_valuation}
                          onChange={(e) => updateFormData('property_valuation', Number(e.target.value))}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="210000"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Gastos de compra (%)
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          max="1"
                          value={formData.purchase_taxes_percentage}
                          onChange={(e) => updateFormData('purchase_taxes_percentage', Number(e.target.value))}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                        <p className="mt-1 text-xs text-gray-500">ITP, notaría, registro (típicamente 10-12%)</p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Costos de renovación (€)
                        </label>
                        <input
                          type="number"
                          value={formData.renovation_costs}
                          onChange={(e) => updateFormData('renovation_costs', Number(e.target.value))}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="15000"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Comisión inmobiliaria (€)
                        </label>
                        <input
                          type="number"
                          value={formData.real_estate_commission}
                          onChange={(e) => updateFormData('real_estate_commission', Number(e.target.value))}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="6000"
                        />
                      </div>
                    </div>
                  </div>
                )}

                {/* Financiación Tab */}
                {activeTab === 'financiacion' && (
                  <div className="space-y-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Financiación</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Monto del préstamo (€) *
                        </label>
                        <input
                          type="number"
                          value={formData.loan_amount}
                          onChange={(e) => updateFormData('loan_amount', Number(e.target.value))}
                          className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                            errors.loan_amount ? 'border-red-300' : 'border-gray-300'
                          }`}
                          placeholder="160000"
                        />
                        {errors.loan_amount && (
                          <p className="mt-1 text-sm text-red-600">{errors.loan_amount}</p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Tasa de interés anual
                        </label>
                        <input
                          type="number"
                          step="0.001"
                          min="0"
                          max="1"
                          value={formData.interest_rate}
                          onChange={(e) => updateFormData('interest_rate', Number(e.target.value))}
                          className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                            errors.interest_rate ? 'border-red-300' : 'border-gray-300'
                          }`}
                        />
                        <p className="mt-1 text-xs text-gray-500">
                          Ejemplo: 0.035 para 3.5%. Actual: {(formData.interest_rate * 100).toFixed(2)}%
                        </p>
                        {errors.interest_rate && (
                          <p className="mt-1 text-sm text-red-600">{errors.interest_rate}</p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Plazo del préstamo (años)
                        </label>
                        <select
                          value={formData.loan_term_years}
                          onChange={(e) => updateFormData('loan_term_years', Number(e.target.value))}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value={15}>15 años</option>
                          <option value={20}>20 años</option>
                          <option value={25}>25 años</option>
                          <option value={30}>30 años</option>
                          <option value={35}>35 años</option>
                          <option value={40}>40 años</option>
                        </select>
                      </div>
                    </div>

                    {preview.ltv > 0.8 && (
                      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <div className="flex items-center gap-2">
                          <AlertCircle className="h-5 w-5 text-yellow-600" />
                          <span className="font-medium text-yellow-800">LTV Alto</span>
                        </div>
                        <p className="text-sm text-yellow-700 mt-1">
                          Tu LTV es del {(preview.ltv * 100).toFixed(1)}%. Los bancos suelen requerir LTV máximo del 80%.
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* Ingresos Tab */}
                {activeTab === 'ingresos' && (
                  <div className="space-y-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Ingresos</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Renta mensual (€) *
                        </label>
                        <input
                          type="number"
                          value={formData.monthly_rent}
                          onChange={(e) => updateFormData('monthly_rent', Number(e.target.value))}
                          className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                            errors.monthly_rent ? 'border-red-300' : 'border-gray-300'
                          }`}
                          placeholder="1200"
                        />
                        {errors.monthly_rent && (
                          <p className="mt-1 text-sm text-red-600">{errors.monthly_rent}</p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Incremento anual de renta
                        </label>
                        <input
                          type="number"
                          step="0.001"
                          min="0"
                          max="1"
                          value={formData.annual_rent_increase}
                          onChange={(e) => updateFormData('annual_rent_increase', Number(e.target.value))}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                        <p className="mt-1 text-xs text-gray-500">
                          Ejemplo: 0.02 para 2% anual. Actual: {(formData.annual_rent_increase * 100).toFixed(1)}%
                        </p>
                      </div>
                    </div>

                    {preview.grossYield > 0 && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <h4 className="font-medium text-blue-900 mb-2">Rentabilidad Bruta Estimada</h4>
                        <p className="text-2xl font-bold text-blue-900">{(preview.grossYield * 100).toFixed(2)}%</p>
                        <p className="text-sm text-blue-700 mt-1">
                          Basada en renta anual / precio de compra (sin gastos)
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* Gastos Tab */}
                {activeTab === 'gastos' && (
                  <div className="space-y-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Gastos Anuales</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Gastos de comunidad (€/año)
                        </label>
                        <input
                          type="number"
                          value={formData.community_fees}
                          onChange={(e) => updateFormData('community_fees', Number(e.target.value))}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="1200"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          IBI - Impuesto de bienes inmuebles (€/año) *
                        </label>
                        <input
                          type="number"
                          value={formData.property_tax_ibi}
                          onChange={(e) => updateFormData('property_tax_ibi', Number(e.target.value))}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="800"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Seguro de vida (€/año)
                        </label>
                        <input
                          type="number"
                          value={formData.life_insurance}
                          onChange={(e) => updateFormData('life_insurance', Number(e.target.value))}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="300"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Seguro de hogar (€/año) *
                        </label>
                        <input
                          type="number"
                          value={formData.home_insurance}
                          onChange={(e) => updateFormData('home_insurance', Number(e.target.value))}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="200"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Mantenimiento (% valor propiedad)
                        </label>
                        <input
                          type="number"
                          step="0.001"
                          min="0"
                          max="1"
                          value={formData.maintenance_percentage}
                          onChange={(e) => updateFormData('maintenance_percentage', Number(e.target.value))}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                        <p className="mt-1 text-xs text-gray-500">
                          Típicamente 1%. Actual: {(formData.maintenance_percentage * 100).toFixed(1)}% = {(formData.purchase_price * formData.maintenance_percentage).toLocaleString()}€/año
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Gestión inmobiliaria (€/año)
                        </label>
                        <input
                          type="number"
                          value={formData.property_management_fee}
                          onChange={(e) => updateFormData('property_management_fee', Number(e.target.value))}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="0"
                        />
                        <p className="mt-1 text-xs text-gray-500">Solo si contratas empresa de gestión</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Footer */}
              <div className="p-6 border-t bg-gray-50">
                {apiError && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-center gap-2 text-red-700">
                      <AlertCircle className="h-4 w-4" />
                      <span className="text-sm font-medium">{apiError}</span>
                    </div>
                  </div>
                )}
                
                <div className="flex justify-between items-center">
                  <div className="text-sm text-gray-600">
                    * Campos obligatorios
                  </div>
                  
                  <div className="flex gap-4">
                  <button
                    type="button"
                    onClick={onClose}
                    className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={calculating}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
                  >
                    {calculating ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Calculando...
                      </>
                    ) : (
                      <>
                        <Calculator className="h-4 w-4" />
                        Crear Estudio
                      </>
                    )}
                  </button>
                  </div>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}