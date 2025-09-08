@echo off
echo Configurando para desarrollo local...
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
echo Configuración local restaurada
echo.
echo URLs locales:
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo.
echo Iniciando servidor...
npm run dev