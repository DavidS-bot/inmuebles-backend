"use client";
import { useEffect, useState } from "react";
import { loadTokenFromStorage } from "@/lib/auth";

// Hook para PWA
function usePWA() {
  useEffect(() => {
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

    // Detectar instalación PWA
    let deferredPrompt: any;
    const installPromptHandler = (e: Event) => {
      e.preventDefault();
      deferredPrompt = e;
      
      // Mostrar botón de instalación después de un tiempo
      setTimeout(() => {
        const shouldShow = !localStorage.getItem('pwa-install-dismissed') &&
                          !window.matchMedia('(display-mode: standalone)').matches;
        
        if (shouldShow && confirm('¿Quieres instalar Inmuebles como una app en tu dispositivo?')) {
          deferredPrompt.prompt();
          deferredPrompt.userChoice.then((choiceResult: any) => {
            if (choiceResult.outcome === 'dismissed') {
              localStorage.setItem('pwa-install-dismissed', 'true');
            }
            deferredPrompt = null;
          });
        }
      }, 5000);
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
  }, []);
}

export default function ClientInit() {
  usePWA(); // Inicializar PWA
  
  useEffect(() => { 
    loadTokenFromStorage(); 
  }, []);
  
  return (
    <PWAInstallButton />
  );
}

// Componente para botón de instalación manual
function PWAInstallButton() {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [showButton, setShowButton] = useState(false);

  useEffect(() => {
    const handler = (e: any) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowButton(true);
    };

    window.addEventListener('beforeinstallprompt', handler);
    
    // Mostrar botón después de 10 segundos si no está instalado
    const timer = setTimeout(() => {
      if (!window.matchMedia('(display-mode: standalone)').matches) {
        setShowButton(true);
      }
    }, 10000);

    return () => {
      window.removeEventListener('beforeinstallprompt', handler);
      clearTimeout(timer);
    };
  }, []);

  const handleInstall = () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then((choiceResult: any) => {
        setDeferredPrompt(null);
        setShowButton(false);
      });
    } else {
      // Fallback manual
      alert('Para instalar como app:\n\n📱 Android: Menú ⋮ → "Instalar app"\n🍎 iPhone: Compartir 📤 → "Añadir a pantalla de inicio"');
    }
  };

  if (!showButton) return null;

  return (
    <div 
      onClick={handleInstall}
      style={{
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        zIndex: 1000,
        backgroundColor: '#14b8a6',
        color: 'white',
        padding: '12px 20px',
        borderRadius: '25px',
        fontSize: '14px',
        fontWeight: 'bold',
        cursor: 'pointer',
        boxShadow: '0 4px 12px rgba(52, 152, 219, 0.3)',
      }}
    >
      📱 Instalar App
    </div>
  );
}
