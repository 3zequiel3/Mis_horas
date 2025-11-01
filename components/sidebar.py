# components/sidebar.py
import streamlit as st
import datetime
from sqlalchemy.orm import Session
from services.proyecto_service import obtener_meses_proyecto, agregar_mes_proyecto
from utils.constants import MESES_ES

def render_sidebar(db: Session, proyectos):
    """Renderiza el sidebar completo"""
    st.sidebar.title("📁 Proyectos")

    # Inicializar estado del modal
    if "show_project_modal" not in st.session_state:
        st.session_state["show_project_modal"] = False

    # Selector de proyecto con opción "Sin seleccionar"
    opciones_proyectos = [None] + proyectos
    
    sel_proyecto = st.sidebar.selectbox(
        "Proyecto actual",
        options=opciones_proyectos,
        format_func=lambda x: "Sin seleccionar" if x is None else f"{x.nombre}",
        index=0,
    )

    # Botón nuevo proyecto
    if st.sidebar.button("➕ Nuevo proyecto"):
        st.session_state["show_project_modal"] = True

    # Selector de mes (solo si hay proyecto seleccionado)
    mes_sel = None
    año_sel = None
    
    if sel_proyecto:
        mes_sel, año_sel = render_month_selector(db, sel_proyecto)

    return sel_proyecto, mes_sel, año_sel

def render_month_selector(db: Session, proyecto):
    """Renderiza el selector de mes y funcionalidad para agregar meses"""
    st.sidebar.divider()
    st.sidebar.subheader("📅 Mes")
    
    # Obtener meses del proyecto seleccionado
    meses_proyecto = obtener_meses_proyecto(db, proyecto.id)
    
    mes_sel = None
    año_sel = None
    
    if meses_proyecto:
        # Crear opciones para el selectbox
        opciones_meses = []
        for año, mes in meses_proyecto:
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
        render_add_month_form(db, proyecto)

    return mes_sel, año_sel

def render_add_month_form(db: Session, proyecto):
    """Renderiza el formulario para agregar un nuevo mes"""
    with st.sidebar.form("form_agregar_mes"):
        st.write("**Agregar nuevo mes:**")
        hoy = datetime.date.today()
        nuevo_año = st.number_input("Año", min_value=2020, max_value=2100, value=hoy.year)
        
        # Selectbox con nombres de meses
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