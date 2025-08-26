"use client";
import { useState, useEffect } from "react";
import api from "@/lib/api";

interface Property {
  id: number;
  address: string;
  property_type?: string;
  rooms?: number;
  m2?: number;
  purchase_price?: number;
}

interface FinancialSummary {
  property_id: number;
  total_income: number;
  total_expenses: number;
  net_cash_flow: number;
  total_movements: number;
}

export default function FinancialAgentPage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [summaries, setSummaries] = useState<Record<number, FinancialSummary>>({});
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [selectedYear]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load properties
      const propertiesRes = await api.get("/properties");
      const propertiesData = propertiesRes.data;
      setProperties(propertiesData);

      // Load financial summaries for each property
      const summariesData: Record<number, FinancialSummary> = {};
      for (const property of propertiesData) {
        try {
          const summaryRes = await api.get(
            `/financial-movements/property/${property.id}/summary?year=${selectedYear}`
          );
          summariesData[property.id] = summaryRes.data;
        } catch (error) {
          // Property might not have financial data yet
          summariesData[property.id] = {
            property_id: property.id,
            total_income: 0,
            total_expenses: 0,
            net_cash_flow: 0,
            total_movements: 0
          };
        }
      }
      setSummaries(summariesData);
    } catch (error) {
      console.error("Error loading financial data:", error);
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

  const totalPortfolioIncome = Object.values(summaries).reduce((sum, s) => sum + s.total_income, 0);
  const totalPortfolioExpenses = Object.values(summaries).reduce((sum, s) => sum + s.total_expenses, 0);
  const totalPortfolioCashFlow = totalPortfolioIncome - totalPortfolioExpenses;

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="glass-card rounded-2xl p-8 mb-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              🏛️ Agente Financiero
            </h1>
            <p className="text-gray-600 mt-2 text-lg">Dashboard profesional de análisis financiero inmobiliario</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <a
              href="/dashboard"
              className="flex items-center space-x-2 px-6 py-3 btn-primary text-white rounded-xl font-medium"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2V7zm0 0V6a2 2 0 012-2h6l2 2h6a2 2 0 012 2v1" />
              </svg>
              <span>Dashboard Principal</span>
            </a>
            <select 
              value={selectedYear} 
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              className="glass-card border-0 rounded-xl px-4 py-3 font-medium focus:ring-2 focus:ring-blue-500"
            >
              {[...Array(5)].map((_, i) => {
                const year = new Date().getFullYear() - i;
                return <option key={year} value={year}>{year}</option>
              })}
            </select>
          </div>
        </div>

        
        {/* Traditional Tools Section First */}
        <div className="glass-card rounded-2xl p-6 mb-8">
          <h3 className="text-xl font-bold text-gray-900 mb-6">⚡ Herramientas Tradicionales</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <a
              href="/financial-agent/movements"
              className="group glass-card rounded-xl p-4 hover:scale-105 transition-all duration-300 border border-transparent hover:border-blue-300"
            >
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg mr-3 group-hover:scale-110 transition-transform">
                  <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div>
                  <div className="font-semibold text-gray-900">📊 Movimientos</div>
                  <div className="text-xs text-gray-500">Gestionar extractos</div>
                </div>
              </div>
            </a>

            <a
              href="/financial-agent/contracts"
              className="group glass-card rounded-xl p-4 hover:scale-105 transition-all duration-300 border border-transparent hover:border-green-300"
            >
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg mr-3 group-hover:scale-110 transition-transform">
                  <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <div className="font-semibold text-gray-900">📝 Contratos</div>
                  <div className="text-xs text-gray-500">Gestionar alquileres</div>
                </div>
              </div>
            </a>

            <a
              href="/financial-agent/rules"
              className="group glass-card rounded-xl p-4 hover:scale-105 transition-all duration-300 border border-transparent hover:border-purple-300"
            >
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg mr-3 group-hover:scale-110 transition-transform">
                  <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <div>
                  <div className="font-semibold text-gray-900">⚙️ Reglas</div>
                  <div className="text-xs text-gray-500">Clasificación automática</div>
                </div>
              </div>
            </a>

            <a
              href="/financial-agent/rules/extract"
              className="group glass-card rounded-xl p-4 hover:scale-105 transition-all duration-300 border border-transparent hover:border-orange-300"
            >
              <div className="flex items-center">
                <div className="p-2 bg-orange-100 rounded-lg mr-3 group-hover:scale-110 transition-transform">
                  <svg className="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                  </svg>
                </div>
                <div>
                  <div className="font-semibold text-gray-900">📤 Extractor</div>
                  <div className="text-xs text-gray-500">Procesar archivos</div>
                </div>
              </div>
            </a>
          </div>
        </div>
        
        {/* New Features Access Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <a
            href="/financial-agent/analytics"
            className="group glass-card rounded-xl p-6 hover:scale-105 transition-all duration-300 border-2 border-transparent hover:border-blue-400"
          >
            <div className="flex items-center mb-4">
              <div className="p-3 btn-primary rounded-xl group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">📊 Analytics</h3>
            <p className="text-sm text-gray-600 mb-3">ROI, métricas clave y análisis comparativo de rendimiento</p>
            <div className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full inline-block">✨ Nuevo</div>
          </a>

          <a
            href="/financial-agent/mortgage-calculator"
            className="group glass-card rounded-xl p-6 hover:scale-105 transition-all duration-300 border-2 border-transparent hover:border-purple-400"
          >
            <div className="flex items-center mb-4">
              <div className="p-3 btn-secondary rounded-xl group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">🏦 Calculadora Hipoteca</h3>
            <p className="text-sm text-gray-600 mb-3">Simulador de amortizaciones y análisis de escenarios</p>
            <div className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded-full inline-block">✨ Nuevo</div>
          </a>

          <a
            href="/financial-agent/documents"
            className="group glass-card rounded-xl p-6 hover:scale-105 transition-all duration-300 border-2 border-transparent hover:border-green-400"
          >
            <div className="flex items-center mb-4">
              <div className="p-3 btn-accent rounded-xl group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">📄 Gestor Documentos</h3>
            <p className="text-sm text-gray-600 mb-3">Organización inteligente y alertas automáticas</p>
            <div className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full inline-block">✨ Nuevo</div>
          </a>

          <a
            href="/financial-agent/smart-classifier"
            className="group glass-card rounded-xl p-6 hover:scale-105 transition-all duration-300 border-2 border-transparent hover:border-indigo-400"
          >
            <div className="flex items-center mb-4">
              <div className="p-3 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </div>
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">🎯 Clasificador IA</h3>
            <p className="text-sm text-gray-600 mb-3">Drag & drop inteligente para clasificar movimientos</p>
            <div className="text-xs bg-indigo-100 text-indigo-800 px-2 py-1 rounded-full inline-block">✨ Nuevo</div>
          </a>
        </div>

        {/* Additional Advanced Features */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <a
            href="/financial-agent/notifications"
            className="group glass-card rounded-xl p-6 hover:scale-105 transition-all duration-300 border-2 border-transparent hover:border-yellow-400"
          >
            <div className="flex items-center mb-4">
              <div className="p-3 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-xl group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5zM12 8a4 4 0 100 8 4 4 0 000-8z" />
                </svg>
              </div>
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">🔔 Notificaciones</h3>
            <p className="text-sm text-gray-600 mb-3">Alertas proactivas y oportunidades de ahorro</p>
            <div className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full inline-block">✨ Nuevo</div>
          </a>

          <a
            href="/financial-agent/tax-assistant"
            className="group glass-card rounded-xl p-6 hover:scale-105 transition-all duration-300 border-2 border-transparent hover:border-red-400"
          >
            <div className="flex items-center mb-4">
              <div className="p-3 bg-gradient-to-r from-red-500 to-pink-500 rounded-xl group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">📋 Asistente Fiscal</h3>
            <p className="text-sm text-gray-600 mb-3">Cálculos IRPF y optimización fiscal automática</p>
            <div className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded-full inline-block">✨ Nuevo</div>
          </a>

          <a
            href="/financial-agent/integrations"
            className="group glass-card rounded-xl p-6 hover:scale-105 transition-all duration-300 border-2 border-transparent hover:border-cyan-400"
          >
            <div className="flex items-center mb-4">
              <div className="p-3 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-xl group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
              </div>
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">🔗 Integraciones</h3>
            <p className="text-sm text-gray-600 mb-3">APIs bancarias, seguros y mercado inmobiliario</p>
            <div className="text-xs bg-cyan-100 text-cyan-800 px-2 py-1 rounded-full inline-block">✨ Nuevo</div>
          </a>

          <a
            href="/financial-agent/euribor"
            className="group glass-card rounded-xl p-6 hover:scale-105 transition-all duration-300 border-2 border-transparent hover:border-orange-400"
          >
            <div className="flex items-center mb-4">
              <div className="p-3 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">📈 Tipos Euribor</h3>
            <p className="text-sm text-gray-600 mb-3">Seguimiento automático y proyecciones futuras</p>
            <div className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded-full inline-block">Mejorado</div>
          </a>
        </div>
      </div>

      {/* Portfolio Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="glass-card rounded-2xl p-6 border-l-4 border-green-500">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">💰 Ingresos Totales</p>
              <p className="text-3xl font-bold text-green-600 mt-2">{formatCurrency(totalPortfolioIncome)}</p>
              <p className="text-xs text-gray-500 mt-1">Año {selectedYear}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-xl">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-6 border-l-4 border-red-500">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">💸 Gastos Totales</p>
              <p className="text-3xl font-bold text-red-600 mt-2">{formatCurrency(totalPortfolioExpenses)}</p>
              <p className="text-xs text-gray-500 mt-1">Año {selectedYear}</p>
            </div>
            <div className="p-3 bg-red-100 rounded-xl">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
              </svg>
            </div>
          </div>
        </div>

        <div className={`glass-card rounded-2xl p-6 border-l-4 ${totalPortfolioCashFlow >= 0 ? 'border-blue-500' : 'border-orange-500'}`}>
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">📊 Cash Flow Neto</p>
              <p className={`text-3xl font-bold mt-2 ${totalPortfolioCashFlow >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
                {formatCurrency(totalPortfolioCashFlow)}
              </p>
              <p className="text-xs text-gray-500 mt-1">Año {selectedYear}</p>
            </div>
            <div className={`p-3 rounded-xl ${totalPortfolioCashFlow >= 0 ? 'bg-blue-100' : 'bg-orange-100'}`}>
              <svg className={`w-8 h-8 ${totalPortfolioCashFlow >= 0 ? 'text-blue-600' : 'text-orange-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Properties List */}
      <div className="glass-card rounded-2xl">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">🏠 Propiedades - Análisis Financiero {selectedYear}</h2>
        </div>
        
        {properties.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <p>No hay propiedades registradas.</p>
            <a href="/dashboard/properties" className="text-blue-600 hover:text-blue-800 underline">
              Agregar primera propiedad
            </a>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Propiedad
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ingresos
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Gastos
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cash Flow
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Movimientos
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {properties.map((property) => {
                  const summary = summaries[property.id] || {
                    total_income: 0,
                    total_expenses: 0,
                    net_cash_flow: 0,
                    total_movements: 0
                  };
                  
                  return (
                    <tr key={property.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {property.address}
                          </div>
                          <div className="text-sm text-gray-500">
                            {property.property_type} • {property.rooms} hab • {property.m2}m²
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-green-600 font-medium">
                        {formatCurrency(summary.total_income)}
                      </td>
                      <td className="px-6 py-4 text-sm text-red-600 font-medium">
                        {formatCurrency(summary.total_expenses)}
                      </td>
                      <td className={`px-6 py-4 text-sm font-medium ${summary.net_cash_flow >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
                        {formatCurrency(summary.net_cash_flow)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {summary.total_movements} movimientos
                      </td>
                      <td className="px-6 py-4 text-sm space-x-2">
                        <a
                          href={`/financial-agent/property/${property.id}`}
                          className="text-blue-600 hover:text-blue-800 font-medium"
                        >
                          Ver detalles
                        </a>
                        <span className="text-gray-300">•</span>
                        <a
                          href={`/financial-agent/property/${property.id}/mortgage`}
                          className="text-purple-600 hover:text-purple-800 font-medium"
                        >
                          Hipoteca
                        </a>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}