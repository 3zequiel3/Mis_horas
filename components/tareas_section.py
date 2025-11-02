import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import extract
from models import Dia, Tarea, Usuario
from services.tarea_service import (
    crear_tarea, 
    actualizar_tarea, 
    eliminar_tarea, 
    obtener_tareas_proyecto,
    obtener_horas_tarea_segun_usuario,
    obtener_dias_disponibles  # ← NUEVO: importar función
)
from services.pdf_service import generar_pdf_proyecto
from utils.constants import MESES_ES

def render_tareas_section(db: Session, proyecto, año_sel: int, mes_sel: int):
    """Sección de tareas del proyecto"""
    
    # Obtener configuración del usuario
    usar_horas_reales = st.session_state.get('user_usar_horas_reales', False)
    
    # Header con botones
    col1, col2 = st.columns([3, 1])
    with col1:
        titulo_modo = " (Horas Reales)" if usar_horas_reales else ""
        st.subheader(f"Tareas {MESES_ES[mes_sel]} – {proyecto.nombre}{titulo_modo}")
    with col2:
        if st.button("📥 Exportar PDF", use_container_width=True, type="primary"):
            exportar_pdf(db, proyecto, año_sel, mes_sel)
    
    st.divider()
    
    # Botón para nueva tarea
    col_btn, col_space = st.columns([1, 3])
    with col_btn:
        if st.button("➕ Nueva tarea", key="btn_nueva_tarea", use_container_width=True):
            st.session_state["show_tarea_form"] = True
    
    # Mostrar formulario si está activo
    if st.session_state.get("show_tarea_form", False):
        st.divider()
        render_tarea_form(db, proyecto, año_sel, mes_sel)
    
    st.divider()
    
    # Listar tareas existentes en formato tabla
    tareas = obtener_tareas_proyecto(db, proyecto.id)
    
    # Filtrar tareas del mes actual
    tareas_mes = []
    for tarea in tareas:
        if tarea.dias:
            # Verificar si algún día pertenece al mes/año seleccionado
            for dia in tarea.dias:
                if dia.fecha.year == año_sel and dia.fecha.month == mes_sel:
                    tareas_mes.append(tarea)
                    break
    
    if not tareas_mes:
        st.info("No hay tareas registradas para este mes")
    else:
        render_tareas_tabla_con_acciones(db, tareas_mes, proyecto, año_sel, mes_sel, usar_horas_reales)

def render_tarea_form(db: Session, proyecto, año_sel: int, mes_sel: int):
    """Formulario para crear nueva tarea - SOLO DÍAS DISPONIBLES"""
    
    with st.form("form_tarea", clear_on_submit=True):
        st.markdown("#### ➕ Nueva Tarea")
        
        titulo = st.text_input("Tarea*", placeholder="Ej: Desarrollo módulo de usuarios")
        
        col1, col2 = st.columns(2)
        with col1:
            detalle = st.text_area("Detalle", placeholder="Descripción detallada...", height=100)
        with col2:
            que_falta = st.text_area("¿Qué Falta?", placeholder="Tareas pendientes...", height=100)
        
        # ← CAMBIO: Obtener SOLO días disponibles (no asignados a otras tareas)
        dias_disponibles = obtener_dias_disponibles(
            db, 
            proyecto.id, 
            año_sel, 
            mes_sel,
            tarea_excluir_id=None  # None porque es creación
        )
        
        if not dias_disponibles:
            st.warning("⚠️ No hay días disponibles. Todos los días del mes están asignados a otras tareas.")
            st.info("💡 Puedes editar una tarea existente para reasignar días.")
        
        dias_options = {
            dia.id: f"{dia.fecha.strftime('%d/%m')} - {dia.dia_semana}" 
            for dia in dias_disponibles
        }
        
        dias_seleccionados = st.multiselect(
            "Días trabajados en esto*",
            options=list(dias_options.keys()),
            format_func=lambda x: dias_options[x],
            help="Solo se muestran días no asignados a otras tareas",
            disabled=not dias_disponibles
        )
        
        col_submit, col_cancel = st.columns(2)
        
        with col_submit:
            submit = st.form_submit_button("💾 Guardar tarea", type="primary", use_container_width=True)
        
        with col_cancel:
            cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if submit:
            if not titulo.strip():
                st.error("❌ El título es obligatorio")
            elif not dias_seleccionados:
                st.error("❌ Debes seleccionar al menos un día")
            else:
                # Crear tarea pasando user_id
                nueva_tarea = crear_tarea(
                    db,
                    proyecto_id=proyecto.id,
                    titulo=titulo,
                    detalle=detalle,
                    que_falta=que_falta,
                    dias_ids=dias_seleccionados,
                    usuario_id=st.session_state.user_id
                )
                
                if nueva_tarea:
                    st.success("✅ Tarea creada exitosamente")
                    st.session_state["show_tarea_form"] = False
                    st.rerun()
                else:
                    st.error("❌ Error al crear la tarea")
        
        if cancel:
            st.session_state["show_tarea_form"] = False
            st.rerun()

