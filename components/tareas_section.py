# tareas_section.py
import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from services.tarea_service import (
    obtener_dias_disponibles, crear_tarea, actualizar_tarea, 
    obtener_tareas_proyecto, eliminar_tarea, calcular_horas_tarea
)
from services.pdf_service import generar_pdf_tareas
from utils.constants import MESES_ES
from utils.formatters import horas_a_formato

def render_tareas_section(db: Session, proyecto, año_sel: int, mes_sel: int):
    """Renderiza la sección completa de tareas"""
    # Header con botón de exportar
    col_titulo, col_export = st.columns([3, 1])
    
    with col_titulo:
        st.subheader(f"Tareas {MESES_ES[mes_sel]} – {proyecto.nombre}")
    
    with col_export:
        render_export_button(db, proyecto, mes_sel, año_sel)

    # Formulario para nueva tarea
    render_new_task_form(db, proyecto, año_sel, mes_sel)

    # Tabla de tareas
    render_tasks_table(db, proyecto, año_sel, mes_sel)

def render_export_button(db: Session, proyecto, mes_sel: int, año_sel: int):
    """Renderiza el botón de exportar PDF"""
    if st.button("📄 Exportar PDF", help="Descargar tabla de tareas en PDF"):
        tareas_pdf = obtener_tareas_proyecto(db, proyecto.id)
        
        if tareas_pdf:
            pdf_buffer = generar_pdf_tareas(
                tareas_pdf, 
                proyecto.nombre, 
                MESES_ES[mes_sel], 
                año_sel
            )
            
            nombre_archivo = f"tareas_{proyecto.nombre}_{MESES_ES[mes_sel]}_{año_sel}.pdf".replace(" ", "_")
            
            st.download_button(
                label="⬇️ Descargar PDF",
                data=pdf_buffer.getvalue(),
                file_name=nombre_archivo,
                mime="application/pdf"
            )
        else:
            st.error("No hay tareas para exportar")

def render_new_task_form(db: Session, proyecto, año_sel: int, mes_sel: int):
    """Renderiza el formulario para crear nueva tarea"""
    with st.expander("➕ Nueva tarea", expanded=True):
        form_key = f"form_nueva_tarea_{st.session_state.get('form_reset_counter', 0)}"
        
        with st.form(form_key):
            col1, col2 = st.columns([1.5, 1])
            with col1:
                titulo = st.text_input("Tarea")
                detalle = st.text_area("Detalle")
            with col2:
                que_falta = st.text_area("¿Qué falta?")
            
            # Solo días disponibles
            dias_disponibles = obtener_dias_disponibles(db, proyecto.id, año_sel, mes_sel)
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
                # Mapear días seleccionados
                mapa = {
                    f"{d.fecha.strftime('%d/%m/%Y')} - {d.dia_semana}": d for d in dias_disponibles
                }
                dias_seleccionados = [mapa[dsel] for dsel in dias_sel]
                
                crear_tarea(db, titulo, detalle, que_falta, proyecto.id, dias_seleccionados)
                
                # Reset formulario
                if 'form_reset_counter' not in st.session_state:
                    st.session_state['form_reset_counter'] = 0
                st.session_state['form_reset_counter'] += 1
                
                st.success("Tarea creada ✅")
                st.rerun()
            elif guardar and not titulo.strip():
                st.error("El título de la tarea es obligatorio")

def render_tasks_table(db: Session, proyecto, año_sel: int, mes_sel: int):
    """Renderiza la tabla de tareas con funcionalidad de edición"""
    tareas = obtener_tareas_proyecto(db, proyecto.id)

    if tareas:
        # Preparar datos con columnas de acción
        data_tareas = []
        for t in tareas:
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
                    "Editar": st.session_state.get(f"editing_task_{t.id}", False),
                    "Eliminar": False,
                }
            )

        df_tareas = pd.DataFrame(data_tareas)
        
        # Data editor con columnas de acción
        edited_df = st.data_editor(
            df_tareas,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": None,
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

        # Procesar acciones
        process_task_actions(db, edited_df, proyecto, año_sel, mes_sel)

        # Formularios de edición
        render_edit_forms(db, tareas, proyecto, año_sel, mes_sel)

        # Resumen
        total_horas_tareas = sum(
            sum(dia.horas_reales for dia in tarea.dias) for tarea in tareas
        )
        st.markdown(f"**Total horas reales en tareas:** {horas_a_formato(total_horas_tareas)}")
        st.write(f"📝 {len(tareas)} tareas registradas")
    else:
        st.info("No hay tareas registradas para este proyecto.")

def process_task_actions(db: Session, edited_df: pd.DataFrame, proyecto, año_sel: int, mes_sel: int):
    """Procesa las acciones de editar y eliminar de la tabla"""
    for index, row in edited_df.iterrows():
        tarea_id = int(row["ID"])
        
        # Acción EDITAR
        current_editing = st.session_state.get(f"editing_task_{tarea_id}", False)
        if row["Editar"] != current_editing:
            st.session_state[f"editing_task_{tarea_id}"] = row["Editar"]
            if not row["Editar"]:
                st.session_state[f"confirm_delete_{tarea_id}"] = False
            st.rerun()
        
        # Acción ELIMINAR
        if row["Eliminar"]:
            if st.session_state.get(f"confirm_delete_{tarea_id}", False):
                if eliminar_tarea(db, tarea_id):
                    st.session_state[f"confirm_delete_{tarea_id}"] = False
                    st.success("Tarea eliminada ✅")
                    st.rerun()
            else:
                st.session_state[f"confirm_delete_{tarea_id}"] = True
                st.warning("¿Confirmar eliminar? Marca la casilla nuevamente.")

def render_edit_forms(db: Session, tareas, proyecto, año_sel: int, mes_sel: int):
    """Renderiza los formularios de edición de tareas"""
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
                    
                    # Días disponibles + días actuales
                    dias_disponibles_edit = obtener_dias_disponibles(
                        db, proyecto.id, año_sel, mes_sel, t.id
                    )
                    
                    dias_actuales = list(t.dias)
                    todos_dias_edit = dias_disponibles_edit + dias_actuales
                    todos_dias_edit = list({dia.id: dia for dia in todos_dias_edit}.values())
                    todos_dias_edit.sort(key=lambda x: x.fecha)
                    
                    opciones_dias_edit = [
                        f"{d.fecha.strftime('%d/%m/%Y')} - {d.dia_semana}" 
                        for d in todos_dias_edit
                    ]
                    
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
                    
                    guardar_edit = st.form_submit_button("💾 Guardar cambios", type="primary")
                    
                    if guardar_edit and titulo_edit.strip():
                        # Mapear días seleccionados
                        mapa_edit = {
                            f"{d.fecha.strftime('%d/%m/%Y')} - {d.dia_semana}": d 
                            for d in todos_dias_edit
                        }
                        dias_seleccionados = [mapa_edit[dsel] for dsel in dias_sel_edit]
                        
                        actualizar_tarea(db, t.id, titulo_edit, detalle_edit, que_falta_edit, dias_seleccionados)
                        
                        st.session_state[f"editing_task_{t.id}"] = False
                        st.success("Tarea actualizada ✅")
                        st.rerun()
                    
                    elif guardar_edit and not titulo_edit.strip():
                        st.error("El título de la tarea es obligatorio")