# app.py
import streamlit as st
import datetime
import calendar
import pandas as pd
import io
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch

from sqlalchemy.orm import Session
from sqlalchemy import distinct, func, extract

from db import SessionLocal, init_db
from models import Proyecto, Dia, Tarea

DIAS_ES = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo",
}

# AGREGADO: Diccionario de meses en español
MESES_ES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generar_dias_para_proyecto(db: Session, proyecto: Proyecto):
    """Genera días para el mes inicial del proyecto"""
    # Verificar si ya existen días para este proyecto
    existing = (
        db.query(Dia)
        .filter(Dia.proyecto_id == proyecto.id)
        .first()
    )
    if existing:
        print(f"DEBUG - Ya existen días para proyecto {proyecto.id}")
        return

    # CORREGIDO: Usar MESES_ES para debug
    print(f"DEBUG - Generando días para {proyecto.nombre}: {MESES_ES[proyecto.mes]} {proyecto.anio}")
    
    # Generar días para el mes/año del proyecto
    month_range = calendar.monthrange(proyecto.anio, proyecto.mes)[1]
    print(f"DEBUG - Días en {MESES_ES[proyecto.mes]} {proyecto.anio}: {month_range}")
    
    for day in range(1, month_range + 1):
        fecha = datetime.date(proyecto.anio, proyecto.mes, day)
        weekday = fecha.weekday()
        dia = Dia(
            fecha=fecha,
            dia_semana=DIAS_ES[weekday],
            horas_trabajadas=0,
            horas_reales=0,
            proyecto_id=proyecto.id,
        )
        db.add(dia)
        print(f"DEBUG - Creando día: {fecha} ({DIAS_ES[weekday]})")
    
    db.commit()
    print(f"DEBUG - Días creados exitosamente")

def obtener_meses_proyecto(db: Session, proyecto_id: int):
    """Obtiene todos los meses únicos que tiene un proyecto"""
    # CORREGIDO: usar func.extract en lugar de Dia.fecha.extract
    fechas_unicas = db.query(Dia.fecha).filter(Dia.proyecto_id == proyecto_id).distinct().all()
    años_meses = set()
    
    for fecha_tupla in fechas_unicas:
        fecha = fecha_tupla[0]
        años_meses.add((fecha.year, fecha.month))
    
    meses = sorted(list(años_meses))
    return meses


def agregar_mes_proyecto(db: Session, proyecto: Proyecto, año: int, mes: int):
    """Agrega un nuevo mes al proyecto"""
    # CORREGIDO: usar func.extract
    existing = (
        db.query(Dia)
        .filter(
            Dia.proyecto_id == proyecto.id,
            func.extract('year', Dia.fecha) == año,
            func.extract('month', Dia.fecha) == mes
        )
        .first()
    )
    
    if existing:
        return False  # Ya existe
    
    # Generar días para el nuevo mes
    month_range = calendar.monthrange(año, mes)[1]
    for day in range(1, month_range + 1):
        fecha = datetime.date(año, mes, day)
        weekday = fecha.weekday()
        dia = Dia(
            fecha=fecha,
            dia_semana=DIAS_ES[weekday],
            horas_trabajadas=0,
            horas_reales=0,
            proyecto_id=proyecto.id,
        )
        db.add(dia)
    db.commit()
    return True


def calcular_horas_tarea(tarea: Tarea):
    """Calcula las horas totales de una tarea basándose en los días seleccionados"""
    total_horas = sum(dia.horas_reales for dia in tarea.dias)
    # Formatear como HH:MM
    horas = int(total_horas)
    minutos = int((total_horas - horas) * 60)
    return f"{horas:02d}:{minutos:02d}"


def horas_a_formato(horas_decimal):
    """Convierte horas decimales a formato HH:MM"""
    if horas_decimal == 0:
        return "00:00"
    horas = int(horas_decimal)
    minutos = int((horas_decimal - horas) * 60)
    return f"{horas:02d}:{minutos:02d}"


def formato_a_horas(formato_str):
    """Convierte formato HH:MM a horas decimales"""
    try:
        if ":" in formato_str:
            horas, minutos = formato_str.split(":")
            return int(horas) + int(minutos) / 60
        else:
            return float(formato_str)
    except:
        return 0.0


