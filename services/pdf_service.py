# pdf_service.py
import io
import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from services.tarea_service import calcular_horas_tarea
from utils.formatters import horas_a_formato

def generar_pdf_tareas(tareas, proyecto_nombre, mes_nombre, año):
    """Genera un PDF con la tabla de tareas que se adapta al contenido"""
    buffer = io.BytesIO()
    
    # Configurar documento en landscape para más espacio
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=0.3*inch,
        leftMargin=0.3*inch,
        topMargin=0.8*inch,
        bottomMargin=0.5*inch
    )
    
    # CORREGIDO: Estilos con alineación centrada
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=1  # Centrado
    )
    
    # AGREGADO: Estilo para celdas centradas
    centered_style = ParagraphStyle(
        'CenteredCell',
        parent=styles['Normal'],
        fontSize=8,
        alignment=1,  # Centrado horizontalmente
        leading=10,   # Espaciado entre líneas
    )
    
    # Contenido del PDF
    story = []
    
    # Título
    titulo = f"Reporte de Tareas - {proyecto_nombre}"
    story.append(Paragraph(titulo, title_style))
    
    # Subtítulo
    subtitulo = f"{mes_nombre} {año}"
    story.append(Paragraph(subtitulo, styles['Heading2']))
    story.append(Spacer(1, 15))
    
    if not tareas:
        story.append(Paragraph("No hay tareas registradas para este período.", styles['Normal']))
    else:
        # Preparar datos para la tabla
        data = [['Tarea', 'Detalle', 'Horas', '¿Qué falta?', 'Días Trabajados']]
        
        for tarea in tareas:
            # Calcular horas
            horas = calcular_horas_tarea(tarea)
            
            # Solo fechas, sin días de la semana
            dias_trabajados = ", ".join([
                dia.fecha.strftime('%d/%m') 
                for dia in tarea.dias
            ])
            
            # CORREGIDO: Usar estilo centrado para todas las celdas
            tarea_para = Paragraph(tarea.titulo or "Sin título", centered_style)
            detalle_para = Paragraph(tarea.detalle or "Sin detalle", centered_style)
            horas_para = Paragraph(horas, centered_style)
            que_falta_para = Paragraph(tarea.que_falta or "Nada", centered_style)
            dias_para = Paragraph(dias_trabajados or "Sin días", centered_style)
            
            # Agregar fila a la tabla
            data.append([
                tarea_para,
                detalle_para,
                horas_para,
                que_falta_para,
                dias_para
            ])
        
        # Calcular anchos dinámicamente según el contenido de página
        page_width = landscape(A4)[0] - 0.6*inch
        
        # Distribución de anchos
        col_widths = [
            page_width * 0.20,  # Tarea: 20%
            page_width * 0.35,  # Detalle: 35%
            page_width * 0.10,  # Horas: 10%
            page_width * 0.25,  # ¿Qué falta?: 25%
            page_width * 0.10   # Días: 10%
        ]
        
        # Crear tabla con anchos adaptativos
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        # CORREGIDO: Estilo con alineación centrada vertical y horizontal
        table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),     # CENTRADO HORIZONTAL
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),    # CENTRADO VERTICAL
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            
            # Contenido
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            
            # Espaciado interno mejorado
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            
            # Colores alternos en filas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            
            # Permitir que las celdas se expandan según contenido
            ('WORDWRAP', (0, 0), (-1, -1), 'LTR'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 15))
        
        # Resumen
        total_horas = sum(sum(dia.horas_reales for dia in tarea.dias) for tarea in tareas)
        resumen = f"Total de tareas: {len(tareas)} | Total horas: {horas_a_formato(total_horas)}"
        story.append(Paragraph(resumen, styles['Heading3']))
    
    # Pie de página con fecha de generación
    fecha_generacion = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    pie = f"Generado el {fecha_generacion}"
    story.append(Spacer(1, 20))
    story.append(Paragraph(pie, styles['Normal']))
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    return buffer