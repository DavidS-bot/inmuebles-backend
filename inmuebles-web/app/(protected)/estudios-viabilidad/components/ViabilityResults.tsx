"use client";

import React, { useState, useEffect } from 'react';
import { X, TrendingUp, AlertTriangle, FileText, Download, Edit3, BarChart3, Target, DollarSign } from 'lucide-react';

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
}

interface ViabilityResultsProps {
  study: ViabilityStudy;
  onClose: () => void;
  onStudyUpdated: (study: ViabilityStudy) => void;
}

export default function ViabilityResults({ study, onClose, onStudyUpdated }: ViabilityResultsProps) {
  const [activeTab, setActiveTab] = useState('resumen');

  const tabs = [
    { id: 'resumen', label: 'Resumen Ejecutivo', icon: FileText },
    { id: 'proyeccion', label: 'Proyección Temporal', icon: TrendingUp },
    { id: 'sensibilidad', label: 'Análisis Sensibilidad', icon: BarChart3 },
    { id: 'metricas', label: 'Métricas Detalladas', icon: Target }
  ];

  const getRiskBadgeColor = (risk: string) => {
    switch (risk) {
      case 'LOW': return 'bg-green-100 text-green-800 border-green-200';
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'HIGH': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const rentBuffer = study.monthly_rent > 0 ? ((study.monthly_rent - study.break_even_rent) / study.monthly_rent * 100) : 0;
  const paybackPeriod = study.annual_net_cashflow > 0 ? study.down_payment / study.annual_net_cashflow : null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-7xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b bg-gray-50">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{study.study_name}</h2>
            <div className="flex items-center gap-4 mt-2">
              <span className={`px-3 py-1 text-sm rounded-full border ${getRiskBadgeColor(study.risk_level)}`}>
                Riesgo {study.risk_level}
              </span>
              <span className={`px-3 py-1 text-sm rounded-full ${
                study.is_favorable 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {study.is_favorable ? 'Favorable' : 'No Favorable'}
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100">
              <Download className="h-5 w-5" />
            </button>
            <button className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100">
              <Edit3 className="h-5 w-5" />
            </button>
            <button onClick={onClose} className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100">
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        <div className="flex">
          {/* Sidebar */}
          <div className="w-64 bg-gray-50 border-r">
            <nav className="p-4">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 mb-2 rounded-lg transition-colors text-left ${
                    activeTab === tab.id
                      ? 'bg-blue-100 text-blue-700 border border-blue-300'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <tab.icon className="h-5 w-5" />
                  {tab.label}
                </button>
              ))}
            </nav>

            {/* Quick Stats */}
            <div className="p-4 border-t">
              <h3 className="font-semibold text-gray-900 mb-3">Métricas Clave</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Inversión:</span>
                  <span className="font-medium">{study.down_payment.toLocaleString()}€</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Cashflow:</span>
                  <span className={`font-medium ${study.monthly_net_cashflow >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {study.monthly_net_cashflow > 0 ? '+' : ''}{study.monthly_net_cashflow.toFixed(0)}€
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">ROI:</span>
                  <span className={`font-medium ${study.net_annual_return >= 0.05 ? 'text-green-600' : 'text-red-600'}`}>
                    {(study.net_annual_return * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">LTV:</span>
                  <span className="font-medium">{(study.loan_to_value * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 overflow-y-auto">
            {activeTab === 'resumen' && (
              <div className="p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-6">Resumen Ejecutivo</h3>
                
                {/* Investment Overview */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <DollarSign className="h-8 w-8 text-blue-600" />
                      <h4 className="text-lg font-semibold text-blue-900">Inversión</h4>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-blue-700">Precio compra:</span>
                        <span className="font-medium text-blue-900">{study.purchase_price.toLocaleString()}€</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-blue-700">Total invertido:</span>
                        <span className="font-medium text-blue-900">{study.total_purchase_price.toLocaleString()}€</span>
                      </div>
                      <div className="flex justify-between border-t border-blue-200 pt-2">
                        <span className="text-blue-700">Entrada propia:</span>
                        <span className="font-bold text-blue-900">{study.down_payment.toLocaleString()}€</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-blue-700">Financiación:</span>
                        <span className="font-medium text-blue-900">{study.loan_amount.toLocaleString()}€</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <TrendingUp className="h-8 w-8 text-green-600" />
                      <h4 className="text-lg font-semibold text-green-900">Rentabilidad</h4>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-green-700">ROI Neto:</span>
                        <span className="font-bold text-green-900 text-xl">
                          {(study.net_annual_return * 100).toFixed(2)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-green-700">ROI Total:</span>
                        <span className="font-medium text-green-900">
                          {(study.total_annual_return * 100).toFixed(2)}%
                        </span>
                      </div>
                      <div className="flex justify-between border-t border-green-200 pt-2">
                        <span className="text-green-700">Cashflow/mes:</span>
                        <span className={`font-medium ${study.monthly_net_cashflow >= 0 ? 'text-green-900' : 'text-red-600'}`}>
                          {study.monthly_net_cashflow > 0 ? '+' : ''}{study.monthly_net_cashflow.toFixed(0)}€
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-green-700">Cashflow/año:</span>
                        <span className={`font-medium ${study.annual_net_cashflow >= 0 ? 'text-green-900' : 'text-red-600'}`}>
                          {study.annual_net_cashflow > 0 ? '+' : ''}{study.annual_net_cashflow.toFixed(0)}€
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className={`border rounded-lg p-6 ${
                    study.risk_level === 'LOW' ? 'bg-green-50 border-green-200' :
                    study.risk_level === 'MEDIUM' ? 'bg-yellow-50 border-yellow-200' :
                    'bg-red-50 border-red-200'
                  }`}>
                    <div className="flex items-center gap-3 mb-4">
                      <AlertTriangle className={`h-8 w-8 ${
                        study.risk_level === 'LOW' ? 'text-green-600' :
                        study.risk_level === 'MEDIUM' ? 'text-yellow-600' :
                        'text-red-600'
                      }`} />
                      <h4 className={`text-lg font-semibold ${
                        study.risk_level === 'LOW' ? 'text-green-900' :
                        study.risk_level === 'MEDIUM' ? 'text-yellow-900' :
                        'text-red-900'
                      }`}>Riesgo</h4>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className={study.risk_level === 'LOW' ? 'text-green-700' : study.risk_level === 'MEDIUM' ? 'text-yellow-700' : 'text-red-700'}>
                          Nivel:
                        </span>
                        <span className={`font-bold ${
                          study.risk_level === 'LOW' ? 'text-green-900' :
                          study.risk_level === 'MEDIUM' ? 'text-yellow-900' :
                          'text-red-900'
                        }`}>
                          {study.risk_level}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className={study.risk_level === 'LOW' ? 'text-green-700' : study.risk_level === 'MEDIUM' ? 'text-yellow-700' : 'text-red-700'}>
                          Break-even:
                        </span>
                        <span className={`font-medium ${
                          study.risk_level === 'LOW' ? 'text-green-900' :
                          study.risk_level === 'MEDIUM' ? 'text-yellow-900' :
                          'text-red-900'
                        }`}>
                          {study.break_even_rent.toFixed(0)}€
                        </span>
                      </div>
                      <div className="flex justify-between border-t pt-2" style={{borderColor: study.risk_level === 'LOW' ? '#dcfce7' : study.risk_level === 'MEDIUM' ? '#fef3c7' : '#fee2e2'}}>
                        <span className={study.risk_level === 'LOW' ? 'text-green-700' : study.risk_level === 'MEDIUM' ? 'text-yellow-700' : 'text-red-700'}>
                          Buffer renta:
                        </span>
                        <span className={`font-medium ${
                          rentBuffer > 20 ? 'text-green-600' :
                          rentBuffer > 10 ? 'text-yellow-600' :
                          'text-red-600'
                        }`}>
                          {rentBuffer.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Summary table for quick comparison */}
                <div className="overflow-x-auto">
                  <table className="min-w-full border border-gray-200 rounded-lg">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Métrica</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Valor</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Evaluación</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      <tr>
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">ROI Neto Anual</td>
                        <td className="px-4 py-3 text-sm text-right">{(study.net_annual_return * 100).toFixed(2)}%</td>
                        <td className={`px-4 py-3 text-sm text-right ${
                          study.net_annual_return >= 0.08 ? 'text-green-600' :
                          study.net_annual_return >= 0.05 ? 'text-yellow-600' :
                          'text-red-600'
                        }`}>
                          {study.net_annual_return >= 0.08 ? 'Excelente' :
                           study.net_annual_return >= 0.05 ? 'Bueno' : 'Bajo'}
                        </td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">Cashflow Mensual</td>
                        <td className="px-4 py-3 text-sm text-right">{study.monthly_net_cashflow.toFixed(0)}€</td>
                        <td className={`px-4 py-3 text-sm text-right ${
                          study.monthly_net_cashflow >= 200 ? 'text-green-600' :
                          study.monthly_net_cashflow >= 0 ? 'text-yellow-600' :
                          'text-red-600'
                        }`}>
                          {study.monthly_net_cashflow >= 200 ? 'Excelente' :
                           study.monthly_net_cashflow >= 0 ? 'Neutro' : 'Negativo'}
                        </td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">LTV</td>
                        <td className="px-4 py-3 text-sm text-right">{(study.loan_to_value * 100).toFixed(1)}%</td>
                        <td className={`px-4 py-3 text-sm text-right ${
                          study.loan_to_value <= 0.7 ? 'text-green-600' :
                          study.loan_to_value <= 0.8 ? 'text-yellow-600' :
                          'text-red-600'
                        }`}>
                          {study.loan_to_value <= 0.7 ? 'Conservador' :
                           study.loan_to_value <= 0.8 ? 'Estándar' : 'Alto'}
                        </td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">Buffer de Renta</td>
                        <td className="px-4 py-3 text-sm text-right">{rentBuffer.toFixed(1)}%</td>
                        <td className={`px-4 py-3 text-sm text-right ${
                          rentBuffer >= 20 ? 'text-green-600' :
                          rentBuffer >= 10 ? 'text-yellow-600' :
                          'text-red-600'
                        }`}>
                          {rentBuffer >= 20 ? 'Amplio' :
                           rentBuffer >= 10 ? 'Adecuado' : 'Ajustado'}
                        </td>
                      </tr>
                      {paybackPeriod && (
                        <tr>
                          <td className="px-4 py-3 text-sm font-medium text-gray-900">Periodo Recuperación</td>
                          <td className="px-4 py-3 text-sm text-right">{paybackPeriod.toFixed(1)} años</td>
                          <td className={`px-4 py-3 text-sm text-right ${
                            paybackPeriod <= 12 ? 'text-green-600' :
                            paybackPeriod <= 20 ? 'text-yellow-600' :
                            'text-red-600'
                          }`}>
                            {paybackPeriod <= 12 ? 'Rápido' :
                             paybackPeriod <= 20 ? 'Moderado' : 'Lento'}
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Placeholder for other tabs */}
            {activeTab !== 'resumen' && (
              <div className="p-6 flex items-center justify-center h-64">
                <div className="text-center">
                  <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-xl text-gray-600 mb-2">Funcionalidad en desarrollo</p>
                  <p className="text-gray-500">Esta sección estará disponible próximamente</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}