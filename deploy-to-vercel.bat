@echo off
echo.
echo === ▲ Inmuebles - Deploy Rapido a Internet con Vercel ===
echo.
echo Este deployment pondra tu web en Internet en 3 minutos!
echo.

echo [PASO 1] Preparando el frontend para Vercel...
cd inmuebles-web

echo.
echo [PASO 2] Creando archivo de configuracion...
echo {^
  "buildCommand": "npm run build",^
  "outputDirectory": ".next",^
  "framework": "nextjs",^
  "regions": ["iad1"],^
  "env": {^
    "NEXT_PUBLIC_API_URL": "@api_url",^
    "NEXTAUTH_SECRET": "@nextauth_secret"^
  }^
} > vercel.json

echo.
echo [PASO 3] Desplegando a Vercel...
echo Se abrira tu navegador para autenticarte si es necesario.
vercel --prod

echo.
echo === ✅ Frontend Desplegado! ===
echo.
echo Tu aplicacion web ya esta en Internet!
echo.
echo IMPORTANTE: Para el backend, puedes usar uno de estos servicios gratuitos:
echo 1. Supabase (https://supabase.com) - Base de datos PostgreSQL gratis
echo 2. Railway (https://railway.app) - Para el API backend
echo 3. Render (https://render.com) - Alternativa gratuita
echo.
echo La URL de tu web se mostro arriba (algo como: https://inmuebles-xxx.vercel.app)
echo.
cd ..
pause