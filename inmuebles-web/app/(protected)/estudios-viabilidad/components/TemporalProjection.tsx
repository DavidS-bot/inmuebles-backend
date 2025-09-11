"use client";

import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, Area, AreaChart } from 'recharts';
import { TrendingUp, Calendar, DollarSign, Percent, Home } from 'lucide-react';

interface ProjectionData {
  year: number;
  annual_rent: number;
  annual_expenses: number;
  net_cashflow: number;
  cumulative_cashflow: number;
  property_value: number;
  outstanding_debt: number;
  equity_value: number;
  annual_return: number;
  cumulative_return: number;
}

interface TemporalProjectionProps {
  studyId: number;
}

export default function TemporalProjection({ studyId }: TemporalProjectionProps) {
  const [projectionData, setProjectionData] = useState<ProjectionData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [years, setYears] = useState(10);
  const [activeChart, setActiveChart] = useState('cashflow');

  useEffect(() => {
    fetchProjectionData();
  }, [studyId, years]);

  const fetchProjectionData = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/viability/${studyId}/projection?years=${years}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setProjectionData(data);
      } else {
        setError('Error cargando proyección temporal');
      }
    } catch (err) {
      setError('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || projectionData.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="text-center text-red-600">
          {error || 'No se pudo cargar la proyección temporal'}
        </div>
      </div>
    );
  }

  const chartTabs = [
    { id: 'cashflow', name: 'Cashflow', icon: DollarSign },
    { id: 'value', name: 'Valor del Activo', icon: Home },
    { id: 'returns', name: 'Rentabilidad', icon: Percent },
    { id: 'debt', name: 'Deuda vs Equity', icon: TrendingUp }
  ];

  const finalYear = projectionData[projectionData.length - 1];
  const totalReturn = finalYear ? finalYear.cumulative_return : 0;
  const totalCashflow = finalYear ? finalYear.cumulative_cashflow : 0;
  const finalEquity = finalYear ? finalYear.equity_value : 0;

  return (
    <div className="bg-white rounded-lg shadow-sm">
      {/* Header */}
      <div className="border-b border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Calendar className="h-5 w-5 mr-2 text-blue-600" />
            Proyección Temporal
          </h3>
          
          {/* Years Selector */}
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700">Años:</label>
            <select
              value={years}
              onChange={(e) => setYears(parseInt(e.target.value))}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={5}>5 años</option>
              <option value={10}>10 años</option>
              <option value={15}>15 años</option>
              <option value={20}>20 años</option>
              <option value={25}>25 años</option>
              <option value={30}>30 años</option>
            </select>
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <h4 className="text-sm font-medium text-blue-900">Cashflow Total</h4>
            <p className="text-xl font-bold text-blue-600">
              {formatCurrency(totalCashflow)}
            </p>
          </div>

          <div className="bg-green-50 rounded-lg p-4 border border-green-200">
            <h4 className="text-sm font-medium text-green-900">Retorno Total</h4>
            <p className="text-xl font-bold text-green-600">
              {formatPercentage(totalReturn)}
            </p>
          </div>

          <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
            <h4 className="text-sm font-medium text-purple-900">Equity Final</h4>
            <p className="text-xl font-bold text-purple-600">
              {formatCurrency(finalEquity)}
            </p>
          </div>

          <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
            <h4 className="text-sm font-medium text-orange-900">Proyección</h4>
            <p className="text-xl font-bold text-orange-600">
              {years} años
            </p>
          </div>
        </div>

        {/* Chart Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {chartTabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveChart(tab.id)}
                    className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                      activeChart === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="h-4 w-4 mr-2" />
                    {tab.name}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Charts */}
        <div className="h-80">
          {activeChart === 'cashflow' && (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={projectionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis tickFormatter={(value) => formatCurrency(value)} />
                <Tooltip 
                  formatter={(value: number) => [formatCurrency(value), '']}
                  labelFormatter={(label) => `Año ${label}`}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="cumulative_cashflow"
                  stackId="1"
                  stroke="#3B82F6"
                  fill="#3B82F6"
                  fillOpacity={0.6}
                  name="Cashflow Acumulado"
                />
                <Line
                  type="monotone"
                  dataKey="net_cashflow"
                  stroke="#10B981"
                  strokeWidth={2}
                  name="Cashflow Anual"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}

          {activeChart === 'value' && (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={projectionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis tickFormatter={(value) => formatCurrency(value)} />
                <Tooltip 
                  formatter={(value: number) => [formatCurrency(value), '']}
                  labelFormatter={(label) => `Año ${label}`}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="property_value"
                  stroke="#8B5CF6"
                  strokeWidth={3}
                  name="Valor de la Propiedad"
                />
                <Line
                  type="monotone"
                  dataKey="equity_value"
                  stroke="#10B981"
                  strokeWidth={2}
                  name="Equity Value"
                />
              </LineChart>
            </ResponsiveContainer>
          )}

          {activeChart === 'returns' && (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={projectionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis tickFormatter={(value) => formatPercentage(value)} />
                <Tooltip 
                  formatter={(value: number) => [formatPercentage(value), '']}
                  labelFormatter={(label) => `Año ${label}`}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="cumulative_return"
                  stroke="#F59E0B"
                  fill="#F59E0B"
                  fillOpacity={0.6}
                  name="Retorno Acumulado"
                />
                <Line
                  type="monotone"
                  dataKey="annual_return"
                  stroke="#EF4444"
                  strokeWidth={2}
                  name="Retorno Anual"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}

          {activeChart === 'debt' && (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={projectionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis tickFormatter={(value) => formatCurrency(value)} />
                <Tooltip 
                  formatter={(value: number) => [formatCurrency(value), '']}
                  labelFormatter={(label) => `Año ${label}`}
                />
                <Legend />
                <Bar
                  dataKey="outstanding_debt"
                  stackId="a"
                  fill="#EF4444"
                  name="Deuda Pendiente"
                />
                <Bar
                  dataKey="equity_value"
                  stackId="a"
                  fill="#10B981"
                  name="Equity"
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Key Insights */}
        <div className="mt-6 bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Puntos Clave de la Proyección</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
            <div>
              • <strong>Cashflow positivo alcanzado:</strong> {
                projectionData.find(p => p.net_cashflow > 0)?.year || 'No en este período'
              }
            </div>
            <div>
              • <strong>ROI Break-even:</strong> {
                projectionData.find(p => p.cumulative_return > 0)?.year || 'No en este período'
              } años
            </div>
            <div>
              • <strong>Mejor año de rentabilidad:</strong> Año {
                projectionData.reduce((max, p) => (p.annual_return || 0) > (max.annual_return || 0) ? p : max).year
              }
            </div>
            <div>
              • <strong>Crecimiento de equity promedio:</strong> {
                formatPercentage((finalEquity - projectionData[0]?.equity_value) / projectionData[0]?.equity_value / years)
              } anual
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}