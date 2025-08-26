"use client";
import { useState, useEffect } from "react";
import api from "@/lib/api";
import Layout from '@/components/Layout';

interface MortgagePayment {
  property_id: number;
  outstanding_balance: number;
  current_euribor: number;
  margin: number;
  total_rate: number;
  monthly_payment: number;
  remaining_months: number;
  total_interest_remaining: number;
}

interface PrepaymentSimulation {
  prepayment_amount: number;
  strategy: string;
  current_scenario: {
    monthly_payment: number;
    total_interest: number;
    remaining_months: number;
    end_date: string;
  };
  new_scenario: {
    monthly_payment: number;
    total_interest: number;
    remaining_months: number;
    end_date: string;
  };
  savings: {
    interest_savings: number;
    months_saved: number;
    monthly_savings: number;
    total_savings: number;
  };
}

export default function MortgageCalculatorPage() {
  const [properties, setProperties] = useState<any[]>([]);
  const [selectedProperty, setSelectedProperty] = useState<number | null>(null);
  const [currentPayment, setCurrentPayment] = useState<MortgagePayment | null>(null);
  const [prepaymentAmount, setPrepaymentAmount] = useState<number>(10000);
  const [reduceTerms, setReduceTerms] = useState(true);
  const [simulation, setSimulation] = useState<PrepaymentSimulation | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchProperties();
  }, []);

  useEffect(() => {
    if (selectedProperty) {
      fetchCurrentPayment();
    }
  }, [selectedProperty]);

  const fetchProperties = async () => {
    try {
      const response = await api.get("/properties");
      const propertiesWithMortgage = response.data.filter((p: any) => 
        p.purchase_price && p.purchase_price > 0
      );
      setProperties(propertiesWithMortgage);
      if (propertiesWithMortgage.length > 0) {
        setSelectedProperty(propertiesWithMortgage[0].id);
      }
    } catch (error) {
      console.error("Error fetching properties:", error);
    }
  };

  const fetchCurrentPayment = async () => {
    if (!selectedProperty) return;
    
    setLoading(true);
    try {
      const response = await api.get(`/mortgage-calculator/current-payment/${selectedProperty}`);
      setCurrentPayment(response.data);
    } catch (error) {
      console.error("Error fetching current payment:", error);
    } finally {
      setLoading(false);
    }
  };

  const simulatePrepayment = async () => {
    if (!selectedProperty || !prepaymentAmount) return;

    setLoading(true);
    try {
      const response = await api.post("/mortgage-calculator/simulate-prepayment", {
        property_id: selectedProperty,
        prepayment_amount: prepaymentAmount,
        prepayment_date: new Date().toISOString().split('T')[0],
        reduce_term: reduceTerms
      });
      setSimulation(response.data);
    } catch (error) {
      console.error("Error simulating prepayment:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(3)}%`;
  };

  return (
    <Layout
      title="Calculadora de Hipoteca"
      subtitle="Simula amortizaciones anticipadas y optimiza tu estrategia hipotecaria"
      breadcrumbs={[
        { label: 'Agente Financiero', href: '/financial-agent' },
        { label: 'Calculadora Hipoteca', href: '/financial-agent/mortgage-calculator' }
      ]}
    >
      <div className="space-y-6">

      {/* Property Selection */}
      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold mb-3">Seleccionar Propiedad</h2>
        <select
          value={selectedProperty || ""}
          onChange={(e) => setSelectedProperty(Number(e.target.value))}
          className="w-full border rounded px-3 py-2"
        >
          <option value="">Seleccionar propiedad...</option>
          {properties.map((property) => (
            <option key={property.id} value={property.id}>
              {property.address}
            </option>
          ))}
        </select>
      </div>

      {/* Current Payment Info */}
      {currentPayment && (
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-4">Situación Actual</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded">
              <h3 className="font-medium text-blue-900">Cuota Mensual</h3>
              <p className="text-2xl font-bold text-blue-600">
                {formatCurrency(currentPayment.monthly_payment)}
              </p>
            </div>
            <div className="bg-red-50 p-4 rounded">
              <h3 className="font-medium text-red-900">Saldo Pendiente</h3>
              <p className="text-2xl font-bold text-red-600">
                {formatCurrency(currentPayment.outstanding_balance)}
              </p>
            </div>
            <div className="bg-green-50 p-4 rounded">
              <h3 className="font-medium text-green-900">Tipo de Interés</h3>
              <p className="text-2xl font-bold text-green-600">
                {formatPercentage(currentPayment.total_rate)}
              </p>
            </div>
          </div>
          
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p><span className="font-medium">Euribor actual:</span> {formatPercentage(currentPayment.current_euribor)}</p>
              <p><span className="font-medium">Margen banco:</span> {formatPercentage(currentPayment.margin)}</p>
            </div>
            <div>
              <p><span className="font-medium">Meses restantes:</span> {currentPayment.remaining_months}</p>
              <p><span className="font-medium">Intereses restantes:</span> {formatCurrency(currentPayment.total_interest_remaining)}</p>
            </div>
          </div>
        </div>
      )}

      {/* Prepayment Simulation */}
      {currentPayment && (
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-4">Simulador de Amortización Anticipada</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Cantidad a amortizar
              </label>
              <input
                type="number"
                value={prepaymentAmount}
                onChange={(e) => setPrepaymentAmount(Number(e.target.value))}
                className="w-full border rounded px-3 py-2"
                min="0"
                step="1000"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">
                Estrategia
              </label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="radio"
                    checked={reduceTerms}
                    onChange={() => setReduceTerms(true)}
                    className="mr-2"
                  />
                  Reducir plazo (mantener cuota)
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    checked={!reduceTerms}
                    onChange={() => setReduceTerms(false)}
                    className="mr-2"
                  />
                  Reducir cuota (mantener plazo)
                </label>
              </div>
            </div>
          </div>

          <button
            onClick={simulatePrepayment}
            disabled={loading || !prepaymentAmount}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Calculando..." : "Simular Amortización"}
          </button>
        </div>
      )}

      {/* Simulation Results */}
      {simulation && (
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-4">Resultados de la Simulación</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Current vs New Scenario */}
            <div>
              <h3 className="font-medium mb-3">Comparativa de Escenarios</h3>
              <div className="space-y-4">
                <div className="bg-gray-50 p-3 rounded">
                  <h4 className="font-medium text-gray-700">Escenario Actual</h4>
                  <div className="text-sm space-y-1 mt-2">
                    <p>Cuota: {formatCurrency(simulation.current_scenario.monthly_payment)}</p>
                    <p>Meses restantes: {simulation.current_scenario.remaining_months}</p>
                    <p>Intereses totales: {formatCurrency(simulation.current_scenario.total_interest)}</p>
                  </div>
                </div>
                
                <div className="bg-green-50 p-3 rounded">
                  <h4 className="font-medium text-green-700">Nuevo Escenario</h4>
                  <div className="text-sm space-y-1 mt-2">
                    <p>Cuota: {formatCurrency(simulation.new_scenario.monthly_payment)}</p>
                    <p>Meses restantes: {simulation.new_scenario.remaining_months}</p>
                    <p>Intereses totales: {formatCurrency(simulation.new_scenario.total_interest)}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Savings */}
            <div>
              <h3 className="font-medium mb-3">Ahorros Totales</h3>
              <div className="space-y-3">
                <div className="bg-blue-50 p-3 rounded">
                  <h4 className="font-medium text-blue-900">Ahorro en Intereses</h4>
                  <p className="text-xl font-bold text-blue-600">
                    {formatCurrency(simulation.savings.interest_savings)}
                  </p>
                </div>
                
                {simulation.savings.months_saved > 0 && (
                  <div className="bg-purple-50 p-3 rounded">
                    <h4 className="font-medium text-purple-900">Meses Ahorrados</h4>
                    <p className="text-xl font-bold text-purple-600">
                      {simulation.savings.months_saved} meses
                    </p>
                  </div>
                )}
                
                {simulation.savings.monthly_savings > 0 && (
                  <div className="bg-green-50 p-3 rounded">
                    <h4 className="font-medium text-green-900">Ahorro Mensual</h4>
                    <p className="text-xl font-bold text-green-600">
                      {formatCurrency(simulation.savings.monthly_savings)}
                    </p>
                  </div>
                )}
                
                <div className="bg-yellow-50 p-3 rounded">
                  <h4 className="font-medium text-yellow-900">Ahorro Total</h4>
                  <p className="text-xl font-bold text-yellow-600">
                    {formatCurrency(simulation.savings.total_savings)}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Strategy Info */}
          <div className="mt-4 p-3 bg-gray-50 rounded">
            <p className="text-sm text-gray-600">
              <span className="font-medium">Estrategia seleccionada:</span>{" "}
              {simulation.strategy === "reduce_term" ? "Reducir plazo manteniendo cuota" : "Reducir cuota manteniendo plazo"}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              <span className="font-medium">Amortización:</span> {formatCurrency(simulation.prepayment_amount)}
            </p>
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <h3 className="font-medium text-amber-800 mb-2">💡 Consejos</h3>
        <ul className="text-sm text-amber-700 space-y-1">
          <li>• <strong>Reducir plazo:</strong> Ahorra más intereses a largo plazo</li>
          <li>• <strong>Reducir cuota:</strong> Mejora tu cash flow mensual</li>
          <li>• Considera tu situación financiera y objetivos antes de decidir</li>
          <li>• Los tipos de interés actuales pueden cambiar en futuras revisiones</li>
        </ul>
      </div>
      </div>
    </Layout>
  );
}