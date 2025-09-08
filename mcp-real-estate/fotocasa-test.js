// fotocasa-test.js
const axios = require('axios');
const cheerio = require('cheerio');

async function testFotocasa() {
  try {
    console.log('Probando Fotocasa...');
    
    const url = 'https://www.fotocasa.es/es/comprar/viviendas/madrid-capital/todas-las-zonas/l';
    
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      timeout: 10000
    });
    
    console.log('✅ Fotocasa accesible!');
    console.log('Status:', response.status);
    
    const $ = cheerio.load(response.data);
    const title = $('title').text();
    console.log('Título:', title);
    
    // Buscar propiedades
    const properties = $('.fc-item').length || $('.re-Card').length;
    console.log('Propiedades encontradas:', properties);
    
    return { success: true, properties };
    
  } catch (error) {
    console.log('❌ Error con Fotocasa:', error.message);
    return { success: false };
  }
}

testFotocasa();