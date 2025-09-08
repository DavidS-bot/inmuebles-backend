#!/usr/bin/env python3
"""
Debug específico del problema de la interfaz web
"""

print("DIAGNOSTICO DEL PROBLEMA DE LA INTERFAZ WEB")
print("=" * 60)

print("\nEl archivo de prueba se subió pero no aparecen los 3 movimientos.")
print("Esto indica que el problema NO es el archivo, sino la configuración.")

print("\nPOSIBLES CAUSAS:")
print("1. Los movimientos se suben pero no se asignan al usuario correcto")
print("2. Los movimientos se suben pero no se asignan a ninguna propiedad")
print("3. Los filtros en la interfaz están ocultando los movimientos")
print("4. Problema de permisos/autenticación")
print("5. La interfaz está conectada a una base de datos diferente")

print("\nVAMOS A VERIFICAR CADA POSIBILIDAD:")

print("\n" + "="*60)
print("VERIFICACIÓN 1: FILTROS EN LA INTERFAZ")
print("="*60)
print("En la pantalla de movimientos, verifica estos filtros:")
print("- Propiedad: ¿Está en 'Todas' o en tu propiedad creada?")
print("- Categoría: ¿Está en 'Todas'?")
print("- Fecha Desde: ¿Está vacío o permite 2025?")
print("- Fecha Hasta: ¿Está vacío o permite 2025?")
print("- Campo de búsqueda: ¿Está vacío?")

print("\n" + "="*60)
print("VERIFICACIÓN 2: USUARIO Y PROPIEDADES")
print("="*60)
print("1. ¿Puedes ver tu nombre de usuario en la parte superior derecha?")
print("2. ¿Creaste efectivamente una propiedad antes de subir?")
print("3. ¿Aparece esa propiedad en el filtro 'Propiedad'?")
print("4. ¿Al subir el archivo te pidió seleccionar una propiedad?")

print("\n" + "="*60)
print("VERIFICACIÓN 3: PROCESO DE SUBIDA")
print("="*60)
print("Cuando subiste el archivo test_minimo.xlsx:")
print("1. ¿Apareció algún mensaje de éxito? (ej: '3 movimientos procesados')")
print("2. ¿Apareció algún error?")
print("3. ¿La página se refrescó automáticamente?")
print("4. ¿Te pidió seleccionar formato de archivo?")

print("\n" + "="*60)
print("VERIFICACIÓN 4: CONSOLA DEL NAVEGADOR")
print("="*60)
print("Abre las herramientas de desarrollador en tu navegador:")
print("1. Presiona F12")
print("2. Ve a la pestaña 'Console'")
print("3. Recarga la página de movimientos")
print("4. ¿Aparece algún error en rojo?")
print("5. ¿Hay algún error relacionado con API o fetch?")

print("\n" + "="*60)
print("SOLUCIONES A PROBAR:")
print("="*60)
print("SOLUCIÓN 1 - Limpiar filtros:")
print("- Haz clic en 'Limpiar filtros' si existe el botón")
print("- O resetea manualmente todos los filtros")

print("\nSOLUCIÓN 2 - Recargar página:")
print("- Presiona Ctrl+F5 para recargar completamente")
print("- O cierra y abre nueva pestaña")

print("\nSOLUCIÓN 3 - Crear movimiento manual:")
print("- Busca botón 'Crear movimiento' o '+'")
print("- Crea 1 movimiento manualmente")
print("- Si aparece, el problema es la subida de archivos")
print("- Si no aparece, el problema es la visualización")

print("\n" + "="*60)
print("RESPONDE ESTAS PREGUNTAS:")
print("="*60)
print("1. ¿Qué filtros tienes activos en la pantalla?")
print("2. ¿Qué mensaje aparece cuando subes el archivo?")
print("3. ¿Puedes crear un movimiento manualmente?")
print("4. ¿Hay errores en la consola del navegador (F12)?")
print("5. ¿Aparece tu propiedad creada en el filtro?")

print("\nCon estas respuestas podremos identificar exactamente el problema.")

if __name__ == "__main__":
    pass