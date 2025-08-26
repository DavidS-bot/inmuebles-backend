'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';

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

export default function TaxAssistantPage() {
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [taxSummary, setTaxSummary] = useState<TaxSummary | null>(null);
  const [deductions, setDeductions] = useState<TaxDeduction[]>([]);
  const [annualReport, setAnnualReport] = useState<TaxReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'summary' | 'deductions' | 'report' | 'planning'>('summary');
  const router = useRouter();

  useEffect(() => {
    fetchTaxData();
  }, [selectedYear]);

  const fetchTaxData = async () => {
    setLoading(true);
    try {
      const [summaryRes, deductionsRes, reportRes] = await Promise.all([
        fetch(`http://localhost:8000/tax-assistant/summary/${selectedYear}`),
        fetch(`http://localhost:8000/tax-assistant/deductions/${selectedYear}`),
        fetch(`http://localhost:8000/tax-assistant/annual-report/${selectedYear}`)
      ]);

      const summaryData = await summaryRes.json();
      const deductionsData = await deductionsRes.json();
      const reportData = await reportRes.json();

      setTaxSummary(summaryData);
      setDeductions(deductionsData.deductions || []);
      setAnnualReport(reportData);
    } catch (error) {
      console.error('Error fetching tax data:', error);
    } finally {
      setLoading(false);
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

      <div className="flex justify-center space-x-2 mb-8">
        {[
          { key: 'summary', label: 'Resumen', icon: '📊' },
          { key: 'deductions', label: 'Deducciones', icon: '💰' },
          { key: 'report', label: 'Informe Anual', icon: '📄' },
          { key: 'planning', label: 'Planificación', icon: '🎯' }
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`px-6 py-3 rounded-lg transition-all flex items-center space-x-2 ${
              activeTab === tab.key
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {activeTab === 'summary' && taxSummary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="glass-card p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-2 text-green-600">Ingresos por Alquiler</h3>
            <div className="text-3xl font-bold">€{taxSummary?.rental_income?.toLocaleString() || '0'}</div>
          </div>
          <div className="glass-card p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-2 text-blue-600">Gastos Deducibles</h3>
            <div className="text-3xl font-bold">€{taxSummary?.deductible_expenses?.toLocaleString() || '0'}</div>
          </div>
          <div className="glass-card p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-2 text-indigo-600">Beneficio Neto</h3>
            <div className="text-3xl font-bold">€{taxSummary?.net_income?.toLocaleString() || '0'}</div>
          </div>
          <div className="glass-card p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-2 text-red-600">Obligación Fiscal</h3>
            <div className="text-3xl font-bold">€{taxSummary?.tax_liability?.toLocaleString() || '0'}</div>
          </div>
          <div className="glass-card p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-2 text-purple-600">Tipo Efectivo</h3>
            <div className="text-3xl font-bold">{taxSummary.effective_rate.toFixed(1)}%</div>
          </div>
          <div className="glass-card p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-2 text-orange-600">Ahorro Potencial</h3>
            <div className="text-3xl font-bold">€{taxSummary?.savings_opportunities?.toLocaleString() || '0'}</div>
          </div>
        </div>
      )}

      {activeTab === 'deductions' && (
        <div className="glass-card p-6 rounded-xl">
          <h2 className="text-2xl font-bold mb-6">Deducciones Aplicables</h2>
          <div className="space-y-4">
            {deductions.map((deduction, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-800">{deduction.concept}</h3>
                    <p className="text-gray-600 text-sm mt-1">{deduction.description}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-xl font-bold text-indigo-600">€{deduction?.amount?.toLocaleString() || '0'}</div>
                    <div className="text-sm text-gray-500">{deduction?.percentage?.toFixed(1) || '0'}% del total</div>
                  </div>
                </div>
              </div>
            ))}
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

      {activeTab === 'planning' && (
        <div className="space-y-6">
          <div className="glass-card p-6 rounded-xl">
            <h2 className="text-2xl font-bold mb-6">Planificación Fiscal</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-indigo-600">📈 Estrategias de Optimización</h3>
                <ul className="space-y-2 text-gray-700">
                  <li>• Maximizar deducciones por mantenimiento</li>
                  <li>• Planificar renovaciones antes del cierre fiscal</li>
                  <li>• Considerar amortización acelerada</li>
                  <li>• Evaluar constitución de sociedad</li>
                  <li>• Aprovechar deducciones por eficiencia energética</li>
                </ul>
              </div>
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-green-600">💡 Recomendaciones Personalizadas</h3>
                <ul className="space-y-2 text-gray-700">
                  <li>• Documentar todos los gastos de gestión</li>
                  <li>• Mantener facturas digitalizadas</li>
                  <li>• Revisar contratos de suministros</li>
                  <li>• Evaluar seguros específicos para alquiler</li>
                  <li>• Considerar inversiones en mejoras</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="glass-card p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-4">🗓️ Calendario Fiscal</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {[
                { month: 'Enero-Marzo', task: 'Presentación IRPF año anterior' },
                { month: 'Abril-Junio', task: 'Pago 1er trimestre' },
                { month: 'Julio-Septiembre', task: 'Pago 2do trimestre' },
                { month: 'Octubre-Diciembre', task: 'Planificación año siguiente' }
              ].map((item, index) => (
                <div key={index} className="bg-gradient-to-br from-indigo-50 to-blue-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-indigo-600">{item.month}</h4>
                  <p className="text-sm text-gray-600 mt-1">{item.task}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-center space-x-4">
        <button
          onClick={() => router.push('/financial-agent')}
          className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
        >
          ← Volver al Dashboard
        </button>
        <button
          onClick={fetchTaxData}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          🔄 Actualizar Datos
        </button>
        <button
          className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          📄 Exportar Informe
        </button>
      </div>
      </div>
    </Layout>
  );
}