def render_tareas_tabla_con_acciones(db: Session, tareas: list, proyecto, año_sel: int, mes_sel: int, usar_horas_reales: bool):
    """Renderiza tabla de tareas con columnas de acción (Editar/Eliminar)"""
    
    # Preparar datos con checkboxes - mantener estado previo
    data_tareas = []
    for tarea in tareas:
        dias_mes = [d for d in tarea.dias if d.fecha.year == año_sel and d.fecha.month == mes_sel]
        dias_str = ", ".join([d.fecha.strftime("%d/%m") for d in dias_mes])
        
        # Obtener horas según configuración del usuario
        horas_mostrar = obtener_horas_tarea_segun_usuario(tarea, st.session_state.user_id, db)
        
        # Mantener estado de checkboxes
        editar_activo = st.session_state.get(f"edit_tarea_{tarea.id}", False)
        eliminar_activo = st.session_state.get(f"confirm_delete_{tarea.id}", False)
        
        row_data = {
            "id": tarea.id,
            "Tarea": tarea.titulo,
            "Detalle": tarea.detalle if tarea.detalle else "-",
            "¿Qué Falta?": tarea.que_falta if tarea.que_falta else "-",
            "Días": dias_str,
            "Horas": horas_mostrar,
            "✏️ Editar": editar_activo,
            "🗑️ Eliminar": eliminar_activo
        }
        data_tareas.append(row_data)
    
    df_tareas = pd.DataFrame(data_tareas)
    
    # Etiqueta de columna según configuración
    etiqueta_horas = "⏱️ Horas Reales" if usar_horas_reales else "⏰ Horas Trabajadas"
    
    column_config = {
        "id": None,
        "Tarea": st.column_config.TextColumn("📌 Tarea", width="medium"),
        "Detalle": st.column_config.TextColumn("📝 Detalle", width="large"),
        "¿Qué Falta?": st.column_config.TextColumn("❓ ¿Qué Falta?", width="large"),
        "Días": st.column_config.TextColumn("📅 Días Trabajados", width="medium"),
        "Horas": st.column_config.TextColumn(etiqueta_horas, width="small"),
        "✏️ Editar": st.column_config.CheckboxColumn("✏️ Editar", width="small"),
        "🗑️ Eliminar": st.column_config.CheckboxColumn("🗑️ Eliminar", width="small"),
    }
    
    # Editar la tabla
    edited_df = st.data_editor(
        df_tareas,
        hide_index=True,
        column_config=column_config,
        use_container_width=True,
        num_rows="fixed",
        key=f"tareas_tabla_{proyecto.id}_{año_sel}_{mes_sel}",
        disabled=["id", "Tarea", "Detalle", "¿Qué Falta?", "Días", "Horas"]
    )
    
    # Procesar acciones marcadas
    procesar_acciones_tabla(db, edited_df, tareas, proyecto, año_sel, mes_sel)
    
    st.divider()
    
    # Mostrar total de horas
    total_horas = 0
    for tarea in tareas:
        horas_str = obtener_horas_tarea_segun_usuario(tarea, st.session_state.user_id, db)
        # Convertir HH:MM a float
        if ':' in horas_str:
            partes = horas_str.split(':')
            horas_float = int(partes[0]) + (int(partes[1]) / 60.0)
            total_horas += horas_float
    
    from utils.formatters import horas_a_formato
    etiqueta_total = "💰 Total Horas Reales:" if usar_horas_reales else "⏰ Total Horas Trabajadas:"
    st.markdown(f"### {etiqueta_total} {horas_a_formato(total_horas)}")

