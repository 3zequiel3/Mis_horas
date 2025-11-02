import streamlit as st
from sqlalchemy.orm import Session
from components.forms import render_project_form
from components.dias_section import render_dias_section  
from components.tareas_section import render_tareas_section
from services.proyecto_service import (
    obtener_proyectos_usuario, 
    obtener_meses_proyecto, 
    agregar_mes_proyecto,
    cambiar_estado_proyecto
)
from utils.constants import MESES_ES
import datetime

def render_proyectos_page(db: Session):
    """Página principal de gestión de proyectos"""
    
    # Sidebar con proyectos
    sel_proyecto, mes_sel, año_sel, proyectos = render_sidebar_proyectos_only(db)
    
    # Mostrar formulario de proyecto si está activo
    if st.session_state.get("show_project_modal", False):
        st.title("📁 Gestión de Proyectos")
        render_project_form(db)
        return
    
    # Contenido principal basado en selección
    if not sel_proyecto:
        st.title("📁 Gestión de Proyectos")
        render_no_project_selected(db, proyectos)
        return

    if not proyectos:
        st.title("📁 Gestión de Proyectos")
        render_no_projects_available()
        return

    if not mes_sel or not año_sel:
        st.title("📁 Gestión de Proyectos")
        render_no_month_selected()
        return

    # Vista principal de proyecto con días y tareas
    render_project_work_view(db, sel_proyecto, año_sel, mes_sel)

def render_sidebar_proyectos_only(db: Session):
    """Renderiza solo la parte de proyectos en el sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📁 Mis Proyectos")

    if "show_project_modal" not in st.session_state:
        st.session_state["show_project_modal"] = False

    proyectos = obtener_proyectos_usuario(db, st.session_state.user_id)

    opciones_proyectos = [None] + proyectos
    
    sel_proyecto = st.sidebar.selectbox(
        "Proyecto actual",
        options=opciones_proyectos,
        format_func=lambda x: "Sin seleccionar" if x is None else f"{'✅' if x.activo else '⏸️'} {x.nombre}",
        index=0,
    )

    if st.sidebar.button("➕ Nuevo proyecto", use_container_width=True):
        st.session_state["show_project_modal"] = True

    mes_sel = None
    año_sel = None
    
    if sel_proyecto:
        mes_sel, año_sel = render_month_selector(db, sel_proyecto)

    return sel_proyecto, mes_sel, año_sel, proyectos

def render_month_selector(db: Session, proyecto):
    """Renderiza selector de mes y botón para agregar nuevos meses"""
    st.sidebar.divider()
    st.sidebar.markdown("### 📅 Mes")
    
    meses_proyecto = obtener_meses_proyecto(db, proyecto.id)
    
    mes_sel = None
    año_sel = None
    
    if meses_proyecto:
        opciones_meses = []
        for año, mes in meses_proyecto:
            opciones_meses.append((año, mes, f"{MESES_ES[mes]} {año}"))
        
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
    
    if st.sidebar.button("➕ Agregar mes", use_container_width=True):
        st.session_state["show_add_month"] = True

    if st.session_state.get("show_add_month", False):
        render_add_month_form(db, proyecto)

    return mes_sel, año_sel

def render_add_month_form(db: Session, proyecto):
    """Formulario para agregar un nuevo mes al proyecto"""
    with st.sidebar.form("form_agregar_mes"):
        st.write("**Agregar nuevo mes:**")
        hoy = datetime.date.today()
        nuevo_año = st.number_input("Año", min_value=2020, max_value=2100, value=hoy.year)
        
        opciones_meses_form = [(num, nombre) for num, nombre in MESES_ES.items()]
        mes_seleccionado_form = st.selectbox(
            "Mes",
            options=opciones_meses_form,
            format_func=lambda x: x[1],
            index=hoy.month - 1
        )
        nuevo_mes = mes_seleccionado_form[0]
        
        col1, col2 = st.columns(2)
        with col1:
            agregar = st.form_submit_button("Agregar", type="primary")
        with col2:
            cancelar_mes = st.form_submit_button("Cancelar")
        
        if agregar:
            if agregar_mes_proyecto(db, proyecto, nuevo_año, nuevo_mes):
                st.success(f"✅ {MESES_ES[nuevo_mes]} {nuevo_año} agregado")
                st.session_state["show_add_month"] = False
                st.rerun()
            else:
                st.error("Este mes ya existe en el proyecto")
        
        if cancelar_mes:
            st.session_state["show_add_month"] = False
            st.rerun()

def render_no_project_selected(db: Session, proyectos):
    """Vista cuando no hay proyecto seleccionado - MEJORADA"""
    if proyectos:
        
        st.markdown("### 📋 Tus Proyectos")
        
        # Separar proyectos activos e inactivos
        proyectos_activos = [p for p in proyectos if p.activo]
        proyectos_inactivos = [p for p in proyectos if not p.activo]
        
        # Mostrar proyectos activos
        if proyectos_activos:
            st.markdown("####     ✅ Activos")
            for proyecto in proyectos_activos:
                render_project_card(db, proyecto)
        
        # Mostrar proyectos inactivos
        if proyectos_inactivos:
            with st.expander(f"⏸️ Finalizados ({len(proyectos_inactivos)})", expanded=False):
                for proyecto in proyectos_inactivos:
                    render_project_card(db, proyecto)
    else:
        render_no_projects_available()

def render_project_card(db: Session, proyecto):
    """Card individual para cada proyecto - MEJORADA"""
    estado_color = "#43e97b" if proyecto.activo else "#888"
    estado_icon = "✅" if proyecto.activo else "⏸️"
    estado_text = "Activo" if proyecto.activo else "Finalizado"
    
    with st.container():
        st.markdown(
            f"""
            <div style='padding: 20px; border-radius: 10px; background-color: #1E1E1E; 
                       border-left: 4px solid {estado_color}; margin-bottom: 15px;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <div style='font-size: 20px; font-weight: bold; color: #fff; margin-bottom: 8px;'>
                            {estado_icon} {proyecto.nombre}
                        </div>
                        <div style='font-size: 14px; color: #888; margin-bottom: 8px;'>
                            {proyecto.descripcion if proyecto.descripcion else 'Sin descripción'}
                        </div>
                        <div style='font-size: 12px; color: #666;'>
                            📅 Creado: {proyecto.mes}/{proyecto.anio} • Estado: {estado_text}
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if proyecto.activo:
                if st.button("⏸️ Finalizar", key=f"finish_{proyecto.id}", use_container_width=True):
                    cambiar_estado_proyecto(db, proyecto.id, False)
                    st.success(f"Proyecto '{proyecto.nombre}' finalizado")
                    st.rerun()
            else:
                if st.button("✅ Reactivar", key=f"activate_{proyecto.id}", use_container_width=True):
                    cambiar_estado_proyecto(db, proyecto.id, True)
                    st.success(f"Proyecto '{proyecto.nombre}' reactivado")
                    st.rerun()

