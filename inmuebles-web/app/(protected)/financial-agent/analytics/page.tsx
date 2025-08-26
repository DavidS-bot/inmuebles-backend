"use client";
import { useState, useEffect } from "react";
import api from "@/lib/api";
import Layout from '@/components/Layout';

interface PropertyMetrics {
  property: {
    id: number;
    address: string;
    total_investment: number;
    cash_contributed: number;
    initial_debt: number;
    purchase_price: number;
    current_value: number;
  };
  financial_metrics: {
    total_income: number;
    total_expenses: number;
    net_income: number;
    roi_on_cash: number;
    roi_on_investment: number;
    gross_yield_cash: number;
    gross_yield_investment: number;
    monthly_cash_flow: number;
  };
  income_breakdown: {
    rent: number;
    other: number;
  };
  expenses_by_category: Record<string, number>;
  rental_info: {
    active_contract: boolean;
    monthly_rent: number;
    tenant_name: string | null;
    contract_end: string | null;
  };
  mortgage_info: {
    has_mortgage: boolean;
    outstanding_balance: number;
    monthly_payment: number;
    current_rate: number;
    remaining_months: number;
    start_date: string | null;
    end_date: string | null;
  };
}

interface PortfolioSummary {
  total_properties: number;
  total_investment: number;
  total_income: number;
  total_expenses: number;
  total_net_income: number;
  average_roi: number;
  properties_performance: Array<{
    id: number;
    address: string;
    investment: number;
    total_investment: number;
    income: number;
    expenses: number;
    net_income: number;
    roi: number;
  }>;
}

