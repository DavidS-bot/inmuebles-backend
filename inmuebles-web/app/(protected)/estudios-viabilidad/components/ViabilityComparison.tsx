"use client";

import React, { useState, useEffect } from 'react';
import { X, TrendingUp, BarChart3 } from 'lucide-react';

interface ViabilityComparisonProps {
  studyIds: number[];
  onClose: () => void;
}

export default function ViabilityComparison({ studyIds, onClose }: ViabilityComparisonProps) {
  const [comparisonData, setComparisonData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchComparison();
  }, [studyIds]);

  const fetchComparison = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/viability/compare`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(studyIds)
      });
      
      if (response.ok) {
        const data = await response.json();
        setComparisonData(data);
      }
    } catch (error) {
      console.error('Error fetching comparison:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
        <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-hidden">
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b bg-gray-50">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <BarChart3 className="h-6 w-6 text-blue-600" />
              Comparación de Estudios
            </h2>
            <p className="text-gray-600 mt-1">Análisis comparativo de {studyIds.length} estudios</p>
          </div>
          
          <button onClick={onClose} className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
          {comparisonData ? (
            <div className="space-y-8">
              {/* Winners Section */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h3 className="font-semibold text-green-900 mb-2">Mejor Cashflow</h3>
                  <p className="text-sm text-green-700">{comparisonData.best_cash_flow?.study_name}</p>
                  <p className="text-lg font-bold text-green-900">
                    +{comparisonData.best_cash_flow?.value.toFixed(0)}€/mes
                  </p>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900 mb-2">Mejor ROI Neto</h3>
                  <p className="text-sm text-blue-700">{comparisonData.best_net_return?.study_name}</p>
                  <p className="text-lg font-bold text-blue-900">
                    {(comparisonData.best_net_return?.value * 100).toFixed(1)}%
                  </p>
                </div>

                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h3 className="font-semibold text-purple-900 mb-2">Mejor ROI Total</h3>
                  <p className="text-sm text-purple-700">{comparisonData.best_total_return?.study_name}</p>
                  <p className="text-lg font-bold text-purple-900">
                    {(comparisonData.best_total_return?.value * 100).toFixed(1)}%
                  </p>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h3 className="font-semibold text-yellow-900 mb-2">Menor Riesgo</h3>
                  <p className="text-sm text-yellow-700">{comparisonData.lowest_risk?.study_name}</p>
                  <p className="text-lg font-bold text-yellow-900">
                    {comparisonData.lowest_risk?.risk_level}
                  </p>
                </div>
              </div>

              {/* Comparison Table */}
              <div className="overflow-x-auto">
                <table className="min-w-full border border-gray-200 rounded-lg">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estudio</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Precio</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Entrada</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Renta</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Cashflow</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">ROI Neto</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">ROI Total</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">LTV</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Riesgo</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Estado</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {comparisonData.summary.map((study: any) => (
                      <tr key={study.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">
                          {study.name}
                        </td>
                        <td className="px-4 py-3 text-sm text-right">
                          {study.purchase_price.toLocaleString()}€
                        </td>
                        <td className="px-4 py-3 text-sm text-right">
                          {study.down_payment.toLocaleString()}€
                        </td>
                        <td className="px-4 py-3 text-sm text-right">
                          {study.monthly_rent.toLocaleString()}€
                        </td>
                        <td className={`px-4 py-3 text-sm text-right ${
                          study.monthly_cashflow >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {study.monthly_cashflow > 0 ? '+' : ''}{study.monthly_cashflow.toFixed(0)}€
                        </td>
                        <td className={`px-4 py-3 text-sm text-right ${
                          study.net_annual_return >= 0.05 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {(study.net_annual_return * 100).toFixed(1)}%
                        </td>
                        <td className={`px-4 py-3 text-sm text-right ${
                          study.total_annual_return >= 0.08 ? 'text-green-600' : 'text-yellow-600'
                        }`}>
                          {(study.total_annual_return * 100).toFixed(1)}%
                        </td>
                        <td className="px-4 py-3 text-sm text-right">
                          {(study.loan_to_value * 100).toFixed(1)}%
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            study.risk_level === 'LOW' ? 'bg-green-100 text-green-800' :
                            study.risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {study.risk_level}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            study.is_favorable ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {study.is_favorable ? 'Favorable' : 'No favorable'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No se pudo cargar la comparación
            </div>
          )}
        </div>
      </div>
    </div>
  );
}