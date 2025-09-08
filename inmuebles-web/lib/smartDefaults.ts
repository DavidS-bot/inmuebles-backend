// Smart defaults system for property onboarding
export interface ZoneData {
  avgRent: number;
  avgPrice: number;
  avgM2: number;
  avgRooms: number;
  taxBenefit: number;
  commonExpenses: ExpenseDefault[];
  propertyTypes: PropertyTypeData[];
}

export interface ExpenseDefault {
  name: string;
  amount: number;
  category: string;
  subcategory: string;
  frequency: 'monthly' | 'quarterly' | 'annual';
  description: string;
}

export interface PropertyTypeData {
  type: string;
  avgM2: number;
  avgRooms: number;
  avgPrice: number;
}

export const ZONE_DATABASE: Record<string, ZoneData> = {
  "Madrid Centro": {
    avgRent: 1800,
    avgPrice: 500000,
    avgM2: 85,
    avgRooms: 3,
    taxBenefit: 0.15,
    commonExpenses: [
      { name: "IBI", amount: 1200, category: "Gasto", subcategory: "Impuestos", frequency: "annual", description: "Impuesto sobre Bienes Inmuebles" },
      { name: "Seguro Hogar", amount: 350, category: "Gasto", subcategory: "Seguros", frequency: "annual", description: "Seguro del continente y contenido" },
      { name: "Comunidad", amount: 120, category: "Gasto", subcategory: "Mantenimiento", frequency: "monthly", description: "Gastos de comunidad de propietarios" },
      { name: "Reparaciones", amount: 80, category: "Gasto", subcategory: "Mantenimiento", frequency: "monthly", description: "Mantenimiento y reparaciones estimadas" },
      { name: "Gestión", amount: 50, category: "Gasto", subcategory: "Servicios", frequency: "monthly", description: "Gestión de alquiler (si aplica)" }
    ],
    propertyTypes: [
      { type: "Piso", avgM2: 85, avgRooms: 3, avgPrice: 500000 },
      { type: "Ático", avgM2: 120, avgRooms: 4, avgPrice: 750000 },
      { type: "Estudio", avgM2: 45, avgRooms: 1, avgPrice: 300000 }
    ]
  },
  "Barcelona Centro": {
    avgRent: 1600,
    avgPrice: 450000,
    avgM2: 80,
    avgRooms: 3,
    taxBenefit: 0.14,
    commonExpenses: [
      { name: "IBI", amount: 1000, category: "Gasto", subcategory: "Impuestos", frequency: "annual", description: "Impuesto sobre Bienes Inmuebles" },
      { name: "Seguro Hogar", amount: 320, category: "Gasto", subcategory: "Seguros", frequency: "annual", description: "Seguro del continente y contenido" },
      { name: "Comunidad", amount: 110, category: "Gasto", subcategory: "Mantenimiento", frequency: "monthly", description: "Gastos de comunidad de propietarios" },
      { name: "Reparaciones", amount: 70, category: "Gasto", subcategory: "Mantenimiento", frequency: "monthly", description: "Mantenimiento y reparaciones estimadas" },
      { name: "Gestión", amount: 45, category: "Gasto", subcategory: "Servicios", frequency: "monthly", description: "Gestión de alquiler (si aplica)" }
    ],
    propertyTypes: [
      { type: "Piso", avgM2: 80, avgRooms: 3, avgPrice: 450000 },
      { type: "Ático", avgM2: 110, avgRooms: 4, avgPrice: 650000 },
      { type: "Estudio", avgM2: 40, avgRooms: 1, avgPrice: 280000 }
    ]
  },
  "Valencia": {
    avgRent: 1200,
    avgPrice: 300000,
    avgM2: 95,
    avgRooms: 3,
    taxBenefit: 0.13,
    commonExpenses: [
      { name: "IBI", amount: 800, category: "Gasto", subcategory: "Impuestos", frequency: "annual", description: "Impuesto sobre Bienes Inmuebles" },
      { name: "Seguro Hogar", amount: 280, category: "Gasto", subcategory: "Seguros", frequency: "annual", description: "Seguro del continente y contenido" },
      { name: "Comunidad", amount: 85, category: "Gasto", subcategory: "Mantenimiento", frequency: "monthly", description: "Gastos de comunidad de propietarios" },
      { name: "Reparaciones", amount: 60, category: "Gasto", subcategory: "Mantenimiento", frequency: "monthly", description: "Mantenimiento y reparaciones estimadas" },
      { name: "Gestión", amount: 35, category: "Gasto", subcategory: "Servicios", frequency: "monthly", description: "Gestión de alquiler (si aplica)" }
    ],
    propertyTypes: [
      { type: "Piso", avgM2: 95, avgRooms: 3, avgPrice: 300000 },
      { type: "Casa", avgM2: 150, avgRooms: 4, avgPrice: 400000 },
      { type: "Estudio", avgM2: 50, avgRooms: 1, avgPrice: 180000 }
    ]
  },
  "Sevilla": {
    avgRent: 1000,
    avgPrice: 250000,
    avgM2: 100,
    avgRooms: 3,
    taxBenefit: 0.12,
    commonExpenses: [
      { name: "IBI", amount: 600, category: "Gasto", subcategory: "Impuestos", frequency: "annual", description: "Impuesto sobre Bienes Inmuebles" },
      { name: "Seguro Hogar", amount: 250, category: "Gasto", subcategory: "Seguros", frequency: "annual", description: "Seguro del continente y contenido" },
      { name: "Comunidad", amount: 70, category: "Gasto", subcategory: "Mantenimiento", frequency: "monthly", description: "Gastos de comunidad de propietarios" },
      { name: "Reparaciones", amount: 50, category: "Gasto", subcategory: "Mantenimiento", frequency: "monthly", description: "Mantenimiento y reparaciones estimadas" },
      { name: "Gestión", amount: 30, category: "Gasto", subcategory: "Servicios", frequency: "monthly", description: "Gestión de alquiler (si aplica)" }
    ],
    propertyTypes: [
      { type: "Piso", avgM2: 100, avgRooms: 3, avgPrice: 250000 },
      { type: "Casa", avgM2: 180, avgRooms: 4, avgPrice: 320000 },
      { type: "Estudio", avgM2: 55, avgRooms: 1, avgPrice: 150000 }
    ]
  },
  "Otro": {
    avgRent: 1400,
    avgPrice: 350000,
    avgM2: 90,
    avgRooms: 3,
    taxBenefit: 0.13,
    commonExpenses: [
      { name: "IBI", amount: 800, category: "Gasto", subcategory: "Impuestos", frequency: "annual", description: "Impuesto sobre Bienes Inmuebles" },
      { name: "Seguro Hogar", amount: 300, category: "Gasto", subcategory: "Seguros", frequency: "annual", description: "Seguro del continente y contenido" },
      { name: "Comunidad", amount: 100, category: "Gasto", subcategory: "Mantenimiento", frequency: "monthly", description: "Gastos de comunidad de propietarios" },
      { name: "Reparaciones", amount: 65, category: "Gasto", subcategory: "Mantenimiento", frequency: "monthly", description: "Mantenimiento y reparaciones estimadas" },
      { name: "Gestión", amount: 40, category: "Gasto", subcategory: "Servicios", frequency: "monthly", description: "Gestión de alquiler (si aplica)" }
    ],
    propertyTypes: [
      { type: "Piso", avgM2: 90, avgRooms: 3, avgPrice: 350000 },
      { type: "Casa", avgM2: 140, avgRooms: 4, avgPrice: 450000 },
      { type: "Estudio", avgM2: 48, avgRooms: 1, avgPrice: 200000 }
    ]
  }
};

