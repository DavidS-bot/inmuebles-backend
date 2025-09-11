"use client";

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { Calculator, DollarSign, Percent, TrendingUp, Home, CreditCard, Shield, Clock } from 'lucide-react';

interface DetailedMetricsProps {
  study: any; // We'll receive the full study data as prop
}

export default function DetailedMetrics({ study }: DetailedMetricsProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  // Investment Breakdown Data
  const investmentBreakdown = [
    { name: 'Precio de Compra', value: study.purchase_price, color: '#3B82F6' },
    { name: 'Impuestos y Gastos', value: study.purchase_costs, color: '#EF4444' },
    { name: 'Reformas', value: study.renovation_costs || 0, color: '#F59E0B' },
    { name: 'Comisiones', value: study.real_estate_commission || 0, color: '#8B5CF6' }
  ];

  // Monthly Expenses Breakdown
  const monthlyExpenses = [
    { name: 'Hipoteca', value: study.monthly_mortgage_payment, color: '#EF4444' },
    { name: 'Comunidad', value: (study.community_fees || 0) / 12, color: '#F59E0B' },
    { name: 'IBI', value: (study.property_tax_ibi || 0) / 12, color: '#8B5CF6' },
    { name: 'Seguros', value: ((study.home_insurance || 0) + (study.life_insurance || 0)) / 12, color: '#10B981' },
    { name: 'Mantenimiento', value: (study.purchase_price * study.maintenance_percentage) / 12, color: '#6B7280' }
  ];

  // Financial Ratios
  const financialRatios = [
    {
      category: 'Rentabilidad',
      metrics: [
        { name: 'ROI Anual Neto', value: formatPercentage(study.net_annual_return), icon: TrendingUp, color: 'text-green-600' },
        { name: 'ROI Total Bruto', value: formatPercentage(study.total_annual_return), icon: Percent, color: 'text-blue-600' },
        { name: 'Cap Rate', value: formatPercentage((study.monthly_rent * 12) / study.purchase_price), icon: Calculator, color: 'text-purple-600' },
        { name: 'Cash-on-Cash Return', value: formatPercentage((study.monthly_net_cashflow * 12) / study.down_payment), icon: DollarSign, color: 'text-indigo-600' }
      ]
    },
    {
      category: 'Riesgo y Apalancamiento',
      metrics: [
        { name: 'LTV Ratio', value: formatPercentage(study.loan_to_value), icon: CreditCard, color: 'text-orange-600' },
        { name: 'DSCR', value: `${((study.monthly_rent * 0.8) / study.monthly_mortgage_payment).toFixed(2)}x`, icon: Shield, color: 'text-emerald-600' },
        { name: 'Ratio Alquiler/Precio', value: formatPercentage((study.monthly_rent * 12) / study.purchase_price), icon: Home, color: 'text-cyan-600' },
        { name: 'Break Even Rent', value: formatCurrency(study.break_even_rent), icon: Clock, color: 'text-rose-600' }
      ]
    }
  ];

  // Cash Flow Analysis
  const monthlyIncome = study.monthly_rent;
  const totalMonthlyExpenses = monthlyExpenses.reduce((sum, expense) => sum + expense.value, 0);
  const netCashflow = monthlyIncome - totalMonthlyExpenses;

  const cashflowData = [
    { name: 'Ingresos', income: monthlyIncome, expenses: 0 },
    { name: 'Gastos', income: 0, expenses: totalMonthlyExpenses },
    { name: 'Neto', income: netCashflow > 0 ? netCashflow : 0, expenses: netCashflow < 0 ? Math.abs(netCashflow) : 0 }
  ];

  // ROI Comparison Chart
  const roiComparison = [
    { metric: 'ROI Neto', value: study.net_annual_return * 100 },
    { metric: 'ROI Bruto', value: study.total_annual_return * 100 },
    { metric: 'Euribor + 2%', value: 4.5 }, // Benchmark
    { metric: 'Depósito Bancario', value: 2.0 } // Alternative investment
  ];

  const COLORS = ['#3B82F6', '#EF4444', '#F59E0B', '#8B5CF6', '#10B981', '#6B7280'];

  return (
    <div className="bg-white rounded-lg shadow-sm">
      {/* Header */}
      <div className="border-b border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Calculator className="h-5 w-5 mr-2 text-blue-600" />
          Métricas Detalladas
        </h3>
      </div>

      <div className="p-6 space-y-8">
        {/* Investment Breakdown */}
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-4">Desglose de la Inversión</h4>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={investmentBreakdown}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${formatCurrency(value)}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {investmentBreakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => formatCurrency(value)} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            
            <div className="space-y-3">
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <h5 className="font-medium text-blue-900">Inversión Total</h5>
                <p className="text-2xl font-bold text-blue-600">
                  {formatCurrency(study.total_purchase_price)}
                </p>
              </div>
              <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                <h5 className="font-medium text-green-900">Entrada (Down Payment)</h5>
                <p className="text-xl font-bold text-green-600">
                  {formatCurrency(study.down_payment)}
                </p>
                <p className="text-sm text-green-700">
                  {formatPercentage(study.down_payment / study.total_purchase_price)} del total
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Financial Ratios */}
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-4">Ratios Financieros</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {financialRatios.map((category, categoryIndex) => (
              <div key={categoryIndex} className="space-y-4">
                <h5 className="font-medium text-gray-800 border-b border-gray-200 pb-2">
                  {category.category}
                </h5>
                <div className="space-y-3">
                  {category.metrics.map((metric, metricIndex) => {
                    const Icon = metric.icon;
                    return (
                      <div key={metricIndex} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center">
                          <Icon className={`h-5 w-5 mr-3 ${metric.color}`} />
                          <span className="text-sm font-medium text-gray-700">{metric.name}</span>
                        </div>
                        <span className={`text-lg font-bold ${metric.color}`}>
                          {metric.value}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Monthly Cash Flow Analysis */}
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-4">Análisis de Cash Flow Mensual</h4>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={cashflowData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis tickFormatter={(value) => formatCurrency(value)} />
                  <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  <Legend />
                  <Bar dataKey="income" stackId="a" fill="#10B981" name="Ingresos" />
                  <Bar dataKey="expenses" stackId="a" fill="#EF4444" name="Gastos" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="space-y-3">
              <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                <h5 className="font-medium text-green-900">Ingresos Mensuales</h5>
                <p className="text-xl font-bold text-green-600">
                  {formatCurrency(monthlyIncome)}
                </p>
              </div>
              <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                <h5 className="font-medium text-red-900">Gastos Mensuales</h5>
                <p className="text-xl font-bold text-red-600">
                  {formatCurrency(totalMonthlyExpenses)}
                </p>
              </div>
              <div className={`rounded-lg p-4 border ${
                netCashflow >= 0 
                  ? 'bg-blue-50 border-blue-200' 
                  : 'bg-orange-50 border-orange-200'
              }`}>
                <h5 className={`font-medium ${
                  netCashflow >= 0 ? 'text-blue-900' : 'text-orange-900'
                }`}>
                  Cash Flow Neto
                </h5>
                <p className={`text-xl font-bold ${
                  netCashflow >= 0 ? 'text-blue-600' : 'text-orange-600'
                }`}>
                  {formatCurrency(netCashflow)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* ROI Comparison */}
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-4">Comparación de Rentabilidad</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={roiComparison} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" tickFormatter={(value) => `${value}%`} />
                <YAxis dataKey="metric" type="category" width={120} />
                <Tooltip formatter={(value: number) => `${value.toFixed(2)}%`} />
                <Bar dataKey="value" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Monthly Expenses Breakdown */}
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-4">Desglose de Gastos Mensuales</h4>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={monthlyExpenses}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${formatCurrency(value)}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {monthlyExpenses.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => formatCurrency(value)} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="space-y-2">
              {monthlyExpenses.map((expense, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div className="flex items-center">
                    <div 
                      className="w-4 h-4 rounded mr-3" 
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    ></div>
                    <span className="text-sm font-medium text-gray-700">{expense.name}</span>
                  </div>
                  <span className="text-sm font-bold text-gray-900">
                    {formatCurrency(expense.value)}
                  </span>
                </div>
              ))}
              <div className="border-t border-gray-300 pt-2 mt-3">
                <div className="flex items-center justify-between font-bold">
                  <span className="text-gray-900">Total Mensual</span>
                  <span className="text-gray-900">
                    {formatCurrency(totalMonthlyExpenses)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Key Performance Indicators */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h4 className="text-md font-medium text-gray-900 mb-4">Indicadores Clave de Rendimiento</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {((study.monthly_rent * 12) / study.purchase_price * 100).toFixed(2)}%
              </p>
              <p className="text-xs text-gray-600">Yield Bruto</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {(study.net_annual_return * 100).toFixed(2)}%
              </p>
              <p className="text-xs text-gray-600">Yield Neto</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">
                {(study.down_payment / (study.monthly_net_cashflow * 12) || 0).toFixed(1)}
              </p>
              <p className="text-xs text-gray-600">Años Payback</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">
                {((study.monthly_rent * 0.8) / study.monthly_mortgage_payment).toFixed(1)}x
              </p>
              <p className="text-xs text-gray-600">DSCR</p>
            </div>
          </div>
        </div>

        {/* Metrics Definitions */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
            <Calculator className="h-5 w-5 mr-2 text-blue-600" />
            Definiciones de Métricas
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Rentabilidad Metrics */}
            <div>
              <h5 className="font-medium text-gray-800 border-b border-gray-200 pb-2 mb-3">
                Métricas de Rentabilidad
              </h5>
              <div className="space-y-3">
                <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
                  <h6 className="font-medium text-blue-900 mb-1">ROI Anual Neto</h6>
                  <p className="text-sm text-blue-800">
                    Rentabilidad anual después de gastos e impuestos. Fórmula: (Ingresos anuales - Gastos) / Inversión inicial
                  </p>
                </div>
                
                <div className="bg-green-50 rounded-lg p-3 border border-green-200">
                  <h6 className="font-medium text-green-900 mb-1">ROI Total Bruto</h6>
                  <p className="text-sm text-green-800">
                    Rentabilidad bruta sin deducir gastos operativos. Fórmula: Ingresos anuales / Precio de compra
                  </p>
                </div>
                
                <div className="bg-purple-50 rounded-lg p-3 border border-purple-200">
                  <h6 className="font-medium text-purple-900 mb-1">Cap Rate</h6>
                  <p className="text-sm text-purple-800">
                    Tasa de capitalización. Indica el retorno potencial sin financiación. Fórmula: NOI / Valor del inmueble
                  </p>
                </div>
                
                <div className="bg-indigo-50 rounded-lg p-3 border border-indigo-200">
                  <h6 className="font-medium text-indigo-900 mb-1">Cash-on-Cash Return</h6>
                  <p className="text-sm text-indigo-800">
                    Rentabilidad sobre el efectivo invertido inicialmente. Fórmula: Cash flow anual / Down payment
                  </p>
                </div>
              </div>
            </div>
            
            {/* Risk and Leverage Metrics */}
            <div>
              <h5 className="font-medium text-gray-800 border-b border-gray-200 pb-2 mb-3">
                Métricas de Riesgo y Apalancamiento
              </h5>
              <div className="space-y-3">
                <div className="bg-orange-50 rounded-lg p-3 border border-orange-200">
                  <h6 className="font-medium text-orange-900 mb-1">LTV Ratio</h6>
                  <p className="text-sm text-orange-800">
                    Loan-to-Value. Porcentaje financiado del inmueble. A mayor LTV, mayor apalancamiento y riesgo.
                  </p>
                </div>
                
                <div className="bg-emerald-50 rounded-lg p-3 border border-emerald-200">
                  <h6 className="font-medium text-emerald-900 mb-1">DSCR</h6>
                  <p className="text-sm text-emerald-800">
                    Debt Service Coverage Ratio. Capacidad de pago de la hipoteca. {'>'}1.25 se considera seguro.
                  </p>
                </div>
                
                <div className="bg-cyan-50 rounded-lg p-3 border border-cyan-200">
                  <h6 className="font-medium text-cyan-900 mb-1">Ratio Alquiler/Precio</h6>
                  <p className="text-sm text-cyan-800">
                    Indicador de valor. El 1% mensual es considerado excelente, 0.5% aceptable.
                  </p>
                </div>
                
                <div className="bg-rose-50 rounded-lg p-3 border border-rose-200">
                  <h6 className="font-medium text-rose-900 mb-1">Break Even Rent</h6>
                  <p className="text-sm text-rose-800">
                    Alquiler mínimo necesario para cubrir todos los gastos. Buffer = (Alquiler actual - Break even) / Break even
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          {/* Additional Concepts */}
          <div className="mt-6 bg-gray-50 rounded-lg p-4">
            <h6 className="font-medium text-gray-900 mb-3">Conceptos Adicionales</h6>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-700">
              <div>
                <strong>NOI (Net Operating Income):</strong> Ingresos netos operativos después de gastos pero antes del servicio de la deuda.
              </div>
              <div>
                <strong>Yield Bruto vs Neto:</strong> Bruto no incluye gastos; Neto sí los incluye y es más realista.
              </div>
              <div>
                <strong>Payback Period:</strong> Tiempo necesario para recuperar la inversión inicial a través del cash flow.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}