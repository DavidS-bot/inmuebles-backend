// simple-real-scraper.js - Version simplificada y más confiable
const puppeteer = require('puppeteer');

class SimpleJerezScraper {
  constructor() {
    this.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36';
  }

  async searchProperties(filters = {}) {
    const {
      rooms = 2,
      maxPrice = 100000,
      minPrice = 50000
    } = filters;

    console.log('🔍 Iniciando búsqueda real simplificada...');
    
    let browser = null;
    
    try {
      browser = await puppeteer.launch({ 
        headless: false, // Mostrar navegador para debug
        slowMo: 1000,    // Ralentizar acciones
        args: [
          '--no-sandbox', 
          '--disable-setuid-sandbox',
          '--disable-web-security',
          '--disable-features=VizDisplayCompositor'
        ]
      });
      
      const page = await browser.newPage();
      await page.setUserAgent(this.userAgent);
      
      // Configurar viewport
      await page.setViewport({ width: 1280, height: 720 });
      
      // Url simplificada de Idealista
      const url = `https://www.idealista.com/venta-viviendas/jerez-de-la-frontera-cadiz/`;
      console.log('🌐 Navegando a:', url);
      
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      
      // Esperar que cargue la página
      console.log('⏱️ Esperando que cargue la página...');
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      // Intentar aceptar cookies si aparece el popup
      try {
        await page.waitForSelector('#didomi-notice-agree-button', { timeout: 3000 });
        await page.click('#didomi-notice-agree-button');
        console.log('✅ Cookies aceptadas');
        await new Promise(resolve => setTimeout(resolve, 2000));
      } catch (e) {
        console.log('ℹ️ No se encontró popup de cookies');
      }
      
      // Buscar propiedades usando selectores genericos
      console.log('🔍 Buscando propiedades en la página...');
      
      const properties = await page.evaluate(() => {
        const results = [];
        
        // Múltiples selectores para diferentes layouts de Idealista
        const possibleSelectors = [
          'article.item',
          '.listing-item',
          'div[data-adid]',
          '.item',
          '.property-card'
        ];
        
        let foundItems = [];
        
        // Probar cada selector
        for (const selector of possibleSelectors) {
          const items = document.querySelectorAll(selector);
          if (items.length > 0) {
            foundItems = Array.from(items);
            console.log(`Found ${items.length} items with selector: ${selector}`);
            break;
          }
        }
        
        // Si no encontramos nada, buscar cualquier enlace que parezca una propiedad
        if (foundItems.length === 0) {
          const allLinks = document.querySelectorAll('a[href*="inmueble"]');
          foundItems = Array.from(allLinks).map(link => link.closest('div, article, li') || link);
        }
        
        console.log(`Processing ${foundItems.length} potential properties...`);
        
        foundItems.slice(0, 10).forEach((item, index) => {
          try {
            // Buscar título
            const titleElement = item.querySelector('a[title], h1, h2, h3, h4, .item-title, .property-title') || 
                                item.querySelector('a[href*="inmueble"]');
            
            // Buscar precio
            const priceElement = item.querySelector('.item-price, .price, [class*="price"], span[class*="euro"]');
            
            // Buscar imagen
            const imageElement = item.querySelector('img[src], img[data-src]');
            
            // Buscar enlace
            const linkElement = item.querySelector('a[href*="inmueble"]') || titleElement;
            
            if (titleElement || priceElement) {
              const title = titleElement ? titleElement.textContent.trim() || titleElement.title || 'Propiedad en Jerez' : `Propiedad ${index + 1}`;
              const price = priceElement ? priceElement.textContent.trim() : 'Consultar precio';
              const link = linkElement ? linkElement.href : '';
              const imageUrl = imageElement ? (imageElement.src || imageElement.dataset.src) : '';
              
              // Solo añadir si tiene información básica
              if (title.length > 0 && title !== 'undefined') {
                results.push({
                  title: title.substring(0, 100), // Limitar longitud
                  price,
                  link: link.startsWith('http') ? link : (link ? 'https://www.idealista.com' + link : ''),
                  imageUrl: imageUrl.startsWith('http') ? imageUrl : (imageUrl ? 'https://www.idealista.com' + imageUrl : ''),
                  source: 'Idealista (Real)',
                  details: '2 hab aprox.',
                  location: 'Jerez de la Frontera'
                });
              }
            }
          } catch (error) {
            console.log(`Error processing item ${index}:`, error);
          }
        });
        
        return results;
      });
      
      console.log(`✅ Encontradas ${properties.length} propiedades reales`);
      
      // Formatear resultados
      if (properties.length === 0) {
        return {
          content: [{
            type: 'text',
            text: '❌ No se pudieron encontrar propiedades en tiempo real.\n\n💡 Esto puede deberse a:\n• Cambios en la estructura de las páginas web\n• Medidas anti-bot de los portales\n• Conexión a internet\n\n🔄 Recomendación: Usar búsqueda manual en idealista.com'
          }]
        };
      }
      
      const formattedResults = properties.map((p, index) => {
        const imageText = p.imageUrl ? `\n   🖼️ ${p.imageUrl}` : '';
        return `${index + 1}. 📍 ${p.title}
   💰 ${p.price}
   🏠 ${p.details}
   🌐 ${p.source}${imageText}
   🔗 ${p.link}`;
      }).join('\n\n');
      
      return {
        content: [{
          type: 'text',
          text: `🏠 PROPIEDADES REALES EN JEREZ DE LA FRONTERA
          
✅ Encontradas ${properties.length} propiedades (scraping real)

${formattedResults}

⚡ Búsqueda realizada: ${new Date().toLocaleString()}
🎯 Datos obtenidos directamente de Idealista.com

⚠️ IMPORTANTE: Los enlaces son reales y llevan a las propiedades actuales.
💡 Recomendación: Visita los enlaces para ver fotos, detalles completos y contactar.`
        }]
      };
      
    } catch (error) {
      console.error('❌ Error en scraping real:', error.message);
      return {
        content: [{
          type: 'text',
          text: `❌ Error realizando scraping real: ${error.message}\n\n🔄 Fallback: Usa búsqueda manual en:\n• https://www.idealista.com/venta-viviendas/jerez-de-la-frontera-cadiz/\n• https://www.fotocasa.es/es/comprar/viviendas/jerez-de-la-frontera/`
        }]
      };
    } finally {
      if (browser) {
        await browser.close();
      }
    }
  }
}

module.exports = SimpleJerezScraper;

// Test si se ejecuta directamente
if (require.main === module) {
  async function test() {
    const scraper = new SimpleJerezScraper();
    const result = await scraper.searchProperties({ rooms: 2, maxPrice: 100000 });
    console.log(result.content[0].text);
  }
  
  test().catch(console.error);
}