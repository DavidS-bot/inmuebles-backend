"use client";
import { useState, useEffect } from "react";
import { ChevronDownIcon, ChevronUpIcon } from "@heroicons/react/24/outline";
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

interface PriorityTask {
  id: string;
  title: string;
  description: string;
  urgency: 'high' | 'medium' | 'low';
  icon: string;
  action: string;
  href: string;
}

interface DashboardStats {
  taxSavings: number;
  cashFlow: number;
  roi: number;
  propertiesCount: number;
}

// Loading skeleton component
const StatSkeleton = () => (
  <div className="animate-pulse">
    <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
    <div className="h-12 bg-gray-200 rounded w-32"></div>
  </div>
);

const TaskSkeleton = () => (
  <div className="animate-pulse p-6 border border-gray-200 rounded-xl">
    <div className="h-4 bg-gray-200 rounded w-16 mb-3"></div>
    <div className="h-6 bg-gray-200 rounded w-48 mb-2"></div>
    <div className="h-4 bg-gray-200 rounded w-32 mb-4"></div>
    <div className="h-10 bg-gray-200 rounded w-24"></div>
  </div>
);

export default function FinancialAgentRedesigned() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [summaries, setSummaries] = useState<Record<number, FinancialSummary>>({});
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [loading, setLoading] = useState(true);
  const [showAdvancedTools, setShowAdvancedTools] = useState(false);
  const [showPortfolioDetails, setShowPortfolioDetails] = useState(false);

  const [priorityTasks] = useState<PriorityTask[]>([
    {
      id: '1',
      title: 'Revisar movimientos sin clasificar',
      description: '12 transacciones pendientes de categorización',
      urgency: 'high',
      icon: '🔍',
      action: 'Clasificar ahora',
      href: '/financial-agent/movements?filter=unclassified'
    },
    {
      id: '2', 
      title: 'Actualizar contratos Q4',
      description: '3 contratos próximos a vencer',
      urgency: 'medium',
      icon: '📝',
      action: 'Revisar contratos',
      href: '/financial-agent/contracts?filter=expiring'
    },
    {
      id: '3',
      title: 'Optimizar deducción IRPF',
      description: 'Oportunidad de ahorro fiscal identificada',
      urgency: 'low',
      icon: '💰',
      action: 'Ver detalles',
      href: '/financial-agent/tax-assistant'
    }
  ]);

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

  const calculateStats = (): DashboardStats => {
    const totalIncome = Object.values(summaries).reduce((sum, s) => sum + s.total_income, 0);
    const totalExpenses = Object.values(summaries).reduce((sum, s) => sum + s.total_expenses, 0);
    const cashFlow = totalIncome - totalExpenses;
    
    // Simulación de ahorro fiscal (normalmente vendría del backend)
    const taxSavings = totalExpenses * 0.47; // 47% IRPF estimado
    
    // ROI estimado (necesitaría precio de compra real)
    const totalInvestment = properties.reduce((sum, p) => sum + (p.purchase_price || 0), 0);
    const roi = totalInvestment > 0 ? (cashFlow / totalInvestment) * 100 : 0;
    
    return {
      taxSavings,
      cashFlow,
      roi,
      propertiesCount: properties.length
    };
  };

  const stats = calculateStats();
  
  const getUrgencyColor = (urgency: 'high' | 'medium' | 'low') => {
    switch (urgency) {
      case 'high': return 'border-l-red-500 bg-red-50';
      case 'medium': return 'border-l-yellow-500 bg-yellow-50';
      case 'low': return 'border-l-green-500 bg-green-50';
    }
  };

  const getUrgencyBadge = (urgency: 'high' | 'medium' | 'low') => {
    switch (urgency) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        {/* Hero skeleton */}
        <div className="max-w-7xl mx-auto">
          <div className="bg-white rounded-3xl p-12 shadow-sm mb-8">
            <div className="text-center mb-12">
              <div className="h-20 bg-gray-200 rounded w-96 mx-auto mb-4 animate-pulse"></div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
                <StatSkeleton />
                <StatSkeleton />
                <StatSkeleton />
              </div>
            </div>
          </div>
          
          {/* Tasks skeleton */}
          <div className="bg-white rounded-3xl p-8 shadow-sm">
            <div className="h-8 bg-gray-200 rounded w-64 mb-8 animate-pulse"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <TaskSkeleton />
              <TaskSkeleton />
              <TaskSkeleton />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-8">
        
        {/* HERO SECTION - Simplificada */}
        <div className="bg-white rounded-3xl shadow-sm mb-8 overflow-hidden">
          <div className="p-12 text-center">
            
            {/* Métrica principal gigante */}
            <div className="mb-12">
              <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mb-4">
                {formatCurrency(stats.taxSavings)}
              </h1>
              <p className="text-xl text-gray-600 font-medium">
                ahorrado en impuestos este año
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Gracias a la optimización automática de gastos deducibles
              </p>
            </div>

            {/* KPIs secundarios - Solo 3 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">
                  {formatCurrency(stats.cashFlow)}
                </div>
                <div className="text-sm font-medium text-gray-700">Cash Flow Anual</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-2">
                  {stats.roi.toFixed(1)}%
                </div>
                <div className="text-sm font-medium text-gray-700">ROI Portfolio</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-indigo-600 mb-2">
                  {stats.propertiesCount}
                </div>
                <div className="text-sm font-medium text-gray-700">Propiedades Activas</div>
              </div>
            </div>
            
            {/* Year selector - Más discreto */}
            <div className="mt-8">
              <select 
                value={selectedYear} 
                onChange={(e) => setSelectedYear(Number(e.target.value))}
                className="px-4 py-2 border border-gray-200 rounded-lg text-sm font-medium focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {[...Array(5)].map((_, i) => {
                  const year = new Date().getFullYear() - i;
                  return <option key={year} value={year}>{year}</option>;
                })}
              </select>
            </div>
          </div>
        </div>

        {/* TODAY'S PRIORITIES - Máximo 3 acciones */}
        <div className="bg-white rounded-3xl shadow-sm p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">
              🎯 Prioridades de Hoy
            </h2>
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
              {priorityTasks.filter(task => task.urgency === 'high').length} urgente
            </span>
          </div>

          {priorityTasks.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <div className="text-6xl mb-4">🎉</div>
              <h3 className="text-lg font-medium text-gray-700 mb-2">¡Todo al día!</h3>
              <p className="text-gray-500">No tienes tareas pendientes urgentes</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {priorityTasks.map((task) => (
                <div key={task.id} className={`border-l-4 rounded-xl p-6 ${getUrgencyColor(task.urgency)} transition-all duration-200 hover:shadow-md`}>
                  <div className="flex items-start justify-between mb-3">
                    <span className="text-2xl">{task.icon}</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getUrgencyBadge(task.urgency)}`}>
                      {task.urgency === 'high' ? 'Urgente' : task.urgency === 'medium' ? 'Medio' : 'Bajo'}
                    </span>
                  </div>
                  
                  <h3 className="font-semibold text-gray-900 mb-2">
                    {task.title}
                  </h3>
                  
                  <p className="text-sm text-gray-600 mb-4">
                    {task.description}
                  </p>
                  
                  <a 
                    href={task.href}
                    className={`inline-block px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                      task.urgency === 'high' 
                        ? 'bg-red-600 text-white hover:bg-red-700' 
                        : task.urgency === 'medium'
                        ? 'bg-yellow-600 text-white hover:bg-yellow-700'
                        : 'bg-green-600 text-white hover:bg-green-700'
                    }`}
                  >
                    {task.action}
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* PROGRESSIVE DISCLOSURE - Herramientas Avanzadas */}
        <div className="bg-white rounded-3xl shadow-sm p-8 mb-8">
          <button
            onClick={() => setShowAdvancedTools(!showAdvancedTools)}
            className="flex items-center justify-between w-full text-left mb-4 group"
          >
            <h2 className="text-2xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
              🚀 Herramientas Avanzadas
            </h2>
            {showAdvancedTools ? (
              <ChevronUpIcon className="w-6 h-6 text-gray-400 group-hover:text-blue-600 transition-colors" />
            ) : (
              <ChevronDownIcon className="w-6 h-6 text-gray-400 group-hover:text-blue-600 transition-colors" />
            )}
          </button>

          <div className={`transition-all duration-300 ease-in-out overflow-hidden ${
            showAdvancedTools ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
          }`}>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <a
                href="/financial-agent/analytics"
                className="group p-4 rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all duration-200"
              >
                <div className="text-2xl mb-2">📊</div>
                <div className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">Analytics</div>
                <div className="text-xs text-gray-500">ROI & métricas</div>
              </a>
              
              <a
                href="/financial-agent/mortgage-calculator"
                className="group p-4 rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-md transition-all duration-200"
              >
                <div className="text-2xl mb-2">🧮</div>
                <div className="font-semibold text-gray-900 group-hover:text-purple-600 transition-colors">Calculadora</div>
                <div className="text-xs text-gray-500">Hipotecas</div>
              </a>
              
              <a
                href="/financial-agent/smart-classifier"
                className="group p-4 rounded-xl border border-gray-200 hover:border-indigo-300 hover:shadow-md transition-all duration-200"
              >
                <div className="text-2xl mb-2">🤖</div>
                <div className="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">IA Classifier</div>
                <div className="text-xs text-gray-500">Automático</div>
              </a>
              
              <a
                href="/financial-agent/integrations"
                className="group p-4 rounded-xl border border-gray-200 hover:border-green-300 hover:shadow-md transition-all duration-200"
              >
                <div className="text-2xl mb-2">🔗</div>
                <div className="font-semibold text-gray-900 group-hover:text-green-600 transition-colors">Integraciones</div>
                <div className="text-xs text-gray-500">APIs & Bancos</div>
              </a>
            </div>
          </div>
        </div>

        {/* PROGRESSIVE DISCLOSURE - Detalles del Portfolio */}
        <div className="bg-white rounded-3xl shadow-sm p-8">
          <button
            onClick={() => setShowPortfolioDetails(!showPortfolioDetails)}
            className="flex items-center justify-between w-full text-left mb-4 group"
          >
            <h2 className="text-2xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
              🏠 Portfolio Detallado
            </h2>
            {showPortfolioDetails ? (
              <ChevronUpIcon className="w-6 h-6 text-gray-400 group-hover:text-blue-600 transition-colors" />
            ) : (
              <ChevronDownIcon className="w-6 h-6 text-gray-400 group-hover:text-blue-600 transition-colors" />
            )}
          </button>

          <div className={`transition-all duration-300 ease-in-out overflow-hidden ${
            showPortfolioDetails ? 'max-h-[1000px] opacity-100' : 'max-h-0 opacity-0'
          }`}>
            {properties.length === 0 ? (
              <div className="text-center py-8 mt-6">
                <div className="text-4xl mb-4">🏠</div>
                <h3 className="text-lg font-medium text-gray-700 mb-2">No hay propiedades registradas</h3>
                <p className="text-gray-500 mb-4">Comienza agregando tu primera propiedad</p>
                <a 
                  href="/dashboard/properties" 
                  className="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
                >
                  Agregar Propiedad
                </a>
              </div>
            ) : (
              <div className="mt-6 space-y-4">
                {properties.map((property) => {
                  const summary = summaries[property.id] || {
                    total_income: 0,
                    total_expenses: 0,
                    net_cash_flow: 0,
                    total_movements: 0
                  };
                  
                  return (
                    <div key={property.id} className="border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow duration-200">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900 mb-1">
                            {property.address}
                          </h3>
                          <p className="text-sm text-gray-500 mb-3">
                            {property.property_type} • {property.rooms} hab • {property.m2}m²
                          </p>
                          
                          <div className="grid grid-cols-3 gap-6">
                            <div>
                              <div className="text-sm text-gray-500">Ingresos</div>
                              <div className="text-lg font-semibold text-green-600">
                                {formatCurrency(summary.total_income)}
                              </div>
                            </div>
                            <div>
                              <div className="text-sm text-gray-500">Gastos</div>
                              <div className="text-lg font-semibold text-red-600">
                                {formatCurrency(summary.total_expenses)}
                              </div>
                            </div>
                            <div>
                              <div className="text-sm text-gray-500">Cash Flow</div>
                              <div className={`text-lg font-semibold ${summary.net_cash_flow >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
                                {formatCurrency(summary.net_cash_flow)}
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        <div className="ml-6 flex flex-col space-y-2">
                          <a
                            href={`/financial-agent/property/${property.id}`}
                            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                          >
                            Ver Detalles
                          </a>
                          <a
                            href={`/financial-agent/property/${property.id}/reports`}
                            className="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
                          >
                            Informes
                          </a>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions Floating Button */}
        <div className="fixed bottom-8 right-8">
          <div className="relative">
            <a
              href="/financial-agent/movements"
              className="flex items-center justify-center w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 hover:shadow-xl transition-all duration-200"
              title="Gestionar Movimientos"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}