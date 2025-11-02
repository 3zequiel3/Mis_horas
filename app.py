import streamlit as st
from sqlalchemy.orm import Session
from db import init_db
from components.auth import render_login_page
from views.index import render_dashboard_index
from views.perfil import render_perfil_page
from utils.helpers import get_db
from services.auth_service import logout_usuario, activar_mantener_sesion

def main():
    """Aplicación principal con sistema de navegación"""
    init_db()
    db = next(get_db())
    
    # Verificar autenticación
    if not st.session_state.get('authenticated', False):
        render_login_page(db)
        return
    
    # Configurar página
    st.set_page_config(
        page_title="Mis Horas",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # CSS para ocultar el menú de páginas de Streamlit
    st.markdown("""
        <style>
            /* Ocultar lista de páginas generada por Streamlit */
            [data-testid="stSidebarNav"] {
                display: none;
            }
            
            /* Ocultar el selector de páginas */
            section[data-testid="stSidebarNav"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Inicializar página actual si no existe
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    # Sidebar con navegación condicional
    render_sidebar(db)
    
    # Renderizar página actual
    render_current_page(db)

def render_sidebar(db: Session):
    """Sidebar con navegación y gestión condicional de proyectos"""
    st.sidebar.title("🕒 Mis Horas")
    
    # Botón de logout
    if st.sidebar.button("🚪 Cerrar Sesión", key="logout_top", use_container_width=True, type="secondary"):
        if st.session_state.get('user_id'):
            activar_mantener_sesion(db, st.session_state.user_id, False)
        logout_usuario()
        st.rerun()
    
    st.sidebar.divider()
    
    # Navegación simple
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🏠 Inicio", key="nav_dashboard", use_container_width=True, 
                     type="primary" if st.session_state.current_page == "dashboard" else "secondary"):
            st.session_state.current_page = "dashboard"
            st.rerun()
    
    with col2:
        if st.button("👤 Perfil", key="nav_perfil", use_container_width=True,
                     type="primary" if st.session_state.current_page == "perfil" else "secondary"):
            st.session_state.current_page = "perfil"
            st.rerun()
    
    # Mostrar gestión de proyectos SOLO si estamos en la página de inicio
    if st.session_state.current_page == "dashboard":
        st.sidebar.divider()
        render_sidebar_projects(db)

def render_sidebar_projects(db: Session):
    """Renderiza la gestión de proyectos en el sidebar (solo para dashboard)"""
    from services.proyecto_service import obtener_proyectos_usuario, obtener_meses_proyecto, agregar_mes_proyecto
    from utils.constants import MESES_ES
    import datetime
    
    st.sidebar.markdown("### 📁 Mis Proyectos")
    
    if "show_project_modal" not in st.session_state:
        st.session_state["show_project_modal"] = False
    
    proyectos = obtener_proyectos_usuario(db, st.session_state.user_id)
    
    # Selectbox de proyectos
    opciones_proyectos = [None] + proyectos
    
    sel_proyecto = st.sidebar.selectbox(
        "Proyecto actual",
        options=opciones_proyectos,
        format_func=lambda x: "Sin seleccionar" if x is None else f"{'✅' if x.activo else '⏸️'} {x.nombre}",
        index=0,
        key="selector_proyecto"
    )
    
    # Guardar proyecto seleccionado en session_state
    st.session_state["proyecto_seleccionado"] = sel_proyecto
    
    # Botón nuevo proyecto
    if st.sidebar.button("➕ Nuevo proyecto", use_container_width=True, key="btn_nuevo_proyecto"):
        st.session_state["show_project_modal"] = True
        st.rerun()
    
    # Selector de mes si hay proyecto seleccionado
    if sel_proyecto:
        st.sidebar.divider()
        st.sidebar.markdown("### 📅 Mes")
        
        meses_proyecto = obtener_meses_proyecto(db, sel_proyecto.id)
        
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
            st.session_state["año_seleccionado"] = año_sel
            st.session_state["mes_seleccionado"] = mes_sel
        else:
            st.session_state["año_seleccionado"] = None
            st.session_state["mes_seleccionado"] = None
        
        # Botón agregar mes
        if st.sidebar.button("➕ Agregar mes", use_container_width=True, key="btn_agregar_mes"):
            st.session_state["show_add_month"] = True
        
        # Formulario agregar mes
        if st.session_state.get("show_add_month", False):
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
                    if agregar_mes_proyecto(db, sel_proyecto, nuevo_año, nuevo_mes):
                        st.success(f"✅ {MESES_ES[nuevo_mes]} {nuevo_año} agregado")
                        st.session_state["show_add_month"] = False
                        st.rerun()
                    else:
                        st.error("Este mes ya existe en el proyecto")
                
                if cancelar_mes:
                    st.session_state["show_add_month"] = False
                    st.rerun()

def render_current_page(db: Session):
    """Renderiza la página actual basada en el estado"""
    current_page = st.session_state.get("current_page", "dashboard")
    
    if current_page == "dashboard":
        render_dashboard_index(db)
    elif current_page == "perfil":
        render_perfil_page(db)
    else:
        st.session_state.current_page = "dashboard"
        render_dashboard_index(db)

if __name__ == "__main__":
    main()
