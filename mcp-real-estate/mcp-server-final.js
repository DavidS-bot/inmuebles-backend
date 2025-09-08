// mcp-server-final.js
const JerezPropertyScraper = require('./jerez-scraper');
const SimpleJerezScraper = require('./simple-real-scraper');
const PropertyAlertsSystem = require('./alerts-system');
const InvestmentAdvisor = require('./investment-advisor');

console.log('Iniciando servidor MCP Real Estate...');

// Datos de ejemplo (más adelante conectaremos APIs reales)
const mockProperties = [
  {
    id: 1,
    address: 'Calle Gran Vía, 25, Madrid',
    price: 450000,
    size: 85,
    rooms: 3,
    type: 'apartment',
    neighborhood: 'Centro'
  },
  {
    id: 2,
    address: 'Calle Serrano, 12, Madrid', 
    price: 650000,
    size: 110,
    rooms: 4,
    type: 'apartment',
    neighborhood: 'Salamanca'
  },
  {
    id: 3,
    address: 'Avenida América, 45, Madrid',
    price: 320000,
    size: 75,
    rooms: 2,
    type: 'apartment',
    neighborhood: 'Ciudad Lineal'
  },
  {
    id: 4,
    address: 'Calle Alcalá, 156, Madrid',
    price: 380000,
    size: 68,
    rooms: 2,
    type: 'apartment',
    neighborhood: 'Retiro'
  }
];

