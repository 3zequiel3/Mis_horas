import streamlit as st
from sqlalchemy.orm import Session
from services.proyecto_service import obtener_estadisticas_usuario, cambiar_estado_proyecto
from components.forms import render_project_form
from components.dias_section import render_dias_section
from components.tareas_section import render_tareas_section
from utils.constants import MESES_ES

def render_dashboard_index(db: Session):
    """Página de índice principal del dashboard"""
    
    # Mostrar formulario de proyecto si está activo
    if st.session_state.get("show_project_modal", False):
        render_project_form(db)
        return
    
    # Obtener selección del sidebar
    sel_proyecto = st.session_state.get("proyecto_seleccionado")
    mes_sel = st.session_state.get("mes_seleccionado")
    año_sel = st.session_state.get("año_seleccionado")
    
    # Header
    st.title(f"🏠 Bienvenido, {st.session_state.get('user_nombre', 'Usuario')}")
    st.markdown("---")
    
    # Si hay proyecto y mes seleccionados, mostrar vista de trabajo
    if sel_proyecto and mes_sel and año_sel:
        render_project_work_view(db, sel_proyecto, año_sel, mes_sel)
    else:
        # Mostrar resumen y estadísticas
        render_dashboard_overview(db)

def render_dashboard_overview(db: Session):
    """Vista general del dashboard sin proyecto seleccionado"""
    
    # Obtener estadísticas reales
    stats = obtener_estadisticas_usuario(db, st.session_state.user_id)
    
    # Estadísticas en cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div style='padding: 20px; border-radius: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); text-align: center;'>
                <div style='font-size: 14px; color: #fff; margin-bottom: 10px;'>📁 Proyectos Activos</div>
                <div style='font-size: 36px; font-weight: bold; color: #fff;'>{stats['proyectos_activos']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style='padding: 20px; border-radius: 10px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); text-align: center;'>
                <div style='font-size: 14px; color: #fff; margin-bottom: 10px;'>⏰ Horas Totales</div>
                <div style='font-size: 36px; font-weight: bold; color: #fff;'>{stats['total_horas']:.1f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div style='padding: 20px; border-radius: 10px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); text-align: center;'>
                <div style='font-size: 14px; color: #fff; margin-bottom: 10px;'>📊 Esta Semana</div>
                <div style='font-size: 36px; font-weight: bold; color: #fff;'>{stats['horas_semana']:.1f}h</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"""
            <div style='padding: 20px; border-radius: 10px; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); text-align: center;'>
                <div style='font-size: 14px; color: #fff; margin-bottom: 10px;'>📈 Promedio Diario</div>
                <div style='font-size: 36px; font-weight: bold; color: #fff;'>{stats['promedio_diario']:.1f}h</div>
            </div>
            """,
            unsafe_allow_html=True
        )
     
    st.markdown("---")

def render_project_work_view(db: Session, sel_proyecto, año_sel, mes_sel):
    """Vista principal de trabajo con proyecto seleccionado"""
    
    # Header del proyecto
    estado_badge = "🟢 Activo" if sel_proyecto.activo else "⏸️ Finalizado"
    
    col_header, col_action = st.columns([4, 1])
    
    with col_header:
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       padding: 25px; border-radius: 15px; margin-bottom: 20px;'>
                <div style='font-size: 28px; font-weight: bold; color: #fff; margin-bottom: 8px;'>
                    📁 {sel_proyecto.nombre}
                </div>
                <div style='font-size: 14px; color: #ddd; margin-bottom: 8px;'>
                    {sel_proyecto.descripcion if sel_proyecto.descripcion else 'Sin descripción'}
                </div>
                <div style='font-size: 13px; color: #ccc;'>
                    📅 {MESES_ES[mes_sel]} {año_sel} • {estado_badge}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col_action:
        st.write("")
        st.write("")
        if sel_proyecto.activo:
            if st.button("⏸️ Finalizar", key="finish_main", use_container_width=True):
                cambiar_estado_proyecto(db, sel_proyecto.id, False)
                st.success("Proyecto finalizado")
                st.rerun()
        else:
            if st.button("✅ Reactivar", key="activate_main", use_container_width=True):
                cambiar_estado_proyecto(db, sel_proyecto.id, True)
                st.success("Proyecto reactivado")
                st.rerun()
    
    # Layout de dos columnas: días | tareas
    col_izq, col_der = st.columns([1.1, 1.4], gap="large")
    
    with col_izq:
        render_dias_section(db, sel_proyecto, año_sel, mes_sel)
    
    with col_der:
        render_tareas_section(db, sel_proyecto, año_sel, mes_sel)