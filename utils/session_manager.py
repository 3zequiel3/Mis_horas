import streamlit as st  # ← AGREGAR ESTE IMPORT
import json
import os
from datetime import datetime
from pathlib import Path

# Archivo para guardar usuarios recordados
REMEMBERED_USERS_FILE = Path("data/remembered_users.json")

def ensure_data_directory():
    """Asegura que el directorio data existe"""
    REMEMBERED_USERS_FILE.parent.mkdir(parents=True, exist_ok=True)

def save_remembered_user(user_id: int, username: str, auto_login: bool = False):
    """Guarda un usuario para recordar"""
    ensure_data_directory()
    
    users = get_remembered_users()
    
    # Actualizar o agregar usuario
    users[str(user_id)] = {
        "id": user_id,
        "username": username,
        "last_login": datetime.now().isoformat(),
        "auto_login": auto_login
    }
    
    with open(REMEMBERED_USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def get_remembered_users() -> dict:
    """Obtiene todos los usuarios recordados"""
    ensure_data_directory()
    
    if not REMEMBERED_USERS_FILE.exists():
        return {}
    
    try:
        with open(REMEMBERED_USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def get_remembered_users_list() -> list:
    """Obtiene lista de usuarios recordados ordenados por último login"""
    users = get_remembered_users()
    users_list = list(users.values())
    users_list.sort(key=lambda x: x.get('last_login', ''), reverse=True)
    return users_list

def get_last_logged_user() -> dict:
    """Obtiene el último usuario que inició sesión con auto-login activado"""
    users = get_remembered_users()
    
    # Buscar el usuario con auto_login = True y último login más reciente
    auto_login_users = [u for u in users.values() if u.get('auto_login', False)]
    
    if auto_login_users:
        auto_login_users.sort(key=lambda x: x.get('last_login', ''), reverse=True)
        return auto_login_users[0]
    
    return None

def remove_remembered_user(user_id: int):
    """Elimina un usuario recordado"""
    ensure_data_directory()
    
    users = get_remembered_users()
    
    if str(user_id) in users:
        del users[str(user_id)]
        
        with open(REMEMBERED_USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)

def clear_all_remembered_users():
    """Elimina todos los usuarios recordados"""
    ensure_data_directory()
    
    if REMEMBERED_USERS_FILE.exists():
        REMEMBERED_USERS_FILE.unlink()

def auto_login_if_remembered(db):
    """Intenta hacer auto-login si hay un usuario con esa opción activada"""
    # Si ya está autenticado, no hacer nada
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        return True
    
    # Buscar usuario con auto-login
    last_user = get_last_logged_user()
    
    if last_user:
        from services.auth_service import obtener_usuario_por_id
        usuario = obtener_usuario_por_id(db, last_user['id'])
        
        if usuario:
            # Restaurar sesión
            st.session_state.authenticated = True
            st.session_state.user_id = usuario.id
            st.session_state.user_username = usuario.username
            st.session_state.user_nombre = usuario.nombre_completo
            st.session_state.user_email = usuario.email
            st.session_state.user_foto = usuario.foto_perfil
            
            # Actualizar último login
            save_remembered_user(usuario.id, usuario.username, auto_login=True)
            
            return True
    
    return False