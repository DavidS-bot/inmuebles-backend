import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as patches
from datetime import datetime
import os

# Create PDF document
pdf_filename = 'Inmuebles_Platform_Guide_Claude_AI.pdf'

with PdfPages(pdf_filename) as pdf:
    # Page 1: Cover & Overview
    fig, ax = plt.subplots(figsize=(8.5, 11))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    # Header
    ax.text(5, 12.5, 'PLATAFORMA INMUEBLES', ha='center', va='center', 
            fontsize=24, fontweight='bold', color='#2563eb')
    ax.text(5, 11.8, 'Guía de Referencia para Claude.ai', ha='center', va='center', 
            fontsize=14, style='italic', color='#64748b')
    
    # Description Box
    rect = patches.Rectangle((1, 9), 8, 2.5, linewidth=2, edgecolor='#2563eb', 
                           facecolor='#eff6ff', alpha=0.8)
    ax.add_patch(rect)
    
    ax.text(5, 10.7, 'SISTEMA INTEGRAL DE GESTIÓN', ha='center', va='center', 
            fontsize=14, fontweight='bold', color='#1e40af')
    ax.text(5, 10.2, '• Plataforma completa de inversiones inmobiliarias', ha='center', va='center', 
            fontsize=11, color='#334155')
    ax.text(5, 9.8, '• Integración bancaria automatizada (Bankinter)', ha='center', va='center', 
            fontsize=11, color='#334155')
    ax.text(5, 9.4, '• Análisis financiero avanzado y gestión de contratos', ha='center', va='center', 
            fontsize=11, color='#334155')
    
    # Tech Stack
    ax.text(1, 8.2, 'STACK TECNOLÓGICO', fontsize=14, fontweight='bold', color='#dc2626')
    
    # Backend
    ax.text(1.5, 7.6, 'Backend:', fontsize=12, fontweight='bold', color='#374151')
    ax.text(1.5, 7.2, '• FastAPI (Python) - API REST principal', fontsize=10, color='#4b5563')
    ax.text(1.5, 6.9, '• SQLModel + SQLite - ORM y base de datos', fontsize=10, color='#4b5563')
    ax.text(1.5, 6.6, '• Selenium WebDriver - Scraping bancario', fontsize=10, color='#4b5563')
    ax.text(1.5, 6.3, '• Pandas/NumPy - Análisis financiero', fontsize=10, color='#4b5563')
    
    # Frontend
    ax.text(1.5, 5.8, 'Frontend:', fontsize=12, fontweight='bold', color='#374151')
    ax.text(1.5, 5.4, '• Next.js 14 (React) - App web moderna', fontsize=10, color='#4b5563')
    ax.text(1.5, 5.1, '• TypeScript - Tipado estático', fontsize=10, color='#4b5563')
    ax.text(1.5, 4.8, '• Tailwind CSS - Sistema de diseño', fontsize=10, color='#4b5563')
    ax.text(1.5, 4.5, '• PWA - Aplicación instalable', fontsize=10, color='#4b5563')
    
    # Deployment
    ax.text(1.5, 4.0, 'Deployment:', fontsize=12, fontweight='bold', color='#374151')
    ax.text(1.5, 3.6, '• Frontend: Vercel (inmuebles-web.vercel.app)', fontsize=10, color='#4b5563')
    ax.text(1.5, 3.3, '• Backend: Render (inmuebles-backend-api.onrender.com)', fontsize=10, color='#4b5563')
    
    # Footer
    ax.text(5, 1, f'Generado el {datetime.now().strftime("%d/%m/%Y")} para uso con Claude.ai', 
            ha='center', va='center', fontsize=9, style='italic', color='#6b7280')
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

    # Page 2: Data Models
    fig, ax = plt.subplots(figsize=(8.5, 11))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    ax.text(5, 13, 'MODELOS DE DATOS PRINCIPALES', ha='center', va='center', 
            fontsize=18, fontweight='bold', color='#2563eb')
    
    # Core Models
    y_pos = 12.2
    ax.text(1, y_pos, 'ENTIDADES CORE:', fontsize=14, fontweight='bold', color='#dc2626')
    
    models_data = [
        ('User', 'Usuarios con autenticación JWT'),
        ('Property', 'Propiedades con datos financieros completos'),
        ('FinancialMovement', 'Movimientos bancarios clasificados'),
        ('RentalContract', 'Contratos de alquiler y gestión inquilinos'),
        ('MortgageDetails', 'Hipotecas variables con revisiones'),
        ('ClassificationRule', 'Reglas automáticas de categorización'),
        ('BankConnection', 'Conexiones bancarias (GoCardless)'),
        ('EuriborRate', 'Tasas históricas para hipotecas'),
        ('PaymentRule', 'Configuración de ventanas de pago')
    ]
    
    y_pos = 11.5
    for model, description in models_data:
        ax.text(1.5, y_pos, f'• {model}:', fontsize=11, fontweight='bold', color='#374151')
        ax.text(3.5, y_pos, description, fontsize=10, color='#4b5563')
        y_pos -= 0.4
    
    # Key Relationships
    ax.text(1, 8.5, 'RELACIONES CLAVE:', fontsize=14, fontweight='bold', color='#dc2626')
    relationships = [
        'User → Properties (1:N)',
        'Property → FinancialMovements (1:N)',
        'Property → RentalContracts (1:N)', 
        'Property → MortgageDetails (1:1)',
        'MortgageDetails → MortgageRevisions (1:N)',
        'RentalContract → TenantDocuments (1:N)'
    ]
    
    y_pos = 7.8
    for rel in relationships:
        ax.text(1.5, y_pos, f'• {rel}', fontsize=10, color='#4b5563')
        y_pos -= 0.3
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

    # Page 3: API Endpoints
    fig, ax = plt.subplots(figsize=(8.5, 11))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    ax.text(5, 13, 'ENDPOINTS PRINCIPALES DE LA API', ha='center', va='center', 
            fontsize=18, fontweight='bold', color='#2563eb')
    
    # Endpoints by category
    endpoints_data = [
        ('AUTENTICACIÓN', [
            'POST /auth/login - Login usuario',
            'POST /auth/register - Registro usuario'
        ]),
        ('PROPIEDADES', [
            'GET /properties/ - Listar propiedades',
            'POST /properties/ - Crear propiedad',
            'PUT /properties/{id} - Actualizar propiedad'
        ]),
        ('ANÁLISIS FINANCIERO', [
            'GET /financial-movements/ - Movimientos',
            'POST /financial-movements/upload - Importar',
            'GET /analytics/ - Métricas y análisis',
            'GET /cashflow/ - Flujos de caja'
        ]),
        ('CONTRATOS E HIPOTECAS', [
            'GET /rental-contracts/ - Contratos alquiler',
            'GET /mortgage-details/ - Detalles hipotecas',
            'POST /euribor-rates/ - Tasas Euribor'
        ]),
        ('INTEGRACIÓN BANCARIA', [
            'POST /bankinter-real/scrape - Scraping',
            'GET /bank-integration/ - Estado conexiones',
            'POST /bankinter-upload/ - Upload datos'
        ]),
        ('UTILIDADES', [
            'GET /notifications/ - Notificaciones',
            'POST /classification-rules/ - Reglas',
            'GET /mortgage-calculator/ - Calculadora'
        ])
    ]
    
    y_pos = 12.2
    for category, endpoints in endpoints_data:
        ax.text(1, y_pos, f'{category}:', fontsize=12, fontweight='bold', color='#dc2626')
        y_pos -= 0.3
        for endpoint in endpoints:
            ax.text(1.5, y_pos, f'• {endpoint}', fontsize=9, color='#4b5563')
            y_pos -= 0.25
        y_pos -= 0.1
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

    # Page 4: Development Guide
    fig, ax = plt.subplots(figsize=(8.5, 11))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    ax.text(5, 13, 'GUÍA DE DESARROLLO', ha='center', va='center', 
            fontsize=18, fontweight='bold', color='#2563eb')
    
    # Development commands
    ax.text(1, 12.2, 'COMANDOS PRINCIPALES:', fontsize=14, fontweight='bold', color='#dc2626')
    
    commands = [
        ('Backend Development:', [
            'uvicorn app.main:app --reload --port 8000',
            'python bankinter_auto_download.py',
            'pip install -r requirements.txt'
        ]),
        ('Frontend Development:', [
            'cd inmuebles-web && npm run dev',
            'npm run build && npm run lint',
            'npm install'
        ]),
        ('Deployment:', [
            './deploy-auto.bat',
            './deploy-inmuebles-vercel.bat',
            './deploy-backend-fixed.bat'
        ])
    ]
    
    y_pos = 11.5
    for section, cmds in commands:
        ax.text(1.5, y_pos, section, fontsize=12, fontweight='bold', color='#374151')
        y_pos -= 0.3
        for cmd in cmds:
            ax.text(2, y_pos, f'• {cmd}', fontsize=9, fontfamily='monospace', color='#4b5563')
            y_pos -= 0.25
        y_pos -= 0.2
    
    # Environment Variables
    ax.text(1, 8.5, 'VARIABLES DE ENTORNO:', fontsize=14, fontweight='bold', color='#dc2626')
    env_vars = [
        'BANKINTER_USERNAME=75867185',
        'BANKINTER_PASSWORD=Motoreta123$',
        'DATABASE_URL=sqlite:///./app.db',
        'SECRET_KEY=your-secret-key'
    ]
    
    y_pos = 7.8
    for var in env_vars:
        ax.text(1.5, y_pos, f'• {var}', fontsize=9, fontfamily='monospace', color='#4b5563')
        y_pos -= 0.3
    
    # Key Features
    ax.text(1, 6.5, 'CARACTERÍSTICAS ESPECIALES:', fontsize=14, fontweight='bold', color='#dc2626')
    features = [
        '• Scraping automatizado de Bankinter',
        '• Clasificación inteligente de transacciones', 
        '• Cálculos ROI y rentabilidad automáticos',
        '• Proyecciones hipotecarias con Euribor',
        '• Gestión completa de contratos PDF',
        '• Análisis comparativo de inversiones',
        '• PWA instalable en dispositivos móviles'
    ]
    
    y_pos = 5.8
    for feature in features:
        ax.text(1.5, y_pos, feature, fontsize=10, color='#4b5563')
        y_pos -= 0.3
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

    # Page 5: Prompt Templates
    fig, ax = plt.subplots(figsize=(8.5, 11))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    ax.text(5, 13, 'TEMPLATES DE PROMPTS PARA CLAUDE.AI', ha='center', va='center', 
            fontsize=18, fontweight='bold', color='#2563eb')
    
    # Prompt templates
    prompts = [
        ('NUEVO ENDPOINT:', 
         'Crear endpoint POST /[recurso]/ en FastAPI para [funcionalidad]. Usar modelo [Modelo] de models.py. Incluir validación y autenticación JWT.'),
        
        ('COMPONENTE REACT:', 
         'Crear componente React TypeScript para [funcionalidad] usando Tailwind CSS. Integrar con API endpoint /[ruta]/. Responsive design.'),
        
        ('ANÁLISIS FINANCIERO:', 
         'Implementar cálculo de [métrica] en analytics.py. Usar datos de FinancialMovement y Property. Devolver JSON con métricas.'),
        
        ('SCRAPING BANCARIO:', 
         'Mejorar bankinter_client.py para extraer [datos]. Usar Selenium WebDriver. Clasificar automáticamente con ClassificationRule.'),
        
        ('BASE DE DATOS:', 
         'Añadir campo [campo] al modelo [Modelo] en models.py. Crear migración y actualizar endpoints relacionados.'),
        
        ('FRONTEND DASHBOARD:', 
         'Crear página dashboard para [funcionalidad] en app/(protected)/[ruta]/. Usar contextos y hooks existentes.')
    ]
    
    y_pos = 12.2
    for title, template in prompts:
        ax.text(1, y_pos, title, fontsize=11, fontweight='bold', color='#dc2626')
        y_pos -= 0.3
        
        # Word wrap for long templates
        words = template.split()
        lines = []
        current_line = []
        char_count = 0
        
        for word in words:
            if char_count + len(word) + 1 > 70:  # Line length limit
                lines.append(' '.join(current_line))
                current_line = [word]
                char_count = len(word)
            else:
                current_line.append(word)
                char_count += len(word) + 1
        
        if current_line:
            lines.append(' '.join(current_line))
        
        for line in lines:
            ax.text(1.5, y_pos, line, fontsize=9, color='#4b5563')
            y_pos -= 0.2
        
        y_pos -= 0.2
    
    # Footer
    ax.text(5, 1.5, 'PROYECTO ESTRUCTURADO PARA DESARROLLO EFICIENTE', 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#2563eb')
    ax.text(5, 1, 'Usa estos templates como base para solicitudes específicas en Claude.ai', 
            ha='center', va='center', fontsize=10, style='italic', color='#6b7280')
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

print(f'PDF generado: {pdf_filename}')
print(f'5 paginas con informacion completa del proyecto')
print(f'Listo para subir a Claude.ai como referencia')