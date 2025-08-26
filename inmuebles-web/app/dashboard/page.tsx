"use client";
import { useState, useEffect } from "react";
import Layout from "@/components/Layout";
import Link from "next/link";
import api from "@/lib/api";

interface Property {
  id: number;
  address: string;
  property_type?: string;
  rooms?: number;
  m2?: number;
  purchase_price?: number;
  photo?: string;
}

interface FinancialStats {
  total_properties: number;
  total_investment: number;
  total_market_value: number;
  total_gross_income: number;
  total_expenses: number;
  total_net_income: number;
  total_equity: number;
  total_debt: number;
}

export default function DashboardPage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [stats, setStats] = useState<FinancialStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load properties
      const propertiesRes = await api.get("/properties");
      const propertiesList = propertiesRes.data;
      setProperties(propertiesList);

      // Calculate weighted averages per property
      let totalGrossIncome = 0;
      let totalExpenses = 0;
      let totalDebt = 0;
      let totalMarketValue = 0;
      
      // Use the same analytics endpoint that Dashboard Analytics uses
      try {
        const currentYear = new Date().getFullYear();
        const analyticsRes = await api.get(`/analytics/portfolio-summary?year=${currentYear}`);
        const portfolioData = analyticsRes.data;
        
        console.log('Portfolio summary data:', portfolioData);
        
        // Extract totals from portfolio summary (same as Analytics dashboard)
        totalGrossIncome = portfolioData.total_income || 0;
        totalExpenses = portfolioData.total_expenses || 0;
        
        console.log(`Analytics totals - Income: ${totalGrossIncome}, Expenses: ${totalExpenses}`);
        
      } catch (e) {
        console.log("Could not load analytics data, falling back to financial movements");
        
        // Fallback to financial movements if analytics endpoint fails
        try {
          const movementsRes = await api.get("/financial-movements");
          const movements = movementsRes.data;
          
          const currentYear = new Date().getFullYear();
          const movements2025 = movements.filter((m: any) => {
            if (!m.date) return false;
            const movementYear = new Date(m.date).getFullYear();
            return movementYear === currentYear;
          });
          
          totalGrossIncome = movements2025
            .filter((m: any) => m.amount > 0)
            .reduce((sum: number, m: any) => sum + m.amount, 0);
          
          totalExpenses = movements2025
            .filter((m: any) => m.amount < 0)
            .reduce((sum: number, m: any) => sum + Math.abs(m.amount), 0);
          
        } catch (e2) {
          console.log("Could not load movements either");
        }
      }

      // Load mortgages for debt - FIXED: use trailing slash endpoint
      try {
        const mortgagesRes = await api.get("/mortgage-details/");
        totalDebt = mortgagesRes.data.reduce((sum: number, m: any) => sum + (m.outstanding_balance || 0), 0);
        console.log(`FIXED: Loaded ${mortgagesRes.data.length} mortgages, total debt: ${totalDebt}`);
      } catch (e) {
        console.log("Could not load mortgages:", e);
      }

      // Calculate totals
      const totalInvestment = propertiesList.reduce(
        (sum: number, p: Property) => sum + (p.purchase_price || 0), 
        0
      );

      // Estimate market value (use purchase price * 1.1 as rough estimate if no current value)
      totalMarketValue = propertiesList.reduce((sum: number, p: any) => {
        return sum + (p.current_value || p.purchase_price * 1.1 || 0);
      }, 0);

      const totalEquity = totalMarketValue - totalDebt;
      const totalNetIncome = totalGrossIncome - totalExpenses;

      setStats({
        total_properties: propertiesList.length,
        total_investment: totalInvestment,
        total_market_value: totalMarketValue,
        total_gross_income: totalGrossIncome,
        total_expenses: totalExpenses,
        total_net_income: totalNetIncome,
        total_equity: totalEquity,
        total_debt: totalDebt
      });

    } catch (error) {
      console.error("Error loading dashboard data:", error);
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

  const quickActions = [
    {
      title: "Nueva Propiedad",
      description: "Agregar una propiedad al portafolio",
      href: "/dashboard/properties",
      icon: "🏠",
      gradient: "from-blue-500 to-blue-600"
    },
    {
      title: "Análisis Financiero",
      description: "Ver detalles financieros y análisis",
      href: "/financial-agent",
      icon: "📊",
      gradient: "from-green-500 to-green-600"
    },
    {
      title: "Contratos",
      description: "Gestionar contratos de alquiler",
      href: "/financial-agent/contracts",
      icon: "📄",
      gradient: "from-purple-500 to-purple-600"
    },
    {
      title: "Movimientos",
      description: "Ver movimientos financieros",
      href: "/financial-agent/movements",
      icon: "💰",
      gradient: "from-orange-500 to-orange-600"
    }
  ];

  if (loading) {
    return (
      <Layout title="Dashboard" subtitle="Cargando información...">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout 
      title="Dashboard Principal" 
      subtitle="Vista general de tu portafolio inmobiliario"
      showBreadcrumbs={false}
    >
      {/* Property background image */}
      <div 
        className="fixed inset-0 opacity-10 z-[-1]"
        style={{
          backgroundImage: 'url(/platon30.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          filter: 'contrast(1.2) brightness(1.1)'
        }}
      />
      {/* Main Financial Summary */}
      <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl p-8 mb-8 border border-gray-100">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent mb-6">
          Resumen Financiero Total
        </h2>
        
        {/* Primary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium uppercase tracking-wide">Valor Total Mercado</p>
                <p className="text-3xl font-bold text-blue-900 mt-2">
                  {formatCurrency(stats?.total_market_value || 0)}
                </p>
                <p className="text-xs text-blue-600 mt-1">Valoración actual estimada</p>
              </div>
              <div className="text-4xl">🏢</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium uppercase tracking-wide">Equity Total</p>
                <p className="text-3xl font-bold text-green-900 mt-2">
                  {formatCurrency(stats?.total_equity || 0)}
                </p>
                <p className="text-xs text-green-600 mt-1">Patrimonio neto</p>
              </div>
              <div className="text-4xl">💎</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium uppercase tracking-wide">Deuda Total</p>
                <p className="text-3xl font-bold text-purple-900 mt-2">
                  {formatCurrency(stats?.total_debt || 0)}
                </p>
                <p className="text-xs text-purple-600 mt-1">Hipotecas pendientes</p>
              </div>
              <div className="text-4xl">🏦</div>
            </div>
          </div>
        </div>

        {/* Secondary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center text-white text-xl">
                🏠
              </div>
              <div className="ml-4">
                <p className="text-xs text-gray-500 uppercase">Propiedades</p>
                <p className="text-xl font-bold text-gray-900">{stats?.total_properties || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center text-white text-xl">
                💰
              </div>
              <div className="ml-4">
                <p className="text-xs text-gray-500 uppercase">Ingresos Totales 2025</p>
                <p className="text-xl font-bold text-gray-900">{formatCurrency(stats?.total_gross_income || 0)}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-red-600 rounded-lg flex items-center justify-center text-white text-xl">
                📊
              </div>
              <div className="ml-4">
                <p className="text-xs text-gray-500 uppercase">Gastos Totales 2025</p>
                <p className="text-xl font-bold text-gray-900">{formatCurrency(stats?.total_expenses || 0)}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-lg flex items-center justify-center text-white text-xl">
                ✨
              </div>
              <div className="ml-4">
                <p className="text-xs text-gray-500 uppercase">Cash Neto Total 2025</p>
                <p className="text-xl font-bold text-gray-900">{formatCurrency(stats?.total_net_income || 0)}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Acciones Rápidas</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action) => (
            <Link 
              key={action.href} 
              href={action.href}
              className="group relative bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100"
            >
              <div className={`absolute inset-0 bg-gradient-to-r ${action.gradient} opacity-0 group-hover:opacity-10 transition-opacity`} />
              <div className="relative p-6">
                <div className="text-3xl mb-3">{action.icon}</div>
                <h4 className="text-lg font-semibold text-gray-900 mb-1">{action.title}</h4>
                <p className="text-sm text-gray-600">{action.description}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Properties */}
      {properties.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Propiedades Recientes</h3>
            <Link href="/dashboard/properties" className="text-sm text-blue-600 hover:text-blue-700 font-medium">
              Ver todas →
            </Link>
          </div>
          <div className="grid gap-3">
            {properties.slice(0, 3).map((property) => (
              <div key={property.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="flex items-center space-x-4">
                  {property.photo ? (
                    <img 
                      src={property.photo.startsWith('http') ? property.photo : `${process.env.NEXT_PUBLIC_API_URL}${property.photo}`}
                      alt={property.address}
                      className="w-12 h-12 rounded-lg object-cover"
                    />
                  ) : (
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center text-white">
                      🏠
                    </div>
                  )}
                  <div>
                    <h4 className="font-medium text-gray-900">{property.address}</h4>
                    <div className="flex items-center space-x-3 text-sm text-gray-500">
                      {property.property_type && <span>{property.property_type}</span>}
                      {property.rooms && <span>{property.rooms} hab</span>}
                      {property.m2 && <span>{property.m2}m²</span>}
                    </div>
                  </div>
                </div>
                <p className="text-lg font-semibold text-gray-900">
                  {formatCurrency(property.purchase_price || 0)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer Message */}
      <div className="text-center mt-8 text-gray-500 text-sm">
        <p>Made in Chaparrito with ❤️</p>
      </div>
    </Layout>
  );
}