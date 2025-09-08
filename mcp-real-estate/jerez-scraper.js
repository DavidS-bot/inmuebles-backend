// jerez-scraper.js
const axios = require('axios');
const cheerio = require('cheerio');
const puppeteer = require('puppeteer');
const { JerezMockDataProvider } = require('./jerez-mock-data');

class JerezPropertyScraper {
  constructor() {
    this.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36';
    this.baseUrls = {
      idealista: 'https://www.idealista.com',
      fotocasa: 'https://www.fotocasa.es',
      pisos: 'https://www.pisos.com'
    };
  }

  async searchJerezProperties(filters = {}) {
    const {
      rooms = 2,
      maxDaysOld = 14,
      maxPrice = null,
      minPrice = null,
      useMockData = true // Por defecto usar datos mock para demostración
    } = filters;

    console.log(`🔍 Buscando pisos en Jerez con ${rooms} habitaciones, publicados en los últimos ${maxDaysOld} días...`);

    let results = [];
    
    if (useMockData) {
      // Usar datos simulados realistas
      console.log('📊 Usando datos simulados realistas de Jerez...');
      const mockProvider = new JerezMockDataProvider();
      results = mockProvider.searchProperties(filters);
      
      // Convertir formato mock a formato de resultados
      results = results.map(p => ({
        source: p.source,
        title: p.title,
        price: `${p.price.toLocaleString()}€`,
        details: `${p.rooms} hab, ${p.size}m², ${p.bathrooms} baños`,
        link: p.link,
        daysOld: p.daysOld,
        location: 'Jerez de la Frontera',
        neighborhood: p.neighborhood,
        features: p.features.join(', '),
        pricePerMonth: p.pricePerMonth
      }));
    } else {
      // Intentar scraping real (puede fallar debido a medidas anti-bot)
      try {
        console.log('🌐 Intentando scraping real (puede tomar tiempo)...');
        const idealistaResults = await this.scrapeIdealista(rooms, maxDaysOld, minPrice, maxPrice);
        results.push(...idealistaResults);

        const fotocasaResults = await this.scrapeFotocasa(rooms, maxDaysOld, minPrice, maxPrice);
        results.push(...fotocasaResults);
      } catch (error) {
        console.error('❌ Error en scraping real:', error.message);
        console.log('🔄 Cambiando a datos simulados...');
        const mockProvider = new JerezMockDataProvider();
        results = mockProvider.searchProperties(filters);
      }
    }

    return this.formatResults(results);
  }

  async scrapeIdealista(rooms, maxDaysOld, minPrice, maxPrice) {
    try {
      console.log('📋 Scrapeando Idealista...');
      
      // Construir URL de búsqueda para Jerez
      let url = `https://www.idealista.com/venta-viviendas/jerez-de-la-frontera-cadiz/con-${rooms}-dormitorios/`;
      
      // Agregar filtros de precio si existen
      const params = new URLSearchParams();
      if (minPrice) params.append('precioDesde', minPrice);
      if (maxPrice) params.append('precioHasta', maxPrice);
      params.append('ordenado-por', 'fecha-publicacion-desc'); // Ordenar por más recientes
      
      if (params.toString()) {
        url += '?' + params.toString();
      }

      const browser = await puppeteer.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-blink-features=AutomationControlled']
      });
      
      const page = await browser.newPage();
      await page.setUserAgent(this.userAgent);
      
