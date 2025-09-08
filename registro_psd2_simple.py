#!/usr/bin/env python3
"""
Registro PSD2 Simplificado
=========================
"""

import webbrowser
import datetime
import os

def main():
    print("="*60)
    print("ASISTENTE REGISTRO API PSD2 BANKINTER")
    print("="*60)
    print()
    print("Este asistente te ayudara con:")
    print("[OK] Registrarte como Third Party Provider (TPP)")
    print("[OK] Obtener acceso al sandbox de Redsys")
    print("[OK] Configurar tu aplicacion para Bankinter")
    print()
    
    # Recopilar datos básicos
    print("INFORMACION BASICA:")
    print("-" * 40)
    
    nombre = input("Nombre completo: ").strip() or "David"
    empresa = input("Nombre de empresa: ").strip() or "Gestion Inmobiliaria"
    email = input("Email de contacto: ").strip() or "tu-email@ejemplo.com"
    telefono = input("Telefono: ").strip() or "+34 XXX XXX XXX"
    direccion = input("Direccion: ").strip() or "Tu direccion completa"
    
    # Generar email de solicitud
    email_content = f"""
Asunto: TPP support tool registration

Estimados,

Solicito acceso al sandbox de PSD2 para desarrollo de aplicacion de gestion inmobiliaria.

DATOS DE LA EMPRESA:
- Nombre: {empresa}
- Email: {email}  
- Telefono: {telefono}
- Direccion: {direccion}

DATOS TECNICOS:
- Tipo de servicio: Account Information Service Provider (AISP)
- Finalidad: Gestion automatica de transacciones bancarias para gestion inmobiliaria
- Banco objetivo: Bankinter
- Entorno: Sandbox inicialmente, produccion posteriormente

DATOS DEL DESARROLLADOR:
- Nombre: {nombre}
- Experiencia: Desarrollo de APIs bancarias y aplicaciones de gestion
- Framework: Python + FastAPI
- Casos de uso: Descarga automatica de movimientos bancarios, conciliacion de pagos de alquiler

JUSTIFICACION DEL PROYECTO:
Desarrollo de una aplicacion de gestion inmobiliaria que requiere acceso automatico 
a transacciones bancarias para:
- Conciliacion automatica de pagos de alquiler
- Gestion de gastos e ingresos de propiedades
- Generacion de informes financieros

Cumplo con todos los requisitos tecnicos y de seguridad establecidos por PSD2.

Quedo a la espera de su respuesta para proceder con la configuracion.

Saludos cordiales,
{nombre}
{email}
{telefono}
"""
    
    # Guardar email
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    email_filename = f"email_solicitud_psd2_{timestamp}.txt"
    
    with open(email_filename, 'w', encoding='utf-8') as f:
        f.write(email_content)
    
    print(f"\nEMAIL GENERADO: {email_filename}")
    print("-" * 50)
    print("Para: psd2.sandbox.soporte@redsys.es")
    print("Asunto: TPP support tool registration")
    print()
    
    # Crear configuración
    config_content = f"""# CONFIGURACION PSD2 BANKINTER - {timestamp}

EMPRESA = "{empresa}"
EMAIL = "{email}"
NOMBRE = "{nombre}"

# Completar cuando recibas las credenciales:
CLIENT_ID = "TU_CLIENT_ID_AQUI"
CLIENT_SECRET = "TU_CLIENT_SECRET_AQUI"

# URLs Sandbox
SANDBOX_API = "https://apis-i.redsys.es:20443/psd2/xs2a/api-entrada-xs2a/services/bankinter/v1.1"
SANDBOX_OAUTH = "https://apis-i.redsys.es:20443/psd2/xs2a/api-oauth-xs2a/services/rest/bankinter"
"""
    
    config_filename = "config_psd2.py"
    with open(config_filename, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"CONFIGURACION CREADA: {config_filename}")
    print()
    
    # Abrir enlaces importantes
    print("ABRIENDO ENLACES IMPORTANTES...")
    enlaces = [
        "https://market.apis-i.redsys.es/psd2/xs2a",
        "https://market.apis-i.redsys.es/psd2/xs2a/nodos/bankinter"
    ]
    
    for url in enlaces:
        try:
            webbrowser.open(url)
            print(f"[OK] Abriendo: {url}")
        except:
            print(f"[INFO] Visita manualmente: {url}")
    
    # Próximos pasos
    print("\n" + "="*60)
    print("PROXIMOS PASOS")
    print("="*60)
    print()
    print("PASOS INMEDIATOS (HOY):")
    print("1. Crear cuenta en: https://market.apis-i.redsys.es/psd2/xs2a")
    print(f"2. Enviar email generado ({email_filename}) a: psd2.sandbox.soporte@redsys.es")
    print("3. Asunto EXACTO: TPP support tool registration")
    print()
    print("CUANDO RECIBAS RESPUESTA (1-3 dias):")
    print("4. Seguir instrucciones del email de Redsys")
    print("5. Registrar aplicacion en el portal")
    print("6. Obtener CLIENT_ID y CLIENT_SECRET")
    print("7. Completar archivo config_psd2.py")
    print()
    print("PRUEBAS:")
    print("8. Ejecutar: python bankinter_api_client.py")
    print("9. Probar todas las funcionalidades en sandbox")
    print("10. Solicitar upgrade a produccion")
    print()
    print("TIEMPO ESTIMADO TOTAL: 5-7 dias")
    print()
    print("CONTACTO SOPORTE: psd2.sandbox.soporte@redsys.es")
    
    # Crear checklist simple
    checklist = f"""# CHECKLIST REGISTRO PSD2 - {datetime.datetime.now().strftime('%Y-%m-%d')}

FASE 1 - SOLICITUD:
[ ] Crear cuenta en portal Redsys
[ ] Enviar email de solicitud
[ ] Esperar respuesta (1-3 dias)

FASE 2 - CONFIGURACION:
[ ] Login en portal tras recibir respuesta
[ ] Registrar aplicacion
[ ] Obtener credenciales
[ ] Actualizar config_psd2.py

FASE 3 - PRUEBAS:
[ ] Ejecutar python bankinter_api_client.py
[ ] Probar autenticacion OAuth2
[ ] Probar obtencion de cuentas
[ ] Probar descarga de transacciones

FASE 4 - PRODUCCION:
[ ] Solicitar upgrade
[ ] Configurar SSL
[ ] Pruebas finales
[ ] Integracion completa

Contacto: psd2.sandbox.soporte@redsys.es
Estado: Solicitud inicial
"""
    
    checklist_filename = "checklist_psd2.txt"
    with open(checklist_filename, 'w', encoding='utf-8') as f:
        f.write(checklist)
    
    print(f"CHECKLIST CREADO: {checklist_filename}")
    print()
    print("ARCHIVOS GENERADOS:")
    print(f"- {email_filename} (email para enviar)")
    print(f"- {config_filename} (configuracion)")
    print(f"- {checklist_filename} (seguimiento)")
    print()
    
    # Preguntar si abrir email
    try:
        response = input("Abrir email para copiarlo? (s/n): ").strip().lower()
        if response in ['s', 'si', 'yes', 'y']:
            os.startfile(email_filename)
            print(f"[OK] Abriendo {email_filename}")
    except:
        pass
    
    print("\nPROCESO COMPLETADO!")
    print("Siguiente paso: Envia el email y espera respuesta")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProceso cancelado")
    except Exception as e:
        print(f"\nError: {e}")
        print("Si persiste el problema, usa el procesador manual que ya funciona")