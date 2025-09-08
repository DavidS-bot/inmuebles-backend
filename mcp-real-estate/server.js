// server.js
const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');

// Crear servidor
const server = new Server(
  {
    name: 'real-estate-scraper',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Registrar handler para listar herramientas
server.setRequestHandler('tools/list', async () => {
  return {
    tools: [
      {
        name: 'test_connection',
        description: 'Prueba básica de conexión',
        inputSchema: {
          type: 'object',
          properties: {
            message: {
              type: 'string',
              description: 'Mensaje de prueba',
            },
          },
        },
      },
    ],
  };
});

// Registrar handler para ejecutar herramientas
server.setRequestHandler('tools/call', async (request) => {
  if (request.params.name === 'test_connection') {
    const message = request.params.arguments?.message || 'Sin mensaje';
    return {
      content: [
        {
          type: 'text',
          text: `¡Servidor MCP funcionando! Mensaje: ${message}`,
        },
      ],
    };
  }
  
  throw new Error(`Herramienta no encontrada: ${request.params.name}`);
});

// Iniciar servidor
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error('Error:', error);
  process.exit(1);
});