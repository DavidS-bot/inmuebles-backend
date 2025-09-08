#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando deployment de Inmuebles App...${NC}"

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.prod.yml" ]; then
    error "docker-compose.prod.yml no encontrado. Ejecuta este script desde el directorio backend."
    exit 1
fi

# Crear directorio SSL si no existe
if [ ! -d "ssl" ]; then
    log "Creando directorio SSL..."
    mkdir -p ssl
fi

# Verificar variables de entorno
if [ ! -f ".env.production" ]; then
    warning ".env.production no encontrado. Usando valores por defecto."
    cp .env.production.example .env.production 2>/dev/null || true
fi

log "Deteniendo contenedores existentes..."
docker-compose -f docker-compose.prod.yml down

log "Eliminando imágenes antiguas..."
docker-compose -f docker-compose.prod.yml build --no-cache

log "Iniciando servicios..."
docker-compose -f docker-compose.prod.yml up -d

log "Esperando que los servicios estén listos..."
sleep 30

# Verificar que los servicios estén corriendo
log "Verificando servicios..."

if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    log "✅ Servicios iniciados correctamente"
    
    echo -e "\n${BLUE}📋 Estado de los servicios:${NC}"
    docker-compose -f docker-compose.prod.yml ps
    
    echo -e "\n${GREEN}🎉 Deployment completado!${NC}"
    echo -e "${YELLOW}Tu aplicación está disponible en:${NC}"
    echo -e "  🌐 Frontend: http://localhost"
    echo -e "  🔧 API: http://localhost/api"
    echo -e "  📊 Base de datos: localhost:5432"
    echo -e "\n${YELLOW}Logs útiles:${NC}"
    echo -e "  docker-compose -f docker-compose.prod.yml logs -f web"
    echo -e "  docker-compose -f docker-compose.prod.yml logs -f api"
    echo -e "  docker-compose -f docker-compose.prod.yml logs -f db"
    
else
    error "❌ Algunos servicios no se iniciaron correctamente"
    docker-compose -f docker-compose.prod.yml logs --tail=50
    exit 1
fi