def procesar_acciones_tabla(db: Session, edited_df: pd.DataFrame, 
                            tareas: list, proyecto, año_sel: int, mes_sel: int):
    """Procesa las acciones marcadas en la tabla (Editar/Eliminar)"""
    
    # Detectar cambios en los checkboxes y actualizar session_state
    for idx, row in edited_df.iterrows():
        tarea_id = row["id"]
        editar_marcado = row["✏️ Editar"]
        eliminar_marcado = row["🗑️ Eliminar"]
        
        # Gestionar estado de EDITAR
        estado_actual_editar = st.session_state.get(f"edit_tarea_{tarea_id}", False)
        if editar_marcado != estado_actual_editar:
            st.session_state[f"edit_tarea_{tarea_id}"] = editar_marcado
            # Si se desmarca, limpiar cualquier estado relacionado
            if not editar_marcado:
                # Limpiar estados de confirmación si existen
                if f"confirm_delete_{tarea_id}" in st.session_state:
                    st.session_state[f"confirm_delete_{tarea_id}"] = False
            st.rerun()
        
        # Gestionar estado de ELIMINAR
        estado_actual_eliminar = st.session_state.get(f"confirm_delete_{tarea_id}", False)
        if eliminar_marcado != estado_actual_eliminar:
            st.session_state[f"confirm_delete_{tarea_id}"] = eliminar_marcado
            # Si se desmarca, cerrar confirmación
            if not eliminar_marcado:
                # Limpiar estados de edición si existen
                if f"edit_tarea_{tarea_id}" in st.session_state:
                    st.session_state[f"edit_tarea_{tarea_id}"] = False
            st.rerun()
    
    # Mostrar formularios de edición inline si están activos
    for tarea in tareas:
        if st.session_state.get(f"edit_tarea_{tarea.id}", False):
            st.divider()
            render_editar_tarea_inline(db, tarea, proyecto, año_sel, mes_sel)
    
    # Mostrar confirmaciones de eliminación
    for tarea in tareas:
        if st.session_state.get(f"confirm_delete_{tarea.id}", False):
            st.divider()
            st.warning(f"⚠️ ¿Estás seguro de eliminar la tarea **{tarea.titulo}**?")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("✅ Sí, eliminar", key=f"confirm_yes_{tarea.id}", type="primary", use_container_width=True):
                    if eliminar_tarea(db, tarea.id):
                        st.success("✅ Tarea eliminada exitosamente")
                        # Limpiar estado
                        st.session_state[f"confirm_delete_{tarea.id}"] = False
                        st.rerun()
            with col2:
                if st.button("❌ Cancelar", key=f"confirm_no_{tarea.id}", use_container_width=True):
                    # Desmarcar checkbox
                    st.session_state[f"confirm_delete_{tarea.id}"] = False
                    st.rerun()

