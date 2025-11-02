from sqlalchemy.orm import Session
from models import Usuario
from datetime import datetime
import streamlit as st

def crear_usuario(db: Session, username: str, email: str, password: str, nombre_completo: str = None):
    """Crea un nuevo usuario"""
    # Verificar si ya existe el usuario o email
    existing_user = db.query(Usuario).filter(
        (Usuario.username == username) | (Usuario.email == email)
    ).first()
    
    if existing_user:
        if existing_user.username == username:
            return None, "El nombre de usuario ya está en uso"
        else:
            return None, "El email ya está registrado"
    
    # Crear nuevo usuario
    nuevo_usuario = Usuario(
        username=username,
        email=email,
        password_hash=Usuario.hash_password(password),
        nombre_completo=nombre_completo,
        activo=True,
        mantener_sesion=False,
        usar_horas_reales=False
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario, "Usuario creado exitosamente"

def autenticar_usuario(db: Session, username_or_email: str, password: str):
    """Autentica un usuario por username o email"""
    usuario = db.query(Usuario).filter(
        (Usuario.username == username_or_email) | (Usuario.email == username_or_email)
    ).first()
    
    if usuario and usuario.verificar_password(password):
        # Actualizar último acceso
        usuario.ultimo_acceso = datetime.utcnow()
        db.commit()
        return usuario
    
    return None

def obtener_usuario_por_id(db: Session, user_id: int):
    """Obtiene un usuario por su ID"""
    return db.query(Usuario).filter(Usuario.id == user_id).first()

def actualizar_perfil_usuario(db: Session, user_id: int, nombre_completo: str = None, 
                              email: str = None, foto_perfil: str = None):
    """Actualiza el perfil del usuario"""
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    
    if not usuario:
        return None, "Usuario no encontrado"
    
    # Verificar si el email ya está en uso por otro usuario
    if email and email != usuario.email:
        existing = db.query(Usuario).filter(
            Usuario.email == email, 
            Usuario.id != user_id
        ).first()
        if existing:
            return None, "El email ya está en uso"
    
    # Actualizar campos
    if nombre_completo is not None:
        usuario.nombre_completo = nombre_completo
    if email is not None:
        usuario.email = email
    if foto_perfil is not None:
        usuario.foto_perfil = foto_perfil
    
    db.commit()
    db.refresh(usuario)
    
    return usuario, "Perfil actualizado exitosamente"

def cambiar_password(db: Session, user_id: int, password_actual: str, password_nueva: str):
    """Cambia la contraseña del usuario"""
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    
    if not usuario:
        return False, "Usuario no encontrado"
    
    # Verificar contraseña actual
    if not usuario.verificar_password(password_actual):
        return False, "La contraseña actual es incorrecta"
    
    # Actualizar contraseña
    usuario.password_hash = Usuario.hash_password(password_nueva)
    db.commit()
    
    return True, "Contraseña actualizada exitosamente"

def activar_mantener_sesion(db: Session, user_id: int, activar: bool = True):
    """Activa o desactiva 'mantener sesión' para un usuario"""
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    
    if not usuario:
        return False, "Usuario no encontrado"
    
    usuario.mantener_sesion = activar
    usuario.ultimo_acceso = datetime.utcnow()
    db.commit()
    
    return True, f"Mantener sesión {'activado' if activar else 'desactivado'} exitosamente"

def activar_horas_reales(db: Session, user_id: int, activar: bool = True):
    """Activa o desactiva el cálculo de 'horas reales' (división por 2) para un usuario"""
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    
    if not usuario:
        return False, "Usuario no encontrado"
    
    usuario.usar_horas_reales = activar
    db.commit()
    
    return True, f"Cálculo de horas reales {'activado' if activar else 'desactivado'} exitosamente"

def obtener_usuario_con_sesion_activa(db: Session):
    """Obtiene el último usuario que tiene mantener_sesion=True"""
    usuario = db.query(Usuario).filter(
        Usuario.mantener_sesion == True
    ).order_by(Usuario.ultimo_acceso.desc()).first()
    
    return usuario

def logout_usuario():
    """Cierra la sesión del usuario actual"""
    # Limpiar session_state
    keys_to_keep = []
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]