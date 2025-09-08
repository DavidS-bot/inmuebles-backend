# INFORMACIÓN SOBRE SCREENSHOTS DE LA APLICACIÓN

Este directorio debería contener screenshots automáticos de todas las páginas principales.

## Páginas documentadas:

### Página de Login
**Archivo:** 01_login.png
**Descripción:** Sistema de autenticación con formulario de usuario y contraseña

### Dashboard Principal - Financial Agent
**Archivo:** 02_dashboard_principal.png
**Descripción:** Hub central con resumen de propiedades y métricas por año

### Gestión de Movimientos Financieros
**Archivo:** 03_gestion_movimientos.png
**Descripción:** CRUD completo con filtros, clasificación y asignación a propiedades

### Dashboard de Analytics
**Archivo:** 04_analytics_dashboard.png
**Descripción:** KPIs, gráficos de rentabilidad y análisis comparativo

### Gestión de Contratos
**Archivo:** 05_gestion_contratos.png
**Descripción:** Administración de contratos de alquiler e inquilinos

### Reglas de Clasificación
**Archivo:** 06_reglas_clasificacion.png
**Descripción:** Sistema de automatización para categorización de movimientos

### Centro de Integraciones
**Archivo:** 07_integraciones.png
**Descripción:** Gestión de conexiones con servicios externos

### Integración Bankinter
**Archivo:** 08_integracion_bankinter.png
**Descripción:** Configuración PSD2 y sincronización automática

### Calculadora Hipotecaria
**Archivo:** 09_calculadora_hipoteca.png
**Descripción:** Herramienta de simulación y cálculo de cuotas

### Gestión de Euribor
**Archivo:** 10_gestion_euribor.png
**Descripción:** Seguimiento histórico de tipos de interés

### Gestor de Documentos
**Archivo:** 11_gestor_documentos.png
**Descripción:** Sistema de archivos organizados por propiedad

### Centro de Notificaciones
**Archivo:** 12_notificaciones.png
**Descripción:** Alertas, recordatorios y mensajes del sistema

### Asistente Fiscal
**Archivo:** 13_asistente_fiscal.png
**Descripción:** Herramientas para declaraciones y optimización fiscal

### Clasificador Inteligente
**Archivo:** 14_clasificador_inteligente.png
**Descripción:** Sistema de IA para clasificación automática

### Vista General de Propiedad
**Archivo:** 15_propiedad_vista_general.png
**Descripción:** Dashboard específico con métricas de la propiedad

### Informes Financieros de Propiedad
**Archivo:** 16_informes_propiedad.png
**Descripción:** Reportes detallados con cash flow y análisis mensual

### Gestión Hipotecaria de Propiedad
**Archivo:** 17_hipoteca_propiedad.png
**Descripción:** Administración de hipoteca con cronograma y revisiones

### Reglas Específicas de Propiedad
**Archivo:** 18_reglas_propiedad.png
**Descripción:** Configuración de reglas particulares para la propiedad


## Cómo generar screenshots automáticos:

1. **Instalar ChromeDriver:**
   - Descargar desde: https://chromedriver.chromium.org/
   - Agregar al PATH del sistema

2. **Ejecutar aplicación:**
   ```bash
   cd inmuebles-web
   npm run dev
   ```

3. **Capturar screenshots:**
   ```bash
   python capture_screenshots.py
   ```

## Alternativa manual:

Si el script automático no funciona, puedes tomar screenshots manualmente:
1. Navegar a cada URL en el navegador
2. Guardar screenshot con el nombre indicado
3. Colocar en este directorio

## URLs principales:

- http://localhost:3000/login
- http://localhost:3000/financial-agent
- http://localhost:3000/financial-agent/movements
- http://localhost:3000/financial-agent/analytics
- http://localhost:3000/financial-agent/contracts
- http://localhost:3000/financial-agent/rules
- http://localhost:3000/financial-agent/integrations
- http://localhost:3000/financial-agent/integrations/bankinter
- http://localhost:3000/financial-agent/mortgage-calculator
- http://localhost:3000/financial-agent/euribor
- http://localhost:3000/financial-agent/documents
- http://localhost:3000/financial-agent/notifications
- http://localhost:3000/financial-agent/tax-assistant
- http://localhost:3000/financial-agent/smart-classifier
- http://localhost:3000/financial-agent/property/1
- http://localhost:3000/financial-agent/property/1/reports
- http://localhost:3000/financial-agent/property/1/mortgage
- http://localhost:3000/financial-agent/property/1/rules