export default function AnalyticsPage() {
  const [portfolioData, setPortfolioData] = useState<PortfolioSummary | null>(null);
  const [properties, setProperties] = useState<any[]>([]);
  const [selectedProperty, setSelectedProperty] = useState<number | null>(null);
  const [propertyMetrics, setPropertyMetrics] = useState<PropertyMetrics | null>(null);
  const [marketData, setMarketData] = useState<any[]>([]);
  const [allPropertyMetrics, setAllPropertyMetrics] = useState<PropertyMetrics[]>([]);
  const [year, setYear] = useState(new Date().getFullYear());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPortfolioSummary();
    fetchProperties();
    fetchMarketData();
    fetchAllPropertyMetrics();
  }, [year]);

  useEffect(() => {
    if (selectedProperty) {
      fetchPropertyMetrics(selectedProperty);
    }
  }, [selectedProperty, year]);

  useEffect(() => {
    if (properties.length > 0) {
      fetchAllPropertyMetrics();
    }
  }, [properties, year]);

  const fetchPortfolioSummary = async () => {
    try {
      const response = await api.get(`/analytics/portfolio-summary?year=${year}`);
      setPortfolioData(response.data);
    } catch (error) {
      console.error("Error fetching portfolio summary:", error);
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
    } finally {
      setLoading(false);
    }
  };

  const fetchMarketData = async () => {
    try {
      const response = await fetch('http://localhost:8000/integrations/market-prices');
      const result = await response.json();
      setMarketData(result.market_data || []);
    } catch (error) {
      console.error("Error fetching market data:", error);
    }
  };

  const fetchAllPropertyMetrics = async () => {
    try {
      if (properties.length > 0) {
        console.log("Fetching metrics for", properties.length, "properties");
        const metricsPromises = properties.map(async (property) => {
          try {
            console.log(`Fetching metrics for property ${property.id}`);
            const response = await api.get(`/analytics/dashboard/${property.id}?year=${year}`);
            console.log(`Received metrics for property ${property.id}:`, response.data);
            return response.data;
          } catch (error) {
            console.error(`Error fetching metrics for property ${property.id}:`, error);
            return null;
          }
        });
        
        const allMetrics = await Promise.all(metricsPromises);
        const validMetrics = allMetrics.filter(m => m !== null);
        console.log("Valid metrics received:", validMetrics.length);
        setAllPropertyMetrics(validMetrics);
      }
    } catch (error) {
      console.error("Error fetching all property metrics:", error);
    }
  };

  const fetchPropertyMetrics = async (propertyId: number) => {
    try {
      const response = await api.get(`/analytics/dashboard/${propertyId}?year=${year}`);
      setPropertyMetrics(response.data);
    } catch (error) {
      console.error("Error fetching property metrics:", error);
    }
  };

  const formatCurrency = (amount: number | undefined) => {
    if (amount === undefined || amount === null || isNaN(amount)) {
      return '€0,00';
    }
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const formatPercentage = (value: number | undefined) => {
    if (value === undefined || value === null || isNaN(value)) {
      return '0.00%';
    }
    return `${value.toFixed(2)}%`;
  };

  const getMarketValuation = (propertyId: number, propertyAddress: string) => {
    const marketInfo = marketData.find(data => 
      data.property_id === propertyId || 
      data.address?.toLowerCase().includes(propertyAddress.toLowerCase())
    );
    
    return {
      value: marketInfo?.estimated_value || 0,
      source: marketInfo?.source || 'Fotocasa',
      date: marketInfo?.last_updated || '2024-12-01',
      trend: marketInfo?.market_trend || 'stable'
    };
  };

  if (loading) {
    return <div className="p-6">Cargando analytics...</div>;
  }

  // Calculate totals from all properties using individual property metrics
  const calculateTotals = () => {
    let totalValue = 0;
    let totalDebt = 0;
    
    console.log("=== DEBUG CALCULATE TOTALS ===");
    console.log("allPropertyMetrics length:", allPropertyMetrics.length);
    console.log("portfolioData properties_performance:", portfolioData?.properties_performance?.length);
    console.log("properties length:", properties.length);
    
    if (allPropertyMetrics.length > 0) {
      // Use actual property metrics with mortgage info
      console.log("Using allPropertyMetrics for calculations");
      for (const metrics of allPropertyMetrics) {
        console.log(`Property ${metrics.property.id}:`, {
          has_mortgage: metrics.mortgage_info?.has_mortgage,
          outstanding_balance: metrics.mortgage_info?.outstanding_balance,
          initial_debt: metrics.property.initial_debt
        });
        
        // Get current property value (use market valuation or fallback to property value)
        const marketValuation = getMarketValuation(metrics.property.id, metrics.property.address);
        const currentValue = marketValuation.value || metrics.property.current_value || metrics.property.total_investment;
        
        totalValue += currentValue || 0;
        
        // Use actual outstanding balance from individual property mortgage info
        if (metrics.mortgage_info?.has_mortgage && metrics.mortgage_info.outstanding_balance > 0) {
          console.log(`Adding debt: ${metrics.mortgage_info.outstanding_balance}`);
          totalDebt += metrics.mortgage_info.outstanding_balance;
        } else if (metrics.property.initial_debt && metrics.property.initial_debt > 0) {
          // Fallback to initial debt if outstanding balance not available
          console.log(`Using initial debt as fallback: ${metrics.property.initial_debt}`);
          totalDebt += metrics.property.initial_debt;
        }
      }
    } else if (portfolioData?.properties_performance) {
      // Fallback to portfolio data if individual metrics not available
      console.log("Using portfolioData fallback for calculations");
      for (const prop of portfolioData.properties_performance) {
        const marketValuation = getMarketValuation(prop.id, prop.address);
        const currentValue = marketValuation.value || prop.current_value || prop.total_investment || prop.investment;
        
        totalValue += currentValue || 0;
        
        // Get property from properties array for debt info
        const property = properties.find(p => p.id === prop.id);
        console.log(`Property ${prop.id} debt info:`, property?.initial_debt);
        if (property?.initial_debt && property.initial_debt > 0) {
          console.log(`Adding debt from property: ${property.initial_debt}`);
          totalDebt += property.initial_debt;
        }
      }
    }
    
    console.log("Final totals:", { totalValue, totalDebt });
    console.log("=== END DEBUG ===");
    
    // Equity = Total Value - Total Debt (correct formula)
    const totalEquity = totalValue - totalDebt;
    
    return { totalValue, totalEquity, totalDebt };
  };
  
  const totals = calculateTotals();

  return (
    <Layout
      title="Dashboard de Analytics"
      subtitle="Análisis financiero detallado de tu cartera inmobiliaria"
      breadcrumbs={[
        { label: 'Agente Financiero', href: '/financial-agent' },
        { label: 'Analytics', href: '/financial-agent/analytics' }
      ]}
      actions={
        <select
          value={year}
          onChange={(e) => setYear(Number(e.target.value))}
          className="border rounded px-3 py-2"
        >
          {[2024, 2025, 2026].map(y => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
      }
    >
      <div className="space-y-6">
      
      {/* New Total Summary Header with better contrast */}
      <div className="bg-gradient-to-r from-teal-600 to-teal-700 text-white rounded-lg p-6 shadow-lg">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-white">📊 Resumen Total del Portfolio</h2>
          <button
            onClick={() => window.location.href = '/financial-agent'}
            className="bg-white text-teal-700 hover:bg-gray-100 px-4 py-2 rounded-lg text-sm font-medium transition-all shadow-md border border-gray-200"
          >
            ← Volver a Propiedades
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center bg-white rounded-lg p-4 border border-gray-200 shadow-md">
            <div className="flex items-center justify-center mb-2">
              <span className="text-2xl mr-2">🏠</span>
              <h3 className="text-sm font-medium text-gray-700">Valor Total Propiedades</h3>
            </div>
            <p className="text-3xl font-bold text-gray-900">{formatCurrency(totals.totalValue)}</p>
            <p className="text-xs text-gray-500 mt-1">Valor actual de mercado</p>
          </div>
          <div className="text-center bg-white rounded-lg p-4 border border-gray-200 shadow-md">
            <div className="flex items-center justify-center mb-2">
              <span className="text-2xl mr-2">💎</span>
              <h3 className="text-sm font-medium text-gray-700">Equity Total</h3>
            </div>
            <p className="text-3xl font-bold text-gray-900">{formatCurrency(totals.totalEquity)}</p>
            <p className="text-xs text-gray-500 mt-1">Valor - Deuda pendiente</p>
            <div className="mt-2">
              <span className="text-xs bg-green-500 text-white px-2 py-1 rounded font-medium">
                {totals.totalValue > 0 ? ((totals.totalEquity / totals.totalValue) * 100).toFixed(1) : 0}% del valor total
              </span>
            </div>
          </div>
          <div className="text-center bg-white rounded-lg p-4 border border-gray-200 shadow-md">
            <div className="flex items-center justify-center mb-2">
              <span className="text-2xl mr-2">🏦</span>
              <h3 className="text-sm font-medium text-gray-700">Deuda Total</h3>
            </div>
            <p className="text-3xl font-bold text-gray-900">{formatCurrency(totals.totalDebt)}</p>
            <p className="text-xs text-gray-500 mt-1">Saldo pendiente hipotecas</p>
            <div className="mt-2">
              <span className="text-xs bg-orange-500 text-white px-2 py-1 rounded font-medium">
                {totals.totalValue > 0 ? ((totals.totalDebt / totals.totalValue) * 100).toFixed(1) : 0}% del valor total
              </span>
            </div>
          </div>
        </div>
        
        {/* Quick ratio indicators with better contrast */}
        <div className="mt-6 pt-4 border-t border-white border-opacity-30">
          <div className="flex justify-center space-x-8 text-center">
            <div className="bg-white px-4 py-2 rounded shadow-md border border-gray-200">
              <p className="text-xs text-gray-600">Ratio Deuda/Valor</p>
              <p className="font-bold text-gray-900 text-lg">{totals.totalValue > 0 ? ((totals.totalDebt / totals.totalValue) * 100).toFixed(1) : 0}%</p>
            </div>
            <div className="bg-white px-4 py-2 rounded shadow-md border border-gray-200">
              <p className="text-xs text-gray-600">Apalancamiento</p>
              <p className="font-bold text-gray-900 text-lg">
                {totals.totalEquity > 0 ? (totals.totalDebt / totals.totalEquity).toFixed(2) : 0}x
              </p>
            </div>
            <div className="bg-white px-4 py-2 rounded shadow-md border border-gray-200">
              <p className="text-xs text-gray-600">Total Propiedades</p>
              <p className="font-bold text-gray-900 text-lg">{portfolioData?.total_properties || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Portfolio Summary */}
      {portfolioData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-600">Total Propiedades</h3>
            <p className="text-2xl font-bold">{portfolioData.total_properties}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-600">Inversión Total</h3>
            <p className="text-2xl font-bold">{formatCurrency(portfolioData.total_investment)}</p>
            <p className="text-xs text-gray-500 mt-1">*Precio compra + 10% proxy (impuestos/gastos)</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-600">Ingresos Netos</h3>
            <p className="text-2xl font-bold text-green-600">{formatCurrency(portfolioData.total_net_income)}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-600">ROI sobre cash promedio</h3>
            <p className="text-2xl font-bold text-blue-600">{formatPercentage(portfolioData?.average_roi)}</p>
          </div>
        </div>
      )}

      {/* Property Performance Table */}
      {portfolioData && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold">Rendimiento por Propiedad</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left">Inversión</th>
                  <th className="px-4 py-2 text-right">Valor Actual</th>
                  <th className="px-4 py-2 text-right">Equity</th>
                  <th className="px-4 py-2 text-right">Ingresos</th>
                  <th className="px-4 py-2 text-right">Gastos</th>
                  <th className="px-4 py-2 text-right">Neto</th>
                  <th className="px-4 py-2 text-right">ROI sobre Cash</th>
                  <th className="px-4 py-2 text-center">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {portfolioData.properties_performance.map((prop) => {
                  // Get market valuation from integrations
                  const marketValuation = getMarketValuation(prop.id, prop.address);
                  const currentValue = marketValuation.value || prop.current_value || prop.total_investment || prop.investment;
                  const investment = prop.total_investment || prop.investment;
                  const equity = currentValue - investment;
                  
                  return (
                    <tr key={prop.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-2">
                        <div>
                          <div className="font-medium">{prop.address}</div>
                          <div className="text-sm text-gray-500">{formatCurrency(investment)}</div>
                        </div>
                      </td>
                      <td className="px-4 py-2 text-right">
                        <div className="font-medium">{formatCurrency(currentValue)}</div>
                        <div className="text-xs text-gray-500">
                          {marketValuation.source} - {new Date(marketValuation.date).toLocaleDateString('es-ES')}
                        </div>
                      </td>
                      <td className={`px-4 py-2 text-right font-medium ${equity >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(equity)}
                      </td>
                      <td className="px-4 py-2 text-right text-green-600">{formatCurrency(prop.income)}</td>
                      <td className="px-4 py-2 text-right text-red-600">{formatCurrency(prop.expenses)}</td>
                      <td className="px-4 py-2 text-right font-medium">{formatCurrency(prop.net_income)}</td>
                      <td className="px-4 py-2 text-right font-medium">{formatPercentage(prop?.roi)}</td>
                      <td className="px-4 py-2 text-center">
                        <button
                          onClick={() => setSelectedProperty(prop.id)}
                          className="text-blue-600 hover:underline"
                        >
                          Ver detalles
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Property Details */}
      {selectedProperty && propertyMetrics && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold">
              Análisis Detallado - {propertyMetrics.property.address}
            </h2>
          </div>
          <div className="p-4 space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded">
                <h4 className="font-medium text-blue-900">ROI sobre Cash</h4>
                <p className="text-2xl font-bold text-blue-600">
                  {formatPercentage(propertyMetrics?.financial_metrics?.roi_on_cash)}
                </p>
                <p className="text-xs text-blue-700">Rentabilidad real sobre capital aportado</p>
              </div>
              <div className="bg-green-50 p-4 rounded">
                <h4 className="font-medium text-green-900">Rentabilidad Bruta</h4>
                <p className="text-2xl font-bold text-green-600">
                  {formatPercentage(propertyMetrics?.financial_metrics?.gross_yield_cash)}
                </p>
                <p className="text-xs text-green-700">Sobre cash aportado</p>
              </div>
              <div className="bg-purple-50 p-4 rounded">
                <h4 className="font-medium text-purple-900">Cash Flow Mensual</h4>
                <p className="text-2xl font-bold text-purple-600">
                  {formatCurrency(propertyMetrics?.financial_metrics?.monthly_cash_flow)}
                </p>
                <p className="text-xs text-purple-700">Neto después de gastos</p>
              </div>
            </div>

            {/* Comparación ROI */}
            <div className="bg-gray-50 p-4 rounded mb-6">
              <h4 className="font-medium mb-3">Comparación de Rentabilidades</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm">ROI sobre cash aportado:</span>
                    <span className="font-bold text-blue-600">{formatPercentage(propertyMetrics?.financial_metrics?.roi_on_cash)}</span>
                  </div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm">ROI sobre inversión total:</span>
                    <span className="font-bold text-gray-600">{formatPercentage(propertyMetrics?.financial_metrics?.roi_on_investment)}</span>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm">Cash aportado:</span>
                    <span className="font-bold text-blue-600">{formatCurrency(propertyMetrics?.property?.cash_contributed)}</span>
                  </div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm">Inversión total:</span>
                    <span className="font-bold text-gray-600">{formatCurrency(propertyMetrics?.property?.total_investment)}</span>
                  </div>
                  <div className="text-xs text-gray-500 mt-2">
                    *Inversión total = Precio compra + 10% proxy (impuestos/gastos)
                  </div>
                  <div className="text-xs text-gray-500">
                    *Cash aportado = Precio compra - Importe inicial hipoteca
                  </div>
                </div>
              </div>
            </div>

            {/* Income vs Expenses */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium mb-3">Desglose de Ingresos</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Rentas:</span>
                    <span className="font-medium">{formatCurrency(propertyMetrics?.income_breakdown?.rent)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Otros:</span>
                    <span className="font-medium">{formatCurrency(propertyMetrics?.income_breakdown?.other)}</span>
                  </div>
                  <div className="border-t pt-2 flex justify-between font-semibold">
                    <span>Total:</span>
                    <span>{formatCurrency(propertyMetrics?.financial_metrics?.total_income)}</span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-3">Gastos por Categoría</h4>
                <div className="space-y-2">
                  {Object.entries(propertyMetrics.expenses_by_category).map(([category, amount]) => (
                    <div key={category} className="flex justify-between">
                      <span>{category}:</span>
                      <span className="font-medium">{formatCurrency(amount)}</span>
                    </div>
                  ))}
                  <div className="border-t pt-2 flex justify-between font-semibold">
                    <span>Total:</span>
                    <span>{formatCurrency(propertyMetrics?.financial_metrics?.total_expenses)}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Property Info */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h4 className="font-medium mb-3">Valoración de Mercado</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Propiedad:</span>
                    <span className="font-medium">{propertyMetrics.property.address}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Valor actual:</span>
                    <span className="font-medium text-green-600">
                      {formatCurrency(getMarketValuation(propertyMetrics.property.id, propertyMetrics.property.address).value || propertyMetrics.property.current_value)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Fuente:</span>
                    <span className="font-medium">{getMarketValuation(propertyMetrics.property.id, propertyMetrics.property.address).source}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Fecha valoración:</span>
                    <span className="font-medium">{new Date(getMarketValuation(propertyMetrics.property.id, propertyMetrics.property.address).date).toLocaleDateString('es-ES')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Tendencia:</span>
                    <span className={`font-medium ${
                      getMarketValuation(propertyMetrics.property.id, propertyMetrics.property.address).trend === 'up' ? 'text-green-600' :
                      getMarketValuation(propertyMetrics.property.id, propertyMetrics.property.address).trend === 'down' ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      {getMarketValuation(propertyMetrics.property.id, propertyMetrics.property.address).trend === 'up' ? '↗️ Subida' :
                       getMarketValuation(propertyMetrics.property.id, propertyMetrics.property.address).trend === 'down' ? '↘️ Bajada' : '→ Estable'}
                    </span>
                  </div>
                </div>
              </div>
              <div>
                <h4 className="font-medium mb-3">Información de Alquiler</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Estado:</span>
                    <span className={`font-medium ${propertyMetrics?.rental_info?.active_contract ? 'text-green-600' : 'text-red-600'}`}>
                      {propertyMetrics?.rental_info?.active_contract ? 'Ocupado' : 'Vacío'}
                    </span>
                  </div>
                  {propertyMetrics?.rental_info?.active_contract && (
                    <>
                      <div className="flex justify-between">
                        <span>Inquilino:</span>
                        <span className="font-medium">{propertyMetrics.rental_info.tenant_name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Renta mensual:</span>
                        <span className="font-medium">{formatCurrency(propertyMetrics?.rental_info?.monthly_rent)}</span>
                      </div>
                      {propertyMetrics.rental_info.contract_end && (
                        <div className="flex justify-between">
                          <span>Fin contrato:</span>
                          <span className="font-medium">{new Date(propertyMetrics.rental_info.contract_end).toLocaleDateString()}</span>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>

              {propertyMetrics.mortgage_info.has_mortgage && (
                <div>
                  <h4 className="font-medium mb-3">Información Hipoteca</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Saldo pendiente:</span>
                      <span className="font-medium">{formatCurrency(propertyMetrics?.mortgage_info?.outstanding_balance)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Cuota mensual:</span>
                      <span className="font-medium">{formatCurrency(propertyMetrics?.mortgage_info?.monthly_payment)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Tipo actual:</span>
                      <span className="font-medium">{formatPercentage(propertyMetrics?.mortgage_info?.current_rate)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Meses restantes:</span>
                      <span className="font-medium">{propertyMetrics?.mortgage_info?.remaining_months || 0} meses</span>
                    </div>
                    {propertyMetrics?.mortgage_info?.end_date && (
                      <div className="flex justify-between">
                        <span>Fin hipoteca:</span>
                        <span className="font-medium">{new Date(propertyMetrics?.mortgage_info?.end_date || '').toLocaleDateString()}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      </div>
    </Layout>
  );
}