// idealista-test.js
const axios = require('axios');
const cheerio = require('cheerio');

async function testIdealista() {
  try {
    console.log('Probando acceso a Idealista...');
    
    // URL de búsqueda simple en Madrid
    const url = 'https://www.idealista.com/venta-viviendas/madrid/';
    
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      timeout: 10000
    });
    
    console.log('✅ Conexión a Idealista exitosa!');
    console.log('Status:', response.status);
    
    const $ = cheerio.load(response.data);
    
    // Buscar elementos básicos
    const title = $('title').text();
    console.log('Título de página:', title);
    
    // Intentar encontrar propiedades (esto puede variar)
    const properties = $('.item').length;
    console.log('Elementos .item encontrados:', properties);
    
    return { success: true, properties };
    
  } catch (error) {
    console.error('❌ Error accediendo a Idealista:', error.message);
    
    if (error.response) {
      console.log('Status de respuesta:', error.response.status);
    }
    
    return { success: false, error: error.message };
  }
}

testIdealista().then(result => {
  console.log('Resultado:', result);
  process.exit(0);
});