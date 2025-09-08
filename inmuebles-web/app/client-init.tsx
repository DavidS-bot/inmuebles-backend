"use client";
import { useEffect, useState } from "react";
import { loadTokenFromStorage } from "@/lib/auth";

// Hook para PWA - Fixed
function usePWA() {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);
  
  useEffect(() => {
    if (!mounted) return;
    // Registrar Service Worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js', { scope: '/' })
        .then((registration) => {
          console.log('SW registered: ', registration);
          
          // Verificar actualizaciones
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                  // Nueva versión disponible
                  if (confirm('Nueva versión disponible. ¿Actualizar ahora?')) {
                    newWorker.postMessage({ type: 'SKIP_WAITING' });
                    window.location.reload();
                  }
                }
              });
            }
          });
        })
        .catch((error) => {
          console.log('SW registration failed: ', error);
        });
    }

    // Detectar instalación PWA - DESHABILITADO
    let deferredPrompt: any;
    const installPromptHandler = (e: Event) => {
      e.preventDefault();
      deferredPrompt = e;
      // PWA install popup deshabilitado - no mostrar popup automático
    };

    window.addEventListener('beforeinstallprompt', installPromptHandler);

    // Detectar si ya está instalado
    if (window.matchMedia('(display-mode: standalone)').matches) {
      document.body.classList.add('pwa-installed');
    }

    // Manejo de conexión/desconexión
    const updateOnlineStatus = () => {
      if (navigator.onLine) {
        document.body.classList.remove('offline');
      } else {
        document.body.classList.add('offline');
      }
    };

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();

    return () => {
      window.removeEventListener('beforeinstallprompt', installPromptHandler);
      window.removeEventListener('online', updateOnlineStatus);
      window.removeEventListener('offline', updateOnlineStatus);
    };
  }, [mounted]);
}

export default function ClientInit() {
  usePWA(); // Inicializar PWA
  
  useEffect(() => { 
    loadTokenFromStorage(); 
  }, []);
  
  return null;
}

// Componente para botón de instalación manual - DESHABILITADO
function PWAInstallButton() {
  // PWA install button deshabilitado - no mostrar botón flotante
  return null;
}
