# models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
    Text,
    Table,
    Float,
    UniqueConstraint,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import hashlib

Base = declarative_base()

tarea_dia = Table(
    "tarea_dia",
    Base.metadata,
    Column("tarea_id", Integer, ForeignKey("tareas.id"), primary_key=True),
    Column("dia_id", Integer, ForeignKey("dias.id"), primary_key=True),
)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre_completo = Column(String(100), nullable=True)
    foto_perfil = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    mantener_sesion = Column(Boolean, default=False)
    usar_horas_reales = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    ultimo_acceso = Column(DateTime, nullable=True)

    # Relaciones
    proyectos = relationship("Proyecto", back_populates="usuario", cascade="all, delete-orphan")

    def verificar_password(self, password: str) -> bool:
        """Verifica si la contraseña es correcta"""
        return hashlib.sha256(password.encode()).hexdigest() == self.password_hash

    @staticmethod
    def hash_password(password: str) -> str:
        """Genera hash de la contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()


class Proyecto(Base):
    __tablename__ = "proyectos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    anio = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    activo = Column(Boolean, default=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="proyectos")
    dias = relationship("Dia", back_populates="proyecto", cascade="all, delete-orphan")
    tareas = relationship("Tarea", back_populates="proyecto", cascade="all, delete-orphan")


class Dia(Base):
    __tablename__ = "dias"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, index=True)
    dia_semana = Column(String(20), nullable=False)
    horas_trabajadas = Column(Float, default=0)
    horas_reales = Column(Float, default=0)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=False)

    proyecto = relationship("Proyecto", back_populates="dias")
    tareas = relationship("Tarea", secondary=tarea_dia, back_populates="dias")


class Tarea(Base):
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    detalle = Column(Text, nullable=True)
    horas = Column(String(50), default="")
    que_falta = Column(Text, nullable=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=False)

    proyecto = relationship("Proyecto", back_populates="tareas")
    dias = relationship("Dia", secondary=tarea_dia, back_populates="tareas")
