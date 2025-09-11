'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import { Calculator, TrendingUp, AlertTriangle, CheckCircle, Download, FileText, DollarSign, Calendar, Target, Lightbulb } from 'lucide-react';

interface TaxSummary {
  rental_income: number;
  deductible_expenses: number;
  net_income: number;
  tax_liability: number;
  effective_rate: number;
  savings_opportunities: number;
}

interface TaxDeduction {
  concept: string;
  amount: number;
  percentage: number;
  description: string;
}

interface TaxReport {
  year: number;
  total_rental_income: number;
  total_expenses: number;
  depreciation: number;
  net_result: number;
  tax_rate: number;
  tax_amount: number;
  quarterly_payments: number[];
}

interface Modelo115Data {
  year: number;
  quarter: number;
  total_income: number;
  withholding_rate: number;
  withholding_amount: number;
  previous_withholdings: number;
  net_amount_to_pay: number;
  due_date: string;
  form_data: any;
}

interface ExpenseOptimization {
  category: string;
  current_amount: number;
  potential_savings: number;
  suggestions: string[];
  priority: string;
  confidence: number;
}

interface FiscalDashboard {
  ytd_savings: number;
  upcoming_deadlines: any[];
  optimization_suggestions: ExpenseOptimization[];
  quarterly_comparison: Record<string, number>;
  tax_efficiency_score: number;
  alerts: any[];
}

