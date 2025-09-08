# 🚂 **Pasos para Deploy en Railway - SÚPER FÁCIL**

## ✅ **Ya está preparado todo automáticamente**

### **Paso 1: Abre tu terminal (cmd/PowerShell) y ejecuta:**
```bash
cd C:\Users\davsa\inmuebles\backend
railway login
```
Se abrirá tu navegador → Inicia sesión con GitHub/Google/Email

### **Paso 2: Crear proyecto**
```bash
railway init inmuebles-app
```

### **Paso 3: Añadir base de datos**
```bash
railway add postgresql
```

### **Paso 4: Configurar variables (copia y pega todo junto)**
```bash
railway variables set JWT_SECRET_KEY="railway_jwt_secret_key_super_segura_2024"
railway variables set JWT_ALGORITHM="HS256"  
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30"
railway variables set NEXTAUTH_SECRET="railway_nextauth_secret_super_segura_2024"
railway variables set ALLOWED_ORIGINS="[\"https://*.railway.app\",\"https://localhost:3000\"]"
```

### **Paso 5: Deploy (¡EL FINAL!)**
```bash
railway up --detach
```

## 🎉 **¡LISTO!**

Tu aplicación estará disponible en:
- `https://inmuebles-app-production.railway.app` (o similar)
- La PWA se podrá instalar desde el navegador móvil
- Todo funcionará automáticamente

### **Ver progreso:**
```bash
railway logs --follow
```

### **Abrir tu app:**
```bash
railway open
```

---

## ⚡ **Resumen ultra-rápido:**
1. `railway login` (se abre navegador)
2. `railway init inmuebles-app` 
3. `railway add postgresql`
4. Copiar y pegar las 5 variables de arriba
5. `railway up --detach`

**¡En 2 minutos tu app estará online! 🚀**