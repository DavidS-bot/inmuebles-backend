@echo off
echo === 🏠 Inmuebles - Deploy Automatico ===
echo.

REM Verificar que estamos en el directorio correcto
if not exist "docker-compose.prod.yml" (
    echo [ERROR] No se encuentra docker-compose.prod.yml
    echo         Ejecuta desde el directorio backend/
    pause
    exit /b 1
)

echo [INFO] Iniciando deploy de Inmuebles...

REM Verificar Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no esta instalado
    echo         Descarga desde https://docker.com/get-started
    pause
    exit /b 1
)

REM Crear archivo .env si no existe
if not exist ".env" (
    echo [WARN] Creando archivo .env...
    (
        echo # Base de datos
        echo DATABASE_URL=postgresql://postgres:inmuebles_2024_secure@db:5432/inmuebles_prod
        echo POSTGRES_USER=postgres
        echo POSTGRES_PASSWORD=inmuebles_2024_secure
        echo POSTGRES_DB=inmuebles_prod
        echo.
        echo # Autenticacion
        echo NEXTAUTH_SECRET=clave_secreta_muy_larga_y_segura_cambia_esto
        echo NEXTAUTH_URL=http://localhost
        echo NEXT_PUBLIC_API_URL=http://localhost:8000
        echo.
        echo # JWT
        echo JWT_SECRET_KEY=otra_clave_secreta_jwt_cambia_esto
        echo JWT_ALGORITHM=HS256
        echo ACCESS_TOKEN_EXPIRE_MINUTES=30
        echo.
        echo # CORS
        echo ALLOWED_ORIGINS=["http://localhost:3000","http://localhost"]
    ) > .env
    echo [INFO] Archivo .env creado
)

REM Construir aplicacion
echo [INFO] Construyendo aplicacion...
docker-compose -f docker-compose.prod.yml build
if errorlevel 1 (
    echo [ERROR] Error en el build
    pause
    exit /b 1
)
echo [INFO] ✅ Build completado

REM Lanzar servicios
echo [INFO] Lanzando servicios...
docker-compose -f docker-compose.prod.yml up -d
if errorlevel 1 (
    echo [ERROR] Error lanzando servicios  
    pause
    exit /b 1
)
echo [INFO] ✅ Servicios lanzados

REM Esperar a que servicios esten listos
echo [INFO] Esperando a que los servicios esten listos...
timeout /t 10 /nobreak >nul

REM Mostrar estado
echo [INFO] Estado de los servicios:
docker-compose -f docker-compose.prod.yml ps

echo.
echo === 🎉 Deploy Completado ===
echo.
echo [INFO] Tu aplicacion esta disponible en:
echo         📱 App/Web: http://localhost
echo         🔧 API:     http://localhost:8000
echo         📊 Docs:    http://localhost:8000/docs
echo.
echo [INFO] Para usar con dominio propio:
echo         1. Configura tu dominio para apuntar a la IP del servidor
echo         2. Actualiza NEXTAUTH_URL y NEXT_PUBLIC_API_URL en .env  
echo         3. Ejecuta: docker-compose -f docker-compose.prod.yml restart
echo.
echo [INFO] Comandos utiles:
echo         Ver logs:     docker-compose -f docker-compose.prod.yml logs -f
echo         Parar app:    docker-compose -f docker-compose.prod.yml down
echo         Reiniciar:    docker-compose -f docker-compose.prod.yml restart
echo.
echo [INFO] ¡Listo! 🚀
echo.
pause