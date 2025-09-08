# 🚀 Deployment Guide - Inmuebles App

## Deployment en VPS (Económico y Profesional)

### 1. Preparar el VPS

**Proveedores recomendados:**
- **DigitalOcean**: $4-6/mes (droplet básico)
- **Vultr**: $3.50-5/mes
- **Linode**: $5/mes
- **Hetzner**: €3-5/mes (Europa)

**Especificaciones mínimas:**
- RAM: 2GB
- CPU: 1 vCore
- Disco: 25GB SSD
- Bandwidth: 1TB

### 2. Configuración inicial

```bash
# Conectar al VPS
ssh root@tu-servidor-ip

# Ejecutar script de configuración
curl -fsSL https://raw.githubusercontent.com/tu-usuario/tu-repo/main/vps-setup.sh | bash

# Reiniciar para aplicar cambios de Docker
sudo reboot
```

### 3. Subir código al VPS

```bash
# Opción A: Git (recomendado)
git clone https://github.com/tu-usuario/inmuebles-app.git
cd inmuebles-app/backend

# Opción B: SCP desde tu PC
scp -r C:\Users\davsa\inmuebles\backend user@tu-servidor-ip:/opt/inmuebles/
```

### 4. Configurar variables de entorno

```bash
# Copiar archivo de configuración
cp .env.production .env

# Editar variables importantes
nano .env.production

# Cambiar estos valores:
DB_PASSWORD=tu-password-seguro
JWT_SECRET=tu-jwt-secreto-muy-largo
API_URL=https://tu-dominio.com
```

### 5. Deploy la aplicación

```bash
# Hacer ejecutable el script
chmod +x deploy.sh

# Ejecutar deployment
./deploy.sh
```

### 6. Configurar dominio y SSL

```bash
# Configurar DNS de tu dominio apuntando a la IP del VPS

# Obtener certificado SSL gratuito
sudo certbot --nginx -d tu-dominio.com

# Actualizar nginx.conf para usar HTTPS
nano nginx.conf
# Descomentar la sección HTTPS y cambiar "your-domain.com"

# Reiniciar servicios
docker-compose -f docker-compose.prod.yml restart nginx
```

## 🔧 Comandos útiles

### Gestión de servicios
```bash
# Ver estado
docker-compose -f docker-compose.prod.yml ps

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f [servicio]

# Reiniciar servicio
docker-compose -f docker-compose.prod.yml restart [servicio]

# Actualizar aplicación
git pull
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### Backup de base de datos
```bash
# Crear backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U inmuebles inmuebles > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker-compose -f docker-compose.prod.yml exec -T db psql -U inmuebles inmuebles < backup_20241201.sql
```

### Monitoreo
```bash
# Espacio en disco
df -h

# Uso de memoria
free -h

# Procesos Docker
docker stats

# Logs del sistema
sudo journalctl -u docker
```

## 🛡️ Seguridad

### Configuración básica de seguridad
```bash
# Cambiar puerto SSH (opcional)
sudo nano /etc/ssh/sshd_config
# Port 2222

# Deshabilitar login como root
sudo nano /etc/ssh/sshd_config
# PermitRootLogin no

# Crear usuario no-root
sudo adduser inmuebles
sudo usermod -aG sudo inmuebles
sudo usermod -aG docker inmuebles
```

### Firewall
```bash
# Verificar estado
sudo ufw status

# Abrir puerto específico
sudo ufw allow 8080/tcp
```

## 💰 Costos aproximados

- **VPS básico**: €3-6/mes
- **Dominio**: €10/año
- **SSL**: Gratis (Let's Encrypt)
- **Total mensual**: €3-6

## 🔍 Troubleshooting

### Problemas comunes

**Error: No se conecta la base de datos**
```bash
docker-compose -f docker-compose.prod.yml logs db
# Verificar que PostgreSQL esté iniciado
```

**Error: Frontend no carga**
```bash
docker-compose -f docker-compose.prod.yml logs web
# Verificar variables NEXT_PUBLIC_API_URL
```

**Error: API no responde**
```bash
docker-compose -f docker-compose.prod.yml logs api
# Verificar conexión a base de datos
```

**Sin espacio en disco**
```bash
# Limpiar imágenes Docker no usadas
docker system prune -a

# Ver uso por directorio
du -h /opt/inmuebles/
```

## 📞 Soporte

Si tienes problemas con el deployment:

1. Revisa los logs: `docker-compose -f docker-compose.prod.yml logs`
2. Verifica que todos los servicios estén corriendo: `docker-compose -f docker-compose.prod.yml ps`
3. Comprueba las variables de entorno en `.env.production`# Force redeploy ma.,  9 de sep. de 2025  0:51:29
