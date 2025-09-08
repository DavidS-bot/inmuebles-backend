# GUÍA PASO A PASO - SUBIR MOVIMIENTOS AL AGENTE FINANCIERO

## 🎯 OBJETIVO
Hacer que aparezcan 3 movimientos de prueba en la lista de movimientos.

## 📁 ARCHIVO DE PRUEBA
- **Nombre:** `test_minimo.xlsx`
- **Contenido:** Solo 3 movimientos simples
- **Ubicación:** En la carpeta backend

## 🔧 PASOS A SEGUIR

### PASO 1: PREPARACIÓN
1. Ve a: https://inmuebles-david.vercel.app
2. **IMPORTANTE:** Asegúrate de estar logueado
3. Si no estás logueado, haz login con tus credenciales

### PASO 2: CREAR PROPIEDAD (MUY IMPORTANTE)
1. Ve a la sección de **Propiedades** 
2. Haz clic en **"Crear Propiedad"** o **"Nueva Propiedad"**
3. Rellena los datos básicos:
   - **Nombre:** `Mi Casa de Prueba`
   - **Dirección:** `Calle Prueba 123`
   - **Tipo:** `Apartamento`
   - **Precio:** `100000`
4. **Guarda la propiedad**

### PASO 3: IR A MOVIMIENTOS FINANCIEROS
1. Ve a: **Agente Financiero > Movimientos Financieros**
2. URL directa: https://inmuebles-david.vercel.app/financial-agent/movements

### PASO 4: BUSCAR BOTÓN DE SUBIDA
Busca en la pantalla uno de estos elementos:
- Botón **"Subir Excel"**
- Botón **"Importar"** 
- Botón **"Upload"**
- Botón **"+"** (agregar)
- Área de **drag & drop** (arrastrar archivo)
- Enlace **"Importar movimientos"**

### PASO 5: SUBIR ARCHIVO
1. Haz clic en el botón de subida
2. Selecciona el archivo: **`test_minimo.xlsx`**
3. **IMPORTANTE:** Si te pide seleccionar propiedad, elige **"Mi Casa de Prueba"**
4. Haz clic en **"Subir"** o **"Procesar"**

### PASO 6: VERIFICAR RESULTADO
Deberías ver en la lista:
- ✅ **Total Movimientos: 3**
- ✅ **PRUEBA INGRESO - 1,000.00 €**
- ✅ **PRUEBA GASTO - (500.00) €**
- ✅ **OTRA PRUEBA - 250.00 €**

## 🚨 SI NO VES LOS MOVIMIENTOS

### VERIFICAR FILTROS
1. **Propiedad:** Selecciona "Mi Casa de Prueba" o "Todas"
2. **Categoría:** Selecciona "Todas"
3. **Fecha Desde:** Deja vacío o pon `01/01/2025`
4. **Fecha Hasta:** Deja vacío o pon `31/12/2025`

### VERIFICAR PERMISOS
- ¿Estás logueado con el usuario correcto?
- ¿La propiedad aparece en tu lista de propiedades?

## 📞 PROBLEMA PERSISTENTE
Si sigues sin ver los movimientos después de seguir todos los pasos:

1. **Problema:** La subida no está funcionando
2. **Causa:** Configuración de permisos o base de datos
3. **Solución:** Necesitamos revisar la configuración del backend

## ✅ ÉXITO
Si ves los 3 movimientos de prueba, entonces:
- ✅ El sistema funciona
- ✅ Puedes subir tu archivo real con 1,400+ movimientos
- ✅ Solo cambia `test_minimo.xlsx` por `movimientos_usuario_corregido.xlsx`