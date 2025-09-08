@echo off
echo.
echo === 🚂 Inmuebles - Deploy a Railway ===
echo.
echo Este script te guiara para poner tu web en Internet!
echo.

echo [PASO 1] Haciendo login en Railway...
echo Por favor, se abrira tu navegador para autenticarte.
railway login

echo.
echo [PASO 2] Creando nuevo proyecto en Railway...
railway init

echo.
echo [PASO 3] Vinculando con GitHub (opcional pero recomendado)...
echo Si tienes un repositorio en GitHub, Railway puede hacer deploy automatico.
railway link

echo.
echo [PASO 4] Configurando variables de entorno...
echo.

REM Generar JWT secret aleatorio
for /f %%i in ('powershell -Command "[System.Convert]::ToBase64String((1..32 | ForEach-Object {Get-Random -Maximum 256}))"') do set JWT_SECRET=%%i

echo Configurando variables...
railway variables set DATABASE_URL="railway proveera esto automaticamente"
railway variables set JWT_SECRET="%JWT_SECRET%"
railway variables set FRONTEND_URL="se configurara despues del deploy"
railway variables set CORS_ORIGINS="*"

echo.
echo [PASO 5] Desplegando aplicacion...
railway up

echo.
echo === ✅ Deploy Completado! ===
echo.
echo Tu aplicacion estara disponible en unos minutos en:
echo.
railway open

echo.
echo Para ver los logs:
echo railway logs
echo.
pause