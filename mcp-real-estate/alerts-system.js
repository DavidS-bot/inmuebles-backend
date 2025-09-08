// alerts-system.js - Sistema de Alertas Automáticas para Propiedades

const fs = require('fs').promises;
const path = require('path');
const JerezPropertyScraper = require('./jerez-scraper');
const { JerezMockDataProvider } = require('./jerez-mock-data');

class PropertyAlertsSystem {
  constructor() {
    this.alertsFile = path.join(__dirname, 'alerts-config.json');
    this.alertsHistoryFile = path.join(__dirname, 'alerts-history.json');
    this.scraper = new JerezPropertyScraper();
    this.mockProvider = new JerezMockDataProvider();
    this.isRunning = false;
  }

  // Configurar nueva alerta
  async createAlert(alertConfig) {
    const alert = {
      id: 'alert_' + Date.now(),
      name: alertConfig.name || 'Alerta sin nombre',
      criteria: {
        location: alertConfig.location || 'jerez',
        maxPrice: alertConfig.maxPrice || null,
        minPrice: alertConfig.minPrice || null,
        rooms: alertConfig.rooms || null,
        minSize: alertConfig.minSize || null,
        maxDaysOld: alertConfig.maxDaysOld || 7,
        keywords: alertConfig.keywords || []
      },
      notifications: {
        email: alertConfig.email || null,
        webhook: alertConfig.webhook || null,
        console: alertConfig.console !== false // Por defecto true
      },
      schedule: {
        frequency: alertConfig.frequency || 'hourly', // hourly, daily, weekly
        lastCheck: null,
        nextCheck: null
      },
      active: true,
      created: new Date().toISOString()
    };

    const alerts = await this.getAlerts();
    alerts.push(alert);
    await this.saveAlerts(alerts);

    console.log(`✅ Alerta creada: ${alert.name} (ID: ${alert.id})`);
    return alert;
  }

