import streamlit as st
from sqlalchemy.orm import Session
from services.auth_service import actualizar_perfil_usuario, cambiar_password
from components.auth import validate_email, validate_password
import base64

# Ya NO incluimos render_user_menu - se maneja en app.py

def render_profile_edit_form(db: Session):
    """Formulario para editar datos del perfil"""
    with st.form("edit_profile_form"):
        st.markdown("#### 📝 Editar Información Personal")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nuevo_email = st.text_input(
                "Email",
                value=st.session_state.get('user_email', ''),
                placeholder="ejemplo@email.com"
            )
            
        with col2:
            nuevo_nombre = st.text_input(
                "Nombre Completo",
                value=st.session_state.get('user_nombre', ''),
                placeholder="Juan Pérez"
            )
        
        st.markdown("#### 📷 Foto de Perfil")
        uploaded_file = st.file_uploader(
            "Subir nueva foto",
            type=['png', 'jpg', 'jpeg'],
            help="Tamaño máximo: 5MB"
        )
        
        if uploaded_file:
            st.image(uploaded_file, width=100, caption="Preview de nueva foto")
        
        actualizar_button = st.form_submit_button("💾 Actualizar Perfil", type="primary")
        
        if actualizar_button:
            if not nuevo_email or not nuevo_nombre:
                st.error("Email y nombre son obligatorios")
                return
            
            if not validate_email(nuevo_email):
                st.error("Email inválido")
                return
            
            datos_update = {
                'email': nuevo_email,
                'nombre_completo': nuevo_nombre
            }
            
            if uploaded_file:
                foto_bytes = uploaded_file.read()
                if len(foto_bytes) > 5 * 1024 * 1024:
                    st.error("La imagen es muy grande (máximo 5MB)")
                    return
                
                foto_base64 = base64.b64encode(foto_bytes).decode()
                datos_update['foto_perfil'] = f"data:image/{uploaded_file.type.split('/')[-1]};base64,{foto_base64}"
            
            usuario, mensaje = actualizar_perfil_usuario(
                db, 
                st.session_state.user_id, 
                **datos_update
            )
            
            if usuario:
                st.session_state.user_email = usuario.email
                st.session_state.user_nombre = usuario.nombre_completo
                if usuario.foto_perfil:
                    st.session_state.user_foto = usuario.foto_perfil
                
                st.success(mensaje)
                st.rerun()
            else:
                st.error(mensaje)

def render_password_change_form(db: Session):
    """Formulario para cambiar contraseña"""
    with st.form("change_password_form"):
        st.markdown("#### 🔒 Cambiar Contraseña")
        
        password_actual = st.text_input(
            "Contraseña Actual",
            type="password",
            placeholder="Tu contraseña actual"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            password_nueva = st.text_input(
                "Nueva Contraseña",
                type="password",
                placeholder="Mínimo 6 caracteres"
            )
        
        with col2:
            password_confirm = st.text_input(
                "Confirmar Nueva Contraseña",
                type="password",
                placeholder="Repite la nueva contraseña"
            )
        
        cambiar_button = st.form_submit_button("🔒 Cambiar Contraseña", type="primary")
        
        if cambiar_button:
            if not all([password_actual, password_nueva, password_confirm]):
                st.error("Completa todos los campos")
                return
            
            if password_nueva != password_confirm:
                st.error("Las nuevas contraseñas no coinciden")
                return
            
            password_valid, password_msg = validate_password(password_nueva)
            if not password_valid:
                st.error(password_msg)
                return
            
            success, mensaje = cambiar_password(
                db,
                st.session_state.user_id,
                password_actual,
                password_nueva
            )
            
            if success:
                st.success(mensaje)
            else:
                st.error(mensaje)