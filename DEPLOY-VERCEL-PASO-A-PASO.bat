@echo off
cls
echo ================================================================================
echo                     🚀 INMUEBLES - DEPLOY A INTERNET CON VERCEL
echo ================================================================================
echo.
echo Este script te guiara paso a paso para poner tu web en Internet GRATIS!
echo.
echo --------------------------------------------------------------------------------
echo PASO 1: AUTENTICACION
echo --------------------------------------------------------------------------------
echo.
echo Primero necesitas autenticarte en Vercel.
echo Se abrira tu navegador para que hagas login.
echo.
echo Opciones recomendadas:
echo   1. Continue with GitHub (si tienes cuenta de GitHub)
echo   2. Continue with Email (mas sencillo)
echo.
pause
echo.
echo Ejecutando login...
vercel login
echo.
echo --------------------------------------------------------------------------------
echo PASO 2: CONFIGURACION DEL PROYECTO
echo --------------------------------------------------------------------------------
echo.
echo Ahora vamos a configurar tu proyecto.
echo.
cd inmuebles-web
echo.
echo Cuando te pregunte:
echo   - Set up and deploy: YES (Y)
echo   - Which scope: Selecciona tu cuenta personal
echo   - Link to existing project: NO (N)
echo   - Project name: inmuebles (o el nombre que prefieras)
echo   - Directory: ./ (presiona Enter)
echo   - Override settings: NO (N)
echo.
pause
echo.
echo --------------------------------------------------------------------------------
echo PASO 3: DEPLOYMENT
echo --------------------------------------------------------------------------------
echo.
vercel --prod
echo.
echo --------------------------------------------------------------------------------
echo ✅ DEPLOYMENT COMPLETADO!
echo --------------------------------------------------------------------------------
echo.
echo Tu aplicacion web ya esta en Internet!
echo.
echo La URL de tu aplicacion aparece arriba (algo como: https://inmuebles-xxx.vercel.app)
echo.
echo --------------------------------------------------------------------------------
echo SIGUIENTES PASOS:
echo --------------------------------------------------------------------------------
echo.
echo 1. Guarda la URL de tu aplicacion
echo 2. Para el backend (API y base de datos), opciones gratuitas:
echo    - Supabase.com (base de datos PostgreSQL gratis)
echo    - Railway.app (backend completo)
echo    - Render.com (alternativa gratuita)
echo.
echo 3. Actualiza las variables de entorno en Vercel:
echo    vercel env add NEXT_PUBLIC_API_URL
echo    (pon la URL de tu backend cuando lo tengas)
echo.
echo --------------------------------------------------------------------------------
echo.
cd ..
pause