def generar_pdf_tareas(tareas, proyecto_nombre, mes_nombre, año):
    """Genera un PDF con la tabla de tareas"""
    buffer = io.BytesIO()
    
    # Configurar documento en landscape para más espacio
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=1*inch,
        bottomMargin=0.5*inch
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Centrado
    )
    
    # Contenido del PDF
    story = []
    
    # Título
    titulo = f"Reporte de Tareas - {proyecto_nombre}"
    story.append(Paragraph(titulo, title_style))
    
    # Subtítulo
    subtitulo = f"{mes_nombre} {año}"
    story.append(Paragraph(subtitulo, styles['Heading2']))
    story.append(Spacer(1, 20))
    
    if not tareas:
        story.append(Paragraph("No hay tareas registradas para este período.", styles['Normal']))
    else:
        # Preparar datos para la tabla
        data = [['Tarea', 'Detalle', 'Horas', '¿Qué falta?', 'Días Trabajados']]
        
        for tarea in tareas:
            # Calcular horas
            horas = calcular_horas_tarea(tarea)
            
            # Obtener días trabajados
            dias_trabajados = ", ".join([
                f"{dia.fecha.strftime('%d/%m')} ({dia.dia_semana})" 
                for dia in tarea.dias
            ])
            
            # Agregar fila a la tabla
            data.append([
                tarea.titulo,
                tarea.detalle or "Sin detalle",
                horas,
                tarea.que_falta or "Nada",
                dias_trabajados or "Sin días asignados"
            ])
        
        # Crear tabla
        table = Table(data, colWidths=[2*inch, 3*inch, 1*inch, 2.5*inch, 2.5*inch])
        
        # Estilo de la tabla
        table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            
            # Contenido
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Resumen
        total_horas = sum(sum(dia.horas_reales for dia in tarea.dias) for tarea in tareas)
        resumen = f"Total de tareas: {len(tareas)} | Total horas: {horas_a_formato(total_horas)}"
        story.append(Paragraph(resumen, styles['Heading3']))
    
    # Pie de página con fecha de generación
    fecha_generacion = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    pie = f"Generado el {fecha_generacion}"
    story.append(Spacer(1, 30))
    story.append(Paragraph(pie, styles['Normal']))
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def obtener_dias_disponibles(db: Session, proyecto_id: int, año: int, mes: int, tarea_excluir_id=None):
    """Obtiene días del mes que NO están asignados a otras tareas"""
    # Obtener todos los días del mes
    todos_dias = (
        db.query(Dia)
        .filter(
            Dia.proyecto_id == proyecto_id,
            func.extract('year', Dia.fecha) == año,
            func.extract('month', Dia.fecha) == mes
        )
        .order_by(Dia.fecha.asc())
        .all()
    )
    
    # Obtener días ya asignados a otras tareas (excluyendo la tarea actual si está editando)
    query_tareas = db.query(Tarea).filter(Tarea.proyecto_id == proyecto_id)
    if tarea_excluir_id:
        query_tareas = query_tareas.filter(Tarea.id != tarea_excluir_id)
    
    tareas_otras = query_tareas.all()
    dias_ocupados = set()
    
    for tarea in tareas_otras:
        for dia in tarea.dias:
            dias_ocupados.add(dia.id)
    
    # Filtrar días disponibles
    dias_disponibles = [dia for dia in todos_dias if dia.id not in dias_ocupados]
    return dias_disponibles