// Smart address parsing
export function detectZoneFromAddress(address: string): string {
  const addressLower = address.toLowerCase();
  
  // City detection
  if (addressLower.includes('madrid')) return 'Madrid Centro';
  if (addressLower.includes('barcelona')) return 'Barcelona Centro';
  if (addressLower.includes('valencia')) return 'Valencia';
  if (addressLower.includes('sevilla') || addressLower.includes('seville')) return 'Sevilla';
  
  // District detection for Madrid
  const madridDistricts = ['centro', 'salamanca', 'chamberí', 'retiro', 'chamartín'];
  if (madridDistricts.some(district => addressLower.includes(district))) {
    return 'Madrid Centro';
  }
  
  return 'Otro';
}

// Calculate fiscal savings
export function calculateFiscalSavings(address: string, monthlyRent: number, purchasePrice?: number) {
  const zone = detectZoneFromAddress(address);
  const zoneData = ZONE_DATABASE[zone];
  
  // Estimate purchase price if not provided
  const estimatedPrice = purchasePrice || (monthlyRent * 12 * 16); // 16x annual rent multiplier
  
  // Calculate annual expenses based on zone defaults
  const annualExpenses = zoneData.commonExpenses.reduce((total, expense) => {
    const annualAmount = expense.frequency === 'monthly' 
      ? expense.amount * 12 
      : expense.frequency === 'quarterly' 
        ? expense.amount * 4 
        : expense.amount;
    return total + annualAmount;
  }, 0);
  
  // Spanish tax calculations
  const maxDeductibleAmount = estimatedPrice * 0.03; // Max 3% of property value
  const deductibleAmount = Math.min(annualExpenses, maxDeductibleAmount);
  const irpfRate = 0.21; // 21% IRPF rate for rental income
  const annualSavings = deductibleAmount * irpfRate;
  
  // Market comparison
  const marketComparison = monthlyRent > zoneData.avgRent 
    ? "por encima" 
    : monthlyRent < zoneData.avgRent 
      ? "por debajo" 
      : "en línea con";
  
  const percentage = Math.abs(((monthlyRent - zoneData.avgRent) / zoneData.avgRent) * 100);
  
  return {
    zone,
    annualSavings: Math.round(annualSavings),
    monthlyDeduction: Math.round(deductibleAmount / 12),
    irpfReduction: Math.round(annualSavings / 12),
    zoneComparison: `${percentage.toFixed(0)}% ${marketComparison} del mercado en ${zone}`,
    estimatedPrice,
    totalExpenses: annualExpenses,
    zoneData
  };
}

