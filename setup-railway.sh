#!/bin/bash

# 🚂 Script para Deploy en Railway
echo "=== 🚂 Deploy Automático en Railway ==="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m' 
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Paso 1: Verificar Railway CLI
if ! command -v railway &> /dev/null; then
    log "Instalando Railway CLI..."
    
    # Detectar sistema operativo
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install railway
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://railway.app/install.sh | sh
    else
        warn "Instala Railway CLI manualmente:"
        echo "Windows: https://railway.app/cli"
        echo "macOS: brew install railway"
        echo "Linux: curl -fsSL https://railway.app/install.sh | sh"
        exit 1
    fi
fi

log "✅ Railway CLI instalado"

# Paso 2: Login a Railway
log "Iniciando sesión en Railway..."
railway login

# Paso 3: Crear proyecto
log "Creando proyecto en Railway..."
railway init inmuebles-app

# Paso 4: Configurar base de datos
log "Añadiendo PostgreSQL..."
railway add postgresql

# Paso 5: Configurar variables de entorno
log "Configurando variables de entorno..."

# Generar secrets aleatorios
JWT_SECRET=$(openssl rand -base64 32)
NEXTAUTH_SECRET=$(openssl rand -base64 32)

railway variables set \
  JWT_SECRET_KEY="$JWT_SECRET" \
  JWT_ALGORITHM="HS256" \
  ACCESS_TOKEN_EXPIRE_MINUTES="30" \
  NEXTAUTH_SECRET="$NEXTAUTH_SECRET" \
  ALLOWED_ORIGINS='["https://inmuebles-app.railway.app","https://*.railway.app"]'

log "✅ Variables configuradas"

# Paso 6: Deploy
log "Desplegando aplicación..."
railway up --detach

log "✅ Deploy iniciado!"

echo
echo -e "${BLUE}=== 🎉 Deploy en Railway Completado ===${NC}"
echo
log "Tu aplicación estará disponible en unos minutos en:"
echo "  🌐 https://inmuebles-app.railway.app"
echo
log "Comandos útiles:"
echo "  Ver logs:        railway logs"
echo "  Abrir app:       railway open"
echo "  Ver variables:   railway variables"
echo "  Redeploy:        railway up"
echo
log "¡Tu PWA estará lista en 2-3 minutos! 🚀"