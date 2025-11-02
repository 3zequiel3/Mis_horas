import streamlit as st
from sqlalchemy.orm import Session
from components.user_profile import render_profile_edit_form, render_password_change_form
from services.auth_service import logout_usuario, activar_horas_reales, obtener_usuario_por_id
from components.auth import get_browser_id
import json
from pathlib import Path

def render_perfil_page(db: Session):
    """Página de perfil de usuario"""
    
    # Header simple
    st.title("👤 Mi Perfil")
    st.markdown("---")
    
    # Información básica del usuario
    render_user_info_section()
    
    st.divider()
    
    # Tabs para diferentes secciones
    tab_info, tab_password, tab_sesiones, tab_configuracion = st.tabs([
        "📝 Información Personal", 
        "🔒 Cambiar Contraseña",
        "💻 Sesiones",
        "⚙️ Configuración"
    ])
    
    with tab_info:
        render_profile_edit_form(db)
    
    with tab_password:
        render_password_change_form(db)
    
    with tab_sesiones:
        render_sessions_management(db)
    
    with tab_configuracion:
        render_user_settings(db)

def render_user_info_section():
    """Sección de información básica del usuario"""
    col_foto, col_info = st.columns([1, 3])
    
    with col_foto:
        if st.session_state.get('user_foto'):
            try:
                st.image(st.session_state.user_foto, width=120)
            except:
                st.markdown("👤")
        else:
            st.markdown(
                f"""
                <div style='width: 120px; height: 120px; border-radius: 50%; 
                           background-color: #0066cc; display: flex; 
                           align-items: center; justify-content: center; 
                           color: white; font-size: 48px; font-weight: bold;
                           margin: 0 auto;'>
                    {st.session_state.get('user_nombre', 'U')[0].upper()}
                </div>
                """,
                unsafe_allow_html=True
            )
    
    with col_info:
        st.markdown(f"### {st.session_state.get('user_nombre', 'Usuario')}")
        st.markdown(f"**Usuario:** @{st.session_state.get('user_username', 'username')}")
        st.markdown(f"**Email:** {st.session_state.get('user_email', 'No especificado')}")
        st.markdown(f"**Estado:** 🟢 Activo")