const mcpServer = {
  name: 'real-estate-analyzer',
  version: '1.0.0',
  
  tools: [
    {
      name: 'search_properties',
      description: 'Buscar propiedades por zona, precio y características',
      inputSchema: {
        type: 'object',
        properties: {
          neighborhood: { type: 'string', description: 'Barrio a buscar (Centro, Salamanca, etc.)' },
          max_price: { type: 'number', description: 'Precio máximo en euros' },
          min_size: { type: 'number', description: 'Tamaño mínimo en m²' },
          min_rooms: { type: 'number', description: 'Número mínimo de habitaciones' }
        }
      }
    },
    {
      name: 'analyze_property',
      description: 'Analizar rentabilidad y métricas financieras de una propiedad',
      inputSchema: {
        type: 'object',
        properties: {
          price: { type: 'number', description: 'Precio de compra en euros', required: true },
          size: { type: 'number', description: 'Tamaño en m²', required: true },
          estimated_rent: { type: 'number', description: 'Renta mensual estimada (opcional)' },
          expenses: { type: 'number', description: 'Gastos anuales estimados (opcional)' }
        },
        required: ['price', 'size']
      }
    },
    {
      name: 'compare_neighborhoods',
      description: 'Comparar precios por m² entre diferentes barrios',
      inputSchema: {
        type: 'object',
        properties: {
          neighborhoods: { 
            type: 'array', 
            items: { type: 'string' },
            description: 'Lista de barrios a comparar'
          }
        }
      }
    },
    {
      name: 'investment_calculator',
      description: 'Calcular proyección de inversión a largo plazo',
      inputSchema: {
        type: 'object',
        properties: {
          initial_investment: { type: 'number', description: 'Inversión inicial' },
          monthly_rent: { type: 'number', description: 'Renta mensual' },
          years: { type: 'number', description: 'Años de proyección', default: 10 },
          appreciation_rate: { type: 'number', description: 'Tasa de apreciación anual (%)', default: 3 }
        },
        required: ['initial_investment', 'monthly_rent']
      }
    },
    {
      name: 'search_jerez_properties',
      description: 'Buscar pisos reales en Jerez de la Frontera usando web scraping',
      inputSchema: {
        type: 'object',
        properties: {
          rooms: { type: 'number', description: 'Número de habitaciones', default: 2 },
          maxDaysOld: { type: 'number', description: 'Máximo días desde publicación', default: 14 },
          maxPrice: { type: 'number', description: 'Precio máximo en euros (opcional)' },
          minPrice: { type: 'number', description: 'Precio mínimo en euros (opcional)' }
        }
      }
    },
    {
      name: 'create_alert',
      description: 'Crear alerta automática para nuevas propiedades',
      inputSchema: {
        type: 'object',
        properties: {
          name: { type: 'string', description: 'Nombre de la alerta', required: true },
          location: { type: 'string', description: 'Ubicación (jerez, madrid, etc.)', default: 'jerez' },
          maxPrice: { type: 'number', description: 'Precio máximo en euros' },
          minPrice: { type: 'number', description: 'Precio mínimo en euros' },
          rooms: { type: 'number', description: 'Número de habitaciones' },
          maxDaysOld: { type: 'number', description: 'Máximo días desde publicación', default: 7 },
          email: { type: 'string', description: 'Email para notificaciones' },
          webhook: { type: 'string', description: 'URL de webhook' },
          frequency: { type: 'string', description: 'Frecuencia: hourly, daily, weekly', default: 'daily' }
        },
        required: ['name']
      }
    },
    {
      name: 'list_alerts',
      description: 'Listar todas las alertas configuradas',
      inputSchema: {
        type: 'object',
        properties: {}
      }
    },
    {
      name: 'check_alerts',
      description: 'Verificar manualmente todas las alertas activas',
      inputSchema: {
        type: 'object',
        properties: {}
      }
    },
    {
      name: 'start_monitoring',
      description: 'Iniciar monitoreo automático de alertas',
      inputSchema: {
        type: 'object',
        properties: {
          intervalMinutes: { type: 'number', description: 'Intervalo en minutos entre verificaciones', default: 30 }
        }
      }
    },
    {
      name: 'analyze_investment',
      description: 'Análisis completo de inversión inmobiliaria con datos bancarios',
      inputSchema: {
        type: 'object',
        properties: {
          property: {
            type: 'object',
            description: 'Datos de la propiedad',
            properties: {
              price: { type: 'number', description: 'Precio de compra en euros', required: true },
              size: { type: 'number', description: 'Tamaño en m²', required: true },
              location: { type: 'string', description: 'Ubicación (madrid)', default: 'madrid' },
              neighborhood: { type: 'string', description: 'Barrio (centro, salamanca, retiro)', default: 'centro' }
            },
            required: ['price', 'size']
          },
          bankData: {
            type: 'object',
            description: 'Datos financieros del cliente',
            properties: {
              monthlyIncome: { type: 'number', description: 'Ingresos mensuales netos', required: true },
              monthlyExpenses: { type: 'number', description: 'Gastos mensuales', required: true },
              savings: { type: 'number', description: 'Ahorros disponibles', required: true },
              currentDebt: { type: 'number', description: 'Deuda actual (hipoteca, préstamos)', default: 0 }
            },
            required: ['monthlyIncome', 'monthlyExpenses', 'savings']
          }
        },
        required: ['property', 'bankData']
      }
    }
  ],
  
  handleRequest(method, params) {
    if (method === 'tools/list') {
      return { tools: this.tools };
    }
    
    if (method === 'tools/call') {
      const { name, arguments: args } = params;
      
      switch(name) {
        case 'search_properties':
          return this.searchProperties(args);
        case 'analyze_property':
          return this.analyzeProperty(args);
        case 'compare_neighborhoods':
          return this.compareNeighborhoods(args);
        case 'investment_calculator':
          return this.calculateInvestment(args);
        case 'search_jerez_properties':
          return this.searchJerezPropertiesReal(args);
        case 'create_alert':
          return this.createAlert(args);
        case 'list_alerts':
          return this.listAlerts(args);
        case 'check_alerts':
          return this.checkAlerts(args);
        case 'start_monitoring':
          return this.startMonitoring(args);
        case 'analyze_investment':
          return this.analyzeInvestment(args);
        default:
          return { error: `Herramienta desconocida: ${name}` };
      }
    }
    
    return { error: 'Método no soportado' };
  },
  
  searchProperties(filters) {
    let results = [...mockProperties];
    
    if (filters.neighborhood) {
      results = results.filter(p => 
        p.neighborhood.toLowerCase().includes(filters.neighborhood.toLowerCase())
      );
    }
    
    if (filters.max_price) {
      results = results.filter(p => p.price <= filters.max_price);
    }
    
    if (filters.min_size) {
      results = results.filter(p => p.size >= filters.min_size);
    }
    
    if (filters.min_rooms) {
      results = results.filter(p => p.rooms >= filters.min_rooms);
    }
    
    const summary = results.map(p => {
      const pricePerSqm = Math.round(p.price / p.size);
      return `📍 ${p.address}
   💰 ${p.price.toLocaleString()}€ | 📐 ${p.size}m² | 🏠 ${p.rooms} hab.
   💶 ${pricePerSqm}€/m² | 🏘️ ${p.neighborhood}`;
    }).join('\n\n');
    
    return {
      content: [{
        type: 'text',
        text: `🔍 BÚSQUEDA DE PROPIEDADES\n\nEncontradas ${results.length} propiedades:\n\n${summary}`
      }]
    };
  },
  
  analyzeProperty(data) {
    const pricePerSqm = Math.round(data.price / data.size);
    const estimatedRent = data.estimated_rent || Math.round(data.price * 0.004);
    const annualRent = estimatedRent * 12;
    const expenses = data.expenses || Math.round(annualRent * 0.3); // 30% gastos por defecto
    const netAnnualIncome = annualRent - expenses;
    
    const grossYield = Math.round((annualRent / data.price) * 10000) / 100;
    const netYield = Math.round((netAnnualIncome / data.price) * 10000) / 100;
    
    // Análisis de calidad de inversión
    let rating = '❌ Baja rentabilidad';
    if (netYield >= 6) rating = '✅ Excelente inversión';
    else if (netYield >= 4) rating = '⚠️ Inversión aceptable';
    else if (netYield >= 2) rating = '⚡ Inversión marginal';
    
    return {
      content: [{
        type: 'text',
        text: `📊 ANÁLISIS FINANCIERO COMPLETO

💰 DATOS BÁSICOS:
• Precio: ${data.price.toLocaleString()}€
• Tamaño: ${data.size}m²
• Precio/m²: ${pricePerSqm}€

🏠 INGRESOS:
• Renta mensual: ${estimatedRent.toLocaleString()}€
• Renta anual: ${annualRent.toLocaleString()}€

💸 GASTOS ANUALES:
• Gastos estimados: ${expenses.toLocaleString()}€
• Ingresos netos: ${netAnnualIncome.toLocaleString()}€

📈 RENTABILIDAD:
• Rentabilidad bruta: ${grossYield}%
• Rentabilidad neta: ${netYield}%

🎯 EVALUACIÓN: ${rating}`
      }]
    };
  },
  
  compareNeighborhoods(data) {
    const neighborhoods = data.neighborhoods || ['Centro', 'Salamanca', 'Retiro'];
    const comparison = neighborhoods.map(neighborhood => {
      const properties = mockProperties.filter(p => 
        p.neighborhood.toLowerCase().includes(neighborhood.toLowerCase())
      );
      
      if (properties.length === 0) {
        return `🏘️ ${neighborhood}: Sin datos disponibles`;
      }
      
      const avgPrice = Math.round(
        properties.reduce((sum, p) => sum + p.price, 0) / properties.length
      );
      const avgPricePerSqm = Math.round(
        properties.reduce((sum, p) => sum + (p.price / p.size), 0) / properties.length
      );
      
      return `🏘️ ${neighborhood}:
   💰 Precio medio: ${avgPrice.toLocaleString()}€
   💶 Precio/m² medio: ${avgPricePerSqm}€
   📊 Propiedades: ${properties.length}`;
    }).join('\n\n');
    
    return {
      content: [{
        type: 'text',
        text: `🏘️ COMPARACIÓN DE BARRIOS\n\n${comparison}`
      }]
    };
  },
  
  calculateInvestment(data) {
    const years = data.years || 10;
    const appreciationRate = (data.appreciation_rate || 3) / 100;
    
    const annualRent = data.monthly_rent * 12;
    const totalRentalIncome = annualRent * years;
    
    // Valor futuro con apreciación
    const futureValue = data.initial_investment * Math.pow(1 + appreciationRate, years);
    const capitalGain = futureValue - data.initial_investment;
    
    const totalReturn = totalRentalIncome + capitalGain;
    const annualizedReturn = Math.round(
      (Math.pow(totalReturn / data.initial_investment, 1/years) - 1) * 10000
    ) / 100;
    
    return {
      content: [{
        type: 'text',
        text: `📊 PROYECCIÓN DE INVERSIÓN (${years} años)

💰 INVERSIÓN INICIAL: ${data.initial_investment.toLocaleString()}€

🏠 INGRESOS POR RENTAS:
• Renta anual: ${annualRent.toLocaleString()}€
• Total rentas ${years} años: ${totalRentalIncome.toLocaleString()}€

📈 APRECIACIÓN DEL INMUEBLE:
• Valor inicial: ${data.initial_investment.toLocaleString()}€
• Valor estimado final: ${Math.round(futureValue).toLocaleString()}€
• Ganancia de capital: ${Math.round(capitalGain).toLocaleString()}€

🎯 RESUMEN TOTAL:
• Retorno total: ${Math.round(totalReturn).toLocaleString()}€
• Rentabilidad anualizada: ${annualizedReturn}%
• ROI total: ${Math.round((totalReturn / data.initial_investment - 1) * 100)}%`
      }]
    };
  },

  async searchJerezProperties(filters) {
    console.log('🔍 Iniciando búsqueda en Jerez...');
    const scraper = new JerezPropertyScraper();
    
    try {
      const result = await scraper.searchJerezProperties(filters);
      return result;
    } catch (error) {
      console.error('❌ Error en búsqueda Jerez:', error.message);
      return {
        content: [{
          type: 'text',
          text: `❌ Error al buscar propiedades en Jerez: ${error.message}`
        }]
      };
    }
  },

  async searchJerezPropertiesReal(filters) {
    console.log('🌐 Iniciando búsqueda REAL en Jerez...');
    const scraper = new SimpleJerezScraper();
    
    try {
      const result = await scraper.searchProperties(filters);
      return result;
    } catch (error) {
      console.error('❌ Error en búsqueda real Jerez:', error.message);
      return {
        content: [{
          type: 'text',
          text: `❌ Error al buscar propiedades reales en Jerez: ${error.message}\n\n🔄 Prueba con búsqueda manual en idealista.com`
        }]
      };
    }
  },

  async createAlert(config) {
    console.log('🚨 Creando nueva alerta...');
    
    if (!this.alertsSystem) {
      this.alertsSystem = new PropertyAlertsSystem();
    }
    
    try {
      const alert = await this.alertsSystem.createAlert(config);
      
      return {
        content: [{
          type: 'text',
          text: `✅ ALERTA CREADA EXITOSAMENTE

📋 DETALLES DE LA ALERTA:
• Nombre: ${alert.name}
• ID: ${alert.id}
• Ubicación: ${alert.criteria.location}
• Precio máximo: ${alert.criteria.maxPrice ? alert.criteria.maxPrice.toLocaleString() + '€' : 'Sin límite'}
• Habitaciones: ${alert.criteria.rooms || 'Cualquiera'}
• Frecuencia: ${alert.schedule.frequency}
• Email: ${alert.notifications.email || 'No configurado'}
• Estado: ${alert.active ? 'Activa' : 'Inactiva'}

🔔 NOTIFICACIONES:
${alert.notifications.console ? '✅ Consola' : '❌ Consola'}
${alert.notifications.email ? '✅ Email' : '❌ Email'}  
${alert.notifications.webhook ? '✅ Webhook' : '❌ Webhook'}

⚡ La alerta se ejecutará automáticamente según la frecuencia configurada.
💡 Usa 'start_monitoring' para iniciar el sistema de monitoreo automático.`
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: `❌ Error al crear alerta: ${error.message}`
        }]
      };
    }
  },

  async listAlerts() {
    console.log('📋 Listando alertas...');
    
    if (!this.alertsSystem) {
      this.alertsSystem = new PropertyAlertsSystem();
    }
    
    try {
      const alerts = await this.alertsSystem.getAlerts();
      const stats = await this.alertsSystem.getStats();
      
      if (alerts.length === 0) {
        return {
          content: [{
            type: 'text',
            text: `📭 NO HAY ALERTAS CONFIGURADAS

🔧 Para crear tu primera alerta usa el comando 'create_alert' con parámetros como:
• name: "Pisos baratos Jerez"
• location: "jerez"
• maxPrice: 80000
• rooms: 2
• email: "tu@email.com"`
          }]
        };
      }
      
      const alertsList = alerts.map((alert, index) => {
        const status = alert.active ? '✅ Activa' : '❌ Inactiva';
        const lastCheck = alert.schedule.lastCheck ? 
          new Date(alert.schedule.lastCheck).toLocaleString() : 'Nunca';
        
        return `${index + 1}. 📋 ${alert.name}
   🆔 ID: ${alert.id}
   🏠 Ubicación: ${alert.criteria.location}
   💰 Precio máximo: ${alert.criteria.maxPrice ? alert.criteria.maxPrice.toLocaleString() + '€' : 'Sin límite'}
   🛏️ Habitaciones: ${alert.criteria.rooms || 'Cualquiera'}
   📅 Frecuencia: ${alert.schedule.frequency}
   ⏰ Última verificación: ${lastCheck}
   📧 Email: ${alert.notifications.email || 'No configurado'}
   ${status}`;
      }).join('\n\n');
      
      return {
        content: [{
          type: 'text',
          text: `📋 ALERTAS CONFIGURADAS (${alerts.length})

${alertsList}

📊 ESTADÍSTICAS:
• Total alertas: ${stats.totalAlerts}
• Alertas activas: ${stats.activeAlerts}
• Notificaciones enviadas: ${stats.totalNotifications}
• Monitoreo activo: ${stats.isMonitoring ? '✅ Sí' : '❌ No'}

💡 Usa 'check_alerts' para verificar todas las alertas manualmente.
🚀 Usa 'start_monitoring' para iniciar el monitoreo automático.`
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: `❌ Error al listar alertas: ${error.message}`
        }]
      };
    }
  },

  async checkAlerts() {
    console.log('🔍 Verificando alertas...');
    
    if (!this.alertsSystem) {
      this.alertsSystem = new PropertyAlertsSystem();
    }
    
    try {
      const alerts = await this.alertsSystem.getAlerts();
      const activeAlerts = alerts.filter(a => a.active);
      
      if (activeAlerts.length === 0) {
        return {
          content: [{
            type: 'text',
            text: `⚠️ NO HAY ALERTAS ACTIVAS PARA VERIFICAR

📋 Tienes ${alerts.length} alertas configuradas pero ninguna está activa.
💡 Crea una nueva alerta con 'create_alert' o activa las existentes.`
          }]
        };
      }
      
      let results = [];
      let totalNewProperties = 0;
      
      for (const alert of activeAlerts) {
        const newProperties = await this.alertsSystem.checkAlert(alert);
        totalNewProperties += newProperties.length;
        
        results.push({
          alertName: alert.name,
          propertiesFound: newProperties.length,
          properties: newProperties.slice(0, 3) // Solo mostrar las primeras 3
        });
      }
      
      const summary = results.map(r => {
        if (r.propertiesFound === 0) {
          return `📋 ${r.alertName}: Sin nuevas propiedades`;
        } else {
          const propertiesList = r.properties.map(p => 
            `   • ${p.title} - ${p.price}`
          ).join('\n');
          
          return `🚨 ${r.alertName}: ${r.propertiesFound} nueva(s) propiedad(es)
${propertiesList}${r.propertiesFound > 3 ? `\n   ... y ${r.propertiesFound - 3} más` : ''}`;
        }
      }).join('\n\n');
      
      return {
        content: [{
          type: 'text',
          text: `🔍 VERIFICACIÓN COMPLETA DE ALERTAS

📊 Resultados:
• Alertas verificadas: ${activeAlerts.length}
• Nuevas propiedades encontradas: ${totalNewProperties}

${summary}

✅ Verificación completada. Las notificaciones se han enviado según configuración.
⏰ Próximas verificaciones automáticas según frecuencia configurada.`
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: `❌ Error al verificar alertas: ${error.message}`
        }]
      };
    }
  },

  async startMonitoring(config) {
    console.log('🚀 Iniciando monitoreo automático...');
    
    if (!this.alertsSystem) {
      this.alertsSystem = new PropertyAlertsSystem();
    }
    
    const intervalMinutes = config.intervalMinutes || 30;
    
    try {
      this.alertsSystem.startMonitoring(intervalMinutes);
      
      return {
        content: [{
          type: 'text',
          text: `🚀 MONITOREO AUTOMÁTICO INICIADO

⚡ CONFIGURACIÓN:
• Intervalo de verificación: ${intervalMinutes} minutos
• Sistema: Ejecutándose en segundo plano
• Estado: Activo ✅

🔍 FUNCIONAMIENTO:
• El sistema verificará automáticamente todas las alertas activas
• Se ejecutará cada ${intervalMinutes} minutos
• Las notificaciones se enviarán según configuración de cada alerta
• El monitoreo continuará hasta que se detenga manualmente

📊 Para ver el estado actual usa 'list_alerts'
🔍 Para verificar manualmente usa 'check_alerts'

⚠️ NOTA: El monitoreo se ejecuta mientras el servidor MCP esté activo.
💡 En producción, considera usar un proceso daemon o servicio del sistema.`
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: `❌ Error al iniciar monitoreo: ${error.message}`
        }]
      };
    }
  },

  async analyzeInvestment(data) {
    console.log('🏦 Iniciando análisis de inversión completo...');
    
    if (!this.investmentAdvisor) {
      this.investmentAdvisor = new InvestmentAdvisor();
    }
    
    try {
      const report = this.investmentAdvisor.generateInvestmentReport(
        data.bankData,
        data.property,
        data.property.location || 'madrid',
        data.property.neighborhood || 'centro'
      );
      
      const formatCurrency = (amount) => amount.toLocaleString() + '€';
      const formatPercent = (percent) => percent.toFixed(2) + '%';
      
      return {
        content: [{
          type: 'text',
          text: `🏦 ANÁLISIS COMPLETO DE INVERSIÓN INMOBILIARIA

🏠 PROPIEDAD ANALIZADA:
• Precio: ${formatCurrency(report.propertyData.price)}
• Tamaño: ${report.propertyData.size}m²
• Ubicación: ${report.propertyData.neighborhood || 'Centro'}, Madrid
• Precio/m²: ${formatCurrency(Math.round(report.propertyData.price / report.propertyData.size))}

👤 PERFIL FINANCIERO:
• Ingresos mensuales: ${formatCurrency(report.bankData.monthlyIncome)}
• Gastos mensuales: ${formatCurrency(report.bankData.monthlyExpenses)}
• Ingresos netos: ${formatCurrency(report.affordability.netMonthlyIncome)}
• Ahorros: ${formatCurrency(report.bankData.savings)}
• Deuda actual: ${formatCurrency(report.bankData.currentDebt || 0)}

💳 ANÁLISIS DE CAPACIDAD DE PAGO:
• Entrada requerida (20%): ${formatCurrency(report.affordability.downPayment)}
• Cuota mensual hipoteca: ${formatCurrency(report.affordability.monthlyPayment)}
• Ratio vivienda/ingresos: ${formatPercent(report.affordability.housingRatio)}
• Ratio deuda total: ${formatPercent(report.affordability.debtToIncomeAfter)}
• ${report.affordability.recommendation}

📈 RENTABILIDAD ESPERADA:
• Renta mensual estimada: ${formatCurrency(report.profitability.estimatedRent)}
• Renta anual: ${formatCurrency(report.profitability.annualRent)}
• Gastos anuales: ${formatCurrency(report.profitability.expenses)}
• Ingresos netos anuales: ${formatCurrency(report.profitability.netAnnualIncome)}
• Rentabilidad bruta: ${formatPercent(report.profitability.grossYield)}
• Rentabilidad neta: ${formatPercent(report.profitability.netYield)}
• ${report.profitability.marketAnalysis}

🔄 COMPARACIÓN CON ALTERNATIVAS:
${report.alternatives.alternatives.map(alt => 
`• ${alt.name.toUpperCase()}: ${formatPercent(alt.avgReturn)} anual - ${alt.verdict}`
).join('\n')}

📊 PROYECCIÓN A 10 AÑOS:
• Año 5:
  - Valor propiedad: ${formatCurrency(report.projection.year5.propertyValue)}
  - Rentas acumuladas: ${formatCurrency(report.projection.year5.cumulativeRent)}
  - ROI: ${formatPercent(report.projection.year5.roi)}

• Año 10:
  - Valor propiedad: ${formatCurrency(report.projection.year10.propertyValue)}
  - Rentas acumuladas: ${formatCurrency(report.projection.year10.cumulativeRent)}
  - ROI total: ${formatPercent(report.projection.year10.roi)}
  - Rentabilidad anualizada: ${formatPercent(report.projection.year10.annualizedReturn)}

🎯 RECOMENDACIÓN FINAL:
${this.getFinalRecommendation(report)}`
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: `❌ Error en análisis de inversión: ${error.message}`
        }]
      };
    }
  },

  getFinalRecommendation(report) {
    const { affordability, profitability, projection } = report;
    
    if (affordability.viability === 'no-viable') {
      return '❌ INVERSIÓN NO RECOMENDABLE: No cumples con los criterios financieros mínimos. Considera aumentar ingresos, reducir gastos o buscar propiedades más económicas.';
    }
    
    if (profitability.netYield < 2.5 && projection.year10.annualizedReturn < 5) {
      return '⚠️ INVERSIÓN POCO ATRACTIVA: Aunque es financieramente viable, la rentabilidad está por debajo del mercado. Considera negociar el precio o buscar alternativas.';
    }
    
    if (affordability.viability === 'arriesgada' && profitability.netYield < 4) {
      return '⚠️ INVERSIÓN DE ALTO RIESGO: Estás en el límite de tu capacidad financiera y la rentabilidad no compensa el riesgo. Procede con precaución.';
    }
    
    if (profitability.netYield >= 4 && affordability.viability === 'viable') {
      return '✅ EXCELENTE OPORTUNIDAD: Cumples con todos los criterios financieros y la rentabilidad es atractiva. Esta inversión tiene potencial para generar buenos retornos.';
    }
    
    return '⚡ INVERSIÓN ACEPTABLE: La inversión es viable pero evalúa si se alinea con tus objetivos de riesgo y rentabilidad a largo plazo.';
  }
};

