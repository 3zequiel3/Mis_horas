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
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

tarea_dia = Table(
    "tarea_dia",
    Base.metadata,
    Column("tarea_id", Integer, ForeignKey("tareas.id"), primary_key=True),
    Column("dia_id", Integer, ForeignKey("dias.id"), primary_key=True),
    UniqueConstraint("tarea_id", "dia_id", name="uq_tarea_dia"),
)


class Proyecto(Base):
    __tablename__ = "proyectos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    anio = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)

    dias = relationship("Dia", back_populates="proyecto", cascade="all, delete-orphan")
    tareas = relationship(
        "Tarea", back_populates="proyecto", cascade="all, delete-orphan"
    )


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
    horas = Column(String(50), default="")  # lo dejo string porque vos ponés 18:00
    que_falta = Column(Text, nullable=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=False)

    proyecto = relationship("Proyecto", back_populates="tareas")
    dias = relationship("Dia", secondary=tarea_dia, back_populates="tareas")
