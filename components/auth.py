import streamlit as st
from sqlalchemy.orm import Session
from services.auth_service import (
    crear_usuario, 
    autenticar_usuario, 
    obtener_usuario_por_id
)
import re
import uuid
import json
from pathlib import Path

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
    Genera y mantiene un browser_id único por sesión del navegador.
    - Si ya existe en session_state, lo reutiliza ✅
    - Si no existe pero hay sesión persistente guardada, la recupera ✅
    - Si no existe nada, genera uno nuevo ✅
    """
    # 1. Si ya está en session_state, retornarlo (sesión activa)
    if 'browser_id' in st.session_state:
        return st.session_state.browser_id
    
    # 2. Verificar si hay sesión persistente guardada
    temp_dir = Path("data/temp_sessions")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Usar session_id de Streamlit para identificar esta pestaña
    try:
        session_id = st.runtime.scriptrunner.get_script_run_ctx().session_id
        session_file = temp_dir / f"{session_id}.json"
        
        # Si existe archivo, cargar browser_id
        if session_file.exists():
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                    browser_id = data['browser_id']
                    # Guardar en session_state para no volver a leer el archivo
                    st.session_state.browser_id = browser_id
                    return browser_id
            except:
                pass
    except:
        # Si falla obtener session_id, continuar sin persistencia
        pass
    
    # 3. No existe en ningún lado, generar nuevo
    browser_id = str(uuid.uuid4())
    st.session_state.browser_id = browser_id
    
    # Guardar en archivo SOLO si se activa "mantener sesión"
    # (esto se hace en login_user cuando keep_session=True)
    
    return browser_id

def save_browser_id_to_disk(browser_id: str):
    """Guarda el browser_id en disco para persistencia entre sesiones"""
    try:
        temp_dir = Path("data/temp_sessions")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        session_id = st.runtime.scriptrunner.get_script_run_ctx().session_id
        session_file = temp_dir / f"{session_id}.json"
        
        with open(session_file, 'w') as f:
            json.dump({'browser_id': browser_id}, f)
    except:
        pass

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
    # SOLO si NO está autenticado en session_state
    if 'authenticated' not in st.session_state:
        # Intentar cargar sesión PERSISTENTE (solo si marcó "mantener sesión")
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
        st.caption("💡 Si no marcas esta opción, deberás iniciar sesión al cerrar el navegador")
        
        login_button = st.form_submit_button("🔑 Iniciar Sesión", type="primary", use_container_width=True)
        
        if login_button:
            if not username or not password:
                st.error("Por favor completa todos los campos")
                return
            
            usuario = autenticar_usuario(db, username, password)
            if usuario:
                # Login en session_state (siempre, para que funcione mientras esté abierta la pestaña)
                login_user(usuario, keep_session)
                
                st.success(f"¡Bienvenido {usuario.nombre_completo}!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

def login_user(usuario, mantener_sesion=False):
    """Función helper para hacer login de usuario"""
    # Guardar en session_state (SIEMPRE, para que funcione en la sesión actual)
    st.session_state.authenticated = True
    st.session_state.user_id = usuario.id
    st.session_state.user_username = usuario.username
    st.session_state.user_nombre = usuario.nombre_completo
    st.session_state.user_email = usuario.email
    st.session_state.user_foto = usuario.foto_perfil
    st.session_state.user_mantener_sesion = mantener_sesion
    st.session_state.user_usar_horas_reales = usuario.usar_horas_reales
    
    # Si marcó "mantener sesión", guardar en disco y en browser_sessions.json
    if mantener_sesion:
        browser_id = get_browser_id()
        
        # Guardar browser_id en archivo para persistencia
        save_browser_id_to_disk(browser_id)
        
        # Guardar sesión en browser_sessions.json
        from services.auth_service import guardar_sesion_navegador
        from db import init_db
        from utils.helpers import get_db
        
        init_db()
        db = next(get_db())
        guardar_sesion_navegador(db, browser_id, usuario.id)

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