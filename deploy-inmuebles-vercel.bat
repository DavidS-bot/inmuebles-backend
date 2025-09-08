@echo off
cls
echo.
echo ===============================================================
echo           🚀 INMUEBLES - DEPLOY DIRECTO A VERCEL
echo ===============================================================
echo.
echo Vamos a hacer el deploy de la forma mas simple posible!
echo.

cd inmuebles-web

echo [PASO 1] Limpiando proyecto...
if exist .git rmdir /s /q .git 2>nul
if exist .next rmdir /s /q .next 2>nul
if exist node_modules rmdir /s /q node_modules 2>nul
del nul 2>nul

echo [PASO 2] Instalando dependencias limpias...
npm install --silent

echo [PASO 3] Configurando Vercel...
echo {^
  "name": "inmuebles",^
  "framework": "nextjs",^
  "buildCommand": "npm run build",^
  "outputDirectory": ".next",^
  "installCommand": "npm install"^
} > vercel.json

echo [PASO 4] Haciendo deploy...
echo.
echo Si te pide login, usa tu email: 
echo Si te pregunta por configuracion, responde:
echo - Set up and deploy? Y
echo - Project name? inmuebles  
echo - Directory? (presiona Enter)
echo.
pause

vercel --prod --confirm

echo.
echo ===============================================================
echo                        ✅ COMPLETADO!
echo ===============================================================
echo.
echo Tu aplicacion web ya esta en Internet!
echo La URL aparece arriba.
echo.
pause