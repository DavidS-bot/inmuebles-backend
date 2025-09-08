// demo-alerts.js - Demostración completa del sistema de alertas

const PropertyAlertsSystem = require('./alerts-system');

async function demoCompleto() {
  console.log('🚨 SISTEMA DE ALERTAS AUTOMÁTICAS - DEMO COMPLETO\n');
  console.log('=' .repeat(60));

  const alertSystem = new PropertyAlertsSystem();
  
  // 1. Crear diferentes tipos de alertas
  console.log('\n1️⃣ CREANDO ALERTAS DE EJEMPLO...\n');
  
  const alerta1 = await alertSystem.createAlert({
    name: 'Pisos económicos Jerez',
    location: 'jerez',
    maxPrice: 85000,
    rooms: 2,
    email: 'inversor@ejemplo.com',
    frequency: 'daily',
    console: true
  });
  
  const alerta2 = await alertSystem.createAlert({
    name: 'Oportunidades de inversión',
    location: 'jerez',
    minPrice: 50000,
    maxPrice: 120000,
    rooms: 2,
    email: 'oportunidades@ejemplo.com',
    webhook: 'https://hooks.ejemplo.com/webhook',
    frequency: 'hourly',
    console: true
  });
  
  const alerta3 = await alertSystem.createAlert({
    name: 'Propiedades premium',
    location: 'jerez',
    minPrice: 100000,
    rooms: 2,
    maxDaysOld: 3,
    email: 'premium@ejemplo.com',
    frequency: 'hourly',
    console: true
  });
  
  console.log(`✅ ${alerta1.name} - ID: ${alerta1.id}`);
  console.log(`✅ ${alerta2.name} - ID: ${alerta2.id}`);  
  console.log(`✅ ${alerta3.name} - ID: ${alerta3.id}`);
  
  // 2. Listar alertas
  console.log('\n' + '='.repeat(60));
  console.log('\n2️⃣ LISTADO DE ALERTAS CONFIGURADAS...\n');
  
  const alertas = await alertSystem.getAlerts();
  alertas.forEach((alert, index) => {
    console.log(`📋 ${index + 1}. ${alert.name}`);
    console.log(`   🆔 ID: ${alert.id}`);
    console.log(`   🏠 Ubicación: ${alert.criteria.location}`);
    console.log(`   💰 Precio: ${alert.criteria.minPrice || 0}€ - ${alert.criteria.maxPrice || '∞'}€`);
    console.log(`   🛏️  Habitaciones: ${alert.criteria.rooms || 'Cualquiera'}`);
    console.log(`   📧 Email: ${alert.notifications.email || 'No configurado'}`);
    console.log(`   📅 Frecuencia: ${alert.schedule.frequency}`);
    console.log(`   ${alert.active ? '✅ Activa' : '❌ Inactiva'}`);
    console.log('');
  });
  
  // 3. Verificar alertas manualmente
  console.log('='.repeat(60));
  console.log('\n3️⃣ VERIFICACIÓN MANUAL DE ALERTAS...\n');
  
  for (const alert of alertas) {
    console.log(`🔍 Verificando: ${alert.name}`);
    const newProperties = await alertSystem.checkAlert(alert);
    
    if (newProperties.length > 0) {
      console.log(`   🚨 ${newProperties.length} nuevas propiedades encontradas!`);
    } else {
      console.log(`   ℹ️  Sin nuevas propiedades`);
    }
  }
  
  // 4. Mostrar estadísticas
  console.log('\n' + '='.repeat(60));
  console.log('\n4️⃣ ESTADÍSTICAS DEL SISTEMA...\n');
  
  const stats = await alertSystem.getStats();
  console.log(`📊 Total de alertas: ${stats.totalAlerts}`);
  console.log(`✅ Alertas activas: ${stats.activeAlerts}`);
  console.log(`❌ Alertas inactivas: ${stats.inactiveAlerts}`);
  console.log(`📧 Notificaciones enviadas: ${stats.totalNotifications}`);
  console.log(`🔄 Monitoreo automático: ${stats.isMonitoring ? 'Activo' : 'Inactivo'}`);
  
  if (stats.lastNotification) {
    console.log(`⏰ Última notificación: ${new Date(stats.lastNotification).toLocaleString()}`);
  }
  
  // 5. Demostrar monitoreo automático
  console.log('\n' + '='.repeat(60));
  console.log('\n5️⃣ INICIANDO MONITOREO AUTOMÁTICO...\n');
  
  console.log('🚀 El monitoreo automático verificará las alertas cada 30 segundos');
  console.log('🔔 Las notificaciones se enviarán según configuración');
  console.log('⏹️  Presiona Ctrl+C para detener');
  
  // Iniciar monitoreo con intervalo corto para demo
  alertSystem.startMonitoring(0.5); // 30 segundos para demo
  
  // Mantener el proceso corriendo
  process.on('SIGINT', () => {
    console.log('\n\n⏹️ Deteniendo sistema de alertas...');
    alertSystem.stopMonitoring();
    console.log('✅ Sistema detenido correctamente');
    process.exit(0);
  });
  
  console.log('\n💡 COMANDOS DISPONIBLES EN PRODUCCIÓN:');
  console.log('   • alertSystem.createAlert(config)');
  console.log('   • alertSystem.getAlerts()');
  console.log('   • alertSystem.checkAllAlerts()');
  console.log('   • alertSystem.startMonitoring()');
  console.log('   • alertSystem.stopMonitoring()');
}

// Ejecutar demo
demoCompleto().catch(console.error);