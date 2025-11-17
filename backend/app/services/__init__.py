from app import db
from app.models.usuario import Usuario
from datetime import datetime

class AuthService:
    @staticmethod
    def crear_usuario(username: str, email: str, password: str, nombre_completo: str = None):
        """Crea un nuevo usuario"""
        # Verificar si ya existe
        existing = Usuario.query.filter(
            (Usuario.username == username) | (Usuario.email == email)
        ).first()
        
        if existing:
            if existing.username == username:
                return None, "El nombre de usuario ya está en uso"
            return None, "El email ya está registrado"
        
        # Crear usuario
        usuario = Usuario(
            username=username,
            email=email,
            password_hash=Usuario.hash_password(password),
            nombre_completo=nombre_completo,
            activo=True,
            mantener_sesion=False,
            usar_horas_reales=False
        )
        
        db.session.add(usuario)
        db.session.commit()
        
        return usuario, "Usuario creado exitosamente"
    
    @staticmethod
    def autenticar_usuario(username_or_email: str, password: str):
        """Autentica un usuario"""
        usuario = Usuario.query.filter(
            (Usuario.username == username_or_email) | (Usuario.email == username_or_email)
        ).first()
        
        if usuario and usuario.verificar_password(password):
            usuario.ultimo_acceso = datetime.utcnow()
            db.session.commit()
            return usuario
        
        return None
    
    @staticmethod
    def obtener_usuario_por_id(user_id: int):
        """Obtiene un usuario por ID"""
        return Usuario.query.filter(Usuario.id == user_id).first()
    
    @staticmethod
    def actualizar_perfil(user_id: int, nombre_completo: str = None, 
                         email: str = None, foto_perfil: str = None):
        """Actualiza el perfil del usuario"""
        usuario = Usuario.query.filter(Usuario.id == user_id).first()
        
        if not usuario:
            return None, "Usuario no encontrado"
        
        # Verificar email duplicado
        if email and email != usuario.email:
            existing = Usuario.query.filter(
                Usuario.email == email, 
                Usuario.id != user_id
            ).first()
            if existing:
                return None, "El email ya está en uso"
        
        if nombre_completo is not None:
            usuario.nombre_completo = nombre_completo
        if email is not None:
            usuario.email = email
        if foto_perfil is not None:
            usuario.foto_perfil = foto_perfil
        
        db.session.commit()
        return usuario, "Perfil actualizado"
    
    @staticmethod
    def cambiar_password(user_id: int, password_actual: str, password_nueva: str):
        """Cambia la contraseña"""
        usuario = Usuario.query.filter(Usuario.id == user_id).first()
        
        if not usuario:
            return False, "Usuario no encontrado"
        
        if not usuario.verificar_password(password_actual):
            return False, "Contraseña actual incorrecta"
        
        usuario.password_hash = Usuario.hash_password(password_nueva)
        db.session.commit()
        
        return True, "Contraseña actualizada"
    
    @staticmethod
    def activar_horas_reales(user_id: int, activar: bool):
        """Activa o desactiva horas reales"""
        usuario = Usuario.query.filter(Usuario.id == user_id).first()
        
        if not usuario:
            return False, "Usuario no encontrado"
        
        usuario.usar_horas_reales = activar
        db.session.commit()
        
        return True, "Configuración actualizada"
