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
    """Genera un PDF con la tabla de tareas adaptable al contenido"""
    buffer = io.BytesIO()
    
    # Configuración de documento en horizontal
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=0.3*inch,
        leftMargin=0.3*inch,
        topMargin=0.8*inch,
        bottomMargin=0.5*inch
    )
    
    # Estilos para el documento
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=1  # Centrado
    )
    
    # Estilo para contenido centrado en celdas
    centered_style = ParagraphStyle(
        'CenteredCell',
        parent=styles['Normal'],
        fontSize=8,
        alignment=1,  # Centrado horizontal
        leading=10,   # Espaciado entre líneas
    )
    
    story = []
    
    # Encabezado del documento
    titulo = f"Reporte de Tareas - {proyecto_nombre}"
    story.append(Paragraph(titulo, title_style))
    
    subtitulo = f"{mes_nombre} {año}"
    story.append(Paragraph(subtitulo, styles['Heading2']))
    story.append(Spacer(1, 15))
    
    if not tareas:
        story.append(Paragraph("No hay tareas registradas para este período.", styles['Normal']))
    else:
        # Encabezados de la tabla
        data = [['Tarea', 'Detalle', 'Horas', '¿Qué falta?', 'Días Trabajados']]
        
        for tarea in tareas:
            horas = calcular_horas_tarea(tarea)
            
            # Solo fechas sin días de la semana
            dias_trabajados = ", ".join([
                dia.fecha.strftime('%d/%m') 
                for dia in tarea.dias
            ])
            
            # Convertir contenido a Paragraph para adaptación automática
            tarea_para = Paragraph(tarea.titulo or "Sin título", centered_style)
            detalle_para = Paragraph(tarea.detalle or "Sin detalle", centered_style)
            horas_para = Paragraph(horas, centered_style)
            que_falta_para = Paragraph(tarea.que_falta or "Nada", centered_style)
            dias_para = Paragraph(dias_trabajados or "Sin días", centered_style)
            
            data.append([
                tarea_para,
                detalle_para,
                horas_para,
                que_falta_para,
                dias_para
            ])
        
        # Calcular anchos de columna según espacio disponible
        page_width = landscape(A4)[0] - 0.6*inch
        
        col_widths = [
            page_width * 0.20,  # Tarea: 20%
            page_width * 0.35,  # Detalle: 35%
            page_width * 0.10,  # Horas: 10%
            page_width * 0.25,  # ¿Qué falta?: 25%
            page_width * 0.10   # Días: 10%
        ]
        
        # Crear tabla con estilos
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),     # Centrado horizontal
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),    # Centrado vertical
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            
            # Contenido
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            
            # Espaciado interno
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            
            # Filas alternadas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            
            # Ajuste automático de texto
            ('WORDWRAP', (0, 0), (-1, -1), 'LTR'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 15))
        
        # Resumen de totales
        total_horas = sum(sum(dia.horas_reales for dia in tarea.dias) for tarea in tareas)
        resumen = f"Total de tareas: {len(tareas)} | Total horas: {horas_a_formato(total_horas)}"
        story.append(Paragraph(resumen, styles['Heading3']))
    
    # Pie de página con fecha de generación
    fecha_generacion = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    pie = f"Generado el {fecha_generacion}"
    story.append(Spacer(1, 20))
    story.append(Paragraph(pie, styles['Normal']))
    
    # Construir y retornar PDF
    doc.build(story)
    buffer.seek(0)
    return buffer