// scraper.js
const axios = require('axios');
const cheerio = require('cheerio');

async function testScraping() {
  try {
    console.log('Probando web scraping básico...');
    
    // Vamos a probar con una página simple primero
    const response = await axios.get('https://httpbin.org/html', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; PropertyAnalyzer/1.0)'
      }
    });
    
    console.log('✅ Request exitoso!');
    console.log('Status:', response.status);
    console.log('Contenido recibido:', response.data.length, 'caracteres');
    
    // Parsear HTML
    const $ = cheerio.load(response.data);
    const title = $('title').text();
    console.log('✅ HTML parseado!');
    console.log('Título encontrado:', title);
    
    return { success: true, title };
    
  } catch (error) {
    console.error('❌ Error en scraping:', error.message);
    return { success: false, error: error.message };
  }
}

// Probar
testScraping().then(result => {
  console.log('Resultado final:', result);
  process.exit(0);
});