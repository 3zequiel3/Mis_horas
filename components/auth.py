import streamlit as st
from sqlalchemy.orm import Session
from services.auth_service import (
    crear_usuario, 
    autenticar_usuario, 
    obtener_usuario_por_id
)
import re
import uuid
import hashlib

def validate_email(email: str) -> bool:
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> tuple[bool, str]:
    """Valida que la contraseña cumpla requisitos mínimos"""
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    if not re.search(r'[A-Za-z]', password):
        return False, "La contraseña debe contener al menos una letra"
    if not re.search(r'[0-9]', password):
        return False, "La contraseña debe contener al menos un número"
    return True, ""

def get_browser_id():
    """
    Genera un ID único y persistente para este navegador/dispositivo.
    Se mantiene durante toda la sesión del navegador.
    """
    if 'browser_id' not in st.session_state:
        # Generar ID único basado en información de la sesión
        # Esto se regenera cada vez que se cierra el navegador
        st.session_state.browser_id = str(uuid.uuid4())
    
    return st.session_state.browser_id

def render_login_page(db: Session):
    """Página de login y registro"""
    st.set_page_config(
        page_title="Mis Horas - Login",
        page_icon="🔐",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # CSS para ocultar completamente el sidebar en login
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
            [data-testid="collapsedControl"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Obtener ID único del navegador
    browser_id = get_browser_id()
    
    # Verificar si hay sesión activa para ESTE navegador específico
    if 'authenticated' not in st.session_state:
        # Intentar cargar sesión guardada solo para este navegador
        from services.auth_service import obtener_sesion_activa_para_navegador
        sesion = obtener_sesion_activa_para_navegador(db, browser_id)
        
        if sesion:
            usuario = obtener_usuario_por_id(db, sesion['user_id'])
            if usuario:
                # Restaurar sesión solo para este navegador
                login_user(usuario, mantener_sesion=True)
                st.rerun()
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🕒 Mis Horas")
        st.markdown("### Sistema de Gestión de Tiempo")
    
    # Tabs para Login y Registro
    tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])
    
    with tab_login:
        render_login_form(db)
    
    with tab_register:
        render_register_form(db)

def render_login_form(db: Session):
    """Formulario de inicio de sesión"""
    st.markdown("#### Ingresa a tu cuenta")
    
    with st.form("login_form"):
        username = st.text_input(
            "Usuario o Email",
            placeholder="Ingresa tu usuario o email"
        )
        password = st.text_input(
            "Contraseña",
            type="password",
            placeholder="Ingresa tu contraseña"
        )
        
        keep_session = st.checkbox("Mantener sesión iniciada en este dispositivo", value=False)
        st.caption("💡 Tu sesión solo estará activa en este navegador/dispositivo")
        
        login_button = st.form_submit_button("🔑 Iniciar Sesión", type="primary", use_container_width=True)
        
        if login_button:
            if not username or not password:
                st.error("Por favor completa todos los campos")
                return
            
            usuario = autenticar_usuario(db, username, password)
            if usuario:
                # Obtener ID único de este navegador
                browser_id = get_browser_id()
                
                # Guardar sesión solo para este navegador
                if keep_session:
                    from services.auth_service import guardar_sesion_navegador
                    guardar_sesion_navegador(db, browser_id, usuario.id)
                
                # Login en session_state (temporal)
                login_user(usuario, keep_session)
                
                st.success(f"¡Bienvenido {usuario.nombre_completo}!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

def login_user(usuario, mantener_sesion=False):
    """Función helper para hacer login de usuario"""
    st.session_state.authenticated = True
    st.session_state.user_id = usuario.id
    st.session_state.user_username = usuario.username
    st.session_state.user_nombre = usuario.nombre_completo
    st.session_state.user_email = usuario.email
    st.session_state.user_foto = usuario.foto_perfil
    st.session_state.user_mantener_sesion = mantener_sesion
    st.session_state.user_usar_horas_reales = usuario.usar_horas_reales

def render_register_form(db: Session):
    """Formulario de registro"""
    st.markdown("#### Crea tu cuenta")
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input(
                "Nombre de Usuario",
                placeholder="Ej: juan123",
                help="Solo letras, números y guiones bajos"
            )
            email = st.text_input(
                "Email",
                placeholder="ejemplo@email.com"
            )
        
        with col2:
            nombre_completo = st.text_input(
                "Nombre Completo",
                placeholder="Juan Pérez"
            )
            password = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Mínimo 6 caracteres"
            )
        
        password_confirm = st.text_input(
            "Confirmar Contraseña",
            type="password",
            placeholder="Repite tu contraseña"
        )
        
        acepto_terminos = st.checkbox("Acepto los términos y condiciones")
        register_button = st.form_submit_button("📝 Registrarse", type="primary", use_container_width=True)
        
        if register_button:
            if not all([username, email, nombre_completo, password, password_confirm]):
                st.error("Por favor completa todos los campos")
                return
            
            if not acepto_terminos:
                st.error("Debes aceptar los términos y condiciones")
                return
            
            if password != password_confirm:
                st.error("Las contraseñas no coinciden")
                return
            
            if not validate_email(email):
                st.error("Email inválido")
                return
            
            password_valid, password_msg = validate_password(password)
            if not password_valid:
                st.error(password_msg)
                return
            
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                st.error("El nombre de usuario solo puede contener letras, números y guiones bajos")
                return
            
            usuario, mensaje = crear_usuario(db, username, email, password, nombre_completo)
            if usuario:
                st.success(mensaje)
                st.info("Ahora puedes iniciar sesión con tus credenciales")
            else:
                st.error(mensaje)