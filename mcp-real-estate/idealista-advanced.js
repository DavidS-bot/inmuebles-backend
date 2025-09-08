// idealista-advanced.js
const axios = require('axios');
const cheerio = require('cheerio');

async function testIdealistaAdvanced() {
  try {
    console.log('Probando Idealista con headers avanzados...');
    
    const url = 'https://www.idealista.com/venta-viviendas/madrid/';
    
    // Headers más realistas
    const headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
      'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
      'Accept-Encoding': 'gzip, deflate, br',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Sec-Fetch-Dest': 'document',
      'Sec-Fetch-Mode': 'navigate',
      'Sec-Fetch-Site': 'none',
      'Cache-Control': 'max-age=0'
    };
    
    const response = await axios.get(url, {
      headers,
      timeout: 15000,
      maxRedirects: 5
    });
    
    console.log('✅ ¡Idealista accesible!');
    console.log('Status:', response.status);
    console.log('Tamaño de respuesta:', response.data.length);
    
    const $ = cheerio.load(response.data);
    const title = $('title').text();
    console.log('Título:', title);
    
    return { success: true };
    
  } catch (error) {
    console.log('❌ Aún con error:', error.message);
    if (error.response) {
      console.log('Status:', error.response.status);
    }
    return { success: false, error: error.message };
  }
}

testIdealistaAdvanced();