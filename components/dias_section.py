# dias_section.py
import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from services.dia_service import obtener_dias_mes, actualizar_horas_dia, recalcular_tareas_afectadas
from utils.formatters import horas_a_formato, formato_a_horas
from utils.constants import MESES_ES

def render_dias_section(db: Session, proyecto, año_sel: int, mes_sel: int):
    """Renderiza la sección de días del mes"""
    st.subheader(f"{MESES_ES[mes_sel]} {año_sel} – días")

    # Obtener días del mes
    dias = obtener_dias_mes(db, proyecto.id, año_sel, mes_sel)

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
        key=f"dias_editor_{proyecto.id}_{año_sel}_{mes_sel}"
    )

    # Detectar cambios y guardar automáticamente
    key_prev = f"dias_editor_prev_{proyecto.id}_{año_sel}_{mes_sel}"
    if key_prev not in st.session_state:
        st.session_state[key_prev] = df_dias

    if not edited.equals(st.session_state[key_prev]):
        cambios_detectados = False
        dias_modificados = []
        
        for _, row in edited.iterrows():
            dia_actualizado = actualizar_horas_dia(db, int(row["id"]), str(row["Horas Trabajadas"]))
            if dia_actualizado:
                dias_modificados.append(dia_actualizado)
                cambios_detectados = True
        
        if cambios_detectados:
            # Recalcular tareas afectadas
            for dia_modificado in dias_modificados:
                recalcular_tareas_afectadas(db, dia_modificado)
            
            st.session_state[key_prev] = edited.copy()
            st.success("✅ Guardado automáticamente")
            st.rerun()

    # Totales en formato HH:MM
    total_trab = sum(d.horas_trabajadas for d in dias)
    total_real = sum(d.horas_reales for d in dias)
    st.markdown(f"**Total horas trabajadas:** {horas_a_formato(total_trab)}")
    st.markdown(f"**Total horas reales:** {horas_a_formato(total_real)}")