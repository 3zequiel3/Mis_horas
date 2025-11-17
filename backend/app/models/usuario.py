from app import db
from datetime import datetime
import hashlib

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=True)
    foto_perfil = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True)
    mantener_sesion = db.Column(db.Boolean, default=False)
    usar_horas_reales = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime, nullable=True)

    # Relaciones
    proyectos = db.relationship("Proyecto", back_populates="usuario", cascade="all, delete-orphan")

    def verificar_password(self, password: str) -> bool:
        """Verifica si la contraseña es correcta"""
        return hashlib.sha256(password.encode()).hexdigest() == self.password_hash

    @staticmethod
    def hash_password(password: str) -> str:
        """Genera hash de la contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()

    def to_dict(self):
        """Convierte el usuario a diccionario"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nombre_completo': self.nombre_completo,
            'foto_perfil': self.foto_perfil,
            'activo': self.activo,
            'usar_horas_reales': self.usar_horas_reales,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'ultimo_acceso': self.ultimo_acceso.isoformat() if self.ultimo_acceso else None,
        }
