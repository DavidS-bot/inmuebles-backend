// Service Worker para Inmuebles PWA
const CACHE_NAME = 'inmuebles-v1.0.0';
const API_CACHE = 'inmuebles-api-v1.0.0';

// Archivos esenciales para cachear
const STATIC_CACHE_URLS = [
  '/',
  '/login',
  '/dashboard',
  '/financial-agent',
  '/offline',
  '/manifest.json',
  '/_next/static/css/app/layout.css',
  '/_next/static/chunks/webpack.js',
  '/_next/static/chunks/main.js'
];

// Archivos de API que queremos cachear
const API_CACHE_URLS = [
  '/api/properties',
  '/api/financial-movements',
  '/api/rental-contracts'
];

// Instalación del Service Worker
self.addEventListener('install', (event) => {
  console.log('[SW] Installing Service Worker...');
  
  event.waitUntil(
    Promise.all([
      // Cache estático
      caches.open(CACHE_NAME).then((cache) => {
        return cache.addAll(STATIC_CACHE_URLS.map(url => new Request(url, {
          cache: 'reload'
        })));
      }),
      // Cache API
      caches.open(API_CACHE).then((cache) => {
        return Promise.all(
          API_CACHE_URLS.map(url => 
            fetch(url)
              .then(response => {
                if (response.ok) {
                  cache.put(url, response.clone());
                }
                return response;
              })
              .catch(() => {
                // Ignorar errores durante la instalación
                console.log(`[SW] Could not cache API: ${url}`);
              })
          )
        );
      })
    ]).then(() => {
      // Forzar activación inmediata
      self.skipWaiting();
    })
  );
});

// Activación del Service Worker
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating Service Worker...');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName !== API_CACHE) {
            console.log('[SW] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      // Tomar control inmediato de todas las páginas
      return self.clients.claim();
    })
  );
});

// Interceptar peticiones
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Solo manejar peticiones del mismo origen
  if (url.origin !== location.origin) {
    return;
  }

  event.respondWith(
    handleRequest(request)
  );
});

async function handleRequest(request) {
  const url = new URL(request.url);
  
  // Estrategia para páginas HTML
  if (request.mode === 'navigate') {
    return handleNavigationRequest(request);
  }
  
  // Estrategia para API calls
  if (url.pathname.startsWith('/api/')) {
    return handleApiRequest(request);
  }
  
  // Estrategia para recursos estáticos
  return handleStaticRequest(request);
}

// Manejo de navegación (páginas HTML)
async function handleNavigationRequest(request) {
  try {
    // Intentar red primero
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cachear la respuesta exitosa
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
    
    throw new Error('Network response not ok');
  } catch (error) {
    console.log('[SW] Network failed, trying cache for navigation');
    
    // Buscar en cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Página offline como fallback
    const offlineResponse = await caches.match('/offline');
    return offlineResponse || new Response(
      '<h1>Sin conexión</h1><p>Por favor, verifica tu conexión a internet.</p>',
      { headers: { 'Content-Type': 'text/html' } }
    );
  }
}

// Manejo de peticiones API
async function handleApiRequest(request) {
  try {
    // Network First para datos críticos
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cachear solo GET requests exitosos
      if (request.method === 'GET') {
        const cache = await caches.open(API_CACHE);
        cache.put(request, networkResponse.clone());
      }
      return networkResponse;
    }
    
    throw new Error('API response not ok');
  } catch (error) {
    console.log('[SW] API network failed, trying cache');
    
    // Solo devolver cache para GET requests
    if (request.method === 'GET') {
      const cachedResponse = await caches.match(request);
      if (cachedResponse) {
        // Añadir header indicando que viene de cache
        const headers = new Headers(cachedResponse.headers);
        headers.set('X-From-Cache', 'true');
        
        return new Response(cachedResponse.body, {
          status: cachedResponse.status,
          statusText: cachedResponse.statusText,
          headers: headers
        });
      }
    }
    
    // Error response para métodos que no son GET
    return new Response(
      JSON.stringify({ 
        error: 'Sin conexión', 
        message: 'No se puede realizar esta operación sin conexión' 
      }),
      { 
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Manejo de recursos estáticos
async function handleStaticRequest(request) {
  // Cache First para recursos estáticos
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Static resource failed to load:', request.url);
    
    // Fallback para imágenes
    if (request.destination === 'image') {
      return new Response(
        '<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#f0f0f0"/><text x="50%" y="50%" text-anchor="middle" dy=".3em" font-family="sans-serif" font-size="14">Sin imagen</text></svg>',
        { headers: { 'Content-Type': 'image/svg+xml' } }
      );
    }
    
    return new Response('Recurso no disponible', { status: 404 });
  }
}

// Manejo de mensajes del cliente
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_NAME });
  }
});

// Sincronización en background
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(
      // Aquí podrías sincronizar datos pendientes
      syncPendingData()
    );
  }
});

async function syncPendingData() {
  // Implementar sincronización de datos pendientes
  console.log('[SW] Background sync triggered');
  
  try {
    // Ejemplo: subir fotos pendientes, sincronizar movimientos, etc.
    const pendingRequests = await getPendingRequests();
    
    for (const request of pendingRequests) {
      try {
        await fetch(request.url, request.options);
        await removePendingRequest(request.id);
      } catch (error) {
        console.log('[SW] Failed to sync request:', error);
      }
    }
  } catch (error) {
    console.log('[SW] Background sync failed:', error);
  }
}

// Funciones auxiliares para sincronización
async function getPendingRequests() {
  // Recuperar peticiones pendientes del IndexedDB
  return [];
}

async function removePendingRequest(id) {
  // Eliminar petición completada del IndexedDB
  console.log('[SW] Removing pending request:', id);
}