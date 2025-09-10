"use client";

import React, { useState } from 'react';
import { X } from 'lucide-react';

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

interface SimpleViabilityResultsProps {
  study: ViabilityStudy;
  onClose: () => void;
}

export default function SimpleViabilityResults({ study, onClose }: SimpleViabilityResultsProps) {
  const [activeTab, setActiveTab] = useState('basic');

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

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="border-b border-gray-200 p-6">
          <div className="flex items-center justify-between">
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

        {/* Tabs */}
        <div className="border-b border-gray-200 bg-white">
          <nav className="flex">
            <button
              onClick={() => setActiveTab('basic')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'basic'
                  ? 'border-blue-500 text-blue-600 bg-blue-50'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Datos Básicos
            </button>
            <button
              onClick={() => setActiveTab('advanced')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'advanced'
                  ? 'border-blue-500 text-blue-600 bg-blue-50'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Análisis Avanzado
            </button>
          </nav>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-200px)] p-6">
          {activeTab === 'basic' && (
            <div className="space-y-6">
              {/* Investment Summary */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Resumen de la Inversión</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Precio de Compra:</span>
                      <span className="font-medium">{formatCurrency(study.purchase_price)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Gastos de Compra:</span>
                      <span className="font-medium">{formatCurrency(study.purchase_costs)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Inversión Total:</span>
                      <span className="font-bold text-lg">{formatCurrency(study.total_purchase_price)}</span>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Entrada (Down Payment):</span>
                      <span className="font-medium">{formatCurrency(study.down_payment)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Préstamo:</span>
                      <span className="font-medium">{formatCurrency(study.loan_amount)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">LTV:</span>
                      <span className="font-medium">{formatPercentage(study.loan_to_value)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Monthly Analysis */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Análisis Mensual</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Alquiler Mensual:</span>
                      <span className="font-medium text-green-600">{formatCurrency(study.monthly_rent)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Pago Hipoteca:</span>
                      <span className="font-medium text-red-600">{formatCurrency(study.monthly_mortgage_payment)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Cashflow Neto:</span>
                      <span className={`font-bold text-lg ${study.monthly_net_cashflow >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(study.monthly_net_cashflow)}
                      </span>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">ROI Anual Neto:</span>
                      <span className={`font-medium ${study.net_annual_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatPercentage(study.net_annual_return)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Break Even Rent:</span>
                      <span className="font-medium">{formatCurrency(study.break_even_rent)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Nivel de Riesgo:</span>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${getRiskColor(study.risk_level)}`}>
                        {study.risk_level}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                  <h4 className="font-medium text-blue-900">Rentabilidad</h4>
                  <p className="text-2xl font-bold text-blue-600">
                    {formatPercentage(study.net_annual_return)}
                  </p>
                  <p className="text-sm text-blue-700">ROI Anual Neto</p>
                </div>
                
                <div className={`rounded-lg p-4 border ${study.monthly_net_cashflow >= 0 ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                  <h4 className={`font-medium ${study.monthly_net_cashflow >= 0 ? 'text-green-900' : 'text-red-900'}`}>
                    Cashflow
                  </h4>
                  <p className={`text-2xl font-bold ${study.monthly_net_cashflow >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(study.monthly_net_cashflow)}
                  </p>
                  <p className={`text-sm ${study.monthly_net_cashflow >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                    Mensual
                  </p>
                </div>
                
                <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                  <h4 className="font-medium text-purple-900">Apalancamiento</h4>
                  <p className="text-2xl font-bold text-purple-600">
                    {formatPercentage(study.loan_to_value)}
                  </p>
                  <p className="text-sm text-purple-700">LTV Ratio</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'advanced' && (
            <div className="space-y-6">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-yellow-800">
                      Funciones Avanzadas en Desarrollo
                    </h3>
                    <div className="mt-2 text-sm text-yellow-700">
                      <p>Las siguientes funciones estarán disponibles próximamente:</p>
                      <ul className="mt-2 space-y-1">
                        <li>• Resumen Ejecutivo con KPIs</li>
                        <li>• Proyección Temporal (5-30 años)</li>
                        <li>• Análisis de Sensibilidad</li>
                        <li>• Métricas Detalladas con Charts</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Basic Financial Ratios */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Ratios Financieros</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">
                      {((study.monthly_rent * 12) / study.purchase_price * 100).toFixed(2)}%
                    </p>
                    <p className="text-sm text-gray-600">Yield Bruto</p>
                  </div>
                  
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">
                      {(study.net_annual_return * 100).toFixed(2)}%
                    </p>
                    <p className="text-sm text-gray-600">Yield Neto</p>
                  </div>
                  
                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">
                      {(study.loan_to_value * 100).toFixed(1)}%
                    </p>
                    <p className="text-sm text-gray-600">LTV</p>
                  </div>
                  
                  <div className="text-center">
                    <p className="text-2xl font-bold text-orange-600">
                      {((study.monthly_rent * 0.8) / study.monthly_mortgage_payment).toFixed(1)}x
                    </p>
                    <p className="text-sm text-gray-600">DSCR</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 bg-gray-50 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              {study.is_favorable ? '✅ Inversión Favorable' : '❌ Inversión No Favorable'}
            </div>
            
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 transition-colors"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}