def render_sessions_management(db: Session):
    """Gestión de sesiones usando browser_sessions.json"""
    st.markdown("#### 💻 Gestión de Sesiones")
    
    # Obtener browser_id actual
    browser_id = get_browser_id()
    
    st.markdown("**🔐 Configuración de Sesión Actual:**")
    
    # Verificar si hay sesión persistente para este navegador
    sessions_file = Path("data/browser_sessions.json")
    sesion_activa = False
    
    if sessions_file.exists():
        try:
            with open(sessions_file, 'r') as f:
                sessions = json.load(f)
                sesion_activa = browser_id in sessions
        except:
            sesion_activa = False
    
    # Checkbox para mantener sesión
    mantener_sesion_nuevo = st.checkbox(
        "Mantener sesión iniciada en este dispositivo",
        value=sesion_activa,
        help="No necesitarás iniciar sesión cada vez que abras la página en ESTE navegador",
        key="checkbox_mantener_sesion"
    )
    
    # Detectar cambio
    if mantener_sesion_nuevo != sesion_activa:
        if mantener_sesion_nuevo:
            # Activar sesión persistente
            from services.auth_service import guardar_sesion_navegador
            guardar_sesion_navegador(db, browser_id, st.session_state.user_id)
            st.success("✅ Sesión guardada en este dispositivo")
        else:
            # Desactivar sesión persistente
            from services.auth_service import cerrar_sesion_navegador
            cerrar_sesion_navegador(browser_id)
            st.success("✅ Sesión eliminada de este dispositivo")
        
        st.rerun()
    
    st.divider()
    
    # Explicación
    with st.expander("💡 ¿Qué significa 'Mantener sesión iniciada'?", expanded=False):
        st.markdown("""
        **Cuando está ACTIVADO:**
        - ✅ No necesitas iniciar sesión cada vez que abres o recargas la página
        - ✅ Tu sesión se mantiene activa automáticamente **en este navegador**
        - ✅ Más cómodo para uso personal
        - ⚠️ **Solo funciona en este dispositivo/navegador**
        
        **Cuando está DESACTIVADO:**
        - 🔒 Debes iniciar sesión cada vez
        - 🔒 Más seguro para computadoras compartidas
        - 🔒 Recomendado para dispositivos públicos
        
        **Importante:**
        - Cada navegador/dispositivo tiene su propia sesión independiente
        - Si otro usuario accede desde otro dispositivo, deberá iniciar sesión
        - No se comparten sesiones entre navegadores
        """)
    
    st.divider()
    
    # Mostrar información de sesión actual
    st.markdown("**📊 Información de Sesión:**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🆔 ID de Navegador", browser_id[:8] + "...")
        
    with col2:
        estado = "✅ Persistente" if sesion_activa else "⏳ Temporal"
        st.metric("🔐 Tipo de Sesión", estado)
    
    # Información de último acceso
    usuario = obtener_usuario_por_id(db, st.session_state.user_id)
    if usuario and usuario.ultimo_acceso:
        st.caption(f"🕐 Último acceso: {usuario.ultimo_acceso.strftime('%d/%m/%Y %H:%M')}")
    
    st.divider()
    
    # Ver todas las sesiones activas del usuario
    if sessions_file.exists():
        with st.expander("🔍 Ver sesiones activas", expanded=False):
            try:
                with open(sessions_file, 'r') as f:
                    all_sessions = json.load(f)
                
                user_sessions = [
                    (bid, data) for bid, data in all_sessions.items() 
                    if data.get('user_id') == st.session_state.user_id
                ]
                
                if user_sessions:
                    st.markdown(f"**Tienes {len(user_sessions)} sesión(es) activa(s):**")
                    
                    for bid, data in user_sessions:
                        is_current = bid == browser_id
                        prefix = "🟢 **Esta sesión**" if is_current else "🔵 Otra sesión"
                        
                        st.markdown(f"{prefix}")
                        st.caption(f"   ID: {bid[:16]}...")
                        st.caption(f"   Última actividad: {data.get('last_activity', 'Desconocida')}")
                        
                        if not is_current:
                            if st.button(f"❌ Cerrar sesión {bid[:8]}", key=f"close_{bid}"):
                                from services.auth_service import cerrar_sesion_navegador
                                cerrar_sesion_navegador(bid)
                                st.success("Sesión cerrada")
                                st.rerun()
                        st.markdown("---")
                else:
                    st.info("No hay sesiones persistentes activas")
                    
            except Exception as e:
                st.error(f"Error al cargar sesiones: {str(e)}")
    
    st.divider()
    
    # Cerrar sesión actual
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚪 Cerrar Sesión Actual", type="primary", use_container_width=True):
            logout_usuario()
            st.success("Sesión cerrada correctamente")
            st.rerun()
    
    with col2:
        if st.button("🔴 Cerrar Todas las Sesiones", type="secondary", use_container_width=True):
            # Cerrar todas las sesiones del usuario
            if sessions_file.exists():
                try:
                    with open(sessions_file, 'r') as f:
                        all_sessions = json.load(f)
                    
                    # Filtrar sesiones de este usuario
                    new_sessions = {
                        bid: data for bid, data in all_sessions.items()
                        if data.get('user_id') != st.session_state.user_id
                    }
                    
                    with open(sessions_file, 'w') as f:
                        json.dump(new_sessions, f, indent=2)
                    
                    logout_usuario()
                    st.success("Todas las sesiones cerradas")
                    st.rerun()
                except:
                    st.error("Error al cerrar sesiones")