// Get smart defaults for property
export function getSmartDefaults(address: string, monthlyRent: number, propertyType?: string) {
  const zone = detectZoneFromAddress(address);
  const zoneData = ZONE_DATABASE[zone];
  
  // Find matching property type or use default
  const typeData = propertyType 
    ? zoneData.propertyTypes.find(t => t.type === propertyType) 
    : zoneData.propertyTypes[0]; // Default to first type (usually "Piso")
  
  return {
    zone,
    propertyType: typeData?.type || "Piso",
    rooms: typeData?.avgRooms || zoneData.avgRooms,
    m2: typeData?.avgM2 || zoneData.avgM2,
    estimatedPrice: typeData?.avgPrice || zoneData.avgPrice,
    expenses: zoneData.commonExpenses
  };
}

// Mock Google Maps API simulation
export async function searchAddresses(query: string): Promise<string[]> {
  if (query.length < 3) return [];
  
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 300));
  
  const cities = ['Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Bilbao', 'Málaga'];
  const streets = ['Gran Vía', 'Calle Mayor', 'Paseo de Gracia', 'Avenida Diagonal', 'Calle Alcalá'];
  
  const suggestions: string[] = [];
  
  // Add exact matches
  cities.forEach(city => {
    if (city.toLowerCase().includes(query.toLowerCase())) {
      suggestions.push(`${query}, ${city}, España`);
    }
  });
  
  // Add street suggestions
  streets.forEach(street => {
    if (street.toLowerCase().includes(query.toLowerCase()) || query.toLowerCase().includes(street.toLowerCase())) {
      cities.slice(0, 2).forEach(city => {
        suggestions.push(`${street} 1, ${city}, España`);
      });
    }
  });
  
  // Generic suggestions
  if (suggestions.length < 3) {
    cities.slice(0, 3).forEach(city => {
      suggestions.push(`${query}, ${city}, España`);
    });
  }
  
  return suggestions.slice(0, 5);
}