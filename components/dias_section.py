import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from models import Dia
from services.dia_service import actualizar_horas_dia, recalcular_tareas_afectadas
from utils.formatters import horas_a_formato, formato_a_horas
from utils.constants import MESES_ES

def render_dias_section(db: Session, proyecto, año_sel: int, mes_sel: int):
    """Sección para visualizar y editar horas trabajadas por día"""
    
    # Obtener configuración del usuario
    usar_horas_reales = st.session_state.get('user_usar_horas_reales', False)
    
    # Título dinámico según configuración
    if usar_horas_reales:
        st.subheader(f"{MESES_ES[mes_sel]} {año_sel} – días (Modo: Horas Reales)")
    else:
        st.subheader(f"{MESES_ES[mes_sel]} {año_sel} – días")

    # Obtener días del mes
    dias = (
        db.query(Dia)
        .filter(
            Dia.proyecto_id == proyecto.id,
            extract('year', Dia.fecha) == año_sel,
            extract('month', Dia.fecha) == mes_sel
        )
        .order_by(Dia.fecha)
        .all()
    )

    if not dias:
        st.info("No hay días registrados para este mes")
        return

    # Preparar datos según configuración
    data_dias = []
    for d in dias:
        row_data = {
            "id": d.id,
            "Fecha": d.fecha.strftime("%d/%m/%Y"),
            "Día": d.dia_semana,
            "Horas Trabajadas": horas_a_formato(d.horas_trabajadas),
        }
        
        # Si horas reales está activado, AGREGAR la columna adicional
        if usar_horas_reales:
            row_data["Horas Reales"] = horas_a_formato(d.horas_reales)
        
        data_dias.append(row_data)
    
    df_dias = pd.DataFrame(data_dias)

    # Configurar columnas
    column_config = {
        "id": None,  # Ocultar ID
        "Fecha": st.column_config.Column(disabled=True, width="small"),
        "Día": st.column_config.Column(disabled=True, width="small"),
        "Horas Trabajadas": st.column_config.TextColumn(
            "⏰ Horas Trabajadas",
            help="Formato HH:MM (ej: 02:30 para 2 horas y 30 minutos)",
            width="medium"
        ),
    }
    
    # Si horas reales está activado, agregar configuración de columna
    if usar_horas_reales:
        column_config["Horas Reales"] = st.column_config.TextColumn(
            "⏱️ Horas Reales",
            disabled=True,
            help="Calculado automáticamente: Horas Trabajadas ÷ 2",
            width="medium"
        )

    # Editor de datos
    edited = st.data_editor(
        df_dias,
        hide_index=True,
        column_config=column_config,
        use_container_width=True,
        num_rows="fixed",
        key=f"dias_editor_{proyecto.id}_{año_sel}_{mes_sel}"
    )

    # Detectar cambios y guardar automáticamente
    key_prev = f"dias_editor_prev_{proyecto.id}_{año_sel}_{mes_sel}"
    if key_prev not in st.session_state:
        st.session_state[key_prev] = df_dias.copy()

    if not edited.equals(st.session_state[key_prev]):
        cambios_detectados = False
        dias_modificados = []
        
        for idx, row in edited.iterrows():
            # Obtener valor anterior
            valor_anterior = st.session_state[key_prev].loc[idx, "Horas Trabajadas"]
            valor_nuevo = row["Horas Trabajadas"]
            
            # Solo actualizar si cambió
            if valor_nuevo != valor_anterior:
                dia_actualizado = actualizar_horas_dia(
                    db, 
                    int(row["id"]), 
                    str(valor_nuevo),
                    st.session_state.user_id
                )
                if dia_actualizado:
                    dias_modificados.append(dia_actualizado)
                    cambios_detectados = True
        
        if cambios_detectados:
            # Recalcular horas de tareas afectadas por los cambios
            for dia_modificado in dias_modificados:
                recalcular_tareas_afectadas(db, dia_modificado)
            
            st.session_state[key_prev] = edited.copy()
            st.success("✅ Guardado automáticamente")
            st.rerun()

    # Mostrar totales según configuración
    st.divider()
    
    if usar_horas_reales:
        total_trabajadas = sum(d.horas_trabajadas for d in dias)
        total_reales = sum(d.horas_reales for d in dias)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Total horas trabajadas:** {horas_a_formato(total_trabajadas)}")
        with col2:
            st.markdown(f"**Total horas reales:** {horas_a_formato(total_reales)}")
    else:
        total = sum(d.horas_trabajadas for d in dias)
        st.markdown(f"**Total horas trabajadas:** {horas_a_formato(total)}")

def render_totales_mes(db: Session, proyecto_id: int, año: int, mes: int, usar_horas_reales: bool):
    """Muestra los totales del mes"""
    # Calcular totales
    total_trabajadas = db.query(func.sum(Dia.horas_trabajadas)).filter(
        Dia.proyecto_id == proyecto_id,
        extract('year', Dia.fecha) == año,
        extract('month', Dia.fecha) == mes
    ).scalar() or 0
    
    total_reales = db.query(func.sum(Dia.horas_reales)).filter(
        Dia.proyecto_id == proyecto_id,
        extract('year', Dia.fecha) == año,
        extract('month', Dia.fecha) == mes
    ).scalar() or 0
    
    # Mostrar según configuración
    if usar_horas_reales:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📊 Total Horas Trabajadas", f"{total_trabajadas:.1f}h")
        with col2:
            st.metric("⏱️ Total Horas Reales", f"{total_reales:.1f}h")
    else:
        st.metric("📊 Total Horas del Mes", f"{total_trabajadas:.1f}h")