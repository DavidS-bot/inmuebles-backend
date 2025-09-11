"use client";

import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Home, BarChart3, AlertTriangle, DollarSign, PieChart, Calendar } from 'lucide-react';

interface ExecutiveSummaryProps {
  studyId: number;
}

interface SummaryData {
  study_name: string;
  investment_summary: {
    total_investment: number;
    down_payment: number;
    loan_amount: number;
    loan_to_value: number;
  };
  return_metrics: {
    net_annual_return: number;
    total_annual_return: number;
    monthly_cashflow: number;
    annual_cashflow: number;
    payback_period_years: number;
  };
  risk_assessment: {
    risk_level: string;
    is_favorable: boolean;
    break_even_rent: number;
    rent_buffer_percent: number;
    months_to_positive_cashflow: number;
  };
  key_assumptions: {
    purchase_price: number;
    monthly_rent: number;
    interest_rate: number;
    loan_term: number;
    annual_rent_increase: number;
  };
}

export default function ExecutiveSummary({ studyId }: ExecutiveSummaryProps) {
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchExecutiveSummary();
  }, [studyId]);

  const fetchExecutiveSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = localStorage.getItem('auth_token');
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      const response = await fetch(`${API_URL}/viability/${studyId}/summary`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSummary(data);
      } else {
        setError('Error al cargar el resumen ejecutivo');
      }
    } catch (err) {
      setError('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  const getGradeColor = (grade?: string) => {
    if (!grade) return 'text-gray-600 bg-gray-50 border-gray-200';
    switch (grade.toUpperCase()) {
      case 'A': return 'text-green-600 bg-green-50 border-green-200';
      case 'B': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'C': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'D': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getRiskColor = (risk?: string) => {
    if (!risk) return 'text-gray-600 bg-gray-50 border-gray-200';
    switch (risk.toUpperCase()) {
      case 'LOW': return 'text-green-600 bg-green-50 border-green-200';
      case 'MEDIUM': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'HIGH': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
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

  const getInvestmentGrade = (returnRate: number): string => {
    if (returnRate > 0.08) return 'A';
    if (returnRate > 0.06) return 'B';
    if (returnRate > 0.04) return 'C';
    return 'D';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="p-6 text-center">
        <div className="text-red-600 mb-4">
          <AlertTriangle className="h-12 w-12 mx-auto mb-2" />
          <p>{error || 'No se pudieron cargar los datos'}</p>
        </div>
        <button 
          onClick={fetchExecutiveSummary}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Reintentar
        </button>
      </div>
    );
  }

  const investmentGrade = getInvestmentGrade(summary.return_metrics?.net_annual_return || 0);

  return (
    <div className="bg-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200">
        <div className="p-6">
          <h3 className="text-xl font-bold text-gray-900 flex items-center mb-4">
            <TrendingUp className="h-5 w-5 mr-2 text-blue-600" />
            Resumen Ejecutivo
          </h3>
          
          <div className="flex items-center space-x-4">
            {/* Investment Grade */}
            <div className={`px-3 py-1 rounded-full border text-sm font-medium ${getGradeColor(investmentGrade)}`}>
              Grado: {investmentGrade}
            </div>
            
            {/* Risk Assessment */}
            <div className={`px-3 py-1 rounded-full border text-sm font-medium ${getRiskColor(summary.risk_assessment?.risk_level)}`}>
              Riesgo: {summary.risk_assessment?.risk_level || 'UNKNOWN'}
            </div>

            {/* Favorable Status */}
            <div className={`px-3 py-1 rounded-full border text-sm font-medium ${summary.risk_assessment?.is_favorable ? 'text-green-600 bg-green-50 border-green-200' : 'text-red-600 bg-red-50 border-red-200'}`}>
              {summary.risk_assessment?.is_favorable ? 'FAVORABLE' : 'NO FAVORABLE'}
            </div>
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {/* Total Investment */}
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <div className="flex items-center">
              <Home className="h-8 w-8 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-900">Inversión Total</p>
                <p className="text-lg font-bold text-blue-600">
                  {formatCurrency(summary.investment_summary?.total_investment || 0)}
                </p>
              </div>
            </div>
          </div>

          {/* Monthly Cashflow */}
          <div className={`rounded-lg p-4 border ${
            (summary.return_metrics?.monthly_cashflow || 0) >= 0 
              ? 'bg-green-50 border-green-200' 
              : 'bg-red-50 border-red-200'
          }`}>
            <div className="flex items-center">
              {(summary.return_metrics?.monthly_cashflow || 0) >= 0 ? (
                <TrendingUp className="h-8 w-8 text-green-600" />
              ) : (
                <TrendingDown className="h-8 w-8 text-red-600" />
              )}
              <div className="ml-3">
                <p className={`text-sm font-medium ${
                  (summary.return_metrics?.monthly_cashflow || 0) >= 0 ? 'text-green-900' : 'text-red-900'
                }`}>
                  Cashflow Mensual
                </p>
                <p className={`text-lg font-bold ${
                  (summary.return_metrics?.monthly_cashflow || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatCurrency(summary.return_metrics?.monthly_cashflow || 0)}
                </p>
              </div>
            </div>
          </div>

          {/* Annual Return */}
          <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
            <div className="flex items-center">
              <BarChart3 className="h-8 w-8 text-purple-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-purple-900">ROI Anual Neto</p>
                <p className="text-lg font-bold text-purple-600">
                  {formatPercentage(summary.return_metrics?.net_annual_return || 0)}
                </p>
              </div>
            </div>
          </div>

          {/* Break Even */}
          <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
            <div className="flex items-center">
              <AlertTriangle className="h-8 w-8 text-orange-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-orange-900">Break Even</p>
                <p className="text-lg font-bold text-orange-600">
                  {formatCurrency(summary.risk_assessment?.break_even_rent || 0)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Additional Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">LTV Ratio</h4>
            <p className="text-2xl font-bold text-blue-600">
              {formatPercentage(summary.investment_summary?.loan_to_value || 0)}
            </p>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Periodo de Recuperación</h4>
            <p className="text-2xl font-bold text-green-600">
              {(summary.return_metrics?.payback_period_years || 0).toFixed(1)} años
            </p>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Buffer de Renta</h4>
            <p className="text-2xl font-bold text-purple-600">
              {(summary.risk_assessment?.rent_buffer_percent || 0).toFixed(1)}%
            </p>
          </div>
        </div>

        {/* Assumptions */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3">Asunciones Clave</h4>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Precio Compra:</span>
              <p className="font-medium">{formatCurrency(summary.key_assumptions?.purchase_price || 0)}</p>
            </div>
            <div>
              <span className="text-gray-600">Renta Mensual:</span>
              <p className="font-medium">{formatCurrency(summary.key_assumptions?.monthly_rent || 0)}</p>
            </div>
            <div>
              <span className="text-gray-600">Tipo Interés:</span>
              <p className="font-medium">{formatPercentage(summary.key_assumptions?.interest_rate || 0)}</p>
            </div>
            <div>
              <span className="text-gray-600">Plazo Hipoteca:</span>
              <p className="font-medium">{summary.key_assumptions?.loan_term || 0} años</p>
            </div>
            <div>
              <span className="text-gray-600">Incremento Anual:</span>
              <p className="font-medium">{formatPercentage(summary.key_assumptions?.annual_rent_increase || 0)}</p>
            </div>
          </div>
        </div>

        {/* Investment Rating Explanation */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h4 className="font-medium text-gray-900 mb-4 flex items-center">
            <BarChart3 className="h-5 w-5 mr-2 text-blue-600" />
            Explicación de la Calificación
          </h4>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Investment Grade Explanation */}
            <div>
              <h5 className="font-medium text-gray-800 border-b border-gray-200 pb-2 mb-3">
                Grado de Inversión
              </h5>
              <div className="space-y-3">
                <div className={`rounded-lg p-3 border ${getGradeColor('A')}`}>
                  <div className="flex items-center mb-2">
                    <span className="font-bold text-lg mr-2">A</span>
                    <span className="font-medium">Excelente (ROI {'>'} 8%)</span>
                  </div>
                  <p className="text-sm">
                    Inversión de alta calidad con rentabilidad superior al 8% anual. 
                    Flujo de caja positivo robusto y métricas financieras sólidas.
                  </p>
                </div>
                
                <div className={`rounded-lg p-3 border ${getGradeColor('B')}`}>
                  <div className="flex items-center mb-2">
                    <span className="font-bold text-lg mr-2">B</span>
                    <span className="font-medium">Buena (ROI 6-8%)</span>
                  </div>
                  <p className="text-sm">
                    Inversión sólida con rentabilidad entre 6-8%. Buen equilibrio 
                    entre riesgo y rentabilidad.
                  </p>
                </div>
                
                <div className={`rounded-lg p-3 border ${getGradeColor('C')}`}>
                  <div className="flex items-center mb-2">
                    <span className="font-bold text-lg mr-2">C</span>
                    <span className="font-medium">Aceptable (ROI 4-6%)</span>
                  </div>
                  <p className="text-sm">
                    Inversión moderada con rentabilidad entre 4-6%. Requiere 
                    análisis adicional de riesgos.
                  </p>
                </div>
                
                <div className={`rounded-lg p-3 border ${getGradeColor('D')}`}>
                  <div className="flex items-center mb-2">
                    <span className="font-bold text-lg mr-2">D</span>
                    <span className="font-medium">Riesgo Alto (ROI {'<'} 4%)</span>
                  </div>
                  <p className="text-sm">
                    Inversión de alto riesgo con rentabilidad inferior al 4%. 
                    No recomendada sin optimizaciones significativas.
                  </p>
                </div>
              </div>
            </div>
            
            {/* Risk Level Explanation */}
            <div>
              <h5 className="font-medium text-gray-800 border-b border-gray-200 pb-2 mb-3">
                Nivel de Riesgo
              </h5>
              <div className="space-y-3">
                <div className={`rounded-lg p-3 border ${getRiskColor('LOW')}`}>
                  <div className="flex items-center mb-2">
                    <span className="font-bold text-lg mr-2">LOW</span>
                    <span className="font-medium">Riesgo Bajo</span>
                  </div>
                  <p className="text-sm mb-2">
                    Inversión con riesgo mínimo. Características favorables:
                  </p>
                  <ul className="text-xs space-y-1">
                    <li>• Cash flow positivo consistente</li>
                    <li>• LTV {'<'} 75%</li>
                    <li>• ROI neto {'>'} 6%</li>
                    <li>• Buffer de renta {'>'} 20%</li>
                  </ul>
                </div>
                
                <div className={`rounded-lg p-3 border ${getRiskColor('MEDIUM')}`}>
                  <div className="flex items-center mb-2">
                    <span className="font-bold text-lg mr-2">MEDIUM</span>
                    <span className="font-medium">Riesgo Moderado</span>
                  </div>
                  <p className="text-sm mb-2">
                    Inversión con riesgo controlado. Factores a monitorear:
                  </p>
                  <ul className="text-xs space-y-1">
                    <li>• LTV entre 75-85%</li>
                    <li>• ROI entre 4-6%</li>
                    <li>• Cash flow ajustado</li>
                    <li>• Sensibilidad a cambios de mercado</li>
                  </ul>
                </div>
                
                <div className={`rounded-lg p-3 border ${getRiskColor('HIGH')}`}>
                  <div className="flex items-center mb-2">
                    <span className="font-bold text-lg mr-2">HIGH</span>
                    <span className="font-medium">Riesgo Alto</span>
                  </div>
                  <p className="text-sm mb-2">
                    Inversión de alto riesgo. Señales de alerta:
                  </p>
                  <ul className="text-xs space-y-1">
                    <li>• Cash flow negativo o muy ajustado</li>
                    <li>• LTV {'>'} 85%</li>
                    <li>• ROI {'<'} 4%</li>
                    <li>• Alta sensibilidad a variaciones</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
          
          {/* Status Explanation */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <h5 className="font-medium text-gray-800 mb-3">Estado de la Inversión</h5>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                <div className="flex items-center mb-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                  <span className="font-medium text-green-900">FAVORABLE</span>
                </div>
                <p className="text-sm text-green-800">
                  La inversión cumple con los criterios de rentabilidad y riesgo establecidos. 
                  Se recomienda proceder con la adquisición tras verificar las asunciones del mercado local.
                </p>
              </div>
              
              <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                <div className="flex items-center mb-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                  <span className="font-medium text-red-900">NO FAVORABLE</span>
                </div>
                <p className="text-sm text-red-800">
                  La inversión presenta riesgos significativos o rentabilidad insuficiente. 
                  Se requiere optimización de parámetros o buscar alternativas más atractivas.
                </p>
              </div>
            </div>
          </div>
          
          {/* Current Investment Summary */}
          <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h6 className="font-medium text-blue-900 mb-2">Resumen de Tu Inversión</h6>
            <div className="text-sm text-blue-800">
              <p>
                <strong>Grado {investmentGrade}</strong>: {
                  investmentGrade === 'A' ? 'Excelente inversión con alta rentabilidad' :
                  investmentGrade === 'B' ? 'Buena inversión con rentabilidad sólida' :
                  investmentGrade === 'C' ? 'Inversión aceptable que requiere monitoreo' :
                  'Inversión de alto riesgo que requiere optimización'
                }
              </p>
              <p className="mt-1">
                <strong>Riesgo {summary.risk_assessment?.risk_level || 'UNKNOWN'}</strong>: {
                  summary.risk_assessment?.risk_level === 'LOW' ? 'Mínimo, inversión muy segura' :
                  summary.risk_assessment?.risk_level === 'MEDIUM' ? 'Moderado, requiere seguimiento' :
                  'Alto, requiere medidas de mitigación'
                }
              </p>
              <p className="mt-1">
                <strong>Estado</strong>: {summary.risk_assessment?.is_favorable ? 
                  'Recomendamos proceder con esta inversión' : 
                  'Sugerimos revisar parámetros antes de proceder'
                }
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}