def render_editar_tarea_inline(db: Session, tarea: Tarea, proyecto, año_sel: int, mes_sel: int):
    """Formulario inline para editar una tarea - INCLUYE DÍAS DISPONIBLES + PROPIOS"""
    
    with st.form(f"form_editar_tarea_{tarea.id}", clear_on_submit=False):
        st.markdown(f"#### ✏️ Editando: **{tarea.titulo}**")
        
        titulo = st.text_input("Tarea*", value=tarea.titulo, key=f"edit_titulo_{tarea.id}")
        
        col1, col2 = st.columns(2)
        with col1:
            detalle = st.text_area("Detalle", value=tarea.detalle if tarea.detalle else "", height=100, key=f"edit_detalle_{tarea.id}")
        with col2:
            que_falta = st.text_area("¿Qué Falta?", value=tarea.que_falta if tarea.que_falta else "", height=100, key=f"edit_falta_{tarea.id}")
        
        # ← CAMBIO: Obtener días disponibles EXCLUYENDO esta tarea
        dias_disponibles = obtener_dias_disponibles(
            db, 
            proyecto.id, 
            año_sel, 
            mes_sel,
            tarea_excluir_id=tarea.id  # ← Excluir esta tarea para permitir reasignación
        )
        
        dias_options = {
            dia.id: f"{dia.fecha.strftime('%d/%m')} - {dia.dia_semana}" 
            for dia in dias_disponibles
        }
        
        # Obtener días actuales de esta tarea
        dias_actuales = [d.id for d in tarea.dias if d.fecha.year == año_sel and d.fecha.month == mes_sel]
        
        dias_seleccionados = st.multiselect(
            "Días trabajados en esto*",
            options=list(dias_options.keys()),
            default=dias_actuales,
            format_func=lambda x: dias_options[x],
            help="Selecciona los días en los que trabajaste en esta tarea (incluye días propios + disponibles)",
            key=f"edit_dias_{tarea.id}"
        )
        
        col_submit, col_cancel = st.columns(2)
        
        with col_submit:
            submit = st.form_submit_button("💾 Guardar cambios", type="primary", use_container_width=True)
        
        with col_cancel:
            cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if submit:
            if not titulo.strip():
                st.error("❌ El título es obligatorio")
            elif not dias_seleccionados:
                st.error("❌ Debes seleccionar al menos un día")
            else:
                tarea_actualizada = actualizar_tarea(
                    db,
                    tarea_id=tarea.id,
                    titulo=titulo,
                    detalle=detalle,
                    que_falta=que_falta,
                    dias_ids=dias_seleccionados,
                    usuario_id=st.session_state.user_id
                )
                
                if tarea_actualizada:
                    st.success("✅ Tarea actualizada exitosamente")
                    # Desmarcar checkbox y cerrar formulario
                    st.session_state[f"edit_tarea_{tarea.id}"] = False
                    st.rerun()
                else:
                    st.error("❌ Error al actualizar la tarea")
        
        if cancel:
            # Desmarcar checkbox y cerrar formulario
            st.session_state[f"edit_tarea_{tarea.id}"] = False
            st.rerun()

def exportar_pdf(db: Session, proyecto, año_sel: int, mes_sel: int):
    """Exporta el proyecto a PDF según configuración del usuario"""
    
    usuario = db.query(Usuario).filter(Usuario.id == st.session_state.user_id).first()
    usar_horas_reales = usuario.usar_horas_reales if usuario else False
    
    dias = db.query(Dia).filter(
        Dia.proyecto_id == proyecto.id,
        extract('year', Dia.fecha) == año_sel,
        extract('month', Dia.fecha) == mes_sel
    ).order_by(Dia.fecha).all()
    
    tareas = obtener_tareas_proyecto(db, proyecto.id)
    tareas_mes = []
    for tarea in tareas:
        if tarea.dias:
            for dia in tarea.dias:
                if dia.fecha.year == año_sel and dia.fecha.month == mes_sel:
                    tareas_mes.append(tarea)
                    break
    
    # Generar PDF con las tareas y la configuración
    pdf_buffer = generar_pdf_proyecto(
        proyecto, 
        dias, 
        tareas_mes, 
        mes_sel, 
        año_sel, 
        usar_horas_reales,
        st.session_state.user_id,
        db
    )
    
    st.download_button(
        label="📥 Descargar PDF",
        data=pdf_buffer,
        file_name=f"{proyecto.nombre}_{MESES_ES[mes_sel]}_{año_sel}.pdf",
        mime="application/pdf",
        use_container_width=True
    )