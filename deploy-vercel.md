# ▲ Deploy en Vercel + Supabase

## Frontend (Vercel):

### 1. Instalar Vercel CLI
```bash
npm i -g vercel
```

### 2. Deploy Frontend
```bash
cd inmuebles-web
vercel
```

## Backend (Supabase):

### 1. Crear proyecto en Supabase
- Ve a: https://supabase.com
- Crea nuevo proyecto
- Obtén tu DATABASE_URL

### 2. Deploy API en Vercel
```bash
cd backend
vercel --prod
```

## Configuración env:
```env
# Frontend (.env.production)
NEXT_PUBLIC_API_URL=https://api-inmuebles.vercel.app
NEXTAUTH_URL=https://inmuebles.vercel.app

# Backend
DATABASE_URL=postgresql://...supabase.co:5432/postgres
```

## Ventajas:
- ✅ Gratis para proyectos pequeños
- ✅ CDN global para el frontend
- ✅ Base de datos PostgreSQL profesional
- ✅ Analytics incluidos
- ✅ Preview deployments automáticos