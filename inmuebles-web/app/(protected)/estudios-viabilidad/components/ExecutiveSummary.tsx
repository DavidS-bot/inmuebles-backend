"use client";

import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, DollarSign, Calendar, Percent, Home, Clock } from 'lucide-react';

interface ExecutiveSummaryData {
  investment_grade: string;
  profitability_score: number;
  risk_assessment: string;
  payback_period_years: number;
  break_even_point: string;
  key_metrics: {
    total_investment: number;
    monthly_cashflow: number;
    annual_return: number;
    ltv_ratio: number;
    debt_service_coverage: number;
    cap_rate: number;
  };
  recommendations: string[];
  warnings: string[];
}

interface ExecutiveSummaryProps {
  studyId: number;
}

export default function ExecutiveSummary({ studyId }: ExecutiveSummaryProps) {
  const [summary, setSummary] = useState<ExecutiveSummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchExecutiveSummary();
  }, [studyId]);

  const fetchExecutiveSummary = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/viability/${studyId}/summary`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSummary(data);
      } else {
        setError('Error cargando resumen ejecutivo');
      }
    } catch (err) {
      setError('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="text-center text-red-600">
          {error || 'No se pudo cargar el resumen ejecutivo'}
        </div>
      </div>
    );
  }

  const getGradeColor = (grade: string) => {
    switch (grade.toUpperCase()) {
      case 'A': return 'text-green-600 bg-green-50 border-green-200';
      case 'B': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'C': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'D': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getRiskColor = (risk: string) => {
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

  return (
    <div className="bg-white rounded-lg shadow-sm">
      {/* Header */}
      <div className="border-b border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-blue-600" />
            Resumen Ejecutivo
          </h3>
          
          <div className="flex items-center space-x-4">
            {/* Investment Grade */}
            <div className={`px-3 py-1 rounded-full border text-sm font-medium ${getGradeColor(summary.investment_grade)}`}>
              Grado: {summary.investment_grade}
            </div>
            
            {/* Risk Assessment */}
            <div className={`px-3 py-1 rounded-full border text-sm font-medium ${getRiskColor(summary.risk_assessment)}`}>
              Riesgo: {summary.risk_assessment}
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
                  {formatCurrency(summary.key_metrics.total_investment)}
                </p>
              </div>
            </div>
          </div>

          {/* Monthly Cashflow */}
          <div className={`rounded-lg p-4 border ${
            summary.key_metrics.monthly_cashflow >= 0 
              ? 'bg-green-50 border-green-200' 
              : 'bg-red-50 border-red-200'
          }`}>
            <div className="flex items-center">
              {summary.key_metrics.monthly_cashflow >= 0 ? (
                <TrendingUp className="h-8 w-8 text-green-600" />
              ) : (
                <TrendingDown className="h-8 w-8 text-red-600" />
              )}
              <div className="ml-3">
                <p className={`text-sm font-medium ${
                  summary.key_metrics.monthly_cashflow >= 0 ? 'text-green-900' : 'text-red-900'
                }`}>
                  Cashflow Mensual
                </p>
                <p className={`text-lg font-bold ${
                  summary.key_metrics.monthly_cashflow >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatCurrency(summary.key_metrics.monthly_cashflow)}
                </p>
              </div>
            </div>
          </div>

          {/* Annual Return */}
          <div className={`rounded-lg p-4 border ${
            summary.key_metrics.annual_return >= 0 
              ? 'bg-green-50 border-green-200' 
              : 'bg-red-50 border-red-200'
          }`}>
            <div className="flex items-center">
              <Percent className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-green-900">Rentabilidad Anual</p>
                <p className={`text-lg font-bold ${
                  summary.key_metrics.annual_return >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatPercentage(summary.key_metrics.annual_return)}
                </p>
              </div>
            </div>
          </div>

          {/* Payback Period */}
          <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-purple-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-purple-900">Payback</p>
                <p className="text-lg font-bold text-purple-600">
                  {summary.payback_period_years.toFixed(1)} años
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">LTV Ratio</h4>
            <p className="text-xl font-bold text-gray-700">
              {formatPercentage(summary.key_metrics.ltv_ratio)}
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Cap Rate</h4>
            <p className="text-xl font-bold text-gray-700">
              {formatPercentage(summary.key_metrics.cap_rate)}
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">DSCR</h4>
            <p className="text-xl font-bold text-gray-700">
              {summary.key_metrics.debt_service_coverage.toFixed(2)}x
            </p>
          </div>
        </div>

        {/* Recommendations and Warnings */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Recommendations */}
          {summary.recommendations.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
                <TrendingUp className="h-4 w-4 mr-2 text-green-600" />
                Recomendaciones
              </h4>
              <ul className="space-y-2">
                {summary.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start">
                    <div className="flex-shrink-0 w-2 h-2 bg-green-500 rounded-full mt-2 mr-3"></div>
                    <span className="text-sm text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Warnings */}
          {summary.warnings.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
                <AlertTriangle className="h-4 w-4 mr-2 text-yellow-600" />
                Advertencias
              </h4>
              <ul className="space-y-2">
                {summary.warnings.map((warning, index) => (
                  <li key={index} className="flex items-start">
                    <div className="flex-shrink-0 w-2 h-2 bg-yellow-500 rounded-full mt-2 mr-3"></div>
                    <span className="text-sm text-gray-700">{warning}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Break Even Point */}
        <div className="mt-6 bg-blue-50 rounded-lg p-4 border border-blue-200">
          <h4 className="text-sm font-medium text-blue-900 mb-2">Punto de Equilibrio</h4>
          <p className="text-sm text-blue-700">{summary.break_even_point}</p>
        </div>
      </div>
    </div>
  );
}