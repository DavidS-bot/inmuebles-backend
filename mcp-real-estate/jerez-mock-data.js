// jerez-mock-data.js - Datos simulados realistas de propiedades en Jerez

const mockJerezProperties = [
  {
    id: 'jerez_001',
    title: 'Piso en Centro histórico, Jerez de la Frontera',
    address: 'Calle Larga, 45, Jerez de la Frontera',
    price: 89000,
    pricePerMonth: 850, // alquiler estimado
    size: 75,
    rooms: 2,
    bathrooms: 1,
    type: 'apartment',
    neighborhood: 'Centro Histórico',
    daysOld: 3,
    source: 'Idealista',
    link: 'https://www.idealista.com/inmueble/mock001',
    features: ['Balcón', 'Calefacción', 'Ascensor'],
    description: 'Piso reformado en el corazón de Jerez, cerca de la Catedral y zona comercial.',
    images: 12,
    publishedDate: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  },
  {
    id: 'jerez_002',
    title: 'Apartamento moderno zona Universidad',
    address: 'Avenida de Europa, 123, Jerez de la Frontera',
    price: 95000,
    pricePerMonth: 900,
    size: 68,
    rooms: 2,
    bathrooms: 2,
    type: 'apartment',
    neighborhood: 'Zona Universidad',
    daysOld: 1,
    source: 'Fotocasa',
    link: 'https://www.fotocasa.es/inmueble/mock002',
    features: ['Aire acondicionado', 'Parking', 'Terraza'],
    description: 'Apartamento recién reformado cerca del campus universitario.',
    images: 8,
    publishedDate: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  },
  {
    id: 'jerez_003',
    title: 'Piso luminoso en Barrio de Santiago',
    address: 'Calle Santiago, 78, Jerez de la Frontera',
    price: 72000,
    pricePerMonth: 750,
    size: 82,
    rooms: 2,
    bathrooms: 1,
    type: 'apartment',
    neighborhood: 'Barrio de Santiago',
    daysOld: 7,
    source: 'Idealista',
    link: 'https://www.idealista.com/inmueble/mock003',
    features: ['Patio', 'Calefacción', 'Reformado'],
    description: 'Piso con mucha luz natural y patio interior en barrio tradicional.',
    images: 15,
    publishedDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  },
  {
    id: 'jerez_004',
    title: 'Dúplex en Zona Norte con garaje',
    address: 'Calle Cartuja, 156, Jerez de la Frontera',
    price: 125000,
    pricePerMonth: 1100,
    size: 95,
    rooms: 2,
    bathrooms: 2,
    type: 'duplex',
    neighborhood: 'Zona Norte',
    daysOld: 5,
    source: 'Pisos.com',
    link: 'https://www.pisos.com/inmueble/mock004',
    features: ['Garaje incluido', 'Trastero', 'Jardín comunitario'],
    description: 'Dúplex moderno con garaje y trastero incluidos.',
    images: 20,
    publishedDate: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  },
  {
    id: 'jerez_005',
    title: 'Piso económico para reformar',
    address: 'Calle Porvera, 23, Jerez de la Frontera',
    price: 58000,
    pricePerMonth: 650,
    size: 70,
    rooms: 2,
    bathrooms: 1,
    type: 'apartment',
    neighborhood: 'Porvera',
    daysOld: 12,
    source: 'Fotocasa',
    link: 'https://www.fotocasa.es/inmueble/mock005',
    features: ['Para reformar', 'Bien comunicado', 'Precio negociable'],
    description: 'Piso con potencial para inversores, necesita reforma completa.',
    images: 6,
    publishedDate: new Date(Date.now() - 12 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  },
  {
    id: 'jerez_006',
    title: 'Moderno apartamento Zona Comercial',
    address: 'Calle Consistorio, 89, Jerez de la Frontera',
    price: 105000,
    pricePerMonth: 950,
    size: 78,
    rooms: 2,
    bathrooms: 2,
    type: 'apartment',
    neighborhood: 'Zona Comercial',
    daysOld: 2,
    source: 'Idealista',
    link: 'https://www.idealista.com/inmueble/mock006',
    features: ['Recién reformado', 'Aire acondicionado', 'Céntrico'],
    description: 'Apartamento completamente reformado en zona comercial.',
    images: 18,
    publishedDate: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  },
  {
    id: 'jerez_007',
    title: 'Piso con terraza en La Plata',
    address: 'Calle La Plata, 67, Jerez de la Frontera',
    price: 88000,
    pricePerMonth: 825,
    size: 80,
    rooms: 2,
    bathrooms: 1,
    type: 'apartment',
    neighborhood: 'La Plata',
    daysOld: 9,
    source: 'Pisos.com',
    link: 'https://www.pisos.com/inmueble/mock007',
    features: ['Terraza 15m²', 'Vistas despejadas', 'Ascensor'],
    description: 'Piso con gran terraza y vistas despejadas a la ciudad.',
    images: 11,
    publishedDate: new Date(Date.now() - 9 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  },
  {
    id: 'jerez_008',
    title: 'Apartamento nuevo construcción',
    address: 'Urbanización Los Álamos, Jerez de la Frontera',
    price: 135000,
    pricePerMonth: 1200,
    size: 85,
    rooms: 2,
    bathrooms: 2,
    type: 'apartment',
    neighborhood: 'Los Álamos',
    daysOld: 6,
    source: 'Fotocasa',
    link: 'https://www.fotocasa.es/inmueble/mock008',
    features: ['Obra nueva', 'Piscina comunitaria', 'Parking'],
    description: 'Apartamento en urbanización nueva con todas las comodidades.',
    images: 25,
    publishedDate: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  }
];

class JerezMockDataProvider {
  constructor() {
    this.properties = mockJerezProperties;
  }

  searchProperties(filters = {}) {
    const {
      rooms = 2,
      maxDaysOld = 14,
      maxPrice = null,
      minPrice = null,
      neighborhood = null
    } = filters;

    let results = [...this.properties];

    // Filtrar por habitaciones
    if (rooms) {
      results = results.filter(p => p.rooms === rooms);
    }

    // Filtrar por días de antigüedad
    if (maxDaysOld) {
      results = results.filter(p => p.daysOld <= maxDaysOld);
    }

    // Filtrar por precio máximo
    if (maxPrice) {
      results = results.filter(p => p.price <= maxPrice);
    }

    // Filtrar por precio mínimo
    if (minPrice) {
      results = results.filter(p => p.price >= minPrice);
    }

    // Filtrar por barrio
    if (neighborhood) {
      results = results.filter(p => 
        p.neighborhood.toLowerCase().includes(neighborhood.toLowerCase())
      );
    }

    // Ordenar por fecha de publicación (más recientes primero)
    results.sort((a, b) => a.daysOld - b.daysOld);

    return results;
  }

  getPropertyById(id) {
    return this.properties.find(p => p.id === id);
  }

  getNeighborhoods() {
    const neighborhoods = [...new Set(this.properties.map(p => p.neighborhood))];
    return neighborhoods.sort();
  }

  getPriceStats() {
    const prices = this.properties.map(p => p.price);
    return {
      min: Math.min(...prices),
      max: Math.max(...prices),
      avg: Math.round(prices.reduce((a, b) => a + b, 0) / prices.length),
      count: prices.length
    };
  }
}

module.exports = { JerezMockDataProvider, mockJerezProperties };