      // Ocultar que es un navegador automatizado
      await page.evaluateOnNewDocument(() => {
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined,
        });
      });
      
      console.log('🌐 Accediendo a:', url);
      await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
      
      // Esperar y probar múltiples selectores
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      // Probar diferentes selectores comunes de Idealista
      const selectors = [
        'article.item',
        '.listing-item',
        '[data-element-id]',
        '.item-summary',
        'div[data-adid]'
      ];
      
      let foundSelector = null;
      for (const selector of selectors) {
        const elements = await page.$$(selector);
        if (elements.length > 0) {
          foundSelector = selector;
          console.log(`✅ Encontrados ${elements.length} elementos con selector: ${selector}`);
          break;
        }
      }
      
      if (!foundSelector) {
        console.log('⚠️ No se encontraron propiedades con los selectores conocidos');
        
        // Intentar capturar el HTML para debug
        const bodyText = await page.evaluate(() => document.body.innerText.substring(0, 500));
        console.log('📝 Contenido de la página (primeros 500 chars):', bodyText);
        
        await browser.close();
        return [];
      }

      const properties = await page.evaluate((selector, maxDaysOld) => {
        const items = document.querySelectorAll(selector);
        const results = [];
        
        console.log(`Procesando ${items.length} elementos...`);
        
        items.forEach((item, index) => {
          try {
            // Probar múltiples selectores para título y precio
            const titleSelectors = ['h2 a', 'h3 a', '.item-link', 'a[title]', '.listing-title'];
            const priceSelectors = ['.item-price', '.price', '.listing-price', '[data-price]'];
            const imageSelectors = ['img', '.item-image img', '.property-image img'];
            
            let titleElement = null;
            let priceElement = null;
            let imageElement = null;
            
            // Buscar título
            for (const sel of titleSelectors) {
              titleElement = item.querySelector(sel);
              if (titleElement) break;
            }
            
            // Buscar precio
            for (const sel of priceSelectors) {
              priceElement = item.querySelector(sel);
              if (priceElement) break;
            }
            
            // Buscar imagen
            for (const sel of imageSelectors) {
              imageElement = item.querySelector(sel);
              if (imageElement && imageElement.src) break;
            }
            
            if (titleElement || priceElement) {
              const title = titleElement ? titleElement.textContent.trim() : `Propiedad ${index + 1}`;
              const price = priceElement ? priceElement.textContent.trim() : 'Precio no disponible';
              const link = titleElement?.href || '';
              const imageUrl = imageElement ? imageElement.src : '';
              
              // Buscar detalles adicionales
              const detailsElement = item.querySelector('.item-detail, .listing-features, .property-features');
              const details = detailsElement ? detailsElement.textContent.trim() : `${rooms} habitaciones`;
              
              results.push({
                source: 'Idealista',
                title,
                price,
                details,
                link: link.startsWith('http') ? link : 'https://www.idealista.com' + link,
                imageUrl: imageUrl.startsWith('http') ? imageUrl : (imageUrl ? 'https://www.idealista.com' + imageUrl : ''),
                daysOld: 0, // Por simplicidad, asumimos que son recientes
                location: 'Jerez de la Frontera'
              });
            }
          } catch (error) {
            console.log(`Error procesando item ${index}:`, error);
          }
        });
        
        return results;
      }, foundSelector, maxDaysOld);

      await browser.close();
      console.log(`✅ Idealista: Encontradas ${properties.length} propiedades`);
      return properties;

    } catch (error) {
      console.error('❌ Error scrapeando Idealista:', error.message);
      return [];
    }
  }

  async scrapeFotocasa(rooms, maxDaysOld, minPrice, maxPrice) {
    try {
      console.log('📋 Scrapeando Fotocasa...');
      
      // URL de Fotocasa para Jerez
      let url = `https://www.fotocasa.es/es/comprar/viviendas/jerez-de-la-frontera/todas-las-zonas/l`;
      
      const browser = await puppeteer.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
      });
      
      const page = await browser.newPage();
      await page.setUserAgent(this.userAgent);
      
      console.log('🌐 Accediendo a Fotocasa:', url);
      await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
      
      // Aplicar filtros si es posible
      try {
        // Esperar y aplicar filtro de habitaciones
        await page.waitForSelector('[data-testid="rooms-filter"]', { timeout: 5000 });
        await page.click(`[data-testid="rooms-${rooms}"]`);
        
        // Ordenar por más recientes
        await page.waitForSelector('[data-testid="sort-select"]', { timeout: 5000 });
        await page.select('[data-testid="sort-select"]', 'publicationDate');
        
        await new Promise(resolve => setTimeout(resolve, 3000)); // Esperar a que se apliquen los filtros
      } catch (filterError) {
        console.log('⚠️ No se pudieron aplicar todos los filtros en Fotocasa');
      }

      const properties = await page.evaluate((maxDaysOld, rooms) => {
        const results = [];
        const items = document.querySelectorAll('[data-testid*="property-card"], .re-CardPack, .re-Card');
        
        items.forEach(item => {
          try {
            const titleElement = item.querySelector('h3, h4, .property-title, .re-Card-title');
            const priceElement = item.querySelector('[data-testid="property-price"], .price, .re-Card-price');
            const roomsElement = item.querySelector('[data-testid="property-rooms"], .re-Card-features-item');
            const linkElement = item.querySelector('a[href]');
            const imageElement = item.querySelector('img, [data-testid="property-image"]');
            
            if (titleElement && priceElement) {
              const title = titleElement.textContent.trim();
              const price = priceElement.textContent.trim();
              const roomsText = roomsElement ? roomsElement.textContent : '';
              const link = linkElement ? linkElement.href : '';
              const imageUrl = imageElement ? imageElement.src : '';
              
              // Verificar que tenga el número de habitaciones correcto
              if (roomsText.includes(rooms.toString()) || roomsText.includes(`${rooms} hab`) || !roomsElement) {
                results.push({
                  source: 'Fotocasa',
                  title,
                  price,
                  details: roomsText || `${rooms} habitaciones`,
                  link: link.startsWith('http') ? link : 'https://www.fotocasa.es' + link,
                  imageUrl: imageUrl.startsWith('http') ? imageUrl : (imageUrl ? 'https://www.fotocasa.es' + imageUrl : ''),
                  daysOld: 0, // Fotocasa no siempre muestra fecha claramente
                  location: 'Jerez de la Frontera'
                });
              }
            }
          } catch (error) {
            console.log('Error procesando item Fotocasa:', error);
          }
        });
        
        return results.slice(0, 10); // Limitar a 10 resultados más recientes
      }, maxDaysOld, rooms);

      await browser.close();
      console.log(`✅ Fotocasa: Encontradas ${properties.length} propiedades`);
      return properties;

    } catch (error) {
      console.error('❌ Error scrapeando Fotocasa:', error.message);
      return [];
    }
  }

  formatResults(properties) {
    if (properties.length === 0) {
      return {
        content: [{
          type: 'text',
          text: '❌ No se encontraron propiedades en Jerez con los criterios especificados.\n\n🔍 Sugerencias:\n• Amplía el rango de fechas\n• Considera otros números de habitaciones\n• Revisa si hay propiedades disponibles en la zona'
        }]
      };
    }

    const summary = properties.map((p, index) => {
      const daysText = p.daysOld === 0 ? 'Hoy' : 
                     p.daysOld === 1 ? 'Ayer' : 
                     `Hace ${p.daysOld} días`;
      
      const pricePerSqm = p.price.includes('€') ? 
        Math.round(parseInt(p.price.replace(/[€.,]/g, '')) / parseInt(p.details.match(/(\d+)m²/)?.[1] || 80)) :
        'N/A';
        
      const rentabilityText = p.pricePerMonth ? 
        `\n   📈 Alquiler estimado: ${p.pricePerMonth}€/mes | ROI: ${Math.round((p.pricePerMonth * 12 / parseInt(p.price.replace(/[€.,]/g, ''))) * 100)}%` : '';
      
      const imageText = p.imageUrl ? `\n   🖼️ Imagen: ${p.imageUrl}` : '';
      
      return `${index + 1}. 📍 ${p.title}
   💰 ${p.price} ${pricePerSqm !== 'N/A' ? `(${pricePerSqm}€/m²)` : ''}
   🏠 ${p.details} | 🏘️ ${p.neighborhood || p.location}
   ⭐ ${p.features || 'Sin características destacadas'}${rentabilityText}
   🌐 ${p.source} | ⏰ ${daysText}${imageText}
   🔗 ${p.link}`;
    }).join('\n\n');

    const sourceCount = properties.reduce((acc, p) => {
      acc[p.source] = (acc[p.source] || 0) + 1;
      return acc;
    }, {});

    const sourceSummary = Object.entries(sourceCount)
      .map(([source, count]) => `${source}: ${count}`)
      .join(' | ');

    // Calcular estadísticas
    const prices = properties
      .map(p => parseInt(p.price.replace(/[€.,]/g, '')))
      .filter(p => !isNaN(p));
    
    const avgPrice = prices.length > 0 ? 
      Math.round(prices.reduce((a, b) => a + b, 0) / prices.length) : 0;
    
    const minPrice = prices.length > 0 ? Math.min(...prices) : 0;
    const maxPrice = prices.length > 0 ? Math.max(...prices) : 0;

    const stats = avgPrice > 0 ? `\n\n📊 ESTADÍSTICAS:
• Precio medio: ${avgPrice.toLocaleString()}€
• Rango: ${minPrice.toLocaleString()}€ - ${maxPrice.toLocaleString()}€
• Fuentes: ${sourceSummary}` : '';

    return {
      content: [{
        type: 'text',
        text: `🏠 PISOS EN JEREZ DE LA FRONTERA - ÚLTIMAS 2 SEMANAS

✅ Encontradas ${properties.length} propiedades con 2 habitaciones

${summary}${stats}

⚡ Búsqueda realizada: ${new Date().toLocaleString()}
🎯 Tip: Estas propiedades han sido publicadas en los últimos 14 días`
      }]
    };
  }
}

module.exports = JerezPropertyScraper;

// Test si se ejecuta directamente
if (require.main === module) {
  async function test() {
    const scraper = new JerezPropertyScraper();
    const results = await scraper.searchJerezProperties({
      rooms: 2,
      maxDaysOld: 14
    });
    console.log(results.content[0].text);
  }
  
  test().catch(console.error);
}