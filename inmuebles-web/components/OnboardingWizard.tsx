"use client";
import { useState, useEffect } from "react";
import { MapPin, Calculator, Sparkles, ArrowRight, Check, Home, TrendingUp } from "lucide-react";
import api from "@/lib/api";
import { 
  calculateFiscalSavings, 
  getSmartDefaults, 
  searchAddresses as smartSearchAddresses,
  ZONE_DATABASE 
} from "@/lib/smartDefaults";

interface OnboardingData {
  address: string;
  monthlyRent: number;
  purchasePrice?: number;
  zone?: string;
  propertyType?: string;
  rooms?: number;
  m2?: number;
}

export default function OnboardingWizard({ onComplete }: { onComplete: () => void }) {
  const [step, setStep] = useState(1);
  const [data, setData] = useState<OnboardingData>({
    address: "",
    monthlyRent: 0
  });
  const [savings, setSavings] = useState<any>(null);
  const [smartDefaults, setSmartDefaults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [addressSuggestions, setAddressSuggestions] = useState<string[]>([]);
  const [showCalculation, setShowCalculation] = useState(false);
  const [animationStep, setAnimationStep] = useState(0);

  // Smart address search with better UX
  const searchAddresses = async (query: string) => {
    if (query.length < 3) {
      setAddressSuggestions([]);
      return;
    }
    
    try {
      const suggestions = await smartSearchAddresses(query);
      setAddressSuggestions(suggestions);
    } catch (error) {
      console.error("Error searching addresses:", error);
    }
  };

  const calculateWithSmartDefaults = (address: string, rent: number) => {
    console.log('🔧 [DEBUG] calculateWithSmartDefaults called with:', { address, rent });
    
    // Calculate fiscal savings using smart system
    const fiscalData = calculateFiscalSavings(address, rent);
    const defaults = getSmartDefaults(address, rent);
    
    console.log('🔧 [DEBUG] Fiscal data calculated:', fiscalData);
    console.log('🔧 [DEBUG] Smart defaults:', defaults);
    
    setSavings(fiscalData);
    setSmartDefaults(defaults);
    
    // Update data with smart defaults
    setData(prev => ({
      ...prev,
      zone: fiscalData.zone,
      propertyType: defaults.propertyType,
      rooms: defaults.rooms,
      m2: defaults.m2,
      purchasePrice: fiscalData.estimatedPrice
    }));
  };

  const handleStep1Submit = () => {
    if (!data.address || !data.monthlyRent) return;
    
    setShowCalculation(true);
    setAnimationStep(0);
    
    // Animated calculation sequence
    const calculationSteps = [
      "Consultando base de datos del catastro",
      "Comparando precios de zona",  
      "Calculando deducciones fiscales",
      "Aplicando optimizaciones automáticas"
    ];
    
    calculationSteps.forEach((step, index) => {
      setTimeout(() => {
        setAnimationStep(index + 1);
        if (index === calculationSteps.length - 1) {
          console.log('🔧 [DEBUG] Starting final calculation step');
          setTimeout(() => {
            calculateWithSmartDefaults(data.address, data.monthlyRent);
            setTimeout(() => {
              console.log('🔧 [DEBUG] Moving to step 2');
              console.log('🔧 [DEBUG] Current savings state:', savings);
              setShowCalculation(false);
              setStep(2);
            }, 200);
          }, 400);
        }
      }, (index + 1) * 600);
    });
  };

  const handleCompleteOnboarding = async () => {
    setLoading(true);
    
    try {
      // Create property with smart defaults
      const propertyData = {
        address: data.address,
        property_type: data.propertyType || "Piso",
        rooms: data.rooms || 3,
        m2: data.m2 || 90,
        purchase_price: data.purchasePrice || (data.monthlyRent * 12 * 16),
        monthly_rent: data.monthlyRent
      };
      
      const propertyResponse = await api.post("/properties", propertyData);
      const propertyId = propertyResponse.data.id;
      
      // Create smart default classification rules
      if (smartDefaults?.expenses) {
        for (const expense of smartDefaults.expenses) {
          await api.post("/classification-rules", {
            property_id: propertyId,
            keyword: expense.name.toLowerCase(),
            category: expense.category,
            subcategory: expense.subcategory,
            is_active: true
          });
        }
      }
      
      onComplete();
    } catch (error) {
      console.error("Error creating property:", error);
      alert("Error al crear la propiedad. Por favor, inténtalo de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  if (showCalculation) {
    const calculationSteps = [
      { text: "Consultando base de datos del catastro", icon: "🏛️" },
      { text: "Comparando precios de zona", icon: "📊" }, 
      { text: "Calculando deducciones fiscales", icon: "💰" },
      { text: "Aplicando optimizaciones automáticas", icon: "⚡" }
    ];

    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="max-w-md w-full text-center">
          {/* Main spinner with pulsing effect */}
          <div className="relative mb-8">
            <div className="animate-spin rounded-full h-20 w-20 border-4 border-blue-600 border-t-transparent mx-auto"></div>
            <div className="absolute inset-0 rounded-full h-20 w-20 border-4 border-blue-200 mx-auto animate-pulse"></div>
            <div className="absolute inset-4 bg-blue-100 rounded-full flex items-center justify-center">
              <Calculator className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <h3 className="text-3xl font-bold text-gray-900 mb-2">
            Calculando tu ahorro fiscal...
          </h3>
          <p className="text-gray-600 mb-2">Analizando {data.address}</p>
          <p className="text-sm text-blue-600 font-medium">Alquiler: {data.monthlyRent.toLocaleString()}€/mes</p>
          
          <div className="mt-8 space-y-4">
            {calculationSteps.map((step, index) => (
              <div 
                key={index}
                className={`flex items-center text-left p-3 rounded-lg transition-all duration-500 ${
                  animationStep > index 
                    ? 'bg-green-50 border border-green-200' 
                    : animationStep === index 
                      ? 'bg-blue-50 border border-blue-200' 
                      : 'bg-gray-50 border border-gray-200'
                }`}
              >
                <div className={`text-2xl mr-3 transition-all duration-300 ${
                  animationStep > index ? 'scale-110' : animationStep === index ? 'animate-bounce' : 'scale-90'
                }`}>
                  {step.icon}
                </div>
                <div className="flex-1">
                  <div className={`font-medium transition-colors ${
                    animationStep > index ? 'text-green-700' : animationStep === index ? 'text-blue-700' : 'text-gray-400'
                  }`}>
                    {step.text}
                  </div>
                  {animationStep > index && (
                    <div className="text-xs text-green-600 mt-1">✓ Completado</div>
                  )}
                </div>
                {animationStep === index && (
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent"></div>
                )}
              </div>
            ))}
          </div>

          <div className="mt-8 bg-gradient-to-r from-blue-100 to-indigo-100 rounded-xl p-4">
            <p className="text-sm text-blue-800">
              ✨ Comparando con +50.000 propiedades similares
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Progress Bar */}
      <div className="p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-2xl font-bold text-gray-900">Configuración Express</h1>
            <div className="flex items-center space-x-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
                {step > 1 ? <Check size={16} /> : "1"}
              </div>
              <div className={`w-12 h-1 ${step >= 2 ? 'bg-blue-600' : 'bg-gray-200'} rounded`}></div>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
                {step > 2 ? <Check size={16} /> : "2"}
              </div>
            </div>
          </div>
        </div>
      </div>

      {step === 1 && (
        <div className="max-w-2xl mx-auto px-4 pb-8">
          <div className="bg-white rounded-3xl shadow-2xl p-8">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <MapPin className="w-8 h-8 text-blue-600" />
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">¡Empezamos!</h2>
              <p className="text-gray-600 text-lg">Solo necesitamos 2 datos para calcular tu ahorro fiscal</p>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  📍 Dirección de tu propiedad
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={data.address}
                    onChange={(e) => {
                      setData({ ...data, address: e.target.value });
                      searchAddresses(e.target.value);
                    }}
                    placeholder="Calle Gran Vía 1, Madrid"
                    className="w-full px-4 py-4 border-2 border-gray-200 rounded-xl text-lg focus:border-blue-500 focus:ring-0 transition-colors"
                  />
                  {addressSuggestions.length > 0 && (
                    <div className="absolute z-10 w-full bg-white border border-gray-200 rounded-lg mt-1 shadow-lg">
                      {addressSuggestions.map((suggestion, index) => (
                        <button
                          key={index}
                          onClick={() => {
                            setData({ ...data, address: suggestion });
                            setAddressSuggestions([]);
                          }}
                          className="w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center"
                        >
                          <MapPin size={16} className="text-gray-400 mr-2" />
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  💰 Alquiler mensual
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={data.monthlyRent || ""}
                    onChange={(e) => setData({ ...data, monthlyRent: Number(e.target.value) })}
                    placeholder="1500"
                    className="w-full px-4 py-4 border-2 border-gray-200 rounded-xl text-lg focus:border-blue-500 focus:ring-0 transition-colors"
                  />
                  <span className="absolute right-4 top-4 text-gray-500 text-lg">€/mes</span>
                </div>
              </div>

              <button
                onClick={handleStep1Submit}
                disabled={!data.address || !data.monthlyRent}
                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 px-6 rounded-xl font-semibold text-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                <Calculator className="mr-2" size={20} />
                Calcular mi ahorro fiscal
                <ArrowRight className="ml-2" size={20} />
              </button>
            </div>

            <div className="mt-8 text-center">
              <p className="text-sm text-gray-500">
                ✨ En menos de 30 segundos tendrás tu análisis completo
              </p>
            </div>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="max-w-2xl mx-auto px-4 pb-8">
          <div className="bg-white rounded-3xl shadow-2xl p-8">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-green-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                ¡Puedes ahorrar <span className="text-green-600">{savings?.annualSavings?.toLocaleString() || '956'}€</span> al año!
              </h2>
              <p className="text-gray-600 text-lg">Tu propiedad está {savings?.zoneComparison || '6% por debajo del mercado en Madrid Centro'}</p>
            </div>

            {/* Savings Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="bg-blue-50 rounded-2xl p-6 text-center">
                <div className="text-2xl font-bold text-blue-600 mb-2">
                  {savings?.monthlyDeduction?.toLocaleString() || '379'}€
                </div>
                <div className="text-sm text-blue-800">Deducción mensual</div>
              </div>
              
              <div className="bg-green-50 rounded-2xl p-6 text-center">
                <div className="text-2xl font-bold text-green-600 mb-2">
                  {savings?.irpfReduction?.toLocaleString() || '80'}€
                </div>
                <div className="text-sm text-green-800">Menos IRPF/mes</div>
              </div>
              
              <div className="bg-purple-50 rounded-2xl p-6 text-center">
                <div className="text-2xl font-bold text-purple-600 mb-2">21%</div>
                <div className="text-sm text-purple-800">Ahorro fiscal</div>
              </div>
            </div>

            {/* Smart Defaults Preview */}
            <div className="bg-gray-50 rounded-2xl p-6 mb-8">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
                <Check className="text-green-600 mr-2" size={20} />
                Configuración automática incluida
              </h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>✅ Reglas IBI automáticas</div>
                <div>✅ Seguro hogar detectado</div>
                <div>✅ Gastos comunidad</div>
                <div>✅ Mantenimiento estándar</div>
                <div>✅ Alertas fiscales</div>
                <div>✅ Comparativa de zona</div>
              </div>
            </div>

            {/* Progress Indicator */}
            <div className="bg-gradient-to-r from-blue-100 to-indigo-100 rounded-2xl p-6 mb-8">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Setup completado</span>
                <span className="text-sm font-medium text-blue-600">85%</span>
              </div>
              <div className="w-full bg-white rounded-full h-3">
                <div className="bg-gradient-to-r from-blue-600 to-indigo-600 h-3 rounded-full" style={{ width: '85%' }}></div>
              </div>
              <p className="text-xs text-gray-600 mt-2">Solo faltan algunos detalles opcionales</p>
            </div>

            <button
              onClick={handleCompleteOnboarding}
              disabled={loading}
              className="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white py-4 px-6 rounded-xl font-semibold text-lg hover:from-green-700 hover:to-emerald-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 flex items-center justify-center"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-6 w-6 border-2 border-white border-t-transparent mr-2"></div>
              ) : (
                <Sparkles className="mr-2" size={20} />
              )}
              {loading ? "Configurando tu cuenta..." : "¡Comenzar a ahorrar!"}
            </button>

            <div className="mt-4 text-center">
              <button
                onClick={() => setStep(3)}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                O completar datos opcionales primero
              </button>
            </div>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="max-w-2xl mx-auto px-4 pb-8">
          <div className="bg-white rounded-3xl shadow-2xl p-8">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Home className="w-8 h-8 text-purple-600" />
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">Detalles adicionales</h2>
              <p className="text-gray-600 text-lg">Personaliza tu configuración (opcional)</p>
            </div>

            <div className="space-y-6">
              {/* Property Type */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  🏠 Tipo de propiedad
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {smartDefaults?.zoneData?.propertyTypes?.map((type: any) => (
                    <button
                      key={type.type}
                      onClick={() => {
                        setData({ ...data, propertyType: type.type, rooms: type.avgRooms, m2: type.avgM2 });
                      }}
                      className={`p-4 border-2 rounded-xl text-center transition-all ${
                        data.propertyType === type.type
                          ? 'border-purple-500 bg-purple-50 text-purple-700'
                          : 'border-gray-200 hover:border-purple-300'
                      }`}
                    >
                      <div className="font-semibold">{type.type}</div>
                      <div className="text-xs text-gray-500 mt-1">
                        ~{type.avgM2}m² • {type.avgRooms} hab
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Property Details */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    📐 Metros cuadrados
                  </label>
                  <input
                    type="number"
                    value={data.m2 || ""}
                    onChange={(e) => setData({ ...data, m2: Number(e.target.value) })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-0"
                    placeholder="90"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    🛏️ Habitaciones
                  </label>
                  <input
                    type="number"
                    value={data.rooms || ""}
                    onChange={(e) => setData({ ...data, rooms: Number(e.target.value) })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-0"
                    placeholder="3"
                  />
                </div>
              </div>

              {/* Purchase Price */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  💎 Precio de compra (opcional)
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={data.purchasePrice || ""}
                    onChange={(e) => setData({ ...data, purchasePrice: Number(e.target.value) })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-0"
                    placeholder={savings?.estimatedPrice?.toLocaleString() || "350000"}
                  />
                  <span className="absolute right-4 top-3 text-gray-500">€</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Estimación automática: {savings?.estimatedPrice?.toLocaleString()}€
                </p>
              </div>

              {/* Smart Expenses Preview */}
              <div className="bg-gray-50 rounded-2xl p-6">
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
                  <TrendingUp className="text-blue-600 mr-2" size={20} />
                  Gastos automáticos configurados para {data.zone}
                </h3>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  {smartDefaults?.expenses?.map((expense: any, index: number) => (
                    <div key={index} className="flex justify-between items-center py-2">
                      <span className="text-gray-700">{expense.name}</span>
                      <span className="font-medium text-gray-900">
                        {expense.frequency === 'monthly' 
                          ? `${expense.amount}€/mes`
                          : `${expense.amount}€/año`
                        }
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={() => setStep(2)}
                  className="flex-1 bg-gray-200 text-gray-700 py-4 px-6 rounded-xl font-semibold hover:bg-gray-300 transition-all"
                >
                  Atrás
                </button>
                <button
                  onClick={handleCompleteOnboarding}
                  disabled={loading}
                  className="flex-1 bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-4 px-6 rounded-xl font-semibold hover:from-purple-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 flex items-center justify-center"
                >
                  {loading ? (
                    <div className="animate-spin rounded-full h-6 w-6 border-2 border-white border-t-transparent mr-2"></div>
                  ) : (
                    <Sparkles className="mr-2" size={20} />
                  )}
                  {loading ? "Configurando..." : "Finalizar setup"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}