#!/bin/bash

# 🚀 Script de Deploy Automático - Inmuebles App
echo "=== 🏠 Inmuebles - Deploy Automático ==="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.prod.yml" ]; then
    error "No se encuentra docker-compose.prod.yml. Ejecuta desde el directorio backend/"
    exit 1
fi

log "Iniciando deploy de Inmuebles..."

# Paso 1: Verificar Docker
if ! command -v docker &> /dev/null; then
    error "Docker no está instalado. Instálalo primero:"
    echo "curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
    exit 1
fi

# Paso 2: Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    warn "Creando archivo .env..."
    cat > .env << EOF
# Base de datos
DATABASE_URL=postgresql://postgres:inmuebles_2024_secure@db:5432/inmuebles_prod
POSTGRES_USER=postgres
POSTGRES_PASSWORD=inmuebles_2024_secure
POSTGRES_DB=inmuebles_prod

# Autenticación
NEXTAUTH_SECRET=$(openssl rand -base64 32)
NEXTAUTH_URL=http://localhost
NEXT_PUBLIC_API_URL=http://localhost:8000

# JWT
JWT_SECRET_KEY=$(openssl rand -base64 32)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost"]
EOF
    log "Archivo .env creado. Revisa y modifica las variables según tu configuración."
fi

# Paso 3: Construir y lanzar contenedores
log "Construyendo aplicación..."
if docker-compose -f docker-compose.prod.yml build; then
    log "✅ Build completado exitosamente"
else
    error "❌ Error en el build"
    exit 1
fi

log "Lanzando servicios..."
if docker-compose -f docker-compose.prod.yml up -d; then
    log "✅ Servicios lanzados exitosamente"
else
    error "❌ Error lanzando servicios"
    exit 1
fi

# Paso 4: Esperar a que los servicios estén listos
log "Esperando a que los servicios estén listos..."
sleep 10

# Paso 5: Verificar estado de los contenedores
log "Estado de los servicios:"
docker-compose -f docker-compose.prod.yml ps

# Paso 6: Ejecutar migraciones de base de datos
log "Ejecutando migraciones de base de datos..."
sleep 5
docker-compose -f docker-compose.prod.yml exec -T api python -c "
from app.db import engine, Base
Base.metadata.create_all(bind=engine)
print('✅ Migraciones ejecutadas')
" 2>/dev/null || warn "No se pudieron ejecutar las migraciones automáticamente"

# Paso 7: Verificar que la app funciona
log "Verificando que la aplicación funciona..."

# Verificar API
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 | grep -q "200\|404"; then
    log "✅ API funcionando en http://localhost:8000"
else
    warn "⚠️  API no responde en http://localhost:8000"
fi

# Verificar Frontend
sleep 2
if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200"; then
    log "✅ Frontend funcionando en http://localhost"
else
    warn "⚠️  Frontend no responde en http://localhost"
fi

echo
echo -e "${BLUE}=== 🎉 Deploy Completado ===${NC}"
echo
log "Tu aplicación está disponible en:"
echo "  📱 App/Web: http://localhost"
echo "  🔧 API:     http://localhost:8000" 
echo "  📊 Docs:    http://localhost:8000/docs"
echo
log "Para usar con dominio propio:"
echo "  1. Configura tu dominio para apuntar a la IP del servidor"
echo "  2. Actualiza NEXTAUTH_URL y NEXT_PUBLIC_API_URL en .env"
echo "  3. Ejecuta: docker-compose -f docker-compose.prod.yml restart"
echo
log "Comandos útiles:"
echo "  Ver logs:     docker-compose -f docker-compose.prod.yml logs -f"
echo "  Parar app:    docker-compose -f docker-compose.prod.yml down"
echo "  Reiniciar:    docker-compose -f docker-compose.prod.yml restart"
echo
log "¡Listo! 🚀"