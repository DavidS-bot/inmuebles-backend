# 🚂 Deploy en Railway

## Pasos para deployment:

### 1. Instalar Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Login en Railway
```bash
railway login
```

### 3. Crear nuevo proyecto
```bash
railway init
```

### 4. Configurar variables de entorno
```bash
railway variables set DATABASE_URL="postgresql://..."
railway variables set JWT_SECRET="tu-secret-key-segura"
railway variables set NEXTAUTH_URL="https://tu-app.railway.app"
```

### 5. Deploy
```bash
railway up
```

## Ventajas:
- ✅ Soporte nativo para Docker Compose
- ✅ Base de datos PostgreSQL incluida
- ✅ SSL automático
- ✅ $5 USD de crédito gratis al mes
- ✅ Deploy automático desde GitHub

## URLs después del deploy:
- Frontend: https://inmuebles.railway.app
- API: https://inmuebles-api.railway.app