def main():
    st.set_page_config(
        page_title="Mis Horas",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_db()
    db = next(get_db())

    # ---------- SIDEBAR ----------
    st.sidebar.title("📁 Proyectos")

    # levantamos proyectos
    proyectos = db.query(Proyecto).order_by(Proyecto.id.desc()).all()

    if "show_project_modal" not in st.session_state:
        st.session_state["show_project_modal"] = False

    # CORREGIDO: Agregar opción "Sin seleccionar" al inicio
    opciones_proyectos = [None] + proyectos
    
    sel_proyecto = st.sidebar.selectbox(
        "Proyecto actual",
        options=opciones_proyectos,
        format_func=lambda x: "Sin seleccionar" if x is None else f"{x.nombre}",
        index=0,  # CORREGIDO: Siempre empezar con "Sin seleccionar"
    )

    if st.sidebar.button("➕ Nuevo proyecto"):
        st.session_state["show_project_modal"] = True

    # ---------- SELECTOR DE MES (solo si hay proyecto seleccionado) ----------
    mes_sel = None
    año_sel = None
    
    if sel_proyecto:
        st.sidebar.divider()
        st.sidebar.subheader("📅 Mes")
        
        # Obtener meses del proyecto seleccionado
        meses_proyecto = obtener_meses_proyecto(db, sel_proyecto.id)
        
        if meses_proyecto:
            # Crear opciones para el selectbox
            opciones_meses = []
            for año, mes in meses_proyecto:
                # CORREGIDO: Usar MESES_ES en lugar de calendar.month_name
                opciones_meses.append((año, mes, f"{MESES_ES[mes]} {año}"))
            
            # Seleccionar mes actual por defecto
            hoy = datetime.date.today()
            indice_default = 0
            for i, (año, mes, _) in enumerate(opciones_meses):
                if año == hoy.year and mes == hoy.month:
                    indice_default = i
                    break
            
            mes_seleccionado = st.sidebar.selectbox(
                "Mes actual",
                options=opciones_meses,
                format_func=lambda x: x[2],
                index=indice_default if indice_default < len(opciones_meses) else 0,
                key="selector_mes"
            )
            
            año_sel, mes_sel, _ = mes_seleccionado
        
        # Botón para agregar nuevo mes
        if st.sidebar.button("➕ Agregar mes"):
            st.session_state["show_add_month"] = True

        # Formulario para agregar mes
        if st.session_state.get("show_add_month", False):
            with st.sidebar.form("form_agregar_mes"):
                st.write("**Agregar nuevo mes:**")
                hoy = datetime.date.today()
                nuevo_año = st.number_input("Año", min_value=2020, max_value=2100, value=hoy.year)
                
                # CORREGIDO: Usar selectbox con nombres de meses
                opciones_meses_form = [(num, nombre) for num, nombre in MESES_ES.items()]
                mes_seleccionado_form = st.selectbox(
                    "Mes",
                    options=opciones_meses_form,
                    format_func=lambda x: x[1],  # Mostrar el nombre del mes
                    index=hoy.month - 1  # Mes actual por defecto (restamos 1 porque el índice empieza en 0)
                )
                nuevo_mes = mes_seleccionado_form[0]  # Obtener el número del mes
                
                col1, col2 = st.columns(2)
                with col1:
                    agregar = st.form_submit_button("Agregar", type="primary")
                with col2:
                    cancelar_mes = st.form_submit_button("Cancelar")
                
                if agregar:
                    if agregar_mes_proyecto(db, sel_proyecto, nuevo_año, nuevo_mes):
                        # CORREGIDO: Usar MESES_ES
                        st.success(f"✅ {MESES_ES[nuevo_mes]} {nuevo_año} agregado")
                        st.session_state["show_add_month"] = False
                        st.rerun()
                    else:
                        st.error("Este mes ya existe en el proyecto")
                
                if cancelar_mes:
                    st.session_state["show_add_month"] = False
                    st.rerun()

    # ---------- FORMULARIO CREAR PROYECTO ----------
    if st.session_state["show_project_modal"]:
        with st.expander("🆕 Nuevo proyecto", expanded=True):
            with st.form("form_nuevo_proyecto"):
                nombre = st.text_input("Nombre del proyecto")
                descripcion = st.text_area("Descripción", "")
                hoy = datetime.date.today()
                colm1, colm2 = st.columns(2)
                with colm1:
                    anio = st.number_input("Año", min_value=2020, max_value=2100, value=hoy.year)
                with colm2:
                    mes = st.number_input("Mes", min_value=1, max_value=12, value=hoy.month)

                colb1, colb2 = st.columns(2)
                with colb1:
                    crear = st.form_submit_button("Crear", type="primary")
                with colb2:
                    cancelar = st.form_submit_button("Cancelar")

                if crear and nombre.strip():
                    nuevo = Proyecto(
                        nombre=nombre,
                        descripcion=descripcion,
                        anio=anio,
                        mes=mes,
                    )
                    db.add(nuevo)
                    db.commit()
                    db.refresh(nuevo)
                    generar_dias_para_proyecto(db, nuevo)
                    st.success("Proyecto creado ✅")
                    st.session_state["show_project_modal"] = False
                    st.rerun()
                elif crear and not nombre.strip():
                    st.error("El nombre del proyecto es obligatorio")

                if cancelar:
                    st.session_state["show_project_modal"] = False
                    st.rerun()

        st.divider()

    # ---------- MAIN ----------
    if not st.session_state.get("show_project_modal", False):
        st.title("🕒 Mis horas")

        # CORREGIDO: Mensaje diferente si no hay proyecto seleccionado
        if not sel_proyecto:
            st.info("Selecciona un proyecto desde el sidebar para comenzar.")
            return

        if not proyectos:
            st.info("No hay proyectos todavía. Creá uno desde el sidebar.")
            return

        if not mes_sel or not año_sel:
            st.info("Selecciona un mes desde el sidebar para continuar.")
            return

        proyecto_sel: Proyecto = sel_proyecto

        col_izq, col_der = st.columns([1.1, 1.4], gap="large")

        # ===================== IZQUIERDA: DÍAS =====================
        with col_izq:
            # CORREGIDO: Usar MESES_ES
            st.subheader(f"{MESES_ES[mes_sel]} {año_sel} – días")

            # Filtrar días por mes y año seleccionado
            print(f"DEBUG - Filtrando días para proyecto {proyecto_sel.id}, año {año_sel}, mes {mes_sel}")
            
            dias = (
                db.query(Dia)
                .filter(
                    Dia.proyecto_id == proyecto_sel.id,
                    func.extract('year', Dia.fecha) == año_sel,
                    func.extract('month', Dia.fecha) == mes_sel
                )
                .order_by(Dia.fecha.asc())
                .all()
            )
            
            print(f"DEBUG - Días encontrados: {len(dias)}")
            for d in dias[:5]:  # Mostrar solo los primeros 5
                print(f"  - {d.fecha} ({d.dia_semana})")

            # Crear DataFrame con formato HH:MM
            data_dias = []
            for d in dias:
                horas_reales = d.horas_trabajadas / 2
                data_dias.append(
                    {
                        "id": d.id,
                        "Fecha": d.fecha.strftime("%d/%m/%Y"),
                        "Día": d.dia_semana,
                        "Horas Trabajadas": horas_a_formato(d.horas_trabajadas),
                        "Horas Reales": horas_a_formato(horas_reales),
                    }
                )
            df_dias = pd.DataFrame(data_dias)

            # Data editor con formato de texto para HH:MM
            edited = st.data_editor(
                df_dias,
                hide_index=True,
                column_config={
                    "id": None,
                    "Fecha": st.column_config.Column(disabled=True),
                    "Día": st.column_config.Column(disabled=True),
                    "Horas Trabajadas": st.column_config.TextColumn(
                        help="Formato HH:MM (ej: 02:30 para 2 horas y 30 minutos)",
                        width="small"
                    ),
                    "Horas Reales": st.column_config.TextColumn(
                        disabled=True,
                        help="Se calcula automáticamente: Horas Trabajadas ÷ 2",
                        width="small"
                    ),
                },
                use_container_width=True,
                num_rows="fixed",
                key=f"dias_editor_{proyecto_sel.id}_{año_sel}_{mes_sel}"
            )

            # Detectar cambios y guardar automáticamente
            key_prev = f"dias_editor_prev_{proyecto_sel.id}_{año_sel}_{mes_sel}"
            if key_prev not in st.session_state:
                st.session_state[key_prev] = df_dias

            # CORREGIDO: Comparar cambios y actualizar tareas afectadas
            if not edited.equals(st.session_state[key_prev]):
                cambios_detectados = False
                dias_modificados = []
                
                for _, row in edited.iterrows():
                    dia_db = db.query(Dia).filter(Dia.id == int(row["id"])).first()
                    if dia_db:
                        horas_trabajadas = formato_a_horas(str(row["Horas Trabajadas"]))
                        if dia_db.horas_trabajadas != horas_trabajadas:
                            dia_db.horas_trabajadas = horas_trabajadas
                            dia_db.horas_reales = horas_trabajadas / 2
                            dias_modificados.append(dia_db)
                            cambios_detectados = True
                
                if cambios_detectados:
                    db.commit()
                    
                    # CORREGIDO: Recalcular horas de tareas que usan estos días
                    for dia_modificado in dias_modificados:
                        # Buscar tareas que usan este día
                        tareas_afectadas = db.query(Tarea).filter(
                            Tarea.dias.contains(dia_modificado)
                        ).all()
                        
                        for tarea in tareas_afectadas:
                            tarea.horas = calcular_horas_tarea(tarea)
                    
                    db.commit()
                    st.session_state[key_prev] = edited.copy()
                    st.success("✅ Guardado automáticamente")
                    st.rerun()

            # Totales en formato HH:MM
            total_trab = sum(d.horas_trabajadas for d in dias)
            total_real = sum(d.horas_reales for d in dias)
            st.markdown(f"**Total horas trabajadas:** {horas_a_formato(total_trab)}")
            st.markdown(f"**Total horas reales:** {horas_a_formato(total_real)}")

        # ===================== DERECHA: TAREAS =====================
        with col_der:
            # Header con botón de exportar
            col_titulo, col_export = st.columns([3, 1])
            
            with col_titulo:
                # CORREGIDO: Usar MESES_ES
                st.subheader(f"Tareas {MESES_ES[mes_sel]} – {proyecto_sel.nombre}")
            
            with col_export:
                if st.button("📄 Exportar PDF", help="Descargar tabla de tareas en PDF"):
                    # Obtener todas las tareas para el PDF
                    tareas_pdf = (
                        db.query(Tarea)
                        .filter(Tarea.proyecto_id == proyecto_sel.id)
                        .order_by(Tarea.id.asc())
                        .all()
                    )
                    
                    if tareas_pdf:
                        # Generar PDF
                        pdf_buffer = generar_pdf_tareas(
                            tareas_pdf, 
                            proyecto_sel.nombre, 
                            MESES_ES[mes_sel],  # CORREGIDO: Usar MESES_ES
                            año_sel
                        )
                        
                        # Nombre del archivo - CORREGIDO
                        nombre_archivo = f"tareas_{proyecto_sel.nombre}_{MESES_ES[mes_sel]}_{año_sel}.pdf".replace(" ", "_")

                        # Botón de descarga
                        st.download_button(
                            label="⬇️ Descargar PDF",
                            data=pdf_buffer.getvalue(),
                            file_name=nombre_archivo,
                            mime="application/pdf"
                        )
                    else:
                        st.error("No hay tareas para exportar")

            # Formulario para nueva tarea (SIN campo horas) - CON RESET
            with st.expander("➕ Nueva tarea", expanded=True):
                # Clave única para resetear el formulario
                form_key = f"form_nueva_tarea_{st.session_state.get('form_reset_counter', 0)}"
                
                with st.form(form_key):
                    col1, col2 = st.columns([1.5, 1])
                    with col1:
                        titulo = st.text_input("Tarea")
                        detalle = st.text_area("Detalle")
                    with col2:
                        que_falta = st.text_area("¿Qué falta?")
                    
                    # CORREGIDO: Solo días disponibles (no asignados a otras tareas)
                    dias_disponibles = obtener_dias_disponibles(db, proyecto_sel.id, año_sel, mes_sel)
                    dias_del_mes = [
                        f"{d.fecha.strftime('%d/%m/%Y')} - {d.dia_semana}" for d in dias_disponibles
                    ]
                    dias_sel = st.multiselect(
                        "Días trabajados en eso", 
                        options=dias_del_mes,
                        help="Solo se muestran días no asignados a otras tareas"
                    )

                    guardar = st.form_submit_button("Guardar tarea", type="primary")

                    if guardar and titulo.strip():
                        # Crear tarea
                        tarea = Tarea(
                            titulo=titulo,
                            detalle=detalle,
                            horas="",
                            que_falta=que_falta,
                            proyecto_id=proyecto_sel.id,
                        )
                        db.add(tarea)
                        db.commit()
                        db.refresh(tarea)

                        # CORREGIDO: Mapear días disponibles (no todos los días)
                        mapa = {
                            f"{d.fecha.strftime('%d/%m/%Y')} - {d.dia_semana}": d for d in dias_disponibles
                        }
                        for dsel in dias_sel:
                            d_obj = mapa[dsel]
                            tarea.dias.append(d_obj)
                        
                        # Calcular y guardar horas automáticamente
                        tarea.horas = calcular_horas_tarea(tarea)
                        db.commit()
                        
                        # RESETEAR FORMULARIO
                        if 'form_reset_counter' not in st.session_state:
                            st.session_state['form_reset_counter'] = 0
                        st.session_state['form_reset_counter'] += 1
                        
                        st.success("Tarea creada ✅")
                        st.rerun()
                    elif guardar and not titulo.strip():
                        st.error("El título de la tarea es obligatorio")

            # Cargar tareas del proyecto (ORDENADAS POR ID ASC - más antigua primero)
            tareas = (
                db.query(Tarea)
                .filter(Tarea.proyecto_id == proyecto_sel.id)
                .order_by(Tarea.id.asc())  # CAMBIADO: de más antigua a más reciente
                .all()
            )

            # Tabla de tareas con botones integrados EN la tabla
            if tareas:
                # Preparar datos con columnas de acción
                data_tareas = []
                for i, t in enumerate(tareas):
                    # Recalcular horas en tiempo real
                    horas_calculadas = calcular_horas_tarea(t)
                    # Actualizar en la BD si es diferente
                    if t.horas != horas_calculadas:
                        t.horas = horas_calculadas
                        db.commit()
                    
                    data_tareas.append(
                        {
                            "ID": t.id,
                            "Tarea": t.titulo,
                            "Detalle": t.detalle if t.detalle else "Sin detalle",
                            "Horas": horas_calculadas,
                            "¿Qué falta?": t.que_falta if t.que_falta else "Nada",
                            "Días": ", ".join([d.fecha.strftime("%d/%m") for d in t.dias]) if t.dias else "Sin días",
                            "Editar": st.session_state.get(f"editing_task_{t.id}", False),  # CORREGIDO: Mantener estado
                            "Eliminar": False,  # Columna de checkbox para eliminar
                        }
                    )

                df_tareas = pd.DataFrame(data_tareas)
                
                # Usar data_editor con columnas de checkbox
                edited_df = st.data_editor(
                    df_tareas,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "ID": None,  # Ocultar ID
                        "Tarea": st.column_config.TextColumn("Tarea", width="medium", disabled=True),
                        "Detalle": st.column_config.TextColumn("Detalle", width="large", disabled=True),
                        "Horas": st.column_config.TextColumn("Horas", width="small", disabled=True),
                        "¿Qué falta?": st.column_config.TextColumn("¿Qué falta?", width="medium", disabled=True),
                        "Días": st.column_config.TextColumn("Días", width="medium", disabled=True),
                        "Editar": st.column_config.CheckboxColumn("✏️", help="Marcar para editar"),
                        "Eliminar": st.column_config.CheckboxColumn("🗑️", help="Marcar para eliminar"),
                    },
                    key="tabla_tareas_con_acciones"
                )

                # CORREGIDO: Procesar acciones seleccionadas
                for index, row in edited_df.iterrows():
                    tarea_id = int(row["ID"])
                    
                    # Acción EDITAR - Cambiar estado si se marcó/desmarcó
                    current_editing = st.session_state.get(f"editing_task_{tarea_id}", False)
                    if row["Editar"] != current_editing:
                        st.session_state[f"editing_task_{tarea_id}"] = row["Editar"]
                        if not row["Editar"]:
                            # Si se desmarcó, limpiar estados de confirmación
                            st.session_state[f"confirm_delete_{tarea_id}"] = False
                        st.rerun()
                    
                    # Acción ELIMINAR
                    if row["Eliminar"]:
                        tarea_a_eliminar = db.query(Tarea).filter(Tarea.id == tarea_id).first()
                        if tarea_a_eliminar:
                            if st.session_state.get(f"confirm_delete_{tarea_id}", False):
                                db.delete(tarea_a_eliminar)
                                db.commit()
                                st.session_state[f"confirm_delete_{tarea_id}"] = False
                                st.success(f"Tarea '{tarea_a_eliminar.titulo}' eliminada ✅")
                                st.rerun()
                            else:
                                st.session_state[f"confirm_delete_{tarea_id}"] = True
                                st.warning(f"¿Confirmar eliminar '{tarea_a_eliminar.titulo}'? Marca la casilla nuevamente.")

                # CORREGIDO: FORMULARIOS DE EDICIÓN (sin botón cancelar)
                for t in tareas:
                    if st.session_state.get(f"editing_task_{t.id}", False):
                        st.divider()
                        with st.expander(f"✏️ Editando: {t.titulo}", expanded=True):
                            with st.form(f"edit_form_{t.id}"):
                                # Campos editables
                                col1_edit, col2_edit = st.columns([1.5, 1])
                                with col1_edit:
                                    titulo_edit = st.text_input("Tarea", value=t.titulo)
                                    detalle_edit = st.text_area("Detalle", value=t.detalle or "")
                                with col2_edit:
                                    que_falta_edit = st.text_area("¿Qué falta?", value=t.que_falta or "")
                                
                                # Días disponibles (incluyendo los ya asignados a esta tarea)
                                dias_disponibles_edit = obtener_dias_disponibles(
                                    db, proyecto_sel.id, año_sel, mes_sel, t.id
                                )
                                
                                # Agregar días ya asignados a esta tarea
                                dias_actuales = list(t.dias)
                                todos_dias_edit = dias_disponibles_edit + dias_actuales
                                
                                # Remover duplicados y ordenar
                                todos_dias_edit = list({dia.id: dia for dia in todos_dias_edit}.values())
                                todos_dias_edit.sort(key=lambda x: x.fecha)
                                
                                # Crear opciones para multiselect
                                opciones_dias_edit = [
                                    f"{d.fecha.strftime('%d/%m/%Y')} - {d.dia_semana}" 
                                    for d in todos_dias_edit
                                ]
                                
                                # Días preseleccionados (los que ya tiene la tarea)
                                dias_preseleccionados = [
                                    f"{d.fecha.strftime('%d/%m/%Y')} - {d.dia_semana}" 
                                    for d in t.dias
                                ]
                                
                                dias_sel_edit = st.multiselect(
                                    "Días trabajados en eso",
                                    options=opciones_dias_edit,
                                    default=dias_preseleccionados,
                                    help="Días disponibles + días ya asignados a esta tarea. Para cancelar, desmarca la casilla ✏️ arriba."
                                )
                                
                                # CORREGIDO: Solo botón de guardar
                                guardar_edit = st.form_submit_button("💾 Guardar cambios", type="primary")
                                
                                if guardar_edit and titulo_edit.strip():
                                    # Actualizar campos básicos
                                    t.titulo = titulo_edit
                                    t.detalle = detalle_edit
                                    t.que_falta = que_falta_edit
                                    
                                    # Limpiar días actuales
                                    t.dias.clear()
                                    
                                    # Asignar nuevos días
                                    mapa_edit = {
                                        f"{d.fecha.strftime('%d/%m/%Y')} - {d.dia_semana}": d 
                                        for d in todos_dias_edit
                                    }
                                    for dsel in dias_sel_edit:
                                        d_obj = mapa_edit[dsel]
                                        t.dias.append(d_obj)
                                    
                                    # Recalcular horas
                                    t.horas = calcular_horas_tarea(t)
                                    
                                    db.commit()
                                    # CORREGIDO: Cerrar modal automáticamente
                                    st.session_state[f"editing_task_{t.id}"] = False
                                    st.success("Tarea actualizada ✅")
                                    st.rerun()
                                
                                elif guardar_edit and not titulo_edit.strip():
                                    st.error("El título de la tarea es obligatorio")

                # Resumen de horas por tareas en formato HH:MM
                total_horas_tareas = sum(
                    sum(dia.horas_reales for dia in tarea.dias) for tarea in tareas
                )
                st.markdown(f"**Total horas reales en tareas:** {horas_a_formato(total_horas_tareas)}")
                st.write(f"📝 {len(tareas)} tareas registradas")
            else:
                st.info("No hay tareas registradas para este proyecto.")


if __name__ == "__main__":
    main()
