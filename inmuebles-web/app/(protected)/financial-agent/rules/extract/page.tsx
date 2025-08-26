"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import Layout from '@/components/Layout';

interface ConceptInfo {
  concept: string;
  frequency: number;
  avg_amount: number;
  min_amount: number;
  max_amount: number;
  is_income: boolean;
  sample_dates: string[];
}

interface Property {
  id: number;
  address: string;
}

interface RuleSuggestion {
  keyword: string;
  category: string;
  subcategory?: string;
  tenant_name?: string;
  confidence: number;
  source: string;
  suggested_keywords: string[];
}

export default function ExtractConceptsPage() {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedProperty, setSelectedProperty] = useState<number>(0);
  const [properties, setProperties] = useState<Property[]>([]);
  const [extracting, setExtracting] = useState(false);
  const [concepts, setConcepts] = useState<ConceptInfo[]>([]);
  const [suggestions, setSuggestions] = useState<RuleSuggestion[]>([]);
  const [selectedConcepts, setSelectedConcepts] = useState<Set<string>>(new Set());
  const [rules, setRules] = useState<Record<string, {category: string, subcategory: string, tenant_name: string}>>({});
  const [creating, setCreating] = useState(false);

  // Load properties on component mount
  useEffect(() => {
    loadProperties();
  }, []);

  const loadProperties = async () => {
    try {
      const response = await api.get("/properties");
      setProperties(response.data);
    } catch (error) {
      console.error("Error loading properties:", error);
    }
  };

  const handleExtractConcepts = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile || !selectedProperty) return;

    setExtracting(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await api.post('/financial-movements/extract-concepts', formData);

      setConcepts(response.data.concepts);
      
      // Load suggestions for the selected property
      const suggestionsResponse = await api.get(`/classification-rules/property/${selectedProperty}/suggestions`);
      setSuggestions(suggestionsResponse.data.suggestions);

      alert(`✅ Conceptos extraídos exitosamente!\n\n📊 Total conceptos únicos: ${response.data.unique_concepts}\n📄 Total filas procesadas: ${response.data.total_rows}`);
      
    } catch (error: any) {
      console.error('Error extracting concepts:', error);
      const errorMessage = error?.response?.data?.detail || 'Error al procesar el archivo Excel';
      alert(`❌ Error: ${errorMessage}`);
    } finally {
      setExtracting(false);
    }
  };

  const handleConceptSelect = (concept: string, selected: boolean) => {
    const newSelected = new Set(selectedConcepts);
    if (selected) {
      newSelected.add(concept);
      // Initialize rule data if not exists
      if (!rules[concept]) {
        setRules(prev => ({
          ...prev,
          [concept]: {
            category: "Gasto",
            subcategory: "",
            tenant_name: ""
          }
        }));
      }
    } else {
      newSelected.delete(concept);
      // Remove rule data
      setRules(prev => {
        const newRules = {...prev};
        delete newRules[concept];
        return newRules;
      });
    }
    setSelectedConcepts(newSelected);
  };

  const handleRuleChange = (concept: string, field: string, value: string) => {
    setRules(prev => ({
      ...prev,
      [concept]: {
        ...prev[concept],
        [field]: value
      }
    }));
  };

  const applySuggestion = (suggestion: RuleSuggestion) => {
    const concept = suggestion.keyword;
    setSelectedConcepts(prev => new Set(prev).add(concept));
    setRules(prev => ({
      ...prev,
      [concept]: {
        category: suggestion.category,
        subcategory: suggestion.subcategory || "",
        tenant_name: suggestion.tenant_name || ""
      }
    }));
  };

  const handleCreateRules = async () => {
    if (!selectedProperty || selectedConcepts.size === 0) return;

    setCreating(true);
    try {
      const rulesToCreate = Array.from(selectedConcepts).map(concept => ({
        keyword: concept,
        category: rules[concept].category,
        subcategory: rules[concept].subcategory || null,
        tenant_name: rules[concept].tenant_name || null
      }));

      await api.post('/classification-rules/bulk', {
        property_id: selectedProperty,
        rules: rulesToCreate
      });

      alert(`✅ Reglas creadas exitosamente!\n\n📊 Total reglas creadas: ${rulesToCreate.length}`);
      
      // Redirect to rules page
      router.push(`/financial-agent/property/${selectedProperty}/rules`);
      
    } catch (error: any) {
      console.error('Error creating rules:', error);
      const errorMessage = error?.response?.data?.detail || 'Error al crear las reglas';
      alert(`❌ Error: ${errorMessage}`);
    } finally {
      setCreating(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  return (
    <Layout
      title="📋 Crear Reglas desde Extracto"
      subtitle="Extrae conceptos del extracto bancario para crear reglas de clasificación"
      breadcrumbs={[
        { label: 'Agente Financiero', href: '/financial-agent' },
        { label: 'Reglas', href: '/financial-agent/rules' },
        { label: 'Extraer Conceptos', href: '/financial-agent/rules/extract' }
      ]}
    >
      <div className="space-y-6">

      {/* Upload Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">1. Subir Extracto Bancario</h2>
        
        <form onSubmit={handleExtractConcepts} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Propiedad *
            </label>
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
              Archivo Excel (.xls, .xlsx) *
            </label>
            <input
              type="file"
              accept=".xls,.xlsx"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              El archivo debe contener columnas: <strong>Fecha</strong>, <strong>Concepto</strong>, <strong>Importe</strong>
            </p>
          </div>

          <button
            type="submit"
            disabled={extracting || !selectedFile || !selectedProperty}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {extracting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                <span>Extrayendo conceptos...</span>
              </>
            ) : (
              <>
                <span>🔍</span>
                <span>Extraer Conceptos</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">2. Sugerencias Basadas en Contratos</h2>
          <p className="text-sm text-gray-600 mb-4">
            Reglas sugeridas automáticamente basadas en tus contratos de alquiler y patrones comunes:
          </p>
          
          <div className="space-y-3">
            {suggestions.map((suggestion, index) => (
              <div key={index} className="border border-gray-200 rounded-md p-3 flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">{suggestion.keyword}</span>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      suggestion.category === 'Renta' ? 'bg-green-100 text-green-800' :
                      suggestion.category === 'Hipoteca' ? 'bg-red-100 text-red-800' :
                      'bg-orange-100 text-orange-800'
                    }`}>
                      {suggestion.category}
                    </span>
                    <span className="text-xs text-gray-500">
                      Confianza: {suggestion.confidence}%
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{suggestion.source}</p>
                  {suggestion.subcategory && (
                    <p className="text-xs text-gray-600">Subcategoría: {suggestion.subcategory}</p>
                  )}
                </div>
                <button
                  onClick={() => applySuggestion(suggestion)}
                  className="px-3 py-1 text-xs bg-blue-100 text-blue-800 rounded hover:bg-blue-200"
                >
                  Aplicar
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Extracted Concepts */}
      {concepts.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-medium text-gray-900">3. Conceptos Extraídos ({concepts.length})</h2>
            <div className="text-sm text-gray-600">
              Seleccionados: {selectedConcepts.size}
            </div>
          </div>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {concepts.map((conceptInfo, index) => (
              <div key={index} className="border border-gray-200 rounded-md p-3">
                <div className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    checked={selectedConcepts.has(conceptInfo.concept)}
                    onChange={(e) => handleConceptSelect(conceptInfo.concept, e.target.checked)}
                    className="mt-1"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium text-gray-900 truncate">
                        {conceptInfo.concept}
                      </h4>
                      <div className="flex items-center space-x-2 text-xs text-gray-500">
                        <span>Frecuencia: {conceptInfo.frequency}</span>
                        <span className={conceptInfo.is_income ? 'text-green-600' : 'text-red-600'}>
                          {formatCurrency(conceptInfo.avg_amount)}
                        </span>
                      </div>
                    </div>
                    
                    {selectedConcepts.has(conceptInfo.concept) && (
                      <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Categoría *
                          </label>
                          <select
                            value={rules[conceptInfo.concept]?.category || "Gasto"}
                            onChange={(e) => handleRuleChange(conceptInfo.concept, "category", e.target.value)}
                            className="w-full text-xs border border-gray-300 rounded px-2 py-1"
                          >
                            <option value="Renta">Renta</option>
                            <option value="Hipoteca">Hipoteca</option>
                            <option value="Gasto">Gasto</option>
                          </select>
                        </div>
                        
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Subcategoría
                          </label>
                          <input
                            type="text"
                            value={rules[conceptInfo.concept]?.subcategory || ""}
                            onChange={(e) => handleRuleChange(conceptInfo.concept, "subcategory", e.target.value)}
                            className="w-full text-xs border border-gray-300 rounded px-2 py-1"
                            placeholder="Ej: IBI, Comunidad"
                          />
                        </div>
                        
                        {rules[conceptInfo.concept]?.category === "Renta" && (
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              Nombre Inquilino
                            </label>
                            <input
                              type="text"
                              value={rules[conceptInfo.concept]?.tenant_name || ""}
                              onChange={(e) => handleRuleChange(conceptInfo.concept, "tenant_name", e.target.value)}
                              className="w-full text-xs border border-gray-300 rounded px-2 py-1"
                              placeholder="Nombre del inquilino"
                            />
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Create Rules */}
      {selectedConcepts.size > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">4. Crear Reglas</h2>
          <p className="text-sm text-gray-600 mb-4">
            Se crearán {selectedConcepts.size} reglas de clasificación para la propiedad seleccionada.
          </p>
          
          <div className="flex space-x-4">
            <button
              onClick={handleCreateRules}
              disabled={creating || selectedConcepts.size === 0}
              className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {creating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  <span>Creando reglas...</span>
                </>
              ) : (
                <>
                  <span>✅</span>
                  <span>Crear {selectedConcepts.size} Reglas</span>
                </>
              )}
            </button>
            
            <button
              onClick={() => router.back()}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}
      </div>
    </Layout>
  );
}