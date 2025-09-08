// investment-advisor.js
class InvestmentAdvisor {
  constructor() {
    this.marketData = {
      madrid: {
        centro: { avgPricePerSqm: 5500, avgRent: 16, appreciation: 3.5 },
        salamanca: { avgPricePerSqm: 6200, avgRent: 14, appreciation: 4.0 },
        retiro: { avgPricePerSqm: 5800, avgRent: 15, appreciation: 3.8 }
      },
      alternatives: {
        'bolsa-espana': { avgReturn: 7.2, volatility: 18.5, risk: 'medio' },
        'bonos-estado': { avgReturn: 2.8, volatility: 4.2, risk: 'bajo' },
        'reit': { avgReturn: 6.5, volatility: 15.3, risk: 'medio-bajo' },
        'deposito': { avgReturn: 3.2, volatility: 0.1, risk: 'muy-bajo' }
      }
    };
  }

  analyzeAffordability(bankData, propertyPrice) {
    const monthlyIncome = bankData.monthlyIncome || 0;
    const monthlyExpenses = bankData.monthlyExpenses || 0;
    const savings = bankData.savings || 0;
    const currentDebt = bankData.currentDebt || 0;
    
    // Cálculos de capacidad de pago
    const netMonthlyIncome = monthlyIncome - monthlyExpenses;
    const debtToIncomeRatio = (currentDebt / monthlyIncome) || 0;
    const downPayment = propertyPrice * 0.2; // 20% entrada típica
    const loanAmount = propertyPrice - downPayment;
    const monthlyPayment = this.calculateMortgagePayment(loanAmount, 3.5, 30);
    
    // Ratios financieros
    const housingRatio = (monthlyPayment / monthlyIncome) * 100;
    const debtToIncomeAfter = ((currentDebt + monthlyPayment) / monthlyIncome) * 100;
    
    // Análisis de viabilidad
    let viability = 'no-viable';
    let recommendation = '';
    
    if (housingRatio <= 30 && debtToIncomeAfter <= 40 && savings >= downPayment) {
      viability = 'viable';
      recommendation = '✅ Inversión financieramente viable';
    } else if (housingRatio <= 35 && debtToIncomeAfter <= 45) {
      viability = 'arriesgada';
      recommendation = '⚠️ Inversión arriesgada - considerar reducir precio';
    } else {
      viability = 'no-viable';
      recommendation = '❌ Inversión no recomendable con ingresos actuales';
    }
    
    return {
      viability,
      recommendation,
      downPayment,
      monthlyPayment,
      housingRatio: Math.round(housingRatio * 100) / 100,
      debtToIncomeAfter: Math.round(debtToIncomeAfter * 100) / 100,
      netMonthlyIncome,
      debtToIncomeRatio: Math.round(debtToIncomeRatio * 100) / 100
    };
  }

  calculateExpectedProfitability(propertyData, location = 'madrid', neighborhood = 'centro') {
    const marketInfo = this.marketData.madrid[neighborhood.toLowerCase()] || this.marketData.madrid.centro;
    
    const estimatedRent = (propertyData.size * marketInfo.avgRent);
    const annualRent = estimatedRent * 12;
    const expenses = annualRent * 0.35; // 35% gastos
    const netAnnualIncome = annualRent - expenses;
    
    const grossYield = (annualRent / propertyData.price) * 100;
    const netYield = (netAnnualIncome / propertyData.price) * 100;
    
    // Análisis de mercado
    let marketAnalysis = '';
    if (netYield >= 5) marketAnalysis = '🚀 Excelente rentabilidad para el mercado';
    else if (netYield >= 3.5) marketAnalysis = '✅ Rentabilidad por encima del promedio';
    else if (netYield >= 2.5) marketAnalysis = '⚠️ Rentabilidad en línea con mercado';
    else marketAnalysis = '❌ Rentabilidad por debajo del mercado';
    
    return {
      estimatedRent,
      annualRent,
      expenses,
      netAnnualIncome,
      grossYield: Math.round(grossYield * 100) / 100,
      netYield: Math.round(netYield * 100) / 100,
      marketAnalysis,
      appreciation: marketInfo.appreciation
    };
  }

