"use client";

import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { AlertTriangle, TrendingUp, TrendingDown, Target, Activity } from 'lucide-react';

interface SensitivityData {
  base_scenario: {
    annual_return: number;
    monthly_cashflow: number;
    break_even_rent: number;
    risk_level: string;
  };
  optimistic_scenario: {
    annual_return: number;
    monthly_cashflow: number;
    break_even_rent: number;
    assumptions: string[];
  };
  pessimistic_scenario: {
    annual_return: number;
    monthly_cashflow: number;
    break_even_rent: number;
    assumptions: string[];
  };
  sensitivity_factors: Array<{
    factor: string;
    impact_low: number;
    impact_high: number;
    current_value: number;
    risk_level: string;
  }>;
  stress_tests: Array<{
    test_name: string;
    scenario: string;
    impact_on_return: number;
    impact_on_cashflow: number;
    probability: string;
  }>;
}

interface SensitivityAnalysisProps {
  studyId: number;
}

export default function SensitivityAnalysis({ studyId }: SensitivityAnalysisProps) {
  const [sensitivityData, setSensitivityData] = useState<SensitivityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('scenarios');

  useEffect(() => {
    fetchSensitivityData();
  }, [studyId]);

  const fetchSensitivityData = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/viability/${studyId}/sensitivity-analysis`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
      });

      if (response.ok) {
        const data = await response.json();
        setSensitivityData(data);
      } else {
        setError('Error cargando análisis de sensibilidad');
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
    return `${(value * 100).toFixed(2)}%`;
  };

  const getImpactColor = (impact: number) => {
    if (impact > 0.1) return 'text-red-600 bg-red-50 border-red-200';
    if (impact > 0.05) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-green-600 bg-green-50 border-green-200';
  };

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
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

  if (error || !sensitivityData) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="text-center text-red-600">
          {error || 'No se pudo cargar el análisis de sensibilidad'}
        </div>
      </div>
    );
  }

  const scenarioData = [
    {
      name: 'Pesimista',
      return: sensitivityData.pessimistic_scenario.annual_return * 100,
      cashflow: sensitivityData.pessimistic_scenario.monthly_cashflow,
      color: '#EF4444'
    },
    {
      name: 'Base',
      return: sensitivityData.base_scenario.annual_return * 100,
      cashflow: sensitivityData.base_scenario.monthly_cashflow,
      color: '#3B82F6'
    },
    {
      name: 'Optimista',
      return: sensitivityData.optimistic_scenario.annual_return * 100,
      cashflow: sensitivityData.optimistic_scenario.monthly_cashflow,
      color: '#10B981'
    }
  ];

  const radarData = sensitivityData.sensitivity_factors.map(factor => ({
    factor: factor.factor,
    impact: Math.abs(factor.impact_high - factor.impact_low) * 100,
    fullMark: 20
  }));

  const tabs = [
    { id: 'scenarios', name: 'Escenarios', icon: Target },
    { id: 'factors', name: 'Factores de Riesgo', icon: Activity },
    { id: 'stress', name: 'Stress Tests', icon: AlertTriangle }
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm">
      {/* Header */}
      <div className="border-b border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <AlertTriangle className="h-5 w-5 mr-2 text-orange-600" />
          Análisis de Sensibilidad
        </h3>
      </div>

      <div className="p-6">
        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                      activeTab === tab.id
                        ? 'border-orange-500 text-orange-600'
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

        {/* Scenarios Tab */}
        {activeTab === 'scenarios' && (
          <div>
            {/* Scenario Comparison Chart */}
            <div className="mb-6">
              <h4 className="text-md font-medium text-gray-900 mb-4">Comparación de Escenarios</h4>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={scenarioData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis yAxisId="left" orientation="left" tickFormatter={(value) => `${value}%`} />
                    <YAxis yAxisId="right" orientation="right" tickFormatter={(value) => formatCurrency(value)} />
                    <Tooltip 
                      formatter={(value: number, name: string) => [
                        name === 'return' ? `${value.toFixed(2)}%` : formatCurrency(value),
                        name === 'return' ? 'Rentabilidad Anual' : 'Cashflow Mensual'
                      ]}
                    />
                    <Legend />
                    <Bar yAxisId="left" dataKey="return" fill="#3B82F6" name="Rentabilidad %" />
                    <Bar yAxisId="right" dataKey="cashflow" fill="#10B981" name="Cashflow €" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Scenario Details */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Pessimistic */}
              <div className="border border-red-200 rounded-lg p-4 bg-red-50">
                <h5 className="font-medium text-red-900 mb-3 flex items-center">
                  <TrendingDown className="h-4 w-4 mr-2" />
                  Escenario Pesimista
                </h5>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="font-medium">Rentabilidad:</span> {formatPercentage(sensitivityData.pessimistic_scenario.annual_return)}
                  </div>
                  <div>
                    <span className="font-medium">Cashflow:</span> {formatCurrency(sensitivityData.pessimistic_scenario.monthly_cashflow)}
                  </div>
                  <div>
                    <span className="font-medium">Break-even:</span> {formatCurrency(sensitivityData.pessimistic_scenario.break_even_rent)}
                  </div>
                </div>
                <div className="mt-3">
                  <h6 className="font-medium text-red-900 mb-2">Asunciones:</h6>
                  <ul className="text-xs text-red-700 space-y-1">
                    {sensitivityData.pessimistic_scenario.assumptions.map((assumption, index) => (
                      <li key={index}>• {assumption}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Base */}
              <div className="border border-blue-200 rounded-lg p-4 bg-blue-50">
                <h5 className="font-medium text-blue-900 mb-3 flex items-center">
                  <Target className="h-4 w-4 mr-2" />
                  Escenario Base
                </h5>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="font-medium">Rentabilidad:</span> {formatPercentage(sensitivityData.base_scenario.annual_return)}
                  </div>
                  <div>
                    <span className="font-medium">Cashflow:</span> {formatCurrency(sensitivityData.base_scenario.monthly_cashflow)}
                  </div>
                  <div>
                    <span className="font-medium">Break-even:</span> {formatCurrency(sensitivityData.base_scenario.break_even_rent)}
                  </div>
                  <div className={`mt-2 px-2 py-1 rounded text-xs font-medium ${getRiskColor(sensitivityData.base_scenario.risk_level)}`}>
                    Riesgo: {sensitivityData.base_scenario.risk_level}
                  </div>
                </div>
              </div>

              {/* Optimistic */}
              <div className="border border-green-200 rounded-lg p-4 bg-green-50">
                <h5 className="font-medium text-green-900 mb-3 flex items-center">
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Escenario Optimista
                </h5>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="font-medium">Rentabilidad:</span> {formatPercentage(sensitivityData.optimistic_scenario.annual_return)}
                  </div>
                  <div>
                    <span className="font-medium">Cashflow:</span> {formatCurrency(sensitivityData.optimistic_scenario.monthly_cashflow)}
                  </div>
                  <div>
                    <span className="font-medium">Break-even:</span> {formatCurrency(sensitivityData.optimistic_scenario.break_even_rent)}
                  </div>
                </div>
                <div className="mt-3">
                  <h6 className="font-medium text-green-900 mb-2">Asunciones:</h6>
                  <ul className="text-xs text-green-700 space-y-1">
                    {sensitivityData.optimistic_scenario.assumptions.map((assumption, index) => (
                      <li key={index}>• {assumption}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Factors Tab */}
        {activeTab === 'factors' && (
          <div>
            {/* Radar Chart */}
            <div className="mb-6">
              <h4 className="text-md font-medium text-gray-900 mb-4">Impacto de Factores de Riesgo</h4>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="factor" />
                    <PolarRadiusAxis angle={0} domain={[0, 20]} />
                    <Radar
                      name="Impacto"
                      dataKey="impact"
                      stroke="#F59E0B"
                      fill="#F59E0B"
                      fillOpacity={0.6}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Factors Table */}
            <div>
              <h4 className="text-md font-medium text-gray-900 mb-4">Análisis Detallado de Factores</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Factor</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Valor Actual</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Impacto Bajo</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Impacto Alto</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Riesgo</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {sensitivityData.sensitivity_factors.map((factor, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {factor.factor}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {factor.current_value.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatPercentage(factor.impact_low)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatPercentage(factor.impact_high)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getRiskColor(factor.risk_level)}`}>
                            {factor.risk_level}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Stress Tests Tab */}
        {activeTab === 'stress' && (
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-4">Pruebas de Estrés</h4>
            <div className="space-y-4">
              {sensitivityData.stress_tests.map((test, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h5 className="font-medium text-gray-900">{test.test_name}</h5>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      test.probability === 'High' ? 'text-red-600 bg-red-50' :
                      test.probability === 'Medium' ? 'text-yellow-600 bg-yellow-50' :
                      'text-green-600 bg-green-50'
                    }`}>
                      {test.probability}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-3">{test.scenario}</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 rounded p-3">
                      <span className="text-sm font-medium text-gray-700">Impacto en Rentabilidad:</span>
                      <span className={`ml-2 font-bold ${test.impact_on_return < 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {formatPercentage(test.impact_on_return)}
                      </span>
                    </div>
                    <div className="bg-gray-50 rounded p-3">
                      <span className="text-sm font-medium text-gray-700">Impacto en Cashflow:</span>
                      <span className={`ml-2 font-bold ${test.impact_on_cashflow < 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {formatCurrency(test.impact_on_cashflow)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}