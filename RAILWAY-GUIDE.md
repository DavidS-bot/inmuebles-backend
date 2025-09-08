# 🚂 Guía Railway - Deploy Súper Fácil

## Método 1: Con Script Automático (Más Fácil)

```bash
# Ejecutar script automático
./setup-railway.sh
```

¡Y listo! Tu app estará online en 2 minutos.

---

## Método 2: Manual (Paso a Paso)

### Paso 1: Crear cuenta en Railway
1. Ve a [railway.app](https://railway.app)
2. Haz clic en "Start a New Project"
3. Inicia sesión con GitHub/Google/Email

### Paso 2: Instalar Railway CLI

**Windows:**
```cmd
powershell -c "irm https://railway.app/install.ps1 | iex"
```

**macOS:**
```bash
brew install railway
```

**Linux:**
```bash
curl -fsSL https://railway.app/install.sh | sh
```

### Paso 3: Login y crear proyecto
```bash
# Login
railway login

# Ir a tu carpeta
cd inmuebles/backend

# Crear proyecto
railway init
```

### Paso 4: Añadir base de datos
```bash
railway add postgresql
```

### Paso 5: Configurar variables de entorno
En el dashboard de Railway o por CLI:

```bash
# Variables esenciales
railway variables set DATABASE_URL="$DATABASE_URL"
railway variables set JWT_SECRET_KEY="tu_clave_jwt_super_secreta"  
railway variables set NEXTAUTH_SECRET="tu_clave_nextauth_super_secreta"
railway variables set ALLOWED_ORIGINS='["https://*.railway.app"]'
```

### Paso 6: Deploy
```bash
railway up
```

¡Listo! En 2-3 minutos tu app estará online.

---

## Método 3: Deploy Web (Sin CLI)

### Paso 1: Subir código a GitHub
1. Crea un repositorio en GitHub
2. Sube tu carpeta `inmuebles/backend`

### Paso 2: Conectar en Railway
1. Ve a [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo"
3. Selecciona tu repositorio
4. Railway detecta automáticamente el Dockerfile

### Paso 3: Configurar variables
En el dashboard → Variables:
- `JWT_SECRET_KEY`: Clave JWT secreta
- `NEXTAUTH_SECRET`: Clave NextAuth secreta  
- `ALLOWED_ORIGINS`: `["https://*.railway.app"]`

### Paso 4: Añadir base de datos
En tu proyecto → "New" → "Database" → "Add PostgreSQL"

¡Listo!

---

## 🎯 Resultado Final

Tu aplicación estará disponible en:
- **URL**: `https://tu-proyecto.railway.app`
- **Features**: 
  - ✅ Base de datos PostgreSQL
  - ✅ HTTPS automático
  - ✅ PWA funcionando
  - ✅ Apps móvil instalable
  - ✅ Deploy automático en cada commit
  - ✅ Logs en tiempo real
  - ✅ Escalado automático

## 💰 Costos
- **Gratis**: $5/mes de crédito incluido
- **Hobby**: $5/mes (suficiente para tu app)
- **Pro**: $20/mes (para más tráfico)

## 🛠️ Comandos Útiles

```bash
# Ver logs en vivo
railway logs

# Abrir tu app
railway open

# Ver variables
railway variables

# Redeploy
railway up

# Conectar a base de datos
railway connect postgresql
```

## 🔧 Troubleshooting

**Error "Module not found":**
```bash
railway variables set PYTHONPATH="/app"
```

**Error de puerto:**
Railway asigna automáticamente el puerto, no lo configures.

**Error de base de datos:**
La variable `DATABASE_URL` se configura automáticamente al añadir PostgreSQL.

---

## ✨ Próximos Pasos

1. **Dominio personalizado**: Conecta tu propio dominio
2. **CI/CD**: Deploy automático en cada commit
3. **Monitoring**: Logs y métricas automáticas
4. **Backups**: Backups automáticos de la DB

¡Tu aplicación Inmuebles estará online en minutos! 🏠🚀