@echo off
echo Configurando para desarrollo móvil...
copy .env.mobile .env.local
echo NEXT_PUBLIC_API_URL=http://192.168.1.39:8000 se ha configurado
echo.
echo URLs para móvil:
echo Frontend: http://192.168.1.39:3000
echo Backend:  http://192.168.1.39:8000
echo.
echo Iniciando servidor...
npm run dev