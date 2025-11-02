import streamlit as st
import datetime
from sqlalchemy.orm import Session
from services.proyecto_service import crear_proyecto

def render_project_form(db: Session):
    """Formulario para crear un nuevo proyecto con mes y año inicial"""
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
                crear_proyecto(
                    db, 
                    nombre, 
                    descripcion, 
                    anio, 
                    mes, 
                    st.session_state.user_id
                )
                st.success("Proyecto creado ✅")
                st.session_state["show_project_modal"] = False
                st.rerun()
            elif crear and not nombre.strip():
                st.error("El nombre del proyecto es obligatorio")

            if cancelar:
                st.session_state["show_project_modal"] = False
                st.rerun()