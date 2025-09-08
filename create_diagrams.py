#!/usr/bin/env python3
"""
Script para crear diagramas visuales de la estructura de la aplicación
Genera diagramas de arquitectura, flujo de datos y estructura de navegación
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

def create_architecture_diagram():
    """Crear diagrama de arquitectura del sistema"""
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Colores
    frontend_color = '#3b82f6'  # Azul
    backend_color = '#ef4444'   # Rojo
    db_color = '#22c55e'        # Verde
    external_color = '#f59e0b'  # Amarillo
    
    # Frontend Layer
    frontend_box = FancyBboxPatch((0.5, 6), 3, 1.5, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=frontend_color, 
                                  edgecolor='black', 
                                  alpha=0.7)
    ax.add_patch(frontend_box)
    ax.text(2, 6.75, 'FRONTEND\n(Next.js + React + TypeScript)\nVercel Deployment', 
            ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    
    # Backend Layer
    backend_box = FancyBboxPatch((0.5, 4), 3, 1.5, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=backend_color, 
                                 edgecolor='black', 
                                 alpha=0.7)
    ax.add_patch(backend_box)
    ax.text(2, 4.75, 'BACKEND API\n(FastAPI + Python)\nRender/Railway Deployment', 
            ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    
    # Database Layer
    db_box = FancyBboxPatch((0.5, 2), 3, 1.5, 
                            boxstyle="round,pad=0.1", 
                            facecolor=db_color, 
                            edgecolor='black', 
                            alpha=0.7)
    ax.add_patch(db_box)
    ax.text(2, 2.75, 'DATABASE\n(PostgreSQL)\nCloud Hosting', 
            ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    
    # External Services
    external_box = FancyBboxPatch((5.5, 4), 3.5, 1.5, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=external_color, 
                                  edgecolor='black', 
                                  alpha=0.7)
    ax.add_patch(external_box)
    ax.text(7.25, 4.75, 'EXTERNAL SERVICES\n• Bankinter PSD2 API\n• Document Storage\n• Email Services', 
            ha='center', va='center', fontsize=10, fontweight='bold', color='black')
    
    # Arrows
    # Frontend -> Backend
    ax.annotate('', xy=(2, 4), xytext=(2, 6),
                arrowprops=dict(arrowstyle='<->', lw=2, color='black'))
    ax.text(2.3, 5, 'REST API\nJWT Auth', ha='left', va='center', fontsize=8)
    
    # Backend -> Database
    ax.annotate('', xy=(2, 2), xytext=(2, 4),
                arrowprops=dict(arrowstyle='<->', lw=2, color='black'))
    ax.text(2.3, 3, 'SQLAlchemy\nORM', ha='left', va='center', fontsize=8)
    
    # Backend -> External
    ax.annotate('', xy=(5.5, 4.75), xytext=(3.5, 4.75),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(4.5, 5, 'HTTP\nRequests', ha='center', va='center', fontsize=8)
    
    # Title
    ax.text(5, 7.5, 'ARQUITECTURA DEL SISTEMA - APLICACIÓN INMUEBLES', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(r'C:\Users\davsa\inmuebles\backend\diagrama_arquitectura.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Diagrama de arquitectura creado: diagrama_arquitectura.png")

def create_navigation_structure():
    """Crear diagrama de estructura de navegación"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Colores para diferentes niveles
    level1_color = '#1e40af'  # Azul oscuro
    level2_color = '#3b82f6'  # Azul medio
    level3_color = '#93c5fd'  # Azul claro
    
    # Root - Home
    home_box = FancyBboxPatch((5.5, 9), 1, 0.6, 
                              boxstyle="round,pad=0.05", 
                              facecolor=level1_color, 
                              edgecolor='black', 
                              alpha=0.8)
    ax.add_patch(home_box)
    ax.text(6, 9.3, 'HOME\n/', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    
    # Main sections
    sections = [
        {'name': 'LOGIN', 'route': '/login', 'pos': (1, 7.5)},
        {'name': 'DASHBOARD', 'route': '/dashboard', 'pos': (5, 7.5)},
        {'name': 'FINANCIAL\nAGENT', 'route': '/financial-agent', 'pos': (9, 7.5)}
    ]
    
    for section in sections:
        box = FancyBboxPatch((section['pos'][0]-0.5, section['pos'][1]-0.3), 1, 0.6, 
                             boxstyle="round,pad=0.05", 
                             facecolor=level2_color, 
                             edgecolor='black', 
                             alpha=0.8)
        ax.add_patch(box)
        ax.text(section['pos'][0], section['pos'][1], f"{section['name']}\n{section['route']}", 
                ha='center', va='center', fontsize=8, fontweight='bold', color='white')
        
        # Connection to home
        ax.plot([6, section['pos'][0]], [9, section['pos'][1]+0.3], 'k-', alpha=0.6)
    
    # Financial Agent subsections
    fa_subsections = [
        {'name': 'MOVEMENTS', 'route': '/movements', 'pos': (1, 5.5)},
        {'name': 'ANALYTICS', 'route': '/analytics', 'pos': (3, 5.5)},
        {'name': 'CONTRACTS', 'route': '/contracts', 'pos': (5, 5.5)},
        {'name': 'RULES', 'route': '/rules', 'pos': (7, 5.5)},
        {'name': 'INTEGRATIONS', 'route': '/integrations', 'pos': (9, 5.5)},
        {'name': 'EURIBOR', 'route': '/euribor', 'pos': (11, 5.5)},
        {'name': 'CALCULATOR', 'route': '/mortgage-calculator', 'pos': (1, 4)},
        {'name': 'DOCUMENTS', 'route': '/documents', 'pos': (3, 4)},
        {'name': 'NOTIFICATIONS', 'route': '/notifications', 'pos': (5, 4)},
        {'name': 'TAX ASSISTANT', 'route': '/tax-assistant', 'pos': (7, 4)},
        {'name': 'CLASSIFIER', 'route': '/smart-classifier', 'pos': (9, 4)}
    ]
    
    for subsection in fa_subsections:
        box = FancyBboxPatch((subsection['pos'][0]-0.4, subsection['pos'][1]-0.25), 0.8, 0.5, 
                             boxstyle="round,pad=0.03", 
                             facecolor=level3_color, 
                             edgecolor='black', 
                             alpha=0.8)
        ax.add_patch(box)
        ax.text(subsection['pos'][0], subsection['pos'][1], f"{subsection['name']}\n{subsection['route']}", 
                ha='center', va='center', fontsize=7, color='black')
        
        # Connection to Financial Agent
        ax.plot([9, subsection['pos'][0]], [7.2, subsection['pos'][1]+0.25], 'k-', alpha=0.4)
    
    # Property specific routes
    property_box = FancyBboxPatch((5, 2.5), 2, 0.6, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor='#dc2626', 
                                  edgecolor='black', 
                                  alpha=0.8)
    ax.add_patch(property_box)
    ax.text(6, 2.8, 'PROPERTY [ID]\n/property/[id]', 
            ha='center', va='center', fontsize=8, fontweight='bold', color='white')
    
    # Property subsections
    prop_subsections = [
        {'name': 'REPORTS', 'route': '/reports', 'pos': (2, 1.5)},
        {'name': 'MORTGAGE', 'route': '/mortgage', 'pos': (4, 1.5)},
        {'name': 'RULES', 'route': '/rules', 'pos': (6, 1.5)},
        {'name': 'CONTRACTS', 'route': '/contracts/new', 'pos': (8, 1.5)}
    ]
    
    for subsection in prop_subsections:
        box = FancyBboxPatch((subsection['pos'][0]-0.4, subsection['pos'][1]-0.25), 0.8, 0.5, 
                             boxstyle="round,pad=0.03", 
                             facecolor='#fca5a5', 
                             edgecolor='black', 
                             alpha=0.8)
        ax.add_patch(box)
        ax.text(subsection['pos'][0], subsection['pos'][1], f"{subsection['name']}\n{subsection['route']}", 
                ha='center', va='center', fontsize=7, color='black')
        
        # Connection to Property
        ax.plot([6, subsection['pos'][0]], [2.5, subsection['pos'][1]+0.25], 'k-', alpha=0.4)
    
    # Connection from FA to Property
    ax.plot([9, 6], [7.2, 3.1], 'k-', alpha=0.6)
    
    # Title
    ax.text(6, 9.8, 'ESTRUCTURA DE NAVEGACIÓN - APLICACIÓN INMUEBLES', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Legend
    legend_elements = [
        mpatches.Rectangle((0, 0), 1, 1, facecolor=level1_color, alpha=0.8, label='Nivel Principal'),
        mpatches.Rectangle((0, 0), 1, 1, facecolor=level2_color, alpha=0.8, label='Módulos Principales'),
        mpatches.Rectangle((0, 0), 1, 1, facecolor=level3_color, alpha=0.8, label='Funcionalidades'),
        mpatches.Rectangle((0, 0), 1, 1, facecolor='#dc2626', alpha=0.8, label='Rutas Dinámicas')
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))
    
    plt.tight_layout()
    plt.savefig(r'C:\Users\davsa\inmuebles\backend\diagrama_navegacion.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Diagrama de navegación creado: diagrama_navegacion.png")

def create_data_flow_diagram():
    """Crear diagrama de flujo de datos"""
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # User
    user_box = FancyBboxPatch((0.5, 6.5), 1.5, 1, 
                              boxstyle="round,pad=0.1", 
                              facecolor='#8b5cf6', 
                              edgecolor='black', 
                              alpha=0.8)
    ax.add_patch(user_box)
    ax.text(1.25, 7, 'USUARIO', ha='center', va='center', 
            fontsize=11, fontweight='bold', color='white')
    
    # Frontend
    frontend_box = FancyBboxPatch((3.5, 6.5), 2, 1, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='#3b82f6', 
                                  edgecolor='black', 
                                  alpha=0.8)
    ax.add_patch(frontend_box)
    ax.text(4.5, 7, 'FRONTEND\n(React/Next.js)', ha='center', va='center', 
            fontsize=10, fontweight='bold', color='white')
    
    # Backend API
    backend_box = FancyBboxPatch((7, 6.5), 2, 1, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#ef4444', 
                                 edgecolor='black', 
                                 alpha=0.8)
    ax.add_patch(backend_box)
    ax.text(8, 7, 'BACKEND\n(FastAPI)', ha='center', va='center', 
            fontsize=10, fontweight='bold', color='white')
    
    # Database
    db_box = FancyBboxPatch((7, 4.5), 2, 1, 
                            boxstyle="round,pad=0.1", 
                            facecolor='#22c55e', 
                            edgecolor='black', 
                            alpha=0.8)
    ax.add_patch(db_box)
    ax.text(8, 5, 'DATABASE\n(PostgreSQL)', ha='center', va='center', 
            fontsize=10, fontweight='bold', color='white')
    
    # External APIs
    external_box = FancyBboxPatch((4, 4.5), 2, 1, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='#f59e0b', 
                                  edgecolor='black', 
                                  alpha=0.8)
    ax.add_patch(external_box)
    ax.text(5, 5, 'BANKINTER\nAPI (PSD2)', ha='center', va='center', 
            fontsize=10, fontweight='bold', color='black')
    
    # Classification Engine
    ai_box = FancyBboxPatch((1, 4.5), 2, 1, 
                            boxstyle="round,pad=0.1", 
                            facecolor='#a855f7', 
                            edgecolor='black', 
                            alpha=0.8)
    ax.add_patch(ai_box)
    ax.text(2, 5, 'CLASIFICADOR\nINTELIGENTE', ha='center', va='center', 
            fontsize=10, fontweight='bold', color='white')
    
    # Analytics Engine
    analytics_box = FancyBboxPatch((4, 2.5), 2, 1, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='#06b6d4', 
                                   edgecolor='black', 
                                   alpha=0.8)
    ax.add_patch(analytics_box)
    ax.text(5, 3, 'MOTOR DE\nANALYTICS', ha='center', va='center', 
            fontsize=10, fontweight='bold', color='white')
    
    # Arrows and labels
    # User -> Frontend
    ax.annotate('', xy=(3.5, 7), xytext=(2, 7),
                arrowprops=dict(arrowstyle='<->', lw=2, color='black'))
    ax.text(2.75, 7.3, 'Interacción\nUI/UX', ha='center', va='bottom', fontsize=8)
    
    # Frontend -> Backend
    ax.annotate('', xy=(7, 7), xytext=(5.5, 7),
                arrowprops=dict(arrowstyle='<->', lw=2, color='black'))
    ax.text(6.25, 7.3, 'REST API\nJSON', ha='center', va='bottom', fontsize=8)
    
    # Backend -> Database
    ax.annotate('', xy=(8, 4.5), xytext=(8, 6.5),
                arrowprops=dict(arrowstyle='<->', lw=2, color='black'))
    ax.text(8.5, 5.5, 'SQL\nQueries', ha='left', va='center', fontsize=8)
    
    # Backend -> External API
    ax.annotate('', xy=(6, 5), xytext=(7, 6.5),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(6.2, 5.8, 'HTTP\nRequests', ha='left', va='center', fontsize=8)
    
    # Backend -> AI
    ax.annotate('', xy=(3, 5), xytext=(7, 6.5),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(4.5, 6, 'Procesamiento\nTexto', ha='center', va='center', fontsize=8)
    
    # Backend -> Analytics
    ax.annotate('', xy=(5, 2.5), xytext=(8, 4.5),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(6.8, 3.2, 'Cálculos\nMétricas', ha='center', va='center', fontsize=8)
    
    # Title
    ax.text(5, 7.8, 'FLUJO DE DATOS - APLICACIÓN INMUEBLES', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(r'C:\Users\davsa\inmuebles\backend\diagrama_flujo_datos.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Diagrama de flujo de datos creado: diagrama_flujo_datos.png")

if __name__ == "__main__":
    print("Creando diagramas de la aplicación...")
    
    try:
        create_architecture_diagram()
        create_navigation_structure()
        create_data_flow_diagram()
        
        print("\n¡Todos los diagramas han sido creados exitosamente!")
        print("Archivos generados:")
        print("- diagrama_arquitectura.png")
        print("- diagrama_navegacion.png")
        print("- diagrama_flujo_datos.png")
        
    except Exception as e:
        print(f"Error al crear diagramas: {str(e)}")