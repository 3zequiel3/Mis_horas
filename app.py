# app.py
import streamlit as st
from sqlalchemy.orm import Session
from db import init_db
from models import Proyecto
from components.sidebar import render_sidebar
from components.forms import render_project_form
from components.dias_section import render_dias_section  
from components.tareas_section import render_tareas_section
from utils.helpers import get_db

def main():
    st.set_page_config(
        page_title="Mis Horas",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_db()
    db = next(get_db())

    # Cargar proyectos
    proyectos = db.query(Proyecto).order_by(Proyecto.id.desc()).all()
    
    # Renderizar sidebar
    sel_proyecto, mes_sel, año_sel = render_sidebar(db, proyectos)
    
    # Renderizar formulario de proyecto si está activo
    if st.session_state.get("show_project_modal", False):
        render_project_form(db)
        st.divider()

    # Main content
    if not st.session_state.get("show_project_modal", False):
        st.title("🕒 Mis horas")

        if not sel_proyecto:
            st.info("Selecciona un proyecto desde el sidebar para comenzar.")
            return

        if not proyectos:
            st.info("No hay proyectos todavía. Creá uno desde el sidebar.")
            return

        if not mes_sel or not año_sel:
            st.info("Selecciona un mes desde el sidebar para continuar.")
            return

        # Layout principal
        col_izq, col_der = st.columns([1.1, 1.4], gap="large")

        with col_izq:
            render_dias_section(db, sel_proyecto, año_sel, mes_sel)

        with col_der:
            render_tareas_section(db, sel_proyecto, año_sel, mes_sel)

if __name__ == "__main__":
    main()
