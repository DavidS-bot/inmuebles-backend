#!/usr/bin/env python3
"""
Script para tomar screenshots manuales con pyautogui
Alternativa cuando Selenium no está disponible
"""

import time
import os
import webbrowser
from PIL import Image
import io

def take_manual_screenshots():
    """Tomar screenshots manuales del navegador"""
    
    # URLs principales a capturar
    urls = [
        ('http://localhost:3000/login', '01_login.png'),
        ('http://localhost:3000/financial-agent', '02_dashboard_principal.png'),
        ('http://localhost:3000/financial-agent/movements', '03_gestion_movimientos.png'),
        ('http://localhost:3000/financial-agent/analytics', '04_analytics_dashboard.png'),
        ('http://localhost:3000/financial-agent/contracts', '05_gestion_contratos.png'),
    ]
    
    screenshot_dir = r"C:\Users\davsa\inmuebles\backend\screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    print("INSTRUCCIONES PARA SCREENSHOTS MANUALES:")
    print("="*50)
    print("1. Este script abrirá cada URL en tu navegador")
    print("2. Espera 5 segundos entre cada URL")
    print("3. Asegúrate de que el navegador esté visible y maximizado")
    print("4. Presiona Enter para comenzar...")
    
    input()
    
    for url, filename in urls:
        print(f"\nAbriendo: {url}")
        webbrowser.open(url)
        
        print(f"Esperando 5 segundos para que cargue...")
        time.sleep(5)
        
        print(f"AHORA: Toma screenshot manualmente y guárdalo como: {filename}")
        print("Presiona Enter cuando hayas guardado el screenshot...")
        input()
    
    print("\n¡Screenshots manuales completados!")
    print("Verifica que todos los archivos estén en:", screenshot_dir)

def create_sample_screenshots():
    """Crear screenshots de muestra usando HTML simple"""
    
    screenshot_dir = r"C:\Users\davsa\inmuebles\backend\screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    # Crear HTML de muestra para demostrar las páginas
    sample_pages = [
        {
            'filename': 'sample_login.html',
            'title': 'Login - Aplicación Inmuebles',
            'content': '''
            <div style="max-width: 400px; margin: 50px auto; padding: 40px; border: 1px solid #ddd; border-radius: 8px; font-family: Arial;">
                <h2 style="text-align: center; color: #333;">🏠 Inmuebles</h2>
                <h3 style="text-align: center; color: #666;">Iniciar Sesión</h3>
                <form style="margin-top: 30px;">
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: bold;">Usuario:</label>
                        <input type="text" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px;">
                    </div>
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: bold;">Contraseña:</label>
                        <input type="password" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px;">
                    </div>
                    <button type="submit" style="width: 100%; padding: 12px; background: #3b82f6; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer;">
                        Iniciar Sesión
                    </button>
                </form>
            </div>
            '''
        },
        {
            'filename': 'sample_dashboard.html',
            'title': 'Dashboard - Agente Financiero',
            'content': '''
            <div style="font-family: Arial; padding: 20px; background: #f8f9fa;">
                <header style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h1 style="margin: 0; color: #1f2937;">📊 Agente Financiero</h1>
                    <p style="margin: 5px 0 0 0; color: #6b7280;">Dashboard Principal - 2025</p>
                </header>
                
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px;">
                    <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #22c55e;">
                        <h3 style="margin: 0 0 10px 0; color: #16a34a;">€15,240</h3>
                        <p style="margin: 0; color: #6b7280; font-size: 14px;">Ingresos Totales</p>
                    </div>
                    <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #ef4444;">
                        <h3 style="margin: 0 0 10px 0; color: #dc2626;">€8,750</h3>
                        <p style="margin: 0; color: #6b7280; font-size: 14px;">Gastos Totales</p>
                    </div>
                    <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #3b82f6;">
                        <h3 style="margin: 0 0 10px 0; color: #2563eb;">€6,490</h3>
                        <p style="margin: 0; color: #6b7280; font-size: 14px;">Cash Flow Neto</p>
                    </div>
                    <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #8b5cf6;">
                        <h3 style="margin: 0 0 10px 0; color: #7c3aed;">8.2%</h3>
                        <p style="margin: 0; color: #6b7280; font-size: 14px;">ROI Anual</p>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h3 style="margin: 0 0 15px 0; color: #1f2937;">🏠 Mis Propiedades</h3>
                        <div style="margin-bottom: 10px; padding: 10px; background: #f3f4f6; border-radius: 4px;">
                            <strong>Aranguren, 68</strong> - €650/mes
                        </div>
                        <div style="margin-bottom: 10px; padding: 10px; background: #f3f4f6; border-radius: 4px;">
                            <strong>Lago de Enol, 1</strong> - €720/mes
                        </div>
                        <div style="margin-bottom: 10px; padding: 10px; background: #f3f4f6; border-radius: 4px;">
                            <strong>Platón, 30</strong> - €580/mes
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h3 style="margin: 0 0 15px 0; color: #1f2937;">📈 Acciones Rápidas</h3>
                        <div style="margin-bottom: 10px;">
                            <button style="width: 100%; padding: 12px; background: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer; margin-bottom: 8px;">
                                💰 Gestionar Movimientos
                            </button>
                            <button style="width: 100%; padding: 12px; background: #10b981; color: white; border: none; border-radius: 4px; cursor: pointer; margin-bottom: 8px;">
                                📊 Ver Analytics
                            </button>
                            <button style="width: 100%; padding: 12px; background: #f59e0b; color: white; border: none; border-radius: 4px; cursor: pointer;">
                                📋 Gestionar Contratos
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            '''
        }
    ]
    
    # Crear archivos HTML de muestra
    for page in sample_pages:
        file_path = os.path.join(screenshot_dir, page['filename'])
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f'''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page['title']}</title>
</head>
<body style="margin: 0; padding: 20px; background: #f3f4f6;">
    {page['content']}
</body>
</html>
            ''')
    
    print(f"Archivos HTML de muestra creados en: {screenshot_dir}")
    print("Puedes abrir estos archivos en tu navegador y tomar screenshots manuales:")
    
    for page in sample_pages:
        file_path = os.path.join(screenshot_dir, page['filename'])
        print(f"- {page['filename']} - {page['title']}")

if __name__ == "__main__":
    print("Herramientas para Screenshots de la Aplicación")
    print("="*50)
    print("1. Crear archivos HTML de muestra")
    print("2. Guía para screenshots manuales")
    print("3. Salir")
    
    choice = input("\nElige una opción (1-3): ").strip()
    
    if choice == "1":
        create_sample_screenshots()
        print("\n¡Archivos de muestra creados!")
        print("Abre los archivos HTML en tu navegador para ver ejemplos visuales.")
        
    elif choice == "2":
        take_manual_screenshots()
        
    else:
        print("Script terminado.")
        
    print(f"\nRecuerda: La aplicación debe estar corriendo en localhost:3000")
    print(f"Directorio de screenshots: C:\\Users\\davsa\\inmuebles\\backend\\screenshots")