  // Obtener todas las alertas
  async getAlerts() {
    try {
      const data = await fs.readFile(this.alertsFile, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      return []; // Si no existe el archivo, devolver array vacío
    }
  }

  // Guardar alertas
  async saveAlerts(alerts) {
    await fs.writeFile(this.alertsFile, JSON.stringify(alerts, null, 2));
  }

  // Obtener historial de alertas
  async getAlertsHistory() {
    try {
      const data = await fs.readFile(this.alertsHistoryFile, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      return [];
    }
  }

  // Guardar en historial
  async saveToHistory(alertId, properties, timestamp) {
    const history = await this.getAlertsHistory();
    history.push({
      alertId,
      timestamp,
      propertiesFound: properties.length,
      properties: properties.slice(0, 5) // Solo guardar las primeras 5 para no ocupar mucho espacio
    });

    // Mantener solo los últimos 100 registros
    if (history.length > 100) {
      history.splice(0, history.length - 100);
    }

    await fs.writeFile(this.alertsHistoryFile, JSON.stringify(history, null, 2));
  }

  // Verificar una alerta específica
  async checkAlert(alert) {
    console.log(`🔍 Verificando alerta: ${alert.name}`);

    try {
      let properties = [];

      if (alert.criteria.location === 'jerez') {
        // Buscar en Jerez usando el scraper
        const results = await this.scraper.searchJerezProperties({
          rooms: alert.criteria.rooms,
          maxDaysOld: alert.criteria.maxDaysOld,
          maxPrice: alert.criteria.maxPrice,
          minPrice: alert.criteria.minPrice,
          useMockData: true // Usar datos mock para demostración
        });

        if (results.content && results.content[0]) {
          // Parsear resultados (esto es simplificado, en producción sería más robusto)
          properties = this.parsePropertiesFromResults(results.content[0].text);
        }
      }

      // Filtrar por palabras clave si están definidas
      if (alert.criteria.keywords.length > 0) {
        properties = properties.filter(prop => 
          alert.criteria.keywords.some(keyword => 
            prop.title.toLowerCase().includes(keyword.toLowerCase()) ||
            prop.description.toLowerCase().includes(keyword.toLowerCase())
          )
        );
      }

      // Filtrar propiedades nuevas (que no hayamos visto antes)
      const newProperties = await this.filterNewProperties(alert.id, properties);

      if (newProperties.length > 0) {
        console.log(`🚨 ¡${newProperties.length} nuevas propiedades encontradas para: ${alert.name}!`);
        await this.sendNotification(alert, newProperties);
        await this.saveToHistory(alert.id, newProperties, new Date().toISOString());
      } else {
        console.log(`ℹ️ No hay nuevas propiedades para: ${alert.name}`);
      }

      // Actualizar última verificación
      alert.schedule.lastCheck = new Date().toISOString();
      alert.schedule.nextCheck = this.calculateNextCheck(alert.schedule.frequency);

      return newProperties;

    } catch (error) {
      console.error(`❌ Error verificando alerta ${alert.name}:`, error.message);
      return [];
    }
  }

  // Parsear propiedades de los resultados de texto (método simplificado)
  parsePropertiesFromResults(resultsText) {
    const properties = [];
    const lines = resultsText.split('\n');
    
    let currentProperty = null;
    for (const line of lines) {
      if (line.match(/^\d+\. 📍/)) {
        if (currentProperty) properties.push(currentProperty);
        currentProperty = {
          title: line.substring(line.indexOf('📍') + 2).trim(),
          price: '',
          details: '',
          link: '',
          id: 'parsed_' + Date.now() + Math.random()
        };
      } else if (currentProperty) {
        if (line.includes('💰')) currentProperty.price = line.substring(line.indexOf('💰') + 2).split('|')[0].trim();
        if (line.includes('🏠')) currentProperty.details = line.substring(line.indexOf('🏠') + 2).split('|')[0].trim();
        if (line.includes('🔗')) currentProperty.link = line.substring(line.indexOf('🔗') + 2).trim();
      }
    }
    if (currentProperty) properties.push(currentProperty);
    
    return properties;
  }

  // Filtrar propiedades nuevas
  async filterNewProperties(alertId, properties) {
    const history = await this.getAlertsHistory();
    const previousProperties = history
      .filter(h => h.alertId === alertId)
      .flatMap(h => h.properties)
      .map(p => p.id || p.title);

    return properties.filter(prop => 
      !previousProperties.includes(prop.id || prop.title)
    );
  }

  // Calcular próxima verificación
  calculateNextCheck(frequency) {
    const now = new Date();
    switch (frequency) {
      case 'hourly':
        return new Date(now.getTime() + 60 * 60 * 1000).toISOString();
      case 'daily':
        return new Date(now.getTime() + 24 * 60 * 60 * 1000).toISOString();
      case 'weekly':
        return new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString();
      default:
        return new Date(now.getTime() + 60 * 60 * 1000).toISOString();
    }
  }

  // Enviar notificación
  async sendNotification(alert, properties) {
    const message = this.formatNotificationMessage(alert, properties);

    // Notificación por consola
    if (alert.notifications.console) {
      console.log('\n' + '='.repeat(60));
      console.log('🚨 ALERTA DE PROPIEDADES');
      console.log('='.repeat(60));
      console.log(message);
      console.log('='.repeat(60) + '\n');
    }

    // Notificación por email (simulada)
    if (alert.notifications.email) {
      console.log(`📧 Enviando email a: ${alert.notifications.email}`);
      // Aquí integrarías con un servicio de email real como SendGrid, Nodemailer, etc.
      await this.sendEmailNotification(alert.notifications.email, alert.name, message);
    }

    // Notificación por webhook (simulada)
    if (alert.notifications.webhook) {
      console.log(`🔔 Enviando webhook a: ${alert.notifications.webhook}`);
      // Aquí enviarías una petición HTTP POST al webhook
      await this.sendWebhookNotification(alert.notifications.webhook, {
        alertId: alert.id,
        alertName: alert.name,
        propertiesCount: properties.length,
        properties: properties.slice(0, 3), // Enviar solo las primeras 3
        timestamp: new Date().toISOString()
      });
    }
  }

  // Formatear mensaje de notificación
  formatNotificationMessage(alert, properties) {
    let message = `🏠 NUEVAS PROPIEDADES ENCONTRADAS\n`;
    message += `📊 Alerta: ${alert.name}\n`;
    message += `🔍 Encontradas: ${properties.length} propiedades\n\n`;

    properties.slice(0, 5).forEach((prop, index) => {
      message += `${index + 1}. ${prop.title}\n`;
      message += `   💰 ${prop.price}\n`;
      message += `   🏠 ${prop.details}\n`;
      message += `   🔗 ${prop.link}\n\n`;
    });

    if (properties.length > 5) {
      message += `... y ${properties.length - 5} propiedades más.\n`;
    }

    return message;
  }

  // Simular envío de email
  async sendEmailNotification(email, alertName, message) {
    // Simulación - en producción usarías un servicio real
    console.log(`📧 EMAIL ENVIADO A: ${email}`);
    console.log(`📄 ASUNTO: Nueva propiedad - ${alertName}`);
    console.log(`📝 CONTENIDO:\n${message}`);
    return Promise.resolve();
  }

  // Simular webhook
  async sendWebhookNotification(webhookUrl, data) {
    // Simulación - en producción harías una petición HTTP real
    console.log(`🔔 WEBHOOK ENVIADO A: ${webhookUrl}`);
    console.log(`📦 DATOS:`, JSON.stringify(data, null, 2));
    return Promise.resolve();
  }

  // Verificar todas las alertas activas
  async checkAllAlerts() {
    const alerts = await this.getAlerts();
    const activeAlerts = alerts.filter(alert => alert.active);

    console.log(`🔍 Verificando ${activeAlerts.length} alertas activas...`);

    for (const alert of activeAlerts) {
      // Solo verificar si es hora de hacerlo
      if (!alert.schedule.nextCheck || new Date() >= new Date(alert.schedule.nextCheck)) {
        await this.checkAlert(alert);
      }
    }

    // Actualizar alertas
    await this.saveAlerts(alerts);
  }

  // Iniciar sistema de monitoreo automático
  startMonitoring(intervalMinutes = 30) {
    if (this.isRunning) {
      console.log('⚠️ El sistema de monitoreo ya está ejecutándose');
      return;
    }

    console.log(`🚀 Iniciando sistema de alertas (verificación cada ${intervalMinutes} minutos)`);
    this.isRunning = true;

    // Verificación inicial
    this.checkAllAlerts();

    // Programar verificaciones periódicas
    this.monitoringInterval = setInterval(async () => {
      if (this.isRunning) {
        console.log('🔄 Ejecutando verificación periódica de alertas...');
        await this.checkAllAlerts();
      }
    }, intervalMinutes * 60 * 1000);
  }

  // Detener monitoreo
  stopMonitoring() {
    console.log('⏹️ Deteniendo sistema de alertas');
    this.isRunning = false;
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
    }
  }

  // Obtener estadísticas
  async getStats() {
    const alerts = await this.getAlerts();
    const history = await this.getAlertsHistory();

    return {
      totalAlerts: alerts.length,
      activeAlerts: alerts.filter(a => a.active).length,
      inactiveAlerts: alerts.filter(a => !a.active).length,
      totalNotifications: history.length,
      lastNotification: history.length > 0 ? history[history.length - 1].timestamp : null,
      isMonitoring: this.isRunning
    };
  }
}

module.exports = PropertyAlertsSystem;

// Test si se ejecuta directamente
if (require.main === module) {
  async function testAlerts() {
    const alertSystem = new PropertyAlertsSystem();
    
    console.log('🧪 DEMO: Sistema de Alertas de Propiedades\n');
    
    // Crear alerta de ejemplo
    const alert = await alertSystem.createAlert({
      name: 'Pisos baratos Jerez',
      location: 'jerez',
      maxPrice: 80000,
      rooms: 2,
      maxDaysOld: 14,
      email: 'usuario@ejemplo.com',
      console: true,
      frequency: 'hourly'
    });
    
    console.log('🔍 Verificando alerta...');
    await alertSystem.checkAlert(alert);
    
    console.log('\n📊 Estadísticas:');
    const stats = await alertSystem.getStats();
    console.log(stats);
    
    console.log('\n⚡ Para usar en producción, ejecuta: alertSystem.startMonitoring()');
  }
  
  testAlerts().catch(console.error);
}