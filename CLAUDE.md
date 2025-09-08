# Proyecto Inmuebles - Plataforma de Gestión de Inversiones Inmobiliarias

## Descripción del Proyecto
Plataforma web completa para gestión y análisis de inversiones inmobiliarias con integración bancaria automática (Bankinter), análisis financiero avanzado y herramientas de gestión de propiedades.

## Arquitectura del Sistema

### Stack Tecnológico
**Backend:**
- FastAPI (Python) - API REST principal
- SQLModel + SQLite - ORM y base de datos
- Selenium + WebDriver - Scraping bancario automatizado
- Pandas/NumPy - Análisis de datos financieros

**Frontend:**
- Next.js 14 (React) - Aplicación web
- TypeScript - Tipado estático
- Tailwind CSS - Estilos y UI
- PWA - Aplicación web progresiva

### Estructura de Directorios
```
inmuebles/
├── backend/           # FastAPI Backend
│   ├── app/
│   │   ├── routers/   # Endpoints de la API
│   │   ├── models.py  # Modelos de datos SQLModel
│   │   ├── main.py    # Aplicación principal
│   │   └── services/  # Servicios y lógica de negocio
│   └── mcp-real-estate/ # Servidor MCP para análisis
└── inmuebles-web/     # Next.js Frontend
    ├── app/           # App Router (Next.js 14)
    ├── components/    # Componentes React reutilizables
    └── contexts/      # Context providers
```

## Modelos de Datos Principales

### Usuario y Propiedades
- **User**: Usuarios del sistema con autenticación
- **Property**: Propiedades inmobiliarias con datos financieros
- **Rule/ClassificationRule**: Reglas de clasificación automática

### Gestión Financiera
- **FinancialMovement**: Movimientos bancarios importados
- **MortgageDetails**: Detalles de hipotecas variables
- **RentalContract**: Contratos de alquiler y gestión de inquilinos
- **EuriborRate**: Tasas Euribor históricas

### Integración Bancaria
- **BankConnection**: Conexiones con entidades bancarias
- **BankAccount**: Cuentas bancarias vinculadas

## Comandos Importantes

### Desarrollo Backend
```bash
# Iniciar servidor de desarrollo
uvicorn app.main:app --reload --port 8000

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar scraper Bankinter
python bankinter_auto_download.py
```

### Desarrollo Frontend
```bash
cd inmuebles-web
npm install
npm run dev  # Puerto 3000
npm run build
npm run lint
```

### Deployment
```bash
# Deploy automático a Vercel
./deploy-auto.bat
./deploy-inmuebles-vercel.bat

# Deploy backend
./deploy-backend-fixed.bat

# Verificar deployment
./check-deployment.bat
```

## Endpoints Principales de la API

### Autenticación
- `POST /auth/login` - Login de usuario
- `POST /auth/register` - Registro de usuario

### Gestión de Propiedades
- `GET /properties/` - Listar propiedades
- `POST /properties/` - Crear propiedad
- `PUT /properties/{id}` - Actualizar propiedad

### Análisis Financiero
- `GET /financial-movements/` - Movimientos financieros
- `POST /financial-movements/upload` - Importar movimientos
- `GET /analytics/` - Métricas y análisis

### Contratos e Hipotecas
- `GET /rental-contracts/` - Contratos de alquiler
- `GET /mortgage-details/` - Detalles de hipotecas
- `POST /euribor-rates/` - Actualizar tasas Euribor

### Integración Bancaria
- `POST /bankinter-real/scrape` - Scraping Bankinter
- `GET /bank-integration/` - Estado de conexiones bancarias

## Configuración de Entorno

### Variables de Entorno
```bash
# Credenciales Bankinter
BANKINTER_USERNAME=75867185
BANKINTER_PASSWORD=Motoreta123$

# Base de datos
DATABASE_URL=sqlite:///./app.db

# JWT y autenticación
SECRET_KEY=your-secret-key
```

### URLs de Deployment
- **Frontend**: https://inmuebles-web.vercel.app
- **Backend**: https://inmuebles-backend-api.onrender.com

## Características Especiales

### Integración Bancaria Automatizada
- **Scraping Bankinter**: Descarga automática de movimientos bancarios
- **Clasificación inteligente**: Categorización automática de transacciones
- **Conciliación**: Asociación automática con propiedades

### Análisis Financiero Avanzado
- **ROI y rentabilidad**: Cálculos automáticos por propiedad
- **Proyecciones hipotecarias**: Simulaciones con Euribor variable
- **Cash flow**: Análisis de flujos de caja mensuales
- **Comparativa de mercado**: Análisis de inversiones

### Gestión de Contratos
- **Upload de PDFs**: Almacenamiento de contratos
- **Datos de inquilinos**: Gestión completa de información
- **Fechas de vencimiento**: Alertas automáticas

## Servidor MCP (Real Estate Analyzer)
Servidor especializado para análisis inmobiliario ubicado en `mcp-real-estate/`:
- Búsqueda de propiedades
- Cálculos de rentabilidad
- Proyecciones de inversión
- Comparativas de mercado

## Scripts de Mantenimiento

### Scraping y Datos
- `bankinter_auto_download.py` - Descarga automática Bankinter
- `upload_to_production.py` - Migración a producción
- `complete_migration.py` - Migración completa de datos

### Utilidades
- `create_production_admin.py` - Crear usuario administrador
- `check_production_status.py` - Verificar estado de producción
- `analyze_user_file.py` - Análisis de archivos de usuario

## Notas de Desarrollo

### Autenticación
- Sistema JWT con tokens de sesión
- Middleware de autenticación en todas las rutas protegidas

### Base de Datos
- SQLite para desarrollo local
- PostgreSQL recomendado para producción
- Migraciones automáticas con SQLModel

### Frontend PWA
- Installable como aplicación móvil
- Offline capability básica
- Responsive design completo

### Integración Continua
- Deploy automático en push a main
- Verificación de tipos TypeScript
- Linting automático

---
*Última actualización: Septiembre 2025*
*Configurado como agente financiero especializado en análisis de inversiones inmobiliarias*