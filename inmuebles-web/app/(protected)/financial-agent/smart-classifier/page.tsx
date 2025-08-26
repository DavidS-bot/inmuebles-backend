"use client";
import { useState, useEffect } from "react";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import api from "@/lib/api";
import Layout from '@/components/Layout';

interface Movement {
  id: number;
  date: string;
  concept: string;
  amount: number;
  category: string;
  subcategory?: string;
  is_classified: boolean;
}

interface Category {
  id: string;
  name: string;
  color: string;
  icon: string;
  movements: Movement[];
}

export default function SmartClassifierPage() {
  const [unclassifiedMovements, setUnclassifiedMovements] = useState<Movement[]>([]);
  const [categories, setCategories] = useState<Category[]>([
    {
      id: "rent",
      name: "Rentas",
      color: "bg-green-100 border-green-300",
      icon: "💰",
      movements: []
    },
    {
      id: "mortgage",
      name: "Hipoteca",
      color: "bg-blue-100 border-blue-300",
      icon: "🏦",
      movements: []
    },
    {
      id: "maintenance",
      name: "Mantenimiento",
      color: "bg-orange-100 border-orange-300",
      icon: "🔧",
      movements: []
    },
    {
      id: "utilities",
      name: "Suministros",
      color: "bg-yellow-100 border-yellow-300",
      icon: "⚡",
      movements: []
    },
    {
      id: "taxes",
      name: "Impuestos",
      color: "bg-red-100 border-red-300",
      icon: "📋",
      movements: []
    },
    {
      id: "insurance",
      name: "Seguros",
      color: "bg-purple-100 border-purple-300",
      icon: "🛡️",
      movements: []
    }
  ]);
  const [loading, setLoading] = useState(true);
  const [selectedProperty, setSelectedProperty] = useState<number | null>(null);
  const [properties, setProperties] = useState<any[]>([]);
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    fetchProperties();
    checkDarkMode();
  }, []);

  useEffect(() => {
    if (selectedProperty) {
      fetchUnclassifiedMovements();
    }
  }, [selectedProperty]);

  const checkDarkMode = () => {
    const darkMode = localStorage.getItem('darkMode') === 'true' || 
                     window.matchMedia('(prefers-color-scheme: dark)').matches;
    setIsDarkMode(darkMode);
    document.documentElement.classList.toggle('dark', darkMode);
  };

  const toggleDarkMode = () => {
    const newDarkMode = !isDarkMode;
    setIsDarkMode(newDarkMode);
    localStorage.setItem('darkMode', newDarkMode.toString());
    document.documentElement.classList.toggle('dark', newDarkMode);
  };

  const fetchProperties = async () => {
    try {
      const response = await api.get("/properties");
      setProperties(response.data);
      if (response.data.length > 0) {
        setSelectedProperty(response.data[0].id);
      }
    } catch (error) {
      console.error("Error fetching properties:", error);
    }
  };

  const fetchUnclassifiedMovements = async () => {
    if (!selectedProperty) return;
    
    setLoading(true);
    try {
      const response = await api.get(`/financial-movements/?property_id=${selectedProperty}&is_classified=false`);
      setUnclassifiedMovements(response.data.slice(0, 20)); // Limitar a 20 para mejor UX
    } catch (error) {
      console.error("Error fetching movements:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDragEnd = async (result: any) => {
    const { destination, source, draggableId } = result;

    if (!destination) {
      return;
    }

    if (destination.droppableId === source.droppableId && destination.index === source.index) {
      return;
    }

    const movementId = parseInt(draggableId);
    const movement = unclassifiedMovements.find(m => m.id === movementId);
    
    if (!movement) return;

    // Determinar la nueva categoría
    let newCategory = "";
    let newSubcategory = "";

    switch (destination.droppableId) {
      case "rent":
        newCategory = "Renta";
        break;
      case "mortgage":
        newCategory = "Hipoteca";
        break;
      case "maintenance":
        newCategory = "Gasto";
        newSubcategory = "Mantenimiento";
        break;
      case "utilities":
        newCategory = "Gasto";
        newSubcategory = "Suministros";
        break;
      case "taxes":
        newCategory = "Gasto";
        newSubcategory = "Impuestos";
        break;
      case "insurance":
        newCategory = "Gasto";
        newSubcategory = "Seguros";
        break;
    }

    try {
      // Actualizar en el backend
      await api.put(`/financial-movements/${movementId}`, {
        ...movement,
        category: newCategory,
        subcategory: newSubcategory,
        is_classified: true
      });

      // Actualizar estado local
      setUnclassifiedMovements(prev => prev.filter(m => m.id !== movementId));
      
      const categoryIndex = categories.findIndex(c => c.id === destination.droppableId);
      if (categoryIndex !== -1) {
        const updatedCategories = [...categories];
        updatedCategories[categoryIndex].movements.push({
          ...movement,
          category: newCategory,
          subcategory: newSubcategory,
          is_classified: true
        });
        setCategories(updatedCategories);
      }

      // Mostrar feedback visual
      showSuccess(`Movimiento clasificado como ${newCategory}${newSubcategory ? ` - ${newSubcategory}` : ''}`);
      
    } catch (error) {
      console.error("Error updating movement:", error);
      showError("Error al clasificar el movimiento");
    }
  };

  const autoClassifyMovements = async () => {
    if (!selectedProperty) return;

    setLoading(true);
    try {
      const response = await api.post(`/classification-rules/auto-classify`, {
        property_id: selectedProperty
      });
      
      await fetchUnclassifiedMovements();
      showSuccess(`${response.data.classified_count} movimientos clasificados automáticamente`);
    } catch (error) {
      console.error("Error auto-classifying:", error);
      showError("Error en la clasificación automática");
    } finally {
      setLoading(false);
    }
  };

  const showSuccess = (message: string) => {
    // Crear notificación de éxito
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 transform transition-all duration-300';
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.transform = 'translateX(100%)';
      setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
  };

  const showError = (message: string) => {
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 transform transition-all duration-300';
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.transform = 'translateX(100%)';
      setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  return (
    <Layout
      title="🎯 Clasificador Inteligente"
      subtitle="Arrastra y suelta los movimientos para clasificarlos automáticamente"
      breadcrumbs={[
        { label: 'Agente Financiero', href: '/financial-agent' },
        { label: 'Clasificador Inteligente', href: '/financial-agent/smart-classifier' }
      ]}
      actions={
        <div className="flex items-center space-x-4">
          <button
            onClick={toggleDarkMode}
            className="p-2 rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          >
            {isDarkMode ? '☀️' : '🌙'}
          </button>
          
          <select
            value={selectedProperty || ""}
            onChange={(e) => setSelectedProperty(Number(e.target.value))}
            className="glass-card border-0 rounded-xl px-4 py-2 font-medium focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
          >
            <option value="">Seleccionar propiedad...</option>
            {properties.map((property) => (
              <option key={property.id} value={property.id}>
                {property.address}
              </option>
            ))}
          </select>
          
          <button
            onClick={autoClassifyMovements}
            disabled={loading || !selectedProperty}
            className="btn-primary text-white px-6 py-2 rounded-xl font-medium disabled:opacity-50"
          >
            🤖 Auto-clasificar
          </button>
        </div>
      }
    >
      <div className={`transition-colors duration-300 ${isDarkMode ? 'dark bg-gray-900' : 'bg-gray-50'}`}>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="glass-card rounded-xl p-6">
            <div className="flex items-center">
              <div className="p-3 bg-yellow-100 rounded-xl mr-4">
                <span className="text-2xl">📝</span>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-300">Sin Clasificar</p>
                <p className="text-2xl font-bold text-yellow-600">{unclassifiedMovements.length}</p>
              </div>
            </div>
          </div>
          
          <div className="glass-card rounded-xl p-6">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-xl mr-4">
                <span className="text-2xl">✅</span>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-300">Clasificados</p>
                <p className="text-2xl font-bold text-green-600">
                  {categories.reduce((sum, cat) => sum + cat.movements.length, 0)}
                </p>
              </div>
            </div>
          </div>
          
          <div className="glass-card rounded-xl p-6">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-xl mr-4">
                <span className="text-2xl">🎯</span>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-300">Precisión IA</p>
                <p className="text-2xl font-bold text-blue-600">94%</p>
              </div>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <DragDropContext onDragEnd={handleDragEnd}>
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Movimientos sin clasificar */}
              <div className="lg:col-span-2">
                <div className="glass-card rounded-xl p-6">
                  <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
                    📋 Movimientos por Clasificar
                  </h2>
                  
                  <Droppable droppableId="unclassified">
                    {(provided, snapshot) => (
                      <div
                        {...provided.droppableProps}
                        ref={provided.innerRef}
                        className={`min-h-[400px] p-4 rounded-lg border-2 border-dashed transition-colors ${
                          snapshot.isDraggingOver
                            ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20'
                            : 'border-gray-300 dark:border-gray-600'
                        }`}
                      >
                        {unclassifiedMovements.length === 0 ? (
                          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                            <span className="text-4xl mb-4 block">🎉</span>
                            <p>¡Todos los movimientos están clasificados!</p>
                          </div>
                        ) : (
                          unclassifiedMovements.map((movement, index) => (
                            <Draggable
                              key={movement.id}
                              draggableId={movement.id.toString()}
                              index={index}
                            >
                              {(provided, snapshot) => (
                                <div
                                  ref={provided.innerRef}
                                  {...provided.draggableProps}
                                  {...provided.dragHandleProps}
                                  className={`mb-3 p-4 rounded-lg border transition-all duration-200 cursor-move ${
                                    snapshot.isDragging
                                      ? 'shadow-lg bg-white dark:bg-gray-800 transform rotate-2 scale-105'
                                      : 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:bg-white dark:hover:bg-gray-700 hover:shadow-md'
                                  }`}
                                >
                                  <div className="flex justify-between items-start">
                                    <div className="flex-1">
                                      <p className="font-medium text-gray-900 dark:text-white">
                                        {movement.concept}
                                      </p>
                                      <p className="text-sm text-gray-500 dark:text-gray-400">
                                        {new Date(movement.date).toLocaleDateString()}
                                      </p>
                                    </div>
                                    <div className="text-right">
                                      <p className={`font-bold ${
                                        movement.amount >= 0 
                                          ? 'text-green-600' 
                                          : 'text-red-600'
                                      }`}>
                                        {formatCurrency(movement.amount)}
                                      </p>
                                      <span className="text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 px-2 py-1 rounded-full">
                                        Arrastrar para clasificar
                                      </span>
                                    </div>
                                  </div>
                                </div>
                              )}
                            </Draggable>
                          ))
                        )}
                        {provided.placeholder}
                      </div>
                    )}
                  </Droppable>
                </div>
              </div>

              {/* Categorías */}
              <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4">
                {categories.map((category) => (
                  <div key={category.id} className="glass-card rounded-xl p-4">
                    <h3 className="font-bold mb-3 text-gray-900 dark:text-white flex items-center">
                      <span className="mr-2 text-xl">{category.icon}</span>
                      {category.name}
                      <span className="ml-auto text-sm bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-2 py-1 rounded-full">
                        {category.movements.length}
                      </span>
                    </h3>
                    
                    <Droppable droppableId={category.id}>
                      {(provided, snapshot) => (
                        <div
                          {...provided.droppableProps}
                          ref={provided.innerRef}
                          className={`min-h-[120px] p-3 rounded-lg border-2 border-dashed transition-all duration-200 ${
                            snapshot.isDraggingOver
                              ? `${category.color} scale-105 shadow-lg`
                              : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-800'
                          }`}
                        >
                          {category.movements.slice(-3).map((movement, index) => (
                            <div
                              key={movement.id}
                              className="mb-2 p-2 bg-white dark:bg-gray-700 rounded border text-xs"
                            >
                              <p className="font-medium text-gray-900 dark:text-white truncate">
                                {movement.concept}
                              </p>
                              <p className={`font-bold ${
                                movement.amount >= 0 ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {formatCurrency(movement.amount)}
                              </p>
                            </div>
                          ))}
                          
                          {category.movements.length === 0 && (
                            <div className="text-center text-gray-400 dark:text-gray-500 py-8">
                              <p className="text-sm">Arrastra movimientos aquí</p>
                            </div>
                          )}
                          
                          {provided.placeholder}
                        </div>
                      )}
                    </Droppable>
                  </div>
                ))}
              </div>
            </div>
          </DragDropContext>
        )}

        {/* Tips */}
        <div className="mt-8 glass-card rounded-xl p-6">
          <h3 className="font-bold text-gray-900 dark:text-white mb-4">💡 Consejos de Clasificación</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600 dark:text-gray-300">
            <div>
              <p><strong>🎯 Precisión:</strong> Clasifica correctamente para mejorar la IA</p>
              <p><strong>🏃 Rapidez:</strong> Usa arrastrar y soltar para clasificar rápidamente</p>
            </div>
            <div>
              <p><strong>🤖 Automatización:</strong> La IA aprende de tus clasificaciones</p>
              <p><strong>📊 Informes:</strong> Datos precisos mejoran los análisis fiscales</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}