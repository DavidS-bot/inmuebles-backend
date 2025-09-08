"use client";
import { useState, useEffect } from "react";
import api from "@/lib/api";

interface Property {
  id: number;
  address: string;
}

interface ClassificationRule {
  id: number;
  property_id: number;
  keyword: string;
  category: string;
  subcategory?: string;
  tenant_name?: string;
  is_active: boolean;
}

interface RuleWithProperty extends ClassificationRule {
  property_address: string;
}

interface RentalContract {
  id: number;
  tenant_name: string;
}

export default function RulesTab() {
  const [rules, setRules] = useState<RuleWithProperty[]>([]);
  const [properties, setProperties] = useState<Property[]>([]);
  const [contracts, setContracts] = useState<RentalContract[]>([]);
  const [propertyContracts, setPropertyContracts] = useState<RentalContract[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNewRuleModal, setShowNewRuleModal] = useState(false);
  const [showTestModal, setShowTestModal] = useState(false);
  const [selectedProperty, setSelectedProperty] = useState<number>(0);
  
  // New rule form
  const [newRule, setNewRule] = useState({
    property_id: 0,
    keyword: "",
    category: "Gasto",
    subcategory: "",
    tenant_name: ""
  });

  // Test functionality
  const [testConcepts, setTestConcepts] = useState("");
  const [testResults, setTestResults] = useState<any[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  // Load tenants when property is selected in new rule form
  useEffect(() => {
    if (newRule.property_id > 0) {
      loadPropertyContracts(newRule.property_id);
    } else {
      setPropertyContracts([]);
    }
  }, [newRule.property_id]);

  const loadPropertyContracts = async (propertyId: number) => {
    try {
      const endpoint = `/rental-contracts/?property_id=${propertyId}`;
      const response = await api.get(endpoint);
      
      if (response.data && Array.isArray(response.data)) {
        const validContracts = response.data.filter((contract: any) => 
          contract.tenant_name && contract.tenant_name.trim()
        );
        setPropertyContracts(validContracts);
      }
    } catch (error) {
      console.error("Error loading property contracts:", error);
      setPropertyContracts([]);
    }
  };

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load properties
      let propertiesData: Property[] = [];
      try {
        const propertiesRes = await api.get("/properties");
        propertiesData = propertiesRes.data;
        setProperties(propertiesData);
      } catch (propertiesError) {
        console.warn("Properties endpoint failed:", propertiesError);
        setProperties([]);
      }

      // Load rules
      const rulesRes = await api.get("/classification-rules/");
      
      // Enrich rules with property info
      const enrichedRules = rulesRes.data.map((rule: ClassificationRule) => {
        const property = propertiesData.find((p: Property) => p.id === rule.property_id);
        return {
          ...rule,
          property_address: property?.address || "Propiedad desconocida"
        };
      });

      setRules(enrichedRules);

      // Load contracts for tenant names
      try {
        const contractsRes = await api.get("/rental-contracts/");
        setContracts(contractsRes.data);
      } catch (error) {
        console.warn("Error loading contracts:", error);
        setContracts([]);
      }
    } catch (error) {
      console.error("Error loading rules:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const ruleData = {
        ...newRule,
        property_id: newRule.property_id > 0 ? Number(newRule.property_id) : null,
        subcategory: newRule.subcategory || null,
        tenant_name: newRule.tenant_name || null
      };

      await api.post("/classification-rules/", ruleData);
      
      setShowNewRuleModal(false);
      setNewRule({
        property_id: 0,
        keyword: "",
        category: "Gasto",
        subcategory: "",
        tenant_name: ""
      });
      
      await loadData();
    } catch (error) {
      console.error("Error creating rule:", error);
      alert("Error al crear la regla");
    }
  };

  const handleToggleRule = async (ruleId: number, currentStatus: boolean) => {
    try {
      await api.put(`/classification-rules/${ruleId}`, {
        is_active: !currentStatus
      });
      await loadData();
    } catch (error) {
      console.error("Error toggling rule:", error);
    }
  };

  const handleDeleteRule = async (ruleId: number) => {
    if (!confirm("¿Estás seguro de que quieres eliminar esta regla?")) {
      return;
    }

    try {
      await api.delete(`/classification-rules/${ruleId}`);
      await loadData();
    } catch (error) {
      console.error("Error deleting rule:", error);
    }
  };

  const handleTestRules = async () => {
    if (!testConcepts.trim()) {
      alert("Por favor, ingresa algunos conceptos para probar");
      return;
    }

    try {
      const conceptsArray = testConcepts.split('\n').filter(c => c.trim());
      const results = await Promise.all(
        conceptsArray.map(async (concept) => {
          try {
            const response = await api.post('/classification-rules/test', {
              concept: concept.trim()
            });
            return {
              concept: concept.trim(),
              ...response.data
            };
          } catch (error) {
            return {
              concept: concept.trim(),
              matched: false,
              error: "Error en clasificación"
            };
          }
        })
      );
      
      setTestResults(results);
    } catch (error) {
      console.error("Error testing rules:", error);
      alert("Error al probar las reglas");
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      "Renta": "text-green-700 bg-green-100",
      "Hipoteca": "text-red-700 bg-red-100", 
      "Gasto": "text-orange-700 bg-orange-100"
    };
    return colors[category] || "text-gray-700 bg-gray-100";
  };

  // Group rules by category
  const rulesByCategory = {
    Renta: rules.filter(r => r.category === "Renta"),
    Hipoteca: rules.filter(r => r.category === "Hipoteca"),
    Gasto: rules.filter(r => r.category === "Gasto")
  };

  const totalRules = rules.length;
  const activeRules = rules.filter(r => r.is_active).length;
  const inactiveRules = totalRules - activeRules;

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-blue-500">
          <p className="text-sm text-gray-600">Total Reglas</p>
          <p className="text-2xl font-bold text-blue-600">{totalRules}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-green-500">
          <p className="text-sm text-gray-600">Reglas Activas</p>
          <p className="text-2xl font-bold text-green-600">{activeRules}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-gray-500">
          <p className="text-sm text-gray-600">Reglas Inactivas</p>
          <p className="text-2xl font-bold text-gray-600">{inactiveRules}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-purple-500">
          <p className="text-sm text-gray-600">Propiedades</p>
          <p className="text-2xl font-bold text-purple-600">{properties.length}</p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">Reglas de Clasificación</h3>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowNewRuleModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            + Nueva Regla
          </button>
          <button
            onClick={() => setShowTestModal(true)}
            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
          >
            🧪 Probar Reglas
          </button>
        </div>
      </div>

      {/* Rules by Category */}
      <div className="space-y-6">
        {Object.entries(rulesByCategory).map(([category, categoryRules]) => (
          <div key={category} className="bg-white rounded-lg shadow">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                {category} ({categoryRules.length} reglas)
              </h3>
            </div>
            
            {categoryRules.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                <p>No hay reglas configuradas para {category}</p>
                <button
                  onClick={() => {
                    setNewRule({...newRule, category});
                    setShowNewRuleModal(true);
                  }}
                  className="mt-2 text-blue-600 hover:underline"
                >
                  Crear primera regla para {category}
                </button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Palabra Clave</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Propiedad</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Subcategoría</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Inquilino</th>
                      <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">Acciones</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {categoryRules.map((rule) => (
                      <tr key={rule.id} className="hover:bg-gray-50">
                        <td className="px-4 py-2">
                          <button
                            onClick={() => handleToggleRule(rule.id, rule.is_active)}
                            className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                              rule.is_active 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}
                          >
                            {rule.is_active ? 'Activa' : 'Inactiva'}
                          </button>
                        </td>
                        <td className="px-4 py-2">
                          <span className="font-medium text-gray-900">{rule.keyword}</span>
                        </td>
                        <td className="px-4 py-2 text-sm text-gray-600">
                          {rule.property_address}
                        </td>
                        <td className="px-4 py-2 text-sm text-gray-600">
                          {rule.subcategory || '-'}
                        </td>
                        <td className="px-4 py-2 text-sm text-gray-600">
                          {rule.tenant_name || '-'}
                        </td>
                        <td className="px-4 py-2 text-center">
                          <button
                            onClick={() => handleDeleteRule(rule.id)}
                            className="text-red-600 hover:text-red-800 text-sm"
                            title="Eliminar regla"
                          >
                            🗑️
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* New Rule Modal */}
      {showNewRuleModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Nueva Regla de Clasificación</h3>
            
            <form onSubmit={handleCreateRule} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Palabra Clave *
                </label>
                <input
                  type="text"
                  value={newRule.keyword}
                  onChange={(e) => setNewRule({...newRule, keyword: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ej: Ikea, bankinter, Trans Inm"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Esta palabra debe aparecer en el concepto del movimiento
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Categoría</label>
                <select
                  value={newRule.category}
                  onChange={(e) => setNewRule({...newRule, category: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                >
                  <option value="Renta">Renta</option>
                  <option value="Hipoteca">Hipoteca</option>
                  <option value="Gasto">Gasto</option>
                </select>
              </div>

              {properties.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Propiedad (Opcional)
                  </label>
                  <select
                    value={newRule.property_id}
                    onChange={(e) => setNewRule({...newRule, property_id: Number(e.target.value)})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value={0}>Cualquier propiedad</option>
                    {properties.map((property) => (
                      <option key={property.id} value={property.id}>
                        {property.address}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Subcategoría (Opcional)
                </label>
                <input
                  type="text"
                  value={newRule.subcategory}
                  onChange={(e) => setNewRule({...newRule, subcategory: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ej: IBI, Comunidad, Reparaciones"
                />
              </div>

              {newRule.category === "Renta" && propertyContracts.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Inquilino (Opcional)
                  </label>
                  <select
                    value={newRule.tenant_name}
                    onChange={(e) => setNewRule({...newRule, tenant_name: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="">Seleccionar inquilino</option>
                    {propertyContracts.map((contract, index) => (
                      <option key={index} value={contract.tenant_name}>
                        {contract.tenant_name}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="flex justify-end space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowNewRuleModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Crear Regla
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Test Modal */}
      {showTestModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">🧪 Probar Reglas de Clasificación</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Conceptos a Probar (uno por línea)
                </label>
                <textarea
                  value={testConcepts}
                  onChange={(e) => setTestConcepts(e.target.value)}
                  rows={6}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Trans Inm/ Antonio Jose Lopez-
Recib /bankinter Seguros De Vi
Ikea Jerez Hfb
Liquid. Cuota Ptmo. 510043004"
                />
              </div>

              <button
                onClick={handleTestRules}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
              >
                Probar Clasificación
              </button>

              {testResults.length > 0 && (
                <div className="mt-6">
                  <h4 className="font-medium mb-3">Resultados:</h4>
                  <div className="space-y-2">
                    {testResults.map((result, index) => (
                      <div key={index} className="border rounded p-3">
                        <div className="flex justify-between items-start">
                          <span className="font-medium">{result.concept}</span>
                          <span className={`px-2 py-1 rounded text-xs ${
                            result.matched 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {result.matched ? 'Clasificado' : 'No clasificado'}
                          </span>
                        </div>
                        {result.matched && (
                          <div className="mt-2 text-sm text-gray-600">
                            <p><strong>Categoría:</strong> {result.category}</p>
                            {result.subcategory && <p><strong>Subcategoría:</strong> {result.subcategory}</p>}
                            {result.tenant_name && <p><strong>Inquilino:</strong> {result.tenant_name}</p>}
                            {result.property_address && <p><strong>Propiedad:</strong> {result.property_address}</p>}
                            <p><strong>Regla:</strong> "{result.keyword}"</p>
                          </div>
                        )}
                        {result.error && (
                          <div className="mt-2 text-sm text-red-600">
                            <p>Error: {result.error}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex justify-end space-x-4 pt-4">
                <button
                  onClick={() => {
                    setShowTestModal(false);
                    setTestResults([]);
                    setTestConcepts("");
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}