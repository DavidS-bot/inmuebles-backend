#!/usr/bin/env python3
"""
Asistente de Registro PSD2
=========================

Asistente interactivo para el proceso de registro como TPP
en la plataforma Redsys para acceso a APIs PSD2 de Bankinter.
"""

import webbrowser
import datetime
import os

class RegistroPSD2Assistant:
    """Asistente para el proceso de registro PSD2"""
    
    def __init__(self):
        self.user_data = {}
        
    def welcome(self):
        """Pantalla de bienvenida"""
        print("="*60)
        print("🏦 ASISTENTE REGISTRO API PSD2 BANKINTER")
        print("="*60)
        print()
        print("Este asistente te guiará paso a paso para:")
        print("✅ Registrarte como Third Party Provider (TPP)")
        print("✅ Obtener acceso al sandbox de Redsys")
        print("✅ Configurar tu aplicación para Bankinter")
        print("✅ Generar emails y documentos necesarios")
        print()
        print("Tiempo estimado total: 5-7 días")
        print("Tiempo estimado hoy: 20 minutos")
        print()
        
    def collect_user_info(self):
        """Recopilar información del usuario"""
        print("📝 PASO 1: INFORMACIÓN BÁSICA")
        print("-" * 40)
        
        self.user_data['nombre'] = input("Nombre completo: ").strip()
        self.user_data['empresa'] = input("Nombre de empresa (o tu nombre si es personal): ").strip()
        self.user_data['email'] = input("Email de contacto: ").strip()
        self.user_data['telefono'] = input("Teléfono: ").strip()
        self.user_data['direccion'] = input("Dirección completa: ").strip()
        
        print("\n✅ Información recopilada correctamente")
        
    def generate_registration_email(self):
        """Generar email de solicitud"""
        email_content = f"""
Asunto: TPP support tool registration

Estimados,

Solicito acceso al sandbox de PSD2 para desarrollo de aplicación de gestión inmobiliaria.

DATOS DE LA EMPRESA:
- Nombre: {self.user_data['empresa']}
- Email: {self.user_data['email']}  
- Teléfono: {self.user_data['telefono']}
- Dirección: {self.user_data['direccion']}

DATOS TÉCNICOS:
- Tipo de servicio: Account Information Service Provider (AISP)
- Finalidad: Gestión automática de transacciones bancarias para gestión inmobiliaria
- Banco objetivo: Bankinter
- Entorno: Sandbox inicialmente, producción posteriormente

DATOS DEL DESARROLLADOR:
- Nombre: {self.user_data['nombre']}
- Experiencia: Desarrollo de APIs bancarias y aplicaciones de gestión
- Framework: Python + FastAPI
- Casos de uso: Descarga automática de movimientos bancarios, conciliación de pagos de alquiler

JUSTIFICACIÓN DEL PROYECTO:
Desarrollo de una aplicación de gestión inmobiliaria que requiere acceso automático 
a transacciones bancarias para:
- Conciliación automática de pagos de alquiler
- Gestión de gastos e ingresos de propiedades
- Generación de informes financieros

Cumplo con todos los requisitos técnicos y de seguridad establecidos por PSD2.

Quedo a la espera de su respuesta para proceder con la configuración.

Saludos cordiales,
{self.user_data['nombre']}
{self.user_data['email']}
{self.user_data['telefono']}
"""
        
        # Guardar email en archivo
        filename = f"email_solicitud_psd2_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(email_content)
        
        print(f"\n📧 EMAIL GENERADO: {filename}")
        print("-" * 50)
        print("Para: psd2.sandbox.soporte@redsys.es")
        print("Asunto: TPP support tool registration")
        print(f"Contenido guardado en: {filename}")
        print()
        print("⚠️  IMPORTANTE:")
        print("- Copia el contenido del archivo")
        print("- Envía desde tu email personal/empresarial")
        print("- El asunto DEBE ser exactamente: TPP support tool registration")
        
        return filename
    
    def open_registration_links(self):
        """Abrir enlaces relevantes"""
        print("\n🌐 ABRIENDO ENLACES IMPORTANTES...")
        
        links = [
            ("Portal Principal Redsys", "https://market.apis-i.redsys.es/psd2/xs2a"),
            ("Guía Web Redsys", "https://market.apis-i.redsys.es/psd2/xs2a/guia"),
            ("APIs Bankinter", "https://market.apis-i.redsys.es/psd2/xs2a/nodos/bankinter")
        ]
        
        for name, url in links:
            try:
                print(f"Abriendo: {name}")
                webbrowser.open(url)
            except:
                print(f"❌ No se pudo abrir: {url}")
                print(f"   Copia y pega manualmente: {url}")
        
        print("\n✅ Enlaces abiertos en tu navegador")
        
    def create_config_template(self):
        """Crear template de configuración"""
        config_content = f"""
# CONFIGURACIÓN API PSD2 BANKINTER
# ================================

# Datos de registro
EMPRESA = "{self.user_data['empresa']}"
EMAIL = "{self.user_data['email']}"
TELEFONO = "{self.user_data['telefono']}"

# Credenciales (completar cuando las recibas)
CLIENT_ID = "TU_CLIENT_ID_AQUI"
CLIENT_SECRET = "TU_CLIENT_SECRET_AQUI"

# URLs del entorno sandbox
SANDBOX_API_URL = "https://apis-i.redsys.es:20443/psd2/xs2a/api-entrada-xs2a/services/bankinter/v1.1"
SANDBOX_OAUTH_URL = "https://apis-i.redsys.es:20443/psd2/xs2a/api-oauth-xs2a/services/rest/bankinter"

# URLs de producción (para el futuro)
PROD_API_URL = "https://apis-i.redsys.es:20443/psd2/xs2a/api-entrada-xs2a/services/bankinter/v1.1"
PROD_OAUTH_URL = "https://apis-i.redsys.es:20443/psd2/xs2a/api-oauth-xs2a/services/rest/bankinter"

# Configuración de la aplicación
APP_NAME = "Inmuebles Management App"
APP_DESCRIPTION = "Aplicación de gestión inmobiliaria con integración bancaria"
CALLBACK_URL = "http://localhost:8000/callback"

# Fecha de solicitud
FECHA_SOLICITUD = "{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
"""
        
        filename = "config_psd2.py"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"\n⚙️ CONFIGURACIÓN CREADA: {filename}")
        print("Completarás las credenciales cuando recibas respuesta de Redsys")
        
        return filename
    
    def show_next_steps(self):
        """Mostrar próximos pasos"""
        print("\n" + "="*60)
        print("🎯 PRÓXIMOS PASOS")
        print("="*60)
        
        steps = [
            ("HOY", [
                "✅ 1. Crear cuenta en https://market.apis-i.redsys.es",
                "✅ 2. Enviar el email generado a: psd2.sandbox.soporte@redsys.es", 
                "✅ 3. Guardar este asistente para cuando recibas respuesta"
            ]),
            ("CUANDO RECIBAS RESPUESTA (1-3 días)", [
                "📧 4. Seguir instrucciones del email de Redsys",
                "🔧 5. Registrar tu aplicación en el portal",
                "🔑 6. Obtener CLIENT_ID y CLIENT_SECRET",
                "⚙️ 7. Completar config_psd2.py con las credenciales"
            ]),
            ("PRUEBAS Y PRODUCCIÓN", [
                "🧪 8. Ejecutar pruebas en sandbox",
                "✅ 9. Solicitar upgrade a producción",
                "🚀 10. ¡Usar la API oficialmente!"
            ])
        ]
        
        for phase, phase_steps in steps:
            print(f"\n🕐 {phase}:")
            for step in phase_steps:
                print(f"   {step}")
        
        print(f"\n📱 CONTACTO DE SOPORTE:")
        print(f"   Email: psd2.sandbox.soporte@redsys.es")
        print(f"   Asunto: TPP support tool registration")
        
        print(f"\n⏰ TIEMPO ESTIMADO TOTAL: 5-7 días")
    
    def create_checklist(self):
        """Crear checklist de seguimiento"""
        checklist_content = f"""
# ✅ CHECKLIST REGISTRO PSD2 BANKINTER
# Creado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📋 FASE 1: SOLICITUD INICIAL
- [ ] Crear cuenta en https://market.apis-i.redsys.es/psd2/xs2a
- [ ] Enviar email a: psd2.sandbox.soporte@redsys.es
- [ ] Asunto: "TPP support tool registration"
- [ ] Incluir datos generados por el asistente

## 📋 FASE 2: CONFIGURACIÓN (Tras recibir respuesta)
- [ ] Login en el portal Redsys
- [ ] Registrar aplicación: "Inmuebles Management App"
- [ ] Obtener CLIENT_ID
- [ ] Obtener CLIENT_SECRET
- [ ] Completar archivo config_psd2.py

## 📋 FASE 3: PRUEBAS SANDBOX
- [ ] Ejecutar: python bankinter_api_client.py
- [ ] Probar autenticación OAuth2
- [ ] Probar creación de consentimiento
- [ ] Probar obtención de cuentas
- [ ] Probar descarga de transacciones

## 📋 FASE 4: PRODUCCIÓN
- [ ] Solicitar upgrade a producción
- [ ] Configurar certificado SSL propio
- [ ] Pruebas finales con datos reales
- [ ] Integración con sistema inmobiliario

## 📞 CONTACTOS IMPORTANTES
- Soporte: psd2.sandbox.soporte@redsys.es
- Portal: https://market.apis-i.redsys.es/psd2/xs2a
- Documentación: https://market.apis-i.redsys.es/psd2/xs2a/guia

## 📊 PROGRESO
Fecha de inicio: {datetime.datetime.now().strftime('%Y-%m-%d')}
Estado actual: Solicitud inicial
Próximo paso: Enviar email de solicitud

---
Actualiza este archivo según vayas completando los pasos.
"""
        
        filename = "checklist_psd2.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(checklist_content)
        
        print(f"\n📋 CHECKLIST CREADO: {filename}")
        print("Úsalo para hacer seguimiento del progreso")
        
        return filename
    
    def run(self):
        """Ejecutar asistente completo"""
        self.welcome()
        
        # Recopilar información
        self.collect_user_info()
        
        # Generar documentos
        email_file = self.generate_registration_email()
        config_file = self.create_config_template()
        checklist_file = self.create_checklist()
        
        # Abrir enlaces
        self.open_registration_links()
        
        # Mostrar próximos pasos
        self.show_next_steps()
        
        print("\n" + "="*60)
        print("🎉 ASISTENTE COMPLETADO")
        print("="*60)
        print(f"📧 Email generado: {email_file}")
        print(f"⚙️ Config template: {config_file}")
        print(f"📋 Checklist: {checklist_file}")
        print()
        print("⏰ Próximo paso: Envía el email y espera respuesta (1-3 días)")
        print("🔄 Vuelve a ejecutar este script cuando recibas las credenciales")


def main():
    """Función principal"""
    try:
        assistant = RegistroPSD2Assistant()
        assistant.run()
        
        print("\n¿Quieres abrir el email generado para copiarlo? (s/n): ", end="")
        try:
            response = input().strip().lower()
            if response in ['s', 'si', 'yes', 'y']:
                # Buscar el archivo de email más reciente
                email_files = [f for f in os.listdir('.') if f.startswith('email_solicitud_psd2_')]
                if email_files:
                    latest_email = sorted(email_files)[-1]
                    os.startfile(latest_email)  # Windows
                    print(f"✅ Abriendo {latest_email}")
        except:
            pass
        
    except KeyboardInterrupt:
        print("\n\n👋 Proceso cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Contacta con soporte si el problema persiste")


if __name__ == "__main__":
    main()