def render_no_projects_available():
    """Vista cuando no hay proyectos"""
    st.markdown("""
    ### 🎯 ¡Empecemos!
    
    Parece que aún no tienes proyectos. Crear tu primer proyecto es muy fácil:
    
    1. 👈 Haz clic en "➕ Nuevo proyecto" en el sidebar
    2. 📝 Completa el nombre y descripción
    3. 📅 Selecciona el mes y año de inicio
    4. ✅ ¡Listo para empezar a registrar horas!
    """)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("➕ Crear Mi Primer Proyecto", type="primary", use_container_width=True):
            st.session_state["show_project_modal"] = True
            st.rerun()

def render_no_month_selected():
    """Vista cuando no hay mes seleccionado"""
    st.info("👈 Selecciona un mes desde el sidebar para continuar.")
    
    st.markdown("""
    ### 📅 Gestión de Meses
    
    Cada proyecto puede tener múltiples meses. Puedes:
    - Ver meses existentes en el selector
    - Agregar nuevos meses con el botón "➕ Agregar mes"
    - Navegar entre diferentes períodos
    """)

def render_project_work_view(db: Session, sel_proyecto, año_sel, mes_sel):
    """Vista principal de trabajo con proyecto seleccionado - MEJORADA"""
    # Header mejorado del proyecto
    col_header, col_actions = st.columns([4, 1])
    
    with col_header:
        estado_badge = "🟢 Activo" if sel_proyecto.activo else "⏸️ Finalizado"
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       padding: 30px; border-radius: 15px; margin-bottom: 20px;'>
                <div style='font-size: 32px; font-weight: bold; color: #fff; margin-bottom: 10px;'>
                    📁 {sel_proyecto.nombre}
                </div>
                <div style='font-size: 16px; color: #ddd; margin-bottom: 10px;'>
                    {sel_proyecto.descripcion if sel_proyecto.descripcion else 'Sin descripción'}
                </div>
                <div style='font-size: 14px; color: #ccc;'>
                    📅 {MESES_ES[mes_sel]} {año_sel} • {estado_badge}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col_actions:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        if sel_proyecto.activo:
            if st.button("⏸️ Finalizar", key="finish_main", use_container_width=True, type="secondary"):
                cambiar_estado_proyecto(db, sel_proyecto.id, False)
                st.success("Proyecto finalizado")
                st.rerun()
    
    # Layout de dos columnas: días | tareas
    col_izq, col_der = st.columns([1.1, 1.4], gap="large")

    with col_izq:
        render_dias_section(db, sel_proyecto, año_sel, mes_sel)

    with col_der:
        render_tareas_section(db, sel_proyecto, año_sel, mes_sel)