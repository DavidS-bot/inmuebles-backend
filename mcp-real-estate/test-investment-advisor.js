// test-investment-advisor.js
const InvestmentAdvisor = require('./investment-advisor');

console.log('🧪 PRUEBA DEL AGENTE DE ANÁLISIS DE INVERSIÓN\n');

const advisor = new InvestmentAdvisor();

// Datos de ejemplo del prompt original
const propertyData = {
  price: 350000,
  size: 80,
  location: 'madrid',
  neighborhood: 'centro'
};

const bankData = {
  monthlyIncome: 4500,
  monthlyExpenses: 2800,
  savings: 85000,
  currentDebt: 0
};

console.log('🏠 PROPIEDAD ANALIZADA:');
console.log(`• Precio: ${propertyData.price.toLocaleString()}€`);
console.log(`• Tamaño: ${propertyData.size}m²`);
console.log(`• Ubicación: ${propertyData.neighborhood}, Madrid`);

console.log('\n👤 PERFIL FINANCIERO:');
console.log(`• Ingresos mensuales: ${bankData.monthlyIncome.toLocaleString()}€`);
console.log(`• Gastos mensuales: ${bankData.monthlyExpenses.toLocaleString()}€`);
console.log(`• Ingresos netos: ${(bankData.monthlyIncome - bankData.monthlyExpenses).toLocaleString()}€`);
console.log(`• Ahorros: ${bankData.savings.toLocaleString()}€`);

console.log('\n📊 EJECUTANDO ANÁLISIS COMPLETO...\n');

const report = advisor.generateInvestmentReport(bankData, propertyData, 'madrid', 'centro');

console.log('💳 CAPACIDAD DE PAGO:');
console.log(`• Entrada requerida (20%): ${report.affordability.downPayment.toLocaleString()}€`);
console.log(`• Cuota mensual hipoteca: ${report.affordability.monthlyPayment.toLocaleString()}€`);
console.log(`• Ratio vivienda/ingresos: ${report.affordability.housingRatio}%`);
console.log(`• Ratio deuda total: ${report.affordability.debtToIncomeAfter}%`);
console.log(`• ${report.affordability.recommendation}`);

console.log('\n📈 RENTABILIDAD ESPERADA:');
console.log(`• Renta mensual estimada: ${report.profitability.estimatedRent.toLocaleString()}€`);
console.log(`• Rentabilidad neta: ${report.profitability.netYield.toFixed(2)}%`);
console.log(`• ${report.profitability.marketAnalysis}`);

console.log('\n🔄 COMPARACIÓN CON ALTERNATIVAS:');
report.alternatives.alternatives.forEach(alt => {
  console.log(`• ${alt.name.toUpperCase()}: ${alt.avgReturn}% anual - ${alt.verdict}`);
});

console.log('\n📊 PROYECCIÓN A 10 AÑOS:');
console.log(`• Valor final propiedad: ${report.projection.year10.propertyValue.toLocaleString()}€`);
console.log(`• Rentas acumuladas: ${report.projection.year10.cumulativeRent.toLocaleString()}€`);
console.log(`• ROI total: ${report.projection.year10.roi}%`);
console.log(`• Rentabilidad anualizada: ${report.projection.year10.annualizedReturn}%`);

console.log('\n🎯 RECOMENDACIÓN FINAL:');
if (report.affordability.viability === 'no-viable') {
  console.log('❌ INVERSIÓN NO RECOMENDABLE: No cumples con los criterios financieros mínimos.');
} else if (report.profitability.netYield < 2.5 && report.projection.year10.annualizedReturn < 5) {
  console.log('⚠️ INVERSIÓN POCO ATRACTIVA: La rentabilidad está por debajo del mercado.');
} else if (report.affordability.viability === 'arriesgada' && report.profitability.netYield < 4) {
  console.log('⚠️ INVERSIÓN DE ALTO RIESGO: Estás en el límite de capacidad financiera.');
} else if (report.profitability.netYield >= 4 && report.affordability.viability === 'viable') {
  console.log('✅ EXCELENTE OPORTUNIDAD: Cumples criterios financieros y rentabilidad atractiva.');
} else {
  console.log('⚡ INVERSIÓN ACEPTABLE: Es viable pero evalúa si se alinea con tus objetivos.');
}

console.log('\n✅ Análisis completado exitosamente!');