export default function TaxAssistantPage() {
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedQuarter, setSelectedQuarter] = useState(1);
  const [taxSummary, setTaxSummary] = useState<TaxSummary | null>(null);
  const [deductions, setDeductions] = useState<TaxDeduction[]>([]);
  const [annualReport, setAnnualReport] = useState<TaxReport | null>(null);
  const [fiscalDashboard, setFiscalDashboard] = useState<FiscalDashboard | null>(null);
  const [expenseOptimizer, setExpenseOptimizer] = useState<any>(null);
  const [modelo115, setModelo115] = useState<Modelo115Data | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'modelo115' | 'optimizer' | 'report' | 'planning'>('dashboard');
  const [modelo115Input, setModelo115Input] = useState({
    rental_income: 0,
    previous_withholdings: 0
  });
  const router = useRouter();

  useEffect(() => {
    fetchTaxData();
  }, [selectedYear]);

  const fetchTaxData = async () => {
    setLoading(true);
    try {
      const [summaryRes, deductionsRes, reportRes, dashboardRes, optimizerRes] = await Promise.all([
        fetch(`http://localhost:8000/tax-assistant/summary/${selectedYear}`),
        fetch(`http://localhost:8000/tax-assistant/deductions/${selectedYear}`),
        fetch(`http://localhost:8000/tax-assistant/annual-report/${selectedYear}`),
        fetch(`http://localhost:8000/tax-assistant/fiscal-dashboard/${selectedYear}`),
        fetch(`http://localhost:8000/tax-assistant/expense-optimizer/${selectedYear}`)
      ]);

      const summaryData = await summaryRes.json();
      const deductionsData = await deductionsRes.json();
      const reportData = await reportRes.json();
      const dashboardData = await dashboardRes.json();
      const optimizerData = await optimizerRes.json();

      setTaxSummary(summaryData);
      setDeductions(deductionsData.deductions || []);
      setAnnualReport(reportData);
      setFiscalDashboard(dashboardData);
      setExpenseOptimizer(optimizerData);
    } catch (error) {
      console.error('Error fetching tax data:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateModelo115 = async () => {
    try {
      const response = await fetch(`http://localhost:8000/tax-assistant/modelo-115/calculate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          year: selectedYear,
          quarter: selectedQuarter,
          rental_income: modelo115Input.rental_income,
          previous_withholdings: modelo115Input.previous_withholdings
        })
      });
      
      const data = await response.json();
      setModelo115(data);
    } catch (error) {
      console.error('Error calculating Modelo 115:', error);
    }
  };

  const downloadModelo115PDF = async () => {
    try {
      const response = await fetch(`http://localhost:8000/tax-assistant/modelo-115/generate-pdf/${selectedYear}/${selectedQuarter}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `modelo_115_${selectedYear}_Q${selectedQuarter}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading PDF:', error);
    }
  };

  const availableYears = [2024, 2023, 2022, 2021];

  if (loading) {
    return (
      <div className="min-h-screen p-8 flex items-center justify-center">
        <div className="glass-card p-8 rounded-xl">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="text-center mt-4 text-gray-600">Calculando datos fiscales...</p>
        </div>
      </div>
    );
  }

  return (
    <Layout
      title="Asistente Fiscal"
      subtitle="Optimización fiscal inteligente para propiedades inmobiliarias"
      breadcrumbs={[
        { label: 'Agente Financiero', href: '/financial-agent' },
        { label: 'Asistente Fiscal', href: '/financial-agent/tax-assistant' }
      ]}
      actions={
        <select
          value={selectedYear}
          onChange={(e) => setSelectedYear(Number(e.target.value))}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        >
          {availableYears.map(year => (
            <option key={year} value={year}>{year}</option>
          ))}
        </select>
      }
    >
      <div className="space-y-8">

      <div className="flex flex-wrap justify-center gap-2 mb-8">
        {[
          { key: 'dashboard', label: 'Dashboard Fiscal', icon: TrendingUp, color: 'indigo' },
          { key: 'modelo115', label: 'Modelo 115', icon: Calculator, color: 'green' },
          { key: 'optimizer', label: 'Optimizador', icon: Target, color: 'purple' },
          { key: 'report', label: 'Informe Anual', icon: FileText, color: 'blue' },
          { key: 'planning', label: 'Planificación', icon: Lightbulb, color: 'orange' }
        ].map(tab => {
          const IconComponent = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`px-6 py-3 rounded-lg transition-all flex items-center space-x-2 ${
                activeTab === tab.key
                  ? `bg-${tab.color}-600 text-white shadow-lg`
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              <IconComponent size={18} />
              <span className="font-medium">{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* DASHBOARD FISCAL */}
      {activeTab === 'dashboard' && fiscalDashboard && (
        <div className="space-y-6">
          {/* Métricas principales */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-6 rounded-xl shadow-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100 text-sm font-medium">Ahorro YTD</p>
                  <p className="text-3xl font-bold">€{(fiscalDashboard?.ytd_savings || 0).toLocaleString()}</p>
                </div>
                <TrendingUp className="w-8 h-8 text-green-200" />
              </div>
              <p className="text-green-100 text-xs mt-2">vs año anterior</p>
            </div>
            
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6 rounded-xl shadow-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm font-medium">Eficiencia Fiscal</p>
                  <p className="text-3xl font-bold">{(fiscalDashboard?.tax_efficiency_score || 0).toFixed(0)}%</p>
                </div>
                <Target className="w-8 h-8 text-blue-200" />
              </div>
              <p className="text-blue-100 text-xs mt-2">ratio gastos/ingresos</p>
            </div>
            
            <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-6 rounded-xl shadow-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-100 text-sm font-medium">Próximo Vencimiento</p>
                  <p className="text-lg font-bold">
                    {fiscalDashboard?.upcoming_deadlines?.[0]?.days_remaining || 'N/A'} días
                  </p>
                </div>
                <Calendar className="w-8 h-8 text-purple-200" />
              </div>
              <p className="text-purple-100 text-xs mt-2">
                {fiscalDashboard?.upcoming_deadlines?.[0]?.description || 'Sin vencimientos'}
              </p>
            </div>
            
            <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-6 rounded-xl shadow-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-orange-100 text-sm font-medium">Oportunidades</p>
                  <p className="text-3xl font-bold">{fiscalDashboard?.optimization_suggestions?.length || 0}</p>
                </div>
                <Lightbulb className="w-8 h-8 text-orange-200" />
              </div>
              <p className="text-orange-100 text-xs mt-2">mejoras identificadas</p>
            </div>
          </div>
          
          {/* Alertas proactivas */}
          {fiscalDashboard?.alerts && fiscalDashboard.alerts.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-500" />
                Alertas Proactivas
              </h3>
              <div className="space-y-3">
                {(fiscalDashboard?.alerts || []).map((alert, index) => (
                  <div key={index} className={`p-4 rounded-lg border-l-4 ${
                    alert.type === 'warning' ? 'bg-amber-50 border-amber-500' :
                    alert.type === 'success' ? 'bg-green-50 border-green-500' :
                    'bg-blue-50 border-blue-500'
                  }`}>
                    <h4 className="font-medium text-gray-900">{alert.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Comparativa trimestral */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Evolución Trimestral {selectedYear}</h3>
            <div className="grid grid-cols-4 gap-4">
              {Object.entries(fiscalDashboard?.quarterly_comparison || {}).map(([quarter, profit]) => (
                <div key={quarter} className="bg-gray-50 p-4 rounded-lg text-center">
                  <p className="text-sm font-medium text-gray-600">{quarter}</p>
                  <p className={`text-xl font-bold ${
                    (profit as number) > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    €{((profit as number) || 0).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* MODELO 115 CALCULATOR */}
      {activeTab === 'modelo115' && (
        <div className="space-y-6">
          {/* Input Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <Calculator className="w-6 h-6 text-green-600" />
              Calculadora Modelo 115 - Retención IRPF
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Año</label>
                <select
                  value={selectedYear}
                  onChange={(e) => setSelectedYear(Number(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                >
                  {[2024, 2023, 2022].map(year => (
                    <option key={year} value={year}>{year}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Trimestre</label>
                <select
                  value={selectedQuarter}
                  onChange={(e) => setSelectedQuarter(Number(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                >
                  {[1, 2, 3, 4].map(quarter => (
                    <option key={quarter} value={quarter}>{quarter}º Trimestre</option>
                  ))}
                </select>
              </div>
              
              <div className="md:col-span-1">
                <button
                  onClick={calculateModelo115}
                  className="w-full h-full bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
                >
                  Calcular Modelo 115
                </button>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Ingresos por Alquiler (€)</label>
                <input
                  type="number"
                  value={modelo115Input.rental_income}
                  onChange={(e) => setModelo115Input(prev => ({...prev, rental_income: Number(e.target.value)}))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  placeholder="Ej: 3000"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Retenciones Anteriores (€)</label>
                <input
                  type="number"
                  value={modelo115Input.previous_withholdings}
                  onChange={(e) => setModelo115Input(prev => ({...prev, previous_withholdings: Number(e.target.value)}))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  placeholder="Ej: 0"
                />
              </div>
            </div>
          </div>
          
          {/* Results Section */}
          {modelo115 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-semibold">Formulario 115 - {modelo115.year} Q{modelo115.quarter}</h3>
                <button
                  onClick={downloadModelo115PDF}
                  className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Download size={16} />
                  Descargar PDF
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex justify-between py-3 border-b">
                    <span className="font-medium">Ingresos Totales:</span>
                    <span className="font-semibold text-blue-600">€{(modelo115?.total_income || 0).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between py-3 border-b">
                    <span className="font-medium">Tipo de Retención:</span>
                    <span className="font-semibold">{((modelo115?.withholding_rate || 0) * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex justify-between py-3 border-b">
                    <span className="font-medium">Retención Practicada:</span>
                    <span className="font-semibold text-orange-600">€{(modelo115?.withholding_amount || 0).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between py-3 border-b">
                    <span className="font-medium">Retenciones Anteriores:</span>
                    <span className="font-semibold">€{(modelo115?.previous_withholdings || 0).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between py-3 border-b-2 border-gray-300 bg-green-50 px-4 rounded">
                    <span className="font-bold text-lg">A Ingresar:</span>
                    <span className="font-bold text-lg text-green-600">€{(modelo115?.net_amount_to_pay || 0).toLocaleString()}</span>
                  </div>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold mb-3 text-red-600">⚠️ Fecha Límite</h4>
                  <p className="text-2xl font-bold text-red-600">{modelo115?.due_date || 'N/A'}</p>
                  <p className="text-sm text-gray-600 mt-2">Presentación y pago del Modelo 115</p>
                  
                  <div className="mt-4 p-3 bg-blue-50 rounded border-l-4 border-blue-500">
                    <p className="text-sm text-blue-800">
                      <strong>Recuerda:</strong> El Modelo 115 debe presentarse trimestralmente, 
                      incluso si el importe a ingresar es cero.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* OPTIMIZADOR DE GASTOS */}
      {activeTab === 'optimizer' && expenseOptimizer && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <Target className="w-6 h-6 text-purple-600" />
              Optimizador de Gastos Deducibles IA
            </h2>
            
            {/* Resumen */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-blue-600 font-medium">Ingresos Totales</p>
                <p className="text-2xl font-bold text-blue-800">€{(expenseOptimizer?.total_income || 0).toLocaleString()}</p>
              </div>
              <div className="bg-red-50 p-4 rounded-lg">
                <p className="text-red-600 font-medium">Gastos Actuales</p>
                <p className="text-2xl font-bold text-red-800">€{(expenseOptimizer?.current_expenses || 0).toLocaleString()}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-green-600 font-medium">Ahorro Fiscal Estimado</p>
                <p className="text-2xl font-bold text-green-800">€{(expenseOptimizer?.estimated_tax_savings || 0).toLocaleString()}</p>
              </div>
            </div>
            
            {/* Sugerencias de optimización */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold mb-4">Sugerencias de Optimización IA-Powered</h3>
              {(expenseOptimizer?.optimizations || []).map((optimization: ExpenseOptimization, index: number) => (
                <div key={index} className={`border rounded-lg p-6 ${
                  optimization.priority === 'high' ? 'border-red-200 bg-red-50' :
                  optimization.priority === 'medium' ? 'border-yellow-200 bg-yellow-50' :
                  'border-green-200 bg-green-50'
                }`}>
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                        optimization.priority === 'high' ? 'bg-red-100 text-red-800' :
                        optimization.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {optimization.priority?.toUpperCase() || 'NORMAL'}
                      </div>
                      <h4 className="text-lg font-semibold">{optimization.category}</h4>
                      <span className="text-sm text-gray-500">({(optimization.confidence * 100).toFixed(0)}% confianza)</span>
                    </div>
                    {optimization.potential_savings > 0 && (
                      <div className="text-right">
                        <p className="text-sm text-gray-600">Ahorro Potencial</p>
                        <p className="text-xl font-bold text-green-600">€{(optimization?.potential_savings || 0).toLocaleString()}</p>
                      </div>
                    )}
                  </div>
                  
                  <div className="mb-3">
                    <p className="text-sm text-gray-600 mb-2">Gasto actual: <span className="font-medium">€{(optimization?.current_amount || 0).toLocaleString()}</span></p>
                  </div>
                  
                  <div className="space-y-2">
                    <p className="font-medium text-gray-800">Recomendaciones:</p>
                    <ul className="space-y-1">
                      {(optimization?.suggestions || []).map((suggestion, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                          <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                          {suggestion}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {activeTab === 'report' && annualReport && (
        <div className="glass-card p-6 rounded-xl">
          <h2 className="text-2xl font-bold mb-6">Informe Anual {annualReport.year}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex justify-between py-2 border-b">
                <span className="font-medium">Ingresos por Alquiler:</span>
                <span className="text-green-600 font-semibold">€{annualReport?.total_rental_income?.toLocaleString() || '0'}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="font-medium">Gastos Totales:</span>
                <span className="text-red-600 font-semibold">€{annualReport?.total_expenses?.toLocaleString() || '0'}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="font-medium">Depreciación:</span>
                <span className="text-blue-600 font-semibold">€{annualReport?.depreciation?.toLocaleString() || '0'}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="font-medium">Resultado Neto:</span>
                <span className="text-indigo-600 font-semibold">€{annualReport?.net_result?.toLocaleString() || '0'}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="font-medium">Tipo Impositivo:</span>
                <span className="font-semibold">{annualReport?.tax_rate?.toFixed(1) || '0'}%</span>
              </div>
              <div className="flex justify-between py-3 border-b-2 border-gray-300">
                <span className="font-bold text-lg">Importe a Pagar:</span>
                <span className="font-bold text-lg text-red-600">€{annualReport?.tax_amount?.toLocaleString() || '0'}</span>
              </div>
            </div>
            <div>
              <h3 className="font-semibold mb-3">Pagos Trimestrales</h3>
              <div className="space-y-2">
                {(annualReport?.quarterly_payments || []).map((payment, index) => (
                  <div key={index} className="flex justify-between py-2 px-3 bg-gray-50 rounded">
                    <span>Q{index + 1} {annualReport?.year || new Date().getFullYear()}:</span>
                    <span className="font-semibold">€{payment?.toLocaleString() || '0'}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'planning' && fiscalDashboard && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <Lightbulb className="w-6 h-6 text-orange-600" />
              Planificación Fiscal Estratégica
            </h2>
            
            {/* Próximos vencimientos destacados */}
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
              <h3 className="text-lg font-semibold text-red-800 mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Próximos Vencimientos Importantes
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {(fiscalDashboard?.upcoming_deadlines || []).slice(0, 4).map((deadline, index) => (
                  <div key={index} className={`p-4 rounded border ${
                    deadline.days_remaining <= 30 ? 'bg-red-100 border-red-300' :
                    deadline.days_remaining <= 60 ? 'bg-yellow-100 border-yellow-300' :
                    'bg-green-100 border-green-300'
                  }`}>
                    <p className="font-medium text-gray-800">{deadline.description}</p>
                    <p className="text-sm text-gray-600">{deadline.date}</p>
                    <p className={`text-sm font-bold ${
                      deadline.days_remaining <= 30 ? 'text-red-700' :
                      deadline.days_remaining <= 60 ? 'text-yellow-700' :
                      'text-green-700'
                    }`}>
                      {deadline.days_remaining > 0 ? `${deadline.days_remaining} días restantes` : 'Vencido'}
                    </p>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-indigo-600 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Estrategias de Optimización
                </h3>
                <div className="space-y-3">
                  <div className="p-4 bg-indigo-50 rounded-lg">
                    <h4 className="font-medium text-indigo-800">Maximizar Deducciones</h4>
                    <p className="text-sm text-indigo-600 mt-1">Planifica gastos deducibles antes del cierre fiscal</p>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <h4 className="font-medium text-purple-800">Amortización Estratégica</h4>
                    <p className="text-sm text-purple-600 mt-1">Optimiza la amortización del 3% anual</p>
                  </div>
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-medium text-blue-800">Estructura Societaria</h4>
                    <p className="text-sm text-blue-600 mt-1">Evalúa constituir sociedad para altos ingresos</p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg">
                    <h4 className="font-medium text-green-800">Eficiencia Energética</h4>
                    <p className="text-sm text-green-600 mt-1">Deducciones adicionales por mejoras sostenibles</p>
                  </div>
                </div>
              </div>
              
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-green-600 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5" />
                  Lista de Verificación Fiscal
                </h3>
                <div className="space-y-2">
                  {[
                    'Digitalizar todas las facturas y recibos',
                    'Revisar contratos de arrendamiento',
                    'Documentar gastos de gestión y administración',
                    'Actualizar seguros de responsabilidad civil',
                    'Planificar mejoras y reparaciones',
                    'Revisar deducciones por suministros',
                    'Preparar documentación para asesor fiscal',
                    'Calcular pagos fraccionados trimestrales'
                  ].map((item, index) => (
                    <label key={index} className="flex items-center gap-3 p-2 hover:bg-gray-50 rounded cursor-pointer">
                      <input type="checkbox" className="w-4 h-4 text-green-600 rounded" />
                      <span className="text-sm text-gray-700">{item}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
          
          {/* Calendario fiscal visual */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-blue-600" />
              Calendario Fiscal {selectedYear}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {[
                { period: 'Q1', months: 'Ene-Mar', task: 'Preparación IRPF', color: 'blue' },
                { period: 'Q2', months: 'Abr-Jun', task: 'Modelo 115 - Q1', color: 'green' },
                { period: 'Q3', months: 'Jul-Sep', task: 'Modelo 115 - Q2', color: 'purple' },
                { period: 'Q4', months: 'Oct-Dec', task: 'Planificación fiscal', color: 'orange' }
              ].map((item, index) => (
                <div key={index} className={`p-4 rounded-lg border-2 ${
                  item.color === 'blue' ? 'bg-blue-50 border-blue-200' :
                  item.color === 'green' ? 'bg-green-50 border-green-200' :
                  item.color === 'purple' ? 'bg-purple-50 border-purple-200' :
                  'bg-orange-50 border-orange-200'
                }`}>
                  <h4 className={`font-semibold ${
                    item.color === 'blue' ? 'text-blue-600' :
                    item.color === 'green' ? 'text-green-600' :
                    item.color === 'purple' ? 'text-purple-600' :
                    'text-orange-600'
                  }`}>
                    {item.period} - {item.months}
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">{item.task}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="flex flex-wrap justify-center gap-4">
        <button
          onClick={() => router.push('/financial-agent')}
          className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center gap-2"
        >
          ← Volver al Dashboard
        </button>
        <button
          onClick={fetchTaxData}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
        >
          <TrendingUp size={16} />
          Actualizar Datos
        </button>
        {activeTab === 'modelo115' && modelo115 && (
          <button
            onClick={downloadModelo115PDF}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
          >
            <Download size={16} />
            Descargar Modelo 115
          </button>
        )}
        <button
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <FileText size={16} />
          Exportar Informe Completo
        </button>
      </div>
      </div>
    </Layout>
  );
}