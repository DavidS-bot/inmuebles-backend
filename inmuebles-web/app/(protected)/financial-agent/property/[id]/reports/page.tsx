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

interface MonthlyData {
  month: string;
  income: number;
  expenses: number;
  net: number;
  movements_count: number;
}

interface MonthlyResponse {
  property_id: number;
  year: number;
  monthly_data: MonthlyData[];
}

export default function PropertyReportsPage() {
  const params = useParams();
  const propertyId = Number(params.id);
  
  const [property, setProperty] = useState<Property | null>(null);
  const [summary, setSummary] = useState<FinancialSummary | null>(null);
  const [monthlyData, setMonthlyData] = useState<MonthlyData[]>([]);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [loading, setLoading] = useState(true);

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
      const summaryRes = await api.get(`/financial-movements/property/${propertyId}/summary?year=${selectedYear}`);
      setSummary(summaryRes.data);

      // Load real monthly data
      try {
        const monthlyRes = await api.get(`/financial-movements/property/${propertyId}/monthly?year=${selectedYear}`);
        console.log("Monthly data response:", monthlyRes.data);
        setMonthlyData(monthlyRes.data.monthly_data);
      } catch (monthlyError) {
        console.error("Error loading monthly data:", monthlyError);
        // Fallback to empty data if monthly endpoint fails
        setMonthlyData([]);
      }

    } catch (error) {
      console.error("Error loading reports:", error);
    } finally {
      setLoading(false);
    }
  };


  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const calculateROI = () => {
    if (!property?.purchase_price || !summary) return 0;
    return (summary.net_cash_flow / property.purchase_price) * 100;
  };

  const calculateMonthlyAverage = (total: number) => {
    if (!monthlyData || monthlyData.length === 0) return total / 12;
    
    // Count months that have actual data (non-zero income or expenses)
    const monthsWithData = monthlyData.filter(month => 
      month.income > 0 || month.expenses > 0 || month.movements_count > 0
    ).length;
    
    return monthsWithData > 0 ? total / monthsWithData : total / 12;
  };

  const getYearOptions = () => {
    const currentYear = new Date().getFullYear();
    return Array.from({ length: 5 }, (_, i) => currentYear - i);
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
      <div className="flex justify-between items-center">
        <div>
          <nav className="text-sm text-gray-500 mb-2">
            <a href="/financial-agent" className="hover:text-blue-600">Agente Financiero</a>
            <span className="mx-2">&gt;</span>
            <a href={`/financial-agent/property/${propertyId}`} className="hover:text-blue-600">
              {property.address}
            </a>
            <span className="mx-2">&gt;</span>
            <span>Informes</span>
          </nav>
          <h1 className="text-3xl font-bold text-gray-900">📊 Informes Financieros</h1>
          <p className="text-gray-600 mt-1">{property.address}</p>
        </div>
        
        <select 
          value={selectedYear} 
          onChange={(e) => setSelectedYear(Number(e.target.value))}
          className="border border-gray-300 rounded-md px-3 py-2"
        >
          {getYearOptions().map(year => (
            <option key={year} value={year}>{year}</option>
          ))}
        </select>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Ingresos Anuales</p>
              <p className="text-2xl font-bold text-green-600">
                {formatCurrency(summary?.total_income || 0)}
              </p>
            </div>
            <div className="text-green-500">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-500">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Gastos Anuales</p>
              <p className="text-2xl font-bold text-red-600">
                {formatCurrency(summary?.total_expenses || 0)}
              </p>
            </div>
            <div className="text-red-500">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
              </svg>
            </div>
          </div>
        </div>

        <div className={`bg-white rounded-lg shadow p-6 border-l-4 ${(summary?.net_cash_flow || 0) >= 0 ? 'border-blue-500' : 'border-orange-500'}`}>
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Cash Flow Neto</p>
              <p className={`text-2xl font-bold ${(summary?.net_cash_flow || 0) >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
                {formatCurrency(summary?.net_cash_flow || 0)}
              </p>
            </div>
            <div className={(summary?.net_cash_flow || 0) >= 0 ? 'text-blue-500' : 'text-orange-500'}>
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">ROI Anual</p>
              <p className={`text-2xl font-bold ${calculateROI() >= 0 ? 'text-purple-600' : 'text-orange-600'}`}>
                {calculateROI().toFixed(1)}%
              </p>
            </div>
            <div className="text-purple-500">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Cash Flow Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">📈 Cash Flow Mensual {selectedYear}</h3>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {monthlyData.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <p>No hay datos mensuales disponibles</p>
                <p className="text-sm mt-2">Puede que no haya movimientos financieros para este año o haya un error cargando los datos.</p>
              </div>
            ) : (
              monthlyData.map((data, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div className="flex flex-col">
                    <span className="text-sm font-medium text-gray-700">{data.month}</span>
                    <span className="text-xs text-gray-500">
                      {data.movements_count} movimientos
                    </span>
                  </div>
                  <div className="flex space-x-4 text-sm">
                    <span className="text-green-600">+{formatCurrency(data.income)}</span>
                    <span className="text-red-600">-{formatCurrency(data.expenses)}</span>
                    <span className={`font-medium ${data.net >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
                      {formatCurrency(data.net)}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Category Breakdown */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">🏷️ Desglose por Categorías</h3>
          <div className="space-y-3">
            {summary?.summary_by_category && Object.entries(summary.summary_by_category).map(([category, data]) => (
              <div key={category} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex items-center">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full mr-3 ${
                    category === 'Renta' ? 'bg-green-100 text-green-700' :
                    category === 'Hipoteca' ? 'bg-red-100 text-red-700' :
                    'bg-orange-100 text-orange-700'
                  }`}>
                    {category}
                  </span>
                  <span className="text-sm text-gray-600">{data.count} movimientos</span>
                </div>
                <span className={`text-sm font-medium ${
                  data.total >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatCurrency(data.total)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Property Details */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">🏠 Información de la Propiedad</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div>
            <p className="text-sm text-gray-600">Tipo</p>
            <p className="font-medium">{property.property_type || 'No especificado'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Habitaciones</p>
            <p className="font-medium">{property.rooms || 'No especificado'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Superficie</p>
            <p className="font-medium">{property.m2 ? `${property.m2}m²` : 'No especificado'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Precio de Compra</p>
            <p className="font-medium">
              {property.purchase_price ? formatCurrency(property.purchase_price) : 'No especificado'}
            </p>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">📋 Métricas Clave {selectedYear}</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <p className="text-2xl font-bold text-blue-600">
              {summary?.total_movements || 0}
            </p>
            <p className="text-sm text-gray-600">Total Movimientos</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <p className="text-2xl font-bold text-green-600">
              {summary?.total_income ? formatCurrency(calculateMonthlyAverage(summary.total_income)) : '€0'}
            </p>
            <p className="text-sm text-gray-600">Ingreso Promedio Mensual</p>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <p className="text-2xl font-bold text-purple-600">
              {summary?.net_cash_flow ? formatCurrency(calculateMonthlyAverage(summary.net_cash_flow)) : '€0'}
            </p>
            <p className="text-sm text-gray-600">Cash Flow Promedio Mensual</p>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end space-x-4">
        <button
          onClick={() => window.print()}
          className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 flex items-center space-x-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
          </svg>
          <span>Imprimir Informe</span>
        </button>
        <button
          onClick={() => alert('Funcionalidad de exportación en desarrollo')}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>Exportar PDF</span>
        </button>
      </div>
    </div>
  );
}