"use client";

import React, { useState, useEffect } from 'react';
import { Calculator, TrendingUp, AlertTriangle, FileText, Plus, Search, Filter } from 'lucide-react';
import ViabilityForm from './components/ViabilityForm';
import ViabilityResults from './components/ViabilityResults';
import ViabilityComparison from './components/ViabilityComparison';

interface ViabilityStudy {
  id: number;
  study_name: string;
  purchase_price: number;
  monthly_rent: number;
  down_payment: number;
  loan_to_value: number;
  net_annual_return: number;
  total_annual_return: number;
  monthly_net_cashflow: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  is_favorable: boolean;
  created_at: string;
  break_even_rent: number;
}

export default function EstudiosViabilidad() {
  const [studies, setStudies] = useState<ViabilityStudy[]>([]);
  const [activeStudy, setActiveStudy] = useState<ViabilityStudy | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [showComparison, setShowComparison] = useState(false);
  const [selectedStudies, setSelectedStudies] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRisk, setFilterRisk] = useState<string>('ALL');

  useEffect(() => {
    fetchViabilityStudies();
  }, []);

  const fetchViabilityStudies = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/viability/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setStudies(data);
      }
    } catch (error) {
      console.error('Error fetching studies:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStudyCreated = (newStudy: ViabilityStudy) => {
    setStudies([...studies, newStudy]);
    setShowForm(false);
  };

  const handleStudyDeleted = async (studyId: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este estudio?')) {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/viability/${studyId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        
        if (response.ok) {
          setStudies(studies.filter(s => s.id !== studyId));
        }
      } catch (error) {
        console.error('Error deleting study:', error);
      }
    }
  };

  const filteredStudies = studies.filter(study => {
    const matchesSearch = study.study_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRisk = filterRisk === 'ALL' || study.risk_level === filterRisk;
    return matchesSearch && matchesRisk;
  });

  const studyStats = {
    total: studies.length,
    favorable: studies.filter(s => s.is_favorable).length,
    avgReturn: studies.length > 0 ? studies.reduce((sum, s) => sum + s.net_annual_return, 0) / studies.length : 0,
    avgCashflow: studies.length > 0 ? studies.reduce((sum, s) => sum + s.monthly_net_cashflow, 0) / studies.length : 0
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Calculator className="h-8 w-8 text-blue-600" />
            Estudios de Viabilidad
          </h1>
          <p className="text-gray-600 mt-2">
            Análisis completo de rentabilidad y riesgo para inversiones inmobiliarias
          </p>
        </div>
        
        <div className="flex gap-2">
          {selectedStudies.length > 1 && (
            <button
              onClick={() => setShowComparison(true)}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
            >
              <TrendingUp className="h-4 w-4" />
              Comparar ({selectedStudies.length})
            </button>
          )}
          
          <button
            onClick={() => setShowForm(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <Plus className="h-5 w-5" />
            Nuevo Estudio
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Calculator className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Total Estudios</p>
              <p className="text-2xl font-semibold text-gray-900">{studyStats.total}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Favorables</p>
              <p className="text-2xl font-semibold text-gray-900">{studyStats.favorable}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <FileText className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Rentabilidad Media</p>
              <p className="text-2xl font-semibold text-gray-900">
                {(studyStats.avgReturn * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Cashflow Medio</p>
              <p className="text-2xl font-semibold text-gray-900">
                {studyStats.avgCashflow.toFixed(0)}€
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar estudios..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-gray-500" />
          <select
            value={filterRisk}
            onChange={(e) => setFilterRisk(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="ALL">Todos los riesgos</option>
            <option value="LOW">Riesgo Bajo</option>
            <option value="MEDIUM">Riesgo Medio</option>
            <option value="HIGH">Riesgo Alto</option>
          </select>
        </div>
      </div>

      {/* Studies List */}
      {filteredStudies.length === 0 ? (
        <div className="text-center py-12">
          <Calculator className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <p className="text-xl text-gray-600 mb-2">No tienes estudios de viabilidad</p>
          <p className="text-gray-500 mb-6">Crea tu primer análisis de inversión inmobiliaria</p>
          <button
            onClick={() => setShowForm(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Crear Primer Estudio
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredStudies.map((study) => (
            <div key={study.id} className="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow">
              {/* Header with selection */}
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={selectedStudies.includes(study.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedStudies([...selectedStudies, study.id]);
                      } else {
                        setSelectedStudies(selectedStudies.filter(id => id !== study.id));
                      }
                    }}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <h3 className="text-lg font-semibold text-gray-900 flex-1">{study.study_name}</h3>
                </div>
                
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    study.risk_level === 'LOW' ? 'bg-green-100 text-green-800' :
                    study.risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {study.risk_level}
                  </span>
                </div>
              </div>
              
              {/* Key Metrics */}
              <div className="space-y-3 mb-4">
                <div className="flex justify-between">
                  <span className="text-gray-600">Precio compra:</span>
                  <span className="font-medium">{study.purchase_price.toLocaleString()}€</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Renta mensual:</span>
                  <span className="font-medium">{study.monthly_rent.toLocaleString()}€</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Entrada:</span>
                  <span className="font-medium">{study.down_payment.toLocaleString()}€</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">LTV:</span>
                  <span className="font-medium">{(study.loan_to_value * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between border-t pt-2">
                  <span className="text-gray-600">Cashflow:</span>
                  <span className={`font-medium ${study.monthly_net_cashflow >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {study.monthly_net_cashflow > 0 ? '+' : ''}{study.monthly_net_cashflow.toFixed(0)}€
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Rentabilidad neta:</span>
                  <span className={`font-medium ${study.net_annual_return >= 0.05 ? 'text-green-600' : 'text-red-600'}`}>
                    {(study.net_annual_return * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Rentabilidad total:</span>
                  <span className={`font-medium ${study.total_annual_return >= 0.08 ? 'text-green-600' : 'text-orange-600'}`}>
                    {(study.total_annual_return * 100).toFixed(2)}%
                  </span>
                </div>
              </div>
              
              {/* Status and Actions */}
              <div className="flex justify-between items-center pt-4 border-t">
                <div className="flex items-center gap-2">
                  {study.is_favorable ? (
                    <TrendingUp className="h-4 w-4 text-green-600" />
                  ) : (
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                  )}
                  <span className={`text-sm ${study.is_favorable ? 'text-green-600' : 'text-red-600'}`}>
                    {study.is_favorable ? 'Favorable' : 'No favorable'}
                  </span>
                </div>
                
                <div className="flex gap-2">
                  <button
                    onClick={() => setActiveStudy(study)}
                    className="text-blue-600 hover:text-blue-800 flex items-center gap-1 px-2 py-1 rounded hover:bg-blue-50"
                  >
                    <FileText className="h-4 w-4" />
                    Detalle
                  </button>
                  <button
                    onClick={() => handleStudyDeleted(study.id)}
                    className="text-red-600 hover:text-red-800 px-2 py-1 rounded hover:bg-red-50"
                  >
                    ×
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modals */}
      {showForm && (
        <ViabilityForm
          onClose={() => setShowForm(false)}
          onStudyCreated={handleStudyCreated}
        />
      )}

      {activeStudy && (
        <ViabilityResults
          study={activeStudy}
          onClose={() => setActiveStudy(null)}
          onStudyUpdated={(updatedStudy) => {
            setStudies(studies.map(s => s.id === updatedStudy.id ? updatedStudy : s));
            setActiveStudy(updatedStudy);
          }}
        />
      )}

      {showComparison && selectedStudies.length > 1 && (
        <ViabilityComparison
          studyIds={selectedStudies}
          onClose={() => setShowComparison(false)}
        />
      )}
    </div>
  );
}