def render_user_settings(db: Session):
    """Configuraciones del usuario"""
    st.markdown("#### ⚙️ Configuración de Horas")
    
    # Obtener usuario actual
    usuario = obtener_usuario_por_id(db, st.session_state.user_id)
    
    if not usuario:
        st.error("Error al cargar información del usuario")
        return
    
    # Configuración de horas reales con CHECKBOX
    st.markdown("**⏰ Cálculo de Horas Reales**")
    
    usar_horas_reales_actual = usuario.usar_horas_reales
    
    usar_horas_reales_nuevo = st.checkbox(
        "Activar columna 'Horas Reales' (divide horas trabajadas ÷ 2)",
        value=usar_horas_reales_actual,
        help="Muestra una columna adicional con las horas trabajadas divididas entre 2",
        key="checkbox_horas_reales"
    )
    
    # Detectar cambio
    if usar_horas_reales_nuevo != usar_horas_reales_actual:
        success, mensaje = activar_horas_reales(db, usuario.id, usar_horas_reales_nuevo)
        if success:
            st.session_state.user_usar_horas_reales = usar_horas_reales_nuevo
            st.success(f"✅ {mensaje}")
            st.rerun()
        else:
            st.error(mensaje)
    
    # Mensaje informativo según estado
    if usar_horas_reales_nuevo:
        st.info("✅ La tabla de días mostrará la columna 'Horas Reales' calculada automáticamente")
    else:
        st.info("ℹ️ La tabla de días solo mostrará 'Horas Trabajadas'")
    
    st.divider()
    
    # Explicación detallada
    with st.expander("💡 ¿Qué son las 'Horas Reales'?", expanded=False):
        st.markdown("""
        ### Explicación del Cálculo
        
        **Modo Estándar (Desactivado):**
        - La tabla muestra solo "Horas Trabajadas"
        - Si registras 8 horas, se muestran 8 horas
        - Las estadísticas usan este valor directamente
        
        **Modo Horas Reales (Activado):**
        - La tabla muestra "Horas Trabajadas" Y "Horas Reales"
        - "Horas Reales" se calcula automáticamente: `horas_trabajadas ÷ 2`
        - Si registras 16 horas, se mostrarán 8 horas reales
        - Las estadísticas usan las horas reales
        
        ### Ejemplo Práctico
        
        **Sin horas reales:**
        ```
        | Fecha      | Horas Trabajadas |
        |------------|------------------|
        | 01/11/2025 | 8.0              |
        | 02/11/2025 | 6.0              |
        
        Estadísticas: 14h totales
        ```
        
        **Con horas reales:**
        ```
        | Fecha      | Horas Trabajadas | Horas Reales |
        |------------|------------------|--------------|
        | 01/11/2025 | 16.0             | 8.0          |
        | 02/11/2025 | 12.0             | 6.0          |
        
        Estadísticas: 14h reales (28h trabajadas)
        ```
        
        ### ¿Cuándo usar esta opción?
        - ✅ Cuando tu sistema requiere registrar el doble de horas
        - ✅ Cuando necesitas ver ambos valores en la tabla
        - ✅ Cuando las estadísticas deben usar horas reales
        - ❌ Si registras horas normales, déjalo desactivado
        """)
    
    st.divider()
    
    # Vista previa del cálculo
    st.markdown("**📊 Vista Previa del Cálculo**")
    
    col_a, col_b, col_c = st.columns(3)
    
    ejemplo_horas = 16
    
    with col_a:
        st.metric(
            label="Horas Registradas",
            value=f"{ejemplo_horas}h",
            help="Horas que ingresas en la tabla"
        )
    
    with col_b:
        st.metric(
            label="Sin Horas Reales",
            value=f"{ejemplo_horas}h",
            help="Solo se muestra este valor"
        )
    
    with col_c:
        st.metric(
            label="Con Horas Reales",
            value=f"{ejemplo_horas / 2}h",
            help="Columna adicional con valor dividido"
        )
    
    st.divider()
    
    # Otras configuraciones (placeholder)
    st.markdown("#### 🔔 Notificaciones")
    notifications_email = st.checkbox("Recibir notificaciones por email", value=False, disabled=True)
    st.caption("⚠️ Funcionalidad próximamente")
    
    st.divider()
    
    # Zona de peligro
    with st.expander("⚠️ Zona de Peligro", expanded=False):
        st.markdown("**Eliminar Cuenta**")
        st.warning("⚠️ Esta acción no se puede deshacer.")
        
        confirm_delete = st.checkbox("Entiendo que esta acción es irreversible")
        
        if confirm_delete:
            if st.button("🗑️ Eliminar Mi Cuenta", type="secondary"):
                st.error("Funcionalidad próximamente")