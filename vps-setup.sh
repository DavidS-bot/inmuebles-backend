#!/bin/bash

# Script para configurar un VPS nuevo con tu aplicación de inmuebles

echo "🚀 Configurando VPS para Inmuebles App..."

# Actualizar sistema
echo "📦 Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar Docker
echo "🐳 Instalando Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
echo "🔧 Instalando Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Instalar herramientas útiles
echo "🛠️ Instalando herramientas..."
sudo apt install -y git curl wget htop nginx certbot python3-certbot-nginx ufw

# Configurar firewall
echo "🔒 Configurando firewall..."
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Crear directorio de la aplicación
echo "📁 Creando directorios..."
sudo mkdir -p /opt/inmuebles
sudo chown $USER:$USER /opt/inmuebles
cd /opt/inmuebles

echo "✅ VPS configurado correctamente!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Sube tu código: git clone <tu-repo> ."
echo "2. Configura variables: cp .env.production.example .env.production"
echo "3. Ejecuta: chmod +x deploy.sh && ./deploy.sh"
echo "4. Para SSL: sudo certbot --nginx -d tu-dominio.com"
echo ""
echo "🔗 Comandos útiles:"
echo "  - Ver logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  - Reiniciar: docker-compose -f docker-compose.prod.yml restart"
echo "  - Estado: docker-compose -f docker-compose.prod.yml ps"