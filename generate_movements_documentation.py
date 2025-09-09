#!/usr/bin/env python3
"""
Generador de documentación PDF para MovementsTab - Plataforma Inmuebles
Genera documentación detallada de todas las funcionalidades del sidebar
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os

class MovementsDocumentationGenerator:
    def __init__(self):
        self.doc = None
        self.story = []
        self.styles = getSampleStyleSheet()
        self.setup_styles()
    
    def setup_styles(self):
        # Custom styles
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            spaceBefore=30,
            textColor=colors.darkgreen
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubSectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            spaceBefore=20,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='FunctionHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.darkred
        ))
        
        self.styles.add(ParagraphStyle(
            name='CodeStyle',
            parent=self.styles['Code'],
            fontSize=10,
            backgroundColor=colors.lightgrey,
            borderWidth=1,
            borderColor=colors.grey,
            leftIndent=20,
            rightIndent=20
        ))

    def generate_documentation(self, filename="MovementsTab_Funcionalidades_Detalladas.pdf"):
        """Genera el documento PDF completo"""
        
        # Create document
        self.doc = SimpleDocTemplate(filename, pagesize=A4)
        
        # Title page
        self.add_title_page()
        
        # Table of contents
        self.add_table_of_contents()
        
        # Main content sections
        self.add_overview_section()
        self.add_interface_structure()
        self.add_action_buttons_section()
        self.add_summary_cards_section()
        self.add_filters_section()
        self.add_data_table_section()
        self.add_modals_section()
        self.add_technical_implementation()
        self.add_improvement_suggestions()
        
        # Build PDF
        self.doc.build(self.story)
        print(f"Documentacion generada: {filename}")
    
    def add_title_page(self):
        """Página de título"""
        self.story.append(Spacer(1, 2*inch))
        
        title = Paragraph("DOCUMENTACIÓN TÉCNICA DETALLADA", self.styles['CustomTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.5*inch))
        
        subtitle = Paragraph("MovementsTab - Gestión de Movimientos Financieros", self.styles['Heading1'])
        self.story.append(subtitle)
        self.story.append(Spacer(1, 0.3*inch))
        
        platform = Paragraph("Plataforma de Gestión de Inversiones Inmobiliarias", self.styles['Heading2'])
        self.story.append(platform)
        self.story.append(Spacer(1, 1*inch))
        
        # Project info table
        project_data = [
            ['URL de Producción:', 'https://inmuebles-david.vercel.app/financial-agent/movements'],
            ['Tecnología Frontend:', 'Next.js 14 + TypeScript + Tailwind CSS'],
            ['Tecnología Backend:', 'FastAPI + Python + SQLModel'],
            ['Fecha de Documentación:', datetime.now().strftime('%d/%m/%Y')],
            ['Versión:', '2.1.0']
        ]
        
        project_table = Table(project_data, colWidths=[2.5*inch, 3.5*inch])
        project_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(project_table)
        self.story.append(PageBreak())
    
    def add_table_of_contents(self):
        """Tabla de contenidos"""
        self.story.append(Paragraph("ÍNDICE DE CONTENIDOS", self.styles['SectionHeader']))
        self.story.append(Spacer(1, 0.3*inch))
        
        toc_data = [
            ["1.", "Visión General del Sistema", "3"],
            ["2.", "Estructura de la Interfaz", "4"],
            ["3.", "Botones de Acción Principales", "5"],
            ["4.", "Tarjetas de Resumen Financiero", "8"],
            ["5.", "Sistema de Filtros Avanzados", "9"],
            ["6.", "Tabla de Datos de Movimientos", "10"],
            ["7.", "Modales y Formularios", "11"],
            ["8.", "Implementación Técnica", "14"],
            ["9.", "Sugerencias de Mejora", "16"],
        ]
        
        toc_table = Table(toc_data, colWidths=[0.5*inch, 4.5*inch, 1*inch])
        toc_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        self.story.append(toc_table)
        self.story.append(PageBreak())
    
    def add_overview_section(self):
        """Sección de visión general"""
        self.story.append(Paragraph("1. VISIÓN GENERAL DEL SISTEMA", self.styles['SectionHeader']))
        
        overview_text = """
        <b>MovementsTab</b> es el componente central de gestión de movimientos financieros en la plataforma de inversiones inmobiliarias. 
        Proporciona una interfaz completa para la administración, visualización y análisis de transacciones financieras relacionadas 
        con propiedades inmobiliarias.
        
        <br/><br/><b>Características Principales:</b>
        <br/>• Gestión integral de movimientos financieros (ingresos, gastos, rentas, hipotecas)
        <br/>• Integración automática con Bankinter para sincronización bancaria
        <br/>• Sistema de filtros avanzados para análisis detallado
        <br/>• Carga masiva de datos desde archivos Excel/CSV
        <br/>• Clasificación automática e inteligente de transacciones
        <br/>• Análisis financiero con métricas clave y reportes
        <br/>• Gestión de propiedades múltiples con asignación específica
        <br/>• Interfaz responsive y optimizada para dispositivos móviles
        """
        
        self.story.append(Paragraph(overview_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.3*inch))
        
        # Architecture diagram description
        arch_text = """
        <b>Arquitectura del Componente:</b>
        <br/>El componente está construido usando React con hooks para gestión de estado, TypeScript para tipado fuerte,
        y Tailwind CSS para styling. Se integra con un backend FastAPI a través de llamadas API REST.
        """
        
        self.story.append(Paragraph(arch_text, self.styles['BodyText']))
    
    def add_interface_structure(self):
        """Estructura de la interfaz"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("2. ESTRUCTURA DE LA INTERFAZ", self.styles['SectionHeader']))
        
        structure_text = """
        La interfaz se organiza en <b>cinco secciones principales</b> dispuestas verticalmente:
        """
        self.story.append(Paragraph(structure_text, self.styles['BodyText']))
        
        # Structure table
        structure_data = [
            ['Sección', 'Descripción', 'Funcionalidad Principal'],
            ['Barra de Acciones', 'Botones principales de operación', 'Crear, Importar, Sincronizar, Exportar, Eliminar'],
            ['Tarjetas de Resumen', 'Métricas financieras clave', 'Visualización de KPIs financieros'],
            ['Panel de Filtros', 'Controles de búsqueda y filtrado', 'Filtrado dinámico de datos'],
            ['Tabla de Movimientos', 'Listado detallado de transacciones', 'Visualización y gestión individual'],
            ['Sistema de Modales', 'Formularios y confirmaciones', 'Interacciones avanzadas']
        ]
        
        structure_table = Table(structure_data, colWidths=[1.8*inch, 2.2*inch, 2.2*inch])
        structure_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(Spacer(1, 0.2*inch))
        self.story.append(structure_table)
    
    def add_action_buttons_section(self):
        """Sección detallada de botones de acción"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("3. BOTONES DE ACCIÓN PRINCIPALES", self.styles['SectionHeader']))
        
        intro_text = """
        La barra de acciones contiene <b>7 botones principales</b> que proporcionan toda la funcionalidad operativa del sistema:
        """
        self.story.append(Paragraph(intro_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Button 1: Nuevo Movimiento
        self.story.append(Paragraph("3.1 ➕ Nuevo Movimiento", self.styles['FunctionHeader']))
        button1_text = """
        <b>Función:</b> Abre modal para crear manualmente un nuevo movimiento financiero.
        <br/><b>Localización:</b> Primer botón (azul primario)
        <br/><b>Estado:</b> Siempre activo
        <br/><b>Handler:</b> setShowNewMovementModal(true)
        <br/><b>Campos del formulario:</b>
        <br/>• Propiedad (select con propiedades disponibles)
        <br/>• Fecha (date picker)
        <br/>• Concepto (text input - descripción del movimiento)
        <br/>• Importe (number input - positivo para ingresos, negativo para gastos)
        <br/>• Categoría (select: Renta, Hipoteca, Gasto)
        <br/>• Subcategoría (text input opcional)
        <br/>• Inquilino (text input opcional)
        """
        self.story.append(Paragraph(button1_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.1*inch))
        
        # Button 2: Analizar Conceptos
        self.story.append(Paragraph("3.2 📋 Analizar Conceptos", self.styles['FunctionHeader']))
        button2_text = """
        <b>Función:</b> Analiza automáticamente los conceptos de un archivo Excel seleccionado y sugiere categorizaciones.
        <br/><b>Localización:</b> Segundo botón (gris secundario)
        <br/><b>Estado:</b> Deshabilitado si no hay archivo seleccionado o está en proceso de análisis
        <br/><b>Handler:</b> handleAnalyzeConcepts()
        <br/><b>Proceso:</b>
        <br/>• Requiere archivo Excel previamente seleccionado
        <br/>• Envía archivo al endpoint /financial-movements/analyze-concepts
        <br/>• Procesa respuesta con conceptos categorizados automáticamente
        <br/>• Abre modal con resultados del análisis
        <br/>• Permite revisión y ajuste manual de categorizaciones
        """
        self.story.append(Paragraph(button2_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.1*inch))
        
        # Button 3: Subir Extracto
        self.story.append(Paragraph("3.3 📁 Subir Extracto", self.styles['FunctionHeader']))
        button3_text = """
        <b>Función:</b> Permite cargar masivamente movimientos desde archivo Excel o CSV.
        <br/><b>Localización:</b> Tercer botón (verde)
        <br/><b>Estado:</b> Siempre activo
        <br/><b>Handler:</b> setShowUploadModal(true)
        <br/><b>Funcionalidad:</b>
        <br/>• Abre selector de archivos (.xlsx, .csv soportados)
        <br/>• Validación de formato en cliente
        <br/>• Upload con progress bar
        <br/>• Procesamiento en servidor con deduplicación automática
        <br/>• Reporte detallado de resultados (creados, duplicados, errores)
        <br/>• Recarga automática de datos tras procesamiento exitoso
        """
        self.story.append(Paragraph(button3_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.1*inch))
        
        # Button 4: Actualizar Bankinter
        self.story.append(Paragraph("3.4 🏦 Actualizar Bankinter", self.styles['FunctionHeader']))
        button4_text = """
        <b>Función:</b> Sincronización automática con datos bancarios de Bankinter.
        <br/><b>Localización:</b> Cuarto botón (naranja)
        <br/><b>Estado:</b> Deshabilitado durante proceso de actualización
        <br/><b>Handler:</b> handleBankinterUpdate()
        <br/><b>Modalidades:</b>
        <br/>• <b>Scraper Real:</b> Abre navegador, conecta con Bankinter, descarga datos actuales (2-3 min)
        <br/>• <b>Producción:</b> Usa endpoint /integrations/bankinter/sync-now con datos preexistentes
        <br/><b>Proceso:</b>
        <br/>• Confirmación de modalidad con usuario
        <br/>• Ejecución de sincronización (local o remota)
        <br/>• Procesamiento de movimientos con detección de duplicados
        <br/>• Reporte de resultados (nuevos, duplicados, período)
        <br/>• Recarga automática de interfaz
        """
        self.story.append(Paragraph(button4_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.1*inch))
        
        # Button 5: Exportar Excel
        self.story.append(Paragraph("3.5 📊 Exportar Excel", self.styles['FunctionHeader']))
        button5_text = """
        <b>Función:</b> Genera y descarga archivo Excel con todos los movimientos filtrados.
        <br/><b>Localización:</b> Quinto botón (verde)
        <br/><b>Estado:</b> Deshabilitado si no hay movimientos o está exportando
        <br/><b>Handler:</b> handleExportToExcel()
        <br/><b>Características:</b>
        <br/>• Respeta filtros activos en la interfaz
        <br/>• Incluye todas las columnas disponibles
        <br/>• Formato compatible con Excel estándar
        <br/>• Nombre de archivo con timestamp
        <br/>• Progress indicator durante generación
        """
        self.story.append(Paragraph(button5_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.1*inch))
        
        # Button 6: Borrar por Fechas
        self.story.append(Paragraph("3.6 📅 Borrar por Fechas", self.styles['FunctionHeader']))
        button6_text = """
        <b>Función:</b> Eliminación masiva de movimientos en rango de fechas específico.
        <br/><b>Localización:</b> Sexto botón (amarillo/warning)
        <br/><b>Estado:</b> Siempre activo
        <br/><b>Handler:</b> setShowDateRangeDeleteModal(true)
        <br/><b>Funcionalidad:</b>
        <br/>• Modal con formulario de fechas (desde/hasta)
        <br/>• Opción de filtrar por propiedad específica
        <br/>• Confirmación explícita antes de eliminación
        <br/>• Validación de fechas en cliente
        <br/>• Reporte de cantidad eliminada
        <br/>• Recarga automática tras operación
        """
        self.story.append(Paragraph(button6_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.1*inch))
        
        # Button 7: Borrar Todo
        self.story.append(Paragraph("3.7 🗑️ Borrar Todo", self.styles['FunctionHeader']))
        button7_text = """
        <b>Función:</b> Eliminación completa de todos los movimientos del usuario.
        <br/><b>Localización:</b> Séptimo botón (rojo/danger)
        <br/><b>Estado:</b> Siempre activo
        <br/><b>Handler:</b> setShowDeleteAllModal(true)
        <br/><b>Seguridad:</b>
        <br/>• Doble confirmación requerida
        <br/>• Modal de advertencia explícita
        <br/>• Operación irreversible claramente indicada
        <br/>• Endpoint /financial-movements/bulk-delete
        <br/>• Reporte final de elementos eliminados
        """
        self.story.append(Paragraph(button7_text, self.styles['BodyText']))
    
    def add_summary_cards_section(self):
        """Sección de tarjetas de resumen"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("4. TARJETAS DE RESUMEN FINANCIERO", self.styles['SectionHeader']))
        
        intro_text = """
        El dashboard presenta <b>4 tarjetas de KPI</b> que ofrecen una visión instantánea de la situación financiera:
        """
        self.story.append(Paragraph(intro_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Cards table
        cards_data = [
            ['Tarjeta', 'Métrica', 'Cálculo', 'Color/Estilo'],
            ['💰 Total Ingresos', 'Suma de movimientos positivos', 'movements.filter(m => m.amount > 0)', 'Verde / border-green-500'],
            ['💸 Total Gastos', 'Suma de movimientos negativos', 'Math.abs(movements.filter(m => m.amount < 0))', 'Rojo / border-red-500'],
            ['📊 Cash Flow Neto', 'Diferencia ingresos-gastos', 'totalIncome - totalExpenses', 'Azul/Naranja según signo'],
            ['📈 Total Movimientos', 'Cantidad total de registros', 'movements.length', 'Gris / border-gray-500']
        ]
        
        cards_table = Table(cards_data, colWidths=[1.3*inch, 1.8*inch, 1.8*inch, 1.3*inch])
        cards_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(cards_table)
        self.story.append(Spacer(1, 0.2*inch))
        
        features_text = """
        <b>Características Técnicas:</b>
        <br/>• Actualización automática en tiempo real
        <br/>• Cálculos reactivos basados en filtros activos
        <br/>• Formato de moneda localizado (español)
        <br/>• Estilo glass-card con efectos visuales modernos
        <br/>• Responsive design con grid CSS adaptativo
        """
        self.story.append(Paragraph(features_text, self.styles['BodyText']))
    
    def add_filters_section(self):
        """Sección del sistema de filtros"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("5. SISTEMA DE FILTROS AVANZADOS", self.styles['SectionHeader']))
        
        intro_text = """
        El panel de filtros proporciona <b>6 campos de búsqueda</b> que funcionan de manera combinada y reactiva:
        """
        self.story.append(Paragraph(intro_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Filters table
        filters_data = [
            ['Campo', 'Tipo', 'Opciones/Validación', 'Funcionalidad'],
            ['Propiedad', 'Select', 'Todas / Sin asignar / Lista propiedades', 'Filtro por propiedad específica'],
            ['Categoría', 'Select', 'Todas / Renta / Hipoteca / Gasto', 'Filtro por tipo de movimiento'],
            ['Fecha Desde', 'Date', 'Formato YYYY-MM-DD', 'Filtro de inicio de período'],
            ['Fecha Hasta', 'Date', 'Formato YYYY-MM-DD', 'Filtro de fin de período'],
            ['Búsqueda', 'Text', 'Placeholder: "Concepto, propiedad, inquilino..."', 'Búsqueda de texto libre'],
            ['Limpiar filtros', 'Button', 'Resetea todos los campos', 'Restaura vista completa']
        ]
        
        filters_table = Table(filters_data, colWidths=[1.2*inch, 0.8*inch, 2.2*inch, 2*inch])
        filters_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(filters_table)
        self.story.append(Spacer(1, 0.2*inch))
        
        behavior_text = """
        <b>Comportamiento del Sistema:</b>
        <br/>• <b>Filtrado en tiempo real:</b> useEffect se ejecuta en cada cambio de filters
        <br/>• <b>Combinación de filtros:</b> Todos los campos activos se aplican simultáneamente
        <br/>• <b>Persistencia de estado:</b> Los filtros se mantienen durante la sesión
        <br/>• <b>Contador dinámico:</b> Muestra "X de Y movimientos" en tiempo real
        <br/>• <b>Performance optimizada:</b> Debouncing en campos de texto
        """
        self.story.append(Paragraph(behavior_text, self.styles['BodyText']))
    
    def add_data_table_section(self):
        """Sección de la tabla de datos"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("6. TABLA DE DATOS DE MOVIMIENTOS", self.styles['SectionHeader']))
        
        intro_text = """
        La tabla principal presenta los movimientos en formato tabular con <b>paginación y acciones por fila</b>:
        """
        self.story.append(Paragraph(intro_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Table columns
        columns_data = [
            ['Columna', 'Datos', 'Formato', 'Funcionalidad'],
            ['Fecha', 'movement.date', 'DD/MM/YYYY localizado', 'Ordenación cronológica'],
            ['Propiedad', 'property_address', 'Texto o "Sin asignar"', 'Identificación de propiedad'],
            ['Concepto', 'movement.concept', 'Texto truncado si es largo', 'Descripción del movimiento'],
            ['Categoría', 'movement.category', 'Badge coloreado', 'Clasificación visual'],
            ['Importe', 'movement.amount', 'Formato moneda €', 'Verde (+) / Rojo (-)'],
            ['Acciones', 'Botones', 'Editar / Eliminar', 'Operaciones individuales']
        ]
        
        columns_table = Table(columns_data, colWidths=[1*inch, 1.3*inch, 1.5*inch, 2.4*inch])
        columns_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(columns_table)
        self.story.append(Spacer(1, 0.2*inch))
        
        features_text = """
        <b>Características de la Tabla:</b>
        <br/>• <b>Paginación:</b> 50 elementos por página con controles de navegación
        <br/>• <b>Responsive:</b> Scroll horizontal en dispositivos móviles
        <br/>• <b>Estados vacíos:</b> Mensaje motivacional cuando no hay datos
        <br/>• <b>Loading states:</b> Spinner durante carga de datos
        <br/>• <b>Colores contextuales:</b> Verde para ingresos, rojo para gastos
        <br/>• <b>Acciones por fila:</b> Editar y eliminar individual
        """
        self.story.append(Paragraph(features_text, self.styles['BodyText']))
    
    def add_modals_section(self):
        """Sección de modales y formularios"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("7. MODALES Y FORMULARIOS", self.styles['SectionHeader']))
        
        intro_text = """
        El sistema incluye <b>8 modales especializados</b> para diferentes operaciones:
        """
        self.story.append(Paragraph(intro_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Modal 1: Upload
        self.story.append(Paragraph("7.1 Modal de Subida de Archivos", self.styles['SubSectionHeader']))
        modal1_text = """
        <b>Estado:</b> showUploadModal
        <br/><b>Función:</b> Permite seleccionar y subir archivo Excel/CSV
        <br/><b>Campos:</b>
        <br/>• File input con validación de extensión (.xlsx, .csv)
        <br/>• Preview del nombre de archivo seleccionado
        <br/>• Progress bar durante upload
        <br/>• Botones: Cancelar, Subir
        <br/><b>Validaciones:</b> Tamaño máximo, formato de archivo, estructura de datos
        """
        self.story.append(Paragraph(modal1_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.15*inch))
        
        # Modal 2: New Movement
        self.story.append(Paragraph("7.2 Modal de Nuevo Movimiento", self.styles['SubSectionHeader']))
        modal2_text = """
        <b>Estado:</b> showNewMovementModal
        <br/><b>Función:</b> Formulario completo para crear movimiento manual
        <br/><b>Campos:</b>
        <br/>• Propiedad (select con opciones disponibles)
        <br/>• Fecha (date picker con valor por defecto hoy)
        <br/>• Concepto (text area para descripción)
        <br/>• Importe (number input con validación)
        <br/>• Categoría (select: Renta/Hipoteca/Gasto)
        <br/>• Subcategoría (text input opcional)
        <br/>• Inquilino (text input opcional)
        <br/><b>Validaciones:</b> Campos requeridos, formato de importe, fechas válidas
        """
        self.story.append(Paragraph(modal2_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.15*inch))
        
        # Modal 3: Date Range Delete
        self.story.append(Paragraph("7.3 Modal de Eliminación por Fechas", self.styles['SubSectionHeader']))
        modal3_text = """
        <b>Estado:</b> showDateRangeDeleteModal
        <br/><b>Función:</b> Eliminación masiva en rango de fechas
        <br/><b>Campos:</b>
        <br/>• Fecha desde (date picker requerido)
        <br/>• Fecha hasta (date picker requerido)
        <br/>• Propiedad (select opcional para filtrar)
        <br/>• Checkbox de confirmación
        <br/><b>Seguridad:</b> Doble confirmación, preview de elementos a eliminar
        """
        self.story.append(Paragraph(modal3_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.15*inch))
        
        # Modal 4: Delete All Confirmation
        self.story.append(Paragraph("7.4 Modal de Confirmación de Eliminación Total", self.styles['SubSectionHeader']))
        modal4_text = """
        <b>Estado:</b> showDeleteAllModal
        <br/><b>Función:</b> Confirmación para borrar todos los movimientos
        <br/><b>Elementos:</b>
        <br/>• Mensaje de advertencia clara
        <br/>• Contador de elementos a eliminar
        <br/>• Texto de confirmación explícita
        <br/>• Botones: Cancelar, Confirmar eliminación
        <br/><b>Seguridad:</b> Operación irreversible claramente indicada
        """
        self.story.append(Paragraph(modal4_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.15*inch))
        
        # Modal 5: Edit Movement
        self.story.append(Paragraph("7.5 Modal de Edición de Movimiento", self.styles['SubSectionHeader']))
        modal5_text = """
        <b>Estado:</b> showEditMovementModal + editingMovement
        <br/><b>Función:</b> Editar movimiento existente
        <br/><b>Campos:</b> Idénticos al modal de nuevo movimiento
        <br/><b>Datos:</b> Pre-poblados con valores existentes
        <br/><b>Funcionalidad:</b> PUT request para actualizar registro
        """
        self.story.append(Paragraph(modal5_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.15*inch))
        
        # Modal 6: Delete Movement
        self.story.append(Paragraph("7.6 Modal de Eliminación Individual", self.styles['SubSectionHeader']))
        modal6_text = """
        <b>Estado:</b> showDeleteMovementModal + selectedMovement
        <br/><b>Función:</b> Confirmar eliminación de movimiento específico
        <br/><b>Datos:</b> Muestra detalles del movimiento a eliminar
        <br/><b>Seguridad:</b> Confirmación explícita requerida
        """
        self.story.append(Paragraph(modal6_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.15*inch))
        
        # Modal 7: Assign Modal
        self.story.append(Paragraph("7.7 Modal de Asignación Masiva", self.styles['SubSectionHeader']))
        modal7_text = """
        <b>Estado:</b> showAssignModal + selectedProperty
        <br/><b>Función:</b> Asignar múltiples movimientos a una propiedad
        <br/><b>Campos:</b>
        <br/>• Select de propiedad destino
        <br/>• Lista de movimientos seleccionados
        <br/>• Botones de confirmación
        """
        self.story.append(Paragraph(modal7_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.15*inch))
        
        # Modal 8: Analyze Concepts
        self.story.append(Paragraph("7.8 Modal de Análisis de Conceptos", self.styles['SubSectionHeader']))
        modal8_text = """
        <b>Estado:</b> showAnalyzeConceptsModal + analyzedConcepts
        <br/><b>Función:</b> Mostrar resultados de análisis automático
        <br/><b>Contenido:</b>
        <br/>• Lista de conceptos analizados
        <br/>• Categorías sugeridas automáticamente
        <br/>• Controles para ajustar clasificaciones
        <br/>• Botón para aplicar cambios masivamente
        """
        self.story.append(Paragraph(modal8_text, self.styles['BodyText']))
    
    def add_technical_implementation(self):
        """Sección de implementación técnica"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("8. IMPLEMENTACIÓN TÉCNICA", self.styles['SectionHeader']))
        
        # State Management
        self.story.append(Paragraph("8.1 Gestión de Estado", self.styles['SubSectionHeader']))
        state_text = """
        El componente utiliza <b>múltiples hooks de React</b> para gestión compleja de estado:
        """
        self.story.append(Paragraph(state_text, self.styles['BodyText']))
        
        state_data = [
            ['Estado', 'Tipo', 'Propósito'],
            ['movements', 'MovementWithProperty[]', 'Array principal de datos'],
            ['properties', 'Property[]', 'Lista de propiedades disponibles'],
            ['loading', 'boolean', 'Estado de carga general'],
            ['filters', 'object', 'Filtros activos'],
            ['pagination', 'object', 'Control de paginación'],
            ['modals', '8x boolean', 'Estados de visibilidad de modales'],
            ['forms', 'multiple objects', 'Datos de formularios'],
            ['processing states', '5x boolean', 'Estados de operaciones async']
        ]
        
        state_table = Table(state_data, colWidths=[2*inch, 1.5*inch, 2.7*inch])
        state_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(state_table)
        self.story.append(Spacer(1, 0.2*inch))
        
        # API Integration
        self.story.append(Paragraph("8.2 Integración con API", self.styles['SubSectionHeader']))
        api_text = """
        <b>Endpoints utilizados:</b>
        <br/>• <b>GET /financial-movements/</b> - Carga de movimientos con filtros
        <br/>• <b>POST /financial-movements/</b> - Crear nuevo movimiento
        <br/>• <b>PUT /financial-movements/{id}</b> - Actualizar movimiento
        <br/>• <b>DELETE /financial-movements/{id}</b> - Eliminar movimiento individual
        <br/>• <b>POST /financial-movements/upload-excel-global</b> - Carga masiva
        <br/>• <b>POST /financial-movements/bulk-delete</b> - Eliminación masiva
        <br/>• <b>DELETE /financial-movements/delete-by-date-range</b> - Eliminación por fechas
        <br/>• <b>POST /integrations/bankinter/sync-now</b> - Sincronización bancaria
        <br/>• <b>GET /properties/</b> - Listado de propiedades
        """
        self.story.append(Paragraph(api_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Error Handling
        self.story.append(Paragraph("8.3 Manejo de Errores", self.styles['SubSectionHeader']))
        error_text = """
        <b>Sistema robusto de manejo de errores:</b>
        <br/>• Función extractErrorMessage() para parsing consistente
        <br/>• Try-catch en todas las operaciones async
        <br/>• Estados de loading/disabled durante operaciones
        <br/>• Feedback visual inmediato con alerts
        <br/>• Recuperación automática en operaciones fallidas
        <br/>• Logging detallado en consola para debugging
        """
        self.story.append(Paragraph(error_text, self.styles['BodyText']))
    
    def add_improvement_suggestions(self):
        """Sección de sugerencias de mejora"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("9. SUGERENCIAS DE MEJORA", self.styles['SectionHeader']))
        
        intro_text = """
        Basándose en el análisis del código actual, se proponen las siguientes <b>mejoras prioritarias</b>:
        """
        self.story.append(Paragraph(intro_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # UX/UI Improvements
        self.story.append(Paragraph("9.1 Mejoras de UX/UI", self.styles['SubSectionHeader']))
        ux_text = """
        <b>1. Sistema de Notificaciones Avanzado:</b>
        <br/>• Reemplazar alerts con toast notifications elegantes
        <br/>• Progress bars para operaciones de larga duración
        <br/>• Feedback visual mejorado con micro-interacciones
        
        <br/><br/><b>2. Interfaz Más Intuitiva:</b>
        <br/>• Drag & drop para asignación de movimientos a propiedades
        <br/>• Bulk selection con checkboxes para operaciones masivas
        <br/>• Preview en tiempo real antes de operaciones destructivas
        <br/>• Shortcuts de teclado para operaciones frecuentes
        
        <br/><br/><b>3. Visualización de Datos:</b>
        <br/>• Gráficos interactivos de tendencias financieras
        <br/>• Dashboard con métricas avanzadas (ROI, proyecciones)
        <br/>• Calendario de movimientos para vista temporal
        <br/>• Categorización visual con colores consistentes
        """
        self.story.append(Paragraph(ux_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Technical Improvements  
        self.story.append(Paragraph("9.2 Mejoras Técnicas", self.styles['SubSectionHeader']))
        tech_text = """
        <b>1. Performance y Escalabilidad:</b>
        <br/>• Implementar virtualización para tablas grandes (react-window)
        <br/>• Lazy loading de datos con infinite scroll
        <br/>• Memoización de componentes pesados (React.memo)
        <br/>• Debouncing optimizado en filtros de texto
        
        <br/><br/><b>2. Gestión de Estado:</b>
        <br/>• Migrar a Context API o Zustand para estado global
        <br/>• Implementar cache de datos con React Query
        <br/>• Estados derivados computados automáticamente
        <br/>• Persistencia de filtros y preferencias en localStorage
        
        <br/><br/><b>3. Validación y Seguridad:</b>
        <br/>• Schema validation con Zod o Yup
        <br/>• Validación en tiempo real de formularios
        <br/>• Rate limiting en operaciones críticas
        <br/>• Confirmaciones multi-factor para eliminaciones masivas
        """
        self.story.append(Paragraph(tech_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Feature Enhancements
        self.story.append(Paragraph("9.3 Nuevas Funcionalidades", self.styles['SubSectionHeader']))
        features_text = """
        <b>1. Automatización Inteligente:</b>
        <br/>• ML para categorización automática de conceptos
        <br/>• Detección de patrones recurrentes (rentas, hipotecas)
        <br/>• Sugerencias predictivas basadas en historial
        <br/>• Alertas automáticas para gastos inusuales
        
        <br/><br/><b>2. Reportes y Analytics:</b>
        <br/>• Generación automática de reportes mensuales/anuales
        <br/>• Comparativas período-sobre-período
        <br/>• Proyecciones financieras basadas en tendencias
        <br/>• Exportación a múltiples formatos (PDF, CSV, JSON)
        
        <br/><br/><b>3. Integración Bancaria Ampliada:</b>
        <br/>• Soporte para múltiples bancos (no solo Bankinter)
        <br/>• Sincronización automática programada
        <br/>• Detección de movimientos duplicados cross-platform
        <br/>• API PSD2 para conexiones más robustas
        """
        self.story.append(Paragraph(features_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Implementation Priority
        self.story.append(Paragraph("9.4 Priorización de Implementación", self.styles['SubSectionHeader']))
        priority_text = """
        <b>🔴 Prioridad Alta (1-2 sprints):</b>
        <br/>• Sistema de notificaciones toast
        <br/>• Validación mejorada de formularios
        <br/>• Performance optimization con memoization
        
        <br/><br/><b>🟡 Prioridad Media (3-4 sprints):</b>
        <br/>• Gestión de estado centralizada
        <br/>• Funcionalidades de bulk operations
        <br/>• Reportes básicos automatizados
        
        <br/><br/><b>🟢 Prioridad Baja (5+ sprints):</b>
        <br/>• ML para categorización
        <br/>• Integración multi-banco
        <br/>• Dashboard analytics avanzado
        """
        self.story.append(Paragraph(priority_text, self.styles['BodyText']))

def main():
    """Función principal"""
    print("Generando documentacion detallada de MovementsTab...")
    
    generator = MovementsDocumentationGenerator()
    filename = "MovementsTab_Funcionalidades_Detalladas.pdf"
    
    try:
        generator.generate_documentation(filename)
        print("Documentacion generada exitosamente!")
        print(f"Archivo: {filename}")
        print(f"Ubicacion: {os.path.abspath(filename)}")
        
        # Additional instructions
        print("\nINSTRUCCIONES PARA CLAUDE.AI:")
        print("1. Sube este PDF a Claude.ai")
        print("2. Usa este prompt inicial:")
        print('   "Analiza esta documentacion detallada del componente MovementsTab de mi plataforma inmobiliaria.')
        print('   Basandote en toda la informacion tecnica proporcionada, sugiere mejoras especificas')
        print('   priorizadas por impacto y factibilidad tecnica. Incluye codigo de ejemplo cuando sea relevante."')
        
    except Exception as e:
        print(f"Error generando documentacion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()