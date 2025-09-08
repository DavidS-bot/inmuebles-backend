# 🚀 Guía para Lanzar Inmuebles Online

## Opción 1: VPS con Docker (Recomendada)

### Paso 1: Conseguir un VPS
Necesitas un servidor VPS con:
- **RAM**: Mínimo 2GB (recomendado 4GB)
- **CPU**: 1-2 cores
- **Almacenamiento**: 20GB mínimo
- **SO**: Ubuntu 20.04/22.04

**Proveedores recomendados:**
- **DigitalOcean** (~$12/mes) - Fácil setup
- **Vultr** (~$10/mes) - Buena relación precio/rendimiento  
- **Linode** (~$12/mes) - Muy estable
- **AWS EC2** (t3.small ~$15/mes) - Más complejo pero escalable

### Paso 2: Configurar el VPS
```bash
# Conectar por SSH
ssh root@tu-servidor-ip

# Actualizar sistema
apt update && apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
apt install docker-compose -y

# Crear usuario para la app
useradd -m -s /bin/bash inmuebles
usermod -aG docker inmuebles
```

### Paso 3: Subir archivos al servidor
```bash
# Desde tu PC, comprimir la aplicación
tar -czf inmuebles.tar.gz inmuebles/backend/

# Subir al servidor
scp inmuebles.tar.gz root@tu-servidor-ip:/home/inmuebles/

# En el servidor
cd /home/inmuebles
tar -xzf inmuebles.tar.gz
chown -R inmuebles:inmuebles backend/
```

### Paso 4: Configurar variables de entorno
```bash
# En el servidor
cd /home/inmuebles/backend
cp .env.example .env

# Editar configuración
nano .env
```

**Variables importantes:**
```env
DATABASE_URL=postgresql://postgres:tu_password_seguro@db:5432/inmuebles_prod
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password_muy_seguro
POSTGRES_DB=inmuebles_prod
NEXTAUTH_SECRET=clave_secreta_muy_larga_y_segura
NEXTAUTH_URL=https://tu-dominio.com
NEXT_PUBLIC_API_URL=https://tu-dominio.com/api
```

### Paso 5: Lanzar la aplicación
```bash
# Construir y lanzar
docker-compose -f docker-compose.prod.yml up --build -d

# Verificar que funciona
docker-compose -f docker-compose.prod.yml ps
```

### Paso 6: Configurar dominio y SSL

#### Con dominio propio:
1. **Comprar dominio** (Namecheap, GoDaddy, etc.)
2. **Configurar DNS**:
   ```
   A record: @ -> IP_DE_TU_SERVIDOR
   A record: www -> IP_DE_TU_SERVIDOR
   ```
3. **Configurar SSL automático**:
   ```bash
   # Instalar Certbot
   apt install certbot python3-certbot-nginx -y
   
   # Obtener certificado SSL
   certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
   ```

#### Sin dominio (IP pública):
Tu app estará disponible en: `http://IP_DE_TU_SERVIDOR`

---

## Opción 2: Vercel (Más Fácil, Solo Frontend)

### Paso 1: Preparar para Vercel
```bash
cd inmuebles-web
npm install -g vercel
```

### Paso 2: Deploy
```bash
vercel

# Seguir las instrucciones:
# - Set up and deploy? Y
# - Which scope? Tu cuenta
# - Link to existing project? N
# - Project name: inmuebles
# - Directory: ./
# - Override settings? N
```

### Paso 3: Configurar variables de entorno
En tu dashboard de Vercel:
1. Ve a tu proyecto → Settings → Environment Variables
2. Añade:
   ```
   NEXTAUTH_SECRET=tu_clave_secreta
   NEXTAUTH_URL=https://tu-app.vercel.app
   NEXT_PUBLIC_API_URL=https://tu-backend-url.com/api
   ```

---

## Opción 3: Railway (Backend + Frontend)

### Deploy automático:
1. Ve a [railway.app](https://railway.app)
2. Conecta tu repositorio GitHub
3. Railway detectará automáticamente Docker
4. Configura variables de entorno
5. ¡Listo!

---

## ✅ Verificación del Deploy

### Tests básicos:
```bash
# Verificar web
curl -I https://tu-dominio.com

# Verificar API
curl https://tu-dominio.com/api/properties

# Verificar PWA
curl https://tu-dominio.com/manifest.json
```

### PWA en móvil:
1. Abre Chrome/Safari en tu móvil
2. Ve a tu dominio
3. Deberías ver el prompt "Instalar app"
4. La app funcionará offline parcialmente

---

## 🔧 Comandos útiles

### Ver logs:
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### Reiniciar servicios:
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Actualizar aplicación:
```bash
git pull
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

---

## 💰 Costos estimados:

- **VPS básico**: $10-15/mes
- **Dominio**: $10-15/año  
- **SSL**: Gratis con Let's Encrypt
- **Total**: ~$12-18/mes

**Opciones gratuitas/baratas:**
- Vercel (frontend): Gratis hasta cierto límite
- Railway: $5/mes con créditos incluidos
- PlanetScale (DB): Plan gratuito disponible

---

¿Qué opción prefieres? Te ayudo con la que elijas.