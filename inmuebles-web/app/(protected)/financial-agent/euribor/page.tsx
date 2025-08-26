"use client";
import { useState, useEffect } from "react";
import api from "@/lib/api";
import Layout from '@/components/Layout';

interface EuriborRate {
  id: number;
  date: string;
  rate_12m?: number;
  rate_6m?: number;
  rate_3m?: number;
  rate_1m?: number;
  source?: string;
  created_at?: string;
}

export default function EuriborManagementPage() {
  const [rates, setRates] = useState<EuriborRate[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showBulkModal, setShowBulkModal] = useState(false);
  const [editingRate, setEditingRate] = useState<EuriborRate | null>(null);
  
  // Add form state
  const [newRate, setNewRate] = useState({
    date: "",
    rate_12m: "",
    rate_6m: "",
    rate_3m: "",
    rate_1m: "",
    source: ""
  });

  // Bulk import state
  const [bulkText, setBulkText] = useState("");
  const [bulkDateFormat, setBulkDateFormat] = useState("%Y-%m-%d");
  const [bulkSeparator, setBulkSeparator] = useState("\t");

  useEffect(() => {
    loadRates();
  }, []);

  const loadRates = async () => {
    try {
      setLoading(true);
      const response = await api.get("/euribor-rates/");
      setRates(response.data);
    } catch (error) {
      console.error("Error loading Euribor rates:", error);
      alert("Error al cargar las tasas Euribor");
    } finally {
      setLoading(false);
    }
  };

  const handleAddRate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const rateData = {
        date: newRate.date,
        rate_12m: newRate.rate_12m ? parseFloat(newRate.rate_12m) : null,
        rate_6m: newRate.rate_6m ? parseFloat(newRate.rate_6m) : null,
        rate_3m: newRate.rate_3m ? parseFloat(newRate.rate_3m) : null,
        rate_1m: newRate.rate_1m ? parseFloat(newRate.rate_1m) : null,
        source: newRate.source || null
      };

      await api.post("/euribor-rates/", rateData);
      
      setShowAddModal(false);
      setNewRate({
        date: "",
        rate_12m: "",
        rate_6m: "",
        rate_3m: "",
        rate_1m: "",
        source: ""
      });
      
      await loadRates();
      alert("✅ Tasa Euribor añadida exitosamente");
      
    } catch (error: any) {
      console.error("Error adding rate:", error);
      const errorMessage = error?.response?.data?.detail || "Error al añadir la tasa";
      alert(`❌ Error: ${errorMessage}`);
    }
  };

  const handleBulkImport = async () => {
    if (!bulkText.trim()) {
      alert("Por favor, introduce datos para importar");
      return;
    }

    try {
      // First parse the text
      const parseResponse = await api.post("/euribor-rates/parse-text", bulkText, {
        params: {
          date_format: bulkDateFormat,
          separator: bulkSeparator
        }
      });

      const parsedData = parseResponse.data;
      
      if (parsedData.errors && parsedData.errors.length > 0) {
        const proceed = confirm(
          `Se encontraron ${parsedData.errors.length} errores:\n\n` +
          parsedData.errors.slice(0, 5).join('\n') +
          (parsedData.errors.length > 5 ? `\n... y ${parsedData.errors.length - 5} más` : '') +
          `\n\n¿Continuar con ${parsedData.parsed_data.length} registros válidos?`
        );
        
        if (!proceed) return;
      }

      // Then create the rates
      const bulkResponse = await api.post("/euribor-rates/bulk", {
        rates: parsedData.parsed_data
      }, {
        params: { overwrite: true }
      });

      const result = bulkResponse.data;
      
      let message = "✅ Importación completada\n\n";
      message += `📊 Creados: ${result.created.length}\n`;
      message += `🔄 Actualizados: ${result.updated.length}\n`;
      
      if (result.errors && result.errors.length > 0) {
        message += `❌ Errores: ${result.errors.length}\n`;
        message += "\nPrimeros errores:\n" + result.errors.slice(0, 3).join('\n');
      }

      alert(message);
      setShowBulkModal(false);
      setBulkText("");
      await loadRates();

    } catch (error: any) {
      console.error("Error bulk importing:", error);
      const errorMessage = error?.response?.data?.detail || "Error en la importación masiva";
      alert(`❌ Error: ${errorMessage}`);
    }
  };

  const handleUpdateRate = async (rate: EuriborRate) => {
    try {
      await api.put(`/euribor-rates/${rate.id}`, {
        rate_12m: rate.rate_12m,
        rate_6m: rate.rate_6m,
        rate_3m: rate.rate_3m,
        rate_1m: rate.rate_1m,
        source: rate.source
      });
      
      setEditingRate(null);
      await loadRates();
      alert("✅ Tasa actualizada exitosamente");
      
    } catch (error: any) {
      console.error("Error updating rate:", error);
      const errorMessage = error?.response?.data?.detail || "Error al actualizar la tasa";
      alert(`❌ Error: ${errorMessage}`);
    }
  };

  const handleDeleteRate = async (rateId: number) => {
    if (!confirm("¿Estás seguro de que quieres eliminar esta tasa?")) {
      return;
    }

    try {
      await api.delete(`/euribor-rates/${rateId}`);
      await loadRates();
      alert("✅ Tasa eliminada exitosamente");
    } catch (error) {
      console.error("Error deleting rate:", error);
      alert("❌ Error al eliminar la tasa");
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES');
  };

  const formatRate = (rate?: number) => {
    if (rate === null || rate === undefined) return "-";
    return `${rate.toFixed(3)}%`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <Layout
      title="📈 Gestión de Tasas Euribor"
      subtitle="Administra las tasas históricas del Euribor para cálculos de hipotecas"
      breadcrumbs={[
        { label: 'Agente Financiero', href: '/financial-agent' },
        { label: 'Tasas Euribor', href: '/financial-agent/euribor' }
      ]}
      actions={
        <div className="flex space-x-3">
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            + Nueva Tasa
          </button>
          <button
            onClick={() => setShowBulkModal(true)}
            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
          >
            📋 Importar Datos
          </button>
        </div>
      }
    >
      <div className="space-y-6">

      {/* Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
          <p className="text-sm text-gray-600">Total Registros</p>
          <p className="text-2xl font-bold text-blue-600">{rates.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
          <p className="text-sm text-gray-600">Última Tasa 12M</p>
          <p className="text-2xl font-bold text-green-600">
            {rates.length > 0 ? formatRate(rates[0]?.rate_12m) : "-"}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-orange-500">
          <p className="text-sm text-gray-600">Fecha Más Reciente</p>
          <p className="text-lg font-bold text-orange-600">
            {rates.length > 0 ? formatDate(rates[0]?.date) : "-"}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500">
          <p className="text-sm text-gray-600">Rango de Fechas</p>
          <p className="text-sm font-bold text-purple-600">
            {rates.length > 1 
              ? `${formatDate(rates[rates.length - 1]?.date)} - ${formatDate(rates[0]?.date)}`
              : rates.length === 1 ? formatDate(rates[0]?.date) : "-"
            }
          </p>
        </div>
      </div>

      {/* Rates Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Tasas Euribor</h2>
        </div>
        
        {rates.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <p>No hay tasas registradas</p>
            <p className="mt-2 text-sm">
              <button
                onClick={() => setShowAddModal(true)}
                className="text-blue-600 hover:underline"
              >
                Añadir primera tasa
              </button>
              {" o "}
              <button
                onClick={() => setShowBulkModal(true)}
                className="text-green-600 hover:underline"
              >
                Importar datos
              </button>
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Fecha
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Euribor 12M
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Euribor 6M
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Euribor 3M
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Euribor 1M
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Fuente
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {rates.map((rate) => (
                  <tr key={rate.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {formatDate(rate.date)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {editingRate?.id === rate.id ? (
                        <input
                          type="number"
                          step="0.001"
                          value={editingRate.rate_12m || ""}
                          onChange={(e) => setEditingRate({
                            ...editingRate,
                            rate_12m: e.target.value ? parseFloat(e.target.value) : undefined
                          })}
                          className="w-20 px-2 py-1 text-xs border border-gray-300 rounded"
                        />
                      ) : (
                        formatRate(rate.rate_12m)
                      )}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {editingRate?.id === rate.id ? (
                        <input
                          type="number"
                          step="0.001"
                          value={editingRate.rate_6m || ""}
                          onChange={(e) => setEditingRate({
                            ...editingRate,
                            rate_6m: e.target.value ? parseFloat(e.target.value) : undefined
                          })}
                          className="w-20 px-2 py-1 text-xs border border-gray-300 rounded"
                        />
                      ) : (
                        formatRate(rate.rate_6m)
                      )}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {editingRate?.id === rate.id ? (
                        <input
                          type="number"
                          step="0.001"
                          value={editingRate.rate_3m || ""}
                          onChange={(e) => setEditingRate({
                            ...editingRate,
                            rate_3m: e.target.value ? parseFloat(e.target.value) : undefined
                          })}
                          className="w-20 px-2 py-1 text-xs border border-gray-300 rounded"
                        />
                      ) : (
                        formatRate(rate.rate_3m)
                      )}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {editingRate?.id === rate.id ? (
                        <input
                          type="number"
                          step="0.001"
                          value={editingRate.rate_1m || ""}
                          onChange={(e) => setEditingRate({
                            ...editingRate,
                            rate_1m: e.target.value ? parseFloat(e.target.value) : undefined
                          })}
                          className="w-20 px-2 py-1 text-xs border border-gray-300 rounded"
                        />
                      ) : (
                        formatRate(rate.rate_1m)
                      )}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {editingRate?.id === rate.id ? (
                        <input
                          type="text"
                          value={editingRate.source || ""}
                          onChange={(e) => setEditingRate({
                            ...editingRate,
                            source: e.target.value
                          })}
                          className="w-24 px-2 py-1 text-xs border border-gray-300 rounded"
                        />
                      ) : (
                        rate.source || "-"
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <div className="flex justify-center space-x-2">
                        {editingRate?.id === rate.id ? (
                          <>
                            <button
                              onClick={() => handleUpdateRate(editingRate)}
                              className="text-green-600 hover:text-green-800 text-sm"
                              title="Guardar"
                            >
                              ✅
                            </button>
                            <button
                              onClick={() => setEditingRate(null)}
                              className="text-gray-600 hover:text-gray-800 text-sm"
                              title="Cancelar"
                            >
                              ❌
                            </button>
                          </>
                        ) : (
                          <>
                            <button
                              onClick={() => setEditingRate(rate)}
                              className="text-blue-600 hover:text-blue-800 text-sm"
                              title="Editar"
                            >
                              ✏️
                            </button>
                            <button
                              onClick={() => handleDeleteRate(rate.id)}
                              className="text-red-600 hover:text-red-800 text-sm"
                              title="Eliminar"
                            >
                              🗑️
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Rate Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Nueva Tasa Euribor</h3>
            
            <form onSubmit={handleAddRate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Fecha *
                </label>
                <input
                  type="date"
                  value={newRate.date}
                  onChange={(e) => setNewRate({...newRate, date: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Euribor 12M (%)
                  </label>
                  <input
                    type="number"
                    step="0.001"
                    value={newRate.rate_12m}
                    onChange={(e) => setNewRate({...newRate, rate_12m: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    placeholder="3.755"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Euribor 6M (%)
                  </label>
                  <input
                    type="number"
                    step="0.001"
                    value={newRate.rate_6m}
                    onChange={(e) => setNewRate({...newRate, rate_6m: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    placeholder="3.685"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Euribor 3M (%)
                  </label>
                  <input
                    type="number"
                    step="0.001"
                    value={newRate.rate_3m}
                    onChange={(e) => setNewRate({...newRate, rate_3m: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    placeholder="3.610"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Euribor 1M (%)
                  </label>
                  <input
                    type="number"
                    step="0.001"
                    value={newRate.rate_1m}
                    onChange={(e) => setNewRate({...newRate, rate_1m: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    placeholder="3.540"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Fuente
                </label>
                <input
                  type="text"
                  value={newRate.source}
                  onChange={(e) => setNewRate({...newRate, source: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Banco de España"
                />
              </div>

              <div className="flex justify-end space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowAddModal(false);
                    setNewRate({
                      date: "",
                      rate_12m: "",
                      rate_6m: "",
                      rate_3m: "",
                      rate_1m: "",
                      source: ""
                    });
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Añadir Tasa
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Bulk Import Modal */}
      {showBulkModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Importar Datos Masivamente</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Formato de Fecha
                </label>
                <select
                  value={bulkDateFormat}
                  onChange={(e) => setBulkDateFormat(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="%Y-%m-%d">YYYY-MM-DD (2024-01-15)</option>
                  <option value="%d/%m/%Y">DD/MM/YYYY (15/01/2024)</option>
                  <option value="%m/%d/%Y">MM/DD/YYYY (01/15/2024)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Separador
                </label>
                <select
                  value={bulkSeparator}
                  onChange={(e) => setBulkSeparator(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="\t">Tabulación (desde Excel)</option>
                  <option value=",">Coma (CSV)</option>
                  <option value=";">Punto y coma</option>
                  <option value=" ">Espacio</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Datos (Fecha, Euribor 12M, 6M, 3M, 1M)
                </label>
                <textarea
                  value={bulkText}
                  onChange={(e) => setBulkText(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  rows={10}
                  placeholder="2024-01-01	3.755	3.685	3.610	3.540
2024-02-01	3.823	3.742	3.671	3.595
2024-03-01	3.891	3.812	3.734	3.661"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Pega los datos directamente desde Excel. Formato: Fecha [TAB] Euribor12M [TAB] Euribor6M [TAB] Euribor3M [TAB] Euribor1M
                </p>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                <p className="text-sm text-blue-800">
                  💡 Puedes copiar directamente desde Excel o Google Sheets. Los valores duplicados serán sobrescritos.
                </p>
              </div>

              <div className="flex justify-end space-x-4 pt-4">
                <button
                  onClick={() => {
                    setShowBulkModal(false);
                    setBulkText("");
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleBulkImport}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  disabled={!bulkText.trim()}
                >
                  Importar Datos
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      </div>
    </Layout>
  );
}