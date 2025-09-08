@echo off
echo.
echo === 🏠 Inmuebles - Estado del Deployment ===
echo.

echo [INFO] Verificando contenedores...
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo [INFO] Verificando logs recientes...
docker compose -f docker-compose.prod.yml logs --tail=10

echo.
echo [INFO] URLs de acceso:
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📊 Documentacion API: http://localhost:8000/docs
echo.

pause