#!/usr/bin/env python3
"""
Diagnóstico específico de los errores de API encontrados
"""

print("DIAGNÓSTICO DE ERRORES DE API")
print("=" * 50)

print("\nERRORES IDENTIFICADOS:")
print("1. Error 405 (Method Not Allowed) - al cargar movimientos")
print("2. Error 401 (Unauthorized) - en manifest.json")

print("\n" + "="*50)
print("ANÁLISIS DEL PROBLEMA:")
print("="*50)

print("\nERROR 405 - Method Not Allowed:")
print("- La interfaz web está intentando usar un método HTTP incorrecto")
print("- Por ejemplo: usando POST cuando debería usar GET")
print("- O el endpoint no existe en el backend")

print("\nERROR 401 - Unauthorized:")
print("- Problemas de autenticación")
print("- Token de sesión expirado o inválido")
print("- Usuario no autenticado correctamente")

print("\n" + "="*50)
print("CAUSAS PROBABLES:")
print("="*50)

print("\n1. PROBLEMA DE AUTENTICACIÓN:")
print("   - No estás realmente logueado")
print("   - El token de sesión expiró")
print("   - Problema con las credenciales")

print("\n2. PROBLEMA DE CONFIGURACIÓN DE API:")
print("   - La interfaz web apunta a endpoints incorrectos")
print("   - Diferencia entre desarrollo y producción")
print("   - CORS o configuración de métodos HTTP")

print("\n3. PROBLEMA DE PERMISOS:")
print("   - Tu usuario no tiene permisos para ver movimientos")
print("   - Falta configuración de roles/permisos")

print("\n" + "="*50)
print("SOLUCIONES A PROBAR:")
print("="*50)

print("\nSOLUCIÓN 1 - Re-login completo:")
print("1. Cierra completamente el navegador")
print("2. Abre nueva ventana")
print("3. Ve a https://inmuebles-david.vercel.app")
print("4. Haz login de nuevo")
print("5. Ve a movimientos financieros")

print("\nSOLUCIÓN 2 - Limpiar datos del navegador:")
print("1. Presiona Ctrl+Shift+Delete")
print("2. Selecciona 'Cookies y datos de sitios'")
print("3. Selecciona 'Solo para inmuebles-david.vercel.app'")
print("4. Haz clic en 'Eliminar'")
print("5. Recarga la página y vuelve a loguearte")

print("\nSOLUCIÓN 3 - Modo incógnito:")
print("1. Abre ventana de incógnito (Ctrl+Shift+N)")
print("2. Ve a https://inmuebles-david.vercel.app")
print("3. Haz login")
print("4. Prueba crear/ver movimientos")

print("\nSOLUCIÓN 4 - Verificar permisos de usuario:")
print("¿Con qué credenciales te estás logueando?")
print("- ¿Es un usuario administrador?")
print("- ¿Tiene permisos para crear/ver movimientos?")
print("- ¿Es el mismo usuario con el que configuramos el sistema?")

print("\n" + "="*50)
print("TEST RÁPIDO:")
print("="*50)
print("1. Después de hacer login, presiona F12")
print("2. Ve a la pestaña 'Network'")
print("3. Recarga la página de movimientos")
print("4. Mira las requests que aparecen:")
print("   - ¿Hay requests a /financial-movements/?")
print("   - ¿Cuál es el status de esas requests?")
print("   - ¿Aparece Authorization: Bearer token en los headers?")

print("\n" + "="*50)
print("SIGUIENTE PASO:")
print("="*50)
print("Prueba la SOLUCIÓN 1 (re-login completo) primero.")
print("Si sigue dando error 401/405, el problema es de configuración del backend.")
print("En ese caso necesitaremos revisar la configuración de la aplicación.")

if __name__ == "__main__":
    pass