  compareWithAlternatives(investmentAmount, expectedNetYield) {
    const alternatives = Object.entries(this.marketData.alternatives).map(([name, data]) => {
      const annualReturn = investmentAmount * (data.avgReturn / 100);
      const riskAdjustedReturn = annualReturn / (1 + data.volatility / 100);
      
      return {
        name,
        avgReturn: data.avgReturn,
        annualReturn,
        volatility: data.volatility,
        risk: data.risk,
        riskAdjustedReturn
      };
    });
    
    const propertyAnnualReturn = investmentAmount * (expectedNetYield / 100);
    
    // Comparación
    let comparison = alternatives.map(alt => {
      const difference = expectedNetYield - alt.avgReturn;
      let verdict = '';
      
      if (difference > 2) verdict = '🏠 Inmueble claramente superior';
      else if (difference > 0.5) verdict = '✅ Inmueble ligeramente mejor';
      else if (difference > -0.5) verdict = '⚖️ Rendimientos similares';
      else if (difference > -2) verdict = '⚠️ Alternativa ligeramente mejor';
      else verdict = '❌ Alternativa claramente superior';
      
      return {
        ...alt,
        difference: Math.round(difference * 100) / 100,
        verdict
      };
    });
    
    return {
      propertyReturn: expectedNetYield,
      propertyAnnualReturn,
      alternatives: comparison
    };
  }

  projectROI(investmentData, years = 10) {
    const { initialInvestment, monthlyRent, appreciation, expenses } = investmentData;
    
    let results = [];
    let cumulativeRent = 0;
    let propertyValue = initialInvestment;
    
    for (let year = 1; year <= years; year++) {
      const annualRent = monthlyRent * 12;
      const annualExpenses = annualRent * (expenses / 100);
      const netAnnualRent = annualRent - annualExpenses;
      
      cumulativeRent += netAnnualRent;
      propertyValue *= (1 + appreciation / 100);
      
      const totalReturn = cumulativeRent + (propertyValue - initialInvestment);
      const roi = (totalReturn / initialInvestment) * 100;
      const annualizedReturn = Math.pow(totalReturn / initialInvestment, 1/year) - 1;
      
      results.push({
        year,
        propertyValue: Math.round(propertyValue),
        cumulativeRent: Math.round(cumulativeRent),
        totalReturn: Math.round(totalReturn),
        roi: Math.round(roi * 100) / 100,
        annualizedReturn: Math.round(annualizedReturn * 10000) / 100
      });
    }
    
    return results;
  }

  calculateMortgagePayment(principal, annualRate, years) {
    const monthlyRate = annualRate / 100 / 12;
    const numPayments = years * 12;
    
    if (monthlyRate === 0) return principal / numPayments;
    
    const monthlyPayment = principal * (monthlyRate * Math.pow(1 + monthlyRate, numPayments)) / 
                          (Math.pow(1 + monthlyRate, numPayments) - 1);
    
    return Math.round(monthlyPayment);
  }

  generateInvestmentReport(bankData, propertyData, location = 'madrid', neighborhood = 'centro') {
    const affordability = this.analyzeAffordability(bankData, propertyData.price);
    const profitability = this.calculateExpectedProfitability(propertyData, location, neighborhood);
    const alternatives = this.compareWithAlternatives(propertyData.price, profitability.netYield);
    const projection = this.projectROI({
      initialInvestment: propertyData.price,
      monthlyRent: profitability.estimatedRent,
      appreciation: profitability.appreciation,
      expenses: 35
    }, 10);
    
    return {
      propertyData,
      bankData,
      affordability,
      profitability,
      alternatives,
      projection: {
        year5: projection[4],
        year10: projection[9],
        fullProjection: projection
      }
    };
  }
}

module.exports = InvestmentAdvisor;