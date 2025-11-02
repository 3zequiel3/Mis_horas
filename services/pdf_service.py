import io
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from utils.constants import MESES_ES
from utils.formatters import horas_a_formato
from services.tarea_service import obtener_horas_tarea_segun_usuario

def generar_pdf_proyecto(proyecto, dias, tareas, mes: int, año: int, usar_horas_reales: bool, usuario_id: int, db):
    """
    Genera un PDF con el resumen de tareas del proyecto
    - Hoja en vertical (portrait)
    - Tabla horizontal adaptativa al contenido
    - Fuente pequeña y optimizada
    """
    buffer = io.BytesIO()

    # Configuración de documento en VERTICAL
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,  # ← VERTICAL por defecto
        rightMargin=0.4*inch,
        leftMargin=0.4*inch,
        topMargin=0.6*inch,
        bottomMargin=0.5*inch
    )

    # ============ ESTILOS ============
    styles = getSampleStyleSheet()
    
    # Título principal - más compacto
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=6,
        alignment=1,  # Centrado
        textColor=colors.HexColor('#1a237e'),
        fontName='Helvetica-Bold'
    )
    
    # Subtítulo - más pequeño
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=4,
        alignment=1,
        textColor=colors.HexColor('#455a64'),
        fontName='Helvetica'
    )
    
    # Info adicional - compacta
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=8,
        spaceAfter=12,
        alignment=1,
        textColor=colors.HexColor('#607d8b'),
        fontName='Helvetica-Oblique'
    )

    # Estilo para contenido centrado en celdas - MÁS PEQUEÑO
    centered_style = ParagraphStyle(
        'CenteredCell',
        parent=styles['Normal'],
        fontSize=7,  # ← Reducido de 9 a 7
        alignment=1,  # Centrado horizontal
        leading=9,    # ← Reducido de 11 a 9
        fontName='Helvetica'
    )
    
    # Estilo para header de columnas - MÁS PEQUEÑO
    header_style = ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontSize=8,  # ← Reducido de 10 a 8
        alignment=1,
        fontName='Helvetica-Bold',
        textColor=colors.whitesmoke
    )

    story = []

    # ============ ENCABEZADO COMPACTO ============
    titulo = f"{proyecto.nombre}"
    story.append(Paragraph(titulo, title_style))

    subtitulo = f"{MESES_ES[mes]} {año}"
    story.append(Paragraph(subtitulo, subtitle_style))
    
    # Descripción del proyecto si existe
    if proyecto.descripcion:
        story.append(Paragraph(f"<i>{proyecto.descripcion}</i>", info_style))
    
    story.append(Spacer(1, 10))

    # ============ TABLA DE TAREAS ADAPTATIVA ============  
    if not tareas:
        story.append(Paragraph("No hay tareas registradas para este período.", info_style))
    else:
        # Etiqueta de columna de horas según configuración
        etiqueta_horas = "Horas"
        
        # Encabezados de la tabla - ABREVIADOS
        data = [[
            Paragraph('<b>Tarea</b>', header_style),
            Paragraph('<b>Detalle</b>', header_style),
            Paragraph(f'<b>{etiqueta_horas}</b>', header_style),
            Paragraph('<b>¿Qué Falta?</b>', header_style),
            Paragraph('<b>Días</b>', header_style)
        ]]

        total_horas = 0

        for tarea in tareas:
            # Obtener horas según configuración del usuario
            horas_tarea = obtener_horas_tarea_segun_usuario(tarea, usuario_id, db)
            
            # Convertir a float para sumar
            if ':' in horas_tarea:
                partes = horas_tarea.split(':')
                horas_float = int(partes[0]) + (int(partes[1]) / 60.0)
            else:
                horas_float = 0
            
            total_horas += horas_float

            # Filtrar días del mes actual
            dias_mes = [d for d in tarea.dias if d.fecha.year == año and d.fecha.month == mes]
            
            # Solo fechas sin días de la semana - FORMATO COMPACTO
            dias_trabajados = ", ".join([
                dia.fecha.strftime('%d/%m')
                for dia in dias_mes
            ])

            # Convertir contenido a Paragraph para adaptación automática
            tarea_para = Paragraph(tarea.titulo or "Sin título", centered_style)
            detalle_para = Paragraph(tarea.detalle or "-", centered_style)
            horas_para = Paragraph(horas_tarea, centered_style)
            que_falta_para = Paragraph(tarea.que_falta or "-", centered_style)
            dias_para = Paragraph(dias_trabajados or "-", centered_style)

            data.append([
                tarea_para,
                detalle_para,
                horas_para,
                que_falta_para,
                dias_para
            ])

        # Calcular anchos de columna según espacio disponible - OPTIMIZADO PARA VERTICAL
        page_width = A4[0] - 0.8*inch  # Ancho disponible en vertical

        col_widths = [
            page_width * 0.18,  # Tarea: 18%
            page_width * 0.32,  # Detalle: 32%
            page_width * 0.12,  # Horas: 12%
            page_width * 0.28,  # ¿Qué falta?: 28%
            page_width * 0.10   # Días: 10%
        ]

        # Crear tabla con estilos - PADDING REDUCIDO
        table = Table(data, colWidths=col_widths, repeatRows=1)

        table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),     # Centrado horizontal
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),    # Centrado vertical
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),

            # Contenido
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),  # ← Fuente más pequeña
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdbdbd')),

            # Espaciado interno - REDUCIDO
            ('LEFTPADDING', (0, 0), (-1, -1), 4),   # ← Reducido de 6 a 4
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),  # ← Reducido de 6 a 4
            ('TOPPADDING', (0, 0), (-1, -1), 4),    # ← Reducido de 6 a 4
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4), # ← Reducido de 6 a 4

            # Filas alternadas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),

            # Ajuste automático de texto
            ('WORDWRAP', (0, 0), (-1, -1), 'LTR'),
        ]))

        story.append(table)
        story.append(Spacer(1, 10))

        # ============ RESUMEN DE TOTALES ============
        resumen_style = ParagraphStyle(
            'ResumenStyle',
            parent=styles['Heading3'],
            fontSize=10,  # ← Reducido de 12 a 10
            alignment=1,
            textColor=colors.HexColor('#1a237e'),
            fontName='Helvetica-Bold'
        )
        
        resumen = f"Total: <b>{len(tareas)}</b> tareas | <b>{horas_a_formato(total_horas)} Horas</b>"
        story.append(Paragraph(resumen, resumen_style))

    # ============ PIE DE PÁGINA ============
    story.append(Spacer(1, 15))
    
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=7,  # ← Reducido de 8 a 7
        alignment=1,
        textColor=colors.HexColor('#9e9e9e')
    )
    
    fecha_generacion = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    pie = f"Generado: {fecha_generacion}"
    story.append(Paragraph(pie, footer_style))

    # Construir y retornar PDF
    doc.build(story)
    buffer.seek(0)
    return buffer