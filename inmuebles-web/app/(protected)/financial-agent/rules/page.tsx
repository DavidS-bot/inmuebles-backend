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

export default function ClassificationRulesPage() {
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
    console.log(`[DEBUG] Property changed to: ${newRule.property_id}`);
    if (newRule.property_id > 0) {
      console.log(`[DEBUG] Loading contracts for property ${newRule.property_id}`);
      loadPropertyContracts(newRule.property_id);
    } else {
      console.log('[DEBUG] No property selected, clearing contracts');
      setPropertyContracts([]);
    }
  }, [newRule.property_id]);

  const loadPropertyContracts = async (propertyId: number) => {
    try {
      console.log(`[DEBUG] Cargando contratos para propiedad ${propertyId}...`);
      
      // Use the correct endpoint that works: /rental-contracts/?property_id=X
      try {
        const endpoint = `/rental-contracts/?property_id=${propertyId}`;
        console.log(`[DEBUG] Usando endpoint: ${endpoint}`);
        const response = await api.get(endpoint);
        console.log(`[DEBUG] Contratos encontrados:`, response.data.length);
        
        if (response.data && Array.isArray(response.data)) {
          const validContracts = response.data.filter((contract: any) => 
            contract.tenant_name && contract.tenant_name.trim()
          );
          setPropertyContracts(validContracts);
          console.log(`[DEBUG] Contratos validos para propiedad ${propertyId}:`, validContracts.length);
          return;
        }
      } catch (error) {
        console.log(`[DEBUG] Endpoint principal fallo:`, error);
      }
      
      // Fallback: filter from all contracts if main endpoint fails
      console.log("[DEBUG] Usando fallback - filtrando de todos los contratos");
      const filteredContracts = contracts.filter((contract: any) => 
        contract.property_id === propertyId && contract.tenant_name?.trim()
      );
      setPropertyContracts(filteredContracts);
      console.log(`[DEBUG] Contratos filtrados:`, filteredContracts.length);
      
    } catch (error) {
      console.error("Error loading property contracts:", error);
      setPropertyContracts([]);
    }
  };

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load properties (handle gracefully if endpoint fails)
      let propertiesData: Property[] = [];
      try {
        const propertiesRes = await api.get("/properties");
        propertiesData = propertiesRes.data;
        setProperties(propertiesData);
        console.log("✓ [DEBUG] Propiedades cargadas:", propertiesData.length);
      } catch (propertiesError) {
        console.warn("⚠️ [DEBUG] Properties endpoint failed, continuing without properties:", propertiesError);
        setProperties([]);
      }

      // Load rules - FIXED: use trailing slash
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

      // Load contracts for tenant names - FIXED: use trailing slash
      try {
        const contractsRes = await api.get("/rental-contracts/");
        setContracts(contractsRes.data);
        console.log("[DEBUG] Todos los contratos cargados:", contractsRes.data.length);
      } catch (error) {
        console.warn("[DEBUG] Error cargando contratos:", error);
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
        property_id: Number(newRule.property_id),
        subcategory: newRule.subcategory || undefined,
        tenant_name: newRule.tenant_name || undefined
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

  const handleToggleRule = async (ruleId: number, isActive: boolean) => {
    try {
      await api.put(`/classification-rules/${ruleId}`, { is_active: !isActive });
      await loadData();
    } catch (error) {
      console.error("Error updating rule:", error);
      alert("Error al actualizar la regla");
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
      alert("Error al eliminar la regla");
    }
  };

  const handleTestRules = async () => {
    if (!selectedProperty || !testConcepts.trim()) {
      alert("Selecciona una propiedad e ingresa conceptos para probar");
      return;
    }

    try {
      const concepts = testConcepts.split('\n').filter(c => c.trim());
      
      const response = await api.post("/classification-rules/test-classification", {
        property_id: selectedProperty,
        test_concepts: concepts
      });
      
      setTestResults(response.data.test_results || []);
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
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">⚙️ Reglas de Clasificación</h1>
            <p className="text-gray-600 mt-1">Cargando información...</p>
          </div>
        </div>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">⚙️ Reglas de Clasificación</h1>
          <p className="text-gray-600 mt-1">Configurar clasificación automática de movimientos</p>
        </div>
        <div className="flex space-x-3">
          <a
            href="/financial-agent/rules/extract"
            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 flex items-center space-x-2"
          >
            <span>📋</span>
            <span>Crear desde Extracto</span>
          </a>
          <button
            onClick={() => setShowTestModal(true)}
            className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700"
          >
            🧪 Probar Reglas
          </button>
          <button
            onClick={() => setShowNewRuleModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            + Nueva Regla
          </button>
        </div>
      </div>
      <div className="space-y-6">

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
          <p className="text-sm text-gray-600">Total Reglas</p>
          <p className="text-2xl font-bold text-blue-600">{totalRules}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
          <p className="text-sm text-gray-600">Reglas Activas</p>
          <p className="text-2xl font-bold text-green-600">{activeRules}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-gray-500">
          <p className="text-sm text-gray-600">Reglas Inactivas</p>
          <p className="text-2xl font-bold text-gray-600">{inactiveRules}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500">
          <p className="text-sm text-gray-600">Propiedades</p>
          <p className="text-2xl font-bold text-purple-600">{properties.length}</p>
        </div>
      </div>

      {/* Rules by Category */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {Object.entries(rulesByCategory).map(([category, categoryRules]) => (
          <div key={category} className="bg-white rounded-lg shadow">
            <div className={`px-4 py-3 border-b ${getCategoryColor(category)} rounded-t-lg`}>
              <h3 className="font-medium">
                {category === "Renta" ? "🏠 Rentas" : category === "Hipoteca" ? "🏦 Hipotecas" : "💳 Gastos"} 
                <span className="ml-2">({categoryRules.length})</span>
              </h3>
            </div>
            
            <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
              {categoryRules.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4">
                  No hay reglas de {category.toLowerCase()}
                </p>
              ) : (
                categoryRules.map((rule) => (
                  <div
                    key={rule.id}
                    className={`p-3 border rounded-lg ${
                      rule.is_active ? "border-gray-200 bg-white" : "border-gray-300 bg-gray-50"
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <div className="font-medium text-sm">"{rule.keyword}"</div>
                        <div className="text-xs text-gray-600">{rule.property_address}</div>
                        {rule.subcategory && (
                          <div className="text-xs text-gray-500">→ {rule.subcategory}</div>
                        )}
                        {rule.tenant_name && (
                          <div className="text-xs text-blue-600">👤 {rule.tenant_name}</div>
                        )}
                      </div>
                      <div className="flex items-center space-x-1">
                        <button
                          onClick={() => handleToggleRule(rule.id, rule.is_active)}
                          className={`text-xs px-2 py-1 rounded ${
                            rule.is_active
                              ? "bg-green-100 text-green-700 hover:bg-green-200"
                              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                          }`}
                          title={rule.is_active ? "Desactivar regla" : "Activar regla"}
                        >
                          {rule.is_active ? "ON" : "OFF"}
                        </button>
                        <button
                          onClick={() => handleDeleteRule(rule.id)}
                          className="text-xs text-red-600 hover:text-red-800"
                          title="Eliminar regla"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Help Section */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-3">💡 Cómo funcionan las reglas</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
          <div>
            <h4 className="font-medium mb-2">🔍 Palabras Clave</h4>
            <ul className="space-y-1 text-xs">
              <li>• Las reglas buscan palabras clave en los conceptos de movimientos</li>
              <li>• No distinguen mayúsculas/minúsculas</li>
              <li>• Ejemplos: "SANTANDER", "RENTA", "IBI", "COMUNIDAD"</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium mb-2">⚡ Procesamiento</h4>
            <ul className="space-y-1 text-xs">
              <li>• Las reglas se aplican en orden de creación</li>
              <li>• Solo reglas activas se utilizan para clasificar</li>
              <li>• Un movimiento se clasifica con la primera regla que coincide</li>
            </ul>
          </div>
        </div>
      </div>

      {/* New Rule Modal */}
      {showNewRuleModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Nueva Regla de Clasificación</h3>
            
            <form onSubmit={handleCreateRule} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Propiedad</label>
                <select
                  value={newRule.property_id}
                  onChange={(e) => setNewRule({...newRule, property_id: Number(e.target.value), tenant_name: ""})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                >
                  <option value={0}>Seleccionar propiedad</option>
                  {properties.map((property) => (
                    <option key={property.id} value={property.id}>
                      {property.address}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Palabra Clave</label>
                  <input
                    type="text"
                    value={newRule.keyword}
                    onChange={(e) => setNewRule({...newRule, keyword: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    placeholder="Ej: SANTANDER, IBI"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">Texto a buscar en conceptos</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Categoría</label>
                  <select
                    value={newRule.category}
                    onChange={(e) => setNewRule({...newRule, category: e.target.value, tenant_name: ""})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  >
                    <option value="Renta">Renta</option>
                    <option value="Hipoteca">Hipoteca</option>
                    <option value="Gasto">Gasto</option>
                  </select>
                </div>
              </div>

              {newRule.category === "Gasto" && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Subcategoría</label>
                  <input
                    type="text"
                    value={newRule.subcategory}
                    onChange={(e) => setNewRule({...newRule, subcategory: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    placeholder="Ej: Comunidad, IBI, Seguro"
                  />
                </div>
              )}

              {newRule.category === "Renta" && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Inquilino (opcional)</label>
                  <select
                    value={newRule.tenant_name}
                    onChange={(e) => setNewRule({...newRule, tenant_name: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="">Sin asociar</option>
                    {propertyContracts.map((contract, index) => (
                      <option key={index} value={contract.tenant_name}>
                        {contract.tenant_name}
                      </option>
                    ))}
                  </select>
                  {newRule.property_id > 0 && propertyContracts.length === 0 && (
                    <p className="text-xs text-gray-500 mt-1">
                      No se encontraron inquilinos para esta propiedad
                    </p>
                  )}
                  <p className="text-xs text-gray-400 mt-1">
                    [DEBUG] Contratos disponibles: {propertyContracts.length} | Propiedad: {newRule.property_id}
                  </p>
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

      {/* Test Rules Modal */}
      {showTestModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-medium text-gray-900 mb-4">🧪 Probar Reglas de Clasificación</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Propiedad</label>
                <select
                  value={selectedProperty}
                  onChange={(e) => setSelectedProperty(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                >
                  <option value={0}>Seleccionar propiedad</option>
                  {properties.map((property) => (
                    <option key={property.id} value={property.id}>
                      {property.address}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Conceptos a Probar (uno por línea)
                </label>
                <textarea
                  value={testConcepts}
                  onChange={(e) => setTestConcepts(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 h-32"
                  placeholder={`Ejemplo:
TRANSFERENCIA RENTA ABRIL
SANTANDER HIPOTECA 04-2024
IBI PRIMER PLAZO
COMUNIDAD PROPIETARIOS`}
                />
              </div>

              <button
                onClick={handleTestRules}
                className="w-full bg-purple-600 text-white py-2 rounded-md hover:bg-purple-700"
                disabled={!selectedProperty || !testConcepts.trim()}
              >
                Ejecutar Prueba
              </button>

              {testResults.length > 0 && (
                <div className="border-t pt-4">
                  <h4 className="font-medium text-gray-900 mb-3">Resultados de la Prueba</h4>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {testResults.map((result, index) => (
                      <div
                        key={index}
                        className={`p-3 border rounded-lg ${
                          result.matched ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"
                        }`}
                      >
                        <div className="text-sm">
                          <div className="font-medium">{result.concept}</div>
                          <div className="flex items-center space-x-4 mt-1">
                            <span className={`px-2 py-1 text-xs rounded-full ${
                              result.matched 
                                ? "bg-green-100 text-green-700" 
                                : "bg-red-100 text-red-700"
                            }`}>
                              {result.category}
                            </span>
                            {result.matched && result.keyword && (
                              <span className="text-xs text-gray-600">
                                Palabra: "{result.keyword}"
                              </span>
                            )}
                            {result.tenant_name && (
                              <span className="text-xs text-blue-600">
                                👤 {result.tenant_name}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex justify-end space-x-4 pt-4 border-t">
                <button
                  onClick={() => {
                    setShowTestModal(false);
                    setTestConcepts("");
                    setTestResults([]);
                    setSelectedProperty(0);
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
    </div>
  );
}