// Inicializar servidor
console.log('✅ Servidor MCP iniciado:', mcpServer.name);
console.log('📝 Versión:', mcpServer.version);
console.log('\n🔧 Herramientas disponibles:');
mcpServer.tools.forEach((tool, index) => {
  console.log(`${index + 1}. ${tool.name}: ${tool.description}`);
});

// Ejecutar pruebas de demostración
console.log('\n🧪 DEMOSTRACIONES:');

console.log('\n1️⃣ Búsqueda en Centro con presupuesto 500k€:');
const searchResult = mcpServer.handleRequest('tools/call', {
  name: 'search_properties',
  arguments: { neighborhood: 'Centro', max_price: 500000 }
});
console.log(searchResult.content[0].text);

console.log('\n2️⃣ Análisis de propiedad 300k€, 70m²:');
const analysisResult = mcpServer.handleRequest('tools/call', {
  name: 'analyze_property', 
  arguments: { price: 300000, size: 70, estimated_rent: 1200 }
});
console.log(analysisResult.content[0].text);

console.log('\n3️⃣ Comparación de barrios:');
const comparisonResult = mcpServer.handleRequest('tools/call', {
  name: 'compare_neighborhoods',
  arguments: { neighborhoods: ['Centro', 'Salamanca', 'Retiro'] }
});
console.log(comparisonResult.content[0].text);

console.log('\n4️⃣ Proyección inversión 10 años:');
const investmentResult = mcpServer.handleRequest('tools/call', {
  name: 'investment_calculator',
  arguments: { 
    initial_investment: 400000, 
    monthly_rent: 1800,
    years: 10,
    appreciation_rate: 4
  }
});
console.log(investmentResult.content[0].text);

console.log('\n✅ ¡Servidor completamente funcional!');
console.log('📋 Listo para integrar con Claude Code.');
console.log('\nPresiona Ctrl+C para salir...');

// Mantener el proceso activo
process.stdin.resume();