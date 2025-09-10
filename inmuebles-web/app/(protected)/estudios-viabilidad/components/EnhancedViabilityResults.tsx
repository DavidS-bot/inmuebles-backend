"use client";

import React, { useState } from 'react';
import { X, FileText, BarChart3, Target, DollarSign, TrendingUp, Activity, Calculator } from 'lucide-react';
import ExecutiveSummary from './ExecutiveSummary';
import TemporalProjection from './TemporalProjection';
import SensitivityAnalysis from './SensitivityAnalysis';
import DetailedMetrics from './DetailedMetrics';

interface ViabilityStudy {
  id: number;
  study_name: string;
  purchase_price: number;
  total_purchase_price: number;
  down_payment: number;
  loan_amount: number;
  loan_to_value: number;
  monthly_rent: number;
  monthly_mortgage_payment: number;
  net_annual_return: number;
  total_annual_return: number;
  monthly_net_cashflow: number;
  annual_net_cashflow: number;
  break_even_rent: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  is_favorable: boolean;
  interest_rate: number;
  loan_term_years: number;
  monthly_equity_increase: number;
  annual_equity_increase: number;
  purchase_costs: number;
  renovation_costs?: number;
  real_estate_commission?: number;
  community_fees?: number;
  property_tax_ibi?: number;
  home_insurance?: number;
  life_insurance?: number;
  maintenance_percentage: number;
  created_at?: string;
}

interface EnhancedViabilityResultsProps {
  study: ViabilityStudy;
  onClose: () => void;
}

export default function EnhancedViabilityResults({ study, onClose }: EnhancedViabilityResultsProps) {
  const [activeTab, setActiveTab] = useState('summary');

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

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'LOW': return 'text-green-600 bg-green-50 border-green-200';
      case 'MEDIUM': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'HIGH': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const tabs = [
    { 
      id: 'summary', 
      name: 'Resumen Ejecutivo', 
      icon: FileText, 
      description: 'KPIs clave y recomendaciones'
    },
    { 
      id: 'projection', 
      name: 'Proyección Temporal', 
      icon: TrendingUp, 
      description: 'Evolución a 10-30 años'
    },
    { 
      id: 'sensitivity', 
      name: 'Análisis de Sensibilidad', 
      icon: Activity, 
      description: 'Escenarios y factores de riesgo'
    },
    { 
      id: 'metrics', 
      name: 'Métricas Detalladas', 
      icon: Calculator, 
      description: 'Análisis financiero profundo'
    }
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-7xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="border-b border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div>
                <h2 className="text-xl font-bold text-gray-900">{study.study_name}</h2>
                <div className="flex items-center space-x-4 mt-2">
                  <span className="text-sm text-gray-600">
                    Inversión: {formatCurrency(study.total_purchase_price)}
                  </span>
                  <span className="text-sm text-gray-600">
                    ROI: {formatPercentage(study.net_annual_return)}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getRiskColor(study.risk_level)}`}>
                    {study.risk_level}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full border ${
                    study.is_favorable 
                      ? 'text-green-600 bg-green-50 border-green-200' 
                      : 'text-red-600 bg-red-50 border-red-200'
                  }`}>
                    {study.is_favorable ? 'FAVORABLE' : 'NO FAVORABLE'}
                  </span>
                </div>
              </div>
            </div>
            
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Quick Stats Bar */}
        <div className="border-b border-gray-200 bg-gray-50 px-6 py-3">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-sm text-gray-600">Cashflow Mensual</p>
              <p className={`font-bold ${study.monthly_net_cashflow >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(study.monthly_net_cashflow)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">LTV</p>
              <p className="font-bold text-blue-600">
                {formatPercentage(study.loan_to_value)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Break Even</p>
              <p className="font-bold text-purple-600">
                {formatCurrency(study.break_even_rent)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Entrada</p>
              <p className="font-bold text-orange-600">
                {formatCurrency(study.down_payment)}
              </p>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="border-b border-gray-200 bg-white">
          <nav className="flex overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-shrink-0 flex items-center px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600 bg-blue-50'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  <div className="text-left">
                    <div>{tab.name}</div>
                    <div className="text-xs text-gray-400 font-normal">
                      {tab.description}
                    </div>
                  </div>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-200px)]">
          {activeTab === 'summary' && (
            <div className="p-6">
              <ExecutiveSummary studyId={study.id} />
            </div>
          )}

          {activeTab === 'projection' && (
            <div className="p-6">
              <TemporalProjection studyId={study.id} />
            </div>
          )}

          {activeTab === 'sensitivity' && (
            <div className="p-6">
              <SensitivityAnalysis studyId={study.id} />
            </div>
          )}

          {activeTab === 'metrics' && (
            <div className="p-6">
              <DetailedMetrics study={study} />
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="border-t border-gray-200 bg-gray-50 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Estudio creado: {new Date(study.created_at || Date.now()).toLocaleDateString('es-ES')}
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => window.print()}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                Imprimir Informe
              </button>
              
              <button
                onClick={() => {
                  // TODO: Implement export functionality
                  alert('Función de exportación en desarrollo');
                }}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 transition-colors"
              >
                Exportar PDF
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}