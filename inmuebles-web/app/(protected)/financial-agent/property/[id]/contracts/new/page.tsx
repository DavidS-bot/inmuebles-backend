"use client";
import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import api from "@/lib/api";

interface Property {
  id: number;
  address: string;
  property_type?: string;
  rooms?: number;
  m2?: number;
}

export default function NewRentalContractPage() {
  const params = useParams();
  const router = useRouter();
  const propertyId = Number(params.id);
  
  const [property, setProperty] = useState<Property | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string>("");

  // Form data
  const [formData, setFormData] = useState({
    tenant_name: "",
    start_date: "",
    end_date: "",
    monthly_rent: "",
    deposit: ""
  });

  useEffect(() => {
    if (propertyId) {
      loadProperty();
    }
  }, [propertyId]);

  const loadProperty = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/properties/${propertyId}`);
      setProperty(response.data);
    } catch (error) {
      console.error("Error loading property:", error);
      setError("Error al cargar la propiedad");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const contractData = {
        property_id: propertyId,
        tenant_name: formData.tenant_name,
        start_date: formData.start_date,
        end_date: formData.end_date || null,
        monthly_rent: parseFloat(formData.monthly_rent),
        deposit: formData.deposit ? parseFloat(formData.deposit) : null
      };

      await api.post("/rental-contracts", contractData);
      
      // Redirect back to property details
      router.push(`/financial-agent/property/${propertyId}`);
    } catch (error: any) {
      console.error("Error creating contract:", error);
      setError(error?.response?.data?.detail || "Error al crear el contrato");
    } finally {
      setSubmitting(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
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
      <div>
        <nav className="text-sm text-gray-500 mb-2">
          <a href="/financial-agent" className="hover:text-blue-600">Agente Financiero</a>
          <span className="mx-2">&gt;</span>
          <a href={`/financial-agent/property/${propertyId}`} className="hover:text-blue-600">
            {property.address}
          </a>
          <span className="mx-2">&gt;</span>
          <span>Nuevo Contrato</span>
        </nav>
        <h1 className="text-3xl font-bold text-gray-900">📄 Nuevo Contrato de Alquiler</h1>
        <p className="text-gray-600 mt-1">{property.address}</p>
      </div>

      {/* Form */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Información del Contrato</h2>
          <p className="text-sm text-gray-600 mt-1">
            Complete los datos del nuevo contrato de alquiler
          </p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Tenant Information */}
          <div className="space-y-4">
            <h3 className="text-md font-medium text-gray-900">Datos del Inquilino</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nombre del Inquilino *
              </label>
              <input
                type="text"
                value={formData.tenant_name}
                onChange={(e) => handleInputChange("tenant_name", e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Ej: Juan Pérez García"
                required
              />
            </div>
          </div>

          {/* Contract Dates */}
          <div className="space-y-4">
            <h3 className="text-md font-medium text-gray-900">Fechas del Contrato</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Fecha de Inicio *
                </label>
                <input
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => handleInputChange("start_date", e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Fecha de Fin (opcional)
                </label>
                <input
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => handleInputChange("end_date", e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Dejar vacío para contrato indefinido
                </p>
              </div>
            </div>
          </div>

          {/* Financial Information */}
          <div className="space-y-4">
            <h3 className="text-md font-medium text-gray-900">Información Económica</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Renta Mensual (€) *
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.monthly_rent}
                  onChange={(e) => handleInputChange("monthly_rent", e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="1000.00"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Depósito/Fianza (€)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.deposit}
                  onChange={(e) => handleInputChange("deposit", e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="2000.00"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Normalmente 1-2 meses de renta
                </p>
              </div>
            </div>
          </div>

          {/* Property Summary */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-md font-medium text-gray-900 mb-3">Resumen de la Propiedad</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Dirección:</span>
                <p className="font-medium">{property.address}</p>
              </div>
              {property.property_type && (
                <div>
                  <span className="text-gray-600">Tipo:</span>
                  <p className="font-medium">{property.property_type}</p>
                </div>
              )}
              {property.rooms && (
                <div>
                  <span className="text-gray-600">Habitaciones:</span>
                  <p className="font-medium">{property.rooms}</p>
                </div>
              )}
              {property.m2 && (
                <div>
                  <span className="text-gray-600">Superficie:</span>
                  <p className="font-medium">{property.m2}m²</p>
                </div>
              )}
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={() => router.push(`/financial-agent/property/${propertyId}`)}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              disabled={submitting}
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {submitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  <span>Creando...</span>
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span>Crear Contrato</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}